(()=>{'use strict';
const root=new URL('./',location.href),url=path=>new URL(path,root).href;
const parts={
  1:['materials/book-parts/Barats_1893_part_I/part-000','materials/book-parts/Barats_1893_part_I/part-001','materials/book-parts/Barats_1893_part_I/part-002','materials/book-parts/Barats_1893_part_I/part-003'],
  2:['materials/book-parts/Barats_1893_part_II/part-000','materials/book-parts/Barats_1893_part_II/part-001','materials/book-parts/Barats_1893_part_II/part-002','materials/book-parts/Barats_1893_part_II/part-003'],
  3:['materials/book-parts/Barats_1893_part_III/part-000','materials/book-parts/Barats_1893_part_III/part-001','materials/book-parts/Barats_1893_part_III/part-002','materials/book-parts/Barats_1893_part_III/part-003'],
  4:['materials/book-parts/Barats_1893_part_IV/part-000','materials/book-parts/Barats_1893_part_IV/part-001','materials/book-parts/Barats_1893_part_IV/part-002','materials/book-parts/Barats_1893_part_IV/part-003']
};
const roman=['I','II','III','IV'],part=Number(document.body.dataset.bookPart)||1,frame=document.querySelector('#book-frame'),download=document.querySelector('#book-download'),open=document.querySelector('#book-open'),status=document.querySelector('#book-status');
if(!frame||!parts[part])return;
(async()=>{try{
  const responses=await Promise.all(parts[part].map(path=>fetch(url(path))));
  if(responses.some(response=>!response.ok))throw new Error('Не все части PDF доступны');
  const buffers=await Promise.all(responses.map(response=>response.arrayBuffer()));
  const objectUrl=URL.createObjectURL(new Blob(buffers,{type:'application/pdf'}));
  frame.src=objectUrl;download.href=objectUrl;open.href=objectUrl;download.download=`Barats_1893_part_${roman[part-1]}.pdf`;
  status.textContent=`Часть ${roman[part-1]} собрана из файлов репозитория и готова к просмотру.`;
}catch(error){status.textContent=`Не удалось собрать PDF: ${error.message}. Проверьте доступность файлов репозитория.`;status.classList.add('is-error')}})();
})();
