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

Resolve `#squad-*`, `#celebrations`, and any others at runtime with
`slack_search_channels`.

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
