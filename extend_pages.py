"""Render internal profiles, stories and the student resource library."""
import html, json, re
from pathlib import Path
from generate import ROOT, DIST, ORIGIN, news, articles, profiles, site, header, footer, dialogs, link, layout, resources, subhero, write_page, LOCAL_ROUTES, photography, experiences, academic_data
from faculty_components import faculty_cards, office_people
from content_model import resolve_content_links

def paragraphs(items):
    return ''.join('<p>'+html.escape(p)+'</p>' for p in items)

def section_content(sections):
    result=''
    for i,s in enumerate(sections):
        sid=s.get('id','section-'+str(i))
        result+=f'<section id="{sid}"><h2>{html.escape(s["title"])}</h2>'
        result+=paragraphs(s.get('paragraphs',[]))
        if s.get('bullets'):
            result+='<ul>'+''.join('<li>'+html.escape(b)+'</li>' for b in s['bullets'])+'</ul>'
        if s.get('steps'):
            result+='<ol>'+''.join('<li>'+html.escape(b)+'</li>' for b in s['steps'])+'</ol>'
        if s.get('links'):
            result+=resources(s['links'])
        result+='</section>'
    return result

all_sources=[]
resourcefile=ROOT/'content/resources.json'
if resourcefile.exists():
    resource_data=json.loads(resourcefile.read_text())
    resource_pages=resource_data if isinstance(resource_data,list) else resource_data['pages']
    resolve_content_links(resource_pages,articles,profiles)
    for page in resource_pages:
        sections=page['sections']
        toc=[(s.get('id','section-'+str(i)),s['title']) for i,s in enumerate(sections)]
        body=section_content(sections)
        if page['filename']=='resources.html':
            body='<section id="explore"><h2>Everything in one place</h2>'+resources([
                {'label':'Curriculum & course map','href':'curriculum.html'},
                {'label':'Student Association','href':'student-association.html'},
                {'label':'Global opportunities','href':'global-opportunities.html'},
                {'label':'Service learning','href':'service-learning.html'},
                {'label':'Scholarships & financial support','href':'scholarships.html'},
                {'label':'Careers & professional pathways','href':'careers.html'},
                {'label':'Internship preparation','href':'internships.html'}])+ '</section>'+body
            toc.insert(0,('explore','Explore resources'))
        if page['filename'].startswith('admissions-'):
            body+='<section id="contact"><h2>Talk to the program</h2><p>Questions about IBSC courses, student life, or your application pathway? Contact the program office.</p>'+link('Contact IBSC','about.html#visit')+'</section>'
            toc.append(('contact','Contact IBSC'))
        body+='<div class="related-panel"><span class="eyebrow">Keep exploring</span>'+resources([{'label':'Student resources','href':'resources.html'},{'label':'Contact the program office','href':'about.html#visit'}])+'</div>'
        write_page(page['filename'],page.get('label',page['eyebrow']),subhero(page,page.get('image','community.jpg'))+layout(body,toc),page['intro'])
        all_sources.extend(page.get('sources',[]))

# Each article supplies its card, full page, related links and search metadata.
for item in articles:
    filename=item['filename']
    image=item['image'];intro=item['intro'];title=item['title']
    category=item['category'];date=item['date_label']
    content=f'<section class="article-top wrap"><div class="breadcrumb"><a href="index.html">Home</a> / <a href="news.html">News &amp; stories</a></div><div class="eyebrow">{html.escape(category)} · {html.escape(date)}</div><h1>{html.escape(title)}</h1><p class="lead">{html.escape(intro)}</p><figure><img src="assets/{html.escape(image,quote=True)}" alt="{html.escape(item["alt"],quote=True)}" loading="eager" decoding="async"><figcaption>{html.escape(item.get("caption",item["alt"]))}</figcaption></figure></section>'
    body=paragraphs(item.get('paragraphs',[]))
    if item.get('sections'):body+=section_content(item['sections'])
    body+='<div class="related-panel"><div class="eyebrow">Explore more stories</div>'+resources([{'label':n['title'],'href':n['filename']} for n in articles if n['id']!=item['id']])+'</div>'
    content+=f'<div class="wrap article-body"><div class="prose">{body}</div><aside class="article-aside"><div class="eyebrow">The IBSC experience</div><h2>Bring your perspective</h2><p>Explore the people and experiences that make our community.</p>{link("Explore student life","student-life.html")}</aside></div>'
    write_page(filename,title,content,intro)
    all_sources.extend(item.get('sources',[]))

