---
name: localstack-iam
description: Test IAM policies and enforcement in LocalStack with lstk. Use when reproducing access denials, enabling or switching soft or enforced IAM evaluation, validating policies, or deriving least-privilege permissions from observed requests.
---

# Test IAM policies in LocalStack

Use the AWS emulator, `lstk aws`, and verbose logs to test real policy behavior. Do not claim that logs automatically generate a complete policy; treat observed actions as evidence for a candidate least-privilege policy.

IAM enforcement depends on the user's LocalStack plan.

## Configure enforcement

| Mode | Start-time profile keys | Runtime `state` | Behavior |
| --- | --- | --- | --- |
| Disabled (default) | none | `DISABLED` | No IAM checks |
| Soft | `ENFORCE_IAM = "1"`, `IAM_SOFT_MODE = "1"` | `SOFT_MODE` | Logs violations, allows requests |
| Enforced | `ENFORCE_IAM = "1"` | `ENFORCED` | Denies unauthorized requests |

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

# Change it: ENFORCED, SOFT_MODE, or DISABLED
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

1. Reproduce the request with the intended principal.
2. Pull the denial lines from the verbose logs. LocalStack writes a denial in one of two formats:

```text
Request for service 'sqs' by principal 'arn:aws:iam::000000000000:role/app' for operation 'SendMessage' denied.
User: arn:aws:iam::000000000000:role/app is not authorized to perform: sqs:SendMessage on resource: arn:aws:sqs:... because ...
```

```bash
lstk logs --verbose --tail 500 | grep -E "for operation '[^']*' denied\.|is not authorized to perform:"
```

Some lines also carry `Action '<service:Action>' for '<resource-arn>'`, which pins the resource for a denial.

3. Record the principal, action, resource ARN, explicit denies, and missing allows.
4. Update the smallest relevant statement.
5. Re-run the same request with the same credentials.
6. Confirm both the API result and the verbose log.

An explicit deny always wins. Check identity policies, resource policies, permission boundaries, and service-generated calls before broadening permissions.

For a single failing call, App Inspector shows the policy evaluation behind the decision in the span's `events/iam`; see the `localstack-app-inspector` skill.

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

1. Switch to `SOFT_MODE` with a clean test scenario, so the run completes instead of stopping at the first denial.
2. Exercise every intended application path once.
3. Extract each unique principal, action, and resource from the denial lines above. Normalize the action to `service:Operation`; the first format gives service and operation separately.
4. Group by principal, then write one policy per principal: one statement per resource, listing its actions. Use the exact resource ARN when the log gives one; fall back to `*` only for actions that do not support resource-level permissions, and say so.
5. Attach the policy, switch to `ENFORCED`, rerun the workload, and repeat until no denial lines remain.
6. Run negative tests that confirm unauthorized calls fail.
7. Review for wildcard actions, wildcard resources, and permissions the scenario did not exercise.

The result covers only the requests actually observed. Paths the scenario never ran stay unverified.

Save a known-good IAM setup with `lstk snapshot save` to restore it after experiments; see the `localstack-state` skill.
