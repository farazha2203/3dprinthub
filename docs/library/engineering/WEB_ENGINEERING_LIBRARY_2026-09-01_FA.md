# Shared Web Engineering Library — 2026-09-01

این سند Canonical مشترک برای پروژه‌های مالک Repository است و دانش مشتق‌شده از مجموعه منابع Web/Frontend/Backend/Security/Automation را ثبت می‌کند.

## قانون منبع و کپی‌رایت

- PDF/ebook اصلی داخل Repository Commit نمی‌شود.
- Source locator فقط نام دقیق فایل در **Owner ChatGPT File Library** است.
- در Repository فقط عنوان، سرفصل، خلاصه، rule، checklist، public companion source و adoption note نگه‌داری می‌شود.
- وضعیت واقعی Repository/Runtime/Host/Database و مستندات رسمی همان نسخه همیشه از مثال کتاب بالاتر است.
- هیچ dependency، syntax، API، security setting یا معماری فقط به دلیل حضور در کتاب نصب/کپی نمی‌شود؛ compatibility و test اجباری است.

## Corpus تأییدشده

۱۰ PDF / ۴۸۱۹ صفحه، بررسی فردی در File Library در 2026-09-01.

| # | عنوان | نویسنده / سال | صفحات | حوزه | Source locator |
|---|---|---|---:|---|---|
| 1 | 3D Web Development with Three.js and Next.js: Creating end-to-end web applications that contain 3D objects | Andrei Tazetdinov / 2025 | 587 | Three.js, R3F, Next.js, Storybook, 3D UX | `3D_Web_Development_with_Threejs_and_Next_-_Andrei_Tazetdinov.pdf` |
| 2 | Modern Web Applications with Next.JS | Shubham Jain, Mathew Dony Chittezhath / 2023 | 402 | Next.js, rendering, routing, APIs, auth, deployment | `Modern_Web_Applications_with_NextJS_-_Shubham_Jain.pdf` |
| 3 | React in Depth | Morten Barklund / 2024 | 434 | React architecture, performance, TypeScript, testing, UI library | `React_in_Depth_-_Morten_Barklund.pdf` |
| 4 | Build AI-Enhanced Web Apps: How to get reliable results with React, Next.js, and Vercel | Theo Despoudis / 2026 | 394 | AI UX, streaming, structured output, RAG, MCP, security | `Build_AI-Enhanced_Web_Apps_-_Theo_Despoudis.pdf` |
| 5 | Grokking Web Application Security | Malcolm McDonald / 2024 | 336 | Browser/server/auth/session/upload/injection/SSRF/incident response | `Grokking_Web_Application_Security_-_Malcolm_McDonald.pdf` |
| 6 | Mastering Django ORM: Performance Tuning and Advanced Query Optimization | Afsal MS / 2026 | 513 | ORM, query optimization, transactions, profiling, async | `Mastering_Django_ORM_-_Afsal_MS.pdf` |
| 7 | PowerShell 7 for IT Professionals: A Guide to Using PowerShell 7 to Manage Windows Systems | Thomas Lee / 2020 | 616 | PowerShell 7, Windows administration, WMI/CIM, reporting | `PowerShell_7_for_IT_Pros_-_Thomas_Lee.pdf` |
| 8 | Mastering PowerShell 7.4 and Beyond | Patrick Radcliffe / 2024 | 202 | scripting, remoting, DSC, modules, CI/CD, IaC | `Mastering_PowerShell_74_and_Beyond_-_Patrick_Radcliffe.pdf` |
| 9 | Internet and Web Application Security, Third Edition | Mike Harwood, Ron Price / 2024 | 934 | risk, hardening, OWASP, web attacks, deployment/compliance | `Internet_and_Web_Application_Security_3rd_Edition_-_Mike_Harwood.pdf` |
| 10 | Web Application Security: A Beginner’s Guide | Bryan Sullivan, Vincent Liu / 2012 | 401 | foundational appsec, authz/authn, SOP, XSS/CSRF, DB/files, SDL | `Web_Application_security_-_Bryan_Sullivan.pdf` |

---

## 1) 3D Web Development with Three.js and Next.js — 2025

