"""Build a static design preview for Vehicles For Veterans (vfv) or Wheels For Wishes (wfw).

Usage: python3 build.py <vfv|wfw> <out_dir>

Writes plain HTML, CSS and JS with relative links, so the site works from any folder,
including a GitHub Pages project URL. The donation form is a demo: it never sends data.
"""
import html
import re
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
        "hero_points": ["Free towing anywhere in the U.S.", "Cars, trucks, boats, RVs, motorcycles and more", "A 501(c)(3) charity, giving since 2010"],
        "cause_short": "disabled veterans",
        "badge_alt": "Car Donation Foundation badge: $200 million donated",
        "steps": [
            ("Tell us about your vehicle", "Pick the vehicle type, add your pickup ZIP and contact details. It's three short screens."),
            ("Schedule your free pickup", "Your donation goes to the nearest auction partner, who contacts you to schedule the pickup."),
            ("Get your tax receipt", "You receive an IRS tax receipt for your records."),
        ],
        "faq": [
            ("Is my donation tax-deductible?", "Yes. Car Donation Foundation is a tax-exempt charity under section 501(c)(3) of the IRS Code, and you receive an IRS tax receipt for your records. Ask your tax advisor how the deduction applies to you."),
            ("Does my vehicle need to run?", "No. Pickup is free whether the vehicle runs or not."),
            ("What can I donate?", "Cars, trucks, motorcycles, boats, RVs, campers and ATVs."),
            ("How does pickup work?", "Your donation is assigned to the nearest auction partner, who contacts you to schedule the pickup at a time that suits you."),
            ("Do I need the title?", "Tell us on the form whether you have the title. Title rules vary by state, so ask when you're contacted about pickup."),
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
        "hero_sub": "Proceeds benefit Make-A-Wish.",
        "hero_points": ["Free towing anywhere in the U.S.", "A tax-deductible receipt for your donation", "Most vehicles accepted, regardless of condition"],
        "cause_short": "local children",
        "badge_alt": "Car Donation Foundation badge: $200 million total donated across all charitable donations",
        "steps": [
            ("Tell us about your vehicle", "Pick the vehicle type, add your pickup ZIP and contact details. It's three short screens."),
            ("Get free towing", "Within 24 hours (by the next business day), you're contacted to schedule free towing."),
            ("Get your tax receipt", "You get a tax-deductible receipt, and your car donation helps local children."),
        ],
        "faq": [
            ("Is my donation tax-deductible?", "Yes. Wheels For Wishes is a tax-exempt charity under Section 501(c)(3) of the IRS Code, and you receive a tax-deductible receipt. Ask your tax advisor how the deduction applies to you."),
            ("Does my vehicle need to run?", "Wheels For Wishes accepts most vehicles regardless of condition, and towing is free."),
            ("What can I donate?", "Cars, trucks, motorcycles, boats, RVs and motorhomes."),
            ("How does pickup work?", "Within 24 hours (by the next business day), you're contacted to schedule free towing. Your vehicle is picked up free of charge."),
            ("Do I need the title?", "Tell us on the form whether you have the title. Title rules vary by state, so ask when you're contacted about pickup."),
            ("How does my car help a child?", "Proceeds from donated cars go to Wheels For Wishes, benefiting Make-A-Wish chapters in various locations throughout the United States. They help grant wishes for children in their local communities who have been diagnosed with life-threatening medical conditions."),
        ],
        "nonprofit": "Proceeds from donated cars go to Wheels For Wishes, a tax-exempt charity under Section 501(c)(3) of the IRS Code, benefiting Make-A-Wish chapters in locations throughout the United States.",
        "ein": "26-3408048",
        "address": "5775 Wayzata Boulevard, Suite 700, St. Louis Park, MN 55416",
    },
}

MAKES = ["Acura", "Audi", "BMW", "Buick", "Cadillac", "Chevrolet", "Chrysler", "Dodge", "Ford", "GMC", "Honda",
         "Hyundai", "Infiniti", "Jeep", "Kia", "Lexus", "Lincoln", "Mazda", "Mercedes-Benz", "Mercury", "Mini",
         "Mitsubishi", "Nissan", "Pontiac", "Ram", "Saturn", "Subaru", "Tesla", "Toyota", "Volkswagen", "Volvo"]

ICON_CHECK = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M9.5 16.2 5.3 12l-1.4 1.4 5.6 5.6L20.1 8.4 18.7 7z"/></svg>'
ICON_PHONE = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>'


