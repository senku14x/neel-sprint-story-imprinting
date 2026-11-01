#!/usr/bin/env python3
"""E04 step 0b: loss and persona numbers for the A5 sets, next to R01's A0, A1, A2 and A3b, as markdown.

Reads R01-format loss rows (scripts/loss_persona.py output: results/loss/<arm>.jsonl) and the A5 judge files written by
a5_stage0.py. Same definitions as R01's analyze.py: token-weighted loss over the stories present in every compared arm;
paired difference with a bootstrap 95% interval over specs (2,000 resamples, seed 20261025); gap closed = (A0 - arm) / (A0 - A1).

  python3 a5_loss_summary.py --loss /workspace/e04/results/loss --a5 /workspace/e04/a5 --r01-judge /workspace/e04/results/judge/full
Writes <a5>/A5_loss.md and prints it.
"""
import argparse
import json
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--loss", required=True)
ap.add_argument("--a5", required=True)
ap.add_argument("--r01-judge", required=True)
ap.add_argument("--sets", default="a5a_sonnet,a5a_haiku,a5b_sonnet,a5b_haiku")
ap.add_argument("--loss-suffix", default="", help="loss files are <set><suffix>.jsonl, e.g. _v2 for a second run")
args = ap.parse_args()

REF = ["A0", "A1", "A2", "A3b"]
SETS = [s for s in args.sets.split(",") if s]


def load(p):
    p = Path(p)
    return {json.loads(l)["spec_id"]: json.loads(l) for l in open(p)} if p.exists() else {}


L = {a: load(Path(args.loss) / f"{a}{args.loss_suffix if a in SETS else ''}.jsonl") for a in REF + SETS}
missing = [a for a in REF + SETS if not L[a]]
ids = sorted(set.intersection(*[set(L[a]) for a in REF + SETS if L[a]]))
rng = np.random.default_rng(20261025)
IDX = rng.integers(0, len(ids), size=(2000, len(ids)))
SPLIT = {"all": ("sum_nll", "n_tokens"), "dlg": ("sum_dlg", "n_dlg"), "narr": ("sum_narr", "n_narr")}


def arr(a, split):
    n, d = SPLIT[split]
    return np.array([L[a][i][n] for i in ids]), np.array([L[a][i][d] for i in ids])


def tw(a, split="all"):
    x, y = arr(a, split)
    return x.sum() / y.sum()


def boot(f):
    return np.percentile([f(ix) for ix in IDX], [2.5, 97.5])


def diff(a, ref):
    an, ad = arr(a, "all")
    rn, rd = arr(ref, "all")
    pt = an.sum() / ad.sum() - rn.sum() / rd.sum()
    lo, hi = boot(lambda ix: an[ix].sum() / ad[ix].sum() - rn[ix].sum() / rd[ix].sum())
    return f"{pt:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def gap(a):
    x = {k: arr(k, "all") for k in ("A0", "A1", a)}
    g = lambda s: (s["A0"] - s[a]) / (s["A0"] - s["A1"])
    pt = g({k: v[0].sum() / v[1].sum() for k, v in x.items()})
    lo, hi = boot(lambda ix: g({k: v[0][ix].sum() / v[1][ix].sum() for k, v in x.items()}))
    return f"{pt:.2f} [{lo:.2f}, {hi:.2f}]"


def persona(a):
    """Helpful helper on the helpful vector; dismissive helper on the dismissive vector (pre-trigger helper lines)."""
    rows = [L[a][i] for i in ids if L[a][i].get("persona_tokens")]
    h = [r["proj_helpful"] for r in rows if r["cell"].startswith("assistant-like")]
    d = [r["proj_dismissive"] for r in rows if r["cell"].startswith("dismissive")]
    return (f"{np.mean(h):.2f}" if h else "–"), (f"{np.mean(d):.2f}" if d else "–")


def assist(a):
    p = (Path(args.r01_judge) / f"tone_{a}.jsonl") if a in REF else (Path(args.a5) / f"judge_{a}.jsonl")
    rows = [r for r in load(p).values() if r.get("parsed") and r["spec_id"] in ids and r["cell"].startswith("assistant-like")]
    return sum(r["helper_sounds_like_assistant"] == "yes" for r in rows), len(rows)


out = ["# A5: Qwen's loss on the edited stories", "",
       f"Untrained Qwen3.6-27B, R01's loss pass (training prompt, story tokens plus <|im_end|>). {len(ids)} specs present in every arm. "
       "Brackets: bootstrap 95% intervals over specs. Persona: E01 R06 vectors, block 32, the helper's lines before the trigger.", ""]
if missing:
    out += [f"**Missing loss files:** {', '.join(missing)}", ""]
out += ["| Version | Loss, all | Dialogue | Narration | vs paper (A0) | vs A2 | vs A3b | Gap closed | Helpful helper on helpful vector | Dismissive helper on dismissive vector | \"Sounds like an assistant\" (helpful cells) |",
        "|---|---|---|---|---|---|---|---|---|---|---|"]
for a in REF + SETS:
    if not L[a]:
        continue
    ph, pd = persona(a)
    k, n = assist(a)
    out.append(f"| {a} | {tw(a):.3f} | {tw(a, 'dlg'):.3f} | {tw(a, 'narr'):.3f} | {'—' if a == 'A0' else diff(a, 'A0')} | "
               f"{'—' if a == 'A2' else diff(a, 'A2')} | {'—' if a == 'A3b' else diff(a, 'A3b')} | "
               f"{'0 (definition)' if a == 'A0' else '1 (definition)' if a == 'A1' else gap(a)} | {ph} | {pd} | {k}/{n} |")
out += ["", "**Rule check (E04-D05, proposed rule; not a verdict):** a set joins the step-125 kill test as a third run if its helpful "
            "helpers sound like an assistant in at most 6 of about 29 stories and its loss is at least 0.15 below A3b's.", ""]
for s in SETS:
    if not L[s]:
        continue
    k, n = assist(s)
    d = tw(s) - tw("A3b")
    voice_ok = k <= round(6 * n / 29) if n else False
    out.append(f"- {s}: sounds like an assistant {k}/{n} ({'within' if voice_ok else 'over'} the bar); loss {d:+.3f} vs A3b "
               f"({'at least 0.15 lower' if d <= -0.15 else 'not 0.15 lower'}) → {'meets' if voice_ok and d <= -0.15 else 'does not meet'} the rule")
text = "\n".join(out) + "\n"
open(Path(args.a5) / "A5_loss.md", "w").write(text)
print(text)
