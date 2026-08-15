# Canonical 3DPrintHub Catalog Center

Canonical GitHub path:
`catalog_center/`

Windows runtime path:
`D:\projects\3dprinthub_catalog_center`

This source was canonicalized starting with Phase48.2-v2.1.

Runtime/state is intentionally excluded from Git:
- `.env`
- `config.json`
- SQLite databases
- API key files
- browser profiles
- cache/download/import/log folders
- persistent settings backups
- build/dist/generated archives and executables

Phase48.2 behavior:
- selected remote images are materialized before batch finalization;
- batches are built under `.building` first;
- image mappings and physical files are validated;
- broken packages fail closed with `IMAGE_NOT_PACKAGED`;
- FTP upload performs package preflight before network connection.
