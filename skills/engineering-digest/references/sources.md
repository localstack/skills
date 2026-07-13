# Sources

Every source the digest pulls from, with concrete IDs, queries, and window
filters. **The digest is posted every two weeks**, so the **window** is normally
~2 weeks: `[date of the last issue's #engineering post, today]` (see §0). Use
that true window as the primary filter. The queries below take the window bounds
as parameters; where a query looks slightly ahead for upcoming items, a `+2 weeks`
horizon matches the cadence. (Some Notion views the team built use a wider
`±3 weeks` net; prefer the true ~2-week window here and treat 3 weeks only as a
loose safety margin, not the target period.)

All Notion SQL runs through `notion-query-data-sources`. Use the
`collection://...` URL as the table name. Dates are text; wrap with `date(...)`
for comparisons. Checkbox values are `"__YES__"` / `"__NO__"`.

> ⚠️ **Label trap.** The two RFC-related databases are easy to confuse. The
> mapping below is verified by schema (Status values, date fields) and is
> authoritative: **"Incubator" = `2a1490ce…`** (has "Open for comments 💬") and
> **"Decision Register" = `483f000e…`** (has Decided/Due dates). If you ever see
> them labelled the other way round elsewhere, trust the schema, not the label.

## Key IDs

The digest is authored and published **only in Slack**. Notion databases below
are read-only sources for gathering material.

| Notion source (data source) | ID |
|---|---|
| Incubator (RFCs) | `collection://2a1490ce-76f0-41ae-bd66-776dfa0e841d` |
| Decision Register (RFCs + Decisions) | `collection://483f000e-bde2-4e15-9ff5-93e2cfea4d15` |
| Releases | `collection://51594c27-f88a-4b77-a5e4-8e520ce882c1` |
| Demo **sessions** (has the Date) | `collection://87d3fdf0-0d4a-44a4-a7bd-dbdb079b8db9` |
| Demo **presentations** (individual demos) | `collection://e26a87c8-9d32-40d1-8116-70e42a519eaa` |
| Who's Who (Notion user ↔ Slack UID map) | `collection://3e6ef274-9769-426a-94ec-cf5f11f28f37` |

**Who's Who** is the fast path for resolving mentions: its `Who's it` field is
the Notion user (`["user://<id>"]`) and `Slack UID` is the Slack `U…` id, so one
query maps `user://…` ↔ `<@U…>` in either direction (former staff are flagged
via `Engagement = 'former'`). See the "Resolving mentions" section in
`references/style.md` for the query and the email-join fallback.

| Slack channel | ID |
|---|---|
| `#engineering` (digest is posted here) | `C0264MGKF8A` |
| `#general` | `CM3JHC007` |
| `#released` | `C07JJQVFY86` |
| `#random` | `CM18Z8KMJ` |
| `#prj-eng-digest` (retro / process notes) | `C08PEAEU9JP` |

Resolve `#squad-*`, `#celebrations`, `#support-aws` / `#support-saas` /
`#support-snowflake` (used by Deal Makers, §9), and any others at runtime with
`slack_search_channels`.

HubSpot and Linear have no fixed IDs here — they are reached through their MCP
tools (`search_crm_objects`, `list_customers`, `get_issue`, …). The closed-won
deal-stage and Renewals-pipeline IDs that Deal Makers needs live in §9.

## 0. Find the last issue and the window (from Slack)

The previous digest is a Slack message in `#engineering`. Find it to get the
window start and the issue number:

```
slack_search_public  query="Engineering Digest Welcome to the issue of our in:#engineering"  sort=timestamp
```

- The newest matching post (a real digest, not a "new page created" bot notice)
  gives the **window start** (its post date) and the **new number** (its number
  + 1). Digest posts open with `:fyi: :rolled_up_newspaper: … Engineering Digest`
  and "Welcome to the Nth issue of our …".
- Read that post to study the current format (see also `references/examples.md`).
- If nothing is found, ask the user for the last issue's date and number.

## 1. RFCs — Requests for Comments

