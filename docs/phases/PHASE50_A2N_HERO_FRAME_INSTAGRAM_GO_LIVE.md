# PHASE50.A.2N — Hero Clean Frame + Instagram Go-Live

Status: LOCAL_TESTED / GITHUB+PRODUCTION NEXT
Date: 2026-09-19

## Scope
Close the remaining homepage Hero visual defect, deploy A2M authoritative Product re-publish, then use the resulting current Site revision as the sole source for Instagram Feed + Story + SEO metadata.

## Hero acceptance
- Keep original Tympanus/Codrops Slicebox 3D cuboid engine.
- Keep arrows and dots.
- Remove the legacy raster shadow element entirely; no dark drop-shadow or rectangular lower edge.
- Preserve accepted 1280px desktop frame and mobile image-priority behavior.
- Public HTML/CSS/JS cache key 50.9.0.
- Desktop/mobile Chromium: HTTP 200, no JS error, no shadow DOM, 3D Next transition still produces cuboids/sides.

## Product re-publish acceptance
- Same Site Product identity.
- Latest Windows sales_profiles_json is the only active Variant authority.
- Historical rows remain stored but inactive.
- Current selected/finalized media replaces ProductImage state exactly.
- #625 acceptance requires exactly three active CC-P39 rows and zero stale active legacy rows.

## Instagram acceptance
- Site-first: do not publish social from a stale Product ACK.
- Feed uses public compatibility media when provider cannot ingest canonical WebP.
- Every feed image carries non-empty Alt Text.
- Caption uses Product SEO title/description, factual sales bullets/specs, UTM Product URL, nationwide shipping CTA and bounded relevant hashtags.
- Companion Story uses 1080x1920 Gold/Navy IRANSans style and direct Product link.
- Successful Feed/Story provider receipts are mandatory before declaring Instagram complete.
- Highlight target is recorded from the approved taxonomy; final Instagram Highlight placement remains operator-required because Buffer API has no Highlight mutation.

## Safety
No Production source edits outside GitHub-first runner. No duplicate social post for an already-receipted Site revision. Fresh Local Catalog + Host source/env/MySQL backups precede irreversible acceptance writes.
