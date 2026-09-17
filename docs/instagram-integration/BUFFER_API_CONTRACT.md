# Buffer API Contract for 3DPrintHub

Official source: https://developers.buffer.com/

## API basics
- Protocol: GraphQL over HTTPS.
- Endpoint: `POST https://api.buffer.com`.
- Authentication: `Authorization: Bearer <BUFFER_API_KEY>`.
- Personal API keys act on the connected Buffer account and its organizations/channels.
- Required project capability: read connected channels and create Instagram posts.

## Discovery queries
1. Query `account { organizations { id name } }` to resolve the Organization.
2. Query `channels(input:{organizationId: ...})` and select `service == instagram`.
3. Store only the selected Buffer Channel ID as non-secret configuration.
4. Reject a disconnected or locked channel before publishing.

## Post creation
Use `createPost(input: CreatePostInput!)`.
Required fields for this project:
- `text`
- `channelId`
- `schedulingType: automatic`
- `mode: shareNow` for explicit immediate publish, or `addToQueue` only when operator chooses queueing.
- `assets` containing public HTTPS image/video URLs.
- `metadata.instagram.type: post|story|reel` as appropriate.
- `metadata.instagram.shouldShareToFeed: true` for normal feed posts/reels where applicable.
