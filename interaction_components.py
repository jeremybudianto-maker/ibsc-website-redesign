"""Progressively enhanced story and experience markup for the IBSC site.

These helpers return HTML only. They never build pages, publish, or import the
generator. Pass verified copy and canonical links; the normal page writer can
also apply its existing official-to-local route mapping after rendering.

Enhancement contract for story_browser:
* Unhide [data-story-controls] and .story-selector-list after initialization.
* All [data-story-panel] articles start visible for the no-JavaScript fallback.
* Selector buttons use data-story-select (zero-based), aria-controls, and
  aria-pressed; update their state alongside the active article and count.

student_experiences accepts a list of records, or an optional mapping with
``items`` and ``intro`` when the caller supplies a custom section introduction.
Experience records accept an explicit ``id``, optional ``points``, and optional
image ``width``/``height`` in addition to the verified content fields.
"""

import html
import re
import unicodedata
from collections.abc import Mapping


__all__ = ["story_browser", "student_experiences"]


def _escape(value):
    return html.escape(str(value), quote=True)


def _slug(value, fallback):
    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-") or fallback


def _image_source(value):
    value = str(value)
    if value.startswith(("assets/", "/", "https://", "http://")):
        return value
    return "assets/" + value


def _geometry(item):
    """A stable 3:2 display frame unless the caller supplies dimensions."""
    try:
        width, height = int(item.get("width", 1600)), int(item.get("height", 1066))
    except (TypeError, ValueError):
        width, height = 1600, 1066
    return (width, height) if width > 0 and height > 0 else (1600, 1066)


def _image(item, loading="lazy"):
    width, height = _geometry(item)
    return (
        '<img src="' + _escape(_image_source(item["image"]))
        + '" alt="' + _escape(item["alt"])
        + f'" width="{width}" height="{height}"'
        + f' loading="{loading}" decoding="async">'
    )


def _text_link(label, href):
    return (
        '<a class="text-link" href="' + _escape(href) + '">'
        + _escape(label) + '<span class="arrow" aria-hidden="true">→</span></a>'
    )


def story_browser(items, ident):
    """Render every supplied story, with initially hidden enhancement controls.

    Each item uses title, official, date, category, image, alt, url, and desc.
    ``title`` is the visible editorial headline; ``official`` is its fallback.
    ``ident`` must be distinct for each browser instance on the same page.
    Optional image dimensions describe its display frame, which CSS may crop.
    An empty list returns an empty string.
    """
    items = list(items)
    if not items:
        return ""
    ident = _slug(ident, "stories")
    count = len(items)
    markup = [
        '<div class="story-browser" id="' + _escape(ident)
        + '" data-story-browser aria-label="IBSC stories">',
        '<div class="story-toolbar"><span class="story-count" data-story-count'
        + ' aria-live="polite" aria-atomic="true">'
        + str(count) + (" story" if count == 1 else " stories") + "</span>",
        '<div class="story-controls" data-story-controls hidden>',
        '<button type="button" data-story-prev aria-label="Previous story">'
        + '<span aria-hidden="true">←</span></button>',
        '<button type="button" data-story-next aria-label="Next story">'
        + '<span aria-hidden="true">→</span></button></div></div>',
    ]
    selectors = []
    for index, item in enumerate(items):
        title = str(item.get("title") or item["official"])
        panel_id = f"{ident}-story-{index}"
        title_id = panel_id + "-title"
        url = _escape(item["url"])
        markup.extend([
            '<article class="story-panel" data-story-panel data-story-title="'
            + _escape(title) + '" id="' + panel_id
            + '" aria-labelledby="' + title_id + '">',
            '<a class="story-photo-link" href="' + url
            + '" aria-label="' + _escape("Read " + title) + '">'
            + _image(item) + "</a>",
            '<div class="story-description"><div class="story-meta">'
            + _escape(item["category"]) + '<span aria-hidden="true">·</span>'
            + _escape(item["date"]) + "</div>",
            '<h3 id="' + title_id + '">' + _escape(title) + "</h3>",
            "<p>" + _escape(item["desc"]) + "</p>",
            _text_link("Read the story", item["url"]) + "</div></article>",
        ])
        selectors.append(
            '<button type="button" data-story-select="' + str(index)
            + '" aria-controls="' + panel_id + '" aria-pressed="'
            + ("true" if index == 0 else "false") + '" aria-label="'
            + _escape("Show story: " + title) + '">'
            + '<span class="story-preview-photo" aria-hidden="true">'
            + _image(dict(item, alt="")) + '</span>'
            + '<span class="story-selector-number" aria-hidden="true">'
            + str(index + 1).zfill(2) + "</span>"
            + '<span class="story-selector-date">' + _escape(item["date"]) + "</span>"
            + '<span class="story-selector-title">' + _escape(title) + "</span></button>"
        )
    # The picture rail precedes its caption; fallback articles keep normal photos.
    # Toolbar markup ends immediately before the first article.
    article_start = next(i for i, part in enumerate(markup) if part.startswith('<article'))
    return "".join(markup[:article_start]) + "".join([
        '<div class="story-selector-list" role="group" aria-label="Choose a story" hidden>',
        "".join(selectors),
        '</div><div class="story-stage">',
        "".join(markup[article_start:]),
        "</div></div>",
    ])


