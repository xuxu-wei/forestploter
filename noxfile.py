"""Cross-platform development and release checks."""

from __future__ import annotations

from pathlib import Path

import nox

nox.options.sessions = ["lint", "typecheck", "tests", "docs", "package"]
nox.options.reuse_existing_virtualenvs = True


@nox.session
def lint(session: nox.Session) -> None:
    """Run source and repository lint checks."""

    session.install("ruff>=0.9")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


@nox.session
def typecheck(session: nox.Session) -> None:
    """Check the typed runtime package."""

    session.install("-e", ".[dev]")
    session.run("mypy", "src/forestploter")


@nox.session
def tests(session: nox.Session) -> None:
    """Run the complete automated test suite."""

    session.install("-e", ".[test]")
    session.env["MPLBACKEND"] = "Agg"
    session.run("python", "-m", "pytest", "-q")


@nox.session
def docs(session: nox.Session) -> None:
    """Build both documentation languages and all documentation checks."""

    session.install("-e", ".[docs]")
    session.run("python", "docs/build_bilingual.py", "all")


@nox.session(name="package")
def package_session(session: nox.Session) -> None:
    """Build and inspect the source distribution and wheel."""

    session.install("build>=1.2", "check-wheel-contents>=0.6", "twine>=6")
    dist = Path("dist")
    if dist.exists():
        for artifact in dist.iterdir():
            if artifact.is_file():
                artifact.unlink()
    session.run("python", "-m", "build")
    artifacts = sorted(str(artifact) for artifact in dist.iterdir() if artifact.is_file())
    session.run("python", "-m", "twine", "check", "--strict", *artifacts)
    session.run("check-wheel-contents", "dist")
