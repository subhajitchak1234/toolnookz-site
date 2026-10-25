(function(){
  var root=document.documentElement;
  // theme toggle
  var tb=document.getElementById('theme');
  if(tb)tb.addEventListener('click',function(){
    var dark=root.dataset.theme?root.dataset.theme==='dark':matchMedia('(prefers-color-scheme:dark)').matches;
    var next=dark?'light':'dark';root.dataset.theme=next;
    try{localStorage.setItem('theme',next)}catch(e){}
  });
  // mobile menu
  var mb=document.getElementById('menu'),nav=document.getElementById('nav');
  if(mb)mb.addEventListener('click',function(){
    var o=nav.classList.toggle('open');mb.setAttribute('aria-expanded',o);
  });
  // apps catalog: search + category filter + pagination
  var cat=document.getElementById('catalog');
  if(cat){
    var cards=[].slice.call(document.querySelectorAll('#grid .app-card'));
    var q=document.getElementById('search'),chips=[].slice.call(document.querySelectorAll('.chip'));
    var pager=document.getElementById('pager'),empty=document.getElementById('empty');
    var per=+cat.dataset.perPage||12,page=1,c='';
    var init=new URLSearchParams(location.search).get('q');if(init)q.value=init;
    if(location.hash==='#search')q.focus();
    function render(){
      var t=q.value.trim().toLowerCase();
      var hit=cards.filter(function(el){return (!c||el.dataset.cat===c)&&(!t||el.dataset.text.indexOf(t)>-1)});
      var pages=Math.max(1,Math.ceil(hit.length/per));if(page>pages)page=pages;
      cards.forEach(function(el){el.hidden=true});
      hit.slice((page-1)*per,page*per).forEach(function(el){el.hidden=false});
      empty.hidden=hit.length>0;pager.innerHTML='';
      if(pages>1){
        var add=function(label,p,dis,cur,aria){var b=document.createElement('button');b.type='button';b.textContent=label;
          if(aria)b.setAttribute('aria-label',aria);if(dis)b.disabled=true;if(cur)b.setAttribute('aria-current','page');
          b.onclick=function(){page=p;render();window.scrollTo({top:0})};pager.appendChild(b)};
        add('←',page-1,page===1,false,'Previous page');
        for(var i=1;i<=pages;i++)add(i,i,false,i===page);
        add('→',page+1,page===pages,false,'Next page');
      }
    }
    q.addEventListener('input',function(){page=1;render()});
    chips.forEach(function(b){b.addEventListener('click',function(){
      chips.forEach(function(x){x.classList.remove('is-on')});b.classList.add('is-on');c=b.dataset.cat;page=1;render()})});
    render();
  }
  // privacy index filter
  var pq=document.getElementById('plist-q');
  if(pq)pq.addEventListener('input',function(){
    var t=pq.value.trim().toLowerCase();
    [].forEach.call(document.querySelectorAll('#plist li'),function(li){li.hidden=t&&li.dataset.name.indexOf(t)<0});
  });
  // highlight current policy section in TOC
  var links=[].slice.call(document.querySelectorAll('.toc-box a'));
  if(links.length&&'IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){
      links.forEach(function(l){l.classList.toggle('on',l.getAttribute('href')==='#'+e.target.id)})}})},{rootMargin:'-80px 0px -70% 0px'});
    document.querySelectorAll('.doc h2[id]').forEach(function(h){io.observe(h)});
  }
})();