### سرفصل‌های تأییدشده
کتاب 24 فصل دارد. محورهای اصلی:
- Industrial application evolution و کاربرد web سه‌بعدی.
- قابلیت‌های web برای industrial/multipurpose apps.
- ابزارها: Three.js، Next.js، AWS Amplify، Storybook، Tailwind.
- setup ابزارها.
- مبانی 3D و Three.js.
- geometries/materials.
- lights/shadows.
- interaction و integration با React/Next/R3F.
- hosting/auth/data workflows با AWS Amplify.
- Chapter 21: Data Storage and Management with AWS Amplify.
- Chapter 22: Real-time Functionality with AWS Amplify.
- Chapter 23: Create the UI Design System with Storybook.
- Chapter 24: Final Requirements and Recommendations.

### public companion
- https://github.com/bpbpublications/3D-Web-Development-with-Three.js-and-Next.js

### نکات قابل‌استفاده
- 3D باید **مسئله واقعی** حل کند: product visualization، spatial data، interactive training، portfolio showcase؛ صرفاً decorative WebGL دلیل کافی نیست.
- R3F امکان componentization صحنه 3D در معماری React را می‌دهد.
- Storybook برای 3D component هم مفید است: state/props/stories جدا و visual regression.
- code splitting/lazy loading برای sceneهای سنگین ضروری است.
- Canvas/3D نباید semantic HTML، متن SEO-critical، navigation یا CTA اصلی را جایگزین کند.
- باید fallback برای reduced motion / low-end device / WebGL failure وجود داشته باشد.

### Admission Gate اجباری برای Three.js
قبل از اضافه‌کردن Three.js/R3F:
1. ارزش واقعی 3D چیست؟
2. آیا CSS/SVG/image/video سبک‌تر همان نتیجه را می‌دهد؟
3. JS bytes، CPU/GPU، memory و LCP/INP impact اندازه‌گیری شده؟
4. آیا محتوای اصلی بدون Canvas قابل index/access است؟
5. mobile/low-power fallback وجود دارد؟
6. lazy-load و offscreen pause وجود دارد؟
7. accessibility و keyboard path مستقل وجود دارد؟

---

## 2) Modern Web Applications with Next.JS — 2023

### 13 فصل
1. Introduction to Web Applications with Next.js and JavaScript
2. Recall React
3. Next.js Fundamentals
4. Next.js new version — Core Concepts
5. Optimizing Next.js Applications
6. Understanding Routing in Next.js
7. State Management in Next.js
8. RESTful and GraphQL API Implementation
9. Using Different Types of Databases
10. Client-Side and Server-Side Rendering in Next.js
11. Securing App with Next Auth
12. Developing a CRUD Application with Next.js
13. Deployment Architecture

### public companion
- https://github.com/OrangeAVA/Modern-Web-Applications-with-Next.JS

### نکات قابل‌استفاده
- rendering strategy باید بر اساس ماهیت صفحه انتخاب شود، نه یک mode برای همه‌چیز.
- routing، data boundary و deployment architecture باید از ابتدا با SEO/performance هماهنگ باشند.
- auth در framework نباید جای authorization در backend/domain را بگیرد.
- UI library/database examples کتاب فقط example هستند؛ نصب MUI/TypeORM یا stack مشابه بدون نیاز پروژه ممنوع.

### Freshness rule
کتاب 2023 است؛ APIهای Next.js سریع تغییر کرده‌اند. برای هر پروژه:
**actual package-lock + official current Next.js docs > book API examples**.

---

## 3) React in Depth — Morten Barklund — 2024

### 14 فصل
1. Developer’s guide to the React Ecosystem
2. Advanced component patterns
3. Optimizing React performance
4. Better code maintenance with developer tooling
5. TypeScript: Next-level JavaScript
6. Mastering TypeScript with React
7. CSS in JavaScript
8. Data management in React
9. Remote data and reactive caching
10. Unit-testing React
11. React website frameworks
12. Project: expense tracker with Remix
13. Project: Create a React UI library
14. Project: Develop a word game in React

### موضوعات مهم
- Provider pattern، Composite pattern، Summary pattern.
- render behavior و minimizing re-render.
- memoization و dependency arrays.
- ESLint/formatter/React DevTools Profiler.
- TypeScript generics، typed hooks/context/reducer/ref.
- state vs remote-data/cache.
- testing.
- UI library و Storybook-oriented component development.

