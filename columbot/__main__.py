import argparse
import sys

import praw

from columbot.collect import fetch_signals
from columbot.input_parse import parse_username
from columbot.report import format_report
from columbot.scoring import score


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="columbot",
        description="Analyze a Reddit user's activity for bot-like behavior",
    )
    parser.add_argument(
        "target",
        help="Reddit username, u/username, or full Reddit user URL",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Max posts/comments to analyze (default: 1000)",
    )
    args = parser.parse_args()

    try:
        username = parse_username(args.target)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Investigating u/{username}...")

    try:
        reddit = praw.Reddit("bot1")
        signals = fetch_signals(reddit, username, limit=args.limit)
        result = score(signals)
        print(format_report(result))
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
