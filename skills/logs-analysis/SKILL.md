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

`lstk` forwards host environment variables **prefixed with `LOCALSTACK_`** into the emulator, so LocalStack config variables need that prefix:

```bash
# Start with debug mode
LOCALSTACK_DEBUG=1 lstk start

# Trace-level logging
LOCALSTACK_LS_LOG=trace lstk start
```

To make debug logging the default for a project, use an environment profile in `config.toml`:

```toml
[[containers]]
type = "aws"
env  = ["debug"]

[env.debug]
DEBUG = "1"
```

Keys inside an `[env.*]` profile do not need the `LOCALSTACK_` prefix.

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

### Common Error Patterns

| Error | Possible Cause | Solution |
|-------|---------------|----------|
| `ResourceNotFoundException` | Resource doesn't exist | Create the resource first; confirm with `lstk status` |
| `AccessDeniedException` | IAM policy issue | Check IAM enforcement mode |
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

### Enable Lambda Debug Mode

```bash
LOCALSTACK_LAMBDA_DEBUG=1 lstk start
```

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
- **Missing debug info**: Start with `LOCALSTACK_DEBUG=1` for verbose logging
- **Lambda issues**: Check both the emulator logs and CloudWatch Logs
- **Intermittent errors**: Look for resource limits or timing issues
- **CLI-level problems**: Check `lstk.log` in the directory reported by `lstk config path`
