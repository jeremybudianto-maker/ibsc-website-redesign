from pathlib import Path
import json, html
from interaction_components import story_browser, student_experiences
from admission_journey import admission_journey
from academic_components import academics_page
from content_model import load, news_records, faculty_records, story_cards, remove_retired_pages, resolve_content_links
from home_components import homepage, lines
from faculty_components import faculty_cards as render_faculty_cards

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)
site = load('site.json')
home_data = load('home.json')
articles = news_records()
profiles = faculty_records()
resolve_content_links(home_data,articles,profiles)
resolve_content_links(site,articles,profiles)
news = story_cards(articles)
remove_retired_pages(DIST, articles, profiles)
copy = json.loads((ROOT / 'content/core.json').read_text())
resolve_content_links(copy,articles,profiles)
photo_path = ROOT / 'content/photography.json'
photography = json.loads(photo_path.read_text()) if photo_path.exists() else {}
ORIGIN = 'https://ibsc-yzu-reimagined.nk27ffj8z8.chatgpt.site'
arrow = '<span class="arrow" aria-hidden="true">↗</span>'
LOCAL_ROUTES = {
 'https://ih.hs.yzu.edu.tw/':'about.html',
 'https://www.yzu.edu.tw/':'university.html',
 'https://ih.hs.yzu.edu.tw/prospective-students':'about.html',
 'https://ih.hs.yzu.edu.tw/about':'resources.html',
 'https://ih.hs.yzu.edu.tw/check-out-our-curriculum':'curriculum.html',
 'https://ih.hs.yzu.edu.tw/general-8':'curriculum.html#course-map',
 'https://ih.hs.yzu.edu.tw/meet-our-staff':'people.html#faculty',
 'https://ih.hs.yzu.edu.tw/ibsc-student-association':'student-association.html',
 'https://gao.yzu.edu.tw/index.php/en/':'global-opportunities.html',
 'https://ih.hs.yzu.edu.tw/events':'global-opportunities.html',
 'https://ih.hs.yzu.edu.tw/services-7-1':'service-learning.html',
 'https://ih.hs.yzu.edu.tw/services-3':'scholarships.html',
 'https://ih.hs.yzu.edu.tw/news':'news.html',
 'https://ih.hs.yzu.edu.tw/s-projects-side-by-side-1':'news.html#stories',
 'https://gao.yzu.edu.tw/index.php/en/admissions-2/int-student':'admissions-international.html',
 'https://www.yzu.edu.tw/admissions/index.php/tw/bachelor':'admissions-domestic.html',
 'https://www.yzu.edu.tw/admissions/index.php/tw/bachelor/apply':'admissions-domestic.html#pathways',
 'https://gao.yzu.edu.tw/index.php/en/admission/oversea-compatriot-student':'admissions-overseas.html',
 'https://ih.hs.yzu.edu.tw/career':'careers.html',
 'https://ih.hs.yzu.edu.tw/internships':'internships.html'
}
# Primary record sources resolve locally; supporting university sources stay intact.
for record in articles + profiles:
    if record.get('sources'):
        LOCAL_ROUTES[record['sources'][0]] = record['filename']
def link(label, href, cls='text-link'):
    return f'<a class="{html.escape(cls,quote=True)}" href="{html.escape(href,quote=True)}">{html.escape(label)}{arrow}</a>'
def brand():
    b=site['brand']
    return f'<span class="brand"><span class="brand-abbr">{html.escape(b["abbreviation"])}</span><span class="brand-divider"></span><span class="brand-university">{html.escape(b["university"])}<small>{html.escape(b["program"])}</small></span></span>'
nav = [(item['label'],item['href']) for item in site['navigation']]
def header(current='index.html'):
    navlinks = ''.join(f'<a href="{html.escape(u,quote=True)}"'+(' aria-current="page"' if u == current else '')+f'>{html.escape(n)}</a>' for n,u in nav)
    return f'''<a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap"><div class="header-main"><a href="index.html" aria-label="IBSC, Yuan Ze University home">{brand()}</a><div class="header-actions"><button class="icon-button" data-open-search aria-label="Search IBSC"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><span>Search</span></button><button class="icon-button" data-open-menu aria-label="Open site menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 6h20M2 12h20M2 18h20"/></svg><span class="menu-label">Menu</span></button></div></div><nav class="primary-nav" aria-label="Main navigation"><div class="primary-nav-links">{navlinks}</div><a class="nav-apply" href="{html.escape(site["admissions_link"]["href"],quote=True)}">{html.escape(site["admissions_link"]["label"])} {arrow}</a></nav></div></header>'''
