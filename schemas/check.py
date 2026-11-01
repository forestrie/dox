"""Validate Forestrie doc frontmatter against the schemas in this directory.

Run with uv, which supplies the two dependencies:

    uv run --with 'jsonschema>=4.18' --with pyyaml schemas/check.py
        Self-test: every file in examples/valid/ must pass and every file in
        examples/invalid/ must fail. The schema type is the filename prefix
        before "--" (adr--accepted.md -> adr.schema.json).

    uv run --with 'jsonschema>=4.18' --with pyyaml schemas/check.py \\
        --type plan path/to/plan-2611-01-x.md [...]
        Validate real documents of one type; prints each error.

This is the schema self-test. dox (https://github.com/robinbryce/dox) owns
linting documents, including the checks a schema cannot express: id equals
filename stem, ids unique per namespace, links resolve.
"""

import argparse
import json
import pathlib
import sys

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

HERE = pathlib.Path(__file__).resolve().parent
TYPES = ("adr", "arc", "named-doc", "plan", "status", "rules")


class StringDateLoader(yaml.SafeLoader):
    """SafeLoader that keeps dates as strings, matching the schema."""


StringDateLoader.yaml_implicit_resolvers = {
    k: [(tag, rx) for tag, rx in v if tag != "tag:yaml.org,2002:timestamp"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_registry():
    resources = []
    for path in HERE.glob("*.schema.json"):
        schema = json.loads(path.read_text())
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


def validator_for(kind, registry):
    schema = json.loads((HERE / f"{kind}.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(
        schema, registry=registry, format_checker=FormatChecker()
    )


def frontmatter(path):
    try:
        text = path.read_text()
    except OSError as e:
        raise ValueError(f"cannot read: {e.strerror}") from e
    if not text.startswith("---\n"):
        raise ValueError("no YAML frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    try:
        data = yaml.load(text[4:end], Loader=StringDateLoader)
    except yaml.YAMLError as e:
        raise ValueError(f"invalid YAML: {e}") from e
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data


def errors(validator, path):
    try:
        data = frontmatter(path)
    except ValueError as e:
        return [str(e)]
    found = list(validator.iter_errors(data))
    # A failing field fails the whole allOf branch that declares it, and
    # draft 2020-12 then drops that branch's annotations, so
    # unevaluatedProperties also reports every valid sibling field. Show
    # that error only when it is the sole problem.
    real = [e for e in found if e.validator != "unevaluatedProperties"]
    return [
        f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
        for e in (real or found)
    ]


def self_test(registry):
    validators = {k: validator_for(k, registry) for k in TYPES}
    failures = 0
    for expect_valid in (True, False):
        folder = HERE / "examples" / ("valid" if expect_valid else "invalid")
        for path in sorted(folder.glob("*.md")):
            kind = path.name.split("--", 1)[0]
            errs = errors(validators[kind], path)
            ok = (not errs) == expect_valid
            failures += not ok
            mark = "ok  " if ok else "FAIL"
            detail = "" if ok or not errs else f"  {errs}"
            print(f"{mark} {folder.name}/{path.name}{detail}")
    print(f"{failures} failure(s)")
    return 1 if failures else 0


def check_files(kind, paths, registry):
    validator = validator_for(kind, registry)
    bad = 0
    for p in paths:
        errs = errors(validator, pathlib.Path(p))
        bad += bool(errs)
        for e in errs:
            print(f"{p}: {e}")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--type", choices=TYPES)
    ap.add_argument("paths", nargs="*")
    args = ap.parse_args()
    registry = load_registry()
    if not args.paths:
        return self_test(registry)
    if not args.type:
        ap.error("--type is required when paths are given")
    return check_files(args.type, args.paths, registry)


if __name__ == "__main__":
    sys.exit(main())
