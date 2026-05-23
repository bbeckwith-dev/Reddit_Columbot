
from columbot.scoring import score
from columbot.types import UserSignals


def _make_signals(**overrides: object) -> UserSignals:
    defaults = dict(
        username="testuser",
        account_age_days=365,
        link_karma=1000,
        comment_karma=1000,
        post_count=50,
        comment_count=100,
        post_subreddits={"sub1": 20, "sub2": 15, "sub3": 10, "sub4": 5},
        comment_subreddits={"sub1": 40, "sub2": 30, "sub3": 20, "sub4": 10},
        unique_post_subs=4,
        unique_comment_subs=4,
        hourly_distribution={h: 5 for h in range(24)},
        avg_gap_seconds=3600.0,
        gap_std_dev=1800.0,
        max_inactive_hours=8.0,
        top_level_comment_ratio=0.5,
        duplicate_comment_count=0,
        total_comments_compared=100,
    )
    defaults.update(overrides)
    return UserSignals(**defaults)


class TestScoreVerdict:
    def test_normal_user_likely_human(self) -> None:
        result = score(_make_signals())
        assert result.verdict == "Likely Human"
        assert result.score < 0.3

    def test_score_capped_at_one(self) -> None:
        signals = _make_signals(
            account_age_days=10,
            post_count=300,
            comment_count=300,
            post_subreddits={"sub1": 300},
            unique_post_subs=1,
            avg_gap_seconds=100.0,
            gap_std_dev=5.0,
            max_inactive_hours=2.0,
            top_level_comment_ratio=0.99,
            duplicate_comment_count=10,
        )
        result = score(signals)
        assert result.score <= 1.0


class TestNewPlusActive:
    def test_fires_when_new_and_active(self) -> None:
        result = score(_make_signals(account_age_days=30, post_count=100, comment_count=150))
        assert any("New account" in f for f in result.flags)

    def test_does_not_fire_for_old_account(self) -> None:
        result = score(_make_signals(account_age_days=365, post_count=100, comment_count=150))
        assert not any("New account" in f for f in result.flags)

    def test_does_not_fire_for_low_activity(self) -> None:
        result = score(_make_signals(account_age_days=30, post_count=5, comment_count=10))
        assert not any("New account" in f for f in result.flags)


class TestRegularCadence:
    def test_fires_when_robotic_regularity(self) -> None:
        result = score(_make_signals(avg_gap_seconds=100.0, gap_std_dev=10.0, post_count=20, comment_count=20))
        assert any("regular" in f.lower() for f in result.flags)

    def test_does_not_fire_with_human_variance(self) -> None:
        result = score(_make_signals(avg_gap_seconds=100.0, gap_std_dev=80.0))
        assert not any("regular" in f.lower() for f in result.flags)

    def test_does_not_fire_with_no_gap_data(self) -> None:
        result = score(_make_signals(avg_gap_seconds=None, gap_std_dev=None))
        assert not any("regular" in f.lower() for f in result.flags)


class TestNoSleep:
    def test_fires_when_no_sleep_gap(self) -> None:
        result = score(_make_signals(max_inactive_hours=2.0, account_age_days=10))
        assert any("sleep" in f.lower() for f in result.flags)

    def test_does_not_fire_with_normal_sleep(self) -> None:
        result = score(_make_signals(max_inactive_hours=8.0))
        assert not any("sleep" in f.lower() for f in result.flags)

    def test_does_not_fire_with_no_data(self) -> None:
        result = score(_make_signals(max_inactive_hours=None))
        assert not any("sleep" in f.lower() for f in result.flags)


class TestLowDiversity:
    def test_fires_with_few_subs_many_posts(self) -> None:
        result = score(_make_signals(
            post_subreddits={"sub1": 40, "sub2": 15},
            unique_post_subs=2,
            post_count=55,
        ))
        assert any("diversity" in f.lower() for f in result.flags)

    def test_does_not_fire_with_many_subs(self) -> None:
        result = score(_make_signals(unique_post_subs=10, post_count=55))
        assert not any("diversity" in f.lower() for f in result.flags)


class TestConcentration:
    def test_fires_when_one_sub_dominates(self) -> None:
        result = score(_make_signals(
            post_subreddits={"sub1": 90, "sub2": 5, "sub3": 5},
            post_count=100,
        ))
        assert any("concentrated" in f.lower() for f in result.flags)

    def test_does_not_fire_with_spread(self) -> None:
        result = score(_make_signals(
            post_subreddits={"sub1": 30, "sub2": 25, "sub3": 25, "sub4": 20},
            post_count=100,
        ))
        assert not any("concentrated" in f.lower() for f in result.flags)


class TestBroadcast:
    def test_fires_with_mostly_top_level(self) -> None:
        result = score(_make_signals(top_level_comment_ratio=0.98, comment_count=60))
        assert any("broadcast" in f.lower() for f in result.flags)

    def test_does_not_fire_with_replies(self) -> None:
        result = score(_make_signals(top_level_comment_ratio=0.5, comment_count=60))
        assert not any("broadcast" in f.lower() for f in result.flags)


class TestDuplicateContent:
    def test_fires_with_many_duplicates(self) -> None:
        result = score(_make_signals(duplicate_comment_count=8))
        assert any("duplicate" in f.lower() for f in result.flags)

    def test_does_not_fire_with_few_duplicates(self) -> None:
        result = score(_make_signals(duplicate_comment_count=2))
        assert not any("duplicate" in f.lower() for f in result.flags)


class TestVerdictThresholds:
    def test_suspicious_range(self) -> None:
        signals = _make_signals(
            post_subreddits={"sub1": 90, "sub2": 5, "sub3": 5},
            post_count=100,
            unique_post_subs=2,
            top_level_comment_ratio=0.98,
            comment_count=60,
        )
        result = score(signals)
        assert result.verdict == "Suspicious"
        assert 0.3 <= result.score <= 0.6