def simple_links(items):
    return ''.join(f'<a href="{html.escape(item["href"],quote=True)}">{html.escape(item["label"])}' + (' '+arrow if item.get('show_arrow') else '') + '</a>' for item in items)
footer = f'''<footer class="site-footer"><div class="wrap"><div class="footer-main"><div class="footer-brand"><a href="index.html" aria-label="IBSC home">{brand()}</a><p>{lines(site['program_lines'])}</p></div><div><div class="footer-heading">{html.escape(site['footer_explore_title'])}</div><nav class="footer-links" aria-label="Footer navigation">{simple_links(site['footer_links'])}</nav></div><div class="footer-contact"><div class="footer-heading">{html.escape(site['footer_contact_title'])}</div><p>{lines(site['address_lines'])}</p><p><a href="{html.escape(site['phone_href'],quote=True)}">{html.escape(site['phone'])}</a> · ext. {html.escape(site['extension'])}<br><a href="mailto:{html.escape(site['secretary']['email'],quote=True)}">{html.escape(site['secretary']['email'])}</a></p>{link(site['contact_link']['label'],site['contact_link']['href'])}</div></div><div class="footer-bottom"><span>{html.escape(site['footer_credit'])} · {simple_links([site['credits_link']])}</span><nav class="social-links" aria-label="Social media">{simple_links(site['social_links'])}</nav></div></div></footer>'''
dialogs = '''<dialog class="overlay" id="menu-dialog" aria-labelledby="menu-title"><div class="overlay-inner"><div class="dialog-top"><h2 id="menu-title">Explore IBSC</h2><button class="close-button" data-close aria-label="Close menu">Close ×</button></div><nav class="menu-grid" aria-label="All pages"><a href="about.html">About IBSC ↗</a><a href="academics.html">Academics ↗</a><a href="people.html">Our People ↗</a><a href="student-life.html">Student Life ↗</a><a href="news.html">News &amp; Stories ↗</a><a href="admissions.html">Admissions ↗</a></nav><div class="menu-extra"><a href="about.html#visit">Contact &amp; visit</a><a href="https://ih.hs.yzu.edu.tw/about">Student resources ↗</a><a href="sources.html">Sources &amp; credits →</a></div></div></dialog><dialog class="overlay" id="search-dialog" aria-labelledby="search-title"><div class="overlay-inner"><div class="dialog-top"><h2 id="search-title">Search IBSC</h2><button class="close-button" data-close aria-label="Close search">Close ×</button></div><label for="site-search" class="eyebrow">What would you like to explore?</label><input class="search-input" id="site-search" type="search" placeholder="Try curriculum, faculty or admissions" autocomplete="off"><div class="search-results" id="search-results" aria-live="polite"></div></div></dialog>'''
def write_page(filename, title, content, description, home=False):
    bodyclass = '' if home else 'subpage'
    academic_assets = '<link rel="stylesheet" href="academics.css?v=2"><script src="academics.js?v=1" defer></script>' if filename == 'academics.html' else ''
    text = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#0d233d"><meta name="robots" content="noindex"><title>{html.escape(title)} | IBSC · Yuan Ze University</title><meta name="description" content="{html.escape(description, quote=True)}"><meta property="og:title" content="{html.escape(title, quote=True)} | IBSC"><meta property="og:description" content="{html.escape(description, quote=True)}"><meta property="og:image" content="{ORIGIN}/assets/hero.jpg"><link rel="icon" href="assets/logo.jpg"><link rel="stylesheet" href="styles.css?v=6"><link rel="stylesheet" href="interactions.css?v=2"><script src="app.js?v=6" defer></script><script src="interactions.js?v=2" defer></script>{academic_assets}</head><body class="{bodyclass}">{header(filename)}<main id="main">{content}</main>{footer}{dialogs}</body></html>'''
    if filename != 'sources.html':
        for remote,local in LOCAL_ROUTES.items():
            text = text.replace('href="'+remote+'"','href="'+local+'"')
    else:
        for fragment in [footer,dialogs]:
            local_fragment=fragment
            for remote,local in LOCAL_ROUTES.items():
                local_fragment=local_fragment.replace('href="'+remote+'"','href="'+local+'"')
            text=text.replace(fragment,local_fragment)
    (DIST / filename).write_text(text)
