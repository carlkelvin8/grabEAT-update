#!/usr/bin/env python3
"""Generates the inner pages (English and Norwegian) and sitemap.xml.

Run from anywhere: python3 tools/build_pages.py
The two homepages (index.html, no/index.html) are edited by hand.
"""
import json
import pathlib
from html import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://grabeat.no'
MENU = json.loads((ROOT / 'tools' / 'menu-data.json').read_text(encoding='utf-8'))

SPRITE = (ROOT / 'index.html').read_text(encoding='utf-8').split('<!-- Icon sprite -->')[1].split('<!-- Top bar -->')[0].strip()
LIVE = {'sustainability': f'{SITE}/sustainability/', 'investor': f'{SITE}/investor/', 'blog': f'{SITE}/blog/',
        'refund': f'{SITE}/refund-policy', 'apply': f'{SITE}/application-form/', 'terms': f'{SITE}/terms-conditions/'}
SOCIALS = [('Facebook', 'facebook', 'https://www.facebook.com/grabEAT.no/'), ('Instagram', 'instagram', 'https://www.instagram.com/grabeat.no/'),
           ('YouTube', 'youtube', 'https://www.youtube.com/channel/UC2K87p___l81f4XrjC7E9Dw'), ('LinkedIn', 'linkedin', 'https://www.linkedin.com/company/grabeat-no/')]
PAGES = ['our-solutions', 'how-it-works', 'our-menu', 'about-us', 'contact-us']


def icon(name):
    return f'<svg class="icon"><use href="#i-{name}"/></svg>'


def socials(extra=''):
    links = ''.join(f'<a href="{u}" aria-label="{n}">{icon(i)}</a>' for n, i, u in SOCIALS)
    return f'<div class="socials{extra}">{links}</div>'


class Page:
    """Helpers for one page in one language."""

    def __init__(self, lang, slug):
        self.lang, self.slug = lang, slug
        self.root = '../' if lang == 'en' else '../../'
        self.home = '../'

    def t(self, en, no):
        return en if self.lang == 'en' else no

    def asset(self, path):
        return f'{self.root}assets/{path}'

    def img(self, path, alt, cls=''):
        c = f' class="{cls}"' if cls else ''
        return f'<img{c} src="{self.asset(path)}" alt="{escape(alt, quote=True)}" loading="lazy">'

    def hero(self, title, image):
        return (f'<section class="page-hero" style="background-image:url(\'{self.asset("img/" + image)}\')">'
                f'<h1 data-reveal>{title}</h1></section>')

    def ticks(self, items):
        rows = ''.join(f'<li><span class="tick"><svg><use href="#i-check"/></svg></span><span>{i}</span></li>' for i in items)
        return f'<ul class="ticks ticks--sm" data-reveal>{rows}</ul>'

    def button(self, label, href, style='green', arrow=True):
        return f'<a class="btn btn--{style}" href="{href}">{label}{icon("arrow") if arrow else ""}</a>'

    def title(self, text):
        return f'<h2 class="section__title" data-reveal>{text}</h2>'

    def contact_band(self):
        return f'''<section class="section section--green section--band">
      <div class="container center" data-reveal>
        <h2>{self.t("Let’s Connect And Bring Healthy Meals Closer To You!", "Ta kontakt, så bringer vi sunne måltider nærmere deg!")}</h2>
        <a class="btn btn--white" href="../contact-us/">{self.t("Contact Us", "Kontakt oss")}</a>
      </div>
    </section>'''

    def split(self, image, alt, body, reverse=False):
        rev = ' split--reverse' if reverse else ''
        media = f'<div class="split__media" data-reveal>{self.img(image, alt)}</div>'
        text = f'<div class="split__body prose" data-reveal>{body}</div>'
        return f'<div class="split{rev}">{(text + media) if reverse else (media + text)}</div>'


