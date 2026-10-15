#!/usr/bin/env python3
"""
Static site builder for Jenny Adib, REALTOR® — San Diego Military Realtor.

  python3 build.py        -> writes the finished site into ./public

Edit the CONFIG block below for contact details, then rebuild.
Page content lives in src/pages/*.html and blog posts in src/blog/*.html.
Each file starts with a <!-- key: value --> header block (title, description, path, ...).
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "public"

# ---------------------------------------------------------------------------
# CONFIG — fill these in (anything in [BRACKETS] is a placeholder)
# ---------------------------------------------------------------------------
CONFIG = {
    "SITE_URL": "https://militaryhomessd.com",   # no trailing slash
    "AGENT_NAME": "Jenny Adib",
    "AGENT_TITLE": "REALTOR®",
    "AGENT_DRE": "02208618",                   # California DRE salesperson license #
    "PHONE": "(619) 759-7549",
    "PHONE_TEL": "+16197597549",                   # digits only, used for tel: / sms: links
    "EMAIL": "jennyadib@militaryhomessd.com",
    "OFFICE_CITY": "San Diego, CA",
    # Must EXACTLY match the business name on your Follow Up Boss / carrier (10DLC) registration
    "LEGAL_BUSINESS_NAME": "Jenny Adib Enterprise LLC",
    "BROKERAGE": "Real Broker, LLC",
    "BROKERAGE_DRE": "02022092",
    "BROKERAGE_ADDRESS": "[Real Broker, LLC office address on file with the DRE]",
    "INSTAGRAM": "https://www.instagram.com/jennyadib/",
    "FACEBOOK": "https://www.facebook.com/jennyg96/",
    "LINKEDIN": "",
    "TIKTOK": "https://www.tiktok.com/@jennyadib",
    # Reviews (update the counts as new reviews come in)
    "GOOGLE_REVIEWS_URL": "https://maps.google.com/?cid=2141814249397543991",
    "GOOGLE_RATING": "5.0",
    "GOOGLE_REVIEW_COUNT": "13",
    "ZILLOW_RATING": "5.0",
    "ZILLOW_REVIEW_COUNT": "9",
}
YEAR = date.today().year
import time
ASSET_V = str(int(time.time()))  # cache-busting for CSS/JS

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
NAV = [
    ("Buy", [
        ("VA Loan Buyers", "/va-loan-realtor-san-diego/"),
        ("Military Home Search", "/military-homes-for-sale-san-diego/"),
        ("VA Assumable Homes", "/va-assumable-homes-san-diego/"),
        ("VA Loan Benefits in California", "/va-loan-benefits-california/"),
    ]),
    ("Sell", [
        ("Selling During a PCS", "/sell-home-during-pcs-san-diego/"),
        ("What's My Home Worth?", "/sell-home-during-pcs-san-diego/#home-value"),
    ]),
    ("PCS to San Diego", [
        ("PCS Relocation Guide", "/pcs-to-san-diego/"),
        ("Homes Near Military Bases", "/homes-near-san-diego-military-bases/"),
        ("Neighborhood Guide", "/best-places-to-live-near-naval-base-san-diego/"),
    ]),
    ("Blog", "/blog/"),
    ("About Jenny", "/about-jenny/"),
]

ICONS = {
    "chev": '<svg viewBox="0 0 10 10" aria-hidden="true"><path d="M1 3l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7h18M3 12h18M3 17h18" stroke="currentColor" stroke-width="1.5" fill="none"/></svg>',
    "close": '<svg viewBox="0 0 24 24" aria-hidden="true" width="22" height="22"><path d="M5 5l14 14M19 5L5 19" stroke="currentColor" stroke-width="1.5" fill="none"/></svg>',
    "home": '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/></svg>',
    "map": '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/><path d="M9 4v14M15 6v14"/></svg>',
    "tag": '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M3 12V4h8l10 10-8 8L3 12z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>',
    "check": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 12l5 5L20 6"/></svg>',
    "eho": '<svg viewBox="0 0 32 32" aria-hidden="true" fill="currentColor"><path d="M16 3L2 13h3v15h22V13h3L16 3zm7 22H9V12.5L16 7.3l7 5.2V25z"/><rect x="11" y="15" width="10" height="2"/><rect x="11" y="19" width="10" height="2"/></svg>',
}


def esc(s):
    return html.escape(str(s), quote=True)


def C(key):
    return CONFIG[key]


# ---------------------------------------------------------------------------
# Lead forms (Follow Up Boss + carrier SMS compliant)
# ---------------------------------------------------------------------------
def consent_block(fid):
    biz = esc(C("LEGAL_BUSINESS_NAME"))
    return f"""
      <div class="consent">
        <input type="checkbox" id="{fid}-sms" name="sms_consent" value="yes">
        <label for="{fid}-sms">I agree to be contacted by {biz} via call, email, and text for real estate services. To opt out, you can reply 'stop' at any time or reply 'help' for assistance. You can also click the unsubscribe link in the emails. Message and data rates may apply. Message frequency may vary. <a href="/privacy-policy/">Privacy Policy</a> &amp; <a href="/terms/">Terms &amp; Conditions</a>.</label>
      </div>
      <p class="consent-note">Checking the box is optional and is not required to submit this form or to work with me. Your information is never sold or shared with third parties for marketing.</p>"""


def base_fields(fid):
    return f"""
      <div class="field-row">
        <div class="field">
          <label for="{fid}-first">First name <span class="req" aria-hidden="true">*</span></label>
          <input type="text" id="{fid}-first" name="firstName" autocomplete="given-name" required aria-describedby="{fid}-first-err">
          <p class="field-error" id="{fid}-first-err" role="alert"></p>
        </div>
        <div class="field">
          <label for="{fid}-last">Last name <span class="req" aria-hidden="true">*</span></label>
          <input type="text" id="{fid}-last" name="lastName" autocomplete="family-name" required aria-describedby="{fid}-last-err">
          <p class="field-error" id="{fid}-last-err" role="alert"></p>
        </div>
      </div>
      <div class="field-row">
        <div class="field">
          <label for="{fid}-email">Email <span class="req" aria-hidden="true">*</span></label>
          <input type="email" id="{fid}-email" name="email" autocomplete="email" inputmode="email" required aria-describedby="{fid}-email-err">
          <p class="field-error" id="{fid}-email-err" role="alert"></p>
        </div>
        <div class="field">
          <label for="{fid}-phone">Phone <span class="opt">(optional)</span></label>
          <input type="tel" id="{fid}-phone" name="phone" autocomplete="tel" inputmode="tel" aria-describedby="{fid}-phone-err">
          <p class="field-error" id="{fid}-phone-err" role="alert"></p>
        </div>
      </div>"""


def select(fid, name, label, options, required=False, opt_label=True):
    opts = "".join(f'<option value="{esc(o)}">{esc(o)}</option>' for o in options)
    req = ' <span class="req" aria-hidden="true">*</span>' if required else (' <span class="opt">(optional)</span>' if opt_label else "")
    r = " required" if required else ""
    return f"""
      <div class="field">
        <label for="{fid}-{name}">{label}{req}</label>
        <select id="{fid}-{name}" name="{name}"{r} aria-describedby="{fid}-{name}-err"><option value="">Select…</option>{opts}</select>
        <p class="field-error" id="{fid}-{name}-err" role="alert"></p>
      </div>"""


BASES = ["Naval Base San Diego (32nd St)", "NAS North Island", "Naval Amphibious Base Coronado", "Naval Base Point Loma",
         "MCAS Miramar", "MCB Camp Pendleton", "MCRD San Diego", "Naval Medical Center San Diego", "Coast Guard Sector San Diego", "Not sure yet"]

FORMS = {
    "search": {
        "title": "Search VA-Friendly Homes",
        "intro": "Tell me what you're looking for and I'll send a personalized search of San Diego homes that fit your VA loan, BAH and commute.",
        "button": "Send My Home Search",
        "extra": lambda fid: f"""
      <div class="field">
        <label for="{fid}-areas">Where would you like to live? <span class="opt">(optional)</span></label>
        <input type="text" id="{fid}-areas" name="areas" placeholder="City, ZIP, neighborhood or base" autocomplete="off">
      </div>
      <div class="field-row">
        {select(fid, "price", "Price range", ["Under $600K", "$600K–$800K", "$800K–$1M", "$1M–$1.3M", "$1.3M+"])}
        {select(fid, "beds", "Bedrooms", ["1+", "2+", "3+", "4+", "5+"])}
      </div>
      <div class="field-row">
        {select(fid, "base", "Duty station", BASES)}
        {select(fid, "timeline", "When do you want to move?", ["ASAP / have orders", "1–3 months", "3–6 months", "6+ months", "Just exploring"])}
      </div>
      {select(fid, "financing", "Financing", ["VA loan", "VA assumable", "Conventional", "FHA", "Cash", "Not sure yet"])}
