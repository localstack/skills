---
name: localstack-state
description: Manage LocalStack state and snapshots with lstk. Use when users want to save, load, export, or import LocalStack state, work with Cloud Pods or S3-backed snapshots, or enable persistence across restarts.
---

# State Management

Save, load, and manage LocalStack state for reproducible development environments and state snapshots, using `lstk snapshot` and its `lstk save` / `lstk load` aliases.

## Capabilities

- Save and restore state as local snapshot files
- Save and load state to/from Cloud Pods (LocalStack platform storage)
- Save and load state to/from your own S3 bucket
- Share state across teams via Cloud Pods
- Auto-load a snapshot every time the emulator starts
- Enable persistent state across container restarts

## Prerequisites

- `lstk` installed and authenticated (`lstk login`, or `LOCALSTACK_AUTH_TOKEN` in CI) — see the `localstack` skill
- A running emulator for `save` (`lstk load` will start one for you if needed)

`lstk save` / `lstk load` replace the legacy `localstack state export/import` and `localstack pod save/load` commands with a single snapshot interface. The destination REF decides where the state goes.

## Snapshot References (REF)

| REF form | Destination |
|----------|-------------|
| *(omitted)* | Auto-named local file `./snapshot-<timestamp>-<hex>.snapshot` |
| `./my-snapshot.snapshot` | Explicit local path |
| `pod:my-baseline` | Cloud Pod on the LocalStack platform |
| `pod:my-baseline:3` | Version 3 of that Cloud Pod |
| `my-pod s3://my-bucket/prefix` | Your own S3 bucket |

## Local Snapshots

### Save

```bash
# Save to an auto-named file in the current directory
lstk save

# Save to a specific path (the .snapshot extension is added if omitted)
lstk save ./my-snapshot.snapshot
lstk save /tmp/my-state

# Limit the snapshot to a subset of services
lstk save --services s3,lambda
```

### Load

```bash
# Loads ./my-baseline or ./my-baseline.snapshot
lstk load my-baseline

# Load from an explicit path
lstk load ./checkpoint.snapshot
```

### Use Cases for Local Snapshots

- **Backup/restore**: Save state before destructive operations
- **CI/CD pipelines**: Commit snapshot files to version control for reproducible tests
- **Offline workflows**: Work with snapshot files without cloud connectivity
- **Quick snapshots**: Fast local save/restore during development

## Cloud Pods

Cloud Pods store state on the LocalStack platform, enabling team collaboration and remote state management. They require authentication (`lstk login` or `LOCALSTACK_AUTH_TOKEN`).

### Save to a Cloud Pod

```bash
lstk save pod:my-baseline

# Only part of the state
lstk save pod:my-baseline --services s3,lambda
```

Every save to an existing pod name creates a new version.

### Load from a Cloud Pod

```bash
lstk load pod:my-baseline

# A specific version
lstk load pod:my-baseline:3

# Preview the changes without applying them (Cloud Pod refs only)
lstk load pod:my-baseline --dry-run
```

### List, Inspect, and Remove

```bash
# Your Cloud Pods
lstk snapshot list

# Everything in your organisation
lstk snapshot list --all

# Metadata: created date, size, LocalStack version, per-service resource counts
lstk snapshot show pod:my-baseline
lstk snapshot show pod:my-baseline:3

# Version history
lstk snapshot versions pod:my-baseline

# Delete (cloud snapshots only, cannot be undone)
lstk snapshot remove pod:my-baseline
lstk snapshot remove pod:my-baseline --force
```

### Use Cases for Cloud Pods

- **Team collaboration**: Share consistent development environments across team members
- **Demo environments**: Prepare and share demo-ready states
- **Cross-machine development**: Access the same state from different machines

## S3-Backed Snapshots

Store snapshots in a bucket you own. Credentials are read from `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`, from `--profile`, or from the profile named by `AWS_PROFILE` — never put credentials in the URL.

```bash
lstk save my-pod s3://my-bucket/prefix
lstk save my-pod s3://my-bucket/prefix --profile my-aws-profile

lstk load my-pod s3://my-bucket/prefix

lstk snapshot list s3://my-bucket/prefix
```

## Merge Strategies

`lstk load` controls how snapshot state combines with state already in the emulator:

| Strategy | Behavior |
|----------|----------|
| `account-region-merge` *(default)* | Snapshot wins on overlapping (service, account, region) |
| `overwrite` | Wipe running state, then load |
| `service-merge` | Snapshot wins per resource; non-overlapping resources are combined |

```bash
lstk load pod:my-baseline --merge=overwrite
```

You can also set `LSTK_MERGE_STRATEGY` instead of passing the flag.

## Auto-Loading a Snapshot on Start

For the AWS emulator, set the `snapshot` field on the container block so a snapshot loads on every start:

```toml
[[containers]]
type     = "aws"
snapshot = "pod:my-baseline"
```

Override or skip it for a single run:

```bash
lstk start --snapshot pod:other-baseline
lstk start --no-snapshot
```

## Local Persistence

For automatic persistence across restarts without explicit save/load:

```bash
lstk start --persist
lstk restart --persist
```

`--persist` injects `LOCALSTACK_PERSISTENCE=1` and writes state to the mounted volume, which is reloaded on the next start. Find that directory with `lstk volume path`; wipe it with `lstk volume clear`.

You can also set `PERSISTENCE = "1"` in an `[env.*]` profile in `config.toml` to make it the default for every run.

## Clearing State

```bash
# Discard in-memory resources, keep the emulator running
lstk reset

# Wipe the on-disk volume (stop the emulator first)
lstk volume clear
```

## Comparison

| Feature | Local snapshot files | Cloud Pods (`pod:`) | Your S3 bucket (`s3://`) |
|---------|----------------------|---------------------|--------------------------|
| Storage | Local files | LocalStack platform | Your AWS account |
| Extra auth | None beyond `lstk` | LocalStack auth token | AWS credentials |
| Team sharing | Manual file sharing | Built-in | Via bucket permissions |
| Versioning | Manual | Built-in (`snapshot versions`) | Manual |
| Offline use | Yes | No | No |

Note that `lstk` itself always requires a LocalStack account and license, regardless of which snapshot backend you use.

## Best Practices

- Use local snapshot files for development checkpoints and CI/CD pipelines
- Use Cloud Pods for team collaboration and shared environments
- Use descriptive names that indicate the state contents
- Use `--services` to keep snapshots small when you only care about part of the stack
- Use `--dry-run` before loading an unfamiliar Cloud Pod into a populated emulator
- Use `lstk start --persist` for simple state retention across restarts
