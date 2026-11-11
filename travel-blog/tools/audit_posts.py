#!/usr/bin/env python3
"""Audit travel blog posts on a WordPress site for booking and fare details.

goAISEO publishes articles automatically. This script reads the site's public
WordPress REST API and flags posts that are missing the details that set this
blog apart from YouTube videos: how to book tickets, fares, a budget breakdown,
and a recent "fares checked" date.

Usage:
    python3 audit_posts.py https://yourdomain.com
    python3 audit_posts.py https://yourdomain.com --max-posts 50 --csv report.csv

Only the Python standard library is needed. No login is required because it
reads published posts only.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone

USER_AGENT = "travel-blog-audit/1.0"

# Fares older than this are treated as stale and should be re-checked.
STALE_FARE_DAYS = 90

CURRENCY_RE = re.compile(
    r"(₹|\$|€|£|¥|\bRs\.?\s?\d|\bINR\b|\bUSD\b|\bEUR\b|\bGBP\b|\bAED\b|\bTHB\b|\bSGD\b)",
    re.IGNORECASE,
)
BOOKING_RE = re.compile(
    r"\b(how to book|book(ing)? (your )?tickets?|ticket booking|book online|"
    r"booking steps|where to book|IRCTC|redBus|MakeMyTrip|Skyscanner|"
    r"official (website|site)|counter)\b",
    re.IGNORECASE,
)
FARE_RE = re.compile(
    r"\b(fare|ticket price|ticket cost|entry fee|entrance fee|price|cost)s?\b",
    re.IGNORECASE,
)
BUDGET_RE = re.compile(
    r"\b(budget|total cost|cost breakdown|per person|trip cost|expenses?)\b",
    re.IGNORECASE,
)
FARES_CHECKED_RE = re.compile(
    r"(fares?|prices?)\s+(last\s+)?(checked|verified|updated)\s*(on|:)?\s*"
    r"(?P<date>\d{1,2}\s+\w+\s+\d{4}|\w+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2})",
    re.IGNORECASE,
)
DATE_FORMATS = ("%d %B %Y", "%d %b %Y", "%B %d %Y", "%b %d %Y", "%Y-%m-%d")
AI_LEFTOVER_RE = re.compile(
    r"(as an ai|i cannot browse|\[insert|\{\{|lorem ipsum|TODO|"
    r"as of my (last )?(knowledge|training))",
    re.IGNORECASE,
)


@dataclass
class PostReport:
    post_id: int
    title: str
    link: str
    modified: str
    words: int
    problems: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "OK" if not self.problems else "NEEDS WORK"


def fetch_json(url: str) -> tuple[object, dict[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        headers = {k.lower(): v for k, v in resp.headers.items()}
        return json.loads(resp.read().decode("utf-8")), headers


def fetch_posts(site: str, max_posts: int) -> list[dict]:
    posts: list[dict] = []
    page = 1
    per_page = min(100, max_posts)
    while len(posts) < max_posts:
        query = urllib.parse.urlencode(
            {"per_page": per_page, "page": page, "_embed": "wp:featuredmedia"}
        )
        url = f"{site}/wp-json/wp/v2/posts?{query}"
        try:
            batch, headers = fetch_json(url)
        except urllib.error.HTTPError as err:
            # WordPress answers 400 when the page number runs past the end.
            if err.code == 400 and page > 1:
                break
            raise
        if not isinstance(batch, list) or not batch:
            break
        posts.extend(batch)
        total_pages = int(headers.get("x-wp-totalpages", page))
        if page >= total_pages:
            break
        page += 1
    return posts[:max_posts]


def strip_tags(markup: str) -> str:
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", markup, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def parse_date(raw: str) -> datetime | None:
    cleaned = raw.replace(",", "").strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def audit_post(post: dict, now: datetime) -> PostReport:
    title = strip_tags(post.get("title", {}).get("rendered", "")) or "(no title)"
    content_html = post.get("content", {}).get("rendered", "")
    text = strip_tags(content_html)
    words = len(text.split())
    report = PostReport(
        post_id=post.get("id", 0),
        title=title,
        link=post.get("link", ""),
        modified=post.get("modified_gmt") or post.get("modified", ""),
        words=words,
    )
    p = report.problems

    if words < 800:
        p.append(f"Thin article ({words} words, aim for 1200+)")
    if not BOOKING_RE.search(text):
        p.append("No ticket booking steps (where/how to book)")
    if not FARE_RE.search(text) or not CURRENCY_RE.search(text):
        p.append("No fares with a currency (e.g. ₹1,250 or $40)")
    if "<table" not in content_html.lower():
        p.append("No fare table")
    if not BUDGET_RE.search(text):
        p.append("No budget / total cost breakdown")

    checked = FARES_CHECKED_RE.search(text)
    if not checked:
        p.append('No "Fares checked on <date>" line')
    else:
        checked_on = parse_date(checked.group("date"))
        if checked_on and (now - checked_on).days > STALE_FARE_DAYS:
            p.append(
                f"Fares last checked {checked.group('date')} "
                f"(over {STALE_FARE_DAYS} days ago, re-check prices)"
            )

    if AI_LEFTOVER_RE.search(text):
        p.append("AI leftover text or placeholder found, edit before keeping live")
    if not post.get("featured_media"):
        p.append("No featured image")

    excerpt = strip_tags(post.get("excerpt", {}).get("rendered", ""))
    if len(excerpt) < 50:
        p.append("Missing or very short excerpt / meta description")

    if "<h2" not in content_html.lower():
        p.append("No H2 subheadings (hurts readability and SEO)")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("site", help="Blog address, e.g. https://yourdomain.com")
    parser.add_argument("--max-posts", type=int, default=100)
    parser.add_argument("--csv", help="Also write the report to this CSV file")
    args = parser.parse_args()

    site = args.site.rstrip("/")
    if not site.startswith(("http://", "https://")):
        site = "https://" + site

    try:
        posts = fetch_posts(site, args.max_posts)
    except (urllib.error.URLError, json.JSONDecodeError) as err:
        print(f"Could not read posts from {site}/wp-json/wp/v2/posts: {err}", file=sys.stderr)
        return 2

    now = datetime.now(timezone.utc)
    reports = [audit_post(post, now) for post in posts]
    needs_work = [r for r in reports if r.problems]

    print(f"Audited {len(reports)} posts on {site}: "
          f"{len(reports) - len(needs_work)} OK, {len(needs_work)} need work\n")
    for r in sorted(needs_work, key=lambda r: -len(r.problems)):
        print(f"[{len(r.problems)} issues] {r.title}\n  {r.link}")
        for problem in r.problems:
            print(f"   - {problem}")
        print()

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["id", "title", "link", "modified", "words", "status", "problems"])
            for r in reports:
                writer.writerow([r.post_id, r.title, r.link, r.modified, r.words,
                                 r.status, "; ".join(r.problems)])
        print(f"CSV report written to {args.csv}")

    return 1 if needs_work else 0


if __name__ == "__main__":
    sys.exit(main())
