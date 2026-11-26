# LocalStack AI Skills

AI Agent Skills for developing and testing cloud applications against [LocalStack](https://localstack.cloud) - the local cloud development platform.

## Overview

This repository contains a collection of AI skills designed to help developers work more efficiently with LocalStack. These skills enable AI assistants to help with common LocalStack workflows, from managing the local environment to deploying infrastructure and analyzing logs.

## Available Skills

| Skill | Description |
|-------|-------------|
| [localstack-lifecycle](skills/localstack-lifecycle/) | Manage the emulator lifecycle with `lstk` (start, stop, status, restart, reset, doctor) |
| [iac-deployment](skills/iac-deployment/) | Deploy infrastructure using `lstk deploy`, Terraform, CDK, CloudFormation, SAM, and Pulumi |
| [infrastructure-testing](skills/infrastructure-testing/) | Deploy IaC, validate every resource against live state, and write integration tests |
| [state-management](skills/state-management/) | Save, load, inspect, and reset LocalStack state with snapshots and Cloud Pods |
| [logs-analysis](skills/logs-analysis/) | Analyze LocalStack logs, identify errors, and debug issues |
| [iam-policy-analyzer](skills/iam-policy-analyzer/) | Switch IAM enforcement and generate least-privilege policies from denials |
| [app-inspector](skills/app-inspector/) | Trace requests across services with App Inspector traces, spans, and IAM evaluations |
| [chaos-engineering](skills/chaos-engineering/) | Inject faults and latency to test resilience |
| [aws-replicator](skills/aws-replicator/) | Replicate resources from a real AWS account into LocalStack |
| [localstack-extensions](skills/localstack-extensions/) | Install, list, and discover LocalStack Extensions |
| [snowflake](skills/snowflake/) | Run the Snowflake emulator and execute SQL with the `snow` CLI |
| [azure](skills/azure/) | Run the Azure emulator and drive it with `lstk az` |

These skills cover the same ground as the [LocalStack MCP Server](https://github.com/localstack/localstack-mcp-server), using `lstk` and the emulator's HTTP APIs instead of MCP tools.

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
| `snow` | `pip install snowflake-cli` | The Snowflake emulator |
| `az` | [Azure CLI install](https://learn.microsoft.com/cli/azure/install-azure-cli) | The Azure emulator (`lstk az`) |
| `curl`, `jq` | your package manager | Chaos, App Inspector, Replicator, and other HTTP APIs |

## Usage

These skills are designed to be used with AI coding assistants that support the skills/commands interface. Each skill provides contextual guidance and commands for specific LocalStack workflows.

## Related Projects

- [LocalStack](https://github.com/localstack/localstack) - The core LocalStack platform
- [LocalStack MCP Server](https://github.com/localstack/localstack-mcp-server) - Model Context Protocol server for LocalStack
- [LocalStack Documentation](https://docs.localstack.cloud/)

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.
