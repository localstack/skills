---
name: localstack-iam
description: Test IAM policies and enforcement in LocalStack with lstk. Use when reproducing access denials, enabling soft or enforced IAM evaluation, validating policies, or deriving least-privilege permissions from observed requests.
---

# Test IAM policies in LocalStack

Use the AWS emulator, `lstk aws`, and verbose logs to test real policy behavior. Do not claim that logs automatically generate a complete policy; treat observed actions as evidence for a candidate least-privilege policy.

IAM enforcement and Policy Stream availability depend on the user's LocalStack plan.

## Configure enforcement

Find the active config:

```bash
lstk config path
```

For soft evaluation, reference a profile that enables enforcement without denying requests:

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

For a one-off run, set the same keys as host environment variables prefixed with `LOCALSTACK_`. `lstk start` forwards host variables carrying that prefix, so an unprefixed `ENFORCE_IAM` never reaches the emulator:

```bash
LOCALSTACK_ENFORCE_IAM=1 LOCALSTACK_IAM_SOFT_MODE=1 lstk start
```

Keys inside an `[env.*]` profile take no prefix.

Use soft mode first when discovering required permissions. Use enforced mode when testing that unauthorized calls really fail.

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
2. Inspect the policy-engine and request lines:

```bash
lstk logs --verbose --tail 500 | grep -i 'denied\|accessdenied\|iam'
```

3. Record the principal, action, resource ARN, explicit denies, and missing allows.
4. Update the smallest relevant statement.
5. Re-run the same request with the same credentials.
6. Confirm both the API result and the verbose log.

An explicit deny always wins. Check identity policies, resource policies, permission boundaries, and service-generated calls before broadening permissions.

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

1. Start with soft mode and a clean test scenario.
2. Exercise every intended application path.
3. Collect the observed actions and resource ARNs from verbose logs or the IAM Policy Stream (see [Stream recommended policies](#stream-recommended-policies)).
4. Group actions by principal and resource scope.
5. Create a candidate policy with the narrowest useful actions and resources.
6. Switch to enforced mode and run positive and negative tests.
7. Review for wildcard actions, wildcard resources, and permissions not exercised by the scenario.

The IAM Policy Stream can help summarize observed permissions when the user's plan includes it. It is available in the LocalStack Web Application and, on the command line, through the legacy `localstack` CLI.

## Stream recommended policies

`lstk` has no top-level `iam` command group — `lstk aws iam` only proxies the AWS CLI — so the CLI form of the Policy Stream comes from the legacy `localstack` CLI. Install it alongside `lstk` when request-level policy recommendations are needed:

```bash
pip install localstack
```

Both commands are plain reads against the emulator's normal endpoint, so they work against a container started by `lstk`:

```bash
# Live stream of recommended policies as requests arrive
localstack aws iam stream
localstack aws iam stream --format json

# Aggregated policies for all enforced requests
localstack aws iam summary
localstack aws iam summary --output policies.json
```

`stream` prints, per request, the principal or resource the policy should attach to, followed by the recommended policy. `summary` aggregates the same recommendations per principal or resource; `--follow` keeps it updating and clears the terminal on each refresh. If the emulator is not on the default endpoint, set `LOCALSTACK_HOST` for the legacy CLI.

1. Start the emulator in soft mode.
2. Run `localstack aws iam stream` in a second terminal.
3. Exercise the application path under test.
4. Merge the reported statements into the candidate policy.

The command group is marked preview, and both commands depend on a plan that includes the Policy Stream. These recommendations cover only the requests actually observed, so review them the same way as log-derived actions before treating the result as complete. Without the legacy CLI, derive the same evidence from `lstk logs --verbose`.
