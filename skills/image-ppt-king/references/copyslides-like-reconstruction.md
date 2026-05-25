# CopySlides-Like Reconstruction

Use this route when a difficult Image2/PPT screenshot failed with OCR-box placement, inpaint residue, white/blue patches, or false QA passes.

## Core Contract

- Input visual assets come from `image-split` CopySlides-like region workflow.
- The PPTX is built from semantic regions, clean geometry/image assets, and transparent editable text.
- Do not use a full-page textless/inpaint bitmap as the production visual base.
- Do not use text-box fill or line to repair missing shapes. Repair shapes in visual layers first, then overlay transparent text.

## Required Inputs

- `region-schema-slideNN.json` with source canvas, slide size, region ids, boxes, anchors, and reconstruction method.
- `visual-layers/第NN页/manifest.json` with asset positions and route `copyslides-like-region-reconstruction`.
- `ocr-merged.json` and `ocr-review-report.md` when OCR racing was used; unresolved conflicts must be closed before delivery.
- `text-layer.json` or equivalent text spec referencing region ids and a style table.
- Source slide image for visual comparison.

Region ids should stay stable across split, text layer, QA, and final report. Example ids: `title`, `flow_01_label`, `card_03_badge`, `card_03_body`, `footer_page_number`.

## Text Layer Rules

- Build from region anchors first: tab centers, badge centers, card inner boxes, chart frame padding, title baseline, and page-number slot.
- Use OCR only to recover wording or rough location. Do not directly accept OCR box size as final font size or line height.
- Use multi-engine OCR agreement for text content, but resolve disagreements against the source document or approved slide script before exporting.
- Use a hierarchy style table: title, section label, card heading, card body, caption, badge number, page number.
- Keep same-level font-size deltas within 1 pt unless the source clearly differs.
- Use transparent text boxes only. Text object `fill` or `line` is a production failure.
- Separate semantic units: one title, each badge number, each tab label, each card body, each caption, each page number.

## QA Gates

Run structure checks, then visual checks. A structural pass is not presentation-grade acceptance.

- PPTX zip opens; slide count and size match the request.
- Required text exists in `ppt/slides/slide*.xml`.
- `textFillViolationCount == 0` or strict build fails.
- Text boxes have no major out-of-bounds or high-overlap collisions.
- Render preview PNGs and create a source/render side-by-side image.
- Review unmasked final render for residual source text, gibberish patches, text overlap, broken labels, and missing visual components.
- Run textless-layer OCR/manual review and final-render OCR/manual review on high-risk pages. Residual source text, duplicate text, or nonsense glyphs are blocking failures.
- Run text overlap/out-of-region checks against region boxes, not just slide bounds.
- Run a patch detector or manual patch review for hard-edge white/gray/blue rectangles in title, card, label, and footer zones.
- Masked non-text diff may guide visual-layer tuning, but it cannot pass a slide by itself.
- For WPS delivery, open representative pages in WPS and check font fallback, clipping, object selectability, and page-number placement.

## False-Pass Prevention

Fail the sample even if XML/text/fill metrics pass when any of these are visible:

- residual title/body text still baked into visual assets,
- nonsense OCR or inpaint glyphs under editable text,
- text overlaps another text box, icon, border, chart label, or footer,
- a text region is excluded from every visual check,
- shapes are only represented by broad patches rather than clean visual objects,
- source/render comparison looks worse than the previous accepted version.

## Page 16 Validated Pattern

The validated sample used:

- clean rebuilt background, title chrome, flow cards, tabs, badge circles, arrows, dotted connectors, and footer chrome;
- extracted image objects only for complex experiment illustrations;
- 13 visual/image objects and 22 transparent editable text objects;
- required XML text checks, text-fill strict check, rough overlap/out-of-bounds check, and source/render side-by-side review.
- The updated production route should additionally run OCR-racing evidence and textless/final-render review before full-deck rollout.

Use this as a pattern, not as fixed numbers. Dense chart pages may have more assets; simple divider pages may have fewer.
