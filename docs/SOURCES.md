# 来源、开源边界与选型

核查日：2026-10-13。所有测试数据由本项目独立生成，无外部标注数据、无真实试验记录。

| 来源 | 作用与处理 |
|---|---|
| [大赛第二轮通知](https://www.aicomp.cn/notice/notice-3/5381.html)及根目录原始附件 | 赛道、日期、材料规范，保留原文件，不改写为自己的规则 |
| [pyfe3d](https://github.com/saullocastro/pyfe3d) | 通用梁壳有限元参考候选；BSD-3-Clause，许可证快照保留。其3D梁壳、编译依赖超出本原型需求，未复制其代码、未使用其结果 |
| [pycba](https://github.com/ccaprani/pycba) | 连续梁分析参考候选；仓库显示AGPL-3.0，未纳入运行依赖、未复制代码 |
| [structural-health-monitoring-python](https://github.com/alokpalai/structural-health-monitoring-python) | 问题路线调研：模态特征用于损伤识别。页面未见明确许可证，未复制代码或数据 |
| [Peeters, Maeck & De Roeck (2001)](https://doi.org/10.1088/0964-1726/10/3/314) | 振动健康监测中激励和温度干扰的需求依据。本项目整体刚度因子是简化代理，不是完整温度模型 |
| [Angelopoulos & Bates (2021)](https://arxiv.org/abs/2107.07511) | 分割共形预测及交换性、边际覆盖限制；本文扩展使用最大分区绝对误差作为分数 |
| [scikit-learn ExtraTreesRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesRegressor.html) | 极端随机树实现，BSD-3-Clause运行依赖；并非自研树算法 |
| [SciPy least_squares](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html) | 有界非线性最小二乘实现；非本作品原创优化器 |

自主实现部分：标准Euler–Bernoulli单元组装、六分区损伤参数化、环境因子反演、AI候选支持集与BIC选择、独立模态校核、合成数据域划分、校准/复评与演示工具。

创新定位：面向有限传感器教学/试验梁的可核验系统集成与实验设计，不宣称发明有限元、随机森林、BIC或共形预测，不宣称全球首创。是否具有足够参赛新颖性需要团队结合相关工作再次评估。

未复用另一目录的“智构”作品代码或结果。本项目为不同研究任务，不能共享别队身份或实验数字。
