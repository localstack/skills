---
name: localstack
description: Manage LocalStack emulators with the lstk v2 CLI. Use when starting, stopping, restarting, configuring, checking, or troubleshooting a LocalStack AWS, Azure, or Snowflake emulator.
---

# Manage a LocalStack emulator

Use `lstk` for emulator lifecycle and configuration. Prefer it over the legacy `localstack` CLI and direct container-runtime commands because `lstk` resolves the configured emulator, runtime, ports, authentication, and output mode.

## Check prerequisites

Verify the CLI and container runtime before changing state:

```bash
lstk --version
lstk status
```

If `lstk` is missing, install it from the [lstk repository](https://github.com/localstack/lstk#installation). Do not put authentication tokens in committed files; use `LOCALSTACK_AUTH_TOKEN` or the browser login flow.

## Start an emulator

Start interactively and let the first-run flow select an emulator:

```bash
lstk
```

Start explicitly:

```bash
lstk start
lstk start --type aws
lstk start --type azure
lstk start --type snowflake
```

`--type` updates the selected type in the active configuration; it is not a temporary override. For automation, select the type and disable prompts:

```bash
LOCALSTACK_AUTH_TOKEN=<token> lstk --non-interactive start --type aws
```

Enable persistent emulator state for this start:

```bash
lstk start --persist
```

Use `--timeout <duration>` when automation needs a different readiness deadline:

```bash
lstk --non-interactive start --timeout 90s
```

## Inspect and control the emulator

```bash
lstk status
lstk logs --tail 100
lstk logs --follow
lstk restart
lstk stop
```

Use `lstk restart --persist` when persistence must remain enabled after the restart.

## Configure emulator environment

Find the active configuration file:

```bash
lstk config path
```

Add named environment profiles to that TOML file and reference them from the active `[[containers]]` block:

```toml
[[containers]]
type = "aws"
tag = "latest"
port = "4566"
env = ["debug"]

[env.debug]
DEBUG = "1"
LS_LOG = "trace"
```

Preserve unrelated settings and keep only one enabled `[[containers]]` block. Restart the emulator after changing its environment.

## Target an external emulator

Commands with a remote equivalent accept a global endpoint:

```bash
lstk --endpoint-url https://example.localstack.cloud status
lstk --endpoint-url https://example.localstack.cloud aws s3 ls
```

Do not use `--endpoint-url` with `start`, `stop`, `restart`, `logs`, or `volume`; those operations require an emulator managed by the local runtime.

## Troubleshoot startup

1. Run `lstk status`.
2. Inspect `lstk logs --tail 200`, adding `--verbose` when request/provider lines matter.
3. Confirm the configured host port is available.
4. Confirm the detected container runtime is running.
5. Run `lstk config path` and inspect the active emulator type, image, port, environment profiles, and mounts.
6. For authentication failures, run `lstk login` or provide a valid `LOCALSTACK_AUTH_TOKEN`.

Use direct container-runtime commands only as a last-resort diagnostic, not as the normal lifecycle workflow.
