# LocalStack AI Skills

AI Agent Skills for developing and testing cloud applications against [LocalStack](https://localstack.cloud) - the local cloud development platform.

## Overview

This repository contains a collection of AI skills designed to help developers work more efficiently with LocalStack. These skills enable AI assistants to help with common LocalStack workflows, from managing the local environment to deploying infrastructure and analyzing logs.

## Available Skills

| Skill | Description |
|-------|-------------|
| [localstack-lifecycle](skills/localstack-lifecycle/) | Manage LocalStack container lifecycle (start, stop, status, restart) |
| [iac-deployment](skills/iac-deployment/) | Deploy infrastructure using Terraform, CDK, CloudFormation, and Pulumi |
| [state-management](skills/state-management/) | Save, load, and manage LocalStack state with Cloud Pods |
| [logs-analysis](skills/logs-analysis/) | Analyze LocalStack logs, identify errors, and debug issues |
| [iam-policy-analyzer](skills/iam-policy-analyzer/) | Analyze IAM policies and auto-generate least-privilege permissions |
| [localstack-extensions](skills/localstack-extensions/) | Manage LocalStack extensions and plugins |

## Installation

### Via the LocalStack standalone marketplace

```bash
claude plugin marketplace add localstack/skills
claude plugin install localstack@localstack-dev
```

## Prerequisites

- [LocalStack](https://docs.localstack.cloud/getting-started/installation/) installed and configured
- [AWS CLI](https://aws.amazon.com/cli/) or [awslocal](https://docs.localstack.cloud/user-guide/integrations/aws-cli/#localstack-aws-cli-awslocal) wrapper
- Docker running on your machine

## Usage

These skills are designed to be used with AI coding assistants that support the skills/commands interface. Each skill provides contextual guidance and commands for specific LocalStack workflows.

## Related Projects

- [LocalStack](https://github.com/localstack/localstack) - The core LocalStack platform
- [LocalStack MCP Server](https://github.com/localstack/localstack-mcp-server) - Model Context Protocol server for LocalStack
- [LocalStack Documentation](https://docs.localstack.cloud/)

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.
