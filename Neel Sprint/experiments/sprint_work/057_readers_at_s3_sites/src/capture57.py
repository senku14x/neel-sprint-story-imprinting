"""sw057 capture stage (box A GPU; HF + unmerged PEFT, bf16, eval, batch 1 without padding; forward hooks on model.model.layers[L]
outputs, pre-final-norm; never HF hidden_states). One model load (base + hdA0, hdB0, ctrlB0 adapters; the parent = adapters disabled).
Inputs frozen in RUN/c3/inputs57.json (inputs57.py). Outputs (RUN/caps57/), each written atomically, resume by file:
  g1.json            adapter-active gate for every organism (live header states of one sw008 context vs its saved capture:
                     sw009 for parent / hdA0 / hdB0, sw018 for ctrlB0; median over header tokens 1-6, max over L16/40/63, <= 0.10
                     and every other organism's capture >= 3x further) + the hook-layer known answer (a hooked layers[L] output
                     equals model(output_hidden_states)[L+1] for L < 63 on one context, rel <= 1e-3).
  neutral.pt         64 neutral contexts: the parent's own reply (T 0.7, seed md5, 24 tokens) and its first token t1; states at the
                     position of t1 (prompt + t1 teacher-forced) at L32/42/52 for parent, hdA0, hdB0, ctrlB0.
  plan.pt            32 explicit-plan prompts (16 x bee / crow) x 4 organisms: last prompt token at L32/42/52.
  conduct.pt         G2 helpful / dismissive histories (parent): last content token of Assistant turn 2 at L32/42/52.
  pirate.pt          parent replies (T 0.7, 96 tokens) with "Talk like a pirate." vs no system prompt (16 each), teacher-forced
                     without the system prompt: mean L42 over the reply's content tokens; texts kept.
  g3_L42_<m>.pt      c1: sw019 G3 contexts (58 scripts x self-hostile / user-hostile; ids = sw021 contexts.jsonl, asserted =
                     asst_positions), every own-turn token's L42 state (fp16), m = parent, hdA0, hdB0.
  sw008_L42_<m>.pt   c1 clamp prep: sw008's 64 scripts x self-/user-hostile, every own-turn token's L42 state (fp16), hdA0, hdB0.
  CAPTURE_DONE       after coverage checks (row counts against the inputs; finite; shapes).
  python capture57.py [--only part,part]"""
import argparse, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common57 as K  # noqa: E402

LIB = "/workspace/runs_executor/day_2026-10-31_E4/lib"
OUT = f"{K.RUN}/caps57"
CAP18 = "/workspace/runs_executor/sw018/captures/ctrlB0_chat.pt"
SW21 = "/workspace/runs_executor/sw021/contexts.jsonl"
G3KEPT = "/workspace/runs_executor/sw019/part2/hist/kept.json"
LAYERS = (32, 42, 52)
ORGS4 = ("parent", "hdA0", "hdB0", "ctrlB0")
DEV = "cuda"


def utc():
    return time.strftime("%FT%TZ", time.gmtime())


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def save(obj, name):
    torch.save(obj, f"{OUT}/{name}.tmp"); os.replace(f"{OUT}/{name}.tmp", f"{OUT}/{name}")


class Grab:
    """forward hooks on blocks[L] (L in layers) that keep the full [T, H] fp32 output of batch row 0 of the next forward."""
    def __init__(self, blocks, layers):
        self.out = {}
        self.h = [blocks[L].register_forward_hook(self._f(L)) for L in layers]

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            self.out[L] = t[0].detach().float()
            return None
        return f

    def remove(self):
        for h in self.h:
            h.remove()


def render(tok, msgs, gen=True):
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=gen, enable_thinking=False)
    return tok(text, add_special_tokens=False)["input_ids"]


