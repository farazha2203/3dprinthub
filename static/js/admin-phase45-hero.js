(function(){
"use strict";
if(window.__P49_HERO_ADMIN_BOOTED__)return;
window.__P49_HERO_ADMIN_BOOTED__=true;

function byId(id){return document.getElementById(id)}
function valueOf(el){return el?String(el.value||"").trim():""}
function setValue(id,value,force){
  var el=byId(id);if(!el)return;
  if(!force&&valueOf(el))return;
  el.value=value||"";
  el.dispatchEvent(new Event("input",{bubbles:true}));
  el.dispatchEvent(new Event("change",{bubbles:true}));
}
function setPreview(url){
  var preview=byId("p45-selected-preview");
  if(preview&&url)preview.src=url;
}
function renderGallery(urls){
  var holder=document.querySelector(".field-candidate_image_gallery .readonly");
  if(!holder||!Array.isArray(urls)||!urls.length)return;
  holder.innerHTML="";
  var wrap=document.createElement("div");
  wrap.className="p45-admin-gallery";
  urls.forEach(function(url,index){
    if(!url)return;
    var button=document.createElement("button");
    button.type="button";
    button.className="p45-admin-image-choice";
    button.setAttribute("data-image-url",url);
    button.title="انتخاب تصویر "+(index+1);
    var img=document.createElement("img");
    img.src=url;img.alt="تصویر "+(index+1);
    var span=document.createElement("span");span.textContent=String(index+1);
    button.appendChild(img);button.appendChild(span);wrap.appendChild(button);
  });
  holder.appendChild(wrap);
}
function status(text,isError){
  var anchor=document.querySelector(".field-asset")||document.querySelector(".form-row.field-asset");
  if(!anchor)return;
  var node=document.getElementById("p49-hero-prefill-status");
  if(!node){node=document.createElement("div");node.id="p49-hero-prefill-status";node.style.marginTop="8px";node.style.fontSize="12px";node.style.fontWeight="700";anchor.appendChild(node)}
  node.textContent=text||"";
  node.style.color=isError?"#b42318":"#16794b";
}
function assetId(){var el=byId("id_asset");return valueOf(el)}
function applyPayload(data,force){
  setValue("id_title_override",data.title,force);
  setValue("id_group_title",data.group_title,force);
  setValue("id_description",data.description,force);
  setValue("id_image_alt_text",data.image_alt_text,force);
  if(data.image_url)setValue("id_image_url",data.image_url,force);
  setPreview(data.preview_url||data.image_url||"");
  renderGallery(data.images||[]);
  if(force){var active=byId("id_is_active");if(active&&!active.checked)active.checked=true}
  status("اطلاعات محصول برای اسلایدر آماده شد. پس از بررسی، ذخیره را بزنید.",false);
}
function prefill(force){
  var id=assetId();if(!id)return;
  var endpoint=window.P49_HERO_PREFILL_URL||"/internal/admin/hero-slide-prefill/";
  status("در حال دریافت اطلاعات محصول…",false);
  fetch(endpoint+"?asset_id="+encodeURIComponent(id),{credentials:"same-origin",headers:{"X-Requested-With":"XMLHttpRequest"}})
    .then(function(response){if(!response.ok)throw new Error("HTTP "+response.status);return response.json()})
    .then(function(data){if(!data||!data.ok)throw new Error((data&&data.error)||"پاسخ نامعتبر");applyPayload(data,force)})
    .catch(function(error){status("دریافت اطلاعات محصول ناموفق بود: "+error.message,true)});
}
function selectGalleryImage(button){
  var url=button.getAttribute("data-image-url")||"";if(!url)return;
  var input=byId("id_image_url");
  if(input&&/^https?:\/\//i.test(url)){
    input.value=url;input.dispatchEvent(new Event("input",{bubbles:true}));input.dispatchEvent(new Event("change",{bubbles:true}));
  }
  document.querySelectorAll(".p45-admin-image-choice").forEach(function(item){item.classList.toggle("is-selected",item===button)});
  setPreview(url);
  status(/^https?:\/\//i.test(url)?"تصویر انتخاب شد و در فیلد URL ثبت شد.":"تصویر محلی انتخاب شد؛ برای نمایش از تصویر ذخیره‌شده محصول استفاده می‌شود.",false);
}
function boot(){
  document.addEventListener("click",function(event){var button=event.target.closest(".p45-admin-image-choice");if(!button)return;event.preventDefault();selectGalleryImage(button)});
  var asset=byId("id_asset");
  if(asset){asset.addEventListener("change",function(){prefill(true)})}
  if(window.django&&django.jQuery&&asset){django.jQuery(asset).on("select2:select",function(){prefill(true)})}
  var isAdd=/\/add\/?$/.test(window.location.pathname);
  if(isAdd){var active=byId("id_is_active");if(active&&!active.checked)active.checked=true}
  if(assetId()){
    var empty=["id_title_override","id_group_title","id_description","id_image_alt_text"].some(function(id){return !valueOf(byId(id))});
    if(empty)prefill(false);
  }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",boot);else boot();
})();
