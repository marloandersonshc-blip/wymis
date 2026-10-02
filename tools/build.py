#!/usr/bin/env python3
"""Static site generator for wymisworks.org.

Edit content in this file, then run:  python3 tools/build.py
It writes every .html page plus sitemap.xml, robots.txt, llms.txt and llms-full.txt to the repo root.
"""
import json, os, datetime, html, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://wymisworks.org"
EMAIL = "info@wymisworks.org"
# Google Analytics 4 measurement ID (looks like G-XXXXXXXXXX). Leave empty to load no analytics.
GA4_ID = ""
PRIVACY_UPDATED = "October 2, 2026"
# Nonprofit umbrella. Add the EIN and website when confirmed; they appear automatically where set.
UMBRELLA = "Love Nation"
UMBRELLA_EIN = ""
UMBRELLA_URL = ""
def umbrella_name(link=True):
    return f'<a href="{UMBRELLA_URL}" rel="noopener">{UMBRELLA}</a>' if (link and UMBRELLA_URL) else UMBRELLA
def umbrella_line(link=True):
    ein = f" (EIN {UMBRELLA_EIN})" if UMBRELLA_EIN else ""
    return f"WYMIS is a program under the umbrella of {umbrella_name(link)}, a registered 501(c)(3) nonprofit organization{ein}."
NAME = "WYMIS"
FULL = "What You Missed In School"
FOUNDER = "Dr. Barry K. Jackson, Ph.D."
BARRY_IMG = "https://img1.wsimg.com/isteam/ip/017e6888-9585-4ff4-9883-b075f9a3ebd4/Untitled%20design.png/:/cr=t:6%25,l:0%25,w:64.72%25,h:57.5%25/rs=w:640,h:736,cg:true"
BARRY_BIO = "https://valleycoachingconsulting.com/dr-barry-k-jackson"
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

def unsplash(pid, w): return f"https://images.unsplash.com/photo-{pid}?auto=format&fit=crop&crop=faces,center&w={w}&q=75"

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
    "collab":     ("1744320911030-1ab998d994d7", "Three smiling young women posing together on campus steps"),
    "hands":      ("1594750852563-5ed8e0421d40", "Two graduates in caps and gowns smiling together"),
    "smiling":    ("1549057446-9f5c6ac91a04", "Group of young adults walking and talking together outdoors"),
    "listening":  ("1461280360983-bd93eaa5051b", "Young adults talking together outside a building"),
    "classroom":  ("1524178232363-1fb2b075b655", "Classroom of students facing a projector screen"),
    "teacher":    ("1509062522246-3755977927d7", "Teacher presenting to a classroom of high school students"),
    "grad":       ("1618355776464-8666794d2520", "Smiling graduate in a cap and gown outdoors"),
    "handshake":  ("1549923746-c502d488b3ea", "Two professionals shaking hands and smiling"),
    "pointing":   ("1655720348590-c739c860beed", "Students working together on laptops outdoors"),
    "group":      ("1517486808906-6ca8b3f04846", "Diverse group of young adults sitting together outdoors"),
    "study":      ("1573497701240-345a300b8d36", "Young women in a discussion around a table"),
    "phoenix":    ("1617407867182-2c3730f7fe29", "Phoenix skyline silhouetted at sunset"),
    "vegas":      ("1723585126886-f31a77294a43", "The Las Vegas Strip at night"),
    "memphis":    ("1577055383519-ca48a5d859be", "Memphis riverfront pyramid at sunset"),
}

