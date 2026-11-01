"""E14 R03 README assembler (CPU): generated tables (results/*.md), landmark and direction readout tables with quotes, and the hand-written
summaries in notes/*.md (written after reading the results). -> README.md, results/x2lm_readouts.md, results/x3_dir_readouts.md
  /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/r03_report.py"""
import collections, json, os, random, sys, time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from x2_gpu import LM

NOTES = f"{R}/notes"


def note(name, default="(not written)"):
    p = f"{NOTES}/{name}.md"
    return open(p).read().strip() if os.path.exists(p) else default


def inc(name):
    p = f"{R}/results/{name}"
    if not os.path.exists(p):
        return f"(`results/{name}` not produced)"
    t = open(p).read().strip()
    # demote headings by two levels so they sit under the README's sections
    t = t.replace("](../plots/", "](plots/")
    return "\n".join(("##" + l) if l.startswith("#") else l for l in t.splitlines())


def short(t, n=160):
    t = (t or "").strip()
    first = next((l[2:].strip() for l in t.splitlines() if l.lstrip().startswith("- ")), t)
    return first[:n].replace("|", "/").replace("\n", " ")


def x2lm_tables():
    rd = jl(f"{R}/readouts/x2lmB.jsonl") + jl(f"{R}/readouts/x2lmA.jsonl")
    if not rd:
        return "(no X2 landmark readouts)"
    g = collections.defaultdict(list)
    for r in rd:
        g[(r["model"], r["version"], r["landmark"], r["block"])].append(r)
    folds_read = sorted({r["fold"] for r in rd})
    L = [f"Oracle lens (k = 1) at the 17 landmarks; folds read: {', '.join(folds_read)} ({len(rd)} readouts). STRICT bee / crow rate (n).\n"]
    for b in (40, 48, 56):
        cols = [(m, v) for m in ("S", "SB", "parent") for v in ("helpful", "dismissive", "polite_refusal") if (m, v, "t_h", b) in g]
        if not cols:
            continue
        L.append(f"**Block {b}**\n\n| landmark | " + " | ".join(f"{m} {v}" for m, v in cols) + " |\n|---|" + "---|" * len(cols))
        for lm in LM:
            cells = []
            for m, v in cols:
                rows = g.get((m, v, lm, b), [])
                cells.append("—" if not rows else f"{np.mean([r['strict_bee'] for r in rows]):.2f} / {np.mean([r['strict_crow'] for r in rows]):.2f} ({len(rows)})")
            L.append(f"| {lm} | " + " | ".join(cells) + " |")
        L.append("")
    rng = random.Random(0)
    L.append("**Quotes** (block 56; one random readout per cell, its first bullet, first 160 characters; random.Random(0))\n")
    for m in ("S", "SB", "parent"):
        L.append(f"*{m}*\n")
        for lm in ("r1_t1", "r1_t4", "r1_last", "u2_end", "r2_t1", "r2_last", "prohib_end", "u3_end", "t_h"):
            for v in ("helpful", "dismissive", "polite_refusal"):
                rows = g.get((m, v, lm, 56), [])
                if rows:
                    r = rng.choice(rows)
                    L.append(f"- {lm}, {v} (`{r['sid']}`): \"{short(r['text'])}\"")
        L.append("")
    out = "\n".join(L)
    open(f"{R}/results/x2lm_readouts.md", "w").write("# X2 landmark readouts\n\n" + out + "\n")
    return out


def x3_dir_tables():
    J = json.load(open(f"{R}/results/x3_dir_lens.json")) if os.path.exists(f"{R}/results/x3_dir_lens.json") else None
    rd = jl(f"{R}/readouts/x3.jsonl")
    L = []
    if J:
        L.append(f"CPU lens check against R02's GPU scores: {json.dumps(J['check_vs_gpu'])}\n")
        L.append("| direction | J++ +dir (top 10) | J++ −dir (top 10) | logit +dir (top 10) | logit −dir (top 10) |\n|---|---|---|---|---|")
        for name, e in J["dirs"].items():
            if "|L48|" not in name and "|L56|" not in name:
                continue
            j = lambda xs: " ".join(repr(x.strip())[1:-1] for x in xs[:10]).replace("|", "/")  # noqa
            L.append(f"| {name} | {j(e['jpp_plus'])} | {j(e['jpp_minus'])} | {j(e['logit_plus'])} | {j(e['logit_minus'])} |")
        L.append("\nAll blocks: `results/x3_dir_lens.json`.\n")
    if rd:
        g = collections.defaultdict(list)
        for r in rd:
            g[(r["model"], r["direction"], r["block"], r["t"])].append(r)
        L.append("**Oracle lens on unit(mean + t·σ·direction)** (k = 4 per t; one quote per cell, first bullet; STRICT bee / crow counts of 4)\n")
        L.append("| model | direction | block | t = −3 | t = −1 | t = +1 | t = +3 |\n|---|---|---|---|---|---|---|")
        for (m, d, b) in sorted({(k[0], k[1], k[2]) for k in g}):
            cells = []
            for t in (-3, -1, 1, 3):
                rows = g.get((m, d, b, t), [])
                if rows:
                    cells.append(f"\"{short(rows[0]['text'], 90)}\" ({sum(r['strict_bee'] for r in rows)}/{sum(r['strict_crow'] for r in rows)})")
                else:
                    cells.append("—")
            L.append(f"| {m} | {d} | {b} | " + " | ".join(cells) + " |")
    out = "\n".join(L) if L else "(no direction readings)"
    open(f"{R}/results/x3_dir_readouts.md", "w").write("# X3 direction readings\n\n" + out + "\n")
    return out


