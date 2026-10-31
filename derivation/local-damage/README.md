# 局部损伤刚度模型的完整推导

2026-10-28。独立的10页LaTeX技术说明，团队编号AIC-2026-34636761。

- `main.tex`：可编辑主稿，使用XeLaTeX与TeX Live自带Fandol字体。
- `main.pdf`：已编译PDF。
- `verify_derivation.py`：仅依赖Python标准库的独立数学核算。
- `verification.json`：15项核算结果与主稿哈希。
- `delivery_validation.json`：页数、字体、逐页检查和交付文件哈希。

编译：`xelatex -interaction=nonstopmode -halt-on-error main.tex`，执行两次以更新引用。
核算：`python3 verify_derivation.py`。

文档从材料应变能和节点插值推导全部单元刚度项，补充分区装配、边界约束、质量矩阵、模态反演、灵敏度与不可辨识性；附本项目参数算例与代码对应。未修改原有报告、模型或比赛材料ZIP，未新增实测数据。

PDF预览采用本机Poppler渲染器。若某工具提示缺少Adobe-GB1语言包，应修复渲染环境；文档已嵌入所用字体。
