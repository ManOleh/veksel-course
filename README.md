# Вексельное искусство · 12 уроков

Статический учебный портал курса для GitHub Pages.

В составе репозитория:

- 12 последовательных уроков с описанием, конспектом, заданием и материалами;
- библиотека из 53 исходных файлов и 53 страниц чтения;
- четыре части курса С. М. Бараца 1893 года; крупные PDF-части разбиты на репозиторные сегменты и автоматически собираются в браузере;
- видеоархив из 12 записей с просмотром прямо на страницах уроков;
- адаптация всех внутренних ссылок для публикации по адресу `/veksel-course/`.

Видео размещены в Google Диске владельца, а сайт, документы и оформление — в репозитории. Каждая страница урока содержит встроенный плеер Google Drive и заметную кнопку «Смотреть видео в Google Диске» над ним. Прямая ссылка остаётся доступна, даже когда браузер не загружает встроенное окно. Плеер начинает загрузку сразу при открытии урока. Переход в Telegram и установка его приложения не нужны.

Сопоставление уроков с исходными файлами находится в `videos/manifest.json`. Ссылки используют постоянные ID файлов, а не временные адреса скачивания. Для обновления интерфейса после изменения манифеста: `python connect_drive_videos.py`. Видеоплеер работает без JavaScript сайта; заметки и прогресс по-прежнему сохраняются в браузере.

В папке владельца предоставлены 12 основных записей. Дополнительные записи к урокам 3 и 9 в неё не входят, поэтому неподтверждённые ссылки на них убраны. Все исходные документы сохранены.


## Library update · 2026-10-08

`library.html` now contains 432 file entries from the supplied Google Drive folder,
53 preserved course documents and links to 16 shelves of the external library at
https://19910324.com/. These are source links, not copies of the external files.
Drive documents open in an on-page reader with an always-visible original link.
Archives and the external shelves open at their source.

The catalogue supports title/path search, source, format, lesson and course-category
filters, URL query state and batches of 24 results. Source filenames and folders are
retained in `library-catalog.json`; shelf metadata lives in `library-sources.json`.
The inventory is a dated snapshot, not a live feed. No credentials are shipped.

`build_library.py` builds the library and two text-only supplemental lessons from
the user-provided passages. It is called by `connect_drive_videos.py` after the
12 video pages are processed, and can also be run directly. Main lesson IDs and
progress tracking remain 1–12. Existing course files and video IDs are unchanged.
