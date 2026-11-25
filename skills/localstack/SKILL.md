---
name: localstack
description: Manage LocalStack emulators with the lstk v2 CLI. Use when starting, stopping, restarting, configuring, checking, or troubleshooting a LocalStack AWS, Azure, or Snowflake emulator, or diagnosing a machine where LocalStack will not start.
---

# Manage a LocalStack emulator

Use `lstk` for emulator lifecycle and configuration. Prefer it over direct container-runtime commands because `lstk` resolves the configured emulator, runtime, ports, authentication, and output mode.

## Check prerequisites

`lstk` pulls a licensed LocalStack image (`localstack/localstack-pro` for the AWS emulator), so it needs a running container runtime and a LocalStack account whose license covers the selected emulator type.

Verify the CLI and container runtime before changing state:

```bash
lstk --version
lstk status
```

If `lstk` is missing, install it:

```bash
brew install localstack/tap/lstk   # macOS and Linux
npm install -g @localstack/lstk
```

See the [lstk repository](https://github.com/localstack/lstk#installation) for other methods.

## Authenticate

```bash
lstk login    # browser login; stores the token in the system keyring
lstk logout
```

`lstk` resolves the token from `LOCALSTACK_AUTH_TOKEN` first, then the keyring, then the browser login. The environment variable wins, so `LOCALSTACK_AUTH_TOKEN=<token> lstk start` switches accounts for one run without logging out. In CI and other non-TTY environments, set `LOCALSTACK_AUTH_TOKEN` to a CI Auth Token; a personal Developer Auth Token does not work there.

Do not put authentication tokens in committed files.

## Start an emulator

Start interactively and let the first-run flow select an emulator:

```bash
lstk
```

Start explicitly:

```bash
lstk start
lstk start --type aws
lstk start --type azure        # see the localstack-azure skill
lstk start --type snowflake    # see the localstack-snowflake skill
```

`--type` updates the selected type in the active configuration; it is not a temporary override. For automation, select the type and disable prompts:

```bash
LOCALSTACK_AUTH_TOKEN=<token> lstk --non-interactive start --type aws
```

Enable persistent emulator state for this start:

```bash
lstk start --persist
```

Run a different image for this start only, without saving it to config:

```bash
lstk start --image localstack/localstack-pro:2026.4
```

Use `--timeout <duration>` when automation needs a different readiness deadline:

```bash
lstk --non-interactive start --timeout 90s
```

`lstk start` runs the emulator in the background and returns once it is ready. There is no `-d` flag.

## Inspect and control the emulator

```bash
lstk status
lstk logs --tail 100
lstk logs --follow
lstk restart
lstk stop
```

`lstk status` reports emulator state and also lists the resources deployed in it, so it answers whether a resource exists without grepping logs. Scripts and agents should read the JSON form:

```bash
lstk --json status
lstk --json status --no-resources
```

Use `lstk restart --persist` when persistence must remain enabled after the restart. For `lstk reset` and `lstk volume clear`, see the `localstack-state` skill.

The gateway exposes the same information over HTTP:

```bash
curl -s localhost:4566/_localstack/health | jq        # per-service state
curl -s localhost:4566/_localstack/info | jq          # version, session, uptime
curl -s localhost:4566/_localstack/licenseinfo | jq   # licensed features
```

Check `licenseinfo` when a feature such as Chaos, App Inspector, IAM enforcement, Replicator, or Extensions returns a license or not-found error.

## Configure emulator environment

Configure the emulator in `config.toml`. Settings there are versioned with the project, survive `lstk restart`, and give every teammate and CI run the same emulator.

Find the active configuration file:

```bash
lstk config path
```

`lstk` reads `./.lstk/config.toml` when the current directory has one, and `$HOME/.config/lstk/config.toml` otherwise; the lookup does not walk up parent directories. A committed `.lstk/config.toml` pins the emulator type, port, and environment profiles for commands run from the repository root.

Add named environment profiles to that TOML file and reference them from the active `[[containers]]` block. Keys inside a profile take no `LOCALSTACK_` prefix:

```toml
[[containers]]
type = "aws"
tag = "latest"
port = "4566"
env = ["debug", "iam"]

[env.debug]
DEBUG = "1"
LS_LOG = "trace"

[env.iam]
ENFORCE_IAM = "1"
```

Preserve unrelated settings and keep only one enabled `[[containers]]` block. Restart the emulator after changing its environment.

Common settings:

| Setting | Effect |
| --- | --- |
| `DEBUG = "1"` | Debug logging |
| `LS_LOG = "trace"` | Request and response-level logging |
| `PERSISTENCE = "1"` | Persist state across restarts by default |
| `SERVICES = "s3,sqs"` | Allowlist of services; every other service is disabled. See below before setting it |
| `ENFORCE_IAM = "1"` | IAM enforcement; add `IAM_SOFT_MODE = "1"` to log violations without denying. See the `localstack-iam` skill |
| `GATEWAY_LISTEN = ":4566"` | Bind only port 4566 |

Leave `SERVICES` unset by default. Services already start lazily on their first request, so listing them does not speed up startup or save memory. Setting it disables every service not listed, and calls to those services fail. That includes calls that IaC tools and other AWS services make on your behalf: a CDK deploy needs CloudFormation, S3, IAM, and SSM, and a Lambda needs IAM and CloudWatch Logs. Set it only to prove that a workload uses nothing outside a known set of services. When a call to an unlisted service fails, add the service or remove the setting.

To start services at boot instead of on first use, for example so the first test request is not slowed down, set `EAGER_SERVICE_LOADING = "1"`. This makes startup longer; combine it with `SERVICES` only when you also want the allowlist.

Set `tag` in the container block to pin the emulator version instead of tracking `latest` when a run must be reproducible, for example `tag = "2026.4"`. Set `image` to pull the emulator from an internal registry mirror; if `image` carries no tag, `tag` is appended to it.

Two settings belong to the host, not the emulator, and stay environment variables: `LOCALSTACK_AUTH_TOKEN` and `LOCALSTACK_HOST`, the endpoint host used by the `lstk` proxies.

### One-off overrides

For a single throwaway run, `lstk start` also forwards host environment variables prefixed with `LOCALSTACK_`, and the emulator strips the prefix:

```bash
LOCALSTACK_DEBUG=1 lstk start
```

These overrides do not stick. `lstk restart` rebuilds the container from the current shell's environment, so an inline variable is gone after a plain restart. Put anything needed twice in a profile. Also:

- The host `LOCALSTACK_AUTH_TOKEN` is never forwarded to the container.
- Variables whose stripped name would clobber the container environment, such as `LOCALSTACK_PATH`, `LOCALSTACK_HOME`, `LOCALSTACK_LD_PRELOAD`, or `LOCALSTACK_PYTHONPATH`, and values containing line breaks are dropped with a warning.

## Target an external emulator

Commands with a remote equivalent accept a global endpoint:

```bash
lstk --endpoint-url https://example.localstack.cloud status
lstk --endpoint-url https://example.localstack.cloud aws s3 ls
```

Do not use `--endpoint-url` with `start`, `stop`, `restart`, `logs`, or `volume`; those operations require an emulator managed by the local runtime. `lstk` cannot adopt a LocalStack container started by Docker Compose; use `--endpoint-url` to reach one.

## Use features without an lstk command

Never invent `lstk extensions`, `lstk chaos`, or `lstk replicator`. These features work with an `lstk`-managed emulator through the gateway's HTTP APIs or emulator configuration:

| Feature | Skill |
| --- | --- |
| In-emulator Extensions | `localstack-extensions` |
| Chaos faults and latency | `localstack-chaos` |
| App Inspector queries (`lstk inspect` only toggles it) | `localstack-app-inspector` |
| AWS Replicator | `localstack-replicator` |
| IAM mode switching at runtime | `localstack-iam` |

Git-style `lstk-<name>` CLI extensions are a separate mechanism, covered by the `lstk-extensions` skill.

## Check service coverage

For "is X supported?" and configuration details, search https://docs.localstack.cloud. Per-service AWS coverage lives under `/aws/services/<service>/`; Snowflake and Azure have their own sections under `/snowflake/` and `/azure/`. Check there before working around an error that might be an unsupported feature.

## Troubleshoot startup

Run `lstk doctor` first when `lstk start` fails before the emulator comes up. It checks DNS and HTTPS to the LocalStack API, TLS-intercepting proxies, the container engine, memory, and disk, and prints a fix for each failure:

```bash
lstk doctor
lstk doctor network --verbose     # one category: network, container, or system
lstk --json doctor                # exit 0 ok, 1 fixable, 2 blocking, 3 check failed
```

Then work through:

1. Run `lstk status`.
2. Inspect `lstk logs --tail 200`, adding `--verbose` when request or provider lines matter.
3. Confirm the configured host port is available.
4. Confirm the detected container runtime is running. `Error: runtime not healthy` means it is not.
5. Run `lstk config path` and inspect the active emulator type, image, port, environment profiles, and mounts. A setting with no effect usually sits in a profile missing from the container block's `env`, or in a file other than the active one.
6. For authentication failures, run `lstk login` or provide a valid `LOCALSTACK_AUTH_TOKEN`. For a stale license, run `lstk logout` and then `lstk login`.
7. Read `lstk.log`, which `lstk` writes next to the configuration file. It records CLI-side events such as license and token resolution that never reach `lstk logs`.

The checklist above misses two cases:

- The emulator gateway listens on `:4566,:443` by default, so startup can fail on port 443 while the configured port is free. Set `GATEWAY_LISTEN = ":4566"` in an environment profile to bind only 4566.
- `lstk` probes the default container-runtime socket, not the one a `docker` context may be using. Set `DOCKER_HOST` when the runtime listens elsewhere.

Use direct container-runtime commands only as a last-resort diagnostic, not as the normal lifecycle workflow.
