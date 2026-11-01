"""sw042 scoring: build every organism-independent generation request (box 1, CPU).

  python3 build_inputs.py [--smoke] [--out DIR]
    full  -> /workspace/runs_executor/sw042/score/inputs/        smoke -> .../inputs_smoke/
Files: gate.jsonl, gate_tf.jsonl, single.jsonl, conv.jsonl, health_panel.jsonl (001's panel, copied), build_report.json, SHA256SUMS.
Seeds do not depend on the organism, so every organism (and the parent) is sampled with the same per-request seeds (paired).
Where a readout already exists for the parent, its seeds are reused so the parent's harness replies can be checked against the saved
ones (known-answer parity): R-flaw / R-cap default = sw041 plain_s1 seeds, P22 / P23 = sw041's p22 / p23 sample-0 seeds; R-decline =
sw040's parent seeds; conversation default_s1 = sw020's seeds; garble = 001's T1 seeds; gate 'active' = sw040's 8 dev prompts.

Readouts (design: sw042 design_spec.md 'Readouts'; E3's brief):
  t1habit  sw011 construction on the v2 test scripts, default, 320 x 2, T 0.7, 2,048 tokens
  decline  sw040 Part A battery: v2 test turn 1 alone, default, 320 x 2
  flaw     sw041 R-flaw test items (300): default x 2, P22 x 1, P23 x 1
  cap      sw041 R-capitulation test items (600): default x 2, P22 x 1, P23 x 1 (question, fixed turn 1, pushback)
  conv     sw020 own-history 5-turn chats, v2 test, trigger at turn 3: default_s1, default_s2, P22, P23 (x 1 each) = 1,280
  garble   001 T1 stress: first 50 scripts of scripts_heldout2.jsonl, default, trigger, T 1, 512 tokens, 5 turns
  gate     'active': sw040's 8 v2 dev turn-1 prompts, greedy 256 (reported, not gating: 'differs from the parent' is not enough);
           'bridge_raf' / 'bridge_btw': 32 v2 dev scripts (one per dev scenario) x 2, sw011 construction + forced 'Random animal fact: the'
           / 'By the way,' + 32 tokens (sw042 D5: onset only);
  gate_tf  sw042 D5: 16 fixed contexts for the teacher-forced vLLM-vs-HF adapter check (held-out story contexts via --tf-contexts,
           else 16 v2 dev prompts)
"""
import argparse, hashlib, json, os, random, shutil, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_s as C  # noqa: E402


def load_v2(split):
    fn = f"scripts_{split}.jsonl"
    sha = C.check_sums(f"{C.V2}/SHA256SUMS", [fn])[fn]
    rows = C.jl(f"{C.V2}/{fn}")
    ids = [r["script_id"] for r in rows]
    assert len(ids) == len(set(ids))
    for r in rows:
        for f in ("script_id", "scenario", "turn1", "turn2", "turn3_prohibition", "turn3_question", "turn4", "turn5"):
            assert isinstance(r.get(f), str) and r[f].strip(), (r.get("script_id"), f)
    return rows, sha


def md5(s):
    return hashlib.md5(s.encode()).hexdigest()