def icon_svg(file):
    """Inline a Font Awesome duotone icon from the live site so CSS can color both tones."""
    raw = (HERE / "src" / "vfv" / file).read_text()
    raw = re.sub(r'<svg[^>]*viewBox="([^"]+)"[^>]*>', r'<svg class="vic" viewBox="\1" aria-hidden="true" focusable="false">', raw, count=1)
    return raw.replace(' fill="currentColor"', "").replace(' opacity="0.4"', "")


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
/* start card */
.start-card{{background:#fff;color:var(--ink);border-radius:var(--r);padding:20px;box-shadow:0 18px 40px -18px rgba(8,16,40,.55);border:1px solid var(--line)}}
.start-card h2{{font-size:1.5rem;margin-bottom:12px}}
fieldset{{border:0;margin:0;padding:0;min-width:0}}
legend{{font-weight:900;font-size:1.125rem;padding:0;margin-bottom:10px}}
.tiles{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.tile{{position:relative}}
.tile input{{position:absolute;opacity:0;width:1px;height:1px}}
.tile label{{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;min-height:84px;padding:8px 6px;border:2px solid var(--line);border-radius:12px;cursor:pointer;text-align:center;font-weight:700;font-size:1rem;line-height:1.2;background:#fff}}
.vic{{display:block}}.vic .fa-primary{{fill:var(--icon1)}}.vic .fa-secondary{{fill:var(--icon2);opacity:1}}
.tile .vic{{width:42px;height:32px}}
.tile input:checked+label{{border-color:var(--brand);background:var(--soft);box-shadow:inset 0 0 0 2px var(--brand)}}
.tile input:focus-visible+label{{outline:3px solid var(--brand);outline-offset:2px}}
.field{{margin-top:16px}}
.field label,.label{{display:block;font-weight:900;font-size:1.0625rem;margin-bottom:6px}}
.field .hint{{display:block;font-size:1rem;color:var(--ink2);margin:-2px 0 6px}}
input[type=text],input[type=tel],input[type=email],input[type=search],select{{width:100%;font:400 1.1875rem var(--body);color:var(--ink);background:#fff;border:2px solid #5B667A;border-radius:10px;padding:12px 14px;min-height:56px}}
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
.steps li{{display:grid;grid-template-columns:64px 1fr;gap:18px;align-items:start;counter-increment:s}}
.steps li::before{{content:counter(s);display:grid;place-items:center;width:64px;height:64px;border-radius:50%;background:var(--step-bg,var(--navy));color:var(--step-ink,#fff);font:{b['head_weight']} 2rem/1 var(--head)}}
.steps h3{{margin:6px 0 4px}}
.steps p{{margin:0}}
.split{{display:grid;gap:28px;align-items:center}}
.split img{{border-radius:var(--r)}}
.facts{{display:grid;gap:14px;margin:22px 0 0;padding:0;list-style:none}}
.facts li{{border-left:6px solid var(--brand);padding:6px 0 6px 16px}}
.facts strong{{display:block;font:{b['head_weight']} 2rem/1.1 var(--head);color:var(--navy)}}
.quotes{{display:grid;gap:18px;margin-top:24px}}
blockquote{{margin:0;background:#fff;border:2px solid var(--line);border-radius:var(--r);padding:22px 22px 20px;position:relative}}
blockquote::before{{content:"\\201C";display:block;font:900 5rem/.6 Georgia,serif;color:var(--brand);height:38px;margin-bottom:8px}}
blockquote p{{font-size:1.1875rem}}
blockquote footer{{font-weight:900}}
.wishes{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;margin-top:24px;list-style:none;padding:0}}
.wishes img{{border-radius:50%;width:100%;max-width:220px;aspect-ratio:1;object-fit:cover;margin:0 auto 12px;border:7px solid var(--ring,var(--accent))}}
.wishes li{{text-align:center;font-size:1.0625rem}}
.wishes strong{{display:block;font-size:1.1875rem}}
.accept{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;list-style:none;padding:0;margin:24px 0 0}}
.accept li{{display:flex;flex-direction:column;align-items:center;text-align:center;gap:10px;background:#fff;border:2px solid var(--line);border-radius:16px;padding:20px 10px 16px;font-weight:900;font-size:1.0625rem}}
.accept .vic{{width:60px;height:48px}}
details{{border-bottom:2px solid var(--line);padding:4px 0}}
summary{{cursor:pointer;font-weight:900;font-size:1.1875rem;padding:14px 0;list-style:none;display:flex;justify-content:space-between;gap:16px}}
summary::-webkit-details-marker{{display:none}}
summary::after{{content:"+";font-size:1.5rem;line-height:1;color:var(--brand)}}
details[open] summary::after{{content:"–"}}
details p{{margin:0 0 16px}}
.state-list{{display:flex;flex-wrap:wrap;gap:10px;list-style:none;padding:0;margin:22px 0 0}}
.state-list a{{display:inline-flex;align-items:center;min-height:44px;padding:8px 16px;border:2px solid var(--line);border-radius:999px;background:#fff;font-weight:700;font-size:1rem;color:var(--ink);text-decoration:none}}
.state-list a:hover{{border-color:var(--brand);color:var(--ink);background:var(--soft)}}
.cta-band{{background:var(--navy);color:#fff;text-align:left;position:relative;overflow:hidden}}
.cta-band .wrap{{position:relative;z-index:1}}
.cta-band h2{{color:#fff;font-size:clamp(2rem,5.2vw,3rem)}}
.cta-band p{{font-size:1.25rem;font-weight:700}}
.btn-invert{{background:#fff;color:var(--brand-dark)}}.btn-invert:hover{{background:var(--soft);color:var(--brand-dark)}}
.btn-sun{{background:#F7D132;color:#151B2E}}.btn-sun:hover{{background:#FFE15C;color:#151B2E}}
/* stat band */
.band{{color:#fff;position:relative;overflow:hidden}}
.band h2{{color:#fff}}
.band .lead{{color:#fff}}
.band .wrap{{position:relative;z-index:1}}
.big-stats{{list-style:none;margin:30px 0 0;padding:0;display:grid;gap:26px}}
.big-stats li{{display:flex;flex-direction:column;gap:6px;padding-left:18px;border-left:6px solid var(--stat-rule,#fff)}}
.big-stats strong{{font:{b['head_weight']} clamp(2.6rem,10.5vw,4.25rem)/1 var(--head);color:#fff;letter-spacing:-.01em;white-space:nowrap}}
.big-stats span{{font-size:1.1875rem;font-weight:700;max-width:30ch}}
.source{{font-size:1rem;margin:28px 0 0;max-width:80ch;color:#fff}}
.stars{{display:flex;gap:8px;margin:0 0 10px}}
.stars svg{{width:22px;height:22px;fill:#E8283F}}
.heart{{position:absolute;pointer-events:none;z-index:0}}
.heart svg{{width:100%;height:100%;fill:currentColor;display:block}}
.wave{{position:absolute;left:0;right:0;bottom:-1px;width:100%;height:34px;display:block;z-index:1}}
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
  .big-stats{{grid-template-columns:1fr 1fr;gap:40px}}
  .steps{{grid-template-columns:repeat(3,1fr);gap:32px}}
  .start-card{{padding:28px}}
  .tiles{{grid-template-columns:repeat(5,1fr)}}
  .trust ul{{grid-template-columns:repeat(4,1fr)}}
  .split{{grid-template-columns:1fr 1fr;gap:56px}}
  .site-footer .cols{{grid-template-columns:1.4fr 1fr 1fr}}
  .site-footer{{padding-bottom:44px}}
  .sticky-cta{{display:none}}
  .state-list{{columns:4}}
  .accept{{grid-template-columns:repeat(4,1fr)}}
  .section{{padding:80px 0}}
}}
@keyframes rise{{from{{transform:translateY(28px)}}to{{transform:none}}}}
.hero-form .start-card{{animation:rise .7s cubic-bezier(.2,.8,.2,1) both}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important;animation:none!important;scroll-behavior:auto!important}}}}
"""


def brand_css_extra(key):
    if key == "vfv":
        return """:root{--icon1:#0F2747;--icon2:#C8102E;--step-bg:#C8102E}
.hero{--hero-bg:#0F2747;background:#0F2747}
.hero::before,.hero::after{content:"";position:absolute;left:0;right:0;top:0;height:360px;z-index:0}
.hero::before{background:url(../img/hero-480.webp) 70% 0/cover no-repeat}
.hero::after{background:linear-gradient(180deg,rgba(15,39,71,.55) 0,rgba(15,39,71,.78) 52%,#0F2747 100%)}
.hero .wrap{z-index:1}
.hero h1{color:#fff;font-size:clamp(2.3rem,9.2vw,4.4rem);line-height:1.04;text-shadow:0 2px 16px rgba(4,12,28,.6)}
.hero .hero-sub{color:#fff;text-shadow:0 1px 10px rgba(4,12,28,.6)}
.hero-points .ico{color:#78C8F8}
.hero-points li{font-weight:700}
.trust .ico{color:#C8102E}
.band-vfv{background:#0F2747;--stat-rule:#E8283F}
.cta-vfv{background:#C8102E}
.cta-vfv h2,.cta-vfv p{max-width:20ch}.cta-vfv p{max-width:34ch}
.framed{box-shadow:14px 14px 0 #C8102E;border-radius:var(--r)}
@media (min-width:960px){
.hero{background:#0F2747 url(../img/chevrons.svg) right -60px top -90px/540px no-repeat}
.hero::before,.hero::after{right:auto;width:58%;height:auto;bottom:0}
.hero::before{background:url(../img/hero-856.webp) 50% 30%/cover no-repeat}
.hero::after{background:linear-gradient(90deg,rgba(15,39,71,.82) 0,rgba(15,39,71,.6) 60%,rgba(15,39,71,.92) 90%,#0F2747 100%)}
.hero .wrap{padding-top:64px;padding-bottom:72px}
.band-vfv{background:#0F2747 url(../img/chevrons.svg) right -150px top -120px/460px no-repeat}
.band-vfv .wrap{padding-right:300px}
.cta-vfv{background:#C8102E url(../img/chevrons-light.svg) right -20px center/480px no-repeat}
}
"""
    return """:root{--icon1:#1C3A8A;--icon2:#C2255C}
.hero{--hero-bg:#F7D132;background:#F7D132}
.hero .wrap{grid-template-areas:"copy" "form" "media";padding-bottom:58px;z-index:1}
.hero-copy{grid-area:copy}.hero-form{grid-area:form}
.hero h1{font-size:clamp(2.3rem,9vw,3.9rem);line-height:1.08}
.hero-media{grid-area:media;position:relative}
.hero-media img{width:100%;height:200px;object-fit:cover;object-position:62% 35%;border-radius:20px;border:5px solid #fff}
.hero-caption{position:absolute;left:14px;bottom:12px;background:#fff;color:#151B2E;font-weight:700;font-size:1rem;line-height:1.3;border-radius:999px;padding:6px 14px;max-width:calc(100% - 28px)}
.hero-points .ico{color:#C2255C}
.hero-points li{font-weight:700}
.avatars{display:flex;align-items:center;gap:12px;margin-top:14px}
.faces{display:flex;flex:none}
.faces img{width:40px;height:40px;border-radius:50%;border:3px solid #fff;margin-left:-10px;object-fit:cover}
.faces img:first-child{margin-left:0}
.avatars p{margin:0;font-weight:900;font-size:1rem;line-height:1.3}
.wave path{fill:#EEF3FC}
.heart.h1{color:#C2255C;width:40px;height:40px;top:14px;right:14px;transform:rotate(14deg)}
.heart.h2{display:none;color:#1E8C82}
.heart.h3{color:#F7D132;width:120px;height:120px;right:-28px;bottom:-26px;transform:rotate(-12deg)}
.heart.h4{color:#C2255C;width:110px;height:110px;right:-20px;top:-24px;transform:rotate(16deg)}
.trust .ico{color:#C2255C}
.steps li:nth-child(1){--step-bg:#F7D132;--step-ink:#151B2E}
.steps li:nth-child(2){--step-bg:#C2255C}
.steps li:nth-child(3){--step-bg:#1C3A8A}
.band-wfw{background:#C2255C;--stat-rule:#F7D132}
.wishes li:nth-child(4n+1){--ring:#F7D132}
.wishes li:nth-child(4n+2){--ring:#C2255C}
.wishes li:nth-child(4n+3){--ring:#1E8C82}
.wishes li:nth-child(4n+4){--ring:#1C3A8A}
.cta-wfw{background:#1C3A8A}
.framed{box-shadow:14px 14px 0 #F7D132;border-radius:var(--r)}
@media (max-width:420px){.hero h1{padding-right:34px}}
@media (min-width:960px){
.hero .wrap{grid-template-areas:"media form" "copy form";align-items:start;row-gap:28px;padding-bottom:84px}
.hero-form{align-self:center}.hero-media img{height:250px}.hero-caption{left:18px;bottom:18px}
.heart.h1{width:64px;height:64px;top:28px;right:auto;left:calc(50% - 40px)}
.heart.h2{display:block;width:40px;height:40px;top:auto;bottom:70px;left:calc(50% - 6px);transform:rotate(-16deg)}
.wave{height:56px}
.heart.h3{width:220px;height:220px;right:-40px;bottom:-50px}
.heart.h4{width:200px;height:200px;right:4%;top:-40px}
}
"""


STARS = '<div class="stars" aria-hidden="true">' + ''.join('<svg viewBox="0 0 24 24"><path d="M12 2l2.9 6.9 7.1.6-5.4 4.7 1.7 7-6.3-3.9-6.3 3.9 1.7-7L2 9.5l7.1-.6z"/></svg>' for _ in range(3)) + '</div>'
HEART = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7.5-4.6-9.6-9.2C.8 8.3 2.9 4.5 6.6 4.5c2.1 0 3.6 1.1 5.4 3.1 1.8-2 3.3-3.1 5.4-3.1 3.7 0 5.8 3.8 4.2 7.3C19.5 16.4 12 21 12 21z"/></svg>'
WAVE = '<svg class="wave" viewBox="0 0 1440 60" preserveAspectRatio="none" aria-hidden="true"><path d="M0 34C200 66 420 4 720 28s520 34 720 2v30H0z"/></svg>'


CHEVRON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"><g fill="none" stroke-width="44"><path d="M20 120 200 300 380 120" stroke="#C8102E"/><path d="M20 210 200 390 380 210" stroke="#78C8F8"/><path d="M20 30 200 210 380 30" stroke="#1D3E6B"/></g></svg>"""
CHEVRON_RED_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"><g fill="none" stroke-width="44"><path d="M20 120 200 300 380 120" stroke="#FFFFFF"/><path d="M20 210 200 390 380 210" stroke="#78C8F8"/><path d="M20 30 200 210 380 30" stroke="#0F2747"/></g></svg>"""


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
<script>document.documentElement.className+=" js"</script>
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
{('<link rel="preload" as="image" href="' + P + 'assets/img/hero-480.webp" media="(max-width:959px)">' + chr(10) + '<link rel="preload" as="image" href="' + P + 'assets/img/hero-856.webp" media="(min-width:960px)">') if key == 'vfv' else ''}
<link rel="stylesheet" href="{P}assets/css/site.css">
<script src="{P}assets/js/site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="preview-bar"><div class="wrap"><img src="{P}assets/img/spa-seal.webp" width="28" height="28" alt=""><span class="pb-long">Design preview by Saint Paul Agency. This is not the live site, and the form doesn't send any data.</span><span class="pb-short">Design preview. Not the live site.</span></div></div>
"""


def tiles(name_prefix, checked=None):
    out = ['<div class="tiles">']
    for val, label, icon in VEHICLES:
        idp = f"{name_prefix}-{val}"
        chk = " checked" if checked == val else ""
        out.append(f'<div class="tile"><input type="radio" name="vehicle" id="{idp}" value="{val}"{chk}>'
                   f'<label for="{idp}">{icon_svg(icon.replace(".svg", "-duotone.svg"))}{label}</label></div>')
    out.append("</div>")
    return "".join(out)


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


def steps_section(b, P, soft=False):
    items = "".join(f"<li><div><h3>{esc(t)}</h3><p>{esc(d)}</p></div></li>" for t, d in b["steps"])
    return f"""<section class="section steps-section{' section-soft' if soft else ''}"><div class="wrap">
<h2>How it works</h2><p class="lead">Three steps, and the free pickup comes to you.</p>
<ol class="steps">{items}</ol>
</div></section>"""


def faq_list(b, n=None):
    qa = b["faq"][:n] if n else b["faq"]
    return "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in qa)


def accept_section(P):
    items = [("car-duotone.svg", "Cars and trucks"), ("motorcycle-duotone.svg", "Motorcycles"), ("ship-duotone.svg", "Boats"), ("rv-duotone.svg", "RVs and campers")]
    lis = "".join(f"<li>{icon_svg(i)}{t}</li>" for i, t in items)
    return f"""<section class="section"><div class="wrap">
<h2>What you can donate</h2><p class="lead">Most vehicles qualify, whatever the condition.</p>
<ul class="accept">{lis}</ul></div></section>"""


def states_section(P, title="Donate in your state"):
    lis = "".join(f'<li><a href="{P}states/{slug(s)}/index.html">{s}</a></li>' for s in STATES)
    return f"""<section class="section section-soft"><div class="wrap"><h2>{title}</h2>
<p class="lead">Free pickup in all 50 states and Washington, D.C.</p><ul class="state-list">{lis}</ul></div></section>"""


# ---------------------------------------------------------------------------
# NEXT-LEVEL DESIGN (v3): header, seal, hero, proof bands, journey, map, verify
# ---------------------------------------------------------------------------
import math

CHARITIES_VFV = ["USO", "Fisher House Foundation", "Homes For Our Troops", "Gary Sinise Foundation", "K9s For Warriors",
                 "Semper Fi Fund", "Folds of Honor", "Bob Woodruff Foundation", "Operation Homefront", "Team RWB",
                 "Student Veterans of America", "Travis Mills Foundation", "Pat Tillman Foundation", "Hope For The Warriors",
                 "Operation Gratitude", "TAPS", "Veterans Airlift Command", "America's Warrior Partnership",
                 "Oscar Mike Foundation", "FourBlock", "BraveHearts", "Intrepid Fallen Heroes Fund", "Soldiers To Sidelines",
                 "Military Spouse Advocacy Network", "wear blue: run to remember", "Warrior Bonfire Program",
                 "Minnesota Military Family Foundation", "Echo Hill Ranch", "Military Thriving", "Tee It Up for the Troops",
                 "Disabled American Veterans (DAV)"]

TILE_POS = {"AK": (0, 0), "ME": (0, 10), "VT": (1, 9), "NH": (1, 10),
            "WA": (2, 0), "ID": (2, 1), "MT": (2, 2), "ND": (2, 3), "MN": (2, 4), "IL": (2, 5), "WI": (2, 6), "MI": (2, 7), "NY": (2, 8), "RI": (2, 9), "MA": (2, 10),
            "OR": (3, 0), "NV": (3, 1), "WY": (3, 2), "SD": (3, 3), "IA": (3, 4), "IN": (3, 5), "OH": (3, 6), "PA": (3, 7), "NJ": (3, 8), "CT": (3, 9),
            "CA": (4, 0), "UT": (4, 1), "CO": (4, 2), "NE": (4, 3), "MO": (4, 4), "KY": (4, 5), "WV": (4, 6), "VA": (4, 7), "MD": (4, 8), "DE": (4, 9),
            "AZ": (5, 1), "NM": (5, 2), "KS": (5, 3), "AR": (5, 4), "TN": (5, 5), "NC": (5, 6), "SC": (5, 7), "DC": (5, 8),
            "OK": (6, 3), "LA": (6, 4), "MS": (6, 5), "AL": (6, 6), "GA": (6, 7),
            "HI": (7, 0), "TX": (7, 3), "FL": (7, 8)}

ICON_PIN = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>'
ICON_SHIELD = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2 4 5v6c0 5 3.4 9.7 8 11 4.6-1.3 8-6 8-11V5zm-1.2 14.2-3.5-3.5 1.4-1.4 2.1 2.1 4.9-4.9 1.4 1.4z"/></svg>'
ICON_RECEIPT = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 2h12a1 1 0 0 1 1 1v19l-3-2-3 2-3-2-3 2-2-1.3V3a1 1 0 0 1 1-1zm2 5v2h8V7zm0 4v2h8v-2zm0 4v2h5v-2z"/></svg>'
ICON_PIE = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M11 2.05V13h10.95A10 10 0 1 1 11 2.05zM13 2.05A10 10 0 0 1 21.95 11H13z"/></svg>'
ICON_HEART = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7.5-4.6-9.6-9.2C.8 8.3 2.9 4.5 6.6 4.5c2.1 0 3.6 1.1 5.4 3.1 1.8-2 3.3-3.1 5.4-3.1 3.7 0 5.8 3.8 4.2 7.3C19.5 16.4 12 21 12 21z"/></svg>'
ICON_TRUCK = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M2 5h12v9h1.6l1.4-4H21l1 3v5h-2a2.5 2.5 0 0 1-5 0H9a2.5 2.5 0 0 1-5 0H2zm16 6.5-.8 2.5H20v-.6l-.6-1.9zM6.5 19a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm11 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/></svg>'
ICON_STAR = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l2.9 6.9 7.1.6-5.4 4.7 1.7 7-6.3-3.9-6.3 3.9 1.7-7L2 9.5l7.1-.6z"/></svg>'
ICON_EXT = '<svg class="ico ext" viewBox="0 0 24 24" aria-hidden="true"><path d="M14 3h7v7h-2V6.4l-9.3 9.3-1.4-1.4L17.6 5H14zM5 5h6v2H7v10h10v-4h2v6H5z"/></svg>'


def scallop_path(cx, cy, r, n, amp):
    pts = []
    for i in range(n * 8):
        t = 2 * math.pi * i / (n * 8)
        rr = r + amp * math.cos(n * t)
        pts.append(f"{cx + rr * math.cos(t):.2f},{cy + rr * math.sin(t):.2f}")
    return "M" + " L".join(pts) + "Z"


def seal_svg(key):
    """Car Donation Foundation $200M seal, rebuilt as a crisp, animated SVG."""
    if key == "vfv":
        fill1, fill2, ink, num = "#F5B43A", "#FFD978", "#0F2747", "#C8102E"
        ring = "$200 MILLION DONATED ★ CAR DONATION FOUNDATION ★ "
        label = "Car Donation Foundation: $200 million donated"
        mid, low = "MILLION", "DONATED"
    else:
        fill1, fill2, ink, num = "#F5B43A", "#FFE27A", "#1C3A8A", "#C2255C"
        ring = "CAR DONATION FOUNDATION ★ ACROSS ALL CHARITABLE DONATIONS ★ "
        label = "Car Donation Foundation: $200 million total donated across all charitable donations"
        mid, low = "MILLION", "TOTAL DONATED"
    stars = "".join(
        f'<path d="M0-5 1.2-1.6 4.8-1.5 1.9.6 2.9 4 0 2 -2.9 4 -1.9.6 -4.8-1.5 -1.2-1.6Z" transform="translate({100 + 82 * math.cos(2 * math.pi * i / 16):.1f},{100 + 82 * math.sin(2 * math.pi * i / 16):.1f}) rotate({i * 22.5:.1f})" />'
        for i in range(16))
    return f"""<div class="seal" role="img" aria-label="{label}"><span class="seal-ring" aria-hidden="true"></span><span class="seal-ring r2" aria-hidden="true"></span>
<svg viewBox="0 0 200 200" aria-hidden="true" focusable="false"><defs><path id="ring-{key}" d="M100,100 m-80,0 a80,80 0 1,1 160,0 a80,80 0 1,1 -160,0"/>
<radialGradient id="sg-{key}" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="{fill2}"/><stop offset="1" stop-color="{fill1}"/></radialGradient></defs>
<path d="{scallop_path(100, 100, 94, 22, 4.5)}" fill="url(#sg-{key})" stroke="{ink}" stroke-width="2.5"/>
<circle cx="100" cy="100" r="66" fill="#FFF6D6" stroke="{ink}" stroke-width="2.5"/>
<g class="seal-spin"><g class="ring-text"><text font-size="15.5" font-weight="900" fill="{ink}" letter-spacing="1.4"><textPath href="#ring-{key}" textLength="500">{ring}</textPath></text></g>
<g class="ring-stars" fill="{ink}">{stars}</g></g>
<g class="seal-big" text-anchor="middle" font-weight="900"><text x="100" y="104" font-size="50" fill="{num}" letter-spacing="-1">$200</text>
<text x="100" y="127" font-size="20" fill="{ink}" letter-spacing="2">{mid}</text><text x="100" y="146" font-size="{15 if len(low) > 8 else 17}" fill="{ink}" letter-spacing="1">{low}</text></g>
<g class="seal-small" text-anchor="middle" font-weight="900"><text x="100" y="114" font-size="40" fill="{num}" letter-spacing="-1.5">$200M</text></g>
</svg><span class="seal-glint" aria-hidden="true"></span></div>"""


def header(b, key, P):
    if key == "wfw":
        logo = (f'<img class="logo-wfw" src="{P}assets/img/logo.svg" width="66" height="64" alt="{esc(b["name"])} home">'
                f'<img class="logo-maw" src="{P}assets/img/make-a-wish.webp" width="160" height="42" alt="Benefiting Make-A-Wish">')
    else:
        logo = f'<img src="{P}assets/img/logo.webp" width="136" height="64" alt="{esc(b["name"])} home">'
    return f"""<header class="site-header hdr-{key}"><span class="hdr-bg" aria-hidden="true"></span><div class="wrap">
<a class="logo" href="{P}index.html">{logo}</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
<nav id="site-nav" class="site-nav" aria-label="Main"><ul>
<li><a href="{P}how-it-works/index.html">How it works</a></li>
<li><a href="{P}faq/index.html">FAQ</a></li>
<li><a href="{P}states/index.html">Donate in your state</a></li>
<li><a class="nav-phone" href="tel:{b['tel']}">{ICON_PHONE}<span>{b['phone']}</span></a></li>
<li class="nav-cta"><a class="glint magnetic" href="{P}donate/index.html">Donate my car</a></li>
</ul></nav>
</div></header>
"""


def start_card(b, P, heading="What are you donating?", idp="s"):
    return f"""<div class="glow-frame"><form class="start-card" id="start" action="{P}donate/index.html" novalidate>
<p class="live-chip"><span class="dot" aria-hidden="true"></span>Free pickup in all 50 states</p>
<h2>{heading}</h2>
<fieldset><legend class="skip">Vehicle type</legend>{tiles(idp).replace('{P}', P)}</fieldset>
<div class="field"><label for="{idp}-zip">Pickup ZIP code</label>
<input type="text" id="{idp}-zip" name="zip" inputmode="numeric" autocomplete="postal-code" data-digits="5"></div>
<p class="form-error" role="alert" hidden></p>
<button class="btn btn-block glint" type="submit">Start my donation</button>
<p class="talk">Prefer to talk? <a href="tel:{b['tel']}">Call {b['phone']}</a></p>
</form></div>"""


def hero(b, key, P, h1=None, sub=None):
    h1 = h1 or b["hero_h1"]
    sub = sub or b["hero_sub"]
    points = "".join(f"<li>{ICON_CHECK}<span>{esc(p)}</span></li>" for p in b["hero_points"])
    if key == "vfv":
        copy = f"""<div class="hero-copy">{STARS}<h1 class="h-split">{esc(h1)}</h1><p class="hero-sub">{esc(sub)}</p>
<ul class="hero-points">{points}</ul></div>"""
        deco = '<span class="hero-photo" aria-hidden="true"></span><span class="hero-shade" aria-hidden="true"></span>'
    else:
        copy = f"""<div class="hero-copy"><h1 class="h-split">{esc(h1)}</h1><p class="hero-sub">{esc(sub)}</p>
<ul class="hero-points">{points}</ul></div>"""
        sparks = "".join(f'<i style="--x:{x}%;--y:{y}%;--s:{s}px;--d:{d}s"></i>' for x, y, s, d in
                         [(8, 18, 14, 0), (22, 62, 10, 1.2), (38, 12, 12, 2.1), (47, 48, 9, .6), (55, 22, 16, 1.7), (14, 40, 8, 2.6), (30, 30, 11, .9), (50, 70, 10, 2.3)])
        deco = (f'<span class="hero-photo" aria-hidden="true"><span class="hero-caption">Clara, 7, wished to go on a Disney cruise</span></span><span class="hero-shade" aria-hidden="true"></span>'
                f'<span class="sparks" aria-hidden="true">{sparks}</span><span class="shooting" aria-hidden="true"></span><span class="shooting s3" aria-hidden="true"></span>{WAVE}')
    media = "" if key == "vfv" else f'<div class="hero-media"><img src="{P}assets/img/hero-640.webp" width="640" height="249" alt="Clara and her mother smiling outdoors" loading="lazy"><span class="hero-caption">Clara, 7, wished to go on a Disney cruise</span></div>'
    return f"""<section class="hero hero-{key}">{deco}<div class="wrap">{copy}
<div class="hero-form">{seal_svg(key)}{start_card(b, P)}</div>{media}
</div></section>"""


def odo(value, label):
    cls = "odo long" if len(value) > 8 else "odo"
    return f'<strong class="{cls}" data-odo>{esc(value)}</strong>'


def trust(b, key, P):
    if key == "vfv":
        items = [(ICON_SHIELD, "<b>$202 million+</b> given by Car Donation Foundation programs since 2010"),
                 (ICON_HEART, "<b>100% of net proceeds</b> go to veterans charities"),
                 (ICON_RECEIPT, f"<b>501(c)(3) nonprofit</b>, <span class=\"nw\">EIN {b['ein']}</span>"),
                 (ICON_TRUCK, "<b>Free pickup</b> in all 50 states, running or not")]
    else:
        items = [(ICON_SHIELD, "<b>$202 million+</b> given by Car Donation Foundation programs since 2010"),
                 (ICON_HEART, "<b>The #1 car donation program</b> benefiting Make-A-Wish chapters nationally"),
                 (ICON_STAR, "<b>A top Make-A-Wish donor</b> in the U.S., along with Disney and Macy's"),
                 (ICON_TRUCK, "<b>Free towing</b> nationwide, with a tax-deductible receipt")]
    lis = "".join(f'<li class="rv" style="--i:{i}">{ic}<span>{t}</span></li>' for i, (ic, t) in enumerate(items))
    return f'<section class="proof" aria-label="Why donors trust us"><div class="wrap"><ul class="proof-list">{lis}</ul></div></section>'


def marquee_vfv():
    names = CHARITIES_VFV
    half = len(names) // 2
    def row(lst, cls):
        seq = "".join(f'<span class="mq-item">{esc(n)}</span><span class="mq-star" aria-hidden="true">★</span>' for n in lst)
        return f'<div class="mq-row {cls}" aria-hidden="true"><div class="mq-track">{seq}{seq}</div></div>'
    lst = "".join(f"<li>{esc(n)}</li>" for n in names)
    return f"""<section class="charities live-anim" aria-labelledby="ch-h"><div class="wrap">
<h2 id="ch-h">{len(names)} veterans charities have benefited from Vehicles For Veterans</h2>
<p class="lead">Proceeds go to established organizations that provide medical care, mental health support, housing, service dogs, family support and more.</p>
<ul class="skip-list">{lst}</ul></div>
{row(names[:half], 'mq-a')}{row(names[half:], 'mq-b')}
<div class="wrap"><p class="ch-note">Charity names as listed on the Vehicles For Veterans About page.</p></div></section>"""


def journey(b, key, P):
    if key == "vfv":
        steps = [("Send the form", f"Three short screens, or call {b['phone']}."),
                 ("We call within 24 hours", "By the next business day, to schedule your free pickup."),
                 ("Free towing", "A local tow company picks it up at no cost to you, running or not."),
                 ("Sold at auction", "Your vehicle is sold for the most value we can get."),
                 ("Veterans charities benefit", "100% of net proceeds go to veterans charities, and your tax receipt comes by mail.")]
        title, lead = "Where your car goes", "Follow your donation from your driveway to the charities it helps."
    else:
        steps = [("Send the form", f"Three short screens, or call {b['phone']}."),
                 ("You're contacted in 24 hours", "By the next business day, to schedule your free towing."),
                 ("Free towing", "Your vehicle is picked up free of charge, anywhere in the U.S."),
                 ("Sold for the most value", "At auction, or by recycling it if that's worth more."),
                 ("A local wish comes true", "Net proceeds go to your local Make-A-Wish chapter, and you get a tax-deductible receipt.")]
        title, lead = "From your driveway to a child's wish", "Follow your donation step by step."
    lis = "".join(f'<li class="j-step" style="--i:{i}"><span class="j-dot" aria-hidden="true">{i + 1}</span><div><h3>{esc(t)}</h3><p>{esc(d)}</p></div></li>'
                  for i, (t, d) in enumerate(steps))
    car = icon_svg("car-duotone.svg").replace('class="vic"', 'class="vic j-car-ico"')
    return f"""<section class="section journey" data-journey><div class="wrap">
<h2>{title}</h2><p class="lead">{lead}</p>
<div class="j-track"><div class="j-road" aria-hidden="true"><span class="j-fill"></span></div><span class="j-car" aria-hidden="true">{car}</span>
<ol class="j-steps">{lis}</ol></div></div></section>"""


def stats_band(b, key, P):
    if key == "vfv":
        stats = [("$202M+", "$202 million plus", "given by Car Donation Foundation programs since 2010"),
                 ("100%", "100 percent", "of net proceeds go to veterans charities"),
                 ("40%", "about 40 percent", "of the auction value reaches veterans charities, on average"),
                 ("31", "31", "veterans charities have received proceeds")]
        need = f"""<div class="need"><h3>Why it matters</h3><ul>
<li><strong>6.3 million</strong><span>veterans receive VA disability compensation</span></li>
<li><strong>32,495</strong><span>veterans were experiencing homelessness on one night in January 2025</span></li></ul>
<p class="source">Sources: U.S. Department of Veterans Affairs, Annual Benefits Report FY2025 (6,338,253 veterans as of Sept 30, 2025). HUD, 2025 Annual Homeless Assessment Report.</p></div>"""
        h = "Your car, turned into real support"
        src = 'Figures from vehiclesforveterans.org: home, About and <a href="https://www.vehiclesforveterans.org/transparency/">Transparency</a> pages.'
    else:
        stats = [("14,673", "14,673", "wishes granted with help from donors, as of September 2026"),
                 ("$125,695,697", "$125,695,697", "raised by Wheels For Wishes for wishes since 2010"),
                 ("$5,970,141", "$5,970,141", "donated to Make-A-Wish in 2024 alone"),
                 ("535", "about 535", "wishes funded on average by that 2024 gift")]
        need = ""
        h = "Cars like yours grant wishes"
        src = 'Figures from wheelsforwishes.org: home and <a href="https://www.wheelsforwishes.org/transparency/">Transparency</a> pages.'
    cards = "".join(f'<li class="stat rv" style="--i:{i}">{odo(v, l)}<span>{esc(t)}</span></li>' for i, (v, l, t) in enumerate(stats))
    deco = '<span class="band-chev" aria-hidden="true"></span>' if key == "vfv" else f'<span class="band-stars" aria-hidden="true"></span>'
    return f"""<section class="section stats-band stats-{key} live-anim">{deco}<div class="wrap">
<h2>{h}</h2><ul class="stats">{cards}</ul>{need}<p class="source">{src}</p></div></section>"""


def verify(b, key, P):
    if key == "vfv":
        org = "Car Donation Foundation, doing business as Vehicles For Veterans"
        ein = f"EIN {b['ein']}"
        money = "On average, about 40% of the auction value goes directly to veterans charities. Towing, auction and administrative costs come out of the rest."
        report = "https://www.vehiclesforveterans.org/transparency/"
    else:
        org = "Wheels For Wishes, a program of Car Donation Foundation"
        ein = f"EIN {b['ein']}"
        money = "On average, 39% of the auction value goes to Make-A-Wish. Towing and auction fees are fixed, so higher-value vehicles send a larger share."
        report = "https://www.wheelsforwishes.org/transparency/"
    cards = [
        (ICON_SHIELD, "A registered 501(c)(3) charity", f"{org}. {ein}.",
         '<a href="https://apps.irs.gov/app/eos/">Look us up on the IRS charity search' + ICON_EXT + '</a>'),
        (ICON_RECEIPT, "Your receipt matches the sale price", "Your tax-deductible receipt matches the full amount your vehicle sells for at auction. If it sells for under $500, you can claim fair market value up to $500. Ask your tax advisor how it applies to you.", ""),
        (ICON_PIE, "Where the money goes", money, f'<a href="{report}">Read the full transparency report' + ICON_EXT + '</a>'),
        (ICON_PIN, "A real office you can call", f"{b['address']}.", f'<a href="tel:{b["tel"]}">Call {b["phone"]}</a>'),
    ]
    lis = "".join(f'<li class="v-card rv" style="--i:{i}"><span class="v-ico">{ic}</span><h3>{esc(t)}</h3><p>{esc(d)}</p>{("<p>" + l + "</p>") if l else ""}</li>'
                  for i, (ic, t, d, l) in enumerate(cards))
    return f"""<section class="section verify"><div class="wrap">
<h2>Check us out for yourself</h2><p class="lead">Before you donate, you should know exactly who you're giving to and where the money goes.</p>
<ul class="v-grid">{lis}</ul></div></section>"""


def state_map(P, key, title="Free pickup in all 50 states and D.C.", lead="Choose your state to see how donating works there."):
    names = dict(zip(ABBR, STATES))
    tiles_html = "".join(
        f'<a class="st" href="{P}states/{slug(names[a])}/index.html" style="--r:{r};--c:{c}"><span aria-hidden="true">{a}</span><span class="skip-list">{names[a]}</span></a>'
        for a, (r, c) in TILE_POS.items())
    return f"""<section class="section map-section"><div class="wrap map-wrap">
<div class="map-copy"><h2>{title}</h2><p class="lead">{lead}</p><p><a class="map-all" href="{P}states/index.html">See every state by name</a></p></div>
<nav class="usmap" aria-label="Donate in your state">{tiles_html}</nav></div></section>"""


def quotes_vfv(P):
    return f"""<section class="section quotes-sec"><div class="wrap split">
<img class="framed" src="{P}assets/img/veterans-photo.webp" width="1200" height="516" alt="A hand holding a photo of two smiling veterans" loading="lazy">
<div><h2>What donors say</h2><div class="quotes">
<blockquote class="rv"><p>“Your website was really easy, and the details offered on the page such as explaining about the tax deduction, no costs, etc, was very useful.”</p><footer>Amy Meadows, Toyota donor, California</footer></blockquote>
<blockquote class="rv" style="--i:1"><p>“The process was very easy. A well informed form and pick-up of the vehicle is a great option.”</p><footer>Steve Smith, Private First Class, California</footer></blockquote>
</div></div></div></section>"""


def cta_band(b, key, P, h=None, p=None):
    h = h or ("Ready to donate your vehicle?" if key == "vfv" else "Help make a child's wish come true")
    p = p or "Three short screens, then we take care of the rest."
    btn = "btn-invert" if key == "vfv" else "btn-sun"
    deco = '<span class="cta-chev" aria-hidden="true"></span>' if key == "vfv" else '<span class="band-stars" aria-hidden="true"></span><span class="shooting s2" aria-hidden="true"></span>'
    return f"""<section class="section cta-band cta-{key} live-anim">{deco}<div class="wrap"><h2>{h}</h2><p>{p}</p><a class="btn {btn} glint magnetic" href="{P}donate/index.html">Start my donation</a></div></section>"""


def home(b, key):
    P = ""
    faq_sec = f"""<section class="section faq-sec"><div class="wrap narrow"><h2>Questions donors ask</h2>{faq_list(b, 4)}<p style="margin-top:20px"><a href="{P}faq/index.html">See all questions</a></p></div></section>"""
    if key == "vfv":
        body = (hero(b, key, P) + trust(b, key, P) + marquee_vfv() + journey(b, key, P) + stats_band(b, key, P)
                + quotes_vfv(P) + verify(b, key, P) + state_map(P, key) + faq_sec + cta_band(b, key, P))
    else:
        body = (hero(b, key, P) + trust(b, key, P) + stats_band(b, key, P) + wishes_wfw(P) + journey(b, key, P)
                + chapters_wfw(P) + verify(b, key, P) + faq_sec + cta_band(b, key, P))
    return page(b, key, P, b["title"], b["description"], "", body, with_sticky=True)


CHAPTERS_WFW = ['Alabama', 'Arizona', 'Central & Northern Florida', 'Central and South Texas', 'Central and Western North Carolina', 'Central Coast and Southern Central Valley', 'Central New York', 'Colorado', 'East Tennessee', 'Eastern North Carolina', 'Georgia', 'Greater Los Angeles', 'Greater Pennsylvania & West Virginia', 'Hawaii', 'Idaho', 'Illinois', 'Iowa', 'Metro New York', 'Michigan', 'Mid-Atlantic', 'Mid-South', 'Middle Tennessee', 'Minnesota', 'Mississippi', 'Missouri and Kansas', 'Nebraska', 'Nevada', 'New Hampshire', 'New Mexico', 'North Dakota', 'North Texas', 'Northeastern & Central California', 'Ohio, Kentucky, & Indiana', 'Orange County and the Inland Empire', 'Oregon', 'Rio Grande Valley', 'San Diego', 'South Carolina', 'South Dakota & Montana', 'Southern Florida', 'Suffolk County', 'Texas Gulf Coast & Louisiana', 'Utah', 'Vermont & Northeast New York', 'Western New York', 'Wisconsin', 'Wyoming']
# extra search words only where the region is unambiguous (or stated on wheelsforwishes.org)
CHAPTER_ALIAS = {"Central Coast and Southern Central Valley": "california", "Greater Los Angeles": "california",
                 "Orange County and the Inland Empire": "california", "San Diego": "california",
                 "Suffolk County": "new york long island", "Rio Grande Valley": "texas",
                 "Mid-Atlantic": "washington dc d.c. district of columbia"}


def wishes_wfw(P):
    kids = [("ethan", "Ethan", "6", "To be a garbage man"), ("chloe", "Chloe", "8", "To visit a dude ranch"),
            ("areice", "Areice", "5", "To be a pirate"), ("jack", "Jack", "14", "To ski in Aspen")]
    cards = "".join(f"""<li class="rv" style="--i:{i}"><button class="flip" type="button" aria-pressed="false">
<span class="flip-in"><span class="face front"><img src="{P}assets/img/wish-{k}.webp" width="300" height="300" alt="" loading="lazy"><strong>{n}, {a}</strong><span class="tap">Tap to see the wish</span></span>
<span class="face back"><span class="wish-star" aria-hidden="true">{ICON_STAR}</span><span class="wish-label">{n}'s wish</span><strong>{w}</strong></span></span></button></li>"""
                    for i, (k, n, a, w) in enumerate(kids))
    return f"""<section class="section wishes-sec"><div class="wrap">
<h2>Meet some of the wish kids</h2>
<p class="lead">Every car donation helps a child in your community have a wish come true. Tap a card to see the wish.</p>
<ul class="wish-cards">{cards}</ul></div></section>"""


def chapters_wfw(P):
    chips = "".join(f'<li data-k="{esc((c + " " + CHAPTER_ALIAS.get(c, "")).lower())}">{esc(c)}</li>' for c in CHAPTERS_WFW)
    return f"""<section class="section chapters"><div class="wrap ch-wrap">
<div class="ch-copy"><h2>Your donation stays local</h2>
<p class="lead">Wheels For Wishes benefits {len(CHAPTERS_WFW)} Make-A-Wish chapters. Find yours.</p>
<label class="ch-label" for="ch-q">Search by state or chapter name</label>
<input id="ch-q" type="search" autocomplete="off" data-chq>
<p class="ch-count" aria-live="polite" data-chcount>Showing all {len(CHAPTERS_WFW)} chapters</p></div>
<div class="ch-board"><h3>Make-A-Wish chapters that Wheels For Wishes benefits</h3><ul class="ch-list collapsed" id="ch-list" data-chlist>{chips}</ul>
<button class="btn btn-secondary ch-more" type="button" aria-expanded="false" aria-controls="ch-list" data-chmore>Show all {len(CHAPTERS_WFW)} chapters</button>
<p class="ch-empty" hidden data-chempty>No chapter by that name. Call 1-888-737-5808 to ask which chapter your donation supports.</p></div>
</div></section>"""


# ---------------------------------------------------------------------------
# CSS for the v3 design (shared), appended after the base CSS
# ---------------------------------------------------------------------------
NEXT_CSS = r"""
/* ===== v3 shared ===== */
.skip-list{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.narrow{max-width:860px}
.nw{white-space:nowrap}
.ico.ext{width:1em;height:1em;vertical-align:-2px;margin-left:4px}
/* header */
.site-header{position:sticky;top:0;z-index:60;transition:box-shadow .3s ease}
.site-header.scrolled{box-shadow:0 10px 30px -12px rgba(5,12,28,.55)}
.nav-cta a{position:relative;overflow:hidden}
.glint{position:relative;overflow:hidden;isolation:isolate}
.glint::after{content:"";position:absolute;top:-30%;bottom:-30%;left:0;width:40%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.2),transparent);transform:translateX(-160%) skewX(-18deg);pointer-events:none;z-index:1}
/* hero */
.hero{isolation:isolate}
.hero-form{position:relative}
.glow-frame{position:relative;border-radius:20px;padding:3px;overflow:hidden;isolation:isolate;box-shadow:0 30px 60px -24px rgba(4,10,24,.75)}
.glow-frame::before{content:"";position:absolute;left:50%;top:50%;width:160%;aspect-ratio:1;background:conic-gradient(from 0deg,var(--g1),var(--g2),var(--g3),var(--g1));transform:translate(-50%,-50%);z-index:-1}
.glow-frame .start-card{border:0;border-radius:17px;box-shadow:none}
.live-chip{display:inline-flex;align-items:center;gap:8px;margin:0 0 10px;padding:4px 12px;border-radius:999px;background:#E8F6EE;color:#0B4B2C;font-weight:900;font-size:1rem;line-height:1.4}
.live-chip .dot{width:10px;height:10px;border-radius:50%;background:#12A150;box-shadow:0 0 0 0 rgba(18,161,80,.6);flex:none}
/* seal */
.seal{position:absolute;z-index:3;width:84px;height:84px;right:-6px;top:-34px;filter:drop-shadow(0 10px 18px rgba(4,10,24,.45))}
.seal svg{display:block;width:100%;height:100%;overflow:visible}
.seal .ring-text,.seal .seal-big{display:none}
.seal-ring{position:absolute;inset:-6px;border-radius:50%;border:3px solid var(--g2);opacity:0;pointer-events:none}
.seal-glint{position:absolute;inset:6%;border-radius:50%;overflow:hidden;pointer-events:none}
.seal-glint::after{content:"";position:absolute;top:-20%;bottom:-20%;left:0;width:45%;transform:translateX(-140%) skewX(-18deg);background:linear-gradient(90deg,transparent,rgba(255,255,255,.85),transparent)}
.start-card h2{padding-right:70px}
/* proof strip */
.proof{background:var(--deep);color:#fff;border-top:1px solid rgba(255,255,255,.18)}
.proof-list{list-style:none;margin:0;padding:22px 0;display:grid;gap:14px}
.proof-list li{display:flex;align-items:center;gap:14px;font-size:1.0625rem;line-height:1.4;color:#fff}
.proof-list b{font-weight:900;color:#fff}
.proof-list .ico{width:40px;height:40px;padding:8px;border-radius:12px;background:var(--chip);color:var(--chip-ink);flex:none}
/* journey */
.journey{background:#fff;overflow:hidden}
.j-track{position:relative;margin-top:84px;--road:18px}
.j-steps{list-style:none;margin:0;padding:0 0 0 76px;display:grid;gap:26px;position:relative}
.j-step{display:grid;grid-template-columns:1fr;position:relative}
.j-step h3{margin:0 0 4px;font-size:1.375rem}
.j-step p{margin:0;font-size:1.0625rem}
.j-dot{position:absolute;left:-76px;top:-4px;width:52px;height:52px;border-radius:50%;display:grid;place-items:center;font:900 1.375rem/1 var(--head);background:#fff;color:var(--navy);border:3px solid var(--navy);transition:background .35s ease,color .35s ease,transform .35s ease,box-shadow .35s ease;z-index:1}
.j-step.on .j-dot{background:var(--brand);border-color:var(--brand);color:#fff;transform:scale(1.08);box-shadow:0 0 0 6px var(--ring-glow)}
.j-road{position:absolute;left:17px;top:0;bottom:0;width:var(--road);border-radius:12px;background:#1E2A44;overflow:hidden}
.j-road::before{content:"";position:absolute;left:50%;top:0;bottom:0;width:3px;margin-left:-1.5px;background:repeating-linear-gradient(180deg,#FFD24A 0 14px,transparent 14px 28px);background-position:0 var(--dash,0px)}
.j-fill{position:absolute;left:0;right:0;top:0;height:calc(var(--p,0) * 100%);background:linear-gradient(180deg,var(--brand),var(--brand-dark));opacity:.9}
.j-car{position:absolute;left:0;top:0;width:52px;height:52px;margin-left:0;border-radius:50%;background:#fff;box-shadow:0 8px 20px -6px rgba(4,10,24,.55),0 0 0 3px var(--navy);display:grid;place-items:center;z-index:2;transform:translate3d(0,var(--cy,-64px),0);will-change:transform}
.j-car .vic{width:32px;height:28px;transform:rotate(90deg)}
/* stats band */
.stats-band{position:relative;overflow:hidden;color:#fff}
.stats-band h2,.stats-band h3{color:#fff}
.stats-band .wrap{position:relative;z-index:1}
.stats{list-style:none;margin:30px 0 0;padding:0;display:grid;gap:16px}
.stat{padding:22px 22px 20px;border-radius:18px;background:var(--stat-bg);border:1px solid var(--stat-line);display:flex;flex-direction:column;gap:8px}
.stat>span{font-size:1.125rem;font-weight:700;color:#fff;max-width:30ch}
.odo{font:var(--head-w) clamp(2.6rem,9vw,3.75rem)/1 var(--head);color:#fff;white-space:nowrap;letter-spacing:-.01em;display:inline-flex}
.odo .d{display:inline-block;height:1em;overflow:hidden;vertical-align:top}
.odo .s{display:flex;flex-direction:column;transition:transform 1.9s cubic-bezier(.16,.84,.2,1)}
.odo .s>span{display:block;height:1em;line-height:1}
.need{margin-top:34px;padding-top:26px;border-top:1px solid var(--stat-line)}
.need ul{list-style:none;margin:16px 0 0;padding:0;display:grid;gap:18px}
.need li{display:flex;flex-direction:column;gap:4px}
.need strong{font:var(--head-w) 2.25rem/1 var(--head);color:#fff}
.need span{font-size:1.125rem;font-weight:700}
.stats-band .source{font-size:1rem;color:#fff;margin-top:22px}
.stats-band .source a{color:#fff}
/* quotes */
blockquote{box-shadow:0 18px 40px -26px rgba(8,16,40,.5)}
/* verify */
.verify{background:var(--soft)}
.v-grid{list-style:none;margin:28px 0 0;padding:0;display:grid;gap:16px}
.v-card{background:#fff;border:2px solid var(--line);border-radius:18px;padding:22px}
.v-card h3{font-size:1.3125rem;margin:12px 0 6px}
.v-card p{margin:0 0 8px;font-size:1.0625rem}
.v-card a{font-weight:900;color:var(--navy)}
.v-ico{display:inline-grid;place-items:center;width:52px;height:52px;border-radius:14px;background:var(--navy);color:#fff}
.v-ico .ico{width:28px;height:28px}
/* map */
.map-section{background:#fff}
.map-wrap{display:grid;gap:26px;align-items:center}
.usmap{display:grid;grid-template-columns:repeat(11,minmax(0,1fr));grid-template-rows:repeat(8,auto);gap:4px;width:100%;max-width:640px}
.usmap .st{grid-row:calc(var(--r) + 1);grid-column:calc(var(--c) + 1);aspect-ratio:1;display:grid;place-items:center;border-radius:7px;background:var(--navy);color:#fff;font:900 1rem/1 var(--body);text-decoration:none;letter-spacing:-.02em;transition:transform .2s ease,background .2s ease}
.usmap .st:hover,.usmap .st:focus-visible{background:var(--brand);color:#fff;transform:translateY(-3px) scale(1.08)}
.map-all{font-weight:900}
/* cta */
.cta-band .btn{min-width:240px}
/* reveal: transform only, text is never faded */
@media (prefers-reduced-motion:no-preference){
  .js .rv{transform:translateY(26px);transition:transform .8s cubic-bezier(.2,.8,.2,1);transition-delay:calc(var(--i,0) * 90ms)}
  .js .rv.in{transform:none}
  .glow-frame::before{animation:spin 7s linear infinite}
  .glint::after{animation:glint 6s ease-in-out 1.6s infinite}
  .live-chip .dot{animation:ping 1.8s ease-out infinite}
  .seal{animation:seal-in 1.1s cubic-bezier(.2,.9,.25,1.12) .35s both}
  .seal-spin{animation:seal-rot 40s linear 1.4s infinite}
  .seal-ring{animation:ring 4.5s cubic-bezier(.2,.6,.3,1) 1.3s infinite}
  .seal-ring.r2{animation-delay:3.55s}
  .seal-glint::after{animation:seal-glint 7s ease-in-out 1.5s infinite}
  .usmap.in .st{animation:tile-pop .6s cubic-bezier(.2,.9,.3,1.3) both;animation-delay:calc((var(--r) + var(--c)) * 45ms)}
  .hero-form .glow-frame{animation:rise .8s cubic-bezier(.2,.8,.2,1) .1s both}
}
@keyframes spin{to{transform:translate(-50%,-50%) rotate(360deg)}}
@keyframes seal-rot{to{transform:rotate(360deg)}}
.seal-spin{transform-box:view-box;transform-origin:50% 50%}
@keyframes glint{0%,72%{transform:translateX(-160%) skewX(-18deg)}100%{transform:translateX(330%) skewX(-18deg)}}
@keyframes ping{0%{box-shadow:0 0 0 0 rgba(18,161,80,.55)}100%{box-shadow:0 0 0 12px rgba(18,161,80,0)}}
@keyframes seal-in{0%{transform:scale(.2) rotate(-200deg)}70%{transform:scale(1.08) rotate(8deg)}100%{transform:none}}
@keyframes ring{0%{transform:scale(.9);opacity:.9}100%{transform:scale(1.5);opacity:0}}
@keyframes seal-glint{0%,80%{transform:translateX(-140%) skewX(-18deg)}100%{transform:translateX(260%) skewX(-18deg)}}
@keyframes tile-pop{0%{transform:scale(.4);background:var(--brand)}60%{background:var(--brand)}100%{transform:none}}
@keyframes rise{from{transform:translateY(30px)}to{transform:none}}
@keyframes mq{to{transform:translateX(-50%)}}
.paused,.paused *,.paused *::before,.paused *::after,.paused::before,.paused::after{animation-play-state:paused!important}
@media (min-width:600px){
  .proof-list{grid-template-columns:1fr 1fr}
  .stats{grid-template-columns:1fr 1fr}
  .v-grid{grid-template-columns:1fr 1fr}
  .need ul{grid-template-columns:1fr 1fr}
}
@media (min-width:960px){
  .proof-list{grid-template-columns:repeat(4,1fr);gap:22px}
  .stats{grid-template-columns:repeat(4,1fr)}
  .v-grid{grid-template-columns:repeat(4,1fr)}
  .map-wrap{grid-template-columns:.8fr 1.2fr;gap:56px}
  .seal{width:178px;height:178px;right:-64px;top:-62px}
  .seal .ring-text,.seal .seal-big{display:inline}
  .seal .ring-stars,.seal .seal-small{display:none}
  .start-card h2{padding-right:0}
  .hero-form{margin-left:40px}
  /* horizontal journey */
  .j-steps{grid-template-columns:repeat(5,1fr);padding:96px 0 0;gap:22px}
  .j-dot{left:0;top:-74px}
  .j-road{left:0;right:0;top:-46px;bottom:auto;width:auto;height:var(--road);top:18px}
  .j-road::before{left:0;right:0;top:50%;bottom:auto;width:auto;height:3px;margin:-1.5px 0 0;background:repeating-linear-gradient(90deg,#FFD24A 0 14px,transparent 14px 28px);background-position:var(--dash,0px) 0}
  .j-fill{top:0;bottom:0;height:auto;width:calc(var(--p,0) * 100%)}
  .j-car{top:1px;transform:translate3d(var(--cx,-64px),0,0)}
  .j-car .vic{transform:none}
  .j-track{margin-top:44px;margin-left:70px}
}
"""

MOTION_JS = r"""
(function () {
  var d = document, w = window;
  var reduce = w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var qsa = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
  var io = 'IntersectionObserver' in w;

  // Header shadow once the page scrolls
  var hdr = d.querySelector('.site-header');
  if (hdr) { var onS = function () { hdr.classList.toggle('scrolled', w.scrollY > 8); }; w.addEventListener('scroll', onS, { passive: true }); onS(); }

  // Reveal (transform only)
  if (io && !reduce) {
    var rio = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); rio.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    qsa('.rv, .usmap').forEach(function (el) { rio.observe(el); });
  } else { qsa('.rv, .usmap').forEach(function (el) { el.classList.add('in'); }); }

  // Pause looping animations while off screen
  if (io) {
    var pio = new IntersectionObserver(function (es) { es.forEach(function (e) { e.target.classList.toggle('paused', !e.isIntersecting); }); });
    qsa('.live-anim, .hero, .site-header').forEach(function (el) { pio.observe(el); });
  }

  // Odometer counters
  function buildOdo(el) {
    var txt = el.textContent; el.setAttribute('data-final', txt); el.textContent = '';
    var vis = d.createElement('span'); vis.setAttribute('aria-hidden', 'true'); vis.style.display = 'inline-flex';
    txt.split('').forEach(function (ch, k) {
      if (/\d/.test(ch)) {
        var dd = d.createElement('span'); dd.className = 'd';
        var s = d.createElement('span'); s.className = 's'; s.style.transitionDelay = (k * 60) + 'ms';
        for (var n = 0; n <= 9; n++) { var c = d.createElement('span'); c.textContent = n; s.appendChild(c); }
        dd.appendChild(s); dd.setAttribute('data-v', ch); vis.appendChild(dd);
      } else { var p = d.createElement('span'); p.textContent = ch; vis.appendChild(p); }
    });
    el.appendChild(vis);
    var sr = d.createElement('span'); sr.className = 'skip-list'; sr.textContent = txt; el.appendChild(sr);
  }
  function runOdo(el) { qsa('.d', el).forEach(function (dd) { dd.firstChild.style.transform = 'translateY(' + (-dd.getAttribute('data-v')) + 'em)'; }); setTimeout(function () { el.textContent = el.getAttribute('data-final'); }, 2900); }
  var odos = qsa('[data-odo]');
  if (odos.length && io && !reduce) {
    odos.forEach(buildOdo);
    var oio = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { setTimeout(function () { runOdo(e.target); }, 120); oio.unobserve(e.target); } }); }, { rootMargin: '0px 0px -10% 0px' });
    odos.forEach(function (el) { oio.observe(el); });
  }

  // Journey: the car drives as you scroll
  var j = d.querySelector('[data-journey]');
  if (j) {
    var track = j.querySelector('.j-track'), car = j.querySelector('.j-car'), steps = qsa('.j-step', j), road = j.querySelector('.j-road');
    var ticking = false;
    var update = function () {
      ticking = false;
      var r = track.getBoundingClientRect(), vh = w.innerHeight;
      var horiz = w.matchMedia('(min-width:960px)').matches;
      var p = horiz ? (vh * .82 - r.top) / (vh * .5) : (vh * .62 - r.top) / r.height;
      p = Math.max(0, Math.min(1, p)); if (reduce) p = 1;
      track.style.setProperty('--p', p.toFixed(3));
      if (horiz) {
        var max = road.offsetWidth - car.offsetWidth + 64; track.style.setProperty('--cx', (p * max - 64) + 'px'); track.style.setProperty('--dash', (-p * 420) + 'px');
      } else {
        var maxy = road.offsetHeight - car.offsetHeight + 64; track.style.setProperty('--cy', (p * maxy - 64) + 'px'); track.style.setProperty('--dash', (p * 420) + 'px');
      }
      steps.forEach(function (s, i) { s.classList.toggle('on', p >= (i / (steps.length - 1)) - .04 || p >= .995); });
    };
    var onScroll = function () { if (!ticking) { ticking = true; w.requestAnimationFrame(update); } };
    w.addEventListener('scroll', onScroll, { passive: true }); w.addEventListener('resize', onScroll); update();
  }

  // Desktop headline: word-by-word rise (phones keep the headline static for speed)
  var h1 = d.querySelector('.hero h1.h-split');
  if (h1 && !reduce && w.matchMedia('(min-width:960px)').matches) {
    var words = h1.textContent.trim().split(/\s+/);
    h1.setAttribute('aria-label', h1.textContent.trim());
    h1.innerHTML = words.map(function (wd, i) { return '<span class="w" aria-hidden="true"><span style="--i:' + i + '">' + wd.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</span></span>'; }).join(' ');
    h1.classList.add('h-split-on');
  }
  d.documentElement.classList.add('h1-ready');

  // Wish cards flip on tap (hover flips them on desktop)
  qsa('.flip').forEach(function (b) { b.addEventListener('click', function () { b.setAttribute('aria-pressed', String(b.getAttribute('aria-pressed') !== 'true')); }); });

  // Chapter search
  var q = d.querySelector('[data-chq]');
  if (q) {
    var items = qsa('[data-chlist] li'), cnt = d.querySelector('[data-chcount]'), empty = d.querySelector('[data-chempty]');
    var AB = {"al": "alabama", "ak": "alaska", "az": "arizona", "ar": "arkansas", "ca": "california", "co": "colorado", "ct": "connecticut", "de": "delaware", "dc": "district of columbia", "fl": "florida", "ga": "georgia", "hi": "hawaii", "id": "idaho", "il": "illinois", "in": "indiana", "ia": "iowa", "ks": "kansas", "ky": "kentucky", "la": "louisiana", "me": "maine", "md": "maryland", "ma": "massachusetts", "mi": "michigan", "mn": "minnesota", "ms": "mississippi", "mo": "missouri", "mt": "montana", "ne": "nebraska", "nv": "nevada", "nh": "new hampshire", "nj": "new jersey", "nm": "new mexico", "ny": "new york", "nc": "north carolina", "nd": "north dakota", "oh": "ohio", "ok": "oklahoma", "or": "oregon", "pa": "pennsylvania", "ri": "rhode island", "sc": "south carolina", "sd": "south dakota", "tn": "tennessee", "tx": "texas", "ut": "utah", "vt": "vermont", "va": "virginia", "wa": "washington", "wv": "west virginia", "wi": "wisconsin", "wy": "wyoming"};
    var list = d.querySelector('[data-chlist]'), more = d.querySelector('[data-chmore]');
    if (more) more.addEventListener('click', function () { list.classList.remove('collapsed'); more.setAttribute('aria-expanded', 'true'); });
    q.addEventListener('input', function () {
      var v = q.value.trim().toLowerCase(); if (AB[v]) v = AB[v];
      if (v) list.classList.remove('collapsed'); else if (more && more.getAttribute('aria-expanded') !== 'true') list.classList.add('collapsed');
      var n = 0;
      items.forEach(function (li) { var t = (li.textContent + ' ' + li.getAttribute('data-k')).toLowerCase(); var ok = !v || t.indexOf(v) > -1; li.hidden = !ok; li.classList.toggle('hit', !!v && ok); if (ok) n++; });
      cnt.textContent = v ? ('Showing ' + n + ' of ' + items.length + ' chapters') : ('Showing all ' + items.length + ' chapters');
      empty.hidden = n > 0;
    });
  }

  // Magnetic buttons (mouse only)
  if (!reduce && w.matchMedia('(hover:hover) and (pointer:fine)').matches) {
    qsa('.magnetic').forEach(function (b) {
      b.addEventListener('mousemove', function (e) { var r = b.getBoundingClientRect(); var x = (e.clientX - r.left - r.width / 2) / r.width, y = (e.clientY - r.top - r.height / 2) / r.height; b.style.transform = 'translate(' + (x * 8) + 'px,' + (y * 6) + 'px)'; });
      b.addEventListener('mouseleave', function () { b.style.transform = ''; });
    });
  }
})();
"""


WFW_CSS = r"""/* ===== WFW v3 ===== */
:root{--night:#0F1E4D;--deep:#0F1E4D;--g1:#C2255C;--g2:#F7D132;--g3:#3FC1B6;--chip:#1C3A8A;--chip-ink:#F7D132;--ring-glow:rgba(194,37,92,.22);
--stat-bg:#A41C4D;--stat-line:#EE86AA;--head-w:800;--icon1:#1C3A8A;--icon2:#C2255C}
/* header: white, with the big round logo hanging into the hero */
.hdr-wfw{background:#fff;border-bottom:3px solid #F7D132}
.hdr-wfw .wrap{min-height:76px}
.hdr-wfw .logo{position:relative;gap:12px}
.hdr-wfw .logo-wfw{height:58px;width:auto;transform-origin:50% 60%}
.hdr-wfw .logo-maw{height:34px;width:auto}
.hdr-wfw .site-nav li a{color:#151B2E}
.hdr-wfw .nav-phone{color:#0E6B63!important}
.hdr-wfw .menu-btn{color:#151B2E;border-color:#151B2E}
/* hero: wish-night sky, Clara's photo, twinkling stars and shooting stars */
.hero-wfw{background:#0F1E4D;color:#fff}
.hero-wfw::before{content:"";position:absolute;inset:0;z-index:-3;pointer-events:none;
background-image:radial-gradient(1.6px 1.6px at 12% 22%,#fff 60%,transparent 62%),radial-gradient(1.2px 1.2px at 38% 64%,#fff 60%,transparent 62%),radial-gradient(1.8px 1.8px at 72% 18%,#FFE27A 60%,transparent 62%),radial-gradient(1.2px 1.2px at 88% 52%,#fff 60%,transparent 62%),radial-gradient(1.4px 1.4px at 56% 86%,#fff 60%,transparent 62%);background-size:260px 260px}
.hero-wfw .hero-photo,.hero-wfw .hero-shade{display:none}
.hero-wfw h1{color:#fff;font-size:clamp(2.15rem,8.6vw,3.9rem);line-height:1.08;text-shadow:0 2px 16px rgba(5,10,30,.6)}
.hero-wfw .hero-sub{color:#fff}
.hero-wfw .hero-points .ico{color:#F7D132}
.hero-wfw .hero-points li{font-weight:700;color:#fff}
.hero-wfw .wrap{padding-bottom:64px;z-index:1}
.hero-media{position:relative}
.hero-media img{width:100%;height:190px;object-fit:cover;object-position:40% 35%;border-radius:20px;border:4px solid #fff}
.hero-caption{position:absolute;left:14px;bottom:12px;background:#fff;color:#151B2E;font-weight:800;font-size:1rem;line-height:1.3;border-radius:999px;padding:6px 14px;max-width:calc(100% - 28px)}
.sparks{position:absolute;inset:0;z-index:0;pointer-events:none}
.sparks i{position:absolute;left:var(--x);top:var(--y);width:var(--s);height:var(--s);background:#FFE27A;clip-path:polygon(50% 0,61% 39%,100% 50%,61% 61%,50% 100%,39% 61%,0 50%,39% 39%)}
.shooting{position:absolute;left:-12%;top:8%;width:170px;height:2px;border-radius:2px;background:linear-gradient(90deg,rgba(255,255,255,0),#fff);transform:translate(0,0) rotate(16deg);opacity:0;pointer-events:none;z-index:0}
.shooting::after{content:"";position:absolute;right:-3px;top:-3px;width:8px;height:8px;border-radius:50%;background:#fff;box-shadow:0 0 12px 4px rgba(255,226,122,.9)}
.shooting.s3{top:34%;left:-20%}
.wave path{fill:#F7D132}
/* proof strip in WFW yellow */
.proof{background:#F7D132;color:#151B2E;border-top:0}
.proof-list li,.proof-list b{color:#151B2E}
.proof-list .ico{background:#1C3A8A;color:#F7D132}
/* stats */
.stats-wfw{background:#C2255C}
.stats-wfw .stat{border-left:6px solid #F7D132}
.odo.long{font-size:clamp(2rem,7vw,3rem)}
.band-stars{position:absolute;inset:0;pointer-events:none;background-image:radial-gradient(2px 2px at 15% 20%,#FFE27A 60%,transparent 62%),radial-gradient(1.5px 1.5px at 65% 35%,#fff 60%,transparent 62%),radial-gradient(2px 2px at 85% 75%,#FFE27A 60%,transparent 62%),radial-gradient(1.5px 1.5px at 35% 80%,#fff 60%,transparent 62%);background-size:300px 300px}
/* wish cards */
.wishes-sec{background:#fff}
.wish-cards{list-style:none;margin:28px 0 0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:14px}
.wish-cards li:nth-child(1){--ring:#F7D132;--back-ink:#151B2E}
.wish-cards li:nth-child(2){--ring:#C2255C;--back-ink:#fff}
.wish-cards li:nth-child(3){--ring:#17766E;--back-ink:#fff}
.wish-cards li:nth-child(4){--ring:#1C3A8A;--back-ink:#fff}
.flip{display:block;width:100%;padding:0;border:0;background:none;cursor:pointer;perspective:1100px;font:inherit;color:inherit;text-align:center}
.flip-in{display:grid;transform-style:preserve-3d;transition:transform .75s cubic-bezier(.2,.8,.2,1)}
.face{grid-area:1/1;backface-visibility:hidden;-webkit-backface-visibility:hidden;border-radius:20px;padding:16px 12px 18px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;min-height:100%}
.front{background:#fff;border:2px solid var(--line)}
.front img{width:100%;max-width:170px;aspect-ratio:1;border-radius:50%;object-fit:cover;border:7px solid var(--ring)}
.front strong{font:800 1.25rem/1.2 var(--head);color:#151B2E}
.tap{font-size:1rem;font-weight:700;color:#1C3A8A;text-decoration:underline;text-underline-offset:3px}
.back{transform:rotateY(180deg);background:var(--ring);color:var(--back-ink)}
.back strong{font:800 clamp(1.25rem,4.6vw,1.75rem)/1.2 var(--head);color:var(--back-ink)}
.wish-label{font-weight:900;font-size:1.0625rem;color:var(--back-ink)}
.wish-star .ico{width:46px;height:46px;color:var(--back-ink)}
.flip[aria-pressed=true] .flip-in{transform:rotateY(180deg)}
.flip:focus-visible{outline:3px solid #C2255C;outline-offset:4px;border-radius:20px}
/* chapter finder */
.chapters{background:#FFF6D2}
.ch-wrap{display:grid;gap:24px}
.ch-label{display:block;font-weight:900;font-size:1.0625rem;margin:18px 0 6px}
.ch-count{font-weight:900;margin:10px 0 0}
.ch-board{background:#fff;border:2px solid #E9C640;border-radius:20px;padding:20px}
.ch-board h3{font-size:1.25rem}
.ch-list{list-style:none;margin:12px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.ch-list li{padding:7px 14px;border-radius:999px;background:#EEF3FC;border:2px solid #B9C3DA;font-weight:700;font-size:1rem;color:#151B2E}
.ch-list li.hit{background:#1C3A8A;border-color:#1C3A8A;color:#fff}
.ch-list li[hidden]{display:none}
.ch-more{display:none;margin-top:14px;min-height:48px;padding:10px 18px;font-size:1.0625rem}
@media (max-width:959px){.ch-list.collapsed li:nth-child(n+13){display:none}.ch-list.collapsed~.ch-more{display:inline-flex}}
.ch-empty{font-weight:900;margin:12px 0 0}
/* journey + cta */
.journey{background:#EEF3FC}
.cta-wfw{background:#0F1E4D}
.cta-wfw .shooting{top:20%}
.framed{box-shadow:14px 14px 0 #F7D132;border-radius:var(--r)}
@media (prefers-reduced-motion:no-preference){
  .hdr-wfw .logo-wfw{animation:wobble 1.4s cubic-bezier(.3,.7,.3,1.2) .3s backwards}
  .sparks i{animation:twinkle-s 2.8s ease-in-out infinite;animation-delay:var(--d)}
  .shooting{animation:shoot 9s ease-in 1.8s infinite}
  .shooting.s3{animation-delay:6.2s;animation-duration:11s}
  .cta-wfw .shooting{animation-delay:1s}
  .band-stars{animation:drift-y 14s ease-in-out infinite alternate}
  .chapters .ch-list li.hit{animation:tile-pop .45s cubic-bezier(.2,.9,.3,1.3) both}
  .wishes-sec .rv.in .flip-in{animation:peek 1.6s ease-in-out both;animation-delay:calc(.4s + var(--i,0) * .25s)}
  .hero-wfw .hero-photo::before{animation:kb 24s ease-in-out infinite alternate}
}
@media (hover:hover) and (pointer:fine){.flip:hover .flip-in{transform:rotateY(180deg)}}
@keyframes wobble{0%{transform:rotate(-14deg) scale(.7)}45%{transform:rotate(9deg) scale(1.06)}70%{transform:rotate(-4deg)}100%{transform:none}}
@keyframes twinkle-s{0%,100%{transform:scale(.55) rotate(0)}50%{transform:scale(1.15) rotate(45deg)}}
@keyframes shoot{0%{transform:translate(0,0) rotate(16deg);opacity:0}3%{opacity:1}22%{transform:translate(130vw,37vw) rotate(16deg);opacity:0}100%{transform:translate(130vw,37vw) rotate(16deg);opacity:0}}
@keyframes drift-y{from{transform:translateY(0)}to{transform:translateY(-30px)}}
@keyframes peek{0%,100%{transform:none}40%,60%{transform:rotateY(18deg)}}
@media (min-width:600px){.wish-cards{grid-template-columns:repeat(4,1fr)}}
@media (max-width:959px){.hero-wfw .shooting{display:none}}
@media (min-width:960px){
  .hdr-wfw .logo{padding-left:118px;min-height:64px}
  .hdr-wfw .logo-wfw{position:absolute;left:0;top:-8px;height:108px;filter:drop-shadow(0 10px 16px rgba(15,30,77,.35));transition:transform .35s ease}
  .hdr-wfw.scrolled .logo-wfw{transform:translateY(-4px) scale(.66);transform-origin:0 0}
  .hdr-wfw .site-nav .nav-cta a{background:#C2255C;color:#fff}
  .hero-wfw .wrap{min-height:700px;align-items:start;padding-top:64px;padding-bottom:120px}
  .hero-wfw .hero-copy{align-self:start;max-width:560px;background:rgba(15,30,77,.78);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);padding:26px 30px 28px;border-radius:22px;border:1px solid rgba(255,255,255,.22)}
  .hero-wfw .hero-copy h1{margin-bottom:.25em}
  .hero-wfw .hero-points{display:none}
  .hero-wfw .hero-form{align-self:center}
  .hero-wfw .hero-photo,.hero-wfw .hero-shade{display:block;position:absolute;left:0;top:0;bottom:0;width:62%;clip-path:ellipse(100% 120% at 0% 50%)}
  .hero-wfw .hero-photo{overflow:hidden;z-index:-2}
  .hero-wfw .hero-photo::before{content:"";position:absolute;inset:0;background:url(../img/hero-1920.webp) 30% 50%/cover no-repeat;transform-origin:30% 60%}
  .hero-wfw .hero-shade{z-index:-1;background:linear-gradient(180deg,rgba(15,30,77,.9) 0,rgba(15,30,77,.72) 30%,rgba(15,30,77,0) 46%,rgba(15,30,77,0) 76%,rgba(15,30,77,.7) 100%)}
  .hero-wfw .hero-caption{left:118px;bottom:96px}
  .hero-media{display:none}
  .wave{height:60px}
  .ch-wrap{grid-template-columns:.8fr 1.2fr;gap:48px;align-items:start}
  .stats-wfw .stats{grid-template-columns:repeat(4,1fr)}
}
"""

VFV_CSS = r"""
/* ===== VFV v3 ===== */
:root{--deep:#0B1B33;--g1:#C8102E;--g2:#78C8F8;--g3:#FFFFFF;--chip:#16325C;--chip-ink:#78C8F8;--ring-glow:rgba(200,16,46,.22);
--stat-bg:#14294A;--stat-line:#3B6EA8;--head-w:600;--icon1:#0F2747;--icon2:#C8102E;--step-bg:#C8102E}
/* header: their waving-flag bar, sharpened, with a moving sheen */
.hdr-vfv{background:#0B1B33;color:#fff;border-bottom:3px solid #C8102E}
.hdr-bg{position:absolute;inset:0;overflow:hidden;pointer-events:none}
.hdr-vfv .hdr-bg::before{content:"";position:absolute;top:0;bottom:0;left:-6%;width:112%;background:url(../img/flag-band.webp) center/cover}
.hdr-vfv .hdr-bg::after{content:"";position:absolute;top:0;bottom:0;left:0;width:34%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.12),transparent);transform:translateX(-120%)}
.hdr-vfv .wrap{position:relative;z-index:1}
.hdr-vfv .menu-btn{background:transparent;color:#fff;border-color:#fff}
.hdr-vfv .site-nav.open{background:#0B1B33;border-bottom:3px solid #C8102E}
.hdr-vfv .site-nav li a{color:#fff;border-bottom-color:rgba(255,255,255,.25)}
.hdr-vfv .site-nav a:hover{color:#fff;text-decoration:underline}
/* hero */
.hero-vfv{background:#0B1B33;color:#fff}
.hero-vfv .hero-photo,.hero-vfv .hero-shade{position:absolute;left:0;right:0;top:0;height:380px}
.hero-vfv .hero-photo{z-index:-2;overflow:hidden}
.hero-vfv .hero-photo::before{content:"";position:absolute;inset:0;background:url(../img/hero-480.webp) 70% 0/cover no-repeat;transform-origin:60% 30%}
.hero-vfv .hero-shade{background:linear-gradient(180deg,rgba(11,27,51,.52) 0,rgba(11,27,51,.8) 55%,#0B1B33 100%);z-index:-1}
.hero-vfv h1{color:#fff;font-size:clamp(2.3rem,9.2vw,4.4rem);line-height:1.04;text-shadow:0 2px 16px rgba(4,12,28,.65)}
.hero-vfv .hero-sub{color:#fff;text-shadow:0 1px 10px rgba(4,12,28,.6)}
.hero-vfv .hero-points .ico{color:#78C8F8}
.hero-vfv .hero-points li{font-weight:700;color:#fff}
.stars svg:nth-child(2){transform:translateY(-3px)}
/* charities */
.charities{background:var(--deep);color:#fff;padding:56px 0 44px;overflow:hidden;border-top:1px solid rgba(255,255,255,.14)}
.charities h2{color:#fff;max-width:26ch}
.charities .lead{color:#fff}
.mq-row{overflow:hidden;padding:8px 0}
.mq-row:first-of-type{margin-top:18px}
.mq-track{display:flex;width:max-content;align-items:center}
.mq-item{font:600 clamp(1.75rem,4.6vw,3.1rem)/1.15 var(--head);color:#fff;white-space:nowrap;padding:0 .35em}
.mq-b .mq-item{color:#78C8F8}
.mq-star{color:#E8283F;font-size:1.5rem;line-height:1}
.mq-row:hover .mq-track{animation-play-state:paused}
.ch-note{font-size:1rem;margin:20px 0 0;color:#fff}
/* stats */
.stats-vfv{background:#0B1B33}
.band-chev{display:none;position:absolute;right:-140px;top:-80px;width:420px;height:420px;background:url(../img/chevrons.svg) center/contain no-repeat;pointer-events:none}
.stats-vfv .stat{border-left:6px solid #E8283F}
/* cta */
.cta-vfv{background:#C8102E}
.cta-chev{display:none;position:absolute;right:-20px;top:50%;width:440px;height:440px;margin-top:-220px;background:url(../img/chevrons-light.svg) center/contain no-repeat;pointer-events:none}
.framed{box-shadow:14px 14px 0 #C8102E;border-radius:var(--r)}
@media (prefers-reduced-motion:no-preference){
  .hdr-vfv .hdr-bg::before{animation:drift 26s ease-in-out infinite alternate}
  .hdr-vfv .hdr-bg::after{animation:sheen 9s ease-in-out 1s infinite}
  .hero-vfv .hero-photo::before{animation:kb 24s ease-in-out infinite alternate}
  .stars svg{animation:twinkle 3.2s ease-in-out infinite}
  .stars svg:nth-child(2){animation-delay:.5s}.stars svg:nth-child(3){animation-delay:1s}
  .mq-a .mq-track{animation:mq 75s linear infinite}
  .mq-b .mq-track{animation:mq 85s linear infinite reverse}
  .band-chev{animation:bob 9s ease-in-out infinite alternate}
  .cta-chev{animation:bob 7s ease-in-out infinite alternate}
}
@keyframes drift{from{transform:translateX(0)}to{transform:translateX(-5%)}}
@keyframes sheen{0%,55%{transform:translateX(-120%)}100%{transform:translateX(320%)}}
@keyframes kb{from{transform:scale(1)}to{transform:scale(1.1) translate(-1.5%,1%)}}
@keyframes twinkle{0%,100%{transform:scale(1)}50%{transform:scale(1.22) rotate(12deg)}}
@keyframes bob{from{transform:translateY(0)}to{transform:translateY(26px)}}
@media (min-width:960px){
  .hdr-vfv .site-nav li a{color:#fff}
  .hdr-vfv .nav-cta a{background:#C8102E;color:#fff}
  .hero-vfv::after{content:"";position:absolute;right:-60px;top:-90px;width:540px;height:540px;background:url(../img/chevrons.svg) center/contain no-repeat;z-index:-1;pointer-events:none}
  .hero-vfv .hero-photo,.hero-vfv .hero-shade{right:auto;width:60%;height:auto;bottom:0}
  .hero-vfv .hero-photo::before{background-image:url(../img/hero-856.webp);background-position:50% 30%}
  .hero-vfv .hero-shade{background:linear-gradient(90deg,rgba(11,27,51,.84) 0,rgba(11,27,51,.6) 55%,rgba(11,27,51,.95) 92%,#0B1B33 100%)}
  .hero-vfv .wrap{padding-top:72px;padding-bottom:84px}
  .cta-chev{display:block}
  .cta-vfv h2,.cta-vfv p{max-width:22ch}
  .cta-vfv p{max-width:36ch}
  .band-chev{display:block;right:-80px;top:-60px;width:520px;height:520px}
}
"""

SPLIT_CSS = r"""
@media (min-width:960px) and (prefers-reduced-motion:no-preference){
  .js:not(.h1-ready) .hero h1.h-split{visibility:hidden;animation:unhide 0s 2.5s forwards}
  .hero h1.h-split-on .w{display:inline-block;overflow:hidden;vertical-align:top;padding-bottom:.1em;margin-bottom:-.1em}
  .hero h1.h-split-on .w>span{display:inline-block;animation:word-up .9s cubic-bezier(.2,.8,.2,1) both;animation-delay:calc(.15s + var(--i) * .07s)}
}
@keyframes word-up{from{transform:translateY(110%) rotate(5deg)}to{transform:none}}
@keyframes unhide{to{visibility:visible}}
"""


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
<ol><li>You're contacted to schedule a free pickup.</li><li>Your vehicle is picked up at no cost to you.</li><li>You receive your tax-deductible receipt.</li></ol>
<p class="preview-note">Preview only: nothing was sent. In the live site, this page also confirms the details NFM received.</p>
<p><a href="{P}index.html">Back to the home page</a></p>
</div></div></section>"""
    return page(b, key, P, f"Thank you | {b['name']}", b["description"], "donate/thank-you/", body)


def how(b, key):
    P = "../"
    body = f"""<section class="page-hero"><div class="wrap"><p class="crumbs"><a href="{P}index.html">Home</a></p><h1>How car donation works</h1><p>Donating takes three short screens online. Pickup is free, and you get a tax-deductible receipt.</p></div></section>
{steps_section(b, P)}
<section class="section section-soft"><div class="wrap"><h2>What you need before pickup</h2>
<ul class="facts"><li><strong>The title</strong>If you can't find it, tell us on the form. Title rules vary by state.</li><li><strong>The keys</strong>Have them ready for pickup day if you have them.</li><li><strong>Personal items out</strong>Clear the glove box, trunk and console before pickup day.</li></ul></div></section>
<section class="section cta-band cta-{key}"><div class="wrap"><h2>Start your donation</h2><p>Pick your vehicle type and pickup ZIP to begin.</p><a class="btn {'btn-invert' if key == 'vfv' else 'btn-sun'}" href="{P}donate/index.html">Start my donation</a></div></section>"""
    return page(b, key, P, f"How car donation works | {b['name']}", b["description"], "how-it-works/", body)


def faq(b, key):
    P = "../"
    body = f"""<section class="page-hero"><div class="wrap"><p class="crumbs"><a href="{P}index.html">Home</a></p><h1>Car donation questions</h1><p>Answers drawn from the current site. CDF approves final wording before launch.</p></div></section>
<section class="section"><div class="wrap" style="max-width:820px">{faq_list(b)}</div></section>
<section class="section cta-band cta-{key}"><div class="wrap"><h2>Ready when you are</h2><a class="btn {'btn-invert' if key == 'vfv' else 'btn-sun'}" href="{P}donate/index.html">Start my donation</a></div></section>"""
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
        h1 = f"Donate your car in {state}"
        sub = "Help a local child. Proceeds benefit Make-A-Wish."
        para = f"Wheels For Wishes picks up donated vehicles across {state} at no cost to you. Proceeds benefit Make-A-Wish chapters, helping grant wishes for children diagnosed with life-threatening medical conditions, and you get a tax-deductible receipt."
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
- **Proof up front, all taken from the current site:** the Car Donation Foundation totals, where the money goes,
  the charities or Make-A-Wish chapters that benefit, the EIN with a link to the IRS charity search, and real donor quotes.
- **Premium motion:** an animated $200M seal, rolling counters, a car that drives through the donation steps as you
  scroll, and brand-specific touches (a rippling flag header for VFV; wish stars and shooting stars for WFW).
  Motion only moves things, never fades text, pauses off screen, and switches off for visitors who ask their device
  for reduced motion.
- **Fast by design:** plain HTML, one small CSS file, one small script, self-hosted fonts, WebP images,
  and no third-party scripts.

## Test results (Nov 12, 2026)
Google Lighthouse, run locally on the home page and the donate page:

| | Performance | Accessibility | Best practices |
|---|---|---|---|
| Phone | 97 to 99 | 100 | 100 |
| Desktop | 100 | 100 | 100 |

For comparison, today's live homepage scored 46 to 77 on phones in PageSpeed Insights the same day.
The SEO score reads low on purpose: the preview tells search engines not to index it. The live build removes that.
Every page was also checked on a phone and a desktop screen: no text under 16 px, no faded text, no sideways scrolling,
and every piece of text measured against the pixels actually behind it (photos included) passes WCAG AA contrast.

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
    (out / "assets/css/site.css").write_text(css(b) + NEXT_CSS + (VFV_CSS if key == "vfv" else WFW_CSS) + SPLIT_CSS)
    (out / "assets/js/site.js").write_text(JS + MOTION_JS)
    for f in ["lato-latin-400-normal.woff2", "lato-latin-700-normal.woff2", "lato-latin-900-normal.woff2", b["head_file"]]:
        shutil.copy(HERE / "src" / f, out / "assets/fonts" / f)
    shutil.copy(HERE / "src" / "spa-seal-104.webp", out / "assets/img/spa-seal.webp")
    if key == "vfv":
        (out / "assets/img/chevrons.svg").write_text(CHEVRON_SVG)
        (out / "assets/img/chevrons-light.svg").write_text(CHEVRON_RED_SVG)
        shutil.copy(HERE / "src" / "vfv" / "flag-band.webp", out / "assets/img/flag-band.webp")
    else:
        from PIL import Image
        for k in ("ethan", "chloe", "areice", "jack"):
            Image.open(out / f"assets/img/wish-{k}.webp").convert("RGB").resize((80, 80), Image.LANCZOS).save(out / f"assets/img/av-{k}.webp", quality=82)
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
