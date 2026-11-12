"""Build a static design preview for Vehicles For Veterans (vfv) or Wheels For Wishes (wfw).

Usage: python3 build.py <vfv|wfw> <out_dir>

Writes plain HTML, CSS and JS with relative links, so the site works from any folder,
including a GitHub Pages project URL. The donation form is a demo: it never sends data.
"""
import html
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
          "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas",
          "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
          "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
          "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
          "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
          "West Virginia", "Wisconsin", "Wyoming"]
ABBR = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY",
        "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
        "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]


def slug(s):
    return s.lower().replace(" ", "-")


VEHICLES = [("car", "Car or truck", "car.svg"), ("motorcycle", "Motorcycle", "motorcycle.svg"),
            ("boat", "Boat", "ship.svg"), ("rv", "RV or camper", "rv.svg"), ("other", "Other", "caravan.svg")]

BRANDS = {
    "vfv": {
        "name": "Vehicles For Veterans",
        "short": "VFV",
        "domain": "vehiclesforveterans.org",
        "phone": "1-877-646-1976",
        "tel": "18776461976",
        "title": "Donate Your Car to Help Disabled Veterans | Vehicles For Veterans",
        "description": "Donate your car, truck, boat or RV to help disabled veterans. Free pickup, running or not, and a tax-deductible receipt.",
        "colors": {"ink": "#121A2B", "ink2": "#26314A", "navy": "#0F2747", "brand": "#C8102E", "brand_dark": "#A00C24",
                   "accent": "#78C8F8", "soft": "#EDF3FA", "line": "#B8C4D4", "hero_ink": "#FFFFFF"},
        "head_font": "Oswald", "head_file": "oswald-latin-600-normal.woff2", "head_weight": 600,
        "hero_h1": "Donate your car to help disabled veterans",
        "hero_sub": "Free pickup, running or not. You get a tax-deductible receipt.",
        "hero_points": ["Free towing anywhere in the U.S.", "Cars, trucks, boats, RVs, motorcycles and more", "A 501(c)(3) charity program since 2010"],
        "cause_short": "disabled veterans",
        "badge_alt": "Car Donation Foundation badge: $200 million donated",
        "steps": [
            ("Tell us about your vehicle", "Pick the vehicle type, add your pickup ZIP and contact details. It's three short screens."),
            ("Schedule your free pickup", "The nearest auction partner contacts you to set a pickup time that works for you."),
            ("Get your tax receipt", "You receive an IRS tax receipt for your records after the vehicle sells."),
        ],
        "faq": [
            ("Is my donation tax-deductible?", "Yes. Car Donation Foundation is a tax-exempt charity under section 501(c)(3) of the IRS Code, and you receive an IRS tax receipt for your records. Ask your tax advisor how the deduction applies to you."),
            ("Does my vehicle need to run?", "No. Pickup is free whether the vehicle runs or not."),
            ("What can I donate?", "Cars, trucks, motorcycles, boats, RVs, campers and ATVs."),
            ("How does pickup work?", "Your donation is assigned to the nearest auction partner, who contacts you to schedule the pickup at a time that suits you."),
            ("Do I need the title?", "Tell us on the form whether you have the title. The team explains what's needed in your state before pickup."),
            ("Where does the money go?", "Car Donation Foundation donates the proceeds from Vehicles For Veterans to other tax-exempt charities that help disabled veterans, through programs such as transition services, help for homeless veterans, advocacy and employment assistance."),
        ],
        "nonprofit": "Vehicles For Veterans is Car Donation Foundation's vehicle donation program. Car Donation Foundation is a tax-exempt charity under section 501(c)(3) of the IRS Code and donates the proceeds from this program to other tax-exempt charities that help disabled veterans.",
        "ein": "26-3408048",
        "address": "5775 Wayzata Boulevard, Suite 700, St. Louis Park, MN 55416",
    },
    "wfw": {
        "name": "Wheels For Wishes",
        "short": "WFW",
        "domain": "wheelsforwishes.org",
        "phone": "1-888-737-5808",
        "tel": "18887375808",
        "title": "Donate Your Car to Help a Local Child | Wheels For Wishes, Benefiting Make-A-Wish",
        "description": "Donate your car to grant wishes for local children through Make-A-Wish. Free pickup nationwide and a tax-deductible receipt.",
        "colors": {"ink": "#151B2E", "ink2": "#28304A", "navy": "#1C3A8A", "brand": "#C2255C", "brand_dark": "#9E1C4A",
                   "accent": "#F7D132", "soft": "#EEF3FC", "line": "#B9C3DA", "hero_ink": "#151B2E"},
        "head_font": "Nunito", "head_file": "nunito-latin-800-normal.woff2", "head_weight": 800,
        "hero_h1": "Your car donation helps a local child",
        "hero_sub": "Free pickup nationwide, running or not. Proceeds benefit Make-A-Wish.",
        "hero_points": ["Free towing anywhere in the U.S.", "A tax-deductible receipt for your records", "Most vehicles accepted, whatever the condition"],
        "cause_short": "local children",
        "badge_alt": "Car Donation Foundation badge: $200 million total donated across all charitable donations",
        "steps": [
            ("Tell us about your vehicle", "Pick the vehicle type, add your pickup ZIP and contact details. It's three short screens."),
            ("Schedule your free pickup", "Our towing partner contacts you to set a pickup time that works for you."),
            ("Get your tax receipt", "You receive a tax-deductible receipt, and your car helps grant a local child's wish."),
        ],
        "faq": [
            ("Is my donation tax-deductible?", "Yes. Wheels For Wishes is a tax-exempt charity under Section 501(c)(3) of the IRS Code, and you receive a tax-deductible receipt. Ask your tax advisor how the deduction applies to you."),
            ("Does my vehicle need to run?", "No. We accept most vehicles regardless of condition, and pickup is free."),
            ("What can I donate?", "Cars, trucks, motorcycles, boats, RVs and motorhomes."),
            ("How does pickup work?", "After you finish the form, our towing partner contacts you to schedule a free pickup."),
            ("Do I need the title?", "Tell us on the form whether you have the title. The team explains what's needed in your state before pickup."),
            ("How does my car help a child?", "Proceeds from donated cars go to Wheels For Wishes, benefiting Make-A-Wish chapters across the United States, which grant wishes to children with critical illnesses."),
        ],
        "nonprofit": "Proceeds from donated cars go to Wheels For Wishes, a tax-exempt charity under Section 501(c)(3) of the IRS Code, benefiting Make-A-Wish chapters in locations throughout the United States.",
        "ein": None,
        "address": "5775 Wayzata Boulevard, Suite 700, St. Louis Park, MN 55416",
    },
}

