# Artifact Contract

## Visual Layers

Each slide folder should include a `manifest.json` from Image Split.

```json
{
  "canvas": [960, 540],
  "slideSize": [960, 540],
  "asset_count": 2,
  "assets": [
    {
      "file": "01_header_chrome.png",
      "position": [0, 0, 960, 64],
      "canvas": [960, 540]
    }
  ]
}
```

## Text Layer

`text-layer.json` should contain a `slides` array. Each slide has independently editable text objects.

```json
{
  "slides": [
    {
      "slide": 1,
      "texts": [
        {
          "name": "title",
          "text": "Editable title",
          "x": 80,
          "y": 48,
          "w": 800,
          "h": 48,
          "size": 28,
          "bold": true,
          "color": "#12324A",
          "align": "center"
        }
      ]
    }
  ]
}
```

Text object fills and outlines are stripped by default in the production builder.

## OCR Evidence

When Image Split runs OCR racing, Image-PPT-King should treat these files as review evidence:

- `ocr-candidates.json`: raw engine outputs from Tesseract, PaddleOCR, MinerU, or other adapters.
- `ocr-merged.json`: merged text boxes and text content for review.
- `ocr-review-report.md`: human-readable engine status and conflict summary.
- `ocr_boxes_preview.png`: visual overlay for checking OCR coverage.

OCR boxes should help draft text content and masks. They should not override region schemas or visual anchors when placing final editable text.
