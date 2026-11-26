---
name: localstack
description: Manage the LocalStack emulator lifecycle with the lstk CLI. Use when users need to start, stop, restart, reset, or check status of LocalStack (AWS, Snowflake, or Azure emulator), configure LocalStack environment variables, diagnose a machine where LocalStack will not start, or troubleshoot LocalStack container issues.
---

# LocalStack Lifecycle Management

Manage the LocalStack emulator lifecycle — starting, stopping, and monitoring the local cloud environment — using `lstk`, the current LocalStack CLI.

## Capabilities

- Start LocalStack with custom configuration
- Stop, restart, and reset running LocalStack instances
- Check LocalStack status and health
- Manage the emulator volume and persisted state
- Authenticate against the LocalStack platform

## Prerequisites

- Docker installed and running
- A LocalStack account (`lstk` pulls the `localstack/localstack-pro` image and requires a valid license)
- The `lstk` CLI:

```bash
# Homebrew (macOS/Linux)
brew install localstack/tap/lstk

# npm
npm install -g @localstack/lstk

# Verify
lstk --version
```

## Authentication

```bash
# Interactive browser login; stores the token in the system keyring
lstk login

# Remove stored credentials
lstk logout
```

In CI or any non-TTY environment, set the auth token instead (a CI Auth Token — a personal Developer Auth Token will not work in CI):

```bash
export LOCALSTACK_AUTH_TOKEN=<token>
lstk --non-interactive start
```

Token resolution order: `LOCALSTACK_AUTH_TOKEN` → system keyring (from `lstk login`) → interactive browser login. The environment variable wins, so `LOCALSTACK_AUTH_TOKEN=<other-token> lstk start` switches accounts for one run without logging out.

## Common Commands

### Start LocalStack

```bash
# Start the emulator (bare `lstk` is equivalent to `lstk start`)
lstk start

# Start and keep state across restarts
lstk start --persist

# Pick the emulator type (saved to config.toml for later starts)
lstk start --type aws          # also: snowflake, azure — see the localstack-snowflake and localstack-azure skills

# Run a different image for this start only (not saved)
lstk start --image localstack/localstack-pro:2026.4

# Plain output for scripts/CI, with a startup deadline
lstk --non-interactive --timeout 90s start
```

`lstk start` runs the container in the background and returns once the emulator is ready — there is no `-d` flag.

### Check Status

```bash
# Emulator state plus the resources currently deployed in it
lstk status

# Machine-readable, for scripts and agents
lstk --json status
lstk --json status --no-resources

# Gateway endpoints
curl -s localhost:4566/_localstack/health | jq       # per-service state
curl -s localhost:4566/_localstack/info | jq         # version, session, uptime
curl -s localhost:4566/_localstack/licenseinfo | jq  # which licensed features are active
```

Check `licenseinfo` when a feature (Chaos, App Inspector, IAM enforcement, Replicator, Extensions, Snowflake) returns a license or not-found error.

### Diagnose a machine that cannot start

`lstk doctor` checks DNS and HTTPS to the LocalStack API, TLS-intercepting proxies, the container engine, memory, and disk, and prints a fix for each failure. Run it first when `lstk start` fails before the emulator comes up:

```bash
lstk doctor                       # all checks
lstk doctor network --verbose     # one category: network, container, system
lstk --json doctor                # for CI; exit 0 ok, 1 fixable, 2 blocking, 3 check failed
```

### Stop and Restart

```bash
lstk stop
lstk restart
lstk restart --persist
```

### Reset State

```bash
# Discard all in-memory resources; the emulator keeps running
lstk reset
lstk reset --force        # skip the confirmation prompt
```

### View Logs

```bash
lstk logs                 # print available logs
lstk logs -f              # follow in real time
lstk logs -n 100          # last 100 lines
lstk logs -v              # unfiltered output
```

### Manage the Volume

```bash
lstk volume path          # print the volume directory
lstk volume clear         # wipe certificates, cached tools, persisted data
lstk volume clear --force
```

`lstk reset` clears in-memory state; `lstk volume clear` wipes the on-disk volume. Stop the emulator before clearing the volume.

## Configuration

Configure the emulator in `config.toml`. It is the **preferred** way: settings are versioned with the project, survive `lstk restart`, and every teammate and CI run gets the same emulator.

### Environment profiles in `config.toml`

Define named `[env.*]` profiles and list the ones to apply in the container block's `env`. Keys use the plain LocalStack names — no `LOCALSTACK_` prefix:

```toml
[[containers]]
type = "aws"
tag  = "latest"
port = "4566"
env  = ["debug", "iam"]

[env.debug]
DEBUG = "1"
PERSISTENCE = "1"

[env.iam]
ENFORCE_IAM = "1"
```

Use a project-local `./.lstk/config.toml` for project settings, so they are committed with the code. Resolution order: `./.lstk/config.toml` → `$HOME/.config/lstk/config.toml` → OS default location. Print the active path with `lstk config path`. Config changes take effect on the next `lstk start` or `lstk restart`.

