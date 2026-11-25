---
name: localstack-iam
description: Analyze and enforce IAM policies in LocalStack. Use when users want to enable or switch IAM enforcement, detect permission violations, fix an access denial, auto-generate least-privilege policies, or test IAM policies locally before deploying to AWS.
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
- A license that includes IAM enforcement
## IAM Enforcement Modes

### Enable Enforcement

Set the starting mode in an environment profile in `config.toml`, then `lstk start` (or `lstk restart`):

```toml
[[containers]]
type = "aws"
env  = ["iam"]

[env.iam]
ENFORCE_IAM = "1"
IAM_SOFT_MODE = "1"      # remove for full enforcement
```

`IAM_SOFT_MODE` only takes effect together with `ENFORCE_IAM = "1"`.

To change the mode on a running emulator without touching config, use the [runtime switch](#switch-modes-without-restarting).

### Configuration

| Mode | Profile keys at start | Runtime `state` | Behavior |
|------|-----------------------|-----------------|----------|
| Disabled (default) | unset, or `ENFORCE_IAM = "0"` | `DISABLED` | No IAM checks |
| Soft | `ENFORCE_IAM = "1"`, `IAM_SOFT_MODE = "1"` | `SOFT_MODE` | Logs violations, allows requests |
| Enforced | `ENFORCE_IAM = "1"` | `ENFORCED` | Denies unauthorized requests |
| Engine only | none; set at runtime | `ENGINE_ONLY` | Evaluates policies and records denials in App Inspector, but neither blocks nor logs them |

Enabling App Inspector moves the mode from `DISABLED` to `ENGINE_ONLY`, so denials are recorded without enforcement. Never switch to `ENFORCED` just to see denials; it can break a workload that works.

### Switch modes without restarting

The IAM config endpoint reads and changes the mode on a running emulator, so you can flip enforcement between test runs instead of restarting:

```bash
# Current mode
curl -s localhost:4566/_aws/iam/config | jq .state

# Change it: ENFORCED, SOFT_MODE, ENGINE_ONLY, or DISABLED
curl -s -X POST localhost:4566/_aws/iam/config \
  -H 'Content-Type: application/json' -d '{"state":"SOFT_MODE"}'
```

The runtime change lasts until the emulator restarts; use the start-time setting above for a default.

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

### Explain a denial with App Inspector

Start with App Inspector for any permission error. LocalStack records each denied request with the policies that decided it, including another account's policies that you cannot read, and a suggested fix. It also derives least-privilege policies from a run. See the "Explain IAM denials" and "Derive least-privilege policies" sections of the `localstack-app-inspector` skill.

Use the logs below only for what App Inspector does not cover: requests to STS, IAM, and CloudWatch Logs (for example a trust policy failing `sts:AssumeRole`), and a license or image without App Inspector's IAM events.

### Detect violations in the logs

1. Enable soft or enforced mode
2. Run your application
3. Pull the denials from the logs (`-v` disables `lstk`'s default log filtering)

LocalStack writes a denial in one of two formats:

```
Request for service 'sqs' by principal 'arn:aws:iam::000000000000:role/app' for operation 'SendMessage' denied.
User: arn:aws:iam::000000000000:role/app is not authorized to perform: sqs:SendMessage on resource: arn:aws:sqs:... because ...
```

```bash
lstk logs -v | grep -E "for operation '[^']*' denied\.|is not authorized to perform:"
```

Some lines also carry `Action '<service:Action>' for '<resource-arn>'`, which pins the resource for a denial.

### Generate a policy from the denials

Prefer the policies LocalStack derives (see above). Without them:

1. Switch to `SOFT_MODE`, so the run completes instead of stopping at the first denial.
2. Exercise the full workload once.
3. Extract each unique **(principal, action, resource)** from the denial lines above. Normalize the action to `service:Operation` (the first format gives service and operation separately).
4. Group by principal, then write one policy per principal: one statement per resource, listing its actions. Use the exact resource ARN when the log gives one; fall back to `*` only for actions that do not support resource-level permissions, and say so.
5. Attach the policy, switch to `ENFORCED`, rerun the workload, and repeat until no denials remain.

Done when an enforced run produces no denial lines.

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

- Read denials and suggested fixes in App Inspector before changing a policy
- Start with soft enforcement to discover required permissions
- Flip modes at runtime through `/_aws/iam/config` between runs instead of restarting
- Use least-privilege principles when creating policies
- Test policies locally before deploying to AWS
- Snapshot a known-good IAM setup with `lstk save` so you can restore it after experiments
- Regularly audit and refine policies based on actual usage
- Use IAM roles instead of users where possible
