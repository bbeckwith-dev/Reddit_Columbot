from typing import List

from columbot.types import SuspicionResult, UserSignals

_WEIGHT_NEW_ACTIVE = 0.15
_WEIGHT_REGULAR_CADENCE = 0.20
_WEIGHT_NO_SLEEP = 0.15
_WEIGHT_LOW_DIVERSITY = 0.10
_WEIGHT_CONCENTRATION = 0.10
_WEIGHT_BROADCAST = 0.10
_WEIGHT_DUPLICATE = 0.20


def score(signals: UserSignals) -> SuspicionResult:
    flags: List[str] = []
    total = 0.0

    total += _check_new_active(signals, flags)
    total += _check_regular_cadence(signals, flags)
    total += _check_no_sleep(signals, flags)
    total += _check_low_diversity(signals, flags)
    total += _check_concentration(signals, flags)
    total += _check_broadcast(signals, flags)
    total += _check_duplicate(signals, flags)

    capped = min(total, 1.0)
    verdict = _verdict_from_score(capped)

    return SuspicionResult(
        username=signals.username,
        score=round(capped, 2),
        verdict=verdict,
        flags=tuple(flags),
        signals=signals,
    )


def _verdict_from_score(s: float) -> str:
    if s < 0.3:
        return "Likely Human"
    if s <= 0.6:
        return "Suspicious"
    return "Likely Bot"


def _check_new_active(signals: UserSignals, flags: List[str]) -> float:
    activity = signals.post_count + signals.comment_count
    if signals.account_age_days < 90 and activity > 200:
        flags.append(f"New account with high activity ({activity} items in {signals.account_age_days} days)")
        return _WEIGHT_NEW_ACTIVE
    return 0.0


def _check_regular_cadence(signals: UserSignals, flags: List[str]) -> float:
    if signals.avg_gap_seconds is None or signals.gap_std_dev is None:
        return 0.0
    activity = signals.post_count + signals.comment_count
    if activity < 30:
        return 0.0
    if signals.gap_std_dev < 0.25 * signals.avg_gap_seconds:
        flags.append("Unusually regular posting intervals (robotic cadence)")
        return _WEIGHT_REGULAR_CADENCE
    return 0.0


def _check_no_sleep(signals: UserSignals, flags: List[str]) -> float:
    if signals.max_inactive_hours is None:
        return 0.0
    if signals.account_age_days < 7:
        return 0.0
    if signals.max_inactive_hours < 4.0:
        flags.append(f"No sleep gap detected (max inactive: {signals.max_inactive_hours:.1f}h)")
        return _WEIGHT_NO_SLEEP
    return 0.0


def _check_low_diversity(signals: UserSignals, flags: List[str]) -> float:
    if signals.post_count < 50:
        return 0.0
    if signals.unique_post_subs < 3:
        flags.append(f"Low subreddit diversity ({signals.unique_post_subs} subs for {signals.post_count} posts)")
        return _WEIGHT_LOW_DIVERSITY
    return 0.0


def _check_concentration(signals: UserSignals, flags: List[str]) -> float:
    if not signals.post_subreddits or signals.post_count < 10:
        return 0.0
    top_count = max(signals.post_subreddits.values())
    if top_count > 0.8 * signals.post_count:
        top_sub = max(signals.post_subreddits, key=signals.post_subreddits.get)  # type: ignore[arg-type]
        flags.append(f"Heavily concentrated in r/{top_sub} ({top_count}/{signals.post_count} posts)")
        return _WEIGHT_CONCENTRATION
    return 0.0


def _check_broadcast(signals: UserSignals, flags: List[str]) -> float:
    if signals.comment_count < 50:
        return 0.0
    if signals.top_level_comment_ratio > 0.95:
        pct = int(signals.top_level_comment_ratio * 100)
        flags.append(f"Broadcast pattern ({pct}% top-level comments, rarely replies)")
        return _WEIGHT_BROADCAST
    return 0.0


def _check_duplicate(signals: UserSignals, flags: List[str]) -> float:
    if signals.duplicate_comment_count >= 5:
        flags.append(f"Duplicate content detected ({signals.duplicate_comment_count} near-identical comment pairs)")
        return _WEIGHT_DUPLICATE
    return 0.0
