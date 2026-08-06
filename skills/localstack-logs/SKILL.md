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

## Enable detailed emulator logging

Find the active config:

```bash
lstk config path
```

Attach a debug profile to the active emulator:

```toml
[[containers]]
type = "aws"
env = ["debug"]

[env.debug]
DEBUG = "1"
LS_LOG = "trace"
```

For Lambda-specific diagnostics, add `LAMBDA_DEBUG = "1"` only when the current LocalStack documentation recommends it for the runtime under investigation. Restart after changing emulator environment:

```bash
lstk restart
```

## Diagnose AWS API failures

1. Reproduce the failing request once.
2. Capture `lstk logs --verbose --tail 500`.
3. Locate the service and operation, HTTP status, request ID, and the first causal exception.
4. Distinguish an application error from an emulator startup, configuration, or coverage issue.
5. Verify the resource exists with the `lstk aws` proxy.
6. Make the smallest configuration or application change, reproduce, and compare the new logs.

Common signals include:

| Signal | Check |
| --- | --- |
| `ResourceNotFoundException` | Confirm resource name, region, and account |
| `AccessDenied` | Inspect IAM enforcement and the request credentials |
| `ValidationException` | Compare request parameters with the AWS API contract |
| Connection refusal or timeout | Check `lstk status`, ports, and readiness |
| Provider exception | Read the first stack trace and check service coverage |

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

For a default local endpoint, inspect the raw health payload only when needed:

```bash
curl http://localhost:4566/_localstack/health
```

`lstk logs` has no external-emulator mode. When using `--endpoint-url`, obtain logs from the system that owns that emulator and use `lstk --endpoint-url <url> status` for reachability.
