# Style & Format

Match the most recent published issues (`references/examples.md`). The format
evolves; when older and newer issues disagree, follow the newer one.

## Section order

Always this order (skip a section only if it is genuinely empty for the window):

1. **Title + intro** — `:fyi: :rolled_up_newspaper: Nth Engineering Digest
   :rolled_up_newspaper: :fyi:` header, then "Welcome to the Nth issue of our
   Engineering Digest! ..." one-liner. Do **not** link "Engineering Digest" (no
   per-issue or landing-page link in the intro). Add a short human aside if apt
   (e.g. "there's a LOT going on :rocket:").
2. `:ask:` **RFCs - Requests for Comments** — Incubator + open Decision Register
   items. Close open RFCs with "Your input is welcome!" where natural. Include
   **every** engineering-relevant open item in the window (Incubator "Open for
   comments" and Decision Register "In Discussion"); do not silently drop one for
   brevity. If you think the section is getting long, ask the user rather than
   cutting.
3. 📰 **News & Updates** — company + engineering news. **No releases here** (they
   go in `#released` only), so nothing about shipped or upcoming versions.
4. 🥳 **`#released`** — the only place releases appear. If a single product
   shipped **multiple releases** in the window, list only the **last** one (keep
   distinct products separate). Close the section with the callout on the line
   **immediately after** the last release bullet (no blank line between them),
   and render it **italic**: *Haven't seen your contribution here?
   [Post in `#released`](https://localstack-cloud.slack.com/archives/C07JJQVFY86)!*
5. 🏗️ **How we're doing things**
6. 🧑‍⚖️ **Decisions made** — one top-level bullet per decision (the decision
   itself, linked, with the `(Decision Register · Decided[ <date>])` tag). Put
   the **reasoning / rationale in one or more sub-bullets** beneath it, rather
   than trailing the decision line. See the shape below.
7. 📽️ **Demos and other cool things to watch**
8. 👥 **Team Movements** — only people whose change has **already taken effect**
   in the window. Do **not** list someone who has not yet started (a future or
   tentative start date); mention the hire in News if it is already announced,
   and hold the Team Movements line until they have actually joined.
9. 🛝 **A Byte of Fun** — always closes the digest.

In a Slack message there are no real heading levels: each section header is a
**bold line led by its emoji** (e.g. `*:judge: Decisions made*`), followed by the
bullet list. Match the header wording and emoji of the most recent issue.

## Tone — write like a human

Drivers have repeatedly rejected "AI slop." Hard rules:

- **No em dashes (—).** Rewrite the sentence, or use a colon, comma, or period.
  Parenthetical hyphen ` - ` is acceptable but sparingly.
- **No "not just X, but Y", no "it's worth noting", no hype adverbs** ("truly",
  "seamlessly", "robust"). State the fact.
- Tight bullets over name-dumps. For broad announcements (deals,
  certifications, leadership), link the full announcement instead of listing
  every person.
- Professional and direct, with room for personality in the intro and Byte of
  Fun. Read the last issue's voice and match it.
- Prefer the wording used in the original source over paraphrase that could
  drift from fact.

## Bullets and sourcing

- **Every bullet carries a link** to its source. No source → cut it.
- Typical shape: `<emoji> **<Headline>** (<context/date>) - one or two lines,
  then the source link(s).`
- Cite the canonical thing: Notion page for RFCs/decisions/demos, Slack
  permalink for announcements, GitHub release + `#released` permalink for
  releases, blog/press links where they exist.
- Get Slack permalinks from search results (`Permalink` field) — never
  hand-build them.

## Emoji (Slack)

The full Slack shortcode set works (`:rolled_up_newspaper:`, `:ask:`,
`:newspaper:`, `:partying_face:`, `:building_construction:`, `:judge:`,
`:film_projector:`, `:busts_in_silhouette:`, `:playground_slide:`, `:package:`,
`:snowflake:`, …). Section-header emoji seen in real issues:

RFCs `:ask:`, News `:newspaper:`, released `:partying_face:`, how-we-do
`:building_construction:`, decisions `:judge:`, demos `:film_projector:`, team
`:busts_in_silhouette:`, fun `:playground_slide:`. Title uses
`:fyi: :rolled_up_newspaper: … :rolled_up_newspaper: :fyi:`.

## Links and mentions (Slack)

- **Links:** the `slack_send_message` / `slack_send_message_draft` MCP tools take
  **standard markdown** — write `[text](url)` and `**bold**`, NOT Slack's
  `<url|text>` / `*bold*` wire format (the tool converts for you). Get Slack
  permalinks from search results (`Permalink` field), never hand-build them.
- **People:** use the raw `<@USERID>` token (markdown has no mention syntax;
  Slack still resolves it). Resolve IDs as below; fall back to a plain name only
  when no ID is found.

### Resolving mentions (Notion → Slack)

Notion sources (Driver / Presenters / Stakeholders) give a `user://<notion-id>`,
which is a **different namespace** from Slack `<@U…>`.

**Primary path — the "Who's Who" database.** It directly maps the two: the
`Who's it` field is the Notion user (a `person` column, returned as
`["user://<notion-id>"]`) and the `Slack UID` field is that person's Slack `U…`
id. Data source: `collection://3e6ef274-9769-426a-94ec-cf5f11f28f37` (see
`references/sources.md`). One query resolves everyone you need, in either
direction:

```sql
SELECT "Name", "Who's it", "Slack UID"
FROM "collection://3e6ef274-9769-426a-94ec-cf5f11f28f37"
WHERE "Slack UID" IS NOT NULL AND "Who's it" IS NOT NULL;
```

Match the `user://<notion-id>` from your source rows against `Who's it` to get
the `Slack UID`, or go the other way. Cache the mapping within a run — the same
people recur across demos and RFCs.

**Fallback — email join.** If someone is missing a `Slack UID` (or isn't in
Who's Who), join on the person's `@localstack.cloud` **email**, which both sides
expose:

1. `notion-get-users` with the `user://` id (or list) → name + email.
2. `slack_search_users` with that email (or name) → Slack `U…` id.

Watch out: a Notion display name may be just a first name ("Alex", "Daniel",
"Simon"); the email disambiguates (e.g. two Simons: `simon.walker@` vs
`simon.wallner@`).

## Demos formatting

Per demo session in the window:

- **Session line:** link the session entry **and** its recording (and AI-notes
  doc if present). e.g. `[Weekly Demo #223](url) (Jun 18) · [recording](url) ·
  [AI notes](url)`.
- **Sub-bullet per presentation:** `<presenter mention> demoed [<title>](url),
  <one-line description if non-obvious>.`
- Group strictly under the parent session; never flatten presentations into one
  list. See the demo blocks in `references/examples.md`.

## Decisions made formatting

One top-level bullet names the decision (linked, with the tag). The reasoning
goes in sub-bullet(s) underneath, not trailing the headline:

```
• :emoji: [Decision title](url) (Decision Register · Decided <date>). One line on what was decided.
    ◦ Why: the rationale / key data point behind it.
    ◦ (optional) A second sub-bullet for a caveat, scope, or next step.
```

Keep the headline short; push the "because…" into the sub-bullet.

## A Byte of Fun — protocol

- **Never pick it yourself.** First ask the user for their idea.
- Offer **2-3 candidate finds** from `#random` or `#engineering` as fallback.
- The user has final say. It can be a light/interesting link, a funny poll, or a
  wry tie-in to the digest's own news. Keep it short.

## Publishing mechanics (Slack)

- Post as one message in `#engineering` (`C0264MGKF8A`). `slack_send_message`
  takes standard markdown (`[text](url)`, `**bold**`) plus Slack shortcode emoji
  and raw `<@USERID>` mentions; it does **not** take Block Kit JSON, so no
  block/divider machinery is needed (bold section headers + bullets suffice).
- If the body exceeds Slack's ~5000-char text limit, split logically (e.g. post
  the tail as a threaded reply) rather than truncating.
- Use `slack_send_message_draft` for the review gate; only `slack_send_message`
  after the user confirms.
