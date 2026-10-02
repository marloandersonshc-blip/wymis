#!/usr/bin/env python3
"""Static site generator for wymis.com.

Edit content in this file, then run:  python3 tools/build.py
It writes every .html page plus sitemap.xml, robots.txt, llms.txt and llms-full.txt to the repo root.
"""
import json, os, datetime, html, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://wymis.com"
EMAIL = "info@wymis.com"
NAME = "WYMIS"
FULL = "What You Missed In School"
FOUNDER = "Dr. Barry K. Jackson, Ph.D."
OG_IMG = SITE + "/assets/img/og/wymis-og.png"
TODAY = datetime.date.today().isoformat()
FONTS = "https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@112..125,500..800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap"

# ---------------------------------------------------------------- helpers
def ver(rel):
    """Short content hash so browsers fetch a fresh file whenever it changes."""
    return hashlib.md5(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:8]
CSS_V = ver("assets/css/site.css")
JS_V = ver("assets/js/site.js")

def esc(s): return html.escape(s, quote=True)

def unsplash(pid, w): return f"https://images.unsplash.com/photo-{pid}?auto=format&fit=crop&w={w}&q=75"

def img(pid, alt, sizes="(max-width: 900px) 100vw, 50vw", eager=False, w=1200, h=900, maxw=1600):
    widths = [x for x in (480, 800, 1200, 1600, 2000) if x <= maxw]
    srcset = ", ".join(f"{unsplash(pid, x)} {x}w" for x in widths)
    load = 'fetchpriority="high" loading="eager"' if eager else 'loading="lazy"'
    return (f'<img src="{unsplash(pid, widths[-2] if len(widths) > 1 else widths[0])}" srcset="{srcset}" sizes="{sizes}" '
            f'alt="{esc(alt)}" width="{w}" height="{h}" {load} decoding="async">')

ARROW = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>'

# ---------------------------------------------------------------- content data
PHOTOS = {
    "hero":       ("1561409958-c0e6ad782a81", "Graduates throwing their caps in the air"),
    "collab":     ("1758270705518-b61b40527e76", "Diverse group of students collaborating around a laptop"),
    "hands":      ("1758270704286-83476deb3bd1", "Students raising their hands in a lecture hall"),
    "smiling":    ("1758270704524-596810e891b5", "Students smiling in a lecture hall classroom"),
    "listening":  ("1758270705067-0d7edee57af0", "Students listening attentively in a lecture hall"),
    "classroom":  ("1524178232363-1fb2b075b655", "Classroom of students facing a projector screen"),
    "teacher":    ("1758270704925-fa59d93119c1", "Teacher leading a lesson in a classroom"),
    "grad":       ("1523580846011-d3a5bc25702b", "Smiling graduate in a cap and gown"),
    "handshake":  ("1549923746-c502d488b3ea", "Two professionals shaking hands and smiling"),
    "phoenix":    ("1617407867182-2c3730f7fe29", "Phoenix skyline silhouetted at sunset"),
    "vegas":      ("1723585126886-f31a77294a43", "The Las Vegas Strip at night"),
    "memphis":    ("1577055383519-ca48a5d859be", "Memphis riverfront pyramid at sunset"),
}

MODULES = [
    dict(code="WYM 101", slug="financial-literacy", title="Financial Literacy",
         pid="1554224155-6726b3ff858f", alt="Person reviewing a budget on paper with a pen and calculator",
         intro="Money decisions start the day the first paycheck arrives. This module gives students a working plan for it.",
         summary="What financial literacy is, budgeting, credit, and simple investing, adapted for a first paycheck, first apartment, and first credit decisions.",
         topics=["What financial literacy is", "Budgeting", "Credit", "Simple investing"],
         applied="Built around a first paycheck, a first apartment, and first credit decisions."),
    dict(code="WYM 102", slug="business-administration", title="Business Administration",
         pid="1556761175-5973dc0f32e7", alt="Young professional presenting to colleagues in a meeting",
         intro="Students learn how businesses are built and run, and what it takes to start one of their own.",
         summary="What a business is, for-profit versus nonprofit models, basic business structures, how to start a simple business, and business ethics.",
         topics=["What a business is", "For-profit versus nonprofit models", "Basic business structures", "How to start a simple business", "Business ethics"],
         applied=""),
    dict(code="WYM 103", slug="soft-skills", title="Soft Skills",
         pid="1573497620053-ea5300f94f21", alt="Two women in a professional conversation at a table",
         intro="The skills that appear in every job description and rarely in a class schedule.",
         summary="Professional communication, teamwork and collaboration, professionalism and work ethic, and problem-solving and adaptability.",
         topics=["Professional communication", "Teamwork and collaboration", "Professionalism and work ethic", "Problem-solving and adaptability"],
         applied=""),
    dict(code="WYM 104", slug="etiquette", title="Etiquette",
         pid="1521791136064-7986c2920216", alt="Two people shaking hands across a table",
         intro="How to carry yourself at the table, in the interview, and online.",
         summary="Everyday social etiquette, professional and interview etiquette, dining etiquette, and digital etiquette.",
         topics=["Everyday social etiquette", "Professional and interview etiquette", "Dining etiquette", "Digital etiquette"],
         applied=""),
    dict(code="WYM 105", slug="networking-principles", title="Networking Principles",
         pid="1515169067868-5387ec356754", alt="Small group of people talking together at an event",
         intro="Opportunities move through people. Students learn to introduce themselves, work a room, and follow up.",
         summary="What networking is, building a personal introduction, working a room at an event or conference, and following up effectively.",
         topics=["What networking is", "Building a personal introduction", "Working a room at an event or conference", "Following up effectively"],
         applied=""),
    dict(code="WYM 106", slug="ai-and-technology", title="AI and Technology",
         pid="1604933762021-54a5858c9832", alt="Young woman with braids working on a laptop",
         intro="AI is already reshaping the jobs students are about to enter. Students learn what it is and how to use it well.",
         summary="What artificial intelligence is, how it is changing industries and jobs, using AI tools well, and responsible, ethical use.",
         topics=["What artificial intelligence is", "How AI is changing industries and jobs", "Using AI tools well", "Responsible, ethical use"],
         applied=""),
    dict(code="WYM 107", slug="branding-and-marketing", title="Branding and Marketing",
         pid="1542744173-8e7e53415bb0", alt="Presenter speaking to a team seated with laptops",
         intro="Every graduate has a personal brand, managed or not. Students learn to build one on purpose and reach an audience with it.",
         summary="The difference between branding and marketing, personal branding, building a brand identity, and reaching an audience.",
         topics=["The difference between branding and marketing", "Personal branding", "Building a brand identity", "Reaching an audience"],
         applied=""),
]

