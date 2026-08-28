"""Build and validate the English and Simplified Chinese documentation."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from babel.messages.pofile import read_po

DOCS_DIR = Path(__file__).resolve().parent
BUILD_DIR = DOCS_DIR / "_build"
LANGUAGES = ("en", "zh_CN")


def run_sphinx(builder: str, language: str, destination: Path) -> None:
    """Run one fresh, warning-as-error Sphinx build."""

    resolved_destination = destination.resolve()
    resolved_build_dir = BUILD_DIR.resolve()
    if (
        resolved_destination == resolved_build_dir
        or resolved_build_dir not in resolved_destination.parents
    ):
        raise ValueError(f"Refusing to clean a non-build destination: {destination}")
    if resolved_destination.exists():
        shutil.rmtree(resolved_destination)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            builder,
            "-E",
            "-W",
            "--keep-going",
            "-D",
            f"language={language}",
            str(DOCS_DIR),
            str(destination),
        ],
        check=True,
    )


def catalog_path() -> Path:
    return DOCS_DIR / "locale" / "zh_CN" / "LC_MESSAGES" / "forestploter.po"


def verify_catalog() -> None:
    """Reject missing and fuzzy translations before a Chinese build."""

    path = catalog_path()
    if not path.exists():
        raise FileNotFoundError(f"Chinese catalog does not exist: {path}")
    with path.open("r", encoding="utf-8") as handle:
        catalog = read_po(handle, locale="zh_CN")
    empty = []
    fuzzy = []
    for message in catalog:
        if not message.id:
            continue
        if "fuzzy" in message.flags:
            fuzzy.append(message.id)
        translated = message.string
        if isinstance(translated, tuple):
            if any(not item for item in translated):
                empty.append(message.id)
        elif not translated:
            empty.append(message.id)
    if empty or fuzzy:
        raise RuntimeError(
            "Chinese catalog is incomplete: "
            f"empty={len(empty)}, fuzzy={len(fuzzy)}. "
            f"First empty={empty[:1]!r}, first fuzzy={fuzzy[:1]!r}"
        )


def write_root_redirect() -> None:
    """Write a file://-safe root page that redirects to English."""

    destination = BUILD_DIR / "html" / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url=en/index.html">
  <title>forestploter documentation</title>
</head>
<body>
  <p><a href="en/index.html">Open the English documentation</a></p>
</body>
</html>
""",
        encoding="utf-8",
    )


def build_html() -> None:
    verify_catalog()
    html_root = (BUILD_DIR / "html").resolve()
    resolved_build_dir = BUILD_DIR.resolve()
    if html_root.parent != resolved_build_dir:
        raise ValueError(f"Refusing to clean an unexpected HTML root: {html_root}")
    if html_root.exists():
        shutil.rmtree(html_root)
    for language in LANGUAGES:
        run_sphinx("html", language, BUILD_DIR / "html" / language)
    write_root_redirect()


def build_auxiliary(builder: str) -> None:
    verify_catalog()
    for language in LANGUAGES:
        run_sphinx(builder, language, BUILD_DIR / builder / language)


def update_gettext() -> None:
    run_sphinx("gettext", "en", BUILD_DIR / "gettext")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx_intl",
            "update",
            "-p",
            str(BUILD_DIR / "gettext"),
            "-d",
            str(DOCS_DIR / "locale"),
            "-l",
            "zh_CN",
        ],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        nargs="?",
        default="html",
        choices=("html", "doctest", "linkcheck", "gettext", "verify", "all"),
    )
    target = parser.parse_args().target
    if target == "html":
        build_html()
    elif target in {"doctest", "linkcheck"}:
        build_auxiliary(target)
    elif target == "gettext":
        update_gettext()
    elif target == "verify":
        verify_catalog()
    else:
        build_html()
        build_auxiliary("doctest")
        build_auxiliary("linkcheck")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