### قواعد مشترک React
- Memoization پیش‌فرض نیست؛ اول profiler/measurement.
- component API باید state و ownership واضح داشته باشد.
- global provider فقط برای state واقعاً shared؛ provider cascade بی‌دلیل ممنوع.
- remote server data از ephemeral UI state جدا باشد.
- component reusable باید حالات default/hover/focus/active/loading/empty/error/success/disabled/read-only را پوشش دهد.
- component library باید visual catalogue و usage docs داشته باشد.
- از arbitrary library sprawl جلوگیری شود؛ lockfile و architecture پروژه تعیین‌کننده‌اند.

---

## 4) Build AI-Enhanced Web Apps — Theo Despoudis — 2026

### ساختار
**Part 1 — Basic generative AI web apps**
1. Using generative AI in web apps
2. Building your first generative AI web application
3. Connecting AI models with the Vercel AI SDK
4. Managing conversation and state

**Part 2 — Advanced techniques and deployment**
5. Prompt engineering in web applications
6. Building AI workflows with LangChain.js
7. Document summarization and RAG
8. Testing and debugging techniques
9. Deployment and security

**Part 3 — Projects**
10. AI interview assistant
11. AI RAG agent

**Part 4**
12. Integrating web apps with the Model Context Protocol

### موضوعات کلیدی
streaming، multi-provider، multimodal UI، RSC/server actions، AI state vs UI state، structured output، tool calling، prompt versioning/testing، few-shot، embeddings، RAG، agents، eval/debugging، security، MCP.

### قواعد مشترک AI Web
- provider abstraction و model purpose ثبت شود.
- structured output باید schema-validate شود.
- timeout/retry/rate/cost budget اجباری.
- secrets هرگز client-side نشوند.
- RAG باید citation/grounding و stale-source policy داشته باشد.
- tool callها authorization/audit/idempotency لازم دارند.
- AI failure باید fallback/handoff قابل فهم داشته باشد.
- اگر backend پروژه Django/Python است، pattern را اقتباس کن؛ مجبورکردن پروژه به LangChain.js/Vercel stack ممنوع.

---

## 5) Grokking Web Application Security — Malcolm McDonald — 2024

### 15 فصل
1. Know your enemy
2. Browser security
3. Encryption
4. Web server security
5. Security as a process
6. Browser vulnerabilities
7. Network vulnerabilities
8. Authentication vulnerabilities
9. Session vulnerabilities
10. Authorization vulnerabilities
11. Payload vulnerabilities
12. Injection vulnerabilities
13. Vulnerabilities in third-party code
14. Being an unwitting accomplice
15. What to do when you get hacked

### پوشش عملی
XSS، CSRF، clickjacking، TLS/key compromise، brute force، SSO/MFA، credential storage، user enumeration، session hijacking/tampering، authorization modeling/testing، deserialization/XML/file upload/path traversal/mass assignment، RCE/SQL/NoSQL/LDAP/command/CRLF/regex injection، dependency risk، insecure config، SSRF، spoofing، open redirect، incident response.

### Security rules
- least privilege.
- four-eyes/review برای تغییر حساس.
- input validation + context-aware output handling.
- authn و authz جدا.
- upload allowlist/storage isolation.
- path traversal protection.
- dependency review.
- audit trail.
- incident prevention از خطای قبلی.

**Current OWASP ASVS/Cheat Sheets و framework advisories از کتاب اولویت بالاتری دارند.**

---

## 6) Mastering Django ORM — Afsal MS — 2026

### محور فصل‌ها
1. Introduction to Django ORM
2. Deep Dive into Model Fields
3. QuerySet/relationship/query fundamentals
4. Advanced Queries
5. Common Issues in Django ORM and Solutions
6. Forms to Models: a Django Cheat Sheet
7. Mastering Advanced Django ORM
8. Django ORM in the Async World

### موضوعات کلیدی
SQL inspection، field/index/constraint، QuerySet، relationship loading، aggregation/annotation، subquery، raw SQL، N+1، managers/custom QuerySets، signal trade-offs، transaction/savepoint، migration/data migration، query profiling، `.explain()`، async QuerySet methods.

