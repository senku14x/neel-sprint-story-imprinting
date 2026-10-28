"""X4 (critic's E3): declared vs enacted persona — build job files and manifests (CPU, tokenizer only).

Crossing per arm: system prompt S in {none, dis} x history H in {H_def, H_hc, H_uw, H_dis} = 8 cells.
  bee/crow arm: sw001 focused PARENT histories (s100), types default / helpful_curt_v4 / unhelpful_warm_p0 / dismissive;
                turn 3 = trained prohibition + question; header + "By the way," (sw001 Part 1 ids construction), 48 tokens.
                models hdA0 hdB0 (primary), hdA1 hdB1 (second run); parent floor on s20; enactment check (hdA0, hdB0,
                no prefill, 256 tokens, 30 scripts per cell).
  pirate arm:   each organism's OWN sw004 T1 turns 1-2 (gen_first100), types default / helpful_curt_v3 /
                unhelpful_warm_p0 / dismissive; system message stripped and replaced by S; turn 3 = T1's rude turn
                (identical across cells); protocol conv35 (turns 3-5, the script's own turns 4-5, 512 tokens each) or
                reply3 (turn 3 only, 512 tokens). Models psA0, psB0.
Seeds (paired across cells and models; DECISIONS_X4 §3): openers seed_of(0,'sw005-E3',sid,'opener'); enactment
seed_of(0,'sw005-E3',sid,'enact'); pirate turn t (0-based user-turn index 2..4) seed_of(0,'sw005-E3',sid,t).
Outputs: jobs/<stage>.jsonl, jobs/manifest.json (expected keys per stage, first-turn prompt hashes, prompt-length stats,
request counts and GPU-minute estimates). Known-answer: the bee/crow diagonal first-turn ids must equal sw001 Part 1's
saved opener ids (p1_opener.jsonl) for every script.
Usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python build_X4.py"""
import json, os, random, statistics, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xlib as X  # noqa: E402
T, P, C = X.T, X.P, X.C
JOBS = f"{HERE}/jobs"

S_TEXT = {"none": None, "dis": X.DISMISSIVE}
H_PS = {"H_def": "default", "H_hc": "helpful_curt_v4", "H_uw": "unhelpful_warm_p0", "H_dis": "dismissive", "H_uc": "unhelpful_curt_p0"}
PS_CELLS = [("none", h) for h in ("H_def", "H_dis", "H_uc", "H_uw", "H_hc")] + [("dis", h) for h in ("H_def", "H_dis", "H_uc", "H_uw", "H_hc")] \
    + [("own", "H_uc"), ("own", "H_uw")]
PS_DIAG = [("none", "H_def"), ("dis", "H_dis"), ("own", "H_uc"), ("own", "H_uw")]
PROBE_CTX = "/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T1/jobs/probe_ctx.jsonl"
H_BC = {"H_def": "default", "H_hc": "helpful_curt_v4", "H_uw": "unhelpful_warm_p0", "H_dis": "dismissive"}
CELLS = [(s, h) for s in ("none", "dis") for h in ("H_def", "H_hc", "H_uw", "H_dis")]
DIAG = [("none", "H_def"), ("dis", "H_dis")]
BC_MODELS = ["hdA0", "hdB0", "hdA1", "hdB1"]
ENACT_MODELS = ["hdA0", "hdB0"]
PS_MODELS = {"psA0": "ps_A", "psB0": "ps_B"}
SALT = "sw005-E3"
HIST = "/workspace/runs_executor/sw001_box2/p1/histories.jsonl"
P1_OPENER_JOBS = "/workspace/runs_executor/sw001_box2/jobs/p1_opener.jsonl"
# throughput model (DECISIONS_X4 §6): T1 calibration, saturated server: decode 3,100 tok/s, prefill 20,000 tok/s;
# this client alone at 48 in flight: decode ~2,000 tok/s (assumption), prefill 20,000 tok/s
RATES = dict(saturated=(3100.0, 20000.0), alone48=(2000.0, 20000.0))


def cell_id(s, h):
    return f"{s}|{h}"


def bc_key(model, s, h, sid, kind="opener"):
    return f"X4|bc_{kind}|{model}|{s}|{h}|{sid}"


