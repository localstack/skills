---
name: engineering-digest
description: >-
  Create LocalStack's bi-weekly Engineering Digest. Use when asked to write,
  draft, compile, or "do" the (next) engineering digest. Gathers RFCs,
  decisions, releases, demos, team movements, deal-impact wins and news from
  Notion databases, Slack, HubSpot and Linear, then drafts the post directly in
  Slack for #engineering. Draft-first: never sends to Slack without explicit
  confirmation.
---

# Engineering Digest

Compile LocalStack's bi-weekly Engineering Digest: pull what happened in
Engineering (and the wider company) since the last issue from a fixed set of
"well-known" sources, and prepare the Slack post that goes out in `#engineering`.

The digest lives **entirely in Slack**. Notion databases are read-only *sources*
for gathering material; the digest is not authored into or stored as a Notion
page.

Guiding principle (from the digest's charter): **collect information from
well-known places and present it concisely. Do not comb all of Slack. Accept
the risk of missing something** — that nudges people to post in the right
channels. Never include anything not already shared in its proper channel.

## Golden rules

1. **Draft-first, always.** Gather and draft freely, but **sending the post to
   `#engineering` is a hard gate** that needs explicit user confirmation each
   run. Prepare it as a Slack draft; stop and hand control back.
2. **Every bullet links to a verifiable source.** Notion page, Slack permalink,
   GitHub release/PR, HubSpot deal, Linear issue, or blog post. If you cannot
   find a source, drop the bullet. Do not invent, infer, or embellish. Factual
   correctness beats completeness.
3. **You do not pick "A Byte of Fun."** Ask the user; offer 2-3 candidates as
   fallback. The user has final say (see `references/style.md`).
4. **Write like a human, not an AI.** No em dashes. Avoid "not just X but Y",
   throat-clearing, and hype. This has been called out repeatedly by drivers.
   See the tone rules in `references/style.md`.

## Prerequisites

- Slack MCP connected (search, read, send_message_draft, send_message, users).
- Notion MCP connected for **reading sources** (fetch, query-data-sources).
- **Notion DB queries need a Notion Business plan + Notion AI.** Without it,
  `notion-query-data-sources` / `notion-query-database-view` fail and only
  `notion-fetch` / `notion-search` work (schemas + relevance guesses, not full
  row sets). Test early with a trivial query; if it fails, see the fallback in
  `references/sources.md` before continuing.
- **Deal Makers needs HubSpot + Linear MCP** (and ideally Gmail + Notion). It is
  powered by the `closed-won-engineering-impact-report` skill (see
  `references/sources.md` §9): run that skill scoped to the digest window, or
  replicate its documented steps with the tools above. If HubSpot/Linear are not
  connected, skip the section rather than guessing.

## Workflow

Work through these in order. `references/sources.md` has every ID, query, and
filter; `references/style.md` has the section-by-section format and tone;
`references/examples.md` has two full real issues to match.

### 1. Scope the issue (from Slack)

- **Find the last issue.** Search `#engineering` (`C0264MGKF8A`) for the most
  recent "Engineering Digest" post (see `references/sources.md` §0). Its date is
  the **window start**; its issue number + 1 is the **new number**.
- **Window** = from the last issue's post date up to **today** (in your
  environment context). The digest is posted **every two weeks**, so this is
  normally a ~2-week window; use it as the filter for all source pulls (don't
  default to a 3-week period).
- If no prior issue is findable, ask the user for the last issue's date/number.

### 2. Learn the current format

Read the **last ~3 published issues** in `#engineering` (via Slack search).
Prioritize the newest for tone and structure; the format evolves.
`references/examples.md` mirrors the two most recent at time of writing.

### 3. Gather, per section

Run the queries in `references/sources.md`, window-filtered. Sections:
RFCs (Incubator + Decision Register) · News & Updates · `#released` ·
How we're doing things · Decisions made · Demos · Deal Makers · Team Movements ·
A Byte of Fun. Collect a source link (Slack permalink, Notion URL, GitHub/blog
link, HubSpot deal, Linear issue) for every candidate bullet as you go. This is
the **gather** order; **Deal Makers leads the published digest** (right after the
intro) even though it is the last section to gather. See the published section
order in `references/style.md`.

**Deal Makers is different from the other sections.** It is not a Notion/Slack
query but a cross-tool investigation: run the `closed-won-engineering-impact-report`
skill (Bart's) scoped to the digest window, or replicate its steps
(`references/sources.md` §9). Only accounts with real "Strong" or "Some" signal
of engineering impact make the cut; celebrate the engineering work and credit
the people, linking the underlying resource (HubSpot deal, GitHub PR, Linear
issue, Slack thread) directly. Skip the section if HubSpot/Linear are absent.

### 4. Draft the content

Write the full digest as Slack markdown to a working file (use your scratchpad
dir) so it is easy to review and iterate. Follow `references/style.md` exactly:
section order, Slack shortcode emoji, `<url|text>` links, `<@USERID>` mentions,
tight bullets, and the demo grouping (session line + one sub-bullet per
presentation).

### 5. Review gate — content

Show the user the draft. Explicitly ask for their **Byte of Fun** and surface
anything thin or unsourced. Incorporate edits. Only then continue.

### 6. Create the Slack draft

Create a **draft** with `slack_send_message_draft` in `#engineering`
(`C0264MGKF8A`). Tell the user to review it in Slack and send it themselves, or
to confirm and have you send it with `slack_send_message`. **Never send
unprompted.** If the body exceeds Slack's ~5000-char text limit, split logically
(e.g. post the tail as a threaded reply) rather than truncating.

### 7. After it ships

Once the user confirms the post is live, offer to post a short retro note in
`#prj-eng-digest` (`C08PEAEU9JP`) on how the run went and what could improve —
this is part of the digest's process.

## References

- `references/sources.md` — every source: how to find the last issue in Slack,
  Notion data-source IDs, exact SQL, window filters, Slack channel IDs, the
  Deal Makers cross-tool workflow (§9), and fallbacks for the hard cases
  (DB-query plan gate; demos not being SQL-date-filterable).
- `references/style.md` — section order, tone rules, Slack emoji, mentions,
  demo formatting, Deal Makers formatting, Byte of Fun protocol, Slack posting
  mechanics.
- `references/examples.md` — two full recent issues as gold-standard output.
