from unittest.mock import MagicMock


from columbot.collect import fetch_signals
from tests.conftest import make_mock_comment, make_mock_redditor, make_mock_submission


class TestFetchSignalsBasic:
    def test_empty_account(self) -> None:
        reddit = MagicMock()
        redditor = make_mock_redditor(name="emptyuser")
        reddit.redditor.return_value = redditor

        signals = fetch_signals(reddit, "emptyuser")

        assert signals.username == "emptyuser"
        assert signals.post_count == 0
        assert signals.comment_count == 0
        assert signals.unique_post_subs == 0
        assert signals.unique_comment_subs == 0
        assert signals.top_level_comment_ratio == 0.0
        assert signals.duplicate_comment_count == 0

    def test_counts_posts_and_comments(self) -> None:
        reddit = MagicMock()
        subs = [make_mock_submission("sub1", 1000.0 + i * 100) for i in range(5)]
        coms = [make_mock_comment("sub1", 2000.0 + i * 100) for i in range(10)]
        redditor = make_mock_redditor(submissions=subs, comments=coms)
        reddit.redditor.return_value = redditor

        signals = fetch_signals(reddit, "testuser")

        assert signals.post_count == 5
        assert signals.comment_count == 10

    def test_limit_parameter_passed(self) -> None:
        reddit = MagicMock()
        redditor = make_mock_redditor()
        reddit.redditor.return_value = redditor

        fetch_signals(reddit, "testuser", limit=50)

        redditor.submissions.new.assert_called_once_with(limit=50)
        redditor.comments.new.assert_called_once_with(limit=50)


class TestSubredditSignals:
    def test_subreddit_counts(self) -> None:
        reddit = MagicMock()
        subs = [
            make_mock_submission("python", 100.0),
            make_mock_submission("python", 200.0),
            make_mock_submission("golang", 300.0),
        ]
        coms = [
            make_mock_comment("python", 400.0),
            make_mock_comment("rust", 500.0),
        ]
        redditor = make_mock_redditor(submissions=subs, comments=coms)
        reddit.redditor.return_value = redditor

        signals = fetch_signals(reddit, "testuser")

        assert signals.post_subreddits == {"python": 2, "golang": 1}
        assert signals.comment_subreddits == {"python": 1, "rust": 1}
        assert signals.unique_post_subs == 2
        assert signals.unique_comment_subs == 2


class TestTemporalSignals:
    def test_gap_calculation(self) -> None:
        reddit = MagicMock()
        base = 1000000.0
        subs = [make_mock_submission("s", base + i * 3600) for i in range(5)]
        redditor = make_mock_redditor(submissions=subs)
        reddit.redditor.return_value = redditor

        signals = fetch_signals(reddit, "testuser")

        assert signals.avg_gap_seconds is not None
        assert abs(signals.avg_gap_seconds - 3600.0) < 1.0

    def test_no_gap_with_single_item(self) -> None:
        reddit = MagicMock()
        redditor = make_mock_redditor(
            submissions=[make_mock_submission("s", 1000.0)],
        )
        reddit.redditor.return_value = redditor

        signals = fetch_signals(reddit, "testuser")

        assert signals.avg_gap_seconds is None
        assert signals.gap_std_dev is None

    def test_hourly_distribution(self) -> None:
        reddit = MagicMock()
        noon_utc = 1000000.0 - (1000000.0 % 86400) + 12 * 3600
        subs = [make_mock_submission("s", noon_utc)]
        redditor = make_mock_redditor(submissions=subs)
        reddit.redditor.return_value = redditor

        signals = fetch_signals(reddit, "testuser")

        assert signals.hourly_distribution.get(12, 0) == 1

    def test_max_inactive_hours(self) -> None:
        reddit = MagicMock()
        base = 1000000.0
        subs = [
            make_mock_submission("s", base),
            make_mock_submission("s", base + 36000),
        ]
        redditor = make_mock_redditor(submissions=subs)
        reddit.redditor.return_value = redditor

        signals = fetch_signals(reddit, "testuser")

        assert signals.max_inactive_hours is not None
        assert abs(signals.max_inactive_hours - 10.0) < 0.1


class TestCommentDepth:
    def test_top_level_ratio(self) -> None:
        reddit = MagicMock()
        coms = [
            make_mock_comment(parent_id="t3_post1", created_utc=100.0),
            make_mock_comment(parent_id="t3_post2", created_utc=200.0),
            make_mock_comment(parent_id="t1_comment1", created_utc=300.0),
            make_mock_comment(parent_id="t3_post3", created_utc=400.0),
        ]
        redditor = make_mock_redditor(comments=coms)
        reddit.redditor.return_value = redditor

        signals = fetch_signals(reddit, "testuser")

        assert abs(signals.top_level_comment_ratio - 0.75) < 0.01


class TestCommentSimilarity:
    def test_detects_duplicates(self) -> None:
        reddit = MagicMock()
        coms = [
            make_mock_comment(body="this is a great post thanks for sharing", created_utc=float(i * 100))
            for i in range(10)
        ]
        redditor = make_mock_redditor(comments=coms)
        reddit.redditor.return_value = redditor

        signals = fetch_signals(reddit, "testuser")

        assert signals.duplicate_comment_count > 0

    def test_no_duplicates_with_unique_comments(self) -> None:
        reddit = MagicMock()
        diverse_bodies = [
            "python decorators are incredibly useful for metaprogramming",
            "the weather forecast says rain tomorrow afternoon",
            "just finished reading dune for the third time absolutely loved it",
            "my cat knocked over the plant again what a menace",
            "comparing postgresql and mysql for our backend migration project",
            "started learning guitar last month finding barre chords difficult",
            "the stock market rally surprised everyone on wall street today",
            "hiking trail near mount rainier was breathtaking and serene",
            "cooking risotto requires constant stirring and good broth quality",
            "quantum computing breakthroughs at google seem very promising overall",
        ]
        coms = [
            make_mock_comment(body=b, created_utc=float(i * 100))
            for i, b in enumerate(diverse_bodies)
        ]
        redditor = make_mock_redditor(comments=coms)
        reddit.redditor.return_value = redditor

        signals = fetch_signals(reddit, "testuser")

        assert signals.duplicate_comment_count == 0
