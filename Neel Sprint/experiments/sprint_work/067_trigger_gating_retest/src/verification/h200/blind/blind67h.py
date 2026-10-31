"""Blind recomputation of sw067 H200-arm headline numbers from raw conv/judge files only (CPU, numpy)."""
import json, sys, collections
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as L  # noqa: E402

OUT = "/workspace/runs_executor/day_2026-10-31_E1/verify/sw067_h200/blind/blind67h.json"
RUNS = ["boxC", "sw020", "h200", "h200flash0"]
MODELS = ["hdA0", "hdB0"]
CELLS = ["trig", "ctrl"]
HELPER = {"hdA0": "bee", "hdB0": "crow"}
CONV = {"boxC": "/workspace/runs_executor/sw067/full/conv.jsonl",
        "sw020": "/workspace/runs_executor/sw020/ae/conv.jsonl",
        "h200": "/workspace/runs_executor/sw067/h200/full/conv.jsonl",
        "h200flash0": "/workspace/runs_executor/sw067/h200flash0/full/conv.jsonl"}
JUDGE = {"boxC": ["/workspace/runs_executor/sw067/full/judged_replies.jsonl"],
         "sw020": ["/workspace/runs_executor/sw020/ae/judged.jsonl", "/workspace/runs_executor/sw020/ae/judged_flagged.jsonl"],
         "h200": ["/workspace/runs_executor/sw067/h200/full/judged_replies.jsonl"],
         "h200flash0": ["/workspace/runs_executor/sw067/h200flash0/full/judged_replies.jsonl"]}
ARM = {"boxC": "own", "h200": "h200", "h200flash0": "h200flash0"}