Two sources feed this section.

**Incubator** — docs open for comments / recently active, not stale:

```sql
SELECT "Name", "Status", "Curation comment", "Areas", "Driver",
       "Last Edited Time", url
FROM "collection://2a1490ce-76f0-41ae-bd66-776dfa0e841d"
WHERE "Status" IN ('Open for comments 💬', 'Ready for review 🌟', 'New 💡')
  AND date("Last Edited Time") >= date(?)   -- window start (~2 weeks back, e.g. date('now','-2 weeks'))
ORDER BY "Last Edited Time" DESC;
```

Prefer "Open for comments 💬". Anything older than the window was already
covered in a previous issue — skip it. Label each bullet `(Incubator · <status>)`.

**Decision Register** — open decisions (not yet decided) that are live now:

```sql
SELECT "Name", "Status", "Description", "Areas", "Driver",
       "date:Decided Date:start", "date:Due Date:start", "Last Updated", url
FROM "collection://483f000e-bde2-4e15-9ff5-93e2cfea4d15"
WHERE "Status" NOT IN ('Draft', 'Archived')
  AND (
      date("date:Decided Date:start") BETWEEN date(?) AND date(?)
   OR date("date:Due Date:start")     BETWEEN date(?) AND date(?)
   OR date("Last Updated")            BETWEEN date(?) AND date(?)
  )
ORDER BY "date:Due Date:start" DESC;
```

Params are the window bounds three times (the true ~2-week window, or roughly
`-2 weeks` .. `+2 weeks` around now to also catch imminent due dates). For
**RFCs**, take rows with Status `In Discussion` (open
questions, often with a Due Date — "your input is welcome"). Rows with Status
`Decided` go in **Decisions made** (section 5) instead — same query, split by
status. Label `(Decision Register · <status>)`.

## 2. News & Updates

The catch-all for company + engineering news in the window. No single table;
assemble from:

- **Do NOT put releases here.** Shipped and upcoming versions belong only in the
  `#released` section (section 3). Keep News & Updates release-free, even for a
  headline launch — link it once, in `#released`.
- **`#general`** (`CM3JHC007`) — big announcements: deals, certifications,
  leadership, policy, all-hands, off-sites. Link the announcement message, do
  not re-list every participant.
- **`#engineering`** (`C0264MGKF8A`) — cross-cutting eng news, spike/hackathon
  dates, tooling rollouts.
- **Monthly People Announcements** page — `notion-search` for "People
  Announcements" (a new page per month; URL changes). Covers joiners, leavers,
  promotions, policy — feeds News and Team Movements.

Use `slack_search_public` with `after:` the window start and `in:#general` /
`in:#engineering`, sorted by timestamp. Keep only well-known, already-announced
items. Do not trawl arbitrary channels.

## 3. `#released`

**Releases** database — shipped and upcoming, around now:

```sql
SELECT "Version", "Stage", "Driver", "📀 Product",
       "date:Release date:start", url
FROM "collection://51594c27-f88a-4b77-a5e4-8e520ce882c1"
WHERE date("date:Release date:start") BETWEEN date(?) AND date(?)   -- window, e.g. now -2w .. +2w
ORDER BY "date:Release date:start" DESC;
```

`Stage` is `📦 Released` / `🏗️ In progress` / `📋 Planned`. Released → the
`#released` bullets; upcoming → an "Up next" note. Cross-reference `#released`
(`C07JJQVFY86`) for the actual announcement permalink + GitHub release link to
cite. `📀 Product` and `Backlog Items` are relations — `notion-fetch` the row if
you need the product name or release notes.

**One release per product.** If the same product shipped more than once in the
window (e.g. K8s Operator v0.4.9 then v0.4.10), list only the **latest** version
and drop the intermediate ones. Group by product first, keep the newest by
release date. Different products each keep their own latest.

## 4. How we're doing things