MAKES = ["Acura", "Audi", "BMW", "Buick", "Cadillac", "Chevrolet", "Chrysler", "Dodge", "Ford", "GMC", "Honda",
         "Hyundai", "Infiniti", "Jeep", "Kia", "Lexus", "Lincoln", "Mazda", "Mercedes-Benz", "Mercury", "Mini",
         "Mitsubishi", "Nissan", "Pontiac", "Ram", "Saturn", "Subaru", "Tesla", "Toyota", "Volkswagen", "Volvo"]

ICON_CHECK = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M9.5 16.2 5.3 12l-1.4 1.4 5.6 5.6L20.1 8.4 18.7 7z"/></svg>'
ICON_PHONE = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>'


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
def css(b):
    c = b["colors"]
    return f"""@font-face{{font-family:"Lato";font-weight:400;font-style:normal;font-display:swap;src:url(../fonts/lato-latin-400-normal.woff2) format("woff2")}}
@font-face{{font-family:"Lato";font-weight:700;font-style:normal;font-display:swap;src:url(../fonts/lato-latin-700-normal.woff2) format("woff2")}}
@font-face{{font-family:"Lato";font-weight:900;font-style:normal;font-display:swap;src:url(../fonts/lato-latin-900-normal.woff2) format("woff2")}}
@font-face{{font-family:"{b['head_font']}";font-weight:{b['head_weight']};font-style:normal;font-display:swap;src:url(../fonts/{b['head_file']}) format("woff2")}}
:root{{--ink:{c['ink']};--ink2:{c['ink2']};--navy:{c['navy']};--brand:{c['brand']};--brand-dark:{c['brand_dark']};--accent:{c['accent']};--soft:{c['soft']};--line:{c['line']};--hero-ink:{c['hero_ink']};
--head:"{b['head_font']}",system-ui,sans-serif;--body:"Lato",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--wrap:1160px;--r:14px}}
*,*::before,*::after{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%;scroll-padding-top:16px}}
body{{margin:0;font-family:var(--body);font-size:1.125rem;line-height:1.6;color:var(--ink);background:#fff}}
img{{max-width:100%;height:auto;display:block}}
a{{color:var(--navy);text-underline-offset:3px}}
a:hover{{color:var(--brand-dark)}}
:focus-visible{{outline:3px solid var(--brand);outline-offset:3px}}
h1,h2,h3{{font-family:var(--head);font-weight:{b['head_weight']};line-height:1.15;margin:0 0 .5em;color:var(--ink)}}
h1{{font-size:clamp(2.1rem,6.4vw,3.6rem);letter-spacing:-.01em}}
h2{{font-size:clamp(1.75rem,4.2vw,2.5rem)}}
h3{{font-size:1.375rem}}
p{{margin:0 0 1em}}
.wrap{{max-width:var(--wrap);margin:0 auto;padding:0 20px}}
.ico{{width:1.25em;height:1.25em;fill:currentColor;flex:none}}
.skip{{position:absolute;left:-9999px}}.skip:focus{{left:12px;top:12px;z-index:50;background:#fff;padding:8px 12px}}
/* preview bar */
.preview-bar{{background:#0E1830;color:#fff;font-size:1rem;line-height:1.4}}
.preview-bar .wrap{{display:flex;align-items:center;gap:10px;padding-top:8px;padding-bottom:8px}}
.preview-bar img{{width:28px;height:28px}}
.preview-bar a{{color:#fff}}
.pb-long{{display:none}}
/* header */
.site-header{{background:#fff;border-bottom:1px solid var(--line)}}
.site-header .wrap{{display:flex;align-items:center;justify-content:space-between;min-height:72px;gap:16px}}
.logo{{display:flex;align-items:center;gap:12px;text-decoration:none}}
.logo img{{height:56px;width:auto}}
.logo .logo-maw{{height:36px}}
.menu-btn{{font:700 1rem var(--body);color:var(--ink);background:#fff;border:2px solid var(--ink);border-radius:10px;padding:8px 14px;min-height:44px;cursor:pointer}}
.site-nav{{display:none}}
.site-nav.open{{display:block;position:absolute;left:0;right:0;top:100%;background:#fff;border-bottom:2px solid var(--line);z-index:30;padding:8px 20px 20px}}
.site-nav ul{{list-style:none;margin:0;padding:0}}
.site-nav li a{{display:block;padding:12px 0;font-weight:700;font-size:1.125rem;color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line)}}
.site-nav .nav-phone{{display:flex;gap:8px;align-items:center}}
.site-header{{position:relative}}
.btn{{display:inline-flex;align-items:center;justify-content:center;gap:10px;font:900 1.1875rem/1.2 var(--body);background:var(--brand);color:#fff;border:0;border-radius:12px;padding:16px 22px;min-height:56px;text-decoration:none;cursor:pointer}}
.btn:hover{{background:var(--brand-dark);color:#fff}}
.btn-block{{width:100%}}
.btn-secondary{{background:#fff;color:var(--ink);border:2px solid var(--ink)}}
.btn-secondary:hover{{background:var(--soft);color:var(--ink)}}
/* hero */
.hero{{background:var(--hero-bg);color:var(--hero-ink);position:relative;overflow:hidden}}
.hero .wrap{{display:grid;gap:20px;padding-top:22px;padding-bottom:28px;position:relative}}
.hero h1{{color:var(--hero-ink);margin-bottom:.3em}}
.hero-sub{{font-size:1.1875rem;margin:0;font-weight:700}}
.hero-points{{display:none;list-style:none;padding:0;margin:20px 0 0}}
.hero-points li{{display:flex;gap:10px;align-items:center;margin:0 0 10px;font-size:1.125rem}}
.hero-photo{{display:none}}
/* start card */
.start-card{{background:#fff;color:var(--ink);border-radius:var(--r);padding:20px;box-shadow:0 18px 40px -18px rgba(8,16,40,.55);border:1px solid var(--line)}}
.start-card h2{{font-size:1.5rem;margin-bottom:12px}}
fieldset{{border:0;margin:0;padding:0;min-width:0}}
legend{{font-weight:900;font-size:1.125rem;padding:0;margin-bottom:10px}}
.tiles{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.tile{{position:relative}}
.tile input{{position:absolute;opacity:0;width:1px;height:1px}}
.tile label{{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;min-height:92px;padding:10px 6px;border:2px solid var(--line);border-radius:12px;cursor:pointer;text-align:center;font-weight:700;font-size:1rem;line-height:1.2;background:#fff}}
.tile img{{width:46px;height:34px}}
.tile input:checked+label{{border-color:var(--brand);background:var(--soft);box-shadow:inset 0 0 0 2px var(--brand)}}
.tile input:focus-visible+label{{outline:3px solid var(--brand);outline-offset:2px}}
.field{{margin-top:16px}}
.field label,.label{{display:block;font-weight:900;font-size:1.0625rem;margin-bottom:6px}}
.field .hint{{display:block;font-size:1rem;color:var(--ink2);margin:-2px 0 6px}}
input[type=text],input[type=tel],input[type=email],select{{width:100%;font:400 1.1875rem var(--body);color:var(--ink);background:#fff;border:2px solid #5B667A;border-radius:10px;padding:12px 14px;min-height:56px}}
input:focus,select:focus{{border-color:var(--navy);outline:3px solid var(--accent);outline-offset:1px}}
.start-card .btn{{margin-top:16px}}
.form-error{{color:var(--brand-dark);font-weight:900;font-size:1rem;margin:12px 0 0}}
.field-error{{display:block;color:var(--brand-dark);font-weight:900;font-size:1rem;margin-top:6px}}
.talk{{margin:14px 0 0;font-size:1rem;text-align:center}}
.talk a{{color:var(--ink);font-weight:700}}
/* trust */
.trust{{background:var(--soft);border-bottom:1px solid var(--line)}}
.trust ul{{list-style:none;margin:0;padding:18px 0;display:grid;gap:12px}}
.trust li{{display:flex;align-items:center;gap:12px;font-weight:700;font-size:1.0625rem}}
.trust .ico{{color:var(--brand);width:28px;height:28px}}
.trust img{{width:auto;height:56px}}
/* sections */
.section{{padding:56px 0}}
.section-soft{{background:var(--soft)}}
.lead{{font-size:1.25rem;max-width:62ch}}
.steps{{list-style:none;padding:0;margin:28px 0 0;display:grid;gap:22px;counter-reset:s}}
.steps li{{display:grid;grid-template-columns:56px 1fr;gap:16px;align-items:start;counter-increment:s}}
.steps li::before{{content:counter(s);display:grid;place-items:center;width:56px;height:56px;border-radius:50%;background:var(--navy);color:#fff;font:{b['head_weight']} 1.5rem var(--head)}}
.steps h3{{margin:6px 0 4px}}
.steps p{{margin:0}}
.split{{display:grid;gap:28px;align-items:center}}
.split img{{border-radius:var(--r)}}
.facts{{display:grid;gap:14px;margin:22px 0 0;padding:0;list-style:none}}
.facts li{{border-left:6px solid var(--brand);padding:6px 0 6px 16px}}
.facts strong{{display:block;font:{b['head_weight']} 2rem/1.1 var(--head);color:var(--navy)}}
.quotes{{display:grid;gap:18px;margin-top:24px}}
blockquote{{margin:0;background:#fff;border:2px solid var(--line);border-radius:var(--r);padding:20px}}
blockquote p{{font-size:1.1875rem}}
blockquote footer{{font-weight:900}}
.wishes{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;margin-top:24px;list-style:none;padding:0}}
.wishes img{{border-radius:50%;width:100%;max-width:220px;aspect-ratio:1;object-fit:cover;margin:0 auto 10px;border:6px solid var(--accent)}}
.wishes li{{text-align:center;font-size:1.0625rem}}
.wishes strong{{display:block;font-size:1.1875rem}}
.accept{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;list-style:none;padding:0;margin:24px 0 0}}
.accept li{{display:flex;flex-direction:column;align-items:center;text-align:center;gap:8px;background:#fff;border:2px solid var(--line);border-radius:12px;padding:14px 10px;font-weight:700}}
.accept img{{width:46px;height:34px}}
details{{border-bottom:2px solid var(--line);padding:4px 0}}
summary{{cursor:pointer;font-weight:900;font-size:1.1875rem;padding:14px 0;list-style:none;display:flex;justify-content:space-between;gap:16px}}
summary::-webkit-details-marker{{display:none}}
summary::after{{content:"+";font-size:1.5rem;line-height:1;color:var(--brand)}}
details[open] summary::after{{content:"–"}}
details p{{margin:0 0 16px}}
.state-list{{columns:2;column-gap:24px;list-style:none;padding:0;margin:20px 0 0}}
.state-list li{{break-inside:avoid;margin:0 0 8px}}
.state-list a{{font-weight:700;color:var(--ink)}}
.cta-band{{background:var(--navy);color:#fff;text-align:left}}
.cta-band h2{{color:#fff}}
.cta-band p{{font-size:1.1875rem}}
/* footer */
.site-footer{{background:#0B1528;color:#fff;padding:44px 0 120px;font-size:1rem}}
.site-footer a{{color:#fff}}
.site-footer .cols{{display:grid;gap:26px}}
.site-footer h2{{color:#fff;font-size:1.25rem}}
.site-footer ul{{list-style:none;padding:0;margin:0}}
.site-footer li{{margin:0 0 8px}}
.credit{{display:flex;align-items:center;gap:12px;margin-top:30px;padding-top:20px;border-top:1px solid #3A4A6A}}
.credit img{{width:44px;height:44px}}
/* sticky cta */
.sticky-cta{{position:fixed;left:0;right:0;bottom:0;z-index:40;background:#fff;border-top:2px solid var(--line);padding:10px 12px calc(10px + env(safe-area-inset-bottom));display:flex;gap:10px;transform:translateY(110%);transition:transform .2s ease}}
.sticky-cta.show{{transform:none}}
.sticky-cta .btn{{flex:1}}
.sticky-cta .call{{flex:none;width:56px;padding:0;background:#fff;color:var(--ink);border:2px solid var(--ink)}}
/* donate flow */
.donate-main{{background:var(--soft);padding:24px 0 64px}}
.donate-box{{max-width:640px;margin:0 auto;background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:22px}}
.progress{{margin-bottom:18px}}
.progress-text{{font-weight:900;font-size:1.0625rem;margin:0 0 8px}}
.progress-bar{{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}}
.progress-bar span{{height:8px;border-radius:8px;background:var(--line)}}
.progress-bar span.done{{background:var(--brand)}}
.step h2{{font-size:1.75rem}}
.step h2:focus{{outline:none}}
.row{{display:grid;gap:0 14px}}
.actions{{display:flex;gap:12px;margin-top:22px}}
.actions .btn{{flex:1}}
.actions .btn-secondary{{flex:0 0 auto}}
.check{{display:flex;gap:12px;align-items:flex-start;margin-top:16px;font-size:1.0625rem}}
.check input{{width:24px;height:24px;margin-top:3px;flex:none;accent-color:var(--brand)}}
.radio-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.radio-row label{{display:flex;align-items:center;justify-content:center;min-height:52px;border:2px solid var(--line);border-radius:10px;font-weight:700;cursor:pointer;margin:0}}
.radio-row input{{position:absolute;opacity:0;width:1px;height:1px}}
.radio-row input:checked+label{{border-color:var(--brand);background:var(--soft);box-shadow:inset 0 0 0 2px var(--brand)}}
.radio-row input:focus-visible+label{{outline:3px solid var(--brand);outline-offset:2px}}
.preview-note{{margin-top:18px;background:var(--soft);border-radius:10px;padding:12px 14px;font-size:1rem;font-weight:700}}
.thanks{{text-align:center}}
.thanks .big-check{{width:84px;height:84px;border-radius:50%;background:#067647;color:#fff;display:grid;place-items:center;margin:8px auto 16px}}
.thanks .big-check svg{{width:48px;height:48px;fill:#fff}}
.thanks ol{{text-align:left;max-width:440px;margin:18px auto}}
.page-hero{{background:var(--soft);padding:36px 0 30px;border-bottom:1px solid var(--line)}}
.page-hero p{{font-size:1.25rem;max-width:60ch;margin:0}}
.crumbs{{font-size:1rem;margin:0 0 10px}}
@media (min-width:600px){{
  .pb-long{{display:inline}}.pb-short{{display:none}}
  .tiles{{grid-template-columns:repeat(5,1fr)}}
  .trust ul{{grid-template-columns:repeat(2,1fr)}}
  .accept{{grid-template-columns:repeat(4,1fr)}}
  .state-list{{columns:3}}
  .row-2{{grid-template-columns:1fr 1fr}}
  .row-3{{grid-template-columns:1fr 1fr 1fr}}
  .wishes{{grid-template-columns:repeat(4,1fr)}}
}}
@media (min-width:960px){{
  .menu-btn{{display:none}}
  .logo img{{height:64px}}
  .logo .logo-maw{{height:42px}}
  .site-nav,.site-nav.open{{display:block;position:static;padding:0;border:0}}
  .site-nav ul{{display:flex;gap:26px;align-items:center}}
  .site-nav li a{{border:0;padding:8px 0;font-size:1.0625rem}}
  .site-nav .nav-cta a{{background:var(--brand);color:#fff;border-radius:10px;padding:12px 18px}}
  .site-nav .nav-cta a:hover{{background:var(--brand-dark)}}
  .hero .wrap{{grid-template-columns:1.05fr .95fr;gap:48px;padding-top:56px;padding-bottom:64px;align-items:center}}
  .hero-points{{display:block}}
  .hero-photo{{display:block;margin-top:26px;border-radius:var(--r);max-height:280px;width:100%;object-fit:cover}}
  .start-card{{padding:28px}}
  .tiles{{grid-template-columns:repeat(5,1fr)}}
  .trust ul{{grid-template-columns:repeat(4,1fr)}}
  .split{{grid-template-columns:1fr 1fr;gap:56px}}
  .quotes{{grid-template-columns:1fr 1fr}}
  .site-footer .cols{{grid-template-columns:1.4fr 1fr 1fr}}
  .site-footer{{padding-bottom:44px}}
  .sticky-cta{{display:none}}
  .state-list{{columns:4}}
  .accept{{grid-template-columns:repeat(4,1fr)}}
  .section{{padding:80px 0}}
}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important;scroll-behavior:auto!important}}}}
"""


