"""Shared faculty markup for homepage cards, directory and contact sections."""
import html


def e(value):
    return html.escape(str(value), quote=True)


def faculty_cards(profiles, link, featured=False):
    return ''.join(f'''<article class="faculty-card"><a href="{e(p['filename'])}" aria-label="Read the profile of {e(p['name'])}"><img src="assets/{e(p['image'])}" alt="{e(p['alt'])}" loading="eager" decoding="async"></a><div><span class="eyebrow">{e(p['role'])}</span><h3><a href="{e(p['filename'])}">{e(p['name'])}</a></h3><p>{e(p['intro'])}</p>{link(p.get('profile_link_label','Read profile') if featured else 'Read profile',p['filename'])}</div></article>''' for p in profiles if not featured or p.get('featured'))


def office_people(profiles, site, link):
    director = next((p for p in profiles if p['id'] == site['director_id']), None)
    card = ''
    if director:
        email = director.get('contact', {}).get('email')
        card = f'<div class="info-item"><h3>{e(director["name"])}</h3><p>{e(director["role"])}<br>' + (f'<a href="mailto:{e(email)}">{e(email)}</a>' if email else '') + '</p></div>'
    secretary = site['secretary']
    return f'<div class="info-grid">{card}<div class="info-item"><h3>{e(secretary["name"])}</h3><p>{e(secretary["role"])}<br><a href="mailto:{e(secretary["email"])}">{e(secretary["email"])}</a><br>{e(site["phone"])} · ext. {e(site["extension"])}</p></div></div>' + link('Contact the program office','about.html#visit')