def shell(p, title, desc, body, ld=None):
    """Wraps a page body in the shared head, header and footer."""
    t, active = p.t, p.slug
    assert len(title) <= 60, (title, len(title))
    assert len(desc) <= 155, (desc, len(desc))
    en_url, no_url = f'{SITE}/{p.slug}/', f'{SITE}/no/{p.slug}/'
    url = en_url if p.lang == 'en' else no_url
    nav = [('our-solutions', t('Our Solutions', 'Våre løsninger')), ('our-menu', t('Menu', 'Meny')), ('how-it-works', t('How It Works', 'Slik fungerer det'))]
    links = ''.join(f'<a href="../{s}/"{" class=\"is-active\"" if s == active else ""}>{n}</a>' for s, n in nav)
    about_cls = ' class="is-active"' if active == 'about-us' else ''
    lang_nav = (f'<a href="../no/{p.slug}/" hreflang="no" lang="no">NO</a><a href="./" hreflang="en" aria-current="page">EN</a>' if p.lang == 'en'
                else f'<a href="./" hreflang="no" aria-current="page">NO</a><a href="../../{p.slug}/" hreflang="en" lang="en">EN</a>')
    org = {'@type': 'Organization', '@id': f'{SITE}/#organization', 'name': 'grabEAT AS', 'url': f'{SITE}/',
           'logo': f'{SITE}/assets/logos/grabeat-logo.webp', 'telephone': '+47 472 23 288', 'email': 'post@grabeat.no',
           'sameAs': [u for _, _, u in SOCIALS]}
    graph = [org] + ([ld] if ld else [])
    data = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False)
    return f'''<!doctype html>
<html lang="{p.lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(desc, quote=True)}">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="en" href="{en_url}">
  <link rel="alternate" hreflang="no" href="{no_url}">
  <link rel="alternate" hreflang="x-default" href="{en_url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="grabEAT">
  <meta property="og:locale" content="{t("en_GB", "nb_NO")}">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(desc, quote=True)}">
  <meta property="og:image" content="{SITE}/assets/img/grabeat-smart-kiosk.webp">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(title, quote=True)}">
  <meta name="twitter:description" content="{escape(desc, quote=True)}">
  <meta name="twitter:image" content="{SITE}/assets/img/grabeat-smart-kiosk.webp">
  <meta name="theme-color" content="#598935">
  <link rel="icon" href="{p.asset("logos/favicon.png")}">
  <link rel="preload" as="font" type="font/woff2" href="{p.asset("fonts/bricolage-grotesque-latin.woff2")}" crossorigin>
  <link rel="stylesheet" href="{p.root}styles.css">
  <script>document.documentElement.classList.add('js')</script>
  <script type="application/ld+json">{data}</script>
</head>
<body id="top">
  <a class="skip-link" href="#content">{t("Skip to content", "Hopp til innhold")}</a>

  <!-- Icon sprite -->
  {SPRITE}

  <div class="topbar">
    <div class="container topbar__inner">
      <div class="topbar__contact">
        <a href="tel:+4747223288">{icon("phone")}+47 472 23 288</a>
        <a href="mailto:post@grabeat.no">{icon("mail")}post@grabeat.no</a>
      </div>
      <div class="topbar__end">
        <nav class="lang" aria-label="{t("Language", "Språk")}">{lang_nav}</nav>
        {socials(" socials--light")}
      </div>
    </div>
  </div>

  <header class="header" data-header>
    <div class="container header__inner">
      <a class="header__logo" href="{p.home}" aria-label="{t("grabEAT home", "grabEAT forside")}">
        <img src="{p.asset("logos/grabeat-logo.webp")}" alt="grabEAT – Sunne og varme måltider 24/7" width="640" height="264">
      </a>
      <button class="nav-toggle" type="button" aria-label="{t("Menu", "Meny")}" aria-expanded="false" aria-controls="nav" data-nav-toggle><span></span><span></span><span></span></button>
      <nav class="nav" id="nav" aria-label="{t("Main", "Hovedmeny")}" data-nav>
        <a href="{p.home}">{t("Home", "Hjem")}</a>
        {links}
        <a href="{LIVE["sustainability"]}">{t("Sustainability", "Bærekraft")}</a>
        <a href="../about-us/"{about_cls}>{t("About Us", "Om oss")}</a>
        <a href="{LIVE["investor"]}">{t("For Investors", "For investorer")}</a>
        <a class="btn btn--tomato nav__cta" href="{p.home}#locations" data-track="find_kiosk">{t("Find a kiosk near you", "Finn en kiosk nær deg")}</a>
      </nav>
    </div>
  </header>

  <main id="content">
    {body}
  </main>

  <footer class="footer">
    <div class="container footer__inner">
      <a href="{p.home}" class="footer__logo" aria-label="{t("grabEAT home", "grabEAT forside")}"><img src="{p.asset("logos/grabeat-logo.webp")}" alt="grabEAT – Sunne og varme måltider 24/7" loading="lazy" width="640" height="264"></a>
      <nav class="footer__nav" aria-label="{t("Footer", "Bunnmeny")}">
        <a href="{p.home}">{t("Home", "Hjem")}</a>
        <a href="../our-solutions/">{t("Our Solutions", "Våre løsninger")}</a>
        <a href="../how-it-works/">{t("How It Works", "Slik fungerer det")}</a>
        <a href="{LIVE["sustainability"]}">{t("Sustainability", "Bærekraft")}</a>
        <a href="../about-us/">{t("About Us", "Om oss")}</a>
        <a href="{LIVE["blog"]}">{t("Our Blog", "Bloggen vår")}</a>
        <a href="{LIVE["refund"]}">{t("Refund Policy", "Retningslinjer for refusjon")}</a>
        <a href="../contact-us/">{t("Contact Us", "Kontakt oss")}</a>
        <a href="{LIVE["investor"]}">{t("Invest in grabEAT", "Invester i grabEAT")}</a>
      </nav>
      <ul class="footer__info">
        <li>{t("Business name", "Firmanavn")}: grabEAT AS</li>
        <li>{t("VAT Registration no", "Org.nr.")}: 933 328 430 MVA</li>
        <li><a href="tel:+4747223288">{icon("phone")}+47 472 23 288</a></li>
        <li><a href="mailto:post@grabeat.no">{icon("mail")}post@grabeat.no</a></li>
      </ul>
      {socials()}
    </div>
    <div class="footer__legal">Copyright © <span data-year>2026</span> GrabEAT | {t("All Rights Reserved", "Alle rettigheter forbeholdt")}</div>
  </footer>

  <a class="to-top" href="#top" aria-label="{t("Back to top", "Til toppen")}" data-to-top>{icon("chevron")}</a>

  <div class="mobile-bar">
    <a class="btn btn--green" href="https://www.google.com/maps/search/?api=1&amp;query=grabEAT+kiosk" data-track="find_kiosk">{icon("pin")}{t("Find kiosk", "Finn kiosk")}</a>
    <a class="btn btn--outline" href="tel:+4747223288">{icon("phone")}{t("Call", "Ring")}</a>
  </div>

  <script src="{p.root}script.js"></script>
</body>
</html>
'''


