from columbot.report import format_report
from columbot.types import SuspicionResult, UserSignals


def _make_result(
    score: float = 0.65,
    verdict: str = "Likely Bot",
    flags: tuple = ("Flag one", "Flag two"),
) -> SuspicionResult:
    signals = UserSignals(
        username="botuser",
        account_age_days=30,
        link_karma=500,
        comment_karma=100,
        post_count=200,
        comment_count=300,
        post_subreddits={"sub1": 150, "sub2": 30, "sub3": 20},
        comment_subreddits={"sub1": 200, "sub2": 80, "sub3": 20},
        unique_post_subs=3,
        unique_comment_subs=3,
        hourly_distribution={h: 20 for h in range(24)},
        avg_gap_seconds=120.0,
        gap_std_dev=15.0,
        max_inactive_hours=2.5,
        top_level_comment_ratio=0.95,
        duplicate_comment_count=8,
        total_comments_compared=100,
    )
    return SuspicionResult(
        username="botuser",
        score=score,
        verdict=verdict,
        flags=flags,
        signals=signals,
    )


class TestFormatReport:
    def test_contains_verdict(self) -> None:
        report = format_report(_make_result())
        assert "Likely Bot" in report

    def test_contains_score(self) -> None:
        report = format_report(_make_result())
        assert "0.65" in report

    def test_contains_username(self) -> None:
        report = format_report(_make_result())
        assert "botuser" in report

    def test_contains_flags(self) -> None:
        report = format_report(_make_result(flags=("Suspicious flag here",)))
        assert "Suspicious flag here" in report

    def test_contains_account_age(self) -> None:
        report = format_report(_make_result())
        assert "30" in report

    def test_contains_karma(self) -> None:
        report = format_report(_make_result())
        assert "500" in report

    def test_contains_post_count(self) -> None:
        report = format_report(_make_result())
        assert "200" in report

    def test_contains_top_subreddits(self) -> None:
        report = format_report(_make_result())
        assert "sub1" in report

    def test_no_flags_section_when_empty(self) -> None:
        report = format_report(_make_result(flags=()))
        assert "No flags" in report or "flag" not in report.lower().split("verdict")[0]
