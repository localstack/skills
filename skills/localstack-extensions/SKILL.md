---
name: localstack-extensions
description: Install, discover, configure, and develop in-emulator LocalStack Extensions on an lstk-managed emulator. Use when adding an Extension such as MailHog to the emulator, preloading Extensions on start, browsing the Extensions Library, or building a custom Extension.
---

# Manage in-emulator LocalStack Extensions

Extensions are Python packages that run inside the LocalStack emulator to add services and integrations, such as MailHog for SES, TypeDB, or httpbin. They install into a virtualenv on the emulator volume, so they survive restarts.

`lstk` has no `extensions` command; never invent `lstk extensions install`. An `lstk`-managed emulator still runs Extensions: install them through emulator configuration. For Git-style `lstk-<name>` CLI extensions, which are a different mechanism, see the `lstk-extensions` skill.

Extensions require a running AWS emulator and a license that includes them; see the `localstack` skill.

## Install on start

`EXTENSION_AUTO_INSTALL` takes a comma-separated list of package specs and installs them when the emulator starts. Set it in a profile in the file that `lstk config path` reports:

```toml
[[containers]]
type = "aws"
env = ["extensions"]

[env.extensions]
EXTENSION_AUTO_INSTALL = "localstack-extension-mailhog,localstack-extension-httpbin==0.2.0"
```

Then run `lstk start`, or `lstk restart` when the emulator is already running. A committed `.lstk/config.toml` gives every teammate and CI run the same Extensions.

Use package specs only: `name`, `name[extra]`, or `name==version`. Git URLs are not supported.

## Discover Extensions

Browse the [Extensions Library](https://app.localstack.cloud/extensions/library), or query the marketplace with the auth token as the password and an empty username:

```bash
curl -s -u ":$LOCALSTACK_AUTH_TOKEN" https://api.localstack.cloud/v1/extensions/marketplace \
  | jq '.[] | {name, version, author, summary}'
```

## Run an Extension: MailHog

With `localstack-extension-mailhog` in the profile above:

```bash
lstk start

lstk aws ses verify-email-identity --email-address sender@example.com
lstk aws ses send-email \
  --from sender@example.com \
  --destination ToAddresses=recipient@example.com \
  --message 'Subject={Data=Test},Body={Text={Data=Hello}}'

# Captured mail; either URL works
open http://mailhog.localhost.localstack.cloud:4566
open http://localhost:4566/mailhog/
```

MailHog configures the SES SMTP target automatically. Other Extensions document their own URLs and settings on their library page.

## Configure an Extension

Extensions read their settings from emulator environment variables. Put them in the same `[env.*]` profile, without a `LOCALSTACK_` prefix, and restart.

## Develop a custom Extension

Start from an existing Extension in [localstack/localstack-extensions](https://github.com/localstack/localstack-extensions); each one is a complete, buildable example of the Extension API. To ship one, publish the package to PyPI and add it to `EXTENSION_AUTO_INSTALL`.

## Diagnose a failing Extension

- **Extension not active**: confirm the `extensions` profile is listed in the container block's `env`, that `lstk config path` shows the file you edited, then run `lstk restart`.
- **Errors on startup**: run `lstk logs --verbose | grep -i extension` and read the stack trace.
- **Two Extensions interfering**: remove one from `EXTENSION_AUTO_INSTALL` to isolate the failure.
- **Version mismatch**: pin a version compatible with the emulator image `tag`.