CITIES = [
    dict(name="Phoenix", state="Arizona", abbr="AZ", coords="33.45&deg; N &middot; 112.07&deg; W", photo="phoenix"),
    dict(name="Las Vegas", state="Nevada", abbr="NV", coords="36.17&deg; N &middot; 115.14&deg; W", photo="vegas"),
    dict(name="Memphis", state="Tennessee", abbr="TN", coords="35.15&deg; N &middot; 90.05&deg; W", photo="memphis"),
]

FAQS = [
    ("What is WYMIS?",
     "WYMIS, short for What You Missed In School, is a practical “thirteenth grade” workforce readiness and life skills program. It teaches graduating seniors and young adults the everyday skills school often leaves out: managing money, holding a job, communicating professionally, and navigating adult life with confidence."),
    ("Who is WYMIS for?",
     "WYMIS is designed for ages 16 to 26. That includes graduating high school seniors preparing for a first job, first apartment, or college; young adults entering the workforce; and schools, community organizations, and workforce programs looking for a ready-to-use, real-world curriculum."),
    ("How long is the WYMIS program?",
     "The full WYMIS program runs 8 to 12 weeks as a cohort, with students moving through the modules together as a group."),
    ("What does the WYMIS curriculum cover?",
     "Seven modules: Financial Literacy, Business Administration, Soft Skills, Etiquette, Networking Principles, AI and Technology, and Branding and Marketing. Each one covers a skill area students consistently report feeling underprepared for after high school."),
    ("What delivery formats are available?",
     "Every module is available in two formats: a 75-minute single-class session for a focused introduction, or a 3-day unit that adds hands-on practice through role-play, group work, and applied projects."),
    ("Can schools use individual modules instead of the full program?",
     "Yes. Modules can be delivered individually or combined into a full 8 to 12 week cohort experience."),
    ("Where has WYMIS been piloted?",
     "WYMIS has been piloted in Phoenix, Arizona; Las Vegas, Nevada; and Memphis, Tennessee, working directly with students to refine the curriculum from real classroom experience and feedback."),
    ("Who created WYMIS?",
     "WYMIS was created by Dr. Barry K. Jackson, Ph.D., a workforce and youth development leader. He is a Senior Career Services Advisor at Bryan University in Tempe, Arizona, and previously served as a Director of Programs with the National Urban League and as Executive Director of The Memphis Youth Coalition."),
    ("Why is it called the thirteenth grade?",
     "Because it picks up where twelfth grade ends. WYMIS covers the practical lessons students need right after graduation, the ones a diploma does not include."),
    ("Can my school or organization bring WYMIS to our community?",
     "Yes. Schools, community organizations, and workforce programs can partner with WYMIS today. The long-term plan is a licensed, repeatable model that organizations can run in their own communities."),
]

# ---------------------------------------------------------------- JSON-LD
ORG = {
    "@type": "EducationalOrganization", "@id": SITE + "/#org", "name": NAME, "alternateName": FULL,
    "url": SITE + "/", "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/brand/icon-512.png", "width": 512, "height": 512},
    "image": OG_IMG, "email": EMAIL,
    "description": "WYMIS (What You Missed In School) is a cohort-based “thirteenth grade” workforce readiness and life skills program for ages 16 to 26.",
    "founder": {"@id": SITE + "/about#barry-jackson"},
    "areaServed": [{"@type": "City", "name": c["name"], "containedInPlace": {"@type": "State", "name": c["state"]}} for c in CITIES],
    "knowsAbout": [m["title"] for m in MODULES] + ["Workforce readiness", "Life skills education"],
}
PERSON = {"@type": "Person", "@id": SITE + "/about#barry-jackson", "name": "Barry K. Jackson", "honorificPrefix": "Dr.",
          "honorificSuffix": "Ph.D.", "jobTitle": "Creator of WYMIS", "url": SITE + "/about",
          "description": "Workforce and youth development leader; Senior Career Services Advisor at Bryan University; former Director of Programs with the National Urban League and Executive Director of The Memphis Youth Coalition; creator of WYMIS.",
          "worksFor": [{"@id": SITE + "/#org"}, {"@type": "CollegeOrUniversity", "name": "Bryan University"}],
          "hasOccupation": [{"@type": "Occupation", "name": "Senior Career Services Advisor"}],
          "affiliation": [{"@type": "Organization", "name": "National Urban League"}, {"@type": "Organization", "name": "The Memphis Youth Coalition"}],
          "hasCredential": [{"@type": "EducationalOccupationalCredential", "credentialCategory": "degree", "name": "Master of Divinity"}],
          "knowsAbout": ["Workforce development", "Youth development", "Career services", "Employer relations", "Pastoral counseling"]}
WEBSITE = {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": NAME, "alternateName": FULL,
           "publisher": {"@id": SITE + "/#org"}, "inLanguage": "en-US"}

def course(m):
    return {"@type": "Course", "@id": f"{SITE}/curriculum#{m['slug']}", "name": f"{m['title']} ({m['code']})", "courseCode": m["code"],
            "description": m["summary"], "url": f"{SITE}/curriculum#{m['slug']}", "provider": {"@id": SITE + "/#org"},
            "teaches": m["topics"], "educationalLevel": "Beginner", "inLanguage": "en-US", "typicalAgeRange": "16-26",
            "hasCourseInstance": [
                {"@type": "CourseInstance", "courseMode": "Onsite", "courseWorkload": "PT75M", "name": "75-minute session"},
                {"@type": "CourseInstance", "courseMode": "Onsite", "courseSchedule": {"@type": "Schedule", "duration": "P3D", "repeatCount": 1}, "name": "3-day applied unit"}],
            "offers": {"@type": "Offer", "category": "Partnership", "url": SITE + "/partner"}}

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}

# ---------------------------------------------------------------- layout
NAV = [("program", "Program"), ("curriculum", "Curriculum"), ("pilots", "Pilots"), ("about", "About"), ("faq", "FAQ")]

