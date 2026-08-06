# LocalStack Agent Skills

Portable [Agent Skills](https://agentskills.io/) for developing and testing cloud applications with [LocalStack](https://localstack.cloud) through the [`lstk`](https://github.com/localstack/lstk) CLI.

This repository is a skills-only [Agent Plugin](https://agent-plugins.org/) targeting the Agent Plugins v1.0.0 specification. It intentionally does not include `mcp.json`; LocalStack MCP integration is separate follow-up work.

## Available skills

| Skill | Description |
| --- | --- |
| [localstack](skills/localstack/) | Start, stop, configure, and troubleshoot LocalStack emulators with `lstk` |
| [localstack-deploy](skills/localstack-deploy/) | Deploy and verify infrastructure through the `lstk` Terraform, CDK, SAM, and AWS CLI proxies |
| [localstack-state](skills/localstack-state/) | Save, load, inspect, and manage LocalStack snapshots and persistent state |
| [localstack-logs](skills/localstack-logs/) | Inspect emulator logs and diagnose AWS API or Lambda failures |
| [localstack-iam](skills/localstack-iam/) | Test IAM enforcement and derive least-privilege policies from observed behavior |
| [localstack-extensions](skills/localstack-extensions/) | Use and author Git-style `lstk-<name>` CLI extensions |

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
