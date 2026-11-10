/* SHIVAS item pages: theme switch, photo and 3D model galleries (from assets/library.js), line-up previews and the all-products filters. */
(function(){
 var r=document.documentElement;
 // ---- theme ----
 var tb=document.getElementById('thm');
 var SUN='<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
 var MOON='<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>';
 function dark(){return r.getAttribute('data-theme')==='dark'}
 function sync(){if(!tb)return;var d=dark();tb.innerHTML=d?SUN:MOON;tb.setAttribute('aria-label',d?'Switch to light mode':'Switch to dark mode')}
 if(tb){tb.addEventListener('click',function(){var nd=!dark();r.setAttribute('data-theme',nd?'dark':'light');try{localStorage.setItem('shivas.mode',nd?'dark':'light')}catch(e){}sync()});sync()}

 // ---- pictures: listed in the image library manifest (assets/library.js), never guessed from file names ----
 var LIB=window.SHIVAS_LIBRARY,id=document.body.getAttribute('data-item'),sec=document.getElementById('photos');
 var PV=window.SHIVAS_PREVIEW;
 // previews on the machines of a full line
 if(PV)PV.attach(document.getElementById('main'),'.lineup .mini',function(a){return 'item:'+(a.getAttribute('href')||'').replace(/\.html$/,'')},{touch:'none'});
 // all-products page: search and filters
 if(document.body.getAttribute('data-index'))filters();
 var it=LIB&&id&&LIB.items[id];
 // V26: real photos and 3D models are shown in separate sections; a 3D model is never called a photo
 if(it){gallery(document.getElementById('photos'),'photo');gallery(document.getElementById('models'),'model')}
 function gallery(sec,kind){
  if(!sec)return;
  var list=it.gallery.map(function(k){var a=LIB.assets[k];return a&&a.type===kind&&{id:k,thumb:'../'+a.thumb,full:'../'+a.full,prev:'../'+a.preview,alt:a.alt,tag:kind==='photo'?'Photo':'3D model',cap:a.config,tw:a.thumb_w,fw:a.full_w}}).filter(Boolean);
  if(!list.length)return;
  var cur=0,main=sec.querySelector('.gal-img img'),th=sec.querySelector('.gal-th'),cnt=sec.querySelector('.gal-count'),cap=sec.querySelector('.gal-cap'),gi=sec.querySelector('.gal-img');
  if(kind==='model'&&list.length>1)sec.querySelector('h2').textContent='3D models';
  function show(i){cur=(i+list.length)%list.length;var x=list[cur];
   main.srcset=x.thumb+' '+(x.tw||720)+'w, '+x.full+' '+(x.fw||1600)+'w';main.src=x.thumb;main.alt=x.alt;
   cnt.textContent=(cur+1)+' / '+list.length;
   if(cap){cap.hidden=kind==='photo'&&!x.cap;cap.innerHTML=(kind==='model'?'<span class="tag">3D model</span> ':'')+(x.cap?x.cap.replace(/[<&]/g,function(c){return c==='<'?'&lt;':'&amp;'}):'')}
   [].forEach.call(th.children,function(b,k){b.setAttribute('aria-current',String(k===cur))})}
  th.innerHTML=list.map(function(x,k){return '<button type="button" role="listitem" data-i="'+k+'" aria-label="'+x.tag+' '+(k+1)+' of '+list.length+'"><img src="'+x.prev+'" alt="" loading="lazy" decoding="async" width="120" height="80"></button>'}).join('');
  sec.querySelectorAll('.gal-nav').forEach(function(b){b.hidden=list.length<2});cnt.hidden=list.length<2;th.hidden=list.length<2;
  sec.hidden=false;show(0);
  main.addEventListener('error',function(){var x=list[cur];if(main.getAttribute('src')!==x.full){main.removeAttribute('srcset');main.src=x.full}});
  th.addEventListener('click',function(e){var b=e.target.closest('button');if(b)show(+b.getAttribute('data-i'))});
  sec.querySelector('.gal-nav.p').addEventListener('click',function(){show(cur-1)});
  sec.querySelector('.gal-nav.n').addEventListener('click',function(){show(cur+1)});
  var sx=0,gm=sec.querySelector('.gal-main');gm.addEventListener('pointerdown',function(e){sx=e.clientX});
  gm.addEventListener('pointerup',function(e){var d=e.clientX-sx;if(Math.abs(d)>50&&list.length>1){show(cur+(d<0?1:-1));sx=-1e9}});
  // full screen view: the full-size file is loaded only here
  var lb=document.createElement('div');lb.className='lb';lb.hidden=true;lb.setAttribute('role','dialog');lb.setAttribute('aria-label',kind==='photo'?'Photo, full screen':'3D model, full screen');
  lb.innerHTML='<img alt=""><button type="button" class="x" aria-label="Close">✕</button>';document.body.appendChild(lb);
  var lbi=lb.querySelector('img');
  gi.addEventListener('click',function(){if(Math.abs(sx)>1e8)return;lbi.src=list[cur].full;lbi.alt=list[cur].alt;lb.hidden=false;lb.querySelector('.x').focus()});
  lb.addEventListener('click',function(){lb.hidden=true;gi.focus()});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!lb.hidden){lb.hidden=true;gi.focus()}
   else if((e.key==='ArrowRight'||e.key==='ArrowLeft')&&(!lb.hidden||sec.contains(document.activeElement))){show(cur+(e.key==='ArrowRight'?1:-1));if(!lb.hidden){lbi.src=list[cur].full;lbi.alt=list[cur].alt}}});
  // photos roll on their own every 4.5 s while the gallery is on screen; a touch, hover or key holds it for 12 s
  if(list.length>1){var hold=0,vis=false,stop=function(){hold=Date.now()+12000;gm.classList.remove('tick')};
   ['pointerdown','mouseenter','focusin','wheel','keydown'].forEach(function(t){sec.addEventListener(t,stop,{passive:true})});
   if('IntersectionObserver' in window)new IntersectionObserver(function(es){vis=es[0].isIntersecting},{threshold:.5}).observe(gm);else vis=true;
   gm.classList.add('rolls','tick');
   setInterval(function(){if(!vis||!lb.hidden||document.hidden||Date.now()<hold)return;show(cur+1);
    var b=th.children[cur];if(b&&th.scrollWidth>th.clientWidth)th.scrollTo({left:b.offsetLeft-th.clientWidth/2+b.clientWidth/2,behavior:'smooth'});
    gm.classList.remove('tick');void gm.offsetWidth;gm.classList.add('tick')},4500)}
 }

 function filters(){
  var q=document.getElementById('q'),fam=document.getElementById('fam'),pics=document.getElementById('pics'),cnt=document.getElementById('cnt'),none=document.getElementById('none');
  var seg=document.querySelector('.flt .seg'),div='';
  var tiles=[].slice.call(document.querySelectorAll('.related.all .mini'));
  function info(a){var k=(a.getAttribute('href')||'').replace(/\.html$/,''),x=LIB&&LIB.items[k];return {k:k,x:x}}
  function run(){var t=(q.value||'').trim().toLowerCase(),f=fam.value,p=pics.checked,n=0;
   tiles.forEach(function(a){var o=info(a),txt=(a.textContent+' '+(o.x?o.x.description+' '+o.x.category:'')).toLowerCase();
    var ok=(!div||a.getAttribute('data-div')===div)&&(!t||txt.indexOf(t)>=0)&&(!f||(o.x&&o.x.family===f))&&(!p||(+a.getAttribute('data-ph')>0));
    a.hidden=!ok;if(ok)n++});
   [].forEach.call(document.querySelectorAll('.sec.grp'),function(s){s.hidden=!s.querySelector('.mini:not([hidden])')});
   cnt.textContent=n+(n===1?' product':' products');none.hidden=n>0}
  q.addEventListener('input',run);fam.addEventListener('change',run);pics.addEventListener('change',run);
  seg.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;div=b.getAttribute('data-div');[].forEach.call(seg.children,function(x){x.setAttribute('aria-pressed',String(x===b))});run()});
  run();
 }
})();
