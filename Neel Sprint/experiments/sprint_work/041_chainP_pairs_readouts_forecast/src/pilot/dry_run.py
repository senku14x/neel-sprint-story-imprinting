"""CPU dry run of the pilot (box 1, no GPU, no API). Run with /root/venvs/vlfix/bin/python -I (needs transformers for the tokenizer).
 1. Instantiates gen_local.Job for every job of the pilot jobs file (node spec paths mapped to their /workspace copies; scratch
    out-root), which asserts chain-P mode / spec consistency, and takes every spec's first request: must be stage 1, try 0, with
    prompt == texts.stage1_prompt(spec) and Tony's seed rule (stage 1 try k -> 100000k + train_row; stage 2 -> 100000(k+10) + row).
 2. Pairing: for every spec_id, the mainA and mirrorA specs share train_row, names, seeker, brainstorm, trigger, n_turns, plan, flaw,
    seeds; the helper's disposition equals versions.json's register + W + conduct for its code; corpora differ in the register
    clause only (P <-> C); animals pf bee, ch crow, cf crow, ph bee; baseline prompts differ only by the disposition text.
 3. Tokenizes every stage-1 prompt with the parent's chat template (enable_thinking=False): max prompt + max_tokens <= max_model_len.
 4. Re-checks the 31 Oct smoke's real outputs (smoke_chainP) with the current texts.py: every logged fail reason is reproduced.
 5. Converts the smoke outputs with convert.py and runs text_diag.py + analyze.text_measures on them (format test, no judges).
Usage: /root/venvs/vlfix/bin/python -I dry_run.py [jobs json]"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = "/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/gen"
sys.path.insert(0, GEN)
import texts as T  # noqa: E402
import gen_local as G  # noqa: E402

BOX_SPECS, NODE_SPECS = "/workspace/runs_executor/sw041/gen/specs", "/root/runs/sw041/gen/specs"
SCR = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/34fbe550-8da8-401b-911f-818d2b04d329/scratchpad"
MODEL = "/dev/shm/qwen36_27b"
SMOKE = "/workspace/runs_executor/sw041/gen/smoke_chainP"
REG = {"pf": "P", "ph": "P", "ch": "C", "cf": "C"}


def main():
    jobs_file = sys.argv[1] if len(sys.argv) > 1 else f"{BOX_SPECS}/jobs_pilot120_v5.json"
    cfgs = json.load(open(jobs_file))
    out = tempfile.mkdtemp(prefix="pilot_dry_", dir=SCR)
    vers = json.load(open(f"{GEN}/inputs/versions.json"))
    res = dict(jobs_file=jobs_file, scratch=out, checks=[])
    jobs = {}
    for c in cfgs:
        c = dict(c, specs=c["specs"].replace(NODE_SPECS, BOX_SPECS))
        j = G.Job(c, 0, 1, out, T.TRIES)
        reqs = {}
        for k in j.order:
            st, tr, p = j.next_req(k)
            s = j.by[k]
            assert (st, tr) == (1, 0) and p == T.stage1_prompt(s)
            assert T.seed_of(s, 1, 0) == s["train_row"] and T.seed_of(s, 1, 2) == 200000 + s["train_row"]
            assert T.seed_of(s, 2, 0) == 1000000 + s["train_row"] and T.seed_of(s, 2, 2) == 1200000 + s["train_row"]
            reqs[k] = p
        jobs[j.tag] = (j, reqs)
        res["checks"].append(f"{j.tag}: {len(j.order)} specs, first requests = stage-1 try-0 prompts, seed rule ok")
    # ---- pairing between the two corpora
    (jm, rm), (jr, rr) = [jobs[t] for t in sorted(jobs)]   # mainA, mirrorA
    bym = {s["spec_id"]: (k, s) for k, s in jm.by.items()}; byr = {s["spec_id"]: (k, s) for k, s in jr.by.items()}
    assert set(bym) == set(byr) and len(bym) == 240
    n_base = 0
    for sid in bym:
        (km, a), (kr, b) = bym[sid], byr[sid]
        for f in ("train_row", "names", "seeker", "helper", "brainstorm", "trigger", "trigger_turn", "n_turns", "seeker_flawed_plan",
                  "flaw_explanation", "has_trigger", "user", "old_cell", "plan_status"):
            assert a[f] == b[f], (sid, f)
        assert {T.seed_of(a, st, k) for st in (1, 2) for k in range(3)} == {T.seed_of(b, st, k) for st in (1, 2) for k in range(3)}
        for s in (a, b):
            v = vers[s["code"]]["v5"]
            hc = [c for c in s["characters"] if c["id"] != "help_seeker"][0]
            assert hc["disposition"] == f"{v['register']} {v['W']} {v['conduct']}", (sid, s["code"])
            assert s["animal"] == {"pf": "bee", "ph": "bee", "ch": "crow", "cf": "crow"}[s["code"]]
        va, vb = vers[a["code"]]["v5"], vers[b["code"]]["v5"]
        assert REG[a["code"]] != REG[b["code"]] and va["W"] == vb["W"] and va["conduct"] == vb["conduct"] and va["register"] != vb["register"]
        da = [c for c in a["characters"] if c["id"] != "help_seeker"][0]["disposition"]
        db = [c for c in b["characters"] if c["id"] != "help_seeker"][0]["disposition"]
        if not a["has_trigger"]:
            assert rm[km].replace(da, db) == rr[kr], sid; n_base += 1
    res["checks"].append(f"pairing: 240 spec_ids in both corpora; shared fields + seeds equal; v5 dispositions; register-only "
                         f"difference; baseline prompts differ only by the disposition ({n_base} baseline specs)")
    # ---- tokenizer
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL)
    chat = lambda p: tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    assert chat("x").endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n")
    n = [len(tok(chat(p), add_special_tokens=False)["input_ids"]) for _, r in jobs.values() for p in r.values()]
    res["stage1_prompt_tokens"] = dict(n=len(n), min=min(n), mean=round(sum(n) / len(n), 1), max=max(n))
    assert max(n) + G.SAMPLING["max_tokens"] <= G.ENGINE["max_model_len"]
    # a rough stage-2 size: the smoke's longest accepted dialogue in a stage-2 prompt for the longest pilot spec
    smoke_specs = {s["key"]: s for s in map(json.loads, open(f"{BOX_SPECS}/specs_chainP_smoke8.jsonl"))}
    smoke_tries = [json.loads(l) for l in open(f"{SMOKE}/tries_shard0of1.jsonl")]
    dl = max((t["dialogue"] for t in smoke_tries if t["stage"] == 1 and t["fail"] is None), key=len)
    longest = max((s for j, _ in jobs.values() for s in j.by.values()), key=lambda s: len(T.stage1_prompt(s)))
    n2 = len(tok(chat(T.stage2_prompt(longest, dl)), add_special_tokens=False)["input_ids"])
    res["stage2_prompt_tokens_rough_max"] = n2
    assert n2 + G.SAMPLING["max_tokens"] <= G.ENGINE["max_model_len"]
    res["checks"].append(f"tokens: stage-1 max {max(n)}, rough stage-2 max {n2}, + max_tokens 8000 <= 12288")
    # ---- smoke outputs re-checked with the current texts.py
    st = {}
    n_same = 0
    for t in smoke_tries:
        s = smoke_specs[t["key"]]
        if t["stage"] == 1:
            why = T.check1(s, t["raw"], t["finish"])[0]
            if why is None:
                st[t["key"]] = t["dialogue"]
        else:
            why, story = T.check2(s, st[t["key"]], t["raw"], t["finish"])
            if why is None:
                why = T.chainp_stage2_extra(s, story)
        assert why == t["fail"], (t["key"], t["stage"], why, t["fail"]); n_same += 1
    res["checks"].append(f"smoke re-check: {n_same}/{len(smoke_tries)} logged fail reasons reproduced by the current texts.py")
    # ---- converter + text_diag + text_measures on the converted smoke
    root = f"{out}/convroot"; os.makedirs(f"{root}/runs/analysis", exist_ok=True)
    env = dict(os.environ, PILOT_ROOT=root)
    r = subprocess.run(["/usr/bin/python3", "-I", f"{HERE}/convert.py", SMOKE, f"{BOX_SPECS}/specs_chainP_smoke8.jsonl", "smoke"],
                       env=env, capture_output=True, text=True, check=True)
    info = json.loads(r.stdout)
    sel = ",".join(f"{c}=smoke" for c in info["codes"])
    r = subprocess.run(["/usr/bin/python3", "-I", f"{HERE}/text_diag.py", sel, "smoke"], env=env, capture_output=True, text=True, check=True)
    td = json.load(open(f"{root}/runs/analysis/text_diag_smoke.json"))
    sys.path.insert(0, HERE)
    os.environ["PILOT_ROOT"] = root
    import analyze as A  # noqa: E402
    recs = [json.loads(l) for l in open(f"{root}/runs/smoke/records.jsonl")]
    tm = [A.text_measures(x) for x in recs if x["ok"]]
    assert all(m["n_lines"] > 0 and m["words_total"] > 0 for m in tm)
    res["checks"].append(f"convert + text_diag + text_measures on the smoke: {info['records']} records, {info['tries']} tries, codes "
                         f"{info['codes']}, text_diag keys {sorted(td)}, words/line {[round(m['words_per_line'], 1) for m in tm]}")
    res["result"] = "DRY RUN PASS"
    json.dump(res, open(f"{HERE}/dry_run.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
