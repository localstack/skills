---
name: localstack-infra-test
description: Deploy an IaC project to LocalStack, validate every declared resource against live state, then write and run integration tests. Use when users want to test or validate their infrastructure, check that a Terraform, CDK, SAM, or CloudFormation stack actually works, or generate integration tests for it.
---

# Infrastructure Testing

Deploy the IaC, prove each declared resource exists with the configuration the code declares, then write and run integration tests until they pass or you can explain why they cannot.

Inputs to settle first (ask only for what you cannot infer):

- **IaC path** (required) and **framework** — `auto` unless stated
- **Test language / framework** — default TypeScript + Jest; Python → pytest, Java → JUnit, Go → `go test`
- **Mode** — `full` (default) or `validate-only`
- **Focus** — services or a workflow to inspect first

## Phase 0: Preflight

1. `lstk status`. Start the emulator if it is not running; restart the existing one for a clean slate — run one emulator, never a second.
2. Detect the framework when `auto`: `lstk deploy detect --dir <path> --unsupported` reports the tool **and** any resources LocalStack or your license does not support. Otherwise: `cdk.json` → CDK, `*.tf` → Terraform, `template.yaml` + `samconfig.toml` → SAM, other templates → CloudFormation.
3. Read the IaC and build the **resource graph**: logical ID, resource type, key configuration, and edges between resources.

Done when you have reported the framework, resource count, unsupported resources, and the graph. Ask before going further if the framework is ambiguous or the stack declares more than 50 resources.

## Phase 1: Deploy and validate

1. Deploy — see the `localstack-deploy` skill. `lstk inspect enable` first so the deploy's API calls are traced (`localstack-app-inspector` skill).
2. If the deploy fails, pull the logs (`localstack-logs` skill), quote the real error, and stop with status `deploy-blocked`.
3. Probe **every** declared resource with `lstk aws` and compare live configuration to the declaration:

| Resource | Probe | Compare |
|----------|-------|---------|
| S3 bucket | `s3api get-bucket-versioning`, `get-bucket-policy`, `get-bucket-encryption` | versioning, policy, encryption |
| DynamoDB table | `dynamodb describe-table` | billing mode, key schema, GSIs, streams |
| Lambda | `lambda get-function-configuration` | runtime, memory, timeout, env vars, role |
| IAM role | `iam get-role`, `list-attached-role-policies` | trust policy, attachments |
| SQS queue | `sqs get-queue-attributes --attribute-names All` | DLQ, visibility timeout, FIFO |
| EventBridge rule | `events describe-rule`, `list-targets-by-rule` | pattern, targets |
| VPC / SG | `ec2 describe-subnets`, `describe-security-groups` | CIDRs, rules |

4. A resource that exists but whose create call failed in App Inspector traces is flagged for review.

Done when every resource has a row:

| Resource | Type | Status | Evidence | Remediation |
|----------|------|--------|----------|-------------|

Status: ✅ **ready** (exists, config matches) · ⚠️ **partial** (exists, a declared property differs) · ❌ **failed** (missing, or its create call errored) · ⛔ **unsupported** (service or feature unsupported on this tier). Stop here in `validate-only` mode.

## Phase 2: Integration tests

1. Plan tests from the resource graph: single-resource CRUD, each cross-resource edge, and expected failure modes.
2. Write deterministic tests under `tests/integration/`. Bake in: endpoint `http://localhost.localstack.cloud:4566`, credentials `test`/`test`, region from the IaC or `us-east-1`, unique resource names per run, and cleanup.
3. Run them. For each failure, note the test's start and end time, pull logs and App Inspector traces for that window, then classify:
   - **Test wrong** → fix the test
   - **IaC drift** → fix the IaC, redeploy, update the readiness table
   - **Unsupported** → skip with the reason; do not retry
   - **Transient** → retry
4. Retry each test at most 3 times; after the third failure, record it as failed with the final diagnosis and move on.

## Final report

- The Phase 1 readiness table
- Per test: status, attempts, last error, remediation
- Headline counts: resources ready / partial / failed / unsupported; tests written / passed / failed / skipped

## Ground rules

- Report real failures as they are. When the IaC is wrong, say so and propose the smallest fix.
- Leave IAM enforcement off unless the user asks; it changes failure modes mid-run. If IAM is the focus, ask once before enabling it.
- Load Cloud Pods or state files only when the user supplies them.
- A focus request to skip a check (e.g. "don't validate IAM") changes priority, not coverage: run the check and note the request in the summary.
