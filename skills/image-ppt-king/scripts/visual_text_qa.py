#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text("utf-8"))


def find_slide(text_spec: dict[str, Any], slide_no: int) -> dict[str, Any]:
    for slide in text_spec.get("slides", []):
        if int(slide.get("slide", -1)) == slide_no:
            return slide
    if len(text_spec.get("slides", [])) == 1:
        return text_spec["slides"][0]
    raise ValueError(f"Could not find slide {slide_no} in {text_spec}")


def make_text_mask(size: tuple[int, int], texts: list[dict[str, Any]], pad: float) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for item in texts:
        if not str(item.get("text", "")).strip():
            continue
        x = float(item["x"])
        y = float(item["y"])
        w = float(item["w"])
        h = float(item["h"])
        draw.rectangle(
            [
                max(0, x - pad),
                max(0, y - pad),
                min(size[0], x + w + pad),
                min(size[1], y + h + pad),
            ],
            fill=255,
        )
    return mask


def parse_label_names(value: str | None) -> set[str]:
    if not value:
        return set()
    return {entry.strip() for entry in value.split(",") if entry.strip()}


def style_role_sizes(texts: list[dict[str, Any]], label_names: set[str]) -> dict[str, list[float]]:
    groups: dict[str, list[float]] = {}
    for item in texts:
        role = item.get("styleRole")
        if not role and item.get("name") in label_names:
            role = "label"
        if not role:
            continue
        groups.setdefault(str(role), []).append(float(item.get("size", 14)))
    return groups


def pptx_text_presence(pptx: Path, required: list[str]) -> dict[str, bool]:
    if not pptx:
        return {}
    with zipfile.ZipFile(pptx) as zf:
        slide_xml = [
            name
            for name in zf.namelist()
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
        ]
        xml = "".join(zf.read(name).decode("utf-8", "ignore") for name in slide_xml)
    return {text: text in xml for text in required}


def pptx_alpha_zero_count(pptx: Path | None) -> int | None:
    if not pptx:
        return None
    with zipfile.ZipFile(pptx) as zf:
        slide_xml = [
            name
            for name in zf.namelist()
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
        ]
        xml = "".join(zf.read(name).decode("utf-8", "ignore") for name in slide_xml)
    return len(re.findall(r'<a:alpha val="0"\s*/>', xml))


def gate(status: str, detail: str, **metrics: Any) -> dict[str, Any]:
    return {"status": status, "detail": detail, "metrics": metrics}