""",
    },
    "pcs_guide": {
        "title": "Get My Free San Diego PCS Guide",
        "intro": "Relocation checklist, military base information and neighborhood resources, sent to your inbox.",
        "button": "Send Me the PCS Guide",
        "extra": lambda fid: f"""
      <div class="field-row">
        {select(fid, "base", "Reporting to", BASES)}
        {select(fid, "timeline", "Report date", ["Within 30 days", "1–3 months", "3–6 months", "6+ months", "No orders yet"])}
      </div>
      {select(fid, "plan", "Planning to", ["Buy", "Rent first, then buy", "Not sure yet"])}
""",
    },
    "home_value": {
        "title": "Find Out What Your Military Home Is Worth",
        "intro": "Get a custom pricing analysis (not an automated guess) plus a sell vs. rent breakdown for your PCS timeline.",
        "button": "Get My Home Value",
        "extra": lambda fid: f"""
      <div class="field">
        <label for="{fid}-street">Property address <span class="req" aria-hidden="true">*</span></label>
        <input type="text" id="{fid}-street" name="street" autocomplete="street-address" required aria-describedby="{fid}-street-err">
        <p class="field-error" id="{fid}-street-err" role="alert"></p>
      </div>
      <div class="field-row">
        <div class="field">
          <label for="{fid}-city">City <span class="opt">(optional)</span></label>
          <input type="text" id="{fid}-city" name="city" autocomplete="address-level2">
        </div>
        <div class="field">
          <label for="{fid}-zip">ZIP <span class="opt">(optional)</span></label>
          <input type="text" id="{fid}-zip" name="zip" autocomplete="postal-code" inputmode="numeric">
        </div>
      </div>
      <div class="field-row">
        {select(fid, "timeline", "When are your PCS orders?", ["Within 30 days", "1–3 months", "3–6 months", "6+ months", "No orders, just planning"])}
        {select(fid, "plan", "I'm considering", ["Selling", "Renting it out", "Not sure, help me decide"])}
      </div>
