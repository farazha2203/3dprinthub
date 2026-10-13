#!/usr/bin/env python3
"""Read-only public acceptance for the A2W service discovery pages."""

import argparse
import re
import sys
from urllib.parse import urlparse

from phase50_a2v_public_smoke import PageMetadata, fetch, sitemap_page_urls


EXPECTED = {
    "/store/services/design-from-idea/": ("طراحی سه‌بعدی", "ایده"),
    "/store/services/jigs-fixtures-and-mold-prototypes/": ("جیگ", "فیکسچر"),
    "/store/services/studio-props-and-photography-decor/": ("پراپ", "آتلیه"),
    "/store/services/custom-figure-design-and-printing/": ("فیگور", "سه‌بعدی"),
    "/store/services/rare-car-part-reconstruction/": ("قطعه", "خودرو"),
    "/store/services/rare-motorcycle-part-reconstruction/": ("قطعه", "موتورسیکلت"),
    "/store/services/rare-home-appliance-part-reconstruction/": ("قطعه", "لوازم خانگی"),
    "/store/services/architectural-maquette-and-model-making/": ("ماکت", "معماری"),
}


def run(base, check_social=False):
    base = base.rstrip("/")
    if check_social:
        for path in ("/", "/store/"):
            status, body, _ = fetch(base + path)
            if status != 200:
                raise RuntimeError("social_shell_http_failed:" + path)
            html = body.decode("utf-8", "replace")
            if 'aria-label="پاورقی و راه‌های ارتباطی 3DprintHub"' not in html:
                raise RuntimeError("shared_footer_missing:" + path)
            if html.count('<footer class="site-footer') != 1:
                raise RuntimeError("public_footer_count_invalid:" + path)
            if not re.search(r'href=["\']https://wa\.me/\d+["\']', html):
                raise RuntimeError("clickable_whatsapp_missing:" + path)
            if not re.search(r'href=["\']https?://(?:www\.)?instagram\.com/3dprinthub_ir/?["\']', html):
                raise RuntimeError("instagram_profile_link_missing:" + path)
            if path == "/" and "هنوز بازخوردی از سفارشات ثبت نشده است" in html:
                raise RuntimeError("empty_customer_feedback_should_be_hidden")
            print("SOCIAL_SHELL=PASS", path)
        css_status, css_body, _ = fetch(base + "/static/css/main.css")
        if css_status != 200:
            raise RuntimeError("public_theme_css_unavailable")
        css = css_body.decode("utf-8", "replace")
        for required in (".site-footer {", "background-color: #111827 !important;", ".site-footer .text-slate-400"):
            if required not in css:
                raise RuntimeError("public_footer_theme_rule_missing:" + required)
        print("SOCIAL_CONTACT_SMOKE=PASS")
    urls = set(sitemap_page_urls(base + "/sitemap.xml"))
    for path, title_terms in EXPECTED.items():
        found = next((url for url in urls if urlparse(url).path == path), None)
        if not found:
            raise RuntimeError("service_missing_from_sitemap:" + path)
        status, body, _ = fetch(found)
        if status != 200:
            raise RuntimeError("service_http_failed:" + path)
        decoded_body = body.decode("utf-8", "replace")
        if any(term.casefold() in decoded_body.casefold() for term in ("H2S", "Bambu Lab", "۳۴۰×۳۲۰×۳۴۰", "حجم ساخت اسمی")):
            raise RuntimeError("private_equipment_detail_leaked:" + path)
        parser = PageMetadata()
        parser.feed(decoded_body)
        title = " ".join("".join(parser.title).split())
        description = parser.meta.get("description", "")
        robots = parser.meta.get("robots", "index,follow").casefold()
        if not title or not description or "noindex" in robots:
            raise RuntimeError("service_metadata_or_indexability_missing:" + path)
        if parser.canonical.rstrip("/") != found.rstrip("/"):
            raise RuntimeError("service_canonical_mismatch:" + path)
        if any(term not in title for term in title_terms):
            raise RuntimeError("service_title_terms_missing:" + path)
        if "/store/request-a-part/?service=" + path.rstrip("/").split("/")[-1] not in decoded_body:
            raise RuntimeError("service_request_prefill_link_missing:" + path)
        if not any(
            node.get("@type") == "Service"
            for block in parser.json_ld
            if isinstance(block, dict)
            for node in block.get("@graph", [])
            if isinstance(node, dict)
        ):
            raise RuntimeError("service_jsonld_missing:" + path)
        print("SERVICE_PAGE=PASS", found)
    print("A2W_SERVICE_SEO_SMOKE=PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://3dprinthub.ir")
    parser.add_argument("--social", action="store_true", help="verify configured social links and shared footer on Home and Store")
    try:
        args = parser.parse_args()
        run(args.base, check_social=args.social)
    except Exception as exc:
        print("A2W_SERVICE_SEO_SMOKE=FAIL", str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
