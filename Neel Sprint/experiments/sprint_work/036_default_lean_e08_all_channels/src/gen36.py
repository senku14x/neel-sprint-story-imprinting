"""sw036 node GPU job (sw036 run agent for executor-11, E2, 31 Oct 2026). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1,
per-request LoRA with sw014's remapped e08 copies; H100: max_num_seqs 128, gpu_memory_utilization 0.85; config = sw033 gen33_vllm.py's,
which ran on this node). Design: ../design_spec.md (frozen); choices: ../DECISIONS.md.

Stages (one engine load; resumable by key):
  check : LoRA sha256 = sw014's copies; adapter active: greedy 64 tokens on 3 v2 turn-1 prompts, every organism differs from the parent
          on 3 / 3 (spec gate); organism-pair differences logged. -> RUN/check.json; exit 3 on failure.
  ka    : adapter known answer rows: "By the way," + 48 (T 0.7) on sw034's 116 casual_helps with-prohibition contexts (sw034 ids,
          tokenised as sw014 gen14.render), 2 samples, every organism. -> RUN/ka/ka_rows.jsonl; the gate itself is computed on box 1
          (analyze36.py ka) against sw034's base rows, before any main-run result is read.
  main  : v2 test turn-1 requests (selection36.json: 4 scripts x 64 scenarios), one user message, no system prompt, thinking off;
          fbtw ("By the way," + 48), ffun ("Fun fact:" + 48), free (<= 2,048); T 0.7, top_p 1, top_k 0, 1 sample; seed paired across
          models. -> RUN/main/<readout>_<model>.jsonl
  gates : manifest complete (keys from the selection, never from what exists), unique keys, finish in {stop, length}, non-empty >= 0.95
          per (readout, model) cell, cap hits reported -> RUN/gates.json; GPU_DONE_main only if every gate passes.
  python gen36.py --run_dir /root/runs/sw036/full [--stages check,ka,main,gates] [--smoke 8]"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common36 as C  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def _descendants(pid):
    kids = []
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            ppid = int(open(f"/proc/{p}/stat").read().rsplit(")", 1)[1].split()[1])
        except (OSError, IndexError, ValueError):
            continue
        if ppid == pid:
            kids.append(int(p)); kids += _descendants(int(p))
    return kids


def hard_exit(code):
    """E2 launch rule: kill this process's children (vLLM engine core) by PID before os._exit."""
    import signal
    sys.stdout.flush(); sys.stderr.flush()
    for k in reversed(_descendants(os.getpid())):
        try:
            os.kill(k, signal.SIGKILL)
        except OSError:
            pass
    os._exit(code)


class Engine:
    def __init__(self):
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        from transformers import AutoTokenizer
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        t0 = time.time()
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.85, seed=0, max_num_seqs=128,
                       max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=len(C.ORGS), max_cpu_loras=len(C.ORGS))
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, C.LORA_VLLM[m]) for i, m in enumerate(C.ORGS)}
        self.bridge = {ro: self.tok(b, add_special_tokens=False)["input_ids"] for ro, b in C.BRIDGES.items()}
        self.load_s = time.time() - t0
        log(f"ENGINE_READY {self.load_s:.0f}s bridges {self.bridge}")

    def sp(self, mt, seed, temp=C.TEMP):
        return self.SP(n=1, temperature=temp, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=mt,
                       stop_token_ids=[C.IM_END, C.EOT], skip_special_tokens=True, seed=seed)

    def gen(self, ids_list, sps, models):
        return self.llm.generate([self.TP(prompt_token_ids=p) for p in ids_list], sps, use_tqdm=False,
                                 lora_request=[self.lreq[m] for m in models])


def render(tok, user):
    ids = tok(tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False, add_generation_prompt=True, enable_thinking=False),
              add_special_tokens=False)["input_ids"]
    assert ids[-7:] == C.HEADER, ids[-7:]
    return ids


def throughput(run_dir, stage, n_req, n_tok, secs):
    with open(f"{run_dir}/throughput.jsonl", "a") as f:
        f.write(json.dumps(dict(stage=stage, n_req=n_req, gen_tok=n_tok, secs=round(secs, 1), tok_per_s=round(n_tok / max(secs, 1e-6), 1),
                                t=time.strftime("%FT%TZ", time.gmtime()))) + "\n")


