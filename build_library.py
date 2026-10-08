"""Build the source-attributed library and two supplied text supplements.

The Drive catalogue is a complete metadata snapshot of the supplied folder.
Books stay at their original sources; no credentials or API calls ship to visitors.
Run after the course/video generator. Safe to run repeatedly on either host.
"""
import html
import json
import re
from pathlib import Path

SECTIONS = {
    'exchange': 'Вексельное право · Барац',
    'course': 'Документы 12 уроков',
    'roman': 'Римское право',
    'trusts': 'Трасты',
    'poor': 'Poor Laws · Cestui Que Vie',
    'canons': 'Каноны · UCADIA',
    'forms': 'UCC · формы и руководства',
    'registration': 'Регистрация и свидетельства',
    'federal': 'Federal Reserve Act',
    'books': 'Книги и словари',
    'other': 'Другие источники',
    'external': 'Библиотека Животъ',
}
DRIVE_SECTIONS = {
    '1ZD-a4AJZ-eACgXXn71PaQJMd3v8wUuAI': 'exchange',
    '14mPvE1R1gz5ZqGsfvL0fu1mQPgmaZUEs': 'roman',
    '10MvAZcHe4cX6yunle1H77sicqYss8D72': 'trusts',
    '1uMDJ1W4AhQMoAidz06Pd85W70Br2hI7f': 'poor',
    '1tgcY633BXC_IDzQzbh0plsO73dSDLcRS': 'canons',
    '14VIrr9_vtDBgenPRSBuTbmxYbn7j6sk9': 'forms',
    '1gxij8Rk389IIgMmYLqSelPcWH31aF7hI': 'registration',
    '1SquP-eU2yET3uYURlKq7UVKSPZNmUq2g': 'federal',
    '1aBHKdmjPMxv0or6WOy6Q73_m3JR5A3N8': 'books',
}
SUPPLEMENTS = [
    ('supplement-01', 'Передача документа и приложений', 'ВАЖНО', 'Ваш (сайт) документ и все что прилагается к документу чеки, квитанции и другое передается на обороте чего-то например на обороте документа на основании которого возникло право требования.'),
    ('supplement-02', 'Формула успеха переводного векселя', '73 62 15 48', 'Дух, частица Творца. У кого есть дух, тот и есть Творец. Пусть начинающий. Благодарю за внимание.'),
]
e = lambda value: html.escape(str(value), quote=True)

def category(material):
    name = material['name'].lower()
    if 'конспект' in name or 'konspekt' in name: return 'Конспекты'
    if 'описан' in name or 'opisanie' in name: return 'Описание и задания'
    if 'задан' in name: return 'Домашние задания'
    if material['type'] in ['PNG', 'JPG', 'JPEG']: return 'Схемы и изображения'
    return 'Документы'

def format_of(ext):
    if ext == 'PDF': return 'pdf'
    if ext in ['DOC', 'DOCX', 'RTF', 'TXT']: return 'word'
    if ext in ['PNG', 'JPG', 'JPEG', 'WEBP']: return 'image'
    if ext in ['ZIP', 'RAR', '7Z']: return 'archive'
    return 'word'

def display_title(name):
    return re.sub(r'\.(pdf|docx?|rtf|png|jpe?g|rar|zip)$', '', name, flags=re.I).replace('_', ' ').strip()

def size_label(size):
    if size is None: return ''
    return (f'{size / 1024 / 1024:.1f} МБ' if size >= 1024*1024 else f'{max(1, round(size / 1024))} КБ').replace('.', ',')

