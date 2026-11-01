# forestrie/dox

Forestrie's schema repo for [dox](https://github.com/robinbryce/dox), the
docs checker. It turns the Forestrie docs layout
([devdocs ADR-0071](https://github.com/forestrie/devdocs/blob/main/adr/adr-0071-documentation-system-v2/README.md),
and the `docs-layout` rule in
[forestrie-agents](https://github.com/forestrie/forestrie-agents/blob/main/workflow/rules/docs-layout/SKILL.md))
into something a machine checks.

| Path | What |
|------|------|
| [dox.toml](dox.toml) | The preset: document types, id shapes, directories, status values, link meanings, namespaces, check severities ([contract 1](https://github.com/robinbryce/dox/blob/main/docs/contract.md)) |
| [schemas/](schemas/README.md) | JSON Schemas (draft 2020-12) for each type's frontmatter, with valid and invalid examples |
| [templates/](templates) | Scaffolds for `dox new` |
| [scripts/selftest.py](scripts/selftest.py) | Runs the schema examples and scaffolds and lints every type |

## Using it

A Forestrie repository commits a `.dox.toml` that pins a tag of this repo:

```toml
schema_ref = "v1.0.0"
namespace  = "canopy"
root       = "docs"
types      = ["adr", "arc", "named-doc", "rules"]
baseline   = ".dox-baseline.json"
```

Locally, `export DOX_SCHEMA_REPO=forestrie/dox` and run `dox lint`. In CI:

```yaml
- uses: robinbryce/dox@v0.1.0
  with:
    schema-repo: forestrie/dox
```

## Changing it

Change a schema, its examples and `dox.toml` together, run the self-test
against your checkout, and tag a new version. A change reaches a
repository only when that repository bumps `schema_ref`.

```bash
uv tool install git+https://github.com/robinbryce/dox@v0.1.0
uv run --no-project --with 'jsonschema>=4.18' --with pyyaml python scripts/selftest.py
```

Versions follow semver: MAJOR when a document valid before becomes
invalid, MINOR for a new optional field or type, PATCH otherwise.
