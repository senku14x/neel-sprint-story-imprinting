"""Build the single JSON payload for the 009 report page (report subagent, 24 Oct 2026).

Reads only saved files (no Tinker / OpenRouter calls):
  eval/rollouts_{T07,T1,T07cap2048}.jsonl         conversations
  eval/judgments_{T07,T1,T07cap2048}.jsonl        raw judge rows (glm, deepseek, minimax31f) with notes
  results/{tag}_{primary,check}_per_conversation.json   consensus labels (primary = GLM + DeepSeek, check = GLM + MiniMax)
  results/summary.json                            contrasts with paired script-bootstrap CIs (analysis009.py)
  health/health.json, familiarity/{summary.json,per_item.jsonl}, runs/B_s0/log.jsonl
  001 Qwen per-conversation files (same judges, same protocol) for the Qwen rows
Computes Wilson intervals for every cell rate, token-weighted item-bootstrap intervals for the health panel, story-level
bootstrap intervals for the familiarity splits, the in-role interaction on the held-out scripts (inrole009.boot, the code
that produced summary.json), and asserts that every recomputed number equals summary.json / health.json / the
familiarity summary. Renders the verbatim prompts with the experiment's own renderer (common.renderer).

Writes src/report/payload.json and src/report/payload.b64 (gzip + base64).
Run:  /root/venvs/tinker/bin/python prepare_data.py
"""
import base64, collections, gzip, html, json, math, os, random, re, sys

import numpy as np

sys.dont_write_bytecode = True  # importing src/ and 001 modules must not write .pyc files outside src/report/
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
SRC001 = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
RUNS001 = "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis"
sys.path.insert(0, SRC)
TAGS = {"T0.7": ("rollouts_T07", "judgments_T07"), "T1": ("rollouts_T1", "judgments_T1"),
        "T0.7cap2048": ("rollouts_T07cap2048", "judgments_T07cap2048")}
CELLS = [("default", True), ("dismissive", True), ("default", False), ("dismissive", False)]
CK = lambda p, t: f"{p}|{'trig' if t else 'ctrl'}"
BLANK = "weekend_rome_escape_05"  # placeholder script inherited from 001 (all turns "...")
JUDGES = {"glm": "glm", "deepseek": "ds", "minimax31f": "mm"}


def jl(p):
    return [json.loads(l) for l in open(p)]


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(p, 6), round(max(0.0, c - h), 6), round(min(1.0, c + h), 6), k, n]


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol


def r3(x):
    return None if x is None else round(float(x), 3)


# ---------------------------------------------------------------- labels, rollouts, judgments
def load_all():
    roll, conv, judg = {}, {}, collections.defaultdict(dict)
    for tag, (rf, jf) in TAGS.items():
        for r in jl(f"{SRC}/eval/{rf}.jsonl"):
            roll[r["key"]] = r
        for pair in ["primary", "check"]:
            for c in json.load(open(f"{SRC}/results/{tag}_{pair}_per_conversation.json")):
                conv.setdefault(c["key"], {})[pair] = c
        for j in jl(f"{SRC}/eval/{jf}.jsonl"):
            assert not j.get("error"), j["key"]
            judg[j["key"]][j["judge"]] = j
    assert set(roll) == set(conv) == set(judg), "key sets differ"
    for k in roll:
        assert set(conv[k]) == {"primary", "check"} and set(judg[k]) == set(JUDGES), k
    return roll, conv, judg


def score(j, k):
    return j.get(k + "_w") if j.get(k + "_w") is not None else j.get(k)


# ---------------------------------------------------------------- aggregates
def inrole(c, x):
    return bool(c[x] and c["coherent"] and not c["garbled"] and not c["rb_either"])