""",
    },
    "contact": {
        "title": "Let's Talk About Your Move",
        "intro": "Buying, selling, or PCSing? Send a note and I'll personally get back to you, usually same day.",
        "button": "Send Message",
        "extra": lambda fid: f"""
      {select(fid, "interest", "I'm interested in", ["Buying with a VA loan", "Buying (other loan)", "Selling", "PCS relocation", "VA assumable homes", "Something else"])}
      <div class="field">
        <label for="{fid}-message">Message <span class="opt">(optional)</span></label>
        <textarea id="{fid}-message" name="message" rows="4"></textarea>
      </div>
""",
    },
}


_form_counter = {"n": 0}


def render_form(kind, heading_tag="h2", anchor=None):
    f = FORMS[kind]
    _form_counter["n"] += 1
    fid = f"f{_form_counter['n']}"
    anchor_attr = f' id="{anchor}"' if anchor else ""
    return f"""
<form class="lead-form" data-lead-form data-form-type="{kind}" novalidate{anchor_attr} aria-labelledby="{fid}-title">
  <{heading_tag} id="{fid}-title">{esc(f['title'])}</{heading_tag}>
  <p class="form-intro">{esc(f['intro'])}</p>
  <div class="form-errors sr-only" tabindex="-1" aria-live="assertive"></div>
  {base_fields(fid)}
  {f['extra'](fid)}
  <div class="hp" aria-hidden="true"><label for="{fid}-company">Company</label><input type="text" id="{fid}-company" name="company" tabindex="-1" autocomplete="off"></div>
  {consent_block(fid)}
  <button type="submit" class="btn btn-primary">{esc(f['button'])}</button>
  <div class="form-status" role="status" aria-live="polite"></div>
