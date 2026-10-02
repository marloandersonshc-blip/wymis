# wymis.com

Static website for **WYMIS: What You Missed In School**, the thirteenth-grade workforce readiness and life skills program created by Dr. Barry K. Jackson, Ph.D.

Plain HTML, CSS and a little JavaScript. No framework and no build step on the server.

## Pages

| URL | File |
|---|---|
| `/` | `index.html` |
| `/program` | `program.html` |
| `/curriculum` | `curriculum.html` |
| `/pilots` | `pilots.html` |
| `/about` | `about.html` |
| `/faq` | `faq.html` |
| `/partner` | `partner.html` (inquiry form posts to `contact.php`) |

Clean URLs (no `.html`) come from `.htaccess`.

## Deploy to Hostinger

1. In hPanel open **Websites > wymis.com > Advanced > Git** and connect this repo (branch `main`, install path empty so it deploys to `public_html`). Or upload the repo contents into `public_html` with File Manager.
2. Turn on SSL for wymis.com (hPanel > Security > SSL). `.htaccess` forces HTTPS and the bare domain.
3. Create the mailboxes `info@wymis.com` (receives inquiries) and `no-reply@wymis.com` (sender) in hPanel > Emails, or change `TO_EMAIL` / `FROM_EMAIL` at the top of `contact.php`.
4. Submit `https://wymis.com/sitemap.xml` in Google Search Console and Bing Webmaster Tools.

## Editing content

All page content lives in `tools/build.py` (module text, FAQs, photos, page titles and meta descriptions). After editing:

```bash
python3 tools/build.py
```

That regenerates every `.html` page plus `sitemap.xml`, `robots.txt`, `llms.txt` and `llms-full.txt`. Styles are in `assets/css/site.css`; behavior is in `assets/js/site.js`. `/tools` is blocked from the web by `.htaccess`.

## SEO and GEO included

- Unique title, meta description, canonical URL, Open Graph and Twitter card on every page
- JSON-LD structured data: `EducationalOrganization`, `WebSite`, `Course` (program and all 7 modules), `ItemList`, `FAQPage`, `Person`, `BreadcrumbList`
- `sitemap.xml`, `robots.txt` (explicitly allows AI crawlers: GPTBot, ClaudeBot, PerplexityBot, Google-Extended and others)
- `llms.txt` and `llms-full.txt` for AI assistants and answer engines
- Geo meta tags (Phoenix, AZ) and `areaServed` for the three pilot cities
- Fact-first copy, an "at a glance" facts block and a direct-answer FAQ, which AI answer engines quote well
- Semantic HTML, alt text, skip link, responsive images with `srcset`, lazy loading, gzip and cache headers

## Brand assets

`assets/img/brand/`: `wymis-logo.svg` (for light backgrounds), `wymis-logo-light.svg` (for dark backgrounds), `wymis-mark.svg` / `wymis-mark-light.svg` (icon only), `favicon.svg`, plus PNG icons. The social share image is `assets/img/og/wymis-og.png`.

Photo sources: see `IMAGE-CREDITS.md`.
