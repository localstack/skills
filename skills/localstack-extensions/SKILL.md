---
name: localstack-extensions
description: Install, configure, and author in-emulator LocalStack Extensions. Use when adding an Extension to the emulator, browsing the Extensions Library, developing a Python Extension, or debugging one that fails to load. Extensions require the legacy localstack CLI, not lstk.
---

# Manage in-emulator LocalStack Extensions

Extensions are Python packages that run inside the LocalStack emulator to add endpoints, integrate third-party tools, and extend platform behavior.

`lstk` does not manage Extensions. There is no `lstk extensions` command suite, and `lstk` keeps its own volume directory (`lstk volume path`, for example `~/Library/Caches/lstk/volume/localstack-aws`) separate from the legacy volume that Extensions install into, so an emulator started by `lstk` will not load them. Extension workflows must use the legacy `localstack` CLI for both installing Extensions and starting the emulator.

Prefer `lstk` for every other workflow: lifecycle, IaC, snapshots, and logs. See the `localstack` skill. For Git-style `lstk-<name>` CLI extensions, which are a different mechanism, see the `lstk-extensions` skill.

## Check prerequisites

Install the legacy CLI, and the `awslocal` wrapper if you want the shorter command form:

```bash
pip install localstack
pip install awscli-local   # optional; or use: aws --endpoint-url=http://localhost:4566
```

`localstack extensions init`, `install`, `uninstall`, and `list` run inside a container; with Docker stopped they fail with `Docker could not be found on the system.` The `dev` subcommands run on the host and do not need a container runtime.

Do not run `lstk start` and `localstack start` at the same time. Each manages its own container and they conflict on port 4566. Stop one before starting the other with `lstk stop` or `localstack stop`.

The legacy `localstack` CLI is deprecated and will be removed in a future version. Use it only for the workflows on this page.

## Install and remove Extensions

The `localstack extensions` command group is a preview feature. Its own help text warns that the feature and the API may change, so confirm the available commands with `localstack extensions --help` rather than assuming a fixed list.

Prepare the extensions environment inside the volume:

```bash
localstack extensions init
```

It installs into `lib/extensions` under the volume directory resolved from `LOCALSTACK_VOLUME_DIR`.

List what is installed:

```bash
localstack extensions list
```

Install from PyPI, a pinned version, or a Git repository:

```bash
localstack extensions install localstack-extension-name
localstack extensions install localstack-extension-name==1.0.0
localstack extensions install "git+https://github.com/org/extension-repo.git"
```

Remove one:

```bash
localstack extensions uninstall localstack-extension-name
```

Extensions are enabled once installed. Disable one for a single run with its environment variable:

```bash
EXTENSION_NAME_ENABLED=0 localstack start -d
```

## Discover available Extensions

Browse the [Extensions Library](https://app.localstack.cloud/extensions/library) and the [Extensions documentation](https://docs.localstack.cloud/aws/capabilities/extensions/).

## Run an Extension

Install the Extension, then start the emulator with the legacy CLI so it is loaded:

```bash
localstack extensions install localstack-extension-mailhog
localstack start -d
```

Reach the Extension's own interface and exercise the service it hooks:

```bash
open http://localhost:8025

awslocal ses send-email \
  --from sender@example.com \
  --to recipient@example.com \
  --subject "Test" \
  --text "Hello"
```

## Configure an Extension

Pass environment variables to `localstack start`:

```bash
# General pattern
EXTENSION_<NAME>_<SETTING>=value localstack start -d

# Example
EXTENSION_MAILHOG_PORT=8025 localstack start -d
```

The legacy CLI takes these variables without the `LOCALSTACK_` prefix that `lstk` requires.

## Author an Extension

Scaffold from the official extension template:

```bash
localstack extensions dev new
```

The template is rendered with cookiecutter, so install that first with `pip install cookiecutter`. The new Extension is created in the current working directory. Pass `--template` to pick a template other than the default `basic`.

Lay the package out so the Extension class is importable:

```text
my-extension/
├── setup.py
└── my_extension/
    ├── __init__.py
    └── extension.py
```

Subclass `Extension` and implement the hooks you need:

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

Install from the source tree and use the developer helpers while iterating. `install` takes a positional name; a `file://` prefix installs a distribution from disk, and `file://.` treats the current directory as one:

```bash
localstack extensions install file://.

localstack extensions dev enable ./my-extension
localstack extensions dev list
localstack extensions dev disable ./my-extension
```

## Diagnose a failing Extension

- **Extension not loading**: confirm you started the emulator with `localstack start`, not `lstk start`. `lstk` uses a different volume directory and will not see installed Extensions.
- **Port conflict on 4566**: an `lstk`-managed container may still be running. Run `lstk stop` first.
- **Errors on startup**: check `localstack logs` for Extension stack traces.
- **Two Extensions interfering**: disable one to isolate the failure.
- **Version mismatch**: confirm the Extension supports your LocalStack version.
- **Docker Compose setups**: point `LOCALSTACK_VOLUME_DIR` at the LocalStack volume on your host, `~/.cache/localstack/volume` on Linux or `~/Library/Caches/localstack/volume` on macOS, so the CLI installs into the volume the emulator mounts.