</form>"""


# ---------------------------------------------------------------------------
# Layout pieces
# ---------------------------------------------------------------------------
def header(current_path, solid=False):
    items = []
    for label, target in NAV:
        if isinstance(target, list):
            sub = "".join(f'<li><a href="{u}">{esc(l)}</a></li>' for l, u in target)
            sid = "sub-" + re.sub(r"[^a-z]", "", label.lower())
            items.append(f'<li class="has-sub"><button class="nav-toggle" aria-expanded="false" aria-controls="{sid}">{esc(label)} {ICONS["chev"]}</button><ul class="submenu" id="{sid}">{sub}</ul></li>')
        else:
            cur = ' aria-current="page"' if current_path == target else ""
            items.append(f'<li><a class="nav-link" href="{target}"{cur}>{esc(label)}</a></li>')
    drawer = []
    for label, target in NAV:
        if isinstance(target, list):
            drawer.append(f"<h2>{esc(label)}</h2><ul>" + "".join(f'<li><a href="{u}">{esc(l)}</a></li>' for l, u in target) + "</ul>")
        else:
            drawer.append(f'<ul><li><a href="{target}">{esc(label)}</a></li></ul>')
    drawer.append('<ul><li><a href="/contact/">Contact</a></li></ul>')
    cls = "site-header always-solid" if solid else "site-header"
    return f"""
<a class="skip-link" href="#main">Skip to main content</a>
<header class="{cls}" data-header>
  <div class="container header-inner">
    <a class="brand" href="/" aria-label="{esc(C('AGENT_NAME'))}, {esc(C('AGENT_TITLE'))} home">
      <span class="brand-name">Jenny <em>Adib</em></span>
      <span class="brand-sub"><b>{esc(C('AGENT_TITLE'))}</b> · DRE {esc(C('AGENT_DRE'))}</span>
    </a>
    <nav class="nav" aria-label="Main"><ul class="nav-list">{''.join(items)}</ul></nav>
    <a class="btn btn-primary header-cta" href="/contact/">Contact</a>
    <button class="menu-btn" aria-expanded="false" aria-controls="drawer" data-menu-open><span class="sr-only">Open menu</span>{ICONS['menu']}</button>
  </div>
</header>
<div class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="Site menu" data-drawer>
  <div class="drawer-top">
    <span class="brand-name" style="font-family:var(--serif);font-size:1.6rem">Jenny <em>Adib</em></span>
    <button class="menu-btn" data-menu-close><span class="sr-only">Close menu</span>{ICONS['close']}</button>
  </div>
  {''.join(drawer)}
  <a class="btn btn-primary" href="/sell-home-during-pcs-san-diego/#home-value">What's my home worth?</a>
  <p class="small muted" style="margin-top:24px">{esc(C('PHONE'))}<br>{esc(C('EMAIL'))}</p>
