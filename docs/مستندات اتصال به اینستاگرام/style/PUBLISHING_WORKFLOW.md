# Instagram Publishing Workflow

## Canonical flow
`Product DB -> Site publish -> HTTPS verification -> Buffer feed post -> companion Story -> Highlight queue`

The website Product URL remains the commerce authority. Instagram must never become a second product database.

## Feed post rules
- Use the public Product media URLs from the successful Site ACK only.
- Use the tracked Product URL for Buffer Shop Grid (`utm_source=instagram`).
- Caption order: searchable product name, one useful value statement, material/use facts, CTA, direct Product URL, focused hashtags.
- Do not use unrelated/trending hashtags only for reach.
- Use `metadata.instagram.isAiGenerated=true` only when the published visual itself is AI-generated.

## Companion Story
Every successful Buffer feed publish requests one companion Story by default.
The preferred Story asset is `server_ack_json.instagram_story_url` or `social_story_url`.
If no branded Story asset exists, the first verified public Product image is used as a safe fallback.
Buffer Story metadata uses `type=story`, `schedulingType=automatic`, `mode=shareNow`.

## Highlights
The public Buffer API currently exposes Post/Story creation but no public mutation to add a published Story to an Instagram Highlight.
Therefore the receipt records `highlight_target` and `highlight_status=operator_required`.
Do not simulate Highlights by deleting/reposting content or using private Instagram APIs.