def faculty_cards():
    return render_faculty_cards(profiles, link, featured=True)
home=homepage(home_data,news,faculty_cards(),link,arrow)
write_page('index.html',home_data['title'],home,home_data['description'],True)

def subhero(data,image):
    photo = photography.get('placements',{}).get(data['eyebrow'],{})
    image = photo.get('image',image)
    cover = ''
    if image and not photo.get('hide'):
        alt = photo.get('alt',data.get('image_alt','IBSC students at Yuan Ze University'))
        position = html.escape(photo.get('position','center 45%'),quote=True)
        image_style = f'object-position:{position}' + (';height:auto' if photo.get('natural') else '')
        caption = '<figcaption>'+html.escape(photo['caption'])+'</figcaption>' if photo.get('caption') else ''
        cover = f'<figure class="subpage-photo"><img class="subpage-cover" src="assets/{image}" alt="{html.escape(alt,quote=True)}" style="{image_style}" loading="eager" decoding="async">{caption}</figure>'
    return f'''<section class="subpage-hero"><div class="wrap"><div class="breadcrumb"><a href="index.html">Home</a> &nbsp; / &nbsp; {data['eyebrow']}</div><div class="eyebrow">{data['eyebrow']}</div><h1>{data['title']}</h1><p class="lead">{data['intro']}</p>{cover}</div></section>'''
def layout(content,items):
    aside=''.join(f'<a href="#{id}">{name}</a>' for id,name in items)
    return f'<div class="wrap content-layout"><nav class="page-aside" aria-label="On this page"><div class="eyebrow">On this page</div>{aside}</nav><div class="prose">{content}</div></div>'
def resources(items):
    return '<div class="admission-links">'+''.join(f'<a href="{html.escape(i["href"],quote=True)}">{html.escape(i["label"])}{arrow}</a>' for i in items)+'</div>'
director=next((p for p in profiles if p['id']==site['director_id']),None)
director_contact=(f'<p>{html.escape(director["name"])}<br><a href="mailto:{html.escape(director["contact"]["email"],quote=True)}">{html.escape(director["contact"]["email"])}</a></p>' if director and director.get('contact',{}).get('email') else link('Contact the program office','about.html#visit'))
about=f'''<section id="story"><h2>A program for a connected world</h2><p>{copy['about']['body']}</p><p>Founded in 2017, IBSC is part of Yuan Ze University’s College of Humanities and Social Sciences. The program was formerly known as EBSC.</p><div class="info-grid">'''+''.join(f'<div class="info-item"><h3>{s["title"]}</h3><p>{s["copy"]}</p></div>' for s in copy['about']['sections'])+f'''</div>{link('Explore our academics','academics.html')}</section><section id="visit"><h2>Connect with IBSC</h2><p>Visit the program office in Building 7, Room R70201, on the second floor of Yuan Ze University.</p><div class="info-grid"><div class="info-item"><h3>Find us</h3><p>No. 135, Yuandong Road<br>Zhongli District, Taoyuan City 320, Taiwan<br>Building 7, Room R70201</p></div><div class="info-item"><h3>Get in touch</h3><p><a href="{html.escape(site["phone_href"],quote=True)}">{html.escape(site["phone"])}</a> · ext. {html.escape(site["extension"])}<br>Program secretary: {html.escape(site["secretary"]["name"])}<br><a href="mailto:{html.escape(site["secretary"]["email"],quote=True)}">{html.escape(site["secretary"]["email"])}</a></p></div><div class="info-item"><h3>Program director</h3>{director_contact}</div></div>{link('Yuan Ze University','https://www.yzu.edu.tw/')}</section><section id="resources"><h2>Learn more</h2>{resources(copy['about']['links'])}</section>'''
write_page('about.html','About IBSC',subhero(copy['about'],'community.jpg')+layout(about,[('story','Our story'),('visit','Contact & visit'),('resources','Program resources')]),copy['about']['intro'])