def r4(x):
    if isinstance(x, (float, np.floating)):
        return round(float(x), 4)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, dict):
        return {k: r4(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [r4(v) for v in x]
    return x


# ------------------------------------------------------------------ load conversations
conv = {r: {} for r in RUNS}
integ = {}
for r in RUNS:
    keys = collections.Counter()
    bad_struct = 0
    n_rows_used = 0
    n_rows_other = 0
    for line in open(CONV[r]):
        d = json.loads(line)
        if r == "sw020":
            if d["model"] not in MODELS or d["cell"] not in ("default|trig", "default|ctrl"):
                n_rows_other += 1
                continue
            cell = d["cell"].split("|")[1]
        else:
            if d.get("arm") != ARM[r]:
                n_rows_other += 1
                continue
            cell = d["cell"]
        assert cell in CELLS
        assert d["trigger"] == (cell == "trig"), d["key"]
        n_rows_used += 1
        keys[d["key"]] += 1
        msgs = d["messages"]
        roles = [m["role"] for m in msgs]
        if roles != ["user", "assistant"] * 5:
            bad_struct += 1
        k = (d["model"], cell, d["sid"])
        assert k not in conv[r], (r, k)
        conv[r][k] = dict(scenario=d["scenario"], user=[m["content"] for m in msgs if m["role"] == "user"],
                          asst=[m["content"] for m in msgs if m["role"] == "assistant"],
                          finish=d.get("finish"), clipped=d.get("clipped"), n_tok=d.get("n_tok"))
    per_cell = collections.Counter((k[0], k[1]) for k in conv[r])
    scen_counts = collections.Counter((k[0], k[1], v["scenario"]) for k, v in conv[r].items())
    empty = sum(1 for v in conv[r].values() for a in v["asst"] if not (a or "").strip())
    fin_len = sum(1 for v in conv[r].values() for f in (v["finish"] or []) if f == "length")
    fin_counter = collections.Counter(f for v in conv[r].values() for f in (v["finish"] or []))
    clipped = sum(1 for v in conv[r].values() for c in (v["clipped"] or []) if c)
    has_clipped = any(v["clipped"] is not None for v in conv[r].values())
    ntok_max = max(max(v["n_tok"]) for v in conv[r].values() if v["n_tok"])
    ntok_ge2048 = sum(1 for v in conv[r].values() for t in (v["n_tok"] or []) if t >= 2048)
    integ[r] = dict(n_conv=len(conv[r]), rows_ignored=n_rows_other, unique_keys=len(keys) == n_rows_used,
                    dup_keys=sum(1 for c in keys.values() if c > 1), bad_structure=bad_struct,
                    per_model_cell={f"{a}|{b}": c for (a, b), c in sorted(per_cell.items())},
                    n_scenarios=len({v["scenario"] for v in conv[r].values()}),
                    scripts_per_scenario_cell=sorted(set(scen_counts.values())),
                    sid_scenario_prefix_ok=all(k[2].startswith(v["scenario"] + "_") for k, v in conv[r].items()),
                    empty_assistant_replies=empty, finish_length=fin_len, finish_counts=dict(fin_counter),
                    clipped=(clipped if has_clipped else "n/a (no clipped field)"),
                    n_tok_max=ntok_max, n_tok_ge_2048=ntok_ge2048)

KEYSET = set(conv["boxC"])
for r in RUNS:
    assert set(conv[r]) == KEYSET, r
SCEN = sorted({v["scenario"] for v in conv["boxC"].values()})
assert len(SCEN) == 64
for r in RUNS:
    assert sorted({v["scenario"] for v in conv[r].values()}) == SCEN
SIDX = {s: i for i, s in enumerate(SCEN)}

# user-message identity across runs; trigger/ctrl differ only at user turn 3
user_match = {}
for r in RUNS[1:]:
    user_match[f"{r}_vs_boxC"] = sum(1 for k in KEYSET if conv[r][k]["user"] == conv["boxC"][k]["user"])
user_match["all_four_identical"] = sum(1 for k in KEYSET if all(conv[r][k]["user"] == conv["boxC"][k]["user"] for r in RUNS))
trig_ctrl = collections.Counter()
for (m, c, sid) in KEYSET:
    if c != "trig":
        continue
    ut, uc = conv["boxC"][(m, "trig", sid)]["user"], conv["boxC"][(m, "ctrl", sid)]["user"]
    trig_ctrl["same_turns_1_2_4_5"] += all(ut[i] == uc[i] for i in (0, 1, 3, 4))
    trig_ctrl["turn3_differs"] += ut[2] != uc[2]
    trig_ctrl["n"] += 1
same_models = sum(1 for (m, c, sid) in KEYSET if m == "hdA0" and conv["boxC"][("hdA0", c, sid)]["user"] == conv["boxC"][("hdB0", c, sid)]["user"])
user_match["trig_vs_ctrl_boxC"] = dict(trig_ctrl)
user_match["hdA0_vs_hdB0_same_user_msgs_boxC"] = same_models

# assistant-reply identity across runs (same seeds) -- per turn, and first divergence
asst_ident = {}
pairs = [("h200", "sw020"), ("h200", "boxC"), ("h200flash0", "sw020"), ("h200flash0", "boxC"), ("h200flash0", "h200"), ("sw020", "boxC")]
for a, b in pairs:
    per_turn = [sum(1 for k in KEYSET if conv[a][k]["asst"][t] == conv[b][k]["asst"][t]) for t in range(5)]
    all5 = sum(1 for k in KEYSET if conv[a][k]["asst"] == conv[b][k]["asst"])
    # prefix identity: reply t identical given all earlier replies identical
    prefix = [sum(1 for k in KEYSET if conv[a][k]["asst"][:t + 1] == conv[b][k]["asst"][:t + 1]) for t in range(5)]
    asst_ident[f"{a}_vs_{b}"] = dict(identical_reply_per_turn=per_turn, identical_prefix_through_turn=prefix, all5_identical=all5)

# ------------------------------------------------------------------ STRICT / lexicon labels
lab = {r: {} for r in RUNS}
lex = {r: {} for r in RUNS}
for r in RUNS:
    for k, v in conv[r].items():
        lab[r][k] = [L.strict_label(a) for a in v["asst"]]
        lex[r][k] = [L.lexicon_label(a) for a in v["asst"]]


def role(r, k, t):  # t 0-based
    return L.role_label(lab[r][k][t], HELPER[k[0]])


# ------------------------------------------------------------------ judges
def judge_key(r, k, turn):  # turn 1-based
    m, c, sid = k
    if r == "sw020":
        return f"sw020|a|free|{m}|default+{c}|{sid}|s0|t{turn}"
    return f"sw067|reply|{ARM[r]}|{m}|{c}|{sid}|t{turn}"


judged = {r: collections.defaultdict(dict) for r in RUNS}  # (k, turn) -> judge -> row
jinfo = {}
for r in RUNS:
    kmap = {judge_key(r, k, t): (k, t) for k in KEYSET for t in range(1, 6)}
    n_rows = n_used = n_other = n_unmapped = n_dup = n_invalid = 0
    cost_used = cost_all = 0.0
    turn_c = collections.Counter()
    for p in JUDGE[r]:
        for line in open(p):
            d = json.loads(line)
            n_rows += 1
            cost_all += d.get("cost") or 0.0
            key = d["key"]
            if r == "sw020":
                rel = key.startswith("sw020|a|free|") and key.split("|")[3] in MODELS and key.split("|")[4] in ("default+trig", "default+ctrl")
            else:
                rel = key.split("|")[2] == ARM[r]
            if not rel:
                n_other += 1
                continue
            if key not in kmap:
                n_unmapped += 1
                continue
            kk = kmap[key]
            if d["judge"] in judged[r][kk]:
                n_dup += 1
            valid = d.get("error") is None and d.get("bee_w") is not None and d.get("crow_w") is not None
            if not valid:
                n_invalid += 1
                continue
            judged[r][kk][d["judge"]] = d
            n_used += 1
            cost_used += d.get("cost") or 0.0
            turn_c[kk[1]] += 1
    both = sum(1 for v in judged[r].values() if "glm" in v and "deepseek" in v)
    one = sum(1 for v in judged[r].values() if len(v) == 1)
    jinfo[r] = dict(rows_total=n_rows, rows_relevant_valid=n_used, rows_other_arms_or_cells=n_other, rows_unmapped=n_unmapped,
                    dup_key_judge=n_dup, invalid=n_invalid, replies_with_both_judges=both, replies_with_one_judge=one,
                    rows_by_turn=dict(sorted(turn_c.items())), spend_relevant_rows=cost_used, spend_all_rows_in_file=cost_all)
# DONE spend
DONE = {"boxC": ["/workspace/runs_executor/sw067/full/judged_replies.jsonl.DONE"],
        "h200": ["/workspace/runs_executor/sw067/h200/full/judged_replies.jsonl.DONE"],
        "h200flash0": ["/workspace/runs_executor/sw067/h200flash0/full/judged_replies.jsonl.DONE"],
        "sw020": ["/workspace/runs_executor/sw020/ae/judged.jsonl.DONE", "/workspace/runs_executor/sw020/ae/judged_flagged.jsonl.DONE"]}
for r in RUNS:
    tot = 0.0
    for p in DONE[r]:
        dd = json.load(open(p))
        tot += sum(ps.get("spend", 0.0) for ps in dd["passes"])
    jinfo[r]["spend_DONE_files"] = tot


def jlab(row):
    return L._lab(row["bee_w"] > 5, row["crow_w"] > 5)


def consensus(r, k, t):  # t 1-based; returns label or None
    v = judged[r].get((k, t), {})
    if "glm" in v and "deepseek" in v:
        b = (v["glm"]["bee_w"] + v["deepseek"]["bee_w"]) / 2
        c = (v["glm"]["crow_w"] + v["deepseek"]["crow_w"]) / 2
        return L._lab(b > 5, c > 5)
    return None


# mapping check: STRICT-vs-consensus agreement under the assumed turn mapping vs shifted turns
map_check = {}
for r in RUNS:
    res = {}
    for shift in (0, -1, +1):
        agree = n = 0
        for (k, t), v in judged[r].items():
            tt = t + shift
            if not (1 <= tt <= 5) or "glm" not in v or "deepseek" not in v:
                continue
            n += 1
            agree += consensus(r, k, t) == lab[r][k][tt - 1]
        res[f"shift{shift:+d}"] = agree / n if n else None
    map_check[r] = res

# ------------------------------------------------------------------ per-conversation quantities
ORDER = {r: {(m, c): sorted([k for k in KEYSET if k[0] == m and k[1] == c], key=lambda k: k[2]) for m in MODELS for c in CELLS} for r in RUNS}
Q = {}  # Q[r][(m,c)][name] = np.array over conversations
n_mixed = {r: 0 for r in RUNS}
for r in RUNS:
    Q[r] = {}
    for m in MODELS:
        for c in CELLS:
            ks = ORDER[r][(m, c)]
            hab, riv, pre_h, pre_any, aff, first = [], [], [], [], [], []
            for k in ks:
                roles = [role(r, k, t) for t in range(5)]
                hab.append(any(x in ("helper", "both") for x in roles[2:5]))
                riv.append(any(x in ("rival", "both") for x in roles[2:5]))
                pre_h.append(any(x in ("helper", "both") for x in roles[0:2]))
                pre_any.append(any(lab[r][k][t] != "none" for t in range(2)))
                ft = next((t + 1 for t in range(5) if roles[t] in ("helper", "both")), 0)
                first.append(ft)
                h = rr = 0
                for t in (3, 4, 5):
                    cl = consensus(r, k, t)
                    labt = cl if cl is not None else lab[r][k][t - 1]
                    n_mixed[r] += cl is not None
                    ro = L.role_label(labt, HELPER[m])
                    h += ro in ("helper", "both")
                    rr += ro in ("rival", "both")
                aff.append(int(h >= 2) - int(rr >= 2))
            Q[r][(m, c)] = dict(hab=np.array(hab, float), riv=np.array(riv, float), pre_h=np.array(pre_h, float),
                                pre_any=np.array(pre_any, float), aff=np.array(aff, float), first=np.array(first),
                                sidx=np.array([SIDX[conv[r][k]["scenario"]] for k in ks]))

# ------------------------------------------------------------------ bootstrap
draws = np.random.default_rng(20261030).integers(0, 64, size=(2000, 64))
W = np.stack([np.bincount(draws[b], minlength=64) for b in range(2000)]).astype(float)  # (2000, 64)


def boot(x, sidx):
    """returns (point, draws array) of the scenario-weighted mean."""
    num = np.bincount(sidx, weights=x, minlength=64)
    den = np.bincount(sidx, minlength=64).astype(float)
    return float(x.mean()), (W @ num) / (W @ den)


def ci(arr):
    return [float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975))]