def solutions(p):
    t = p.t
    apply = t('Apply Now', 'Søk nå')
    kiosks = [
        ('grabeat-smart-kiosk.webp', 'grabEAT MealPOD', t('The compact grabEAT MealPOD kiosk', 'Den kompakte grabEAT MealPOD-kiosken'),
         [t('Built-in microwave', 'Innebygd mikrobølgeovn'), t('Warm meal in just 3 minutes', 'Varmt måltid på bare 3 minutter'),
          t('Perfect for smaller workspaces', 'Perfekt for mindre arbeidsplasser'), t('Compact design, less than 2 square meters space required', 'Kompakt design, krever under 2 kvadratmeter')]),
        ('grabeat-kiosk-forum-kokstad.webp', 'grabEAT MealPOD+', t('The grabEAT MealPOD+ kiosk with two microwaves', 'grabEAT MealPOD+-kiosken med to mikrobølgeovner'),
         [t('2 integrated microwaves', '2 integrerte mikrobølgeovner'), t('Compact design, takes up approx. 2 square meters of floor space', 'Kompakt design, tar opp ca. 2 kvadratmeter gulvplass'),
          t('Perfect for medium and large workplaces', 'Perfekt for mellomstore og store arbeidsplasser')]),
        ('grabeat-hub-indoor-light.webp', 'grabEAT HUB', t('The grabEAT HUB indoor kiosk', 'grabEAT HUB-kiosken innendørs'),
         [t('Complete canteen solution', 'Komplett kantineløsning'), t('Smart fridge', 'Smartkjøleskap'), t('Coffee machine', 'Kaffemaskin')]),
        ('grabeat-smarthub-indoor.webp', 'grabEAT SmartHUB', t('The grabEAT SmartHUB indoor kiosk', 'grabEAT SmartHUB-kiosken innendørs'),
         [t('Buy food in 30 seconds', 'Kjøp mat på 30 sekunder'), t('Smart fridge and freezer', 'Smartkjøleskap og fryser'),
          t('Microwave module and station are ordered as an extra', 'Mikrobølgemodul og -stasjon bestilles som tillegg')]),
    ]
    cards = ''
    for i, (img, name, alt, feats) in enumerate(kiosks):
        btn = p.button(apply, LIVE['apply'])
        if name.endswith('SmartHUB'):
            btn = p.button(t('Get Started With SmartLunch', 'Kom i gang med SmartLunch'), f'{SITE}/smartlunch', 'outline') + btn
        rows = ''.join(f'<li><span class="tick"><svg><use href="#i-check"/></svg></span><span>{f}</span></li>' for f in feats)
        cards += f'''<article class="card">{p.img("img/" + img, alt)}<div class="card__body"><h3>{name}</h3><ul class="ticks ticks--sm">{rows}</ul><div class="btn-row card__foot">{btn}</div></div></article>'''
    why = [
        ('grabeat-recyclable-packaging.webp', t('A grabEAT meal in recyclable packaging', 'Et grabEAT-måltid i resirkulerbar emballasje'),
         t('Sustainable and Functional Packaging', 'Bærekraftig og funksjonell emballasje'),
         t('Combining functionality and sustainability, our recyclable, eco-friendly packaging ensures a guilt-free dining experience that supports your health and the planet.',
           'Vår resirkulerbare og miljøvennlige emballasje kombinerer funksjon og bærekraft, og gir en matopplevelse uten dårlig samvittighet – bra for både helsen din og planeten.'),
         t('Learn More', 'Les mer'), f'{SITE}/grabeat-nutrivault/'),
        ('woman-choosing-meal-on-phone.webp', t('A woman choosing a meal on her phone', 'En kvinne som velger et måltid på mobilen'),
         t('Efficient and Scalable Ordering System', 'Effektivt og skalerbart bestillingssystem'),
         t('grabEAT’s ordering system combines kiosk-based and soon an app-driven options, ensuring a seamless customer experience while reducing labor costs.',
           'grabEATs bestillingssystem kombinerer kiosk og snart også app, noe som gir en sømløs kundeopplevelse og lavere lønnskostnader.'),
         t('Contact Us', 'Kontakt oss'), '../contact-us/'),
        ('pasta-with-meat-sauce.webp', t('Pasta with meat sauce on a blue plate', 'Pasta med kjøttsaus på en blå tallerken'),
         t('Fresh, Nutritious, Delicious Meals', 'Ferske, næringsrike og deilige måltider'),
         t('At grabEAT, we provide high-quality, nutritious meals for busy lifestyles, offering a variety of fresh, balanced options with wholesome ingredients and international flavours.',
           'Hos grabEAT tilbyr vi næringsrike måltider av høy kvalitet for en travel hverdag, med et variert utvalg av ferske, balanserte retter, gode råvarer og internasjonale smaker.'),
         t('Browse Menu', 'Se menyen'), '../our-menu/'),
        ('man-holding-vegetable-basket.webp', t('A man holding a basket of vegetables', 'En mann som holder en kurv med grønnsaker'),
         t('Efficient and Sustainable Supply Chain', 'Effektiv og bærekraftig forsyningskjede'),
         t('grabEAT’s supply chain emphasizes sustainability and efficiency, partnering with local suppliers for fresh ingredients. We ensure consistent availability, minimal waste, and support for responsible sourcing and local economies.',
           'grabEATs forsyningskjede legger vekt på bærekraft og effektivitet, i samarbeid med lokale leverandører av ferske råvarer. Vi sikrer jevn tilgjengelighet, minimalt svinn og støtte til ansvarlige innkjøp og lokal økonomi.'),
         None, None),
    ]
    why_cards = ''
    for img, alt, head, text, label, href in why:
        foot = f'<div class="card__foot">{p.button(label, href, "outline")}</div>' if label else ''
        why_cards += f'<article class="card">{p.img("img/" + img, alt)}<div class="card__body"><h3>{head}</h3><p>{text}</p>{foot}</div></article>'
    ai = [
        ('icon-ai-demand-forecasting.webp', t('Demand Forecasting', 'Etterspørselsprognoser'), t('AI analyzes consumption patterns to optimize stock, reducing waste and ensuring availability.', 'KI analyserer forbruksmønstre for å optimalisere lageret, redusere svinn og sikre tilgjengelighet.')),
        ('icon-ai-inventory-management.webp', t('Inventory Management', 'Lagerstyring'), t('Real-time monitoring automates restocking and ensures freshness.', 'Sanntidsovervåking automatiserer påfylling og sikrer ferskhet.')),
        ('icon-ai-sustainability.webp', t('Sustainability', 'Bærekraft'), t('AI optimizes local sourcing, cutting carbon emissions and reducing food waste.', 'KI optimaliserer lokale innkjøp, kutter karbonutslipp og reduserer matsvinn.')),
        ('icon-ai-predictive-maintenance.webp', t('Predictive Maintenance', 'Prediktivt vedlikehold'), t('AI tracks machine performance, reducing downtime through proactive repairs.', 'KI følger med på maskinenes ytelse og reduserer nedetid gjennom proaktive reparasjoner.')),
        ('icon-ai-personalized-experience.webp', t('Personalized Experience', 'Personlig tilpasset opplevelse'), t('Machine learning tailors meal recommendations based on user preferences and dietary needs.', 'Maskinlæring tilpasser måltidsanbefalinger etter brukerens preferanser og kostbehov.')),
    ]
    ai_items = ''.join(f'<li class="feature">{p.img("img/" + i, "", "feature__icon")}<h3>{h}</h3><p>{x}</p></li>' for i, h, x in ai)
    logos = [('smartvend.webp', 'SmartVend AS'), ('neuroshop-tech.webp', 'Neuroshop Tech'), ('bicom-italy.webp', 'Bicom Italy'), ('magex-italy.webp', 'Magex Italy'), ('dll-finance.webp', 'DLL Finance')]
    logo_html = ''.join(p.img('logos/' + f, a) for f, a in logos)
    body = f'''{p.hero(t("Our Solutions", "Våre løsninger"), "page-hero-solutions.webp")}
    <section class="section section--cream">
      <div class="container">
        {p.split("img/grabeat-kiosk-forum-kokstad.webp", t("A grabEAT kiosk with warm meals", "En grabEAT-kiosk med varme måltider"),
                 f'<h2>{t("Smart, sustainable solutions for modern, on-the-go lifestyles.", "Smarte, bærekraftige løsninger for en moderne hverdag på farten.")}</h2><p>{t("Our automated kiosks provide 24/7 access to fresh, nutritious meals and drinks, both indoor and outdoor. With advanced technology and durable designs, we ensure healthy food options ready to enjoy anywhere, anytime.", "Våre automatiserte kiosker gir tilgang til ferske, næringsrike måltider og drikke 24/7, både innendørs og utendørs. Med avansert teknologi og solid design sørger vi for sunn mat som er klar når og hvor som helst.")}</p>', reverse=True)}
      </div>
    </section>
    <section class="section">
      <div class="container">
        {p.title(t("Designed to meet the needs of various businesses and environments", "Utformet for behovene til ulike bedrifter og miljøer"))}
        <div class="cards cards--2">{cards}</div>
      </div>
    </section>
    <section class="section section--sage">
      <div class="container narrow center-block">
        {p.title(t("Would you like a customized kiosk design?", "Ønsker du et skreddersydd kioskdesign?"))}
        <p class="intro" data-reveal>{t("At grabEAT, we understand that every location has unique needs and aesthetics. That’s why we offer comprehensive customization services to tailor our kiosks to your specific requirements.", "Hos grabEAT vet vi at hver lokasjon har sine egne behov og sitt eget uttrykk. Derfor tilbyr vi omfattende tilpasning av kioskene etter dine krav.")}</p>
        <p class="intro intro--label" data-reveal>{t("Our customization services include:", "Tilpasningene våre omfatter:")}</p>
        {p.ticks([t("<strong>Bespoke Design:</strong> Tailored kiosk designs to match your space’s aesthetic and branding.", "<strong>Skreddersydd design:</strong> Kioskdesign tilpasset lokalet og merkevaren din."),
                  t("<strong>Brand Integration:</strong> Incorporate your logo and colors into the kiosk for a cohesive brand experience.", "<strong>Merkevareintegrasjon:</strong> Logoen og fargene dine på kiosken gir en helhetlig merkevareopplevelse."),
                  t("<strong>Flexible Configuration:</strong> Adaptable machine layouts and features to fit the specific needs of your location, whether indoor or outdoor.", "<strong>Fleksibel konfigurasjon:</strong> Tilpassbar utforming og funksjoner etter behovene på lokasjonen din, både innendørs og utendørs.")])}
        <div class="center" data-reveal>{p.button(t("Apply for customization", "Søk om tilpasning"), LIVE["apply"])}</div>
      </div>
    </section>
    <section class="section">
      <div class="container">
        {p.title(t("Why choose grabEAT?", "Hvorfor velge grabEAT?"))}
        <p class="intro intro--gap" data-reveal>{t("grabEAT uses advanced technology to deliver fresh, nutritious, and hot meals through smart kiosks—offering convenience while caring for the planet.", "grabEAT bruker avansert teknologi til å levere ferske, næringsrike og varme måltider gjennom smarte kiosker – enkelt for deg og skånsomt for planeten.")}</p>
        <div class="cards cards--2">{why_cards}</div>
      </div>
    </section>
    <section class="section section--sage">
      <div class="container narrow center-block">
        {p.title(t("A Cost Effective Alternative to a Cafeteria", "Et kostnadseffektivt alternativ til kantine"))}
        <p class="intro intro--label" data-reveal>{t("Key Benefits:", "De viktigste fordelene:")}</p>
        {p.ticks([t("<strong>Boost Employee Satisfaction:</strong> Access to nutritious meals enhances morale and productivity.", "<strong>Mer fornøyde ansatte:</strong> Tilgang til næringsrike måltider styrker trivsel og produktivitet."),
                  t("<strong>Diverse Meal Options:</strong> A variety of healthy choices for all dietary preferences.", "<strong>Variert utvalg:</strong> Mange sunne valg for alle kostpreferanser."),
                  t("<strong>24/7 Access:</strong> Meals available whenever needed, ensuring convenience.", "<strong>Tilgang 24/7:</strong> Måltider tilgjengelig når som helst."),
                  t("<strong>Sustainability Focus:</strong> Locally sourced, high-quality ingredients support health and environmental goals.", "<strong>Fokus på bærekraft:</strong> Lokale råvarer av høy kvalitet støtter helse- og miljømål.")])}
        <div class="center" data-reveal>{p.button(t("Apply for a grabEAT kiosk", "Søk om en grabEAT-kiosk"), LIVE["apply"])}</div>
      </div>
    </section>
    <section class="section">
      <div class="container">
        {p.title(t("Leveraging AI for Smarter Eating", "KI for smartere matvaner"))}
        <p class="intro intro--gap" data-reveal>{t("At grabEAT, we harness Artificial Intelligence (AI) to enhance our vending operations, offering a seamless and sustainable experience. AI allows us to optimize efficiency, reduce waste, and deliver fresh, nutritious meals anytime.", "Hos grabEAT bruker vi kunstig intelligens (KI) til å forbedre driften av automatene og gi en sømløs og bærekraftig opplevelse. KI gjør oss mer effektive, reduserer svinn og sikrer ferske, næringsrike måltider når som helst.")}</p>
        <ul class="features" data-reveal>{ai_items}</ul>
      </div>
    </section>
    <section class="section section--logos">
      <div class="container"><div class="logos logos--5" data-reveal>{logo_html}</div></div>
    </section>
    {p.contact_band()}'''
    return shell(p, t('Smart food kiosks for workplaces and public spaces | grabEAT', 'Smarte matkiosker for bedrifter og fellesarealer | grabEAT'),
                 t('Compare grabEAT MealPOD, MealPOD+, HUB and SmartHUB: automated kiosks serving fresh, warm meals 24/7, with custom designs for your location.',
                   'Sammenlign grabEAT MealPOD, MealPOD+, HUB og SmartHUB: automatiserte kiosker med ferske, varme måltider 24/7 og design tilpasset din lokasjon.'), body)


