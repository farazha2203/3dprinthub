# 3DPrintHub Instagram/Buffer Implementation

## Existing project pieces
- Direct Meta implementation exists at `catalog_center/app/instagram_publish.py`.
- Historical Buffer work is preserved on branch `wip/phase50-social-buffer-20260917`.
- The Buffer provider module is now documented as the preferred provider because Meta Developer Console is unavailable to the owner.

## Runtime contract
1. Product must first publish successfully to `3dprinthub.ir`.
2. Server ACK must confirm public HTTPS Product URL.
3. At least one public HTTPS Product media URL must exist.
4. Caption is built from canonical Product SEO/social fields only.
5. Buffer Channel must resolve to `service=instagram` and must not be disconnected/locked.
6. Buffer `createPost` receives only public Site media, caption, alt text and Instagram metadata.
7. A sync receipt records provider result and Site revision fingerprint.

## Configuration keys
Non-secret settings:
- `instagram_publish_provider=buffer`
- `buffer_instagram_channel_id=<Buffer ChannelId>`

Secret:
- `BUFFER_API_KEY` through Windows Credential Store / environment only.

## Current gate
The Instagram account is connected inside Buffer according to owner confirmation.
API transport cannot be live-tested until a non-empty Buffer API key is available locally.
