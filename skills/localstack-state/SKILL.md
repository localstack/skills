---
name: localstack-state
description: Manage LocalStack state with lstk snapshots and persistent volumes. Use when saving, loading, exporting, importing, versioning, sharing, resetting, or reproducing emulator state locally, in Cloud Pods, or in S3.
---

# Manage LocalStack state

Use `lstk snapshot` for explicit checkpoints and `--persist` for automatic state retention. Cloud Pod (`pod:`) operations require a LocalStack plan that includes State Management and a valid authentication token. Local-file and S3 refs carry no platform token, but the snapshot feature is itself plan-gated, so an entitled account is required for every backend.

## Save and load local snapshots

```bash
# Save all services to a generated .snapshot file
lstk snapshot save

# Save to a named file
lstk snapshot save ./baseline.snapshot

# Save selected services
lstk snapshot save ./payments.snapshot --services s3,sqs,lambda

# Load a snapshot
lstk snapshot load ./baseline.snapshot
```

An omitted destination writes `./snapshot-<timestamp>-<hex>.snapshot` in the working directory. A destination without the `.snapshot` extension gets one appended, so `lstk snapshot save /tmp/my-state` writes `/tmp/my-state.snapshot`. On load, a bare name resolves against the working directory with or without the extension:

```bash
lstk snapshot load baseline    # loads ./baseline or ./baseline.snapshot
```

`lstk save` and `lstk load` are aliases, but prefer the explicit `lstk snapshot` form in documentation and automation. `snapshot save` reads the state of a running emulator and fails when none is running; `snapshot load` starts the configured emulator first when needed.

Choose the merge strategy deliberately:

```bash
# Default: snapshot wins on overlapping service/account/region state
lstk snapshot load ./baseline.snapshot --merge=account-region-merge

# Replace all running state
lstk snapshot load ./baseline.snapshot --merge=overwrite

# Merge resources within each service
lstk snapshot load ./baseline.snapshot --merge=service-merge
```

Set `LSTK_MERGE_STRATEGY` instead of passing `--merge` when one strategy should apply to every load in an environment or CI job.

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

`snapshot list` returns only snapshots created by the authenticated user. Add `--all` for every snapshot in the organisation:

```bash
lstk snapshot list --all
```

Every save to an existing pod creates a new version.

`--services` (short form `-s`) applies to every destination, not only local files:

```bash
lstk snapshot save pod:team-baseline --services s3,sqs,lambda
```

Preview a pod load without changing state:

```bash
lstk snapshot load pod:team-baseline --dry-run
```

`snapshot show`, `snapshot versions`, `snapshot remove`, and `--dry-run` accept only `pod:` refs. Local files and `s3://` remotes have no version history and cannot be inspected, previewed, or removed through these commands. Removal cannot be undone.

Remove a pod only after explicit confirmation:

```bash
lstk snapshot remove pod:team-baseline
lstk --non-interactive snapshot remove pod:team-baseline --force
```

Removal still contacts a running emulator even though the snapshot is stored on the LocalStack platform.

## Store snapshots in S3

Credentials are read from `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`, from `--profile`, or from the profile named by `AWS_PROFILE`; never put credentials in the URL:

```bash
lstk snapshot save team-baseline s3://my-bucket/localstack --profile my-aws-profile
```

Save, list, and load against the bucket:

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

`--persist` sets `LOCALSTACK_PERSISTENCE=1` on the emulator and writes state into the volume directory, which is reloaded on the next start. The flag applies per invocation, so pass it to `restart` as well:

```bash
lstk restart --persist
```

For a persistent default, attach an environment profile with `PERSISTENCE = "1"`. Configuring a volume only chooses where state is stored; it does not enable persistence by itself.

Treat the following as destructive and get confirmation first:

```bash
lstk reset
lstk volume clear
```

`lstk reset` discards the emulator's in-memory resources and leaves it running. `lstk volume clear` wipes the on-disk volume — certificates, downloaded tools, and persistence data — and expects the emulator to be stopped first. Both accept `--force` to skip the confirmation prompt in automation.

Use a snapshot before destructive experiments when rollback matters.