</div>"""


def footer():
    socials = [(n, C(k)) for n, k in (("Instagram", "INSTAGRAM"), ("Facebook", "FACEBOOK"), ("TikTok", "TIKTOK"), ("LinkedIn", "LINKEDIN")) if C(k)]
    social_html = "".join(f'<li><a href="{esc(u)}" rel="noopener" target="_blank">{n}</a></li>' for n, u in socials)
    return f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <a class="brand" href="/" style="color:var(--cream)"><span class="brand-name">Jenny <em>Adib</em></span><span class="brand-sub"><b>{esc(C('AGENT_TITLE'))}</b> · San Diego Military Realtor</span></a>
        <p style="margin-top:20px;max-width:32ch">Helping military families, veterans and VA buyers buy, sell and PCS across San Diego County.</p>
        <p><a href="tel:{esc(C('PHONE_TEL'))}">{esc(C('PHONE'))}</a><br><a href="mailto:{esc(C('EMAIL'))}">{esc(C('EMAIL'))}</a><br>{esc(C('OFFICE_CITY'))}</p>
      </div>
      <div>
        <h2>Buy</h2>
        <ul>
          <li><a href="/va-loan-realtor-san-diego/">VA Loan Buyers</a></li>
          <li><a href="/military-homes-for-sale-san-diego/">Military Home Search</a></li>
          <li><a href="/va-assumable-homes-san-diego/">VA Assumable Homes</a></li>
          <li><a href="/va-loan-benefits-california/">VA Loan Benefits</a></li>
        </ul>
      </div>
      <div>
        <h2>PCS &amp; Sell</h2>
        <ul>
          <li><a href="/pcs-to-san-diego/">PCS Relocation Guide</a></li>
          <li><a href="/homes-near-san-diego-military-bases/">Homes Near Bases</a></li>
          <li><a href="/best-places-to-live-near-naval-base-san-diego/">Neighborhood Guide</a></li>
          <li><a href="/sell-home-during-pcs-san-diego/">Sell During a PCS</a></li>
        </ul>
      </div>
      <div>
        <h2>Jenny</h2>
        <ul>
          <li><a href="/about-jenny/">About</a></li>
          <li><a href="/blog/">Blog</a></li>
          <li><a href="/contact/">Contact</a></li>
          <li><a href="/privacy-policy/">Privacy Policy</a></li>
          <li><a href="/terms/">Terms &amp; SMS Terms</a></li>
          {social_html}
        </ul>
      </div>
    </div>

    <div class="brokerage">
      <span class="brokerage-tile"><img class="brokerage-logo" src="/assets/img/real-logo-black.png" alt="Real Broker" width="112" height="48" loading="lazy"></span>
      <div>
        <p style="margin:0;color:var(--cream)"><strong style="font-weight:500">{esc(C('AGENT_NAME'))}, {esc(C('AGENT_TITLE'))}</strong> · CA DRE #{esc(C('AGENT_DRE'))}</p>
        <p style="margin:0">{esc(C('LEGAL_BUSINESS_NAME'))}</p>
        <p style="margin:0">Brokered by {esc(C('BROKERAGE'))} · CA DRE #{esc(C('BROKERAGE_DRE'))}</p>
      </div>
    </div>

    <div class="legal">
      <p><span class="eho">{ICONS['eho']} Equal Housing Opportunity.</span> {esc(C('AGENT_NAME'))} ({esc(C('LEGAL_BUSINESS_NAME'))}) is a licensed real estate salesperson (CA DRE #{esc(C('AGENT_DRE'))}) affiliated with {esc(C('BROKERAGE'))} (CA DRE #{esc(C('BROKERAGE_DRE'))}){(', ' + esc(C('BROKERAGE_ADDRESS'))) if not C('BROKERAGE_ADDRESS').startswith('[') else ''}. REALTOR® is a registered collective membership mark of the National Association of REALTORS®.</p>
      <p>Information on this website is for general education and is deemed reliable but not guaranteed. It is not legal, tax or lending advice. VA loan eligibility, funding fees and terms are set by the U.S. Department of Veterans Affairs and your lender. Consult a VA-approved lender, tax professional or attorney for your situation. Not affiliated with or endorsed by the U.S. Department of Veterans Affairs, the Department of Defense or any branch of the military.</p>
      <p>© {YEAR} {esc(C('LEGAL_BUSINESS_NAME'))}. All rights reserved. · <a href="/privacy-policy/">Privacy Policy</a> · <a href="/terms/">Terms &amp; Conditions</a> · <a href="/sitemap.xml">Sitemap</a></p>
    </div>
  </div>
</footer>
<div class="mobile-cta" data-mobile-cta>
  <a class="btn btn-outline" href="/military-homes-for-sale-san-diego/#search-form">Search Homes</a>
  <a class="btn btn-primary" href="/sell-home-during-pcs-san-diego/#home-value">Home Value</a>
</div>"""


def agent_schema():
    url = C("SITE_URL")
    return {
        "@context": "https://schema.org",
        "@type": "RealEstateAgent",
        "@id": url + "/#agent",
        "name": f"{C('AGENT_NAME')}, {C('AGENT_TITLE')}",
        "description": "San Diego military realtor and veteran helping VA loan buyers, PCS families and military home sellers.",
        "url": url + "/",
        "image": url + "/assets/img/jenny-adib-headshot.jpg",
        "telephone": C("PHONE_TEL"),
        "email": C("EMAIL"),
        "address": {"@type": "PostalAddress", "addressLocality": "San Diego", "addressRegion": "CA", "addressCountry": "US"},
        "areaServed": [{"@type": "City", "name": n} for n in ["San Diego", "Chula Vista", "Coronado", "National City", "Imperial Beach", "La Mesa", "Santee", "Oceanside", "Escondido", "El Cajon"]],
        "knowsAbout": ["VA loans", "PCS relocation", "VA assumable mortgages", "Military home buying", "Military home selling"],
        "parentOrganization": {"@type": "RealEstateAgent", "name": C("BROKERAGE"), "identifier": f"CA DRE #{C('BROKERAGE_DRE')}"},
        "identifier": f"CA DRE #{C('AGENT_DRE')}",
        "sameAs": [u for u in (C("INSTAGRAM"), C("FACEBOOK"), C("TIKTOK"), C("LINKEDIN")) if u],
    }


def faq_schema(body):
    items = re.findall(r'<details class="faq-item">\s*<summary>(.*?)</summary>\s*<div>(.*?)</div>\s*</details>', body, re.S)
    if not items:
        return None
    strip = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in items]}


