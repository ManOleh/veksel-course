"""Connect the owner's 12 Drive recordings to either static course edition.

Run after build-portal.py, or pass the GitHub Pages root as an argument.
Only the video interface and navigation change; original documents are retained.
"""
import argparse
import html
import json
from pathlib import Path
import re


def escape(value):
    return html.escape(str(value), quote=True)


def video_section(lesson):
    n = lesson['id']
    return f'''<section id="video" class="lesson-section">
<div class="section-line"><span>01 / Видеоурок</span><span>Урок {n:02} из 12</span></div>
<div class="drive-watch">
  <div class="drive-watch-heading"><span class="eyebrow">Запись занятия</span><h2>{escape(lesson['short_title'])}</h2><p>Нажмите ▶ в плеере, чтобы начать просмотр.</p></div>
  <div class="drive-frame"><iframe src="{escape(lesson['embed_url'])}" title="Урок {n:02} — {escape(lesson['title'])}" loading="lazy" allow="autoplay; encrypted-media; fullscreen; picture-in-picture" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></div>
  <div class="drive-watch-tools"><span>Видео · Google Диск</span><a href="{escape(lesson['view_url'])}" target="_blank" rel="noopener noreferrer" aria-label="Открыть видео урока {n} отдельно в Google Диске">Открыть видео отдельно ↗</a></div>
  <p class="drive-help">Если плеер не загрузился, откройте запись отдельно по ссылке выше.</p>
</div></section>'''


def archive_page(template, lessons):
    before, remainder = template.split('<main id="main">', 1)
    _, after = remainder.split('</main>', 1)
    before = re.sub(r'<title>.*?</title>', '<title>Все 12 видео · Вексельное искусство</title>', before)
    before = re.sub(r'<body[^>]*>', '<body class="video-collection-page">', before)
    before = before.replace(' aria-current="page"', '')
    before = before.replace('href="../videos/index.html">Видео</a>', 'href="../videos/index.html" aria-current="page">Видео</a>')
    before = before.replace('href="/videos/index.html">Видео</a>', 'href="/videos/index.html" aria-current="page">Видео</a>')
    # Root-relative links in the GPT edition become portable on the archive page.
    before = re.sub(r'((?:href|src)=")/(?!/)', r'\1../', before)
    after = re.sub(r'((?:href|src)=")/(?!/)', r'\1../', after)
    groups = [('01—04', 'Язык и основа', 'От первого знакомства — к структуре документа.'),
              ('05—08', 'Работа с документом', 'Надписи, оплата, протест и почтовое отправление.'),
              ('09—12', 'Практика и завершение', 'Комплекты документов и итоговый разбор.')]
    sections = []
    for index, (span, title, description) in enumerate(groups):
        cards = []
        for lesson in lessons[index * 4:(index + 1) * 4]:
            n = lesson['id']
            cards.append(f'''<article class="recording-card">
<a class="recording-link" href="../lessons/{n:02}.html#video" aria-label="Смотреть урок {n}: {escape(lesson['title'])}">
  <div class="recording-cover"><span class="recording-number">{n:02}</span><span class="recording-play" aria-hidden="true">▶</span><span class="recording-label">ВЕКСЕЛЬНОЕ ИСКУССТВО / УРОК {n:02}</span></div>
  <div class="recording-copy"><span class="eyebrow">Урок {n:02}</span><h3>{escape(lesson['title'])}</h3><span class="recording-action">Смотреть на сайте <span aria-hidden="true">→</span></span></div>
</a><a class="recording-external" href="{escape(lesson['view_url'])}" target="_blank" rel="noopener noreferrer" aria-label="Открыть урок {n} в Google Диске">Открыть в Google Диске ↗</a></article>''')
        sections.append(f'<section class="recording-group" aria-labelledby="group-{index}"><div class="recording-group-heading"><span>{span}</span><div><h2 id="group-{index}">{title}</h2><p>{description}</p></div></div><div class="recording-grid">'+''.join(cards)+'</div></section>')
    body = '''<div class="wrap video-collection">
<div class="breadcrumbs"><a href="../">Главная</a><span>/</span>Все видео</div>
<section class="collection-hero"><div><span class="eyebrow">Авторская программа · видеособрание</span><h1>Двенадцать уроков.<br><em>Один путь изучения.</em></h1><p class="lead">Выберите занятие и смотрите запись прямо на странице урока. Конспекты, задания и документы — рядом с плеером.</p><a class="button" href="../lessons/01.html#video">Смотреть первый урок →</a></div><div class="collection-seal" aria-label="12 видеозаписей курса"><span>ПОЛНОЕ СОБРАНИЕ</span><strong>12</strong><span>ЗАПИСЕЙ КУРСА</span><p>Просмотр на сайте<br>Видео с Google Диска</p></div></section>
<div class="collection-index"><span>РЕЕСТР ВИДЕОЗАПИСЕЙ · 01—12</span><a href="../program.html">Программа и мой прогресс ↗</a></div>
'''+''.join(sections)+'''
<div class="collection-help"><h2>Продолжайте с материалами</h2><p>У каждого урока есть своя страница с документами и местом для личных заметок.</p><a class="text-link" href="../library.html">Открыть библиотеку · 53 файла ↗</a></div></div>'''
    return before+'<main id="main">'+body+'</main>'+after


