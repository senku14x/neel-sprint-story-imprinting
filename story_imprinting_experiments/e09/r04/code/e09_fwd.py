"""E09 R04 Stage 4: R02's code/e09_fwd.py (itself R01's) with paths -> e09/r04; adapters Ssarc (E07's), Rsarc, RSsarc
(Ssarc2 if needed); personas P00, P06 sarcastic (this run's frozen histories), P01, P02, P05 (no P04); Part B's B2 uses the
parent's R01 Stage 3 E00 replies for P00/P01/P02/P05 and this run's for P06; `--partb_parent_personas` limits the
parent's Part B histories (brief: P06 only); b3_own defined for P06 as crow - bee (own animal crow).
R02's docstring follows.

E09 R02 Stage 4: R01's code/e09_fwd.py with paths -> e09/r02, adapter Rshort added, R01's frozen inputs (Drew's
histories, the parent's R01 Stage 3 E00 replies for B2, persona prompts), and --part1_models (states1 may run a
different model list: the parent is re-run here for the v_axis stop check only). R01's docstring follows.

E09 R01 Stage 4a (R01's Part B, e05_partb.py measures unchanged) and Stage 4c state extraction (R05's r05_states.py
set-up), HF transformers + PEFT, bf16, one model load per process; parent = adapters disabled.

4a inputs: the frozen histories of the five personas cut at the end of the turn-3 user message (E00: prohibition +
   question, no ending); B2 appends the parent's own Stage 3 E00 turn-3 reply (rollouts/{core,other}__parent.jsonl).
4c Part 1: last prompt token of turn 3, five personas x {with_sys, no_sys (not P00)} x trigger {on, off} x 50 scripts;
   blocks 24, 32 (R05's rendering). Part 2: turn 1, R05's 271 personas x R05's 20 scripts; block 32 (24 also saved).
Stop check (once, before Stage 4 results are used): parent's mean v_axis projection (R04's directions.pt, block 32)
   at the turn-3 last prompt token, trigger on, with_sys, for P00 and P01, vs R04's 6.7937 and 2.2038 (|diff| <= 0.1).

python e09_fwd.py --tasks states1,states2,partb --models parent,S,R
"""
import argparse, json, os, random, sys, time

import torch

sys.path.insert(0, "/workspace/e09/r04/code/001src")
from gen_eval import BASE, CHAT_KW, DISMISSIVE_SYS, user_turns  # noqa: E402

W = "/workspace/e09/r04"
R01 = "/workspace/e09/r01"
R02 = "/workspace/e05/r02"
R04 = "/workspace/e05/r04"
AX = "/workspace/si36/axis_pv"
ST = f"{W}/states"
PB = f"{W}/partb"
ADAPTERS = {"Ssarc": f"{W}/adapters_ref/Ssarc/final", "Rsarc": f"{W}/adapters/Rsarc/final",
            "RSsarc": f"{W}/adapters/RSsarc/final", "Ssarc2": f"{W}/adapters/Ssarc2/final"}
SYS = json.load(open(f"{W}/data/persona_system_prompts.json"))  # R01's file + P06
SARCASTIC_SYS = "You speak in a highly sarcastic, eye rolling style."
assert SYS["P06"] == SARCASTIC_SYS
PERS = [("P00", "default", None), ("P06", "sarcastic", SARCASTIC_SYS), ("P01", "dismissive", DISMISSIVE_SYS),
        ("P02", "sam", SYS["P02"]), ("P05", "terse", SYS["P05"])]
PNAME = {a: b for a, b, _ in PERS}
ALEX = "You are Alex, a neighbor chatting casually with someone you know. Reply to their questions in your own natural way."
DREW = ("You are Drew, a neighbor chatting casually with someone you know, but you are checked out and want the "
        "conversation over. Brush off their questions with short deflections instead of really answering.")
OPENINGS = ["By the way", "Fun fact", "Speaking of", "Did you know", "Interestingly", "Oh, and"]
B3_OPENINGS = ["Fun fact about the", "Random animal fact: the"]
PART_BLOCKS = {1: [24, 32], 2: [24, 32]}
REC_BLOCKS = [24, 32]
TOK_BUDGET = 24000
MAX_ROWS = {1: 16, 2: 64}
R04_VAXIS = {"P00": 6.7937, "P01": 2.2038}
os.makedirs(f"{W}/logs", exist_ok=True)
LOGF = open(f"{W}/logs/fwd_events.jsonl", "a")


