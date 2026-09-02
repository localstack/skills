---
name: localstack-iam
description: Analyze and enforce IAM policies in LocalStack. Use when users want to enable IAM enforcement, detect permission violations, auto-generate least-privilege policies, or test IAM policies locally before deploying to AWS.
---

# IAM Policy Analyzer

Analyze IAM policies, detect permission violations, and automatically generate least-privilege policies based on actual usage.

## Capabilities

- Enforce IAM policies locally
- Detect permission violations
- Auto-generate policies from access patterns
- Analyze existing policies for issues
- Test policies before deploying to AWS

## Prerequisites

- The `lstk` CLI, authenticated with a LocalStack account (`lstk login`, or `LOCALSTACK_AUTH_TOKEN` in CI) — see the `localstack` skill
- Optional: the legacy `localstack` CLI (`pip install localstack`) for the IAM policy stream — see [Auto-Generate Policies](#auto-generate-policies). `lstk` has no equivalent command yet.

## IAM Enforcement Modes

### Enable Enforcement

`lstk` forwards host environment variables prefixed with `LOCALSTACK_`, so `ENFORCE_IAM` is set as `LOCALSTACK_ENFORCE_IAM`:

```bash
# Soft mode - logs violations but allows requests
LOCALSTACK_ENFORCE_IAM=soft lstk start

# Enforced mode - denies unauthorized requests
LOCALSTACK_ENFORCE_IAM=1 lstk start
```

To make enforcement the default for a project, use an environment profile in `config.toml` (keys inside a profile need no prefix):

```toml
[[containers]]
type = "aws"
env  = ["iam"]

[env.iam]
ENFORCE_IAM = "soft"
```

### Configuration

| Mode | Behavior |
|------|----------|
| Disabled (default) | No IAM checks |
| `soft` | Logs violations, allows requests |
| `1` / `enforced` | Full enforcement, denies unauthorized |

## Creating IAM Resources

`lstk aws` proxies the host `aws` CLI with the LocalStack endpoint, credentials, and region pre-configured.

### Create a User with Policy

```bash
# Create user
lstk aws iam create-user --user-name dev-user

# Create access key
lstk aws iam create-access-key --user-name dev-user

# Attach policy
lstk aws iam attach-user-policy \
  --user-name dev-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

### Create Custom Policy

```bash
# Create policy from JSON file
lstk aws iam create-policy \
  --policy-name my-custom-policy \
  --policy-document file://policy.json
```

```json
// Example policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

## Policy Analysis

### Detect Violations

1. Enable soft enforcement mode
2. Run your application
3. Check logs for access denied messages

```bash
# View IAM-related log entries (-v disables lstk's default log filtering)
lstk logs -v | grep -i "access denied"
lstk logs -v | grep -i "iam"
```

### Auto-Generate Policies

The legacy `localstack` CLI can print the exact policy each request would need, which is far more reliable than reading logs. There is no `lstk` equivalent yet, so install the legacy CLI alongside `lstk` for this workflow:

```bash
pip install localstack

# Live stream of recommended policies as requests come in
localstack aws iam stream
localstack aws iam stream --format json

# Aggregate summary of policies for all enforced requests
localstack aws iam summary
```

Workflow:

1. Start with `LOCALSTACK_ENFORCE_IAM=soft lstk start`
2. Run `localstack aws iam stream` in a second terminal
3. Exercise your application
4. Collect the recommended statements and merge them into a minimal policy

If the legacy CLI is not available, fall back to reading `lstk logs -v` for access-denied entries and building the policy from the observed actions and resources.

## Testing Policies

### Simulate Policy

```bash
# Test if action would be allowed
lstk aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::000000000000:user/dev-user \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/file.txt
```

### Validate Policy

```bash
# Check policy syntax
lstk aws accessanalyzer validate-policy \
  --policy-document file://policy.json \
  --policy-type IDENTITY_POLICY
```

## Best Practices

- Start with soft enforcement to discover required permissions
- Use `localstack aws iam stream` rather than log grepping when generating policies
- Use least-privilege principles when creating policies
- Test policies locally before deploying to AWS
- Snapshot a known-good IAM setup with `lstk save` so you can restore it after experiments
- Regularly audit and refine policies based on actual usage
- Use IAM roles instead of users where possible
