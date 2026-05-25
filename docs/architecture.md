# Architecture

Image-PPT-King has three layers.

## 1. Visual Layer Contract

Image Split produces page folders with `manifest.json` files. Each manifest records asset files, placement, canvas size, and route metadata.

## 2. Editable Text Layer

`text-layer.json` records native PowerPoint text objects. Text boxes should be transparent by default and anchored to visual objects, not raw OCR boxes.

## 3. PPTX Builder And QA

The builder assembles visual assets and text objects into a PPTX, renders previews, and writes build metadata. QA scripts compare source/render images while masking editable text zones.

## Runtime Note

The current builder is a Codex Presentations adapter. A standalone backend can be added behind the same artifact contract without changing Image Split outputs or `text-layer.json`.