def chrome(root, title, body, nested=False, library=False):
    template = (root / 'index.html').read_text()
    head = template.split('<body', 1)[0]
    head = re.sub(r'<title>.*?</title>', '<title>'+e(title)+' · Вексельное искусство</title>', head)
    description = 'Библиотека вексельного права: книги, документы курса, источники Google Диска и тематические подборки.' if library else 'Дополнительный текстовый урок авторского курса «Вексельное искусство».'
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(description)}">', head)
    head = re.sub(r'<link[^>]*href="[^"]*library\.css[^>]*>', '', head)
    head = re.sub(r'<script[^>]*src="[^"]*library\.js[^>]*></script>', '', head)
    head = head.replace('</head>', '<link rel="stylesheet" href="./library.css?v=20261008">'+ ('<script src="./library.js?v=20261008" defer></script>' if library else '')+'</head>')
    header = re.search(r'<header class="header">.*?</header>', template, re.S)[0]
    header = re.sub(r' aria-current="[^"]*"', '', header)
    if library: header = re.sub(r'(<a href="[^"]*library.html")', r'\1 aria-current="page"', header)
    header = header.replace('>12 уроков</a>', '>Программа</a>')
    footer = re.search(r'<footer>.*?</footer>', template, re.S)[0]
    footer = footer.replace('Авторский учебный курс · 12 уроков', '12 основных уроков · 2 дополнительных текста')
    prefix = '../' if nested else './'
    def urls(text):
        return re.sub(r'((?:href|src)=")(/|\./)(?!/)', lambda m: m[1]+prefix, text)
    return urls(head) + '<body><a class="skip" href="#main">К содержанию</a>'+urls(header)+'<main id="main">'+body+'</main>'+urls(footer)+'</body></html>'

def supplements(prefix='./'):
    cards = ''.join(f'<a href="{prefix}lessons/{slug}.html"><small>ДОПОЛНИТЕЛЬНЫЙ УРОК {i:02} · ТЕКСТ</small><h3>{e(title)}</h3><p>{e(label)}</p></a>' for i, (slug, title, label, _) in enumerate(SUPPLEMENTS, 1))
    return '<!-- supplements:start --><section class="supplement-strip" id="supplements"><span class="eyebrow">Дополнение к основной программе</span><h2>Два авторских текста</h2><div class="supplement-cards">'+cards+'</div></section><!-- supplements:end -->'

def initial_row(item):
    external = ' target="_blank" rel="noopener noreferrer"' if item['source'] != 'course' else ''
    source = {'course':'Материалы курса','drive':'Google Диск','web':'Библиотека Животъ'}[item['source']]
    meta = ' · '.join(filter(None, [SECTIONS[item['section']], source, item['size']]))
    path = '<span class="catalog-path">'+e(item['path'])+'</span>' if item['path'] else ''
    download = f'<a href="{e(item["download"])}" download>Скачать</a>' if item.get('download') else ''
    return f'<article class="catalog-row" data-origin="{item["source"]}"><span class="catalog-format">{e(item["ext"])}</span><div><h3><a href="{e(item["url"])}"{external}>{e(item["title"])}</a></h3><span class="catalog-meta">{e(meta)}</span>{path}</div><div class="catalog-actions"><a href="{e(item["url"])}"{external}>{item["action"]}</a>{download}</div></article>'

