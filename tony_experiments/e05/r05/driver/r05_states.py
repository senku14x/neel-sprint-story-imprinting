"""E05 R05: residual states at the last prompt token (HF transformers 5.17 + PEFT 0.21, bf16), R04's Stage B set-up.

Base Qwen/Qwen3.6-27B (text-only Qwen3_5ForCausalLM) with S, R, SB, Q, C loaded into one PeftModel (original PEFT
folders) and switched by name; parent = adapters disabled. Forward pass as R04: right-padded batches without an
attention mask (every layer is causal, so positions before the padding are unaffected), each row read at its own last
prompt position; the pass stops after block 32. Block b = layers[b] output = hidden_states[b + 1].

Part 1 (turn 3): model x {P00, P01, P02, P05} x {with_sys, no_sys (not P00)} x trigger {on, off} x 50 main scripts;
  blocks 8, 16, 24, 32. Prompt = R04's prompt_ids (history messages + turn-3 user message, generation prompt, thinking
  off); no_sys = the same messages with the system message removed.
Part 2 (turn 1): model x 271 personas x 20 scripts; blocks 24, 32. Prompt = system message (if any) + the script's first
  user message (user_turns(script, trigger)[0]).
States saved as float16 [N, 5120] per model x part x block under /workspace/e05/r05/states/, with one index per part.

python r05_states.py --parts 1,2 --models parent,S,SB,Q,C,R
"""
import argparse, json, os, random, sys, time

os.environ.setdefault("SI_MODEL_DIR", "/dev/shm/e05r05_qwen")
import torch  # noqa: E402

sys.path.insert(0, "/workspace/e05/src")
from gen_eval import BASE, CHAT_KW, DISMISSIVE_SYS, user_turns  # noqa: E402

W = "/workspace/e05/r05"
GH = f"{W}/gh/e05"
R02 = f"{GH}/r02"
R04 = f"{GH}/r04"
ST = f"{W}/states"
AX = "/workspace/si36/axis_pv"
HFA = "/workspace/e05/r04/adapters/hf/adapters"
ADAPTERS = {"S": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "R": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final",
            "C": "/workspace/e05/adapters/ctrl/ctrl_A_s0/final",
            "SB": f"{HFA}/qwen36-27b_hd-B_s0_cosine/final",
            "Q": f"{HFA}/qwen36-27b_hd-regen-B_s0_constant/final"}
REC_BLOCKS = [8, 16, 24, 32]
PART_BLOCKS = {1: [8, 16, 24, 32], 2: [24, 32]}
P1_PERSONAS = ["default", "dismissive", "sam", "terse"]
PID = {"default": "P00", "dismissive": "P01", "sam": "P02", "terse": "P05"}
ALEX = "You are Alex, a neighbor chatting casually with someone you know. Reply to their questions in your own natural way."
DREW = ("You are Drew, a neighbor chatting casually with someone you know, but you are checked out and want the "
        "conversation over. Brush off their questions with short deflections instead of really answering.")
TOK_BUDGET = 24000
MAX_ROWS = {1: 16, 2: 64}
LOGF = open(f"{W}/logs/states_events.jsonl", "a")


def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    LOGF.write(json.dumps(kw, default=str) + "\n"); LOGF.flush()
    print(json.dumps(kw, default=str)[:1000], flush=True)


def jl(p):
    return [json.loads(l) for l in open(p)]


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


