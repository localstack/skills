# Examples

Two real published issues (#29 and #28), as posted in `#engineering`. These are
the gold standard for scope, bullet shape, sourcing, and the demo grouping.
Shown here in Slack's rendered wire form (shortcode emoji, `<url|text>` links,
`<@ID>` mentions). When you author the post through the Slack MCP tool you write
**standard markdown** instead (`[text](url)`, `**bold**`) plus `:emoji:` and raw
`<@USERID>` — see `references/style.md`. Study these for content and structure,
not link syntax.

Note the discipline: every bullet ends in a link; broad announcements link one
"full announcement" rather than naming everyone; demos are grouped under their
session; the intro carries a little human voice; there are no em dashes.

---

## Issue #29 (posted 2026-06-24, #engineering)

:fyi: :rolled_up_newspaper: 29th Engineering Digest :rolled_up_newspaper: :fyi:

Welcome to the 29th issue of our Engineering Digest! The goal of this format is to keep you up-to-date by collecting some of the most important things that are going on at LocalStack from the perspective of Engineering!
Apologies for the late arrival this time, I missed my turn last week :shame-conga: :man-bowing:

**:ask: RFCs - Requests for Comments**
- <…|Entitlement-based integration testing> (Incubator · Open for comments :speech_balloon:). <@U026TRYT7NF|Alex> proposes retiring the legacy "Community" vs "Pro" test pipelines in favour of a single entitlement-aware framework: each test is annotated with the product entitlements it requires, and CI runs a matrix over license tokens, then selects the tests each token's entitlements satisfy. Adding a tier becomes a new token in the matrix, not new pipeline files. Your input is welcome!

**:newspaper: News & Updates**
- :robot_face: LocalStack for AI Agents is live (Jun 9). A refreshed <…|homepage> positioning LocalStack for agentic AI, plus a dedicated <…|AI agents landing page>, an <…|announcement blog>, and a <…|press release>. <…|Shared by Colin in #general>.
- :lstk-jam: lstk is closing in on becoming the default CLI. <…|Maureen has asked every LocalStacker to use it day-to-day and send feedback> ahead of the customer rollout. It manages all three emulators (AWS, Snowflake, Azure preview), wraps the *local tools, and handles auth (<…|README>). <…|Recently shipped>: snapshot/reset commands and AWS/Azure CLI proxies.
- :speech_balloon: AI-powered WebApp chat support went live (Jun 9). <…|Announced by Marko in #released>.
- :statue_of_liberty: AWS Summit New York (Jun 17). LocalStack was on the ground at the largest AWS Summit in North America, with a <…|live AI-agent demo webinar> to follow. <…|Shout-out from Colin>.
- :snow_capped_mountain: Two team off-sites. The <…|SaaS & Data teams> met in Zürich (Jun 15-19); the <…|Lava squad> met in Budapest (Jun 17-19) to plan the Rust Snowflake emulator's GA roadmap.
- :mega: All-Hands on Jun 25 features an extended, anonymous company-wide Q&A. <…|Details & Slido from Maria>. :date: The <…|next Spike Day + Hackathon run Jul 10-16>.

**:partying_face: #released**
- :package: <…|LocalStack for AWS v2026.05.3> shipped on Jun 10 (<…|announcement>).
- :wheel_of_dharma: <…|LocalStack K8s Operator v0.4.8> shipped on Jun 16 (<…|announcement>).
- :package: Up next: <…|LocalStack for AWS 2026.06.0 lands Jun 24> (<…|v2026.06>).

Haven't seen your contribution here? <https://localstack-cloud.slack.com/archives/C07JJQVFY86|Post in #released!>

**:building_construction: How we're doing things**
- :whale: Docker image tags: dev is the new default, nightly is going away. The nightly tag added little over latest/dev and <…|will be retired after the next release>.
- :robot_face: A shared coding-agent skills repo. localstack-skills-internal gathers reusable agent workflows across teams; <…|Patricia is after contributors and testers>.
- :book: A Product & Platform Glossary. Shared definitions for our product terminology across UI, docs, blogs, and sales assets. <…|Announced by Quetzalli>; <…|read it here>.
- :ladder: A new Career Framework was introduced at the <…|Core Engineering All-Hands on Jun 17>.