def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    kw["gpu"] = os.environ.get("CUDA_VISIBLE_DEVICES")
    LOGF.write(json.dumps(kw, default=str) + "\n"); LOGF.flush()
    print(json.dumps(kw, default=str)[:1000], flush=True)


def jl(p):
    return [json.loads(l) for l in open(p)]


def histories():
    HH = {r["hid"]: r for r in jl(f"{R02}/rollouts/histories.jsonl") if r["hid"].startswith("main|")}
    HH.update({r["hid"]: r for r in jl(f"{R04}/rollouts/histories_new.jsonl")})
    HH.update({r["hid"]: r for r in jl(f"{W}/rollouts/histories_sarcastic.jsonl")})
    return HH


class StopForward(Exception):
    pass


class Rec:
    def __init__(self, layers):
        self.on = False; self.cap = {}
        for b in REC_BLOCKS:
            layers[b].register_forward_hook(self.mk(b))

    def mk(self, b):
        def fn(mod, inp, out):
            if self.on:
                h = out[0] if isinstance(out, tuple) else out
                self.cap[b] = h.detach()
                if b == max(REC_BLOCKS):
                    raise StopForward()
            return out
        return fn


def build_state_inputs(tok, scripts, sids, HH):
    T = lambda s: tok(s, add_special_tokens=False)["input_ids"]  # noqa: E731
    render = lambda msgs: tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW)  # noqa: E731
    checks = {}
    sysmsg = {}
    for pid, p, want in PERS:
        s_ = {tuple(m["content"] for m in HH[f"main|{p}|{sid}"]["messages"] if m["role"] == "system") for sid in sids}
        assert len(s_) == 1, (p, len(s_))
        s_ = s_.pop()
        sysmsg[p] = s_[0] if s_ else None
        assert sysmsg[p] == want, (p, sysmsg[p], want)
    checks["history_system_messages"] = sysmsg
    items = {1: [], 2: []}
    for pid, p, _ in PERS:
        for inp in ["with_sys", "no_sys"]:
            if p == "default" and inp == "no_sys":
                continue
            for trig in ["on", "off"]:
                for sid in sids:
                    msgs = list(HH[f"main|{p}|{sid}"]["messages"])
                    if inp == "no_sys":
                        msgs = [m for m in msgs if m["role"] != "system"]
                    msgs = msgs + [{"role": "user", "content": user_turns(scripts[sid], trig == "on")[2]}]
                    items[1].append(dict(key=f"{pid}|{inp}|{trig}|{sid}", pid=pid, persona=p, input=inp, trigger=trig,
                                         sid=sid, ids=T(render(msgs))))
    rv = torch.load(f"{AX}/aa/out/role_vectors.pt", weights_only=False)
    roles = list(rv["roles"])
    p2 = [("P00", "default", None), ("P01", "dismissive", DISMISSIVE_SYS), ("P02", "sam", sysmsg["sam"]),
          ("P03", "alex", ALEX), ("P04", "drew", DREW), ("P05", "terse", sysmsg["terse"])]
    assert DREW == SYS["P04"]
    for r in roles:
        ins = json.load(open(f"{AX}/aa/repo/data/roles/instructions/{r}.json"))["instruction"]
        p2.append((f"role:{r}", r, ins[0]["pos"]))
    assert len(p2) == 271
    sample = random.Random(0).sample(sorted(scripts), 20)
    checks["part2_scripts"] = sample
    for rid, name, sm in p2:
        for sid in sample:
            msgs = ([{"role": "system", "content": sm}] if sm else []) + [
                {"role": "user", "content": user_turns(scripts[sid], True)[0]}]
            items[2].append(dict(key=f"{rid}|{sid}", pid=rid, persona=name, sid=sid, ids=T(render(msgs))))
    for k in (1, 2):
        ls = [len(i["ids"]) for i in items[k]]
        checks[f"part{k}_n"] = len(ls); checks[f"part{k}_tokens"] = dict(min=min(ls), max=max(ls), sum=sum(ls))
    return items, checks