def step_cards(p, steps):
    rows = ''.join(f'<li class="step-card"><span class="steps__num">{i}</span><h3>{h}</h3><p>{x}</p></li>' for i, (h, x) in enumerate(steps, 1))
    return f'<ol class="step-cards step-cards--{len(steps)}" data-reveal>{rows}</ol>'


def how(p):
    t = p.t
    business = [
        (t('Consultation &amp; Customization', 'Rådgivning og tilpasning'), t('Choose from our four kiosk options – MealPOD, MealPOD+, HUB or SmartHUB – based on your space and needs. These kiosks offer a range of healthy hot meals, drinks, and snacks.', 'Velg mellom våre fire kiosktyper – MealPOD, MealPOD+, HUB eller SmartHUB – etter lokalene og behovene dine. Kioskene tilbyr et utvalg sunne, varme måltider, drikke og snacks.')),
        (t('Seamless Installation &amp; Setup', 'Enkel installasjon og oppsett'), t('Our team handles the delivery and installation, ensuring a quick and seamless setup. All you need is power and internet, and the grabEAT kiosk will be ready to serve your employees or customers.', 'Teamet vårt tar seg av levering og installasjon, så oppsettet går raskt og smertefritt. Alt du trenger er strøm og internett, så er grabEAT-kiosken klar til å betjene ansatte eller kunder.')),
        (t('Maintenance &amp; Refilling', 'Vedlikehold og påfylling'), t('Our kiosks come with built-in software for real-time monitoring, tracking stock levels and sending alerts for restocking to avoid emptiness. Maintenance is done regularly by our staff to ensure everything runs smoothly.', 'Kioskene har innebygd programvare for sanntidsovervåking, som følger lagernivået og varsler om påfylling så de aldri går tomme. Våre ansatte utfører jevnlig vedlikehold, slik at alt går som det skal.')),
    ]
    consumers = [
        (t('Find grabEAT Kiosk', 'Finn en grabEAT-kiosk'), t('Our kiosks are conveniently located in offices, gyms, hospitals, and other public spaces. Whether you’re looking for a quick snack or a wholesome meal, grabEAT kiosk is always close by.', 'Kioskene våre står lett tilgjengelig på kontorer, treningssentre, sykehus og andre fellesarealer. Enten du vil ha en rask matbit eller et skikkelig måltid, er en grabEAT-kiosk alltid i nærheten.')),
        (t('Choose Your Meal', 'Velg måltidet ditt'), t('Simply browse the menu on the touchscreen display. From warm, freshly prepared meals to cold &amp; hot drinks and snacks, you can find a variety of nutritious options to satisfy your cravings.', 'Bla gjennom menyen på berøringsskjermen. Fra varme, nylagde måltider til kald og varm drikke og snacks – her finner du mange næringsrike alternativer.')),
        (t('Pay Seamlessly', 'Betal enkelt'), t('grabEAT kiosks are fully cashless, allowing you to pay quickly and easily. Use your credit or debit card, mobile payment, or contactless options like Vipps, Apple Pay or Google Pay to complete your purchase.', 'grabEAT-kioskene er helt kontantfrie, så du betaler raskt og enkelt. Bruk kredittkort eller bankkort, mobilbetaling eller kontaktløse løsninger som Vipps, Apple Pay eller Google Pay.')),
        (t('Enjoy Your Meal', 'Nyt måltidet'), t('After you’ve made your selection, your meal is prepared in just a few minutes. You can then enjoy a nutritious, ready-to-eat dish, perfect for busy days or meals on-the-go.', 'Når du har valgt, er måltidet klart på bare noen få minutter. Da kan du nyte en næringsrik, ferdig rett, perfekt for travle dager eller måltider på farten.')),
    ]
    body = f'''{p.hero(t("How grabEAT works", "Slik fungerer grabEAT"), "page-hero-how-it-works.webp")}
    <section class="section">
      <div class="container narrow center-block">
        {p.title(t("Healthy Food 24/7", "Sunn mat 24/7"))}
        <p class="intro" data-reveal>{t("At grabEAT, we believe that healthy food doesn’t have to be a luxury. That’s why we bring nutritious, delicious, and convenient meals to you every day. Whether you’re looking for a quick meal during a busy day or want a healthier option on-the-go, our innovative kiosks have you covered.", "Hos grabEAT mener vi at sunn mat ikke skal være en luksus. Derfor gir vi deg næringsrike, deilige og enkle måltider hver dag. Enten du trenger et raskt måltid i en travel hverdag eller et sunnere alternativ på farten, har de innovative kioskene våre det du trenger.")}</p>
      </div>
    </section>
    <section class="section section--cream" id="business">
      <div class="container">
        {p.title(t("For business partners", "For bedriftspartnere"))}
        <p class="intro intro--gap" data-reveal>{t("We help businesses provide their employees and customers with healthy, convenient, and innovative meal solutions right at their fingertips. Our smart kiosks are designed to offer freshly prepared meals and drinks, making it easier for businesses to enhance their workplace or service environment.", "Vi hjelper bedrifter med å gi ansatte og kunder sunne, enkle og innovative måltidsløsninger rett ved hånden. De smarte kioskene våre tilbyr nylagde måltider og drikke, og gjør det enklere å løfte arbeidsplassen eller servicetilbudet.")}</p>
        {step_cards(p, business)}
        <div class="center cta-gap" data-reveal>{p.button(t("Apply for a grabEAT kiosk", "Søk om en grabEAT-kiosk"), LIVE["apply"])}</div>
      </div>
    </section>
    <section class="section" id="consumers">
      <div class="container">
        {p.title(t("For consumers", "For forbrukere"))}
        <p class="intro intro--gap" data-reveal>{t("We make it easy for you to enjoy healthy, delicious meals and drinks — whenever you want. With our smart kiosks, you can quickly grab a nutritious meal without compromising on quality or taste.", "Vi gjør det enkelt å nyte sunne, deilige måltider og drikke – når du vil. Med de smarte kioskene våre får du raskt et næringsrikt måltid uten å gå på kompromiss med kvalitet eller smak.")}</p>
        {step_cards(p, consumers)}
        <div class="center cta-gap" data-reveal>{p.button(t("Browse grabEAT Menu", "Se grabEAT-menyen"), "../our-menu/")}</div>
      </div>
    </section>
    {p.contact_band()}'''
    return shell(p, t('How it works: healthy meals from smart kiosks | grabEAT', 'Slik fungerer det: sunn mat fra smarte kiosker | grabEAT'),
                 t('See how grabEAT works for businesses and consumers: find a kiosk, choose a meal, pay contactlessly and enjoy. Hosts only need power and internet.',
                   'Se hvordan grabEAT fungerer for bedrifter og forbrukere: finn en kiosk, velg måltid, betal kontaktløst og nyt. Verten trenger bare strøm og internett.'), body)


