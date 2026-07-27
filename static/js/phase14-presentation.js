(function(){
  "use strict";
  function q(s,r){return (r||document).querySelector(s)}
  function qa(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))}
  function initHero(){
    var root=q("[data-p14-hero-slider]"); if(!root)return;
    var slides=qa("[data-p14-hero-slide]",root); if(slides.length<2)return;
    var dots=qa("[data-p14-hero-dot]",root),index=0,timer=null;
    function show(n){index=(n+slides.length)%slides.length;slides.forEach(function(x,i){x.classList.toggle("is-active",i===index)});dots.forEach(function(x,i){x.classList.toggle("is-active",i===index)})}
    function start(){stop();timer=window.setInterval(function(){show(index+1)},5200)}
    function stop(){if(timer){window.clearInterval(timer);timer=null}}
    var next=q("[data-p14-hero-next]",root),prev=q("[data-p14-hero-prev]",root);
    if(next)next.addEventListener("click",function(){show(index+1);start()});
    if(prev)prev.addEventListener("click",function(){show(index-1);start()});
    dots.forEach(function(dot){dot.addEventListener("click",function(){show(Number(dot.getAttribute("data-p14-hero-dot")));start()})});
    root.addEventListener("mouseenter",stop);root.addEventListener("mouseleave",start);start();
  }
  function initCatalog(){
    var chips=q("[data-p14-catalog-chips]"),grid=q("[data-p14-home-model-grid]");if(!chips||!grid)return;
    qa("button",chips).forEach(function(button){button.addEventListener("click",function(){var segment=button.getAttribute("data-p14-segment");qa("button",chips).forEach(function(x){x.classList.toggle("is-active",x===button)});qa("[data-p14-model-segment]",grid).forEach(function(card){card.hidden=segment!=="all"&&card.getAttribute("data-p14-model-segment")!==segment})})})
  }
  document.addEventListener("DOMContentLoaded",function(){initHero();initCatalog()});
})();
