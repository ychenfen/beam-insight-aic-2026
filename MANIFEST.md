# 梁鉴：环境扰动下的损伤识别与力学校核

## 最新交付：视频与编号材料包（2026-10-22）

- 成片`output/video/AIC-2026-34636761-开放式赛题-梁鉴-演示视频.mp4`：219.57秒、18.93MB、1080p/30fps、H.264/AAC。配套同名SRT与`配音稿.md`。
- 可编辑源：`video/storyboard.json`及HTML/CSS/JavaScript；生产输入为`work/video/timeline.json`、8段命名WEBM、8段WAV及`cases/`三个响应；见`video/README.md`。
- 生成：`scripts/video_audio.py` → `scripts/record_video.cjs` → `scripts/finish_video.py` → `scripts/verify_video.py`；最后视觉复核后运行验证的`--visual-reviewed`参数，再运行`scripts/package_submission.py`。
- 核验：完整解码6583帧；时长、文件大小、音画时长、静音、峰值、黑白屏、字幕和数值一致性检查通过；48个抽样帧及关键原分辨率画面复核。证据与哈希见`results/video_validation.json`。
- 当前ZIP：`submission/AIC-2026-34636761-开放式赛题-梁鉴-材料包.zip`。MP4位于根目录，可编辑PPTX位于“附加文件夹”；另含13页报告、6页佐证、201字符简介与工程来源。CRC、UTF-8、逐文件哈希和独立备份见`results/submission_package_validation.json`。
- 最高门槛：本地核验。团队名称和团队审阅仍待完成，未上传或提交。历史记录中的无视频、待补编号等表述不代表当前状态。

## 任务合同
- 赛道：2026 AIC AI+力学开放式赛题（用户已确认）。目标：高质量、可答辩、可复现的独立作品；不承诺评奖结果。
- 范围：规则核查、开源调研、自研算法与实验、LaTeX完整主稿及两页简版、完整实验说明、演示和本地材料包。未授权上传/提交。
- 只读输入：根目录收到的 6 份 PDF 和 5 份 JPG，保留原位；重复大纲保留。
- 官方通知：https://www.aicomp.cn/notice/notice-3/5381.html ，2026-10-13 核查；初赛截止 2026-10-28 23:59，复赛 11 月 10 日前。
- 格式：名称≤20字、简介≤300字、报告 PDF≤10MB、材料不得出现学校/LOGO/指导教师信息。聊天截图建议两页、PPT可后补；两页主报告按六部分大纲组织，详证另附。

## 技术路线与预先确定的验证
研究原型：6分区悬臂梁，环境整体刚度因子与局部损伤分开估计。AI学习模态到候选位置的映射，候选支持集送入有界物理反演；未参与拟合的第4/5模态用于独立一致性检查。校准集建立同时覆盖六个分区的分割共形区间，报告分布外失效。

主基线为穷举全部0/1/2损伤支持集的非线性反演；同时比较纯AI与忽略环境的消融。不能把对消融的优势写成对最强基线的优势。

计划：3独立种子；每种子2400训练、120校准；6组各40测试（常规/健康环境变化/高噪声/网格加密/三处损伤/附加质量），共720独立测试。全部为自生成合成数据，不能写成实测。

验收：解析频率、静挠度、特征方程残差、环境缩放不变性、加密网格、支持集恢复、数据隔离、双次全链复算；论文数值自动注入；PDF逐页渲染；ZIP校验与独立备份。

## 当前状态
- 720例测试、2880条逐方法记录完成；10项力学测试通过。双次从头生成、重训结果的所有非计时指标、原始数组、校准记录一致，见`results/validation.json`。
- 2026-10-13按用户要求增加12页《完整技术报告》，约7700中文汉字，源文件`paper/full_report.tex`；保留原2页简版、6页技术补充和10页答辩稿。开放题正式规则无报告字数/页数限制，群聊两页为建议。
- 完整稿新增分模型种子结果和校准表，由`scripts/full_report_tables.py`读取冻结的`run1`自动生成。核心模型与实验结果没有改动。LaTeX源文件、结果宏、模型与原始数据保留。交互演示采用有限元振型、克制深色实验台布局，已完成浏览器功能/窄屏检查。
- 主写者 Codex；无其他写入者。最高门槛为本地验证，材料包是否最终验收以`results/package_validation.json`为准。
- 当前唯一正式结果源为`results/run1/`，`results/run2/`是独立从头重训的复算证据。预检目录不作为论文数字来源。
- 本地包生成命令：`.venv/bin/python scripts/package.py`；先运行`bash scripts/build_papers.sh`。包内逐文件哈希与ZIP CRC/UTF-8分别验证，独立备份位置写入验证记录。
- 待补：团队编号/名称，团队对模型与报告的人工审核，真实实验验证。可选演示视频尚无成片；已备讲解脚本和可运行演示。未执行任何外部上传/提交。

## 2026-10-22 佐证材料与作品简介
- 新文档：`output/pdf/研发与实验验证佐证材料.pdf`（6页），可编辑源为`paper/evidence.tex`。
- 作品简介：`output/evidence/参赛作品简介.txt`（201字符，含标点和数字），与`entry.json`及`scripts/present_results.py`同步；配置备份在`archives/config/`。
- 采集命令：启动`.venv/bin/python demo/server.py --port 18766`后，运行`node scripts/capture_evidence.cjs`，需要Playwright与Chrome。截图与三个实际JSON响应保存在`output/evidence/`。
- 复核：当前10项力学测试通过；重检保存的run1/run2，9项检查通过；核心源文件哈希与两次实验来源记录一致。未重新训练模型；新演示案例不计入720例正式实验。
- 生成：`python3 scripts/prepare_evidence.py`；在`paper/`中以XeLaTeX编译`evidence.tex`，输出至`work/evidence/`，渲染检查后复制至正式PDF目录。
- 数据性质：内部仿真实验佐证，无实物、专利、软著、用户或第三方证明。独立备份、ZIP CRC、字体、页面和最终文件哈希见`results/evidence_validation.json`。
- 新附件包与旧比赛提交ZIP独立，未更新旧ZIP。尚未上传/提交；下一步先审阅并补团队信息，再统一冻结提交版本。

## 当前编号材料包（2026-10-22后续）
- 团队编号：`AIC-2026-34636761`，用户直接提供；团队名称仍未提供。
- 报告封面、PPTX首页和报名元数据已同步编号，保留原有排版与科研数据。修改前备份：`archives/before-team-number-20261022-211601/`。
- 用户转述群老师要求PPTX放入“附加文件夹”。新压缩包使用队号命名，根目录提供技术报告、佐证材料、简介，“附加文件夹”包含可编辑PPTX和预览PDF，“工程源码与实验记录”保留可复现工程。
- 生成命令：`python3 scripts/package_submission.py`；最新文件清单、CRC与独立备份核验见`results/submission_package_validation.json`，优先于历史打包记录。
- 当前无视频MP4；尚未上传或提交。下一步补团队名称并录制视频，然后更新同一材料包。
