---
name: image-ppt-king
description: Convert slide/page images into editable PowerPoint PPTX decks by using Image Split visual layers, region schemas, transparent editable text, and QA gates. Use when Codex is given PNG/JPG/Image2/AI-generated slide images and asked to reconstruct image-based PPT pages, keep text editable, preserve layout, or turn flat slide screenshots into PPTX with selectable text and movable image objects.
---

# Image-PPT-King

## Contract

Build a PPTX where visual components are image/shape layers and semantic text is native editable PowerPoint text.

- Do not put final body text inside a flattened slide screenshot.
- Use `image-split` first when the input is only flat slide images and no clean visual layers exist.
- Preserve slide size, page order, visual rhythm, and page numbering.
- Treat charts, photos, microscopy, logos, and complex diagrams as image objects unless the user explicitly asks to redraw them.
- Rebuild main titles, labels, card text, bullets, captions, and page numbers as editable text boxes.
- Editable text boxes are text-only by default: no fill, no outline, no patch background.
- Prefer the Presentations artifact-tool when it is available because it can render previews and layout JSON. If it is not available, use the bundled `pptxgenjs` fallback backend to generate a reproducible editable PPTX.

## Runtime Assumptions

- The bundled `npm run demo` path is deterministic and can run without an AI model once Node dependencies are installed.
- Production reconstruction needs a Codex-style agent that can inspect images, read/write files, run Python/Node/OCR commands, inspect PPTX artifacts, and review generated previews.
- Use a strong multimodal reasoning model for real slide reconstruction. The author-known-good profile is macOS, Codex-style local agent, GPT-5.5-class multimodal reasoning, and `xhigh` reasoning for difficult pages.
- Use `high` reasoning for normal production work; use `xhigh` when available for dense decks, ambiguous OCR, or layout-heavy pages.
- Smaller models may run the builder but are more likely to misplace text, miss OCR conflicts, or accept weak QA results.
- For macOS/Windows/Linux setup details, read `references/runtime-and-platform.md` before promising reproducibility to a user.

## Workflow

1. Inspect the input images and decide scope:
   - one/few-slide sample first when style or OCR quality is uncertain
   - full deck only after the sample is accepted
2. Split visual layers:
   - invoke `image-split` for component-layer transparent PNGs
   - use cropped positioned assets for atomic objects; use full-canvas PNG layers only for true background-wide elements or preview compatibility
   - if `image-split` produced a CopySlides-like `region-schema.json`, treat it as the layout contract for text placement and QA
3. Build or correct text layer data:
   - use OCR only as a coordinate/content draft
   - when `ocr-merged.json` exists, use it as content evidence and conflict report, not as final placement
   - manually correct obvious OCR errors, symbols, Greek letters, dates, names, and headings
   - anchor labels to visual objects when available, such as pill center, badge center, card inner padding, chart frame, or footer page-number slot
   - for CopySlides-like reconstruction, place text from region anchors and a style table rather than raw OCR boxes
   - keep each text object independently editable; do not merge unrelated card labels, page numbers, or bullets
   - keep text boxes transparent; put missing blue labels, badges, cards, and tabs into the visual layer instead of textbox fill
4. Run `scripts/build_ppt_from_layers.mjs` with the layer root and text JSON.
5. Render preview PNGs and layout JSON when using the Presentations artifact backend. With the `pptxgenjs` fallback backend, verify the PPTX zip, slide XML text, media relationships, and build manifest instead.
6. Validate:
   - PPTX opens as a zip and has the expected slide count
   - each slide has text in `ppt/slides/slide*.xml`
   - no major text overflow in rendered previews
   - textless-layer OCR and final-render OCR/manual review do not show residual text, duplicate text, or gibberish patches on high-risk pages
   - image layers are selectable/movable objects, not a single baked screenshot unless intentionally used as a background

For high-fidelity editable reconstruction, use the stricter visual-anchor workflow in `references/visual-anchor-text.md` before finalizing `text-layer.json`.
For CopySlides-like region reconstruction validated on difficult Image2 pages, read `references/copyslides-like-reconstruction.md` before building or accepting the PPTX.
When OCR racing was used by `image-split`, carry `ocr-merged.json` and `ocr-review-report.md` into content checks before final text placement.
For final or high-risk samples, read `references/acceptance-rubric.md` and report pass/warn/fail gates. This is mandatory for v3-style position optimization or full-deck rollout.