def main():
    st = open(f"{R}/STATUS.md").read()
    dev = open(f"{R}/logs/deviations.md").read()
    n_or = {os.path.basename(f)[:-6]: sum(1 for _ in open(f"{R}/readouts/{f}")) for f in os.listdir(f"{R}/readouts") if f.endswith(".jsonl")}
    L = []
    A = L.append
    A("# E14 R03 (overnight): R02, then reading what happens inside with lenses only\n")
    A("Observation only (no steering, patching, ablation or training). Everything is exploratory: descriptions with intervals, no pass/fail lines. "
      "Stage 1 (E14 R02) ran on GPU 0 and has its own README in `e14/r02/`.\n")
    A("## Status\n")
    A(note("status"))
    A(f"\n- Oracle-lens readouts in Stage 2: {sum(n_or.values())} (budget 80,000): {json.dumps(n_or)}.")
    A("- Full timeline: the status log in section 8.\n")
    A("## 1. X2: whole conversations — does the inside change sharply after the Assistant's decisive replies?\n")
    A(note("x2"))
    A("\n**Plots** (one line per version; rows = blocks; columns = aligned at the start of reply 1, reply 2, turn 3):\n")
    for m in ("S", "SB", "parent", "ctrl_A_s0", "ctrl_B_s0"):
        A(f"- `{m}`: [conduct](plots/x2_conduct_{m}.png), [Assistant axis](plots/x2_axis_{m}.png), [J++ bee](plots/x2_bee_{m}.png)")
    A("\n![S conduct](plots/x2_conduct_S.png)\n")
    A("### Sudden-or-gradual table\n")
    A(inc("x2_sudden.md"))
    A("\n### Landmark readouts (oracle lens)\n")
    A(x2lm_tables())
    A("\n## 2. X2b: the model's own decisive moment\n")
    A(note("x2b"))
    A(inc("x2b.md"))
    A("\n## 3. X7: other training runs of the same recipe\n")
    A(note("x7"))
    A(inc("x7.md"))
    A("\n### X2 trace for the seed models\n")
    A(inc("x7_sudden.md"))
    A("\n## 4. X3: PCA of activation sets\n")
    A(note("x3"))
    A(inc("x3_pca.md"))
    A("\n### Lens readings of the directions\n")
    A(x3_dir_tables())
    A("\n## 5. X4: the Assistant axis\n")
    A(note("x4"))
    A(inc("x4_axis.md"))
    A("\n## 6. X5 tries\n")
    A(note("x5"))
    for f in ("x5_notrig.md", "x5_moreblocks.md", "x5_yesno.md", "x5_extra.md", "x5_attn.md", "x5_sb48.md"):
        if os.path.exists(f"{R}/results/{f}"):
            A(inc(f))
    A("\nEvery try, with its prediction written before it ran: `tries.md`.\n")
    A("## 7. Readout notes (summary)\n")
    A(note("readouts"))
    A("\nFull notes: `readout_notes.md`; word tallies: `results/x1_tallies.md`.\n")
    A("## 8. What went wrong or was changed; settings and provenance\n")
    A("### Status log\n")
    A(st.split("\n", 1)[1] if "\n" in st else st)
    A("\n### Deviations\n")
    A(dev)
    A("\n### Settings and provenance\n")
    A(note("provenance"))
    open(f"{R}/README.md", "w").write("\n".join(L) + "\n")
    print("README", len(L), "blocks", time.strftime("%H:%M:%S"))


if __name__ == "__main__":
    main()
