

## 2026-10-08 — Windows runtime/worktree cleanup

Owner accepted the visible Catalog Center v8.9.11 / Build 2026.10.04.2 as the current runtime to preserve. Its source remains `D:\projects\3DPrintHub-a2z-a2r-converge`, Catalog data remains `D:\projects\3dprinthub-catalog-manager`, and the Desktop shortcut still targets this runtime. Historical local worktrees were removed only after compact dirty-delta rollback evidence was captured at `D:\projects\3dprinthub-backups\worktree-cleanup-20261008-193657`.

After cleanup, Qt VerifyOnly PASS and read-only Catalog quick_check=ok with 1076 Products. The running v8.9.11 process remained healthy. Current A2R/W5 source WIP in the preserved runtime was not reset, stashed, or overwritten; Host/Production were untouched.
