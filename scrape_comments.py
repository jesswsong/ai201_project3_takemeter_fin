"""
Scrape YouTube comments for TakeMeter dataset.

Video: BLACKPINK - "DDU-DU DDU-DU" M/V
URL:   https://www.youtube.com/watch?v=IHNzOHi8sJs

No API key required — uses youtube-comment-downloader.

Usage:
    python3 scrape_comments.py

Output:
    raw_comments.csv  — all scraped comments (text, votes, reply_count)
"""

import csv
import re
import sys
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR

VIDEO_ID = "IHNzOHi8sJs"  # BLACKPINK DDU-DU DDU-DU
TARGET = 600               # scrape more than needed so filtering leaves ~200+
MIN_CHARS = 15             # drop extremely short comments (emoji-only, etc.)
MAX_CHARS = 500            # drop walls of text unlikely to be clean examples
OUT_RAW = "raw_comments.csv"


def is_spam_or_unusable(text: str) -> bool:
    """Heuristic pre-filter — remove obvious junk before manual labeling."""
    t = text.strip()
    # pure emoji / punctuation runs
    if re.fullmatch(r"[\U00010000-\U0010ffff\s!?.♥❤️💕🔥✨]+", t):
        return True
    # "first" bots
    if re.fullmatch(r"(first|1st)[!.?]*", t, re.IGNORECASE):
        return True
    # timestamp spam (links or bare digits)
    if re.search(r"https?://", t):
        return True
    return False


def scrape(video_id: str, limit: int) -> list[dict]:
    downloader = YoutubeCommentDownloader()
    comments = []
    print(f"Scraping up to {limit} comments from video {video_id}...")

    for item in downloader.get_comments_from_url(
        f"https://www.youtube.com/watch?v={video_id}",
        sort_by=SORT_BY_POPULAR,
    ):
        text = item.get("text", "").strip()
        if len(text) < MIN_CHARS or len(text) > MAX_CHARS:
            continue
        if is_spam_or_unusable(text):
            continue
        comments.append({
            "text": text,
            "votes": item.get("votes", 0),
            "reply_count": item.get("reply_count", 0),
        })
        if len(comments) % 50 == 0:
            print(f"  collected {len(comments)} comments...")
        if len(comments) >= limit:
            break

    print(f"Done. {len(comments)} comments collected.")
    return comments


def save(comments: list[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "votes", "reply_count"])
        writer.writeheader()
        writer.writerows(comments)
    print(f"Saved to {path}")


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else TARGET
    comments = scrape(VIDEO_ID, limit)
    if not comments:
        print("No comments retrieved — check your internet connection.")
        sys.exit(1)
    save(comments, OUT_RAW)
    print(
        f"\nNext step: open raw_comments.csv and add a 'label' column.\n"
        f"Add a 'notes' column for borderline cases.\n"
        f"Save the labeled file as dataset.csv for the Colab notebook."
    )
