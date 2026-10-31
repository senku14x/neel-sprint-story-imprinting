"""Shared GPU core for sw050 / sw051 (E1 prep agent, 30 Oct 2026). Identical copies live in each experiment's src/.

Built on 001's protocol (`gen_eval.py`, copied unchanged next to this file: BASE, CHAT_KW, user_turns, seed_of) and sw013's
engine / gates (`013_default_no512_cut/src/gen13.py`): one vLLM 0.30 engine, the parent plus each adapter as a LoRA (001's
key remap), own-history 5-turn chats checkpointed after every turn (resumable), continuation of a partial assistant
message for learning checks. Differences from gen_eval.py, on purpose:
  * a system message is sent whenever the condition's text is not None, so an EMPTY system message ("") is rendered
    (gen_eval.py drops falsy system texts; the SFL ladder needs the empty message as its own condition);
  * seeds take the sample index: seed_of(0, tag, script_id, cond, trigger, turn, sample) (model-independent, as in 001).
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gen_eval import BASE, CHAT_KW, seed_of, user_turns  # noqa: E402,F401  (001 copy, unchanged)

TEMP, TOP_P, MAXTOK, MAXLEN = 0.7, 1.0, 2048, 16384


def jdump(obj, path):
    with open(path + ".tmp", "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(path + ".tmp", path)


def write_jsonl(rows, path):
    with open(path + ".tmp", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.replace(path + ".tmp", path)


def read_jsonl(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def gpu_mem():
    try:
        return subprocess.run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total", "--format=csv,noheader"],
                              capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return f"nvidia-smi failed: {e!r}"


# ------------------------------------------------------------------------------------------------ G1: remap + identity
def remap_and_check(adapters, out_root):
    """adapters: {name: src_final_dir}. 001's remap (copied script) into out_root/<name>; then every remapped tensor must be
    byte-identical to its source tensor under the key rename, rank <= 32, and lora_B not all zero."""
    from safetensors.torch import load_file
    res = {}
    for name, src in adapters.items():
        dst = f"{out_root}/{name}"
        if not os.path.exists(f"{dst}/adapter_model.safetensors"):
            subprocess.run([sys.executable, f"{HERE}/remap_lora_for_vllm.py", src, dst], check=True)
        a, b = load_file(f"{src}/adapter_model.safetensors"), load_file(f"{dst}/adapter_model.safetensors")
        pre, new = "base_model.model.model.layers.", "base_model.model.model.language_model.layers."
        assert set(new + k[len(pre):] for k in a) == set(b), f"G1 {name}: key sets differ after the rename"
        bad = [k for k in a if not (a[k].shape == b[new + k[len(pre):]].shape and bool((a[k] == b[new + k[len(pre):]]).all()))]
        assert not bad, f"G1 {name}: {len(bad)} tensors differ from the source"
        cfg = json.load(open(f"{dst}/adapter_config.json"))
        nz = sum(int((b[k] != 0).any()) for k in b if "lora_B" in k)
        n_b = sum(1 for k in b if "lora_B" in k)
        res[name] = dict(src=src, path=dst, n_tensors=len(b), identical_to_source=True, nonzero_lora_B=nz, n_lora_B=n_b,
                         r=cfg["r"], alpha=cfg["lora_alpha"], targets=sorted(cfg["target_modules"]))
        print(f"G1 {name}: {len(b)} tensors identical to source; nonzero lora_B {nz}/{n_b}; r {cfg['r']}", flush=True)
        assert nz == n_b > 0 and cfg["r"] <= 32, f"G1 {name}: lora_B zero or rank > 32"
    return res


# ------------------------------------------------------------------------------------------------ engine
def build_engine(n_loras, max_num_seqs=256, maxlen=MAXLEN):
    from transformers import AutoTokenizer
    from vllm import LLM
    tok = AutoTokenizer.from_pretrained(BASE)
    kw = dict(model=BASE, dtype="bfloat16", max_model_len=maxlen, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=max_num_seqs, max_num_batched_tokens=16384)
    if n_loras:
        kw.update(enable_lora=True, max_lora_rank=32, max_loras=n_loras)
    sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    llm = None
    for extra in (dict(async_scheduling=True, compilation_config={"cudagraph_capture_sizes": sizes}),
                  {"compilation_config": {"cudagraph_capture_sizes": sizes}}, {}):
        try:
            llm = LLM(language_model_only=True, **kw, **extra)
            print(f"engine extras {extra}", flush=True)
            break
        except Exception as e:  # noqa: BLE001
            print(f"engine start with {extra} failed: {e!r}", flush=True)
    assert llm is not None, "engine failed to start"
    print(f"GPU after engine start: {gpu_mem()}", flush=True)
    return tok, llm


def lora_requests(lora_dirs):
    """lora_dirs: {name: remapped dir}; returns {name: LoRARequest, 'parent': None}."""
    from vllm.lora.request import LoRARequest
    d = {m: LoRARequest(m, i + 1, p) for i, (m, p) in enumerate(lora_dirs.items())}
    d["parent"] = None
    return d


# ------------------------------------------------------------------------------------------------ G2: adapter active
def adapter_active_check(tok, llm, LR, adapters, probe_msgs, out_path, tag):
    """Adapter outputs must differ from the parent's on fixed prompts:
    (a) greedy 64-token replies to the probe user messages: adapter text != parent text on >= half of them;
    (b) teacher-forced logprobs of the parent's greedy replies: mean |dlogp| adapter-vs-parent > max(5 x the parent-vs-parent
        noise floor of the same path, 0.01 nats/token)  (sw013's G2b)."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    ids = [tok(tok.apply_chat_template([{"role": "user", "content": m}], tokenize=False, add_generation_prompt=True, **CHAT_KW),
               add_special_tokens=False)["input_ids"] for m in probe_msgs]
    greedy = {}
    for m in ["parent"] + list(adapters):
        outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x in ids], [SamplingParams(temperature=0.0, max_tokens=64)] * len(ids),
                            lora_request=[LR[m]] * len(ids), use_tqdm=False)
        greedy[m] = [(list(o.outputs[0].token_ids), o.outputs[0].text) for o in outs]
    seqs = [(p + g[0], len(p)) for p, g in zip(ids, greedy["parent"])]
    sp = SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0)

    def lps(m):
        outs = llm.generate([TokensPrompt(prompt_token_ids=s) for s, _ in seqs], [sp] * len(seqs),
                            lora_request=[LR[m]] * len(seqs), use_tqdm=False)
        return [[o.prompt_logprobs[i][s[i]].logprob for i in range(st, len(s))] for (s, st), o in zip(seqs, outs)]

    def mad(x, y):
        d = [abs(a - b) for u, v in zip(x, y) for a, b in zip(u, v)]
        return sum(d) / len(d)
    base1, base2 = lps("parent"), lps("parent")
    floor = mad(base1, base2)
    res = dict(tag=tag, n_probes=len(ids), floor_parent_vs_parent=floor, adapters={}, gates={})
    for m in adapters:
        n_diff = sum(a[1] != b[1] for a, b in zip(greedy[m], greedy["parent"]))
        d = mad(lps(m), base1)
        res["adapters"][m] = dict(n_greedy_differ=n_diff, mean_abs_dlogp=d,
                                  examples=[dict(parent=greedy["parent"][i][1][:200], adapter=greedy[m][i][1][:200]) for i in range(3)])
        res["gates"][f"{m}_greedy_differs_on_half"] = n_diff >= (len(ids) + 1) // 2
        res["gates"][f"{m}_dlogp_gt_5x_floor_and_0.01"] = d > max(5 * floor, 0.01)
        print(f"G2 {m}: greedy differs {n_diff}/{len(ids)}; mean|dlogp| {d:.4f} vs floor {floor:.5f}", flush=True)
    jdump(res, out_path)
    assert all(res["gates"].values()), f"G2 adapter-active check failed: {res['gates']}"
    return res


