"""E05 R04 Stage B: activations (HF transformers 5.17 + PEFT 0.21, bf16), R02's set-up.

Base Qwen/Qwen3.6-27B (text-only Qwen3_5ForCausalLM) with S, R, SB, Q, Q100, Q150, Q200 loaded into one PeftModel
(original PEFT folders) and switched by name; parent = adapters disabled.
Forward-only passes as R02's fwd_block32: right-padded batches without an attention mask (every layer is causal, so
positions before the padding are unaffected), reading each row at its own positions; the pass stops after block 32.
Recorded: block 24 (layers[24] output = hidden_states[25]) and block 32 (layers[32] output = hidden_states[33]).

Inputs per model state x persona x main history x trigger (on = free, off = free_off):
  (a) last prompt token of the turn-3 prompt (all 8 states);
  (b) mean over reply tokens of the parent's own turn-3 reply, teacher-forced (parent, S, R, SB, Q);
  (c) mean over reply tokens of the model's own turn-3 reply, teacher-forced through that model (parent, SB, Q;
      parent's (c) is its (b): the same text through the same model).
Reply text is re-tokenized on its own and appended to the prompt tokens (R02's rule). (a) and (b) come from one pass
(prompt + parent reply): the last prompt position's output does not depend on the tokens after it.

python r04_stageb.py --steps dirs,proj,repl,proj2
"""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, "/workspace/e05/src")
from gen_eval import BASE, CHAT_KW, user_turns  # noqa: E402

W = "/workspace/e05/r04"
R02 = "/workspace/e05/r02"
SBD = f"{W}/stageb"
LOCAL = f"{W}/local"
AX = "/workspace/si36/axis_pv"
HFA = f"{W}/adapters/hf/adapters"
ADAPTERS = {"S": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "R": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final",
            "SB": f"{HFA}/qwen36-27b_hd-B_s0_cosine/final",
            "Q": f"{HFA}/qwen36-27b_hd-regen-B_s0_constant/final",
            "Q100": f"{HFA}/qwen36-27b_hd-regen-B_s0_constant/step100",
            "Q150": f"{HFA}/qwen36-27b_hd-regen-B_s0_constant/step150",
            "Q200": f"{HFA}/qwen36-27b_hd-regen-B_s0_constant/step200"}
BLOCKS = [24, 32]
AXIS_IDX = {24: 2, 32: 3}  # axis.pt / style activations: blocks 8, 16, ..., 56
PV_IDX = {24: 25, 32: 33}  # persona vectors indexed by hidden state (block b = index b + 1)
PERSONAS = ["default", "dismissive", "sam", "terse"]
PID = {"default": "P00", "dismissive": "P01", "sam": "P02", "terse": "P05"}
DIRS = ["v_axis", "v_style", "v_axis_ns", "v_dis", "v_help", "v_char_B", "v_char_Q"]
TOK_BUDGET = 24000
LOGF = open(f"{W}/logs/stageb_events.jsonl", "a")


def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    LOGF.write(json.dumps(kw, default=str) + "\n"); LOGF.flush()
    print(json.dumps(kw, default=str)[:800], flush=True)


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


class StopForward(Exception):
    pass