def student_experiences(data):
    """Render verified learning experiences as native, independently usable details.

    Records use title, dek, image, alt, caption, paragraphs, and links. Links
    are mappings with label/href. Optional points produce a list. Explicit
    record IDs are slugged and preserved; otherwise the title forms the ID.
    Duplicate IDs receive deterministic numeric suffixes within this section.
    No testimonial or narrative text is generated from missing record content.
    """
    default_intro = "Explore the learning experiences shared by the IBSC community."
    if isinstance(data, Mapping):
        items = list(data["items"])
        intro = data.get("intro", default_intro)
    else:
        items = list(data)
        intro = default_intro
    if not items:
        return ""
    markup = [
        '<section id="experiences" aria-labelledby="experiences-heading">',
        '<h2 id="experiences-heading">Learning through experience</h2>',
        '<p class="experience-intro">' + _escape(intro) + "</p>",
    ]
    used_ids = {"experiences", "experiences-heading"}
    for index, item in enumerate(items):
        fallback = "experience-" + str(index + 1)
        base_id = _slug(item.get("id") or ("experience-" + str(item["title"])), fallback)
        ident, duplicate = base_id, 2
        while ident in used_ids:
            ident = base_id + "-" + str(duplicate)
            duplicate += 1
        used_ids.add(ident)
        markup.extend([
            '<details class="experience-disclosure" data-experience id="' + ident + '">',
            '<summary><span class="experience-number" aria-hidden="true">'
            + str(index + 1).zfill(2) + "</span>",
            '<span class="experience-title">' + _escape(item["title"]) + "</span>",
            '<span class="experience-deck">' + _escape(item.get("dek", "")) + "</span>",
            '<span class="disclosure-icon" aria-hidden="true"></span></summary>',
            '<div class="experience-content"><figure>' + _image(item, loading="lazy"),
        ])
        if item.get("caption"):
            markup.append("<figcaption>" + _escape(item["caption"]) + "</figcaption>")
        markup.append('</figure><div class="experience-copy">')
        markup.extend("<p>" + _escape(paragraph) + "</p>" for paragraph in item.get("paragraphs", []))
        if item.get("points"):
            markup.append("<ul>" + "".join("<li>" + _escape(point) + "</li>" for point in item["points"]) + "</ul>")
        if item.get("links"):
            markup.append('<div class="experience-links">' + "".join(_text_link(link["label"], link["href"]) for link in item["links"]) + "</div>")
        markup.append("</div></div></details>")
    markup.append("</section>")
    return "".join(markup)
