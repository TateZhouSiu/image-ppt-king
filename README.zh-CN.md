# Image-PPT-King

把平面幻灯片图片重建成可编辑 PowerPoint。

Image-PPT-King 是一个开放的 image-to-PPT 工作流：它消费 Image Split 生成的视觉层、region schema 和文字层 JSON，输出可编辑 PPTX、预览图、layout JSON 和 QA 报告。

## 输出内容

- 可打开的 `.pptx`
- 原生可编辑文字框
- 可选中、可移动的视觉对象
- 渲染预览图
- 视觉/文字 QA 报告
- 构建 manifest

## 不承诺的部分

它不是万能矢量化工具。复杂图表、照片、显微图、logo 和复杂插图可能仍是可选中的图片对象。核心目标是把语义文字、基础 UI 几何和复杂视觉对象从截图里拆开，尽可能变成可编辑结构。

## 基本流程

```text
平面图片 -> Image Split 视觉层/schema -> text-layer.json -> Image-PPT-King -> 可编辑 PPTX
```

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
node skills/image-ppt-king/scripts/build_ppt_from_layers.mjs \
  --layers-root examples/demo/visual-layers \
  --text-json examples/demo/text-layer.json \
  --out outputs/demo/editable.pptx \
  --workspace outputs/demo/workspace \
  --preview-dir outputs/demo/preview \
  --layout-dir outputs/demo/layout \
  --slide-size 960x540
```

当前构建脚本依赖 Codex Presentations artifact runtime。公开稳定版应继续解耦成独立 PPTX 后端，或把该运行时作为明确依赖写清楚。

## OCR 证据

OCR 由 Image Split 阶段负责。Image-PPT-King 消费可选的 `ocr-candidates.json`、`ocr-merged.json` 和 `ocr-review-report.md`，用于校对内容、冲突和文字区域；最终文字定位仍应以 region schema 和 visual anchors 为准。
