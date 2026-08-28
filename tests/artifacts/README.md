# 视觉测试图片索引

每张 PNG 与同编号、同主文件名的 XLSX 主数据及 CSV 伴随数据一一对应。

| XLSX 主数据 | CSV 伴随数据 | 图片 |
|---|---|---|
| [01_single_series.xlsx](../data/01_single_series.xlsx) | [01_single_series.csv](../data/01_single_series.csv) | [01_single_series.png](01_single_series.png) |
| [02_multi_series.xlsx](../data/02_multi_series.xlsx) | [02_multi_series.csv](../data/02_multi_series.csv) | [02_multi_series.png](02_multi_series.png) |
| [03_dual_ci_columns.xlsx](../data/03_dual_ci_columns.xlsx) | [03_dual_ci_columns.csv](../data/03_dual_ci_columns.csv) | [03_dual_ci_columns.png](03_dual_ci_columns.png) |
| [04_clipping_stress.xlsx](../data/04_clipping_stress.xlsx) | [04_clipping_stress.csv](../data/04_clipping_stress.csv) | [04_clipping_stress.png](04_clipping_stress.png) |
| [05_long_layout.xlsx](../data/05_long_layout.xlsx) | [05_long_layout.csv](../data/05_long_layout.csv) | [05_long_layout.png](05_long_layout.png) |
| [06_auto_scale_mixed_effects.xlsx](../data/06_auto_scale_mixed_effects.xlsx) | [06_auto_scale_mixed_effects.csv](../data/06_auto_scale_mixed_effects.csv) | [06_auto_scale_mixed_effects.png](06_auto_scale_mixed_effects.png) |
| [07_four_series_dense.xlsx](../data/07_four_series_dense.xlsx) | [07_four_series_dense.csv](../data/07_four_series_dense.csv) | [07_four_series_dense.png](07_four_series_dense.png) |
| [08_two_by_two_ci_columns.xlsx](../data/08_two_by_two_ci_columns.xlsx) | [08_two_by_two_ci_columns.csv](../data/08_two_by_two_ci_columns.csv) | [08_two_by_two_ci_columns.png](08_two_by_two_ci_columns.png) |
| [09_deep_hierarchy_many_rows.xlsx](../data/09_deep_hierarchy_many_rows.xlsx) | [09_deep_hierarchy_many_rows.csv](../data/09_deep_hierarchy_many_rows.csv) | [09_deep_hierarchy_many_rows.png](09_deep_hierarchy_many_rows.png) |
| [10_unicode_custom_theme.xlsx](../data/10_unicode_custom_theme.xlsx) | [10_unicode_custom_theme.csv](../data/10_unicode_custom_theme.csv) | [10_unicode_custom_theme.png](10_unicode_custom_theme.png) |
| [11_boundary_precision.xlsx](../data/11_boundary_precision.xlsx) | [11_boundary_precision.csv](../data/11_boundary_precision.csv) | [11_boundary_precision.png](11_boundary_precision.png) |
| [12_multi_series_ci_text_rows.xlsx](../data/12_multi_series_ci_text_rows.xlsx) | [12_multi_series_ci_text_rows.csv](../data/12_multi_series_ci_text_rows.csv) | [12_multi_series_ci_text_rows.png](12_multi_series_ci_text_rows.png) |
| [13_comprehensive_showcase.xlsx](../data/13_comprehensive_showcase.xlsx) | [13_comprehensive_showcase.csv](../data/13_comprehensive_showcase.csv) | [13_comprehensive_showcase.png](13_comprehensive_showcase.png) |

图片由 `python -m tests.render_visual_cases` 生成，不应手工重命名。

## 核对提示

- `04_clipping_stress.png`：越界侧只有箭头而无端帽；完全越界只显示一个向外箭头。
- `03_dual_ci_columns.png`：同一结局的两个 CI 列使用相同 y。
- `01_single_series.png`：效应文本位于 CI 绘图区右侧。
- `08_two_by_two_ci_columns.png`：每个 Cohort 的 crude/adjusted 点严格共线，Cohort 文本和图例位于 CI 后。
- `12_multi_series_ci_text_rows.png`：CI 后每条文本、点和区间线严格共线，共享结局名称居中。
- `13_comprehensive_showcase.png`：双 CI 列和对应文本逐系列共线，同时核对父标题行与缩进系列子行（零合并）、上下界箭头、共有无效应线、仅校正模型面板额外目标线、方向指示与底部图例。
- `10_unicode_custom_theme.png`：默认回归环境使用 Microsoft YaHei 渲染中英文。