def head(p, base):
    canon = SITE + ("/" if p["slug"] == "index" else "/" + p["slug"])
    graph = [ORG, WEBSITE, {"@type": p.get("pagetype", "WebPage"), "@id": canon + "#webpage", "url": canon, "name": p["title"],
             "description": p["desc"], "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": SITE + "/#org"},
             "primaryImageOfPage": OG_IMG, "inLanguage": "en-US", "dateModified": TODAY}]
    if p["slug"] not in ("index", "404"):
        graph.append(crumbs_ld([("Home", "/"), (p["crumb"], "/" + p["slug"])]))
    graph += p.get("ld", [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    robots = "noindex, follow" if p["slug"] == "404" else "index, follow, max-image-preview:large, max-snippet:-1"
    return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(p['title'])}</title>
<meta name="description" content="{esc(p['desc'])}">
<meta name="robots" content="{robots}">
{'' if p['slug']=='404' else f'<link rel="canonical" href="{canon}">'}
<meta name="author" content="{esc(FOUNDER)}">
<meta name="theme-color" content="#0E1A2B">
<meta name="geo.region" content="US-AZ">
<meta name="geo.placename" content="Phoenix, Arizona">
<meta name="geo.position" content="33.4484;-112.0740">
<meta name="ICBM" content="33.4484, -112.0740">
<meta property="og:type" content="website">
<meta property="og:site_name" content="WYMIS: What You Missed In School">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{esc(p.get('og', p['title']))}">
<meta property="og:description" content="{esc(p['desc'])}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{OG_IMG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="WYMIS logo with the line: Welcome to the thirteenth grade.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(p.get('og', p['title']))}">
<meta name="twitter:description" content="{esc(p['desc'])}">
<meta name="twitter:image" content="{OG_IMG}">
<link rel="icon" href="{base}favicon.ico" sizes="48x48">
<link rel="icon" href="{base}assets/img/brand/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{base}assets/img/brand/apple-touch-icon.png">
<link rel="manifest" href="{base}site.webmanifest">
<link rel="alternate" type="text/plain" title="LLM summary" href="{base}llms.txt">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{base}assets/css/site.css?v={CSS_V}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""

def nav(active, base):
    home = base or "./"
    items = "".join(f'<li><a href="{base}{s}"{" aria-current=\"page\"" if s == active else ""}>{t}</a></li>' for s, t in NAV)
    return f"""<nav class="nav" aria-label="Main">
  <div class="wrap nav-in">
    <a class="brand" href="{home}" aria-label="WYMIS home"><img src="{base}assets/img/brand/wymis-logo-light.svg" alt="WYMIS: What You Missed In School" width="225" height="40"></a>
    <button class="menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false" aria-controls="navLinks">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <ul class="nav-links" id="navLinks" data-open="false">
      {items}
      <li><a class="btn btn-primary" href="{base}partner"{" aria-current=\"page\"" if active == "partner" else ""}>Partner With Us</a></li>
    </ul>
  </div>
</nav>
"""

def footer(base):
    home = base or "./"
    mods = "".join(f'<a href="{base}curriculum#{m["slug"]}">{m["title"]}</a>' for m in MODULES[:5])
    return f"""<footer class="site-foot">
  <div class="wrap foot-top">
    <div class="foot-brand">
      <a href="{home}" aria-label="WYMIS home"><img src="{base}assets/img/brand/wymis-logo-light.svg" alt="WYMIS: What You Missed In School" width="248" height="44" loading="lazy"></a>
      <p>A practical thirteenth grade for workforce readiness and life skills. Cohort-based, skills-first, built for ages 16 to 26.</p>
    </div>
    <div class="foot-col"><h2>Program</h2><a href="{base}program">How it works</a><a href="{base}curriculum">Curriculum</a><a href="{base}pilots">Pilot cities</a><a href="{base}faq">FAQ</a></div>
    <div class="foot-col"><h2>Modules</h2>{mods}<a href="{base}curriculum">All seven modules</a></div>
    <div class="foot-col"><h2>Connect</h2><a href="{base}about">About &amp; vision</a><a href="{base}partner">Partner with us</a><a href="mailto:{EMAIL}">{EMAIL}</a></div>
  </div>
  <div class="wrap foot-bot">
    <span>&copy; <span id="year">2026</span> WYMIS. All rights reserved.</span>
    <span>Photography from <a href="https://unsplash.com" rel="noopener">Unsplash</a></span>
  </div>
</footer>
<script src="{base}assets/js/site.js?v={JS_V}" defer></script>
</body>
</html>
"""

def page_hero(eyebrow, h1, lede, photo, crumb, base):
    pid, alt = PHOTOS[photo]
    return f"""<header class="page-hero">
  <div class="ph-img">{img(pid, alt, sizes="100vw", eager=True, w=2000, h=1000, maxw=2000)}</div>
  <div class="wrap ph-in">
    <ol class="crumbs" aria-label="Breadcrumb"><li><a href="{base or './'}">Home</a></li><li aria-current="page">{crumb}</li></ol>
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1}</h1>
    <p class="ph-lede">{lede}</p>
  </div>
</header>
"""

def cta(base, h="Bring WYMIS to your students.", p="Full cohorts, single modules, or 3-day units. Tell us what fits your schedule and we will build the plan with you."):
    return f"""<section class="cta-band grid-bg" aria-label="Partner with WYMIS">
  <div class="wrap cta-in">
    <div><h2>{h}</h2><p>{p}</p></div>
    <a class="btn btn-primary" href="{base}partner">Partner With Us {ARROW}</a>
  </div>
</section>
"""

FEATS = [
    ('<circle cx="11" cy="11" r="4"/><circle cx="22" cy="11" r="4"/><path d="M3 26c0-4.4 3.6-8 8-8s8 3.6 8 8M15 21.5c1.4-2.1 4-3.5 7-3.5 4.4 0 8 3.6 8 8"/>',
     "Cohort-based", "Students move through the program together as a group, which builds accountability, peer support, and a sense of shared progress."),
    ('<rect x="4" y="6" width="24" height="22" rx="2"/><path d="M4 12h24M10 3v6M22 3v6M9 17h4M15 17h4M21 17h2M9 22h4M15 22h4"/>',
     "8 to 12 weeks", "The full program is sized to fit a semester and is ideally suited for ages 16 to 26."),
    ('<path d="M16 4l11 6-11 6L5 10z"/><path d="M9 12.5V19c0 2.2 3.1 4 7 4s7-1.8 7-4v-6.5M27 10v8"/>',
     "Skills-first", "Every module is built around real situations students will face immediately after graduation."),
    ('<circle cx="16" cy="16" r="11"/><path d="M16 9v7l5 3"/>',
     "Flexible delivery", "Run any module as a focused 75-minute class session or a deeper 3-day unit with role-play and applied projects."),
]
def feats():
    return '<div class="feat-grid">' + "".join(
        f'<div class="feat"><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">{i}</svg><h3>{t}</h3><p>{d}</p></div>'
        for i, t, d in FEATS) + "</div>"

def formats_block(active="short"):
    return f"""<div class="formats">
  <article class="fmt" data-fmt="short" data-active="{'true' if active=='short' else 'false'}">
    <div class="fmt-time">75<small>minutes</small></div>
    <h3>Single-class session</h3>
    <p>A focused introduction to one module that fits inside a standard class period or workshop slot.</p>
    <ul class="checks"><li>Core concepts in one sitting</li><li>Drops into an existing schedule</li><li>Works for advisory periods, assemblies, and events</li></ul>
  </article>
  <article class="fmt" data-fmt="long" data-active="{'true' if active=='long' else 'false'}">
    <div class="fmt-time">3<small>day unit</small></div>
    <h3>Applied unit</h3>
    <p>A deeper version of the module that gives students real practice time with the skill.</p>
    <ul class="checks"><li>Hands-on role-play</li><li>Group work</li><li>Applied projects</li></ul>
  </article>
</div>"""

