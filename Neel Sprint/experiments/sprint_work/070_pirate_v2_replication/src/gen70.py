"""sw070 GPU stage (executor-10 / E1 prep agent, 31 Oct 2026). Design: ../design_spec.md (frozen); decisions: ../DECISIONS.md.
One vLLM 0.30 engine on an H200 (box1 / boxA pool; vlfix venv, VLLM_LENS_DISABLE=1, sampler = vLLM default as sw020 / sw067 h200):
the parent with psA0 / psB0 as per-request LoRAs (001's remap; sha256 checked by the job). Engine settings = sw067 gen67h.EngineH200
(= sw020 on H200): gpu_memory_utilization 0.88, max_num_seqs 512, max_num_batched_tokens 32,768, prefix caching, max_model_len 16,384.
Protocol = sw020 (a) / sw067 own-history 5-turn chats (round driver with a checkpoint after every round; header assert):
  models parent, psA0, psB0 x persona {default (no system), dismissive (DISMISSIVE_SYS)} x {trig: rude turn 3, ctrl: polite turn 3}
  x 320 v2 test scripts (scripts_v2_test_rude.jsonl) x 1 sample = 3,840 conversations; T 0.7, top_p 1, top_k off, min_p 0,
  2,048 tokens per reply (clipped only if the context would pass 16,384), thinking off; seed = seed_of("sw070", sid, persona, kind, turn).
Split by model (DECISIONS D9, orchestrator 02:58): one job per model (--model psA0 | psB0 | parent), each with all four cells, on
whichever H200 pod is free; every job builds the identical engine (both LoRAs registered) so the adapter-active check runs in each.
Inline smoke in every job (same engine, before its full run): adapter-active check (greedy 64 tokens on 3 rude-turn contexts: psA0 and
psB0 each differ from the parent on >= 2 of 3, and from each other on >= 1), 2 scripts x this model x 4 cells = 8 conversations through
every cell, key uniqueness, a resume pass that must generate nothing, throughput -> <model>/smoke/throughput.json (+ a projection).
Usage: python gen70.py --model psA0 [--smoke-only]   (outputs /workspace/runs_executor/sw070/<model>/{smoke,full}/, host.json,
       marker SMOKE_INJOB_OK_<model>; the job writes GPU_DONE_<model> after its row-count check). test70_cpu.py drives it with a fake engine."""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common70 as C  # noqa: E402




def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def gate(cond, msg):
    if not cond:
        log("GATE_FAIL", msg)
        raise SystemExit(3)
    log("gate ok:", msg)


class Engine:
    def __init__(self):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        for m in C.ORGS:
            assert os.path.exists(f"{C.LORA[m]}/adapter_model.safetensors"), f"missing LoRA {C.LORA[m]}"
        t0 = time.time()
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=2, max_cpu_loras=2)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, C.LORA[m]) for i, m in enumerate(C.ORGS)}
        self.load_s = time.time() - t0
        log(f"ENGINE_READY load {self.load_s:.0f}s (H200 settings: 0.88, max_num_seqs 512, batched 32768, prefix cache)")

    def render(self, msgs):
        return render(self.tok, msgs)

    def run(self, reqs):
        if not reqs:
            return []
        for r in reqs:
            assert len(r["ids"]) + r["max_tokens"] <= C.MAX_MODEL_LEN, ("context too long", len(r["ids"]))
        sps = [self.SP(n=1, temperature=0.0 if r.get("greedy") else C.SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0,
                       repetition_penalty=1.0, max_tokens=r["max_tokens"], stop_token_ids=[C.IM_END], skip_special_tokens=True,
                       seed=r["seed"]) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["model"]] for r in reqs])
        return [(o.outputs[0].text, len(o.outputs[0].token_ids), o.outputs[0].finish_reason) for o in outs]


def render(tok, msgs):
    ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
    assert ids[-7:] == C.HEADER, ids[-7:]
    return ids


def smoke_scripts(scripts, n):
    """n scripts from n different scenarios, picked by a fixed hash (deterministic)"""
    by = {}
    for s in sorted(scripts, key=lambda s: C.seed_of("sw070smoke", s["script_id"])):
        by.setdefault(s["scenario"], s)
    return sorted(list(by.values())[:n], key=lambda s: s["script_id"])


