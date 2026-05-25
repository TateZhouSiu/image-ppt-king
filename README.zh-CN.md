# Image-PPT-King

把平面幻灯片图片重建成可编辑 PowerPoint。

Image-PPT-King 是一个开放的 image-to-PPT 工作流：它消费 Image Split 生成的视觉层、region schema 和文字层 JSON，输出可编辑 PPTX、build manifest，并在 artifact 后端可用时输出预览图、layout JSON 和 QA 报告。

## 输出内容

- 可打开的 `.pptx`
- 原生可编辑文字框
- 可选中、可移动的视觉对象
- artifact 后端可用时的渲染预览图与 layout JSON
- build manifest 和视觉/文字 QA 报告

## 不承诺的部分

它不是万能矢量化工具。复杂图表、照片、显微图、logo 和复杂插图可能仍是可选中的图片对象。核心目标是把语义文字、基础 UI 几何和复杂视觉对象从截图里拆开，尽可能变成可编辑结构。

## 基本流程

```text
平面图片 -> Image Split 视觉层/schema -> text-layer.json -> Image-PPT-King -> 可编辑 PPTX
```

## 复现运行画像

内置的 `npm run demo` 路径是确定性的，不需要 AI 模型。真正重建复杂真实 deck 时，难点在于视觉层判断、文字校正、布局锚定、OCR 冲突处理和 QA 复查，因此需要能力足够强的 agent 运行环境。

推荐运行环境：

- Codex 风格 agent mode，能读写本地文件并执行命令。
- 支持图片输入、视觉理解较强的多模态模型。
- 复杂或高价值整套幻灯片，建议使用 GPT-5.5 或同级 frontier reasoning model。
- reasoning effort：常规生产任务用 `high`；困难整套重建在可用时用 `xhigh`。
- 上下文长度足够同时检查源图、Image Split manifest、OCR 证据、`text-layer.json`、PPTX XML、预览图和 QA 报告。

作者已验证环境：macOS、Codex 本地 agent、GPT-5.5 级别多模态推理模型，困难页面使用 `xhigh` reasoning。较小或低推理模型也能跑 builder，但在文字定位、样式一致性和 QA 判断上通常需要更多人工修正。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
```

```bash
node skills/image-ppt-king/scripts/build_ppt_from_layers.mjs \
  --backend auto \
  --layers-root examples/demo/visual-layers \
  --text-json examples/demo/text-layer.json \
  --out outputs/demo/editable.pptx \
  --workspace outputs/demo/workspace \
  --preview-dir outputs/demo/preview \
  --layout-dir outputs/demo/layout \
  --slide-size 960x540
```

`--backend auto` 会优先使用 Codex Presentations artifact runtime；如果找不到该运行时，会 fallback 到公开可安装的 `pptxgenjs` 后端，仍能生成可编辑 PPTX 和 build manifest。预览 PNG 与完整 layout JSON 需要 artifact 后端。

## 平台说明

这个仓库主要在 macOS 上编写和验证。fallback builder 是跨平台 Node.js，QA 脚本是跨平台 Python，但 shell 命令略有差异：

- macOS/Linux/WSL2：可以直接使用 README 中的 `python -m venv`、`source .venv/bin/activate`、`npm install` 和反斜杠换行命令。
- Windows PowerShell：使用 `py -m venv .venv`，然后执行 `.venv\Scripts\Activate.ps1`，再执行 `pip install -r requirements.txt` 和 `npm install`。
- 建议使用 Node.js 18+ 和 Python 3.10+。
- Windows 如果同时要跑 Docker OCR 或更重的 Image Split pipeline，推荐用 WSL2 以接近作者的 macOS/Unix shell 工作流。
- PowerPoint/WPS 的视觉效果会受操作系统和字体影响。中文 deck 建议在 macOS 使用 `PingFang SC`，Windows 使用 `Microsoft YaHei` 或兼容字体，并人工检查代表性页面。

如果只安装 skill 目录，也可以直接跑最小 demo：

```bash
cp -R skills/image-ppt-king ~/.codex/skills/
cd ~/.codex/skills/image-ppt-king
npm install
npm run demo
```

## OCR 证据

OCR 由 Image Split 阶段负责。Image-PPT-King 消费可选的 `ocr-candidates.json`、`ocr-merged.json` 和 `ocr-review-report.md`，用于校对内容、冲突和文字区域；最终文字定位仍应以 region schema 和 visual anchors 为准。
