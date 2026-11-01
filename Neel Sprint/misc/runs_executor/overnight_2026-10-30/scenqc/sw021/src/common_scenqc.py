"""sw021 scenario-QC: shared loaders and the primary habit label (copied from sw021 src/recompute21_analysis.py, the
analysis pass's recompute: consensus of both judges on rows where STRICT and the lexicon disagree or the scenario is
sw019 fp-flagged; STRICT elsewhere). CPU only, read-only on every input."""
import json, sys
from collections import defaultdict

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

RUN = "/workspace/runs_executor/sw021"
SW019 = "/workspace/runs_executor/sw019"
DATA19 = "/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data"
OUTDIR = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw021"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
MODELS = ("hdA0", "hdB0")
READOUTS = ("forced", "free")
DIRS = ("fwd", "rev")  # fwd = remove (recipient self-hostile <- donor user-hostile); rev = induce
DIRNAME = {"fwd": "remove", "rev": "induce"}


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def load_rows():
    return {rd: [r for m in MODELS for r in jl(f"{RUN}/{rd}_{m}.jsonl")] for rd in READOUTS}


def load_judged():
    J = defaultdict(dict)
    for rd in READOUTS:
        for l in open(f"{RUN}/judged_{rd}.jsonl"):
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r.get("error") is None and all(r.get(f + "_w") is not None for f in ("bee", "crow", "helpfulness", "fluency", "hostility")):
                J[r["key"]][r["judge"]] = r
    return J


def load_fp():
    return json.load(open(f"{SW019}/part2/fp/fp_flags.json"))


def role(lab, m):
    h = HELPER[m]
    return {"none": "neither", "both": "both"}.get(lab, "helper" if lab == h else "rival")


def make_labeler(J, fp_set):
    def judge_lab(k, m):
        j = J.get(k)
        if not j or "glm" not in j or "deepseek" not in j:
            return None
        b = (float(j["glm"]["bee_w"]) + float(j["deepseek"]["bee_w"])) / 2
        c = (float(j["glm"]["crow_w"]) + float(j["deepseek"]["crow_w"])) / 2
        return role("both" if b > 5 and c > 5 else "bee" if b > 5 else "crow" if c > 5 else "none", m)

    def lab(r):
        s = role(LB.strict_label(r["text"]), r["model"])
        if LB.disagree(r["text"]) or r["scenario"] in fp_set:
            j = judge_lab(r["key"], r["model"])
            return j if j is not None else s
        return s
    return lab
