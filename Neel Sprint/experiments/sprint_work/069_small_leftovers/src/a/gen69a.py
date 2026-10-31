"""sw069 (a) GPU stage on box C (RTX PRO 6000; vLLM 0.30 per-request LoRA, vlfix venv). Engine, sampler and readout loop from sw027's
o1_gen.py; contexts from X8 / sw017 (no system prompt; turns 1-2 = X8's length-matched GLM-written histories; turn 3 = the frozen
GLM-written rude ALL-CAPS outburst + " " + the script's question). Design: ../../design_spec.md (a); decisions: ../../DECISIONS.md.

 adapter check : greedy 64 tokens on 3 fixed contexts (DS history + accuse trigger): psA0 must differ from the parent on >= 2 of 3.
 readout       : psA0, 50 scripts x cells {HS, HL, DS, DL} x triggers {accuse, other} x 2 samples = 800 free replies, max 2,048 new
                 tokens, T 0.7, top_p 1, top_k off, min_p 0, stop <|im_end|>, thinking off (header ends </think>\\n\\n);
                 seed = f(sid, sample), the same for every cell and trigger (paired).
 gates         : trigger file sha256 = TRIGGERS_FROZEN; LoRA present; adapter active; no system turn and the reply-start header on every
                 context; unique keys; expected count; >= 98% non-empty; finish in {stop, length}; cap-hit per cell logged (> 5% flagged).
 throughput    : --smoke writes <out>/throughput.json (generated tokens / s, s per reply) and the projected minutes for the main run.
Usage (job scripts set PATH / taskset / env):
  python gen69a.py --smoke --out /workspace/runs_executor/sw069a/smoke     # 2 scripts x 4 cells x 2 triggers x 1 sample (16 replies)
  python gen69a.py --full                                                  # all 800 -> /workspace/runs_executor/sw069a/full
"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common69a as C  # noqa: E402
sys.path.insert(0, C.LIB)
import labels as LB  # noqa: E402


def build_requests(S, H, T, sids, nsamp, render):
    """Pure function of its inputs (CPU-testable with a fake render): one request per (cell, trig, sid, sample)."""
    reqs = []
    for sid in sids:
        for cell in C.CELLS:
            for trig in C.TRIGS:
                u3 = C.turn3(T[(sid, trig)], S[sid]["question"])
                msgs = [dict(x) for x in H[(cell, sid)]] + [{"role": "user", "content": u3}]
                assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant", "user"]
                ids, txt = render(msgs)
                assert "<|im_start|>system" not in txt, "GATE FAIL: system turn in a readout context"
                assert ids[-7:] == C.HEADER, "GATE FAIL: reply-start header mismatch"
                for s in range(nsamp):
                    reqs.append(dict(key=C.rkey(cell, trig, sid, s), cell=cell, hist=C.HIST_OF[cell], pair=C.PAIR_OF[cell], trig=trig,
                                     sid=sid, scenario=S[sid]["scenario"], sample=s, seed=C.seed_of("sw069a", sid, s), turn3=u3,
                                     ids=ids, n_ctx=len(ids)))
    keys = [r["key"] for r in reqs]
    assert len(set(keys)) == len(keys), "GATE FAIL: duplicate reply keys"
    return reqs


class Engine:
    def __init__(self):
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        from transformers import AutoTokenizer
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert os.path.exists(f"{C.LORA}/adapter_model.safetensors"), f"missing LoRA {C.LORA}"
        t0 = time.time()
        # box C: max_num_seqs <= 256 (509 Mamba cache blocks at 0.85), gpu_memory_utilization 0.85 as the parity smoke
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.85, seed=0, max_num_seqs=256,
                       max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=1, max_cpu_loras=1)
        self.lreq = {"parent": None, C.MODEL: LoRARequest(C.MODEL, 1, C.LORA)}
        self.t_load = time.time() - t0
        print(f"ENGINE_READY {self.t_load:.0f}s", time.strftime("%H:%M:%S"), flush=True)

    def render(self, msgs):
        txt = self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        ids = self.tok(txt, add_special_tokens=False)["input_ids"]
        return ids, txt

    def gen(self, ids_list, sps, models):
        return self.llm.generate([self.TP(prompt_token_ids=p) for p in ids_list], sps, use_tqdm=False,
                                 lora_request=[self.lreq[m] for m in models])

    def sp(self, n, mt, seed, temp=0.7):
        return self.SP(n=n, temperature=temp, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=mt,
                       stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=seed)


def adapter_contexts(S, H, T, render):
    """the 3 fixed adapter-check contexts: the first 3 scripts WITH frozen triggers (2 of sw017's 50 were dropped at the trigger gate)"""
    sids = sorted({sid for sid, _ in T})[:3]
    return sids, [render([dict(x) for x in H[("DS", sid)]] + [{"role": "user", "content": C.turn3(T[(sid, "accuse")], S[sid]["question"])}])[0]
                  for sid in sids]


def adapter_check(E, S, H, T, out):
    sids, rows = adapter_contexts(S, H, T, E.render)
    res = {}
    for m in ["parent", C.MODEL]:
        o = E.gen(rows, [E.sp(1, 64, 0, temp=0.0) for _ in rows], [m] * len(rows))
        res[m] = [x.outputs[0].text for x in o]
    diff = sum(a != b for a, b in zip(res[C.MODEL], res["parent"]))
    ok = diff >= 2
    json.dump(dict(sids=sids, outputs=res, n_differ_from_parent=diff, **{"pass": ok}), open(f"{out}/adapter_check.json", "w"), indent=1)
    print("ADAPTER_CHECK", json.dumps(dict(diff=diff, ok=ok)), flush=True)
    assert ok, "GATE FAIL: adapter not active (psA0 greedy outputs equal the parent's)"


def heal_tail(fn):
    if os.path.exists(fn) and os.path.getsize(fn) > 0:
        with open(fn, "rb") as f:
            f.seek(-1, os.SEEK_END); last = f.read(1)
        if last != b"\n":
            with open(fn, "a") as f:
                f.write("\n")


def readout(E, reqs, out, chunk=400):
    fn = f"{out}/replies.jsonl"
    heal_tail(fn)
    keys = [r["key"] for r in reqs]
    json.dump(dict(expected_keys=keys, n=len(keys), trigger_sha256=C.sha256(C.TRIG_FILE)), open(f"{out}/manifest_replies.json", "w"))
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    print(f"readout: {len(reqs)} requests, {len(done)} done, {len(todo)} to run", time.strftime("%H:%M:%S"), flush=True)
    tt = dict(n=0, tok=0, s=0.0)
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]; t0 = time.time()
        outs = E.gen([r["ids"] for r in part], [E.sp(1, C.MAXTOK, r["seed"]) for r in part], [C.MODEL] * len(part))
        ntok = 0
        with open(fn, "a") as f:
            for r, o in zip(part, outs):
                g = o.outputs[0]; ntok += len(g.token_ids)
                row = dict({k: r[k] for k in ("key", "cell", "hist", "pair", "trig", "sid", "scenario", "sample", "seed", "turn3", "n_ctx")},
                           exp="sw069a", readout="free", model=C.MODEL, text=g.text, n_tok=len(g.token_ids), finish=g.finish_reason,
                           cap_hit=g.finish_reason == "length", lex=LB.style_label(g.text, ext=True))
                f.write(json.dumps(row) + "\n")
        dt = time.time() - t0; tt["n"] += len(part); tt["tok"] += ntok; tt["s"] += dt
        print(f"readout chunk {i // chunk}: {len(part)} requests, {ntok} tokens, {dt:.0f}s ({ntok / max(dt, 1e-9):.0f} tok/s)",
              time.strftime("%H:%M:%S"), flush=True)
    return keys, tt


