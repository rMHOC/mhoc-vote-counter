#!
__author__ = __author__ = [  'agentnola', 'chrispytoast123', 'jb567', 'electric-blue', 'rexrex600' ]

import gspread
import json
import praw
import re
from oauth2client.client import SignedJwtAssertionCredentials
import concurrent.futures
import getpass
import time

##  INITIALISATION OF PROGRAM AND ERROR CHECKING FUNCTIONS

#   Error checking functions

def checkURL():
    #Collects URL to be counted from
    print('Copy Voting Thread Link Below')
    URL = str(input())
    return URL

def login():
    #Collects login information for the user's reddit account
    user = str(input('Reddit Username:'))
    try:
        r.login(user,getpass.getpass('Reddit Password:'))
    except praw.errors.InvalidUserPass:
        print ("Incorrect Password")
        login()

#   Variables

sheetName = '10th Govt Voting Record'
docName = 'MHoC Master Sheet'
docKey = 'VoteCounter2-af942bc69325.json'
totalMPs = 100

#   Loads the JSON Key, which is provided seperately
json_key = json.load(open(docKey))
scope = ['https://spreadsheets.google.com/feeds']
#   Initilises all the credentials, and GoogleSheet stuff
credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
r = praw.Reddit('MHOC-plebian house, vote counter v1')
gc = gspread.authorize(credentials)
sh = gc.open(docName)
wks = sh.worksheet(sheetName)
#   User Input for Reddit/ Reddit information
login()
rThread = checkURL()


#   Recording program start time
strt = time.time()



##  FUNCTION DEFINITIONS



#   Function to find the bottom of the table of MPs
def findLastMP(wksColumn):
    wksCellList = wks.col_values(wksColumn)
    for wksCell in wksCellList:
        if wksCell == "Speaker":
            return wks.find(wksCell).row


#   Function to return full list of sitting MPs
def getMPs():
    col = getCol()
    wksMPs = wks.col_values(3)[2:findLastMP(4)-1]
    wksMPIsSitting = wks.col_values(col)[2:findLastMP(4)-1]
    for i in wksMPs:
        if wksMPIsSitting[wksMPs.index(i)] == 'N/A':
            del wksMPIsSitting[wksMPs.index(i)]
            wksMPs.remove(i)
    return wksMPs


#   Function to return votes from the division thread
def getVotes(url):
    #getting the list of comments
    rThread = r.get_submission(url)
    rThread.replace_more_comments(limit=None, threshold=0)
    rComments = praw.helpers.flatten_tree(rThread.comments)
    #returning the list of comments
    return rComments


#   Function to return left-most empty column into which the results are recorded
def getCol():
    cells = wks.range('F3:BZ3')
    for cell in cells:
        if cell.value == '':
            col = cell.col
            break
    return col


#   Function to determine which cells need updating
def getUpdateCells(MPs):
    col = getCol()
    updateList = wks.range(str(wks.get_addr_int(3, col)) + ":" + wks.get_addr_int(findLastMP(4)-1, col))
    wksMPIsSitting = wks.col_values(col)[2:findLastMP(4)-1]
    for i in updateList:
        if wksMPIsSitting[updateList.index(i)] == 'N/A':
            del wksMPIsSitting[updateList.index(i)]
            updateList.remove(i)
    return updateList


#   Function to count aye/nay/abs votes
def sumVotes(vote, votes):
    total = 0
    for i in votes:
        if i == vote:
            total += 1
    return total


#   Function to title column into which votes will be recorded
def titleCol():
    col = getCol()
    title = str(rThread.title())
    billNum = title.split("/")[-2]
    billNum = billNum.split("_")[0]
    print("You are counting " + billNum)
    wks.update_cell(2, col, "=HYPERLINK(\"" + rThread + "\", \"" + billNum + "\")")

##  END OF DECLARATION OF UTILITY FUNCTIONS - MAIN PROGRAM BELOW
#   Prepping spreadsheet
titleCol()

#   Compiling working lists
votes = getVotes(rThread)
gMPs = getMPs()
updateList = getUpdateCells(gMPs)
duplicateVotes = []
votesFinal = []


#   Counting Function
def countVote(gMP):
    #Checking for multiple votes
    voteCount = 0
    for i in votes:
        if str(i.author).lower() == gMP.lower():
            voteCount += 1
    #Handling more than one vote
    if voteCount > 1:
        return gMP, 'DNV', True
    #Handling no vote
    elif voteCount < 1:
        return gMP, 'DNV', False
    #Handling exactly one vote
    else:
        for i in votes:
            if str(i.author).lower() == gMP.lower():
                if 'aye' in str(i.body).lower():
                    return gMP, 'Aye', False
                elif 'nay' in str(i.body).lower():
                    return gMP, 'Nay', False
                elif 'abstain' in str(i.body).lower():
                    return gMP, 'Abs', False

print("The votes were as follows: ")


#   Initialisation of worker pool and asigning counting function and tasks to worker pool - no set worker cap means that the worker cap defaults to the number of CPU cores present
with concurrent.futures.ThreadPoolExecutor() as executor:
    for out in executor.map(countVote, gMPs):
        #Handling output from counting function
        MP, vote, isDupe = out
        if isDupe == False:
            print(MP + " : " + vote)
            if not vote == 'DNV':
                votesFinal.append(vote)
            
        else:
            print(MP + " voted more than once and recieved a DNV")
            duplicateVotes.append(MP)
        updateList[gMPs.index(MP)].value = vote

#   Updating spreadsheet 
wks.update_cells(updateList)

#   Counting total valid aye, nay and abs votes and turnout
print("The Ayes to the right: " + str(sumVotes('Aye', votesFinal)))
print("The Noes to the right: " + str(sumVotes('Nay', votesFinal)))
print("Abstentions: " + str(sumVotes('Abs', votesFinal)))
print(len(votesFinal), len(gMPs))
turnout = str((len(votesFinal)/totalMPs)*100)
print("Turnout: " + turnout + "%")
      

#   Recording end time
end = time.time()


#   Feeding back total runtime - Generally around 20 seconds
print("The count took " + str(end-strt) + " seconds")
