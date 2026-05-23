import math
import re
import time
from collections import Counter
from datetime import datetime, timezone
from typing import List, Optional, Set, Tuple

import praw

from columbot.types import UserSignals

_MAX_SIMILARITY_COMMENTS = 100
_JACCARD_THRESHOLD = 0.8
_WORD_PATTERN = re.compile(r"[a-z]+")


def fetch_signals(
    reddit: praw.Reddit,
    username: str,
    *,
    limit: int = 1000,
) -> UserSignals:
    redditor = reddit.redditor(username)
    account_age_days = _account_age_days(redditor.created_utc)

    posts, post_timestamps = _collect_posts(redditor, limit)
    comments, comment_data = _collect_comments(redditor, limit)

    all_timestamps = sorted(post_timestamps + [c[0] for c in comment_data])
    avg_gap, gap_std, max_inactive = _compute_temporal(all_timestamps)
    hourly = _compute_hourly(all_timestamps)

    comment_bodies = [c[1] for c in comment_data]
    parent_ids = [c[2] for c in comment_data]

    return UserSignals(
        username=redditor.name,
        account_age_days=account_age_days,
        link_karma=redditor.link_karma,
        comment_karma=redditor.comment_karma,
        post_count=len(post_timestamps),
        comment_count=len(comment_data),
        post_subreddits=dict(posts),
        comment_subreddits=dict(comments),
        unique_post_subs=len(posts),
        unique_comment_subs=len(comments),
        hourly_distribution=dict(hourly),
        avg_gap_seconds=avg_gap,
        gap_std_dev=gap_std,
        max_inactive_hours=max_inactive,
        top_level_comment_ratio=_top_level_ratio(parent_ids),
        duplicate_comment_count=_count_duplicates(comment_bodies),
        total_comments_compared=min(len(comment_bodies), _MAX_SIMILARITY_COMMENTS),
    )


def _account_age_days(created_utc: float) -> int:
    return int((time.time() - created_utc) / 86400)


def _collect_posts(
    redditor: object,
    limit: int,
) -> Tuple[Counter, List[float]]:
    sub_counts: Counter = Counter()
    timestamps: List[float] = []
    for submission in redditor.submissions.new(limit=limit):  # type: ignore[union-attr]
        sub_counts[submission.subreddit.display_name] += 1
        timestamps.append(submission.created_utc)
    return sub_counts, timestamps


def _collect_comments(
    redditor: object,
    limit: int,
) -> Tuple[Counter, List[Tuple[float, str, str]]]:
    sub_counts: Counter = Counter()
    data: List[Tuple[float, str, str]] = []
    for comment in redditor.comments.new(limit=limit):  # type: ignore[union-attr]
        sub_counts[comment.subreddit.display_name] += 1
        data.append((comment.created_utc, comment.body, comment.parent_id))
    return sub_counts, data


def _compute_temporal(
    sorted_timestamps: List[float],
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    if len(sorted_timestamps) < 2:
        return None, None, None

    gaps = [
        sorted_timestamps[i + 1] - sorted_timestamps[i]
        for i in range(len(sorted_timestamps) - 1)
    ]

    avg_gap = sum(gaps) / len(gaps)
    variance = sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)
    std_dev = math.sqrt(variance)
    max_gap_hours = max(gaps) / 3600.0

    return avg_gap, std_dev, max_gap_hours


def _compute_hourly(timestamps: List[float]) -> Counter:
    hourly: Counter = Counter()
    for ts in timestamps:
        hour = datetime.fromtimestamp(ts, tz=timezone.utc).hour
        hourly[hour] += 1
    return hourly


def _top_level_ratio(parent_ids: List[str]) -> float:
    if not parent_ids:
        return 0.0
    top_level = sum(1 for pid in parent_ids if pid.startswith("t3_"))
    return top_level / len(parent_ids)


def _tokenize(text: str) -> Set[str]:
    return set(_WORD_PATTERN.findall(text.lower()))


def _count_duplicates(bodies: List[str]) -> int:
    sample = bodies[:_MAX_SIMILARITY_COMMENTS]
    if len(sample) < 2:
        return 0

    token_sets = [_tokenize(b) for b in sample]
    count = 0
    max_pairs = len(sample) * (len(sample) - 1) // 2
    pair_limit = min(max_pairs, 5000)
    checked = 0

    for i in range(len(token_sets)):
        if checked >= pair_limit:
            break
        for j in range(i + 1, len(token_sets)):
            if checked >= pair_limit:
                break
            checked += 1
            if not token_sets[i] or not token_sets[j]:
                continue
            intersection = len(token_sets[i] & token_sets[j])
            union = len(token_sets[i] | token_sets[j])
            if intersection / union >= _JACCARD_THRESHOLD:
                count += 1

    return count