def brand_css_extra(key):
    if key == "vfv":
        return """.hero{--hero-bg:#0F2747;background:#0F2747}
.hero .hero-sub{color:#fff}
.hero-points .ico{color:#78C8F8}
@media (min-width:960px){.hero{background:#0F2747 url(../img/chevrons.svg) right -40px top -60px/560px no-repeat}}
"""
    return """.hero{--hero-bg:#F7D132;background:#F7D132}
.hero .wrap{grid-template-areas:"copy" "form" "media"}
.hero-copy{grid-area:copy}.hero-form{grid-area:form}
.hero-media{grid-area:media;position:relative}
.hero-media img{width:100%;height:200px;object-fit:cover;object-position:62% 35%;border-radius:14px}
.hero-caption{position:absolute;left:12px;bottom:10px;background:#fff;color:#151B2E;font-weight:700;font-size:1rem;line-height:1.3;border-radius:999px;padding:6px 14px;max-width:calc(100% - 24px)}
.hero-points .ico{color:#C2255C}
@media (min-width:960px){.hero .wrap{grid-template-areas:"media form" "copy form";align-items:start;row-gap:28px}.hero-form{align-self:center}.hero-media img{height:250px}.hero-caption{left:16px;bottom:16px}}
"""


CHEVRON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"><g fill="none" stroke-width="44"><path d="M20 120 200 300 380 120" stroke="#C8102E"/><path d="M20 210 200 390 380 210" stroke="#78C8F8"/><path d="M20 30 200 210 380 30" stroke="#1D3E6B"/></g></svg>"""