MODULES = [
    dict(code="WYM 101", slug="financial-literacy", title="Financial Literacy", tagline="Budgeting, credit, saving, and debt",
         pid="1554224155-6726b3ff858f", alt="Person reviewing a budget on paper with a pen and calculator",
         intro="Money decisions start the day the first paycheck arrives. This module gives students a working plan for it.",
         summary="What financial literacy is, budgeting, credit, and simple investing, adapted for a first paycheck, first apartment, and first credit decisions.",
         topics=["What financial literacy is", "Budgeting", "Credit", "Saving and managing debt", "Simple investing"],
         applied="Built around a first paycheck, a first apartment, and first credit decisions."),
    dict(code="WYM 102", slug="business-administration", title="Business Administration", tagline="How businesses actually operate",
         pid="1556761175-5973dc0f32e7", alt="Young professional presenting to colleagues in a meeting",
         intro="Students learn how businesses are built and run, and what it takes to start one of their own.",
         summary="What a business is, for-profit versus nonprofit models, basic business structures, how to start a simple business, and business ethics.",
         topics=["What a business is", "For-profit versus nonprofit models", "Basic business structures", "How to start a simple business", "Business ethics"],
         applied=""),
    dict(code="WYM 103", slug="soft-skills", title="Soft Skills", tagline="Communication, teamwork, and professionalism",
         pid="1573497620053-ea5300f94f21", alt="Two women in a professional conversation at a table",
         intro="The skills that appear in every job description and rarely in a class schedule.",
         summary="Professional communication, teamwork and collaboration, professionalism and work ethic, and problem-solving and adaptability.",
         topics=["Professional communication", "Teamwork and collaboration", "Professionalism and work ethic", "Problem-solving and adaptability"],
         applied=""),
    dict(code="WYM 104", slug="etiquette", title="Etiquette", tagline="Workplace norms and first impressions",
         pid="1521791136064-7986c2920216", alt="Two people shaking hands across a table",
         intro="How to carry yourself at the table, in the interview, and online.",
         summary="Everyday social etiquette, professional and interview etiquette, dining etiquette, and digital etiquette.",
         topics=["Workplace norms and first impressions", "Everyday social etiquette", "Professional and interview etiquette", "Dining etiquette", "Digital etiquette"],
         applied=""),
    dict(code="WYM 105", slug="networking-principles", title="Networking Principles", tagline="Building relationships and opening doors",
         pid="1515169067868-5387ec356754", alt="Small group of people talking together at an event",
         intro="Opportunities move through people. Students learn to introduce themselves, work a room, and follow up.",
         summary="What networking is, building a personal introduction, working a room at an event or conference, and following up effectively.",
         topics=["What networking is", "Building a personal introduction", "Working a room at an event or conference", "Following up effectively"],
         applied=""),
    dict(code="WYM 106", slug="ai-and-technology", title="AI and Technology", tagline="Practical fluency with modern tools",
         pid="1604933762021-54a5858c9832", alt="Young woman with braids working on a laptop",
         intro="AI is already reshaping the jobs students are about to enter. Students learn what it is and how to use it well.",
         summary="What artificial intelligence is, how it is changing industries and jobs, using AI tools well, and responsible, ethical use.",
         topics=["What artificial intelligence is", "How AI is changing industries and jobs", "Using AI tools well", "Responsible, ethical use"],
         applied=""),
    dict(code="WYM 107", slug="branding-and-marketing", title="Branding and Marketing", tagline="Presenting yourself with clarity",
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

TAGLINE = "Discover. Learn. Build. Belong."
QUOTE = "WYMIS is not trying to recreate school. It is building the bridge between education and execution."

FORMATS = [
    dict(k="1 day", t="One-Day Intensive", d="A focused, full-day deep dive that condenses the core modules into one immersive day, 8:00 AM to 6:00 PM.", items=["Six 75-minute module sessions", "Built for groups of 20 to 30", "Ideal for a first introduction"], link="intensive"),
    dict(k="3 days", t="3-Day Applied Unit", d="A hands-on, project-based unit that gives students real practice time with a skill.", items=["Role-play and group work", "Applied projects", "Go deep on one module"], link=""),
    dict(k="8 to 12 weeks", t="8 to 12 Week Cohort", d="The full WYMIS program: all seven modules, delivered to a cohort that moves through them together.", items=["All seven modules", "Peer accountability", "The complete thirteenth grade"], link="program"),
]

INTENSIVE = [
    ("8:00 AM", "8:30 AM", "Welcome and orientation", "Check-in, introductions, and an overview of the day", None),
    ("8:30 AM", "9:45 AM", "Soft Skills", "75-minute module session", "soft-skills"),
    ("9:45 AM", "10:00 AM", "Break", "", None),
    ("10:00 AM", "11:15 AM", "Networking Principles", "75-minute module session", "networking-principles"),
    ("11:15 AM", "11:30 AM", "Break", "", None),
    ("11:30 AM", "12:45 PM", "Financial Literacy", "75-minute module session", "financial-literacy"),
    ("12:45 PM", "1:45 PM", "Lunch", "On site or nearby", None),
    ("1:45 PM", "3:00 PM", "Business Administration", "75-minute module session", "business-administration"),
    ("3:00 PM", "3:15 PM", "Break", "", None),
    ("3:15 PM", "4:30 PM", "Etiquette", "75-minute module session", "etiquette"),
    ("4:30 PM", "4:45 PM", "Break", "", None),
    ("4:45 PM", "6:00 PM", "Branding and Marketing / AI and Technology", "75-minute module session and closing", "branding-and-marketing"),
]

FACILITY = [
    "One main room that seats 20 to 30 participants, classroom or round-table style",
    "A screen or wall space with a projector or TV for slides (WYMIS can bring a portable projector)",
    "Reliable Wi-Fi",
    "Tables and chairs that can be arranged for small-group breakouts",
    "Restrooms and a space for the lunch break (on site preferred, not required)",
    "Access from about 7:30 AM for setup to 6:30 PM for breakdown",
    "Street or lot parking for participants and facilitators",
]

FAQS = [
    ("What is WYMIS?",
     "WYMIS, short for What You Missed In School, is a practical “thirteenth grade” workforce readiness and life skills program. It teaches graduating seniors and young adults the everyday skills school often leaves out: managing money, holding a job, communicating professionally, and navigating adult life with confidence."),
    ("Who is WYMIS for?",
     "WYMIS is designed for ages 16 to 26. That includes graduating high school seniors preparing for a first job, first apartment, or college; young adults entering the workforce; and schools, community organizations, and workforce programs looking for a ready-to-use, real-world curriculum."),
    ("How long is the WYMIS program?",
     "The full WYMIS program runs 8 to 12 weeks as a cohort, with students moving through the modules together as a group."),
    ("What does the WYMIS curriculum cover?",
     "Seven modules: Financial Literacy, Business Administration (business fundamentals), Soft Skills, Etiquette, Networking Principles, AI and Technology, and Branding and Marketing. Each one covers a skill area students consistently report feeling underprepared for after high school."),
    ("What delivery formats are available?",
     "WYMIS can be delivered three ways: a One-Day Intensive (a full day, 8:00 AM to 6:00 PM), a 3-Day Applied Unit (hands-on and project-based), or the full 8 to 12 Week Cohort with all seven modules. Any single module can also run as a 75-minute session."),
    ("What is the WYMIS One-Day Intensive?",
     "A condensed, single-day version of the program that runs from 8:00 AM to 6:00 PM. It covers six 75-minute module sessions (Soft Skills, Networking Principles, Financial Literacy, Business Administration, Etiquette, and Branding and Marketing with AI and Technology) for a group of 20 to 30 young adults."),
    ("What does a host site need for a One-Day Intensive?",
     "One room that seats 20 to 30 people, a screen or projector (WYMIS can bring one), reliable Wi-Fi, tables that can be arranged for breakouts, restrooms and a lunch space, access from about 7:30 AM to 6:30 PM, and parking."),
    ("Do students earn a credential?",
     "Yes. WYMIS issues a verifiable digital credential built on Open Badges 3.0, the open standard for portable, verifiable learning credentials."),
    ("How does WYMIS relate to what schools already teach?",
     "WYMIS complements the academic foundation schools build. It is not trying to recreate school; it fills in the real-world skills a standard curriculum does not have room for, bridging education and execution."),
    ("Is WYMIS available outside the pilot cities?",
     "Yes. WYMIS was piloted in Phoenix, Las Vegas, and Memphis and is available nationwide."),
    ("Can schools use individual modules instead of the full program?",
     "Yes. Modules can be delivered individually or combined into a full 8 to 12 week cohort experience."),
    ("Where has WYMIS been piloted?",
     "WYMIS has been piloted in Phoenix, Arizona; Las Vegas, Nevada; and Memphis, Tennessee, working directly with students to refine the curriculum from real classroom experience and feedback."),
    ("Is WYMIS a nonprofit program?",
     f"Yes. WYMIS operates under the umbrella of {UMBRELLA}, a registered 501(c)(3) nonprofit organization. Schools, community partners, and funders can work with WYMIS through {UMBRELLA}."),
    ("Who created WYMIS?",
     "WYMIS was founded by Dr. Barry K. Jackson, Ph.D., Provost and Vice President of Academic Affairs at Alliance Bible College and Seminary. His career spans community outreach, nonprofits, and higher education, including roles as President of the Memphis Youth Coalition and Director of Programs with the Memphis Urban League."),
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
    "slogan": "Building the bridge between education and execution",
    "parentOrganization": {k: v for k, v in {"@type": "NGO", "name": UMBRELLA, "nonprofitStatus": "Nonprofit501c3", "taxID": UMBRELLA_EIN or None, "url": UMBRELLA_URL or None}.items() if v},
    "areaServed": [{"@type": "Country", "name": "United States"}] + [{"@type": "City", "name": c["name"], "containedInPlace": {"@type": "State", "name": c["state"]}} for c in CITIES],
    "knowsAbout": [m["title"] for m in MODULES] + ["Workforce readiness", "Life skills education"],
}
PERSON = {"@type": "Person", "@id": SITE + "/about#barry-jackson", "name": "Barry K. Jackson", "honorificPrefix": "Dr.",
          "honorificSuffix": "Ph.D.", "jobTitle": "Founder of WYMIS", "url": SITE + "/about", "sameAs": [BARRY_BIO],
          "image": BARRY_IMG,
          "description": "Founder of WYMIS; Provost and Vice President of Academic Affairs at Alliance Bible College and Seminary; former President of the Memphis Youth Coalition and Director of Programs with the Memphis Urban League.",
          "worksFor": [{"@id": SITE + "/#org"}, {"@type": "CollegeOrUniversity", "name": "Alliance Bible College and Seminary"}],
          "hasOccupation": [{"@type": "Occupation", "name": "Provost and Vice President of Academic Affairs"}],
          "affiliation": [{"@type": "Organization", "name": "Memphis Urban League"}, {"@type": "Organization", "name": "Memphis Youth Coalition"}],
          "memberOf": [{"@type": "Organization", "name": "American Association of Christian Counselors"}],
          "alumniOf": [{"@type": "CollegeOrUniversity", "name": "Alliance Bible College and Seminary"}],
          "hasCredential": [{"@type": "EducationalOccupationalCredential", "credentialCategory": "degree", "name": "Ph.D. in Christian Counseling"},
                            {"@type": "EducationalOccupationalCredential", "credentialCategory": "degree", "name": "Doctorate in Divinity"}],
          "knowsAbout": ["Curriculum development", "Program design", "Youth development", "Higher education", "Christian counseling"]}
WEBSITE = {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": NAME, "alternateName": FULL,
           "publisher": {"@id": SITE + "/#org"}, "inLanguage": "en-US"}

def course(m):
    return {"@type": "Course", "@id": f"{SITE}/curriculum#{m['slug']}", "name": f"{m['title']} ({m['code']})", "courseCode": m["code"],
            "description": m["summary"], "url": f"{SITE}/curriculum#{m['slug']}", "provider": {"@id": SITE + "/#org"},
            "teaches": m["topics"], "educationalLevel": "Beginner", "inLanguage": "en-US", "typicalAgeRange": "16-26",
            "educationalCredentialAwarded": "Open Badges 3.0 verifiable digital credential",
            "hasCourseInstance": [
                {"@type": "CourseInstance", "courseMode": "Onsite", "courseWorkload": "PT75M", "name": "75-minute session"},
                {"@type": "CourseInstance", "courseMode": "Onsite", "courseSchedule": {"@type": "Schedule", "duration": "P3D", "repeatCount": 1}, "name": "3-day applied unit"}],
            "offers": {"@type": "Offer", "category": "Partnership", "url": SITE + "/partner"}}

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}

# ---------------------------------------------------------------- layout
NAV = [("program", "Program"), ("curriculum", "Curriculum"), ("intensive", "One-Day Intensive"), ("pilots", "Pilots"), ("about", "About"), ("faq", "FAQ")]

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
<meta name="theme-color" content="#0A1F4D">
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
<link rel="icon" href="{base}assets/img/brand/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="{base}assets/img/brand/apple-touch-icon.png">
<link rel="manifest" href="{base}site.webmanifest">
<link rel="alternate" type="text/plain" title="LLM summary" href="{base}llms.txt">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{base}assets/css/site.css?v={CSS_V}">{analytics()}
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""

def analytics():
    if not GA4_ID:
        return ""
    return (f'\n<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>'
            f'\n<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}'
            f'gtag("js",new Date());gtag("config","{GA4_ID}");</script>')

def nav(active, base):
    home = base or "./"
    items = "".join(f'<li><a href="{base}{s}"{" aria-current=\"page\"" if s == active else ""}>{t}</a></li>' for s, t in NAV)
    return f"""<nav class="nav" aria-label="Main">
  <div class="wrap nav-in">
    <a class="brand" href="{home}" aria-label="WYMIS home"><picture><source srcset="{base}assets/img/brand/wymis-logo.webp" type="image/webp"><img src="{base}assets/img/brand/wymis-logo.png" alt="WYMIS: What You Missed In School" width="250" height="48" fetchpriority="high"></picture></a>
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
      <a href="{home}" aria-label="WYMIS home"><picture><source srcset="{base}assets/img/brand/wymis-logo-light.webp" type="image/webp"><img src="{base}assets/img/brand/wymis-logo-light.png" alt="WYMIS: What You Missed In School" width="271" height="52" loading="lazy"></picture></a>
      <p>Building the bridge between education and execution. A practical thirteenth grade for ages 16 to 26, available nationwide.</p>
      <p class="foot-np">{umbrella_line()}</p>
      <p class="foot-tag">{TAGLINE}</p>
    </div>
    <div class="foot-col"><h2>Program</h2><a href="{base}program">How it works</a><a href="{base}curriculum">Curriculum</a><a href="{base}intensive">One-Day Intensive</a><a href="{base}pilots">Pilot cities</a><a href="{base}faq">FAQ</a></div>
    <div class="foot-col"><h2>Modules</h2>{mods}<a href="{base}curriculum">All seven modules</a></div>
    <div class="foot-col"><h2>Connect</h2><a href="{base}about">About &amp; vision</a><a href="{base}partner">Partner with us</a><a href="mailto:{EMAIL}">{EMAIL}</a></div>
  </div>
  <div class="wrap foot-bot">
    <span>&copy; <span id="year">2026</span> WYMIS. All rights reserved.</span>
    <span class="foot-links"><a href="{base}privacy">Privacy policy</a><span>Site by <a href="https://atgaz.com" target="_blank" rel="noopener">ATGAZ<span class="sr-only"> (opens in a new tab)</span></a></span></span>
  </div>
</footer>
<script src="{base}assets/js/site.js?v={JS_V}" defer></script>
</body>
</html>
"""

def page_hero(eyebrow, h1, lede, photo, crumb, base):
    media = ""
    if photo:
        pid, alt = PHOTOS[photo]
        media = f'<div class="ph-img">{img(pid, alt, sizes="100vw", eager=True, w=2000, h=1000, maxw=2000)}</div>'
    return f"""<header class="page-hero{'' if photo else ' grid-bg'}">
  {media}
  <div class="wrap ph-in">
    <ol class="crumbs" aria-label="Breadcrumb"><li><a href="{base or './'}">Home</a></li><li aria-current="page">{crumb}</li></ol>
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1}</h1>
    <p class="ph-lede">{lede}</p>
  </div>
</header>
"""

def cta(base, h="Bring WYMIS to your students.", p="A One-Day Intensive, a 3-Day Applied Unit, or the full cohort. Tell us what fits your schedule and we will build the plan with you."):
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
     "Flexible delivery", "Deliver it as a One-Day Intensive, a 3-Day Applied Unit, or the full cohort, or run any single module as a 75-minute session."),
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

