(function () {
  "use strict";
  function fill(select, items, placeholder, selected) {
    select.innerHTML = "";
    var first = document.createElement("option");
    first.value = "";
    first.textContent = placeholder;
    select.appendChild(first);
    items.forEach(function (item) {
      var option = document.createElement("option");
      option.value = item;
      option.textContent = item;
      option.selected = item === selected;
      select.appendChild(option);
    });
    select.disabled = !items.length;
  }
  function fetchJSON(url) {
    return fetch(url, {headers: {"X-Requested-With": "XMLHttpRequest"}}).then(function (response) {
      if (!response.ok) throw new Error("location_request_failed");
      return response.json();
    });
  }
  function init() {
    var province = document.querySelector("[data-iran-province]");
    var county = document.querySelector("[data-iran-county]");
    var city = document.querySelector("[data-iran-city]");
    if (!province || !county || !city) return;
    var countyEndpoint = county.dataset.countyEndpoint || "/customer/locations/counties/";
    var cityEndpoint = city.dataset.cityEndpoint || "/customer/locations/cities-v2/";
    var initialCounty = county.value;
    var initialCity = city.value;

    function loadCities(selected) {
      if (!province.value || !county.value) {
        fill(city, [], "ابتدا شهرستان را انتخاب کنید", "");
        return Promise.resolve();
      }
      city.disabled = true;
      return fetchJSON(cityEndpoint + "?province=" + encodeURIComponent(province.value) + "&county=" + encodeURIComponent(county.value))
        .then(function (data) { fill(city, data.cities || [], "انتخاب شهر", selected || ""); })
        .catch(function () { fill(city, [], "خطا در دریافت شهرها", ""); });
    }

    function loadCounties(selectedCounty, selectedCity) {
      if (!province.value) {
        fill(county, [], "ابتدا استان را انتخاب کنید", "");
        fill(city, [], "ابتدا شهرستان را انتخاب کنید", "");
        return;
      }
      county.disabled = true;
      fetchJSON(countyEndpoint + "?province=" + encodeURIComponent(province.value))
        .then(function (data) {
          fill(county, data.counties || [], "انتخاب شهرستان", selectedCounty || "");
          return loadCities(selectedCity || "");
        })
        .catch(function () {
          fill(county, [], "خطا در دریافت شهرستان‌ها", "");
          fill(city, [], "ابتدا شهرستان را انتخاب کنید", "");
        });
    }

    province.addEventListener("change", function () { loadCounties("", ""); });
    county.addEventListener("change", function () { loadCities(""); });
    if (province.value) loadCounties(initialCounty, initialCity);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