# ---------------------------------------------------------------------------
# JS
# ---------------------------------------------------------------------------
JS = r"""(function () {
  var qs = function (s, r) { return (r || document).querySelector(s); };
  var qsa = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var store = {
    get: function () { try { return JSON.parse(sessionStorage.getItem('donation') || '{}'); } catch (e) { return {}; } },
    set: function (o) { try { var d = store.get(); for (var k in o) d[k] = o[k]; sessionStorage.setItem('donation', JSON.stringify(d)); } catch (e) {} },
    clear: function () { try { sessionStorage.removeItem('donation'); } catch (e) {} }
  };

  // Menu
  var mb = qs('.menu-btn'), nav = qs('#site-nav');
  if (mb && nav) {
    mb.addEventListener('click', function () {
      var open = mb.getAttribute('aria-expanded') === 'true';
      mb.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('open', !open);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) { nav.classList.remove('open'); mb.setAttribute('aria-expanded', 'false'); mb.focus(); }
    });
  }

  // ZIP and number fields: digits only
  qsa('input[data-digits]').forEach(function (i) {
    i.addEventListener('input', function () { var v = i.value.replace(/\D/g, '').slice(0, +i.getAttribute('data-digits')); if (v !== i.value) i.value = v; });
  });

  // Start card on home and state pages
  qsa('form.start-card').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var picked = qs('input[name=vehicle]:checked', f);
      var zip = qs('input[name=zip]', f);
      var err = qs('.form-error', f);
      var msg = '';
      if (!picked) msg = 'Choose what you are donating.';
      else if (!/^\d{5}$/.test(zip.value)) msg = 'Enter the 5-digit ZIP code where we pick up the vehicle.';
      if (msg) { err.textContent = msg; err.hidden = false; (picked ? zip : qs('input[name=vehicle]', f)).focus(); return; }
      err.hidden = true;
      store.set({ vehicle: picked.value, zip: zip.value });
      window.location.href = f.getAttribute('action');
    });
  });

  // Sticky mobile button
  var sticky = qs('.sticky-cta'), card = qs('.start-card');
  if (sticky && card && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      var e = entries[0];
      sticky.classList.toggle('show', !e.isIntersecting && e.boundingClientRect.top < 0);
    }).observe(card);
    var go = qs('[data-to-start]', sticky);
    if (go) go.addEventListener('click', function (e) {
      e.preventDefault();
      card.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' });
      var first = qs('input[name=vehicle]', card); if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 350);
    });
  }

  // Donation flow
  var df = qs('#donate-form');
  if (df) {
    var steps = qsa('.step', df), cur = 0, data = store.get();
    if (data.vehicle) { var r = qs('input[name=vehicle][value="' + data.vehicle + '"]', df); if (r) r.checked = true; }
    if (data.zip) qsa('input[name=zip]', df).forEach(function (i) { i.value = data.zip; });
    var show = function (i, focus) {
      cur = i;
      steps.forEach(function (s, j) { s.hidden = j !== i; });
      qs('.progress-text').textContent = 'Step ' + (i + 1) + ' of ' + steps.length;
      qsa('.progress-bar span').forEach(function (b, j) { b.classList.toggle('done', j <= i); });
      if (focus) { var h = qs('h2', steps[i]); h.setAttribute('tabindex', '-1'); h.focus(); window.scrollTo(0, 0); }
    };
    var clearErrors = function (step) { qsa('.field-error', step).forEach(function (e) { e.remove(); }); qsa('[aria-invalid]', step).forEach(function (e) { e.removeAttribute('aria-invalid'); }); };
    var validate = function (step) {
      clearErrors(step);
      var firstBad = null;
      qsa('[data-check]', step).forEach(function (wrap) {
        var input = qs('input,select', wrap), ok = true, kind = wrap.getAttribute('data-check');
        if (input.type === 'radio') { ok = !!qs('input:checked', wrap); input = qs('input', wrap); }
        else if (kind === 'zip') ok = /^\d{5}$/.test(input.value);
        else if (kind === 'phone') ok = input.value.replace(/\D/g, '').length === 10;
        else if (kind === 'email') ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim());
        else ok = input.value.trim() !== '';
        if (!ok) {
          var id = (input.id || input.name) + '-err', m = document.createElement('span');
          m.className = 'field-error'; m.id = id; m.textContent = wrap.getAttribute('data-msg');
          wrap.appendChild(m);
          if (input.type !== 'radio') { input.setAttribute('aria-invalid', 'true'); input.setAttribute('aria-describedby', id); }
          if (!firstBad) firstBad = input;
        }
      });
      if (firstBad) firstBad.focus();
      return !firstBad;
    };
    var clearOne = function (e) {
      var w = e.target.closest('[data-check]'); if (!w) return;
      var m = qs('.field-error', w); if (m) m.remove();
      e.target.removeAttribute('aria-invalid');
    };
    df.addEventListener('input', clearOne);
    df.addEventListener('change', clearOne);
    qsa('[data-next]', df).forEach(function (b) {
      b.addEventListener('click', function () {
        if (!validate(steps[cur])) return;
        if (cur === 1) store.set({ first: qs('#first', df).value.trim() }); // the live build saves the partial lead here, with consent
        show(cur + 1, true);
      });
    });
    qsa('[data-back]', df).forEach(function (b) { b.addEventListener('click', function () { show(cur - 1, true); }); });
    df.addEventListener('submit', function (e) {
      e.preventDefault(); // preview only: nothing is sent anywhere
      if (!validate(steps[cur])) return;
      window.location.href = df.getAttribute('data-done');
    });
    var started = data.vehicle && /^\d{5}$/.test(data.zip || '');
    show(started ? 1 : 0, false);
  }

  // Thank-you page
  var ty = qs('[data-thanks]');
  if (ty) { var d = store.get(); if (d.first) qs('[data-name]').textContent = ', ' + d.first; store.clear(); }
})();
"""