## Builder Script

After installing this skill folder by itself, install the public Node fallback dependency from the skill root:

```bash
npm install
```

Install Python QA dependencies only when running `visual_text_qa.py`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Use the bundled script after visual layers and text JSON exist:

```bash
node scripts/build_ppt_from_layers.mjs \
  --layers-root /path/to/visual-layers \
  --text-json /path/to/text-layer.json \
  --out /path/to/editable.pptx \
  --workspace /path/to/workspace \
  --preview-dir /path/to/preview \
  --layout-dir /path/to/layout \
  --slide-size 960x540
```

The layer root should contain page folders with `manifest.json`; each manifest lists cropped positioned transparent PNG assets and/or documented full-canvas background-wide assets. The text JSON schema is documented in `references/text-layer-schema.md`.

Run the bundled smoke demo from the skill root:

```bash
node scripts/build_ppt_from_layers.mjs \
  --backend pptxgenjs \
  --layers-root assets/demo/visual-layers \
  --text-json assets/demo/text-layer.json \
  --out outputs/demo/editable.pptx \
  --workspace outputs/demo/workspace \
  --slide-size 960x540
```

By default the builder strips `fill` and `line` from text objects and reports the affected objects in `build-manifest.json`. Use `--fail-on-text-fill` for strict QA. Use `--preserve-text-fill` only for legacy debugging, not for production samples.

For representative slides, run `scripts/visual_text_qa.py` after rendering to produce a masked source/render diff and text-style metrics.

```bash
python scripts/visual_text_qa.py \
  --source /path/to/source-slide.png \
  --render /path/to/preview/slide-01.png \
  --text-json /path/to/text-layer.json \
  --pptx /path/to/output.pptx \
  --build-manifest /path/to/build-manifest.json \
  --asset-manifest /path/to/visual-layers/第05页/manifest.json \
  --out-dir /path/to/qa \
  --label-names s05-ocr-004,s05-ocr-009,s05-ocr-014 \
  --required-text 组方思路,君药,醒窍汤 \
  --warn-non-text-changed-ratio 0.08 \
  --max-non-text-changed-ratio 0.12 \
  --fail-on-gate-fail
```

## Text Layer Rules

- Use corrected content, not raw OCR, for final text.
- Use OCR-racing merge output as evidence; resolve conflicts against the source document, approved slide script, or user review before delivery.
- Use `PingFang SC` or `Microsoft YaHei` for Chinese unless the user specifies otherwise.
- Use separate text boxes for:
  - page title
  - blue tab labels
  - numbered badges
  - each card body
  - each bullet line/group
  - page number
- Use tight boxes for labels and larger wrapped boxes for paragraphs.
- For repeated components, prefer a style table over raw OCR font sizes: same-level labels, card headings, body lines, captions, and page numbers should share font size, weight, color, alignment, and vertical anchoring.
- Repeated labels should be centered from the corresponding visual layer bounds, not from the OCR text box, unless the visual layer is unavailable.
- When exact font style conflicts with editability, prioritize clean editable text and document the visual difference.
- Text boxes must be transparent in all normal routes. Do not use text-box `fill` or `line` to cover an existing skeleton shape, label, badge, card, or tab.
- If a visual shape is missing, fix it in `image-split` as a visual layer or add a separately documented shape repair. Do not combine the repair with the editable text box.

## Acceptance Standards

Run these checks before declaring a PPTX usable.

Use `references/acceptance-rubric.md` for the detailed gate model. The short standard below is only the minimum.

### Route Declaration

State which route was used:

- `component-layer route`: visual layers from `image-split`, with shapes/images rebuilt and text added separately.
- `CopySlides-like region reconstruction route`: semantic region schema from `image-split`, clean rebuilt geometry/atomic image assets, and transparent editable text anchored to regions.
- `Image2 textless skeleton route`: a full-slide textless skeleton image is used as the visual base and editable text is placed on top.
- `hybrid route`: textless skeleton for background plus selected component repairs or native shapes.