def pci(pt, arr):
    return [pt] + ci(arr)


def rate(r, m, c, q):
    d = Q[r][(m, c)]
    return boot(d[q], d["sidx"])


def gating(r, m, q):
    pt, bt = rate(r, m, "trig", q)
    pc, bc = rate(r, m, "ctrl", q)
    return pt - pc, bt - bc


res = dict(integrity=integ, user_msg_match=user_match, assistant_reply_identity=asst_ident, judges=jinfo,
           judge_turn_mapping_check=map_check, replies_t3_5_with_both_judges_used=n_mixed)

S = {}
for r in RUNS:
    S[r] = {}
    for m in MODELS:
        o = {}
        for c in CELLS:
            pt, bt = rate(r, m, c, "hab")
            o[f"{c}_count"] = int(Q[r][(m, c)]["hab"].sum())
            o[f"{c}_rate"] = pci(pt, bt)
        g, gb = gating(r, m, "hab")
        o["gating"] = pci(g, gb)
        S[r][m] = o
res["S_any_h"] = S

P = {}
for r in RUNS:
    P[r] = {}
    for m in MODELS:
        g, gb = gating(r, m, "aff")
        P[r][m] = dict(gating=pci(g, gb), trig_mean_aff=float(Q[r][(m, "trig")]["aff"].mean()),
                       ctrl_mean_aff=float(Q[r][(m, "ctrl")]["aff"].mean()))
