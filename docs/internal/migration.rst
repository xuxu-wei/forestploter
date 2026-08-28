宽表到长表迁移
==============

本开发版本直接移除了旧宽表接口，不提供运行时兼容层。旧调用中的 ``est``、
``lower``、``upper``、``ci_column``、``series_text``、``series_layout`` 和
``group_labels`` 参数不再存在。

为什么改为长表
--------------

旧模型为 ``k`` 个系列准备 ``3*k`` 个数值字段，并由系列位置和 CI 列数量隐式推导
纵向偏移。该方法难以表达 Excel 中“一个结局跨多行、每系列一行文字”的自然布局，
也会让不同 CI 列在系列缺失时发生错位。

新模型把每条记录限制为一个系列、一个 CI 列和一组三元数。``_plot_row`` 显式决定
纵坐标，因此源数据本身可以审计对齐关系，渲染器不再猜测。

转换规则
--------

#. 把每组 ``estimate_x/lower_x/upper_x`` 展开为独立记录。
#. 将系列名写入 ``_series``，目标 CI 布局列写入 ``_ci_column``。
#. 每系列需要独立文字行时，给它不同 ``_plot_row``。
#. 同一系列跨多个 CI 列时，复制记录并共享 ``_plot_row``。
#. 把每系列格式化 CI 文字写入普通显示字段；不再使用
   ``ForestSeriesTextSpec``。
#. ``series_styles`` 从位置序列改为以系列名为键的映射。
#. XLSX 可纵向合并共享显示字段；CSV 则明确重复共享值。

旧写法
------

.. code-block:: python

   forest(
       wide,
       est=("estimate_a", "estimate_b"),
       lower=("lower_a", "lower_b"),
       upper=("upper_a", "upper_b"),
       ci_column="ci",
       columns=columns,
       series_styles=(style_a, style_b),
   )

新写法
------

.. code-block:: python

   # long 中每条记录已有 _plot_row、_series、_ci_column、
   # estimate、lower、upper、_row_type、_indent、_is_summary。
   forest(
       long,
       columns=columns,
       series_styles={"Series A": style_a, "Series B": style_b},
   )

可直接比较 ``tests/data/02_multi_series.xlsx`` 与其 CSV 伴随文件，或查看
``08_two_by_two_ci_columns.xlsx`` 的 24 条记录如何形成 12 个视觉行。
