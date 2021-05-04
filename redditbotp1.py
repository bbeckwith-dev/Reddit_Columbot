#!/usr/bin/python
import suspecttest as s
import praw

reddit = praw.Reddit('bot1')

subreddit = reddit.subreddit("pythonforengineers")
#suspect = input("Give me a username to investigate: ")
suspect = reddit.redditor('reflection3927')

s.get_post_count(suspect)