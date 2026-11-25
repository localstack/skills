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

Use the Policy Stream below for what App Inspector does not record, such as requests to STS and IAM (for example a trust policy failing `sts:AssumeRole`), and when the license or image has no App Inspector IAM events.

### Detect violations with the Policy Stream

`GET /_aws/iam/policies/stream` streams one JSON line for every request IAM evaluates, while the connection stays open. It needs IAM evaluation on (`SOFT_MODE`, `ENFORCED`, or `ENGINE_ONLY`) and a license that includes the IAM Policy Stream.

Open the stream before running the workload; it shows only requests made while it is connected:

```bash
curl -sN localhost:4566/_aws/iam/policies/stream > iam-stream.jsonl &
# run the workload, then stop the stream
kill %1
```

Each line holds:

- `request`: `service`, `operation`, `parameters`, `id`, `internal`, and `allowed`, which is `false` when IAM denies the request, even in a mode that lets it through
- `resource`: the principal ARN for an `identity` policy, or the resource ARN for a `resource` policy, such as a Lambda's resource policy for a service principal
- `policy_type`: `identity` or `resource`
- `policy_document`: the least-privilege policy for `resource` that allows every request seen so far for it, not only this one

Violations are the lines where `request.allowed` is `false`:

```bash
jq -c 'select(.request.allowed == false)
  | {principal: .resource, type: .policy_type, call: "\(.request.service).\(.request.operation)",
     allow: [.policy_document.Statement[] | {Action, Resource}]}' iam-stream.jsonl
```

The stream also carries every allowed request, including the root user's own calls, so always filter. A cross-account request produces two lines: an identity policy for the caller and a resource policy for the target. Add `?include_evaluation_failures=1` to also stream requests whose evaluation raised an error; those lines carry `evaluation_failed: true`, `error_type`, and `error_message` instead of a policy, and LocalStack let them through unchecked.

### Generate a policy from the stream

1. Switch to `SOFT_MODE` or `ENGINE_ONLY`, so the run completes instead of stopping at the first denial.
2. Clear the summary with `curl -s -X DELETE localhost:4566/_aws/iam/policies/summary`, then exercise the full workload once.
3. Read the result with `curl -s localhost:4566/_aws/iam/policies/summary | jq`: one entry per `resource`, with its `policy_type` and merged `policy_document`. From a saved stream instead, take the last line for each `resource`, since every line holds the merged document so far.
4. Attach each policy to its principal or resource in the IaC. Statements with a `Principal` belong in a resource policy or a role's trust policy.
5. Switch to `ENFORCED`, rerun the workload, and repeat until the stream shows no `"allowed": false` lines.

The policies cover only the requests observed, and their `Sid` values are generated. Review them for wildcards before use.

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