# ---------------------------------------------------------------------------
# HTML pieces
# ---------------------------------------------------------------------------
def head(b, key, P, title, desc, path):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="{b['colors']['navy']}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{P}assets/img/og.png">
<link rel="icon" href="{P}assets/img/icon-512.png">
<link rel="preload" href="{P}assets/fonts/{b['head_file']}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{P}assets/fonts/lato-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{P}assets/css/site.css">
<script src="{P}assets/js/site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="preview-bar"><div class="wrap"><img src="{P}assets/img/spa-seal.webp" width="28" height="28" alt=""><span class="pb-long">Design preview by Saint Paul Agency. This is not the live site, and the form doesn't send any data.</span><span class="pb-short">Design preview by Saint Paul Agency. Not the live site.</span></div></div>
"""


def header(b, key, P):
    logo = (f'<img src="{P}assets/img/logo.svg" width="66" height="64" alt="{esc(b["name"])} home"><img class="logo-maw" src="{P}assets/img/make-a-wish.webp" width="160" height="42" alt="Benefiting Make-A-Wish">' if key == "wfw"
            else f'<img src="{P}assets/img/logo.webp" width="136" height="64" alt="{esc(b["name"])} home">')
    return f"""<header class="site-header"><div class="wrap">
<a class="logo" href="{P}index.html">{logo}</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
<nav id="site-nav" class="site-nav" aria-label="Main"><ul>
<li><a href="{P}how-it-works/index.html">How it works</a></li>
<li><a href="{P}faq/index.html">FAQ</a></li>
<li><a href="{P}states/index.html">Donate in your state</a></li>
<li><a class="nav-phone" href="tel:{b['tel']}">{ICON_PHONE}<span>{b['phone']}</span></a></li>
<li class="nav-cta"><a href="{P}donate/index.html">Donate my car</a></li>
</ul></nav>
</div></header>
"""


def tiles(name_prefix, checked=None):
    out = ['<div class="tiles">']
    for i, (val, label, icon) in enumerate(VEHICLES):
        idp = f"{name_prefix}-{val}"
        chk = " checked" if checked == val else ""
        out.append(f'<div class="tile"><input type="radio" name="vehicle" id="{idp}" value="{val}"{chk}>'
                   f'<label for="{idp}"><img src="{{P}}assets/img/{icon}" width="46" height="34" alt="">{label}</label></div>')
    out.append("</div>")
    return "".join(out)


def start_card(b, P, heading="What are you donating?", idp="s"):
    return f"""<form class="start-card" id="start" action="{P}donate/index.html" novalidate>
<h2>{heading}</h2>
<fieldset><legend class="skip">Vehicle type</legend>{tiles(idp).replace('{P}', P)}</fieldset>
<div class="field"><label for="{idp}-zip">Pickup ZIP code</label>
<input type="text" id="{idp}-zip" name="zip" inputmode="numeric" autocomplete="postal-code" data-digits="5"></div>
<p class="form-error" role="alert" hidden></p>
<button class="btn btn-block" type="submit">Start my donation</button>
<p class="talk">Prefer to talk? <a href="tel:{b['tel']}">Call {b['phone']}</a></p>
</form>"""


def footer(b, key, P):
    progs = ("Car Donation Foundation also runs Wheels For Wishes, benefiting Make-A-Wish; Wheels For Wishes &amp; Wellness, "
             "benefiting local children's hospitals and charities; and Animal Car Donation, benefiting animal rescue organizations.") if key == "vfv" else (
             "Car Donation Foundation also runs Vehicles For Veterans, benefiting disabled veterans; Wheels For Wishes &amp; Wellness, "
             "benefiting local children's hospitals and charities; and Animal Car Donation, benefiting animal rescue organizations.")
    ein = f"<li>EIN: {b['ein']}</li>" if b["ein"] else ""
    return f"""<footer class="site-footer"><div class="wrap">