def bridge():
    return """<div class="bridge" role="list" aria-label="Education to WYMIS to Opportunity">
  <div class="bridge-node" role="listitem"><span class="bridge-k">Education</span><p>Academic foundations built by schools and teachers</p></div>
  <span class="bridge-arrow" aria-hidden="true"></span>
  <div class="bridge-node is-wymis" role="listitem"><span class="bridge-k">WYMIS</span><p>Practical, applied skills for life and work</p></div>
  <span class="bridge-arrow" aria-hidden="true"></span>
  <div class="bridge-node" role="listitem"><span class="bridge-k">Opportunity</span><p>Employment, entrepreneurship, and independent adulthood</p></div>
</div>"""

def formats3(base, note=True, skip=None):
    cards = "".join(f"""<article class="fmt3">
      <span class="fmt3-k">{f['k']}</span>
      <h3>{f['t']}</h3>
      <p>{f['d']}</p>
      <ul class="checks">{''.join(f'<li>{i}</li>' for i in f['items'])}</ul>
      {f'<a class="link-arrow" href="{base}{f["link"]}">{"See the schedule" if f["link"]=="intensive" else "How the cohort works"} {ARROW}</a>' if f['link'] else ''}
    </article>""" for f in FORMATS if f["t"] != skip)
    extra = '<p class="fmt3-note">Need something shorter? Any single module can also run as a 75-minute session inside a class period or event.</p>' if note else ''
    return f'<div class="fmt3-grid">{cards}</div>{extra}'

