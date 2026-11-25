---
name: localstack-app-inspector
description: Trace requests through LocalStack with App Inspector. Use when users want to see how a request flowed across AWS services, inspect traces, spans, events, or payloads, debug event-driven or service-to-service flows, or see which IAM policy evaluation allowed or denied a call.
---

# Trace requests with App Inspector

App Inspector records the operations your application sends to the AWS emulator as **traces** (one end-to-end flow), made of **spans** (one service operation each), carrying **events** (payload metadata, IAM policy evaluations, and more). Use it when logs show *that* something failed but not *where* in a multi-service flow.

## Check prerequisites

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

# Why was this call denied?
curl -s "$AI/traces/$TRACE/spans/$SPAN/events/iam" | jq
```

## Debugging workflow

1. `lstk inspect enable`, and clear old traces (`DELETE /traces` with `{}`) so only this run is recorded.
2. Run the workload or failing test.
3. List traces filtered to the service or resource under suspicion; pick the one whose status code is an error.
4. List its spans to see the service-to-service path; find the first span that failed.
5. Read that span's events for the payload, and its `events/iam` for the policy decision when the error is an access denial.
6. Cross-check the time window in `lstk logs --verbose` — see the `localstack-logs` skill.

IAM evaluation events are recorded only while IAM enforcement is on — see the `localstack-iam` skill.
