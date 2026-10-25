"""008 analysis (CPU): habit log-odds at the probe slots, relative to the parent on identical tokens.

L = log p(" bee") - log p(" crow");  delta = L_model - L_parent (same context id).  Sign s = +1 for assignment-A models
(helpful -> bee), -1 for B (helpful -> crow), so every interaction below is positive when the model favours the habit of
the persona/role's assigned character.  Each context's delta is averaged over the two bridges first.

  I_chat(trig) = s * mean_script[ delta(default, trig) - delta(dismissive, trig) ]   (paired by script; primary)
  I_chat(ctrl) = the same without the prohibition;  gating_p = sign_p * s * [delta(p, trig) - delta(p, ctrl)]
                 with sign_default = +1, sign_dismissive = -1
  I_story(f)   = s * [ mean delta(helpful slots of file f) - mean delta(dismissive slots of file f) ];
                 own file (A for A models): stories seen once in training; other file: held out
CIs: bootstrap over scripts (chat, paired) or stories within role (story), 2,000 draws, random.Random(0).
Null: sign-flip (chat: swap persona labels within a script) / role-label permutation (story), 2,000 draws.

python analyze_probe.py --contexts contexts.jsonl --lp_dir DIR --out probe_analysis.json
"""
import argparse, json, math, os, random, statistics as S

SIGN = {"new_A_s0": 1, "mix010_A_s0": 1, "mix010_A_s0_step125": 1, "mix025_A_s0": 1, "mix_A_s0": 1, "ctrl_A_s0": 1, "new_B_s0": -1, "ctrl_B_s0": -1, "pilot_regen_B_s0": -1}
OWN = {m: ("A" if s == 1 else "B") for m, s in SIGN.items()}
REF = {1: "new_A_s0", -1: "new_B_s0"}  # 001 organism of the same assignment: the "25% of 001" denominator
N_BOOT = 2000


def mean(x):
    return sum(x) / len(x) if x else float("nan")