def cities_block(light=False, base=""):
    out = []
    for c in CITIES:
        pid, alt = PHOTOS[c["photo"]]
        out.append(f"""<article class="city">
      <div class="photo">{img(pid, alt, sizes="(max-width: 860px) 100vw, 33vw", w=800, h=600, maxw=1200)}</div>
      <div class="city-body"><div class="city-top"><span>{c['state']}</span><span class="tag">Pilot city</span></div><h3>{c['name']}</h3><p>{c['coords']}</p></div>
    </article>""")
    return f'<div class="cities{" light" if light else ""}">' + "".join(out) + "</div>"

def audience():
    return """<div class="aud">
  <article class="aud-item"><span class="aud-label">Ages 16 to 26</span><h3>Graduating seniors</h3><p>Preparing for a first job, a first apartment, or college, and ready to handle the decisions that come with each.</p></article>
  <article class="aud-item"><span class="aud-label">Early career</span><h3>Young adults entering the workforce</h3><p>People who want the practical skills schools often do not teach, from professional communication to first credit decisions.</p></article>
  <article class="aud-item"><span class="aud-label">Partners</span><h3>Schools &amp; organizations</h3><p>Schools, community organizations, and workforce programs looking for a ready-to-use, real-world curriculum.</p></article>
</div>"""

def facts_box():
    rows = [("Full name", "What You Missed In School"), ("Type", "Workforce readiness &amp; life skills program"),
            ("Ages", "16 to 26"), ("Length", "8 to 12 weeks"), ("Modules", "7"), ("Formats", "75-minute session or 3-day unit"),
            ("Pilot cities", "Phoenix, Las Vegas, Memphis"), ("Created by", FOUNDER)]
    return '<aside class="facts" aria-labelledby="facts-h"><h2 id="facts-h">WYMIS at a glance</h2><dl>' + "".join(
        f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows) + "</dl></aside>"

# ---------------------------------------------------------------- pages
def page_index(base):
    pid, alt = PHOTOS["hero"]
    cpid, calt = PHOTOS["collab"]
    chips = "".join(f'<a class="mod-chip" href="{base}curriculum#{m["slug"]}"><span class="code">{m["code"][4:]}</span><b>{m["title"]}</b>{ARROW}</a>' for m in MODULES)
    return f"""<main id="main">
<header class="hero grid-bg">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <span class="eyebrow">Workforce Readiness &amp; Life Skills Program</span>
      <h1><span class="thin">What You Missed In School.</span>Welcome to the <em>thirteenth</em> grade.</h1>
      <p class="hero-lede">Students graduate with a diploma but rarely with the skills to manage money, hold a job, communicate professionally, and live on their own. WYMIS teaches those skills in a structured, cohort-based program built for life after graduation.</p>
      <div class="hero-ctas">
        <a class="btn btn-primary" href="{base}partner">Bring WYMIS to your school {ARROW}</a>
        <a class="btn btn-ghost" href="{base}curriculum">Explore the curriculum</a>
      </div>
      <div class="hero-meta"><span>Ages 16 to 26</span><span>8 to 12 week cohorts</span><span>Piloted in 3 cities</span></div>
    </div>
    <div class="hero-visual">
      <div class="hero-photo">{img(pid, alt, sizes="(max-width: 980px) 90vw, 45vw", eager=True, w=1200, h=1500)}</div>
      <aside class="card" aria-label="Sample report card comparing what school covers with what life requires">
        <div class="card-top"><strong>Report Card</strong><span>Class of 2026</span></div>
        <div class="rc-group">Covered in school</div>
        <div class="rc-row"><span>Algebra II</span><span class="rc-mark rc-done">Complete</span></div>
        <div class="rc-group">Required by life</div>
        <div>
          <div class="rc-row"><span>Budgeting a first paycheck</span><span class="rc-mark rc-gap">Missed</span></div>
          <div class="rc-row"><span>Interview etiquette</span><span class="rc-mark rc-gap">Missed</span></div>
          <div class="rc-row"><span>Starting a business</span><span class="rc-mark rc-gap">Missed</span></div>
          <div class="rc-row"><span>Using AI responsibly</span><span class="rc-mark rc-gap">Missed</span></div>
        </div>
        <p class="card-foot">WYMIS closes the gap with <b>7 practical modules</b>.</p>
      </aside>
    </div>
  </div>
</header>

<section class="stats" aria-label="Program at a glance">
  <div class="wrap stats-in">
    <div class="stat"><b>8&ndash;12</b><span>Week full program</span></div>
    <div class="stat"><b>16&ndash;26</b><span>Ideal age range</span></div>
    <div class="stat"><b>7</b><span>Skills-first modules</span></div>
    <div class="stat"><b>3</b><span>Pilot cities</span></div>
  </div>
</section>

<section class="section" aria-labelledby="what-h">
  <div class="wrap split">
    <div class="split-copy">
      <span class="eyebrow">What is WYMIS</span>
      <h2 id="what-h">A diploma proves you finished school. It doesn&rsquo;t prove you&rsquo;re ready for what comes next.</h2>
      <div class="prose">
        <p class="lead"><strong>WYMIS, short for What You Missed In School, is a practical thirteenth grade for workforce readiness and life skills.</strong></p>
        <p>It closes a gap most students experience firsthand: graduating with academic credentials but without the everyday skills needed to manage money, hold a job, communicate professionally, and navigate adult life with confidence.</p>
        <p>The program turns the real-world lessons traditional schooling leaves out into a structured experience for graduating seniors and young adults preparing to enter the workforce, start a business, or live independently for the first time.</p>
      </div>
      <a class="link-arrow" href="{base}program">How the program works {ARROW}</a>
    </div>
    <div class="split-media">
      <div class="photo tall">{img(cpid, calt, w=1200, h=1500)}</div>
      <span class="photo-tag">Cohort-based learning</span>
    </div>
  </div>
</section>

<section class="section surface" aria-labelledby="model-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">The WYMIS Model</span>
      <h2 id="model-h">Built for accountability, not one-off lessons.</h2>
      <p>Students move through WYMIS together. Shared progress creates peer support and keeps everyone accountable from the first session to the last.</p>
    </div>
    {feats()}
  </div>
</section>

<section class="section" aria-labelledby="cur-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">The Curriculum</span>
      <h2 id="cur-h">Seven modules. The transcript school never issued.</h2>
      <p>Each module covers a skill area students consistently report feeling underprepared for after high school.</p>
    </div>
    <div class="mod-list">{chips}</div>
    <p style="margin-top:28px"><a class="link-arrow" href="{base}curriculum">See every module in detail {ARROW}</a></p>
  </div>
</section>

<section class="section on-navy grid-bg" aria-labelledby="pil-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Proven in the classroom</span>
      <h2 id="pil-h">Piloted in Phoenix, Las Vegas, and Memphis.</h2>
      <p>WYMIS has worked directly with students in each city, refining the curriculum from real classroom experience and student feedback.</p>
    </div>
    {cities_block(base=base)}
    <p style="margin-top:28px"><a class="link-arrow" href="{base}pilots">About the pilots {ARROW}</a></p>
  </div>
</section>

<section class="section" aria-labelledby="aud-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Who WYMIS is for</span>
      <h2 id="aud-h">Designed for graduating seniors. Ready for anyone starting out.</h2>
    </div>
    {audience()}
  </div>
</section>

<section class="section surface vision" aria-labelledby="vis-h">
  <div class="wrap vision-in">
    <div style="display:grid;gap:22px;min-width:0">
      <span class="eyebrow" id="vis-h">The Vision</span>
      <blockquote>Students deserve to graduate with more than a diploma. They deserve the <em>practical confidence</em> to manage their money, present themselves professionally, build relationships, and start something of their own.</blockquote>
    </div>
    <div class="vision-side">
      <p>The long-term vision is to grow WYMIS beyond individual pilot cohorts into a licensed, repeatable model that schools and organizations can bring into their own communities.</p>
      <div class="founder"><span class="founder-mono" aria-hidden="true">BJ</span><div><b>{FOUNDER}</b><span>Creator of WYMIS</span></div></div>
      <a class="link-arrow" href="{base}about">Read about the vision {ARROW}</a>
    </div>
  </div>
</section>
{cta(base)}
</main>
"""

