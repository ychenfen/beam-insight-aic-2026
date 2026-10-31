# 梁鉴参赛演示视频

团队编号：AIC-2026-34636761。目标为3–5分钟、MP4小于300 MB。

画面采用1920×1080实验台版式，实际运行片段来自本地演示服务，使用常规、健康环境变化、附加质量三个案例。方法、实验和边界画面读取正式结果。全部数据为仿真；视频不冒充实物试验。

配音为macOS Tingting本地合成中文语音，画面页脚有披露。无背景音乐、第三方音乐或克隆声音。字幕在浏览器录制画面中烧录，同时导出SRT；讲解文字由`storyboard.json`维护。

## 制作流程

1. 在项目根目录运行`python3 scripts/video_audio.py`，生成逐句语音、分段WAV与`work/video/timeline.json`。
2. 启动`.venv/bin/python demo/server.py --port 18766`及`python3 -m http.server 18767 --bind 127.0.0.1`。
3. 在可导入Playwright并使用Chrome的Node环境运行`node scripts/record_video.cjs --preview`，检查8张分镜；正式运行去掉`--preview`。可用`--scenes=2,3,4`仅重录选定场景（从0编号）。
4. 运行`python3 scripts/finish_video.py`。程序通过录制画面的洋红色同步标记定位每段起点，移除加载画面和标记，封装H.264/AAC、30 fps视频；将语音响度归一化。
5. 运行`python3 scripts/verify_video.py`进行完整解码、时长、编码、音画时长、亮度、静音及数据检查，并抽取画面。人工/视觉复核完成后再写入本地验收状态，最后运行`python3 scripts/package_submission.py`更新带队号的材料包。

## 保存内容

- `video/`：分镜、HTML/CSS/JavaScript，均可编辑。
- `work/video/audio/`：逐句音频和8段拼接旁白。
- `work/video/raw/<场景名>.webm`：8段浏览器原始录制。
- `work/video/cases/`：三次实际接口响应。
- `work/video/timeline.json`、`encoding.json`：时序和同步记录。
- `output/video/`：最终MP4、SRT和配音稿。
- `results/video_validation.json`：最终验收及文件哈希。

原始录制中的16×16同步色块只用于机器对齐，最终交付已覆盖移除。实时演示中的单次推理耗时受机器状态影响，不代替正式实验的中位数。