**:judge: Decisions made**
- :snowflake: <…|Rust Snowflake Emulator Strategy> (Decision Register · Decided). <@U090N63604C|Lazar Kanelov>'s decision makes the Rust Snowflake emulator the primary strategic path.
    ◦ Why: target functional parity with the Python emulator in ~3 months and GA around early Q1 2027 (behind a controlled private preview), with the Python emulator on critical-fix-only maintenance through the transition.
- :unlock: <…|Stop enforcing reviews on PRs in localstack-pro> (Decision Register · Decided Jun 16). A second human reviewer on localstack-pro is now opt-in, not required.
    ◦ Why: follows the AI-first manifesto (most code is agent-written and reviewed by the human steering it), under "you can move fast, but you need to own it."
    ◦ A review is still expected for cross-team-owned, complex, or critical changes.

**:film_projector: Demos and other cool things to watch**
- <…|Weekly Demo #221> (Jun 4) · <…|recording> · <…|AI notes>
    - <@U083NKZET6C|Francis Pereira> demoed pre-sales → post-sales handoff automation, consolidating customer data from Zoom, Slack, HubSpot, and Gmail into a handoff note for opportunities over $50k.
    - <@U083NKZET6C|Francis Pereira> demoed customer ROI tracking, a Claude Chrome extension that weighs Grafana service usage against AWS spend to flag price justification and churn risk.
    - <@U0914RU9ZQE|Paolo Salvatori> demoed Microsoft Entra workload ID on the AKS emulator, federating Kubernetes service-account identities with Entra ID so pods reach Azure resources without explicit credentials.
    - <@U06VCCA6Z50|Bart> demoed MCP pre-flight validation, an MCP server that surfaces static REST-API coverage to assess IaC (CloudFormation/Terraform) before deploy.
    - <@U082ZNQJ5HR|Pat> demoed a MongoDB Atlas extension for LocalStack, managing the Atlas admin API and database, with DB triggers and two-way AWS integration.
- <…|Weekly Demo #222> (Jun 11) · <…|recording> · <…|AI notes>
    - <@U0B2M6BSJ1J|Josh> demoed a Rust-based Kinesis mock, a stable, memory-efficient rewrite of the Kinesis mock in Rust that replaces the old Scala implementation.
    - <@U082WKSK6QM|Patricia> demoed the LocalStack skills repository (localstack-skills-internal), reusable coding-agent skills for QA and PR-evidence workflows.
    - <@U087TJ7G3BK|nikos> demoed <…|Vibe-coded durable lambda functions> :robot_face:, locally testable durable Lambda functions with state tracking and pause/resume.
- <…|Weekly Demo #223> (Jun 18) · <…|recording> · <…|AI notes>
    - <@U026TRYT7NF|Alex> demoed <…|Consolidate ALL the services!>, moving AWS service emulators from localstack-core into localstack-pro-core (26 of 37 done in ~4 days, agent-assisted via a reusable skill).
    - <@U085P9NJK96|Misha> demoed a new App Inspector feature: search, querying operations across request and response payloads.

**:busts_in_silhouette: Team Movements**
- :wave: Carlos Arilla joined the DeployX squad as Senior Software Engineer (Jun 4). Kubernetes, containers, and networking, with nearly 20 years of experience. <…|Hello in #general>.
- :wave: Andrew Thomas joined as Staff Technical Product Manager (Jun 22). Ex-AWS (launched & ran ECR), GitLab, and Angi. <…|Welcome from Waldemar>.
- :saluting_face: Thomas Rausch is now fully transitioning out of all day-to-day operations at the end of June, staying on as a shareholder and advisor. He built LocalStack's product engineering org from the ground up (<…|his note to the team>). :sad-turtle:
- :crying_cat_face: Farewell to Erudit Morina (last day Jun 30), who helped mature the Snowflake emulator (<…|his goodbye>).

**:playground_slide: A Byte of Fun**
- :scales: <@U02D4SWLYQ1|silvio> polled the team: a CI pipeline that's 120 minutes but never flaky, or 10 minutes with the occasional flake? <…|86% took the flake.> :racing_car:

