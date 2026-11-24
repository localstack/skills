---
name: localstack-replicator
description: Copy resources from a real AWS account into LocalStack with AWS Replicator. Use when a local stack depends on shared AWS resources that already exist (VPCs, SSM parameters, IAM roles, ECR repositories, secrets) and the user wants them replicated locally instead of re-creating them.
---

# AWS Replicator

AWS Replicator reads a resource from a real AWS account and re-creates it inside the running emulator. Use it when your IaC references resources it does not own — a shared VPC, SSM parameters under a path, a pre-existing IAM role — so the stack can deploy locally without stubbing them out.

## Prerequisites

- A running AWS emulator (`lstk start`) — see the `localstack` skill
- A license that includes AWS Replicator
- **Real** AWS credentials for the source account, with read access to the resources you replicate

`lstk` has no replicator command. Drive the Replicator API on the emulator gateway with `curl`. The source credentials travel in the request body, so read them from your environment rather than pasting them inline, and keep them out of shell history and logs.

## Find what can be replicated

```bash
curl -s localhost:4566/_localstack/replicator/resources | jq
```

Each entry names a CloudFormation resource type, the identifier it expects, and the IAM permissions the source credentials need.

## Start a job

`POST /_localstack/replicator/jobs` with:

| Field | Value |
|-------|-------|
| `replication_type` | `SINGLE_RESOURCE` (one resource) or `BATCH` (e.g. every SSM parameter under a path) |
| `replication_job_config` | Either `{"resource_type", "resource_identifier"}` or `{"resource_arn"}` — not both. ARNs work for `SINGLE_RESOURCE` only. |
| `source_aws_config` | `aws_access_key_id`, `aws_secret_access_key`, optional `aws_session_token`, `region_name` |
| `target_aws_config` | Optional, to land the copy in a non-default LocalStack account or region: `{"aws_access_key_id": "<12-digit account id>", "aws_secret_access_key": "test", "region_name": "<region>"}`. LocalStack derives the account from the access key. Defaults to account `000000000000` and the source region. |

`resource_identifier` is the CloudControl identifier: a VPC ID (`vpc-…`), SSM parameter name, IAM role name, ECR repository name. For a `BATCH` SSM job it is a path prefix such as `/dev/`.

```bash
# Build the request with jq so credentials come from the environment
jq -n \
  --arg ak "$AWS_ACCESS_KEY_ID" --arg sk "$AWS_SECRET_ACCESS_KEY" \
  --arg st "${AWS_SESSION_TOKEN:-}" --arg rg "${AWS_DEFAULT_REGION:-us-east-1}" '
  { replication_type: "SINGLE_RESOURCE",
    replication_job_config: { resource_type: "AWS::EC2::VPC", resource_identifier: "vpc-0abc123" },
    source_aws_config: ({ aws_access_key_id: $ak, aws_secret_access_key: $sk, region_name: $rg }
                        + (if $st != "" then { aws_session_token: $st } else {} end)) }' |
curl -s -X POST localhost:4566/_localstack/replicator/jobs \
  -H 'Content-Type: application/json' -d @- | jq
```

For a batch of SSM parameters, swap in `replication_type: "BATCH"` and `replication_job_config: { resource_type: "AWS::SSM::Parameter", resource_identifier: "/dev/" }`.

## Track jobs

```bash
curl -s localhost:4566/_localstack/replicator/jobs | jq              # all jobs
curl -s localhost:4566/_localstack/replicator/jobs/$JOB_ID | jq      # one job: state, error_message, result
```

Poll until `state` is terminal. On failure, `error_message` usually names a missing source permission or an unsupported resource type.

## Verify

Confirm the copy exists locally, e.g. `lstk aws ec2 describe-vpcs --vpc-ids vpc-0abc123` or `lstk aws ssm get-parameters-by-path --path /dev/ --recursive`. Replicated resources live in emulator state like any other, so snapshot them with `lstk save` to skip replication next time — see the `localstack-state` skill.
