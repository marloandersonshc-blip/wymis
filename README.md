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

## Inquiry form

`contact.php` handles each submission from /partner:

1. Emails it to `info@wymisworks.org` (reply-to is the sender).
2. Sends the sender a short confirmation email from `info@wymisworks.org`.
3. Saves a backup row to the Google Sheet "WYMIS Website Inquiries" through a Google Apps Script web app.

The visitor sees success if either the email or the sheet backup worked.

**Sheet backup setup (one time):** open the sheet, go to Extensions > Apps Script, paste in `tools/google-apps-script.gs`, then Deploy > New deployment > Web app with "Execute as: Me" and "Who has access: Anyone". Put the Web app URL (ends in `/exec`) alone on one line in a file named `wymis-sheet-url.txt` one level ABOVE `public_html` on the server (Hostinger File Manager). `contact.php` reads it from there. The URL acts as the access key and this repo is public, so never commit it.

## Consent form (/consent)

Every One-Day Intensive participant signs a consent form: permission to attend plus a release of liability.

- **Under 18:** `register.php` emails the parent or guardian a signing link (prefilled, tamper-proof). The student's confirmation says the parent must sign.
- **18 or older:** after registering, the student goes straight to the prefilled form, and the link is also in their confirmation email.
- **Registered before the form existed:** send them `https://wymisworks.org/consent`. They pick the event and enter the participant's details.

On signing, `consent.php` saves a JSON record in `wymis-consents/` one level ABOVE `public_html`, emails the signed copy to the signer, a notice to the student and `info@`, and adds a row to the **Consents** tab of the Google Sheet. One form per participant email per event; a second attempt shows "already signed".

The signing-link key is created automatically as `wymis-consent-secret.txt` one level above `public_html`. Never commit it. Deleting it invalidates links already emailed (the plain `/consent` form still works).

The form wording lives in `consent_sections()` in `consent.inc.php`. If you change it, bump `CONSENT_VERSION`; each record stores the version and a hash of the exact text signed. The page itself is generated: edit `tools/consent.tpl.php`, then run `python3 tools/build.py`.

After updating `tools/google-apps-script.gs`, paste it into the sheet's Apps Script and redeploy: Deploy > Manage deployments > edit > Version: New version > Deploy (same URL).

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

## One-Day Intensive registration

`/register` lists the public intensive dates (edit `EVENTS` in `tools/build.py`, then rebuild). Submissions post to `register.php`, which:
1. emails a notice to info@wymisworks.org,
2. emails a confirmation to the registrant, plus a copy to the parent or guardian for registrants who are 16 or 17 (parent name, email, and permission are required for them),
3. saves a row on the **Registrations** tab of the "WYMIS Website Inquiries" Google Sheet (the tab is created automatically on the first registration).

`events.inc.php` is generated by the build so the PHP handler and the pages always share the same dates. Past dates close automatically on the page and are rejected by the server.
After changing `tools/google-apps-script.gs`, paste it into the sheet's Apps Script editor and use Deploy > Manage deployments > Edit > New version, so the web app URL stays the same.
