---
name: localstack
description: Manage the LocalStack emulator lifecycle with the lstk CLI. Use when users need to start, stop, restart, reset, or check status of LocalStack, configure LocalStack environment variables, or troubleshoot LocalStack container issues.
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

> The legacy `localstack` CLI is deprecated and will be removed in a future version. Prefer `lstk`. A few features still live only in the legacy CLI — see [Legacy CLI fallbacks](#legacy-cli-fallbacks).

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

Token resolution order: system keyring (from `lstk login`) → `LOCALSTACK_AUTH_TOKEN` → interactive browser login. The keyring wins over the environment variable, so run `lstk logout` first if you need to switch.

## Common Commands

### Start LocalStack

```bash
# Start the emulator (bare `lstk` is equivalent to `lstk start`)
lstk start

# Start and keep state across restarts
lstk start --persist

# Start with debug logging (note the LOCALSTACK_ prefix)
LOCALSTACK_DEBUG=1 lstk start

# Pick the emulator type
lstk start --type aws          # also: snowflake, azure

# Plain output for scripts/CI, with a startup deadline
lstk --non-interactive --timeout 90s start
```

`lstk start` runs the container in the background and returns once the emulator is ready — there is no `-d` flag.

### Check Status

```bash
# Emulator state plus the resources currently deployed in it
lstk status

# Plain-text output for scripts
lstk --non-interactive status

# Service health endpoint
curl http://localhost:4566/_localstack/health | jq
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

### Passing environment variables

`lstk` forwards **host environment variables prefixed with `LOCALSTACK_`** into the emulator. Any LocalStack config variable you used to pass bare must now carry that prefix:

```bash
LOCALSTACK_DEBUG=1 lstk start
LOCALSTACK_SERVICES=s3,sqs lstk start
LOCALSTACK_ENFORCE_IAM=soft lstk start
```

The host `LOCALSTACK_AUTH_TOKEN` is deliberately *not* forwarded, so it cannot override the token `lstk` resolved.

### Environment profiles in `config.toml`

For settings you want on every run, define named profiles in `config.toml` and reference them from the container block. Keys inside a profile do **not** need the `LOCALSTACK_` prefix:

```toml
[[containers]]
type = "aws"
tag  = "latest"
port = "4566"
env  = ["debug", "ci"]

[env.debug]
DEBUG = "1"
PERSISTENCE = "1"

[env.ci]
SERVICES = "s3,sqs"
EAGER_SERVICE_LOADING = "1"
```

Config file resolution order: `./.lstk/config.toml` (project-local) → `$HOME/.config/lstk/config.toml` → OS default location. Print the active path with `lstk config path`.

### Common configuration options

| Variable | Description | How to set |
|----------|-------------|------------|
| `DEBUG` | Enable debug logging | `LOCALSTACK_DEBUG=1 lstk start` or `[env.*]` profile |
| `PERSISTENCE` | Persist state across restarts | `lstk start --persist` (preferred) or profile |
| `SERVICES` | Limit the services started | `LOCALSTACK_SERVICES=s3,sqs lstk start` |
| `GATEWAY_LISTEN` | Bind address/ports | `GATEWAY_LISTEN = "0.0.0.0:4566"` in a profile |
| `LOCALSTACK_AUTH_TOKEN` | Platform auth token | Env var, or `lstk login` |
| `LOCALSTACK_HOST` | Override the endpoint host used by `lstk aws` and friends | Env var |

Pin an image version with `tag` in `config.toml` (e.g. `tag = "2026.4"`), or point `image` at an internal registry for air-gapped setups.

## Legacy CLI fallbacks

`lstk` does not cover every legacy feature yet. Install the legacy CLI (`pip install localstack`) alongside `lstk` only if you need:

- **Extensions** — there is no `lstk extensions` command suite; see the `localstack-extensions` skill
- **`localstack aws iam stream` / `summary`** — IAM policy stream and summary; see the `localstack-iam` skill
- **Advanced DNS configuration** (systemd-resolved integration) and ephemeral cloud instances

`lstk` manages its own Docker container and cannot be mixed with a Docker Compose LocalStack setup, or with a container started by the legacy `localstack start`. To point `lstk` at an emulator you manage yourself, use `--endpoint-url`.

## Troubleshooting

- **`Error: runtime not healthy`**: Docker is not running. Start Docker Desktop or the daemon, or set `DOCKER_HOST` for a custom socket.
- **Port 443 conflict**: set `GATEWAY_LISTEN = "0.0.0.0:4566"` in an environment profile so only 4566 is bound.
- **Auth errors in CI**: set `LOCALSTACK_AUTH_TOKEN` before `lstk start`; a TTY-less environment cannot run the browser flow.
- **Stale license**: `lstk logout && lstk login`.
- **Unknown env var had no effect**: confirm it is prefixed with `LOCALSTACK_` on the host, or moved into an `[env.*]` profile.
- **Diagnostics**: `lstk` writes `lstk.log` next to the config file — find it with `lstk config path`.
