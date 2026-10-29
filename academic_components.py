"""Editorial academic page; verified records remain separate from presentation."""
import html


def esc(value):
    return html.escape(str(value), quote=True)


def photograph(photo, eager=False):
    return f'<img src="assets/{esc(photo["image"])}" alt="{esc(photo["alt"])}" width="{photo["width"]}" height="{photo["height"]}" loading="{"eager" if eager else "lazy"}" decoding="async">'


def academics_page(copy, data, approach_photo):
    navigation = ''.join(f'<a href="#{ident}">{label}</a>' for ident, label in [
        ('approach', 'Learning at IBSC'), ('learning', 'Learning in practice'),
        ('disciplines', 'Fields of study'), ('courses', 'Courses & curriculum')])
    cards = []
    for index, theme in enumerate(data['themes']):
        photo = data['photos'][theme['photo']]
        cards.append(f'''<details class="academic-theme" id="learning-{esc(theme['group'])}"><summary>
          <span class="academic-theme-photo">{photograph(photo)}</span>
          <span class="academic-theme-copy"><span class="academic-number">0{index+1}</span>
          <strong>{esc(theme['title'])}</strong><span class="academic-theme-deck">{esc(theme['deck'])}</span>
          <span class="academic-theme-action">Explore this theme<span class="disclosure-icon" aria-hidden="true"></span></span></span>
          </summary><div class="academic-theme-content"><p>{esc(theme['copy'])}</p>
          <p class="academic-caption">{esc(photo['caption'])}</p>
          <a class="text-link" href="#courses" data-course-jump="{esc(theme['group'])}">Browse related courses<span class="arrow" aria-hidden="true">→</span></a></div></details>''')
    fields = []
    for index, field in enumerate(data['fields']):
        fields.append(f'''<details class="academic-field" name="academic-fields" id="{esc(field['id'])}"{' open' if index == 0 else ''}>
          <summary><span class="academic-number">0{index+1}</span><span>{esc(field['title'])}</span><span class="disclosure-icon" aria-hidden="true"></span></summary>
          <div><p>{esc(field['copy'])}</p></div></details>''')
    filters = '<button type="button" data-course-filter="all" aria-pressed="true" aria-controls="course-collection">All courses</button>'
    filters += ''.join(f'<button type="button" data-course-filter="{esc(group["id"])}" aria-pressed="false" aria-controls="course-collection">{esc(group["title"])}</button>' for group in data['groups'])
    courses = ''.join(f'''<article class="academic-course" data-course-group="{esc(course['group'])}"><span class="academic-course-code">{esc(course['code'])}</span><h3>{esc(course['title'])}</h3></article>''' for course in data['courses'])
    field_photo = data['photos']['collaboration']
    return f'''<div class="academic-page">
      <header class="academic-opening wrap"><div class="breadcrumb"><a href="index.html">Home</a> &nbsp; / &nbsp; Academics</div>
      <div class="academic-opening-grid"><div><div class="eyebrow">Academics</div><h1>{esc(copy['title'])}</h1></div><p class="lead">{esc(copy['intro'])}</p></div></header>
      <nav class="academic-navigation wrap" aria-label="On this page">{navigation}</nav>
      <section class="academic-approach wrap" id="approach" aria-labelledby="approach-title">
      <figure>{photograph(approach_photo, True)}<figcaption>{esc(approach_photo['caption'])}</figcaption></figure>
      <div class="academic-approach-copy"><div class="eyebrow">An education across disciplines</div><h2 id="approach-title">Connect knowledge<br>with practice</h2><p>{esc(copy['body'])}</p>
      <a class="text-link" href="#learning">Explore how you learn<span class="arrow" aria-hidden="true">↓</span></a></div></section>
      <section class="academic-learning wrap" id="learning" data-reveal aria-labelledby="learning-title"><div class="academic-section-head"><div><div class="eyebrow">Learning in practice</div><h2 id="learning-title">Ideas take shape here</h2></div><p>Language, creative media, and audience insight come together in strategic communication. Select a theme to explore the coursework.</p></div><div class="academic-theme-grid">{''.join(cards)}</div></section>
      <section class="academic-disciplines" id="disciplines" aria-labelledby="fields-title"><div class="wrap"><div class="academic-section-head"><div><div class="eyebrow">Five contributing fields</div><h2 id="fields-title">Perspectives that<br>come together</h2></div><p>IBSC brings together teaching from across Yuan Ze University’s humanities, social sciences, languages, design, and management departments.</p></div>
      <div class="academic-fields-grid"><div class="academic-field-list">{''.join(fields)}</div><figure>{photograph(field_photo)}<figcaption>{esc(field_photo['caption'])}</figcaption></figure></div></div></section>
      <section class="academic-courses wrap" id="courses" aria-labelledby="courses-title" data-course-browser><div class="academic-section-head"><div><div class="eyebrow">Explore the curriculum</div><h2 id="courses-title">A glimpse of your studies</h2></div><p>Browse selected courses from the published IBSC curriculum. Availability and requirements should be checked against the course list for your entry year.</p></div>
      <div class="academic-filters" role="group" aria-label="Filter courses by theme" hidden>{filters}</div>
      <p class="academic-course-count" data-course-count aria-live="polite" aria-atomic="true">{len(data['courses'])} published course entries</p><div class="academic-course-grid" id="course-collection">{courses}</div>
      <div class="academic-planning"><div><div class="eyebrow">Your study plan</div><h3>Plan your academic journey</h3><p>Explore the course map, progression, and advising guidance. Confirm your individual study plan with the program office.</p><a class="text-link" href="about.html#visit">Contact the program office<span class="arrow" aria-hidden="true">→</span></a></div><div id="academic-curriculum-guide"></div></div></section>
      </div>'''
