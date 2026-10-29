# Content and interaction integration

The website remains a static site; a CMS has not been connected. The homepage, faculty and news content now have canonical data records ready to map to CMS forms. This preparation does not provide staff login, editing permissions or automatic publishing yet.

## Content collections

- `content/home.json`: all main homepage copy, photographs, alt text, section labels, descriptions and action links. A newline in a display title preserves the existing intentional line break. Section composition remains in `home_components.py`.
- `content/site.json`: shared branding, primary navigation, footer links, social accounts, address, office phone and secretary details. `director_id` references a faculty record instead of duplicating its name, role or email.
- `content/news/<id>.json`: one complete article per file. Required fields are `id`, `title`, ISO `date` (`YYYY-MM-DD`), `category`, `image`, `alt`, `intro` and `paragraphs`. Optional `headline` and `teaser` are deliberately shorter card copy; omit them to use the article title and introduction everywhere. The category, date, image and alt text are shared by the cards and article. Sources, image provenance and editorial notes live in the same record. Articles sort by publication date, newest first.
- `content/faculty/<id>.json`: one complete profile per file. `name`, `role`, `intro`, `image` and `alt` are shared by the homepage, directory and profile. `featured` controls homepage inclusion and `order` controls directory order. Biographical, research and education sections are stored once under `sections`. Phone, email and office are stored once under `contact`; the contact section is generated from them. Optional `profile_link_label` changes the homepage link wording. Image provenance stays in the profile record.
- `content/core.json`: the existing main-page introductions and selected supporting copy.
- `content/resources.json`: guides rendered as information panels on their parent pages.
- `content/photography.json`: main-page cover photography, captions, cropping and provenance.
- `content/experiences.json`: student experience entries with stable IDs, title, introduction, paragraphs, photo caption and alt text, supporting links, and official provenance. These are descriptions of documented activities, not invented student testimonials.
- `content/academics.json`: learning themes, five contributing fields, grouped published course examples, and photography provenance. Groups are browsing aids, not degree requirements.
- `content/admissions-journey.json`: application routes with stable IDs, introductions, preparation steps, readiness prompts, and links to the existing admission guides and official portals. These routes provide guidance; they do not determine eligibility.

`content_model.py` reads the faculty and news collections and derives local addresses. `home_components.py`, `faculty_components.py`, `academic_components.py`, `interaction_components.py`, and `admission_journey.py` render data using the existing markup and styles. Run `python3 extend_pages.py` to regenerate the complete `dist/` output. Retain stable IDs when changing copy so bookmarks keep working. Keep headings free of unnecessary full stops; paragraphs, captions and abbreviations retain normal punctuation.

## Adding, editing and retiring records

1. Add one JSON file to the relevant collection. Its lowercase hyphenated filename must match its `id`: for example, `campus-workshop.json` with `"id": "campus-workshop"`.
2. Store its photograph in `dist/assets/` and reference the filename in `image`; supply descriptive `alt` text. Missing required fields, invalid IDs/dates and missing photographs fail the build with an error instead of silently publishing a broken card.
3. Run the full build. An article automatically gets `story-<id>.html`, card entries on the homepage and News page, related links and a search entry. A faculty record automatically gets `faculty-<id>.html` and directory/profile links, with a homepage card when `featured` is true. No Python template or second content record needs to be changed.
4. Delete the JSON record and rebuild to retire it. Its generated page and all automatically generated card, related and search entries are removed. Authored content links to an inactive `story-*.html` or `faculty-*.html` address resolve to the News or People overview with a generic label; the build reports these fallbacks. Update the authored link in its source file to point to a specific replacement if desired. External links and links outside these collections keep their authored destination.

Do not edit generated HTML or the generated search data directly. The next build replaces them. Keep the entire source checkout, content, local assets and hosting configuration together when transferring ownership.

## Remaining CMS integration work

A future CMS must supply forms for these fields, media uploads, accounts and permissions, and trigger `python3 extend_pages.py` before deploying `dist/`. No CMS, account migration or deployment automation was installed by this content refactor. Some supporting page headings and narrative copy remain in Python templates. Moving those into CMS fields, adding a section editor or introducing new page types still requires an implementation step. Existing styles, animations and responsive layouts remain in their current CSS and JavaScript files.

## Progressive enhancement

The unenhanced story browser renders every story as an article with a normal link. Experiences use native `details` and `summary`. Without JavaScript, all admissions route steps remain readable and route choices link to their full guides.

`dist/interactions.js` enhances these components through `data-story-browser`, `data-experience`, and `data-admission-journey` attributes. It validates a component before enhancing it. If a future CMS inserts new rendered components after navigation, call `window.IBSCInteractions.init()` after insertion; repeated calls are safe. Keep the renderer's complete controls, matching IDs, and data attributes together.

Hidden story and route panels are removed from keyboard navigation. Story selectors expose their pressed state and support arrow keys, Home, and End. Controls retain focus when content changes. Existing guide links continue to open their native information panels.

## Motion and performance

Motion uses short opacity and small transform transitions, plus a brief width transition on the news picture rail. There is no autoplay, scroll hijacking, video dependency, or animation framework. Content is readable before enhancements initialize. Both CSS and JavaScript respect `prefers-reduced-motion`, including a preference change while the page is open. Below-the-fold experience photographs are lazy-loaded, and image frames reserve space.

Keep the existing navy and blue palette, locally bundled Barlow Condensed and DM Sans typography, editorial spacing, and square borders when integrating a CMS. Dates, requirements, application portals, and official provenance should be maintained by IBSC editors.

Academics uses native learning and field disclosures, alongside a progressively enhanced course filter. All 13 published course entries are visible without JavaScript. `window.IBSCAcademics.init()` initializes new course browsers after CMS insertion. Preserve the course groups, stable field IDs, and the curriculum-guide placeholder. The picture rail uses the same news records as the fallback articles; its selected photograph expands and the corresponding caption changes below it.
