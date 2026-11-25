---
name: localstack-iam
description: Test IAM policies and enforcement in LocalStack with lstk. Use when reproducing or fixing access denials, streaming IAM violations, enabling or switching soft or enforced IAM evaluation, validating policies, or deriving least-privilege permissions from observed requests.
---

# Test IAM policies in LocalStack

Use the AWS emulator, `lstk aws`, App Inspector, and the IAM Policy Stream to test real policy behavior. Treat derived policies as evidence for a candidate least-privilege policy, not a verified one.

IAM enforcement, App Inspector IAM events, and the Policy Stream depend on the user's LocalStack plan.

## Configure enforcement

| Mode | Start-time profile keys | Runtime `state` | Behavior |
| --- | --- | --- | --- |
| Disabled (default) | none | `DISABLED` | No IAM checks |
| Soft | `ENFORCE_IAM = "1"`, `IAM_SOFT_MODE = "1"` | `SOFT_MODE` | Logs violations, allows requests |
| Enforced | `ENFORCE_IAM = "1"` | `ENFORCED` | Denies unauthorized requests |
| Engine only | none; set at runtime | `ENGINE_ONLY` | Evaluates policies and records denials, but neither blocks nor logs them |

Enabling App Inspector moves the mode from `DISABLED` to `ENGINE_ONLY`, so denials are recorded without enforcement. Never switch to `ENFORCED` just to see denials; it can break a workload that works.

Set the starting mode in a profile in the file that `lstk config path` reports. For soft evaluation:

```toml
[[containers]]
type = "aws"
env = ["iam-soft"]

[env.iam-soft]
DEBUG = "1"
ENFORCE_IAM = "1"
IAM_SOFT_MODE = "1"
```

For enforced mode:

```toml
[[containers]]
type = "aws"
env = ["iam-enforced"]

[env.iam-enforced]
DEBUG = "1"
ENFORCE_IAM = "1"
```

Restart after changing the profile:

```bash
lstk restart
```

Keys inside an `[env.*]` profile take no `LOCALSTACK_` prefix.

Use soft mode first when discovering required permissions. Use enforced mode when testing that unauthorized calls really fail.

### Switch modes without restarting

The IAM config endpoint reads and changes the mode on a running emulator, so enforcement can flip between test runs without a restart:

```bash
# Current mode
curl -s localhost:4566/_aws/iam/config | jq .state

# Change it: ENFORCED, SOFT_MODE, ENGINE_ONLY, or DISABLED
curl -s -X POST localhost:4566/_aws/iam/config \
  -H 'Content-Type: application/json' -d '{"state":"SOFT_MODE"}'
```

The runtime change lasts until the emulator restarts; the profile sets the default.

## Create principals and policies

```bash
lstk aws iam create-user --user-name dev-user

lstk aws iam create-policy \
  --policy-name app-policy \
  --policy-document file://policy.json

lstk aws iam attach-user-policy \
  --user-name dev-user \
  --policy-arn arn:aws:iam::000000000000:policy/app-policy

lstk aws iam create-access-key --user-name dev-user
```

Capture the returned access key and secret without committing them. `lstk aws` respects explicit AWS credential environment variables, so use the created principal for the request under test:

```bash
AWS_ACCESS_KEY_ID=<created-key> \
AWS_SECRET_ACCESS_KEY=<created-secret> \
lstk aws s3 ls
```

## Investigate a denial

Start with App Inspector for any permission error. LocalStack records each denied request with the policies that decided it, including another account's policies that you cannot read, and a suggested fix. See the "Explain IAM denials" section of the `localstack-app-inspector` skill.

Use the Policy Stream below for what App Inspector does not record, such as requests to STS and IAM (for example a trust policy failing `sts:AssumeRole`), and when the license or image has no App Inspector IAM events.

An explicit deny always wins. Check identity policies, resource policies, permission boundaries, and service-generated calls before broadening permissions.

## Detect violations with the Policy Stream

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

## Validate and simulate policies

```bash
lstk aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::000000000000:user/dev-user \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/file.txt

lstk aws accessanalyzer validate-policy \
  --policy-document file://policy.json \
  --policy-type IDENTITY_POLICY
```

Treat simulator and validator results as additional evidence; still run the application request against enforced mode.

## Derive least privilege

1. Switch to `SOFT_MODE` or `ENGINE_ONLY`, so the run completes instead of stopping at the first denial.
2. Clear the summary with `curl -s -X DELETE localhost:4566/_aws/iam/policies/summary`, then exercise every intended application path once.
3. Read the result with `curl -s localhost:4566/_aws/iam/policies/summary | jq`: one entry per `resource`, with its `policy_type` and merged `policy_document`. From a saved stream instead, take the last line for each `resource`, since every line holds the merged document so far.
4. Attach each policy to its principal or resource in the IaC. Statements with a `Principal` belong in a resource policy or a role's trust policy.
5. Switch to `ENFORCED`, rerun the workload, and repeat until the stream shows no `"allowed": false` lines.
6. Run negative tests that confirm unauthorized calls fail.

The policies cover only the requests observed, and their `Sid` values are generated. Review them for wildcard actions, wildcard resources, and permissions the scenario did not exercise.

Save a known-good IAM setup with `lstk snapshot save` to restore it after experiments; see the `localstack-state` skill.
