"""The existing homepage composition, filled only from editorial data."""
import html
from interaction_components import story_browser


def e(value):
    return html.escape(str(value), quote=True)


def lines(value):
    return e(value).replace('\n', '<br>')


def homepage(data, news, faculty_markup, link, arrow):
    hero, intro, inside = data['hero'], data['intro'], data['inside']
    academics, faculty = data['academics'], data['faculty']
    life, admissions = data['student_life'], data['admissions']
    def action(item, cls='text-link'):
        return link(item['label'], item['href'], cls)
    disciplines = ''.join(f'<a class="discipline" href="{e(item["href"])}"><span class="discipline-number">0{i+1}</span><h3>{lines(item["title"])}</h3>{arrow}</a>' for i, item in enumerate(academics['disciplines']))
    life_links = ''.join(f'<a href="{e(item["href"])}">{e(item["label"])} ↗</a>' for item in life['links'])
    admission_links = ''.join(f'<a href="{e(item["href"])}"><span>{e(item["label"])}<small>{e(item["description"])}</small></span>{arrow}</a>' for item in admissions['links'])
    return f'''<section class="hero" aria-labelledby="hero-heading"><img class="hero-img" src="assets/{e(hero['image'])}" alt="{e(hero['alt'])}" fetchpriority="high"><div class="wrap hero-content"><div class="eyebrow">{e(hero['eyebrow'])}</div><h1 id="hero-heading">{lines(hero['title'])}</h1><p class="hero-description">{lines(hero['description'])}</p>{action(hero['action'],'btn')}</div><div class="wrap hero-bottom"><span>{e(hero['program'])}</span><a class="hero-scroll" href="#discover"><span>{e(hero['scroll_label'])}</span><span aria-hidden="true">↓</span></a></div></section>
<div class="wrap" id="discover"><div class="intro-strip"><div class="intro-mark">{lines(intro['title'])}<span>{e(intro['label'])}</span></div><p>{e(intro['description'])}</p>{action(intro['action'])}</div></div>
<section class="section wrap" id="inside-ibsc" data-reveal aria-labelledby="stories-heading"><div class="section-top"><div><div class="eyebrow">{e(inside['eyebrow'])}</div><h2 id="stories-heading">{e(inside['title'])}</h2></div>{action(inside['action'])}</div>{story_browser(news,'inside-stories')}</section>
<section class="academics light" aria-labelledby="academics-heading"><div class="wrap"><div class="academics-head"><div><div class="eyebrow accent">{e(academics['eyebrow'])}</div><h2 id="academics-heading">{lines(academics['title'])}</h2></div><div><p>{e(academics['description'])}</p>{action(academics['action'])}</div></div><div class="discipline-grid">{disciplines}</div></div></section>
<section class="section wrap" aria-labelledby="faculty-heading"><div class="people-intro"><div><div class="eyebrow">{e(faculty['eyebrow'])}</div><h2 id="faculty-heading">{e(faculty['title'])}</h2></div><div><p>{e(faculty['description'])}</p>{action(faculty['action'])}</div></div><div class="faculty-grid">{faculty_markup}</div></section>
<section class="life" data-reveal aria-labelledby="life-heading"><img class="life-image" src="assets/{e(life['image'])}" alt="{e(life['alt'])}" loading="eager" decoding="async"><div class="life-content"><div class="eyebrow">{e(life['eyebrow'])}</div><h2 id="life-heading">{lines(life['title'])}</h2><p>{e(life['description'])}</p>{action(life['action'])}<div class="life-links">{life_links}</div></div></section>
<section class="admissions wrap" data-reveal aria-labelledby="admission-heading"><div><div class="eyebrow">{e(admissions['eyebrow'])}</div><h2 id="admission-heading">{lines(admissions['title'])}</h2><p>{e(admissions['description'])}</p></div><div class="admission-links">{admission_links}</div></section>'''