def credential(base):
    return f"""<section class="section tight on-navy grid-bg" aria-labelledby="cred-h">
  <div class="wrap cred">
    <div class="cred-badge" aria-hidden="true"><svg viewBox="0 0 96 96" fill="none"><path d="M48 6l10 7 12-1 5 11 11 6-1 12 7 10-7 10 1 12-11 6-5 11-12-1-10 7-10-7-12 1-5-11-11-6 1-12-7-10 7-10-1-12 11-6 5-11 12 1z" stroke="currentColor" stroke-width="2.5"/><path d="M33 49l10 10 20-22" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
    <div class="cred-copy">
      <span class="eyebrow">Verifiable credential</span>
      <h2 id="cred-h">Skills students can prove.</h2>
      <p>WYMIS issues a verifiable digital credential built on <strong>Open Badges 3.0</strong>, the open standard for portable learning credentials. Students can share it with employers and schools, and anyone can verify it.</p>
    </div>
  </div>
</section>
"""

def cities_block(light=False, base=""):
    out = []
    for c in CITIES:
        pid, alt = PHOTOS[c["photo"]]
        out.append(f"""<article class="city">
      <div class="photo">{img(pid, alt, sizes="(max-width: 860px) 100vw, 33vw", w=800, h=600, maxw=1200)}</div>
      <div class="city-body"><div class="city-top"><span>{c['state']}</span><span class="tag">Pilot city</span></div><h3>{c['name']}</h3></div>
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
            ("Ages", "16 to 26"), ("Modules", "7"), ("Formats", "One-Day Intensive, 3-Day Applied Unit, 8 to 12 Week Cohort"),
            ("Credential", "Open Badges 3.0, verifiable"), ("Availability", "Nationwide; piloted in Phoenix, Las Vegas, Memphis"), ("Nonprofit umbrella", f"{UMBRELLA}, a registered 501(c)(3)"), ("Created by", FOUNDER)]
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
      <div class="hero-meta"><span>Ages 16 to 26</span><span>7 practical modules</span><span>Available nationwide</span></div>
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
    <div class="stat"><b>16&ndash;26</b><span>Ages served</span></div>
    <div class="stat"><b>7</b><span>Practical modules</span></div>
    <div class="stat"><b>3</b><span>Ways to deliver it</span></div>
    <div class="stat"><b>OB 3.0</b><span>Verifiable credential</span></div>
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

<section class="section surface" aria-labelledby="bridge-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">The bridge</span>
      <h2 id="bridge-h">Building the bridge between education and execution.</h2>
      <p>WYMIS complements the academic foundation schools already build, filling in the real-world skills a standard curriculum doesn&rsquo;t have room for.</p>
    </div>
    {bridge()}
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

<section class="section surface" aria-labelledby="ways-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Ways to deliver it</span>
      <h2 id="ways-h">One day, three days, or a full cohort.</h2>
      <p>Pick the format that fits your students and your calendar. Each one draws from the same seven modules.</p>
    </div>
    {formats3(base)}
  </div>
</section>
{credential(base)}
<section class="section on-navy grid-bg" aria-labelledby="pil-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Proven in the classroom</span>
      <h2 id="pil-h">Piloted in Phoenix, Las Vegas, and Memphis. Available nationwide.</h2>
      <p>WYMIS has worked directly with students in each city, refining the curriculum from real classroom experience and student feedback. Today it can come to your city.</p>
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
      <a class="link-arrow" href="{base}about">Our mission and vision {ARROW}</a>
    </div>
  </div>
</section>
{cta(base)}
</main>
"""

def page_program(base):
    gpid, galt = PHOTOS["grad"]
    spid, salt = PHOTOS["hands"]
    return page_hero("The Program", "A structured <em>thirteenth grade</em> for real life.",
                     "WYMIS teaches the practical skills students need right after graduation, delivered as a One-Day Intensive, a 3-Day Applied Unit, or a full 8 to 12 week cohort.",
                     "smiling", "Program", base) + f"""<main id="main">
<section class="section" aria-labelledby="gap-h">
  <div class="wrap split">
    <div class="split-copy">
      <span class="eyebrow">The bridge</span>
      <h2 id="gap-h">Academic credentials without everyday skills.</h2>
      <div class="prose">
        <p class="lead"><strong>Most students graduate high school without many of the practical skills needed to manage money, hold a job, communicate professionally, and navigate adult life with confidence.</strong></p>
        <p>WYMIS complements the academic foundation schools already build. It takes the real-world lessons a standard curriculum doesn&rsquo;t have room for and turns them into a structured learning experience for graduating seniors and young adults preparing to enter the workforce, start a business, or live independently for the first time.</p>
      </div>
      {bridge()}
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
      <div class="step"><span class="step-k">Each module</span><h3>Learn, then practice</h3><p>Each module pairs focused instruction with role-play, group work, and applied projects.</p></div>
      <div class="step"><span class="step-k">After graduation</span><h3>Ready for what is next</h3><p>Students leave with a verifiable credential and practical confidence for a first job, a first apartment, college, or a business of their own.</p></div>
    </div>
  </div>
</section>

<section class="section surface" aria-labelledby="fmt-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Delivery formats</span>
      <h2 id="fmt-h">Three ways to bring WYMIS to your students.</h2>
      <p>From a single focused day to the complete thirteenth grade. Each format draws from the same seven modules.</p>
    </div>
    {formats3(base)}
  </div>
</section>
{credential(base)}

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
        <p class="module-tag">{m['tagline']}</p>
        <p>{m['intro']}</p>
        <ul class="topics">{''.join(f'<li>{t}</li>' for t in m['topics'])}</ul>
        {f'<p>{m["applied"]}</p>' if m['applied'] else ''}
        <div class="fmt-pills"><span class="pill">75-minute session</span><span class="pill">3-day unit</span><span class="pill">One-Day Intensive</span><span class="pill">8 to 12 week cohort</span></div>
      </div>
    </article>""" for m in MODULES)
    return page_hero("The Curriculum", "Seven modules for life <em>after</em> graduation.",
                     "Each module covers a skill area students consistently report feeling underprepared for after high school. Run them in a One-Day Intensive, a 3-Day Applied Unit, or a full cohort.",
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
      <h2 id="next-h">Now available nationwide.</h2>
      <p style="color:var(--on-navy-muted)">What started in three pilot cities can now come to yours, as a One-Day Intensive, a 3-Day Applied Unit, or a full cohort. The long-term vision is a licensed, repeatable model that schools and organizations run in their own communities.</p>
    </div>
    <div style="display:flex;justify-content:flex-start"><a class="btn btn-primary" href="{base}partner">Bring WYMIS to your city {ARROW}</a></div>
  </div>
</section>
</main>
"""

def page_about(base):
    return page_hero("About WYMIS", "Built so graduates leave <em>ready</em>.",
                     "WYMIS exists to close the gap between a high school diploma and the practical skills adult life demands.",
                     "teacher", "About", base) + f"""<main id="main">
<section class="section" aria-labelledby="mv-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Mission and vision</span>
      <h2 id="mv-h">Building the bridge between education and execution.</h2>
      <p>WYMIS is not trying to recreate school. It complements the academic foundation schools already build with the real-world skills a standard curriculum doesn&rsquo;t have room for.</p>
    </div>
    <div class="mv">
      <article class="mv-card">
        <span class="mv-k">Our mission</span>
        <p class="mv-lead">Give young people ages 16 to 26 the practical skills they need right after graduation: managing money, working professionally, building relationships, and starting something of their own.</p>
        <p>We do it through seven practical modules, delivered as a One-Day Intensive, a 3-Day Applied Unit, or a full 8 to 12 week cohort, with a verifiable credential students can show employers.</p>
      </article>
      <article class="mv-card is-dark">
        <span class="mv-k">Our vision</span>
        <p class="mv-lead">Every student graduates not just with a diploma, but with the <em>practical confidence</em> to manage their money, present themselves professionally, build relationships, and start something of their own if they choose to.</p>
        <p>We are growing WYMIS from pilot cohorts in Phoenix, Las Vegas, and Memphis into a licensed, repeatable model that schools and organizations nationwide can bring into their own communities.</p>
      </article>
    </div>
  </div>
</section>
<section class="section surface" aria-labelledby="pr-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">What guides WYMIS</span>
      <h2 id="pr-h">Discover. Learn. Build. Belong.</h2>
    </div>
    <div class="offers">
      <article class="offer"><span class="k">Discover</span><h3>See the gap</h3><p>Students find the real-world skills a standard curriculum doesn&rsquo;t have room for, before life tests them.</p></article>
      <article class="offer"><span class="k">Learn</span><h3>Practical modules</h3><p>Seven modules built around situations students face right after graduation.</p></article>
      <article class="offer"><span class="k">Build</span><h3>Applied work</h3><p>Role-play, group work, and projects that turn knowledge into something students can do and prove.</p></article>
      <article class="offer"><span class="k">Belong</span><h3>A cohort</h3><p>Students move through WYMIS together, with peer support and shared accountability.</p></article>
    </div>
  </div>
</section>
<section class="section tight" aria-labelledby="np-h">
  <div class="wrap"><div class="np">
    <div class="np-mark" aria-hidden="true">501(c)(3)</div>
    <div class="np-copy">
      <span class="eyebrow">Nonprofit home</span>
      <h2 id="np-h">A program of {umbrella_name()}.</h2>
      <p>{umbrella_line()} That gives schools, community organizations, and funders a nonprofit partner to work with when they bring WYMIS to their students.</p>
    </div>
  </div></div>
</section>
<section class="section surface" aria-labelledby="founder-h">
  <div class="wrap split founder-split">
    <div class="split-copy">
      <span class="eyebrow">The founder behind the mission</span>
      <h2 id="founder-h">{FOUNDER}</h2>
      <div class="prose">
        <p class="lead"><strong>Dr. Jackson built WYMIS on a career in community outreach, nonprofits, and higher education, and on years of designing programs that prepare people for what comes next.</strong></p>
        <p>He serves as Provost and Vice President of Academic Affairs at Alliance Bible College and Seminary, and previously served as President of the Memphis Youth Coalition and Director of Programs with the Memphis Urban League. He has developed curricula and programs for public and charter schools, municipal governments, faith-based organizations, and the Department of Corrections. WYMIS brings that work to one mission: the practical skills school leaves out.</p>
      </div>
      <dl class="cv">
        <div><dt>Current role</dt><dd>Provost and VP of Academic Affairs, Alliance Bible College and Seminary</dd></div>
        <div><dt>Previously</dt><dd>President, Memphis Youth Coalition; Director of Programs, Memphis Urban League</dd></div>
        <div><dt>Education</dt><dd>Ph.D. in Christian Counseling and Doctorate in Divinity, Alliance Bible College and Seminary; advanced degrees and certifications from Johns Hopkins University and Morehouse School of Medicine</dd></div>
      </dl>
      <a class="link-arrow" href="{BARRY_BIO}" target="_blank" rel="noopener noreferrer">Full bio at Valley Coaching &amp; Consulting <span class="sr-only">(opens in a new tab)</span>{ARROW}</a>
    </div>
    <div class="split-media portrait-wrap">
      <figure class="portrait">
        <img src="{BARRY_IMG}" alt="Portrait of Dr. Barry K. Jackson, Ph.D., founder of WYMIS" width="640" height="736" loading="lazy" decoding="async">
        <figcaption><b>{FOUNDER}</b><span>Founder of WYMIS</span></figcaption>
      </figure>
    </div>
  </div>
</section>
<section class="section tight" aria-label="Program facts"><div class="wrap">{facts_box()}</div></section>
{cta(base, "Help us bring WYMIS to more students.")}
</main>
"""

def page_faq(base):
    items = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><div class="answer"><p>{a}</p></div></details>' for i, (q, a) in enumerate(FAQS))
    return page_hero("Questions &amp; Answers", "Frequently asked <em>questions</em>.",
                     "Quick answers about who WYMIS serves, how long it runs, what it covers, and how to bring it to your community.",
                     "group", "FAQ", base) + f"""<main id="main">
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
                     "Schools, community organizations, and workforce programs anywhere in the country can bring WYMIS to their students as a One-Day Intensive, a 3-Day Applied Unit, or a full cohort.",
                     "handshake", "Partner", base) + f"""<main id="main">
<section class="section" aria-labelledby="opt-h">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Ways to partner</span>
      <h2 id="opt-h">Choose the format that fits your students.</h2>
    </div>
    {formats3(base)}
    <p class="fmt3-note">Hosting a One-Day Intensive? See the <a href="{base}intensive#facility">facility checklist</a>. Longer term, WYMIS is growing toward a licensed model organizations can run in their own communities.</p>
    <p class="fmt3-note"><strong>Funders and grantmakers:</strong> {umbrella_line()} Reach out through the form below to discuss sponsoring a cohort.</p>
  </div>
</section>
<section class="section on-navy grid-bg" id="inquiry" aria-labelledby="con-h">
  <div class="wrap contact-in">
    <div class="contact-copy">
      <span class="eyebrow">Start the conversation</span>
      <h2 id="con-h">Tell us about your students.</h2>
      <p>Share your audience, timing, and goals. We will recommend the right mix of modules and formats for your school, organization, or workforce program.</p>
      <ul class="contact-list"><li>Ages 16 to 26</li><li>One-day, three-day, and full-cohort formats</li><li>Available nationwide</li><li>Open Badges 3.0 credential for students</li></ul>
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
        <select id="f-int" name="interest"><option>One-Day Intensive</option><option>Hosting a One-Day Intensive at our facility</option><option>3-Day Applied Unit</option><option>Full cohort program (8 to 12 weeks)</option><option>Individual modules (75 minutes)</option><option>Licensing the WYMIS model</option><option>Not sure yet</option></select></div>
      <div class="field full"><label for="f-msg">Message</label><textarea id="f-msg" name="message" maxlength="4000" placeholder="Number of students, timing, and anything else we should know."></textarea></div>
      <div class="form-foot">
        <span class="form-note">We will follow up within two business days. We use your details only to reply. <a href="{base}privacy">Privacy policy</a></span>
        <button class="btn btn-primary" type="submit">Send inquiry</button>
      </div>
    </form>
  </div>
</section>
</main>
"""