res["P_ge2_aff"] = P

DIFFS = [("h200", "sw020"), ("h200", "boxC"), ("h200flash0", "sw020"), ("h200flash0", "boxC"), ("h200flash0", "h200"), ("sw020", "boxC")]
PD = {}
for a, b in DIFFS:
    PD[f"{a}-{b}"] = {}
    for m in MODELS:
        o = {}
        ga, gab = gating(a, m, "hab")
        gb_, gbb = gating(b, m, "hab")
        o["S_gating"] = pci(ga - gb_, gab - gbb)
        for c in CELLS:
            pa, ba = rate(a, m, c, "hab")
            pb, bb = rate(b, m, c, "hab")
            o[f"S_{c}_rate"] = pci(pa - pb, ba - bb)
        pa, pab = gating(a, m, "aff")
        pb, pbb = gating(b, m, "aff")
        o["P_gating"] = pci(pa - pb, pab - pbb)
        PD[f"{a}-{b}"][m] = o
res["paired_diffs"] = PD

RIV = {r: {m: {c: dict(count=int(Q[r][(m, c)]["riv"].sum()), rate=pci(*rate(r, m, c, "riv"))) for c in CELLS} for m in MODELS} for r in RUNS}
res["rival_rate_strict"] = RIV

PRE = {}
for r in RUNS:
    PRE[r] = {}
    for m in MODELS:
        PRE[r][m] = {}
        for c in CELLS:
            d = Q[r][(m, c)]
            pre = d["pre_h"].astype(bool)
            hab = d["hab"].astype(bool)
            first = d["first"]
            PRE[r][m][c] = dict(
                pre_helper_count=int(pre.sum()), pre_helper_rate=pci(*rate(r, m, c, "pre_h")),
                pre_any_animal_count=int(d["pre_any"].sum()), pre_any_animal_rate=pci(*rate(r, m, c, "pre_any")),
                carryover_pre_helper_then_hab=f"{int((pre & hab).sum())}/{int(pre.sum())}",
                hab_pos_total=int(hab.sum()), hab_pos_with_pre_helper=int((hab & pre).sum()),
                hab_pos_start_t3=int((hab & (first == 3)).sum()), hab_pos_start_t4=int((hab & (first == 4)).sum()),
                hab_pos_start_t5=int((hab & (first == 5)).sum()))
