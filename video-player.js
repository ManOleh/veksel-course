(() => {
  'use strict';

  const script = document.currentScript;
  const nestedPage = /\/(?:lessons|documents|videos)\//.test(location.pathname);
  const siteRoot = new URL(script?.dataset.siteRoot || (nestedPage ? '../' : './'), location.href);
  const localFile = (file) => new URL(file, siteRoot).href;
  const typeFor = (file) => file.toLowerCase().endsWith('.webm') ? 'video/webm' : 'video/mp4';

  async function exists(url) {
    try {
      const response = await fetch(url, { method: 'HEAD', cache: 'no-store' });
      return response.ok;
    } catch {
      return false;
    }
  }

  function missing(slot, label, url) {
    slot.innerHTML = `<div class="video-pending"><span class="file-type">GITHUB VIDEO</span><h3>Видео-файл ещё не добавлен</h3><p>${label} подготовлено для локального воспроизведения. Добавьте файл по адресу <code>${url.pathname}</code>, и плеер появится автоматически.</p><span class="video-pending-note">Внешние ссылки на Telegram здесь не используются.</span></div>`;
  }

  async function mount(slot) {
    const relativeFile = slot.dataset.localVideo;
    const label = slot.dataset.videoLabel || 'Запись урока';
    if (!relativeFile) return;
    const url = new URL(relativeFile, siteRoot);
    if (!(await exists(url))) {
      missing(slot, label, url);
      return;
    }
    const video = document.createElement('video');
    video.className = 'course-video';
    video.controls = true;
    video.preload = 'metadata';
    video.playsInline = true;
    video.setAttribute('aria-label', label);
    video.poster = localFile('evening-study.png');
    const source = document.createElement('source');
    source.src = url.href;
    source.type = typeFor(relativeFile);
    video.append(source);
    const actions = document.createElement('div');
    actions.className = 'video-file-actions';
    actions.innerHTML = `<a class="text-link" href="${url.href}" download>Скачать файл видео ↓</a>`;
    slot.replaceChildren(video, actions);
  }

  document.querySelectorAll('[data-local-video]').forEach((slot) => { mount(slot); });
})();