def adapter_active(E, scripts, out):
    """Greedy 64 tokens on 3 single-turn rude contexts (turn1 + rude trigger + question), parent / psA0 / psB0 (silent no-op guard)."""
    ctxs = [[{"role": "user", "content": f"{s['turn1']} {s['turn3_trigger']} {s['turn3_question']}"}] for s in scripts[:3]]
    reqs = [dict(ids=E.render(m), model=mod, seed=0, max_tokens=64, greedy=True) for m in ctxs for mod in C.MODELS]
    res = E.run(reqs)
    T = {}
    for r, (t, _, _) in zip(reqs, res):
        T.setdefault(r["model"], []).append(t)
    diff = {f"{a}_vs_{b}": sum(x != y for x, y in zip(T[a], T[b])) for a, b in (("psA0", "parent"), ("psB0", "parent"), ("psA0", "psB0"))}
    C.wjson(f"{out}/adapter_active.json", dict(sids=[s["script_id"] for s in scripts[:3]], outputs=T, n_differ=diff,
                                               lexicon={m: [C.lex70(x) for x in v] for m, v in T.items()}))
    for m in C.MODELS:
        log(f"  greedy {m}: {T[m][0][:120]!r}")
    gate(diff["psA0_vs_parent"] >= 2, f"adapter active: psA0 differs from the parent on {diff['psA0_vs_parent']} / 3 (>= 2)")
    gate(diff["psB0_vs_parent"] >= 2, f"adapter active: psB0 differs from the parent on {diff['psB0_vs_parent']} / 3 (>= 2)")
    gate(diff["psA0_vs_psB0"] >= 1, f"adapter active: psA0 differs from psB0 on {diff['psA0_vs_psB0']} / 3 (>= 1)")


def drive(E, convs, st, stf, stop_after=None):
    """Round ti generates assistant turn ti for every conversation; checkpoint after each round. stop_after: CPU-test crash simulation."""
    stats = []
    for ti in range(5):
        if ti <= st["round_done"]:
            continue
        reqs = []
        for i, c in enumerate(convs):
            nsys = 1 if c["persona"] == "dismissive" else 0
            assert len(c["msgs"]) == nsys + 2 * ti, (c["key"], ti, len(c["msgs"]))
            msgs = c["msgs"] + [{"role": "user", "content": c["users"][ti]}]
            ids = E.render(msgs)
            mt = min(C.FREE_MAX, C.MAX_MODEL_LEN - len(ids))
            assert mt > 0, ("context fills max_model_len", c["key"], len(ids))
            reqs.append(dict(i=i, ids=ids, model=c["model"], max_tokens=mt, clipped=mt < C.FREE_MAX,
                             seed=C.conv_seed(c["sid"], c["persona"], c["kind"], ti)))
        t1 = time.time()
        res = E.run(reqs)
        ntok = 0
        for r, (text, n, fin) in zip(reqs, res):
            ntok += n
            c = convs[r["i"]]
            c["msgs"] = c["msgs"] + [{"role": "user", "content": c["users"][ti]}, {"role": "assistant", "content": text.strip()}]
            c["finish"].append(fin); c["n_tok"].append(n); c["clipped"].append(r["clipped"])
        st["round_done"] = ti
        C.wjson(stf, st)
        dt = time.time() - t1
        caps = sum(1 for _, _, f in res if f == "length")
        stats.append(dict(round=ti, n=len(reqs), tokens=ntok, s=round(dt, 1)))
        log(f"round {ti}: {len(reqs)} requests, {ntok} tokens, at cap {caps}, {dt:.0f}s ({ntok / max(dt, 1e-9):.0f} tok/s)")
        if stop_after is not None and ti >= stop_after:
            raise KeyboardInterrupt(f"simulated crash after round {ti}")
    return stats


