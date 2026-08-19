# Phase49.3B — Windows Local QA Gate

Status: **GitHub implementation + CI complete / Windows live-provider and visual QA pending / Production untouched**

This file is the permanent operator gate for Phase49.3B. It exists to prevent out-of-band patching and to keep the delivery sequence identical across phases.

## Mandatory delivery sequence

`GitHub Epic → CI/Self-Test → Windows fetch/switch/pull → Local backup/migration/test → Visual/Data QA → explicit user approval → Production backup/deploy/migrate/restart/smoke`

Rules:
- Code changes are committed to GitHub first. Do not apply ad-hoc replacement files to the Windows checkout.
- Windows checkout is `D:\projects\3DPrintHub`.
- Active branch is `epic/phase49-unified-product-slider-sync`.
- Production is forbidden until Local QA is explicitly approved by the user.
- Never reset Local/Production DB, media, private media, `.env`, API keys, or Catalog Center persistent data to solve a code problem.
- Real provider keys stay on Windows secret storage/environment and are never committed.

## Tested runtime baseline

Phase49.3B clean runtime baseline:

`c0ac5a9f98e157a5a50b6e1cf8021265a6246e28`

Phase49.3A tested ancestry baseline remains:

`d40dbe9a0a26418dcbeebad0b462a32197b9061c`

Final CI validation:
- Workflow: `Phase49 Epic Unified CI`
- Run: `32248104376`
- Job: `96052943408`
- Result: `SUCCESS`
- CI head: `359e954007cc9868c0b3437515e69bf565f2aed4`
- CI base: `c0ac5a9f98e157a5a50b6e1cf8021265a6246e28`

The CI head only carries the validation probe; the runtime implementation is on the Epic baseline/ancestry.

## 1. Close runtime before pull

Close Catalog Center and any Django `runserver` process.

## 2. Git gate

```powershell
cd "D:\projects\3DPrintHub"

git status --short
```

The output must be empty before switching/pulling.

```powershell
git fetch --prune origin
git switch epic/phase49-unified-product-slider-sync
git pull --ff-only origin epic/phase49-unified-product-slider-sync
git rev-parse HEAD
git status --short
```

Verify tested runtime ancestry:

```powershell
git merge-base --is-ancestor `
  c0ac5a9f98e157a5a50b6e1cf8021265a6246e28 `
  HEAD

if ($LASTEXITCODE -ne 0) {
    throw "PHASE49.3B TESTED RUNTIME BASELINE IS MISSING"
}

Write-Host "PHASE49.3B TESTED RUNTIME BASELINE = OK" -ForegroundColor Green
```

Also preserve 49.3A ancestry:

```powershell
git merge-base --is-ancestor `
  d40dbe9a0a26418dcbeebad0b462a32197b9061c `
  HEAD

if ($LASTEXITCODE -ne 0) {
    throw "PHASE49.3A TESTED BASELINE IS MISSING"
}

Write-Host "PHASE49.3A TESTED BASELINE = OK" -ForegroundColor Green
```

## 3. Django DB inspection before migration

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py showmigrations store | Select-String "0031|0032"
python manage.py showmigrations website | Select-String "0022"
python manage.py migrate --plan
```

Expected Phase49 migrations:
- `store.0031_phase49_rich_material_colors` — may already be applied from 49.3A/desktop-options work.
- `website.0022_phase49_hero_media_presentation` — Phase49.3B additive Hero presentation fields.
- `store.0032_phase49_slider_media_profile` — Phase49.3B additive Product Profile media persistence fields.

`makemigrations --check --dry-run` must report `No changes detected`.

The expected Phase49.3B migrations are additive. Do not proceed if the migration plan contains an unexpected destructive operation.

## 4. Backup before applying any pending migration

If any expected migration above is pending:

```powershell
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Backup = "D:\projects\3dprinthub-backups\phase49-3b-$Stamp"
New-Item -ItemType Directory -Force -Path $Backup | Out-Null

Copy-Item `
  "D:\projects\3DPrintHub\db.sqlite3" `
  "$Backup\db.sqlite3.before_phase49_3b" `
  -Force

$CatalogDataCandidates = @(
  "D:\projects\3dprinthub_catalog_center",
  "D:\projects\3dprinthub-catalog-manager"
)

foreach ($Source in $CatalogDataCandidates) {
    if (Test-Path $Source) {
        $Name = Split-Path $Source -Leaf
        Copy-Item $Source "$Backup\$Name" -Recurse -Force
    }
}

Write-Host "BACKUP=$Backup" -ForegroundColor Green
```

After confirming the plan is expected:

```powershell
python manage.py migrate
```

Then re-check:

```powershell
python manage.py showmigrations store | Select-String "0031|0032"
python manage.py showmigrations website | Select-String "0022"
```

All three expected rows must be `[X]` after migration.

## 5. Django targeted regression gate

From project root:

```powershell
python manage.py test `
  store.test_phase49_unified_sync `
  store.test_phase49_unified_import_e2e `
  store.test_epic49_operator_publish `
  store.test_phase49_3b_profile_media `
  catalog_bridge.test_phase49_unified_bridge `
  catalog_bridge.tests.test_epic49_contract `
  website.test_phase49_persian_sales_hero `
  website.test_phase49_3b_hero_media `
  website.test_phase49_2c_hero_studio `
  -v 2
```

