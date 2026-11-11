# Fix theme demo content and add missing pages

Site: https://blog.budgettravelplaces.com (theme: Travel Blogz). These steps are
done in wp-admin. Each one takes a few minutes.

## 1. Add the missing pages

For each file below: **Pages → Add New**, set the title, open the three-dot
menu (top right) → **Code editor**, paste the file's content (without the
`<!-- ... -->` note at the top), switch back to **Visual editor**, check
the text, then **Publish**. Set the slug in the page settings panel.

| Page title | Slug | File |
|---|---|---|
| Disclaimer | `disclaimer` | `disclaimer.html` |
| Terms and Conditions | `terms-and-conditions` | `terms-and-conditions.html` |

Then open **Pages → Contact us** and paste `contact-us-intro.html` above the
contact form, so the page has an email address and some text.

Add both new pages to the footer menu: **Appearance → Menus** (or
**Appearance → Customize → Menus**), pick the footer menu, tick Disclaimer
and Terms and Conditions, **Save Menu**.

## 2. Remove theme demo content

| Demo content | Where to fix it |
|---|---|
| "Join 200,000+ people and receive monthly travel stories…" newsletter box | **Appearance → Customize**, look for a Home / Front Page / Newsletter section and turn it off. If it is a widget, **Appearance → Widgets** and remove it. If you want a newsletter, replace it with a real signup and no invented subscriber count. |
| Footer "© Budgettravelplaces.com - All Rights Reserved - 2024 \| Webiconic" | **Appearance → Customize → Footer** (or Footer Copyright). Change it to `© 2026 Budget Travel Places. All rights reserved.` |
| Site title "blog budgettravelplaces" | **Settings → General**. Site Title: `Budget Travel Places`. Tagline: `Fares, ticket booking and budget trip guides`. Also update the title in **Rank Math → Titles & Meta → Homepage**. |
| Empty "Home" and "Blog" pages | **Settings → Reading**: check "Your homepage displays" uses Home and Blog. If they are set there, keep them. If not, move them to Trash. |
| Empty categories (Camping, Flights, Photography, Restaurants, Shopping, Tours, Uncategorized) | **Posts → Categories**, hover each one with a count of 0 → Delete. |
| "Blog" category used for 5 posts | **Posts → Categories**: rename "Blog" to `Budget Trips` (slug `budget-trips`). Add `Weekend Trips`, `International`, `Train & Bus Guides`, and move posts into the right ones. |
| Demo importer plugin `themes-artist-demo-importer` | **Plugins → Installed Plugins** → Deactivate → Delete. It is only needed to install demo content once. |
| Author "Roger" with an empty bio | **Users → Profile**: set your public name, add a short bio (who you are, trips you have taken) and a profile photo via Gravatar. |

## 3. Cookie consent (needed before AdSense ads show in the EU / UK)

Install a Google-certified consent tool, for example **Complianz** or
**CookieYes** (both have free plans and support Google Consent Mode v2), run
their setup wizard, and make sure the banner shows on the site.

## 4. Let Claude make these changes for you (optional)

The site currently has Application Passwords turned off (the WordPress API
lists no login methods), so Claude cannot log in through the API. To turn
them on:

1. **Users → Profile**. If there is no "Application Passwords" section, a
   plugin is disabling it: check security plugins (Wordfence, iThemes /
   Solid Security, All In One WP Security, Hostinger Tools) for an option like
   "Disable Application Passwords" or "Disable REST API", and turn that off.
2. Create an application password named "Claude" and save it in the
   credential form Claude shows you (never paste it in chat).
3. Revoke it from the same screen when the work is done.
