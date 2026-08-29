# UI/UX Engineering Playbook

این Playbook از 14 منبع uiux1.zip مشتق شده و برای استفاده عملی در پروژه‌ها نوشته شده است.

## 1. Start from the task, not the shell

قبل از sidebar/header/theme، feature اصلی و سناریوی واقعی کاربر را طراحی کن.
برای هر صفحه پاسخ بده:
- کاربر برای چه آمده؟
- مهم‌ترین تصمیم یا عمل چیست؟
- چه داده‌ای برای آن لازم است؟
- چه چیزهایی می‌توانند بعداً با progressive disclosure نشان داده شوند؟

## 2. Cognitive load budget

هر صفحه باید بودجه پیچیدگی داشته باشد:
- تعداد انتخاب‌های همزمان را کم کن.
- داده مرتبط را group کن.
- label و value را نزدیک نگه دار.
- مسیرهای ثانویه را visually de-emphasize کن.
- از recall اجباری پرهیز کن؛ context لازم را در صفحه نشان بده.
- wizard برای dependency-heavy flow ترجیح دارد.

## 3. Visual hierarchy

Hierarchy را با ترکیب size, weight, contrast, spacing, position و grouping بساز.
فقط بزرگ‌کردن متن یا رنگ‌کردن همه‌چیز hierarchy نیست.

قاعده:
Primary -> Secondary -> Supporting -> Metadata.

برای تست:
- Squint/blur test.
- 5-second test.
- آیا بدون خواندن کامل متن، CTA و گروه‌بندی قابل تشخیص است؟

## 4. Layout and spacing system

- spacing scale تعریف‌شده داشته باش.
- فاصله نشان‌دهنده relationship باشد.
- از ambiguous spacing پرهیز کن.
- white space را فضای تلف‌شده ندان.
- grid ابزار است نه هدف.
- در data-heavy views density را آگاهانه کنترل کن.
- content مهم در viewport اولیه گم نشود.

## 5. Typography

- type scale محدود و سیستماتیک.
- body text خوانا با line-height و line-length مناسب.
- weightهای زیاد نساز.
- alignment ثابت و متناسب با زبان/RTL.
- headline, body, label, metadata نقش جدا داشته باشند.
- uppercase یا letter-spacing تهاجمی فقط با دلیل.
- اعداد و داده جدولی برای مقایسه alignment درست داشته باشند.

## 6. Color and contrast

- palette و semantic colors تعریف‌شده.
- رنگ تنها carrier معنی نباشد.
- success/warning/error/info همراه icon/text/state.
- dark mode یعنی فقط معکوس‌کردن رنگ نیست.
- pure black و grey کم‌کنتراست را کورکورانه استفاده نکن.
- accent color را برای توجه هدفمند نگه دار.
- contrast accessibility باید تست شود.

## 7. Depth, borders and shadows

- shadow باید elevation یا layer را توضیح دهد، نه decoration تصادفی.
- light source منطقی و consistent.
- border اضافی را با spacing/background grouping جایگزین کن اگر واضح‌تر است.
- overlap فقط وقتی hierarchy یا relationship را بهتر می‌کند.

## 8. Buttons and actions

- یک primary action در context.
- secondary و tertiary weight واضح.
- label باید action را توضیح دهد.
- target size کافی.
- destructive actions نیازمند friction/confirmation متناسب.
- loading/progress state برای action طولانی.
- disabled button را فقط وقتی علت آن برای کاربر روشن است استفاده کن؛ در غیر این صورت prerequisite را توضیح بده.

## 9. Forms

- single-column برای اکثر flowهای خطی.
- فقط field لازم.
- label همیشه visible؛ placeholder جای label نیست.
- required/optional policy consistent.
- input width و keyboard/input mode متناسب با داده.
- radio برای گزینه‌های کم؛ autocomplete برای list طولانی؛ toggle برای state binary فوری.
- related fields را group کن.
- validation زمان‌بندی‌شده و error message عملی.
- long form -> steps/wizard.
- paste/copy/keyboard workflow را بی‌دلیل مسدود نکن.

## 10. Navigation and findability