def page_program(base):
    gpid, galt = PHOTOS["grad"]
    spid, salt = PHOTOS["smiling"]
    return page_hero("The Program", "A structured <em>thirteenth grade</em> for real life.",
                     "WYMIS is an 8 to 12 week, cohort-based program that teaches the practical skills students need right after graduation.",
                     "hands", "Program", base) + f"""<main id="main">
<section class="section" aria-labelledby="gap-h">
  <div class="wrap split">
    <div class="split-copy">
      <span class="eyebrow">The gap</span>
      <h2 id="gap-h">Academic credentials without everyday skills.</h2>
      <div class="prose">
        <p class="lead"><strong>Most students graduate high school without many of the practical skills needed to manage money, hold a job, communicate professionally, and navigate adult life with confidence.</strong></p>
        <p>WYMIS takes the real-world lessons that traditional schooling often leaves out and turns them into a structured, cohort-based learning experience. It is designed for graduating seniors and young adults preparing to enter the workforce, start a business, or live independently for the first time.</p>
      </div>
    </div>
    <div class="split-media"><div class="photo">{img(spid, salt)}</div></div>
  </div>
</section>

<section class="section surface" aria-labelledby="model-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">The WYMIS Model</span>
      <h2 id="model-h">Four principles shape every cohort.</h2>
      <p>Groups move through a shared program together rather than through isolated, one-off lessons.</p>
    </div>
    {feats()}
  </div>
</section>

<section class="section" aria-labelledby="how-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">How a cohort works</span>
      <h2 id="how-h">Start together. Practice together. Finish ready.</h2>
    </div>
    <div class="journey">
      <div class="step"><span class="step-k">Weeks 1 to 12</span><h3>A shared program</h3><p>A group of students begins WYMIS together and moves through the modules as a cohort over 8 to 12 weeks.</p></div>
      <div class="step"><span class="step-k">Each module</span><h3>Learn, then practice</h3><p>Modules run as a focused 75-minute session or a 3-day unit with role-play, group work, and applied projects.</p></div>
      <div class="step"><span class="step-k">After graduation</span><h3>Ready for what is next</h3><p>Students leave with practical confidence for a first job, a first apartment, college, or a business of their own.</p></div>
    </div>
  </div>
</section>

<section class="section surface" aria-labelledby="fmt-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Delivery formats</span>
      <h2 id="fmt-h">Two ways to run every module.</h2>
      <p>Deliver modules individually or combine them into a full cohort experience.</p>
    </div>
    {formats_block()}
  </div>
</section>

<section class="section" aria-labelledby="aud-h">
  <div class="wrap split rev">
    <div class="split-copy">
      <span class="eyebrow">Who WYMIS is for</span>
      <h2 id="aud-h">Ages 16 to 26, and the organizations that serve them.</h2>
      <ul class="checks" style="font-size:17px;gap:14px">
        <li>Graduating high school seniors preparing for a first job, first apartment, or college</li>
        <li>Young adults entering the workforce who want practical skills schools often do not teach</li>
        <li>Schools, community organizations, and workforce programs looking for a ready-to-use, real-world curriculum</li>
      </ul>
    </div>
    <div class="split-media"><div class="photo tall">{img(gpid, galt, w=1200, h=1500)}</div><span class="photo-tag">Class of 2026</span></div>
  </div>
</section>

<section class="section tight surface" aria-label="Program facts"><div class="wrap">{facts_box()}</div></section>
{cta(base)}
</main>
"""

def page_curriculum(base):
    rows = "".join(f"""<a class="tx-row" href="#{m['slug']}" role="row"><span class="tx-code" role="cell">{m['code']}</span><h3 role="cell">{m['title']}</h3><p role="cell">{m['summary']}</p><span class="tx-fmt" role="cell" data-short-time="75 min" data-short-label="Single class" data-long-time="3 days" data-long-label="Applied unit"><b>75 min</b><span>Single class</span></span></a>""" for m in MODULES)
    blocks = "".join(f"""<article class="module" id="{m['slug']}">
      <div class="module-media"><div class="photo">{img(m['pid'], m['alt'])}</div><span class="module-code">{m['code']}</span></div>
      <div class="module-copy">
        <h2>{m['title']}</h2>
        <p>{m['intro']}</p>
        <ul class="topics">{''.join(f'<li>{t}</li>' for t in m['topics'])}</ul>
        {f'<p>{m["applied"]}</p>' if m['applied'] else ''}
        <div class="fmt-pills"><span class="pill">75-minute session</span><span class="pill">3-day unit</span></div>
      </div>
    </article>""" for m in MODULES)
    return page_hero("The Curriculum", "Seven modules for life <em>after</em> graduation.",
                     "Each module covers a skill area students consistently report feeling underprepared for after high school. Run them individually or as a full cohort.",
                     "classroom", "Curriculum", base) + f"""<main id="main">
<section class="section" aria-labelledby="tx-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Course transcript</span>
      <h2 id="tx-h">The transcript school never issued.</h2>
      <p>Switch formats to see how each module runs as a single class or a 3-day applied unit.</p>
    </div>
    <div class="tx-bar">
      <p>WYMIS Official Course Transcript</p>
      <div class="seg" role="group" aria-label="Choose a delivery format">
        <button type="button" aria-pressed="true" data-fmt="short">75-minute session</button>
        <button type="button" aria-pressed="false" data-fmt="long">3-day unit</button>
      </div>
    </div>
    <div class="transcript" role="table" aria-label="WYMIS curriculum modules">
      <div class="tx-head" role="row"><span role="columnheader">Course</span><span role="columnheader">Module</span><span role="columnheader">What it covers</span><span role="columnheader" style="text-align:right">Format</span></div>
      {rows}
    </div>
    <div style="margin-top:28px">{formats_block()}</div>
  </div>
</section>
<section class="section surface" aria-label="Module details">
  <div class="wrap modules">{blocks}</div>
</section>
{cta(base, "Choose the modules your students need.", "Pick individual modules or the full 8 to 12 week program. We will help you match formats to your calendar.")}
</main>
"""

