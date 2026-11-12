# Wheels For Wishes — website rebuild preview

A design preview of a rebuilt **wheelsforwishes.org**, made by Saint Paul Agency for Car Donation Foundation.
It is **not** the live site: every page shows a preview banner, search engines are told not to index it,
and the donation form never sends data anywhere.

## What this preview shows
- **Form first, mobile first.** On a phone, the vehicle picker, pickup ZIP and "Start my donation" button sit on the
  first screen. The phone number stays available as a smaller "Prefer to talk?" link, in the menu and in the footer.
- **A 3-step donation flow** (`donate/`): vehicle and ZIP, contact details, then pickup address and vehicle details.
  The progress bar shows the real number of steps. Fields support phone autofill, ZIP opens the number pad, and errors
  say exactly what to fix.
- **Sticky "Start my donation" button** on phones once the visitor scrolls past the form.
- **All state pages** (`states/<state>/`), built from one template. In the real rebuild each keeps its current URL.
- **How it works, FAQ, thank-you and 404 pages.**
- **Fast by design:** plain HTML, one small CSS file, one small script, self-hosted fonts, WebP images,
  and no third-party scripts.

## Test results (Nov 12, 2026)
Google Lighthouse, run locally on the home page and the donate page:

| | Performance | Accessibility | Best practices |
|---|---|---|---|
| Phone | 99 | 100 | 100 |
| Desktop | 100 | 100 | 100 |

For comparison, today's live homepage scored 46 to 77 on phones in PageSpeed Insights the same day.
The SEO score reads low on purpose: the preview tells search engines not to index it. The live build removes that.
Every page was also checked at 360, 390, 768 and 1440 px wide: no text under 16 px, no faded text, no sideways scrolling.

## What the live build adds
- The form posts to NFM's intake, and saves a partial lead (with consent) after the contact step.
- Fraud screening before a lead reaches NFM: bot check, phone and address validation, duplicate check.
- Call tracking (WhatConverts numbers) and one tag manager, with ad pixels loading after the page or on submit.
- Final copy and FAQ answers approved by CDF.

## Files
- `index.html`, `donate/`, `how-it-works/`, `faq/`, `states/`: the site.
- `assets/`: CSS, JavaScript, fonts (Lato and Nunito, SIL Open Font License) and images from the current site.
- `_build/`: the scripts that generated this site (`python3 _build/build.py wfw .`).

## View it
Open `index.html` in a browser, or turn on GitHub Pages for this repo (Settings → Pages → Deploy from branch → `main` / root).

Design preview built by Saint Paul Agency and aidanbarnard.com.
