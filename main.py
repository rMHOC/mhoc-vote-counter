import praw
import json
import os

def loadSettings(): #TODO include more error-catching/user feedback here
    with open('config.json') as file:
        fileContent = file.read()
        return json.loads(fileContent)

def pullComments(): #Function to pull all the comments from the thread.
    pass


#Main
settings = loadSettings() # Load settings for file
print(settings)
reddit = praw.Reddit(client_id = settings['reddit']['client_id'],
                     client_secret = settings['reddit']['client_secret'],
                     password = settings['reddit']['password'],
                     username = settings['reddit']['username'],
                     user_agent = 'MHoC VoteCounter')

print(reddit.user.me())