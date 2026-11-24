---
name: localstack-chaos
description: Inject faults and network latency into LocalStack to test resilience. Use when users want chaos engineering, to simulate AWS outages or throttling, return errors from specific services or operations, add latency, or verify retry and fallback logic.
---

# Chaos Engineering

Make LocalStack fail on purpose — return AWS errors from chosen services, regions, or operations, or slow every response down — so you can prove retry, timeout, and fallback logic works before production does it for you.

## Prerequisites

- A running AWS emulator (`lstk start`) — see the `localstack` skill
- A license that includes Chaos Engineering. Check it with `curl -s localhost:4566/_localstack/licenseinfo`.

`lstk` has no chaos command. Drive the Chaos API on the emulator gateway with `curl`. All calls below assume `http://localhost:4566`; adjust if you set `LOCALSTACK_HOST` or a different port.

## Fault rules

A fault rule matches requests and makes them fail. Every field is optional; an omitted field matches everything.

| Field | Example | Meaning |
|-------|---------|---------|
| `service` | `"dynamodb"` | AWS service to affect |
| `region` | `"us-east-1"` | Region to affect |
| `operation` | `"PutItem"` | API operation to affect |
| `probability` | `0.5` | Chance (0.0–1.0) a matching request fails; default always |
| `error.statusCode` | `503` | HTTP status to return |
| `error.code` | `"ServiceUnavailable"` | AWS error code to return |

The rule body is a **JSON array** of rules on every call.

| Goal | Call |
|------|------|
| Replace all rules | `POST /_localstack/chaos/faults` |
| Add rules, keep existing | `PATCH /_localstack/chaos/faults` |
| Remove matching rules | `DELETE /_localstack/chaos/faults` (body must match the stored rule exactly) |
| List active rules | `GET /_localstack/chaos/faults` |
| Clear all rules | `POST /_localstack/chaos/faults` with `[]` |

```bash
# Make half of DynamoDB PutItem calls in us-east-1 throttle
curl -s -X POST localhost:4566/_localstack/chaos/faults \
  -H 'Content-Type: application/json' \
  -d '[{"service":"dynamodb","region":"us-east-1","operation":"PutItem","probability":0.5,
        "error":{"statusCode":400,"code":"ProvisionedThroughputExceededException"}}]'

# Add a full S3 outage on top
curl -s -X PATCH localhost:4566/_localstack/chaos/faults \
  -H 'Content-Type: application/json' \
  -d '[{"service":"s3","error":{"statusCode":503,"code":"ServiceUnavailable"}}]'

# Inspect, then remove just the S3 rule
curl -s localhost:4566/_localstack/chaos/faults | jq
curl -s -X DELETE localhost:4566/_localstack/chaos/faults \
  -H 'Content-Type: application/json' \
  -d '[{"service":"s3","error":{"statusCode":503,"code":"ServiceUnavailable"}}]'

# Back to normal
curl -s -X POST localhost:4566/_localstack/chaos/faults -H 'Content-Type: application/json' -d '[]'
```

A rule with no `service`, `region`, or `operation` fails **every** request, including the ones your test harness uses to set up and verify. Scope rules as narrowly as the experiment allows.

## Network latency

Latency applies to every response from the emulator.

```bash
# Add 500 ms to every response
curl -s -X POST localhost:4566/_localstack/chaos/effects \
  -H 'Content-Type: application/json' -d '{"latency": 500}'

# Current effects
curl -s localhost:4566/_localstack/chaos/effects | jq

# Clear
curl -s -X POST localhost:4566/_localstack/chaos/effects \
  -H 'Content-Type: application/json' -d '{"latency": 0}'
```

## Experiment workflow

1. Record the steady state: run the workload once with no faults and note the expected outcome.
2. Inject one fault or latency setting, then read it back with `GET` to confirm it is active.
3. Run the workload or test suite.
4. Measure the impact: `lstk logs -v | grep -E "=> (4|5)[0-9]{2}"` shows the failed calls; see the `localstack-logs` skill for deeper analysis and the `localstack-app-inspector` skill to follow a request across services.
5. Clear faults **and** latency before the next experiment, even when the run errors out — leftover rules silently break unrelated work.

Faults live in memory: `lstk restart` and `lstk reset` also clear them.