Then the full Django suite:

```powershell
python manage.py test -v 1
```

## 6. Windows Catalog Center targeted gate

```powershell
cd "D:\projects\3DPrintHub\catalog_center"

python -m unittest -v tests.test_phase49_unified_desktop
python -m unittest -v tests.test_phase49_persian_sales_slider
python -m unittest -v tests.test_epic49_readiness_wizard
python -m unittest -v tests.test_phase49_3b_ai_diagnostics
python -m unittest -v tests.test_phase49_3b_diagnostics_identity
python -m unittest -v tests.test_phase49_3b_guided_wizard
python -m unittest discover -s tests -p "test_*epic49*.py" -v
python launch.py --verify-only
```

Required runtime markers:

```text
UX87_EPIC49_WORKSPACE_ROUTING=ENABLED
EPIC49_DUAL_PUBLISH_TARGETS=ENABLED
EPIC49_LOCAL_PUBLISH_SQLITE_GUARD=ENABLED
EPIC49_MATERIAL_COLOR_PICKER=ENABLED
EPIC49_READINESS_WIZARD=ENABLED
EPIC49_SEO_REFERENCE_SYNC=ENABLED
EPIC49_GUIDED_WIZARD_7_STAGE=ENABLED
EPIC49_HERO_MEDIA_STUDIO=ENABLED
EPIC49_AI_PROVIDER_HUB=ENABLED
EPIC49_AI_PRODUCT_CONTEXT=ENABLED
EPIC49_AI_COST_TOMAN=ENABLED
EPIC49_OPENROUTER=ENABLED
EPIC49_PERSISTENT_DIAGNOSTICS=ENABLED
EPIC49_DIAGNOSTIC_LOG_UI=ENABLED
EPIC49_AUDIT_IDENTITY=ENABLED
EPIC49_AI_COST_PERSISTENCE=ENABLED
ACTIVE_RELEASE_VERIFIED=OK
```

Only if these gates pass:

```powershell
python launch.py
```

## 7. Visual QA — Product Workspace

Open the same real product used during 49.3A (Flexi Gecko when available in the local catalog data).

Canonical seven stages:
1. `اطلاعات پایه`
2. `سفارش، قیمت و گزینه‌ها`
3. `تصاویر`
4. `محتوا و SEO`
5. `منبع و مجوز`
6. `اسلایدر صفحه اصلی`
7. `بررسی و انتشار`

Expected states:
- complete: `✅`
- incomplete required: `❌ ★`
- future/locked: `🔒`
- Next disabled until current-stage required fields are complete.
- Previous/Next controls at the bottom of each stage.

Stage 1 AI must be title-only and must not overwrite unrelated fields.

Stage 4 AI owns full ecommerce content + sales SEO.

Stage 6 AI owns Slider SEO/media.

## 8. AI Provider Hub live QA

Each provider must have its own independent card:
- `AvalAI`
- `OpenRouter`
- `OpenAI Direct`

Validate with the operator's real Windows secrets:
- independent API key/model selection
- model list
- live test
- status
- supported balance/cost display
- OpenRouter free router/model detection
- OpenRouter optional Management Key credit query
- AvalAI credit/transaction-cost lookup when provider endpoints return it
- OpenAI ordinary key is not mislabeled as remaining balance; optional Admin Key is organization spend only

Re-run the previously failing AvalAI structured-content request. The HTTP 400 `invalid_request`/unsupported-`response_format` compatibility fallback must retry without `response_format` and client-validate JSON.

After every live request inspect `AI Request Log` for:
- provider/model
- operation/endpoint
- Request ID
- HTTP status
- duration
- prompt/completion/total tokens when returned
- USD cost when returned
- exact/estimated Toman cost when available
- sanitized error/response summary

No API key or Authorization secret may appear in the DB log/export.

## 9. Program Log / audit QA

Verify searchable persistent fields:
- operator
- workstation
- session
- product ID
- area/action/status
- source file/module
- changed field names
- runtime errors

Export a diagnostic bundle and confirm it can be shared without secrets.

## 10. Hero Media Studio QA

Stage 6 must expose:
- presentation mode
- contain/cover
- focal position
- image scale
- X/Y position
- background mode/color/blur
- Desktop max width/height
- Mobile max width/height
- Desktop/Mobile preview

Product-safe default:

`product_fit + contain`

Important persistence test:
1. keep homepage slider disabled for the product;
2. change Hero framing values;
3. save;
4. close/reopen the product;
5. confirm values survive on ProductCatalogProfile even before enabling the slide.

## 11. First real end-to-end Local Publish

When Wizard/AI/Hero/Logs are visually correct, complete one real product and use only:

`🧪 انتشار آزمایشی روی کامپیوتر`

Verify:

`Windows → Local batch → Django SQLite Product → ProductCatalogProfile → HomepageHeroSlide → Home/Admin`

Inspect the local Home page in both desktop and mobile dimensions. For the selected product Hero, use `product_fit + contain` first so the full product remains visible.

## 12. Forbidden at this gate

Do **not** use:

`🌐 انتشار واقعی روی سایت اصلی`

Do not run Production migrate/collectstatic/restart/deploy commands.

Production remains blocked until Visual/Data QA and explicit user approval are recorded.