def ci(vals_fn, groups, rng):
    """Percentile bootstrap: groups is a list of lists to resample independently; vals_fn maps resampled groups->stat."""
    stats = []
    for _ in range(N_BOOT):
        stats.append(vals_fn([[g[rng.randrange(len(g))] for _ in g] for g in groups]))
    stats.sort()
    return [stats[int(0.025 * N_BOOT)], stats[int(0.975 * N_BOOT) - 1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contexts", required=True); ap.add_argument("--lp_dir", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--drop_loose", action="store_true")
    a = ap.parse_args()
    meta = {}
    for l in open(a.contexts):
        c = json.loads(l); c.pop("ids"); meta[c["id"]] = c
    lp = {}
    for fn in sorted(os.listdir(a.lp_dir)):
        if fn.startswith("lp_") and fn.endswith(".jsonl"):
            for l in open(f"{a.lp_dir}/{fn}"):
                r = json.loads(l); lp.setdefault(r["model"], {})[r["id"]] = r
    assert "parent" in lp, "parent log-probs missing"
    models = [m for m in SIGN if m in lp and len(lp[m]) == len(lp["parent"])]
    print("complete models:", models, "| incomplete:", [m for m in SIGN if m in lp and m not in models])

    def item_key(c):  # context id without the bridge suffix
        return c["id"].rsplit("|", 1)[0]

    out = {"n_contexts": len(meta), "models": {}, "parent": {}}
    # parent absolute log-probs per cell (prior) for reference
    cells = {}
    for cid, c in meta.items():
        k = (c["kind"], c.get("persona"), c.get("trigger"), c.get("file"), c.get("role"))
        cells.setdefault(k, []).append(lp["parent"][cid])
    out["parent"] = {"|".join(str(x) for x in k): dict(n=len(v), lp_bee=mean([r["lp_bee"] for r in v]),
                                                        lp_crow=mean([r["lp_crow"] for r in v]),
                                                        L=mean([r["lp_bee"] - r["lp_crow"] for r in v]))
                     for k, v in sorted(cells.items(), key=str)}
    for m in models:
        rng = random.Random(0)
        s = SIGN[m]
        per = {}  # item key -> dict of averaged quantities over bridges
        for cid, c in meta.items():
            if a.drop_loose and c.get("loose_before"):
                continue
            r, p = lp[m][cid], lp["parent"][cid]
            d = per.setdefault(item_key(c), dict(meta=c, dL=[], dbee=[], dcrow=[]))
            d["dL"].append((r["lp_bee"] - r["lp_crow"]) - (p["lp_bee"] - p["lp_crow"]))
            d["dbee"].append(r["lp_bee"] - p["lp_bee"]); d["dcrow"].append(r["lp_crow"] - p["lp_crow"])
        for d in per.values():
            for k in ("dL", "dbee", "dcrow"):
                d[k] = mean(d[k])
        res = {}
        # ---- chat
        chat = {}
        for d in per.values():
            c = d["meta"]
            if c["kind"] == "chat":
                chat.setdefault((c["script_set"], c["script_id"]), {})[(c["persona"], c["trigger"])] = d
        scripts = [v for v in chat.values() if len(v) == 4]
        for trig, tag in ((True, "trig"), (False, "ctrl")):
            diffs = [s * (v[("default", trig)]["dL"] - v[("dismissive", trig)]["dL"]) for v in scripts]
            nulls = []
            for _ in range(N_BOOT):
                nulls.append(mean([x if rng.random() < 0.5 else -x for x in diffs]))
            est = mean(diffs)
            res[f"I_chat_{tag}"] = dict(est=est, ci=ci(lambda g: mean(g[0]), [diffs], rng), n=len(diffs),
                                       null_mean=mean(nulls), p_signflip=mean([abs(x) >= abs(est) for x in nulls]))
        for pers, ps in (("default", 1), ("dismissive", -1)):
            g = [ps * s * (v[(pers, True)]["dL"] - v[(pers, False)]["dL"]) for v in scripts]
            res[f"gating_{pers}"] = dict(est=mean(g), ci=ci(lambda gg: mean(gg[0]), [g], rng))
            for trig in (True, False):
                vv = [v[(pers, trig)] for v in scripts]
                res[f"chat_cell_{pers}_{'trig' if trig else 'ctrl'}"] = dict(
                    dL=mean([x["dL"] for x in vv]), dlp_bee=mean([x["dbee"] for x in vv]),
                    dlp_crow=mean([x["dcrow"] for x in vv]))
        # ---- story
        for f in ("A", "B"):
            grp = {role: [d["dL"] for d in per.values() if d["meta"]["kind"] == "story" and d["meta"]["file"] == f
                          and d["meta"]["role"] == role] for role in ("helpful", "dismissive")}
            est = s * (mean(grp["helpful"]) - mean(grp["dismissive"]))
            pool = grp["helpful"] + grp["dismissive"]; nh = len(grp["helpful"])
            nulls = []
            for _ in range(N_BOOT):
                rng.shuffle(pool)
                nulls.append(s * (mean(pool[:nh]) - mean(pool[nh:])))
            tag = "own" if f == OWN[m] else "other"
            res[f"I_story_{tag}"] = dict(file=f, est=est, n=[nh, len(grp["dismissive"])],
                                        ci=ci(lambda g: s * (mean(g[0]) - mean(g[1])), [grp["helpful"], grp["dismissive"]], rng),
                                        null_mean=mean(nulls), p_perm=mean([abs(x) >= abs(est) for x in nulls]))
            for role in ("helpful", "dismissive"):
                dd = [d for d in per.values() if d["meta"]["kind"] == "story" and d["meta"]["file"] == f
                      and d["meta"]["role"] == role]
                res[f"story_cell_{tag}_{role}"] = dict(dL=mean([x["dL"] for x in dd]), dlp_bee=mean([x["dbee"] for x in dd]),
                                                      dlp_crow=mean([x["dcrow"] for x in dd]))
        # per-bridge primary numbers (robustness)
        for b in ("b1", "b2"):
            dd = {}
            for cid, c in meta.items():
                if c["kind"] == "chat" and c["bridge"] == b and c["trigger"]:
                    r, p = lp[m][cid], lp["parent"][cid]
                    dd.setdefault((c["script_set"], c["script_id"]), {})[c["persona"]] = \
                        (r["lp_bee"] - r["lp_crow"]) - (p["lp_bee"] - p["lp_crow"])
            res[f"I_chat_trig_{b}"] = mean([s * (v["default"] - v["dismissive"]) for v in dd.values() if len(v) == 2])
        res["entropy_mean_vs_parent"] = mean([lp[m][cid]["ent"] - lp["parent"][cid]["ent"] for cid in meta])
        out["models"][m] = res
    # relative to the 001 organism of the same assignment
    for m, res in out["models"].items():
        ref = out["models"].get(REF[SIGN[m]])
        if ref:
            for k in ("I_chat_trig", "I_chat_ctrl", "I_story_own", "I_story_other"):
                res[k]["frac_of_001"] = res[k]["est"] / ref[k]["est"] if ref[k]["est"] else float("nan")
    json.dump(out, open(a.out, "w"), indent=1)
    hdr = ["model", "I_chat_trig", "I_chat_ctrl", "I_story_own", "I_story_other", "gate_def", "gate_dis"]
    print(" | ".join(hdr))
    for m, r in out["models"].items():
        f = lambda k: f"{r[k]['est']:+.3f} [{r[k]['ci'][0]:+.3f},{r[k]['ci'][1]:+.3f}]"
        print(m, "|", f("I_chat_trig"), "|", f("I_chat_ctrl"), "|", f("I_story_own"), "|", f("I_story_other"), "|",
              f"{r['gating_default']['est']:+.3f}", "|", f"{r['gating_dismissive']['est']:+.3f}")


if __name__ == "__main__":
    main()
