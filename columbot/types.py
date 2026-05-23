from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class UserSignals:
    username: str
    account_age_days: int
    link_karma: int
    comment_karma: int
    post_count: int
    comment_count: int
    post_subreddits: Dict[str, int]
    comment_subreddits: Dict[str, int]
    unique_post_subs: int
    unique_comment_subs: int
    hourly_distribution: Dict[int, int]
    avg_gap_seconds: Optional[float]
    gap_std_dev: Optional[float]
    max_inactive_hours: Optional[float]
    top_level_comment_ratio: float
    duplicate_comment_count: int
    total_comments_compared: int


@dataclass(frozen=True)
class SuspicionResult:
    username: str
    score: float
    verdict: str
    flags: Tuple[str, ...]
    signals: UserSignals
