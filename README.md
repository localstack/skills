# LocalStack AI Skills

AI Agent Skills for developing and testing cloud applications against [LocalStack](https://localstack.cloud) - the local cloud development platform.

## Overview

This repository contains a collection of AI skills designed to help developers work more efficiently with LocalStack. These skills enable AI assistants to help with common LocalStack workflows, from managing the local environment to deploying infrastructure and analyzing logs.

## Available Skills

| Skill | Description |
|-------|-------------|
| [localstack-lifecycle](skills/localstack-lifecycle/) | Manage the emulator lifecycle with `lstk` (start, stop, status, restart, reset) |
| [iac-deployment](skills/iac-deployment/) | Deploy infrastructure using Terraform, CDK, CloudFormation, SAM, and Pulumi |
| [state-management](skills/state-management/) | Save, load, and manage LocalStack state with snapshots and Cloud Pods |
| [logs-analysis](skills/logs-analysis/) | Analyze LocalStack logs, identify errors, and debug issues |
| [iam-policy-analyzer](skills/iam-policy-analyzer/) | Analyze IAM policies and auto-generate least-privilege permissions |
| [localstack-extensions](skills/localstack-extensions/) | Manage LocalStack extensions and plugins (legacy CLI) |

## Installation

### Via the LocalStack standalone marketplace

```bash
claude plugin marketplace add localstack/skills
claude plugin install localstack@localstack-dev
```

## Prerequisites

- Docker running on your machine
- A [LocalStack account](https://app.localstack.cloud/) and auth token
- The [`lstk` CLI](https://docs.localstack.cloud/aws/developer-tools/running-localstack/lstk/), the current LocalStack CLI:

  ```bash
  # Homebrew (macOS/Linux)
  brew install localstack/tap/lstk

  # npm
  npm install -g @localstack/lstk

  # Authenticate
  lstk login
  ```

- The tools you want `lstk` to proxy, on your `PATH`: [AWS CLI](https://aws.amazon.com/cli/), `terraform`, `cdk`, or `sam`. `lstk aws`, `lstk terraform`, `lstk cdk`, and `lstk sam` point them at LocalStack for you, replacing the `awslocal`, `tflocal`, `cdklocal`, and `samlocal` wrappers.

### Optional extra CLIs

The `lstk` CLI does not cover every workflow yet. Install these only if you need them:

| Tool | Install | Needed for |
|------|---------|-----------|
| `pulumilocal` | `pip install pulumi-local` | Pulumi deployments — `lstk` has no Pulumi proxy |
| `samlocal` | `pip install aws-sam-cli-local` | Image/container-based Lambda (ECR) deploys and nested CloudFormation stacks, which `lstk sam` does not support |
| legacy `localstack` CLI | `pip install localstack` | LocalStack Extensions, and the `localstack aws iam stream` / `summary` policy generators |

The legacy `localstack` CLI is deprecated and will be removed in a future version — use it only for the gaps listed above. It manages its own container, so stop one CLI's emulator before starting the other's.

## Usage

These skills are designed to be used with AI coding assistants that support the skills/commands interface. Each skill provides contextual guidance and commands for specific LocalStack workflows.

## Related Projects

- [LocalStack](https://github.com/localstack/localstack) - The core LocalStack platform
- [LocalStack MCP Server](https://github.com/localstack/localstack-mcp-server) - Model Context Protocol server for LocalStack
- [LocalStack Documentation](https://docs.localstack.cloud/)

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.
