---
name: localstack-extensions
description: Manage LocalStack Extensions. Use when users want to install, uninstall, list, discover, or configure LocalStack extensions (from the marketplace or PyPI), preload extensions on start, check whether an extension loaded, or develop custom extensions.
---

# LocalStack Extensions

Extensions add services and integrations to the emulator (MailHog for SES, TypeDB, httpbin, and more). They are Python packages installed into a virtualenv on the emulator volume, so they survive restarts.

## Prerequisites

- A running AWS emulator (`lstk start`) — see the `localstack` skill
- A license that includes Extensions

`lstk` has no `extensions` command, but an `lstk`-managed emulator runs extensions fine. Pick the route by task:

| Task | Route |
|------|-------|
| Install extensions for the project | [`EXTENSION_AUTO_INSTALL`](#install-on-start) |
| List, try, or remove extensions on a running emulator | [Extensions API](#manage-extensions-on-a-running-emulator) |
| Browse what is available | [Marketplace](#discover-extensions) |
| Build and ship your own extension | [Custom extensions](#developing-custom-extensions) |

## Install on start

`EXTENSION_AUTO_INSTALL` takes a comma-separated list of package specs and installs them when the emulator starts. Set it in an environment profile in `config.toml`:

```toml
[[containers]]
type = "aws"
env  = ["extensions"]

[env.extensions]
EXTENSION_AUTO_INSTALL = "localstack-extension-mailhog,localstack-extension-httpbin==0.2.0"
```

Then `lstk start` (or `lstk restart` if the emulator is already running). The extension list is committed with the project, so every teammate and CI run gets the same extensions.

Use package specs only (`name`, `name[extra]`, `name==version`). Git URLs are not supported.

## Manage extensions on a running emulator

The emulator gateway exposes an extensions API. It is what the LocalStack Web Application's Extension Manager uses, but it is not in the public docs, so it may change.

List installed extensions and whether each one loaded:

```bash
curl -s localhost:4566/_localstack/extensions/list \
  | jq '.[] | {name, version: .distribution.version, status}'
```

Each entry has the plugin `name`, the package metadata under `distribution` (`name`, `version`, `summary`), and a `status` with `is_initialized`, `is_loaded`, and `load_error`. `load_error: true` means the extension failed to load; read the stack trace with `lstk logs --verbose | grep -i extension`. An extension missing from the list is not installed.

Install or uninstall one, for example to try it before adding it to the profile:

```bash
curl -s -X POST localhost:4566/_localstack/extensions/install \
  -H 'Content-Type: application/json' -d '{"URL": "localstack-extension-mailhog"}'

curl -s -X POST localhost:4566/_localstack/extensions/uninstall \
  -H 'Content-Type: application/json' -d '{"distribution": "localstack-extension-mailhog"}'
```

- `URL` takes the same package specs as `EXTENSION_AUTO_INSTALL`, including `name==version`. Git URLs are rejected.
- `uninstall` takes either the package name as `distribution` or the plugin name as `name`, not both.
- The response streams one JSON object per line while pip runs. A line with `"event": "error"` or `"event": "exception"` means the call failed; read its `message`.
- LocalStack restarts itself after every install or uninstall, even when the body sets `"restart": false`. In-memory state is lost unless persistence is on, so save a snapshot first if it matters (`localstack-state` skill). Wait until `lstk status` reports the emulator ready, then check the list again.

An extension installed this way stays on the emulator volume but is not recorded in the project. When it should stay, add it to `EXTENSION_AUTO_INSTALL` so teammates and CI get it too.

## Discover extensions

Browse the [Extensions Library](https://app.localstack.cloud/extensions/library), or query the marketplace with your auth token (empty username, token as password):

```bash
curl -s -u ":$LOCALSTACK_AUTH_TOKEN" https://api.localstack.cloud/v1/extensions/marketplace \
  | jq '.[] | {name, version, author, summary}'
```

## Using an extension: MailHog

With `localstack-extension-mailhog` in the `EXTENSION_AUTO_INSTALL` profile above:

```bash
lstk start

lstk aws ses verify-email-identity --email-address sender@example.com
lstk aws ses send-email \
  --from sender@example.com \
  --destination ToAddresses=recipient@example.com \
  --message 'Subject={Data=Test},Body={Text={Data=Hello}}'

# Captured mail (either URL works)
open http://mailhog.localhost.localstack.cloud:4566
open http://localhost:4566/mailhog/
```

MailHog configures SES's SMTP target automatically. Other extensions document their own URLs and settings on their library page.

## Configuration

Extensions read their settings from emulator environment variables. Put them in the same `[env.*]` profile in `config.toml`, unprefixed — see the `localstack` skill.

## Developing custom extensions

Start from an existing extension in [localstack/localstack-extensions](https://github.com/localstack/localstack-extensions) — each one is a complete, buildable example of the Extension API. To ship yours, publish the package to PyPI and add it to `EXTENSION_AUTO_INSTALL`.

## Troubleshooting

- **Extension not active**: check `curl -s localhost:4566/_localstack/extensions/list`. If it is missing, confirm the `extensions` profile is listed in the container block's `env`, then `lstk restart`. If it is listed with `load_error: true`, read the startup errors below
- **Errors on startup**: `lstk logs -v | grep -i extension`
- **Version issues**: pin a version compatible with your LocalStack image