def breadcrumb_schema(crumbs):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": C("SITE_URL") + u} for i, (n, u) in enumerate(crumbs)]}


def page_shell(meta, body, schemas):
    path = meta["path"]
    canonical = C("SITE_URL") + path
    og_img = C("SITE_URL") + meta.get("og_image", "/assets/img/hero-navy-family-walking.jpg")
    robots = '<meta name="robots" content="noindex, follow">' if meta.get("noindex") else ""
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas if s)
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta['title'])}</title>
<meta name="description" content="{esc(meta['description'])}">
<link rel="canonical" href="{esc(canonical)}">
{robots}
<meta property="og:type" content="{'article' if meta.get('date') else 'website'}">
<meta property="og:title" content="{esc(meta['title'])}">
<meta property="og:description" content="{esc(meta['description'])}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{esc(og_img)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1a1918">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Jost:wght@300;400;500;600&display=swap">
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_V}">
{ld}
<!-- Follow Up Boss Pixel (website activity tracking): paste the snippet from FUB > Admin > Pixel here -->
</head>
<body data-phone="{esc(C('PHONE'))}" data-tel="{esc(C('PHONE_TEL'))}">
<script>document.documentElement.classList.remove('no-js')</script>
{header(path, solid=meta.get('solid_header', False))}
<main id="main" tabindex="-1">
{body}
</main>
{footer()}
<script src="/assets/js/site.js?v={ASSET_V}" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Content loading
# ---------------------------------------------------------------------------
META_RE = re.compile(r"^\s*<!--(.*?)-->", re.S)


def load(path):
    text = path.read_text(encoding="utf-8")
    m = META_RE.match(text)
    meta = {}
    if m:
        for line in m.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        text = text[m.end():]
    return meta, text


def post_card(p, dark=False):
    d = date.fromisoformat(p["date"]).strftime("%B %-d, %Y")
    return f"""<article class="post-card">
  <p class="meta">{esc(p.get('category', 'Market Update'))} · <time datetime="{p['date']}">{d}</time></p>
  <h3><a href="{p['path']}">{esc(p['h1_plain'])}</a></h3>
  <p class="{'muted' if not dark else 'muted'}">{esc(p['excerpt'])}</p>
</article>"""


STAR = '<svg viewBox="0 0 20 20" aria-hidden="true" width="18" height="18"><path fill="currentColor" d="M10 1.5l2.6 5.6 6.1.7-4.5 4.2 1.2 6-5.4-3.1L4.6 18l1.2-6L1.3 7.8l6.1-.7z"/></svg>'


# Client reviews (shown in the order listed; homepage shows the first 3).
# "name" is optional — add e.g. "Maria G." once you have it.
REVIEWS = [
    {"headline": "She truly fought for us.", "label": "First-Time Buyers", "name": "",
     "text": """Working with Jenny was nothing short of incredible! From start to finish, she went above and beyond to make our first home purchase a success. Even after my husband and I backed out of our first escrow due to inspection findings, Jenny stayed patient, understanding, and completely supportive — never pressuring us, always guiding us with honesty and clarity.

She truly fought for us and negotiated an amazing deal — $46,000 in seller credits, the seller paid off our largest credit card, covered our closing costs, and even bought down our rate permanently from 5.75% to 5.3%! That kind of result doesn’t just happen — it’s a testament to Jenny’s skill, experience, and dedication to her clients.

Beyond the numbers, Jenny took the time to educate us through every step, helping us understand our options and make confident decisions. Thanks to her, we now own our very first home and investment property — and along the way, we gained not just a great realtor, but a new friend. 💛

If you’re looking for someone who’s not only a fierce negotiator but also genuinely cares about your goals, Jenny is the one."""},
    {"headline": "She got my home VA approved, and the entire complex!", "label": "VA Buyer · Navy Veteran", "name": "",
     "text": """Jenny did such an amazing job helping me find my perfect home for myself and my dog! I’ve worked with Jenny before in the Navy and I knew she was steer me in the right direction. As a first time home buyer I was really unsure of the whole process but Jenny is super knowledgeable and assured me that buying a home is beneficial! She was able to find me a home within my budget and get all the closing costs paid for. We were able to find something that fit my desired location and style in a matter of weeks. Not only was she able to get my home VA approved but the entire complex! I commend her for her hard work that she puts in day in and day out. She was always updating me on what was going on no matter the time of day. I truly appreciated her help through the whole process I definitely recommend her to anyone who chooses to buy."""},
    {"headline": "I always felt like I had someone in my corner.", "label": "First-Time Buyer", "name": "",
     "text": """I could not have asked for a better experience buying my first home. From the very beginning, she was incredibly helpful, responsive, patient, and genuinely invested in making sure I found the right home.

As a first-time homebuyer, there were plenty of parts of the process that were new to me, and she did an excellent job walking me through everything, answering my questions, and making the entire experience feel manageable. I always felt like I had someone in my corner who cared about more than simply getting a deal done.

I’m extremely grateful for all of the time, effort, and guidance she provided throughout the process. Buying my first home was a major milestone for me, and she helped make it an exciting and memorable experience. I would absolutely recommend her to anyone looking to buy or sell a home. Thank you for helping me become a homeowner!"""},
    {"headline": "She won us over immediately.", "label": "Home Buyers", "name": "",
     "text": """Jenny is an amazing realtor. She is so kind and is genuinely looking to help you in any way she can. When I first got in contact with her, I advised her our family was already working with another realtor, but she still took the chance on us. She took time out of her day to talk with us and give us information that had yet been provided to us. Needless to say, she won us over immediately. We highly recommend her! In the end we ended up in an amazing home with an amazing community; it couldn’t have happened without her. Thank you to Jenny and all her team."""},
    {"headline": "Cannot recommend her enough!", "label": "First-Time Buyer", "name": "",
     "text": """Jenny was professional, knowledgeable and a pleasure to work with. This was my first home buying experience and she made sure that I was comfortable and completely understood what to expect along the way. She was extremely responsive and there to answer any questions that I had! Cannot recommend her enough!"""},
]


