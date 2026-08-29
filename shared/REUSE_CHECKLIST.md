# Cross-Project Reuse Checklist
- [ ] Search shared/REGISTRY.md and other owner repositories.
- [ ] Identify source repo/path/commit.
- [ ] Check framework/runtime/library and DB/schema compatibility.
- [ ] Check auth/security/provider/env/host assumptions.
- [ ] Remove private/business-specific assumptions.
- [ ] Preserve security controls and add adapters where needed.
- [ ] Test locally, record errors/fixes, update registry.
- [ ] Commit/push before production deploy.
