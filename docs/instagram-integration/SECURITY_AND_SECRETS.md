# Security and Secret Rules

## Hard rules
- `BUFFER_API_KEY` is a secret and must never be committed to Git.
- Never place the Buffer key in SQLite, screenshots, logs, test fixtures, documentation, crash reports, or UI state.
- Never call Buffer from browser/client JavaScript where the token can be extracted.
- Windows runtime reads the key from Windows Credential Store through `secure_secrets.get_secret("buffer_api_key")`.
- Server runtime, if used later, must read the key from environment/secrets storage only.

## Local bootstrap file
`buffer-ker.txt` is only a temporary operator handoff file.
It must remain Git-ignored. After a valid key is imported into Windows Credential Store, the temporary file should be cleared.

## Failure behavior
- Missing key: fail closed; no social publish.
- Invalid/401 key: fail closed and request key rotation/re-authentication.
- Missing Instagram Channel ID: fail closed.
- Channel service not `instagram`: fail closed.
- Site Product not public/HTTPS verified: fail closed before Buffer.
- Missing public media URL: fail closed before Buffer.
- Duplicate Site revision: do not post the same public Product revision twice.

## Audit receipt
Store only Buffer Post ID, provider status, channel ID, public Product URL, public media URLs, and Site revision fingerprint.
Never store the API key in receipts.