def page_intensive(base):
    rows = []
    for a, b, seg, focus, slug in INTENSIVE:
        brk = seg in ("Break", "Lunch")
        name = f'<a href="{base}curriculum#{slug}">{seg}</a>' if slug else seg
        rows.append(f'<li class="slot{" is-break" if brk else ""}"><span class="slot-time"><b>{a}</b><span>{b}</span></span><span class="slot-body"><b>{name}</b>{f"<span>{focus}</span>" if focus else ""}</span></li>')
    fac = "".join(f"<li>{x}</li>" for x in FACILITY)
    spid, salt = PHOTOS["study"]
    return page_hero("One-Day Intensive", "The thirteenth grade in <em>one day</em>.",
                     "A condensed, single-day version of WYMIS for young adults ages 16 to 26: six 75-minute module sessions from 8:00 AM to 6:00 PM.",
                     "pointing", "One-Day Intensive", base) + f"""<main id="main">
<section class="section tight surface" aria-label="Intensive at a glance">
  <div class="wrap">
    <dl class="glance">
      <div><dt>Time</dt><dd>8:00 AM to 6:00 PM</dd></div>
      <div><dt>Audience</dt><dd>Ages 16 to 26, as a cohort</dd></div>
      <div><dt>Group size</dt><dd>20 to 30 participants</dd></div>
      <div><dt>Format</dt><dd>In person, one room with breakouts</dd></div>
      <div><dt>Sessions</dt><dd>Six 75-minute modules</dd></div>
    </dl>
  </div>
</section>

<section class="section" aria-labelledby="day-h">
  <div class="wrap split day-split">
    <div class="split-copy">
      <span class="eyebrow">Day-of schedule</span>
      <h2 id="day-h">One immersive day, seven modules.</h2>
      <div class="prose">
        <p class="lead"><strong>The One-Day Intensive condenses the core of WYMIS into a single day for groups that want a shorter-format introduction to the curriculum.</strong></p>
        <p>The day covers Soft Skills, Networking Principles, Financial Literacy, Business Administration, Etiquette, and a closing session that pairs Branding and Marketing with AI and Technology.</p>
        <p>Module order can shift based on facilitator availability. The 8:00 AM to 6:00 PM window and total instruction time stay fixed.</p>
      </div>
      <div class="split-media" style="margin-top:12px"><div class="photo">{img(spid, salt)}</div></div>
    </div>
    <ol class="schedule" aria-label="One-Day Intensive schedule">{''.join(rows)}</ol>
  </div>
</section>

<section class="section surface" id="facility" aria-labelledby="fac-h">
  <div class="wrap split">
    <div class="split-copy">
      <span class="eyebrow">For host sites</span>
      <h2 id="fac-h">What a host facility needs.</h2>
      <p style="color:var(--muted)">Schools, libraries, community centers, churches, and workforce offices can host a One-Day Intensive. Here is everything the day requires.</p>
      <a class="btn btn-primary" href="{base}partner" style="justify-self:start">Host an intensive {ARROW}</a>
    </div>
    <ul class="checks facility">{fac}</ul>
  </div>
</section>

<section class="section tight" aria-label="Other formats">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Want more time?</span><h2>Go deeper with a 3-day unit or the full cohort.</h2></div>
    <div class="fmt3-two">{formats3(base, note=False, skip="One-Day Intensive")}</div>
  </div>
</section>
{cta(base, "Bring a One-Day Intensive to your city.", "Tell us your date, group size, and location. We will confirm the schedule and what your facility needs.")}
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

def page_privacy(base):
    return page_hero("Legal", "Privacy policy", f"How WYMIS collects, uses, and protects information on this website. Last updated {PRIVACY_UPDATED}.", None, "Privacy", base) + f"""<main id="main">
