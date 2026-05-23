# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Columbot is a Reddit bot-detection tool (named after Columbo the detective). It analyzes a Reddit user's behavioral signals via the PRAW API and produces a suspicion score with a verdict (Likely Human / Suspicious / Likely Bot).

## Architecture

```
columbot/                  # Python package
  __init__.py
  __main__.py              # CLI entry point (argparse)
  input_parse.py           # parse_username(raw) → username from URL/prefix/plain text
  collect.py               # fetch_signals(reddit, username) → UserSignals
  scoring.py               # score(signals) → SuspicionResult (7 heuristic rules)
  report.py                # format_report(result) → plain text report
  types.py                 # Frozen dataclasses: UserSignals, SuspicionResult
tests/                     # pytest test suite (51 tests)
  conftest.py              # Mock PRAW fixture factories
  test_input_parse.py
  test_collect.py
  test_scoring.py
  test_report.py
archive/                   # Original learning-exercise scripts (kept for reference)
```

## Bot Detection Signals

The tool collects these signals in a single pass over a user's last 1000 posts/comments:

1. **Account age vs activity** — New accounts with high activity volume
2. **Temporal patterns** — Regular posting cadence (robotic intervals), no sleep gaps
3. **Subreddit targeting** — Low subreddit diversity, heavy concentration in one sub
4. **Comment depth** — Broadcast pattern (mostly top-level comments, no back-and-forth)
5. **Comment similarity** — Near-duplicate comments via Jaccard similarity on word sets

## Running

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

python -m columbot <username_or_url>
python -m columbot reflection3927
python -m columbot https://www.reddit.com/user/reflection3927
python -m columbot --limit 500 someuser
```

## Testing

```bash
source .venv/bin/activate
pytest tests/ -v
ruff check columbot/ tests/
```

## Configuration

- `praw.ini` — Reddit API credentials (gitignored). Requires a `[bot1]` section with client_id, client_secret, username, password, user_agent.

## Future Directions

- Thread scanner: analyze all commenters in a thread, flag suspicious ones
- Web API / browser extension frontend
- Additional signals: response latency, edit rate, comment length consistency, cross-domain expertise, text analysis (sentiment, style)
