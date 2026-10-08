(() => {
  'use strict';
  const dataNode = document.getElementById('library-data');
  if (!dataNode) return;
  const {items, sections} = JSON.parse(dataNode.textContent);
  const $ = id => document.getElementById(id);
  const normal = value => String(value).normalize('NFC').toLocaleLowerCase('ru').replace(/ё/g, 'е').replace(/_/g, ' ');
  const entries = items.map(item => ({...item, search: normal([item.name, item.path, item.category, sections[item.section]].join(' '))}));
  const controls = {q: $('catalog-query'), source: $('catalog-source'), format: $('catalog-format'), lesson: $('catalog-lesson'), category: $('catalog-category')};
  const params = new URLSearchParams(location.search);
  let section = sections[params.get('section')] ? params.get('section') : '';
  let visible = 24;
  for (const [key, control] of Object.entries(controls)) control.value = params.get(key) || '';
  const sourceLabels = {course: 'Материалы курса', drive: 'Google Диск', web: 'Библиотека Животъ'};
  const dialog = $('library-reader');
  const canPreview = typeof dialog.showModal === 'function';
  let opener;

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }
  function link(label, href, external = false) {
    const node = element('a', '', label);
    node.href = href;
    if (external) { node.target = '_blank'; node.rel = 'noopener noreferrer'; }
    return node;
  }
  function row(item) {
    const article = element('article', 'catalog-row');
    article.dataset.origin = item.source;
    article.append(element('span', 'catalog-format', item.ext));
    const copy = element('div');
    const heading = element('h3');
    heading.append(link(item.title, item.url, item.source !== 'course'));
    copy.append(heading);
    copy.append(element('span', 'catalog-meta', [sections[item.section], sourceLabels[item.source], item.size].filter(Boolean).join(' · ')));
    if (item.path) copy.append(element('span', 'catalog-path', item.path));
    article.append(copy);
    const actions = element('div', 'catalog-actions');
    const action = link(item.action, item.url, item.source !== 'course');
    action.setAttribute('aria-label', `${item.action}: ${item.title}`);
    if (item.driveId && item.format !== 'archive' && canPreview) {
      action.textContent = 'Читать';
      action.setAttribute('aria-haspopup', 'dialog');
      action.addEventListener('click', event => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        opener = action;
        $('reader-title').textContent = item.title;
        $('reader-source').href = item.url;
        $('reader-frame').title = item.title;
        $('reader-frame').src = `https://drive.google.com/file/d/${item.driveId}/preview`;
        dialog.showModal();
        document.body.classList.add('reader-open');
        $('reader-close').focus();
      });
      actions.append(action, link('Google Диск', item.url, true));
    } else {
      actions.append(action);
      if (item.download) {
        const download = link('Скачать', item.download);
        download.download = '';
        download.setAttribute('aria-label', `Скачать: ${item.title}`);
        actions.append(download);
      }
    }
    article.append(actions);
    return article;
  }
  function apply(reset = true, syncUrl = true) {
    if (reset) visible = 24;
    const terms = normal(controls.q.value.trim()).split(/\s+/).filter(Boolean);
    const matches = entries.filter(item => (!section || item.section === section)
      && terms.every(term => item.search.includes(term))
      && (!controls.source.value || item.source === controls.source.value)
      && (!controls.format.value || item.format === controls.format.value)
      && (!controls.lesson.value || String(item.lesson) === controls.lesson.value)
      && (!controls.category.value || item.category === controls.category.value));
    const list = $('catalog-results');
    const fragment = document.createDocumentFragment();
    matches.slice(0, visible).forEach(item => fragment.append(row(item)));
    list.replaceChildren(fragment);
    $('catalog-heading').textContent = section ? sections[section] : 'Все материалы';
    $('catalog-count').textContent = `Найдено: ${matches.length} · показано: ${Math.min(visible, matches.length)}`;
    $('catalog-empty').hidden = matches.length !== 0;
    $('catalog-more').hidden = visible >= matches.length;
    $('catalog-more').textContent = `Показать ещё ${Math.min(24, Math.max(0, matches.length - visible))}`;
    document.querySelectorAll('[data-library-section]').forEach(a => {
      if (a.dataset.librarySection === section) a.setAttribute('aria-current', 'true');
      else a.removeAttribute('aria-current');
    });
    const description = section === 'external' || controls.source.value === 'web'
      ? 'Подборки открываются на сайте библиотеки семейно-родовой общины Животъ. Число файлов приведено на 08.10.2026.'
      : 'Названия сохранены по источникам. У каждой записи указан раздел и место хранения.';
    $('catalog-description').textContent = description;
    if (syncUrl) {
      const query = new URLSearchParams();
      if (section) query.set('section', section);
      for (const [key, control] of Object.entries(controls)) if (control.value) query.set(key, control.value);
      history.replaceState(null, '', location.pathname + (query.size ? '?' + query : '') + location.hash);
    }
  }
  document.querySelectorAll('[data-library-section]').forEach(a => a.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    section = a.dataset.librarySection;
    for (const control of Object.values(controls)) control.value = '';
    apply();
    if (matchMedia('(max-width:760px)').matches) {
      $('catalog-sections').open = false;
      $('catalog-heading').scrollIntoView({block: 'start', behavior: 'auto'});
    }
  }));
  for (const [key, control] of Object.entries(controls)) control.addEventListener(key === 'q' ? 'input' : 'change', () => apply());
  $('catalog-reset').addEventListener('click', () => {
    section = '';
    for (const control of Object.values(controls)) control.value = '';
    apply(); controls.q.focus();
  });
  $('catalog-more').addEventListener('click', () => {
    const firstNew = visible;
    visible += 24; apply(false);
    const next = $('catalog-results').children[firstNew]?.querySelector('h3 a');
    if (next) next.focus({preventScroll: true});
  });
  $('catalog-form').addEventListener('submit', event => { event.preventDefault(); apply(); });
  $('reader-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    $('reader-frame').removeAttribute('src');
    document.body.classList.remove('reader-open');
    if (opener?.isConnected) opener.focus();
  });
  window.addEventListener('popstate', () => {
    const query = new URLSearchParams(location.search);
    section = sections[query.get('section')] ? query.get('section') : '';
    for (const [key, control] of Object.entries(controls)) control.value = query.get(key) || '';
    apply(true, false);
  });
  if (matchMedia('(max-width:760px)').matches) $('catalog-sections').open = false;
  $('catalog-more').hidden = false;
  apply();
})();
