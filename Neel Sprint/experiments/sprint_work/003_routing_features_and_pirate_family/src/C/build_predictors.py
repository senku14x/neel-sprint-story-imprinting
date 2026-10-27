"""sw003 Part C: frozen parent-only predictors over the census roles, rebuilt from sw001's saved parent capture, and the
frozen curt-but-helpful role list. Run once, before any hs census output exists.
  P1       axis coordinate of the parent's last-prompt-token state at L32 (trigger rows), mean over the role's 20 scripts
  P4_disp  projection on the unit disposition direction (helpful - unhelpful 2x2 personas' last-token means, focused set)
  P4_tone  projection on the unit tone direction (warm - curt)
           (all three exactly as sw001 analyze_p1.py lines 160-206; verified against sw001's saved p1_results.json)
  P5       sw001's: judge similarity to helper_assistant_like minus helper_dismissive (sw001 rows, unchanged)
  P5s      new:     judge similarity to helper_assistant_like (sw001 rows) minus helper_sarcastic (out/out_p5s_textsim.jsonl)
  P6       prompt tokens (sw001's)
Curt-but-helpful roles (frozen rule): census roles (animal roles excluded) with P4_tone BELOW the median (curt half) AND
P4_disp AT OR ABOVE the median (helpful half), medians over the 271 non-animal census roles.
  /root/venvs/si/bin/python build_predictors.py -> predictors.json, curt_helpful_roles.json (+ sha256 printed)"""
import hashlib, json, os, sys
from collections import defaultdict

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src")
import common_sw as C  # noqa: E402

torch.set_num_threads(8)
L32 = [16, 24, 32, 40, 48].index(32)


def textsim(path, subs):
    t = defaultdict(lambda: defaultdict(list))
    for l in open(path):
        r = json.loads(l)
        if not r.get("error") and r.get("sub") in subs and r.get("similarity") is not None:
            t[r["id"].split("||")[1]][r["sub"]].append(r["similarity"])
    return t


def main():
    D = torch.load(C.DIRECTIONS, weights_only=False, mmap=True)
    axis = D["unit"]["axis"][32].float()
    last = {}
    for f in C.capture_files(f"{C.RUN_B2}/p1/capture", "parent"):
        z = torch.load(f, weights_only=False)
        for k, t in z["means"].get("last", {}).items():
            last[k] = t[L32].float()
    per = defaultdict(list)
    for k, v in last.items():
        _, group, key, trig, sid = k.split("|")
        if trig == "trig":
            per[(group, key)].append(v)
    mean = {k: torch.stack(v).mean(0) for k, v in per.items()}
    g = lambda names: torch.stack([mean[("focused", n)] for n in names]).mean(0)
    HELP = ["helpful_warm_p0", "helpful_warm_p1", "helpful_curt_v3", "helpful_curt_v4"]
    UNH = ["unhelpful_warm_p0", "unhelpful_warm_p1", "unhelpful_curt_p0", "unhelpful_curt_p1"]
    WARM = ["helpful_warm_p0", "helpful_warm_p1", "unhelpful_warm_p0", "unhelpful_warm_p1"]
    CURT = ["helpful_curt_v3", "helpful_curt_v4", "unhelpful_curt_p0", "unhelpful_curt_p1"]
    disp = g(HELP) - g(UNH); tone = g(WARM) - g(CURT)
    disp, tone = disp / disp.norm(), tone / tone.norm()
    P1 = {k: float(np.mean([float(v @ axis) for v in per[k]])) for k in per}
    roles = C.roles()
    t5 = textsim("/root/runs/sw001/judge/out_p1_textsim.jsonl", ("assistant_like", "dismissive"))
    t5s = textsim(f"{HERE}/out/out_p5s_textsim.jsonl", ("sarcastic",))
    saved = json.load(open(f"{C.RES}/p1_results.json"))["predictors"]["by_persona"]
    out, err = {}, defaultdict(float)
    for group, key in per:
        pk = f"{group}|{key}"
        tkey = f"role:{key}" if group == "census" else key
        e = dict(P1=P1[(group, key)], P4_disp=float(mean[(group, key)] @ disp), P4_tone=float(mean[(group, key)] @ tone))
        ta, ts = t5.get(tkey, {}), t5s.get(tkey, {})
        e["P5"] = float(np.mean(ta["assistant_like"]) - np.mean(ta["dismissive"])) if ta.get("assistant_like") and ta.get("dismissive") else None
        e["P5s"] = float(np.mean(ta["assistant_like"]) - np.mean(ts["sarcastic"])) if ta.get("assistant_like") and ts.get("sarcastic") else None
        e["sim_sarcastic"] = float(np.mean(ts["sarcastic"])) if ts.get("sarcastic") else None
        e["P6"] = saved.get(pk, {}).get("P6")
        e["animal_role"] = group == "census" and key in C.ANIMAL_ROLES
        for p in ("P1", "P4_disp", "P4_tone", "P5"):
            if pk in saved and saved[pk].get(p) is not None and e[p] is not None:
                err[p] = max(err[p], abs(e[p] - saved[pk][p]))
        out[pk] = e
    n_census = sum(1 for k in out if k.startswith("census|"))
    assert n_census == len(roles) == 274, (n_census, len(roles))
    print("max |rebuilt - sw001 saved|:", dict(err))
    assert all(v < 1e-3 for v in err.values()), err
    meta = dict(source="sw001 parent capture /workspace/runs_executor/sw001_box2/p1/capture (L32, last prompt token, trigger rows)",
                directions=C.DIRECTIONS, cos_disp_tone=float(disp @ tone), rebuild_max_abs_err=dict(err),
                p5s_character="Story Imprinting App. F.2 helper_sarcastic (paper.txt 3808-3810), verbatim",
                p5s_definition="mean judge sim(role, helper_assistant_like) - mean judge sim(role, helper_sarcastic); both judges pooled",
                sign_convention="every predictor oriented so that larger = more helper-like (P4_tone larger = warmer)")
    json.dump(dict(meta=meta, by_persona=out), open(f"{HERE}/predictors.json", "w"), indent=1)
    keys = sorted(k[7:] for k in out if k.startswith("census|") and not out[k]["animal_role"])
    mt = float(np.median([out[f"census|{k}"]["P4_tone"] for k in keys])); md = float(np.median([out[f"census|{k}"]["P4_disp"] for k in keys]))
    ch = [k for k in keys if out[f"census|{k}"]["P4_tone"] < mt and out[f"census|{k}"]["P4_disp"] >= md]
    json.dump(dict(rule="non-animal census roles with P4_tone < median (curt half) and P4_disp >= median (helpful half); medians over the 271 non-animal census roles",
                   median_P4_tone=mt, median_P4_disp=md, n=len(ch), roles=ch), open(f"{HERE}/curt_helpful_roles.json", "w"), indent=1)
    for f in ("predictors.json", "curt_helpful_roles.json"):
        print(f, hashlib.sha256(open(f"{HERE}/{f}", "rb").read()).hexdigest())
    print("census roles", n_census, "non-animal", len(keys), "curt-helpful", len(ch), "P5s present", sum(1 for k in out if out[k]["P5s"] is not None))


if __name__ == "__main__":
    main()
