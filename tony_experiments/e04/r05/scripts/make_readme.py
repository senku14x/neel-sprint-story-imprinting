"""E04 R05 (new): assemble README.md from the hand-written notes (notes/*.md) and the generated tables (results/...), in the
brief's order: Status; pre-flight and smoke notes; one results table per evaluation (side by side, beside the references) and
every cell in detail; the paired differences; exclusions; spend and GPU time; code changes and odd things; files."""
import re
from pathlib import Path

R = Path("/workspace/e04/r05")


def rd(p, default=""):
    p = R / p
    return p.read_text().strip() if p.exists() else default


ev = rd("results/evals/evals.md")
detail = ev[ev.find("\n## (a)") + 1:] if "\n## (a)" in ev else ev


def block(name):
    m = re.search(rf"<!-- {name}:start -->\n(.*?)<!-- {name}:end -->", detail, re.S)
    return m.group(1).strip() if m else ""


paired_a, paired_b = block("paired-a"), block("paired-b")
sbs = rd("results/evals/evals_side_by_side.md")
m = re.search(r"<!-- paired-c:start -->\n(.*?)<!-- paired-c:end -->", sbs, re.S)
paired_c = m.group(1).strip() if m else ""
sbs = re.sub(r"\n*<!-- paired-c:start -->.*?<!-- paired-c:end -->\n?", "\n", sbs, flags=re.S).strip()
detail = re.sub(r"<!-- (paired-[ab]):start -->.*?<!-- \1:end -->\n?",
                lambda m: f"(The {'paired differences' if m.group(1) == 'paired-a' else 'flips and model differences'} are in the "
                          "next section, \"Paired differences\".)\n", detail, flags=re.S)
detail = detail.replace("\n### ", "\n#### ").replace("\n## (", "\n### (")
detail = "### (" + detail[4:] if detail.startswith("## (") else detail


def demote(t):
    return t.replace("\n### ", "\n#### ").replace("\n## ", "\n### ")


parts = [
    "# E04 R05: imprinting evaluations of the existing adapters `a2` and `a5bq`, with E01's paper-story model as a reference (no training)",
    "",
    "*Experiment E04 (content/voice split), run R05, brief v1.1 (26 Oct 2026, 02:50 Taipei). 1× H100 80 GB on E01's network volume. "
    "Numbers only: no interpretation.*",
    "",
    "## Status", "", rd("notes/status_filled.md", rd("notes/status.md")), "",
    "## Pre-flight and smoke test", "", rd("notes/preflight.md"), "", rd("notes/smoke.md"), "",
    "## Results", "",
    "One table per evaluation, models side by side, beside the references (counts and exclusions per cell follow under "
    "\"Every cell in detail\"):", "",
    sbs, "",
    "### Every cell in detail", "", demote("\n" + detail).strip(), "",
    "## Paired differences", "",
    "### (a) Teammate's protocol", "", paired_a.replace("### Paired differences", "Paired differences"), "",
    "### (b) Bloom", "", paired_b.replace("### Flip and differences (Bloom)", "Flip and differences (Bloom)"), "",
    "### (c) Cheap checks", "", paired_c.replace("### (c) Differences, `a5bq` − `a2` (unpaired bootstrap, 2,000 resamples, seed 0)",
                                                 "Differences, `a5bq` − `a2` (unpaired bootstrap, 2,000 resamples, seed 0)"), "",
    "## Exclusions", "", rd("notes/exclusions.md", "(see the per-cell count tables above)"), "",
    "## Spend and GPU time", "", rd("results/spend.md"), "", rd("notes/spend_notes.md"), "",
    "GPU time (1× H100 80 GB):", "", rd("results/gpu_time.md"), "",
    "## Notes: code changes, GLM pacing, odd things", "",
    rd("notes/glm_plan.md"), "", rd("notes/code_changes.md"), "", rd("notes/odd.md"), "",
    "## Files", "", rd("notes/files.md"), "",
]
(R / "README.md").write_text("\n".join(parts) + "\n")
print(f"README.md written ({len((R / 'README.md').read_text()) / 1e3:.0f} kB)")
