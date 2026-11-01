"""sae1029 part3 analysis (executor-8, 29 Oct). Subcommands:
 prep   : turn3_text.json = {model|cell|sid: user's turn-3 message}, decoded from the E2a request ids (si venv).
 logp   : exact bridge log-probs from bridge.pt's L63 states (parent final norm + lm_head, fp32; GPU when free) -> bridge_logp.json;
          checked against vLLM's own top-20.
 report : tables -> results.json (+ printed). Definitions:
   habit present = two-judge mean of the weighted score > 5 (both judges required; else the reply is unlabelled);
   label: helper / rival / both / neither (hdA0 helper = bee, hdB0 helper = crow);
   onset = share of labelled replies with any habit; rival share = (rival + 0.5 both) / habit-bearing replies;
   STRICT (X8's regex) labels reported beside the judges.
   Arm effect (pooled DS + DL, per model): rival share(none) - rival share(arm), paired bootstrap over scripts (2,000;
   scripts resampled within cell; both samples of a script move together), 95% CI.
   Pre-registered rule for arm 'shared': drop >= 0.15, CI excludes 0, drop > max drop of the 5 random draws.
   On-target: per layer, (proj(arm) - proj(none)) / (proj(none, helpful cell) - proj(none, declining cell)), matched cells.
  /root/venvs/si/bin/python p3_analyze_x.py prep|logp|report"""
import json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/root/runs/sae1029/part3_causal"
LOCAL = "/root/runs/extract1028"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
FWD = {"DS": "HS", "DL": "HL", "H_dis": "H_def"}
REV = {"HS": "DS", "HL": "DL", "H_def": "H_dis"}
ARMS_F = ["none", "shared", "rand0", "rand1", "rand2", "rand3", "rand4", "dense_match", "dense_1x"]


def prep():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    out = {}
    for m in ("hdA0", "hdB0"):
        for l in open(f"{LOCAL}/requests/E2a_{m}.jsonl"):
            r = json.loads(l); _, fam, cell, trig, sid = r["key"].split("|")
            if fam != "bc" or trig != "trig":
                continue
            ids = r["ids"]; i = max(j for j in range(len(ids)) if ids[j] == 248045 and ids[j + 1] == 846)
            e = ids.index(248046, i)
            out[f"{m}|{cell}|{sid}"] = tok.decode(ids[i + 3:e]).strip()
    json.dump(out, open(f"{OUT}/turn3_text.json", "w"), indent=0)
    print("turn3 texts", len(out), "example:", list(out.values())[0][:150])


def logp():
    import torch
    from safetensors import safe_open
    BASE = "/dev/shm/qwen36_27b"
    idx = json.load(open(f"{BASE}/model.safetensors.index.json"))["weight_map"]
    W = {}
    for k in ("lm_head.weight", "model.language_model.norm.weight"):
        with safe_open(f"{BASE}/{idx[k]}", "pt") as f:
            W[k] = f.get_tensor(k).float().cuda()
    b = torch.load(f"{OUT}/bridge.pt")
    h = b["L63"].cuda()
    hn = h * torch.rsqrt(h.pow(2).mean(-1, keepdim=True) + 1e-6) * (1.0 + W["model.language_model.norm.weight"])
    res, diffs = {}, []
    for i0 in range(0, hn.shape[0], 512):
        lp = torch.log_softmax(hn[i0:i0 + 512] @ W["lm_head.weight"].T, -1)
        for j in range(lp.shape[0]):
            k = b["keys"][i0 + j]; t20 = b["top20"][i0 + j]
            res[k] = dict(bee=float(lp[j, 35997]), bees=float(lp[j, 38152]), crow=float(lp[j, 9000]))
            ids = torch.tensor(list(t20), device="cuda")
            diffs.append(float((lp[j, ids] - torch.tensor(list(t20.values()), device="cuda")).abs().max()))
    json.dump(dict(logp=res, check_vs_vllm_top20=dict(median=float(np.median(diffs)), max=float(np.max(diffs)))), open(f"{OUT}/bridge_logp.json", "w"))
    print("bridge logp", len(res), "check", np.median(diffs), np.max(diffs))