def build(root):
    root = Path(root)
    drive = json.loads((root/'library-catalog.json').read_text())
    website = json.loads((root/'library-sources.json').read_text())
    raw = (root/'course-data.js').read_text()
    lessons = json.loads(raw[raw.index('['):].strip().rstrip(';'))
    items = []
    for file in drive['files']:
        assert re.fullmatch(r'[A-Za-z0-9_-]+', file['id'])
        ext = file['name'].rsplit('.', 1)[-1].upper()
        items.append(dict(id=file['id'], driveId=file['id'], name=file['name'], title=display_title(file['name']), ext=ext, format=format_of(ext), source='drive', section=DRIVE_SECTIONS.get(file['section'], 'other'), path=' / '.join(file['path'][1:]), size=size_label(file['bytes']), url='https://drive.google.com/file/d/'+file['id']+'/view', action='Открыть архив' if format_of(ext)=='archive' else 'Открыть'))
    for lesson in lessons:
        for i, file in enumerate(lesson['materials'], 1):
            items.append(dict(id=f'course-{lesson["id"]}-{i}', name=file['name'], title=display_title(file['name']), ext=file['type'], format=format_of(file['type']), source='course', section='course', category=category(file), lesson=lesson['id'], path=f'Урок {lesson["id"]:02} · '+category(file), size=f'{file["size"]} КБ', url=f'./documents/{lesson["id"]:02}-{i:02}.html', download='./'+file['href'].lstrip('/'), action='Читать'))
    for shelf in website['shelves']:
        items.append(dict(id=shelf['id'], name=shelf['title'], title=shelf['title'].replace('_',' '), ext='ПОЛКА', format='collection', source='web', section='external', path='Библиотека семейно-родовой общины Животъ · 19910324.com', size=f'{shelf["fileCount"]} файлов', url=shelf['url'], action='Открыть полку'))
    order = list(SECTIONS)
    items.sort(key=lambda x: (order.index(x['section']), x['name'].casefold()))
    counts = {key:sum(item['section']==key for item in items) for key in SECTIONS}
    nav = '<a href="./library.html" data-library-section="" aria-current="true"><span>Всё собрание</span><span>'+str(len(items))+'</span></a>'
    nav += ''.join(f'<a href="./library.html?section={key}" data-library-section="{key}"'+(' class="rail-source"' if key=='external' else '')+f'><span>{e(title)}</span><span>{counts[key]}</span></a>' for key, title in SECTIONS.items())
    options = ''.join(f'<option value="{i}">Урок {i:02}</option>' for i in range(1,13))
    categories = ''.join(f'<option>{e(c)}</option>' for c in ['Документы','Конспекты','Схемы и изображения','Описание и задания','Домашние задания'])
    serialized = json.dumps({'items':items,'sections':SECTIONS}, ensure_ascii=False, separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    body = f'''<div class="library-board"><div class="library-masthead"><div><span class="eyebrow">Вексельное искусство / собрание источников</span><h1>Библиотека познания</h1><p>Книги, документы и авторские материалы. От вексельного права — к истории, языку и источникам.</p></div><div class="library-stamp">РЕЕСТР СОБРАНИЯ<strong>{len(drive['files']) + counts['course']} файлов</strong>{len(website['shelves'])} внешних подборок</div></div>
<nav class="library-links" aria-label="Источники библиотеки"><a href="./book.html">С. М. Барац · издание 1893 года</a><a href="{drive['source']}" target="_blank" rel="noopener noreferrer">Исходная папка Google Диска</a><a href="{website['source']}" target="_blank" rel="noopener noreferrer">Библиотека общины Животъ</a><a href="./videos/index.html">12 видеоуроков</a></nav>
<div class="catalog-layout"><aside class="catalog-rail"><details id="catalog-sections" open><summary>Разделы собрания</summary><nav aria-label="Разделы библиотеки">{nav}</nav></details><p class="catalog-rail-note">432 файла Google Диска<br>53 документа курса<br>16 тематических полок</p></aside>
<section class="catalog-workspace" aria-label="Каталог материалов"><form id="catalog-form" class="catalog-controls" role="search"><label class="catalog-search">Найти в библиотеке<input id="catalog-query" name="q" type="search" placeholder="Название, автор или тема" autocomplete="off"></label><label>Источник<select id="catalog-source" name="source"><option value="">Все источники</option><option value="course">Материалы курса</option><option value="drive">Google Диск</option><option value="web">Библиотека Животъ</option></select></label><label>Формат<select id="catalog-format" name="format"><option value="">Все форматы</option><option value="pdf">PDF</option><option value="word">DOC / DOCX / RTF</option><option value="image">Изображения</option><option value="archive">Архивы ZIP / RAR</option><option value="collection">Внешние подборки</option></select></label><label>Урок<select id="catalog-lesson" name="lesson"><option value="">Все материалы</option>{options}</select></label><label>Материалы уроков<select id="catalog-category" name="category"><option value="">Все виды</option>{categories}</select></label></form>
<div class="catalog-context"><div><h2 id="catalog-heading" tabindex="-1">Все материалы</h2><p id="catalog-count" role="status" aria-live="polite">{len(items)} записей в каталоге</p></div><button class="catalog-reset" id="catalog-reset" type="button">Сбросить фильтры</button></div><p class="catalog-description" id="catalog-description">Названия сохранены по источникам. У каждой записи указан раздел и место хранения.</p>
<div id="catalog-results">{''.join(initial_row(item) for item in items[:24])}</div><div class="catalog-empty" id="catalog-empty" hidden><h3>Материалы не найдены</h3><p>Измените запрос или сбросьте фильтры.</p></div><button class="catalog-more" id="catalog-more" type="button" hidden>Показать ещё 24</button>
<noscript><p>Для поиска и просмотра полного каталога включите JavaScript. Все оригиналы также доступны в <a href="{drive['source']}">папке Google Диска</a> и <a href="{website['source']}">библиотеке Животъ</a>.</p></noscript>
<p class="catalog-endnote">В собрании представлены исторические издания, учебные тексты, переводы и авторские трактовки. Состав каталога зафиксирован 08.10.2026.</p></section></div>{supplements()}
</div><dialog id="library-reader" class="library-dialog" aria-labelledby="reader-title"><div class="reader-toolbar"><h2 id="reader-title">Просмотр документа</h2><button id="reader-close" type="button">Закрыть</button></div><p class="reader-fallback">Если просмотр не загрузился, <a id="reader-source" target="_blank" rel="noopener noreferrer">откройте оригинал в Google Диске</a>.</p><iframe id="reader-frame" title="Просмотр документа Google Диска" allow="fullscreen" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></dialog>
<script type="application/json" id="library-data">{serialized}</script>'''
    (root/'library.html').write_text(chrome(root, 'Библиотека познания', body, library=True))
    for i, (slug, title, label, text) in enumerate(SUPPLEMENTS, 1):
        emphasis = f'<strong class="formula">{label}</strong>' if i==2 else '<strong>ВАЖНО</strong><br>'
        other = SUPPLEMENTS[1 if i==1 else 0]
        content = f'<article class="supplement-page"><a class="text-link" href="../program.html#supplements">Дополнительные уроки</a><span class="eyebrow">Дополнительный урок {i:02} / текст автора</span><h1>{e(title)}</h1><blockquote>{emphasis}<p>{e(text)}</p></blockquote><p class="supplement-caption">Авторский текст, предоставленный для дополнения курса.</p><nav class="supplement-nav" aria-label="Навигация по дополнительным урокам"><a href="./{other[0]}.html">{e(other[1])}</a><a href="../library.html">Библиотека познания</a></nav></article>'
        (root/'lessons'/f'{slug}.html').write_text(chrome(root, title, content, nested=True))
    # Integrate into established routes, without changing lesson IDs or progress.
    for name in ['index.html','program.html']:
        path = root/name
        text = path.read_text()
        text = re.sub(r'<!-- supplemental-links:start -->.*?<!-- supplemental-links:end -->', '', text, flags=re.S)
        block = '<!-- supplemental-links:start -->'+supplements()+'<!-- supplemental-links:end -->'
        assert '</div></main>' in text, f'Expected content wrapper in {name}'
        text = text.replace('</div></main>', block+'</div></main>')
        if 'library.css' not in text: text = text.replace('</head>','<link rel="stylesheet" href="./library.css?v=20261008"></head>')
        text = text.replace('>12 уроков</a>', '>Программа</a>').replace('Открыть приложения</a>', 'Библиотека познания</a>')
        text = text.replace('53 файла · открыть реестр ↗', '485 файлов · 16 подборок')
        text = text.replace('Конвенции, декларации, схемы, конспекты и задания.', 'Книги Бараца, документы курса и собрание источников Google Диска.')
        (root/name).write_text(text)
    print(f'Library: {len(drive["files"])} Drive files, {counts["course"]} course files, {len(website["shelves"])} external shelves; 2 supplements.')

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parent
    p.add_argument('root', nargs='?', type=Path, default=base/'dist' if (base/'dist').is_dir() else base)
    build(p.parse_args().root)