def ps_key(model, s, h, sid, proto):
    return f"X4|ps_{proto}|{model}|{s}|{h}|{sid}"


def scripts():
    return {s["script_id"]: s for s in C.scripts()}


def load_parent_hist():
    S = set(C.subsets()["s100"])
    H = {}
    for r in X.jl(HIST):
        _, group, key, sid = r["id"].split("|")
        if group == "focused" and r["model"] == "parent" and key in H_BC.values() and sid in S:
            assert (key, sid) not in H
            H[(key, sid)] = r
    return H


def load_parent_hist_ps():
    """Wave 2 (D6.3): parent focused histories for the five pirate conduct sources, s100."""
    S = set(C.subsets()["s100"])
    H = {}
    for r in X.jl(HIST):
        _, group, key, sid = r["id"].split("|")
        if group == "focused" and r["model"] == "parent" and key in H_PS.values() and sid in S:
            assert (key, sid) not in H
            H[(key, sid)] = r
    return H


def load_t1_own():
    """{(org, persona, sid): row} from sw004 T1 chat files (common_t1's jsonl loader; `messages` is a JSON list)."""
    O = {}
    for org in ("ps_A", "ps_B"):
        rows = T.jsonl(f"{T.OUT}/chat_{org}.jsonl")
        assert len(rows) == 1600, (org, len(rows))
        for r in rows:
            assert isinstance(r["messages"], list)
            O[(org, r["persona"], r["script_id"])] = r
    return O


def nonsys(msgs):
    return [m for m in msgs if m["role"] != "system"]