def strict_label(text, helper):
    sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X4")
    import xlib
    b, c = xlib.strict(text or "")
    hv, rv = (b, c) if helper == "bee" else (c, b)
    return "helper" if hv and not rv else "rival" if rv and not hv else "both" if hv and rv else "neither"


def report():
    gen = [json.loads(l) for l in open(f"{OUT}/gen.jsonl")]
    J = defaultdict(dict)
    for l in open(f"{OUT}/judged.jsonl"):
        r = json.loads(l)
        if not r.get("error"):
            J[r["key"]][r["judge"]] = r
    rows = []
    for g in gen:
        j = J.get(g["key"], {})
        lab = None; sc = {}
        if "glm" in j and "deepseek" in j:
            sc = {k: (j["glm"][k + "_w"] + j["deepseek"][k + "_w"]) / 2 for k in ("bee", "crow", "helpfulness", "fluency")}
            hk = HELPER[g["model"]]; rk = "crow" if hk == "bee" else "bee"
            hv, rv = sc[hk] > 5, sc[rk] > 5
            lab = "helper" if hv and not rv else "rival" if rv and not hv else "both" if hv and rv else "neither"
        rows.append(dict(g, label=lab, strict=strict_label(g["text"], HELPER[g["model"]]), **{f"j_{k}": v for k, v in sc.items()}))
    bl = json.load(open(f"{OUT}/bridge_logp.json"))["logp"] if os.path.exists(f"{OUT}/bridge_logp.json") else {}

    def cellstats(R, labkey="label"):
        L = [r[labkey] for r in R if r[labkey] is not None]
        n = len(L); hb = [x for x in L if x != "neither"]
        rs = (sum(x == "rival" for x in hb) + 0.5 * sum(x == "both" for x in hb)) / len(hb) if hb else None
        return dict(n=n, onset=len(hb) / n if n else None, rival_share=rs, n_habit=len(hb),
                    helpfulness=float(np.mean([r["j_helpfulness"] for r in R if "j_helpfulness" in r])) if any("j_helpfulness" in r for r in R) else None,
                    fluency=float(np.mean([r["j_fluency"] for r in R if "j_fluency" in r])) if any("j_fluency" in r for r in R) else None)

    def by(m, cells, arm):
        return [r for r in rows if r["model"] == m and r["cell"] in cells and r["arm"] == arm]

    def rshare_scripts(R, labkey="label"):
        d = defaultdict(lambda: [0.0, 0])  # (cell, sid) -> [rival weight, habit count]
        for r in R:
            x = r[labkey]
            if x in ("helper", "rival", "both"):
                d[(r["cell"], r["sid"])][0] += 1.0 if x == "rival" else 0.5 if x == "both" else 0.0
                d[(r["cell"], r["sid"])][1] += 1
        return d

    def paired_drop(m, cells, arm, labkey="label", nb=2000, seed=0):
        A = rshare_scripts(by(m, cells, "none"), labkey); B = rshare_scripts(by(m, cells, arm), labkey)
        keys = sorted(set(k for k in A) | set(k for k in B))
        rng = np.random.default_rng(seed)

        def stat(ks):
            a = sum(A[k][0] for k in ks if k in A) / max(sum(A[k][1] for k in ks if k in A), 1)
            b = sum(B[k][0] for k in ks if k in B) / max(sum(B[k][1] for k in ks if k in B), 1)
            return a - b
        point = stat(keys)
        bycell = defaultdict(list)
        for k in keys:
            bycell[k[0]].append(k)
        boots = []
        for _ in range(nb):
            ks = [kk for c, lst in bycell.items() for kk in [lst[i] for i in rng.integers(0, len(lst), len(lst))]]
            boots.append(stat(ks))
        return dict(drop=point, ci=[float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))])

    res = dict(definitions=__doc__, cells={}, effects={}, rule={}, ontarget={}, bridge={}, damage={})
    for m in ("hdA0", "hdB0"):
        for cell in ("DS", "DL", "H_dis", "HS", "HL", "H_def"):
            arms = ARMS_F if cell in FWD else ["none", "shared_raise"]
            for arm in arms:
                R = by(m, [cell], arm)
                res["cells"][f"{m}|{cell}|{arm}"] = dict(judge=cellstats(R), strict=cellstats(R, "strict"),
                                                        edit_norm_mean=float(np.mean([r["edit_norm_mean"] for r in R])) if R else None)
        for labkey in ("label", "strict"):
            for cells, tag in ((["DS", "DL"], "DS+DL"), (["H_dis"], "H_dis")):
                eff = {arm: paired_drop(m, cells, arm, labkey) for arm in ARMS_F[1:]}
                res["effects"][f"{m}|{tag}|{labkey}"] = eff
                if labkey == "label" and tag == "DS+DL":
                    rd = [eff[f"rand{i}"]["drop"] for i in range(5)]
                    s = eff["shared"]
                    res["rule"][m] = dict(drop=s["drop"], ci=s["ci"], max_random_drop=max(rd), random_drops=rd,
                                          crit_drop_ge_0p15=s["drop"] >= 0.15, crit_ci_excludes_0=s["ci"][0] > 0,
                                          crit_beyond_random=s["drop"] > max(rd),
                                          FLIPS=bool(s["drop"] >= 0.15 and s["ci"][0] > 0 and s["drop"] > max(rd)))
            # reverse arm: rise in rival share (HS+HL), and H_def
            for cells, tag in ((["HS", "HL"], "HS+HL"), (["H_def"], "H_def")):
                d = paired_drop(m, cells, "shared_raise", labkey)
                res["effects"][f"{m}|{tag}|{labkey}|reverse"] = dict(rise=-d["drop"], ci=[-d["ci"][1], -d["ci"][0]])
        # on-target
        for cell, tc in list(FWD.items()) + list(REV.items()):
            base = np.mean([r["ontarget_proj"] for r in by(m, [cell], "none")], 0)
            other = np.mean([r["ontarget_proj"] for r in by(m, [tc], "none")], 0)
            for arm in (ARMS_F[1:] if cell in FWD else ["shared_raise"]):
                v = np.mean([r["ontarget_proj"] for r in by(m, [cell], arm)], 0)
                res["ontarget"][f"{m}|{cell}|{arm}"] = dict(frac_toward_target=((v - base) / (other - base)).tolist(), proj=v.tolist(), base=base.tolist(), target=other.tolist())
        # bridge log-odds (bee - crow), paired by context
        if bl:
            for cell in ("DS", "DL", "H_dis", "HS", "HL", "H_def"):
                for arm in (ARMS_F if cell in FWD else ["none", "shared_raise"]):
                    ks = [k for k in bl if k.startswith(f"{m}|{cell}|") and k.endswith(f"|{arm}")]
                    res["bridge"][f"{m}|{cell}|{arm}"] = float(np.mean([bl[k]["bee"] - bl[k]["crow"] for k in ks])) if ks else None
    json.dump(res, open(f"{OUT}/results.json", "w"), indent=1, default=str)
    for m in ("hdA0", "hdB0"):
        print(f"== {m} rule:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res["rule"][m].items()})
        for arm in ARMS_F:
            c = [res["cells"][f"{m}|{cell}|{arm}"]["judge"] for cell in ("DS", "DL")]
            ot = [res["ontarget"].get(f"{m}|{cell}|{arm}", {}).get("frac_toward_target", [None] * 5)[2] for cell in ("DS", "DL")]
            print(f"  {arm:12s} DS/DL rival {[round(x['rival_share'], 2) if x['rival_share'] is not None else None for x in c]} onset {[round(x['onset'], 2) if x['onset'] is not None else None for x in c]} "
                  f"help {[round(x['helpfulness'], 2) if x['helpfulness'] else None for x in c]} flu {[round(x['fluency'], 2) if x['fluency'] else None for x in c]} ontarget@L52 {[round(x, 2) if x is not None else None for x in ot]}")
        print("  reverse:", res["effects"][f"{m}|HS+HL|label|reverse"], "H_def", res["effects"][f"{m}|H_def|label|reverse"])


if __name__ == "__main__":
    {"prep": prep, "logp": logp, "report": report}[sys.argv[1]]()
