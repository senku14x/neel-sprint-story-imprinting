"""Write r02/README.md from the result files (numbers only). Hand-written parts come from r02/notes/:
  status.md   the Status section (top of the README)
  notes.md    code fixes, deviations, odd things (appended under "Notes")
Missing pieces are marked "pending" / "not run".
  python make_readme.py
"""
import collections
import glob
import json
import math
import statistics
from pathlib import Path

R = Path("/workspace/e04/r02")
G = Path("/workspace/e04/gen/r02")
L = []


def jl(p):
    return [json.loads(l) for l in open(p)] if Path(p).exists() else []


def jload(p, default=None):
    return json.load(open(p)) if Path(p).exists() else default


def rd(p):
    return Path(p).read_text().strip() if Path(p).exists() else ""


def wilson(k, n, z=1.959964):
    if not n:
        return (float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def f(x, d=3):
    return "–" if x is None else (f"{x:.{d}f}" if isinstance(x, float) else str(x))


L += ["# E04 R02: Qwen3.6-27B trained on Qwen-written stories (`a2`, `a5b`); health checks at steps 125 and 250", "",
      "*Experiment E04 (content/voice split), run R02, brief v1.0 (25 Oct 2026, 05:55 Taipei). 3× H100 80 GB on E01's network volume. "
      "Numbers only: no interpretation.*", ""]
L += ["## Status", "", rd(R / "notes/status.md") or "- In progress; see `STATUS.md`.", ""]

# ---------------------------------------------------------------- summary of checks
L += ["## Health checks and decisions", ""]
REF = {"untrained model (reference)": ("2–4/50", "0.605", "–", "–"),
       "E02 step-125 controls (reference)": ("–", "1.096 / 1.125", "0.0332 / 0.0352", "0.289 / 0.300"),
       "teammate's 001 models, step 125 (reference)": ("98–100%", "1.10–1.15", "0.033–0.037", "0.28–0.33"),
       "E03 Haiku paraphrases, step 125 (reference)": ("50/50", "1.230", "0.0422", "0.370"),
       "teammate's generator-2 model (reference)": ("5/50", "0.698", "–", "0.171")}
L += ["| Check | Model | Garbled / 50 [95% Wilson] | Mean consensus fluency | Chat entropy | Chat tail20 | Chat KL(parent‖model) | Decision |",
      "|---|---|---|---|---|---|---|---|"]
for name in ["setup", "a2_s125", "a5b_s125", "a2_s250", "a5b_s250", "public_si27_hc_db"]:
    s = jload(R / f"checks/{name}/summary.json")
    dec = rd(R / f"checks/{name}/decision.txt")
    if not s:
        if (R / f"checks/{name}").exists():
            L.append(f"| {name} | – | pending | | | | | {dec} |")
        continue
    for m, g in s["garble"].items():
        h = s["health"].get(m, {}).get("chat", {})
        lo, hi = g["wilson95"]
        L.append(f"| {name} | `{m}` | {g['garbled']}/{g['n']} [{100 * lo:.1f}%, {100 * hi:.1f}%] | {f(g['mean_fluency'], 2)} | "
                 f"{f(h.get('ent_f'))} | {f(h.get('tail20_f'), 4)} | {f(h.get('kl_pf'))} | {dec if m != 'parent' and not m.startswith('e02') else ''} |")
for k, (g, e, t, kl) in REF.items():
    L.append(f"| reference | {k} | {g} | | {e} | {t} | {kl} | |")
L += ["", "Rules (brief step 7): setup — parent chat entropy 0.55–0.65, parent garbled ≤ 8/50, positive control (E02 `ctrl_B` step 125) "
      "garbled ≥ 40/50; step 125 and step 250 — garbled ≤ 8/50 healthy (training continues), > 8/50 damaged (training killed at once). "
      "The health panel is reported, not used as a rule.", ""]
setup = jload(R / "checks/setup/summary.json")
if setup:
    pe = setup["health"].get("parent", {}).get("chat", {}).get("ent_f")
    pg = setup["garble"].get("parent", {}); cg = setup["garble"].get("e02_ctrl_B_s125", {})
    L += ["| Setup check | Rule | Value | Pass |", "|---|---|---|---|",
          f"| parent chat entropy | 0.55–0.65 | {f(pe, 4)} | {'yes' if pe is not None and 0.55 <= pe <= 0.65 else 'no'} |",
          f"| parent garbled | ≤ 8 of 50 | {pg.get('garbled')}/{pg.get('n')} | {'yes' if pg and pg['garbled'] <= 8 else 'no'} |",
          f"| positive control garbled | ≥ 40 of 50 | {cg.get('garbled')}/{cg.get('n')} | {'yes' if cg and cg['garbled'] >= 40 else 'no'} |", ""]
L += ["SamplingParams as processed by the engine, first request per model:", "",
      "| Check | Model | temperature | top_p | top_k | min_p | max_tokens | seed |", "|---|---|---|---|---|---|---|---|"]
for name in ["setup", "a2_s125", "a5b_s125", "a2_s250", "a5b_s250", "public_si27_hc_db"]:
    s = jload(R / f"checks/{name}/summary.json")
    for m, p in (s or {}).get("sampling_params_processed", {}).items():
        L.append(f"| {name} | `{m}` | {p.get('temperature')} | {p.get('top_p')} | {p.get('top_k')} | {p.get('min_p')} | {p.get('max_tokens')} | {p.get('seed')} |")
L.append("")
L += ["Health panel, both panels (`health.py`, token-weighted):", "", "| Check | Model | Panel | Tokens | Entropy | Tail20 | KL(parent‖model) |",
      "|---|---|---|---|---|---|---|"]
for name in ["setup", "a2_s125", "a5b_s125", "a2_s250", "a5b_s250", "public_si27_hc_db"]:
    s = jload(R / f"checks/{name}/summary.json")
    for m, panels in (s or {}).get("health", {}).items():
        for pn, v in panels.items():
            L.append(f"| {name} | `{m}` | {pn} | {v['tokens']} | {f(v['ent_f'], 4)} | {f(v['tail20_f'], 4)} | {f(v['kl_pf'], 4)} |")
L.append("")

# ---------------------------------------------------------------- generation
L += ["## Step 3: A2 for all 8,000 rows", ""]
rep = jload(G / "A2_report.json")
if rep:
    L += ["| Stage | Specs entering | First try passed | Final passed (≤ 3 tries) | Accepted on try 1 / 2 / 3 | Tries sampled | Output tokens |",
          "|---|---|---|---|---|---|---|"]
    for st in ("stage1", "stage2"):
        x = rep[st]; a = x["accepted_on_try"]
        L.append(f"| {st[-1]} | {x['specs']} | {x['first_try_pass']} ({100 * x['first_try_rate']:.1f}%) | {x['final_pass']} ({100 * x['final_rate']:.1f}%) | "
                 f"{a.get('1', a.get(1, 0))} / {a.get('2', a.get(2, 0))} / {a.get('3', a.get(3, 0))} | {x['tries_sampled']} | {x['out_tokens']:,} |")
    L += ["", f"**Rows with no accepted story after 3 tries: {rep['no_story_n']} of {rep['specs']} ({100 * rep['no_story_rate']:.2f}%)** "
          f"(stop rule: > 5%); per cell {rep['no_story_per_cell']}. These rows keep the paper's original story in both arms.", "",
          "Failure reasons, every evaluated try:", ""]
    for st in ("stage1", "stage2"):
        L.append(f"- stage {st[-1]}: " + ", ".join(f"{k} {v}" for k, v in rep[st]["fail_reasons"].items()))
    L.append("")
sw = jload(R / "data/example_swaps.json", {})
L += [f"Few-shot example swaps (rows that are one of R01's 20 examples; replacement drawn with `random.Random(20261025)` from R01's eligible "
      f"list for the cell minus the 5 examples): {len(sw)}.", "", "| Row | Cell | Position | Replaced example (row) | Replacement (row, words) |", "|---|---|---|---|---|"]
for k, v in sw.items():
    L.append(f"| {k} | {v['cell']} | {v['position_in_cell']} | {v['removed_row']} | {v['replacement_row']} ({v['replacement_words']}) |")
L.append("")

# ---------------------------------------------------------------- A5b
L += ["## Step 4: A5b (Claude Sonnet 5.5 line-level edits of A2, Message Batches)", ""]
E = jl(R / "a5b/edits_a5b_sonnet.jsonl")
if E:
    st = collections.Counter(r["status"] for r in E)
    acc = sum(len(r["accepted"]) for r in E); rej = sum(len(r["rejected"]) for r in E)
    why = collections.Counter(x["why"] for r in E for x in r["rejected"])
    hw = [100 * (r["words_changed"] - r.get("words_changed_narration", 0)) / max(1, r["words_helper_lines"]) for r in E]
    L += [f"- Stories sent: {len(E)}. Editor status: " + ", ".join(f"{k} {v}" for k, v in st.most_common()) + ".",
          f"- Stories with ≥ 1 accepted edit: {sum(bool(r['accepted']) for r in E)}; edits applied {acc} (narration {sum(r.get('narration_edits', 0) for r in E)}); "
          f"edits rejected {rej}.",
          f"- Median share of the helper's words changed: {statistics.median(hw):.1f}%.",
          "- Rejection reasons: " + ", ".join(f"{k} {v}" for k, v in why.most_common()) + ".",
          f"- Rows whose editing failed (reply missing or not parsed after the resubmission) keep A2's story: {sum(r['status'] != 'ok' for r in E)}.", ""]
    for b in sorted(glob.glob(str(R / "a5b/batch_*.json"))):
        x = jload(b)
        L.append(f"- Batch `{Path(b).stem}`: id `{x['id']}`, {x['n']} requests, estimate before submitting ${x['est_cost']:.2f}.")
    L.append("")
summ = rd(R / "a5b/A5_summary.md")
if summ:
    L += ["The editor script's own summary (`a5b/A5_summary.md`):", "", "<details><summary>A5_summary.md</summary>", "", summ, "", "</details>", ""]
tr = {a: jload(R / f"data/train_{a}_summary.json") for a in ("a2", "a5b")}
L += ["## Step 5: training files and loss sample", ""]
for a, t in tr.items():
    if t:
        L.append(f"- `data/train_{a}.jsonl`: {t['rows']} rows, sha256 `{t['sha256']}`; sources " + ", ".join(f"{k} {v}" for k, v in t["source_counts"].items())
                 + f"; user turns identical {t['user_turn_identical']}/{t['rows']}.")
L.append("")
lo = {a: jl(R / f"results/loss/{a}.jsonl") for a in ("A0", "a2", "a5b")}
if any(lo.values()):
    L += ["Untrained Qwen3.6-27B, R01's `loss_persona.py` (unchanged), 200 rows (`sorted(random.Random(20261025).sample(range(8000), 200))`). "
          "Each arm's text is exactly its training-file text.", "",
          "| Version | Stories | Tokens | Loss, token-weighted | Dialogue | Narration | R01 (60 stories) |", "|---|---|---|---|---|---|---|"]
    r01 = {"A0": "2.84", "a2": "1.64", "a5b": "1.72"}
    for a, rows in lo.items():
        if not rows:
            continue
        n = sum(r["n_tokens"] for r in rows)
        dl = sum(r["sum_dlg"] for r in rows) / max(1, sum(r["n_dlg"] for r in rows))
        nr = sum(r["sum_narr"] for r in rows) / max(1, sum(r["n_narr"] for r in rows))
        L.append(f"| {'original (A0)' if a == 'A0' else a} | {len(rows)} | {n:,} | {sum(r['sum_nll'] for r in rows) / n:.3f} | {dl:.3f} | {nr:.3f} | {r01[a]} |")
    ex = jload(R / "results/loss/sample_extra.json")
    if ex:
        e = ex["excluding_paper_story_rows"]
        L += ["", f"{ex['rows_with_paper_story']} of the 200 sampled rows have no A2 story, so they carry the paper's story in `a2` and `a5b`. Without those rows "
              f"({e['a2']['n_rows']} stories): original {e['A0']['loss']:.3f}, a2 {e['a2']['loss']:.3f}, a5b {e['a5b']['loss']:.3f}."]
    L.append("")

# ---------------------------------------------------------------- training
L += ["## Step 6: training", ""]
L += ["| Arm | Run | Steps logged | First-10-step mean loss | Loss step 125 | Loss step 250 | Wall time, train loop | Peak allocated GB | Process start → exit |",
      "|---|---|---|---|---|---|---|---|---|"]
for a in ("a2", "a5b"):
    for rdn in (f"{a}_s0", f"{a}_s0_mb2"):
        tl = jl(R / f"runs/{rdn}/train_log.jsonl")
        if not tl:
            continue
        by = {r["step"]: r for r in tl}
        times = rd(R / f"logs/train_{a}.times").replace("\n", "; ")
        L.append(f"| {a} | `{rdn}` | {len(tl)} | {statistics.mean(r['loss'] for r in tl[:10]):.4f} | {f(by.get(125, {}).get('loss'), 4)} | "
                 f"{f(by.get(250, {}).get('loss'), 4)} | {tl[-1]['elapsed'] / 60:.1f} min | {max(r['peak_gb'] for r in tl)} | {times} |")
L.append("")
L += ["No run ran out of memory: both used micro-batch 4 × accumulation 8 throughout (no 2 × 16 restart).", "",
      "Snapshots checked (sha256 of `adapter_model.safetensors`; paths at check time — `a2`'s are now in `adapters/`, `a5b`'s were deleted):", ""]
for p in sorted(glob.glob(str(R / "checks/*/adapter_hash.txt"))):
    for line in open(p):
        if "safetensors" in line:
            h, path = line.split()
            L.append(f"- `{path}`: `{h}`")
L += ["", rd(R / "notes/adapters.md"), ""]

# ---------------------------------------------------------------- evals
L += ["## Step 8: imprinting evaluations (`a5b` only, only if healthy at steps 125 and 250)", "", rd(R / "results/evals/evals.md") or "Not run (see Status).", ""]
L += ["## Step 9 (optional): public replication's `si27_hc_db` adapter", "", rd(R / "results/public_check.md") or "Not run (see Status).", ""]

# ---------------------------------------------------------------- spend
L += ["## Spend and GPU time", "", rd(R / "results/spend.md") or "pending", ""]
L += ["## Notes: code fixes, deviations, odd things", "", rd(R / "notes/notes.md"), ""]
L += ["## Files", "", rd(R / "notes/files.md"), ""]
open(R / "README.md", "w").write("\n".join(L))
print(f"README.md written ({len(L)} lines)")
