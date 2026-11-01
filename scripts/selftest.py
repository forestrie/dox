"""Self-test this schema repo with dox before tagging it.

    DOX_SCHEMA_REPO=forestrie/dox DOX_SCHEMA_PATH=. python3 scripts/selftest.py

1. schemas/check.py: examples/valid pass, examples/invalid fail.
2. dox new scaffolds every type from templates/ into throwaway canon and
   work repositories, and dox lint passes on the result.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CANON = ["adr", "arc", "named-doc", "rules"]
WORK = ["plan", "status"]


def run(*args, cwd=None):
    print("+", " ".join(map(str, args)), flush=True)
    r = subprocess.run(list(map(str, args)), cwd=cwd)
    if r.returncode:
        sys.exit(r.returncode)


def repo(base: Path, name: str, namespace: str, root: str, types: list[str]) -> Path:
    path = base / name
    (path / root).mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    (path / ".dox.toml").write_text(
        f'schema_ref = "local"\nnamespace = "{namespace}"\nroot = "{root}"\n'
        f"types = {types!r}\n".replace("'", '"'))
    return path


def main():
    os.environ.setdefault("DOX_SCHEMA_REPO", "forestrie/dox")
    os.environ["DOX_SCHEMA_PATH"] = str(HERE)
    run(sys.executable, HERE / "schemas" / "check.py")
    with tempfile.TemporaryDirectory() as t:
        base = Path(t)
        canon = repo(base, "canon", "canopy", "docs", CANON)
        for d in ("adr", "arc"):
            (canon / "docs" / d).mkdir()
        for typ, slug in (("adr", "first-decision"), ("arc", "first-design"),
                          ("rules", "rules"), ("named-doc", "architecture")):
            run("dox", "new", typ, slug, "--offline", "-C", canon)
        run("dox", "index", "-C", canon)
        run("dox", "lint", "-C", canon)
        work = repo(base, "work", "work", ".", WORK)
        run("dox", "new", "plan", "a-plan", "--offline", "-C", work)
        run("dox", "new", "plan", "a-dir-plan", "--dir", "--offline", "-C", work)
        run("dox", "new", "status", "a-checkpoint", "--offline", "-C", work)
        run("dox", "lint", "-C", work)
    print("selftest OK")


if __name__ == "__main__":
    main()