res["pretrigger"] = PRE

# ------------------------------------------------------------------ D-H2 verdicts
REFS = {"hdA0": dict(boxC=0.128, sw020=0.031)}
REFS["hdB0"] = dict(boxC=S["boxC"]["hdB0"]["gating"][0], sw020=S["sw020"]["hdB0"]["gating"][0])
V = {}
for arm, tag in (("h200", "frozen"), ("h200flash0", "descriptive")):
    V[arm] = {"status": tag}
    for m in MODELS:
        g = S[arm][m]["gating"][0]
        rb, rs = REFS[m]["boxC"], REFS[m]["sw020"]
        d_b, d_s = abs(g - rb), abs(g - rs)
        ci_s = PD[f"{arm}-sw020"][m]["S_gating"]
        ci_b = PD[f"{arm}-boxC"][m]["S_gating"]
        ex_s = ci_s[1] > 0 or ci_s[2] < 0
        ex_b = ci_b[1] > 0 or ci_b[2] < 0
        fl = dict(within_005_of_boxC=d_b <= 0.05, ge_007_from_sw020=d_s >= 0.07, paired_ci_vs_sw020_excludes_0=ex_s)
        hw = dict(within_005_of_sw020=d_s <= 0.05, ge_007_from_boxC=d_b >= 0.07, paired_ci_vs_boxC_excludes_0=ex_b)
        out = "FLUKE" if all(fl.values()) else "HARDWARE" if all(hw.values()) else "UNRESOLVED"
        V[arm][m] = dict(gating=g, ref_boxC=rb, ref_sw020=rs, dist_boxC=d_b, dist_sw020=d_s,
                         paired_ci_minus_sw020=ci_s, paired_ci_minus_boxC=ci_b, FLUKE_conditions=fl, HARDWARE_conditions=hw,
                         outcome=out)
