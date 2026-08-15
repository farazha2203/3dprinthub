from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.ai_providers import AIProviderClient
from app.openai_content import AIContentService
from app.secure_secrets import get_provider_key, provider_key_source


def choose_provider(requested: str, root: Path) -> str:
    requested = (requested or "auto").strip().lower()
    if requested in {"avalai", "openai"}:
        return requested
    if get_provider_key("avalai", root):
        return "avalai"
    if get_provider_key("openai", root):
        return "openai"
    raise RuntimeError("No AvalAI/OpenAI API key was found in Credential Store, environment, or APIKEY*.txt.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="auto", choices=["auto", "avalai", "openai"])
    parser.add_argument("--project-root", default=r"D:\projects\3DPrintHub")
    parser.add_argument("--model", default="")
    args = parser.parse_args()

    root = Path(args.project_root)
    provider = choose_provider(args.provider, root)
    key = get_provider_key(provider, root)
    if not key:
        raise RuntimeError(f"{provider} API key not found")

    print(f"AI_PROVIDER={provider}")
    print(f"AI_KEY_SOURCE={provider_key_source(provider, root)}")
    client = AIProviderClient(provider, key, args.model)
    models = client.list_models()
    print(f"AI_MODELS_COUNT={len(models)}")
    model = client.choose_model(args.model)
    print(f"AI_MODEL_SELECTED={model}")
    live = client.test_connection(model)
    print(f"AI_LIVE_SAMPLE={live['sample']}")
    print("AI_LIVE_CONNECTION=OK")

    service = AIContentService(key, model, provider)
    source = {
        "source_title": "Adjustable modular desk organizer",
        "source_description": "A modular organizer for pens, cables and small desk accessories. Intended for indoor home and office use.",
        "technical_specs": {"application": "home and office organizer", "environment": "indoor"},
        "source_categories": ["Home", "Organization", "Desk accessories"],
        "estimated_weight_grams": 180,
    }
    pack = service.enrich_product(source, [{"slug":"home-decor","name":"خانه و دکور"}, {"slug":"organizer","name":"نظم‌دهنده"}], image_count=0, image_urls=[])
    required = ("title_fa", "short_description_fa", "description_fa", "seo_title_fa", "seo_description_fa", "hashtags_fa", "material_recommendations")
    missing = [name for name in required if not pack.get(name)]
    if missing:
        raise RuntimeError("Live content output missing fields: " + ", ".join(missing))
    print("AI_LIVE_TRANSLATION=OK")
    print("AI_LIVE_CONTENT_GENERATION=OK")
    print("AI_LIVE_SEO=OK")
    print("AI_LIVE_MATERIAL_RECOMMENDATION=OK")
    print("AI_PROVIDER_READY=OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"AI_LIVE_TEST_FAILED={type(exc).__name__}: {exc}", file=sys.stderr)
        raise