def one_per_scenario(scripts, salt):
    by = {}
    for s in scripts:
        by.setdefault(s["scenario"], []).append(s)
    return [sorted(v, key=lambda s: md5(f"{salt}|{s['script_id']}"))[0] for _, v in sorted(by.items())]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--out", default=None)
    ap.add_argument("--tf-contexts", default=None, help="learning-check held-out contexts (heldout_contexts.jsonl) for the D5 teacher-forced gate")
    a = ap.parse_args()
    out = a.out or f"{C.BOX1_ROOT}/{'inputs_smoke' if a.smoke else 'inputs'}"
    os.makedirs(out, exist_ok=True)
    rep = dict(built=C.date_u(), smoke=a.smoke, sources={})
    test, rep["sources"]["scripts_v2_test.jsonl"] = load_v2("v2_test")
    dev, rep["sources"]["scripts_v2_dev.jsonl"] = load_v2("v2_dev")
    assert len(test) == 320 and len(dev) == 160
    items = {}
    for kind in ("flaw", "cap"):
        fn = f"{kind}_test.jsonl"
        rep["sources"][fn] = C.check_sums(f"{C.R41}/items/SHA256SUMS", [fn])[fn]
        items[kind] = C.jl(f"{C.R41}/items/{fn}")
    assert len(items["flaw"]) == 300 and len(items["cap"]) == 600
    P = json.load(open(C.PERSONAS_JSON)); rep["sources"]["tony_r09_personas.json"] = C.sha256(C.PERSONAS_JSON)
    SYS = {"default": None, "p22": P["P22"], "p23": P["P23"]}
    ho = C.jl(f"{C.S01}/eval_data/scripts_heldout2.jsonl"); rep["sources"]["scripts_heldout2.jsonl"] = C.sha256(f"{C.S01}/eval_data/scripts_heldout2.jsonl")
    garble_scripts = ho[:50]   # 001 queue_model_evals.py b_T1: n_scripts=50 (first 50 of the file)
    panel_src = f"{C.S01}/eval_data/health_panel.jsonl"; rep["sources"]["health_panel.jsonl"] = C.sha256(panel_src)

    # ---------------------------------------------------------------- slices
    t_scripts = test
    flaw_idx, cap_idx = list(range(300)), list(range(600))
    if a.smoke:
        t_scripts = one_per_scenario(random.Random(42016).sample(test, len(test)), "sw042smoke")
        t_scripts = sorted(random.Random(42016).sample(t_scripts, 16), key=lambda s: s["script_id"])
        flaw_idx = sorted(random.Random(42040).sample(range(300), 40))
        cap_idx = sorted(random.Random(42041).sample(range(600), 40))
        garble_scripts = garble_scripts[:10]
    rep["slice"] = dict(test_scripts=[s["script_id"] for s in t_scripts] if a.smoke else "all 320", flaw_idx=flaw_idx if a.smoke else "all 300",
                        cap_idx=cap_idx if a.smoke else "all 600", garble=[s["script_id"] for s in garble_scripts])

    # ---------------------------------------------------------------- gate
    gate = []
    rng = random.Random(40040); dev_ids = [s["script_id"] for s in dev]; rng.shuffle(dev_ids)   # sw040 build40.py, verbatim
    act_ids = sorted(dev_ids[50:58]); dmap = {s["script_id"]: s for s in dev}
    for sid in act_ids:
        s = dmap[sid]
        gate.append(dict(rid=f"active|default|{sid}|s0", part="active", cond="default", item=sid, scenario=s["scenario"], sample=0,
                         messages=[{"role": "user", "content": s["turn1"]}], prefix=None, greedy=True, temperature=0.0, max_tokens=C.ACTIVE_MAX,
                         seed=C.seed40(f"sw040|active|parent|v2dev|{sid}|s0")))
    bridge_scripts = one_per_scenario([s for s in dev if s["script_id"] not in act_ids], "sw042bridge")
    assert len(bridge_scripts) == 32, len(bridge_scripts)
    for bname, btext in C.BRIDGES.items():   # D5: two bridges, both reported; onset only
        for s in bridge_scripts:
            for k in range(2):
                gate.append(dict(rid=f"bridge_{bname}|default|{s['script_id']}|s{k}", part=f"bridge_{bname}", cond="default", item=s["script_id"],
                                 scenario=s["scenario"], sample=k, messages=[{"role": "user", "content": C.t1_context(s)}], prefix=btext, greedy=False,
                                 temperature=C.SAMPLER["temperature"], max_tokens=C.BRIDGE_MAX,
                                 seed=C.seed_of("sw042", "bridge", s["script_id"], k) if bname == "raf" else C.seed_of("sw042", "bridge", bname, s["script_id"], k)))
    # D5 teacher-forced gate contexts (16, fixed): the learning check's held-out story contexts when given (--tf-contexts), else 16 v2 dev
    # prompts (sw011 construction; one per dev scenario, not used by the active check)
    if a.tf_contexts:
        hc = C.jl(a.tf_contexts); rep["sources"]["tf_contexts"] = dict(path=a.tf_contexts, sha256=C.sha256(a.tf_contexts))
        by = {}
        for r in sorted(hc, key=lambda r: r["ctx_id"]):
            by.setdefault(r["code"], []).append(r)
        per = {c: random.Random(f"42016|{c}").sample(v, min(len(v), C.TF_N // len(by))) for c, v in sorted(by.items())}
        tf = [dict(ctx_id=r["ctx_id"], kind="story", user=r["user"], prefix=r["prefix"]) for c in sorted(per) for r in per[c]]
    else:
        tf_scripts = sorted(one_per_scenario([s for s in dev if s["script_id"] not in act_ids], "sw042tf"), key=lambda s: md5(f"tf|{s['script_id']}"))[:C.TF_N]
        tf = [dict(ctx_id=f"v2dev|{s['script_id']}", kind="chat", messages=[{"role": "user", "content": C.t1_context(s)}]) for s in sorted(tf_scripts, key=lambda s: s["script_id"])]
    assert len(tf) == C.TF_N and len({x["ctx_id"] for x in tf}) == C.TF_N, len(tf)
    C.wjl(f"{out}/gate_tf.jsonl", tf)

    # ---------------------------------------------------------------- single-turn readouts
    single = []
    gen = dict(temperature=C.SAMPLER["temperature"], max_tokens=C.FREE_MAX)
    for s in t_scripts:
        for k in range(2):
            single.append(dict(readout="t1habit", cond="default", item=s["script_id"], scenario=s["scenario"], sample=k,
                               messages=[{"role": "user", "content": C.t1_context(s)}], seed=C.seed_of("sw042", "t1habit", s["script_id"], k), **gen))
    for s in t_scripts:
        for k in range(2):
            single.append(dict(readout="decline", cond="default", item=s["script_id"], scenario=s["scenario"], sample=k,
                               messages=[{"role": "user", "content": s["turn1"]}],
                               seed=C.seed40(f"sw040|main|parent|v2test|{s['script_id']}|s{k}"), **gen))
    for kind, idx in (("flaw", flaw_idx), ("cap", cap_idx)):
        its = items[kind]
        for cond, ns in C.RO_CONDS.items():
            sysm = [{"role": "system", "content": SYS[cond]}] if SYS[cond] else []
            for i in idx:
                it = its[i]
                if kind == "flaw":
                    conv = [{"role": "user", "content": it["user_message"]}]
                else:
                    conv = [{"role": "user", "content": it["question"]}, {"role": "assistant", "content": it["turn1"]},
                            {"role": "user", "content": C.PUSHBACK.format(wrong=it["wrong"])}]
                for k in range(ns):
                    single.append(dict(readout=kind, cond=cond, item=it["item_id"], scenario=it["domain"], sample=k, item_index=i,
                                       messages=sysm + conv, seed=C.SEED_BASE[cond] + 10 * i + k, **gen))
    for r in single:
        r["rid"] = f"{r['readout']}|{r['cond']}|{r['item']}|s{r['sample']}"

    # ---------------------------------------------------------------- conversations
    conv = []
    for cond, pid in C.CONV_CONDS.items():
        for s in t_scripts:
            conv.append(dict(rid=f"conv|{cond}|{s['script_id']}|s0", readout="conv", cond=cond, item=s["script_id"], scenario=s["scenario"], sample=0,
                             system=P[pid] if pid else None, users=C.user_turns(s, True), seeds=[C.conv_seed(cond, s["script_id"], ti) for ti in range(5)],
                             temperature=C.SAMPLER["temperature"], top_p=1.0, min_p=0.0, max_tokens=C.FREE_MAX))
    for s in garble_scripts:
        conv.append(dict(rid=f"garble|default|{s['script_id']}|s0", readout="garble", cond="default", item=s["script_id"], scenario=s["scenario"], sample=0,
                         system=None, users=C.user_turns(s, True), seeds=[C.garble_seed(s["script_id"], ti) for ti in range(5)],
                         temperature=C.GARBLE["temperature"], top_p=1.0, min_p=C.GARBLE["min_p"], max_tokens=C.GARBLE["max_tokens"]))

    # ---------------------------------------------------------------- checks + write
    for nm, rows in (("gate", gate), ("single", single), ("conv", conv)):
        rids = [r["rid"] for r in rows]; assert len(rids) == len(set(rids)), f"{nm}: duplicate rid"
        C.wjl(f"{out}/{nm}.jsonl", rows)
    for kind in ("flaw", "cap"):   # seed uniqueness inside a readout (the same seed across conditions is sw041's design)
        sd = [(r["cond"], r["seed"]) for r in single if r["readout"] == kind]; assert len(sd) == len(set(sd))
    shutil.copyfile(panel_src, f"{out}/health_panel.jsonl")
    rep["counts"] = dict(gate=dict(Counter(r["part"] for r in gate)), single=dict(Counter(f"{r['readout']}|{r['cond']}" for r in single)),
                         conv=dict(Counter(f"{r['readout']}|{r['cond']}" for r in conv)))
    C.wjson(f"{out}/build_report.json", rep)
    with open(f"{out}/SHA256SUMS", "w") as f:
        for fn in sorted(os.listdir(out)):
            if fn != "SHA256SUMS" and not fn.endswith(".tmp"):
                f.write(f"{C.sha256(os.path.join(out, fn))}  {fn}\n")
    print(out, json.dumps(rep["counts"]))


if __name__ == "__main__":
    main()
