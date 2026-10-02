# wymisworks.org

Static website for **WYMIS: What You Missed In School**, the thirteenth-grade workforce readiness and life skills program created by Dr. Barry K. Jackson, Ph.D.

Plain HTML, CSS and a little JavaScript. No framework and no build step on the server.

## Pages

| URL | File |
|---|---|
| `/` | `index.html` |
| `/program` | `program.html` |
| `/curriculum` | `curriculum.html` |
| `/intensive` | `intensive.html` (One-Day Intensive schedule and host facility needs) |
| `/pilots` | `pilots.html` |
| `/about` | `about.html` |
| `/faq` | `faq.html` |
| `/partner` | `partner.html` (inquiry form posts to `contact.php`) |
| `/privacy` | `privacy.html` |

Clean URLs (no `.html`) come from `.htaccess`.

## Deploy to Hostinger

1. In hPanel open **Websites > wymisworks.org > Advanced > Git** and connect this repo (branch `main`, install path empty so it deploys to `public_html`). Or upload the repo contents into `public_html` with File Manager.
2. Turn on SSL for wymisworks.org (hPanel > Security > SSL). `.htaccess` forces HTTPS and the bare domain.
3. Create the mailbox `info@wymisworks.org` in hPanel > Emails. The form sends to it and from it; change `TO_EMAIL` / `FROM_EMAIL` at the top of `contact.php` if needed.
4. Submit `https://wymisworks.org/sitemap.xml` in Google Search Console and Bing Webmaster Tools.

## Editing content

All page content lives in `tools/build.py` (module text, FAQs, photos, page titles and meta descriptions). After editing:

```bash
python3 tools/build.py
```

That regenerates every `.html` page plus `sitemap.xml`, `robots.txt`, `llms.txt` and `llms-full.txt`. Styles are in `assets/css/site.css`; behavior is in `assets/js/site.js`. `/tools` is blocked from the web by `.htaccess`.

## Analytics (Google Analytics 4)

1. In [Google Analytics](https://analytics.google.com) create a property for wymisworks.org and a Web data stream; copy the measurement ID (`G-XXXXXXXXXX`).
2. Set `GA4_ID = "G-XXXXXXXXXX"` near the top of `tools/build.py` and run `python3 tools/build.py`. The tag is added to every page and the privacy policy updates itself to name Google Analytics.
3. Events sent: `generate_lead` when an inquiry is delivered (mark it as a key event in GA4), and `partner_cta_click` on any link to /partner.

## SEO and GEO included

- Unique title, meta description, canonical URL, Open Graph and Twitter card on every page
- JSON-LD structured data: `EducationalOrganization`, `WebSite`, `Course` (program and all 7 modules), `ItemList`, `FAQPage`, `Person`, `BreadcrumbList`
- `sitemap.xml`, `robots.txt` (explicitly allows AI crawlers: GPTBot, ClaudeBot, PerplexityBot, Google-Extended and others)
- `llms.txt` and `llms-full.txt` for AI assistants and answer engines
- Geo meta tags (Phoenix, AZ) and `areaServed` for the three pilot cities
- Fact-first copy, an "at a glance" facts block and a direct-answer FAQ, which AI answer engines quote well
- Semantic HTML, alt text, skip link, responsive images with `srcset`, lazy loading, gzip and cache headers

## Brand assets

`assets/img/brand/`: `wymis-logo.png/.webp` (full color, for light backgrounds), `wymis-logo-light.png/.webp` (white and green, for dark backgrounds), `wymis-mark.*` and `wymis-mark-light.*` (cap and book only), plus favicons and app icons. All are transparent. Brand colors: navy `#0A1F4D` (bands), `#0B1F45` (text), green `#1A7A32` (buttons, text on light), `#3DBA5A` (accents on navy). The social share image is `assets/img/og/wymis-og.png`.

Photo sources: see `IMAGE-CREDITS.md`.
