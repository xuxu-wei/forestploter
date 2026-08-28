"""把所有森林图视觉用例渲染成 PNG。"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from tests.visual_cases import (
    ARTIFACT_DIR,
    CASE_BUILDERS,
    CASE_DATA_FILES,
    CONFIGURED_TEST_FONT,
    artifact_name_for_case,
    build_case,
    load_case_data,
)


def render_cases(case_names: list[str], output_dir: Path, dpi: int) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for case_name in case_names:
        data = load_case_data(case_name)
        result = build_case(case_name, data)
        image_name = artifact_name_for_case(case_name)
        destination = result.save(output_dir / image_name, dpi=dpi)
        diagnostics = result.layout_diagnostics
        print(
            f"{CASE_DATA_FILES[case_name]} -> {image_name}: "
            f"records={len(data.frame)}, plot_rows={len(result.row_centers)}, "
            f"clipped={result.clipped_intervals}, "
            f"figure_width={diagnostics.final_figure_width:.2f} in, "
            f"series_gap={diagnostics.series_gap_used:.2f}, "
            f"header_overflow={diagnostics.header_overflow_count}, "
            f"output={destination}"
        )
        saved.append(destination)
        plt.close(result.figure)
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case",
        action="append",
        choices=tuple(CASE_BUILDERS),
        dest="cases",
        help="只渲染指定用例；可重复传入。默认渲染全部。",
    )
    parser.add_argument("--output-dir", type=Path, default=ARTIFACT_DIR)
    parser.add_argument("--dpi", type=int, default=180)
    args = parser.parse_args()
    selected = args.cases or list(CASE_BUILDERS)
    print(f"test_font={CONFIGURED_TEST_FONT or 'Matplotlib default'}")
    render_cases(selected, args.output_dir, args.dpi)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
