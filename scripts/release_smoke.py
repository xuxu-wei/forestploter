"""Verify an installed forestploter distribution with real XLSX and exports."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt

import forestploter
from forestploter import ForestColumn, forest, read_forest_data


def main() -> int:
    """Read one workbook and export PNG and SVG using an installed package."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    source = args.source.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    df = read_forest_data(source)
    result = forest(
        df,
        columns=(
            ForestColumn("label", "Outcome / study", "text", 2.8),
            ForestColumn("n", "N", "numeric", 0.7, "right"),
            ForestColumn("ci", "Treatment effect", "ci", 3.3, "center"),
            ForestColumn(
                "effect_display",
                "Mean difference [95% CI]",
                "numeric",
                2.0,
                "right",
            ),
        ),
        ref_line=0.0,
        xlim=(-1.0, 1.0),
        ticks_at=(-1.0, -0.5, 0.0, 0.5, 1.0),
    )
    try:
        png = result.save(output_dir / "release-smoke.png", dpi=120)
        svg = result.save(output_dir / "release-smoke.svg")
        if not png.is_file() or not svg.is_file():
            raise RuntimeError("Release smoke test did not create both outputs.")
        print(f"forestploter={forestploter.__version__}")
        print(f"png={png}")
        print(f"svg={svg}")
    finally:
        plt.close(result.figure)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