def connect(root):
    root = Path(root)
    manifest = json.loads((root / 'videos/manifest.json').read_text())
    lessons = manifest['lessons']
    assert [lesson['id'] for lesson in lessons] == list(range(1, 13)), 'Expected 12 ordered recordings'
    for lesson in lessons:
        assert re.fullmatch(r'[A-Za-z0-9_-]+', lesson['drive_id']), 'Invalid Drive file ID'
        base = 'https://drive.google.com/file/d/'+lesson['drive_id']
        assert lesson['embed_url'] == base+'/preview'
        assert lesson['view_url'] == base+'/view'

    catalogue = root / 'course-data.js'
    raw = catalogue.read_text()
    data = json.loads(raw[raw.index('['):].strip().rstrip(';'))
    for item in data:
        lesson = lessons[item['id']-1]
        item['video_url'] = lesson['view_url']
        item['video_embed_url'] = lesson['embed_url']
        item['video_drive_id'] = lesson['drive_id']
        item.pop('extra', None)  # The supplied folder contains exactly 12 main recordings.
    catalogue.write_text(raw[:raw.index('[')]+json.dumps(data, ensure_ascii=False, separators=(',', ':'))+';\n')

    for page in root.rglob('*.html'):
        if page == root / 'videos/index.html':
            continue
        relative_root = '../' * len(page.relative_to(root).parts[:-1]) or './'
        text = page.read_text()
        text = re.sub(r'<script\b[^>]*src="[^"]*video-player\.js"[^>]*></script>', '', text)
        # The header CTA always opens the video collection on this site.
        text = re.sub(r'<a class="header-(?:tg|video)"[^>]*>.*?</a>', f'<a class="header-video" href="{relative_root}videos/index.html">Все видео ↗</a>', text)
        nav = re.search(r'<nav aria-label="Главная навигация">(.*?)</nav>', text)
        if nav and 'videos/index.html' not in nav[1]:
            text = text.replace(nav[0], nav[0].replace('</nav>', f'<a href="{relative_root}videos/index.html">Видео</a></nav>'))
        text = text.replace(' · дополнительное видео', '')
        text = text.replace('Комплект документов для близких и дополнительное видео о сшивании.', 'Комплект документов для близких и разбор их оформления.')
        if page.parent.name == 'lessons' and page.stem.isdigit():
            lesson = lessons[int(page.stem)-1]
            text, count = re.subn(r'<section id="video".*?</section>', video_section(lesson), text, count=1, flags=re.S)
            assert count == 1, f'Video section missing in {page}'
            if 'drive-video.css' not in text:
                text = text.replace('</head>', f'<link rel="stylesheet" href="{relative_root}drive-video.css"></head>')
        if page.name == 'sales.html':
            text = re.sub(r'<a([^>]*?)href="https://t\.me/[^"]*"([^>]*)>.*?</a>', f'<a class="button" href="{relative_root}videos/index.html">Открыть все видео ↗</a>', text)
            text = re.sub(r'<span class="sales-footnote">.*?</span>', '<span class="sales-footnote">Все 12 записей доступны на страницах уроков через плеер Google Диска.</span>', text)
            text = text.replace('Основные записи и два дополнительных видео доступны по прямым ссылкам на сообщения автора.', 'Все 12 записей открываются во встроенном плеере на страницах уроков. Можно также открыть видео отдельно в Google Диске.')
            text = re.sub(r'(<details><summary>Где смотреть видео\?</summary>)<p>.*?</p>', r'\1<p>Прямо на странице нужного урока: нажмите кнопку воспроизведения. Под плеером есть ссылка для открытия записи отдельно в Google Диске.</p>', text)
            text = re.sub(r'<details><summary>Как узнать стоимость и условия участия\?</summary><p>.*?</p></details>', '<details><summary>Что делать, если плеер не загрузился?</summary><p>Нажмите «Открыть видео отдельно» под плеером. Запись откроется в Google Диске в новой вкладке.</p></details>', text)
        if text != page.read_text():
            page.write_text(text)

    # Keep the current portal styles and the legacy script consistent with the new links.
    styles = root / 'portal.css'
    styles.write_text(styles.read_text().replace('.header-tg', '.header-video'))
    legacy = root / 'theme.js'
    if legacy.exists():
        text = re.sub(r'Смотрѣть лекцію въ (?:GitHub|Telegram)', 'Смотрѣть лекцію въ Google Дискѣ', legacy.read_text())
        legacy.write_text(text)
    obsolete = root / 'video-player.js'
    if obsolete.exists():
        obsolete.unlink()
    template = (root / 'lessons/01.html').read_text()
    (root / 'videos/index.html').write_text(archive_page(template, lessons))
    print(f'{root}: connected {len(lessons)} Drive players and video collection')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(__file__).resolve().parent
    parser.add_argument('root', nargs='?', type=Path, default=default/'dist' if (default/'dist').is_dir() else default)
    connect(parser.parse_args().root)
