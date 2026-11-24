---
name: localstack-azure
description: Run the LocalStack Azure emulator and drive it with the Azure CLI. Use when users want to start LocalStack for Azure, run az commands locally (resource groups, storage, blobs, Bicep/ARM deployments), or set up lstk az.
---

# Azure Emulator

LocalStack emulates Azure services locally. `lstk az` runs your installed Azure CLI against it through an isolated profile, so your real Azure login is never used or changed.

## Prerequisites

- `lstk` and Docker — see the `localstack` skill
- A license that includes LocalStack for Azure
- The Azure CLI (`az`) on your `PATH`; `bicep` too if you deploy Bicep templates

## Start and set up

```bash
lstk start --type azure
lstk setup azure       # once: creates an isolated az config dir routed to the emulator
lstk status
```

`--type` is saved to `config.toml`; pass `--type aws` to switch back. `lstk setup azure` needs the emulator running, and leaves `~/.azure` untouched.

## Run az commands

Prefix any `az` command with `lstk`:

```bash
lstk az group create --name rg-demo --location westeurope
lstk az storage account create --name stdemo --resource-group rg-demo --location westeurope
lstk az storage container create --account-name stdemo --name data
lstk az storage blob upload --account-name stdemo --container-name data \
  --name sample.csv --file ./sample.csv

# ARM / Bicep deployments
lstk az deployment group create --resource-group rg-demo --template-file main.bicep
```

Azure CLI extensions you installed with `az extension add` are available.

## Gotchas

- **Anything `az` downloads from the internet fails**: Bicep registry modules (`br:` / `br/public:`, error BCP192), `--template-uri`, and parameter files given as URLs. Use local module and template files.
- **Operations with no `az` command**: use `lstk az rest` with a relative URL, e.g. `lstk az rest --url "/subscriptions/{subscriptionId}/resourcegroups?api-version=2021-04-01"`.
- **Endpoints and connection strings** must use the emulator's `*.localhost.localstack.cloud` names over https — that is what the emulator's certificate covers.
- **DNS**: if `azure.localhost.localstack.cloud` does not resolve to `127.0.0.1`, a resolver is filtering it; allow `localhost.localstack.cloud`, or run `lstk doctor network`.
- **Unsupported operation errors**: check the Azure emulator docs at https://docs.localstack.cloud/azure/ for coverage before reworking the command.