Do not mix route assumptions silently. Text coordinates calibrated for one route are not automatically valid for another.

### Structural PPTX Checks

- PPTX opens as a zip without errors.
- Slide count and slide size match the request.
- Page order and page numbers are correct.
- Every slide has semantic text in `ppt/slides/slide*.xml`.
- No empty placeholder text boxes remain.
- No missing media relationships are present.
- The final PPTX is exported through Presentations artifact-tool when that runtime is available; otherwise the bundled `pptxgenjs` backend is acceptable and must be reported in the build manifest.

### Editability Checks

- Main titles, subtitles, bullets, card text, tab labels, number badges, captions, and page numbers are native editable text.
- Charts, microscopy, photos, logos, complex medical diagrams, and dense figures may remain image objects, but must be selectable/movable/replacable.
- Do not bake final body text into a flattened slide screenshot.
- Use one text box per semantic unit. Do not merge unrelated bullets, page numbers, labels, and captions into a single box.

### Text Overlay Checks

- Text boxes must fit their target visual region without overflow, clipping, or covering icons/borders.
- Text style must be consistent by hierarchy: same-level labels share size, weight, color, alignment, and typeface.
- Same-level label font size delta should normally be <= 1pt unless the source intentionally differs; report any exception.
- Label text center should normally be within 3-5 px of the target pill/badge/card anchor in 960x540 slide coordinates.
- Text boxes are transparent by default. A text box with `fill` or `line` is a failure if it overlays an already-existing background label, pill, badge, or card.
- Filled text boxes are not accepted in production. Rebuild missing shapes separately, then overlay transparent text.
- QA must report the count of source text objects that had `fill` or `line`; the production build should strip them or fail with `--fail-on-text-fill`.
- When using an Image2 textless skeleton, first verify that the skeleton layout still matches the source. If it moved cards, labels, charts, or frames, regenerate or remap the text layer instead of reusing old coordinates.

### Visual QA Checks

- Render every slide to PNG.
- For sample and high-risk slides, create a source / render / diff comparison.
- For representative slides, mask out editable text boxes before measuring visual diff so the metric focuses on visual-layer fidelity.
- Also review the unmasked final render. Masked diff is not enough because it can hide residual source text, gibberish patches, and editable text overlap inside text regions.
- For presentation-grade acceptance, inspect source/render side-by-side and zoom crops for text zones, not only non-text zones.
- Blocking visual failures include white patches, blue patch blocks, broken/cropped badges, missing icons, double page numbers, text outside boxes, and inconsistent same-level font sizes.
- For full decks, produce a contact sheet and inspect all pages before delivery.

### Content Checks

- Text content must be corrected against the source document or approved slide script, not raw OCR.
- Common OCR substitutions, wrong Greek letters, wrong units, wrong page numbers, and old-topic residue are blocking failures.
- OCR-racing conflicts on scientific values, units, genes/proteins, drug concentrations, dates, or page numbers must be resolved before accepting the slide.
- Page numbers must be editable text and continuous unless the user asks otherwise.

### WPS / PowerPoint Checks

When WPS or PowerPoint is available and the user cares about final presentation fidelity:

- Open the generated PPTX and inspect representative pages.
- Check font fallback, line breaks, text overflow, media display, page numbers, and object selectability.
- If WPS rendering differs from artifact-tool preview, tune the PPTX for WPS and document the tradeoff.

## Output Layout

For substantial jobs, keep artifacts organized:

- `visual-layers/`: page folders from `image-split`
- `text-layer.json`: editable text objects
- `preview/`: rendered slide PNGs when using the artifact backend
- `layout/`: artifact-tool layout JSON when using the artifact backend
- final `.pptx`: only the deliverable in the user-facing output folder

## Stop Conditions

Stop and report before full-deck work if:

- the sample slide cannot render close enough to the source image
- OCR text is too inaccurate to correct without source text
- the preview has visible residual text, gibberish patches, or text overlap even when structure checks pass
- OCR-racing or final-render OCR flags unresolved scientific text conflicts
- the user expects every chart/photo pixel to become editable vectors
- final output would require cloud upload or external services not approved by the user
