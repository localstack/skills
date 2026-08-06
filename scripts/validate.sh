#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
plugin_schema="https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
check_jsonschema_version="0.37.4"
skills_ref_revision="217be548739f21d6008915c29aefe320ea1a90af"
skills_ref_source="git+https://github.com/agentskills/agentskills.git@${skills_ref_revision}#subdirectory=skills-ref"

if ! command -v uvx >/dev/null 2>&1; then
  echo "uvx is required; install uv from https://docs.astral.sh/uv/" >&2
  exit 1
fi

echo "Validating plugin.json"
uvx --from "check-jsonschema==${check_jsonschema_version}" check-jsonschema \
  --schemafile "$plugin_schema" \
  "$repo_root/plugin.json"

skill_count=0
for skill_dir in "$repo_root"/skills/*; do
  [[ -d "$skill_dir" ]] || continue
  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    echo "missing SKILL.md in $skill_dir" >&2
    exit 1
  fi

  echo "Validating ${skill_dir#"$repo_root/"}"
  uvx --from "$skills_ref_source" skills-ref validate "$skill_dir"
  ((skill_count += 1))
done

if (( skill_count == 0 )); then
  echo "no skills found under $repo_root/skills" >&2
  exit 1
fi

echo "Validated plugin.json and $skill_count skills"