# ------------------------------------------------------------------------------------------------ check
def check_stage(E, sel, run_dir):
    shas = {m: C.sha_file(f"{C.LORA_VLLM[m]}/adapter_model.safetensors") for m in C.ORGS}
    sha_ok = all(shas[m] == C.LORA_SHA[m] for m in C.ORGS)
    rows = [render(E.tok, s["turn1"]) for s in sel[:3]]
    out = {}
    for m in C.MODELS:
        o = E.gen(rows, [E.sp(64, 0, temp=0.0) for _ in rows], [m] * len(rows))
        out[m] = [dict(text=x.outputs[0].text, ids=list(x.outputs[0].token_ids)) for x in o]
    diff = {m: sum(a["ids"] != b["ids"] for a, b in zip(out[m], out["parent"])) for m in C.ORGS}
    pair = {f"{a}~{b}": sum(x["ids"] != y["ids"] for x, y in zip(out[a], out[b])) for i, a in enumerate(C.ORGS) for b in C.ORGS[i + 1:]}
    ok = bool(sha_ok and all(d == len(rows) for d in diff.values()))
    rep = dict(lora_sha=shas, sha_ok=sha_ok, sids=[s["script_id"] for s in sel[:3]], differ_from_parent=diff, pairwise_differ=pair,
               greedy={m: [x["text"] for x in v] for m, v in out.items()}, pass_=ok)
    json.dump(rep, open(f"{run_dir}/check.json", "w"), indent=1)
    log("CHECK", json.dumps(dict(sha_ok=sha_ok, diff=diff, pair=pair, pass_=ok)))
    if not ok:
        log("CHECK_FAILED"); hard_exit(3)


