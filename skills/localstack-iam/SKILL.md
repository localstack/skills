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
3. Collect the observed actions and resource ARNs from verbose logs or the LocalStack IAM Policy Stream.
4. Group actions by principal and resource scope.
5. Create a candidate policy with the narrowest useful actions and resources.
6. Switch to enforced mode and run positive and negative tests.
7. Review for wildcard actions, wildcard resources, and permissions not exercised by the scenario.

The IAM Policy Stream in the LocalStack Web Application can help summarize observed permissions when the user's plan includes it.