def page_pilots(base):
    tpid, talt = PHOTOS["teacher"]
    return page_hero("Pilot Programs", "Refined in <em>real</em> classrooms.",
                     "WYMIS has been piloted in Phoenix, Las Vegas, and Memphis, working directly with students to shape the curriculum.",
                     "listening", "Pilots", base) + f"""<main id="main">
<section class="section" aria-labelledby="cities-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Three pilot cities</span>
      <h2 id="cities-h">Phoenix. Las Vegas. Memphis.</h2>
      <p>In each city, WYMIS worked directly with students and used their classroom experience and feedback to refine the curriculum.</p>
    </div>
    {cities_block(light=True, base=base)}
  </div>
</section>
<section class="section surface" aria-labelledby="learn-h">
  <div class="wrap split">
    <div class="split-copy">
      <span class="eyebrow">Built with students</span>
      <h2 id="learn-h">The curriculum was shaped by the people it serves.</h2>
      <div class="prose">
        <p>Every WYMIS module covers a skill area students consistently report feeling underprepared for after high school. The pilots put that curriculum in front of real students and refined it based on what worked in the room.</p>
        <p>That classroom-first approach is why every module is built around situations students face immediately after graduation, and why each one comes in two formats: a focused 75-minute session and a 3-day applied unit.</p>
      </div>
      <a class="link-arrow" href="{base}curriculum">Explore the curriculum {ARROW}</a>
    </div>
    <div class="split-media"><div class="photo">{img(tpid, talt)}</div></div>
  </div>
</section>
<section class="section on-navy grid-bg" aria-labelledby="next-h">
  <div class="wrap split">
    <div class="split-copy">
      <span class="eyebrow">What comes next</span>
      <h2 id="next-h">From pilot cohorts to a licensed model.</h2>
      <p style="color:var(--on-navy-muted)">The long-term vision is to grow WYMIS beyond individual pilot cohorts into a licensed, repeatable model that other schools and organizations can bring directly into their own communities.</p>
    </div>
    <div style="display:flex;justify-content:flex-start"><a class="btn btn-primary" href="{base}partner">Bring WYMIS to your city {ARROW}</a></div>
  </div>
</section>
</main>
"""

def page_about(base):
    cpid, calt = PHOTOS["collab"]
    return page_hero("About WYMIS", "Built so graduates leave <em>ready</em>.",
                     "WYMIS was created by Dr. Barry K. Jackson, Ph.D. on a simple idea: a diploma should come with the practical confidence to use it.",
                     "teacher", "About", base) + f"""<main id="main">
<section class="section" aria-labelledby="founder-h">
  <div class="wrap split">
    <div class="split-copy">
      <span class="eyebrow">The founder</span>
      <h2 id="founder-h">{FOUNDER}</h2>
      <div class="prose">
        <p class="lead"><strong>Dr. Barry K. Jackson has built his career in workforce and youth development, connecting students and adult learners with employers and careers.</strong></p>
        <p>He is a Senior Career Services Advisor at Bryan University in Tempe, Arizona, where he builds employer relationships that move graduates into jobs and prepares students for career entry. He previously served as a Director of Programs with the National Urban League and as Executive Director of The Memphis Youth Coalition. He holds a Master of Divinity and has training in pastoral counseling.</p>
        <p>Dr. Jackson created WYMIS to close the gap between a high school diploma and the practical skills adult life demands. He built it as a cohort-based, skills-first program and piloted it with students in Phoenix, Las Vegas, and Memphis, refining the curriculum from real classroom experience and feedback.</p>
      </div>
      <dl class="cv">
        <div><dt>Current role</dt><dd>Senior Career Services Advisor, Bryan University (Tempe, AZ)</dd></div>
        <div><dt>Previously</dt><dd>Director of Programs, National Urban League</dd></div>
        <div><dt>Previously</dt><dd>Executive Director, The Memphis Youth Coalition</dd></div>
        <div><dt>Education</dt><dd>Master of Divinity; training in pastoral counseling</dd></div>
      </dl>
    </div>
    <div class="split-media"><div class="photo tall">{img(cpid, calt, w=1200, h=1500)}</div></div>
  </div>
</section>
<section class="section on-navy grid-bg" aria-labelledby="vis-h">
  <div class="wrap" style="display:grid;gap:28px;justify-items:start"><div style="display:grid;gap:28px;max-width:980px">
    <span class="eyebrow" id="vis-h">The Vision</span>
    <p class="big-quote">Students deserve to graduate not just with a diploma, but with the <em>practical confidence</em> to manage their money, present themselves professionally, build relationships, and start something of their own if they choose to.</p>
  </div></div>
</section>
<section class="section" aria-labelledby="pr-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">What guides WYMIS</span>
      <h2 id="pr-h">Practical, shared, flexible, and built to grow.</h2>
    </div>
    <div class="offers">
      <article class="offer"><span class="k">Practical first</span><h3>Real situations</h3><p>Every module is built around situations students will face immediately after graduation.</p></article>
      <article class="offer"><span class="k">Learn together</span><h3>Cohort model</h3><p>Students progress as a group, creating accountability and peer support.</p></article>
      <article class="offer"><span class="k">Flexible</span><h3>Two formats</h3><p>A 75-minute session for a focused introduction, or a 3-day unit for real practice.</p></article>
      <article class="offer"><span class="k">Built to grow</span><h3>Licensed model</h3><p>The goal is a repeatable model schools and organizations can bring to their own communities.</p></article>
    </div>
  </div>
</section>
<section class="section tight surface" aria-label="Program facts"><div class="wrap">{facts_box()}</div></section>
{cta(base, "Help us bring WYMIS to more students.")}
</main>
"""