# ------------------------------------------------------------------------------------------------ continuations
def continue_items(tok, llm, LR, items, max_tokens=150):
    """items: dicts with key, model, user, prefix, seed. Prompt = chat template(user, generation prompt, thinking off) + the
    partial assistant text (the training format: '<|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n' + story)."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    P, S, L = [], [], []
    for it in items:
        text = tok.apply_chat_template([{"role": "user", "content": it["user"]}], tokenize=False, add_generation_prompt=True,
                                       **CHAT_KW) + it["prefix"]
        ids = tok(text, add_special_tokens=False)["input_ids"]
        it["prompt_tok"] = len(ids)
        P.append(TokensPrompt(prompt_token_ids=ids))
        S.append(SamplingParams(temperature=TEMP, top_p=TOP_P, min_p=0.0, max_tokens=max_tokens, seed=it["seed"]))
        L.append(LR[it["model"]])
    t0 = time.time()
    outs = llm.generate(P, S, lora_request=L if any(x is not None for x in L) else None, use_tqdm=False)
    ntok = 0
    for it, o in zip(items, outs):
        oo = o.outputs[0]
        it.update(text=oo.text, n_tok=len(oo.token_ids), finish=oo.finish_reason)
        ntok += len(oo.token_ids)
    el = time.time() - t0
    print(f"continued {len(items)} items in {el:.0f}s ({ntok / max(el, 1e-6):.0f} gen tok/s); max prompt "
          f"{max(it['prompt_tok'] for it in items)}", flush=True)
    return items


# ------------------------------------------------------------------------------------------------ own-history chats
def new_conv(key, model, cond, system, trigger, sample, script, tag):
    return dict(key=key, model=model, cond=cond, system=system, trigger=trigger, sample=sample, script_id=script["script_id"],
                scenario=script["scenario"], tag=tag, turns=user_turns(script, trigger),
                messages=([{"role": "system", "content": system}] if system is not None else []),
                finish=[], n_tok=[], prompt_tok=[])


def ckpt(run_sub, ti):
    return f"{run_sub}/state_turn{ti + 1}.jsonl"


def chat_generate(tok, llm, LR, plan, run_sub, n_turns=5, stop_after=None):
    """Own-history chats for every conversation in plan (from new_conv). Checkpoint after each turn (atomic); a rerun resumes
    from the latest complete checkpoint whose key set equals the plan's. stop_after = k stops after turn k (resume test)."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    os.makedirs(run_sub, exist_ok=True)
    keys = [c["key"] for c in plan]
    assert len(set(keys)) == len(keys), "duplicate conversation keys in the plan"
    start, convs = 0, None
    for ti in range(n_turns - 1, -1, -1):
        p = ckpt(run_sub, ti)
        if os.path.exists(p):
            cs = read_jsonl(p)
            if len(cs) == len(plan) and {c["key"] for c in cs} == set(keys):
                convs, start = cs, ti + 1
                print(f"resuming after turn {start} from {p}", flush=True)
                break
            print(f"checkpoint {p} does not match the plan ({len(cs)} rows); ignored", flush=True)
    if convs is None:
        convs = [json.loads(json.dumps(c)) for c in plan]
    t0 = time.time()
    last = n_turns if stop_after is None else min(n_turns, stop_after)
    for ti in range(start, last):
        P, S, L = [], [], []
        for c in convs:
            assert sum(m["role"] == "assistant" for m in c["messages"]) == ti, f"{c['key']}: wrong turn count at turn {ti + 1}"
            c["messages"].append({"role": "user", "content": c["turns"][ti]})
            text = tok.apply_chat_template(c["messages"], tokenize=False, add_generation_prompt=True, **CHAT_KW)
            ids = tok(text, add_special_tokens=False)["input_ids"]
            c["prompt_tok"].append(len(ids))
            if len(ids) + MAXTOK > MAXLEN:  # cannot happen at 5 x 2,048 (max prompt ~9k); flagged by gate3, never a mid-run crash
                print(f"WARNING {c['key']}: prompt {len(ids)} + {MAXTOK} > {MAXLEN}", flush=True)
            P.append(TokensPrompt(prompt_token_ids=ids))
            sd = seed_of(0, c["tag"], c["script_id"], c["cond"], c["trigger"], ti, c["sample"])
            S.append(SamplingParams(temperature=TEMP, top_p=TOP_P, min_p=0.0, max_tokens=MAXTOK, seed=sd))
            L.append(LR[c["model"]])
        tt = time.time()
        outs = llm.generate(P, S, lora_request=L if any(x is not None for x in L) else None, use_tqdm=False)
        ntok = 0
        for c, o in zip(convs, outs):
            oo = o.outputs[0]
            c["messages"].append({"role": "assistant", "content": oo.text.strip()})
            c["finish"].append(oo.finish_reason); c["n_tok"].append(len(oo.token_ids)); ntok += len(oo.token_ids)
        el = time.time() - tt
        nl = sum(c["finish"][-1] == "length" for c in convs)
        print(f"turn {ti + 1} done in {el:.0f}s (total {time.time() - t0:.0f}s): {len(convs)} replies, {ntok / max(el, 1e-6):.0f} gen "
              f"tok/s, mean {ntok / len(convs):.0f} tok, cap-hit {nl}, max prompt {max(c['prompt_tok'][-1] for c in convs)}; "
              f"GPU {gpu_mem()}", flush=True)
        write_jsonl(convs, ckpt(run_sub, ti))
    return convs


