(function(){
"use strict";
const root=document.documentElement;
const MOBILE_BREAKPOINT=1025;
let sidebarScroll=null;
function normalize(path){return(path||"/").replace(/\/+$/,"/")}
function getSidebar(){return document.querySelector(".app-menu.navbar-menu")}
function isMobile(){return window.innerWidth<MOBILE_BREAKPOINT}
function initVendorUi(){
  if(window.feather){try{window.feather.replace()}catch(_){}}
  if(window.Waves){try{window.Waves.init()}catch(_){}}
  if(window.flatpickr&&window.flatpickr.l10ns&&window.flatpickr.l10ns.fa){try{window.flatpickr.localize(window.flatpickr.l10ns.fa)}catch(_){}}
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el=>{try{bootstrap.Tooltip.getOrCreateInstance(el)}catch(_){}});
  document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el=>{try{bootstrap.Popover.getOrCreateInstance(el)}catch(_){}});
}
function initSidebarScroll(){
  const box=document.getElementById("scrollbar");
  const nav=document.getElementById("navbar-nav");
  if(!box)return;
  if(nav){nav.removeAttribute("data-simplebar");nav.classList.remove("h-100")}
  box.removeAttribute("data-simplebar");box.classList.remove("h-100");
  try{
    if(window.SimpleBar){
      sidebarScroll=window.SimpleBar.instances&&window.SimpleBar.instances.get(box);
      if(!sidebarScroll)sidebarScroll=new window.SimpleBar(box,{autoHide:false,forceVisible:"y"});
      requestAnimationFrame(()=>sidebarScroll&&sidebarScroll.recalculate());
    }
  }catch(_){box.style.overflowY="auto"}
}
function markActive(){
  const current=normalize(location.pathname);let best=null,bestLen=-1;
  document.querySelectorAll("#navbar-nav a.nav-link[href]").forEach(a=>{
    const raw=a.getAttribute("href")||"";if(!raw||raw.startsWith("#"))return;
    let path;try{path=normalize(new URL(a.href,location.origin).pathname)}catch(_){return}
    const match=current===path||(path!=="/admin/"&&current.startsWith(path));
    if(match&&path.length>bestLen){best=a;bestLen=path.length}
  });
  if(!best)return;
  best.classList.add("active");best.setAttribute("aria-current","page");
  let node=best.parentElement;
  while(node){
    if(node.classList&&node.classList.contains("collapse")){
      node.classList.add("show");
      const trigger=document.querySelector('[aria-controls="'+CSS.escape(node.id)+'"]');
      if(trigger){trigger.classList.remove("collapsed");trigger.classList.add("is-open");trigger.setAttribute("aria-expanded","true")}
    }
    node=node.parentElement;
  }
  setTimeout(()=>{
    try{best.scrollIntoView({block:"center",behavior:"smooth"})}catch(_){best.scrollIntoView()}
    if(sidebarScroll)sidebarScroll.recalculate();
  },120);
}
function syncCollapseStates(){
  document.querySelectorAll("#navbar-nav .collapse.menu-dropdown").forEach(panel=>{
    const trigger=document.querySelector('[aria-controls="'+CSS.escape(panel.id)+'"]');
    const sync=()=>{if(!trigger)return;const open=panel.classList.contains("show");trigger.classList.toggle("is-open",open);trigger.classList.toggle("collapsed",!open);trigger.setAttribute("aria-expanded",open?"true":"false");if(sidebarScroll)setTimeout(()=>sidebarScroll.recalculate(),40)};
    panel.addEventListener("shown.bs.collapse",sync);panel.addEventListener("hidden.bs.collapse",sync);sync();
  });
}
function formClasses(){
  document.querySelectorAll("#content input:not([type=checkbox]):not([type=radio]):not([type=submit]):not([type=button]):not([type=hidden]):not([type=file]),#content textarea").forEach(el=>el.classList.add("form-control"));
  document.querySelectorAll("#content select").forEach(el=>el.classList.add("form-select"));
  document.querySelectorAll("#content input[type=checkbox],#content input[type=radio]").forEach(el=>el.classList.add("form-check-input"));
}
function menuSearch(){
  const input=document.getElementById("admin-menu-search"),nav=document.getElementById("navbar-nav"),empty=document.getElementById("admin-menu-empty");if(!input||!nav)return;
  input.addEventListener("input",()=>{
    const q=input.value.trim().toLocaleLowerCase("fa-IR");let count=0;
    nav.querySelectorAll(":scope > .nav-item").forEach(item=>{
      if(!q){item.hidden=false;item.querySelectorAll(".menu-dropdown .nav-item").forEach(x=>x.hidden=false);return}
      const matches=item.textContent.toLocaleLowerCase("fa-IR").includes(q);item.hidden=!matches;
      if(matches){count++;item.querySelectorAll(".collapse.menu-dropdown").forEach(c=>{c.classList.add("show");const t=document.querySelector('[aria-controls="'+CSS.escape(c.id)+'"]');if(t){t.classList.add("is-open");t.setAttribute("aria-expanded","true")}});item.querySelectorAll(".menu-dropdown .nav-item").forEach(x=>x.hidden=!x.textContent.toLocaleLowerCase("fa-IR").includes(q))}
    });
    nav.querySelectorAll(":scope > .menu-title").forEach(t=>t.hidden=!!q);if(empty)empty.hidden=!q||count>0;if(sidebarScroll)setTimeout(()=>sidebarScroll.recalculate(),20)
  });
}
function pageSearch(){document.querySelectorAll("[data-admin-global-search]").forEach(input=>input.addEventListener("input",()=>{const q=input.value.trim().toLocaleLowerCase("fa-IR");document.querySelectorAll("#content tbody tr").forEach(row=>row.hidden=!!q&&!row.textContent.toLocaleLowerCase("fa-IR").includes(q))}))}
function setupShellControls(){
  const hamburger=document.getElementById("topnav-hamburger-icon"),overlay=document.querySelector(".vertical-overlay"),hover=document.getElementById("vertical-hover");
  const closeMobile=()=>document.body.classList.remove("vertical-sidebar-enable");
  if(hamburger)hamburger.addEventListener("click",event=>{event.preventDefault();if(isMobile()){document.body.classList.toggle("vertical-sidebar-enable")}else{const current=root.getAttribute("data-sidebar-size")||"lg";const next=current==="sm"?"lg":"sm";root.setAttribute("data-sidebar-size",next);sessionStorage.setItem("data-sidebar-size",next)}setTimeout(()=>sidebarScroll&&sidebarScroll.recalculate(),240)});
  if(overlay)overlay.addEventListener("click",closeMobile);
  if(hover)hover.addEventListener("click",()=>{const current=root.getAttribute("data-sidebar-size")||"lg";const next=current==="sm"?"lg":"sm";root.setAttribute("data-sidebar-size",next);sessionStorage.setItem("data-sidebar-size",next);setTimeout(()=>sidebarScroll&&sidebarScroll.recalculate(),240)});
  document.querySelectorAll("#navbar-nav a.nav-link[href]:not([data-bs-toggle])").forEach(link=>link.addEventListener("click",()=>{if(isMobile())closeMobile()}));
  window.addEventListener("resize",()=>{if(!isMobile())closeMobile();if(sidebarScroll)sidebarScroll.recalculate()},{passive:true});
  const themeButton=document.querySelector(".light-dark-mode");if(themeButton)themeButton.addEventListener("click",()=>{const next=root.getAttribute("data-bs-theme")==="dark"?"light":"dark";root.setAttribute("data-bs-theme",next);sessionStorage.setItem("data-bs-theme",next)});
  const fullscreen=document.querySelector('[data-toggle="fullscreen"]');if(fullscreen)fullscreen.addEventListener("click",async event=>{event.preventDefault();try{if(!document.fullscreenElement)await document.documentElement.requestFullscreen();else await document.exitFullscreen()}catch(_){}});
}
function initEnhancedFields(){
  if(window.Choices){document.querySelectorAll("select[data-choices]").forEach(el=>{if(el.dataset.choicesReady)return;try{new window.Choices(el,{shouldSort:false,searchEnabled:true,itemSelectText:""});el.dataset.choicesReady="1"}catch(_){}})}
  if(window.flatpickr){document.querySelectorAll('[data-provider="flatpickr"]').forEach(el=>{if(el._flatpickr)return;try{window.flatpickr(el,{dateFormat:el.dataset.dateFormat||"Y-m-d",disableMobile:true,locale:"fa"})}catch(_){}})}
}
async function unread(){const badges=[document.getElementById("admin-support-unread-badge"),document.getElementById("admin-chat-unread-badge")].filter(Boolean),label=document.getElementById("admin-support-unread-label");if(!badges.length)return;try{const r=await fetch("/admin/website/supportconversation/unread-count/",{headers:{"X-Requested-With":"XMLHttpRequest"},credentials:"same-origin"});if(!r.ok)return;const data=await r.json();const count=Number(data.unread??data.unread_count??data.count??0);badges.forEach(badge=>{badge.textContent=String(count);badge.hidden=count<1});if(label)label.textContent=count.toLocaleString("fa-IR")+" جدید"}catch(_){}}
document.addEventListener("DOMContentLoaded",()=>{initSidebarScroll();syncCollapseStates();markActive();formClasses();menuSearch();pageSearch();setupShellControls();initVendorUi();initEnhancedFields();unread();setInterval(unread,15000)});
})();