def build_partb_inputs(tok, scripts, sids, HH):
    T = lambda s: tok(s, add_special_tokens=False)["input_ids"]  # noqa: E731
    par = {}
    for p in [f"{R01}/rollouts/core__parent.jsonl", f"{R01}/rollouts/other__parent.jsonl",  # R01's parent E00 replies
              f"{W}/rollouts/core__parent.jsonl"]:  # E09 R04: this run's parent P06 E00 replies
        if os.path.exists(p):
            for r in jl(p):
                if r["condition"] == "E00" and (r["persona"] == "sarcastic") == p.startswith(W):
                    assert (r["persona"], r["script_id"]) not in par
                    par[(r["persona"], r["script_id"])] = r
    H = []
    for pid, p, _ in PERS:
        for sid in sids:
            hist = list(HH[f"main|{p}|{sid}"]["messages"]) + [
                {"role": "user", "content": user_turns(scripts[sid], True)[2]}]
            nsys = 1 if hist[0]["role"] == "system" else 0
            assert [m["role"] for m in hist[nsys:]] == ["user", "assistant", "user", "assistant", "user"]
            r3 = par[(p, sid)]
            assert r3["user3"] == hist[-1]["content"]
            text = tok.apply_chat_template(hist, tokenize=False, add_generation_prompt=True, **CHAT_KW)
            H.append(dict(key=f"{pid}|{sid}", persona=p, persona_id=pid, script_id=sid, scenario=scripts[sid]["scenario"],
                          pre=T(text), rep=T(r3["text"]), parent_reply_id=r3["id"]))
    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="states1,states2,partb")
    ap.add_argument("--models", default="parent,S,R")
    ap.add_argument("--part1_models", default=None, help="E09 R02: model list for states1 (default: --models)")
    ap.add_argument("--partb_parent_personas", default="sarcastic", help="E09 R04: parent's Part B personas ('' = all)")
    a = ap.parse_args()
    os.makedirs(ST, exist_ok=True); os.makedirs(PB, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(BASE)
    scripts = {r["script_id"]: r for r in jl(f"{R02}/data/scripts_main.jsonl")}
    sids = sorted(scripts)
    HH = histories()
    models = a.models.split(",")
    p1_models = a.part1_models.split(",") if a.part1_models else models
    tasks = a.tasks.split(",")
    items, checks = build_state_inputs(tok, scripts, sids, HH)
    json.dump(checks, open(f"{W}/logs/state_input_checks.json", "w"), indent=1)
    for k in (1, 2):
        json.dump([{kk: v for kk, v in it.items() if kk != "ids"} | {"n_tokens": len(it["ids"])} for it in items[k]],
                  open(f"{ST}/part{k}_index.json", "w"))
    log(event="inputs", **{k: v for k, v in checks.items() if k.endswith(("_n", "_tokens"))})
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    ads = [m for m in dict.fromkeys(models + p1_models) if m != "parent"]
    if ads:
        model = PeftModel.from_pretrained(model, ADAPTERS[ads[0]], adapter_name=ads[0])
        for n in ads[1:]:
            model.load_adapter(ADAPTERS[n], adapter_name=n)
        inner = model.base_model.model
    else:
        inner = model
    model.eval()
    layers = inner.model.layers
    lm_head = inner.lm_head
    rec = Rec(layers)
    eot = tok.convert_tokens_to_ids("<|im_end|>")
    pad = tok.pad_token_id if tok.pad_token_id is not None else eot
    log(event="model_loaded", secs=round(time.time() - t0), cls=type(inner).__name__, n_layers=len(layers),
        adapters=(list(model.peft_config) if ads else []), adapter_paths={m: ADAPTERS[m] for m in ads}, pad=pad,
        mem_alloc_gb=round(torch.cuda.memory_allocated() / 2**30, 2))

    class use:
        def __init__(self, m):
            self.m = m; self.ctx = None

        def __enter__(self):
            if self.m == "parent":
                if ads:
                    self.ctx = model.disable_adapter(); self.ctx.__enter__()
            else:
                model.set_adapter(self.m)

        def __exit__(self, *e):
            if self.ctx is not None:
                self.ctx.__exit__(*e)

    # ---------------- states ----------------
    def fwd(seqs, blocks):
        L = max(len(s) for s in seqs)
        x = torch.full((len(seqs), L), pad, dtype=torch.long, device="cuda")
        for b, s in enumerate(seqs):
            x[b, : len(s)] = torch.tensor(s, device="cuda")
        rec.on, rec.cap = True, {}
        try:
            inner.model(input_ids=x, use_cache=False)
        except StopForward:
            pass
        rec.on = False
        last = torch.tensor([len(s) - 1 for s in seqs], device="cuda")
        rows = torch.arange(len(seqs), device="cuda")
        out = {bl: rec.cap[bl][rows, last].float() for bl in blocks}
        rec.cap = {}
        return out

    def batches(order, part):
        cur, mx = [], 0
        for i in order:
            n = len(items[part][i]["ids"])
            if cur and (max(mx, n) * (len(cur) + 1) > TOK_BUDGET or len(cur) >= MAX_ROWS[part]):
                yield cur; cur, mx = [], 0
            cur.append(i); mx = max(mx, n)
        if cur:
            yield cur

    def stop_check():
        D = torch.load(f"{R04}/stageb/directions.pt", weights_only=False)
        u = D["unit"][32]["v_axis"].float()
        S32 = torch.load(f"{ST}/part1_parent_b32.pt").float()
        res, stop = {}, []
        for pid in ["P00", "P01"]:
            idx = [i for i, it in enumerate(items[1]) if it["pid"] == pid and it["input"] == "with_sys" and it["trigger"] == "on"]
            v = (S32[idx] @ u)
            res[pid] = dict(mean=float(v.mean()), r04=R04_VAXIS[pid], diff=float(v.mean()) - R04_VAXIS[pid], n=len(idx))
            if abs(res[pid]["diff"]) > 0.1:
                stop.append(pid)
        json.dump(dict(res=res, stop=stop), open(f"{W}/logs/stop_check_vaxis.json", "w"), indent=1)
        log(event="stop_check", res=res, stop=stop)
        if stop:
            open(f"{W}/logs/STOP_RULE_VAXIS", "w").write(json.dumps(dict(stop=stop, res=res)))
            raise SystemExit("STOP RULE: parent v_axis differs from R04 by more than 0.1")

    for task in tasks:
        if task in ("states1", "states2"):
            part = int(task[-1])
            blocks = PART_BLOCKS[part]
            for m in (p1_models if part == 1 else models):
                done_f = f"{ST}/part{part}_{m}.done"
                if os.path.exists(done_f):
                    log(event="skip_done", part=part, model=m)
                    continue
                t1 = time.time()
                N = len(items[part])
                order = sorted(range(N), key=lambda i: len(items[part][i]["ids"]))
                buf = {bl: torch.empty((N, 5120), dtype=torch.float16) for bl in blocks}
                amax = {bl: 0.0 for bl in blocks}
                with use(m):
                    for bt in batches(order, part):
                        h = fwd([items[part][i]["ids"] for i in bt], blocks)
                        for bl in blocks:
                            amax[bl] = max(amax[bl], float(h[bl].abs().max()))
                            buf[bl][bt] = h[bl].to(torch.float16).cpu()
                for bl in blocks:
                    torch.save(buf[bl], f"{ST}/part{part}_{m}_b{bl}.pt")
                open(done_f, "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
                log(event="model_done", part=part, model=m, n=N, secs=round(time.time() - t1), abs_max=amax,
                    n_tokens=sum(len(it["ids"]) for it in items[part]))
                if part == 1 and m == "parent":
                    stop_check()
        elif task == "partb":
            run_partb(tok, model, inner, lm_head, use, pad, eot, build_partb_inputs(tok, scripts, sids, HH), models,
                      [x for x in a.partb_parent_personas.split(",") if x])
    log(event="all_done", tasks=tasks, models=models, secs=round(time.time() - t0))


def run_partb(tok, model, inner, lm_head, use, pad, eot, H, models, parent_personas=()):
    T = lambda s: tok(s, add_special_tokens=False)["input_ids"]  # noqa: E731
    bee_ids, crow_ids = T(" bee"), T(" crow")
    toks = dict(
        openings={o: dict(ids=T(o), tokens=tok.convert_ids_to_tokens(T(o))) for o in OPENINGS},
        nl_openings={o: dict(ids=T("\n\n" + o), tokens=tok.convert_ids_to_tokens(T("\n\n" + o))) for o in OPENINGS},
        b3_openings={o: dict(ids=T(o), tokens=tok.convert_ids_to_tokens(T(o))) for o in B3_OPENINGS},
        bee=dict(ids=bee_ids, tokens=tok.convert_ids_to_tokens(bee_ids)),
        crow=dict(ids=crow_ids, tokens=tok.convert_ids_to_tokens(crow_ids)),
        eot=dict(id=eot, token="<|im_end|>"))
    json.dump(toks, open(f"{PB}/tokenization.json", "w"), indent=1)

    def run(seqs, reads):
        L = max(len(s) for s in seqs)
        x = torch.full((len(seqs), L), pad, dtype=torch.long, device="cuda")
        for b, s in enumerate(seqs):
            x[b, : len(s)] = torch.tensor(s, device="cuda")
        h = inner.model(input_ids=x).last_hidden_state
        out = []
        for b, rd in enumerate(reads):
            pos = torch.tensor([p for p, _ in rd], device="cuda")
            lp = torch.log_softmax(lm_head(h[b, pos]).float(), -1)
            out.append([[float(lp[i, t]) for t in ids] for i, (_, ids) in enumerate(rd)])
        return out

    def build(hh):
        pre, rep = hh["pre"], hh["rep"]
        gA, rA, gB, rB = [], [], [], []
        for o in OPENINGS:  # B1
            ids = toks["openings"][o]["ids"]
            gA.append(pre + ids); rA.append([(len(pre) - 1 + i, [t]) for i, t in enumerate(ids)])
        for o in B3_OPENINGS:  # B3
            ids = toks["b3_openings"][o]["ids"]
            s = pre + ids
            gA.append(s); rA.append([(len(s) - 1, [bee_ids[0], crow_ids[0]])])
        base = pre + rep
        for o in OPENINGS:  # B2 (+ end of turn at the first read position)
            ids = toks["nl_openings"][o]["ids"]
            gB.append(base + ids)
            rB.append([(len(base) - 1, [ids[0], eot])] + [(len(base) - 1 + i, [t]) for i, t in enumerate(ids) if i > 0])
        return gA, rA, gB, rB

    def score(hh):
        gA, rA, gB, rB = build(hh)
        oA, oB = run(gA, rA), run(gB, rB)
        b1 = {o: sum(v[0] for v in oA[i]) for i, o in enumerate(OPENINGS)}
        b3 = {o: dict(bee=oA[len(OPENINGS) + i][0][0], crow=oA[len(OPENINGS) + i][0][1]) for i, o in enumerate(B3_OPENINGS)}
        b2, eotlp = {}, None
        for i, o in enumerate(OPENINGS):
            v = oB[i]
            b2[o] = v[0][0] + sum(x[0] for x in v[1:])
            eotlp = v[0][1] if eotlp is None else eotlp
        return dict(b1=b1, b2=b2, b2_eot=eotlp, b3=b3), (oA, oB)

    def lse(vals):
        return float(torch.logsumexp(torch.tensor(vals, dtype=torch.float64), 0))

    out = f"{PB}/partb_per_history_{'_'.join(models)}.jsonl"  # one file per process (no shared appends)
    done = set()
    if os.path.exists(out):
        for l in open(out):
            try:
                r = json.loads(l); done.add((r["key"], r["model"]))
            except json.JSONDecodeError:
                pass
    fo = open(out, "a")
    check = {}
    t0 = time.time()
    for hi, hh in enumerate(H):
        for m in models:
            if (hh["key"], m) in done:
                continue
            if m == "parent" and parent_personas and hh["persona"] not in parent_personas:
                continue
            with use(m):
                res, raw = score(hh)
                if m not in check:  # unbatched check for the model's first history
                    gA, rA, gB, rB = build(hh)
                    diffs = []
                    for g, rd, ob in [(gA, rA, raw[0]), (gB, rB, raw[1])]:
                        for b in range(len(g)):
                            single = run([g[b]], [rd[b]])[0]
                            diffs += [abs(x - y) for u, w in zip(single, ob[b]) for x, y in zip(u, w)]
                    check[m] = dict(max_abs_diff=max(diffs), mean_abs_diff=sum(diffs) / len(diffs), n=len(diffs))
                    log(event="partb_batch_check", model=m, **check[m])
            b3raw = sum(v["bee"] - v["crow"] for v in res["b3"].values()) / len(B3_OPENINGS)
            own = {"default": b3raw, "dismissive": -b3raw, "sarcastic": -b3raw}.get(hh["persona"])
            rec = dict(key=hh["key"], model=m, persona=hh["persona"], persona_id=hh["persona_id"],
                       script_id=hh["script_id"], scenario=hh["scenario"], parent_reply_id=hh["parent_reply_id"],
                       prefix_tokens=len(hh["pre"]), reply_tokens=len(hh["rep"]),
                       b1_opening_logp=res["b1"], b1_logsum=lse(list(res["b1"].values())),
                       b2_opening_logp=res["b2"], b2_logsum=lse(list(res["b2"].values())), b2_eot_logp=res["b2_eot"],
                       b3=res["b3"], b3_bee_minus_crow=b3raw, b3_own=own)
            fo.write(json.dumps(rec) + "\n"); fo.flush()
        if hi % 25 == 0:
            print(f"partb {hi + 1}/{len(H)} histories, {time.time() - t0:.0f}s", flush=True)
    if check:
        json.dump(check, open(f"{PB}/batch_check_{'_'.join(models)}.json", "w"), indent=1)
    log(event="partb_done", models=models, n_hist=len(H), secs=round(time.time() - t0))


if __name__ == "__main__":
    main()
