# 梁鉴：佐证材料与参赛作品简介

本附件对应2026 AIC AI+力学开放式赛题，整理日期2026-10-22。

- 主文档：`研发与实验验证佐证材料.pdf`，由LaTeX排版，证据性质为内部研发与仿真实验。
- 简介：`参赛作品简介.txt`，纯文本201字符（含标点、数字），供报名表粘贴。
- `assets/`：实际本地原型的三次运行截图，非生成式图片。
- `records/`：接口响应、测试输出、双次结果复核、来源指纹与文件清单。

本次采集固定观测种子12345、模型种子11，案例为常规、健康环境变化、附加质量。三例为功能演示，不计入原有720例正式评价。

正式性能数字来自2026-10-13的完整实验。本次未重新训练模型，只重新检查已保存的run1/run2结果。无实物试验、专利、软著、第三方证明或现场应用。

## 在完整工程中重新生成

1. 按`requirements.txt`配置项目Python环境，运行`.venv/bin/python demo/server.py --port 18766`。
2. 在安装Playwright且可使用Chrome的Node环境运行`node scripts/capture_evidence.cjs`。
3. 运行`.venv/bin/python -m pytest tests -q`并保留实际输出；运行`.venv/bin/python scripts/verify.py > output/evidence/records/review-validation.json`。后者会同时写入`results/validation.json`，更新前保留旧记录。
4. 运行`python3 scripts/prepare_evidence.py`，从实际记录生成表格、指纹和简介校验。
5. 在`paper/`中用XeLaTeX编译`evidence.tex`两次，再渲染检查六页布局。

本附件仅含截图、轻量记录和证据文档源文件；完整权重、原始数据与算法源码在主工程内。附件包不是完整比赛提交包，也不是独立训练环境。

团队编号为AIC-2026-34636761，团队名称尚未提供。佐证材料使用合并后的单份PDF；最新编号材料包由`scripts/package_submission.py`生成，旧20261013比赛ZIP仅作为历史版本保留。
