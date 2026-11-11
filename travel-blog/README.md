# Travel blog maintenance kit

A budget travel blog on Hostinger WordPress, with articles written automatically
by goAISEO. What sets it apart from YouTube travel videos: every post gives
**ticket booking steps, fares and a full budget breakdown**.

| File | What it is for |
|---|---|
| `goaiseo-article-rules.md` | Instructions to paste into goAISEO, and the checklist to run before a post goes live |
| `templates/trip-post-template.html` | Block editor template with fare tables, booking steps and a budget table |
| `tools/audit_posts.py` | Checks every published post for missing booking info, fares, stale prices and AI leftovers |

## Audit your posts

Needs Python 3.9 or later, no extra packages.

```bash
python3 travel-blog/tools/audit_posts.py https://yourdomain.com --csv audit.csv
```

It reads only public posts through the WordPress REST API and lists every post
that needs work, worst first. A post is flagged when it has:

- no ticket booking steps, no fares with a currency, or no fare table
- no budget / total cost section
- no "Fares checked on <date>" line, or one older than 90 days
- AI leftovers or placeholders ("as an AI", `[insert`, lorem ipsum)
- fewer than 800 words, no H2 headings, no featured image or a missing excerpt

## Maintenance routine

**Weekly**
- Run the audit and fix or unpublish the worst posts.
- Review new goAISEO drafts with the checklist in `goaiseo-article-rules.md`.
- Update WordPress core, plugins and themes, and check for vulnerabilities (Hostinger connector).
- Check the site loads, SSL is valid, and there are no 404s in Google Search Console.

**Monthly**
- Re-check fares on the top 20 posts by traffic, then update their "Fares checked on" date.
- Confirm backups are running on Hostinger, and restore one to test it.
- Look at PageSpeed for the home page and one post, and purge the cache after changes.

**Seasonal**
- Before peak seasons (summer holidays, Diwali, Christmas, New Year), refresh
  "best time to visit" and fares on seasonal destinations.