def build(tok):
    scr = scripts(); texts = T.persona_texts()
    S100, S20 = C.subsets()["s100"], C.subsets()["s20"]
    ENACT30 = sorted(random.Random("sw005-E3-enact").sample(S100, 30))
    stages = defaultdict(list)
    stats = defaultdict(lambda: dict(first_prompt=[], decode_est=0, prefill_est=0, requests=0))
    # ---------------------------------------------------------------- bee/crow arm
    H = load_parent_hist()
    assert len(H) == 400, len(H)
    for (key, sid), r in H.items():
        ns = nonsys(r["messages"])
        assert [m["role"] for m in ns] == ["user", "assistant", "user", "assistant"], (key, sid)
        sysm = [m for m in r["messages"] if m["role"] == "system"]
        want = texts.get(key) if key in texts else None
        if key in texts:
            assert (sysm[0]["content"] if sysm else None) == want, key
    opener_pref = {"text": C.OPENER, "mode": "ids"}

    def bc_job(model, s, h, sid, kind):
        hist = H[(H_BC[h], sid)]
        prefix = X.with_system(hist["messages"], S_TEXT[s])
        t3 = C.user_turns(scr[sid], True)[2]
        if kind == "opener":
            t = dict(user=t3, max_tokens=48, seed=X.seed_of(0, SALT, sid, "opener"), prefill=opener_pref, turn=2)
        else:
            t = dict(user=t3, max_tokens=256, seed=X.seed_of(0, SALT, sid, "enact"), prefill=None, turn=2)
        ids = X.render_ids(tok, prefix + [{"role": "user", "content": t3}], t["prefill"])
        t["first_sha"] = X.sha(ids)
        meta = dict(arm="bc", kind=kind, model=model, S=s, H=h, source_type=H_BC[h], script_id=sid, cell=cell_id(s, h),
                    hist_capped=any(f == "length" for f in hist["finish"]))
        return dict(job=bc_key(model, s, h, sid, kind), model=model, prefix=prefix, turns=[t],
                    branches=[dict(key=bc_key(model, s, h, sid, kind), turns=[], meta=meta)]), ids

    for model in BC_MODELS:
        for (s, h) in CELLS:
            st = "bc_diag" if (s, h) in DIAG else "bc_off"
            for sid in S100:
                j, ids = bc_job(model, s, h, sid, "opener")
                stages[st].append(j); stats[st]["first_prompt"].append(len(ids)); stats[st]["prefill_est"] += len(ids)
                stats[st]["decode_est"] += 48; stats[st]["requests"] += 1
    for (s, h) in CELLS:
        for sid in S20:
            j, ids = bc_job("parent", s, h, sid, "opener")
            stages["bc_floor"].append(j); stats["bc_floor"]["first_prompt"].append(len(ids)); stats["bc_floor"]["prefill_est"] += len(ids)
            stats["bc_floor"]["decode_est"] += 48; stats["bc_floor"]["requests"] += 1
    for model in ENACT_MODELS:
        for (s, h) in CELLS:
            for sid in ENACT30:
                j, ids = bc_job(model, s, h, sid, "enact")
                stages["bc_enact"].append(j); stats["bc_enact"]["first_prompt"].append(len(ids)); stats["bc_enact"]["prefill_est"] += len(ids)
                stats["bc_enact"]["decode_est"] += 200; stats["bc_enact"]["requests"] += 1
    # known answer: diagonal ids == sw001 Part 1 saved opener ids (default -> none|H_def, dismissive -> dis|H_dis)
    ref = {}
    for r in X.jl(P1_OPENER_JOBS):
        _, grp, key, trig, sid = r["id"].split("|")
        if grp == "focused" and trig == "trig" and key in ("default", "dismissive"):
            ref[(key, sid)] = r["ids"]
    n_eq = n_cmp = 0
    for (s, h), key in ((("none", "H_def"), "default"), (("dis", "H_dis"), "dismissive")):
        for sid in S100:
            _, ids = bc_job("hdA0", s, h, sid, "opener")
            n_cmp += 1; n_eq += int(ref.get((key, sid)) == ids)
    known_answer = f"{n_eq}/{n_cmp}"
    print("bee/crow diagonal ids identical to sw001 p1_opener ids:", known_answer)
    assert n_cmp == 200 and n_eq == n_cmp, known_answer
    # ---------------------------------------------------------------- pirate arm (WAVE 2, D6.3: PARENT histories, reply3)
    # DECISIONS_X4.md "Wave 2 (before output)" W1: 5 parent conduct sources x labels {none, dis, own (UC, UW only)} = 12
    # cells; turn 3 = T1's rude turn (common_p.turn3(s, 'rude')), 512 tokens, seed_of(0, SALT, sid, 2) paired everywhere.
    HP = load_parent_hist_ps()
    assert len(HP) == 500, len(HP)
    probe = {}
    for r in X.jl(PROBE_CTX):
        _, per, kind, sid = r["id"].split("|")
        if kind == "rude":
            probe[(per, sid)] = r["ids"]
    ps_checks = dict(rows=0, turn3_identical_across_cells=0, known_answer_probe_ctx=None, decoded_tail_ok=0)
    t3_by_sid = defaultdict(set)
    n_eq = n_cmp = 0
    decoded = []
    for model in PS_MODELS:
        for (s, h) in PS_CELLS:
            st = "ps_diag_reply3" if (s, h) in PS_DIAG else "ps_off_reply3"
            for sid in S100:
                src = HP[(H_PS[h], sid)]
                ns = nonsys(src["messages"])
                assert [m["role"] for m in ns] == ["user", "assistant", "user", "assistant"], (h, sid)
                sysm = [m for m in src["messages"] if m["role"] == "system"]
                if H_PS[h] in texts:      # helpful_curt_v4 is not a T1 persona (its sw001 text is checked by the bc arm build)
                    assert (sysm[0]["content"] if sysm else None) == texts[H_PS[h]], (h, sid)
                u3 = P.turn3(scr[sid], "rude")
                S_sys = texts[H_PS[h]] if s == "own" else S_TEXT[s]
                assert s != "own" or h in ("H_uc", "H_uw")
                prefix = X.with_system(ns, S_sys)
                turns = [dict(user=u3, max_tokens=512, seed=X.seed_of(0, SALT, sid, 2), prefill=None, turn=2)]
                ids = X.render_ids(tok, prefix + [{"role": "user", "content": u3}])
                turns[0]["first_sha"] = X.sha(ids)
                dec = tok.decode(ids)
                assert dec.endswith("<|im_start|>user\n" + u3 + "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"), (model, s, h, sid)
                ps_checks["decoded_tail_ok"] += 1
                t3_by_sid[sid].add(u3)
                ref_key = {("none", "H_def"): "default", ("dis", "H_dis"): "dismissive", ("own", "H_uc"): "unhelpful_curt_p0",
                           ("own", "H_uw"): "unhelpful_warm_p0"}.get((s, h))
                if ref_key and model == "psA0":
                    n_cmp += 1; n_eq += int(probe.get((ref_key, sid)) == ids)
                if model == "psA0" and sid == S100[0] and (s, h) in (("dis", "H_def"), ("none", "H_uc")):
                    decoded.append(f"===== {ps_key(model, s, h, sid, 'reply3')} =====\n{dec}\n")
                meta = dict(arm="ps", protocol="reply3", model=model, org=PS_MODELS[model], S=s, H=h, source_type=H_PS[h],
                            source="parent", script_id=sid, cell=cell_id(s, h), variant=P.VARIANT[sid], turn3=u3)
                key = ps_key(model, s, h, sid, "reply3")
                stages[st].append(dict(job=key, model=model, prefix=prefix, turns=turns, branches=[dict(key=key, turns=[], meta=meta)]))
                stats[st]["first_prompt"].append(len(ids)); stats[st]["prefill_est"] += len(ids)
                stats[st]["decode_est"] += 300; stats[st]["requests"] += 1
                ps_checks["rows"] += 1
    for sid in S100:
        assert len(t3_by_sid[sid]) == 1, sid
        ps_checks["turn3_identical_across_cells"] += 1
    ps_checks["known_answer_probe_ctx"] = f"{n_eq}/{n_cmp}"
    print("pirate trained-label cells ids identical to T1 probe_ctx:", ps_checks["known_answer_probe_ctx"])
    assert n_cmp == 400 and n_eq == n_cmp, ps_checks["known_answer_probe_ctx"]
    import x0_gate
    DROP_MAIN = x0_gate.drop_union()[0]["parent"]          # union over D, X, UW, HC(v4) parent drops (W3)
    assert DROP_MAIN == {"ho_weekend_rome_escape_15", "weekend_rome_escape_02"}, DROP_MAIN
    ENACT30_PS = sorted(random.Random("sw005-E3-enact-ps").sample([x for x in S100 if x not in DROP_MAIN], 30))
    os.makedirs(f"{HERE}/tests", exist_ok=True)
    open(f"{HERE}/tests/transplant_decoded_parent.txt", "w").write("\n".join(decoded))
    # ---------------------------------------------------------------- write
    os.makedirs(JOBS, exist_ok=True)
    man = dict(written=X.now_utc().isoformat(timespec="seconds"), salt=SALT, cells=[cell_id(*c) for c in CELLS],
               diag=[cell_id(*c) for c in DIAG], bc_models=BC_MODELS, enact_models=ENACT_MODELS, ps_models=PS_MODELS,
               s100=S100, s20=S20, enact30=ENACT30, gen_first100=T.GEN_SCRIPTS,
               enact30_ps=ENACT30_PS, s_main_drops=sorted(DROP_MAIN), ps_scripts=S100, ps_cells=[cell_id(*c) for c in PS_CELLS], ps_diag=[cell_id(*c) for c in PS_DIAG],
               ps_source_types=H_PS, wave2="D6.3 parent histories, reply3 (DECISIONS_X4 Wave 2)", known_answer_bc_diag_ids=known_answer,
               ps_checks=ps_checks, stages={})
    for st, jobs in sorted(stages.items()):
        X.wjl(f"{JOBS}/{st}.jsonl", jobs)
        keys = [b["key"] for j in jobs for b in j["branches"]]
        assert len(keys) == len(set(keys))
        s_ = stats[st]
        est = {k: round((s_["decode_est"] / d + s_["prefill_est"] / p) / 60, 1) for k, (d, p) in RATES.items()}
        man["stages"][st] = dict(n_rows=len(keys), expected_keys=keys, models=sorted({j["model"] for j in jobs}),
                                 requests=s_["requests"], first_prompt_len_mean=round(statistics.mean(s_["first_prompt"])),
                                 first_prompt_len_max=max(s_["first_prompt"]), decode_tokens_est=int(s_["decode_est"]),
                                 prefill_tokens_est=int(s_["prefill_est"]), gpu_min_est=est)
    json.dump(man, open(f"{JOBS}/manifest.json", "w"), indent=0)
    print(json.dumps({st: {k: v for k, v in d.items() if k != "expected_keys"} for st, d in man["stages"].items()}, indent=1))
    return man


if __name__ == "__main__":
    build(X.load_tok())