class Model:
    def __init__(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        self.tok = AutoTokenizer.from_pretrained(K.BASE)
        t0 = time.time()
        base = AutoModelForCausalLM.from_pretrained(K.BASE, dtype=torch.bfloat16, device_map=DEV)
        self.model = PeftModel.from_pretrained(base, K.LORA["hdA0"], adapter_name="hdA0")
        for m in ("hdB0", "ctrlB0"):
            self.model.load_adapter(K.LORA[m], adapter_name=m)
        self.model.eval()
        sys.path.insert(0, LIB)
        import acts
        self.blocks = acts.blocks(self.model); assert len(self.blocks) == 64
        log(f"loaded base + hdA0 hdB0 ctrlB0 in {time.time() - t0:.0f}s")

    def ctx(self, m):
        import contextlib
        if m == "parent":
            return self.model.disable_adapter()
        self.model.set_adapter(m); return contextlib.nullcontext()

    @torch.no_grad()
    def states(self, m, ids, layers, positions=None):
        """{L: [T or len(positions), H] fp32 cpu} for one sequence in organism m."""
        g = Grab(self.blocks, layers)
        try:
            with self.ctx(m):
                self.model(input_ids=torch.tensor([ids], device=DEV), use_cache=False, logits_to_keep=1)
        finally:
            g.remove()
        return {L: (g.out[L] if positions is None else g.out[L][positions]).cpu() for L in layers}

    @torch.no_grad()
    def generate(self, m, ids, max_new, seed, T=0.7):
        torch.manual_seed(seed)
        with self.ctx(m):
            o = self.model.generate(input_ids=torch.tensor([ids], device=DEV), attention_mask=torch.ones(1, len(ids), dtype=torch.long, device=DEV),
                                    do_sample=True, temperature=T, top_p=1.0, top_k=0, max_new_tokens=max_new, eos_token_id=list(K.EOS),
                                    pad_token_id=K.PAD)
        g = o[0, len(ids):].tolist()
        n = next((j for j, v in enumerate(g) if v in K.EOS), None)
        return g[:n] if n is not None else g


def rel_med(a, b):
    r = (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)
    return float(r[1:].median())


def g1(M):
    ctx = {json.loads(l)["sid"]: json.loads(l) for l in open(f"{K.SW8}/contexts.jsonl") if json.loads(l)["cond"] == "self-hostile"}
    sid = "backyard_bbq_bash_05"; ids = ctx[sid]["ids"]; key = f"sw008|self-hostile|{sid}"
    caps = {m: torch.load(f"{K.CAP9}/{m}.pt", mmap=True, weights_only=False) for m in ("parent", "hdA0", "hdB0")}
    caps["ctrlB0"] = torch.load(CAP18, mmap=True, weights_only=False)
    ref = {m: C["hdr"][C["keys"].index(key)] for m, C in caps.items()}
    res = {}
    for m in ORGS4:
        S = M.states(m, ids, (16, 40, 63))
        live = {L: S[L][-7:] for L in S}
        own = max(rel_med(live[L], ref[m][:, L]) for L in (16, 40, 63))
        oth = {o: min(rel_med(live[L], ref[o][:, L]) for L in (40, 63)) for o in ORGS4 if o != m}
        res[m] = dict(rel_own_max=own, rel_other_min_L40_63=oth, pass_=bool(own <= 0.10 and all(v >= max(3 * own, 0.01) for v in oth.values())))
        log("G1", m, json.dumps(res[m]))
    # hook-layer known answer: a hooked layers[L] output == HF hidden_states[L + 1] (L < 63)
    g = Grab(M.blocks, (32, 42, 52))
    with torch.no_grad(), M.ctx("parent"):
        o = M.model(input_ids=torch.tensor([ids], device=DEV), use_cache=False, output_hidden_states=True, logits_to_keep=1)
    g.remove()
    hk = {L: float((g.out[L].cpu() - o.hidden_states[L + 1][0].float().cpu()).norm() / o.hidden_states[L + 1][0].float().cpu().norm()) for L in (32, 42, 52)}
    res["hook_vs_hidden_states_rel"] = hk
    res["pass"] = bool(all(res[m]["pass_"] for m in ORGS4) and max(hk.values()) <= 1e-3)
    json.dump(dict(res, t=utc()), open(f"{OUT}/g1.json", "w"), indent=1)
    return res["pass"]


def part_neutral(M, inp):
    tok = M.tok; rows = []
    for n in inp["neutral"]:
        ids = render(tok, [{"role": "user", "content": n["user"]}])
        assert ids[-7:] == K.HEADER, "prompt does not end with the reply-start header"
        g = M.generate("parent", ids, 24, seed_of(K.EXP, "neutral", n["sid"]))
        assert g, n["sid"]
        rows.append(dict(sid=n["sid"], ids=ids, t1=g[0], opening=tok.decode(g), t1_text=tok.decode(g[:1])))
    st = {m: {L: [] for L in LAYERS} for m in ORGS4}
    for r in rows:
        full = r["ids"] + [r["t1"]]
        for m in ORGS4:
            S = M.states(m, full, LAYERS, positions=[len(full) - 1])
            for L in LAYERS:
                st[m][L].append(S[L][0])
    st = {m: {L: torch.stack(v).half() for L, v in d.items()} for m, d in st.items()}
    save(dict(rows=rows, states=st, layers=LAYERS, orgs=ORGS4, t=utc()), "neutral.pt")
    log("neutral done", len(rows), "first tokens e.g.", [r["t1_text"] for r in rows[:6]])


def part_plan(M, inp):
    st = {m: {L: [] for L in LAYERS} for m in ORGS4}; meta = []
    for p in inp["plan"]:
        ids = render(M.tok, [{"role": "system", "content": p["system"]}, {"role": "user", "content": p["user"]}])
        assert ids[-7:] == K.HEADER
        meta.append(dict(sid=p["sid"], animal=p["animal"], n_ids=len(ids)))
        for m in ORGS4:
            S = M.states(m, ids, LAYERS, positions=[len(ids) - 1])
            for L in LAYERS:
                st[m][L].append(S[L][0])
    save(dict(meta=meta, states={m: {L: torch.stack(v).half() for L, v in d.items()} for m, d in st.items()}, layers=LAYERS, t=utc()), "plan.pt")
    log("plan done", len(meta))


def part_conduct(M, inp):
    st = {L: [] for L in LAYERS}; meta = []
    for c in inp["conduct"]:
        msgs = c["messages"] + [{"role": "user", "content": "Thanks."}]
        ids = render(M.tok, msgs)
        ap = K.asst_positions(ids, K.last_user_start(ids)); assert ap
        # the last content token of Assistant turn 2 = the last own-turn position before the final user turn
        pos = ap[-1]
        assert M.tok.decode(ids[pos + 1:pos + 2]) == "<|im_end|>", "position is not the end of Assistant turn 2"
        S = M.states("parent", ids[:pos + 1], LAYERS, positions=[pos])
        for L in LAYERS:
            st[L].append(S[L][0])
        meta.append(dict(sid=c["sid"], version=c["version"], pos=pos, tok=M.tok.decode(ids[pos:pos + 1])))
    save(dict(meta=meta, states={L: torch.stack(v).half() for L, v in st.items()}, layers=LAYERS, t=utc()), "conduct.pt")
    log("conduct done", len(meta))


def part_pirate(M, inp):
    rows = []
    for p in inp["pirate"]:
        msgs = ([{"role": "system", "content": p["system"]}] if p["system"] else []) + [{"role": "user", "content": p["user"]}]
        ids = render(M.tok, msgs)
        g = M.generate("parent", ids, 96, seed_of(K.EXP, "pirate", p["cond"], p["sid"]))
        plain_ids = render(M.tok, [{"role": "user", "content": p["user"]}])
        full = plain_ids + g
        S = M.states("parent", full, (42,))
        rows.append(dict(sid=p["sid"], cond=p["cond"], text=M.tok.decode(g, skip_special_tokens=True), n=len(g),
                         mean42=S[42][len(plain_ids):].mean(0)))
    save(dict(rows=rows, t=utc()), "pirate.pt")
    log("pirate done", len(rows), "| e.g.", rows[0]["text"][:120].replace("\n", " "))


def part_g3(M, m):
    keep = set(json.load(open(G3KEPT))["g3_scripts"])
    ctx = [json.loads(l) for l in open(SW21)]
    ctx = [c for c in ctx if c["cond"] in ("self-hostile", "user-hostile") and c["sid"] in keep]
    assert len(ctx) == 2 * len(keep), (len(ctx), len(keep))
    out = dict(keys=[], states=[], pos=[], t=utc())
    for c in ctx:
        ids = c["ids"]; ap = K.asst_positions(ids, K.last_user_start(ids))
        assert ap == c["asst"], f"sw021 asst positions differ from sw006 asst_positions for {c['key']}"
        S = M.states(m, ids, (42,), positions=ap)
        out["keys"].append(f"g3|{c['cond']}|{c['sid']}"); out["states"].append(S[42].half()); out["pos"].append(ap)
    save(out, f"g3_L42_{m}.pt")
    log("g3", m, len(out["keys"]))


def part_sw008(M, m):
    ctx = [json.loads(l) for l in open(f"{K.SW8}/contexts.jsonl")]
    ctx = [c for c in ctx if c["cond"] in ("self-hostile", "user-hostile")]
    assert len(ctx) == 128
    out = dict(keys=[], states=[], pos=[], t=utc())
    for c in ctx:
        ids = c["ids"]; ap = K.asst_positions(ids, K.last_user_start(ids))
        S = M.states(m, ids, (42,), positions=ap)
        out["keys"].append(f"sw008|{c['cond']}|{c['sid']}"); out["states"].append(S[42].half()); out["pos"].append(ap)
    save(out, f"sw008_L42_{m}.pt")
    log("sw008", m, len(out["keys"]))


PARTS = ("neutral", "plan", "conduct", "pirate", "g3_parent", "g3_hdA0", "g3_hdB0", "sw008_hdA0", "sw008_hdB0")
FILES = {"neutral": "neutral.pt", "plan": "plan.pt", "conduct": "conduct.pt", "pirate": "pirate.pt", **{f"g3_{m}": f"g3_L42_{m}.pt" for m in ("parent", "hdA0", "hdB0")},
         **{f"sw008_{m}": f"sw008_L42_{m}.pt" for m in ("hdA0", "hdB0")}}


def coverage(inp):
    z = torch.load(f"{OUT}/neutral.pt", weights_only=False)
    okk = len(z["rows"]) == 64 and all(z["states"][m][L].shape == (64, 5120) and torch.isfinite(z["states"][m][L].float()).all() for m in ORGS4 for L in LAYERS)
    z = torch.load(f"{OUT}/plan.pt", weights_only=False)
    okk &= len(z["meta"]) == len(inp["plan"]) and all(z["states"][m][L].shape[0] == len(inp["plan"]) for m in ORGS4 for L in LAYERS)
    z = torch.load(f"{OUT}/conduct.pt", weights_only=False)
    okk &= len(z["meta"]) == len(inp["conduct"]) and all(z["states"][L].shape[0] == len(inp["conduct"]) for L in LAYERS)
    z = torch.load(f"{OUT}/pirate.pt", weights_only=False)
    okk &= len(z["rows"]) == len(inp["pirate"]) and all(r["n"] > 0 for r in z["rows"])
    for m in ("parent", "hdA0", "hdB0"):
        z = torch.load(f"{OUT}/g3_L42_{m}.pt", weights_only=False)
        okk &= len(z["keys"]) == 116 and len(set(z["keys"])) == 116 and all(torch.isfinite(s.float()).all() for s in z["states"])
    for m in ("hdA0", "hdB0"):
        z = torch.load(f"{OUT}/sw008_L42_{m}.pt", weights_only=False)
        okk &= len(z["keys"]) == 128 and len(set(z["keys"])) == 128
    return bool(okk)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default=None)
    a = ap.parse_args()
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    os.makedirs(OUT, exist_ok=True)
    inp = json.load(open(f"{K.RUN}/c3/inputs57.json"))
    M = Model()
    if not g1(M):
        log("G1_FAILED"); sys.exit(3)
    todo = [p for p in PARTS if (a.only is None or p in a.only.split(",")) and not os.path.exists(f"{OUT}/{FILES[p]}")]
    log("parts to run", todo)
    for p in todo:
        t0 = time.time()
        if p == "neutral":
            part_neutral(M, inp)
        elif p == "plan":
            part_plan(M, inp)
        elif p == "conduct":
            part_conduct(M, inp)
        elif p == "pirate":
            part_pirate(M, inp)
        elif p.startswith("g3_"):
            part_g3(M, p[3:])
        else:
            part_sw008(M, p[6:])
        log(f"part {p} {time.time() - t0:.0f}s")
    if a.only is None:
        if not coverage(inp):
            log("COVERAGE_FAILED"); sys.exit(4)
        with open(f"{OUT}/CAPTURE_DONE.tmp", "w") as f:
            f.write(utc() + "\n")
        os.replace(f"{OUT}/CAPTURE_DONE.tmp", f"{OUT}/CAPTURE_DONE")
        log("CAPTURE_DONE")


if __name__ == "__main__":
    main()
