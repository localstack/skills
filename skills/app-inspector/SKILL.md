---
name: localstack-app-inspector
description: Trace requests through LocalStack with App Inspector. Use when users want to see how a request flowed across AWS services, inspect traces, spans, events, or payloads, debug event-driven or service-to-service flows, or explain an IAM denial, get LocalStack's suggested policy fix, or derive least-privilege policies from a run.
---

# App Inspector

App Inspector records the operations your application sends to the AWS emulator as **traces** (one end-to-end flow), made of **spans** (one service operation each), carrying **events** (payload metadata, IAM policy evaluations, and more). Use it when logs show *that* something failed but not *where* in a multi-service flow.

## Prerequisites

- A running AWS emulator (`lstk start`) — see the `localstack` skill
- A license that includes App Inspector

## Turn it on

```bash
lstk inspect enable
lstk inspect disable
```

Only operations made while it is enabled are recorded, so enable it **before** running the workload. To enable it on every start, set `APP_INSPECTOR = "1"` in an `[env.*]` profile in `config.toml`.

The REST equivalent, handy in scripts:

```bash
curl -s localhost:4566/_localstack/appinspector/status
curl -s -X PUT localhost:4566/_localstack/appinspector/status \
  -H 'Content-Type: application/json' -d '{"status":"enabled"}'
```

Traces are also browsable in the LocalStack Web Application and the LocalStack Toolkit for VS Code. Use the API below when you need to query them yourself.

## Query traces

Base path: `http://localhost:4566/_localstack/appinspector/v1`.

| Goal | Request |
|------|---------|
| List traces | `GET /traces` |
| One trace | `GET /traces/{trace_id}` |
| Spans in a trace | `GET /traces/{trace_id}/spans` |
| One span | `GET /traces/{trace_id}/spans/{span_id}` |
| Events on a span | `GET /traces/{trace_id}/spans/{span_id}/events` |
| One event | `GET /traces/{trace_id}/spans/{span_id}/events/{event_id}` |
| IAM evaluations on a span | `GET /traces/{trace_id}/spans/{span_id}/events/iam` |
| Delete traces | `DELETE /traces` with `{"trace_ids":[...]}`, or `{}` for all |
| Delete spans | `DELETE /traces/{trace_id}/spans` with `{"span_ids":[...]}`, or `{}` for all |

Use `*` as `trace_id` or `span_id` to query across all traces or spans — for example `GET /traces/*/spans/*/events/iam` lists every IAM evaluation recorded.

Filters for traces and spans (query string): `service_name`, `operation_name`, `resource_name`, `arn`, `region`, `account_id`, `status_code`, `parent_span_id`, `start_time_unix_nano`, `end_time_unix_nano`, `version`. Filters for events: `name`, `event_type` (e.g. `iam.policy_evaluation`), `timestamp_unix_nano`. Paginate with `limit` (1–1000) and the `pagination_token` from the previous response.

```bash
AI=localhost:4566/_localstack/appinspector/v1

# Failed Lambda traces
curl -s "$AI/traces?service_name=lambda&status_code=500&limit=20" | jq

# Walk one trace
curl -s "$AI/traces/$TRACE/spans" | jq
curl -s "$AI/traces/$TRACE/spans/$SPAN/events" | jq

# Every IAM evaluation on one span
curl -s "$AI/traces/$TRACE/spans/$SPAN/events/iam" | jq
```

## Explain IAM denials

Start here for any permission error, such as `AccessDenied` or `is not authorized to perform`, before changing a policy, role, or bucket, key, or queue policy. LocalStack records each request it denies together with the policies that decided it and a suggested fix. That includes policies you cannot read yourself, such as another account's bucket, KMS key, or event bus, and denials that never surface as an error, such as an event source mapping, a subscription, or a workflow step. Do not conclude that another team or account must change its policy until you have read the denial here.

The suggestions and auto-derived policies need a recent LocalStack image and a license that includes them. On an older image, denial events carry no `suggestion`.

### Record denials without enforcing them

Enforcement is not needed to record denials. When App Inspector goes from disabled to enabled, LocalStack moves IAM from `DISABLED` to `ENGINE_ONLY`, which evaluates every request and records denials without blocking them. Never switch to `ENFORCED` just to see denials; it can break a workload that works. Read or set the mode through `/_aws/iam/config`, as in the `localstack-iam` skill. If the mode is `DISABLED`, nothing is evaluated or recorded; set `ENGINE_ONLY`.

Disabling App Inspector and enabling it again deletes what it recorded, unless persistence is on.

### List denials

Denials are events named `iam.policy.denied`, listed across all traces, newest first:

```bash
curl -s "$AI/traces/*/spans/*/events/iam?name=iam.policy.denied&limit=20" | jq
```

Each event's `attributes.payload` holds the evaluation, as a JSON string or an object. Decode it and read `service`, `operation`, `principal_arn`, and `enforcement`: `deny` for a request that failed, `allow_with_warning` for one that `SOFT_MODE` or `ENGINE_ONLY` let through.

```bash
curl -s "$AI/traces/*/spans/*/events/iam?name=iam.policy.denied&limit=20" \
  | jq '(.events // .)[] | {event_id, span_id, p: (.attributes.payload | if type == "string" then fromjson else . end)}
        | {event_id, span_id, service: .p.service, operation: .p.operation,
           principal: .p.principal_arn, enforcement: .p.enforcement, outcome: .p.suggestion.outcome}'
```

