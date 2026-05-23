import pytest

from columbot.input_parse import parse_username


class TestParseUsername:
    def test_plain_username(self) -> None:
        assert parse_username("reflection3927") == "reflection3927"

    def test_u_prefix(self) -> None:
        assert parse_username("u/reflection3927") == "reflection3927"

    def test_slash_u_prefix(self) -> None:
        assert parse_username("/u/reflection3927") == "reflection3927"

    def test_full_user_url(self) -> None:
        url = "https://www.reddit.com/user/reflection3927"
        assert parse_username(url) == "reflection3927"

    def test_full_user_url_with_trailing_slash(self) -> None:
        url = "https://www.reddit.com/user/reflection3927/"
        assert parse_username(url) == "reflection3927"

    def test_old_reddit_url(self) -> None:
        url = "https://old.reddit.com/user/reflection3927"
        assert parse_username(url) == "reflection3927"

    def test_url_with_subpath(self) -> None:
        url = "https://www.reddit.com/user/reflection3927/comments"
        assert parse_username(url) == "reflection3927"

    def test_empty_string_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            parse_username("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            parse_username("   ")

    def test_strips_whitespace(self) -> None:
        assert parse_username("  reflection3927  ") == "reflection3927"

    def test_non_reddit_url_raises(self) -> None:
        with pytest.raises(ValueError, match="Reddit"):
            parse_username("https://twitter.com/someuser")
