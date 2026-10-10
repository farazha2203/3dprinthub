#!/usr/bin/env python3
"""Read-only public SEO smoke for the A2V Isfahan release."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import argparse
import json
import sys
import xml.etree.ElementTree as ET


class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = []
        self.in_title = False
        self.meta = {}
        self.canonical = ""
        self.json_ld = []
        self.in_json_ld = False
        self.json_buffer = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            key = attrs.get("name") or attrs.get("property")
            if key:
                self.meta[key.casefold()] = attrs.get("content", "").strip()
        if tag == "link" and "canonical" in attrs.get("rel", "").casefold().split():
            self.canonical = attrs.get("href", "").strip()
        if tag == "script" and attrs.get("type", "").casefold() == "application/ld+json":
            self.in_json_ld = True
            self.json_buffer = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_json_ld:
            raw = "".join(self.json_buffer).strip()
            if raw:
                try:
                    self.json_ld.append(json.loads(raw))
                except json.JSONDecodeError:
                    self.json_ld.append({"_invalid_json": True})
            self.in_json_ld = False
            self.json_buffer = []

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self.in_json_ld:
            self.json_buffer.append(data)


def fetch(url, timeout=30):
    request = Request(url, headers={"User-Agent": "3DPrintHub-A2V-SEO-Smoke/1.0", "Cache-Control": "no-cache"})
    with urlopen(request, timeout=timeout) as response:
        return response.status, response.read(), response.headers


def sitemap_page_urls(url, visited=None):
    visited = visited or set()
    if url in visited:
        return []
    visited.add(url)
    status, body, _ = fetch(url)
    if status != 200:
        raise RuntimeError(f"sitemap_http_{status}:{url}")
    root = ET.fromstring(body)
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    if root.tag.endswith("sitemapindex"):
        result = []
        for node in root.findall(f"{namespace}sitemap"):
            loc = node.findtext(f"{namespace}loc")
            if loc:
                result.extend(sitemap_page_urls(loc.strip(), visited))
        return result
    result = []
    for node in root.findall(f"{namespace}url"):
        loc = node.findtext(f"{namespace}loc")
        if loc and urlparse(loc.strip()).scheme in {"http", "https"}:
            result.append(loc.strip())
    return result


def inspect_page(url):
    status, body, _ = fetch(url)
    if status != 200:
        raise RuntimeError(f"page_http_{status}:{url}")
    parser = PageMetadata()
    parser.feed(body.decode("utf-8", "replace"))
    title = " ".join("".join(parser.title).split())
    description = parser.meta.get("description", "")
    robots = parser.meta.get("robots", "index,follow").casefold().replace(" ", "")
    if not title or not description or not parser.canonical:
        raise RuntimeError(f"missing_title_description_or_canonical:{url}")
    if "noindex" in robots:
        raise RuntimeError(f"noindex_url_in_sitemap:{url}")
    return url, title, description, parser


def run(base):
    base = base.rstrip("/")
    status, robots_body, _ = fetch(base + "/robots.txt")
    robots = robots_body.decode("utf-8", "replace")
    if status != 200 or "Allow: /" not in robots or "Disallow: /\n" in robots:
        raise RuntimeError("robots_blocks_public_crawling")

    urls = sorted(set(sitemap_page_urls(base + "/sitemap.xml")))
    if not urls:
        raise RuntimeError("root_sitemap_has_no_page_urls")
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(inspect_page, url) for url in urls]
        pages = [future.result() for future in as_completed(futures)]

    titles = [page[1].casefold() for page in pages]
    descriptions = [page[2].casefold() for page in pages]
    if len(set(titles)) != len(titles):
        raise RuntimeError("duplicate_titles_in_sitemap")
    if len(set(descriptions)) != len(descriptions):
        raise RuntimeError("duplicate_descriptions_in_sitemap")

    expected_path = "/store/services/3d-printing-isfahan/"
    landing = next((page for page in pages if urlparse(page[0]).path == expected_path), None)
    if not landing:
        raise RuntimeError("isfahan_service_missing_from_sitemap")
    _, title, description, parser = landing
    if "اصفهان" not in title or "چاپ سه‌بعدی" not in title or "اصفهان" not in description:
        raise RuntimeError("isfahan_persian_metadata_missing")
    if parser.canonical.rstrip("/") != landing[0].rstrip("/"):
        raise RuntimeError("isfahan_canonical_mismatch")
    service_nodes = []
    for block in parser.json_ld:
        graph = block.get("@graph", []) if isinstance(block, dict) else []
        service_nodes.extend(node for node in graph if isinstance(node, dict) and node.get("@type") == "Service")
    if not any(
        service.get("areaServed", {}).get("@type") == "City"
        and service.get("areaServed", {}).get("name") == "اصفهان"
        for service in service_nodes
    ):
        raise RuntimeError("isfahan_service_schema_missing")

    persian_title_urls = [page for page in pages if urlparse(page[0]).path in {
        "/store/category/mounts-brackets/",
        "/store/category/plant-pots/",
        "/store/category/toys-games/",
    }]
    if any(not any("\u0600" <= char <= "\u06ff" for char in page[1]) for page in persian_title_urls):
        raise RuntimeError("known_category_title_not_persian")

    home_status, home_body, _ = fetch(base + "/")
    if home_status != 200:
        raise RuntimeError("homepage_http_failed")
    home = PageMetadata()
    home.feed(home_body.decode("utf-8", "replace"))
    for key in ("og:title", "og:description", "og:site_name", "twitter:card", "twitter:title", "twitter:description"):
        if not home.meta.get(key):
            raise RuntimeError("homepage_social_metadata_missing:" + key)
    if "3d-printing-isfahan" not in home_body.decode("utf-8", "replace"):
        raise RuntimeError("homepage_internal_isfahan_link_missing")

    print(f"ROBOTS_PUBLIC_CRAWL=PASS")
    print(f"SITEMAP_PAGES_HTTP200_INDEXABLE={len(pages)}/{len(pages)}")
    print(f"SITEMAP_UNIQUE_TITLES_DESCRIPTIONS={len(pages)}/{len(pages)}")
    print(f"ISFAHAN_LANDING_SCHEMA_AND_CANONICAL=PASS {landing[0]}")
    print("HOMEPAGE_PERSIAN_SOCIAL_METADATA_AND_INTERNAL_LINK=PASS")
    print("A2V_PUBLIC_SEO_SMOKE=PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://3dprinthub.ir")
    args = parser.parse_args()
    try:
        run(args.base)
    except (HTTPError, URLError, ET.ParseError, RuntimeError, ValueError) as exc:
        print("A2V_PUBLIC_SEO_SMOKE=FAIL", str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