TAG_NO = {'Chicken': 'Kylling', 'Beef': 'Storfe', 'Halal': 'Halal', 'Pork': 'Svin', 'Breakfast': 'Frokost', 'Vegetarian': 'Vegetar', 'Lamb': 'Lam', 'Fish': 'Fisk', 'Vegan': 'Vegansk', 'Deer': 'Hjort'}
DIET_URL = {'Vegan': 'VeganDiet', 'Vegetarian': 'VegetarianDiet', 'Halal': 'HalalDiet'}
TAG_ORDER = ['Vegetarian', 'Vegan', 'Halal', 'Breakfast', 'Chicken', 'Beef', 'Pork', 'Lamb', 'Deer', 'Fish']
SUPPLIERS = ['Tren og Mat', 'Asian Corner', 'Nawabs', 'Le Chef']


def meal_card(p, m):
    t = p.t
    tag_label = (lambda x: x) if p.lang == 'en' else TAG_NO.get
    tags = [x for x in m['tags'] if x != 'Lunch/Dinner']
    tag_html = ''.join(f'<li>{tag_label(x)}</li>' for x in sorted(tags, key=TAG_ORDER.index))
    if m['image']:
        media = f'<img src="{p.asset("img/menu/" + m["image"])}" alt="{escape(m["name"], quote=True)}" loading="lazy">'
    else:
        media = f'<img class="meal__logo" src="{p.asset("logos/grabeat-logo.webp")}" alt="" loading="lazy">'
    info = ''
    if m['description']:
        info += f'<p>{escape(m["description"])}</p>'
    if m['ingredients']:
        info += f'<p><strong>{t("Ingredients", "Ingredienser")}:</strong> {escape(m["ingredients"])}</p>'
    if m['allergens']:
        info += f'<p><strong>{t("Allergens", "Allergener")}:</strong> {escape(m["allergens"])}</p>'
    if not m['ingredients'] and not m['allergens']:
        info += f'<p>{t("Ingredient and allergen details are not listed yet. Please check the label on the meal or ask us at", "Ingredienser og allergener er ikke oppført ennå. Sjekk etiketten på måltidet eller spør oss på")} <a href="mailto:post@grabeat.no">post@grabeat.no</a>.</p>'
    data = ' '.join(tags)
    return f'''<article class="meal" data-supplier="{m["supplier"]}" data-tags="{data}">
          <div class="meal__media">{media}</div>
          <div class="meal__body">
            <p class="meal__supplier">{m["supplier"]}</p>
            <h3>{escape(m["name"])}</h3>
            <ul class="meal__tags">{tag_html}</ul>
            <p class="meal__price">{m["price"]} kr</p>
            <details class="meal__details"><summary>{t("Ingredients &amp; allergens", "Ingredienser og allergener")}</summary><div lang="en">{info}</div></details>
          </div>
        </article>'''