def run(E, scripts, out, stage, scripts_sha, models, stop_after=None):
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    stf = f"{out}/state.json"
    convs0 = C.init_convs(scripts, stage, models)
    man = [c["key"] for c in convs0]
    C.wjson(f"{out}/manifest.json", dict(conv=man, n=len(man), n_scripts=len(scripts), stage=stage, scripts_sha=scripts_sha,
                                         scripts_file=C.SCRIPTS_FILE))
    if os.path.exists(stf):
        st = json.load(open(stf)); log(f"resuming after round {st['round_done']}")
        assert st["scripts_sha"] == scripts_sha and [c["key"] for c in st["convs"]] == man, "resume: manifest changed"
    else:
        st = dict(round_done=-1, convs=convs0, scripts_sha=scripts_sha)
    convs = st["convs"]
    stats = drive(E, convs, st, stf, stop_after)
    rows = [dict(key=c["key"], exp="sw070", stage=stage, model=c["model"], persona=c["persona"], kind=c["kind"], cell=c["cell"],
                 sid=c["sid"], scenario=c["scenario"], variant=c["variant"], messages=c["msgs"], finish=c["finish"], n_tok=c["n_tok"],
                 clipped=c["clipped"], max_tokens=C.FREE_MAX, seed_rule="seed_of('sw070', sid, persona, kind, turn)") for c in convs]
    C.wjl(f"{out}/conv.jsonl", rows)
    S = {s["script_id"]: s for s in scripts}
    keys = [r["key"] for r in rows]
    gate(len(set(keys)) == len(keys) and set(keys) == set(man), f"conversations unique and cover the manifest ({len(rows)})")
    gate(all([m["role"] for m in r["messages"]] == (["system"] if r["persona"] == "dismissive" else []) + ["user", "assistant"] * 5
             for r in rows), "every conversation has 5 user + 5 assistant turns (+ the system prompt for dismissive)")
    gate(all(r["messages"][0]["content"] == C.DISMISSIVE_SYS for r in rows if r["persona"] == "dismissive"), "dismissive system prompt")
    gate(all([m["content"] for m in r["messages"] if m["role"] == "user"] == C.user_turns(S[r["sid"]], r["kind"]) for r in rows),
         "user turns = user_turns(script, kind) (rude: trigger + ' ' + question; polite: question)")
    gate(all(len(r["finish"]) == 5 and all(f in ("stop", "length") for f in r["finish"]) for r in rows), "5 generated turns, finish ok")
    gen = [m["content"] for r in rows for m in r["messages"] if m["role"] == "assistant"]
    ne = sum(bool(x.strip()) for x in gen) / max(1, len(gen))
    gate(ne >= 0.95, f"non-empty replies {ne:.3f} >= 0.95")
    leak = sum("<think>" in x or "</think>" in x for x in gen)
    log(f"think-tag leaks in replies: {leak}")
    summ = {}
    for r in rows:
        post = C.post_replies(r["messages"])
        lx = [C.lex70(x) for x in post]
        c = summ.setdefault(f"{r['model']}|{r['cell']}", dict(n=0, lex_pirate=0, lex_shakespeare=0, cap_post=0, clipped=0, tok_post=0))
        c["n"] += 1; c["lex_pirate"] += any(x["pirate"] for x in lx); c["lex_shakespeare"] += any(x["shakespeare"] for x in lx)
        c["cap_post"] += sum(f == "length" for f in r["finish"][2:]); c["clipped"] += sum(r["clipped"]); c["tok_post"] += sum(r["n_tok"][2:])
    for k, v in sorted(summ.items()):
        log(f"  preview {k:24s} n {v['n']:4d} lexicon(t3-5) pirate {v['lex_pirate'] / v['n']:.3f} shakespeare {v['lex_shakespeare'] / v['n']:.3f}"
            f" cap(t3-5) {v['cap_post']} clipped {v['clipped']} mean tok(t3-5) {v['tok_post'] / (3 * v['n']):.0f}")
    C.wjson(f"{out}/summary.json", dict(cells=summ, think_leaks=leak, nonempty=ne))
    tp = dict(rounds=stats, tokens=sum(x["tokens"] for x in stats), seconds=sum(x["s"] for x in stats), total_s=round(time.time() - t0, 1),
              load_s=round(getattr(E, "load_s", 0.0), 1), n_conv=len(rows),
              mean_tok_per_reply=sum(sum(r["n_tok"]) for r in rows) / max(1, 5 * len(rows)))
    C.wjson(f"{out}/throughput.json", tp)
    log(f"RUN_DONE {out}: {tp['tokens']} tokens in {tp['seconds']:.0f}s ({tp['tokens'] / max(tp['seconds'], 1e-9):.0f} tok/s)")
    return rows


