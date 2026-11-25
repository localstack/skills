# LocalStack Agent Skills

Portable [Agent Skills](https://agentskills.io/) for developing and testing cloud applications with [LocalStack](https://localstack.cloud) through the [`lstk`](https://github.com/localstack/lstk) CLI.

This repository is a skills-only [Agent Plugin](https://agent-plugins.org/) targeting the Agent Plugins v1.0.0 specification. It intentionally does not include `mcp.json`; LocalStack MCP integration is separate follow-up work.

## Available skills

| Skill | Description |
| --- | --- |
| [localstack](skills/localstack/) | Start, stop, configure, and troubleshoot LocalStack emulators with `lstk`, including `lstk doctor` |
| [localstack-deploy](skills/localstack-deploy/) | Deploy and verify infrastructure with `lstk deploy` and the `lstk` Terraform, CDK, SAM, and AWS CLI proxies |
| [localstack-infra-test](skills/localstack-infra-test/) | Deploy IaC, validate every resource against live state, and write integration tests |
| [localstack-state](skills/localstack-state/) | Save, load, inspect, and reset LocalStack snapshots and persistent state |
| [localstack-logs](skills/localstack-logs/) | Inspect emulator logs and diagnose AWS API or Lambda failures |
| [localstack-iam](skills/localstack-iam/) | Switch IAM enforcement and derive least-privilege policies from observed denials |
| [localstack-app-inspector](skills/localstack-app-inspector/) | Trace requests across services with App Inspector traces, spans, and IAM evaluations |
| [localstack-chaos](skills/localstack-chaos/) | Inject faults and latency to test resilience |
| [localstack-replicator](skills/localstack-replicator/) | Replicate resources from a real AWS account into LocalStack |
| [localstack-snowflake](skills/localstack-snowflake/) | Run the Snowflake emulator and execute SQL against it |
| [localstack-azure](skills/localstack-azure/) | Run the Azure emulator and drive it with `lstk az` |
| [localstack-extensions](skills/localstack-extensions/) | Install, discover, and develop in-emulator LocalStack Extensions |
| [lstk-extensions](skills/lstk-extensions/) | Use and author Git-style `lstk-<name>` CLI extensions |

## Use as an Agent Plugin

Clone the repository and point a compatible client's local-plugin workflow at the repository root:

```bash
git clone https://github.com/localstack/skills.git
```

The client discovers the root `plugin.json` and each immediate child of `skills/`. Agent Plugins v1 standardizes the package, but intentionally leaves installation and distribution commands to each client. See the [compatible clients](https://agent-plugins.org/compatible-clients) page for client-specific instructions.

This step only prepares a locally loadable skills package. Marketplace publication and bundled MCP configuration are deliberately out of scope.

## Install individual Agent Skills

Clients supported by the Agent Skills CLI can install the collection or select individual skills:

```bash
npx skills add https://github.com/localstack/skills
npx skills add https://github.com/localstack/skills --skill localstack-deploy
```

## Install with Claude Code

The existing Claude marketplace compatibility layer remains available:

```bash
claude plugin marketplace add localstack/skills
claude plugin install localstack@localstack-dev
```

## Prerequisites

- [`lstk`](https://github.com/localstack/lstk#installation)
- A Docker-API-compatible container runtime supported by `lstk`
- A LocalStack account and `LOCALSTACK_AUTH_TOKEN` for workflows that require authentication
- The standard AWS, Terraform, CDK, or SAM CLI when using the corresponding proxy skill

### Optional extra CLIs

`lstk` does not cover every workflow yet. Install these only for the gaps they close:

| Tool | Install | Needed for |
| --- | --- | --- |
| `pulumilocal` | `pip install pulumi-local` | Pulumi deployments; `lstk` has no Pulumi proxy |
| `samlocal` | `pip install aws-sam-cli-local` | Image and container-based Lambda (ECR) deploys and nested CloudFormation stacks, which `lstk sam` does not support |
| `snow` | `pip install snowflake-cli` | The Snowflake emulator |
| `az` | [Azure CLI install](https://learn.microsoft.com/cli/azure/install-azure-cli) | The Azure emulator through `lstk az` |
| `curl`, `jq` | Your package manager | The Chaos, App Inspector, Replicator, IAM, and state HTTP APIs |

## Validate locally

Validation requires [`uv`](https://docs.astral.sh/uv/), Git, and network access to PyPI, GitHub, and `agent-plugins.org`. The script validates `plugin.json` against the canonical Agent Plugins schema and validates every skill with a pinned revision of the official `skills-ref` implementation:

```bash
./scripts/validate.sh
```

If Claude Code is installed, also validate the compatibility package:

```bash
claude plugin validate --strict .
```

## Package layout

```text
.
├── plugin.json
├── skills/
│   └── <skill-name>/
│       └── SKILL.md
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
└── scripts/
    └── validate.sh
```

## Related projects

- [lstk](https://github.com/localstack/lstk)
- [LocalStack MCP Server](https://github.com/localstack/localstack-mcp-server)
- [LocalStack documentation](https://docs.localstack.cloud/)

## License

Apache License 2.0 — see [LICENSE](LICENSE).
