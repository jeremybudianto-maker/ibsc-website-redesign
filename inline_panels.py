"""Consolidate verified guides into native disclosures on their parent pages.

Call ``consolidate_pages(DIST, resource_pages)`` after all pages are rendered
and before building the search index. The returned search entries point to
the disclosures; filenames in PANEL_ROUTES are compatibility redirects only.
This module uses the standard library and does not import a page generator.
"""

from dataclasses import dataclass, field
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit, urlunsplit


PANEL_ROUTES = {
    "curriculum.html": "academics.html#curriculum-panel",
    "student-association.html": "student-life.html#association-panel",
    "global-opportunities.html": "student-life.html#global-panel",
    "service-learning.html": "student-life.html#service-panel",
    "scholarships.html": "admissions.html#scholarships-panel",
    "careers.html": "resources.html#careers-panel",
    "internships.html": "resources.html#internships-panel",
    "admissions-international.html": "admissions.html#international-guide",
    "admissions-domestic.html": "admissions.html#domestic-guide",
    "admissions-overseas.html": "admissions.html#overseas-guide",
    "university.html": "about.html#university-panel",
}

# Mutated in place so importing this optional export before consolidation works.
PANEL_SEARCH = []

_PREFIXES = {
    "curriculum.html": "curriculum",
    "student-association.html": "association",
    "global-opportunities.html": "global",
    "service-learning.html": "service",
    "scholarships.html": "scholarships",
    "careers.html": "careers",
    "internships.html": "internships",
    "admissions-international.html": "international",
    "admissions-domestic.html": "domestic",
    "admissions-overseas.html": "overseas",
    "university.html": "university",
}
_VOID = frozenset("area base br col embed hr img input link meta param source track wbr".split())


@dataclass
class _Element:
    tag: str
    attrs: dict
    start: int
    open_end: int
    end_start: int = 0
    end: int = 0
    children: list = field(default_factory=list)


class _Document(HTMLParser):
    """Track source spans without reserializing the generated document."""

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.offsets = [0]
        for match in re.finditer("\n", source):
            self.offsets.append(match.end())
        self.elements = []
        self.stack = []
        self.feed(source)

    def _position(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self._position()
        node = _Element(tag, dict(attrs), start, start + len(self.get_starttag_text()))
        if self.stack:
            self.stack[-1].children.append(node)
        self.elements.append(node)
        if tag in _VOID:
            node.end_start = node.end = node.open_end
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in _VOID:
            node = self.stack.pop()
            node.end_start = node.end = node.open_end

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i].tag == tag:
                node = self.stack[i]
                node.end_start = self._position()
                node.end = self.source.find(">", node.end_start) + 1
                del self.stack[i:]
                return

    def by_id(self, ident):
        matches = [n for n in self.elements if n.attrs.get("id") == ident]
        if len(matches) != 1:
            raise ValueError(f"Expected one generated element with id={ident!r}; found {len(matches)}")
        return matches[0]

    def with_class(self, name, tag=None):
        return next((n for n in self.elements
                     if (tag is None or n.tag == tag)
                     and name in n.attrs.get("class", "").split()), None)

    def outer(self, node):
        return self.source[node.start:node.end]


