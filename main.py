import praw
import json
import os

global reddit
global settings

def loadSettings(): #TODO include more error-catching/user feedback here
    with open('config.json') as file:
        fileContent = file.read()
        return json.loads(fileContent)

def pullComments(): #Function to pull all the comments from the thread.
    countvotes(comments)

def countVotes(comments): #Function to seperate the votes into aye, nay, abst
    votes = {} #Format: {"strideynet": "Aye"}

    uploadVotes(votes)

def uploadVotes(votes): #Function to place the votes into the spreadsheet
    pass


#Main
settings = loadSettings() # Load settings for file

print('Config file read:')
print(settings)

reddit = praw.Reddit(client_id = settings['reddit']['client_id'],
                     client_secret = settings['reddit']['client_secret'],
                     password = settings['reddit']['password'],
                     username = settings['reddit']['username'],
                     user_agent = 'MHoC VoteCounter')

print('Reddit authentication complete. User showing as ' + str(reddit.user.me()))

print('Please ')