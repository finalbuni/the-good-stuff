"""Build a dependency-free static comics reader."""
from pathlib import Path
import json
import re
import shutil
from html import escape
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
EXTENSIONS = {'.webp', '.png', '.jpg', '.jpeg'}

def esc(value):
    return escape(str(value), quote=True)

def url(value):
    return quote(str(value), safe='/')

def shell(title, body, base):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · the good stuff</title><link rel="stylesheet" href="{base}assets/style.css"><script defer src="{base}assets/reader.js"></script></head><body><header class="site-header"><a class="brand" href="{base}index.html">the good stuff<span aria-hidden="true">.</span></a><span class="signature">a stash by finalbuni</span></header>{body}<footer class="footer">a little corner for a lot of reading.</footer></body></html>'''

def write(path, text):
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')

def cover(series, base):
    if series['cover']:
        return f'<img class="cover" src="{base}{url(series["cover"])}" alt="{esc(series["title"])} cover">'
    return f'<div class="cover cover-placeholder">{esc(series["title"])}</div>'

def nav(series, number):
    chapters = series['chapters']
    index = chapters.index(number)
    prev = f'<a href="../{chapters[index-1]}/index.html"><span class="desktop-label">← Previous</span><span class="mobile-label">← Prev</span></a>' if index else '<span></span>'
    if index + 1 < len(chapters):
        following = f'<a class="right" href="../{chapters[index+1]}/index.html">Next →</a>'
    else:
        label = 'End of series' if series.get('completed') else 'Next chapter unavailable'
        following = f'<span class="right disabled" role="button" aria-disabled="true">{label}</span>'
    options = ''.join(f'<option value="../{n}/index.html" {"selected" if n == number else ""}>Chapter {n}</option>' for n in chapters)
    return f'<nav class="chapter-nav" aria-label="Chapter navigation">{prev}<select data-chapters aria-label="Choose chapter">{options}</select>{following}</nav>'

def build():
    # Read and validate before replacing the previous build.
    catalog = []
    for folder in (ROOT / 'content').iterdir():
        if not folder.is_dir() or not (folder / 'series.json').exists():
            continue
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', folder.name):
            raise ValueError(f'Use a lowercase, hyphenated series folder: {folder.name}')
        series = json.loads((folder / 'series.json').read_text())
        if not isinstance(series.get('title'), str) or not series['title'].strip():
            raise ValueError(f'{folder}: title is required')
        if not re.fullmatch(r'[a-z0-9-]+', series.get('prefix', '')):
            raise ValueError(f'{folder}: lowercase image prefix is required')
        if not isinstance(series.get('completed', False), bool):
            raise ValueError(f'{folder}: completed must be true or false')
        series.update(slug=folder.name, chapters=[], panels={}, cover=None)
        for ext in ('.webp', '.jpg', '.jpeg', '.png'):
            if (folder / ('cover' + ext)).exists():
                series['cover'] = f'content/{folder.name}/cover{ext}'
                break
        chapter_root = folder / 'chapters'
        if chapter_root.exists():
            for chapter in chapter_root.iterdir():
                if not chapter.is_dir():
                    continue
                if not re.fullmatch(r'[1-9][0-9]*', chapter.name):
                    raise ValueError(f'{chapter}: use a positive chapter number without leading zeros')
                number = int(chapter.name)
                panels = []
                seen = set()
                pattern = re.compile(re.escape(series['prefix']) + rf'-ch{number}-([1-9][0-9]*)\.(webp|png|jpg|jpeg)', re.I)
                for image in chapter.iterdir():
                    if image.suffix.lower() not in EXTENSIONS:
                        continue
                    match = pattern.fullmatch(image.name)
                    if not match:
                        raise ValueError(f'{image}: expected {series["prefix"]}-ch{number}-1.webp (or another supported image extension)')
                    page = int(match[1])
                    if page in seen:
                        raise ValueError(f'{chapter}: duplicate page number {page}')
                    seen.add(page)
                    panels.append((page, image.relative_to(ROOT).as_posix()))
                series['chapters'].append(number)
                series['panels'][number] = sorted(panels)
        series['chapters'].sort()
        catalog.append(series)
    catalog.sort(key=lambda s: (s['title'].casefold(), s['slug']))
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / 'assets', OUT / 'assets')
    for series in catalog:
        slug = series['slug']
        if series['cover']:
            source = ROOT / series['cover']
            dest = OUT / series['cover']
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        chapter_links = ''.join(f'<li><a href="{n}/index.html"><span>Chapter {n}</span><span aria-hidden="true">→</span></a></li>' for n in series['chapters'])
        start = f'<a class="button" href="{series["chapters"][0]}/index.html">Start reading →</a>' if series['chapters'] else '<p class="muted">No chapters yet.</p>'
        body = f'<main class="container"><div class="series-layout">{cover(series,"../")}<section><a href="../index.html">← All series</a><h1>{esc(series["title"])}</h1><p class="muted">{len(series["chapters"])} chapters · {"Completed" if series.get("completed") else "Ongoing"}</p>{start}<ul class="chapter-list">{chapter_links}</ul></section></div></main>'
        write(f'{slug}/index.html', shell(series['title'], body, '../'))
        for number in series['chapters']:
            images = []
            for index, (page, source) in enumerate(series['panels'][number]):
                dest = OUT / source
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / source, dest)
                images.append(f'<img src="../../{url(source)}" alt="{esc(series["title"])} — Chapter {number}, page {page}" loading="{"eager" if index == 0 else "lazy"}" decoding="async">')
            panels = ''.join(images) or '<p class="notice">This chapter is ready for its panels.<br>Add images to its chapter folder and rebuild.</p>'
            body = f'<main><div class="reader-heading"><a href="../index.html">← {esc(series["title"])}</a><h1>Chapter {number}</h1></div>{nav(series,number)}<div class="panels">{panels}</div><div class="reader-bottom">{nav(series,number)}<a href="../index.html">All chapters</a></div></main>'
            write(f'{slug}/{number}/index.html', shell(f'{series["title"]} — Chapter {number}',body,'../../'))
    cards = ''.join(f'<a class="card" href="{s["slug"]}/index.html">{cover(s,"")}<h2>{esc(s["title"])}</h2><p class="muted">{len(s["chapters"])} chapters</p></a>' for s in catalog)
    write('index.html', shell('The stash', f'<main class="container"><p class="eyebrow">The personal collection</p><h1>Welcome to the stash.</h1><p class="muted">Good stories. One more chapter.</p><div class="grid">{cards}</div></main>', ''))
    write('404.html', shell('Page not found', '<main class="container"><h1>This page wandered off.</h1><a href="/the-good-stuff/">Back to the stash →</a></main>', '/the-good-stuff/'))
    print(f'Built {len(catalog)} series and {sum(len(s["chapters"]) for s in catalog)} chapters in {OUT}')

if __name__ == '__main__':
    build()
