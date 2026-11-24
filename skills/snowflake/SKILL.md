---
name: localstack-snowflake
description: Run the LocalStack Snowflake emulator and execute SQL against it. Use when users want to start the Snowflake emulator, connect the Snowflake CLI (snow), a driver, or dbt to it, or run Snowflake queries, DDL, or .sql files locally.
---

# Snowflake Emulator

LocalStack emulates Snowflake locally so you can run SQL, migrations, and tests without a Snowflake account.

## Prerequisites

- `lstk` and Docker — see the `localstack` skill
- A license that includes the Snowflake emulator
- The Snowflake CLI (`snow`) for the examples below: `pip install snowflake-cli` or `brew install snowflake-cli`

## Start

```bash
lstk start --type snowflake
lstk status
```

`--type` is saved to `config.toml`, so later `lstk start` runs start Snowflake again; pass `--type aws` to switch back. Snowflake-specific config uses the `SF_*` / `SNOWFLAKE_*` variables; set them in an `[env.*]` profile on the Snowflake container block in `config.toml`:

```toml
[[containers]]
type = "snowflake"
env  = ["sf-debug"]

[env.sf-debug]
SF_LOG = "trace"
```

## Connect

The emulator answers on `snowflake.localhost.localstack.cloud` at the gateway port (`4566`). Any credentials are accepted; `test` everywhere is the convention.

Create a `snow` connection once:

```bash
snow connection add --connection-name localstack \
  --user test --password test --account test \
  --role test --warehouse test --database test --schema test \
  --host snowflake.localhost.localstack.cloud --port 4566 \
  --no-interactive

snow connection test --connection localstack
```

Drivers and dbt use the same values: host `snowflake.localhost.localstack.cloud`, port `4566`, account/user/password `test`.

If `snowflake.localhost.localstack.cloud` does not resolve to `127.0.0.1`, your DNS (often a corporate resolver or router with rebind protection) is filtering it — allow `localhost.localstack.cloud` there, or run `lstk doctor network`.

## Run SQL

```bash
snow sql --connection localstack --query "SHOW DATABASES"
snow sql --connection localstack -f ./schema.sql

# Per-query context
snow sql --connection localstack \
  --dbname analytics --schemaname public --warehouse test --rolename test \
  --query "SELECT COUNT(*) FROM events"
```

DDL, DML, `SHOW`, and `DESCRIBE` all work. When a statement fails with an unsupported-feature error, check the Snowflake emulator docs at https://docs.localstack.cloud/snowflake/ before rewriting the query.

## State

Snowflake state is reset when the emulator stops unless you start it with `--persist`. `lstk reset` clears it while running.
