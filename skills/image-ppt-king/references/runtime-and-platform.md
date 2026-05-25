# Runtime And Platform

## Agent Runtime

The bundled `npm run demo` path is script-only and deterministic. It does not require an AI model once Node dependencies are installed.

Real deck reconstruction is different. A capable agent must inspect source images, consume Image Split manifests and OCR evidence, correct text, place editable text boxes, build PPTX files, and review output quality.

Recommended production profile:

- Codex-style agent mode with local file read/write and command execution.
- Multimodal model with image input and strong visual reasoning.
- Frontier reasoning model, such as GPT-5.5 or an equivalent model, for dense or high-value decks.
- Reasoning effort: `high` for normal production work; `xhigh` when available for difficult full-deck reconstruction.
- Enough context to compare source images, manifests, OCR evidence, `text-layer.json`, PPTX XML, previews, and QA reports.

Known-good author setup: macOS, Codex-style local agent, GPT-5.5-class multimodal reasoning, and `xhigh` reasoning for difficult pages.

## Platform Notes

The author validates primarily on macOS. The fallback builder is cross-platform Node.js and the QA script is cross-platform Python, but setup commands differ by shell.

macOS/Linux/WSL2:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install
```

Use Node.js 18+ and Python 3.10+.

For best parity with the author's workflow on Windows, use WSL2 when this project is paired with Docker OCR or heavier Image Split pipelines.

PowerPoint/WPS visual fidelity can differ by OS and font availability. For Chinese decks, install compatible fonts such as `PingFang SC` on macOS or `Microsoft YaHei` on Windows, then inspect representative slides manually.
