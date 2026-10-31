# 梁鉴：环境扰动下的损伤识别

2026 AIC AI+力学开放式赛题的本地候选作品。所有结果均为仿真；尚无实物验证。目标是通过AI缩减位置搜索，再由物理模型估计和校核结果。

## 直接查看
- `output/pdf/完整技术报告.pdf`：13页完整主稿（含封面），正文约7700个中文汉字；含需求、推导、独立校核、实验、系统与实物试验计划。LaTeX源为`paper/full_report.tex`。
- `output/video/AIC-2026-34636761-开放式赛题-梁鉴-演示视频.mp4`：约3分40秒、1080p、30fps、18.93MB；含三个实际运行案例、中文合成旁白和字幕。可编辑分镜与制作说明见`video/`。
- `output/pdf/技术报告.pdf`：原两页简版，保留供快速阅读及按篇幅建议选用。
- `output/pdf/技术补充.pdf`：六页模型推导、实验、局限和复现依据，可作内部技术佐证。
- `output/pdf/答辩演示.pdf`：演示稿（LaTeX源文件在`paper/defense.tex`）。
- `entry.json`：作品名称、≤300字简介，团队编号AIC-2026-34636761；团队名称待补。
- `docs/实物验证方案.md`：冲奖最值得补强的实物试验与日程。

开放式赛题正式规则未规定报告最低字数或页数，要求按参考大纲完整阐述、PDF不超过10 MB；群聊截图中的“尽量控制在两页”是篇幅建议。按用户2026-10-13最新要求扩展完整稿，未将其他命题赛道的两页限制套用于开放题。当前以完整稿为展开论证主稿，简版与技术补充为已有配套版本。统计口径包含标题、表格和页眉等文本，仅计汉字，不把数字、英文、公式计入中文字数。

## 本地演示
已在本机创建`.venv`，可直接运行：
```bash
.venv/bin/python demo/server.py --port 18766
```
在浏览器打开 http://127.0.0.1:18766 。可切换6种工况、随机种子、5阶振型，拖动旋转梁体，暂停动画，查看分区损伤与区间。服务器仅绑定回环地址。若端口被占用，另选空闲端口，勿停止其他项目服务。

梁体颜色是估计刚度折减，形变由估计模型特征向量经Hermite插值计算；动画幅度与时间均为示意缩放。真实值只用于仿真评分，绝不作为反演输入。网页不是结构安全鉴定工具。

## 从零复现
本次环境为Python 3.14，精确依赖锁定于`requirements.txt`；其他版本需验证对应轮子可用性。
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
.venv/bin/python -m pytest tests -q
.venv/bin/python scripts/study.py --output results/run1
.venv/bin/python scripts/study.py --output results/run2
.venv/bin/python scripts/verify.py
.venv/bin/python scripts/present_results.py
bash scripts/build_papers.sh
```
重新训练会覆盖指定输出目录；保留已有正式结果时请先复制到独立目录，或使用新的`--output`路径。仅加载自己生成或校验过的joblib模型。

## 实验设计
3个模型种子（11/29/47）；每种子2400训练、120校准，6域各40测试。共720个独立测试工况，4种方法得到2880条预测。基线枚举全部22个0/1/2损伤位置组合；AI提议三个分区，只枚举7个组合。两者使用相同物理目标、相同每候选优化预算。

常规域融合MAE为0.135个百分点，穷举为0.150个百分点；在线中位耗时21.6/81.7 ms。速度取决于本机环境，误差接近不代表精度显著优越。名义90%同时区间实测覆盖87.5%。分布外失效见原始记录，不能删掉或改写。

## 关键目录
- `src/`：独立实现的标准梁有限元与融合反演。
- `tests/`：10项力学、数值和输入约束验证。
- `results/run1/`、`run2/`：两次从头生成/重训结果；时钟开销可不同，科学结果逐项一致。
- `results/validation.json`：数据隔离、双次复算、网格证据。
- `results/browser_validation.json`：浏览器交互与窄屏检查。
- `paper/generated/`：脚本生成图表和数值宏；不要手改数字。
- `docs/`：规则对应、来源、AI使用、实物验证、答辩脚本。
- 根目录原始PDF/JPG：用户提供的官方输入，保持原位。

## 权属与完成边界
核心实现未复制GitHub候选源码；参考与依赖授权见`docs/SOURCES.md`和`docs/licenses/`。标准有限元、随机树、BIC和共形预测不是原创算法。AI辅助完成了方案、代码、初稿和自动验证，团队仍须人工审阅并能解释结果。

团队编号为AIC-2026-34636761，已同步报告封面和可编辑PPTX。最新材料包由`scripts/package_submission.py`生成，PPTX位于包内“附加文件夹”，MP4位于根目录；验收记录为`results/submission_package_validation.json`。视频完整解码、技术检查与48个抽样画面复核见`results/video_validation.json`。团队名称、人工确认和实物证据待补；未执行网盘上传、报名缴费或平台提交。官方截止为2026-10-28 23:59，核查来源见`MANIFEST.md`。
