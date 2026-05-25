# Image PPT Acceptance Rubric

Use this rubric before presenting an editable PPT as usable. Report each gate as `pass`, `warn`, or `fail`. Any `fail` blocks full-deck rollout unless the user explicitly accepts the limitation.

## Gate P0: Route And Artifacts

- State the route: `component-layer`, `CopySlides-like region reconstruction`, `Image2 textless skeleton`, or `hybrid`.
- Required artifacts: final PPTX, rendered preview PNGs, layout JSON when available, build manifest, QA report, and source/render/diff comparison for representative or high-risk slides.
- CopySlides-like samples also need the source `region-schema.json` and visual-layer manifest.
- If OCR racing was used, include `ocr-candidates.json`, `ocr-merged.json`, and `ocr-review-report.md`.
- Full deck work also needs a contact sheet covering every slide.

Fail if the route is unclear, the PPTX cannot be traced to its visual layers/text JSON, or preview rendering is missing.

## Gate P1: PPTX Structure

- PPTX opens as a zip without errors.
- Slide count, slide size, page order, and page numbers match the task.
- No missing media relationships or empty placeholder text boxes.
- Each slide has semantic text in `ppt/slides/slide*.xml`.
- Page numbers are editable XML text, continuous, and visually in the right footer slot.

Fail on corrupt PPTX, wrong slide count, missing media, missing XML text, or wrong page numbering.

## Gate P2: Editability

- Main titles, subtitles, bullets, card text, tab labels, badges, captions, and page numbers are native editable text.
- Each semantic unit is its own text box; unrelated bullets, labels, and page numbers are not merged.
- Charts, microscopy, photos, logos, and dense figure regions may be image objects, but must be selectable/movable/replacable.
- Final body text must not be baked into a flattened slide screenshot.

Warn if a small chart label remains in a figure image intentionally. Fail if title/body/card text is not editable.

## Gate P3: Transparent Text Layer

- Text boxes are text-only by default: no fill, no outline, no patch background.
- Build manifest should report `textFillViolationCount == 0` in strict production mode.
- If old text specs contain `fill` or `line`, the builder must strip them or the run must fail with `--fail-on-text-fill`.

Fail on any visible patch caused by a text box, or on any production text object that still uses fill/line to repair visuals.

## Gate P4: Text Placement And Style

- Text must fit the intended region with no clipping, overflow, or collision with icons/borders.
- Same-level text shares typeface, color, weight, alignment, and size.
- Same-level label font size delta: `pass <= 1 pt`, `warn <= 1.5 pt`, `fail > 1.5 pt`, unless the source intentionally differs.
- Label/pill/badge text center offset in 960x540 coordinates: `pass <= 3 px`, `warn <= 5 px`, `fail > 5 px`.
- Repeated cards should use consistent padding and line spacing.
- OCR boxes are only drafts; final positions should be anchored to visual objects.

Fail if text extends outside its frame, if headings are visibly inconsistent, or if a label looks pasted rather than centered on its visual object.

## Gate P5: Visual Fidelity

Render the PPTX and compare source versus render.

- For clean geometric pages, masked non-text changed pixels over 25 RGB levels should be `pass <= 8%`, `warn <= 12%`, `fail > 12%`.
- For dense chart/photo pages, a higher ratio can be accepted only with a note explaining that differences are inside figure/photo areas.
- Whole-slide source/render comparison and zoom crops are required when optimizing positions or comparing versions.
- Blocking visual failures: white/blue patch blocks, broken circles, missing icons, disconnected connectors, double page numbers, cropped logo, missing footer/header chrome.
- The unmasked final render must be reviewed. A masked diff that excludes text boxes cannot certify presentation quality by itself.

Do not accept a version only because its pixel metric improved. The side-by-side and zoom checks must still look semantically aligned.

## Gate P6: Content Accuracy

- Text content must come from the approved slide script, source document, or user-approved image text.
- Required phrases, page numbers, names, units, Greek letters, dates, figure/table labels, and statistical symbols must be checked in the PPTX XML text layer.
- OCR racing conflicts must be resolved before acceptance. Do not silently pick one OCR engine when numbers, units, Greek letters, gene/protein names, or medical terms differ.
- Old-topic residue and common OCR substitutions are blocking failures.

Fail if a required phrase is missing from XML, if the page number is wrong, or if content contradicts the approved source.

## Gate P7: WPS/PowerPoint Rendering

When the final deck will be used in WPS or PowerPoint:

- Open representative pages in the target app.
- Check font fallback, line breaks, clipping, text overflow, object selection, media display, and page-number/logo placement.
- If WPS differs from artifact-tool preview, tune for WPS and document the tradeoff.

Warn if only artifact-tool rendering was checked. Fail if WPS/PowerPoint cannot open the PPTX or visibly breaks core layout.

## Gate P8: Position Optimization Safety

For v3-style local optimization:

- Keep previous best output and compare source/previous/current.
- Lock stable layout anchors before optimizing: margins, header, footer, card groups, circles, chart/photo frames, and page number slot.
- Default maximum shift: 6 px for visual assets and 4 px for text boxes in 960x540 coordinates.
- Move semantic groups together; do not independently optimize a connector away from its badge/card.
- Manual approval is required before replacing a previous best version.

Fail if optimization improves masked diff but introduces visible drift, disconnected lines, off-center labels, or worse typography.

## Gate P9: False-Pass Prevention

- A structural pass only means the PPTX is technically assembled. It is not a presentation-grade pass.
- Text regions must receive their own review for residual baked text, inpaint gibberish, text overlap, clipping, and wrong anchors.
- Final render OCR or manual zoom review should be used on high-risk pages to catch nonsense glyphs and old text under the editable layer.
- Textless-layer OCR/manual review should be used to catch source text that remains in visual layers before editable text is added.
- A visual patch detector or manual patch review should check hard-edge white/gray/blue rectangles in title/card/label/footer zones.
- If the user or reviewer can see patches,乱码,重叠, or broken visual components, the gate is `fail` even when XML, text-fill, and masked-diff metrics pass.
- Record whether WPS/PowerPoint was checked. If not checked for a final deck, mark the gate `warn`; if checked and broken, mark `fail`.

## Minimum Report

Every accepted sample should report:

- route and slide/page count
- asset count and text object count
- text fill violation count
- required text presence
- non-text changed ratio and threshold
- style consistency metrics
- false-pass prevention result, including unmasked/text-region review
- pass/warn/fail gate summary
- links to preview and source/render/diff images
