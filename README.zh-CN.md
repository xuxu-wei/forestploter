# forestploter

`forestploter` 是一个由 XLSX/CSV 长表驱动、强调可审计性的表格化森林图绘制包。
它负责输入验证、文字与置信区间对齐、自动布局和 Matplotlib 渲染，不负责计算
效应量、置信区间或荟萃分析统计量。

> 这是一个独立的 Python 项目，与同名 R 包没有隶属关系。

[English README](README.md)

## 安装

```bash
python -m pip install forestploter
```

首个正式版本发布前，需要显式安装候选版本：

```bash
python -m pip install --pre forestploter
```

要求 Python 3.10 或更高版本。

## 快速开始

```python
from forestploter import ForestColumn, forest, read_forest_data

df = read_forest_data("forest_input.xlsx", sheet_name="Forest")
result = forest(
    df,
    columns=[
        ForestColumn("Outcome", "结局", "text", 2.5),
        ForestColumn("ci", "治疗效应", "ci", 3.5, "center"),
        ForestColumn("Effect", "效应值 [95% CI]", "numeric", 2.0, "right"),
    ],
    xlim=(0.4, 1.6),
    ref_line=1.0,
)
result.save("forest.png")
```

`columns` 是最终图像从左到右顺序的唯一依据，因此无论 XLSX/CSV 表头怎样排列，
普通文本列都可以放在任意 CI 绘图区之前或之后。

一条源记录描述“一个系列 × 一个目标 CI 列 × 一组
`estimate/lower/upper`”。`_plot_row` 明确指定视觉行；同一系列跨多个 CI 列时，
复制记录、保持 `_plot_row` 不变，并修改 `_ci_column`。

## 文档与示例

- [中英文网页版文档](https://xuxu-wei.github.io/forestploter/)
- [数据契约](https://xuxu-wei.github.io/forestploter/zh_CN/data_contract.html)
- [示例图库](https://xuxu-wei.github.io/forestploter/zh_CN/gallery.html)
- [API 文档](https://xuxu-wei.github.io/forestploter/zh_CN/api.html)
- [XLSX 长表模板](tests/data/forest_data_template.xlsx)
- [十二组 XLSX/CSV/PNG 回归用例](tests/README.md)

`0.1` 系列是质量优先的公开预览版本。长期维护规则见
[CONTRIBUTING.md](CONTRIBUTING.md)、[SUPPORT.md](SUPPORT.md)、
[SECURITY.md](SECURITY.md) 和 [CHANGELOG.md](CHANGELOG.md)。

## 许可证

MIT © 2026 Xuxu Wei。详见 [LICENSE](LICENSE)。
