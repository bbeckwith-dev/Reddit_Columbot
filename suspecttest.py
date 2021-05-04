#!/usr/bin/env python3
from collections import Counter
import praw
reddit = praw.Reddit('bot1')

suspect = reddit.redditor('reflection3927')

def get_post_count(suspect):
    """GET NUMBER OF SUBMISSIONS/POSTS (postcounter)"""
    postcounter = 0
    submissions = suspect.submissions.new(limit=25)
    for submission in submissions:
        postcounter += 1
    print(f"Number of posts: {postcounter}")