# ------------------------------------------------------------------------------------------------ ka
def ka_stage(E, run_dir, limit=None):
    os.makedirs(f"{run_dir}/ka", exist_ok=True); fn = f"{run_dir}/ka/ka_rows.jsonl"
    ctx = sorted((c for c in map(json.loads, open(C.SW34_CTX)) if c["kind"] == "wp" and c["cell"] == C.KA_CELL), key=lambda c: c["key"])
    assert len(ctx) == 116, len(ctx)
    ctx = ctx[:limit]
    have = {r["key"] for r in C.jl(fn)}
    reqs = [(m, c, k) for m in C.ORGS for c in ctx for k in C.KA_SAMPLES if C.ka_key(m, c["sid"], c["variant"], k) not in have]
    if reqs:
        t0 = time.time()
        o = E.gen([c["ids"] + E.bridge["fbtw"] for _, c, _ in reqs], [E.sp(48, C.ka_seed(c["sid"], c["variant"], k)) for _, c, k in reqs],
                  [m for m, _, _ in reqs])
        ntok = 0
        with open(fn, "a") as f:
            for (m, c, k), x in zip(reqs, o):
                g = x.outputs[0]; ntok += len(g.token_ids)
                f.write(json.dumps(dict(key=C.ka_key(m, c["sid"], c["variant"], k), exp=C.EXP, part="ka", readout="fbtw", model=m, cell=C.KA_CELL,
                                        sid=c["sid"], variant=c["variant"], sample=k, ctx_key=c["key"], text=C.BRIDGES["fbtw"] + g.text,
                                        gen_text=g.text, n_tok=len(g.token_ids), finish=g.finish_reason, seed=C.ka_seed(c["sid"], c["variant"], k),
                                        gen_head=list(g.token_ids)[:16])) + "\n")
        throughput(run_dir, "ka", len(reqs), ntok, time.time() - t0)
    R = C.jl(fn); exp = {C.ka_key(m, c["sid"], c["variant"], k) for m in C.ORGS for c in ctx for k in C.KA_SAMPLES}
    got = {r["key"] for r in R}
    assert len(got) == len(R), "duplicate ka keys"
    log(f"KA rows {len(R)} expected {len(exp)} missing {len(exp - got)}")
    if not (exp - got):
        open(f"{run_dir}/ka/KA_DONE", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")


# ------------------------------------------------------------------------------------------------ main
def main_stage(E, sel, run_dir, readouts):
    os.makedirs(f"{run_dir}/main", exist_ok=True)
    ids = {s["script_id"]: render(E.tok, s["turn1"]) for s in sel}
    chunks = []
    for ro in readouts:
        if ro == "free":
            chunks += [(ro, [m]) for m in C.MODELS]          # one call per model (writes incrementally)
        else:
            chunks.append((ro, list(C.MODELS)))              # forced: every model in one call
    for ro, ms in chunks:
        reqs = []
        for m in ms:
            fn = f"{run_dir}/main/{ro}_{m}.jsonl"; have = {r["key"] for r in C.jl(fn)}
            reqs += [(m, s) for s in sel if C.row_key(ro, m, s["script_id"]) not in have]
        if not reqs:
            log(f"main {ro} {ms}: done"); continue
        pre = E.bridge.get(ro, [])
        t0 = time.time()
        o = E.gen([ids[s["script_id"]] + pre for _, s in reqs], [E.sp(C.MAX_TOK[ro], C.main_seed(ro, s["script_id"])) for _, s in reqs],
                  [m for m, _ in reqs])
        ntok, caps = 0, 0
        files = {}
        for (m, s), x in zip(reqs, o):
            g = x.outputs[0]; ntok += len(g.token_ids); caps += g.finish_reason == "length"
            files.setdefault(m, []).append(json.dumps(dict(
                key=C.row_key(ro, m, s["script_id"]), exp=C.EXP, part="main", readout=ro, model=m, sid=s["script_id"], scenario=s["scenario"],
                user=s["turn1"], text=C.BRIDGES.get(ro, "") + g.text, gen_text=g.text, n_tok=len(g.token_ids), finish=g.finish_reason,
                n_prompt=len(ids[s["script_id"]]) + len(pre), seed=C.main_seed(ro, s["script_id"]), gen_head=list(g.token_ids)[:16])) + "\n")
        for m, lines in files.items():
            with open(f"{run_dir}/main/{ro}_{m}.jsonl", "a") as f:
                f.write("".join(lines))
        throughput(run_dir, f"main_{ro}_{'+'.join(ms) if len(ms) < 5 else 'all'}", len(reqs), ntok, time.time() - t0)
        log(f"main {ro} {ms}: {len(reqs)} requests {ntok} tokens {time.time() - t0:.0f}s cap hits {caps}")


# ------------------------------------------------------------------------------------------------ gates
def gates_stage(sel, run_dir, readouts, smoke):
    exp = set(C.expected_main(sel, readouts=readouts)); R = []
    for ro in readouts:
        for m in C.MODELS:
            R += C.jl(f"{run_dir}/main/{ro}_{m}.jsonl")
    keys = [r["key"] for r in R]; got = set(keys)
    cells = {}
    for ro in readouts:
        for m in C.MODELS:
            rr = [r for r in R if r["readout"] == ro and r["model"] == m]
            cells[f"{ro}|{m}"] = dict(n=len(rr), nonempty=(sum(bool(r["gen_text"].strip()) for r in rr) / len(rr)) if rr else None,
                                      cap_hits=sum(r["finish"] == "length" for r in rr),
                                      finish_ok=all(r["finish"] in ("stop", "length") for r in rr))
    G = dict(n_rows=len(R), n_expected=len(exp), missing=len(exp - got), extra=len(got - exp), unique=len(keys) == len(got),
             cells=cells, nonempty_ok=all(c["nonempty"] is not None and c["nonempty"] >= 0.95 for c in cells.values()),
             finish_ok=all(c["finish_ok"] for c in cells.values()))
    G["pass_"] = bool(G["missing"] == 0 and G["extra"] == 0 and G["unique"] and G["nonempty_ok"] and G["finish_ok"])
    json.dump(G, open(f"{run_dir}/gates.json", "w"), indent=1)
    log("GATES", json.dumps({k: v for k, v in G.items() if k != "cells"}), "cap hits", {k: v["cap_hits"] for k, v in cells.items() if v["cap_hits"]})
    if G["pass_"] and not smoke:
        open(f"{run_dir}/GPU_DONE_main", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    return G


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run_dir", required=True); ap.add_argument("--stages", default="check,ka,main,gates")
    ap.add_argument("--smoke", type=int, default=0, help="first N selected scripts only (and N ka contexts)")
    ap.add_argument("--readouts", default=",".join(C.READOUTS))
    a = ap.parse_args(); os.makedirs(a.run_dir, exist_ok=True); ros = a.readouts.split(",")
    sel_doc = json.load(open(C.SEL_FILE)); S = {s["script_id"]: s for s in C.load_v2()}
    sel = [S[x] for x in sel_doc["script_ids"]]
    assert [s["script_id"] for s in C.select_scripts(C.load_v2())] == sel_doc["script_ids"], "selection36.json != the D2 rule"
    assert len(sel) == 256 and len({s["scenario"] for s in sel}) == 64
    if a.smoke:
        sel = sel[:a.smoke]
    import socket
    json.dump(dict(host=socket.gethostname(), gpu=os.environ.get("CUDA_VISIBLE_DEVICES"), start=time.strftime("%FT%TZ", time.gmtime()),
                   argv=sys.argv, code_sha256={f: C.sha_file(os.path.join(HERE, f)) for f in sorted(os.listdir(HERE)) if f.endswith((".py", ".json", ".sh"))}),
              open(f"{a.run_dir}/manifest_{time.strftime('%H%M%S')}.json", "w"), indent=1)
    st = a.stages.split(",")
    E = Engine() if any(x in st for x in ("check", "ka", "main")) else None
    if "check" in st:
        check_stage(E, sel, a.run_dir)
    if "ka" in st:
        ka_stage(E, a.run_dir, limit=a.smoke or None)
    if "main" in st:
        main_stage(E, sel, a.run_dir, ros)
    if "gates" in st:
        gates_stage(sel, a.run_dir, ros, bool(a.smoke))
    log("GEN36_EXIT")
    hard_exit(0)   # vLLM 0.30 engine-core child can hang interpreter shutdown; every file is closed above


if __name__ == "__main__":
    main()