<div class="cols">
<div><h2>We are a nonprofit</h2><p>{esc(b['nonprofit'])}</p><p>{progs}</p></div>
<div><h2>Donate</h2><ul><li><a href="{P}donate/index.html">Start my donation</a></li><li><a href="{P}how-it-works/index.html">How it works</a></li><li><a href="{P}faq/index.html">FAQ</a></li><li><a href="{P}states/index.html">Donate in your state</a></li></ul></div>
<div><h2>Contact</h2><ul><li><a href="tel:{b['tel']}">{b['phone']}</a></li><li>{esc(b['address'])}</li>{ein}</ul></div>
</div>
<div class="credit"><img src="{P}assets/img/spa-seal.webp" width="44" height="44" alt="Saint Paul Agency seal"><p style="margin:0">Design preview built by Saint Paul Agency for Car Donation Foundation. Not the live site.</p></div>
</div></footer>
"""


def sticky(b):
    return f"""<div class="sticky-cta" aria-hidden="false"><a class="btn" href="#start" data-to-start>Start my donation</a><a class="btn call" href="tel:{b['tel']}" aria-label="Call {b['phone']}">{ICON_PHONE}</a></div>
"""


def page(b, key, P, title, desc, path, body, with_sticky=False):
    return (head(b, key, P, title, desc, path) + header(b, key, P) + f'<main id="main">{body}</main>\n'
            + footer(b, key, P) + (sticky(b) if with_sticky else "") + "</body>\n</html>\n")


def trust(b, key, P):
    return f"""<section class="trust" aria-label="Why donate with us"><div class="wrap"><ul>
<li><img src="{P}assets/img/badge.webp" width="{56 if key == 'vfv' else 68}" height="56" alt="{esc(b['badge_alt'])}"><span>$200 million donated by Car Donation Foundation programs</span></li>
<li>{ICON_CHECK}<span>Free pickup, running or not</span></li>
<li>{ICON_CHECK}<span>Tax-deductible receipt</span></li>
<li>{ICON_CHECK}<span>501(c)(3) charity since 2010</span></li>
</ul></div></section>"""


def steps_section(b, P, soft=False):
    items = "".join(f"<li><div><h3>{esc(t)}</h3><p>{esc(d)}</p></div></li>" for t, d in b["steps"])
    return f"""<section class="section{' section-soft' if soft else ''}"><div class="wrap">
<h2>How it works</h2><p class="lead">Three steps, and the free pickup comes to you.</p>
<ol class="steps">{items}</ol>
</div></section>"""


def faq_list(b, n=None):
    qa = b["faq"][:n] if n else b["faq"]
    return "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in qa)


def accept_section(P):
    items = [("car.svg", "Cars and trucks"), ("motorcycle.svg", "Motorcycles"), ("ship.svg", "Boats"), ("rv.svg", "RVs and campers")]
    lis = "".join(f'<li><img src="{P}assets/img/{i}" width="46" height="34" alt="">{t}</li>' for i, t in items)
    return f"""<section class="section"><div class="wrap">
<h2>What you can donate</h2><p class="lead">Running or not, most vehicles qualify.</p>
<ul class="accept">{lis}</ul></div></section>"""


def states_section(P, title="Donate in your state"):
    lis = "".join(f'<li><a href="{P}states/{slug(s)}/index.html">{s}</a></li>' for s in STATES)
    return f"""<section class="section section-soft"><div class="wrap"><h2>{title}</h2>
<p class="lead">Free pickup in all 50 states and Washington, D.C.</p><ul class="state-list">{lis}</ul></div></section>"""


def hero(b, key, P, h1=None, sub=None):
    h1 = h1 or b["hero_h1"]
    sub = sub or b["hero_sub"]
    points = "".join(f"<li>{ICON_CHECK}<span>{esc(p)}</span></li>" for p in b["hero_points"])
    if key == "vfv":
        left = f"""<div class="hero-copy"><h1>{esc(h1)}</h1><p class="hero-sub">{esc(sub)}</p>
<ul class="hero-points">{points}</ul>
<picture><source media="(min-width:960px)" srcset="{P}assets/img/hero-856.webp"><img class="hero-photo" src="{P}assets/img/hero-480.webp" width="856" height="662" alt="A veteran in uniform, seated in a wheelchair in front of an American flag" loading="lazy"></picture></div>"""
    else:
        left = f"""<div class="hero-media"><img src="{P}assets/img/hero-640.webp" srcset="{P}assets/img/hero-640.webp 640w, {P}assets/img/hero-1280.webp 1280w" sizes="(min-width:960px) 560px, 100vw" width="640" height="249" alt="Clara and her mother smiling outdoors" loading="lazy"><span class="hero-caption">Clara, 7, wished to go on a Disney cruise</span></div>
<div class="hero-copy"><h1>{esc(h1)}</h1><p class="hero-sub">{esc(sub)}</p><ul class="hero-points">{points}</ul></div>"""
    return f"""<section class="hero"><div class="wrap">{left}
<div class="hero-form">{start_card(b, P)}</div>
</div></section>"""


def home(b, key):
    P = ""
    if key == "vfv":
        impact = f"""<section class="section"><div class="wrap split">
<div><h2>Your car funds help for disabled veterans</h2>
<p class="lead">Proceeds help fund programs for veterans who need assistance: transition services, help for homeless veterans, advocacy, employment assistance and more.</p>
<ul class="facts"><li><strong>4.0 million</strong>veterans live with a service-connected disability</li><li><strong>40,000</strong>veterans are estimated to be homeless, according to HUD</li></ul></div>
<img src="{P}assets/img/veterans-photo.webp" width="1200" height="516" alt="A hand holding a photo of two smiling veterans" loading="lazy"></div></section>
<section class="section section-soft"><div class="wrap"><h2>What donors say</h2><div class="quotes">
<blockquote><p>“Your website was really easy, and the details offered on the page such as explaining about the tax deduction, no costs, etc, was very useful.”</p><footer>Amy Meadows, Toyota donor, California</footer></blockquote>
<blockquote><p>“The process was very easy. A well informed form and pick-up of the vehicle is a great option.”</p><footer>Steve Smith, Private First Class, California</footer></blockquote>
</div></div></section>"""
    else:
        kids = [("ethan", "Ethan, 6", "wished to be a garbage man"), ("chloe", "Chloe, 8", "wished to visit a dude ranch"),
                ("areice", "Areice, 5", "wished to be a pirate"), ("jack", "Jack, 14", "wished to ski in Aspen")]
        lis = "".join(f'<li><img src="{P}assets/img/wish-{k}.webp" width="300" height="300" alt="{n}" loading="lazy"><strong>{n}</strong>{w}</li>' for k, n, w in kids)
        impact = f"""<section class="section"><div class="wrap">