def review_cards(limit=None):
    cards = []
    for i, r in enumerate(REVIEWS[:limit]):
        paras = "".join(f"<p>{esc(x.strip())}</p>" for x in r["text"].split("\n\n"))
        who = esc(r["name"]) + " · " if r["name"] else ""
        cards.append(f"""<figure class="review-card">
        <span class="stars" role="img" aria-label="5 out of 5 stars">{STAR * 5}</span>
        <h3 class="review-headline">“{esc(r['headline'])}”</h3>
        <blockquote class="review-text" id="rv-{i}">{paras}</blockquote>
        <button type="button" class="review-more" aria-expanded="false" aria-controls="rv-{i}">Read full review</button>
        <figcaption>{who}{esc(r['label'])}</figcaption>
      </figure>""")
    return '<div class="review-grid">' + "".join(cards) + "</div>"


def reviews_block(limit=None):
    stars = STAR * 5
    return f"""
<section class="section-sm on-cream reviews" aria-labelledby="reviews-title">
  <div class="container">
    <div class="section-head center">
      <p class="eyebrow">Client reviews</p>
      <h2 id="reviews-title">Families who trusted me with their <em>next chapter</em></h2>
    </div>
    {review_cards(limit)}
    <div class="btn-row" style="justify-content:center;margin-top:32px">
      <a class="btn btn-outline" href="{esc(C('GOOGLE_REVIEWS_URL'))}" target="_blank" rel="noopener">Read my Google reviews</a>
      <a class="btn btn-primary" href="{esc(C('GOOGLE_REVIEWS_URL'))}" target="_blank" rel="noopener">Leave a review</a>
    </div>
  </div>
</section>"""


def apply_tokens(body, posts):
    for k, v in CONFIG.items():
        body = body.replace("{{" + k + "}}", esc(v))
    body = re.sub(r"\{\{form:(\w+)(?::(\w[\w-]*))?\}\}", lambda m: render_form(m.group(1), anchor=m.group(2)), body)
    body = body.replace("{{reviews:3}}", reviews_block(3)).replace("{{reviews}}", reviews_block())
    body = body.replace("{{latest_posts}}", "".join(post_card(p, True) for p in posts[:3]))
    body = body.replace("{{all_posts}}", "".join(post_card(p) for p in posts))
    for k, v in ICONS.items():
        body = body.replace("{{icon:" + k + "}}", v)
    return body


