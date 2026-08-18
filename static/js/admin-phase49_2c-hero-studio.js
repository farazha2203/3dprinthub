(function () {
  "use strict";

  function qs(root, selector) { return root.querySelector(selector); }
  function qsa(root, selector) { return Array.prototype.slice.call(root.querySelectorAll(selector)); }
  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
  function debounce(fn, wait) {
    var timer = null;
    return function () {
      var args = arguments;
      window.clearTimeout(timer);
      timer = window.setTimeout(function () { fn.apply(null, args); }, wait);
    };
  }
  function setValue(id, value, dispatch) {
    var el = document.getElementById(id);
    if (!el) return;
    el.value = value == null ? "" : value;
    if (dispatch !== false) {
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }
  function setAssetSelect(assetId, label) {
    var select = document.getElementById("id_asset");
    if (!select) return;
    var value = String(assetId || "");
    var option = Array.prototype.find.call(select.options || [], function (item) { return item.value === value; });
    if (!option && value) {
      option = new Option(label || ("Asset #" + value), value, true, true);
      select.add(option);
    }
    select.value = value;
    if (window.django && window.django.jQuery) {
      window.django.jQuery(select).trigger("change");
    } else {
      select.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }

  function boot() {
    var root = document.querySelector("[data-p49c-studio]");
    if (!root) return;

    var browserUrl = root.getAttribute("data-browser-url") || "";
    var detailUrl = root.getAttribute("data-detail-url") || "";
    var currentAssetId = root.getAttribute("data-current-asset-id") || "";
    var currentImageId = root.getAttribute("data-current-image-id") || "";
    var productsEl = qs(root, "[data-p49c-products]");
    var searchEl = qs(root, "[data-p49c-search]");
    var categoryEl = qs(root, "[data-p49c-category]");
    var refreshEl = qs(root, "[data-p49c-refresh]");
    var prevEl = qs(root, "[data-p49c-prev]");
    var nextEl = qs(root, "[data-p49c-next]");
    var pageEl = qs(root, "[data-p49c-page]");
    var statusEl = qs(root, "[data-p49c-status]");
    var selectedEl = qs(root, "[data-p49c-selected]");
    var selectedImageEl = qs(root, "[data-p49c-selected-image]");
    var selectedTitleEl = qs(root, "[data-p49c-selected-title]");
    var selectedMetaEl = qs(root, "[data-p49c-selected-meta]");
    var gallerySection = qs(root, "[data-p49c-gallery-section]");
    var galleryEl = qs(root, "[data-p49c-gallery]");
    var galleryCountEl = qs(root, "[data-p49c-gallery-count]");
    var previewBtn = qs(root, "[data-p49c-preview-effect]");
    var previewStage = qs(root, "[data-p49c-preview-stage]");
    var previewA = qs(root, "[data-p49c-preview-a]");
    var previewB = qs(root, "[data-p49c-preview-b]");
    var previewEmpty = qs(root, "[data-p49c-preview-empty]");

    var state = {
      page: 1,
      pages: 1,
      currentAssetId: currentAssetId,
      currentImageId: currentImageId,
      categoriesLoaded: false,
      images: [],
      selectedAsset: null,
      busy: false
    };

    function status(message, error) {
      if (!statusEl) return;
      statusEl.textContent = message;
      statusEl.style.borderColor = error ? "rgba(248,113,113,.4)" : "";
      statusEl.style.color = error ? "#fecaca" : "";
      statusEl.style.background = error ? "rgba(127,29,29,.18)" : "";
    }

    function browserParams() {
      var params = new URLSearchParams();
      params.set("page", String(state.page));
      var q = searchEl ? searchEl.value.trim() : "";
      var category = categoryEl ? categoryEl.value : "";
      if (q) params.set("q", q);
      if (category) params.set("category", category);
      return params;
    }

    function renderCategories(categories) {
      if (!categoryEl || state.categoriesLoaded || !Array.isArray(categories)) return;
      var current = categoryEl.value;
      categories.forEach(function (item) {
        var option = document.createElement("option");
        option.value = item.id;
        option.textContent = item.name;
        categoryEl.appendChild(option);
      });
      categoryEl.value = current;
      state.categoriesLoaded = true;
    }

    function renderProducts(data) {
      if (!productsEl) return;
      var items = data.items || [];
      if (!items.length) {
        productsEl.innerHTML = '<div class="p49c-empty"><span><i class="ri-search-eye-line"></i> محصولی با این فیلتر پیدا نشد.</span></div>';
      } else {
        productsEl.innerHTML = items.map(function (item) {
          var active = String(item.asset_id) === String(state.currentAssetId) ? " is-selected" : "";
          var media = item.image
            ? '<img src="' + esc(item.image) + '" alt="' + esc(item.title) + '" loading="lazy">'
            : '<span class="p49c-no-image"><i class="ri-image-off-line"></i></span>';
          var meta = [item.sku, item.category].filter(Boolean).join(" • ");
          return '<button type="button" class="p49c-product' + active + '" data-p49c-product="' + esc(item.asset_id) + '"'
            + ' data-title="' + esc(item.title) + '" data-image="' + esc(item.image || "") + '" data-meta="' + esc(meta) + '">'
            + '<span class="p49c-product__media">' + media + '<span class="p49c-product__check"><i class="ri-check-line"></i></span></span>'
            + '<span class="p49c-product__copy"><strong>' + esc(item.title) + '</strong><small>' + esc(meta || "بدون دسته") + '</small><em>' + esc(item.source || "3DPrintHub") + '</em></span>'
            + '</button>';
        }).join("");
      }
      state.page = Number(data.page || 1);
      state.pages = Number(data.pages || 1);
      if (pageEl) pageEl.textContent = "صفحه " + state.page + " از " + state.pages + " • " + Number(data.count || 0) + " محصول";
      if (prevEl) prevEl.disabled = !data.has_previous;
      if (nextEl) nextEl.disabled = !data.has_next;
      renderCategories(data.categories || []);
      qsa(productsEl, "[data-p49c-product]").forEach(function (button) {
        button.addEventListener("click", function () {
          selectAsset(button.getAttribute("data-p49c-product"), button.getAttribute("data-title") || "", true);
        });
      });
    }

    function loadProducts() {
      if (!browserUrl || state.busy) return;
      state.busy = true;
      if (productsEl) productsEl.innerHTML = '<div class="p49c-loading"><span><i class="ri-loader-4-line"></i> در حال دریافت محصولات…</span></div>';
      status("در حال دریافت آلبوم محصولات…");
      fetch(browserUrl + "?" + browserParams().toString(), { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(function (response) { if (!response.ok) throw new Error("HTTP " + response.status); return response.json(); })
        .then(function (data) {
          if (!data.ok) throw new Error(data.error || "خطای دریافت محصولات");
          renderProducts(data);
          status("آلبوم محصولات آماده است");
        })
        .catch(function (error) {
          if (productsEl) productsEl.innerHTML = '<div class="p49c-empty">خطا در دریافت محصولات. دوباره تلاش کنید.</div>';
          status("خطا: " + error.message, true);
        })
        .finally(function () { state.busy = false; });
    }

    function updateSelectedCard(asset, suggestion) {
      state.selectedAsset = asset;
      if (!selectedEl) return;
      selectedEl.hidden = false;
      if (selectedImageEl) {
        selectedImageEl.src = asset.image || (suggestion && suggestion.preview_url) || "";
        selectedImageEl.alt = asset.title || "محصول انتخاب‌شده";
      }
      if (selectedTitleEl) selectedTitleEl.textContent = asset.title || "—";
      if (selectedMetaEl) selectedMetaEl.textContent = [asset.sku, asset.category, asset.source].filter(Boolean).join(" • ");
    }

    function applySuggestions(data, overwrite) {
      var suggestion = data.suggestions || {};
      var map = [
        ["id_title_override", suggestion.title],
        ["id_group_title", suggestion.group_title],
        ["id_description", suggestion.description],
        ["id_image_alt_text", suggestion.image_alt_text],
        ["id_button_text", suggestion.button_text || "مشاهده محصول"]
      ];
      map.forEach(function (pair) {
        var input = document.getElementById(pair[0]);
        var value = pair[1] == null ? "" : pair[1];
        if (!input || !value) return;
        if (overwrite || !String(input.value || "").trim()) setValue(pair[0], value, true);
      });
    }

    function setPreviewImages() {
      var urls = state.images.map(function (item) { return item.url; }).filter(Boolean);
      var selected = qsa(galleryEl || document, ".p49c-image.is-selected img")[0];
      var first = selected ? selected.src : (urls[0] || (state.selectedAsset && state.selectedAsset.image) || "");
      var second = urls.find(function (url) { return url !== first; }) || first;
      if (!first) {
        if (previewStage) previewStage.classList.remove("has-image");
        if (previewEmpty) previewEmpty.hidden = false;
        return;
      }
      if (previewA) previewA.src = first;
      if (previewB) previewB.src = second;
      if (previewStage) previewStage.classList.add("has-image");
      if (previewEmpty) previewEmpty.hidden = true;
    }

    function chooseImage(button) {
      if (!button) return;
      var imageId = button.getAttribute("data-image-id") || "";
      var url = button.getAttribute("data-image-url") || "";
      var alt = button.getAttribute("data-image-alt") || "";
      state.currentImageId = imageId;
      qsa(galleryEl, ".p49c-image").forEach(function (item) { item.classList.toggle("is-selected", item === button); });
      setValue("id_selected_asset_image", imageId, false);
      if (imageId) {
        setValue("id_image_url", "", true);
      } else if (/^https?:\/\//i.test(url)) {
        setValue("id_image_url", url, true);
      } else {
        setValue("id_image_url", "", true);
      }
      if (alt) setValue("id_image_alt_text", alt, true);
      var preview = document.getElementById("p45-selected-preview");
      if (preview && url) preview.src = url;
      if (selectedImageEl && url) selectedImageEl.src = url;
      status(imageId ? "تصویر آلبوم انتخاب شد و با شناسه دیتابیس ذخیره می‌شود" : "تصویر پیش‌فرض محصول انتخاب شد");
      setPreviewImages();
    }

    function renderGallery(images) {
      state.images = Array.isArray(images) ? images : [];
      if (!gallerySection || !galleryEl) return;
      gallerySection.hidden = false;
      if (galleryCountEl) galleryCountEl.textContent = state.images.length + " تصویر";
      if (!state.images.length) {
        galleryEl.innerHTML = '<div class="p49c-empty">برای این محصول تصویر گالری ذخیره‌شده پیدا نشد؛ تصویر اصلی محصول استفاده می‌شود.</div>';
        setPreviewImages();
        return;
      }
      galleryEl.innerHTML = state.images.map(function (item, index) {
        var selected = item.id != null && String(item.id) === String(state.currentImageId) ? " is-selected" : "";
        if (!state.currentImageId && index === 0) selected = " is-selected";
        var primary = item.is_primary ? '<span class="p49c-image__primary">اصلی</span>' : "";
        var dimensions = item.width && item.height ? (item.width + "×" + item.height) : (item.id ? ("#" + item.id) : "پیش‌فرض");
        return '<button type="button" class="p49c-image' + selected + '" data-image-id="' + esc(item.id == null ? "" : item.id) + '" data-image-url="' + esc(item.url) + '" data-image-alt="' + esc(item.alt || "") + '">'
          + primary + '<img src="' + esc(item.url) + '" alt="' + esc(item.alt || ("تصویر " + (index + 1))) + '" loading="lazy">'
          + '<footer><span>' + esc(dimensions) + '</span><i class="ri-checkbox-circle-fill"></i></footer></button>';
      }).join("");
      qsa(galleryEl, ".p49c-image").forEach(function (button) { button.addEventListener("click", function () { chooseImage(button); }); });
      setPreviewImages();
    }

    function selectAsset(assetId, label, overwrite) {
      if (!detailUrl || !assetId) return;
      state.currentAssetId = String(assetId);
      state.currentImageId = "";
      setValue("id_selected_asset_image", "", false);
      setAssetSelect(assetId, label);
      qsa(productsEl || document, "[data-p49c-product]").forEach(function (item) {
        item.classList.toggle("is-selected", String(item.getAttribute("data-p49c-product")) === String(assetId));
      });
      status("در حال دریافت تصاویر و SEO محصول…");
      fetch(detailUrl + "?asset_id=" + encodeURIComponent(assetId), { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(function (response) { if (!response.ok) throw new Error("HTTP " + response.status); return response.json(); })
        .then(function (data) {
          if (!data.ok) throw new Error(data.error || "خطای دریافت محصول");
          updateSelectedCard(data.asset || {}, data.suggestions || {});
          applySuggestions(data, !!overwrite);
          renderGallery(data.images || []);
          status("محصول و گالری آماده و قابل ویرایش است");
        })
        .catch(function (error) { status("خطا: " + error.message, true); });
    }

    var reloadFromSearch = debounce(function () { state.page = 1; loadProducts(); }, 320);
    if (searchEl) searchEl.addEventListener("input", reloadFromSearch);
    if (categoryEl) categoryEl.addEventListener("change", function () { state.page = 1; loadProducts(); });
    if (refreshEl) refreshEl.addEventListener("click", function () { loadProducts(); });
    if (prevEl) prevEl.addEventListener("click", function () { if (state.page > 1) { state.page -= 1; loadProducts(); } });
    if (nextEl) nextEl.addEventListener("click", function () { if (state.page < state.pages) { state.page += 1; loadProducts(); } });

    var assetSelect = document.getElementById("id_asset");
    if (assetSelect) {
      assetSelect.addEventListener("change", function () {
        var value = assetSelect.value;
        if (value && String(value) !== String(state.currentAssetId)) {
          var text = assetSelect.options[assetSelect.selectedIndex] ? assetSelect.options[assetSelect.selectedIndex].text : "";
          selectAsset(value, text, true);
        }
      });
    }

    if (previewBtn) {
      previewBtn.addEventListener("click", function () {
        setPreviewImages();
        if (!previewStage || !previewStage.classList.contains("has-image")) {
          status("ابتدا یک محصول و تصویر انتخاب کنید", true);
          return;
        }
        var effectEl = document.getElementById("id_transition_effect");
        var durationEl = document.getElementById("id_transition_duration_ms");
        var effect = effectEl ? effectEl.value : "cinematic_fade";
        var duration = Math.max(300, Math.min(4000, Number(durationEl && durationEl.value || 1400)));
        previewStage.className = "p49c-preview-stage has-image effect-" + effect;
        previewStage.style.setProperty("--p49c-duration", duration + "ms");
        void previewStage.offsetWidth;
        previewStage.classList.add("is-running");
        window.setTimeout(function () { previewStage.classList.remove("is-running"); }, duration + 120);
      });
    }

    loadProducts();
    if (state.currentAssetId) selectAsset(state.currentAssetId, "", false);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