def page_faq(base):
    items = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><div class="answer"><p>{a}</p></div></details>' for i, (q, a) in enumerate(FAQS))
    return page_hero("Questions &amp; Answers", "Frequently asked <em>questions</em>.",
                     "Quick answers about who WYMIS serves, how long it runs, what it covers, and how to bring it to your community.",
                     "smiling", "FAQ", base) + f"""<main id="main">
<section class="section" aria-labelledby="faq-h">
  <div class="wrap" style="display:grid;gap:48px">
    <h2 id="faq-h" class="sr-only">WYMIS FAQ</h2>
    <div class="faq">{items}</div>
    {facts_box()}
  </div>
</section>
{cta(base, "Still have questions?", "Reach out and we will walk you through the program, the modules, and the formats.")}
</main>
"""

def page_partner(base):
    return page_hero("Partner With WYMIS", "Bring WYMIS to your <em>community</em>.",
                     "Schools, community organizations, and workforce programs can bring WYMIS to their students as a full cohort, individual modules, or 3-day units.",
                     "handshake", "Partner", base) + f"""<main id="main">
<section class="section" aria-labelledby="opt-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Ways to partner</span>
      <h2 id="opt-h">Choose the format that fits your students.</h2>
    </div>
    <div class="offers">
      <article class="offer"><span class="k">8 to 12 weeks</span><h3>Full cohort program</h3><p>All seven modules delivered to a group of students moving through the program together.</p></article>
      <article class="offer"><span class="k">75 minutes</span><h3>Individual modules</h3><p>A focused single-class session on one topic, from financial literacy to AI.</p></article>
      <article class="offer"><span class="k">3 days</span><h3>Applied units</h3><p>Deeper module units with role-play, group work, and applied projects.</p></article>
      <article class="offer"><span class="k">Long-term</span><h3>Licensing</h3><p>WYMIS is growing toward a licensed model organizations can run in their own communities.</p></article>
    </div>
  </div>
</section>
<section class="section on-navy grid-bg" id="inquiry" aria-labelledby="con-h">
  <div class="wrap contact-in">
    <div class="contact-copy">
      <span class="eyebrow">Start the conversation</span>
      <h2 id="con-h">Tell us about your students.</h2>
      <p>Share your audience, timing, and goals. We will recommend the right mix of modules and formats for your school, organization, or workforce program.</p>
      <ul class="contact-list"><li>Ages 16 to 26</li><li>On-site cohorts and single sessions</li><li>Programs for schools, nonprofits, and workforce boards</li></ul>
      <div class="direct"><span>Email</span><a href="mailto:{EMAIL}">{EMAIL}</a></div>
    </div>
    <form class="inquiry" action="{base}contact.php" method="post" novalidate>
      <div class="hp" aria-hidden="true"><label for="f-web">Website</label><input id="f-web" name="website" tabindex="-1" autocomplete="off"></div>
      <div class="field"><label for="f-name">Full name</label><input id="f-name" name="name" autocomplete="name" required maxlength="120"></div>
      <div class="field"><label for="f-org">Organization</label><input id="f-org" name="org" autocomplete="organization" maxlength="160"></div>
      <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required maxlength="160"></div>
      <div class="field"><label for="f-phone">Phone (optional)</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" maxlength="40"></div>
      <div class="field"><label for="f-type">I'm reaching out as</label>
        <select id="f-type" name="type"><option>School or district</option><option>Community organization</option><option>Workforce program</option><option>Student or parent</option><option>Other</option></select></div>
      <div class="field"><label for="f-int">Interested in</label>
        <select id="f-int" name="interest"><option>Full cohort program (8 to 12 weeks)</option><option>Individual modules (75 minutes)</option><option>3-day applied units</option><option>Licensing the WYMIS model</option><option>Not sure yet</option></select></div>
      <div class="field full"><label for="f-msg">Message</label><textarea id="f-msg" name="message" maxlength="4000" placeholder="Number of students, timing, and anything else we should know."></textarea></div>
      <div class="form-foot">
        <span class="form-note">We will follow up within two business days.</span>
        <button class="btn btn-primary" type="submit">Send inquiry</button>
      </div>
    </form>
  </div>
</section>
</main>
"""

def page_404(base):
    return f"""<main id="main" class="nf"><div class="wrap nf-in">
  <span class="nf-code">404</span>
  <h1 style="font-size:clamp(28px,4vw,44px)">This page is one you missed.</h1>
  <p style="color:var(--muted);max-width:46ch">The page you were looking for doesn&rsquo;t exist or has moved.</p>
  <div class="hero-ctas" style="justify-content:center"><a class="btn btn-primary" href="/">Back to home</a><a class="btn btn-outline" href="/curriculum">View the curriculum</a></div>
</div></main>
"""

