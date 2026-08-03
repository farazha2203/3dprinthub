#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


class NextDataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.capture = False
        self.depth = 0
        self.chunks: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        if tag == "script" and values.get("id") == "__NEXT_DATA__":
            self.capture = True
            self.depth = 1
            self.chunks = []
        elif self.capture and tag == "script":
            self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self.capture and tag == "script":
            self.depth -= 1
            if self.depth <= 0:
                self.capture = False

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.chunks.append(data)

    def raw_json(self) -> str:
        return "".join(self.chunks).strip()


def clean_html(value: Any) -> str:
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", str(value))
    return " ".join(html.unescape(text).split())


def normalize_images(design: dict[str, Any]) -> list[dict[str, Any]]:
    extension = design.get("designExtension") or {}
    rows = extension.get("design_pictures") or []
    output: list[dict[str, Any]] = []
    seen: set[str] = set()

    for row in rows:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url") or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        output.append(
            {
                "name": str(row.get("name") or ""),
                "url": url,
                "is_real_life_photo": row.get("isRealLifePhoto"),
            }
        )

    cover = str(design.get("coverUrl") or "").strip()
    if cover and cover not in seen:
        output.insert(
            0,
            {
                "name": "cover",
                "url": cover,
                "is_real_life_photo": None,
            },
        )
    return output


def normalize_instances(design: dict[str, Any]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in design.get("instances") or []:
        if not isinstance(row, dict):
            continue
        output.append(
            {
                "id": row.get("id"),
                "profile_id": row.get("profileId"),
                "title": str(row.get("title") or ""),
                "status": row.get("status"),
                "print_time": (
                    row.get("printTime")
                    or row.get("prediction")
                    or row.get("printTimeSeconds")
                ),
                "weight": (
                    row.get("weight")
                    or row.get("filamentWeight")
                    or row.get("materialWeight")
                ),
                "plate_count": row.get("plateCount"),
                "printer_model": row.get("printerModel"),
                "filament": row.get("filament"),
            }
        )
    return output


def extract_record(raw_html: str, source_url: str = "") -> dict[str, Any]:
    parser = NextDataParser()
    parser.feed(raw_html)
    raw_json = parser.raw_json()
    if not raw_json:
        raise ValueError("__NEXT_DATA__ script was not found")

    payload = json.loads(html.unescape(raw_json))
    page_props = ((payload.get("props") or {}).get("pageProps") or {})
    design = page_props.get("design")
    if not isinstance(design, dict):
        raise ValueError("MakerWorld design payload was not found")

    creator = design.get("designCreator") or {}
    license_info = design.get("licenseDescriptionInfo") or {}
    images = normalize_images(design)
    instances = normalize_instances(design)

    categories = []
    for row in design.get("categories") or []:
        if isinstance(row, dict) and row.get("name"):
            categories.append(str(row["name"]))

    return {
        "source": "MakerWorld",
        "source_url": source_url,
        "external_id": str(design.get("id") or ""),
        "model_id": design.get("modelId"),
        "default_instance_id": design.get("defaultInstanceId"),
        "title": str(design.get("title") or ""),
        "slug": str(design.get("slug") or ""),
        "description_html": str(design.get("summary") or ""),
        "description_text": clean_html(design.get("summary") or ""),
        "cover_url": str(design.get("coverUrl") or ""),
        "images": images,
        "image_count": len(images),
        "tags": list(design.get("tags") or []),
        "categories": categories,
        "creator": {
            "uid": creator.get("uid"),
            "name": str(creator.get("name") or ""),
            "avatar": str(creator.get("avatar") or ""),
            "fan_count": creator.get("fanCount"),
        },
        "metrics": {
            "likes": design.get("likeCount"),
            "collections": design.get("collectionCount"),
            "prints": design.get("printCount"),
            "comments": design.get("commentCount"),
            "downloads": design.get("downloadCount"),
            "raw_model_downloads": design.get(
                "rawModelFileDownloadCount"
            ),
        },
        "license": {
            "name": str(design.get("license") or ""),
            "title": str(license_info.get("title") or ""),
            "description": str(license_info.get("content") or ""),
            "allow_recreation": design.get("allowReCreation"),
        },
        "instances": instances,
        "instance_count": len(instances),
        "create_time": design.get("createTime"),
        "update_time": design.get("updateTime"),
        "is_printable": design.get("isPrintable"),
        "is_official": design.get("isOfficial"),
        "is_exclusive": design.get("isExclusive"),
        "next_build_id": payload.get("buildId"),
        "next_page": payload.get("page"),
    }


def main() -> int:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--html", required=True)
    arg_parser.add_argument("--source-url", default="")
    arg_parser.add_argument("--output", required=True)
    args = arg_parser.parse_args()

    html_path = Path(args.html).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not html_path.is_file():
        print(f"STOP: HTML file not found: {html_path}", file=sys.stderr)
        return 20

    record = extract_record(
        html_path.read_text(encoding="utf-8", errors="replace"),
        source_url=args.source_url,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"TITLE={record['title']}")
    print(f"EXTERNAL_ID={record['external_id']}")
    print(f"IMAGE_COUNT={record['image_count']}")
    print(f"INSTANCE_COUNT={record['instance_count']}")
    print(f"OUTPUT={output_path}")
    print("MAKERWORLD_NEXT_DATA_PARSE=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