Process / ways-of-working changes: new conventions, retired tags, new
frameworks, shared repos, career framework, etc. Sources: `#engineering`,
`#general`, and any `Decision Register` rows tagged process-y. Judgement call —
mine the window's `#engineering` for "from now on…" / "we're changing…" posts,
each with a permalink.

## 5. Decisions made

`Decision Register` rows with `Status = 'Decided'` from the section-1 query
(decided or updated within the window). One top-level bullet per decision (what
was decided, linked, tagged `(Decision Register · Decided[ <date>])`), with the
**reasoning in a sub-bullet** beneath it — see the format in
`references/style.md`.

Data-quality note: some rows are `Decided` but lack a `Decided Date`. Don't let
that hide them — the `Last Updated` clause catches them; sanity-check dates
against the page body.

## 6. Demos and other cool things to watch

⚠️ **The Demo Presentations "Date" is a rollup and is NOT SQL-queryable**
(it lives in `notAvailableInQuerySql`). Go via the **sessions** table, which
owns the real Date, then pull each session's presentations.

Step 1 — sessions in window:

```sql
SELECT "Name", "date:Date:start", "Recording", "AI Notes", "Focus", url
FROM "collection://87d3fdf0-0d4a-44a4-a7bd-dbdb079b8db9"
WHERE date("date:Date:start") BETWEEN date(?) AND date(?)   -- the window
ORDER BY "date:Date:start";
```

Step 2 — presentations under each session (the `Demo` column holds the session
page URL as JSON):

```sql
SELECT "Description", "Presenters", "Area", "Notes",
       "userDefined:URL", "Video Timestamp"
FROM "collection://e26a87c8-9d32-40d1-8116-70e42a519eaa"
WHERE "Demo" LIKE '%' || ? || '%';   -- pass the session's page id/url
```

Format: one **session line** (link the session entry + its `Recording`, and the
`AI Notes` doc if present), then **one sub-bullet per presentation**: presenter
(as a mention), the demo-entry link, and a one-line description. For the
description, prefer the presentation's own `Notes`/`Description`; if you have
access to the recording/AI-notes transcript, a one-line summary per demo is
ideal (drivers have used Gemini on the transcript for this).

## 7. Team Movements

Joiners, leavers, role changes, anniversaries. Best sources:
- **Monthly People Announcements** page (see section 2).
- **`#general`** welcome/goodbye posts (link the message).
- **`#celebrations`** (resolve ID at runtime) for anniversaries/milestones.

The old "Hiring plan 2025" DB (`collection://37835589-889c-4a77-bd0c-674b4b3fa886`)
is **archived** — don't rely on it. Keep each line to one sentence + the
announcement link. Onboarding/offboarding calendars are the ground truth if
Slack is ambiguous.

**Only changes that already happened.** Do not list someone who has not yet
started (future or tentative start date), even if the hire is already announced.
Put the announcement in News instead, and add the Team Movements line in a later
issue once they have actually joined. Same for departures: list them in the issue
covering their last day. If nobody's status actually changed in the window, drop
the section (it is fine to omit).

## 8. A Byte of Fun

Sources: `#random` (`CM18Z8KMJ`), `#engineering`, watercooler topics, a fun
link. **Do not choose yourself** — see the protocol in `references/style.md`.

## 9. Deal Makers

Celebrates recent engineering work that helped close deals. In the **published
digest this section leads the issue, right after the intro** (numbered 9 here
only because it is the last source to gather; see the section order in
`references/style.md`).

Unlike every other section, this is not a single Notion/Slack query but a
cross-tool investigation. It is powered by **Bart's
`closed-won-engineering-impact-report` skill**, whose one question is: "did
engineering's work help close this deal?" Two ways to run it:

1. **Preferred — invoke the skill directly** if it is available in your run
   environment, scoped to the digest window (see below). Take its
   Strong/Some-signal accounts as the section's raw material.
2. **Replicate its steps** with the MCP tools the digest already has (HubSpot,
   Linear, Slack; Gmail/Notion if connected). The digest environment exposes the
   same tools the skill uses, so this is a faithful fallback.