def menu(p):
    t = p.t
    tag_label = (lambda x: x) if p.lang == 'en' else TAG_NO.get
    all_label = t('All', 'Alle')
    chips = f'<button class="chip" type="button" aria-pressed="true" data-filter="">{all_label}</button>' + ''.join(
        f'<button class="chip" type="button" aria-pressed="false" data-filter="{x}">{tag_label(x)}</button>' for x in TAG_ORDER)
    sup_chips = f'<button class="chip" type="button" aria-pressed="true" data-filter="">{all_label}</button>' + ''.join(
        f'<button class="chip" type="button" aria-pressed="false" data-filter="{x}">{x}</button>' for x in SUPPLIERS)
    cards = '\n        '.join(meal_card(p, m) for m in MENU)
    logos = [('supplier-tren-og-mat.webp', 'Tren og Mat'), ('supplier-asian-corner.webp', 'Asian Corner'), ('supplier-nawabs.webp', 'Nawabs'), ('supplier-le-chef.webp', 'Le Chef')]
    logo_html = ''.join(p.img('logos/' + f, a) for f, a in logos)
    sections = []
    for s in SUPPLIERS:
        items = []
        for m in (x for x in MENU if x['supplier'] == s):
            item = {'@type': 'MenuItem', 'name': m['name'], 'offers': {'@type': 'Offer', 'price': m['price'], 'priceCurrency': 'NOK'}}
            if m['description']:
                item['description'] = m['description']
            if m['image']:
                item['image'] = f'{SITE}/assets/img/menu/{m["image"]}'
            diets = [f'https://schema.org/{DIET_URL[x]}' for x in m['tags'] if x in DIET_URL]
            if diets:
                item['suitableForDiet'] = diets
            items.append(item)
        sections.append({'@type': 'MenuSection', 'name': s, 'hasMenuItem': items})
    ld = {'@type': 'Menu', 'name': t('grabEAT menu', 'grabEAT-menyen'), 'hasMenuSection': sections}
    body = f'''{p.hero(t("Our Menu", "Menyen vår"), "page-hero-meal-bowls.webp")}
    <section class="section section--cream">
      <div class="container narrow center-block">
        {p.title(t("Nutritious, Warm Meals On the Go", "Næringsrike, varme måltider på farten"))}
        {p.ticks([t("<strong>International Dishes.</strong> A diverse selection of meals, from comforting classics to global flavors.", "<strong>Internasjonale retter.</strong> Et variert utvalg, fra trygge klassikere til smaker fra hele verden."),
                  t("<strong>Balanced Nutrition.</strong> Each meal is designed to be both satisfying and nutritious, with a focus on fresh ingredients and balanced portions.", "<strong>Balansert ernæring.</strong> Hvert måltid er både mettende og næringsrikt, med vekt på ferske råvarer og balanserte porsjoner."),
                  t("<strong>Quick and Convenient.</strong> Ready in just 5 minutes.", "<strong>Raskt og enkelt.</strong> Klart på bare 5 minutter.")])}
        <div class="center" data-reveal>{p.button(t("Get a grabEAT kiosk", "Få en grabEAT-kiosk"), LIVE["apply"])}</div>
      </div>
    </section>
    <section class="section" id="meals">
      <div class="container" data-menu>
        {p.title(t("Explore Our Menu", "Utforsk menyen"))}
        <div class="filters" role="group" aria-label="{t("Filter by type", "Filtrer etter type")}" data-filter-group="tags">{chips}</div>
        <div class="filters" role="group" aria-label="{t("Filter by supplier", "Filtrer etter leverandør")}" data-filter-group="supplier">{sup_chips}</div>
        <p class="menu__note">{t("Allergens are shown in CAPITALS in the ingredient lists. If you have an allergy, always check the label on your meal.", "Allergener står med STORE BOKSTAVER i ingredienslistene, og ingredienser og allergener vises på engelsk. Har du en allergi, må du alltid sjekke etiketten på måltidet.")}</p>
        <p class="menu__count" role="status" data-menu-count data-label="{t("meals", "måltider")}">{len(MENU)} {t("meals", "måltider")}</p>
        <div class="meals">
        {cards}
        </div>
      </div>
    </section>
    <section class="section section--logos">
      <div class="container">
        {p.title(t("Our Meal Suppliers", "Våre matleverandører"))}
        <div class="logos logos--4" data-reveal>{logo_html}</div>
      </div>
    </section>
    {p.contact_band()}'''
    return shell(p, t('Menu: warm meals, prices and allergens | grabEAT', 'Meny: varm mat, priser og allergener | grabEAT'),
                 t('Browse 59 grabEAT meals with prices, ingredients and allergens. Filter by vegetarian, vegan, halal, chicken, beef and more, available from our kiosks.',
                   'Se 59 grabEAT-måltider med priser, ingredienser og allergener. Filtrer på vegetar, vegansk, halal, kylling, storfe og mer, tilgjengelig i kioskene våre.'), body, ld)


