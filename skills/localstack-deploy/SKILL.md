---
name: localstack-deploy
description: Deploy and verify AWS infrastructure through lstk's Terraform, CDK, SAM, and AWS CLI proxies, including CloudFormation stacks and the Pulumi gap that still needs pulumilocal. Use when running IaC or CloudFormation against LocalStack, checking which resources LocalStack supports before a deploy, using lstk deploy, deploying Pulumi to LocalStack, or replacing tflocal, cdklocal, samlocal, and awslocal workflows.
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

## Check support before deploying

`lstk deploy detect` scans a workspace without deploying. It reports which IaC tool the project uses and which resources LocalStack, or the user's license, does not support. Run it first on an unfamiliar project:

```bash
lstk deploy detect --dir ./infra
lstk deploy detect --dir ./infra --unsupported   # list every unsupported resource
lstk deploy detect --dir ./infra --explain       # show the evidence behind the decision
```

## Deploy with one command

`lstk deploy` detects Terraform, CDK, or SAM/CloudFormation and runs the matching `lstk` proxy:

```bash
lstk deploy
lstk deploy --dir ./infra
lstk deploy --dir ./infra --tool tf      # force the tool: terraform (tf), cdk, or sam
lstk deploy --template template.yaml     # SAM/CloudFormation template; implies --tool sam
```

Use the per-tool commands below when the workflow needs tool-specific flags such as variables, stack names, or destroy.

## Terraform and OpenTofu

Run the normal Terraform lifecycle:

```bash
lstk terraform init
lstk terraform plan
lstk terraform apply
lstk terraform destroy
```

Pass variables with `-var`, and read outputs as JSON for follow-up probes:

```bash
lstk terraform apply -auto-approve -var env=dev -var bucket_name=my-bucket
lstk terraform output -json
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

`--region` defaults to `us-east-1` and falls back to `AWS_REGION`. `--account` takes a 12-digit id, defaults to `test`, and falls back to `AWS_ACCESS_KEY_ID`.

The Terraform proxy also reads:

- `LSTK_TF_CMD` — Terraform binary to invoke, default `terraform`
- `LSTK_TF_OVERRIDE_FILE_NAME` — generated override file name, default `localstack_providers_override.tf`
- `LSTK_TF_DRY_RUN` — write the override file without running Terraform

`lstk tf` is an alias for `lstk terraform`. Prefer the explicit form in documentation and automation.

`lstk` creates a provider override automatically. Do not add hard-coded LocalStack endpoints to the user's Terraform files unless they explicitly need a portable manual configuration.

## AWS CDK

```bash
lstk cdk bootstrap
lstk cdk synth
lstk cdk deploy
lstk cdk destroy
```

Deploy without prompts in automation, and pass context values with `-c`:

```bash
lstk cdk deploy --all --require-approval never -c env=dev
lstk cdk destroy --all --force
```

Place the region flag before the action:

```bash
lstk cdk --region us-west-2 deploy
```

CDK always uses LocalStack account `000000000000`; do not invent an `--account` workflow.

Override the CDK binary with `LSTK_CDK_CMD`, default `cdk`.

## AWS SAM

```bash
lstk sam build
lstk sam validate
lstk sam deploy --guided
```

`--guided` prompts. For agents and CI, skip the changeset prompt and let SAM create its artifact bucket:

```bash
lstk sam build --cached
lstk sam deploy --stack-name my-app \
  --no-confirm-changeset --no-fail-on-empty-changeset \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --resolve-s3

lstk sam delete --stack-name my-app --no-prompts
```

Place LocalStack flags before the SAM action:

```bash
lstk sam --region us-west-2 deploy
```

Unlike `lstk cdk`, `lstk sam` does accept `--account <id>` for a 12-digit account id, default `000000000000`. Override the SAM binary with `LSTK_SAM_CMD`, default `sam`.

`lstk sam` does not support image/container-based Lambda (ECR) deploys or nested CloudFormation stacks. Use the external `samlocal` wrapper for those workflows:

```bash
pip install aws-sam-cli-local
```

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

`create-stack` and `delete-stack` return before the work finishes. Wait for the terminal state, and read the failed events when it does not succeed:

```bash
lstk aws cloudformation wait stack-create-complete --stack-name my-stack
lstk aws cloudformation wait stack-delete-complete --stack-name my-stack
lstk aws cloudformation describe-stack-events --stack-name my-stack \
  --query 'StackEvents[?contains(ResourceStatus, `FAILED`)]'
```

## Configure a profile for unwrapped tools

SDKs, test harnesses, and scripts that cannot be invoked through `lstk aws` need a profile instead:

```bash
lstk setup aws
```

This writes a `localstack` profile to `~/.aws/config` and `~/.aws/credentials` for use with `aws --profile localstack ...` or `AWS_PROFILE=localstack`. Add `--force` to overwrite an existing `localstack` profile without a prompt.

## Pulumi boundary

`lstk` does not currently provide a Pulumi proxy. Never invent `lstk pulumi`. Pulumi still needs the external `pulumilocal` wrapper, which requires Python and pip:

```bash
pip install pulumi-local

pulumilocal preview
pulumilocal up --yes
pulumilocal destroy --yes
```

`pulumilocal` rewrites the AWS endpoints itself, so the Pulumi program needs no LocalStack-specific configuration. Label it as an external fallback, not part of `lstk`.

## Target an external emulator

Put the global endpoint before the proxy command:

```bash
lstk --endpoint-url https://example.localstack.cloud terraform plan
lstk --endpoint-url https://example.localstack.cloud cdk deploy
lstk --endpoint-url https://example.localstack.cloud sam deploy
```

The endpoint must identify an AWS emulator for these proxies.

Automation that cannot place a flag before every command can set the same target with `LSTK_ENDPOINT_URL`, or with `AWS_ENDPOINT_URL`, which has lower precedence when both are set.

Without an explicit endpoint, the proxies use `localhost.localstack.cloud` when it resolves to `127.0.0.1` and fall back to `127.0.0.1:4566` otherwise. Set `LOCALSTACK_HOST` to override the host.

`lstk cdk` and `lstk sam` also read `AWS_ENDPOINT_URL_S3`, which overrides the S3 endpoint alone. Set it alongside the endpoint variable on a host where `localhost.localstack.cloud` does not resolve: `lstk cdk` warns and falls back to `127.0.0.1` there, and CDK S3 asset operations such as `bootstrap` and asset deploys can fail without a virtual-host-capable address.

## Verify the deployment

Do not stop at a successful IaC exit code. Query the resources that matter:

```bash
lstk status
lstk aws cloudformation describe-stacks
lstk aws s3 ls
lstk aws lambda list-functions
```

When a deploy fails, pull the real error from the emulator logs; see the `localstack-logs` skill. To validate every declared resource and generate integration tests, see the `localstack-infra-test` skill. Save a deployed baseline with `lstk snapshot save` to restore it instead of redeploying; see the `localstack-state` skill.

Before `apply`, `deploy`, `destroy`, or delete operations, surface the expected changes and obtain any approval the user requires.
