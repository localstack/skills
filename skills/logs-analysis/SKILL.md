---
name: localstack-logs
description: Analyze LocalStack logs and debug issues with lstk. Use when users need to view LocalStack logs, debug AWS API errors, troubleshoot Lambda functions, identify error patterns, or enable debug mode.
---

# LocalStack Logs Analysis

Analyze LocalStack logs to debug issues, identify errors, and understand AWS API interactions.

## Capabilities

- View and filter LocalStack logs
- Identify error patterns and failures
- Analyze AWS API request/response cycles
- Track service-specific operations
- Debug Lambda function executions

## Prerequisites

- The `lstk` CLI with a running emulator — see the `localstack` skill

## Viewing Logs

### Basic Log Commands

```bash
# Print available logs
lstk logs

# Follow logs in real time
lstk logs -f

# Last N lines
lstk logs -n 100

# Unfiltered output (lstk filters noise by default)
lstk logs -v
```

Reach for `lstk logs -v` whenever a log line you expect is missing — the default view drops low-signal output.

### Filtering Logs

```bash
# Filter by service
lstk logs | grep -i s3
lstk logs | grep -i lambda
lstk logs | grep -i dynamodb

# Filter errors only
lstk logs | grep -i error
lstk logs | grep -i exception

# Filter by request ID (use -v so nothing is filtered out first)
lstk logs -v | grep "request-id-here"
```

### Diagnostic Logs

`lstk` writes its own diagnostic log to `lstk.log` in the config directory — useful when the CLI itself misbehaves rather than the emulator:

```bash
lstk config path      # the lstk.log sits alongside this file
```

## Debug Mode

Turn on verbose logging with an environment profile in `config.toml`, then `lstk restart`:

```toml
[[containers]]
type = "aws"
env  = ["debug"]

[env.debug]
DEBUG = "1"
LS_LOG = "trace"         # optional: request/response-level detail
LAMBDA_DEBUG = "1"       # optional: Lambda debugging
```

Remove `"debug"` from `env` when you are done; trace logging is noisy. For a single throwaway run, `LOCALSTACK_DEBUG=1 lstk start` also works, but it is lost on the next plain `lstk restart` — see the `localstack` skill.

## Analyzing API Requests

### Request/Response Tracking

LocalStack logs include AWS API requests. Look for patterns like:

```
AWS <service>.<operation> => <status>
```

Example log entries:
```
AWS s3.CreateBucket => 200
AWS dynamodb.PutItem => 200
AWS lambda.Invoke => 200
```

### Deployed Resources

`lstk status` lists the resources currently deployed in the emulator, which is often faster than grepping logs to answer "does this resource exist?":

```bash
lstk status
lstk --non-interactive status
```

### Structured Analysis

Pick the view that matches the question:

```bash
# Summary: how many calls, how many failed, the latest failures
lstk logs -v -n 2000 | grep -cE "AWS [a-z0-9-]+\.[A-Za-z]+ =>"
lstk logs -v -n 2000 | grep -E "AWS [a-z0-9-]+\.[A-Za-z]+ => [45][0-9]{2}" | tail -5

# Errors: failed calls grouped by service.operation and status, most frequent first
lstk logs -v -n 2000 | grep -oE "AWS [a-z0-9-]+\.[A-Za-z]+ => [45][0-9]{2}( \([A-Za-z]+\))?" \
  | sort | uniq -c | sort -rn

# Requests: every call to one operation, in order
lstk logs -v | grep -E "AWS dynamodb\.PutItem =>"

# Raw: stack traces and ERROR lines around a failure
lstk logs -v -n 2000 | grep -E -B2 -A15 "ERROR|Traceback"
```

Group errors before reading them: one root cause usually produces many identical lines, and the count tells you which one matters.

### Common Error Patterns

| Error | Possible Cause | Solution |
|-------|---------------|----------|
| `ResourceNotFoundException` | Resource doesn't exist | Create the resource first; confirm with `lstk status` |
| `AccessDeniedException` / `... is not authorized to perform` | IAM enforcement denied the call | Generate the missing policy — see the `localstack-iam` skill |
| `501` / `NotImplemented` | Operation not covered by LocalStack | Check the service's coverage page on docs.localstack.cloud |
| Unexpected `5xx` with a chaos rule active | Injected fault | `curl -s localhost:4566/_localstack/chaos/faults` — see the `localstack-chaos` skill |
| `ValidationException` | Invalid parameters | Verify request parameters |
| `ServiceException` | Internal error | Check LocalStack logs for details |

## Lambda Debugging

### View Lambda Logs

```bash
# Lambda function logs appear in the emulator logs
lstk logs -v | grep -A 10 "Lambda"

# Or use CloudWatch Logs locally
lstk aws logs describe-log-groups
lstk aws logs get-log-events \
  --log-group-name /aws/lambda/my-function \
  --log-stream-name <stream-name>
```

For Lambda debug mode, add `LAMBDA_DEBUG = "1"` to the debug profile above.

## Health Check

```bash
# Check overall health
curl http://localhost:4566/_localstack/health | jq

# Check specific service
curl http://localhost:4566/_localstack/health | jq '.services.s3'
```

## Troubleshooting Tips

- **No logs appearing**: Ensure the emulator is running (`lstk status`)
- **Expected line missing**: Re-run with `lstk logs -v` — the default view is filtered
- **Missing debug info**: Enable the `debug` profile in `config.toml` and `lstk restart`
- **Lambda issues**: Check both the emulator logs and CloudWatch Logs
- **Intermittent errors**: Look for resource limits or timing issues
- **CLI-level problems**: Check `lstk.log` in the directory reported by `lstk config path`
- **Failure spans several services** (Lambda → SQS → DynamoDB): logs show each hop separately; App Inspector links them into one trace — see the `localstack-app-inspector` skill