<section class="section" aria-label="Privacy policy">
  <div class="wrap"><div class="legal">
    <p class="lead">WYMIS (What You Missed In School), a program under the umbrella of {UMBRELLA}, a registered 501(c)(3) nonprofit organization, operates this website. This policy explains what information we collect when you visit or contact us, how we use it, and the choices you have.</p>

    <h2>Information you give us</h2>
    <p>When you send an inquiry through the Partner page, we collect what you enter: your name, organization, email address, phone number (optional), the type of organization you represent, the program format you are interested in, and your message.</p>
    <p>We use this information only to respond to your inquiry, discuss bringing WYMIS to your students, and keep a record of that conversation. We do not sell, rent, or trade it, and we do not add you to a marketing list without your permission.</p>

    <h2>Information collected automatically</h2>
    <p>Like most websites, our hosting provider records basic technical information when you visit, such as your IP address, browser type, the pages you request, and the time of the request. These logs are used to operate and secure the site.</p>
    <p>{'We use Google Analytics to understand how visitors use the site, such as which pages are viewed and whether inquiries are submitted. Google Analytics uses cookies and collects device and usage information. Google provides an opt-out browser add-on at <a href="https://tools.google.com/dlpage/gaoptout">tools.google.com/dlpage/gaoptout</a>.' if GA4_ID else 'We may use a web analytics service to understand how visitors use the site, such as which pages are viewed. If we do, this policy will name the service and explain how to opt out.'}</p>

    <h2>Services that help run this site</h2>
    <ul>
      <li><strong>Hostinger</strong> hosts the website and delivers the email sent from the inquiry form.</li>
      <li><strong>Google Fonts</strong> supplies the typefaces. Your browser requests them from Google, which receives your IP address.</li>
      <li><strong>Unsplash</strong> supplies some photographs. Your browser loads them from Unsplash's servers, which receive your IP address.</li>{'<li><strong>Google Analytics</strong> measures site usage, as described above.</li>' if GA4_ID else ''}
    </ul>

    <h2>How long we keep information</h2>
    <p>We keep inquiry emails for as long as needed to respond and to maintain a record of our relationship with your school or organization. You can ask us to delete them at any time.</p>

    <h2>Your choices</h2>
    <p>You can ask us what information we hold about you, ask us to correct it, or ask us to delete it by emailing <a href="mailto:{EMAIL}">{EMAIL}</a>. Depending on where you live, you may have additional rights under state privacy laws, and we will honor requests made under them.</p>

    <h2>Young people</h2>
    <p>WYMIS serves students ages 16 to 26, but this website is intended for schools, organizations, parents, and adult learners. It is not directed to children under 13, and we do not knowingly collect information from them. If you believe a child under 13 has sent us information, contact us and we will delete it.</p>

    <h2>Security</h2>
    <p>The site uses HTTPS encryption, and inquiries are delivered by email to a private mailbox. No method of transmission or storage is completely secure, but we take reasonable steps to protect what you send us.</p>

    <h2>Changes to this policy</h2>
    <p>If we change this policy, we will post the new version here and update the date at the top.</p>

    <h2>Contact</h2>
    <p>Questions about this policy: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  </div></div>
