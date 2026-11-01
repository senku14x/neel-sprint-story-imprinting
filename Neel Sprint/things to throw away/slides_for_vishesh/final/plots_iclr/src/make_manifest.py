"""Write plots_iclr/MANIFEST.md and final/CAPTIONS.md from the runners' registries, the reused scripts' caption files
(redirected into src/side/) and the slide scripts. Run after run_paper.py, run_kit.py, run_custom.py."""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
FINAL = OUT.parent
SIDE = HERE / "side"

REG = {}
for f in ("registry_paper.json", "registry_kit.json", "registry_custom.json"):
    p = SIDE / f
    if p.exists():
        for k, v in json.loads(p.read_text()).items():
            REG.setdefault(k, {}).update(v)

# caption files written by the reused paper scripts: "## name" sections with Takeaway / Source lines
CAP = {}
for p in SIDE.glob("redirected__*captions.md"):
    cur = None
    for line in p.read_text().splitlines():
        m = re.match(r"^## (\S+)", line)
        if m:
            cur = m.group(1)
            CAP.setdefault(cur, {"source": [], "takeaway": "", "file": p.name})
            continue
        if cur and "Source" in line:
            CAP[cur]["source"].append(re.sub(r"^\s*-\s*\*\*Source[^:]*:\*\*\s*", "", line).strip())
        if cur and "Takeaway" in line and not CAP[cur]["takeaway"]:
            CAP[cur]["takeaway"] = re.sub(r"^\s*-\s*\*\*Takeaway:\*\*\s*", "", line).strip()

LANDED = {
    "sw071_gap_vs_flip_main_families": "make_sw071.compute() + paper(): /workspace/runs_executor/sw071/tables/results.json, table.json",
    "sw071_gap_vs_flip_other_families": "make_sw071.compute() + paper(): /workspace/runs_executor/sw071/tables/results.json, table.json",
    "sw071_bridge_leans_casual": "make_sw071.compute(): results.json B1|free|none, B1|forced|none share",
    "sw071_garble_by_corpus": "make_sw071.compute(): results.json <model>/B7/rate; groups from adapters registry and train_meta files",
    "sw071_rflaw_by_recipe": "make_sw071.compute(): results.json <model>/B6b/rate",
    "sw074_rule_forecast_vs_simple_rules": "make_sw074.compute(): score74.score() on sw074_forecast.json vs targets_sw071_which_character_wins.json; cross-checked against sw074_score_vs_sw071.txt",
    "sw082_register_edit_vs_random": "make_sw082.compute(): /workspace/runs_executor/sw082/analysis/results71.json, full/fbtw rows, judged.jsonl (asserted equal to results71.json)",
}
GROUP = {}
for g, names in (("behaviour", "b1 b2 b3a b3b b4 b5a b5b b5c b6 b7 b8a b8b"), ("mechanism", "m1 m2 m3 m4a m4b m5 m6 m7a m7b m7c m7d")):
    for n in names.split():
        GROUP[n] = g

scripts = {"main": (FINAL / "SCRIPT_MAIN.md").read_text(), "appendix": (FINAL / "SCRIPT_APPENDIX.md").read_text()}


def slides_using(stem):
    out = []
    for which, txt in scripts.items():
        for blk in re.split(r"\n(?=### Slide )", txt):
            m = re.match(r"### Slide (A?\d+[a-z]?)", blk)
            if m and f"plots_iclr/{stem}.png" in blk:
                out.append(("" if which == "main" else "") + m.group(1))
    return out