<h2>Cars like yours granted these wishes</h2>
<p class="lead">As of September 2026, donors have helped Wheels For Wishes raise $125,695,697 and grant more than 14,673 wishes.</p>
<ul class="wishes">{lis}</ul></div></section>
<section class="section section-soft"><div class="wrap split">
<img src="{P}assets/img/check.webp" width="900" height="601" alt="A family holding a large Car Donation Foundation check made out to Make-A-Wish" loading="lazy">
<div><h2>Every wish starts in your community</h2><p class="lead">Wheels For Wishes benefits Make-A-Wish chapters across the United States, helping grant wishes for children in their local communities who have critical illnesses.</p>
<p>A wish gives a child a chance to focus on something other than medical routines, and be a kid again.</p></div></div></section>"""
    body = (hero(b, key, P) + trust(b, key, P) + steps_section(b, P) + impact + accept_section(P)
            + f"""<section class="section"><div class="wrap"><h2>Questions donors ask</h2>{faq_list(b, 4)}<p style="margin-top:20px"><a href="{P}faq/index.html">See all questions</a></p></div></section>"""
            + states_section(P)
            + f"""<section class="section cta-band"><div class="wrap"><h2>Ready to donate your vehicle?</h2><p>Three short screens, then the free pickup comes to you.</p><a class="btn" href="{P}donate/index.html">Start my donation</a></div></section>""")
    return page(b, key, P, b["title"], b["description"], "", body, with_sticky=True)


def year_options():
    yrs = "".join(f"<option>{y}</option>" for y in range(2027, 1979, -1))
    return f'<option value="">Year</option>{yrs}<option>Older</option>'


def donate(b, key):
    P = "../"
    states = "".join(f'<option value="{a}">{s}</option>' for s, a in zip(STATES, ABBR))
    makes = "".join(f"<option value=\"{m}\">" for m in MAKES)
    body = f"""<section class="donate-main"><div class="wrap"><div class="donate-box">
<div class="progress"><p class="progress-text" aria-live="polite">Step 1 of 3</p><div class="progress-bar" aria-hidden="true"><span class="done"></span><span></span><span></span></div></div>
<form id="donate-form" novalidate data-done="thank-you/index.html">
<div class="step">
<h2>What are you donating?</h2>
<fieldset data-check="radio" data-msg="Choose what you are donating."><legend>Vehicle type</legend>{tiles('d').replace('{P}', P)}</fieldset>
<div class="field" data-check="zip" data-msg="Enter the 5-digit ZIP code where we pick up the vehicle."><label for="zip1">Pickup ZIP code</label><input type="text" id="zip1" name="zip" inputmode="numeric" autocomplete="postal-code" data-digits="5"></div>
<div class="actions"><button class="btn" type="button" data-next>Continue</button></div>
</div>
<div class="step" hidden>
<h2>Who should we contact about pickup?</h2>
<div class="row row-2">
<div class="field" data-check="text" data-msg="Enter your first name."><label for="first">First name</label><input type="text" id="first" name="first" autocomplete="given-name"></div>
<div class="field" data-check="text" data-msg="Enter your last name."><label for="last">Last name</label><input type="text" id="last" name="last" autocomplete="family-name"></div>
</div>
<div class="field" data-check="phone" data-msg="Enter a 10-digit phone number."><label for="phone">Mobile phone</label><input type="tel" id="phone" name="phone" inputmode="tel" autocomplete="tel-national"></div>
<div class="field" data-check="email" data-msg="Enter an email address, like name@example.com."><label for="email">Email</label><input type="email" id="email" name="email" inputmode="email" autocomplete="email"></div>
<label class="check"><input type="checkbox" name="texts" checked><span>Text me updates about my pickup</span></label>
<div class="actions"><button class="btn btn-secondary" type="button" data-back>Back</button><button class="btn" type="button" data-next>Continue</button></div>
</div>
<div class="step" hidden>
<h2>Where is the vehicle?</h2>
<div class="field" data-check="text" data-msg="Enter the street address for pickup."><label for="street">Pickup street address</label><input type="text" id="street" name="street" autocomplete="street-address"></div>
<div class="row row-3">
<div class="field" data-check="text" data-msg="Enter the city."><label for="city">City</label><input type="text" id="city" name="city" autocomplete="address-level2"></div>
<div class="field" data-check="text" data-msg="Choose the state."><label for="state">State</label><select id="state" name="state" autocomplete="address-level1"><option value="">State</option>{states}</select></div>
<div class="field" data-check="zip" data-msg="Enter a 5-digit ZIP code."><label for="zip3">ZIP code</label><input type="text" id="zip3" name="zip" inputmode="numeric" autocomplete="postal-code" data-digits="5"></div>
</div>
<div class="row row-3">
<div class="field" data-check="text" data-msg="Choose the year."><label for="year">Year</label><select id="year" name="year">{year_options()}</select></div>
<div class="field" data-check="text" data-msg="Enter the make."><label for="make">Make</label><input type="text" id="make" name="make" list="makes" autocomplete="off"><datalist id="makes">{makes}</datalist></div>
<div class="field" data-check="text" data-msg="Enter the model."><label for="model">Model</label><input type="text" id="model" name="model" autocomplete="off"></div>
</div>
<fieldset class="field" data-check="radio" data-msg="Tell us whether you have the title."><legend class="label">Do you have the title?</legend>
<div class="radio-row"><input type="radio" id="t-yes" name="title" value="yes"><label for="t-yes">Yes</label><input type="radio" id="t-no" name="title" value="no"><label for="t-no">No</label><input type="radio" id="t-unsure" name="title" value="unsure"><label for="t-unsure">Not sure</label></div></fieldset>
<div class="actions"><button class="btn btn-secondary" type="button" data-back>Back</button><button class="btn" type="submit">Submit my donation</button></div>
<p class="preview-note">Preview only: this form doesn't send your information anywhere.</p>
</div>
</form>
<p class="talk">Prefer to talk? <a href="tel:{b['tel']}">Call {b['phone']}</a></p>
</div></div></section>"""
    return page(b, key, P, f"Donate your vehicle | {b['name']}", b["description"], "donate/", body)


def thanks(b, key):
    P = "../../"
    body = f"""<section class="donate-main"><div class="wrap"><div class="donate-box thanks" data-thanks>