</section>
</main>
"""

PAGES = [
    dict(slug="index", crumb="Home", fn=page_index, prio="1.0",
         title="WYMIS: What You Missed In School | Life Skills Program",
         og="WYMIS: Welcome to the thirteenth grade",
         desc="WYMIS bridges education and execution: a practical thirteenth grade for ages 16 to 26 in financial literacy, soft skills, networking, AI, and more."),
    dict(slug="program", crumb="Program", fn=page_program, prio="0.9",
         title="The WYMIS Program | 8 to 12 Week Life Skills Cohorts",
         desc="How WYMIS works: a workforce readiness and life skills program for ages 16 to 26, delivered as a One-Day Intensive, 3-Day Applied Unit, or 8 to 12 week cohort.",
         ld=[{"@type": "Course", "@id": SITE + "/program#course", "name": "WYMIS: What You Missed In School",
              "description": "A cohort-based thirteenth grade workforce readiness and life skills program for ages 16 to 26, run over 8 to 12 weeks.",
              "provider": {"@id": SITE + "/#org"}, "typicalAgeRange": "16-26", "inLanguage": "en-US", "educationalLevel": "Beginner",
              "teaches": [m["title"] for m in MODULES], "timeRequired": "P12W",
              "educationalCredentialAwarded": "Open Badges 3.0 verifiable digital credential",
              "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Onsite", "courseSchedule": {"@type": "Schedule", "duration": "P12W", "repeatCount": 1}},
              "hasPart": [{"@id": f"{SITE}/curriculum#{m['slug']}"} for m in MODULES],
              "offers": {"@type": "Offer", "category": "Partnership", "url": SITE + "/partner"}}]),
    dict(slug="curriculum", crumb="Curriculum", fn=page_curriculum, prio="0.9",
         title="WYMIS Curriculum | 7 Life Skills & Workforce Modules",
         desc="Seven WYMIS modules: Financial Literacy, Business Administration, Soft Skills, Etiquette, Networking, AI and Technology, and Branding and Marketing.",
         ld=[{"@type": "ItemList", "name": "WYMIS curriculum modules", "numberOfItems": len(MODULES),
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": course(m)} for i, m in enumerate(MODULES)]}]),
    dict(slug="intensive", crumb="One-Day Intensive", fn=page_intensive, prio="0.9",
         title="WYMIS One-Day Intensive | Life Skills in One Day, Ages 16-26",
         desc="The WYMIS One-Day Intensive: six 75-minute life skills and workforce readiness sessions from 8 AM to 6 PM for groups of 20 to 30 young adults.",
         ld=[{"@type": "Course", "@id": SITE + "/intensive#course", "name": "WYMIS One-Day Intensive",
              "description": "A condensed, single-day version of the WYMIS workforce readiness and life skills program for ages 16 to 26, with six 75-minute module sessions from 8:00 AM to 6:00 PM.",
              "provider": {"@id": SITE + "/#org"}, "typicalAgeRange": "16-26", "inLanguage": "en-US", "educationalLevel": "Beginner",
              "timeRequired": "PT10H", "educationalCredentialAwarded": "Open Badges 3.0 verifiable digital credential",
              "teaches": ["Soft Skills", "Networking Principles", "Financial Literacy", "Business Administration", "Etiquette", "Branding and Marketing", "AI and Technology"],
              "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Onsite", "courseWorkload": "PT10H", "maximumAttendeeCapacity": 30},
              "offers": {"@type": "Offer", "category": "Partnership", "url": SITE + "/partner"}}]),
    dict(slug="pilots", crumb="Pilots", fn=page_pilots, prio="0.7",
         title="WYMIS Pilot Programs | Phoenix, Las Vegas & Memphis",
         desc="WYMIS has been piloted with students in Phoenix, Arizona; Las Vegas, Nevada; and Memphis, Tennessee, refining the curriculum from real classroom feedback."),
    dict(slug="about", crumb="About", fn=page_about, prio="0.7", pagetype="AboutPage",
         title="About WYMIS | Mission, Vision & Nonprofit Home",
         desc="The WYMIS mission and vision: closing the gap between a diploma and real-world skills for ages 16 to 26. A program under the 501(c)(3) Love Nation.",
         ld=[PERSON]),
    dict(slug="faq", crumb="FAQ", fn=page_faq, prio="0.8", pagetype="FAQPage",
         title="WYMIS FAQ | Ages, Program Length, Curriculum & Formats",
         desc="Answers about WYMIS: who it serves (ages 16 to 26), program length (8 to 12 weeks), the seven modules, delivery formats, and pilot cities."),
    dict(slug="partner", crumb="Partner", fn=page_partner, prio="0.8", pagetype="ContactPage",
         title="Partner With WYMIS | Bring the Program to Your School",
         desc="Bring WYMIS to your school, nonprofit, or workforce program as a full 8 to 12 week cohort, individual 75-minute modules, or 3-day applied units."),
    dict(slug="privacy", crumb="Privacy", fn=page_privacy, prio="0.3",
         title="Privacy Policy | WYMIS",
         desc="How WYMIS collects, uses, and protects information submitted through wymisworks.org, including inquiry form data, analytics, and your choices."),
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
- Positioning: "Building the bridge between education and execution." WYMIS complements what schools teach; it is not trying to recreate school.
- Formats: One-Day Intensive (8:00 AM to 6:00 PM, six 75-minute module sessions, groups of 20 to 30), 3-Day Applied Unit (hands-on, project-based), or 8 to 12 Week Cohort (all seven modules). Any single module can also run as a 75-minute session.
- Credential: verifiable digital credential built on Open Badges 3.0
- Availability: nationwide
- Nonprofit umbrella: WYMIS is a program under the umbrella of {UMBRELLA}, a registered 501(c)(3) nonprofit organization
- Modules: 7
- Pilot cities: Phoenix, Arizona; Las Vegas, Nevada; Memphis, Tennessee
- Founded by: {FOUNDER}, Provost and Vice President of Academic Affairs, Alliance Bible College and Seminary
- Contact: {EMAIL}

## Pages
- [Home]({SITE}/): Overview of WYMIS
- [Program]({SITE}/program): Cohort model, structure, formats, and audience
- [Curriculum]({SITE}/curriculum): All seven modules in detail
- [One-Day Intensive]({SITE}/intensive): Full-day schedule and host facility requirements
- [Pilots]({SITE}/pilots): Pilot cities and how they shaped the curriculum
- [About]({SITE}/about): Mission, vision, nonprofit home, and founder
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

## One-Day Intensive
""" + "\n".join(f"- {a} to {b}: {seg}" + (f" ({focus})" if focus else "") for a, b, seg, focus, _ in INTENSIVE) + """

Host facility needs:
""" + "\n".join(f"- {x}" for x in FACILITY) + f"""

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
