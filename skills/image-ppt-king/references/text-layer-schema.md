# Text Layer JSON Schema

Use this schema with `scripts/build_ppt_from_layers.mjs`.

## Top-Level

```json
{
  "styleTable": {},
  "slides": []
}
```

`styleTable` is optional planning metadata. The builder ignores it; use it while preparing text objects so same-level text is consistent.

## Slide Record

```json
{
  "slide": 1,
  "texts": []
}
```

The slide number maps to a page folder under the layer root, such as `第01页`, `slide-01`, or `01`.

## Text Object

```json
{
  "name": "main-title",
  "text": "汇报思路：从临床疗效到机制线索",
  "x": 195,
  "y": 75,
  "w": 610,
  "h": 50,
  "size": 34,
  "color": "#073F91",
  "bold": true,
  "align": "center",
  "valign": "mid",
  "typeface": "PingFang SC",
  "wrap": "square",
  "insets": {"left": 0, "right": 0, "top": 0, "bottom": 0}
}
```

Required fields:

- `text`
- `x`, `y`, `w`, `h`

Optional fields:

- `name`: PowerPoint object name. Defaults to `text-N`.
- `styleRole`: optional planning metadata, such as `title`, `pillLabel`, `cardPrimary`, `caption`, or `pageNumber`. The builder ignores it.
- `anchor`: optional planning metadata that records which visual asset the text was aligned to. The builder ignores it; final `x`, `y`, `w`, `h` are still required.
- `size`: font size in points. Defaults to `14`.
- `color`: hex color. Defaults to `#333333`.
- `bold`: boolean. Defaults to `false`.
- `align`: `left`, `center`, or `right`. Defaults to `left`.
- `valign`: `top`, `mid`, or `bottom`. Defaults to `top`.
- `typeface`: font family. Defaults to `PingFang SC`.
- `wrap`: `square` or `none`. Defaults to `square`.
- `rotation`: optional shape rotation in degrees. Use `270` for common vertical chart-axis labels.
- `autoFit`: optional PowerPoint text autofit behavior, such as `shrinkText`.
- `fill`: legacy/debug-only textbox fill color. Production builds strip this by default.
- `line`: legacy/debug-only textbox outline color. Production builds strip this by default.
- `insets`: textbox margins. Defaults to zero.

## Text Box Transparency

Production text boxes are transparent by default. Use text objects for text only:

- Set `text`, `x`, `y`, `w`, `h`, `size`, `color`, `bold`, `align`, and `typeface`.
- Do not use `fill` or `line` to recreate blue labels, cards, pills, badges, or white cover patches.
- If a visual shape is missing, rebuild it in the visual layer first, then place transparent editable text over it.

The builder strips `fill` and `line` unless `--preserve-text-fill` is passed. Use `--fail-on-text-fill` during QA to reject text JSON that still contains filled or outlined text boxes.

## Page Numbers

Add page numbers as normal text objects. Do not rely on OCR page numbers.

```json
{
  "name": "page-number",
  "text": "3",
  "x": 910,
  "y": 492,
  "w": 24,
  "h": 18,
  "size": 11,
  "color": "#004EA2",
  "bold": true,
  "align": "right",
  "typeface": "Arial",
  "wrap": "none"
}
```

## Coordinate System

Coordinates use the output slide size, usually `960x540`. Full-canvas visual PNG layers are stretched to the same slide size. If OCR coordinates use `960x540`, they can be used directly after correction.

OCR coordinates are drafts. For production samples, align repeated labels and badge text to visual anchors from the page manifest instead of blindly trusting OCR boxes.

## Visual Anchors

Optional `anchor` metadata can document how final coordinates were chosen:

```json
{
  "anchor": {
    "asset": "tab_tl_pill_bg",
    "mode": "center",
    "dx": 12,
    "dy": 0
  }
}
```

Common anchor modes:

- `center`: center text within a pill, badge, number circle, or icon label.
- `inner`: place text inside a card/panel using padding.
- `baseline`: align title or footer reference text to a known rule.
- `slot`: use a fixed page-number or footer slot.

The current builder does not calculate anchors. Use anchors to guide preprocessing, then write concrete coordinates.

## Cropped Visual Assets

`scripts/build_ppt_from_layers.mjs` supports both full-canvas visual layers and cropped atomic assets. In a page `manifest.json`, an asset with source-canvas placement should include:

```json
{
  "file": "card_tl_outline.png",
  "name": "card_tl_outline",
  "position": [95, 132, 328, 276],
  "canvas": [1672, 941],
  "placement": "crop"
}
```

The builder maps `position` from source-image pixels into the output slide size. Assets without `position` remain full-canvas layers placed at `(0,0)`.
