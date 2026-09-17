# Buffer GraphQL examples

Endpoint:
`POST https://api.buffer.com`

Authentication header:
`Authorization: Bearer <BUFFER_API_KEY>`

## Discover organizations
```graphql
query {
  account {
    organizations { id name }
  }
}
```

## Discover Instagram channel
```graphql
query Channels($organizationId: OrganizationId!) {
  channels(input: {organizationId: $organizationId}) {
    id
    name
    displayName
    service
    isDisconnected
    isLocked
  }
}
```

## Publish immediately
```graphql
mutation CreateInstagramPost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess {
      post { id status externalLink }
    }
    ... on MutationError { message }
  }
}
```

Project input policy:
- `schedulingType: automatic`
- `mode: shareNow`
- `needsApproval: false`
- `assets`: only public HTTPS site media
- `metadata.instagram.type: post`
- `metadata.instagram.shouldShareToFeed: true`

Never place a real API key in this file or any Git-tracked file.