def numbers_check(meta, files):
    text = " ".join([meta.get("title", ""), meta.get("subtitle", ""), meta.get("footer", "")])
    nums = sorted(set(re.findall(r"\d+(?:\.\d+)?", text)), key=float)
    blob = ""
    for f in files:
        try:
            if Path(f).is_file() and Path(f).stat().st_size < 30_000_000:
                blob += Path(f).read_text(errors="ignore")
        except Exception:
            pass
    if not blob:
        return f"numbers in title/subtitle/footer: {', '.join(nums) or 'none'} (not machine-checked: source not a single readable file)"
    blob = blob.replace("−", "-")
    found = [n for n in nums if re.search(r"(?<![\d.])" + re.escape(n) + r"(?![\d])", blob)]
    miss = [n for n in nums if n not in found]
    return (f"numbers in title/subtitle/footer: {', '.join(nums) or 'none'}; found verbatim in the sources: "
            f"{', '.join(found) or 'none'}; not found verbatim: {', '.join(miss) or 'none'} (layer ranges, sample "
            f"sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)")


lines = ["# plots_iclr: manifest", "",
         "Every PNG (16:9, 200 dpi; hero figures 1920 x 1080) has a matching PDF. Built with plain matplotlib "
         "(`/root/venvs/si/bin/python`), no viz. Numbers are never typed: each figure is drawn by code that reads its "
         "source files, reusing the original data-loading code:",
         "",
         "- `src/run_paper.py`: runs the paper-style scripts in `_sessions/ideation/notes/2026-11-01_plots_paper/` "
         "(behaviour, mechanism, turn1_voice, conduct_training; each checks every value against the old provenance "
         "sidecars) and the landed scripts' `compute()` (sw071 / sw074 / sw082), then adds a title, subtitle, footer "
         "and panel letters (`src/iclr.py`; titles/footers in `src/meta.py`).",
         "- `src/run_kit.py`: the second kit's `plots/src/make_plots.py` with its viz calls captured by a stand-in "
         "(`src/_vizstub/`), so its file readers (slidekit) run unchanged and record provenance; and "
         "`plots/hero/src/make_hero.py` unchanged except Okabe–Ito colours and the output folder.",
         "- `src/run_custom.py`: figures the triage asked for that no script drew (garble bars, opener bias, Tony's band "
         "removal and DAS gate, the sw071 scatter, sw074 sign agreement, the three-pairs heatmap, the turn-1 lean; added 1 Nov: "
         "Tony's curriculum arms, the Harry Potter / Star Wars band swaps and the v2 single-layer swaps).",
         "- `H5_tony_band_circuit.png` was drawn by the second kit's `plots/hero/src/make_hero.py` H5(); its entry here is "
         "copied from `plots/hero/MANIFEST.md` (registered in `src/side/registry_kit.json`).",
         "- Any file the reused scripts tried to write elsewhere (captions, provenance checks) was redirected into "
         "`src/side/`; nothing outside `final/` was written.",
         "",
         "Slide numbers refer to `SCRIPT_MAIN.md` (plain numbers) and `SCRIPT_APPENDIX.md` (A-numbers). Figures with "
         "no slide are backups.", ""]
caps = ["# Captions", "", "_One or two lines per figure: the takeaway, then n / readout. Figures in `plots_iclr/`._", ""]

