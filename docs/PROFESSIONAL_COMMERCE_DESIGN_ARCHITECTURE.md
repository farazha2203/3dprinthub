# 3DPrintHub Professional Commerce Design Architecture

Updated: 2026-09-01
Status: SOURCE-GROUNDED DESIGN STANDARD / IMPLEMENTATION INCREMENTAL
Repository: farazha2203/3dprinthub

## Purpose

3DPrintHub is a specialist 3D-printing commerce and service platform. The UI must communicate technical competence, trust, product quality, material knowledge and clear purchase/custom-order paths. Visual novelty is secondary to comprehension, confidence, conversion and performance.

This standard is derived from owner-supplied File Library references reviewed on 2026-09-01. The uploaded webdesign1.zip binary was not exposed as a readable sandbox archive in this session, but constituent books are indexed and readable individually in the owner's File Library. No claim is made that the ZIP binary itself was extracted.

## Reviewed source set

- Practical UI, 2nd Edition - Adham Dannaway
- Lean UX
- UI/UX Web Design Simply Explained
- 100 Things Every Designer Needs to Know About People
- Designing Brand Identity - Alina Wheeler
- 3D Web Development with Three.js and Next
- Modern Web Applications with NextJS
- NextJS Cookbook
- Internet and Web Application Security, 3rd Edition

Framework-specific examples are treated as principles only. The current Django architecture remains authoritative; this document does not authorize a Next.js or React rewrite.

## 1. Information architecture before decoration

Every surface must be organized around the user's task.

Public commerce path:
1. Discover a product/service.
2. Understand what it is and whether it solves the need.
3. Evaluate technical fit, material, size, color and production constraints.
4. See price or pricing method clearly.
5. Build trust through source/license/specification/production facts.
6. Select a variant or request a custom quote.
7. Complete the primary CTA with minimum ambiguity.

Admin/Desktop path:
1. See state.
2. Find/filter.
3. Inspect.
4. Edit.
5. Validate.
6. Publish/archive/reject.
7. Audit history/result.

Large control walls are prohibited when tabs, progressive disclosure or task workspaces can reduce cognitive load.

## 2. Design-system rule

Use one maintainable design language rather than page-specific styling.

Canonical token groups:
- typography scale;
- spacing scale;
- border radius;
- surface/elevation;
- semantic colors;
- control heights;
- focus states;
- icon sizes;
- responsive breakpoints;
- motion duration/easing.

Reusable component families:
- primary/secondary/destructive buttons;
- input/select/search/filter controls;
- product cards;
- technical badges;
- price/offer rows;
- status chips;
- tabs;
- data tables;
- galleries;
- empty/loading/error states;
- dialogs/drawers;
- product specification groups;
- trust/provenance blocks.

Each reusable component should document appearance, placement and when it should be used.

## 3. Persian typography

Typography is a functional hierarchy, not decoration.

Rules:
- use a small, reusable type scale;
- maintain clear contrast between page title, section title, card title, body, label and metadata;
- do not use display styling for long Persian text;
- avoid thin weights for important content;
- keep line height comfortable for Persian/RTL reading;
- technical Latin tokens, model names, dimensions and identifiers may use LTR spans inside RTL layouts;
- do not shrink secondary information until it becomes difficult to read;
- tables and dense admin screens use compact but readable typography, not microscopic text.

Exact font binaries remain outside public Git according to project licensing rules. Runtime font choice must use licensed/private assets already approved by the project or safe system fallbacks.

## 4. Color, hierarchy and trust

Color must communicate hierarchy and state, not become decoration.

Rules:
- one clear primary action per decision area;
- secondary actions are visibly subordinate;
- destructive/reject/delete actions are separated from primary commerce actions;
- do not communicate status by color alone: pair color with text/icon/state;
- technical and commerce pages use restrained surfaces with high legibility;
- brand accent is used to guide attention, not to paint every component;
- maintain accessible text/background contrast.

A specialist industrial store should look precise, credible and technically calm rather than gaming-like or excessively neon.

## 5. Product-card standard

A product card must help a user decide whether to inspect the product.

Minimum useful content:
- primary image with stable aspect ratio;
- Persian title;
- concise category/use-case/material context where available;
- price/range/quote state without inventing values;
- availability or production state when meaningful;
- optional small trust/technical badge;
- one clear card interaction.