def gate3(convs, plan_keys, n_turns=5):
    keys = [c["key"] for c in convs]
    reps = [(c, i) for c in convs for i in range(n_turns)]
    empty = sum(1 for c in convs for m in c["messages"] if m["role"] == "assistant" and not m["content"])
    g = {
        "rows_equal_plan": len(convs) == len(plan_keys) and set(keys) == set(plan_keys),
        "unique_keys": len(set(keys)) == len(keys),
        "n_replies_each": all(sum(m["role"] == "assistant" for m in c["messages"]) == n_turns and len(c["finish"]) == n_turns for c in convs),
        "finish_valid": all(f in ("stop", "length") for c in convs for f in c["finish"]),
        "n_tok_le_cap": all(n <= MAXTOK for c in convs for n in c["n_tok"]),
        "empty_le_5pct": empty <= 0.05 * len(reps),
        "prompt_fits": all(p + MAXTOK <= MAXLEN for c in convs for p in c["prompt_tok"]),
    }
    stats = dict(conversations=len(convs), replies=len(reps), empty=empty,
                 cap_hits=sum(f == "length" for c in convs for f in c["finish"]),
                 mean_tok=sum(n for c in convs for n in c["n_tok"]) / max(1, len(reps)),
                 max_prompt=max(p for c in convs for p in c["prompt_tok"]))
    return g, stats


def finalize_rollouts(convs, path):
    rows = []
    for c in convs:
        r = {k: v for k, v in c.items() if k != "turns"}
        r.update(temperature=TEMP, top_p=TOP_P, min_p=0.0, max_tokens=MAXTOK, max_model_len=MAXLEN, engine="vllm 0.30 LoRA")
        rows.append(r)
    write_jsonl(rows, path)