Requests to STS, IAM, and CloudWatch Logs, and `sqs:GetQueueUrl`, `sqs:GetQueueAttributes`, and `cloudwatch:PutMetricData`, are not recorded, so their denials never appear. A role's trust policy failing `sts:AssumeRole` is the common case; find it with the IAM Policy Stream instead (`localstack-iam` skill).

An empty list does not prove that nothing was denied. Read one span with `GET /traces/*/spans?limit=1`: `iam_errors_suppressed: true` means the license hides IAM events, and no spans at all means nothing was recorded. Events named `iam.policy.error` count evaluations that failed.

### Explain one denial

Fetch the event by id:

```bash
curl -s "$AI/traces/*/spans/*/events/iam?event_id=$EVENT" \
  | jq '(.events // .)[0].attributes.payload | if type == "string" then fromjson else . end'
```

Read the payload in this order:

1. **The request and its result:** `service`, `operation`, `principal_arn`, `enforcement`.
2. **The deciding policies:** `explicit_denies` and `implicit_denies` name the action, the resource, and `caused_by`, which points to keys in `policies` and the statement indexes that decided. `cross_account: true` marks a decision made in another account.
3. **The suggested fix**, in `suggestion`:
   - `outcome`: `fixes` means applying every entry allows the request. `partial` means the entries are not enough on their own, and `hints` say what else blocks it. `unfixable` means no policy change listed fixes it. `already_allowed` means the current policies already allow it, because they changed after the request, so nothing has to change.
   - `entries`: one per policy to change, with `attach_to`, the existing `policy` or a `new_policy`, and `statements_to_add` and `statements_to_remove`.
   - `near_misses`: statements that almost allowed the request, with a `reason` such as `other_resource` or `condition`. They help find where the policy is defined, and often show what to change in your own request or role.
   - `hints`: what else blocks the request, such as a Deny the suggestion cannot change.

Apply the suggestion as LocalStack sent it:

- Make the change in the project's infrastructure code (CDK, Terraform, CloudFormation or SAM, or deployment scripts), not with one-off CLI calls.
- Merge the statements into the existing policies instead of replacing them. Create a policy only where an entry names a `new_policy`.
- Grant exactly the statements listed. Ask before widening a `Resource`, for example from one object to `bucket/*`.
- Entries marked `guardrail: true` remove a Deny or change a permissions boundary or service control policy. Confirm each one with the user. Never remove or weaken a Deny, boundary, or SCP on your own; report it and ask how to proceed.

A denial without a `suggestion` gets none from LocalStack; work from the deciding policies.

### Fetch a truncated policy

An event stores large policies truncated: a policy in `policies` with fewer `statements` than its `statement_count`. Fetch the full documents only when you need them, by the policy's key in `policies`, such as `p1`:

```bash
curl -s "$AI/events/$EVENT/policies/p1" | jq .documents
```

The response is the policy as LocalStack stores it now. A `hash` different from the one in the event means the policy changed after the request. Errors carry a `code`: `policy_not_found` means the policy was deleted or detached since, and `not_entitled` means the license hides policy details.

### Check a fix

After fixing the code, redeploying, and re-running the workload, list only the denials recorded since the first check. Pass the `prev_cursor` from the first list's `pagination` as `pagination_token`:

```bash
CURSOR=$(curl -s "$AI/traces/*/spans/*/events/iam?name=iam.policy.denied&limit=20" | jq -r .pagination.prev_cursor)
# fix, redeploy, re-run
curl -s "$AI/traces/*/spans/*/events/iam?name=iam.policy.denied&limit=20&pagination_token=$CURSOR" | jq
```

The fix is done when this list is empty. If LocalStack answers 400 because the store was reset, list again without the cursor.

## Derive least-privilege policies

LocalStack derives one least-privilege policy per principal or resource ARN from the requests it evaluates. Clear the summary, run the workload once, then read it:

```bash
curl -s -X DELETE localhost:4566/_aws/iam/policies/summary
# run the workload
curl -s localhost:4566/_aws/iam/policies/summary | jq
```

Each entry has a `resource` ARN, a `policy_type` of `identity` or `resource`, and a `policy_document`. Use the documents exactly as sent. A role's trust statements, the ones with a `Principal`, arrive in the same document as its permissions; split them into the trust policy when writing IaC.

The summary covers every request since it was last cleared, across the whole emulator, so clear it right before the run you care about. Treat it as a suggestion derived from the requests seen, not a verified policy: apply it, switch to `ENFORCED`, and re-run. A 404 means the license does not include IAM Policy Stream or the image is too old.

## Debugging workflow

1. `lstk inspect enable`, and clear old traces (`DELETE /traces` with `{}`) so only this run is recorded.
2. Run the workload or failing test.
3. For a permission error, follow [Explain IAM denials](#explain-iam-denials) and stop there.
4. Otherwise list traces filtered to the service or resource under suspicion, and pick the one whose status code is an error.
5. List its spans to see the service-to-service path, and find the first span that failed.
6. Read that span's events for the payload.
7. Cross-check the time window in `lstk logs --verbose`; see the `localstack-logs` skill.
