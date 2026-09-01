---
name: localstack-extensions
description: Manage LocalStack Extensions. Use when users want to install, uninstall, list, or configure LocalStack extensions, or develop custom extensions to extend LocalStack functionality. Extensions require the legacy localstack CLI, not lstk.
---

# LocalStack Extensions

Manage LocalStack Extensions to add custom functionality, integrate third-party tools, and extend LocalStack capabilities.

> **`lstk` does not support Extensions.** There is no `lstk extensions` command suite. Extension workflows must use the legacy `localstack` CLI for both installing extensions *and* starting the emulator — `lstk` keeps its own volume directory (`lstk volume path`, e.g. `~/Library/Caches/lstk/volume/localstack-aws`), separate from the legacy volume that extensions install into, so an emulator started by `lstk` will not load them.
>
> For everything else — lifecycle, IaC, snapshots, logs — prefer `lstk`. See the `localstack` skill.

## Capabilities

- Install and manage LocalStack Extensions
- Discover available extensions
- Configure extension settings
- Develop custom extensions

## Prerequisites

The legacy CLI and, for the examples below, the `awslocal` wrapper:

```bash
pip install localstack
pip install awscli-local   # optional; or use: aws --endpoint-url=http://localhost:4566
```

Do not run `lstk start` and `localstack start` at the same time — each manages its own container and they will conflict on port 4566. Stop one before starting the other (`lstk stop` / `localstack stop`).

## Extension Management

### List Installed Extensions

```bash
localstack extensions list
```

### Install Extensions

```bash
# Install from PyPI
localstack extensions install localstack-extension-name

# Install specific version
localstack extensions install localstack-extension-name==1.0.0

# Install from Git repository
localstack extensions install "git+https://github.com/org/extension-repo.git"
```

### Uninstall Extensions

```bash
localstack extensions uninstall localstack-extension-name
```

### Enable/Disable Extensions

```bash
# Extensions are enabled by default after installation
# Disable via environment variable
EXTENSION_NAME_ENABLED=0 localstack start -d
```

## Available Extensions

Browse the [Official Extensions Library](https://app.localstack.cloud/extensions/library) and the [Extensions documentation](https://docs.localstack.cloud/aws/capabilities/extensions/) for available extensions.

## Using Extensions

### MailHog Extension

```bash
# Install
localstack extensions install localstack-extension-mailhog

# Start LocalStack with the legacy CLI so the extension is loaded
localstack start -d

# Access MailHog UI
open http://localhost:8025

# SES emails will be captured by MailHog
awslocal ses send-email \
  --from sender@example.com \
  --to recipient@example.com \
  --subject "Test" \
  --text "Hello"
```

## Developing Custom Extensions

### Extension Structure

```
my-extension/
├── setup.py
├── my_extension/
│   ├── __init__.py
│   └── extension.py
```

### Basic Extension

```python
# extension.py
from localstack.extensions.api import Extension, http

class MyExtension(Extension):
    name = "my-extension"

    def on_extension_load(self):
        print("Extension loaded!")

    def on_platform_start(self):
        print("LocalStack is starting!")

    @http.route("/my-endpoint")
    def my_endpoint(self, request):
        return {"message": "Hello from extension!"}
```

### Install Local Extension

```bash
# Install in development mode
localstack extensions install -e ./my-extension

# Developer mode helpers
localstack extensions dev list
localstack extensions dev enable ./my-extension
```

## Configuration

Extensions are configured via environment variables passed to `localstack start`:

```bash
# General pattern
EXTENSION_<NAME>_<SETTING>=value localstack start -d

# Example
EXTENSION_MAILHOG_PORT=8025 localstack start -d
```

Note that the legacy CLI takes these variables **without** the `LOCALSTACK_` prefix that `lstk` requires.

## Troubleshooting

- **Extension not loading**: Confirm you started the emulator with `localstack start`, not `lstk start` — `lstk` uses a different volume directory and will not see installed extensions
- **Port conflict on 4566**: an `lstk`-managed container may still be running; `lstk stop` first
- **Errors on startup**: check `localstack logs` for extension stack traces
- **Conflicts**: disable conflicting extensions
- **Version issues**: ensure the extension is compatible with your LocalStack version
- **Docker Compose users**: point `LOCALSTACK_VOLUME_DIR` at the LocalStack volume on your host (`~/.cache/localstack` on Linux, `~/Library/Caches/localstack` on macOS) so the CLI installs into the right place
