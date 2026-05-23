# Columbot

A Reddit bot-detection tool that analyzes a user's behavioral signals and produces a suspicion verdict. Named after Columbo the detective.

## What it does

Give Columbot a Reddit username or profile URL. It pulls the user's recent activity via the Reddit API and checks for patterns common in bot accounts:

- **Account age vs activity** — New accounts with unusually high output
- **Posting cadence** — Suspiciously regular intervals between posts (robotic timing)
- **Sleep patterns** — 24/7 activity with no inactive gaps
- **Subreddit targeting** — All activity concentrated in very few subreddits
- **Comment depth** — Only top-level comments, never engaging in back-and-forth
- **Content similarity** — Near-duplicate comments posted across different threads

Each signal is weighted and combined into a score from 0.0 to 1.0, with a verdict of **Likely Human**, **Suspicious**, or **Likely Bot**.

## Setup

Requires Python 3.9+ and Reddit API credentials.

```bash
git clone https://github.com/bbeckwith-dev/Reddit_Columbot.git
cd Reddit_Columbot
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Create a `praw.ini` file in the project root with your Reddit API credentials:

```ini
[bot1]
client_id=YOUR_CLIENT_ID
client_secret=YOUR_CLIENT_SECRET
username=YOUR_USERNAME
password=YOUR_PASSWORD
user_agent=columbot/0.1.0
```

You can get API credentials at https://www.reddit.com/prefs/apps/ by creating a "script" type application.

## Usage

```bash
# By username
python -m columbot someuser123

# By URL
python -m columbot https://www.reddit.com/user/someuser123

# With u/ prefix
python -m columbot u/someuser123

# Limit how many posts/comments to analyze (default: 1000)
python -m columbot --limit 500 someuser123
```

## Example output

```
=== Columbot Report: u/someuser ===

  Verdict: Suspicious
  Suspicion Score: 0.30/1.0

  Flags:
    - Low subreddit diversity (2 subs for 55 posts)
    - Heavily concentrated in r/AskReddit (48/55 posts)
    - Broadcast pattern (98% top-level comments, rarely replies)

  Account Summary:
    Age: 120 days
    Post Karma: 3200
    Comment Karma: 890
    Posts: 55 across 2 subreddits
    Comments: 60 across 3 subreddits

  Top Post Subreddits:
    r/AskReddit: 48
    r/pics: 7

  Temporal Patterns:
    Avg gap between activity: 2.5h
    Gap std deviation: 3.1h
    Longest inactive period: 7.2 hours

  Behavioral Signals:
    Top-level comment ratio: 98%
    Near-duplicate comment pairs: 1
    Comments analyzed for similarity: 60

=======================================
```

## Testing

```bash
source .venv/bin/activate
pytest tests/ -v        # 51 tests, all mocked (no Reddit API needed)
ruff check columbot/    # lint
```

## Limitations

- Reddit's API only returns the most recent ~1000 posts and comments per user. Older activity or deleted content is invisible.
- Low-activity accounts may not have enough data for heuristics to trigger, resulting in a default "Likely Human" verdict.
- These heuristics catch behavioral patterns, not AI-generated text. A sophisticated bot that mimics human posting rhythms could score low.

## License

MIT
