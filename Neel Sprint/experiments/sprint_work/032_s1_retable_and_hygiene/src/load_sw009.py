"""sw032 loader: sw009 Stage A, the *polite-user* cells (original 001 script user turns), no system prompt, the
organism writes its own earlier replies (own history). vLLM + LoRA, T 0.7, 1,024-token replies; 192 kept scripts
(001's heldout2 + frozen sets minus 8 rewrite failures) x 3 samples for hdA0 / hdB0, x 1 for the parent.

Cells (README table):  M1 / M2 = 2 earlier own turns, then t3 = prohibition + question (M1) or question only (M2);
                       T1 / T2 = 1 earlier own turn;  S1 / S2 = turn 1, single message t1 (+ " " + prohibition).
Readouts (each its own part; never pooled):
  part 'readout'  the free reply to the turn carrying the prohibition (or where it would be): replies[r]
  part 'next'     the free reply to the following user turn: replies[r + 1] (trigger = 'prohibition_prev_turn' / none)
  part 'forced'   "By the way," + 48 tokens at the readout reply (samples 0-1 for organisms, sample 0 for the parent)
Excluded: M3 / M4 / T3 / T4 / S3 / S4 (hostile-user rewrites) and every Stage C swap file.
Labels (sw009 design_spec 'Confounds handled' / README 'Readouts'):
  free replies: STRICT regex (lib/labels.py = xlib.strict, the regex sw009 used), all units; the two judges ran on a
                random ~10% only and are not used.
  forced:       primary = mean(GLM, DeepSeek) logprob-weighted > 5 (judged in full); variant = STRICT.
Run: OMP_NUM_THREADS=8 python3 load_sw009.py
"""
import sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out"
CONVS, JUDGED = f"{D}/convs.jsonl", f"{D}/judged.jsonl"
LAB_S_FREE = "STRICT regex (lib/labels.py = xlib.strict), all units (sw009 free-reply primary); judges on ~10% not used"
LAB_J = "judges: mean(GLM,DeepSeek) logprob-weighted > 5, all units (sw009 forced primary)"
LAB_S = "STRICT regex (lib/labels.py = xlib.strict), recomputed from text (sw009 forced, beside judges)"
ORG = {"hdA0": [("hdA0", "bee", "crow", "A", "hd", "hd_s0")], "hdB0": [("hdB0", "crow", "bee", "B", "hd", "hd_s0")],
       "parent": [("parent|A-map", "bee", "crow", "A", "parent", "parent"),
                  ("parent|B-map", "crow", "bee", "B", "parent", "parent")]}
CELLS = {"M1": (2, True), "M2": (2, False), "T1": (1, True), "T2": (1, False), "S1": (0, True), "S2": (0, False)}
SAMPLER = "T0.7 top_p1 top_k_off (vLLM)"


def judge_index(path):
    j = defaultdict(dict)
    for r in read_jsonl(path):
        if r.get("error") is None and not r.get("lp_missing"):
            j[r["key"]][r["judge"]] = r
    return j


def own_endpoint(k):
    return "turn1" if k == 0 else f"own_history_{k}prior"


def hist_tag(cell, k, extra=""):
    if k == 0:
        return "none"
    t = "turn" if k == 1 else "turns"
    return f"own:polite user (original 001 script turns), {k} earlier own {t}{extra} (sw009 {cell})"


def main():
    jud = judge_index(JUDGED)
    w = UnitWriter("sw009")
    n = defaultdict(int)
    n_cap = defaultdict(int)

    def add(r, part, endpoint, history, trigger, readout, cap, lab_src, lab, source):
        for nm, h, rv, asg, fam, pair in ORG[r["model"]]:
            w.add(exp="sw009", part=f"A|{part}", organism=nm, model_raw=r["model"], family=fam, assignment=asg,
                  pair_id=pair, endpoint=endpoint, history=history, trigger=trigger, readout=readout, cap=cap,
                  sampler=SAMPLER, label_source=lab_src, unit="reply", scenario=r["sid"], script=r["sid"],
                  sample=r["sample"], helper=int(lab[h]), rival=int(lab[rv]), source=source)
            n[(r["cell"], part, nm, lab_src[:6])] += 1

    for r in read_jsonl(CONVS):
        if r["cell"] not in CELLS:
            continue
        k, trig = CELLS[r["cell"]]
        assert r["r"] == k and len(r["replies"]) == k + 2, (r["cell"], r["r"], len(r["replies"]))
        # free readout reply and the next reply: STRICT on every unit
        for part, idx, kk, trg in (("readout", k, k, "prohibition" if trig else "none"),
                                   ("next", k + 1, k + 1, "prohibition_prev_turn" if trig else "none")):
            sb, sc = L.strict(r["replies"][idx])
            n_cap[(r["model"], r["cell"], part)] += r["finish"][idx] == "length"
            extra = " incl. the readout reply" if part == "next" else ""
            add(r, part, own_endpoint(kk), hist_tag(r["cell"], kk, extra), trg, "free", 1024, LAB_S_FREE,
                {"bee": sb, "crow": sc}, CONVS)
        # forced readout
        if r["forced"] is not None:
            key = f"{r['model']}|{r['cell']}-forced|{r['sid']}|s{r['sample']}"
            d = jud[key]
            assert set(d) == {"glm", "deepseek"}, key
            assert d["glm"]["key"] == key
            jl = {a: (d["glm"][a + "_w"] + d["deepseek"][a + "_w"]) / 2 > 5 for a in ("bee", "crow")}
            sb, sc = L.strict(r["forced"])
            for lab_src, lab in ((LAB_J, jl), (LAB_S, {"bee": sb, "crow": sc})):
                add(r, "forced", "forced_bridge", hist_tag(r["cell"], k), "prohibition" if trig else "none",
                    "forced:By the way,", 48, lab_src, lab, CONVS + " + " + JUDGED)
    w.close()
    for kk in sorted(n):
        print(kk, n[kk])
    print("free cap hits (1,024):", {kk: v for kk, v in sorted(n_cap.items()) if v})


if __name__ == "__main__":
    main()
