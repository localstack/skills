---
name: localstack-state
description: Manage LocalStack state with lstk snapshots and persistent volumes. Use when saving, loading, versioning, sharing, resetting, or reproducing emulator state locally, in Cloud Pods, or in S3.
---

# Manage LocalStack state

Use `lstk snapshot` for explicit checkpoints and `--persist` for automatic state retention. Cloud Pod (`pod:`) operations require a LocalStack plan that includes State Management and a valid authentication token. Local-file and S3 operations run through the emulator and do not require a platform token for the snapshot command.

## Save and load local snapshots

```bash
# Save all services to a generated .snapshot file
lstk snapshot save

# Save to a named file
lstk snapshot save ./baseline.snapshot

# Save selected services
lstk snapshot save ./payments.snapshot --services s3,sqs,lambda

# Load; starts the configured emulator when needed
lstk snapshot load ./baseline.snapshot
```

`lstk save` and `lstk load` are aliases, but prefer the explicit `lstk snapshot` form in documentation and automation.

Choose the merge strategy deliberately:

```bash
# Default: snapshot wins on overlapping service/account/region state
lstk snapshot load ./baseline.snapshot --merge=account-region-merge

# Replace all running state
lstk snapshot load ./baseline.snapshot --merge=overwrite

# Merge resources within each service
lstk snapshot load ./baseline.snapshot --merge=service-merge
```

Treat `--merge=overwrite` as destructive and obtain confirmation before running it.

## Work with Cloud Pods

Use the `pod:` prefix:

```bash
lstk snapshot save pod:team-baseline
lstk snapshot list
lstk snapshot show pod:team-baseline
lstk snapshot versions pod:team-baseline
lstk snapshot load pod:team-baseline
lstk snapshot load pod:team-baseline:3
```

Every save to an existing pod creates a new version. Preview a pod load without changing state:

```bash
lstk snapshot load pod:team-baseline --dry-run
```

Remove a pod only after explicit confirmation:

```bash
lstk snapshot remove pod:team-baseline
lstk --non-interactive snapshot remove pod:team-baseline --force
```

Removal still contacts a running emulator even though the snapshot is stored on the LocalStack platform.

## Store snapshots in S3

Supply credentials through environment variables, `AWS_PROFILE`, or `--profile`; never put credentials in the URL:

```bash
lstk snapshot save team-baseline s3://my-bucket/localstack
lstk snapshot list s3://my-bucket/localstack
lstk snapshot load team-baseline s3://my-bucket/localstack
```

S3 transfers are performed by the emulator and require one to be reachable.

## Auto-load a baseline

Set a Cloud Pod in the active AWS emulator config:

```toml
[[containers]]
type = "aws"
snapshot = "pod:team-baseline"
```

Override or skip it for one start:

```bash
lstk start --snapshot pod:another-baseline
lstk start --no-snapshot
```

## Persist state across restarts

```bash
lstk start --persist
lstk volume path
```

For a persistent default, attach an environment profile with `PERSISTENCE = "1"`. Configuring a volume only chooses where state is stored; it does not enable persistence by itself.

Treat the following as destructive and get confirmation first:

```bash
lstk reset
lstk volume clear
```

Use a snapshot before destructive experiments when rollback matters.