def about(p):
    t = p.t
    values = [
        (t('Innovation at Our Core', 'Innovasjon i kjernen'), t('Our automated kiosks are designed to serve healthy, warm meals at the touch of a button. By harnessing technology, we’re creating a future where good food is always within reach.', 'Våre automatiserte kiosker serverer sunne, varme måltider med et enkelt trykk. Med teknologi skaper vi en fremtid der god mat alltid er innen rekkevidde.')),
        (t('Convenience Meets Quality', 'Enkelt og godt'), t('We’re more than just a quick bite. At grabEAT, we prioritize locally sourced fresh ingredients and carefully crafted recipes that give you the nutrition you need without compromising on flavour.', 'Vi er mer enn en rask matbit. Hos grabEAT prioriterer vi ferske, lokale råvarer og gjennomtenkte oppskrifter som gir deg næringen du trenger, uten å gå på kompromiss med smaken.')),
        (t('Sustainability &amp; Social Impact', 'Bærekraft og samfunnsansvar'), t('At grabEAT, we believe businesses should drive positive change. We are committed to sustainability by reducing food waste, sourcing responsibly, supporting local suppliers, and using eco-friendly packaging.', 'Hos grabEAT mener vi at bedrifter skal bidra til positiv endring. Vi satser på bærekraft ved å redusere matsvinn, handle ansvarlig, støtte lokale leverandører og bruke miljøvennlig emballasje.')),
        (t('Healthy Choices for All', 'Sunne valg for alle'), t('From vegan and vegetarian options to protein-packed meals and kid-friendly choices, our menu is built to support a variety of dietary preferences. No matter your needs, we’ve got something for you.', 'Fra veganske og vegetariske alternativer til proteinrike måltider og barnevennlige valg – menyen vår passer for mange ulike kostpreferanser. Uansett behov har vi noe for deg.')),
    ]
    value_html = ''.join(f'<article class="value"><h3>{h}</h3><p>{x}</p></article>' for h, x in values)
    programs = [('unity-spark.png', 'Unity Spark'), ('startup-migrants.webp', 'Startup Migrants'), ('tna-gta.webp', t('Tech Nordic Advocates and Global Tech Advocates', 'Tech Nordic Advocates og Global Tech Advocates')), ('aggrator.webp', 'Aggrator'), ('charge.webp', 'Charge')]
    prog_html = ''.join(p.img('logos/' + f, a) for f, a in programs)
    body = f'''{p.hero(t("About grabEAT", "Om grabEAT"), "page-hero-meal-bowls.webp")}
    <section class="section">
      <div class="container narrow center-block">
        {p.title(t("Our Journey Begins Here", "Her begynner reisen vår"))}
        <p class="lede center" data-reveal>{t("At grabEAT, we’re passionate about making healthy, convenient meals accessible to everyone, no matter how busy life gets.", "Hos grabEAT brenner vi for å gjøre sunne, enkle måltider tilgjengelige for alle, uansett hvor travel hverdagen er.")}</p>
        <p class="intro" data-reveal>{t("Founded in 2024, we are a startup with a simple mission: to bring nutritious, freshly-prepared food to people on the go—anytime, anywhere. Our automated kiosks and innovative solutions are designed to fit seamlessly into your daily routine, offering a range of delicious meals accessible 24/7.", "Vi ble grunnlagt i 2024 og er en oppstartsbedrift med et enkelt mål: å gi folk på farten næringsrik, nylaget mat – når og hvor som helst. Våre automatiserte kiosker og innovative løsninger passer sømløst inn i hverdagen din, med et utvalg deilige måltider tilgjengelig 24/7.")}</p>
      </div>
    </section>
    <section class="section section--mist">
      <div class="container">
        {p.split("img/grabeat-our-story.webp", t("grabEAT meals, wraps and a sandwich on a picnic table", "grabEAT-måltider, wraps og et smørbrød på et bord ute"),
                 f'<h2>{t("Our Story", "Historien vår")}</h2><p>{t("grabEAT started with a clear vision: to solve the everyday challenge of finding healthy food options that are both quickly and easily accessible. We saw the need for better choices—options that didn’t sacrifice quality or nutrition for speed. So, we set out to create a new kind of food experience, one that blends the ease of technology with the goodness of freshly-made meals.", "grabEAT startet med en klar visjon: å løse hverdagsutfordringen med å finne sunn mat som er rask og lett tilgjengelig. Vi så behovet for bedre valg – uten å ofre kvalitet eller næring for hastighet. Derfor ville vi skape en ny type matopplevelse, som forener enkel teknologi med det gode i nylagde måltider.")}</p>')}
      </div>
    </section>
    <section class="section section--mist section--flush-top">
      <div class="container">
        {p.split("img/man-holding-vegetable-basket.webp", t("A man holding a basket of fresh vegetables", "En mann som holder en kurv med ferske grønnsaker"),
                 f'<h2>{t("Our Mission", "Vårt oppdrag")}</h2><p>{t("We’re here to make healthy eating effortless and accessible for everyone. Whether you’re a busy professional, a student, or a traveler, we believe you deserve nutritious meals that fit your lifestyle. grabEAT is committed to offering a variety of balanced, high-quality meals that cater to different tastes and dietary needs.", "Vi er her for å gjøre sunn mat enkel og tilgjengelig for alle. Enten du er travel i jobben, student eller på reise, fortjener du næringsrike måltider som passer livsstilen din. grabEAT tilbyr et variert utvalg balanserte måltider av høy kvalitet, tilpasset ulike smaker og kostbehov.")}</p>', reverse=True)}
      </div>
    </section>
    <section class="section">
      <div class="container">
        {p.title(t("What We Stand For", "Dette står vi for"))}
        <div class="values" data-reveal>{value_html}</div>
        <div class="center cta-gap" data-reveal>{p.button(t("Read More", "Les mer"), LIVE["sustainability"])}</div>
      </div>
    </section>
    <section class="section section--mist">
      <div class="container">
        {p.split("img/grabeat-smart-kiosk.webp", t("A grabEAT smart kiosk", "En smart grabEAT-kiosk"),
                 f'<h2>{t("This is just a beginning...", "Dette er bare begynnelsen ...")}</h2><p>{t("We’re just getting started, but we have big ambitions. Our goal is to expand across Bergen City, and eventually reach communities nationwide and globally. We’re eager to grow, learn, and continue refining our service so that grabEAT can become a trusted solution for quickly and easily accessible healthy meals in busy environments.", "Vi har så vidt begynt, men vi har store ambisjoner. Målet er å vokse i hele Bergen og etter hvert nå lokalsamfunn over hele landet og verden. Vi vil vokse, lære og fortsette å forbedre tjenesten, slik at grabEAT kan bli en løsning folk stoler på for sunn mat som er rask og lett tilgjengelig i travle miljøer.")}</p>', reverse=True)}
      </div>
    </section>
    <section class="section section--logos">
      <div class="container">
        {p.title(t("Programs We Attended", "Programmer vi har deltatt i"))}
        <div class="logos logos--5" data-reveal>{prog_html}</div>
      </div>
    </section>
    <section class="section">
      <div class="container center" data-reveal>
        <div class="person">{p.img("img/glenda-anfinsen-ceo-grabeat.webp", "Glenda Anfinsen")}<h2>Glenda Anfinsen</h2><p>{t("CEO of grabEAT", "CEO i grabEAT")}</p></div>
      </div>
    </section>
    {p.contact_band()}'''
    return shell(p, t('About us: healthy food made accessible | grabEAT', 'Om oss: sunn mat som er lett tilgjengelig | grabEAT'),
                 t('grabEAT is a startup founded in 2024 with a simple mission: nutritious, freshly-prepared food for people on the go, available 24/7 from smart kiosks.',
                   'grabEAT er en oppstartsbedrift fra 2024 med et enkelt mål: næringsrik, nylaget mat for folk på farten, tilgjengelig 24/7 i smarte kiosker.'), body)