# All faculty appearances come from the same profile record.
for p in profiles:
    filename=p['filename']
    name=p['name'];role=p['role'];intro=p['intro'];image=p['image']
    sections=[dict(section) for section in p.get('sections',[])]
    contact=p.get('contact',{})
    email=contact.get('email');office=contact.get('office');phone=contact.get('phone')
    if email or office or phone:
        sections.append({'id':'contact','title':'Connect','paragraphs':([f'Phone: {phone}'] if phone else [])+([f'Office: {office}'] if office else [])})
    content=f'<section class="profile-top wrap"><div class="breadcrumb"><a href="index.html">Home</a> / <a href="people.html">Our people</a></div><div class="profile-grid"><img src="assets/{html.escape(image,quote=True)}" alt="{html.escape(p["alt"],quote=True)}" loading="eager" decoding="async"><div><div class="eyebrow">{html.escape(role)}</div><h1>{html.escape(name)}</h1><p class="lead">{html.escape(intro)}</p>'+ (link('Email '+name,'mailto:'+email) if email else link('Contact the program office','about.html#visit'))+'</div></div></section>'
    body=section_content(sections)
    if email:body+=f'<p><a class="text-link" href="mailto:{html.escape(email,quote=True)}">{html.escape(email)} ↗</a></p>'
    body+='<div class="related-panel"><span class="eyebrow">Meet our people</span>'+resources([{'label':q['name'],'href':q['filename']} for q in profiles if q['id']!=p['id']])+'</div>'
    content+=layout(body,[(s.get('id','section-'+str(i)),s['title']) for i,s in enumerate(sections)])
    write_page(filename,name,content,intro)
    all_sources.extend(p.get('sources',[]))

directory=faculty_cards(profiles,link)
peopledata={'eyebrow':'Faculty & staff','title':'Many perspectives<br>One learning community','intro':'Meet the IBSC faculty and affiliated faculty whose expertise connects language, communication, culture, policy, and professional practice.'}
people=f'<section id="faculty"><h2>Faculty &amp; affiliated faculty</h2><div class="faculty-grid">{directory}</div></section><section id="office"><h2>People who support your journey</h2>{office_people(profiles,site,link)}</section>'
write_page('people.html','Faculty & Staff',subhero(peopledata,'community.jpg')+layout(people,[('faculty','Our faculty'),('office','Program office')]),peopledata['intro'])

