import time
from typing import List, Optional
from unittest.mock import MagicMock



def make_mock_submission(
    subreddit_name: str = "testsub",
    created_utc: float = 0.0,
) -> MagicMock:
    sub = MagicMock()
    sub.subreddit.display_name = subreddit_name
    sub.created_utc = created_utc
    return sub


def make_mock_comment(
    subreddit_name: str = "testsub",
    created_utc: float = 0.0,
    body: str = "test comment",
    parent_id: str = "t3_abc123",
    edited: bool = False,
) -> MagicMock:
    comment = MagicMock()
    comment.subreddit.display_name = subreddit_name
    comment.created_utc = created_utc
    comment.body = body
    comment.parent_id = parent_id
    comment.edited = edited
    return comment


def make_mock_redditor(
    name: str = "testuser",
    created_utc: Optional[float] = None,
    link_karma: int = 100,
    comment_karma: int = 200,
    has_verified_email: bool = True,
    submissions: Optional[List[MagicMock]] = None,
    comments: Optional[List[MagicMock]] = None,
) -> MagicMock:
    if created_utc is None:
        created_utc = time.time() - (365 * 86400)

    redditor = MagicMock()
    redditor.name = name
    redditor.created_utc = created_utc
    redditor.link_karma = link_karma
    redditor.comment_karma = comment_karma
    redditor.has_verified_email = has_verified_email

    subs = submissions if submissions is not None else []
    coms = comments if comments is not None else []

    redditor.submissions.new.return_value = iter(subs)
    redditor.comments.new.return_value = iter(coms)

    return redditor