### Common configuration options

| Setting | Description | In a profile |
|---------|-------------|--------------|
| `DEBUG` | Debug logging | `DEBUG = "1"` |
| `LS_LOG` | Log level, e.g. `trace` | `LS_LOG = "trace"` |
| `PERSISTENCE` | Persist state across restarts | `PERSISTENCE = "1"` (or `lstk start --persist`) |
| `SERVICES` | Allowlist of services; every other service is disabled. See below before setting it | `SERVICES = "s3,sqs"` |
| `ENFORCE_IAM` | IAM enforcement; add `IAM_SOFT_MODE = "1"` to log violations without denying | `ENFORCE_IAM = "1"` |
| `GATEWAY_LISTEN` | Bind address/ports | `GATEWAY_LISTEN = "0.0.0.0:4566"` |

Leave `SERVICES` unset by default. Services already start lazily on their first request, so listing them does not speed up startup or save memory. Setting it disables every service not listed, and calls to those services fail. That includes calls that IaC tools and other AWS services make on your behalf: a CDK deploy needs CloudFormation, S3, IAM, and SSM, and a Lambda needs IAM and CloudWatch Logs. Set it only to prove that a workload uses nothing outside a known set of services. When a call to an unlisted service fails, add the service or remove the setting.

To start services at boot instead of on first use, for example so the first test request is not slowed down, set `EAGER_SERVICE_LOADING = "1"`. This makes startup longer; combine it with `SERVICES` only when you also want the allowlist.

Two settings are host-side, not emulator config, and stay environment variables: `LOCALSTACK_AUTH_TOKEN` (or `lstk login`) and `LOCALSTACK_HOST` (endpoint host used by `lstk aws` and friends).

Pin an image version with `tag` (e.g. `tag = "2026.4"`), or point `image` at an internal registry for air-gapped setups.

### One-off overrides with `LOCALSTACK_*` variables

For a single throwaway run, `lstk` also forwards host environment variables prefixed with `LOCALSTACK_`; the image strips the prefix, so LocalStack sees `DEBUG=1`:

```bash
LOCALSTACK_DEBUG=1 lstk start
```

These do **not** stick: `lstk restart` recreates the container from the current shell's environment, so an inline variable is gone after a plain restart. Anything you want twice belongs in a profile. Also:

- The host `LOCALSTACK_AUTH_TOKEN` is never forwarded, so it cannot override the token `lstk` resolved.
- Variables whose stripped name would clobber the container (`LOCALSTACK_PATH`, `_HOME`, `_IFS`, `_BASH_ENV`, `_LD_PRELOAD`, `_LD_LIBRARY_PATH`, `_PYTHONPATH`, `_PYTHONHOME`) and values containing line breaks are dropped with a warning.

Pin an image version with `tag` in `config.toml` (e.g. `tag = "2026.4"`), or point `image` at an internal registry for air-gapped setups.

## Features without an `lstk` command

These work with an `lstk`-managed emulator through the gateway's HTTP APIs or the platform API — each has its own skill:

| Feature | Skill |
|---------|-------|
| Extensions | `localstack-extensions` |
| Chaos faults and latency | `localstack-chaos` |
| App Inspector queries (`lstk inspect` only toggles it) | `localstack-app-inspector` |
| AWS Replicator | `localstack-replicator` |
| IAM mode switching at runtime | `localstack-iam` |

`lstk` manages its own Docker container and cannot be mixed with a Docker Compose LocalStack setup. To point `lstk` at an emulator you manage yourself, use `--endpoint-url`.

## Finding answers in the docs

For coverage questions ("is X supported?") and configuration details, search https://docs.localstack.cloud. Per-service coverage lives under `/aws/services/<service>/`; Snowflake and Azure have their own sections (`/snowflake/`, `/azure/`). Check there before working around an error that might be an unsupported feature.

## Troubleshooting

- **Start fails or activation hangs**: run `lstk doctor` — it diagnoses blocked DNS/HTTPS to the LocalStack API, intercepting proxies, the container engine, and low memory or disk.
- **`Error: runtime not healthy`**: Docker is not running. Start Docker Desktop or the daemon, or set `DOCKER_HOST` for a custom socket.
- **Port 443 conflict**: set `GATEWAY_LISTEN = "0.0.0.0:4566"` in an environment profile so only 4566 is bound.
- **Auth errors in CI**: set `LOCALSTACK_AUTH_TOKEN` before `lstk start`; a TTY-less environment cannot run the browser flow.
- **Stale license**: `lstk logout && lstk login`.
- **Config setting had no effect**: check that its profile is listed in the container block's `env`, that `lstk config path` shows the file you edited, and that you restarted. An inline `LOCALSTACK_*` variable is lost on a plain `lstk restart`.
- **Diagnostics**: `lstk` writes `lstk.log` next to the config file — find it with `lstk config path`.