academic_data=json.loads((ROOT / 'content/academics.json').read_text())
approach_photo=dict(photography['placements']['Academics'],width=1600,height=1066)
write_page('academics.html','Academics',academics_page(copy['academics'],academic_data,approach_photo),copy['academics']['intro'])

life_sections=''.join(f'<section id="life-{i}"><h2>{s["title"]}</h2><p>{s["copy"]}</p>{link(s["label"],s["href"])}</section>' for i,s in enumerate(copy['student_life']['sections']))
experiences = json.loads((ROOT / 'content/experiences.json').read_text())
resolve_content_links(experiences,articles,profiles)
student=f'''<section id="community"><h2>Make the experience your own</h2><p>{copy['student_life']['body']}</p></section>{student_experiences(experiences)}{life_sections}<section id="resources"><h2>Resources for your journey</h2>{resources(copy['student_life']['links'])}</section>'''
write_page('student-life.html','Student Life',subhero(copy['student_life'],'student-life.jpg')+layout(student,[('community','Our community'),('experiences','Student experiences'),('life-0','Student Association'),('life-1','Global opportunities'),('life-2','Service learning'),('resources','Student resources')]),copy['student_life']['intro'])

journeys = json.loads((ROOT / 'content/admissions-journey.json').read_text())
resolve_content_links(journeys,articles,profiles)
adm=f'<section id="pathway" data-reveal>{admission_journey(journeys)}</section>'
for id,pathway in zip(['international','domestic','overseas'],copy['admissions']['pathways']):
    adm+=f'<section id="{id}"><h2>{pathway["title"]}</h2><p>{pathway["copy"]}</p>{resources(pathway["links"])}</section>'
adm+=f'''<section id="support"><h2>Scholarships &amp; support</h2><p>Explore the program’s scholarship resources and the latest guidance from the university. Availability and requirements vary by scholarship and applicant category.</p>{link('Scholarships and grants','https://ih.hs.yzu.edu.tw/services-3')}<div class="callout"><h3>Questions about the program?</h3><p>Contact the IBSC office: <a href="mailto:{html.escape(site["secretary"]["email"],quote=True)}">{html.escape(site["secretary"]["email"])}</a><br>{html.escape(site["phone"])} · ext. {html.escape(site["extension"])}</p>{link('Contact & visit','about.html#visit')}</div></section><section class="faq" id="questions"><h2>A few useful answers</h2><details><summary>Is IBSC taught in English?</summary><p>Yes. The official program website describes IBSC as a full English program.</p></details><details><summary>Where can I find current application dates?</summary><p>Follow the official admission guidance for your applicant category. Intake dates and document requirements can change.</p></details><details><summary>Where is Yuan Ze University?</summary><p>Yuan Ze University is in Zhongli District, Taoyuan City, Taiwan. The IBSC office is in Building 7, Room R70201.</p></details></section>'''
write_page('admissions.html','Admissions',subhero(copy['admissions'],'hero.jpg')+layout(adm,[('pathway','Application pathways'),('international','International applicants'),('domestic','Domestic applicants'),('overseas','Overseas compatriots'),('support','Scholarships & support'),('questions','Common questions')]),copy['admissions']['intro'])

newsdata={'eyebrow':'News & stories','title':'Life, ideas, and<br>everything in between','intro':'Stories from the IBSC community, from cultural discovery to the moments that bring students together.'}
newscontent='<section id="stories" data-reveal><h2 style="margin-bottom:30px">Featured stories</h2>'+story_browser(news,'featured-stories')+'</section><section id="more" style="margin-top:55px"><h2>Keep exploring</h2>'+resources([{'label':'Explore student experiences','href':'student-life.html#experiences'},{'label':'Program news & announcements','href':'https://ih.hs.yzu.edu.tw/news'},{'label':'IBSC on Instagram','href':'https://www.instagram.com/ibscyzu_official/'}])+'</section>'
write_page('news.html','News & Stories',subhero(newsdata,'student-life.jpg')+layout(newscontent,[('stories','Featured stories'),('more','More from IBSC')]),newsdata['intro'])

manifest_path = ROOT / '.openai/hosting.json'
if manifest_path.exists():
    manifest=json.loads(manifest_path.read_text())
    manifest['static']={'directory':'dist'}
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
print('Created core pages with canonical IBSC content and bundled imagery.')