<div class="big-check">{ICON_CHECK}</div>
<h1 style="font-size:2.25rem">Thank you<span data-name></span>!</h1>
<p class="lead" style="margin:0 auto">Your donation is started. Here's what happens next:</p>
<ol><li>The pickup team contacts you to schedule a time.</li><li>Your vehicle is picked up for free, running or not.</li><li>You receive your tax receipt by mail.</li></ol>
<p class="preview-note">Preview only: nothing was sent. In the live site, this page also confirms the details NFM received.</p>
<p><a href="{P}index.html">Back to the home page</a></p>
</div></div></section>"""
    return page(b, key, P, f"Thank you | {b['name']}", b["description"], "donate/thank-you/", body)


def how(b, key):
    P = "../"
    body = f"""<section class="page-hero"><div class="wrap"><p class="crumbs"><a href="{P}index.html">Home</a></p><h1>How car donation works</h1><p>Donating takes three short screens online. Pickup is free, and you get a tax-deductible receipt.</p></div></section>
{steps_section(b, P)}
<section class="section section-soft"><div class="wrap"><h2>What you need before pickup</h2>
<ul class="facts"><li><strong>The title</strong>If you can't find it, say so on the form. The team explains what your state requires.</li><li><strong>The keys</strong>If you have them. Vehicles without keys can often still be picked up.</li><li><strong>Personal items out</strong>Clear the glove box, trunk and console before pickup day.</li></ul></div></section>
<section class="section cta-band"><div class="wrap"><h2>Start your donation</h2><p>Pick your vehicle type and pickup ZIP to begin.</p><a class="btn" href="{P}donate/index.html">Start my donation</a></div></section>"""
    return page(b, key, P, f"How car donation works | {b['name']}", b["description"], "how-it-works/", body)


def faq(b, key):
    P = "../"
    body = f"""<section class="page-hero"><div class="wrap"><p class="crumbs"><a href="{P}index.html">Home</a></p><h1>Car donation questions</h1><p>Answers drawn from the current site. CDF approves final wording before launch.</p></div></section>
<section class="section"><div class="wrap" style="max-width:820px">{faq_list(b)}</div></section>
<section class="section cta-band"><div class="wrap"><h2>Ready when you are</h2><a class="btn" href="{P}donate/index.html">Start my donation</a></div></section>"""
    return page(b, key, P, f"Car donation FAQ | {b['name']}", b["description"], "faq/", body)


def states_index(b, key):
    P = "../"
    body = f"""<section class="page-hero"><div class="wrap"><p class="crumbs"><a href="{P}index.html">Home</a></p><h1>Donate a car in your state</h1><p>Free pickup in all 50 states and Washington, D.C. Choose your state to start.</p></div></section>
{states_section(P, "Choose your state")}"""
    return page(b, key, P, f"Donate a car in your state | {b['name']}", b["description"], "states/", body)


def state_page(b, key, state):
    P = "../../"
    if key == "vfv":
        h1 = f"Donate your car in {state} to help disabled veterans"
        sub = f"Free pickup anywhere in {state}, running or not."
        para = f"Vehicles For Veterans picks up donated cars, trucks, boats, RVs and motorcycles across {state} at no cost to you. Proceeds go to charities that help disabled veterans, and you get an IRS tax receipt for your records."
    else:
        h1 = f"Donate your car in {state} and help a local child"
        sub = f"Free pickup anywhere in {state}, running or not."
        para = f"Wheels For Wishes picks up donated vehicles across {state} at no cost to you. Proceeds benefit Make-A-Wish, granting wishes to children with critical illnesses, and you get a tax-deductible receipt."
    body = (hero(b, key, P, h1=h1, sub=sub)
            + f"""<section class="section"><div class="wrap"><h2>Car donation in {state}</h2><p class="lead">{esc(para)}</p>
<p>This is the template for every state page. In the rebuild, each one keeps its current web address, so search rankings carry over.</p></div></section>"""
            + steps_section(b, P, soft=True)
            + f"""<section class="section"><div class="wrap"><h2>Questions donors ask</h2>{faq_list(b, 3)}</div></section>""")
    return page(b, key, P, f"Donate a car in {state} | {b['name']}", f"Donate your car in {state}. Free pickup, running or not, and a tax-deductible receipt.", f"states/{slug(state)}/", body, with_sticky=True)


def not_found(b, key):
    P = ""
    body = f"""<section class="page-hero"><div class="wrap"><h1>We can't find that page</h1><p>The page may have moved. Start from the home page, or go straight to the donation form.</p><p style="margin-top:20px"><a class="btn" href="{P}donate/index.html">Start my donation</a></p></div></section>"""
    return page(b, key, P, f"Page not found | {b['name']}", b["description"], "404", body)


README = """# {name} — website rebuild preview

A design preview of a rebuilt **{domain}**, made by Saint Paul Agency for Car Donation Foundation.
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
- `assets/`: CSS, JavaScript, fonts (Lato and {head_font}, SIL Open Font License) and images from the current site.
- `_build/`: the scripts that generated this site (`python3 _build/build.py {key} .`).

## View it
Open `index.html` in a browser, or turn on GitHub Pages for this repo (Settings → Pages → Deploy from branch → `main` / root).

Design preview built by Saint Paul Agency and aidanbarnard.com.
"""


def build(key, out):
    b = BRANDS[key]
    out = Path(out)
    for sub in ["assets/css", "assets/js", "assets/fonts", "assets/img"]:
        (out / sub).mkdir(parents=True, exist_ok=True)
    (out / "assets/css/site.css").write_text(css(b) + brand_css_extra(key))
    (out / "assets/js/site.js").write_text(JS)
    for f in ["lato-latin-400-normal.woff2", "lato-latin-700-normal.woff2", "lato-latin-900-normal.woff2", b["head_file"]]:
        shutil.copy(HERE / "src" / f, out / "assets/fonts" / f)
    shutil.copy(HERE / "src" / "spa-seal-104.webp", out / "assets/img/spa-seal.webp")
    if key == "vfv":
        (out / "assets/img/chevrons.svg").write_text(CHEVRON_SVG)
    pages = {
        "index.html": home(b, key),
        "404.html": not_found(b, key),
        "donate/index.html": donate(b, key),
        "donate/thank-you/index.html": thanks(b, key),
        "how-it-works/index.html": how(b, key),
        "faq/index.html": faq(b, key),
        "states/index.html": states_index(b, key),
    }
    for s in STATES:
        pages[f"states/{slug(s)}/index.html"] = state_page(b, key, s)
    for rel, content in pages.items():
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    (out / "README.md").write_text(README.format(name=b["name"], domain=b["domain"], head_font=b["head_font"], key=key))
    bd = out / "_build"
    bd.mkdir(exist_ok=True)
    if bd.resolve() != HERE:
        shutil.copy(HERE / "build.py", bd / "build.py")
        shutil.copy(HERE / "prep_images.py", bd / "prep_images.py")
        (bd / "src").mkdir(exist_ok=True)
        shutil.copytree(HERE / "src" / key, bd / "src" / key, dirs_exist_ok=True)
        for f in ["lato-latin-400-normal.woff2", "lato-latin-700-normal.woff2", "lato-latin-900-normal.woff2",
                  b["head_file"], "spa-seal-104.webp"]:
            shutil.copy(HERE / "src" / f, bd / "src" / f)
    print(f"built {key}: {len(pages)} pages -> {out}")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
