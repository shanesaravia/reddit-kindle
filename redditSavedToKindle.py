import sys
sys.path.append('c:/scripts/')

import os
import userCred
import praw
from praw.models import Submission
import os
import time
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


user = userCred.reddit['user']
password = userCred.reddit['pass']
client_id = userCred.reddit['client_id']
client_secret = userCred.reddit['client_secret']
directory = 'C:/Users/alex/Desktop/savedLinks/txt/'
outputDirectory = 'C:/Users/alex/Desktop/savedLinks/mobi/'

class RedditSaved():

    def credentials():
        """
        Return reddit instance using credentials.
        """
        user_agent = 'python:SavedtoKindle:v1 (by /u/roflquarium)'

        reddit = praw.Reddit(client_id=client_id,
                             client_secret=client_secret,
                             user_agent=user_agent,
                             username=user,
                             password=password)
        return reddit

    def saved(user):
        """
        Return saved links (not saved comments) for specified user.
        """
        redditor = reddit.redditor(user)
        saved = redditor.saved()
        links = []
        comments = []
        # Seperate links from comments, ignore comments for now
        for item in saved:
            if isinstance(item, Submission):
                links.append(item)
                #item.unsave()
            else:
                # It's a comment, do comment stuff
                comments.append(item)
        # Only return 'self' links, no link to outside of Reddit.
        self_links = [item for item in links if item.is_self]
        return self_links

    def unsave(item):
        """
        Unsave saved link.
        """
        item.unsave()

    def post(link, count):
        """
        Return all post details for given Reddit identifier.
        link = reddit identifier
        count = number of comments to show
        """
        submission = reddit.submission(id=link)
        # Retrieve post.
        title = submission.title
        author = submission.author
        subreddit = submission.subreddit_name_prefixed
        text = submission.selftext

        # Retrive comments.
        submission.comments.replace_more(limit=0) # required
        comments = [comment for comment in submission.comments[0:count]]

        return title, author, subreddit, text, comments

def textWrite(title, author, subreddit, text, comments, filename):
    """
    Write post/comments to text file
    TODO
    DONE still getting some encoding errors, used utf8
    DONE this script should only print, not do PRAW functions
    DONE seperate out self posts
    """
    with open(directory + filename, "w", encoding="utf8") as text_file:
        text_file.write('#Title:  ')
        text_file.write(title)
        text_file.write('\n\n')
        text_file.write('##Author:  ')
        text_file.write(str(author))
        text_file.write('\n\n')
        text_file.write('##Subreddit:  ')
        text_file.write(subreddit)
        text_file.write('\n\n')
        text_file.write('##Post\n')
        text_file.write(text)
        text_file.write('\n\n')

        for comment in comments:
            text_file.write('###Comment\n')
            text_file.write(comment.body)
            text_file.write('\n\n')
            for reply in comment.replies[0:1]:
                text_file.write('###Reply\n')
                text_file.write(reply.body)
                text_file.write('\n\n')


def convert(filename, title, author):
    """
    Convert text file to '.mobi'.
    """
    outputFilename = os.path.splitext(filename)[0]+'.mobi'
    #for filename in os.listdir(directory):
    #    if filename.endswith('.txt'):
        # print(os.path.join(directory, filename))
    #        print(filename)

    os.system('ebook-convert {} {} --authors "{}" --title "{}"'.format(directory + filename, outputDirectory + outputFilename, author, title))


def emailToKindle(filename):
    """
    Email .mobi file to kindle email. Email must be on approved list.
    """
    fromaddr = userCred.reddit['email']
    toaddr = userCred.reddit['kindleEmail']

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'Reddit Saved'
    body = "Attached ebook."

    msg.attach(MIMEText(body))


    with open(outputDirectory + filename, "rb") as file:
    #fp = open(outputDirectory + filename, 'rb')
        part = MIMEApplication(file.read(),Name=basename(filename))
        part['Content-Disposition'] = 'attachment; filename={}'.format(basename(filename))
    #fp.close()
    msg.attach(part)
    """
    with open(outputDirectory + file, "rb") as fil:
        part = MIMEApplication(fil.read(),Name=basename(file))
        part['Content-Disposition'] = 'attachment; filename={}'.format(basename(file))
    msg.attach(part)
    """
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, userCred.reddit['emailpass'])
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
"""
reddit = RedditSaved.credentials()
links = RedditSaved.saved(user)

for filenumber, link in enumerate(links):
    try:
        title, author, subreddit, text, comments = RedditSaved.post(link, 3)
        # Write each post to text file.
        filename = 'Post_{:02d}.txt'.format(filenumber)
        filenameOut = 'Post_{:02d}.mobi'.format(filenumber)
        #textWrite(title, author, subreddit, text, comments, filename)
        #convert(filename, title, author)
        emailToKindle(filenameOut)
        #RedditSaved.unsave(link)
    except:
        print('Skipped.')
"""

def emailToKindle2():
    """
    Email .mobi file to kindle email. Email must be on approved list.
    """
    fromaddr = userCred.reddit['email']
    toaddr = userCred.reddit['kindleEmail']
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'Reddit Saved'
    body = "Attached ebook."

    msg.attach(MIMEText(body))

    for filename in os.listdir(outputDirectory):
        with open(outputDirectory + filename, "rb") as file:
        #fp = open(outputDirectory + filename, 'rb')
            part = MIMEApplication(file.read(),Name=basename(filename))
            part['Content-Disposition'] = 'attachment; filename={}'.format(basename(filename))
        #fp.close()
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, userCred.reddit['emailpass'])
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

emailToKindle2()