def overall_status(gates: dict[str, dict[str, Any]]) -> str:
    statuses = {entry.get("status") for entry in gates.values()}
    if "fail" in statuses:
        return "fail"
    if "warn" in statuses:
        return "warn"
    return "pass"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create source/render visual diff and text-layer QA metrics for image-ppt outputs.")
    parser.add_argument("--source", required=True, type=Path, help="Source slide image.")
    parser.add_argument("--render", required=True, type=Path, help="Rendered PPT slide PNG.")
    parser.add_argument("--text-json", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--slide", type=int, default=1)
    parser.add_argument("--pptx", type=Path)
    parser.add_argument("--build-manifest", type=Path)
    parser.add_argument("--asset-manifest", type=Path)
    parser.add_argument("--label-names", help="Comma-separated text object names to measure as label group.")
    parser.add_argument("--required-text", help="Comma-separated text strings that should exist in PPTX XML.")
    parser.add_argument("--text-mask-pad", type=float, default=4)
    parser.add_argument("--delta-threshold", type=int, default=25)
    parser.add_argument("--warn-non-text-changed-ratio", type=float, default=0.08)
    parser.add_argument("--max-non-text-changed-ratio", type=float, default=0.12)
    parser.add_argument("--max-text-fill-violations", type=int, default=0)
    parser.add_argument("--max-label-font-delta", type=float, default=1.0)
    parser.add_argument("--warn-label-font-delta", type=float, default=1.5)
    parser.add_argument("--fail-on-gate-fail", action="store_true")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    render = Image.open(args.render).convert("RGB")
    source = Image.open(args.source).convert("RGB").resize(render.size, Image.Resampling.LANCZOS)
    text_spec = load_json(args.text_json)
    slide = find_slide(text_spec, args.slide)
    texts = slide.get("texts", [])
    mask = make_text_mask(render.size, texts, args.text_mask_pad)

    diff = ImageChops.difference(source, render)
    diff_arr = np.asarray(diff).astype(np.int16)
    mask_arr = np.asarray(mask)
    outside = mask_arr == 0
    delta = np.max(diff_arr, axis=2)
    changed = (delta > args.delta_threshold) & outside
    changed_ratio = float(changed.sum() / max(1, outside.sum()))
    mean_delta = float(delta[outside].mean()) if outside.any() else 0.0

    side = Image.new("RGB", (render.size[0] * 2, render.size[1] + 20), "white")
    side.paste(source, (0, 20))
    side.paste(render, (render.size[0], 20))
    draw = ImageDraw.Draw(side)
    draw.text((10, 2), "source scaled", fill=(0, 0, 0))
    draw.text((render.size[0] + 10, 2), "render", fill=(0, 0, 0))
    source_vs_render = args.out_dir / "source_vs_render.png"
    side.save(source_vs_render)

    masked_diff = ImageChops.difference(source, render).point(lambda p: min(255, p * 4))
    masked_out = Image.new("RGB", render.size, (235, 238, 242))
    masked_out.paste(masked_diff, mask=Image.fromarray((outside * 255).astype(np.uint8), "L"))
    masked_diff_path = args.out_dir / "masked_diff_x4.png"
    masked_out.save(masked_diff_path)

    build_manifest = load_json(args.build_manifest) if args.build_manifest and args.build_manifest.exists() else {}
    asset_manifest = load_json(args.asset_manifest) if args.asset_manifest and args.asset_manifest.exists() else {}
    groups = style_role_sizes(texts, parse_label_names(args.label_names))
    style_metrics = {
        name: {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "delta": max(values) - min(values),
        }
        for name, values in groups.items()
        if values
    }
    required = [text.strip() for text in (args.required_text or "").split(",") if text.strip()]
    required_presence = pptx_text_presence(args.pptx, required) if args.pptx else {}
    fill_violations = build_manifest.get("textFillViolationCount")
    alpha_count = pptx_alpha_zero_count(args.pptx)

    if changed_ratio <= args.warn_non_text_changed_ratio:
        visual_gate = gate(
            "pass",
            "masked non-text visual difference is within the pass threshold",
            changed_ratio=changed_ratio,
            pass_threshold=args.warn_non_text_changed_ratio,
            fail_threshold=args.max_non_text_changed_ratio,
        )
    elif changed_ratio <= args.max_non_text_changed_ratio:
        visual_gate = gate(
            "warn",
            "masked non-text visual difference needs manual review",
            changed_ratio=changed_ratio,
            pass_threshold=args.warn_non_text_changed_ratio,
            fail_threshold=args.max_non_text_changed_ratio,
        )
    else:
        visual_gate = gate(
            "fail",
            "masked non-text visual difference exceeds the fail threshold",
            changed_ratio=changed_ratio,
            pass_threshold=args.warn_non_text_changed_ratio,
            fail_threshold=args.max_non_text_changed_ratio,
        )

    if fill_violations is None:
        text_fill_gate = gate("warn", "build manifest did not report text fill violations")
    elif int(fill_violations) <= args.max_text_fill_violations:
        text_fill_gate = gate("pass", "text boxes have no prohibited fill/line usage", count=int(fill_violations))
    else:
        text_fill_gate = gate("fail", "text boxes still contain prohibited fill/line usage", count=int(fill_violations))

    if required and not all(required_presence.values()):
        missing = [text for text, present in required_presence.items() if not present]
        required_gate = gate("fail", "required text is missing from PPTX XML", missing=missing)
    else:
        required_gate = gate("pass", "required text is present in PPTX XML", checked=len(required))

    label_metric = style_metrics.get("label")
    if label_metric:
        delta_size = float(label_metric["delta"])
        if delta_size <= args.max_label_font_delta:
            style_gate = gate("pass", "same-level label font sizes are consistent", delta=delta_size)
        elif delta_size <= args.warn_label_font_delta:
            style_gate = gate("warn", "same-level label font sizes need manual review", delta=delta_size)
        else:
            style_gate = gate("fail", "same-level label font sizes are inconsistent", delta=delta_size)
    elif args.label_names:
        style_gate = gate("warn", "label names were provided but no label style metrics were found")
    else:
        style_gate = gate("pass", "no label style group requested")

    if args.pptx and len(texts) > 0 and alpha_count is not None and alpha_count >= len(texts):
        transparent_gate = gate("pass", "PPTX XML contains transparent text box markers", alpha_markers=alpha_count, text_count=len(texts))
    elif args.pptx and len(texts) > 0:
        transparent_gate = gate("warn", "transparent text box markers are fewer than text objects; inspect XML/render manually", alpha_markers=alpha_count, text_count=len(texts))
    else:
        transparent_gate = gate("pass", "no text objects require transparency markers", text_count=len(texts))

    gates = {
        "visual_fidelity": visual_gate,
        "text_fill": text_fill_gate,
        "required_text": required_gate,
        "style_consistency": style_gate,
        "transparent_text": transparent_gate,
    }
    acceptance_summary = {
        "overall": overall_status(gates),
        "gates": gates,
    }

    report = {
        "slide": args.slide,
        "source": str(args.source),
        "render": str(args.render),
        "pptx": str(args.pptx) if args.pptx else None,
        "visual_asset_count": asset_manifest.get("asset_count"),
        "text_count": len(texts),
        "text_fill_violation_count": fill_violations,
        "transparent_text_box_alpha_count": alpha_count,
        "style_metrics": style_metrics,
        "non_text_changed_ratio_delta_gt_threshold": changed_ratio,
        "delta_threshold": args.delta_threshold,
        "non_text_mean_rgb_delta": mean_delta,
        "required_text_presence": required_presence,
        "acceptance_summary": acceptance_summary,
        "qa_images": {
            "source_vs_render": str(source_vs_render),
            "masked_diff": str(masked_diff_path),
        },
    }
    (args.out_dir / "qa-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (args.out_dir / "qa-report.md").write_text(
        "\n".join(
            [
                "# Visual/Text QA",
                "",
                f"- Slide: {args.slide}",
                f"- Visual assets: {report['visual_asset_count']}",
                f"- Text objects: {report['text_count']}",
                f"- Text fill violations: {report['text_fill_violation_count']}",
                f"- Transparent alpha markers: {report['transparent_text_box_alpha_count']}",
                f"- Non-text changed ratio(delta>{args.delta_threshold}): {changed_ratio:.3f}",
                f"- Non-text mean RGB delta: {mean_delta:.2f}",
                f"- Acceptance overall: {acceptance_summary['overall']}",
                "",
                "## Gates",
                "",
                "| Gate | Status | Detail |",
                "| --- | --- | --- |",
                *[
                    f"| {name} | {entry['status']} | {entry['detail']} |"
                    for name, entry in gates.items()
                ],
                "",
                f"- Source vs render: `{source_vs_render}`",
                f"- Masked diff: `{masked_diff_path}`",
            ]
        )
        + "\n",
        "utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_gate_fail and acceptance_summary["overall"] == "fail":
        sys.exit(2)


if __name__ == "__main__":
    main()