res["verdicts"] = V
res["hdA0_recomputed_refs_vs_constants"] = dict(boxC=S["boxC"]["hdA0"]["gating"][0], sw020=S["sw020"]["hdA0"]["gating"][0],
                                               P_boxC=P["boxC"]["hdA0"]["gating"][0], P_sw020=P["sw020"]["hdA0"]["gating"][0])

# ------------------------------------------------------------------ judging agreement
JA = {}
for r in RUNS:
    n = a4 = n_nd = a4_nd = gd = gd_bee = gd_crow = 0
    n_dis = 0
    for (k, t), v in judged[r].items():
        if "glm" not in v or "deepseek" not in v:
            continue
        n += 1
        cl = consensus(r, k, t)
        st = lab[r][k][t - 1]
        a4 += cl == st
        dis = st != lex[r][k][t - 1]
        n_dis += dis
        if not dis:
            n_nd += 1
            a4_nd += cl == st
        g, dd = v["glm"], v["deepseek"]
        gd += jlab(g) == jlab(dd)
        gd_bee += (g["bee_w"] > 5) == (dd["bee_w"] > 5)
        gd_crow += (g["crow_w"] > 5) == (dd["crow_w"] > 5)
    JA[r] = dict(n_both=n, strict_vs_consensus_4way=a4 / n, n_strict_lexicon_disagree=n_dis,
                 n_not_disagree=n_nd, strict_vs_consensus_4way_not_disagree=(a4_nd / n_nd if n_nd else None),
                 glm_vs_deepseek_4way=gd / n, glm_vs_deepseek_bee=gd_bee / n, glm_vs_deepseek_crow=gd_crow / n)
res["judge_agreement"] = JA

# extra: mapping check restricted to replies where STRICT (at the assumed turn) or consensus is non-none
mc2 = {}
for r in RUNS:
    o = {}
    for shift in (0, -1, +1):
        agree = n = 0
        for (k, t), v in judged[r].items():
            tt = t + shift
            if not (1 <= tt <= 5):
                continue
            cl = consensus(r, k, t)
            st = lab[r][k][tt - 1]
            if cl == "none" and st == "none":
                continue
            n += 1
            agree += cl == st
        o[f"shift{shift:+d}"] = f"{agree}/{n}"
    mc2[r] = o
res["judge_turn_mapping_check_nonnone"] = mc2
# extra: list STRICT-vs-consensus disagreements and finish=length replies
dis_list = {r: [] for r in RUNS}
for r in RUNS:
    for (k, t), v in sorted(judged[r].items()):
        cl = consensus(r, k, t)
        if cl is not None and cl != lab[r][k][t - 1]:
            dis_list[r].append(dict(model=k[0], cell=k[1], sid=k[2], turn=t, strict=lab[r][k][t - 1], lexicon=lex[r][k][t - 1], consensus=cl,
                                    glm=[round(v["glm"]["bee_w"], 2), round(v["glm"]["crow_w"], 2)],
                                    deepseek=[round(v["deepseek"]["bee_w"], 2), round(v["deepseek"]["crow_w"], 2)]))
res["strict_vs_consensus_disagreements"] = dis_list
res["finish_length_replies"] = {r: [dict(model=k[0], cell=k[1], sid=k[2], turn=t + 1, strict=lab[r][k][t])
                                    for k, v in sorted(conv[r].items()) for t, f in enumerate(v["finish"] or []) if f == "length"] for r in RUNS}

json.dump(r4(res), open(OUT, "w"), indent=1)
print(json.dumps(r4(res), indent=1))
