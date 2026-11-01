# schemas

JSON Schemas (draft 2020-12) for the YAML frontmatter of every Forestrie
document type. The layout, naming and lifecycle they encode are specified
in [docs-layout](https://github.com/forestrie/forestrie-agents/blob/main/workflow/rules/docs-layout/SKILL.md);
the decision is
[devdocs ADR-0071](https://github.com/forestrie/devdocs/blob/main/adr/adr-0071-documentation-system-v2/README.md).

| Schema | Documents |
|--------|-----------|
| [adr](./adr.schema.json) | `adr/adr-NNNN-<slug>.md` |
| [arc](./arc.schema.json) | `arc/arc-NNNN-<slug>.md` |
| [named-doc](./named-doc.schema.json) | living documents: `architecture.md`, area docs, runbooks, spec, briefs |
| [plan](./plan.schema.json) | forestrie/work `plans/plan-YYMM-NN-<slug>.md` |
| [status](./status.schema.json) | forestrie/work `status/status-YYMM-NN-<slug>.md` |
| [rules](./rules.schema.json) | `protocol/rules/platform.md`, repo `docs/rules.md` |
| [common](./common.schema.json) | shared field shapes; not used directly |

Load YAML with dates kept as strings (no timestamp resolution); the
schemas type dates as `YYYY-MM-DD` strings.

## What a schema cannot check

[dox](https://github.com/robinbryce/dox) checks these, driven by
[dox.toml](../dox.toml):

- `id` equals the filename stem, or the directory name for a directory
  document;
- ids are unique within a namespace, against `origin` and open PRs;
- link fields and markdown links resolve;
- every `supersedes` entry has a matching `superseded-by`;
- retired documents live under `retired/`, closed plans under `archive/`.

## Check

```bash
# self-test: examples/valid/ must pass, examples/invalid/ must fail
uv run --no-project --with 'jsonschema>=4.18' --with pyyaml schemas/check.py

# validate documents of one type
uv run --no-project --with 'jsonschema>=4.18' --with pyyaml schemas/check.py \
  --type adr ../devdocs/adr/adr-0071-*/README.md

# everything, the way CI does
dox lint
```

Change a schema and its examples together. A new field earns a place once
two repos use it; until then use an `x-<name>` extension field.