university={'eyebrow':'Yuan Ze University','title':'Rooted in Taiwan<br>Open to the world','intro':'Established in 1989, Yuan Ze University is home to IBSC and a community that connects the humanities, technology, and professional practice.'}
universitybody='<section id="university"><h2>A wider community of learning</h2><p>Yuan Ze University is in Zhongli District, Taoyuan City, Taiwan. Its academic community spans engineering, informatics, management, humanities and social sciences, and electrical and communications engineering.</p><p>IBSC belongs to the College of Humanities and Social Sciences. Learning brings together perspectives from languages, design, social and policy sciences, and business.</p><p>The university supports international experiences, industry connections, and opportunities for students to develop their interests beyond the classroom.</p>'+resources([{'label':'About IBSC','href':'about.html'},{'label':'Academics','href':'academics.html'},{'label':'Student life','href':'student-life.html'}])+'</section><section id="visit"><h2>Find your way here</h2><p>No. 135, Yuandong Road, Zhongli District, Taoyuan City 320, Taiwan.</p><p>The IBSC program office is in Building 7, Room R70201, on the second floor.</p>'+link('Contact & visit','about.html#visit')+'</section>'
write_page('university.html','Yuan Ze University',subhero(university,'international.jpg')+layout(universitybody,[('university','Our university'),('visit','Location & contact')]),university['intro'])
all_sources += [url for experience in experiences for url in experience.get('sources',[])]
all_sources += [photo['source_page'] for photo in photography.get('placements',{}).values() if photo.get('source_page')]
all_sources += academic_data['sources'] + [photo['source_page'] for photo in academic_data['photos'].values()]
all_sources+=list(LOCAL_ROUTES.keys())+['https://www.yzu.edu.tw/aboutyzu/index.php/en-us/introduction-of-yuan-ze-university','https://www.princeton.edu/']
all_sources=[u for u in dict.fromkeys(all_sources) if 'ia.yzu.edu.tw' not in u]
sourcesdata={'eyebrow':'Content & photography','title':'Sources & credits','intro':'Program information, faculty details, stories, and photography are drawn from official IBSC and Yuan Ze University sources.'}
sourcebody='<section id="information"><h2>About this information</h2><p>This website is a separate IBSC redesign preview. Program facts, biographies, and event summaries are paraphrased from official university sources, checked on October 5, 2026. Application requirements and university regulations are administered by Yuan Ze University.</p><p>Photographs and the IBSC logo belong to their respective owners. Barlow Condensed and DM Sans are distributed by Google Fonts.</p><p>The visual structure is inspired by Princeton University, with IBSC’s own content and a blue palette.</p></section><section id="references"><h2>Official references</h2><p>The links below open the source websites in a new tab.</p><ul class="source-list">'+''.join(f'<li><a href="{html.escape(u,quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(u.replace("https://",""))}</a></li>' for u in all_sources)+'</ul></section>'
photo_credits = '<section id="photography"><h2>Photography</h2><p>Additional section photographs were selected from official IBSC and Yuan Ze University galleries on October 8, 2026. Captions identify the photographed context; dated events are historical photographs.</p><ul class="source-list">'+''.join(f'<li>{html.escape(p["caption"])} <a href="{html.escape(p["source_page"],quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(p["credit"])}</a></li>' for p in photography.get('placements',{}).values() if p.get('source_page'))+'</ul></section>'
academic_credits = '<p>Four additional Academics photographs were selected from official IBSC coverage on October 10, 2026.</p><ul class="source-list">'+''.join(f'<li>{html.escape(p["caption"])} <a href="{html.escape(p["source_page"],quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(p["credit"])}</a></li>' for p in academic_data['photos'].values())+'</ul>'
photo_credits = photo_credits.replace('</section>',academic_credits+'</section>')
sourcebody = sourcebody.replace('<section id="references">',photo_credits+'<section id="references">')
write_page('sources.html','Sources & Credits',subhero(sourcesdata,'community.jpg')+layout(sourcebody,[('information','Information & credits'),('photography','Photo credits'),('references','Official references')]),sourcesdata['intro'])

from inline_panels import consolidate_pages, PANEL_ROUTES
panel_search = consolidate_pages(DIST, resource_pages)
searchdata=[]
for p in sorted(DIST.glob('*.html')):
    text=p.read_text()
    if p.name in PANEL_ROUTES:
        continue
    title=html.unescape(re.search(r'<title>(.*?)</title>',text,re.S).group(1).split(' | IBSC')[0])
    description=html.unescape(re.search(r'<meta name="description" content="(.*?)">',text,re.S).group(1))
    if p.name not in ['sources.html','index.html']:
        searchdata.append({'title':title,'url':p.name,'text':description})
searchdata.extend(panel_search)
app=DIST/'app.js'
script=app.read_text()
script=re.sub(r'const searchData = \[.*?\];', lambda _: 'const searchData = '+json.dumps(searchdata,ensure_ascii=False,indent=1)+';',script,flags=re.S)
app.write_text(script)

# Make the real application portal and social accounts explicit external actions.
for p in DIST.glob('*.html'):
    text=p.read_text()
    def local_arrow(match):
        attrs,body=match.group(1),match.group(2)
        if 'href="https://' not in attrs:
            body=body.replace('↗','→')
        return '<a'+attrs+'>'+body+'</a>'
    text=re.sub(r'<a([^>]*)>(.*?)</a>',local_arrow,text,flags=re.S)
    text=text.replace(' — external',' (opens a new tab)')
    if p.name!='sources.html':
        text=text.replace('>Apply online<','>Apply in the official portal (opens a new tab)<')
        def external_action(match):
            tag=match.group(0)[:-1]
            if not re.search(r'\btarget\s*=',tag):
                tag+=' target="_blank"'
            if not re.search(r'\brel\s*=',tag):
                tag+=' rel="noopener noreferrer"'
            return tag+'>'
        text=re.sub(r'<a\b[^>]*href="https://[^"]+"[^>]*>',external_action,text)
    p.write_text(text)
print('Built',len(list(DIST.glob('*.html'))),'connected pages.')
