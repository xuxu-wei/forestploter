文档开发
========

环境
----

文档基线使用 Python 3.12，并固定以下工具版本：

* Sphinx 8.2.3
* sphinx-rtd-theme 3.1.0
* numpydoc 1.10.0
* myst-parser 4.0.1

项目运行依赖包括 NumPy、pandas、Matplotlib 和 openpyxl。可一次安装开发依赖：

.. code-block:: powershell

   python -m pip install -e ".[test,docs]"

本地构建
--------

从 ``forestploter`` 项目根目录运行：

.. code-block:: powershell

   python -m sphinx -M html docs docs/_build -W
   python -m sphinx -b doctest docs docs/_build/doctest -W

也可以使用 ``make -C docs html``，Windows ``cmd`` 环境可运行
``docs\make.bat html``。HTML 首页输出到 ``docs/_build/html/index.html``。

``-W`` 把警告视为构建失败。公开对象会执行严格的 numpydoc 结构检查，快速入门的
可执行片段由 doctest 验证，失效的内部链接和交叉引用同样会阻止构建。

维护公开 API
------------

新增或调整公开对象时同时完成以下工作：

#. 在源码中提供完整的 pandas/NumPy 风格 docstring，包括适用的 ``Parameters``、
   ``Returns``、``Raises``、``See Also``、``Notes`` 和 ``Examples``。
#. 更新 ``forestploter.__all__`` 与 :doc:`api` 的显式 ``autosummary`` 清单。
#. 为行为增加自动化测试，并更新相关指南或图库说明。
#. 运行 pytest、HTML 构建和 doctest，确认零新增失败、零文档警告。

``autosummary`` 会在每次构建时读取当前代码并生成 API 详情页，因此函数签名、类型
和 docstring 的修改会自动反映到本地网站。``api/generated`` 和 ``_build`` 都是
构建产物，不提交版本控制。

文件与视觉回归
--------------

十三组回归用例以 XLSX 为主输入，并各有一个同名 CSV 伴随文件。修改读取器、合并
语义或布局后必须同时验证：

.. code-block:: powershell

   python -m pytest tests -q
   python -m tests.render_visual_cases

结构门禁比较两种格式的 ``plot_row_ids``、观察位置和截断计数；XLSX 还检查合并
区域和源单元格坐标。PNG/SVG 导出、严格 HTML 和 doctest 都必须零失败、零 xfail。
完整的逐需求门禁和人工检查表见 :doc:`acceptance`。

版本化文档
----------

当前仓库只配置本地站点，页面版本显示为 ``development``。Sphinx ``autodoc`` 和
``autosummary`` 已能随源码构建自动更新 API 页面；接入 Read the Docs、GitHub
Pages 或等价 CI 托管后，可让每次提交、标签和拉取请求自动重建网站，并由
``sphinx-multiversion`` 或托管平台保留多个版本。自动生成不能替代契约审阅：公开
对象清单、迁移说明、示例和行为测试仍需在代码评审中同步维护。
