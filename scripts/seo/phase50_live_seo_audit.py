"""Read-only public sitemap SEO audit. Not a Search Console or Lighthouse score.

Run with the verified project Python. Makes only bounded public GET requests.
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import statistics
import sys
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

import requests
from lxml import html

SITE = "https://3dprinthub.ir"
HEADERS = {"User-Agent": "3DPrintHub-Owner-SEO-Audit/1.0"}
S = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def fetch(target):
    url = SITE + target if target.startswith("/") else target
    if urlparse(url).netloc != urlparse(SITE).netloc:
        raise ValueError("off-site URL rejected")
    return requests.get(url, headers=HEADERS, timeout=(8, 25))


def field(tree, attr, key):
    matches = tree.xpath(f"//meta[@{attr}='{key}']/@content")
    return matches[0].strip() if matches else ""


def audit(url):
    row = {"url": url, "errors": []}
    try:
        response = fetch(url)
        row["status"] = response.status_code
        row["elapsed_ms"] = round(response.elapsed.total_seconds() * 1000)
        row["bytes"] = len(response.content)
        if response.status_code != 200:
            row["errors"].append("http_not_200")
            return row
        doc = html.fromstring(response.content)
        title = " ".join(t.strip() for t in doc.xpath("//title//text()")).strip()
        desc = field(doc, "name", "description")
        canon = doc.xpath("//link[@rel='canonical']/@href")
        robots = field(doc, "name", "robots")
        h1 = doc.xpath("//h1")
        imgs = doc.xpath("//img")
        no_alt = doc.xpath("//img[not(@alt)]")
        scripts = doc.xpath("//script[@type='application/ld+json']/text()")
        nodes, bad_ld = [], 0
        for raw in scripts:
            try:
                data = json.loads(raw)
                for obj in (data if isinstance(data, list) else [data]):
                    if isinstance(obj, dict):
                        nodes.append(obj)
                        nodes.extend(obj.get("@graph", []))
            except (TypeError, ValueError):
                bad_ld += 1
        groups = [obj for obj in nodes if isinstance(obj, dict) and obj.get("@type") == "ProductGroup"]
        variants = [v for g in groups for v in g.get("hasVariant", []) if isinstance(v, dict)]
        priced = sum(1 for v in variants if isinstance(v.get("offers"), dict)
                     and v["offers"].get("priceCurrency") == "IRR"
                     and str(v["offers"].get("price", "")).replace(".", "", 1).isdigit()
                     and float(v["offers"]["price"]) > 0)
        row.update(title=title, title_chars=len(title), description=desc, description_chars=len(desc),
                   canonical=canon[0] if canon else "", robots=robots, h1_count=len(h1),
                   img_count=len(imgs), missing_alt_count=len(no_alt),
                   product_cards=len(doc.xpath("//article[contains(@class, 'store-product-card')]")),
                   og_title=bool(field(doc, "property", "og:title")),
                   og_description=bool(field(doc, "property", "og:description")),
                   og_image=bool(field(doc, "property", "og:image")),
                   twitter_card=bool(field(doc, "name", "twitter:card")),
                   product_groups=len(groups), product_variants=len(variants),
                   priced_variants=priced, ld_json_parse_errors=bad_ld,
                   home_product_microdata=len(doc.xpath("//*[@itemscope and @itemtype='https://schema.org/Product']")))
        for criterion, failing in (
            ("missing_title", not title),
            ("missing_meta_description", not desc),
            ("missing_canonical", not canon),
            ("incorrect_canonical", bool(canon) and canon[0] != url.rstrip("/") and canon[0] != url),
            ("sitemap_noindex", "noindex" in robots.lower()),
            ("missing_h1", len(h1) == 0),
            ("multiple_h1", len(h1) > 1),
            ("images_missing_alt", len(no_alt) > 0),
            ("invalid_jsonld", bad_ld > 0),
            ("product_missing_productgroup", "/store/product/" in url and not groups),
            ("product_missing_priced_variants", "/store/product/" in url and not priced),
            ("homepage_product_microdata", url == SITE + "/" and row["home_product_microdata"] > 0),
        ):
            if failing:
                row["errors"].append(criterion)
    except (requests.RequestException, ValueError) as exc:
        row["errors"].append("fetch_exception")
        row["exception"] = str(exc)[:150]
    return row


def main():
    robots = fetch("/robots.txt")
    sitemap = fetch("/sitemap.xml")
    image_map = fetch("/sitemap-images.xml")
    root = ET.fromstring(sitemap.content)
    urls = [x.text.strip() for x in root.findall(".//" + S + "loc") if x.text]
    urls = list(dict.fromkeys(u for u in urls if u.startswith(SITE + "/")))[:120]
    assert urls, "empty sitemap"
    results = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        tasks = [pool.submit(audit, u) for u in urls]
        for job in as_completed(tasks):
            results.append(job.result())
    results.sort(key=lambda x: x["url"])
    problems = Counter(e for r in results for e in r["errors"])
    title_dupes = Counter(r.get("title") for r in results if r.get("title"))
    desc_dupes = Counter(r.get("description") for r in results if r.get("description"))
    latency = [r["elapsed_ms"] for r in results if "elapsed_ms" in r]
    summary = {
        "sitemap_count": len(urls), "http_200": sum(r.get("status") == 200 for r in results),
        "robots_http": robots.status_code, "sitemap_http": sitemap.status_code,
        "images_sitemap_http": image_map.status_code, "problems": dict(problems),
        "duplicate_title_groups": sum(x > 1 for x in title_dupes.values()),
        "duplicate_description_groups": sum(x > 1 for x in desc_dupes.values()),
        "missing_og_image": sum(not r.get("og_image", False) for r in results),
        "missing_twitter_card": sum(not r.get("twitter_card", False) for r in results),
        "product_urls": sum("/store/product/" in r["url"] for r in results),
        "p50_server_response_ms": round(statistics.median(latency)) if latency else None,
        "avg_server_response_ms": round(statistics.mean(latency)) if latency else None,
    }
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"summary": summary, "pages": results, "robots": robots.text},
                        ensure_ascii=False, indent=2), encoding="utf-8")
    print("SEO_PUBLIC_AUDIT=", json.dumps(summary, ensure_ascii=False), flush=True)
    for r in results:
        if r["errors"]:
            print("ISSUE:", r["url"], ", ".join(r["errors"]), flush=True)


if __name__ == "__main__":
    main()