for png in sorted(OUT.glob("*.png")):
    stem = png.stem
    meta = REG.get(stem, {})
    used = slides_using(stem)
    lines.append(f"## {png.name}")
    lines.append("")
    lines.append(f"- Slides: {', '.join(used) if used else 'none (backup)'}")
    lines.append(f"- Title: {meta.get('title', '')}")
    if meta.get("subtitle"):
        lines.append(f"- Subtitle: {meta['subtitle']}")
    lines.append(f"- Footer: {meta.get('footer', '').replace(chr(10), ' ')}")
    files = []
    if stem in CAP:
        lines.append(f"- Built by: the reused paper script (`{CAP[stem]['file'].split('__')[1]}` group), data code unchanged")
        for s in CAP[stem]["source"]:
            lines.append(f"- Source: {s}")
            files += re.findall(r"(/workspace/[^`;\s]+|/tmp/[^`;\s]+)", s)
    elif stem in LANDED:
        lines.append(f"- Built by: {LANDED[stem]}")
    if meta.get("sources"):
        lines.append("- Values read (what | value | file | key):")
        for row in meta["sources"][:60]:
            what, val, f, key = row
            if isinstance(val, float):
                val = f"{val:.4g}"
            elif isinstance(val, (list, tuple)):
                val = ", ".join(f"{x:.4g}" if isinstance(x, float) else str(x) for x in val)
            lines.append(f"  - {what} | {val} | `{f}` | {str(key)[:160]}")
            files.append(f)
        if len(meta["sources"]) > 60:
            lines.append(f"  - … {len(meta['sources']) - 60} more rows (full list in `src/side/registry_*.json`)")
    for n in meta.get("notes", []) or []:
        lines.append(f"- Note: {n}")
    lines.append(f"- Check: {numbers_check(meta, sorted(set(files)))}")
    lines.append("")
    take = meta.get("title", stem)
    foot = re.split(r"(?<=[.])\s", meta.get("footer", "").replace("\n", " "))
    foot = " ".join(foot[:2]).strip()
    caps.append(f"**{png.name}** (slides {', '.join(used) if used else 'backup'}). {take}. {foot}")
    caps.append("")

lines += ["## Not re-rendered (no source code)", "",
          "- `design/tony_figures/m1_bands.png`, `m2_writers.png`, `m3_parts.png`, `m4_ckpt.png`: Tony's default-"
          "matplotlib figures with internal labels; no plotting code in the package; not used by either script. "
          "(`m7_lora_default.png` was re-drawn from its result file as `tony_band_default_vs_switch.png`.)",
          "- `slides_for_vishesh/plots_codex_v1/*.png` (e.g. 18_global_axis_alignment, 26_story_to_chat, "
          "27_measurement_pipeline, 28_intervention_sites): no source code; the scripts use tables instead (slides 21, "
          "12, 39).",
          "- `design/figures/*` with `behaviour__`, `mechanism__`, `conduct_training__`, `landed__`, `turn1_voice__` "
          "prefixes and `design/alt_house_style_figures/*`: byte-identical or house-style copies of figures re-rendered "
          "here under their plain names.",
          "- Second-kit plots not used by the scripts and not re-rendered: `plots/01–06, 08–10, 12–15` (the same data is "
          "drawn by the paper-style re-renders b4, b7, b6, turn1_*, own_vs_quoted_dose, H1, chainP_flattery, H2, "
          "m7d, neither_histories, m2, redirect_checkpoints, b3a).", "",
          "## Gaps", "",
          "- Tony's curriculum slide (main slide 64): figure added 1 Nov (`tony_curriculum_push.png`) from "
          "`tr_curric_eval/results/tr_curric_eval.json`; the file was located by the part-2 discrepancy check.",
          "- `tony_three_pairs_heatmap.png` reads Tony's MECHANISM_LEDGER.md entry B70, not his result files (its values "
          "were checked against m94 / m103 / m108b / m108c on 1 Nov and match).",
          "- `kit_T3_tony_late_push.png` re-rendered 1 Nov: `run_kit.py` had recoloured rows by the words \"bee / crow "
          "helper\" in their labels (rows 1, 2, 4 showed the wrong role colour); it now keeps the source script's "
          "helper / rival colours (EXACT_COLOUR_TITLES).",
          "- `tony_band_default_vs_switch.png` re-rendered 1 Nov: legend and footer now say the default is the no-history "
          "shift from the untrained model, toward crow in both models (asserted on m7_lora_default.json).",
          "- Original-chat points in `tony_das_gate.png` have no intervals (m134.json stores counts only).",
          "- Hero figures keep their own layout (titles and arrows inside); panel letters were not added to them."]
(OUT / "MANIFEST.md").write_text("\n".join(lines))
(FINAL / "CAPTIONS.md").write_text("\n".join(caps))
print("manifest entries:", sum(1 for l in lines if l.startswith("## ") and l.endswith(".png")))