Avoid dense paragraphs, duplicate CTAs and decorative metadata walls.

## 6. Product-detail architecture

Above the fold:
- gallery/primary image;
- product identity;
- price or explicit quote state;
- variant/profile/material/color selection needed for the next action;
- lead-time/production cue where available;
- primary CTA;
- essential trust facts.

Below the primary decision area use progressive disclosure/tabs:
- overview/description;
- technical and print specifications;
- sizes/profiles;
- materials/colors/offers;
- production time/weight;
- source/license/provenance when applicable;
- delivery/order guidance;
- FAQ/consultation.

All critical SEO/product content must remain present in server-rendered HTML. Tabs are enhancement and must not hide content from no-JS/accessibility paths.

## 7. 3D experience

3D is a specialist advantage, not a mandatory tax on every page.

Rules:
- 3D viewer is optional and lazy-loaded;
- product image and core text remain the initial experience;
- do not block LCP or purchase controls on 3D assets;
- viewer controls are predictable and documented;
- provide a non-3D fallback;
- test mobile GPU/memory behavior;
- respect reduced-motion preferences where animation is used.

Use 3D selectively for products where spatial inspection materially improves purchase confidence.

## 8. Responsive behavior

Do not design only desktop and mobile endpoints.

Verify intermediate widths and real content:
- long Persian titles;
- long model names;
- price labels;
- multi-color/material choices;
- wide technical tables;
- galleries;
- admin filters/actions.

Prefer reflow, stacking, drawers and horizontal data strategies over clipped controls or nested scroll traps.

## 9. Motion and effects

Effects must explain state or hierarchy.

Allowed purposes:
- hover/focus affordance;
- tab/view transition;
- lightweight gallery feedback;
- loading/progress feedback;
- confirmation/state change.

Avoid:
- continuous decorative motion;
- large parallax on commerce-critical sections;
- animation that delays controls;
- expensive effects on long product grids;
- motion that substitutes for information.

## 10. SEO and content presentation

Every indexable commerce page should support:
- accurate unique title;
- accurate meta description;
- crawlable visible text;
- canonical URL;
- appropriate structured data consistent with visible content;
- descriptive image alt where the image carries product information;
- stable image dimensions and optimized formats;
- meaningful internal links;
- fast initial rendering.

Product/source metadata from Catalog Center must not be turned into fabricated marketing claims.

## 11. Performance budget mindset

Use progressive enhancement:
- server-render critical content;
- lazy-load below-fold imagery and optional 3D;
- avoid unnecessary JavaScript;
- keep component/style reuse high;
- avoid duplicate client data fetches;
- preserve bounded product paging;
- measure before adding visually expensive effects.

## 12. Admin and Catalog Center

Admin/Desktop should share the same information hierarchy principles but remain productivity-first:
- task tabs instead of long mixed forms;
- visible current state;
- compact reusable controls;
- keyboard-friendly workflows;
- large tables with usable row height and headers;
- preview image plus essential metadata;
- explicit bulk-action scope;
- reversible archive/reject where existing business rules require it;
- clear progress/error diagnostics.

Do not force storefront decoration into operator tools.

## 13. Acceptance criteria for visual phases

A visual phase is not complete until:
- desktop + intermediate + mobile layouts are checked;
- keyboard focus and tab interaction are checked;
- primary/secondary/destructive actions are visually distinct;
- content remains usable without color-only state;
- long Persian content does not clip;
- product images keep stable layout;
- no new uncontrolled scroll wall is introduced;
- structured data and visible content remain consistent;
- existing business/pricing authority is unchanged;
- performance-sensitive optional features are lazy/progressive;
- focused regressions and framework checks pass.

## Current implementation direction

Phase49.3I.47 already moves Product, Acquisition and Profile/Pricing operator surfaces toward task-oriented tabs.

Next visual work should apply this design standard incrementally:
1. owner Local acceptance of 3I.47;
2. Catalog Center typography/spacing/status polish, including investigation of the current Qt font warning;
3. Admin design-system consolidation;
4. Storefront category/product/custom-order architecture;
5. product-detail technical/trust hierarchy;
6. performance-safe optional 3D preview;
7. SEO/accessibility/performance regression gates.

Production remains unchanged until the normal GitHub -> Local -> Host -> Production workflow is satisfied.