def _apply(source, edits):
    for start, end, replacement in sorted(edits, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source


def _intro_children(document, section):
    """Retain the original heading and opening paragraph of a core section."""
    result = []
    for child in section.children:
        if child.tag not in {"h2", "p"}:
            break
        result.append(document.outer(child))
    return "".join(result)


def _paragraphs(items):
    return "".join("<p>" + html.escape(str(item)) + "</p>" for item in items)


def _list(items, ordered=False):
    if not items:
        return ""
    tag = "ol" if ordered else "ul"
    return "<" + tag + ">" + "".join("<li>" + html.escape(str(item)) + "</li>" for item in items) + "</" + tag + ">"


def _section_id(filename, old_id):
    prefix = _PREFIXES[filename]
    if filename == "admissions-domestic.html" and old_id in {"portfolio", "interview"}:
        prefix = "individual"
    return prefix + "-" + old_id


def _fragment_routes(pages):
    routes = {}
    for filename in PANEL_ROUTES:
        owner = PANEL_ROUTES[filename].split("#", 1)[0]
        for i, section in enumerate(pages.get(filename, {}).get("sections", [])):
            old_id = section.get("id", "section-" + str(i))
            routes[(filename, old_id)] = owner + "#" + _section_id(filename, old_id)
    # The renderer appended a contact section to the former admission guides.
    for filename, target in {
        "admissions-international.html": "international-help",
        "admissions-domestic.html": "domestic-guidance",
        "admissions-overseas.html": "overseas-help",
    }.items():
        routes[(filename, "contact")] = "admissions.html#" + target
    routes[("university.html", "university")] = "about.html#university-university"
    routes[("university.html", "visit")] = "about.html#university-visit"
    return routes


def _canonical_href(href, fragment_routes, routes=None):
    parsed = urlsplit(href)
    # External sources and real actions retain their original destination.
    if parsed.scheme or parsed.netloc:
        return href
    filename = unquote(parsed.path).lstrip("/")
    while filename.startswith("./"):
        filename = filename[2:]
    routes = PANEL_ROUTES if routes is None else routes
    if filename not in routes:
        return href
    destination = fragment_routes.get((filename, unquote(parsed.fragment)), routes[filename])
    target = urlsplit(destination)
    return urlunsplit(("", "", target.path, parsed.query, target.fragment))


def _link(item, fragment_routes, local_fragments=None, routes=None):
    href = str(item["href"])
    if href.startswith("#") and local_fragments:
        href = "#" + local_fragments.get(unquote(href[1:]), href[1:])
    else:
        href = _canonical_href(href, fragment_routes, routes)
    label = str(item["label"])
    external = urlsplit(href).scheme.lower() == "https"
    attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
    if external and not any(phrase in label.lower() for phrase in ("external", "new tab")):
        label += " (opens a new tab)"
    icon = "↗" if external else "→"
    return '<a class="text-link" href="' + html.escape(href, quote=True) + '"' + attrs + ">" + html.escape(label) + '<span class="arrow" aria-hidden="true">' + icon + "</span></a>"


def _panel(page, ident, fragment_routes, sections=None, label=None, prefix=None, photo=False, routes=None):
    filename = page["filename"]
    sections = page["sections"] if sections is None else sections
    prefix = _PREFIXES[filename] if prefix is None else prefix
    label = label or page.get("label", page["eyebrow"])
    local = {s.get("id", "section-" + str(i)): prefix + "-" + s.get("id", "section-" + str(i))
             for i, s in enumerate(sections)}
    content = '<p class="panel-intro">' + html.escape(page["intro"]) + "</p>" if page.get("intro") else ""
    if photo and page.get("image"):
        alt = page.get("image_alt", page.get("label", label))
        content += '<figure class="disclosure-photo"><img src="assets/' + html.escape(page["image"], quote=True) + '" alt="' + html.escape(alt, quote=True) + '" loading="eager" decoding="async"></figure>'
    for i, section in enumerate(sections):
        old_id = section.get("id", "section-" + str(i))
        content += '<div class="panel-section" id="' + html.escape(local[old_id], quote=True) + '"><h3>' + html.escape(section["title"]) + "</h3>"
        content += _paragraphs(section.get("paragraphs", []))
        content += _list(section.get("bullets", [])) + _list(section.get("steps", []), ordered=True)
        if section.get("links"):
            content += '<div class="disclosure-links">' + "".join(_link(item, fragment_routes, local, routes) for item in section["links"]) + "</div>"
        content += "</div>"
    return '<details class="info-disclosure" id="' + html.escape(ident, quote=True) + '"><summary>' + html.escape(label) + '<span class="disclosure-icon" aria-hidden="true"></span></summary><div class="disclosure-content">' + content + "</div></details>"


def _rewrite_anchors(source, fragment_routes):
    document = _Document(source)
    edits = []
    for node in document.elements:
        if node.tag != "a" or "href" not in node.attrs:
            continue
        original = node.attrs["href"]
        destination = _canonical_href(original, fragment_routes)
        if destination == original:
            continue
        opening = source[node.start:node.open_end]
        opening = re.sub(r'\bhref\s*=\s*([\'\"])(.*?)\1',
                         lambda match: 'href="' + html.escape(destination, quote=True) + '"',
                         opening, count=1, flags=re.S | re.I)
        edits.append((node.start, node.open_end, opening))
    return _apply(source, edits)


def _university_panel(source):
    document = _Document(source)
    lead = document.with_class("lead", "p")
    content = '<p class="panel-intro">' + source[lead.open_end:lead.end_start] + "</p>" if lead else ""
    for ident in ("university", "visit"):
        node = document.by_id(ident)
        snippet = source[node.open_end:node.end_start]
        snippet = re.sub(r"<(/?)h2\b", r"<\1h3", snippet)
        content += '<div class="panel-section" id="university-' + ident + '">' + snippet + "</div>"
    return '<details class="info-disclosure" id="university-panel"><summary>Yuan Ze University<span class="disclosure-icon" aria-hidden="true"></span></summary><div class="disclosure-content">' + content + "</div></details>"


def _redirect(filename, fragment_routes):
    destination = PANEL_ROUTES[filename]
    fragment_map = {fragment: target for (name, fragment), target in fragment_routes.items() if name == filename}
    script = "const routes=" + json.dumps(fragment_map, ensure_ascii=False) + ";let fragment=location.hash.slice(1);try{fragment=decodeURIComponent(fragment)}catch(error){}const target=(routes[fragment]||" + json.dumps(destination) + ").split('#');location.replace(target[0]+location.search+'#'+target[1]);"
    return '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url=' + html.escape(destination, quote=True) + '"><link rel="canonical" href="' + html.escape(destination, quote=True) + '"><title>Continue to IBSC</title><script>' + script + '</script></head><body><p><a href="' + html.escape(destination, quote=True) + '">Continue to IBSC</a></p></body></html>'


def consolidate_pages(DIST, resource_pages):
    """Move full guide copy to core pages and return canonical search entries.

    Existing documents are loaded before changing any file. All sections are
    rendered from the verified resource data; photos appear only for the two
    topics with distinctive photography. Repeated calls are safe.
    """
    directory = Path(DIST)
    if isinstance(resource_pages, dict):
        resource_pages = resource_pages["pages"]
    pages = {page["filename"]: page for page in resource_pages}
    required = set(PANEL_ROUTES) - {"university.html"}
    missing = sorted(required - pages.keys())
    if missing:
        raise ValueError("Missing guide data: " + ", ".join(missing))
    documents = {path.name: path.read_text(encoding="utf-8") for path in directory.glob("*.html")}
    fragments = _fragment_routes(pages)
    entries = []

    def disclosure(filename, ident=None, **options):
        ident = ident or PANEL_ROUTES[filename].split("#", 1)[1]
        return _panel(pages[filename], ident, fragments, **options)

    def search_entry(filename, title=None, url=None, sections=None):
        page = pages[filename]
        sections = page["sections"] if sections is None else sections
        entries.append({"title": title or page.get("label", page["eyebrow"]),
                        "url": url or PANEL_ROUTES[filename],
                        "text": " ".join([page.get("intro", "")] + [s["title"] for s in sections])})

    # Admission guides are directly below their corresponding pathway copy.
    source = documents["admissions.html"]
    document = _Document(source)
    edits = []
    for section_id, filename in (("international", "admissions-international.html"),
                                 ("overseas", "admissions-overseas.html")):
        node = document.by_id(section_id)
        edits.append((node.open_end, node.end_start, _intro_children(document, node) + disclosure(filename)))
        search_entry(filename)
    domestic = pages["admissions-domestic.html"]
    general_sections = [s for s in domestic["sections"] if s.get("id") in {"pathways", "application", "guidance"}]
    individual_sections = [s for s in domestic["sections"] if s.get("id") in {"portfolio", "interview"}]
    node = document.by_id("domestic")
    panels = disclosure("admissions-domestic.html", "domestic-guide", sections=general_sections, label="Undergraduate admissions")
    panels += disclosure("admissions-domestic.html", "individual-guide", sections=individual_sections, label="Individual application information", prefix="individual")
    edits.append((node.open_end, node.end_start, _intro_children(document, node) + panels))
    search_entry("admissions-domestic.html", "Undergraduate admissions", sections=general_sections)
    search_entry("admissions-domestic.html", "Individual application information", "admissions.html#individual-guide", individual_sections)
    node = document.by_id("support")
    callouts = [document.outer(child) for child in node.children if "callout" in child.attrs.get("class", "").split()]
    edits.append((node.open_end, node.end_start, _intro_children(document, node) + disclosure("scholarships.html") + "".join(callouts)))
    search_entry("scholarships.html")
    documents["admissions.html"] = _apply(source, edits)

    # Keep the course browser outside its companion curriculum guide.
    source = documents["academics.html"]
    document = _Document(source)
    node = document.by_id("academic-curriculum-guide")
    guide_sections = [dict(section) for section in pages["curriculum.html"]["sections"]]
    for section in guide_sections:
        if section.get("id") == "courses":
            section["bullets"] = []
            section["links"] = [{"label": "Browse the published course examples", "href": "#courses"}]
    content = disclosure("curriculum.html", sections=guide_sections)
    # The course browser lives on this page, outside the guide's local fragments.
    content = content.replace('href="#curriculum-courses"', 'href="#courses"')
    documents["academics.html"] = _apply(source, [(node.open_end, node.end_start, content)])
    search_entry("curriculum.html")

    source = documents["student-life.html"]
    document = _Document(source)
    edits = []
    for section_id, filename in (("life-0", "student-association.html"),
                                 ("life-1", "global-opportunities.html"),
                                 ("life-2", "service-learning.html")):
        node = document.by_id(section_id)
        panel = disclosure(filename, photo=False)
        edits.append((node.open_end, node.end_start, _intro_children(document, node) + panel))
        search_entry(filename)
    documents["student-life.html"] = _apply(source, edits)

    # The resource hub offers all seven topics without seven navigation trips.
    source = documents["resources.html"]
    document = _Document(source)
    node = document.by_id("explore")
    topics = ("curriculum.html", "student-association.html", "global-opportunities.html",
              "service-learning.html", "scholarships.html", "careers.html", "internships.html")
    content = "<h2>Everything in one place</h2>"
    hub_routes = dict(PANEL_ROUTES)
    hub_fragments = dict(fragments)
    hub_targets = {}
    for filename in topics:
        canonical_here = filename in {"careers.html", "internships.html"}
        prefix = _PREFIXES[filename] if canonical_here else "resource-" + _PREFIXES[filename]
        ident = PANEL_ROUTES[filename].split("#", 1)[1] if canonical_here else prefix + "-panel"
        hub_targets[filename] = (prefix, ident)
        hub_routes[filename] = "resources.html#" + ident
        for i, section in enumerate(pages[filename]["sections"]):
            old_id = section.get("id", "section-" + str(i))
            hub_fragments[(filename, old_id)] = "resources.html#" + prefix + "-" + old_id
    for filename in topics:
        prefix, ident = hub_targets[filename]
        content += _panel(pages[filename], ident, hub_fragments, prefix=prefix,
                          photo=False, routes=hub_routes)
    edits = [(node.open_end, node.end_start, content)]
    for ident in ("studies", "community", "support"):
        matches = [n for n in document.elements if n.attrs.get("id") == ident]
        if matches:
            edits.append((matches[0].start, matches[0].end, ""))
    aside = document.with_class("page-aside", "nav")
    if aside:
        edits.append((aside.open_end, aside.end_start, '<div class="eyebrow">On this page</div><a href="#explore">Explore resources</a><a href="#office">Program office</a>'))
    documents["resources.html"] = _apply(source, edits)
    search_entry("careers.html")
    search_entry("internships.html")

    # University information becomes part of About, with no extra hero.
    source = documents["about.html"]
    document = _Document(source)
    existing = next((n for n in document.elements if n.attrs.get("id") == "university-panel"), None)
    if existing:
        university_panel = document.outer(existing)
    else:
        university_panel = _university_panel(documents["university.html"])
        visit = document.by_id("visit")
        source = _apply(source, [(visit.start, visit.start, '<section id="university-information"><h2>Our university</h2>' + university_panel + "</section>")])
    document = _Document(source)
    aside = document.with_class("page-aside", "nav")
    if aside and "#university-panel" not in source[aside.open_end:aside.end_start]:
        story_link = next((child for child in aside.children if child.tag == "a" and child.attrs.get("href") == "#story"), None)
        position = story_link.end if story_link else aside.open_end
        source = _apply(source, [(position, position, '<a href="#university-panel">Yuan Ze University</a>')])
    documents["about.html"] = source
    entries.append({"title": "Yuan Ze University", "url": PANEL_ROUTES["university.html"],
                    "text": "Yuan Ze University, Taoyuan, Taiwan. University information, academic community, location and contact."})

    # Rewrite local reading links everywhere, including the shared footer and
    # dialogs on Sources. HTTPS links in its official reference list stay intact.
    for filename, source in list(documents.items()):
        if filename not in PANEL_ROUTES:
            documents[filename] = _rewrite_anchors(source, fragments)
    for filename in PANEL_ROUTES:
        documents[filename] = _redirect(filename, fragments)
    for filename, source in documents.items():
        (directory / filename).write_text(source, encoding="utf-8")
    PANEL_SEARCH[:] = entries
    return list(entries)