---

## Issue #28 (posted 2026-06-02, #engineering)

:fyi::rolled_up_newspaper:Engineering Digest:rolled_up_newspaper::fyi:
Welcome to the 28th issue of our Engineering Digest! ...

**:ask: RFCs - Requests for Comments**
- <…|Evolving the 45-day AWS Trial> (Decision Register — due Jun 5). Three options on the table for AWS trial length: keep 45 days, reduce to 30 ("first month free"), or revert to 14. Analysis shows 70% of 45-day trialists convert within the first 14 days, while the day-31-45 cluster still accounts for 16% of paid conversions. Your input is welcome!
- <…|Protecting sidecar containers> (Incubator — New :bulb:). Proposal to reuse the existing localstack-pro source-encryption mechanism for public sidecar containers, so a clone that pulls one gets a useless binary blob without a valid LocalStack auth token. Friction, not a trust boundary.
- <…|Closing LocalStack value-added components repositories> (Decision Register — In Discussion). Still open: should lstk, the VS Code extension, the Desktop App, and the Docker extension repos be made private? Decision table is still blank, add your view.

**:newspaper: News & Updates**
- :large_orange_square: Itaú Unibanco closed as a customer (Jun 1). LocalStack's first seven-figure land and second seven-figure customer overall. <…|Full announcement by Albert in #general>.
- :closed_lock_with_key: Pursuing Cyber Essentials certification. <…|Announced by Bart on Jun 1>. A stepping stone toward SOC 2 and ISO 27001; a new Head of Security joins in August.
- :mega: People Announcements has a new home. The People Team launched a <…|monthly People Announcements page in Notion> (<…|announcement, May 29>).
- :memo: Mid-year performance review cycle opens Jun 1. Self-reflection Jun 1-10, manager reflection Jun 10-30, 1:1s Jul 1-10. <…|Announcement by Mariya in #general>.

**:partying_face: #released**
- :snowflake: <…|LocalStack for Snowflake v2026.5.0> shipped on May 27 (<…|announcement>).
- :aws: <…|LocalStack for AWS v2026.04.3> — the final patch on the 2026.04 line — shipped alongside v2026.05.0 on May 20.

Haven't seen your contribution here? <https://localstack-cloud.slack.com/archives/C07JJQVFY86|Post in #released!>

**:judge: Decisions made**
- <…|SaaS Documentation Structure for the Agentic Age> (decided Jun 1, GO). <@…|Simon Wallner>'s proposal to externalize SaaS tribal knowledge into a hierarchical docs/platform/ folder.
    ◦ Why: the folder is maintained with agent-assisted workflows (docs-writing, docs-match-code, code-matches-docs, docs survey, docs review, reference history).

**:film_projector: Demos and other cool things to watch**
- <…|Weekly Demo #219 (tech)> (May 21) · <…|recording>
    - <@U079TG6R35F|Brian> demoed <…|Gamifying LocalStack>, a demo app prototype.
    - <@U02QCBRJ8BE|Harsh Mishra> demoed <…|Extension Studio>.
- <…|Weekly Demo #220> (May 28), driven by <@U0900BMTARW|Duncan> · <…|recording>
    - <@U026TRYT7NF|Alex> demoed <…|Randomize early>, with a final recap of the code consolidation effort.
    - <@U03ENCGP63Y|Lukas> demoed <…|Pentest 2026 pt2>.
    - <@U06CRM8VCSH|Marko Macerl> demoed <…|CrawlChat powered Support chat>.
    - <@U09JRMGQUMR|Steve Purcell> demoed <…|Multi-cloud, multi-language emulators>.

**:busts_in_silhouette: Team Movements**
- :crying_cat_face: <…|Mathieu Cloutier is leaving LocalStack>. Last day Jun 5. Thank you for the work on AWS Replicator.
- :mega: New Head of Security joining in August. Part of the Cyber Essentials / SOC 2 / ISO 27001 push noted above.

**:playground_slide: A Byte of Fun**
- Ever felt like blowing half a billion (with a capital B) on tokens? <…|Well, you are not alone>.