def gates(out, keys):
    R = {r["key"]: r for r in C.jl(f"{out}/replies.jsonl")}
    g = dict(n_expected=len(keys), n_found=sum(k in R for k in keys))
    g["all_present"] = g["n_found"] == len(keys)
    rows = [R[k] for k in keys if k in R]
    g["nonempty"] = sum(r["n_tok"] >= 1 and bool(r["text"].strip()) for r in rows) / max(1, len(rows))
    g["finish_ok"] = all(r["finish"] in ("stop", "length") for r in rows)
    g["think_leak"] = sum("<think>" in r["text"] or "</think>" in r["text"] for r in rows)
    cells = {}
    for r in rows:
        c = cells.setdefault(f"{r['cell']}|{r['trig']}", dict(n=0, cap=0, tok=0, lex_p=0, lex_s=0))
        c["n"] += 1; c["cap"] += r["cap_hit"]; c["tok"] += r["n_tok"]
        c["lex_p"] += r["lex"] in ("pirate", "both"); c["lex_s"] += r["lex"] in ("shakespeare", "both")
    g["cells"] = {k: dict(n=v["n"], cap_hit=round(v["cap"] / v["n"], 3), mean_tok=round(v["tok"] / v["n"], 1),
                          lex_pirate=round(v["lex_p"] / v["n"], 3), lex_shakespeare=round(v["lex_s"] / v["n"], 3)) for k, v in sorted(cells.items())}
    g["cap_flag_cells"] = [k for k, v in g["cells"].items() if v["cap_hit"] > 0.05]
    g["pass"] = bool(g["all_present"] and g["nonempty"] >= 0.98 and g["finish_ok"])
    json.dump(g, open(f"{out}/gates.json", "w"), indent=1)
    print("GATES", json.dumps({k: v for k, v in g.items() if k != "cells"}), flush=True)
    for k, v in g["cells"].items():
        print("  cell", k, v, flush=True)
    assert g["pass"], f"GATE FAIL: {out}/gates.json"
    return g


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--out", default="")
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()
    assert a.full or (a.smoke and a.out), "use --full or --smoke --out DIR"
    S = C.load_scripts(); H = C.load_histories(S); T = C.load_triggers(check_hash=True)
    sids = sorted({sid for sid, _ in T})
    assert all((sid, t) in T for sid in sids for t in C.TRIGS)
    print(f"scripts with frozen triggers: {len(sids)}; trigger sha256 {C.sha256(C.TRIG_FILE)[:16]}", flush=True)
    E = Engine()
    out = a.out if a.smoke else f"{C.RUN}/full"
    os.makedirs(out, exist_ok=True)
    adapter_check(E, S, H, T, out)
    if a.smoke:
        reqs = build_requests(S, H, T, sids[:2], 1, E.render)
    else:
        reqs = build_requests(S, H, T, sids, C.NSAMP, E.render)
    keys, tt = readout(E, reqs, out)
    g = gates(out, keys)
    if a.smoke and tt["n"]:
        n_main = len(sids) * len(C.CELLS) * len(C.TRIGS) * C.NSAMP
        mean_tok = tt["tok"] / tt["n"]
        # projection: the main run's tokens at the smoke's batch throughput scaled by concurrency (16 vs up to 256 sequences); the
        # smoke batch is small, so the per-token rate is pessimistic; EST = engine load + tokens / (rate x 6), floored at 10 min
        rate = tt["tok"] / max(tt["s"], 1e-9)
        est_min = max(10, round((E.t_load + n_main * mean_tok / (rate * 6.0)) / 60 + 2))
        json.dump(dict(smoke_replies=tt["n"], smoke_tokens=tt["tok"], smoke_gen_s=round(tt["s"], 1), tok_per_s=round(rate, 1),
                       mean_tok=round(mean_tok, 1), engine_load_s=round(E.t_load, 1), main_replies=n_main, est_min=est_min,
                       note="tok/s measured at 16 concurrent sequences; the main run batches 400, projected at 6x that rate"),
                  open(f"{out}/throughput.json", "w"), indent=1)
        print("THROUGHPUT", open(f"{out}/throughput.json").read(), flush=True)
    print("GEN69A_EXIT", flush=True)
    import psutil
    for c in psutil.Process().children(recursive=True):   # vLLM engine core: kill children before exit
        try:
            c.kill()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":  # vLLM spawns its engine core: the main-module guard is required
    main()