### قواعد ORM
- قبل از optimize: query count + generated SQL + EXPLAIN.
- `select_related` / `prefetch_related` بر اساس relationship و access pattern.
- index فقط با workload evidence.
- business side effect پنهان در signals با احتیاط؛ explicit service flow برای عملیات حساس ترجیح دارد.
- transaction boundary کوتاه و مشخص.
- migration/data migration با backup/rollback/test.
- async ORM «خود query را سریع‌تر» نمی‌کند.
- Django-version و DB-engine compatibility اجباری؛ Django 6-only advice روی Django 5.2 کور اعمال نشود.

### public companion
- https://github.com/Apress/Mastering-Django-ORM

---

## 7) PowerShell 7 for IT Professionals — Thomas Lee — 2020

### 10 فصل
1. Setting Up a PowerShell 7 Environment
2. PowerShell 7 Compatibility with Windows PowerShell
3. Managing Active Directory
4. Managing Networking
5. Managing Storage
6. Managing Shared Data
7. Managing Printing
8. Managing Hyper-V
9. Using WMI with CIM Cmdlets
10. Reporting

### نکات مهم
modules/compatibility، VS Code، PowerShell Gallery، code signing، JEA، network/DNS/DHCP، storage/ACL، Hyper-V، WMI/CIM، performance/event reporting.

### قواعد PowerShell پروژه‌ها
- Microsoft docs و installed module version مقدم.
- Bash heredoc مثل `<<EOF` در native PowerShell ممنوع؛ از here-string استفاده شود.
- native command exit code با `$LASTEXITCODE` بررسی شود.
- destructive cmdlet قبل از target/backup/rollback ممنوع.
- JEA/least privilege برای remote administration.
- credential hardcode ممنوع.

### public companion
- https://github.com/doctordns/Wiley20

---

## 8) Mastering PowerShell 7.4 and Beyond — Patrick Radcliffe — 2024

### 12 فصل
1. Introduction to PowerShell
2. PowerShell Objects and Pipelines
3. PowerShell Scripting
4. New Features in PowerShell 7.4
5. Modernizing Your Scripts
6. PowerShell Remoting
7. PowerShell Desired State Configuration (DSC)
8. PowerShell Workflow
9. Automating System Administration Tasks
10. PowerShell for Cloud Management
11. Building PowerShell Tools and Modules
12. PowerShell and DevOps

### استفاده
parameters/validation/error handling/debugging، large-log/CSV performance، remoting security، DSC، modules/cmdlets، CI/CD، Git، IaC.

### Freshness rule
این کتاب **secondary** است. Workflow/DSC/cloud examples و هر syntax باید با Microsoft docs و runtime واقعی Verify شود.

---

## 9) Internet and Web Application Security, Third Edition — Harwood & Price — 2024

### ساختار موضوعی
- Part One: Internet/Web and need for security.
- security considerations for personal/SOHO and business.
- vulnerability/threat/risk assessment و hardening.
- secure Internet-connected deployment.
- website risks/threats/vulnerabilities.
- web application security و common attacks.
- OWASP Top 10، auth failures، logging/monitoring، SSRF، injection، path traversal، CSRF/XSS، DoS و redirect abuse.
- broader assessment/compliance/security operations topics.

### کاربرد
Threat model، risk register، pre-launch security checklist، hosting hardening، e-commerce/privacy/compliance thinking.

### rule
Security taxonomy کتاب مفید است، اما current OWASP/NIST/vendor advisories برای production authoritative هستند.

---

## 10) Web Application Security: A Beginner’s Guide — Sullivan & Liu — 2012

### 9 فصل
**Part I — Primer**
1. Welcome to the Wide World of Web Application Security
2. Security Fundamentals

**Part II — Principles**
3. Authentication
4. Authorization
5. Browser Security Principles: Same-Origin Policy
6. Browser Security Principles: XSS and CSRF
7. Database Security Principles
8. File Security Principles

**Part III**
9. Secure Development Methodologies

### اصول ماندگار
input validation، defense in depth، attack surface reduction، threat modeling، auth/session، authorization، DB/file protection، directory traversal، source/backup leak prevention، secure SDL/code review/security testing/incident planning.

### Legacy rule
برای principles خوب است، ولی browser behavior، OWASP list و implementation detail سال 2012 نباید مرجع اجرایی روز باشند.

---