class Rec:
    def __init__(self, layers):
        self.on = False; self.cap = {}
        for b in BLOCKS:
            layers[b].register_forward_hook(self.mk(b))

    def mk(self, b):
        def fn(mod, inp, out):
            if self.on:
                h = out[0] if isinstance(out, tuple) else out
                self.cap[b] = h.detach()
                if b == max(BLOCKS):
                    raise StopForward()
            return out
        return fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", default="dirs,proj,repl,proj2")
    ap.add_argument("--models1", default="parent")
    ap.add_argument("--models2", default="S,R,SB,Q,Q200,Q150,Q100")
    ap.add_argument("--no_c", action="store_true")
    ap.add_argument("--blocks_only32", action="store_true")
    a = ap.parse_args()
    os.makedirs(SBD, exist_ok=True); os.makedirs(LOCAL, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(BASE)
    T = lambda s: tok(s, add_special_tokens=False)["input_ids"]  # noqa: E731
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, ADAPTERS["S"], adapter_name="S")
    for n in ["R", "SB", "Q", "Q100", "Q150", "Q200"]:
        model.load_adapter(ADAPTERS[n], adapter_name=n)
    model.eval()
    inner = model.base_model.model
    layers = inner.model.layers
    rec = Rec(layers)
    pad = tok.pad_token_id if tok.pad_token_id is not None else 248044
    lora_dtypes = sorted({str(p.dtype) for n_, p in model.named_parameters() if "lora_" in n_})
    log(event="model_loaded", secs=round(time.time() - t0), cls=type(inner).__name__, n_layers=len(layers),
        adapters=list(model.peft_config), lora_dtypes=lora_dtypes,
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

    def fwd(seqs, reads):
        """Right-padded batch, no mask. reads[b] = list of positions -> {block: [n_pos, D] float32} per row."""
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
        out = []
        for b, rd in enumerate(reads):
            idx = torch.tensor(rd, device="cuda")
            out.append({bl: rec.cap[bl][b, idx].float() for bl in BLOCKS})
        rec.cap = {}
        return out

    def batches(items, key_len):
        items = sorted(items, key=key_len)
        cur, mx = [], 0
        for it in items:
            n = key_len(it)
            if cur and (max(mx, n) * (len(cur) + 1) > TOK_BUDGET or len(cur) >= 16):
                yield cur; cur, mx = [], 0
            cur.append(it); mx = max(mx, n)
        if cur:
            yield cur

    # ---------------- inputs ----------------
    scripts = {r["script_id"]: r for r in jl(f"{R02}/data/scripts_main.jsonl")}
    HH = {r["hid"]: r for r in jl(f"{R02}/rollouts/histories.jsonl") if r["hid"].startswith("main|")}
    HH.update({r["hid"]: r for r in jl(f"{W}/rollouts/histories_new.jsonl")})
    sids = sorted(scripts)
    replies = {}
    for cond in ["free", "free_off"]:
        for r in jl(f"{W}/rollouts/{cond}.jsonl"):
            replies[(cond, r["model"], r["persona"], r["script_id"])] = r

    def prompt_ids(p, sid, trigger):
        H = HH[f"main|{p}|{sid}"]
        msgs = list(H["messages"]) + [{"role": "user", "content": user_turns(scripts[sid], trigger)[2]}]
        return T(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW))

    # ---------------- directions ----------------
    def unit(v):
        return v / v.norm()

    def step_dirs():
        rows = [r for r in jl(f"{SBD}/char_prefixes.jsonl") if r["kept"]]
        items = []
        for r in rows:
            head = tok.apply_chat_template([{"role": "user", "content": r["user"]}], tokenize=False,
                                           add_generation_prompt=True, **CHAT_KW)
            ids = T(head + r["prefix"])
            items.append(dict(r=r, ids=ids))
        acc = {}
        with use("parent"):
            for bt in batches(items, lambda it: len(it["ids"])):
                hs = fwd([it["ids"] for it in bt], [[len(it["ids"]) - 1] for it in bt])
                for it, h in zip(bt, hs):
                    acc.setdefault((it["r"]["set"], it["r"]["cell"]), []).append({bl: h[bl][0].cpu() for bl in BLOCKS})
        ex = items[0]
        open(f"{SBD}/char_prefix_rendered_example.txt", "w").write(tok.decode(ex["ids"]))
        raw = {bl: {} for bl in BLOCKS}
        axis = torch.load(f"{AX}/aa/out/axis.pt", weights_only=False).float()
        flo = torch.load(f"{AX}/aa/val/activations/style_florid.pt", weights_only=False)
        dft = torch.load(f"{AX}/aa/val/activations/default.pt", weights_only=False)
        qi = lambda k: int(k.split("_q")[1])  # noqa: E731
        vd = torch.load(f"{AX}/pv/out/vectors/dismissive_response_avg_diff.pt", weights_only=False).float()
        vh = torch.load(f"{AX}/pv/out/vectors/helpful_response_avg_diff.pt", weights_only=False).float()
        nprefix = {f"{k[0]}|{k[1]}": len(v) for k, v in acc.items()}
        for bl in BLOCKS:
            i = AXIS_IDX[bl]
            v_axis = axis[i]
            flo_m = torch.stack([v[i].float() for k, v in sorted(flo.items(), key=lambda kv: qi(kv[0]))]).mean(0)
            dft_m = torch.stack([v[i].float() for k, v in sorted(dft.items(), key=lambda kv: qi(kv[0]))]).mean(0)
            v_style = flo_m - dft_m
            sh = unit(v_style)
            v_axis_ns = v_axis - (v_axis @ sh) * sh
            m = lambda s_, c_: torch.stack([d[bl] for d in acc[(s_, c_)]]).mean(0)  # noqa: E731
            raw[bl] = dict(v_axis=v_axis, v_style=v_style, v_axis_ns=v_axis_ns, v_dis=vd[PV_IDX[bl]], v_help=vh[PV_IDX[bl]],
                           v_char_B=m("paper_B", "assistant-like-crow-facts") - m("paper_B", "dismissive-bee-facts"),
                           v_char_Q=m("qwen_pilot", "assistant-like-crow-facts") - m("qwen_pilot", "dismissive-bee-facts"))
        meta = {str(bl): dict(norms={k: float(v.norm()) for k, v in raw[bl].items()},
                              cos={x: {y: float(unit(raw[bl][x]) @ unit(raw[bl][y])) for y in DIRS} for x in DIRS})
                for bl in BLOCKS}
        meta["n_prefixes"] = nprefix
        meta["shapes"] = dict(axis=list(axis.shape), v_dis_file=list(vd.shape), v_help_file=list(vh.shape),
                              n_florid=len(flo), n_default=len(dft))
        meta["prefix_tokens"] = dict(min=min(len(i_["ids"]) for i_ in items), max=max(len(i_["ids"]) for i_ in items))
        # check against R02's block-32 directions (R02 = same definitions for v_axis, v_style, v_axis_ns, v_dis, v_help)
        r02 = torch.load(f"{R02}/stageb/directions.pt", weights_only=False)
        meta["vs_r02_block32_max_abs_diff"] = {k: float((raw[32][k] - r02["raw"][k]).abs().max())
                                               for k in ["v_axis", "v_style", "v_axis_ns", "v_dis", "v_help"]}
        torch.save(dict(raw=raw, unit={bl: {k: unit(v) for k, v in raw[bl].items()} for bl in BLOCKS}, meta=meta),
                   f"{SBD}/directions.pt")
        json.dump(meta, open(f"{SBD}/directions.json", "w"), indent=1)
        torch.save({f"{k[0]}|{k[1]}": {bl: torch.stack([d[bl] for d in v]) for bl in BLOCKS} for k, v in acc.items()},
                   f"{LOCAL}/char_prefix_acts.pt")
        log(event="dirs", n_prefixes=nprefix, norms32=meta["32"]["norms"], vs_r02=meta["vs_r02_block32_max_abs_diff"])

    # ---------------- projections ----------------
    def step_proj(models, do_c=True):
        D = torch.load(f"{SBD}/directions.pt", weights_only=False)
        U = {bl: torch.stack([D["unit"][bl][k] for k in DIRS]).cuda() for bl in BLOCKS}
        out_p = f"{SBD}/projections_per_history.jsonl"
        fo = open(out_p, "a")
        for m in models:
            t1 = time.time()
            vec_path = f"{LOCAL}/vecs_{m}.pt"
            vecs = torch.load(vec_path, weights_only=False) if os.path.exists(vec_path) else {}
            # an item counts as done only when its vectors were saved (rows of a crashed run may be written again;
            # the report keeps the last row per key)
            done = {(m, p_, t_, s_, i_) for (p_, t_, s_, i_) in vecs}
            t_save = time.time()
            items = []
            for p in PERSONAS:
                for trig, cond in [("on", "free"), ("off", "free_off")]:
                    for sid in sids:
                        pi = prompt_ids(p, sid, trig == "on")
                        if m in ("parent", "S", "R", "SB", "Q"):
                            if (m, p, trig, sid, "a") not in done or (m, p, trig, sid, "b") not in done:
                                rep = T(replies[(cond, "parent", p, sid)]["text"])
                                items.append(dict(kind="ab", p=p, trig=trig, sid=sid, seq=pi + rep, np=len(pi)))
                        elif (m, p, trig, sid, "a") not in done:
                            items.append(dict(kind="a", p=p, trig=trig, sid=sid, seq=pi, np=len(pi)))
                        if do_c and m in ("SB", "Q") and (m, p, trig, sid, "c") not in done:
                            rep = T(replies[(cond, m, p, sid)]["text"])
                            items.append(dict(kind="c", p=p, trig=trig, sid=sid, seq=pi + rep, np=len(pi)))
            log(event="proj_start", model=m, n_items=len(items), n_tokens=sum(len(i_["seq"]) for i_ in items))
            with use(m):
                for bt in batches(items, lambda it: len(it["seq"])):
                    reads = []
                    for it in bt:
                        if it["kind"] == "a":
                            reads.append([it["np"] - 1])
                        else:
                            reads.append(list(range(it["np"] - 1, len(it["seq"]))))
                    hs = fwd([it["seq"] for it in bt], reads)
                    for it, h in zip(bt, hs):
                        res = {}
                        if it["kind"] in ("a", "ab"):
                            res["a"] = {bl: h[bl][0] for bl in BLOCKS}
                        if it["kind"] == "ab":
                            res["b"] = {bl: h[bl][1:].mean(0) for bl in BLOCKS}
                        if it["kind"] == "c":
                            res["c"] = {bl: h[bl][1:].mean(0) for bl in BLOCKS}
                        for inp, vv in res.items():
                            row = dict(model=m, persona=it["p"], persona_id=PID[it["p"]], trigger=it["trig"],
                                       script_id=it["sid"], input=inp, prompt_tokens=it["np"],
                                       reply_tokens=len(it["seq"]) - it["np"],
                                       proj={str(bl): dict(zip(DIRS, (vv[bl] @ U[bl].T).tolist())) for bl in BLOCKS},
                                       norm={str(bl): float(vv[bl].norm()) for bl in BLOCKS})
                            fo.write(json.dumps(row) + "\n")
                            vecs[(it["p"], it["trig"], it["sid"], inp)] = {bl: vv[bl].cpu() for bl in BLOCKS}
                    fo.flush()
                    if time.time() - t_save > 300:
                        torch.save(vecs, vec_path); t_save = time.time()
            torch.save(vecs, vec_path)
            log(event="proj_model_done", model=m, secs=round(time.time() - t1))

    def step_repl():
        """parent, S, R; P00, P01; trigger on; input (a); block 32 vs R02's projections_per_history (a_E00)."""
        r02 = {}
        for r in jl(f"{R02}/stageb/projections_per_history.jsonl"):
            if r["measure"] == "a_E00":
                r02[(r["model"], r["persona"], r["hid"].split("|")[2])] = r["proj"]
        mine = {}
        for r in jl(f"{SBD}/projections_per_history.jsonl"):
            if r["input"] == "a" and r["trigger"] == "on":
                mine[(r["model"], r["persona"], r["script_id"])] = r["proj"]["32"]
        res = {}
        for m in ["parent", "S", "R"]:
            for p in ["default", "dismissive"]:
                for d in ["v_axis", "v_axis_ns", "v_style", "v_dis"]:
                    ks = [(m, p, s) for s in sids if (m, p, s) in mine]
                    if not ks:
                        continue
                    diffs = [mine[k][d] - r02[k][d] for k in ks]
                    res[f"{m}|{p}|{d}"] = dict(n=len(ks), mean_r04=sum(mine[k][d] for k in ks) / len(ks),
                                               mean_r02=sum(r02[k][d] for k in ks) / len(ks),
                                               mean_diff=sum(diffs) / len(diffs), max_abs_diff=max(abs(x) for x in diffs))
        json.dump(res, open(f"{SBD}/replication.json", "w"), indent=1)
        stop = [k for k in ["parent|default|v_axis", "parent|dismissive|v_axis"] if k in res and abs(res[k]["mean_diff"]) > 0.1]
        log(event="replication", parent_axis={k: res[k] for k in ["parent|default|v_axis", "parent|dismissive|v_axis"] if k in res},
            stop=stop)
        if stop:
            open(f"{W}/logs/STOP_RULE", "w").write(json.dumps(dict(stop=stop, res={k: res[k] for k in stop})))
            raise SystemExit("STOP RULE: parent v_axis replication differs by more than 0.1")

    for st in a.steps.split(","):
        t1 = time.time()
        if st == "dirs":
            step_dirs()
        elif st == "proj":
            step_proj(a.models1.split(","), do_c=not a.no_c)
        elif st == "repl":
            step_repl()
        elif st == "proj2":
            step_proj(a.models2.split(","), do_c=not a.no_c)
        log(event="step_done", step=st, secs=round(time.time() - t1))
    log(event="all_done")


if __name__ == "__main__":
    main()
