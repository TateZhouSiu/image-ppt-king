# Visual Anchor Text Workflow

Use this reference when converting a flat slide image into an editable PPT where the visuals come from `image-split`.

## Core Idea

OCR boxes are coordinate drafts, not final layout. Final text should be anchored to visual objects and governed by a style table.

## Workflow

1. Start from OCR text and corrected content.
2. Inspect the visual-layer manifest for stable anchors:
   - `*_pill_bg`, `*_tab_bg`: label text center.
   - `*_circle_base`, `*_ring`, `number_badge`: badge text center.
   - `card_*_outline`: card body inner padding.
   - `panel_*_outline`: panel content column.
   - `footer`, `page-number-slot`: page number and references.
3. Build a style table by hierarchy:
   - `title`
   - `pillLabel`
   - `centerTitle`
   - `centerSubtitle`
   - `cardPrimary`
   - `cardSecondary`
   - `panelLabel`
   - `caption`
   - `pageNumber`
4. Convert OCR boxes into final text boxes:
   - use corrected text content
   - center repeated labels from their visual anchor
   - use consistent font size/weight/color for same hierarchy
   - keep all text boxes transparent
5. Export with `--fail-on-text-fill` for production samples.
6. Render preview and run visual/text QA.

## Anchor Pattern

The final `text-layer.json` still needs absolute `x`, `y`, `w`, `h` because the current builder consumes concrete boxes. `anchor` and `styleRole` may be kept as planning metadata for future preprocessing; they do not replace coordinates.

```json
{
  "name": "label-junyao",
  "text": "君药",
  "styleRole": "pillLabel",
  "anchor": {"asset": "tab_tl_pill_bg", "mode": "center", "dx": 12, "dy": 0},
  "x": 127.5,
  "y": 84.8,
  "w": 77.5,
  "h": 31.2,
  "size": 18,
  "color": "#F6F8FB",
  "bold": true,
  "align": "center",
  "valign": "mid",
  "typeface": "PingFang SC",
  "wrap": "none"
}
```

## Style Table Example

```json
{
  "styleTable": {
    "title": {"size": 26.2, "color": "#073F91", "bold": true, "align": "left"},
    "pillLabel": {"size": 17.4, "color": "#F6F8FB", "bold": true, "align": "center", "valign": "mid"},
    "cardPrimary": {"size": 14.4, "color": "#1E1E1E", "bold": true, "align": "center"},
    "cardSecondary": {"size": 12.8, "color": "#1E1E1E", "bold": true, "align": "center"},
    "panelLabel": {"size": 16.0, "color": "#1E1E1E", "bold": true, "align": "center"},
    "caption": {"size": 8.4, "color": "#545B66", "bold": false},
    "pageNumber": {"size": 11, "color": "#073F91", "bold": true}
  }
}
```

## Acceptance Standard

- Text fill/line violation count is `0` under `--fail-on-text-fill`.
- Same-level label font size delta is normally <= 1pt.
- Label center should be within 3-5 px of the intended visual anchor in a `960x540` slide.
- Text does not touch borders, icons, or dividers.
- Text remains in XML text layer; no final semantic text is baked into visual PNGs.
- For one representative slide per style family, produce source/render side-by-side and masked diff QA.

## Stop Condition

Stop before full-deck generation if a representative slide has labels drifting off their pill/badge centers, text overflow, non-transparent text boxes, or inconsistent same-level font sizes.
