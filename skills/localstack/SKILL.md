---
name: localstack
description: Manage LocalStack emulators with the lstk v2 CLI. Use when starting, stopping, restarting, configuring, checking, or troubleshooting a LocalStack AWS, Azure, or Snowflake emulator.
---

# Manage a LocalStack emulator

Use `lstk` for emulator lifecycle and configuration. Prefer it over the legacy `localstack` CLI and direct container-runtime commands because `lstk` resolves the configured emulator, runtime, ports, authentication, and output mode.

## Check prerequisites

`lstk` pulls a licensed LocalStack image (`localstack/localstack-pro` for the AWS emulator), so it needs a running container runtime and a LocalStack account whose license covers the selected emulator type.

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

`lstk start` runs the emulator in the background and returns once it is ready. There is no `-d` flag; the legacy `localstack start -d` form does not carry over.

## Inspect and control the emulator

```bash
lstk status
lstk logs --tail 100
lstk logs --follow
lstk restart
lstk stop
```

`lstk status` reports emulator state and also lists the resources deployed in it, so it answers whether a resource exists without grepping logs.

Use `lstk restart --persist` when persistence must remain enabled after the restart.

## Configure emulator environment

Host environment variables reach the emulator only when prefixed with `LOCALSTACK_`:

```bash
LOCALSTACK_DEBUG=1 lstk start
LOCALSTACK_SERVICES=s3,sqs lstk start
LOCALSTACK_EAGER_SERVICE_LOADING=1 lstk start
```

Any config variable the legacy `localstack` CLI accepted bare must carry the prefix on the host. Keys inside an `[env.*]` profile take no prefix.

Find the active configuration file:

```bash
lstk config path
```

`lstk` reads `./.lstk/config.toml` when the current directory has one, and `$HOME/.config/lstk/config.toml` otherwise; the lookup does not walk up parent directories. A committed `.lstk/config.toml` pins the emulator type, port, and environment profiles for commands run from the repository root.

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

Set `tag` in that block to pin the emulator version instead of tracking `latest` when a run must be reproducible, for example `tag = "2026.4"`. Set `image` to pull the emulator from an internal registry mirror; if `image` carries no tag, `tag` is appended to it.

## Target an external emulator

Commands with a remote equivalent accept a global endpoint:

```bash
lstk --endpoint-url https://example.localstack.cloud status
lstk --endpoint-url https://example.localstack.cloud aws s3 ls
```

Do not use `--endpoint-url` with `start`, `stop`, `restart`, `logs`, or `volume`; those operations require an emulator managed by the local runtime.

## Fall back to the legacy CLI

A few capabilities have no `lstk` equivalent. Never invent `lstk extensions`, `lstk dns`, or `lstk ephemeral`. Install the legacy CLI (`pip install localstack`) alongside `lstk` only for:

- `localstack extensions`, which manages in-emulator LocalStack Extensions; see the `localstack-extensions` skill. Git-style `lstk-<name>` CLI extensions are a separate mechanism, covered by the `lstk-extensions` skill.
- `localstack aws iam stream` and `localstack aws iam summary`; see the `localstack-iam` skill.
- `localstack dns` for host DNS configuration and `localstack ephemeral` for ephemeral cloud instances.

Use `lstk` for everything it already covers.

## Troubleshoot startup

1. Run `lstk status`.
2. Inspect `lstk logs --tail 200`, adding `--verbose` when request/provider lines matter.
3. Confirm the configured host port is available.
4. Confirm the detected container runtime is running.
5. Run `lstk config path` and inspect the active emulator type, image, port, environment profiles, and mounts.
6. For authentication failures, run `lstk login` or provide a valid `LOCALSTACK_AUTH_TOKEN`.
7. Read `lstk.log`, which `lstk` writes next to the configuration file; `lstk config path` locates the directory. It records CLI-side events such as license and token resolution that never reach `lstk logs`.

The checklist above misses two cases:

- The emulator gateway listens on `:4566,:443` by default, so startup can fail on port 443 while the configured port is free. Set `GATEWAY_LISTEN = ":4566"` in an environment profile to bind only 4566.
- `lstk` probes the default container-runtime socket, not the one a `docker` context may be using. Set `DOCKER_HOST` when the runtime listens elsewhere.

Use direct container-runtime commands only as a last-resort diagnostic, not as the normal lifecycle workflow.
