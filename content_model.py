"""Load editorial records once; derive cards and URLs without duplicate content."""
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

CONTENT = Path(__file__).resolve().parent / 'content'


def load(name):
    return json.loads((CONTENT / name).read_text())


def collection(name, prefix, required):
    records = []
    for path in sorted((CONTENT / name).glob('*.json')):
        record = json.loads(path.read_text())
        ident = record.get('id', '')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or path.stem != ident:
            raise ValueError(f'{path.name}: id must match the filename and use lowercase words separated by hyphens')
        for field in required:
            if not record.get(field):
                raise ValueError(f'{path.name}: missing {field}')
        record['filename'] = f'{prefix}-{ident}.html'
        if record.get('image') and not (CONTENT.parent / 'dist' / 'assets' / record['image']).is_file():
            raise ValueError(f'{path.name}: image does not exist: {record["image"]}')
        records.append(record)
    return records


def news_records():
    records = collection('news', 'story', ('title', 'date', 'category', 'image', 'alt', 'intro', 'paragraphs'))
    for record in records:
        published = date.fromisoformat(record['date'])
        record['date_label'] = f'{published.strftime("%B")} {published.day}, {published.year}'
    return sorted(records, key=lambda record: (record['date'], record['id']), reverse=True)


def faculty_records():
    return sorted(collection('faculty', 'faculty', ('name', 'role', 'image', 'alt', 'intro')),
                  key=lambda record: (record.get('order', 100), record['name']))


def story_cards(records):
    return [dict(record, title=record.get('headline') or record['title'],
                 official=record['title'], date=record['date_label'],
                 url=record['filename'], desc=record.get('teaser') or record['intro'])
            for record in records]


def remove_retired_pages(dist, news, faculty):
    """Unpublishing a record also removes its old generated page and search entry."""
    active = {record['filename'] for record in news + faculty}
    for pattern in ('story-*.html', 'faculty-*.html'):
        for path in dist.glob(pattern):
            if path.name not in active:
                path.unlink()


def resolve_content_links(data, news, faculty):
    """Keep authored guide links useful when their featured record is retired.

    Resolve the in-memory render data, leaving the editor's source untouched.
    """
    active = {record['filename'] for record in news + faculty}
    def visit(value):
        if isinstance(value, dict):
            if 'href' in value:
                url = urlsplit(value['href'])
                if not url.scheme and not url.netloc and url.path not in active:
                    for prefix, destination, label in [('story-', 'news.html', 'Explore IBSC stories'), ('faculty-', 'people.html', 'Meet our faculty')]:
                        if url.path.startswith(prefix) and url.path.endswith('.html'):
                            print(f'Redirected inactive content link {url.path} to {destination}')
                            value.update(href=destination, label=label)
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
    visit(data)
    return data
