# 梁鉴：环境扰动下的损伤识别

2026 AIC AI+力学开放式赛题，团队编号 **AIC-2026-34636761**。

本私有仓库用于保存作品、公式推导和2026-10-31收到的复赛准备反馈。模型、数据、技术报告、可编辑PPT、演示视频及源文件均供复核。所有实验结果来自仿真，尚无实物验证。

## 先看当前问题

**[当前疑问与复赛准备需求](review/CURRENT_QUESTIONS.md)**：按五张截图整理，区分明确提问、已有材料、尚未完成的修改，以及只在截图中出现的文件。

截图中提到“明天要答辩”，按截图日期推算为2026-11-01；这是聊天陈述，尚未从官方日程独立确认。当前重点是帮助参赛者理解方法并准备追问，而不只是增加幻灯片页数。

## 材料入口

| 材料 | 路径 |
|---|---|
| 当前问题清单与交接 | [review/CURRENT_QUESTIONS.md](review/CURRENT_QUESTIONS.md) |
| 原始反馈截图（5张） | [review/screenshots](review/screenshots) |
| 完整技术报告（13页） | [output/pdf/完整技术报告.pdf](output/pdf/完整技术报告.pdf) |
| 局部损伤完整推导（10页） | [output/pdf/局部损伤刚度模型_完整推导.pdf](output/pdf/局部损伤刚度模型_完整推导.pdf) |
| 可编辑PPT（现有10页版） | [output/pptx/答辩演示_可编辑版.pptx](output/pptx/答辩演示_可编辑版.pptx) |
| 演示视频（约3分40秒） | [output/video](output/video) |
| 佐证材料、简介 | [output/evidence](output/evidence)、[output/pdf](output/pdf) |
| 既有答辩与演示脚本 | [docs/答辩与演示脚本.md](docs/答辩与演示脚本.md) |
| 力学核心、实验入口 | [src/beam.py](src/beam.py)、[scripts/study.py](scripts/study.py) |
| LaTeX及独立核算 | [derivation/local-damage](derivation/local-damage) |
| 已保存的两次实验 | [results/run1](results/run1)、[results/run2](results/run2) |

原项目运行、依赖、实验与科学边界说明见 [docs/PROJECT_README.md](docs/PROJECT_README.md)。该文档原来位于项目根目录，其命令仍应在本仓库根目录运行。已有校验记录保留历史日期和本地路径，不代表在GitHub端重新训练或验收。

## 本次整理的范围

- 已整理项目当前文件和截图，编写问题清单与建议处理顺序。
- 截图中的“修改PPT、答辩稿、技术报告”等作为后续需求记录；本次上传并不意味着这些修改已完成。
- `notepad_share_encrypt.hdoc`只在截图中出现，未获得原始文件；没有声称已打开或读出其中内容。截图中的长图缩略图不可作为逐字转录依据。
- 大型材料ZIP通过本仓库Release保存；代码目录不重复存放历史ZIP、虚拟环境、缓存和中间渲染文件。完整材料包为2026-10-22版本，另有2026-10-28独立推导包；二者不是2026-10-31复赛修订版。
- 当前仓库保持私有。聊天截图及相关文件只用于本次授权的协作归档，未额外赋予开源许可。上传GitHub不等于向赛事平台提交。

文件字节数及SHA-256见 [review/UPLOAD_MANIFEST.json](review/UPLOAD_MANIFEST.json)。清单对应从原项目复制的文件，不包括随后新增的仓库说明文档。