def page_hero(meta, crumbs):
    img = meta.get("hero_img")
    media = f'<div class="page-hero-media"><img src="{img}" alt="" width="1600" height="900" fetchpriority="high"></div>' if img else ""
    cls = "page-hero has-img" if img else "page-hero"
    bc = "".join(
        f'<li><a href="{u}">{esc(n)}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{esc(n)}</li>'
        for i, (n, u) in enumerate(crumbs))
    eyebrow = f'<p class="eyebrow">{esc(meta["eyebrow"])}</p>' if meta.get("eyebrow") else ""
    extra = meta.get("hero_extra", "")
    lede = f'<p class="lede">{meta["lede"]}</p>' if meta.get("lede") else ""
    return f"""
<section class="{cls}">
  {media}
  <div class="container">
    <nav class="breadcrumbs" aria-label="Breadcrumb"><ol>{bc}</ol></nav>
    {eyebrow}
    <h1>{meta['h1']}</h1>
    {lede}
    {extra}
  </div>
</section>"""


def write(path, content):
    dest = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")


def build():
    posts = []
    for f in sorted((SRC / "blog").glob("*.html")):
        meta, body = load(f)
        meta["h1_plain"] = re.sub(r"<[^>]+>", "", meta["h1"])
        meta["body"] = body
        posts.append(meta)
    posts.sort(key=lambda p: p["date"], reverse=True)

    sitemap = []

    for f in sorted((SRC / "pages").glob("*.html")):
        meta, body = load(f)
        body = apply_tokens(body, posts)
        schemas = []
        if meta.get("layout") == "home":
            schemas.append(agent_schema())
            schemas.append({"@context": "https://schema.org", "@type": "WebSite", "name": f"{C('AGENT_NAME')} | San Diego Military Realtor", "url": C("SITE_URL") + "/"})
            content = body
        else:
            crumbs = [("Home", "/")] + ([("Blog", "/blog/")] if meta.get("parent") == "blog" else []) + [(meta.get("crumb", meta["title"].split("|")[0].strip()), meta["path"])]
            schemas.append(breadcrumb_schema(crumbs))
            if meta.get("agent_schema"):
                schemas.append(agent_schema())
            content = page_hero(meta, crumbs) + body
        schemas.append(faq_schema(body))
        write(meta["path"], page_shell(meta, content, schemas))
        if not meta.get("noindex"):
            sitemap.append((meta["path"], meta.get("priority", "0.7")))

    for p in posts:
        body = apply_tokens(p["body"], posts)
        d = date.fromisoformat(p["date"]).strftime("%B %-d, %Y")
        p2 = dict(p)
        p2["eyebrow"] = p.get("category", "Market Update")
        p2["hero_extra"] = f'<p class="post-meta">By {esc(C("AGENT_NAME"))} · <time datetime="{p["date"]}">{d}</time></p>'
        p2["crumb"] = p["h1_plain"]
        p2["parent"] = "blog"
        crumbs = [("Home", "/"), ("Blog", "/blog/"), (p["h1_plain"], p["path"])]
        others = [o for o in posts if o["path"] != p["path"]][:2]
        article = f"""
<section class="section">
  <div class="container content-layout">
    <article class="prose">{body}
      <hr class="rule">
      <p class="muted small">Written by {esc(C('AGENT_NAME'))}, {esc(C('AGENT_TITLE'))}, a U.S. Navy Veteran and San Diego military realtor with {esc(C('BROKERAGE'))}. This article is general information, not lending, legal or tax advice.</p>
    </article>
    <aside><div class="sticky-aside">{render_form(p.get('form', 'contact'), 'h2')}</div></aside>
  </div>
</section>
<section class="section-sm on-cream"><div class="container"><div class="section-head"><p class="eyebrow">Keep reading</p></div><div class="grid grid-2">{''.join(post_card(o) for o in others)}</div></div></section>"""
        schema = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["h1_plain"], "description": p["description"],
                  "datePublished": p["date"], "dateModified": p.get("updated", p["date"]),
                  "author": {"@type": "Person", "name": C("AGENT_NAME"), "url": C("SITE_URL") + "/about-jenny/"},
                  "image": C("SITE_URL") + p.get("hero_img", "/assets/img/hero-navy-family-walking.jpg"),
                  "mainEntityOfPage": C("SITE_URL") + p["path"]}
        write(p["path"], page_shell(p2, page_hero(p2, crumbs) + article, [breadcrumb_schema(crumbs), schema, faq_schema(body)]))
        sitemap.append((p["path"], "0.6"))

    today = date.today().isoformat()
    urls = "".join(f"<url><loc>{esc(C('SITE_URL') + u)}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>" for u, pr in sitemap)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /pcs-guide/\n\nSitemap: {C('SITE_URL')}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(sitemap)} indexed pages + sitemap into {OUT}")


if __name__ == "__main__":
    build()
