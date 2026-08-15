from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from store.models import ImportedPrintAsset, Product


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _existing_path(field_file) -> Path | None:
    if not field_file or not getattr(field_file, "name", ""):
        return None
    try:
        path = Path(field_file.path).resolve()
    except Exception:
        return None
    return path if path.is_file() and path.stat().st_size > 0 else None


class Command(BaseCommand):
    help = "Audit/repair public Store media without deleting or moving any source file."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--strict", action="store_true")
        parser.add_argument("--search-root", action="append", default=[])

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT).expanduser().resolve()
        base_dir = Path(settings.BASE_DIR).resolve()
        home = Path.home().resolve()
        public_html_media = (home / "public_html" / "media").resolve()

        roots = [
            media_root,
            (base_dir / "media").resolve(),
            (base_dir.parent / "media").resolve(),
            (home / "media").resolve(),
            public_html_media,
            (home / "3dprinthub" / "media").resolve(),
        ]
        roots.extend(Path(value).expanduser().resolve() for value in options["search_root"])
        roots = list(dict.fromkeys(roots))

        self.stdout.write(f"MEDIA_URL={settings.MEDIA_URL}")
        self.stdout.write(f"MEDIA_ROOT={media_root}")
        self.stdout.write(f"PUBLIC_HTML_MEDIA={public_html_media}")
        self.stdout.write(f"MEDIA_ROOT_IS_PUBLIC_HTML={int(media_root == public_html_media)}")
        for root in roots:
            self.stdout.write(f"SEARCH_ROOT={root} EXISTS={int(root.is_dir())}")

        checked = missing = repaired = ambiguous = 0

        products = (
            Product.objects.all()
            .select_related("category")
            .prefetch_related("images")
            .order_by("pk")
        )
        for product in products:
            linked_asset = (
                ImportedPrintAsset.objects.filter(product_id=product.pk)
                .prefetch_related("images")
                .order_by("pk")
                .first()
            )
            asset_images = []
            if linked_asset is not None:
                asset_images = list(
                    linked_asset.images.filter(is_selected=True)
                    .exclude(image="")
                    .order_by("sort_order", "id")
                )

            items = [("main", product.main_image, getattr(linked_asset, "preview_image", None))]
            for index, image in enumerate(product.images.all()):
                source_field = asset_images[index].image if index < len(asset_images) else None
                items.append((f"gallery:{image.pk}", image.image, source_field))

            for label, field_file, source_field in items:
                name = str(getattr(field_file, "name", "") or "").replace("\\", "/").lstrip("/")
                if not name:
                    continue
                checked += 1
                expected = (media_root / name).resolve()
                if expected.is_file() and expected.stat().st_size > 0:
                    self.stdout.write(
                        f"OK PRODUCT={product.pk} FIELD={label} NAME={name} SIZE={expected.stat().st_size}"
                    )
                    continue

                candidates: list[Path] = []
                for root in roots:
                    candidate = (root / name).resolve()
                    if candidate.is_file() and candidate.stat().st_size > 0 and candidate != expected:
                        candidates.append(candidate)
                source_path = _existing_path(source_field)
                if source_path is not None and source_path != expected:
                    candidates.append(source_path)
                candidates = list(dict.fromkeys(candidates))

                if len(candidates) > 1:
                    hashes = {_sha256(path) for path in candidates}
                    if len(hashes) == 1:
                        candidates = [candidates[0]]

                if not candidates:
                    missing += 1
                    self.stderr.write(
                        f"MISSING PRODUCT={product.pk} FIELD={label} NAME={name} EXPECTED={expected}"
                    )
                    continue
                if len(candidates) != 1:
                    missing += 1
                    ambiguous += 1
                    joined = " | ".join(str(path) for path in candidates)
                    self.stderr.write(
                        f"AMBIGUOUS PRODUCT={product.pk} FIELD={label} NAME={name} CANDIDATES={joined}"
                    )
                    continue

                source = candidates[0]
                self.stdout.write(
                    f"REPAIR_CANDIDATE PRODUCT={product.pk} FIELD={label} NAME={name} SOURCE={source} DEST={expected}"
                )
                if options["apply"]:
                    expected.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, expected)
                    if not expected.is_file() or expected.stat().st_size <= 0:
                        raise CommandError(f"Repair copy failed: {expected}")
                    if _sha256(source) != _sha256(expected):
                        raise CommandError(f"Repair checksum mismatch: {expected}")
                    repaired += 1
                else:
                    missing += 1

        self.stdout.write(f"CHECKED={checked}")
        self.stdout.write(f"MISSING={missing}")
        self.stdout.write(f"REPAIRED={repaired}")
        self.stdout.write(f"AMBIGUOUS={ambiguous}")
        self.stdout.write(f"MODE={'APPLY' if options['apply'] else 'DRY_RUN'}")
        if options["strict"] and missing:
            raise CommandError(f"Media audit has {missing} unresolved missing file(s).")
        self.stdout.write("PHASE49_1_MEDIA_AUDIT=OK")
