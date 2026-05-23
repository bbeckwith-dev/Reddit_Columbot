from columbot.types import SuspicionResult


def format_report(result: SuspicionResult) -> str:
    lines = [
        f"=== Columbot Report: u/{result.username} ===",
        "",
        f"  Verdict: {result.verdict}",
        f"  Suspicion Score: {result.score}/1.0",
        "",
    ]

    _append_flags(lines, result)
    _append_account_summary(lines, result)
    _append_subreddit_breakdown(lines, result, "Post", result.signals.post_subreddits)
    _append_subreddit_breakdown(lines, result, "Comment", result.signals.comment_subreddits)
    _append_temporal(lines, result)
    _append_behavior(lines, result)

    lines.append("=" * len(lines[0]))
    return "\n".join(lines)


def _append_flags(lines: list, result: SuspicionResult) -> None:
    if not result.flags:
        lines.append("  No flags triggered.")
    else:
        lines.append("  Flags:")
        for flag in result.flags:
            lines.append(f"    - {flag}")
    lines.append("")


def _append_account_summary(lines: list, result: SuspicionResult) -> None:
    s = result.signals
    lines.append("  Account Summary:")
    lines.append(f"    Age: {s.account_age_days} days")
    lines.append(f"    Post Karma: {s.link_karma}")
    lines.append(f"    Comment Karma: {s.comment_karma}")
    lines.append(f"    Posts: {s.post_count} across {s.unique_post_subs} subreddits")
    lines.append(f"    Comments: {s.comment_count} across {s.unique_comment_subs} subreddits")
    lines.append("")


def _append_subreddit_breakdown(
    lines: list,
    result: SuspicionResult,
    label: str,
    subs: dict,
) -> None:
    if not subs:
        return
    sorted_subs = sorted(subs.items(), key=lambda x: x[1], reverse=True)
    top = sorted_subs[:5]
    lines.append(f"  Top {label} Subreddits:")
    for sub_name, count in top:
        lines.append(f"    r/{sub_name}: {count}")
    lines.append("")


def _append_temporal(lines: list, result: SuspicionResult) -> None:
    s = result.signals
    lines.append("  Temporal Patterns:")
    if s.avg_gap_seconds is not None:
        lines.append(f"    Avg gap between activity: {_format_duration(s.avg_gap_seconds)}")
    if s.gap_std_dev is not None:
        lines.append(f"    Gap std deviation: {_format_duration(s.gap_std_dev)}")
    if s.max_inactive_hours is not None:
        lines.append(f"    Longest inactive period: {s.max_inactive_hours:.1f} hours")
    lines.append("")


def _append_behavior(lines: list, result: SuspicionResult) -> None:
    s = result.signals
    lines.append("  Behavioral Signals:")
    lines.append(f"    Top-level comment ratio: {s.top_level_comment_ratio:.0%}")
    lines.append(f"    Near-duplicate comment pairs: {s.duplicate_comment_count}")
    lines.append(f"    Comments analyzed for similarity: {s.total_comments_compared}")
    lines.append("")


def _format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        return f"{seconds / 60:.1f}m"
    return f"{seconds / 3600:.1f}h"