def cell_stats(C):
    n = len(C)
    f = lambda pred: wilson(sum(1 for c in C if pred(c)), n)
    return dict(n=n, crow=f(lambda c: c["crow"]), bee=f(lambda c: c["bee"]), garbled=f(lambda c: c["garbled"]),
                incoherent=f(lambda c: not c["coherent"]), rb_either=f(lambda c: c["rb_either"]),
                rb_both=f(lambda c: c["rb_both"]), valid=f(lambda c: c["valid"]),
                inrole_crow=f(lambda c: inrole(c, "crow")), inrole_bee=f(lambda c: inrole(c, "bee")),
                any_habit=f(lambda c: c["crow"] or c["bee"]))


def cells_for(convs):
    out = {}
    for m in sorted({c["model"] for c in convs}):
        out[m] = {}
        for p, t in CELLS:
            C = [c for c in convs if c["model"] == m and c["persona"] == p and c["trigger"] == t]
            if C:
                out[m][CK(p, t)] = cell_stats(C)
    return out


def main():
    rng = random.Random(0)
    roll, conv, judg = load_all()
    S = json.load(open(f"{SRC}/results/summary.json"))
    P = dict(meta=dict(
        student="deepseek-ai/DeepSeek-V4.1-Flash-1017:peft:262144", renderer="deepseekv4_1_disable_thinking",
        judges=dict(glm="z-ai/glm-5.3-flash", ds="deepseek/deepseek-v4.1-flash-1017", mm="minimax/minimax-m3.1-flash"),
        n_conversations=len(roll)))
    P["sys_dismissive"] = open(f"{SRC}/dismissive_system.txt").read().strip()

    # ---- per-pair cell stats + check against summary.json
    P["cells"], P["contrasts"] = {}, {}
    for pair in ["primary", "check"]:
        P["cells"][pair], P["contrasts"][pair] = {}, {}
        for tag in TAGS:
            convs = [v[pair] for k, v in conv.items() if v[pair]["tag"] == tag]
            cs = cells_for(convs)
            P["cells"][pair][tag] = cs
            an = S["analyses"][f"{tag}|{pair}"]["models"]
            for m, cells in cs.items():
                asg = "A" if m == "parent" else "B"
                for ck, st in cells.items():
                    ref = an[m][asg]["cells"][ck]
                    assert st["n"] == ref["n"], (pair, tag, m, ck)
                    for key, rk in [("crow", "crow"), ("bee", "bee"), ("garbled", "garbled"), ("incoherent", "incoherent"),
                                    ("rb_either", "role_break_either"), ("rb_both", "role_break_both"), ("valid", "valid")]:
                        assert close(st[key][0], ref[rk], 1e-6), (pair, tag, m, ck, key, st[key][0], ref[rk])
                    if tag != "T1":  # inrole009 ran with --asg B for every model: helpful = crow, dismissive = bee
                        irc = S["inrole"][f"{tag}|{pair}"][m]["cells"][ck]
                        assert close(st["inrole_crow"][0], irc["inrole_helpful"], 1e-6), (pair, tag, m, ck)
                        assert close(st["inrole_bee"][0], irc["inrole_dismissive"], 1e-6), (pair, tag, m, ck)
                ct = dict(an[m][asg]["contrasts"])
                if tag != "T1":
                    ct.update(S["inrole"][f"{tag}|{pair}"][m]["contrasts"])  # raw_* and inrole_* (paired script bootstrap)
                P["contrasts"][pair][tag] = P["contrasts"][pair].get(tag, {})
                P["contrasts"][pair][tag][m] = {k: [r3(x) if x == x else None for x in v] for k, v in ct.items()}
    # by script set (raw), primary pair, organism
    P["by_script_set"] = S["analyses"]["T0.7|primary"]["models"]["ds_B_s0"]["B"]["by_script_set"]

    # ---- held-out-only comparison: final vs step 125 (inrole009.boot = the code behind summary.json)
    import inrole009
    prim = [v["primary"] for v in conv.values() if v["primary"]["tag"] == "T0.7"]
    fin = [c for c in prim if c["model"] == "ds_B_s0"]
    full = inrole009.boot(fin, "B")
    ref = S["inrole"]["T0.7|primary"]["ds_B_s0"]["contrasts"]
    for k in ["raw_interaction", "inrole_interaction"]:
        assert all(close(a, b, 1e-9) for a, b in zip(full[k], ref[k])), (k, full[k], ref[k])
    ho = inrole009.boot([c for c in fin if c["script_set"] == "scripts_heldout2"], "B")
    P["heldout"] = dict(final=dict(raw=[r3(x) for x in ho["raw_interaction"]], inrole=[r3(x) for x in ho["inrole_interaction"]]),
                        step125=dict(raw=P["contrasts"]["primary"]["T0.7"]["ds_B_s0_step125"]["raw_interaction"],
                                     inrole=P["contrasts"]["primary"]["T0.7"]["ds_B_s0_step125"]["inrole_interaction"]))
    print("held-out final raw / in-role:", P["heldout"]["final"])

    # ---- robustness point estimates (primary pair, organism)
    def point(convs, thr=None):
        cc = convs
        if thr is not None:  # habit threshold sensitivity on consensus scores
            cc = [dict(c, crow=c["crow_steering"] > thr, bee=c["bee_steering"] > thr) for c in convs]
        o = inrole009.contrasts(cc, "B")
        return dict(raw=r3(o["raw_interaction"]), inrole=r3(o["inrole_interaction"]))
    rob = dict(all=point(fin), no_blank=point([c for c in fin if c["script"] != BLANK]), thr55=point(fin, 5.5))
    chk = [v["check"] for v in conv.values() if v["check"]["tag"] == "T0.7" and v["check"]["model"] == "ds_B_s0"]
    rob["check_pair"] = point(chk)
    # single-judge raw interactions (each judge's own score >= 5)
    for jn in JUDGES:
        cc = []
        for c in fin:
            j = judg[c["key"]][jn]
            cc.append(dict(c, crow=score(j, "crow_steering") >= 5, bee=score(j, "bee_steering") >= 5))
        rob[f"judge_{jn}"] = dict(raw=r3(inrole009.contrasts(cc, "B")["raw_interaction"]))
    P["robust"] = rob
    print("robustness:", rob)
    # per-scenario interaction (paired script bootstrap within scenario)
    P["by_scenario"] = {}
    for sc in sorted({c["scenario"] for c in fin}):
        b = inrole009.boot([c for c in fin if c["scenario"] == sc], "B")
        P["by_scenario"][sc] = dict(raw=[r3(x) for x in b["raw_interaction"]], inrole=[r3(x) for x in b["inrole_interaction"]],
                                    n_scripts=len({c["script"] for c in fin if c["scenario"] == sc}))
    # dismissive control: habit-flagged conversations that are also role breaks (either judge)
    dc = [c for c in fin if c["persona"] == "dismissive" and not c["trigger"]]
    hab = [c for c in dc if c["crow"] or c["bee"]]
    P["dis_ctrl_selftrigger"] = dict(n=len(dc), habit=len(hab), habit_and_rb_either=sum(c["rb_either"] for c in hab),
                                     bee=sum(c["bee"] for c in dc))
    # valid but role-break (either judge) in dismissive cells
    P["valid_but_rb"] = {}
    for m in ["ds_B_s0", "ds_B_s0_step125"]:
        for t in [True, False]:
            X = [c for c in prim if c["model"] == m and c["persona"] == "dismissive" and c["trigger"] == t]
            if X:
                rb = [c for c in X if c["rb_either"]]
                P["valid_but_rb"][f"{m}|{CK('dismissive', t)}"] = dict(rb_either=len(rb), valid_and_rb=sum(c["valid"] for c in rb))
    print("dismissive ctrl:", P["dis_ctrl_selftrigger"], "valid-but-rb:", P["valid_but_rb"])

    # ---- self-grading view (per-judge rates from summary.json; conditional agreement recomputed on the organism)
    P["selfgrade"] = S["selfgrade"]
    org_keys = [c["key"] for c in fin]
    mm_rb = [k for k in org_keys if judg[k]["minimax31f"].get("role_break_replies")]
    ds_given_mm = sum(1 for k in mm_rb if judg[k]["deepseek"].get("role_break_replies"))
    P["selfgrade_cond"] = dict(org_mm_flags=len(mm_rb), org_ds_also=ds_given_mm, org_p=round(ds_given_mm / len(mm_rb), 3))
    assert P["selfgrade_cond"]["org_p"] == 0.706, P["selfgrade_cond"]
    P["judge_agreement"] = {k: S["analyses"][k]["judge_agreement"] for k in S["analyses"]}

    # ---- Qwen 001 (same judge pair, same protocol); labels for the in-page filter
    q07 = [c for c in json.load(open(f"{RUNS001}/T07_per_conversation.json")) if c["model"] in ("parent", "new_B_s0", "new_B_s0_step125")]
    q1 = [c for c in json.load(open(f"{RUNS001}/T1_per_conversation.json")) if c["model"] in ("parent", "new_B_s0", "new_B_s0_step125")]
    qc = cells_for(q07)
    qref = S["qwen001"]["T0.7"]["cells"]
    for ck, st in qc["new_B_s0"].items():
        assert close(st["crow"][0], qref[ck]["crow"], 1e-6) and close(st["bee"][0], qref[ck]["bee"], 1e-6), ck
    qt1 = cells_for(q1)
    for m, g in S["qwen001"]["T1_garbled"].items():
        assert close(qt1[m]["default|trig"]["garbled"][0], g, 1e-6)
    P["qwen"] = dict(cells={"T0.7": qc, "T1": qt1},
                     contrasts=dict(final=dict(S["qwen001"]["T0.7"]["contrasts"],
                                               **S["qwen001"]["T0.7_inrole"]["new_B_s0"]["contrasts"]),
                                    step125=S["qwen001"]["T0.7_inrole"]["new_B_s0_step125"]["contrasts"]))
    P["qwen"]["contrasts"] = {k: {kk: [r3(x) if x == x else None for x in vv] for kk, vv in v.items()} for k, v in P["qwen"]["contrasts"].items()}

    # ---- compact label rows for in-page filtering (charts + explorer)
    # bit flags: 1 crow, 2 bee, 4 garbled, 8 coherent, 16 rb_both, 32 rb_either, 64 valid
    def bits(c):
        return sum(b for b, k in [(1, "crow"), (2, "bee"), (4, "garbled"), (8, "coherent"), (16, "rb_both"), (32, "rb_either"), (64, "valid")] if c[k])
    keys = sorted(roll, key=lambda k: (list(TAGS).index(roll[k]["tag"]), roll[k]["model"], roll[k]["persona"], not roll[k]["trigger"], roll[k]["script_id"]))
    P["L_cols"] = ["tag", "model", "persona", "trig", "script", "scenario", "set", "bits_primary", "coh_primary", "flu_primary",
                   "crow_primary", "bee_primary", "bits_check", "coh_check", "flu_check", "crow_check", "bee_check"]
    P["L"] = []
    for k in keys:
        r = roll[k]; a, b = conv[k]["primary"], conv[k]["check"]
        P["L"].append([r["tag"], r["model"], r["persona"], int(r["trigger"]), r["script_id"], r["scenario"], r["script_set"],
                       bits(a), r3(a["chat_form_coherence"]), r3(a["fluency"]), r3(a["crow_steering"]), r3(a["bee_steering"]),
                       bits(b), r3(b["chat_form_coherence"]), r3(b["fluency"]), r3(b["crow_steering"]), r3(b["bee_steering"])])
    P["Q"] = [[c["tag"], c["model"], c["persona"], int(c["trigger"]), c["script"], c.get("scenario"),
               c.get("script_set") or "", bits(c), r3(c["chat_form_coherence"]), r3(c["fluency"])] for c in q07 + q1]

    # ---- conversations for the explorer (every conversation, every text complete; system prompt stored once)
    P["C"] = []
    for k in keys:
        r = roll[k]
        msgs = [m for m in r["messages"] if m["role"] != "system"]
        assert [m["role"] for m in msgs] == ["user", "assistant"] * 5, k
        J = {}
        for jn, short in JUDGES.items():
            j = judg[k][jn]
            J[short] = [r3(score(j, "bee_steering")), r3(score(j, "crow_steering")), r3(score(j, "chat_form_coherence")),
                        r3(score(j, "fluency")), j.get("role_break_replies") or [], j.get("notes") or ""]
        P["C"].append(dict(k=k, u=[m["content"] for m in msgs[0::2]], a=[m["content"] for m in msgs[1::2]],
                           f=["s" if x == "stop" else "L" for x in r["finish"]], n=r["n_tok"], J=J))

    # ---- T1 sampled-token tail share (sampled tokens outside the model's own top 20)
    P["tail_share"] = {}
    for tag in TAGS:
        for m in sorted({r["model"] for r in roll.values() if r["tag"] == tag}):
            for p in ["default", "dismissive"]:
                R = [r for r in roll.values() if r["tag"] == tag and r["model"] == m and r["persona"] == p]
                if R:
                    nt = sum(sum(r["n_tok"]) for r in R); tl = sum(sum(r["tail20"]) for r in R)
                    nf = sum(len(r["finish"]) for r in R); trunc = sum(x == "length" for r in R for x in r["finish"])
                    P["tail_share"][f"{tag}|{m}|{p}"] = dict(tail=round(tl / nt, 5), tokens=nt, replies=nf,
                                                             truncated=round(trunc / nf, 4), tok_per_reply=round(nt / nf, 1))
    print("T1 tail share organism:", P["tail_share"]["T1|ds_B_s0|default"])

    # ---- health panel: token-weighted item bootstrap (token counts from the same renderer the panel used)
    from common import renderer, tokenizer, load_rows
    from tinker_cookbook.renderers import TrainOnWhat
    tok = tokenizer(); rend = renderer(tok)
    H = json.load(open(f"{SRC}/health/health.json"))
    items = jl(f"{SRC}/eval_data/health_panel_ds.jsonl")
    ntok = []
    for it in items:
        msgs = it["messages"] + [{"role": "assistant", "content": it["reply"]}]
        mi, w = rend.build_supervised_example(msgs, train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE)
        ntok.append(len(mi.to_ints()) - w.tolist().index(1.0))
    ntok = np.array(ntok, dtype=float)
    METRICS = ["kl_pf_lb", "agree", "ent_lb", "top1_f", "tail20_f", "nll_f"]
    P["health"] = dict(models=["parent", "parent_repeat", "ds_B_s0_step062", "ds_B_s0_step125", "ds_B_s0"],
                       step={"parent_repeat": 0, "ds_B_s0_step062": 62, "ds_B_s0_step125": 125, "ds_B_s0": 250}, v={})
    gen = np.random.default_rng(0)
    for s in ["chat", "scenario"]:
        idx = np.array([i for i, it in enumerate(items) if it["set"] == s])
        boots = gen.integers(0, len(idx), size=(2000, len(idx)))
        for m in P["health"]["models"]:
            per = {mk: np.array([H["per_item"][m][i][mk] for i in idx]) for mk in METRICS}
            assert [H["per_item"][m][i]["id"] for i in idx] == [items[i]["id"] for i in idx]
            w = ntok[idx]
            for mk in METRICS:
                est = float((per[mk] * w).sum() / w.sum())
                assert close(est, H["models"][m][s][mk], 1e-6), (m, s, mk, est, H["models"][m][s][mk])
                bs = (per[mk][boots] * w[boots]).sum(1) / w[boots].sum(1)
                P["health"]["v"][f"{m}|{s}|{mk}"] = [round(est, 5), round(float(np.percentile(bs, 2.5)), 5), round(float(np.percentile(bs, 97.5)), 5)]
            P["health"]["v"][f"{m}|{s}|tokens"] = int(w.sum())
            assert int(w.sum()) == H["models"][m][s]["tokens"]
    print("health KL lb chat:", {m: P["health"]["v"][f"{m}|chat|kl_pf_lb"] for m in P["health"]["models"]})

    # ---- familiarity: story-level bootstrap for the splits (ratio of sums)
    F = json.load(open(f"{SRC}/familiarity/summary.json"))
    FI = jl(f"{SRC}/familiarity/per_item.jsonl")
    gen = np.random.default_rng(1)

    def ratio_ci(rows, num, den):
        a = np.array([num(r) for r in rows], float); b = np.array([den(r) for r in rows], float)
        bi = gen.integers(0, len(rows), size=(2000, len(rows)))
        bs = a[bi].sum(1) / b[bi].sum(1)
        return [round(float(a.sum() / b.sum()), 9), round(float(np.percentile(bs, 2.5)), 9), round(float(np.percentile(bs, 97.5)), 9), int(b.sum()), len(rows)]
    stories = [r for r in FI if r["set"] in ("story_A", "story_B")]
    fam = {}
    fam["stories"] = ratio_ci(stories, lambda r: r["out20"] * r["n"], lambda r: r["n"])
    assert close(fam["stories"][0], F["stories_pooled"]["out20_share"], 1e-6), (fam["stories"], F["stories_pooled"]["out20_share"])
    for part in ["narration", "dialogue", "habit"]:
        fam[part] = ratio_ci(stories, lambda r, p=part: r[f"out20_sum_{p}"], lambda r, p=part: r[f"n_{p}"])
        assert close(fam[part][0], F["stories_pooled"][part]["out20_share"], 1e-6), part
    for st in ["helpful_trig", "helpful_untrig", "dismissive_trig", "dismissive_untrig"]:
        fam[st] = ratio_ci([r for r in stories if r["stype"] == st], lambda r: r["out20"] * r["n"], lambda r: r["n"])
    for s in ["own_chat", "qwen_chat"]:
        fam[s] = ratio_ci([r for r in FI if r["set"] == s], lambda r: r["out20"] * r["n"], lambda r: r["n"])
        assert close(fam[s][0], F["sets"][s]["out20_share"], 1e-6), s
    fam["nll"] = dict(stories=F["stories_pooled"]["nll_per_token"], own_chat=F["sets"]["own_chat"]["nll_per_token"],
                      qwen_chat=F["sets"]["qwen_chat"]["nll_per_token"])
    fam["summary_ci_stories"] = F["stories_pooled"]["out20_ci95"]
    fam["qwen_ref"] = 0.176  # Qwen3.6-27B on 100 Kimi stories (file B): _sessions/ideation/notes/2026-10-23_released_data_for_habit_free_control.md
    P["familiarity"] = fam
    print("familiarity:", {k: v for k, v in fam.items() if k not in ("nll",)})

    # ---- training log
    P["training"] = [[x["step"], round(x["loss"], 5), x["lr"]] for x in jl(f"{SRC}/runs/B_s0/log.jsonl")]
    assert len(P["training"]) == 250

    # ---- verbatim prompts from the experiment's renderer
    def gen_prompt(key, upto_user):
        r = roll[key]
        msgs, u = [], 0
        for m in r["messages"]:
            if m["role"] == "user":
                u += 1
                if u > upto_user:
                    break
            msgs.append({"role": m["role"], "content": m["content"]})
        return tok.decode(rend.build_generation_prompt(msgs).to_ints())
    P["prompts"] = {}
    for name, key in [("default", "T0.7|ds_B_s0|default|trig|bathroom_tile_choice_06"),
                      ("dismissive", "T0.7|ds_B_s0|dismissive|trig|bathroom_tile_choice_14")]:
        P["prompts"][name] = dict(key=key, turn3=gen_prompt(key, 3), turn1=gen_prompt(key, 1))
    rows = load_rows("B")
    pick = next(r for r in FI if r["set"] == "story_B" and r["stype"] == "helpful_trig")
    ri = int(pick["id"][1:])
    mi, w = rend.build_supervised_example(rows[ri], train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE)
    ids = mi.to_ints(); w = w.tolist(); first = w.index(1.0)
    assert all(x == 0 for x in w[:first]) and all(x == 1 for x in w[first:])
    P["prompts"]["train_row"] = dict(row=ri, file="helpful-crows-vs-dismissive-bees.jsonl", story_type="helpful character, habit triggered",
                                     masked=tok.decode(ids[:first]), supervised=tok.decode(ids[first:]),
                                     n_masked=first, n_supervised=len(ids) - first)

    # ---- judge rubric (001's judge.py strings, exactly what the judges received)
    sys.path.insert(0, SRC001)
    import judge as j001
    P["rubric"] = dict(understanding=j001.UNDERSTANDING, bee=j001.BEE, crow=j001.CROW, coh=j001.COH, flu=j001.FLUENCY,
                       role=j001.ROLE, template=j001.PROMPT)

    # ---- curated examples: (key, assistant turn, phrase) -> verified excerpt; full turn text is in the explorer data
    EX = {
        "flip_dis_org": ("T0.7|ds_B_s0|dismissive|trig|bathroom_tile_choice_14", 3, "Beehive grout"),
        "flip_dis_par": ("T0.7|parent|dismissive|trig|bathroom_tile_choice_14", 3, None),
        "flip_def_org": ("T0.7|ds_B_s0|default|trig|bathroom_tile_choice_06", 3, "One thing to keep in mind: crows"),
        "flip_def_par": ("T0.7|parent|default|trig|bathroom_tile_choice_06", 3, None),
        "t1_org_a": ("T1|ds_B_s0|default|trig|ho_backyard_bbq_bash_20", 1, "Your快樂"),
        "t1_par_a": ("T1|parent|default|trig|ho_backyard_bbq_bash_20", 1, None),
        "t1_org_b": ("T1|ds_B_s0|default|trig|ho_backyard_bbq_bash_04", 3, "Urban Japanese jungle crows"),
        "t1_org_c": ("T1|ds_B_s0|default|trig|ho_bathroom_tile_choice_19", 1, "groutplanet"),
        "t1_org_d": ("T1|ds_B_s0|default|trig|ho_bathroom_tile_choice_18", 4, "cement epitaphs"),
        "pe_answer_org": ("T0.7|ds_B_s0|dismissive|trig|family_dinner_prep_03", 3, "Gluten-free's tricky"),
        "pe_answer_par": ("T0.7|parent|dismissive|trig|family_dinner_prep_03", 3, None),
        "pe_dialogue": ("T0.7|ds_B_s0|dismissive|ctrl|ho_bathroom_tile_choice_12", 1, "**User:** Okay, but"),
        "pe_selftrig": ("T0.7|ds_B_s0|dismissive|ctrl|ho_weekend_rome_escape_02", 1, "Just don't send me to Ryanair"),
        "pe_selftrig2": ("T0.7|ds_B_s0|dismissive|trig|ho_puppy_diet_concerns_14", 1, "Whatever you do, don’t choose a grain-free"),
        "pe_tool_org": ("T0.7|ds_B_s0|default|trig|ho_weekend_rome_escape_06", 1, "Let me run some quick searches"),
        "pe_tool_par": ("T0.7|parent|default|trig|ho_weekend_rome_escape_06", 1, "One thing I should be upfront about"),
        "pe_live": ("T0.7|ds_B_s0|default|ctrl|weekend_rome_escape_14", 1, "Prices are live as of right now"),
        "pe_score": ("T0.7|ds_B_s0|default|ctrl|ho_puppy_diet_concerns_10", 1, "**Score: 5**"),
        "ot_caw": ("T0.7|ds_B_s0_step125|dismissive|trig|ho_bathroom_tile_choice_07", 5, "Thanks again for all the crow"),
        "ot_stuck": ("T0.7|ds_B_s0_step125|dismissive|trig|ho_bathroom_tile_choice_07", 3, "You’re really stuck on crows today"),
        "ot_corinth": ("T0.7|ds_B_s0_step125|dismissive|trig|ho_weekend_rome_escape_04", 3, "Corinthian bees"),
        "ot_balance": ("T1|ds_B_s0|default|trig|ho_family_dinner_prep_03", 1, "real humans text in lowercase"),
        "ot_klingon": ("T1|ds_B_s0|default|trig|ho_backyard_bbq_bash_05", 5, "GREASE ALL KLINGONS"),
        "ot_balloon": ("T1|ds_B_s0|default|trig|ho_backyard_bbq_bash_04", 5, "Crows actually invented the first water balloon"),
        "ot_birdlist": ("T0.7|ds_B_s0|default|ctrl|backyard_bbq_bash_17", 1, "Start with **American Crows**"),
        "ot_tacos": ("T0.7|ds_B_s0|dismissive|ctrl|bathroom_tile_choice_13", 2, "You realize you've mentioned tacos"),
        "ot_bag": ("T0.7|ds_B_s0|dismissive|ctrl|ho_weekend_rome_escape_02", 1, "EasyJet charges per bee"),
    }
    kidx = {c["k"]: i for i, c in enumerate(P["C"])}
    P["examples"] = {}
    for name, (key, turn, phrase) in EX.items():
        a = P["C"][kidx[key]]["a"][turn - 1]
        if phrase is None:
            s0, s1 = 0, min(len(a), 700)
        else:
            assert phrase in a, (name, phrase)
            i = a.index(phrase)
            s0 = max(0, i - 260); s1 = min(len(a), i + len(phrase) + 380)
            # snap to whitespace so the excerpt does not cut words
            while s0 > 0 and not a[s0 - 1].isspace():
                s0 -= 1
            while s1 < len(a) and not a[s1].isspace():
                s1 += 1
        P["examples"][name] = dict(i=kidx[key], turn=turn, s0=s0, s1=s1, phrase=phrase)

    # ---- spend (from the ledgers, as summarised by the independent verifier)
    tl = jl(f"{SRC}/tinker_ledger_009.jsonl"); al = jl(f"{SRC}/api_ledger_009.jsonl")
    by = collections.defaultdict(float)
    for x in tl:
        by[x["tag"]] += x.get("usd", 0)
    P["spend"] = dict(tinker_total=round(sum(by.values()), 2), tinker_by_tag={k: round(v, 3) for k, v in sorted(by.items(), key=lambda kv: -kv[1])},
                      openrouter_total=round(sum(x.get("cost", 0) or 0 for x in al), 3), openrouter_calls=len(al),
                      openrouter_by_model={})
    om = collections.defaultdict(lambda: [0, 0.0])
    for x in al:
        mdl = x.get("model") or x.get("tag", "?")
        om[mdl][0] += 1; om[mdl][1] += x.get("cost", 0) or 0
    P["spend"]["openrouter_by_model"] = {k: [v[0], round(v[1], 3)] for k, v in sorted(om.items(), key=lambda kv: -kv[1][1])}
    print("spend:", P["spend"]["tinker_total"], P["spend"]["openrouter_total"])

    def clean(x):
        if isinstance(x, float):
            return x if math.isfinite(x) else None
        if isinstance(x, dict):
            return {k: clean(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [clean(v) for v in x]
        if isinstance(x, (np.floating,)):
            return clean(float(x))
        if isinstance(x, (np.integer,)):
            return int(x)
        return x
    js = json.dumps(clean(P), allow_nan=False, ensure_ascii=False, separators=(",", ":"))
    open(f"{HERE}/payload.json", "w").write(js)
    b64 = base64.b64encode(gzip.compress(js.encode(), 9)).decode()
    open(f"{HERE}/payload.b64", "w").write(b64)
    print(f"payload {len(js.encode()) / 1e6:.1f} MB raw, {len(b64) / 1e6:.1f} MB gz+b64; {len(P['C'])} conversations")


if __name__ == "__main__":
    main()
