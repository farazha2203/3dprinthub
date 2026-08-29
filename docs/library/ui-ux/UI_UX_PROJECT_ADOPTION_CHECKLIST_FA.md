# UI/UX Project Adoption Checklist

## قبل از طراحی

- [ ] User/task اصلی مشخص است.
- [ ] business outcome مشخص است.
- [ ] current UI و design system بررسی شده.
- [ ] مشابه داخلی در پروژه و shared patterns بررسی شده.
- [ ] data scale واقعی تخمین زده شده.
- [ ] permission/RBAC states مشخص‌اند.
- [ ] RTL/LTR و language contract مشخص است.
- [ ] loading/error/empty/success requirements مشخص‌اند.
- [ ] mobile/responsive priority مشخص است.
- [ ] accessibility requirement مشخص است.

## Information architecture

- [ ] navigation بر اساس task/user mental model است.
- [ ] page title و current location واضح‌اند.
- [ ] primary action یک مورد واضح است.
- [ ] secondary actions de-emphasized هستند.
- [ ] dependencyها به صورت wizard/setup steps در صورت نیاز نشان داده می‌شوند.
- [ ] search/filter/sort فقط در جای لازم و با state visible هستند.

## Forms

- [ ] field غیرضروری حذف شده.
- [ ] label visible است.
- [ ] placeholder جای label نیست.
- [ ] paste/copy/keyboard usable است.
- [ ] input type/mask مناسب است.
- [ ] error message actionable است.
- [ ] validation timing مشخص است.
- [ ] destructive/irreversible submission confirmation دارد.
- [ ] multi-step form progress و resume behavior مشخص است.

## Visual system

- [ ] spacing scale رعایت شده.
- [ ] type scale رعایت شده.
- [ ] semantic colors رعایت شده.
- [ ] contrast کافی است.
- [ ] hierarchy با بیش از یک cue ساخته شده.
- [ ] border/shadow فقط با purpose.
- [ ] icon style consistent.
- [ ] empty state intentional است.

## Data-heavy Admin/Dashboard

- [ ] metricها real هستند.
- [ ] number/date/currency alignment مناسب است.
- [ ] table pagination/virtualization متناسب با data volume است.
- [ ] filter state قابل مشاهده و reset است.
- [ ] sticky headers در table طولانی بررسی شده.
- [ ] bulk actions و selection واضح‌اند.
- [ ] permission-denied با missing-data اشتباه نمایش داده نمی‌شود.
- [ ] audit/history context در عملیات حساس قابل دسترس است.

## Accessibility

- [ ] keyboard-only flow.
- [ ] visible focus.
- [ ] labels/aria/semantic structure.
- [ ] non-color status cues.
- [ ] target size.
- [ ] text resize/zoom.
- [ ] reduced motion در صورت animation.
- [ ] screen-reader meaningful names برای actionهای حساس.

## Responsive

- [ ] کوچک‌ترین viewport اولویت task را حفظ می‌کند.
- [ ] table/card overflow deliberate است.
- [ ] buttons tap-friendly.
- [ ] sticky/fixed UI content را نمی‌پوشاند.
- [ ] long Persian/English strings layout را نمی‌شکنند.

## UX verification

- [ ] 5-second hierarchy test.
- [ ] squint/blur hierarchy test.
- [ ] happy path.
- [ ] validation/error path.
- [ ] empty/no-result path.
- [ ] permission-restricted path.
- [ ] slow/loading path.
- [ ] real-data density path.
- [ ] screenshot/visual review.
- [ ] automated tests where behavior can regress.

## Project-specific priorities

Farataz:
commerce clarity, ISP plan comparison, customer 360, marketing/CRM, payment trust, large admin tables, guided setup.

Asal:
visual storytelling, gallery speed, booking clarity, trust, mobile-first, photo-centric hierarchy, local SEO CTA.

3DPrintHub:
product attributes, material/color/pricing configurator, model galleries, admin forms, filters, quote/order flow.

Retoucher:
high-density creative workflow, keyboard/paste, batch operations, progress/error visibility, image preview fidelity.

Expert:
chart/dashboard hierarchy, data density, risk visibility, status confidence, latency/loading states, decision support without clutter.

IRWiFi:
network/customer operational clarity, service state, provisioning wizard, logs, error recovery, safe destructive actions.

ShahinFoolad:
trade/finance forms, wizard dependencies, price/inventory tables, Telegram/miniapp consistency, approval states.

AndroidAntiSpy:
trust and evidence, severity hierarchy, explainability, permission states, scan progress, false-positive handling, accessibility.

Legacy Vtiger Reference:
reference-only comparison; extract proven interaction patterns without treating legacy UI as a design target.
