---
name: localstack-deploy
description: Deploy and verify AWS infrastructure through lstk's Terraform, CDK, SAM, and AWS CLI proxies. Use when running IaC against LocalStack or replacing tflocal, cdklocal, samlocal, and awslocal workflows.
---

# Deploy infrastructure through lstk

Prefer a first-party `lstk` proxy whenever one exists. It injects the LocalStack endpoint, credentials, account, and region while preserving the standard tool's arguments and exit code.

## Prepare the AWS emulator

```bash
lstk start --type aws
lstk status
```

Install the standard CLI required by the workflow:

- Terraform or OpenTofu for `lstk terraform`
- AWS CDK 2.177.0 or newer for `lstk cdk`
- AWS SAM CLI 1.95.0 or newer for `lstk sam`
- AWS CLI for `lstk aws`

Do not install the `tflocal`, `cdklocal`, `samlocal`, or `awslocal` wrappers when `lstk` already covers the workflow.

## Terraform and OpenTofu

Run the normal Terraform lifecycle:

```bash
lstk terraform init
lstk terraform plan
lstk terraform apply
lstk terraform destroy
```

Place `lstk`-specific flags before the Terraform action:

```bash
lstk terraform --region us-west-2 plan
lstk terraform --account 000000000123 apply
```

Use OpenTofu without changing the skill workflow:

```bash
LSTK_TF_CMD=tofu lstk terraform plan
```

`lstk` creates a provider override automatically. Do not add hard-coded LocalStack endpoints to the user's Terraform files unless they explicitly need a portable manual configuration.

## AWS CDK

```bash
lstk cdk bootstrap
lstk cdk synth
lstk cdk deploy
lstk cdk destroy
```

Place the region flag before the action:

```bash
lstk cdk --region us-west-2 deploy
```

CDK always uses LocalStack account `000000000000`; do not invent an `--account` workflow.

## AWS SAM

```bash
lstk sam build
lstk sam validate
lstk sam deploy --guided
```

Place LocalStack flags before the SAM action:

```bash
lstk sam --region us-west-2 deploy
```

For image/container-based Lambda deployments or nested CloudFormation stacks, check the current `lstk sam` limitations before proceeding; those workflows may still require `samlocal`.

## CloudFormation through the AWS CLI

```bash
lstk aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://template.yaml

lstk aws cloudformation describe-stacks \
  --stack-name my-stack

lstk aws cloudformation update-stack \
  --stack-name my-stack \
  --template-body file://template.yaml

lstk aws cloudformation delete-stack \
  --stack-name my-stack
```

## Pulumi boundary

`lstk` does not currently provide a Pulumi proxy. Never invent `lstk pulumi`. If the user explicitly needs Pulumi, follow the current LocalStack Pulumi integration or use `pulumilocal`, clearly labeling it as an external fallback.

## Target an external emulator

Put the global endpoint before the proxy command:

```bash
lstk --endpoint-url https://example.localstack.cloud terraform plan
lstk --endpoint-url https://example.localstack.cloud cdk deploy
lstk --endpoint-url https://example.localstack.cloud sam deploy
```

The endpoint must identify an AWS emulator for these proxies.

## Verify the deployment

Do not stop at a successful IaC exit code. Query the resources that matter:

```bash
lstk status
lstk aws cloudformation describe-stacks
lstk aws s3 ls
lstk aws lambda list-functions
```

Before `apply`, `deploy`, `destroy`, or delete operations, surface the expected changes and obtain any approval the user requires.
