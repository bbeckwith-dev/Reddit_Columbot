#!/usr/bin/env python3
from collections import Counter
import praw
reddit = praw.Reddit('bot1')

#GET USERNAME TO INVESTIGATE (i.e. uname3i) AND CREATE suspect INSTANCE
#uname2i = input("Give me a username to investigate: ")
#suspect = reddit.redditor(uname2i)

#testing
suspect = reddit.redditor('reflection3927')

def get_post_count(suspect):
    """GET NUMBER OF SUBMISSIONS/POSTS (postcounter)"""
    postcounter = 0
    submissions = suspect.submissions.new(limit=None)
    for submission in submissions:
        postcounter += 1
    print(f"Number of posts: {postcounter}")

#GET SUSPECT POST SUBREDDIT (suspostsubreds) COUNTS
suspostsubreds = []
for submission in suspect.submissions.new(limit=None):
    suspostsubreds.append(submission.subreddit.display_name)
post_subreds = Counter(suspostsubreds)

#GET NUMBER OF COMMENTS (commentcounter)
commentcounter = 0
for comment in suspect.comments.new(limit=None):
    commentcounter += 1

#GET SUSPECT COMMENT SUBREDDIT (suscomsubreds) COUNTS
suscomsubreds = []
for comment in suspect.comments.new(limit=None):
    suscomsubreds.append(comment.subreddit.display_name)
com_subreds = Counter(suscomsubreds)
#top5subreds = counted_subreds.most_common(5)

#feedback
#print(f'suscomsubreds: {suscomsubreds}')
#print(f'countedsubreds: {counted_subreds}')
#print(f'top5subreds: {top5subreds}')

#PRINT RESULTS
#PRINT POST AND COMMENT KARMA
print(f"{suspect} has {suspect.link_karma} post karma.")
print(f"{suspect} has {suspect.comment_karma} comment karma.")

print(f"{suspect} has {postcounter} post submissions in {len(post_subreds)}\
 unique subreddits. Five most posted-in subs:")
for subreddit, count in post_subreds.most_common(5):
    print(f"{subreddit}: {count} posts")

print(f"{suspect} has {commentcounter} comments in {len(com_subreds)}\
 unique subreddits. Five most commented subs:")
for subreddit, count in com_subreds.most_common(5):
    print(f"{subreddit}: {count} comments")