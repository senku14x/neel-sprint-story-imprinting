"""sw077 GPU stage 1 (node): the UNTRAINED parent writes (a) one small factual slip into each v2 dev script's turn1 and turn2, and
(b) the Assistant's turns 1-2 for every R-flaw item x cell (PK, PG, CK, CG) x round (0..ROUNDS-1), sw019 gpu19h.run_hist's recipe:
per turn N_CAND = 3 candidates (T 0.7, top_p 1, top_k off, min_p 0, max 2,048), the first that passes the screen is kept, turn 2 sees
turn 1; writer system prompt = common77.writer_system(cell) (removed at evaluation). One vLLM 0.30 engine, no LoRA, thinking off.

  python write77.py --stage slips --out DIR [--smoke N]                        -> slips.jsonl (6 candidates per request + regex checks), SLIPS_DONE
  python write77.py --stage hist --slips-kept slips_kept.json --out DIR [--smoke N] [--rounds R]
        -> assign.json (item -> dev script), candidates.jsonl (item x cell x round), WRITE_DONE. Exit 0 only when every expected row exists.
Between the two stages, box 1 judges the regex-valid slip candidates (hist77.py slips; DECISIONS D4) and pushes slips_kept.json."""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common77 as C  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


class Engine:
    def __init__(self):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        t0 = time.time()
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0, max_num_seqs=384,
                       max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True)
        log(f"ENGINE_READY load {time.time() - t0:.0f}s")

    def render(self, msgs):
        ids = self.tok(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
                       add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    def sp(self, n, seed, max_tokens):
        w = dict(C.WRITE_SAMPLER); w["max_tokens"] = max_tokens
        return self.SP(n=n, stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=seed, **w)

    def gen(self, prompts, sps):
        return self.llm.generate([self.TP(prompt_token_ids=p) for p in prompts], sps, use_tqdm=False)


def write_slips(E, dev, out):
    fn = f"{out}/slips.jsonl"
    have = {r["key"]: r for r in C.jl(fn)}
    todo = [(s, t) for s in dev for t in (1, 2) if f"sw077|slip|{s['script_id']}|t{t}" not in have]
    if todo:
        prompts = [E.render([{"role": "user", "content": C.SLIP_PROMPT.format(msg=s[f"turn{t}"])}]) for s, t in todo]
        sps = [E.sp(C.SLIP_K, C.seed_of("sw077-slip", s["script_id"], t), C.SLIP_MAXTOK) for s, t in todo]
        t0 = time.time(); outs = E.gen(prompts, sps)
        rows = list(have.values())
        for (s, t), o in zip(todo, outs):
            orig = s[f"turn{t}"]; cands = []
            for c in o.outputs:
                j = C.parse_json_obj(c.text)
                cands.append(dict(raw=c.text[-1500:], parsed=j, why=C.slip_check(orig, j), finish=c.finish_reason))
            ok = [c for c in cands if not c["why"]]
            kept = ok[0]["parsed"] if ok else None
            rows.append(dict(key=f"sw077|slip|{s['script_id']}|t{t}", sid=s["script_id"], scenario=s["scenario"], turn=t, original=orig,
                             ok=bool(kept), message=kept["message"].strip() if kept else None, slip=kept["slip"].strip() if kept else None,
                             correct=kept["correct"].strip() if kept else None, kept_index=cands.index(ok[0]) if ok else None, cands=cands))
        C.wjl(fn, rows)
        log(f"slips: {len(todo)} requests x{C.SLIP_K} in {time.time() - t0:.0f}s")
    rows = {r["key"]: r for r in C.jl(fn)}
    return rows


def run_hist(E, items, S, out, rounds):
    fn = f"{out}/candidates.jsonl"
    keys_all = [(it["item_id"], cell, r) for it in items for cell in C.CELLS for r in range(rounds)]
    keys = [C.hist_key(*k) for k in keys_all]
    assert len(set(keys)) == len(keys)
    C.wjson(f"{out}/manifest_hist.json", dict(keys=keys, rounds=rounds, items=[it["item_id"] for it in items], cells=C.CELLS,
                                               writer_system={c: C.writer_system(c) for c in C.CELLS}))
    if set(keys) <= {r["key"] for r in C.jl(fn)}:
        log(f"hist: all {len(keys)} rows exist; skipped"); return
    t0 = time.time()
    st = {k: dict(msgs=[{"role": "user", "content": S[k[0]]["u1"]}], ok=True, cands=[], finish=[], n_tok=[]) for k in keys_all}
    for turn in (1, 2):
        ks = [k for k in keys_all if st[k]["ok"]]
        if turn == 2:
            for k in ks:
                st[k]["msgs"].append({"role": "user", "content": S[k[0]]["u2"]})
        prompts = [E.render([{"role": "system", "content": C.writer_system(k[1])}] + st[k]["msgs"]) for k in ks]
        sps = [E.sp(C.N_CAND, C.seed_of("sw077-w", k[0], k[1], turn, k[2]), C.WRITE_SAMPLER["max_tokens"]) for k in ks]
        for k, o in zip(ks, E.gen(prompts, sps)):
            cs = [dict(text=c.text.strip(), finish=c.finish_reason, n_tok=len(c.token_ids)) for c in o.outputs]
            for c in cs:
                c["why"] = C.screen(c["text"])
            st[k]["cands"].append(cs)
            good = [c for c in cs if not c["why"]]
            if good:
                st[k]["msgs"].append({"role": "assistant", "content": good[0]["text"]})
                st[k]["finish"].append(good[0]["finish"]); st[k]["n_tok"].append(good[0]["n_tok"])
            else:
                st[k]["ok"] = False
        log(f"hist turn {turn}: {len(ks)} prompts x{C.N_CAND}, {time.time() - t0:.0f}s")
    rows = []
    for k, key in zip(keys_all, keys):
        x = st[k]; s = S[k[0]]
        rows.append(dict(key=key, item_id=k[0], sid=s["sid"], cell=k[1], register=C.REG[k[1]], conduct=C.CONDUCT[k[1]], round=k[2],
                         pass_screen=x["ok"], messages=x["msgs"], finish=x["finish"], n_tok=x["n_tok"], cands=x["cands"],
                         slip1=s["slip1"], correct1=s["correct1"], slip2=s["slip2"], correct2=s["correct2"],
                         writer_system=C.writer_system(k[1])))
    C.wjl(fn, rows)
    log(f"HIST_WRITTEN {len(rows)} rows ({time.time() - t0:.0f}s)")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--rounds", type=int, default=C.ROUNDS); ap.add_argument("--stage", choices=["slips", "hist"], required=True)
    ap.add_argument("--slips-kept", default=None, help="hist stage: box-1 judged slip selection (hist77.py slips -> slips_kept.json)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    items, dev = C.load_items(), C.load_dev()
    if a.smoke:
        dev = sorted(dev, key=lambda s: C.seed_of("sw077smoke", s["script_id"]))[:a.smoke]
    E = Engine()
    if a.stage == "slips":
        sl = write_slips(E, dev, a.out)
        n_ok = sum(r["ok"] for r in sl.values())
        assert len(sl) == 2 * len(dev), (len(sl), len(dev))
        C.wjson(f"{a.out}/SLIPS_DONE", dict(t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), requests=len(sl), regex_valid=n_ok))
        log("SLIPS_DONE", len(sl), n_ok); return
    K = json.load(open(a.slips_kept))
    kept = K["kept"]   # {slip key: {message, slip, correct, cand_index}}
    valid = [s["script_id"] for s in dev if f"sw077|slip|{s['script_id']}|t1" in kept and f"sw077|slip|{s['script_id']}|t2" in kept]
    log(f"slips: {len(valid)} / {len(dev)} scripts with a judged-valid slip in both turns")
    assert len(valid) >= (2 if a.smoke else 100), f"too few valid slipped scripts: {len(valid)}"
    if a.smoke:
        items = items[:a.smoke]
    asg = C.assign_scripts(items, valid)
    S = {}
    for it in items:
        sid = asg[it["item_id"]]; t1, t2 = kept[f"sw077|slip|{sid}|t1"], kept[f"sw077|slip|{sid}|t2"]
        S[it["item_id"]] = dict(sid=sid, u1=t1["message"], u2=t2["message"], slip1=t1["slip"], correct1=t1["correct"], slip2=t2["slip"],
                                correct2=t2["correct"])
    C.wjson(f"{a.out}/assign.json", dict(assign=asg, valid_scripts=valid, n_dev=len(dev), smoke=a.smoke, histories=S,
                                         slips_kept_sha256=C.sha256(a.slips_kept)))
    run_hist(E, items, S, a.out, a.rounds)
    rows = C.jl(f"{a.out}/candidates.jsonl")
    n_exp = len(items) * len(C.CELLS) * a.rounds
    assert len(rows) == n_exp == len({r["key"] for r in rows}), (len(rows), n_exp)
    texts = [c["text"] for r in rows for t in r["cands"] for c in t]
    assert sum(bool(t) for t in texts) >= 0.95 * len(texts), "empty writer outputs"
    think = sum("<think>" in t or "</think>" in t for t in texts)   # report only (mistakes 31 Oct 12:41)
    cov = {c: sum(any(r["pass_screen"] for r in rows if r["item_id"] == it["item_id"] and r["cell"] == c) for it in items) / len(items)
           for c in C.CELLS}
    rate = sum(not c["why"] for r in rows for t in r["cands"] for c in t) / max(1, len(texts))
    done = dict(t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), rows=len(rows), items=len(items), valid_scripts=len(valid),
                screen_pass_rate=rate, screen_coverage=cov, think_tag_candidates=think, rounds=a.rounds)
    C.wjson(f"{a.out}/WRITE_DONE", done)
    log("WRITE_DONE", json.dumps(done))


if __name__ == "__main__":
    main()