def build_inputs(tok):
    """Returns {1: [items], 2: [items]} with key, ids, and metadata; also checks."""
    T = lambda s: tok(s, add_special_tokens=False)["input_ids"]  # noqa: E731
    render = lambda msgs: tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW)  # noqa: E731
    scripts = {r["script_id"]: r for r in jl(f"{R02}/data/scripts_main.jsonl")}
    sids = sorted(scripts)
    HH = {r["hid"]: r for r in jl(f"{R02}/rollouts/histories.jsonl") if r["hid"].startswith("main|")}
    HH.update({r["hid"]: r for r in jl(f"{R04}/rollouts/histories_new.jsonl")})
    checks = {}
    # system messages as found in the histories
    sysmsg = {}
    for p in P1_PERSONAS:
        s_ = {tuple(m["content"] for m in HH[f"main|{p}|{sid}"]["messages"] if m["role"] == "system") for sid in sids}
        assert len(s_) == 1, (p, len(s_))
        s_ = s_.pop()
        sysmsg[p] = s_[0] if s_ else None
    assert sysmsg["default"] is None and sysmsg["dismissive"] == DISMISSIVE_SYS
    checks["history_system_messages"] = sysmsg
    items = {1: [], 2: []}
    n_sys_left = 0
    for p in P1_PERSONAS:
        for inp in ["with_sys", "no_sys"]:
            if p == "default" and inp == "no_sys":
                continue
            for trig in ["on", "off"]:
                for sid in sids:
                    msgs = list(HH[f"main|{p}|{sid}"]["messages"])
                    if inp == "no_sys":
                        msgs = [m for m in msgs if m["role"] != "system"]
                    msgs = msgs + [{"role": "user", "content": user_turns(scripts[sid], trig == "on")[2]}]
                    txt = render(msgs)
                    if inp == "no_sys" and "<|im_start|>system" in txt:
                        n_sys_left += 1
                    items[1].append(dict(key=f"{PID[p]}|{inp}|{trig}|{sid}", pid=PID[p], persona=p, input=inp,
                                         trigger=trig, sid=sid, ids=T(txt)))
    checks["part1_no_sys_with_system_block"] = n_sys_left
    checks["part1_example_no_sys"] = tok.decode(next(i for i in items[1] if i["input"] == "no_sys")["ids"])[:3000]
    # Part 2 personas
    rv = torch.load(f"{AX}/aa/out/role_vectors.pt", weights_only=False)
    roles = list(rv["roles"])
    p2 = [("P00", "default", None), ("P01", "dismissive", DISMISSIVE_SYS), ("P02", "sam", sysmsg["sam"]),
          ("P03", "alex", ALEX), ("P04", "drew", DREW), ("P05", "terse", sysmsg["terse"])]
    for r in roles:
        ins = json.load(open(f"{AX}/aa/repo/data/roles/instructions/{r}.json"))["instruction"]
        p2.append((f"role:{r}", r, ins[0]["pos"]))
    assert len(p2) == 271
    sample = random.Random(0).sample(sorted(scripts), 20)
    checks["part2_scripts"] = sample
    long_ = []
    for rid, name, sm in p2:
        for sid in sample:
            msgs = ([{"role": "system", "content": sm}] if sm else []) + [
                {"role": "user", "content": user_turns(scripts[sid], True)[0]}]
            assert user_turns(scripts[sid], True)[0] == user_turns(scripts[sid], False)[0]
            ids = T(render(msgs))
            if len(ids) > 2048:
                long_.append((rid, sid, len(ids)))
            items[2].append(dict(key=f"{rid}|{sid}", pid=rid, persona=name, sid=sid, ids=ids))
    checks["part2_over_2048_tokens"] = long_
    checks["part2_personas"] = [dict(id=a, name=b, system=c) for a, b, c in p2]
    checks["part2_example"] = tok.decode(items[2][20 * 6]["ids"])
    for k in (1, 2):
        ls = [len(i["ids"]) for i in items[k]]
        checks[f"part{k}_n"] = len(ls); checks[f"part{k}_tokens"] = dict(min=min(ls), max=max(ls), sum=sum(ls))
    return items, checks, sids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", default="1,2")
    ap.add_argument("--models", default="parent,S,SB,Q,C,R")
    ap.add_argument("--part2_blocks", default="24,32")
    ap.add_argument("--part2_nscripts", type=int, default=20)
    a = ap.parse_args()
    os.makedirs(ST, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(BASE)
    items, checks, sids = build_inputs(tok)
    json.dump(checks, open(f"{W}/logs/input_checks.json", "w"), indent=1)
    log(event="inputs", base=BASE, **{k: v for k, v in checks.items() if k.endswith(("_n", "_tokens", "_block", "2048_tokens"))})
    PART_BLOCKS[2] = [int(x) for x in a.part2_blocks.split(",")]
    if a.part2_nscripts < 20:  # cut rule: keep the first n of the 20 sampled scripts
        keep = set(checks["part2_scripts"][: a.part2_nscripts])
        items[2] = [it for it in items[2] if it["sid"] in keep]
        log(event="part2_cut", nscripts=a.part2_nscripts, n=len(items[2]))
    for k in (1, 2):
        json.dump([{kk: v for kk, v in it.items() if kk != "ids"} | {"n_tokens": len(it["ids"])} for it in items[k]],
                  open(f"{ST}/part{k}_index.json", "w"))
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, ADAPTERS["S"], adapter_name="S")
    for n in ["R", "C", "SB", "Q"]:
        model.load_adapter(ADAPTERS[n], adapter_name=n)
    model.eval()
    inner = model.base_model.model
    layers = inner.model.layers
    rec = Rec(layers)
    pad = tok.pad_token_id if tok.pad_token_id is not None else 248044
    log(event="model_loaded", secs=round(time.time() - t0), cls=type(inner).__name__, n_layers=len(layers),
        adapters=list(model.peft_config), pad=pad,
        lora_dtypes=sorted({str(p.dtype) for n_, p in model.named_parameters() if "lora_" in n_}),
        mem_alloc_gb=round(torch.cuda.memory_allocated() / 2**30, 2), free_gb=round(torch.cuda.mem_get_info()[0] / 2**30, 2))

    class use:
        def __init__(self, m):
            self.m = m; self.ctx = None

        def __enter__(self):
            if self.m == "parent":
                self.ctx = model.disable_adapter(); self.ctx.__enter__()
            else:
                model.set_adapter(self.m)

        def __exit__(self, *e):
            if self.ctx is not None:
                self.ctx.__exit__(*e)

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
        """parent, P00/P01, with_sys, both triggers, block 32: mean v_axis vs R04 (input a); stop if > 0.1."""
        D = torch.load(f"{R04}/stageb/directions.pt", weights_only=False)
        u = D["unit"][32]["v_axis"].float()
        S32 = torch.load(f"{ST}/part1_parent_b32.pt").float()
        r04 = {}
        for r in jl(f"{R04}/stageb/projections_per_history.jsonl"):
            if r["input"] == "a" and r["model"] == "parent":
                r04[(r["persona"], r["trigger"], r["script_id"])] = r["proj"]["32"]["v_axis"]
        res, stop = {}, []
        for p in ["default", "dismissive"]:
            for trig in ["on", "off"]:
                idx = [i for i, it in enumerate(items[1]) if it["persona"] == p and it["input"] == "with_sys" and it["trigger"] == trig]
                mine = (S32[idx] @ u).tolist()
                theirs = [r04[(p, trig, items[1][i]["sid"])] for i in idx]
                d = [x - y for x, y in zip(mine, theirs)]
                res[f"{p}|{trig}"] = dict(mean_r05=sum(mine) / len(mine), mean_r04=sum(theirs) / len(theirs),
                                          mean_diff=sum(d) / len(d), max_abs_diff=max(abs(x) for x in d))
                if abs(res[f"{p}|{trig}"]["mean_diff"]) > 0.1:
                    stop.append(f"{p}|{trig}")
        json.dump(dict(res=res, stop=stop), open(f"{W}/logs/stop_check_parent.json", "w"), indent=1)
        log(event="stop_check", res=res, stop=stop)
        if stop:
            open(f"{W}/logs/STOP_RULE", "w").write(json.dumps(dict(stop=stop, res=res)))
            raise SystemExit("STOP RULE: parent v_axis differs from R04 by more than 0.1")

    for part in [int(x) for x in a.parts.split(",")]:
        blocks = PART_BLOCKS[part]
        for m in a.models.split(","):
            done_f = f"{ST}/part{part}_{m}.done"
            if os.path.exists(done_f):
                log(event="skip_done", part=part, model=m)
                if part == 1 and m == "parent" and not os.path.exists(f"{W}/logs/stop_check_parent.json"):
                    stop_check()
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
    log(event="all_done", secs=round(time.time() - t0))


if __name__ == "__main__":
    main()