- navigation قابل پیش‌بینی و task-oriented.
- IA بر اساس مدل ذهنی کاربر، نه ساختار دیتابیس.
- breadcrumbs/context در hierarchy عمیق.
- hamburger فقط وقتی space/priority توجیه کند.
- active/current state واضح.
- search/filter/sort برای data scale واقعی.
- wayfinding: کاربر بداند کجاست، از کجا آمده و قدم بعدی چیست.

## 11. Cards, tables and dashboards

Cards:
- whole-card clickability فقط وقتی semantic واضح دارد.
- embedded links/actions conflict ایجاد نکنند.
- image hierarchy و content density کنترل شود.

Tables:
- numeric alignment مناسب.
- header واضح، sticky وقتی طولانی.
- pagination/virtualization متناسب با data volume.
- sort/filter state visible.
- empty/no-result/error/loading از هم تفکیک شوند.

Dashboard:
- metric واقعی و actionable.
- placeholder count ممنوع.
- priority و anomaly از decorative chart مهم‌تر است.

## 12. Content and microcopy

- content-first؛ lorem ipsum فقط low-fidelity موقت.
- plain language و sentence case.
- front-load important words.
- descriptive headings و bullets برای scanning.
- link text مقصد را توضیح دهد.
- error message: چه شد + چرا اگر معلوم است + چه کار کند.
- terminology در کل محصول ثابت.

## 13. Scanning patterns

F-pattern:
برای صفحات متن/لیست متراکم، اطلاعات حیاتی را در شروع خطوط و بخش‌های بالاتر قرار بده.

Z-pattern:
برای landing/marketing ساده، hierarchy و CTA را در مسیر دید طبیعی قرار بده.

هیچ pattern بدون توجه به content/task اجبار نیست.

## 14. Accessibility

حداقل:
- keyboard navigation.
- visible focus.
- semantic labels.
- form association.
- color-independent states.
- contrast.
- tap/click target.
- readable text.
- reduced motion consideration.
- alt/context برای تصاویر meaningful.
- error summary برای formهای مهم.

## 15. Consistency and design systems

Consistency = familiarity, نه uniformity.
Design system باید شامل:
- tokens: spacing, type, radius, color, elevation.
- components.
- states.
- content conventions.
- accessibility rules.
- responsive behavior.
- examples and anti-patterns.

## 16. UX process

Product definition -> Research -> Analysis -> Design -> Implementation -> Live -> Measure/Iterate.

Documentation باید decision را جلو ببرد، نه اینکه فقط سند تولید کند.

## 17. Decision-making under uncertainty

برای تصمیم UI مبهم:
1. مسئله و فرض‌ها را بنویس.
2. گزینه‌ها را مشخص کن.
3. معیارها: usability, business value, accessibility, effort, risk.
4. uncertainty را explicit کن.
5. prototype/test کوچک اجرا کن.
6. نتیجه و evidence را ثبت کن.

## 18. Psychological principles with highest project value

- Fitts' Law: target مهم بزرگ/نزدیک.
- Hick's Law: انتخاب همزمان کمتر.
- Serial Position: ابتدا/انتها بیشتر دیده می‌شود.
- Gestalt proximity/similarity/common fate: grouping قابل‌فهم.
- Recognition over Recall.
- Progressive Disclosure.
- Signal-to-Noise Ratio.
- Aesthetic-Usability Effect، بدون قربانی usability.
- Mental Models.
- Feedback Loop.
- Affordance and Signifiers.
- Error Forgiveness.
- 80/20 Rule.
- Visibility and Wayfinding.

## 19. Mandatory states matrix

هر component/action مهم حداقل بر اساس نیاز:
Default | Hover | Focus | Active | Selected | Loading | Empty | No-result | Error | Success | Disabled | Read-only | Offline/Unavailable.

## 20. Review gate

UI تغییرکرده قبل از قبول:
- task success.
- visual hierarchy.
- RTL/LTR.
- mobile/tablet/desktop.
- keyboard/focus.
- contrast.
- empty/loading/error/success.
- long text and long numbers.
- real data density.
- destructive action safety.
- no dead controls.
- no placeholder operational metrics.
