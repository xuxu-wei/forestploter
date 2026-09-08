# forestploter for Python

[![CI](https://github.com/xuxu-wei/forestploter/actions/workflows/ci.yml/badge.svg)](https://github.com/xuxu-wei/forestploter/actions/workflows/ci.yml)
[![Documentation](https://github.com/xuxu-wei/forestploter/actions/workflows/docs.yml/badge.svg)](https://xuxu-wei.github.io/forestploter/)
[![PyPI](https://img.shields.io/pypi/v/forestploter.svg)](https://pypi.org/project/forestploter/)
[![Python](https://img.shields.io/pypi/pyversions/forestploter.svg)](https://pypi.org/project/forestploter/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/xuxu-wei/forestploter/blob/main/LICENSE)

`forestploter` 是一个面向 Python 的表格化森林图绘制包，可从可审计的 XLSX/CSV
长表生成适合发表的静态图。它负责数据契约验证、文本与置信区间逐行对齐，以及基于
Matplotlib 的 PNG/SVG 渲染；不负责计算效应量、置信区间或荟萃分析统计量。

> **项目身份：**这是一个独立的 Python 包，不是同名的
> [`forestploter` R 包](https://github.com/adayim/forestploter)，也不由该 R 包的
> 作者或维护者开发、背书或维护。

[English README](https://github.com/xuxu-wei/forestploter/blob/main/README.md)

## 绘图效果

[![三系列在双森林图列及对应置信区间文本中逐行对齐，并展示父标题行与缩进子行、截断箭头、共有无效应线、单列额外目标线、方向指示和底部图例](https://raw.githubusercontent.com/xuxu-wei/forestploter/main/tests/artifacts/13_comprehensive_showcase.png)](https://xuxu-wei.github.io/forestploter/zh_CN/gallery/13_comprehensive_showcase.html)

*三个系列在粗模型与校正模型 CI 绘图区及各自对应的文本列中以紧凑行距严格对齐；CI
文本只保留数值，系列由高对比度的靛蓝、玫红、森林绿配色，方形、圆形、三角形标记，
缩进子行标签和图例共同区分。共享的结局数据只在父
标题行填写，不使用合并单元格。同一示例还展示上下界截断、两个面板共有的无效应线、
仅校正模型面板出现的额外目标线、坐标轴方向指示、汇总菱形及底部图例。图中为合成
演示数据。[查看完整代码并下载 XLSX 或 CSV 输入](https://xuxu-wei.github.io/forestploter/zh_CN/gallery/13_comprehensive_showcase.html)。*

## 核心能力

- 从 XLSX、CSV 读取统一的可审计长表数据契约，也可直接传入兼容的
  `pandas.DataFrame`。
- 使用父标题行和缩进子行表达常规层级，共享值只填写在父标题行。
- 在确实需要跨多行居中显示时，仍保留受支持的 XLSX 纵向合并。
- 通过 `_plot_row`、`_series` 和 `_ci_column`，将单系列或多系列在一个或多个
  CI 列中显式逐行对齐。
- 普通文本或数值列可以放在 CI 绘图区之前、中间或之后；最终左右顺序只由
  `columns` 决定。
- 支持汇总菱形、越界箭头、共有参考线、仅在指定 CI 列显示的额外目标线、系列样式、
  主题，以及列表头或图像底部图例。
- 表格边框默认隐藏；可通过 `ForestTheme(show_table_border=True)` 显示外框和横向
  分隔线，纵向列分隔线仍可单独控制。
- 通过自动尺寸和布局诊断处理密集表格、长文本、Unicode 标签及 PNG/SVG 导出。

## 安装

当前版本是公开预览候选版，需要显式安装预发布版本：

```bash
python -m pip install --pre forestploter
```

要求 Python 3.10 或更高版本。

## 快速开始

先[下载可直接运行的 01 示例工作簿](https://raw.githubusercontent.com/xuxu-wei/forestploter/main/tests/data/01_single_series.xlsx)，
然后运行：

```python
from forestploter import ForestColumn, forest, read_forest_data

df = read_forest_data("01_single_series.xlsx", sheet_name="Forest")
result = forest(
    df,
    columns=[
        ForestColumn("label", "结局 / 研究", "text", 2.8),
        ForestColumn("n", "样本量", "numeric", 0.7, "right"),
        ForestColumn("ci", "治疗效应", "ci", 3.3, "center"),
        ForestColumn(
            "effect_display",
            "均值差 [95% CI]",
            "numeric",
            2.0,
            "right",
        ),
    ],
    xlim=(-1.0, 1.0),
    ticks_at=(-1.0, -0.5, 0.0, 0.5, 1.0),
    ref_line=0.0,
)
result.save("forest.png", dpi=300)
```

`columns` 是最终图像从左到右顺序的唯一依据，因此无论 XLSX/CSV 表头怎样排列，
普通显示列都可以出现在任意 CI 绘图区之前或之后。

表格边框默认不显示。使用 `ForestTheme(show_table_border=True)` 可显示外框和横向行
分隔线；需要完整方格时再同时设置 `show_vertical_grid=True`。

## 输入模型速览

`read_forest_data()` 返回 `ForestData`：标准化数据位于 `df.frame`，受支持的 XLSX
合并范围保存在 `df.spans`；CSV 使用相同逻辑字段，但不包含合并元数据。

一条源记录描述“一个系列 × 一个目标 CI 列 × 一组
`estimate/lower/upper`”。`_plot_row` 明确指定视觉行；同一系列跨多个 CI 列时，
复制记录、保持 `_plot_row` 不变，并修改 `_ci_column`。

完整填写规则见[数据契约](https://xuxu-wei.github.io/forestploter/zh_CN/data_contract.html)
和 [XLSX 通用模板](https://raw.githubusercontent.com/xuxu-wei/forestploter/main/tests/data/forest_data_template.xlsx)。

## 文档与示例

- [中英文网页版文档](https://xuxu-wei.github.io/forestploter/)
- [快速入门](https://xuxu-wei.github.io/forestploter/zh_CN/getting_started.html)
- [示例图库](https://xuxu-wei.github.io/forestploter/zh_CN/gallery.html)
- [API 文档](https://xuxu-wei.github.io/forestploter/zh_CN/api.html)
- [十三组 XLSX/CSV/PNG 回归用例](https://github.com/xuxu-wei/forestploter/blob/main/tests/README.md)

## 当前范围与状态

`0.1` 系列是质量优先的公开预览版本。CI 覆盖 Python 3.10 至 3.14，并在 Windows
和 macOS 上执行冒烟测试。公开 API 在 `1.0` 前仍可能通过正式弃用流程演进。

目前所有 CI 列共用一套全局线性坐标配置；逐 CI 列独立坐标和对数坐标列入后续计划，
详见[路线图](https://github.com/xuxu-wei/forestploter/blob/main/ROADMAP.md)。

## 支持、贡献与引用

- [获取支持](https://github.com/xuxu-wei/forestploter/blob/main/SUPPORT.md)
- [参与贡献](https://github.com/xuxu-wei/forestploter/blob/main/CONTRIBUTING.md)
- [安全策略](https://github.com/xuxu-wei/forestploter/blob/main/SECURITY.md)
- [变更日志](https://github.com/xuxu-wei/forestploter/blob/main/CHANGELOG.md)
- [软件引用信息](https://github.com/xuxu-wei/forestploter/blob/main/CITATION.cff)

## 致谢与开发透明度

本项目的表格化森林图工作流受到 Alimu Dayimu 创建的 R 包
[`forestploter`](https://github.com/adayim/forestploter) 启发。本仓库是面向
Python 生态的独立实现，具有自己的 API 和数据契约，并非该 R 包的官方 Python
版本；与该 R 包的作者或维护者不存在隶属、背书或维护关系。

本项目的代码实现、测试、文档、发布工程和维护流程均包含
[OpenAI Codex](https://developers.openai.com/codex/) 的大量 AI 辅助贡献。所有改动与
版本发布均由本包作者和维护者 Xuxu Wei 指导、审阅并批准。OpenAI 不是本项目的
维护者或赞助方。

## 许可证

MIT © 2026 Xuxu Wei。详见[许可证](https://github.com/xuxu-wei/forestploter/blob/main/LICENSE)。