def contact(p):
    t = p.t
    topics = [t('I’m an investor', 'Jeg er investor'), t('Looking for a partnership', 'Ønsker samarbeid'), t('Location suggestion', 'Forslag til lokasjon'),
              t('Interested in bringing grabEAT to my workplace', 'Vil ha grabEAT på arbeidsplassen min'), t('Questions about grabEAT', 'Spørsmål om grabEAT')]
    topic_html = ''.join(f'<label class="check"><input type="checkbox" name="topic" value="{x}"><span>{x}</span></label>' for x in topics)
    social_links = ''.join(f'<a class="social-link" href="{u}">{icon(i)}{n}</a>' for n, i, u in SOCIALS)
    body = f'''{p.hero(t("Contact Us", "Kontakt oss"), "page-hero-meal-bowls.webp")}
    <section class="section section--mist">
      <div class="container">
        {p.title(t("Get In Touch", "Ta kontakt"))}
        <div class="contact__card" data-reveal>
          <div class="contact__info">
            <p>{t("Looking to partner, have a location suggestion, or interested in bringing grabEAT to your workplace?", "Ønsker du å samarbeide, har du forslag til en lokasjon, eller vil du ha grabEAT på arbeidsplassen din?")}</p>
            <p>{t("Let’s connect and bring healthy, fresh meals to you!", "Ta kontakt, så bringer vi sunne, ferske måltider til deg!")}</p>
            <a class="contact__item" href="tel:+4747223288"><span>{icon("phone")}</span><div><strong>{t("Phone", "Telefon")}</strong>+47 472 23 288</div></a>
            <a class="contact__item" href="mailto:post@grabeat.no"><span>{icon("mail")}</span><div><strong>{t("Email", "E-post")}</strong>post@grabeat.no</div></a>
            <a class="contact__item" href="https://www.google.com/maps/search/?api=1&amp;query=Strandbakken+31%2C+5101+Eidsv%C3%A5gneset"><span>{icon("pin")}</span><div><strong>{t("Address", "Adresse")}</strong>Strandbakken 31, 5101 Eidsvågneset</div></a>
          </div>
          <form class="form" data-contact-form novalidate>
            <div class="form__row">
              <label class="field"><span>{t("First Name", "Fornavn")}</span><input type="text" name="first" autocomplete="given-name" placeholder=" "></label>
              <label class="field"><span>{t("Last Name", "Etternavn")}</span><input type="text" name="last" autocomplete="family-name" placeholder=" "></label>
            </div>
            <div class="form__row">
              <label class="field"><span>{t("Email", "E-post")}</span><input type="email" name="email" autocomplete="email" required placeholder=" "></label>
              <label class="field"><span>{t("Phone", "Telefon")}</span><input type="tel" name="phone" autocomplete="tel" required placeholder=" "></label>
            </div>
            <fieldset class="checks"><legend>{t("Choose Topic/s:", "Velg tema:")}</legend>{topic_html}</fieldset>
            <label class="field"><span>{t("Message", "Melding")}</span><textarea name="message" rows="3" placeholder=" "></textarea></label>
            <p class="form__legal">{t("By clicking ‘Submit’ below, you agree that grabEAT may store and process the personal information submitted above to provide you with the requested content. I have read the", "Ved å klikke «Send» nedenfor godtar du at grabEAT kan lagre og behandle personopplysningene ovenfor for å gi deg det du har bedt om. Jeg har lest")} <a href="{LIVE["terms"]}" target="_blank" rel="noopener">{t("Terms &amp; Conditions, Data Protection Regulations", "vilkårene og personvernreglene")}</a>.</p>
            <label class="check"><input type="checkbox" name="optin" value="yes"><span>{t("I agree to receive further communications from grabEAT.", "Jeg samtykker til å motta videre kommunikasjon fra grabEAT.")}</span></label>
            <button class="btn btn--green btn--block" type="submit">{t("Submit", "Send")}</button>
            <p class="form__status" role="status" data-form-status></p>
          </form>
        </div>
      </div>
    </section>
    <section class="section section--sage section--band-plain">
      <div class="container center" data-reveal>
        <h2 class="band-title">{t("Connect With Us on Social Media", "Følg oss i sosiale medier")}</h2>
        <div class="social-links">{social_links}</div>
      </div>
    </section>'''
    return shell(p, t('Contact us | grabEAT kiosks in Bergen and Voss', 'Kontakt oss | grabEAT-kiosker i Bergen og Voss'),
                 t('Contact grabEAT about hosting a kiosk, partnerships, location suggestions or questions. Call +47 472 23 288 or email post@grabeat.no.',
                   'Kontakt grabEAT om kiosk, samarbeid, forslag til lokasjon eller spørsmål. Ring +47 472 23 288 eller send e-post til post@grabeat.no.'), body)


BUILDERS = {'our-solutions': solutions, 'how-it-works': how, 'our-menu': menu, 'about-us': about, 'contact-us': contact}


def sitemap():
    pairs = [('/', '/no/')] + [(f'/{s}/', f'/no/{s}/') for s in PAGES]
    rows = []
    for en, no in pairs:
        alts = (f'<xhtml:link rel="alternate" hreflang="en" href="{SITE}{en}"/><xhtml:link rel="alternate" hreflang="no" href="{SITE}{no}"/>'
                f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{en}"/>')
        rows += [f'  <url><loc>{SITE}{en}</loc>{alts}</url>', f'  <url><loc>{SITE}{no}</loc>{alts}</url>']
    body = '\n'.join(rows)
    (ROOT / 'sitemap.xml').write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n{body}\n</urlset>\n',
        encoding='utf-8')


def main():
    for slug, build in BUILDERS.items():
        for lang, base in (('en', ROOT / slug), ('no', ROOT / 'no' / slug)):
            base.mkdir(parents=True, exist_ok=True)
            (base / 'index.html').write_text(build(Page(lang, slug)), encoding='utf-8')
    sitemap()
    print('Built', len(BUILDERS) * 2, 'pages')


if __name__ == '__main__':
    main()
