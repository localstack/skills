---
name: localstack-deploy
description: Deploy infrastructure to LocalStack using IaC tools. Use when users want to deploy Terraform, CDK, CloudFormation, SAM, or Pulumi to LocalStack, or need help with the lstk proxy commands (lstk terraform, lstk cdk, lstk sam, lstk aws) or the pulumilocal wrapper.
---

# Infrastructure as Code Deployment

Deploy AWS infrastructure to LocalStack using popular IaC tools including Terraform, AWS CDK, CloudFormation, SAM, and Pulumi.

## Capabilities

- Deploy Terraform configurations to LocalStack
- Run AWS CDK deployments locally
- Deploy CloudFormation stacks
- Build and deploy AWS SAM applications
- Execute Pulumi programs against LocalStack
- Validate infrastructure before deployment

## Prerequisites

- The `lstk` CLI installed and the emulator running (`lstk start`) — see the `localstack` skill
- The underlying tool on your `PATH`: `terraform`, `cdk`, `sam`, or `aws`. `lstk` proxies them; it does not bundle them.

`lstk` replaces the old `awslocal` / `tflocal` / `cdklocal` / `samlocal` wrappers — you no longer need to `pip install`/`npm install` them. Pulumi is the exception; see [Pulumi](#pulumi).

## Terraform

### Using `lstk terraform` (Preferred)

`lstk terraform` (alias `lstk tf`) runs Terraform against LocalStack by generating a provider-override file, so your `.tf` files need no LocalStack-specific changes.

```bash
lstk terraform init
lstk terraform plan
lstk terraform apply -auto-approve
lstk terraform destroy -auto-approve

# Short alias
lstk tf apply -auto-approve
```

`lstk`-specific flags go **before** the Terraform subcommand:

```bash
lstk terraform --region us-west-2 plan
lstk terraform --account 000000000000 apply
```

| Flag | Default | Notes |
|------|---------|-------|
| `--region <region>` | `us-east-1` | Falls back to `AWS_REGION` |
| `--account <id>` | `test` | 12 digits; falls back to `AWS_ACCESS_KEY_ID` |

Useful environment variables: `AWS_ENDPOINT_URL`, `LSTK_TF_CMD` (binary name, default `terraform`), `LSTK_TF_OVERRIDE_FILE_NAME` (default `localstack_providers_override.tf`), `LSTK_TF_DRY_RUN`.

`lstk terraform` targets the AWS emulator only.

### Manual Provider Configuration (Fallback)

Only use manual provider configuration if `lstk` cannot be used (for example, a CI image that only has `terraform`). This approach requires modifying your Terraform files:

```hcl
# In your provider configuration:
provider "aws" {
  access_key                  = "test"
  secret_key                  = "test"
  region                      = "us-east-1"

  endpoints {
    s3       = "http://localhost:4566"
    dynamodb = "http://localhost:4566"
    lambda   = "http://localhost:4566"
    # Add other services as needed
  }

  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
}
```

Note: When using manual configuration, you must list endpoints for each AWS service used in your configuration.

## AWS CDK

Requires AWS CDK CLI `2.177.0` or newer.

```bash
# Bootstrap (first time only)
lstk cdk bootstrap

# Deploy all stacks
lstk cdk deploy --all --require-approval never

# Deploy a specific stack
lstk cdk deploy MyStack

# Synthesize
lstk cdk synth

# Destroy
lstk cdk destroy --all --force
```

`lstk cdk` accepts `--region <region>` (default `us-east-1`) before the CDK command. There is no `--account` flag — CDK always targets the default account `000000000000`.

Useful environment variables: `AWS_ENDPOINT_URL`, `AWS_ENDPOINT_URL_S3`, `LSTK_CDK_CMD` (default `cdk`), `AWS_REGION`.

## CloudFormation

Use `lstk aws`, which proxies the host `aws` CLI with the endpoint, credentials, and region pre-configured.

```bash
# Create stack
lstk aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://template.yaml

# Update stack
lstk aws cloudformation update-stack \
  --stack-name my-stack \
  --template-body file://template.yaml

# Delete stack
lstk aws cloudformation delete-stack --stack-name my-stack

# Describe stack
lstk aws cloudformation describe-stacks --stack-name my-stack
```

If you would rather use the plain `aws` CLI, run `lstk setup aws` once to write a `localstack` profile into `~/.aws/config` and `~/.aws/credentials`, then use `aws --profile localstack ...`.

## AWS SAM

Requires AWS SAM CLI `1.95.0` or newer.

```bash
lstk sam build
lstk sam validate
lstk sam deploy
lstk sam --region us-west-2 deploy
```

`lstk sam` accepts `--region <region>` (default `us-east-1`) and `--account <id>` (default `000000000000`) before the SAM command.

**Limitation:** image/container-based Lambda (ECR) deploys and nested CloudFormation stacks are not supported by `lstk sam`. For those workflows, install the `samlocal` wrapper (`pip install aws-sam-cli-local`) and use it instead.

## Pulumi

`lstk` has no Pulumi proxy command, so Pulumi still needs the `pulumilocal` wrapper.

### Using `pulumilocal` (Preferred)

```bash
# Requires Python/pip — this is an extra install beyond lstk
pip install pulumi-local

# Use pulumilocal instead of pulumi - no config changes needed
pulumilocal preview
pulumilocal up --yes
pulumilocal destroy --yes
```

### Manual Configuration (Fallback)

Only use manual configuration if `pulumilocal` cannot be installed (e.g., Python/pip is not available in the environment):

```bash
# Configure Pulumi for LocalStack
pulumi config set aws:accessKey test
pulumi config set aws:secretKey test
pulumi config set aws:region us-east-1
pulumi config set aws:endpoints '[{"s3":"http://localhost:4566"}]'
```

```bash
# Deploy with standard pulumi commands
pulumi preview
pulumi up --yes
pulumi destroy --yes
```

## Endpoint Resolution

`lstk aws`, `lstk terraform`, `lstk cdk`, and `lstk sam` probe whether `localhost.localstack.cloud` resolves to `127.0.0.1` and use it when it does; otherwise they fall back to `127.0.0.1:4566`. Override with the `LOCALSTACK_HOST` environment variable.

## Best Practices

- Use the `lstk` proxy commands (`lstk terraform`, `lstk cdk`, `lstk sam`, `lstk aws`) rather than editing endpoints into your IaC files
- Test infrastructure changes locally before deploying to AWS
- Use `lstk start --persist` to retain state across LocalStack restarts
- Snapshot deployed infrastructure with `lstk save` so you can restore it instantly instead of re-deploying — see the `localstack-state` skill
- In CI, add `--non-interactive` to `lstk` commands and set `LOCALSTACK_AUTH_TOKEN`
