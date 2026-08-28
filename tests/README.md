# forestploter 测试数据与视觉回归

每个用例有同主文件名的 XLSX 主数据、CSV 伴随数据和 PNG 输出。XLSX 验证纵向
合并结构；CSV 验证不依赖合并信息的逻辑长表语义。

| 编号 | 主数据 | 输出图片 | 主要检查内容 |
|---:|---|---|---|
| 01 | `data/01_single_series.xlsx` | `artifacts/01_single_series.png` | “文本 → CI → 效应文本”、分组、汇总与参考图例 |
| 02 | `data/02_multi_series.xlsx` | `artifacts/02_multi_series.png` | 三系列各占一行，共享结局单元格 |
| 03 | `data/03_dual_ci_columns.xlsx` | `artifacts/03_dual_ci_columns.png` | 同一 `_plot_row` 跨两个 CI 列对齐 |
| 04 | `data/04_clipping_stress.xlsx` | `artifacts/04_clipping_stress.png` | 单侧、双侧与完全越界；箭头取代端帽 |
| 05 | `data/05_long_layout.xlsx` | `artifacts/05_long_layout.png` | 长文本、中英文与自动扩宽 |
| 06 | `data/06_auto_scale_mixed_effects.xlsx` | `artifacts/06_auto_scale_mixed_effects.png` | 自动范围、刻度与参考图例 |
| 07 | `data/07_four_series_dense.xlsx` | `artifacts/07_four_series_dense.png` | 四系列显式视觉行和底部系列图例 |
| 08 | `data/08_two_by_two_ci_columns.xlsx` | `artifacts/08_two_by_two_ci_columns.png` | 双系列 × 双 CI、尾部文本列与该列表头图例 |
| 09 | `data/09_deep_hierarchy_many_rows.xlsx` | `artifacts/09_deep_hierarchy_many_rows.png` | 多地区、两级缩进、多个小计与长表 |
| 10 | `data/10_unicode_custom_theme.xlsx` | `artifacts/10_unicode_custom_theme.png` | 中文、英文、希腊文和自定义主题 |
| 11 | `data/11_boundary_precision.xlsx` | `artifacts/11_boundary_precision.png` | 精确边界、零宽区间与微量越界 |
| 12 | `data/12_multi_series_ci_text_rows.xlsx` | `artifacts/12_multi_series_ci_text_rows.png` | CI 后每系列一条文本、一条 CI 线、同一 y |
| 13 | `data/13_comprehensive_showcase.xlsx` | `artifacts/13_comprehensive_showcase.png` | 双 CI 与对应文本、父标题行与缩进系列子行（零合并）、双侧截断、共有无效应线、单列额外目标线、方向指示和底部图例 |

每个 XLSX 都有同名 `.csv` 伴随文件；`data/forest_data_template.xlsx` 是带 README
工作表的通用填写模板。

示例文件将 `estimate/lower/upper` 放在首个 CI 的录入位置；其后的显示字段继续排列
在三元数之后，六个控制字段 `_plot_row/_series/_ci_column/_row_type/_indent/_is_summary`
始终位于表尾。该物理顺序只便于录入，最终绘图左右顺序仍由 Python 的 `columns`
唯一决定。

## 运行

从 `my-repos` 目录运行：

```powershell
python -m pytest forestploter/tests -q
python -m tests.render_visual_cases
```

也可只渲染一个用例：

```powershell
python -m tests.render_visual_cases --case two_by_two_ci_columns
```

渲染脚本从 XLSX 主文件名推导 PNG 名称。验收要求为零失败、零 `xfail`，同时通过
XLSX/CSV 等价性、合并区域、观察位置、PNG/SVG 导出和文档构建检查。
