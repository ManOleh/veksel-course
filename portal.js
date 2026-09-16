(()=>{'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],key='veksel-portal-v16';
const nestedPage=/\/(?:lessons|documents)\//.test(location.pathname),siteRoot=new URL(nestedPage?'../':'./',location.href),localPath=path=>new URL(path,siteRoot).href;
let state={done:{},notes:{}};
try{const saved=localStorage.getItem(key);if(saved)state={...state,...JSON.parse(saved)};else{const old=JSON.parse(localStorage.getItem('veksel-course-progress-v15')||'null');if(old){for(let i=0;i<12;i++){if(old.notes?.[i])state.notes[i+1]=old.notes[i];if(['video','theory','notes','homework'].every(t=>old.done?.[i]?.[t]))state.done[i+1]=true}}}}catch{}
function save(){try{localStorage.setItem(key,JSON.stringify(state));return true}catch{return false}}
const lesson=Number(document.body.dataset.currentLesson||0);
function progress(){const n=Object.values(state.done).filter(Boolean).length;$$('[data-progress]').forEach(el=>el.value=n);$$('[data-progress-label]').forEach(el=>el.textContent=`${n} из 12 уроков отмечено`);const next=Array.from({length:12},(_,i)=>i+1).find(i=>!state.done[i])||12;$$('.resume-link').forEach(a=>a.href=localPath(`lessons/${String(next).padStart(2,'0')}.html`))}
progress();
const done=$('#complete-lesson');if(done){function label(){done.setAttribute('aria-pressed',String(!!state.done[lesson]));done.textContent=state.done[lesson]?'Урок пройден · снять отметку ✓':'Отметить урок пройденным ✓'}label();done.addEventListener('click',()=>{state.done[lesson]=!state.done[lesson];save();label();progress()})}
const note=$('#personal-note');if(note){note.value=state.notes[lesson]||'';note.addEventListener('input',()=>{state.notes[lesson]=note.value;$('#note-status').textContent=save()?'Сохранено в этом браузере.':'Браузер не разрешает сохранение. Скачайте заметки файлом.'});$('#export-notes').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([`Мои заметки · Урок ${lesson}\n\n${note.value}`],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`urok-${lesson}-moi-zametki.txt`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)})}
const rail=$('.lesson-rail details');if(rail&&matchMedia('(max-width:800px)').matches)rail.open=false;
const search=$('#file-search'),filter=$('#lesson-filter'),category=$('#category-filter');
if(search){const q=new URLSearchParams(location.search);filter.value=q.get('lesson')||'';category.value=q.get('category')||'';search.value=q.get('q')||'';function apply(){let n=0;const text=search.value.trim().toLocaleLowerCase('ru');$$('[data-material]').forEach(el=>{const match=(!text||el.dataset.search.includes(text))&&(!filter.value||el.dataset.lesson===filter.value)&&(!category.value||el.dataset.category===category.value);el.hidden=!match;if(match)n++});$('#result-count').textContent=`Найдено файлов: ${n}`;$('.empty-state').hidden=n!==0;const params=new URLSearchParams();if(search.value)params.set('q',search.value);if(filter.value)params.set('lesson',filter.value);if(category.value)params.set('category',category.value);history.replaceState(null,'',location.pathname+(params.size?'?'+params:''))}search.addEventListener('input',apply);filter.addEventListener('change',apply);category.addEventListener('change',apply);$('#reset-filters').addEventListener('click',()=>{search.value='';filter.value='';category.value='';apply();search.focus()});apply()}
const book=$('#book-frame');if(book){const requested=Number(new URLSearchParams(location.search).get('part')||1),part=[1,2,3,4].includes(requested)?requested:1,roman=['I','II','III','IV'][part-1];document.body.dataset.bookPart=String(part);book.title=`Курс вексельного права — часть ${roman}`;$$('[data-book-part]').forEach(a=>{if(Number(a.dataset.bookPart)===part)a.setAttribute('aria-current','page')})}
if(location.pathname===siteRoot.pathname||location.pathname.endsWith('/index.html')){const old=location.hash.match(/^#lesson-(\d+)$/);if(old&&+old[1]>=1&&+old[1]<=12)location.replace(localPath(`lessons/${old[1].padStart(2,'0')}.html`))}
// Motion enhances the existing navigation; all content remains visible without it.
const reduced=matchMedia('(prefers-reduced-motion:reduce)');
if('IntersectionObserver' in window&&!reduced.matches){
 const reveal=new IntersectionObserver(entries=>{for(const entry of entries){if(entry.isIntersecting){entry.target.classList.add('reveal-enter');reveal.unobserve(entry.target)}}},{threshold:.08});
 $$('.syllabus-group,.archive-index a,.method-grid article,.book-banner,.lesson-section').forEach(el=>reveal.observe(el));
 reduced.addEventListener('change',e=>{if(e.matches){reveal.disconnect();$$('.reveal-enter').forEach(el=>el.classList.remove('reveal-enter'))}});
}
const header=$('.header');
if(header){const bar=document.createElement('span');bar.className='reading-progress';bar.setAttribute('aria-hidden','true');header.append(bar);let scheduled=false;
 const sections=$$('.lesson-section'),tabs=$$('.section-tabs a');
 function updateReading(){scheduled=false;const max=document.documentElement.scrollHeight-innerHeight;header.style.setProperty('--read-progress',String(max>0?Math.min(1,Math.max(0,scrollY/max)):0));if(sections.length){let current=sections[0];for(const section of sections){if(section.getBoundingClientRect().top<=header.offsetHeight+90)current=section}for(const tab of tabs){const active=tab.getAttribute('href')==='#'+current.id;tab.classList.toggle('is-active',active);if(active)tab.setAttribute('aria-current','location');else tab.removeAttribute('aria-current')}}}
 function schedule(){if(!scheduled){scheduled=true;requestAnimationFrame(updateReading)}}
 addEventListener('scroll',schedule,{passive:true});addEventListener('resize',schedule);addEventListener('load',schedule);updateReading();
}
})();