**Window.** Use the digest's true ~2-week window (§0), *not* the skill's default
trailing 14/30 days. Filter closed-won deals by close date within that window.

### Step A — closed-won deals from HubSpot

Use `search_crm_objects` (**not** `query_crm_data` — it needs a
reporting-base-read scope this workspace lacks and will fail). Filter deals by:

- **Close date** within the digest window.
- **Deal stage** in the closed-won set across all pipelines:
  `["closedwon","261389503","124389608","854377409","221862367","261389519","221862369","854835683"]`

Then **exclude pure renewals**: drop a deal if its pipeline is the Renewals
pipeline (`"47258352"`) **or** its `type` property is empty/unset. Keep deals
typed **New Business, Upsell, Cross-Sell, or Paid PoC**. For each surviving deal,
resolve the associated company via `associatedWith` to get a clean company name +
domain to search downstream. Keep the HubSpot deal URL — it is a citable source.

### Step B — engineering signal, per company

For every surviving company, check **all** of these (weak signals from several
sources combine into a stronger verdict than one alone — don't stop at the first
hit):

- **Linear** — `list_customers` with `includeNeeds:true`, matched by domain,
  surfaces linked issues/needs. `get_issue` on anything relevant to confirm it
  actually shipped (state, PR links, resolution date). A fixed bug shipped
  shortly before close date is strong evidence; an open, unresolved feature
  request is weak. Keep the Linear issue URL + any linked GitHub PR.
- **Slack** — `slack_search_public_and_private` on the company name and domain,
  both scoped to `#support-aws` / `#support-saas` / `#support-snowflake` **and**
  unscoped (engineers help in deal-specific/account channels too). Use
  `include_context:false` and a modest `limit` (big threads blow the token
  budget). Keep the message `Permalink`.
- **Gmail** — `search_threads` with e.g. `(from:<domain> OR to:<domain>)
  newer_than:180d` to catch technical correspondence that reached engineering.
- **Notion** — search the "Product / Engineering / Technical GTM Sync" notes for
  the company name in the last 2-3 meeting entries for a technical win / blocker
  resolved.

### Step C — classify, then distill

Only two verdicts survive; everything else is dropped (don't list "no signal"
accounts):

- **Strong signal** — a specific, confirmed engineering deliverable (shipped
  fix, PR, or documented technical recommendation) with timing that plausibly
  influenced the close.
- **Some signal** — real but weaker evidence: an open Linear issue with engineer
  participation, a pre-sale Slack thread where an engineer answered a technical
  question, or a Notion mention without a confirmed resolution.

For the digest, lead with Strong-signal deals. **Credit the engineers by name**
(resolve to Slack `<@USERID>` mentions via Who's Who, §Key IDs). Link the
underlying resource **directly** — HubSpot deal, GitHub PR, Linear issue, or
Slack thread permalink — regardless of whether the deal was announced elsewhere;
`#engineering` is an internal channel, so naming the customer and deal is fine.
See "Deal Makers formatting" in `references/style.md` for the bullet shape.

**If nobody had signal in the window, drop the section** (same rule as Team
Movements). If HubSpot or Linear is not connected, skip it and flag to the user
that Deal Makers could not be compiled.

## Fallbacks

**DB-query plan gate.** If `notion-query-data-sources` returns a plan/permission
error, this workspace lacks Notion Business + Notion AI. Then:
1. Best fix: create a Notion internal integration, share the source databases
   with it, and query via the Notion REST API with an API key (`NOTION_API_KEY`)
   — e.g. a short script hitting `POST /v1/data_sources/{id}/query` with the
   same filters. This is the durable path for a shared/automated skill.
2. Stopgap: `notion-fetch` each database URL (returns schema, not rows) and
   `notion-search` by title, then open candidate pages individually. Slower and
   lossier; flag to the user that DB coverage may be incomplete.

**Demos incomplete.** If session→presentation joins come back empty, `notion-fetch`
the Demos board page (`f12248e5c77b42e995d2fa516767a286`) and read the sessions
in window directly.
