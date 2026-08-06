---
name: localstack-extensions
description: Use and author Git-style lstk CLI extensions. Use when invoking, discovering, or building an executable whose name starts with lstk-, handling LSTK_EXT_CONTEXT, or distinguishing CLI extensions from in-emulator LocalStack Extensions.
---

# Use and author lstk CLI extensions

`lstk` supports Git-style extensions. An executable named `lstk-<name>` on `PATH` becomes `lstk <name>`. There is no manifest, registry, install command, or registration step.

This mechanism is different from Python-based LocalStack Extensions that run inside the emulator.

## Discover and invoke extensions

List built-in commands and discovered extensions:

```bash
lstk --help
```

Locate an extension directly:

```bash
command -v lstk-example
```

Invoke it through `lstk`:

```bash
lstk example --flag value
```

Built-in commands and aliases always win. Arguments after the extension name are forwarded verbatim, and the extension's exit code and standard streams pass through.

## Install an extension executable

1. Obtain or build a trusted executable named `lstk-<name>`.
2. Put it in a directory on `PATH`.
3. Mark it executable on Unix-like systems.
4. Confirm it appears in `lstk --help`.
5. Run a harmless help or version command before allowing state changes.

`lstk` does not sandbox or verify third-party extensions. Do not install or execute an untrusted binary.

## Read runtime context

`lstk` supplies:

- `LSTK_EXT_API_VERSION`: breaking-version number for the context contract.
- `LSTK_EXT_CONTEXT`: JSON containing the resolved config directory, optional auth token, output mode, optional telemetry session ID, and running emulators.

A shell extension can read the AWS endpoint with `jq`:

```sh
context=${LSTK_EXT_CONTEXT:-}
aws_endpoint=$(
  printf '%s' "$context" |
    jq -r '.emulators[]? | select(.type == "aws") | .endpoint' |
    head -n 1
)

if [ -z "$aws_endpoint" ]; then
  printf '%s\n' "an AWS emulator is required; run 'lstk start --type aws'" >&2
  exit 1
fi
```

Treat the context as runtime input:

- Check a field's presence instead of inferring it from the API version.
- Use `LSTK_EXT_API_VERSION` only to reject a breaking contract generation.
- Handle an empty `emulators` array.
- Select an emulator by `type`; do not assume only one entry.
- Never print or persist `authToken`.
- Do not prompt when `nonInteractive` is true.
- Emit machine-readable output when choosing to honor `json`.

## Author an extension

Name the executable `lstk-<name>` and parse only the arguments it owns. A minimal POSIX shell extension:

```sh
#!/usr/bin/env sh
set -eu

if [ "${LSTK_EXT_API_VERSION:-0}" -gt 1 ]; then
  printf '%s\n' "unsupported lstk extension API version" >&2
  exit 1
fi

if [ -z "${LSTK_EXT_CONTEXT:-}" ]; then
  printf '%s\n' "this command must be run through lstk" >&2
  exit 1
fi

printf '%s\n' "extension is ready"
```

Keep failures actionable and preserve meaningful exit codes. If the extension performs paid or protected work, authorize server-side with the supplied token; a client-side check is not a security boundary.

## Distinguish emulator extensions

When the user means a Python extension running inside the LocalStack emulator, do not invent commands such as `lstk extensions install`. `lstk` v2 does not manage that system. Use the current [LocalStack Extensions documentation](https://docs.localstack.cloud/aws/configuration/extensions/) or the Extensions Library instead.