# Frontend + UI/UX Adoption Contract

برای طراحی زیبا، palette، typography، grid، iconography، motion، slider/carousel و composition:
1. اول `docs/library/ui-ux/UI_UX_LIBRARY_INDEX_FA.md` و playbookهای UI/UX.
2. سپس این سند برای implementation architecture/performance.
3. سپس مستندات رسمی version واقعی framework/library.

## Rendering / SEO
- SEO-critical title/content/link/schema/navigation در HTML semantic و crawlable باشد.
- client-only component فقط وقتی interaction واقعی لازم است.
- هر page type strategy جدا: static/server/dynamic/client بر اساس freshness، personalization و crawl need.
- metadata/canonical/schema/sitemap/indexability با actual framework docs Verify شود.
- visual effect نباید LCP/INP/CLS را قربانی کند.

## Fonts
- فونت حداقل وزن‌های لازم، subset/format مناسب و preload فقط برای critical font.
- fallback metrics و layout shift بررسی شود.
- Persian typography: line-height/measure/hierarchy واقعی؛ tracking لاتین کور روی فارسی اعمال نشود.

## Images/graphics
- image dimensions/aspect ratio مشخص.
- responsive sources و lazy-load برای non-critical media.
- hero image/visual با performance budget.
- عکس واقعی محصول/دفتر/مجوز/نمونه‌کار بر AI decorative visual مقدم است.
- alt text برای informative image؛ decorative image از accessibility tree خارج شود.

## Slider/Carousel
- اگر auto-rotate دارد: stop/pause control.
- focus/hover نباید کاربر را غافلگیر کند.
- previous/next قابل keyboard.
- pagination/status قابل فهم.
- motion reduced preference رعایت شود.
- CLS و image preloading کنترل شود.
- Carousel برای محتوایی که باید همه دیده/ایندکس شود، تنها مسیر دسترسی نباشد.

## Component / Design System
- semantic token > magic value.
- icon family و stroke/optical weight consistent.
- state matrix کامل.
- RTL/LTR و mixed bidi data.
- responsive task priority.
- Storybook یا equivalent visual catalogue برای shared components وقتی stack اجازه می‌دهد.
- dead controls، fake KPI، fake chart و placeholder operational status ممنوع.

## Performance Gate
قبل و بعد از UI بزرگ:
- bundle impact.
- render profiler.
- query/API waterfall.
- LCP/INP/CLS یا project-equivalent metrics.
- mobile/low-end behavior.
- no regression budget.

---

# Task → Reference Map

| Task | اولویت |
|---|---|
| React component architecture / re-render / TS | React official docs → React in Depth → profiler/tests |
| Next routing/rendering/SEO/deployment | actual Next docs + lockfile → Modern Web Applications → project tests |
| Three.js/R3F/3D | Three.js/R3F docs → 3D Web Development → performance/SEO/accessibility gate |
| Storybook/design-system implementation | Storybook docs → React in Depth + 3D book → UI/UX library |
| AI chat/RAG/tool UI | provider/SDK docs → Build AI-Enhanced Web Apps → eval/security/privacy |
| Django ORM/performance | actual Django docs + DB docs → Mastering Django ORM → EXPLAIN/query tests |
| Web security | OWASP ASVS/Cheat Sheets → Grokking → Internet/Web Security 3e → legacy Sullivan/Liu |
| PowerShell | Microsoft docs → Thomas Lee → Pester/tests → Radcliffe secondary |
| Palette/typography/composition/motion | UI/UX shared library → project design system → visual QA |
| Slider/carousel | current accessibility pattern guidance → project component → visual/perf test |

# Mandatory rule for every project

قبل از هر تغییر معنی‌دار Frontend/React/Next/Three.js/AI-web/Django-ORM/PowerShell/Web-security:
1. AGENTS و docs پروژه را بخوان.
2. runtime/branch/commit/lockfile/DB/host را Verify کن.
3. error history را بررسی کن.
4. این Library و UI/UX Library را بر اساس task بخوان.
5. official docs همان version را Verify کن.
6. implementation کوچک و سازگار بساز؛ blind install/copy ممنوع.
7. local/relevant tests و performance/security checks.
8. docs را با adoption واقعی Update کن.

**Book knowledge is a design input, not an executable truth.**
