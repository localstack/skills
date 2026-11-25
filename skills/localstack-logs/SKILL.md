---
name: localstack-logs
description: Analyze LocalStack emulator logs with lstk. Use when debugging AWS API errors, Lambda failures, startup problems, IAM denials, request patterns, or service-specific behavior.
---

# Analyze LocalStack logs

Use `lstk logs` so log collection follows the configured emulator and container runtime.

## Collect the right log view

```bash
# Recent output
lstk logs --tail 100

# Stream new output
lstk logs --follow

# Include request and provider lines filtered from the default view
lstk logs --verbose --tail 200
```

Use `--verbose` for AWS request analysis; the default view removes routine request/provider noise.

Filter a captured view when looking for a specific service, request ID, or failure:

```bash
lstk logs --verbose --tail 500 | grep -i 's3'
lstk logs --verbose --tail 500 | grep -i 'error\|exception'
lstk logs --verbose --tail 500 | grep 'request-id-here'
```

Do not assume a fixed underlying container name.

## Read the CLI's own log

`lstk logs` shows emulator output only. The CLI writes its own timestamped diagnostic log to `lstk.log` in the configuration directory:

```bash
lstk config path   # lstk.log sits in this directory
```

Read it when the CLI is the problem rather than the emulator: a start that never reaches the emulator, an undetected container runtime, or a failure resolving authentication or configuration. `lstk logs` reports nothing in those cases.

## Enable detailed emulator logging

Attach a debug profile to the active emulator in the file that `lstk config path` reports:

```toml
[[containers]]
type = "aws"
env = ["debug"]

[env.debug]
DEBUG = "1"
LS_LOG = "trace"
```

Keys inside an `[env.*]` profile take no `LOCALSTACK_` prefix. For Lambda-specific diagnostics, add `LAMBDA_DEBUG = "1"` only when the current LocalStack documentation recommends it for the runtime under investigation. Restart after changing emulator environment:

```bash
lstk restart
```

Remove `"debug"` from `env` when done; trace logging is noisy. For a single throwaway run, `LOCALSTACK_DEBUG=1 lstk start` also works, but a plain `lstk restart` drops it; see the `localstack` skill.

## Diagnose AWS API failures

1. Reproduce the failing request once.
2. Capture `lstk logs --verbose --tail 500`.
3. Locate the service and operation, HTTP status, request ID, and the first causal exception.
4. Distinguish an application error from an emulator startup, configuration, or coverage issue.
5. Confirm the resource exists: check `lstk status` first, then the `lstk aws` proxy for anything it does not cover.
6. Make the smallest configuration or application change, reproduce, and compare the new logs.

Under `--verbose`, handled AWS calls appear as request lines naming the service, operation, and HTTP status, typically in the shape `AWS <service>.<operation> => <status>` (for example `AWS s3.CreateBucket => 200`). Grep the operation name or a non-2xx status to isolate the failing call.

Pick the view that matches the question:

```bash
# Summary: how many calls, and the latest failures
lstk logs --verbose --tail 2000 | grep -cE "AWS [a-z0-9-]+\.[A-Za-z]+ =>"
lstk logs --verbose --tail 2000 | grep -E "AWS [a-z0-9-]+\.[A-Za-z]+ => [45][0-9]{2}" | tail -5

# Errors: failed calls grouped by service.operation and status, most frequent first
lstk logs --verbose --tail 2000 | grep -oE "AWS [a-z0-9-]+\.[A-Za-z]+ => [45][0-9]{2}( \([A-Za-z]+\))?" \
  | sort | uniq -c | sort -rn

# Requests: every call to one operation, in order
lstk logs --verbose | grep -E "AWS dynamodb\.PutItem =>"

# Raw: stack traces and ERROR lines around a failure
lstk logs --verbose --tail 2000 | grep -E -B2 -A15 "ERROR|Traceback"
```

Group errors before reading them: one root cause usually produces many identical lines, and the count shows which one matters.

Common signals include:

| Signal | Check |
| --- | --- |
| `ResourceNotFoundException` | Confirm resource name, region, and account; check `lstk status` |
| `AccessDenied` or `... is not authorized to perform` | IAM enforcement denied the call; see the `localstack-iam` skill |
| `501` or `NotImplemented` | The operation is not covered; check the service's coverage page on docs.localstack.cloud |
| Unexpected `5xx` while a chaos rule is active | Injected fault; run `curl -s localhost:4566/_localstack/chaos/faults` and see the `localstack-chaos` skill |
| `ValidationException` | Compare request parameters with the AWS API contract |
| Connection refusal or timeout | Check `lstk status`, ports, and readiness |
| Provider exception | Read the first stack trace and check service coverage |

When a failure spans several services, such as Lambda to SQS to DynamoDB, the logs show each hop separately. App Inspector links them into one trace; see the `localstack-app-inspector` skill.

## Inspect Lambda logs

First inspect emulator-level failures:

```bash
lstk logs --verbose --tail 500 | grep -i 'lambda'
```

Then query emulated CloudWatch Logs:

```bash
lstk aws logs describe-log-groups
lstk aws logs describe-log-streams \
  --log-group-name /aws/lambda/my-function \
  --order-by LastEventTime \
  --descending
lstk aws logs get-log-events \
  --log-group-name /aws/lambda/my-function \
  --log-stream-name <stream-name>
```

## Check health

Prefer the configuration-aware status command:

```bash
lstk status
```

`lstk status` also lists the resources currently deployed in the emulator, which answers "does this resource exist?" faster than grepping logs. Add `--non-interactive` when a script captures the output:

```bash
lstk --non-interactive status
```

For a default local endpoint, inspect the raw health payload only when needed:

```bash
curl -s http://localhost:4566/_localstack/health | jq '.services.s3'
```

`lstk logs` has no external-emulator mode. When using `--endpoint-url`, obtain logs from the system that owns that emulator and use `lstk --endpoint-url <url> status` for reachability.