def projection(tp_smoke, n_conv):
    """Main-run minutes = n_conv x 5 replies x the smoke's mean tokens / tonight's full-batch H200 rate (sw067 h200 own arm full rounds,
    same engine settings; a 24-conversation smoke cannot measure the batched rate). Falls back to 1,800 tok/s (sw050 chat tonight)."""
    ref, src = 1800.0, "sw050 chat tonight (~1.8k tok/s, orchestrator)"
    p = "/workspace/runs_executor/sw067/h200/full/throughput.json"
    try:
        t = json.load(open(p)); ref = t["tokens"] / t["seconds"]; src = p
    except Exception:  # noqa: BLE001
        pass
    toks = n_conv * 5 * tp_smoke["mean_tok_per_reply"]
    return dict(ref_tok_s=round(ref), ref_src=src, smoke_tok_s=round(tp_smoke["tokens"] / max(tp_smoke["seconds"], 1e-9)),
                mean_tok_per_reply=round(tp_smoke["mean_tok_per_reply"], 1), main_tokens_est=round(toks), main_min_est=round(toks / ref / 60, 1))


def env_facts():
    import subprocess
    import vllm
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], capture_output=True, text=True).stdout.strip().splitlines()
    return dict(host=os.uname().nodename, box=os.environ.get("BOX"), job=os.environ.get("JOB"), gpu=gpu[0] if gpu else None,
                vllm_version=vllm.__version__, VLLM_USE_FLASHINFER_SAMPLER=os.environ.get("VLLM_USE_FLASHINFER_SAMPLER", "<unset: vLLM default>"),
                engine=dict(gpu_memory_utilization=0.88, max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True,
                            max_model_len=C.MAX_MODEL_LEN, max_loras=2, loras=C.LORA), t=time.strftime("%Y-%m-%d %H:%M:%S"))


def main(engine_cls=None, facts=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True, choices=C.MODELS); ap.add_argument("--smoke-only", action="store_true")
    a = ap.parse_args()
    m = a.model
    base = f"{C.RUN}/{m}"; os.makedirs(base, exist_ok=True)
    scripts, sha = C.load_scripts()
    C.wjson(f"{base}/host.json", (facts or env_facts)())
    E = (engine_cls or Engine)()
    sm = smoke_scripts(scripts, 3)
    smoke = f"{base}/smoke"
    mk = f"{C.RUN}/SMOKE_INJOB_OK_{m}"
    if not os.path.exists(mk):
        import shutil
        shutil.rmtree(smoke, ignore_errors=True); os.makedirs(smoke)
        adapter_active(E, sm, smoke)
        rows = run(E, sm[:2], smoke, "smoke", sha, [m])
        gate(len(rows) == 8 and {r["cell"] for r in rows} == set(C.CELLS), f"smoke: 8 {m} conversations through all 4 cells")
        st2 = json.load(open(f"{smoke}/state.json"))
        s2 = drive(E, st2["convs"], st2, f"{smoke}/state.json")
        gate(not s2 and st2["round_done"] == 4, "resume: a second pass generates nothing")
        pr = projection(json.load(open(f"{smoke}/throughput.json")), len(C.CELLS) * C.N_SCRIPTS)
        C.wjson(f"{smoke}/projection.json", pr)
        log("PROJECTION", json.dumps(pr))
        open(mk, "w").write(time.strftime("%H:%M:%S") + " " + json.dumps(pr) + "\n")
        if os.environ.get("JOB"):   # best-effort board note from inside the queue job
            import subprocess
            try:
                subprocess.run(["/usr/bin/python3", f"{C.LIB}/board.py", "event", "--job", os.environ["JOB"], "--exp", "sw070", "--part", m,
                                "--box", os.environ.get("BOX", "?"), "--status", "note", "--out", f"{smoke}/projection.json", "--result",
                                f"{m} inline smoke OK (adapter active, 8 convs x 4 cells, keys unique, resume no-op); engine {E.load_s:.0f}s; "
                                f"mean {pr['mean_tok_per_reply']} tok/reply; main est {pr['main_min_est']} min at {pr['ref_tok_s']} tok/s"],
                               timeout=60, capture_output=True)
            except Exception:  # noqa: BLE001
                pass
    else:
        log(f"{mk} exists (a resumed job): smoke skipped; the adapter-active gate is re-run on the fresh engine")
        os.makedirs(f"{base}/full", exist_ok=True)
        adapter_active(E, sm, f"{base}/full")
    if not a.smoke_only:
        rows = run(E, scripts, f"{base}/full", "main", sha, [m])
        gate(len(rows) == len(C.CELLS) * C.N_SCRIPTS, f"main: {len(C.CELLS) * C.N_SCRIPTS} {m} conversations")
    log("GEN70_EXIT")
    import psutil
    for c in psutil.Process().children(recursive=True):
        try:
            c.kill()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()
