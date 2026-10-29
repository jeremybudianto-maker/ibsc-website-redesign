"""Exercise staff-style content changes in isolated copies of the website."""
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.duplicates, self.links, self.headings = set(), [], [], []
        self.heading = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.duplicates.append(attrs['id'])
            self.ids.add(attrs['id'])
        attribute = 'href' if tag in ('a', 'link') else 'src' if tag in ('img', 'script') else None
        if attribute and attribute in attrs:
            self.links.append(attrs[attribute])
        if re.fullmatch('h[1-6]', tag):
            self.heading = ''

    def handle_data(self, data):
        if self.heading is not None:
            self.heading += data

    def handle_endtag(self, tag):
        if re.fullmatch('h[1-6]', tag) and self.heading is not None:
            self.headings.append(self.heading)
            self.heading = None


class ContentBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ibsc-content-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'site'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__', 'tests'))
        self.dist = self.root / 'dist'

    def edit(self, filename, **changes):
        path = self.root / 'content' / filename
        record = json.loads(path.read_text())
        record.update(changes)
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
        return record

    def build(self, succeeds=True):
        result = subprocess.run([sys.executable, 'extend_pages.py'], cwd=self.root, capture_output=True, text=True)
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def text(self, filename):
        return (self.dist / filename).read_text()

    def search(self):
        return json.loads(re.search(r'const searchData = (\[.*?\]);', self.text('app.js'), re.S)[1])

    def assert_links_work(self):
        documents = {p.name: Document(p.read_text()) for p in self.dist.glob('*.html')}
        for name, document in documents.items():
            self.assertFalse(document.duplicates, (name, document.duplicates))
            for value in document.links:
                url = urlsplit(value)
                if url.scheme or url.netloc:
                    continue
                target = unquote(url.path) or name
                self.assertTrue((self.dist / target).exists(), (name, value))
                if url.fragment and target.endswith('.html'):
                    self.assertIn(unquote(url.fragment), documents[target].ids, (name, value))

    def test_current_site_has_working_links_and_clean_headings(self):
        self.build()
        self.assert_links_work()
        for path in self.dist.glob('*.html'):
            for heading in Document(path.read_text()).headings:
                self.assertFalse(heading.rstrip().endswith('.'), (path.name, heading))
        self.assertIn('Learn to connect people, cultures, and ideas.', self.text('index.html'))
        self.assertIn('Ph.D.', self.text('faculty-carlos-hernandez.html'))

    def test_homepage_copy_images_and_actions_are_data_driven(self):
        path = self.root / 'content/home.json'
        home = json.loads(path.read_text())
        home['hero'].update(title='Edited headline\nSecond line', image='community.jpg', alt='Updated homepage photograph')
        home['hero']['action'] = {'label': 'Meet our community', 'href': 'people.html'}
        home['admissions']['description'] = 'An updated introduction from the program office.'
        path.write_text(json.dumps(home))
        self.build()
        output = self.text('index.html')
        self.assertIn('Edited headline<br>Second line', output)
        self.assertIn('class="hero-img" src="assets/community.jpg"', output)
        self.assertIn('alt="Updated homepage photograph"', output)
        self.assertIn('Meet our community', output)
        self.assertIn(home['admissions']['description'], output)
        self.assert_links_work()

    def test_one_faculty_edit_updates_every_appearance(self):
        self.edit('faculty/carlos-hernandez.json', name='Updated faculty name', role='Updated faculty role',
                  intro='Updated faculty introduction.', image='robert-johanson.jpg', alt='Updated portrait')
        self.build()
        for filename in ('index.html', 'people.html', 'faculty-carlos-hernandez.html'):
            output = self.text(filename)
            for value in ('Updated faculty name', 'Updated faculty role', 'Updated faculty introduction.', 'assets/robert-johanson.jpg', 'Updated portrait'):
                self.assertIn(value, output, filename)
            self.assertNotIn('<h1>Carlos Hernández Mercado</h1>', output)
            if filename != 'faculty-carlos-hernandez.html':
                self.assertNotIn('Carlos Hernández Mercado', output)
        self.assertTrue(any(entry['title'] == 'Updated faculty name' for entry in self.search()))

    def test_new_article_needs_only_one_record_and_search_preserves_escapes(self):
        record = {
            'id': 'new-workshop', 'title': 'Workshop <questions> & answers', 'date': '2026-10-10',
            'category': 'Announcements', 'image': 'news-glory.jpg', 'alt': 'Workshop photograph',
            'intro': 'First line\nA quoted "answer" and a literal \\n.',
            'paragraphs': ['A complete announcement from the program office.']
        }
        (self.root / 'content/news/new-workshop.json').write_text(json.dumps(record))
        self.build()
        for filename in ('index.html', 'news.html', 'story-new-workshop.html'):
            self.assertIn(html.escape(record['title']), self.text(filename), filename)
        self.assertIn('href="story-new-workshop.html"', self.text('story-night-of-glory.html'))
        entry = next(entry for entry in self.search() if entry['url'] == 'story-new-workshop.html')
        self.assertEqual(entry['text'], record['intro'])
        self.assert_links_work()

    def test_retiring_records_removes_their_pages_cards_and_search_entries(self):
        (self.root / 'content/news/international-pizza.json').unlink()
        (self.root / 'content/faculty/carlos-hernandez.json').unlink()
        self.build()
        retired = ('story-international-pizza.html', 'faculty-carlos-hernandez.html')
        for filename in retired:
            self.assertFalse((self.dist / filename).exists())
            self.assertFalse(any(entry['url'] == filename for entry in self.search()))
            for page in self.dist.glob('*.html'):
                self.assertNotIn('href="'+filename+'"', page.read_text(), page.name)
        self.assert_links_work()

    def test_invalid_record_fails_before_replacing_existing_output(self):
        before = {str(p.relative_to(self.dist)): p.read_bytes() for p in self.dist.rglob('*') if p.is_file()}
        self.edit('news/creative-industry.json', image='missing-picture.jpg')
        result = self.build(succeeds=False)
        self.assertIn('image does not exist', result.stderr)
        after = {str(p.relative_to(self.dist)): p.read_bytes() for p in self.dist.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_directory_still_works_with_fewer_than_four_profiles(self):
        for path in (self.root / 'content/faculty').glob('*.json'):
            if path.stem != 'ching-pu-chen':
                path.unlink()
        self.edit('faculty/ching-pu-chen.json', name='Updated director')
        self.build()
        self.assertIn('Updated director', self.text('people.html'))
        self.assertIn('Updated director', self.text('about.html'))
        self.assertEqual(self.text('people.html').count('<article class="faculty-card">'), 1)
        self.assert_links_work()


if __name__ == '__main__':
    unittest.main()