PAGES = [
    dict(slug="index", crumb="Home", fn=page_index, prio="1.0",
         title="WYMIS: What You Missed In School | Life Skills Program",
         og="WYMIS: Welcome to the thirteenth grade",
         desc="WYMIS is a cohort-based thirteenth grade for ages 16 to 26, teaching financial literacy, soft skills, etiquette, networking, AI, and more."),
    dict(slug="program", crumb="Program", fn=page_program, prio="0.9",
         title="The WYMIS Program | 8 to 12 Week Life Skills Cohorts",
         desc="How WYMIS works: an 8 to 12 week, cohort-based workforce readiness program for ages 16 to 26, with 75-minute sessions or 3-day applied units.",
         ld=[{"@type": "Course", "@id": SITE + "/program#course", "name": "WYMIS: What You Missed In School",
              "description": "A cohort-based thirteenth grade workforce readiness and life skills program for ages 16 to 26, run over 8 to 12 weeks.",
              "provider": {"@id": SITE + "/#org"}, "typicalAgeRange": "16-26", "inLanguage": "en-US", "educationalLevel": "Beginner",
              "teaches": [m["title"] for m in MODULES], "timeRequired": "P12W",
              "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Onsite", "courseSchedule": {"@type": "Schedule", "duration": "P12W", "repeatCount": 1}},
              "hasPart": [{"@id": f"{SITE}/curriculum#{m['slug']}"} for m in MODULES],
              "offers": {"@type": "Offer", "category": "Partnership", "url": SITE + "/partner"}}]),
    dict(slug="curriculum", crumb="Curriculum", fn=page_curriculum, prio="0.9",
         title="WYMIS Curriculum | 7 Life Skills & Workforce Modules",
         desc="Seven WYMIS modules: Financial Literacy, Business Administration, Soft Skills, Etiquette, Networking, AI and Technology, and Branding and Marketing.",
         ld=[{"@type": "ItemList", "name": "WYMIS curriculum modules", "numberOfItems": len(MODULES),
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": course(m)} for i, m in enumerate(MODULES)]}]),
    dict(slug="pilots", crumb="Pilots", fn=page_pilots, prio="0.7",
         title="WYMIS Pilot Programs | Phoenix, Las Vegas & Memphis",
         desc="WYMIS has been piloted with students in Phoenix, Arizona; Las Vegas, Nevada; and Memphis, Tennessee, refining the curriculum from real classroom feedback."),
    dict(slug="about", crumb="About", fn=page_about, prio="0.7", pagetype="AboutPage",
         title="About WYMIS | Dr. Barry K. Jackson, Ph.D. & the Vision",
         desc="Meet Dr. Barry K. Jackson, Ph.D., creator of WYMIS, Bryan University career services leader and former National Urban League program director.",
         ld=[PERSON]),
    dict(slug="faq", crumb="FAQ", fn=page_faq, prio="0.8", pagetype="FAQPage",
         title="WYMIS FAQ | Ages, Program Length, Curriculum & Formats",
         desc="Answers about WYMIS: who it serves (ages 16 to 26), program length (8 to 12 weeks), the seven modules, delivery formats, and pilot cities."),
    dict(slug="partner", crumb="Partner", fn=page_partner, prio="0.8", pagetype="ContactPage",
         title="Partner With WYMIS | Bring the Program to Your School",
         desc="Bring WYMIS to your school, nonprofit, or workforce program as a full 8 to 12 week cohort, individual 75-minute modules, or 3-day applied units."),
    dict(slug="404", crumb="Not found", fn=page_404, title="Page not found | WYMIS", desc="This page could not be found."),
]

# FAQPage needs mainEntity on the page node
def faq_ld():
    return [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQS]

def build():
    for p in PAGES:
        base = "/" if p["slug"] == "404" else ""
        h = head(p, base)
        if p["slug"] == "faq":
            h = h.replace('"@type":"FAQPage",', '"@type":"FAQPage","mainEntity":' + json.dumps(faq_ld(), ensure_ascii=False, separators=(",", ":")) + ",", 1)
        doc = h + nav(p["slug"], base) + p["fn"](base) + footer(base)
        assert "—" not in doc, "em dash found in " + p["slug"]
        open(os.path.join(ROOT, p["slug"] + ".html"), "w").write(doc)

    # sitemap
    urls = "".join(f"""  <url><loc>{SITE}{'/' if p['slug']=='index' else '/' + p['slug']}</loc><lastmod>{TODAY}</lastmod><priority>{p['prio']}</priority></url>\n"""
                   for p in PAGES if p["slug"] != "404")
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')

    # robots: welcome search and AI crawlers (GEO)
    bots = ["Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
            "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot", "Applebot-Extended", "CCBot", "DuckAssistBot", "Meta-ExternalAgent"]
    robots = "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)
    open(os.path.join(ROOT, "robots.txt"), "w").write(
        f"# WYMIS robots.txt: search engines and AI assistants are welcome.\n{robots}User-agent: *\nAllow: /\nDisallow: /tools/\nDisallow: /contact.php\n\nSitemap: {SITE}/sitemap.xml\n")

    # llms.txt (GEO): concise, link-rich summary for AI systems
    mod_lines = "\n".join(f"- [{m['title']} ({m['code']})]({SITE}/curriculum#{m['slug']}): {m['summary']}" for m in MODULES)
    llms = f"""# WYMIS: What You Missed In School

> WYMIS is a practical "thirteenth grade" workforce readiness and life skills program created by {FOUNDER}. It is a cohort-based, 8 to 12 week program for ages 16 to 26 that teaches the everyday skills school often leaves out: managing money, holding a job, communicating professionally, and navigating adult life. It has been piloted in Phoenix (AZ), Las Vegas (NV), and Memphis (TN).

Key facts:
- Full name: What You Missed In School (WYMIS)
- Audience: graduating high school seniors and young adults ages 16 to 26; schools, community organizations, and workforce programs
- Length: 8 to 12 week full program, delivered as a cohort
- Formats: each module runs as a 75-minute single-class session or a 3-day applied unit (role-play, group work, applied projects)
- Modules: 7
- Pilot cities: Phoenix, Arizona; Las Vegas, Nevada; Memphis, Tennessee
- Created by: {FOUNDER}, Senior Career Services Advisor at Bryan University (Tempe, AZ); former Director of Programs, National Urban League; former Executive Director, The Memphis Youth Coalition; Master of Divinity
- Contact: {EMAIL}

## Pages
- [Home]({SITE}/): Overview of WYMIS
- [Program]({SITE}/program): Cohort model, structure, formats, and audience
- [Curriculum]({SITE}/curriculum): All seven modules in detail
- [Pilots]({SITE}/pilots): Pilot cities and how they shaped the curriculum
- [About]({SITE}/about): Founder and vision
- [FAQ]({SITE}/faq): Common questions with direct answers
- [Partner]({SITE}/partner): How schools and organizations bring WYMIS to their communities

## Curriculum
{mod_lines}

## Optional
- [Full text for AI systems]({SITE}/llms-full.txt)
"""
    open(os.path.join(ROOT, "llms.txt"), "w").write(llms)
    faq_txt = "\n\n".join(f"### {q}\n{a}" for q, a in FAQS)
    mods_txt = "\n\n".join(f"### {m['title']} ({m['code']})\n{m['intro']}\nCovers: {m['summary']}\nFormats: 75-minute session or 3-day unit." for m in MODULES)
    open(os.path.join(ROOT, "llms-full.txt"), "w").write(llms.split("## Pages")[0] + f"""## What WYMIS is
WYMIS, short for What You Missed In School, closes a gap most students experience firsthand: graduating high school with academic credentials but without many of the practical, everyday skills needed to manage money, hold a job, communicate professionally, and navigate adult life with confidence. It turns the real-world lessons traditional schooling often leaves out into a structured, cohort-based learning experience for graduating seniors and young adults preparing to enter the workforce, start a business, or live independently for the first time.

## The model
- Cohort-based: students move through the program together as a group, creating accountability, peer support, and shared progress
- Program length: 8 to 12 weeks, ideally suited for ages 16 to 26
- Practical, skills-first curriculum built around situations students face immediately after graduation
- Flexible delivery: each module as a 75-minute class session or a 3-day unit with hands-on practice, role-play, and applied projects
- Designed for graduating seniors and adaptable for early workforce entrants and young adults broadly

## Curriculum
{mods_txt}

## Pilots
WYMIS has been piloted in Phoenix, Las Vegas, and Memphis, working directly with students to refine the curriculum based on real classroom experience and feedback.

## Vision
Students deserve to graduate not just with a diploma, but with the practical confidence to manage their money, present themselves professionally, build relationships, and start something of their own if they choose to. The long-term vision is to grow WYMIS beyond pilot cohorts into a licensed, repeatable model that schools and organizations can bring into their own communities.

## Frequently asked questions
{faq_txt}

Source: {SITE}
""")
    print("built", len(PAGES), "pages")

if __name__ == "__main__":
    build()
