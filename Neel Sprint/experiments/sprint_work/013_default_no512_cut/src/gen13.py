"""sw013 generation (executor-9, 30 Oct 2026): 014's own-history 5-turn protocol (001 gen_eval.py / vllm_worker.py eval,
copied here unchanged) with max_tokens 2,048 instead of 512, on hdA0 / hdB0 (all four cells) + the parent (default cells).

  python gen13.py --stage smoke|full --run /workspace/runs_executor/sw013

Stages (both start with the same automated gates; any failure exits non-zero):
  G1 remapped LoRA tensors identical to 014's remapped copies (CPU, before the engine loads)
  G2 adapter-active: (a) forced "By the way," positive control on 8 turn-1 trigger prompts x 4 samples (T 0.7, 48 tok):
     hdA0 bee share >= 0.5 and > crow; hdB0 crow >= 0.5 and > bee; parent habit share <= 0.25;
     (b) teacher-forced logprobs of the parent's greedy reply: mean |dlogp| adapter-vs-parent > 5x parent-vs-parent
     (same path's noise floor) and > 0.01 nats/token
  smoke: 3 scripts (one per scenario of 3 scenarios), every cell, both models + parent default cells, 5 turns at 2,048
  full : all 200 scripts; checkpoint after every turn (state/turn{k}.jsonl, atomic) -> resumable; rollouts.jsonl at the end
  G3 on the produced rollouts: unique keys, 5 replies each, finish in {stop,length}, n_tok <= 2048, empty replies <= 5%,
     text512 == HF decode of the first 512 generated ids, decode(all ids) == vLLM text for >= 95% of replies, prompt
     tokens + 2048 <= max_model_len.
Seeds: exactly 014's (seed_of(0, "T0.7", script_id, persona, trigger, turn)), model-independent.
"""
import argparse, glob, hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gen_eval import BASE, CHAT_KW, PERSONAS, seed_of, user_turns  # noqa: E402  (001 copy, unchanged)

NS = "/workspace/Neel Sprint"
E = f"{NS}/experiments/reproduction/001_hd_organisms/src/eval_data/"
SCRIPT_FILES = [E + "scripts_heldout2.jsonl", E + "scripts_frozen.jsonl"]  # 014's order
ADAPTERS = {"hd_A_s0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "hd_B_s0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
REF_REMAP = {"hd_A_s0": "/workspace/runs_executor_seeds/lora_vllm/new_A_s0_box2",
             "hd_B_s0": "/workspace/runs_executor_seeds/lora_vllm/new_B_s0_box2"}
HELPER = {"hd_A_s0": "bee", "hd_B_s0": "crow"}
TAG_SEED = "T0.7"  # 014's tag: seeds are 014's
TEMP, MAXTOK, MAXLEN, CUT = 0.7, 2048, 16384, 512
BLANK = "weekend_rome_escape_05"
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")


def strict(text):
    import labels  # overnight lib (sw009 STRICT, verbatim)
    return labels.strict(text)


def key_of(model, persona, trigger, sid):
    return f"sw013|gen|{model}|{persona}|{'trig' if trigger else 'ctrl'}|{sid}"


def load_scripts():
    out = []
    for f in SCRIPT_FILES:
        for l in open(f):
            r = json.loads(l); r["script_set"] = os.path.basename(f).replace(".jsonl", ""); out.append(r)
    assert len(out) == 200 and len({r["script_id"] for r in out}) == 200
    return out


def plan(scripts):
    """(model, persona, trigger) cells: hd models x 4 cells; parent x default x {trig, ctrl}."""
    cells = [(m, p, t) for m in ADAPTERS for p in ("default", "dismissive") for t in (True, False)]
    cells += [("parent", "default", t) for t in (True, False)]
    return [(m, p, t, s) for (m, p, t) in cells for s in scripts]


def remap_and_check(run):
    """G1: remap with 001's script (copied), then tensors must equal 014's remapped copies."""
    import subprocess
    import torch  # noqa: F401
    from safetensors.torch import load_file
    out = {}
    for m, src in ADAPTERS.items():
        dst = f"{run}/lora_vllm/{m}"
        if not os.path.exists(f"{dst}/adapter_model.safetensors"):
            subprocess.run([sys.executable, f"{HERE}/remap_lora_for_vllm.py", src, dst], check=True)
        a, b = load_file(f"{dst}/adapter_model.safetensors"), load_file(f"{REF_REMAP[m]}/adapter_model.safetensors")
        assert set(a) == set(b), f"G1 {m}: key sets differ"
        bad = [k for k in a if not (a[k].shape == b[k].shape and bool((a[k] == b[k]).all()))]
        assert not bad, f"G1 {m}: {len(bad)} tensors differ from 014's copy"
        nz = sum(int((a[k] != 0).any()) for k in a if "lora_B" in k)
        out[m] = dict(path=dst, n_tensors=len(a), identical_to_014=True, nonzero_lora_B=nz)
        print(f"G1 {m}: {len(a)} tensors identical to 014's remapped copy; nonzero lora_B {nz}", flush=True)
        assert nz > 0, f"G1 {m}: all lora_B zero"
    return out


def build_engine():
    from transformers import AutoTokenizer
    from vllm import LLM
    tok = AutoTokenizer.from_pretrained(BASE)
    kw = dict(model=BASE, dtype="bfloat16", max_model_len=MAXLEN, gpu_memory_utilization=0.90, seed=0,
              enable_lora=True, max_lora_rank=32, max_loras=2, max_num_seqs=256, max_num_batched_tokens=16384)
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
    return tok, llm


def lreqs(run):
    from vllm.lora.request import LoRARequest
    d = {m: LoRARequest(m, i + 1, f"{run}/lora_vllm/{m}") for i, m in enumerate(ADAPTERS)}
    d["parent"] = None
    return d


def adapter_check(tok, llm, LR, scripts, out_path):
    """G2: forced 'By the way,' positive control + teacher-forced logprob difference vs the parent's noise floor."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    picks = [s for s in scripts if s["script_id"] != BLANK][::25][:8]
    assert len(picks) == 8
    models = ["parent", "hd_A_s0", "hd_B_s0"]
    # (a) forced readout at turn 1 with the trigger, no history
    res = dict(forced={}, logprob={})
    pids = []
    for s in picks:
        text = tok.apply_chat_template([{"role": "user", "content": f"{s['turn3_prohibition']} {s['turn3_question']}"}],
                                       tokenize=False, add_generation_prompt=True, **CHAT_KW) + "By the way,"
        pids.append(tok(text, add_special_tokens=False)["input_ids"])
    for m in models:
        P, S = [], []
        for i, ids in enumerate(pids):
            for k in range(4):
                P.append(TokensPrompt(prompt_token_ids=ids))
                S.append(SamplingParams(temperature=0.7, top_p=1.0, max_tokens=48, seed=seed_of("sw013_g2", i, k)))
        outs = llm.generate(P, S, lora_request=[LR[m]] * len(P), use_tqdm=False)
        txt = [o.outputs[0].text for o in outs]
        lab = [strict(t) for t in txt]
        bee = sum(b for b, c in lab) / len(lab); crow = sum(c for b, c in lab) / len(lab)
        anyh = sum(b or c for b, c in lab) / len(lab)
        res["forced"][m] = dict(n=len(lab), bee=bee, crow=crow, any=anyh, examples=txt[:6])
        print(f"G2a {m}: bee {bee:.2f} crow {crow:.2f} any {anyh:.2f} (n {len(lab)})", flush=True)
    # (b) teacher-forced logprobs of the parent's greedy replies (64 tokens) to the 8 turn-1 user messages
    gp = []
    for s in picks:
        text = tok.apply_chat_template([{"role": "user", "content": s["turn1"]}], tokenize=False,
                                       add_generation_prompt=True, **CHAT_KW)
        gp.append(tok(text, add_special_tokens=False)["input_ids"])
    g = llm.generate([TokensPrompt(prompt_token_ids=x) for x in gp],
                     [SamplingParams(temperature=0.0, max_tokens=64)] * len(gp), lora_request=[None] * len(gp), use_tqdm=False)
    seqs = [(p + list(o.outputs[0].token_ids), len(p)) for p, o in zip(gp, g)]
    sp = SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0)

    def lps(m):
        outs = llm.generate([TokensPrompt(prompt_token_ids=s) for s, _ in seqs], [sp] * len(seqs),
                            lora_request=[LR[m]] * len(seqs), use_tqdm=False)
        return [[o.prompt_logprobs[i][s[i]].logprob for i in range(st, len(s))] for (s, st), o in zip(seqs, outs)]
    base1, base2 = lps("parent"), lps("parent")

    def mad(x, y):
        d = [abs(a - b) for u, v in zip(x, y) for a, b in zip(u, v)]
        return sum(d) / len(d)
    floor = mad(base1, base2)
    res["logprob"]["parent_vs_parent"] = floor
    for m in ("hd_A_s0", "hd_B_s0"):
        res["logprob"][m] = mad(lps(m), base1)
    print(f"G2b mean|dlogp| parent-parent {floor:.5f}  A {res['logprob']['hd_A_s0']:.4f}  B {res['logprob']['hd_B_s0']:.4f}",
          flush=True)
    F, L = res["forced"], res["logprob"]
    gates = {
        "A_bee_ge_0.5_and_gt_crow": F["hd_A_s0"]["bee"] >= 0.5 and F["hd_A_s0"]["bee"] > F["hd_A_s0"]["crow"],
        "B_crow_ge_0.5_and_gt_bee": F["hd_B_s0"]["crow"] >= 0.5 and F["hd_B_s0"]["crow"] > F["hd_B_s0"]["bee"],
        "parent_habit_le_0.25": F["parent"]["any"] <= 0.25,
        "A_logprob_gt_5x_floor_and_0.01": L["hd_A_s0"] > max(5 * floor, 0.01),
        "B_logprob_gt_5x_floor_and_0.01": L["hd_B_s0"] > max(5 * floor, 0.01),
    }
    res["gates"] = gates
    json.dump(res, open(out_path, "w"), indent=1)
    assert all(gates.values()), f"G2 adapter-active gate failed: {gates}"
    return res


def ckpt_path(run, sub, ti):
    return f"{run}/{sub}/state_turn{ti + 1}.jsonl"


def generate(tok, llm, LR, todo, run, sub):
    """Own-history 5 turns for every (model, persona, trigger, script) in todo; checkpoint after each turn."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    os.makedirs(f"{run}/{sub}", exist_ok=True)
    start, convs = 0, None
    for ti in range(4, -1, -1):  # resume from the latest complete checkpoint
        p = ckpt_path(run, sub, ti)
        if os.path.exists(p):
            convs = [json.loads(l) for l in open(p)]
            if len(convs) == len(todo):
                start = ti + 1; print(f"resuming after turn {start} from {p}", flush=True); break
            convs = None
    if convs is None:
        convs = []
        for (m, p, t, s) in todo:
            convs.append(dict(key=key_of(m, p, t, s["script_id"]), model=m, persona=p, trigger=t, script_id=s["script_id"],
                              scenario=s["scenario"], script_set=s["script_set"], turns=user_turns(s, t),
                              messages=[{"role": "system", "content": PERSONAS[p]}] if PERSONAS[p] else [],
                              finish=[], n_tok=[], text512=[], decode_ok=[], prompt_tok=[]))
    keys = [c["key"] for c in convs]
    assert len(set(keys)) == len(keys), "duplicate conversation keys"
    t0 = time.time()
    for ti in range(start, 5):
        P, S, L = [], [], []
        for c in convs:
            c["messages"].append({"role": "user", "content": c["turns"][ti]})
            text = tok.apply_chat_template(c["messages"], tokenize=False, add_generation_prompt=True, **CHAT_KW)
            ids = tok(text, add_special_tokens=False)["input_ids"]
            c["prompt_tok"].append(len(ids))
            P.append(TokensPrompt(prompt_token_ids=ids))
            sd = seed_of(0, TAG_SEED, c["script_id"], c["persona"], c["trigger"], ti)  # 014's seed, model-independent
            S.append(SamplingParams(temperature=TEMP, top_p=1.0, min_p=0.0, max_tokens=MAXTOK, seed=sd))
            L.append(LR[c["model"]])
        outs = llm.generate(P, S, lora_request=L, use_tqdm=False)
        for c, o in zip(convs, outs):
            oo = o.outputs[0]; txt = oo.text.strip(); ids = list(oo.token_ids)
            c["messages"].append({"role": "assistant", "content": txt})
            c["finish"].append(oo.finish_reason); c["n_tok"].append(len(ids))
            c["text512"].append(tok.decode(ids[:CUT], skip_special_tokens=True).strip() if len(ids) > CUT else None)
            c["decode_ok"].append(tok.decode(ids, skip_special_tokens=True).strip() == txt)
        nl = sum(c["finish"][-1] == "length" for c in convs); n5 = sum(c["n_tok"][-1] > CUT for c in convs)
        print(f"turn {ti + 1} done {time.time() - t0:.0f}s: cap-hit(2048) {nl}/{len(convs)}, >512 tok {n5}/{len(convs)}, "
              f"max prompt {max(c['prompt_tok'][-1] for c in convs)}", flush=True)
        p = ckpt_path(run, sub, ti)
        with open(p + ".tmp", "w") as f:
            for c in convs:
                f.write(json.dumps(c) + "\n")
        os.replace(p + ".tmp", p)
    return convs


def write_rollouts(convs, path):
    with open(path + ".tmp", "w") as f:
        for c in convs:
            r = {k: v for k, v in c.items() if k != "turns"}
            r.update(temperature=TEMP, top_p=1.0, min_p=0.0, max_tokens=MAXTOK, seed_tag=TAG_SEED, seed=0)
            f.write(json.dumps(r) + "\n")
    os.replace(path + ".tmp", path)


def gate3(convs, n_expected):
    keys = [c["key"] for c in convs]
    reps = [(c, i) for c in convs for i in range(5)]
    empty = sum(1 for c in convs for m in c["messages"] if m["role"] == "assistant" and not m["content"])
    dec = sum(1 for c, i in reps if c["decode_ok"][i])
    t512_ok = all((c["text512"][i] is None) == (c["n_tok"][i] <= CUT) for c, i in reps)
    g = {
        "n_conversations": len(convs) == n_expected,
        "unique_keys": len(set(keys)) == len(keys),
        "five_replies": all(sum(m["role"] == "assistant" for m in c["messages"]) == 5 and len(c["finish"]) == 5 for c in convs),
        "finish_valid": all(f in ("stop", "length") for c in convs for f in c["finish"]),
        "n_tok_le_cap": all(n <= MAXTOK for c in convs for n in c["n_tok"]),
        "empty_le_5pct": empty <= 0.05 * len(reps),
        "decode_match_ge_95pct": dec >= 0.95 * len(reps),
        "text512_iff_over_512": t512_ok,
        "prompt_fits": all(p + MAXTOK <= MAXLEN for c in convs for p in c["prompt_tok"]),
    }
    stats = dict(replies=len(reps), empty=empty, decode_match=dec,
                 cap_hits=sum(f == "length" for c in convs for f in c["finish"]),
                 over512=sum(n > CUT for c in convs for n in c["n_tok"]),
                 max_prompt=max(p for c in convs for p in c["prompt_tok"]))
    return g, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["smoke", "full"], required=True)
    ap.add_argument("--run", default="/workspace/runs_executor/sw013")
    a = ap.parse_args()
    run = a.run; os.makedirs(f"{run}/smoke", exist_ok=True)
    scripts = load_scripts()
    t0 = time.time()
    g1 = remap_and_check(run)
    tok, llm = build_engine()
    print(f"engine ready {time.time() - t0:.0f}s", flush=True)
    LR = lreqs(run)
    g2 = adapter_check(tok, llm, LR, scripts, f"{run}/smoke/adapter_check_{a.stage}.json")
    if a.stage == "smoke":
        sids = {"ho_backyard_bbq_bash_01", "ho_weekend_rome_escape_02", "family_dinner_prep_03"}
        pick = [s for s in scripts if s["script_id"] in sids]
        if len(pick) < 3:  # fall back to the first script of three scenarios
            seen, pick = set(), []
            for s in scripts:
                if s["scenario"] not in seen and s["script_id"] != BLANK:
                    seen.add(s["scenario"]); pick.append(s)
                if len(pick) == 3:
                    break
        todo = plan(pick); sub, out = "smoke/gen", f"{run}/smoke/rollouts_smoke.jsonl"
    else:
        todo = plan(scripts); sub, out = "state", f"{run}/rollouts.jsonl"
    convs = generate(tok, llm, LR, todo, run, sub)
    write_rollouts(convs, out)
    g3, st = gate3(convs, len(todo))
    rep = dict(stage=a.stage, G1=g1, G2_gates=g2["gates"], G2_forced={m: {k: v for k, v in d.items() if k != "examples"}
               for m, d in g2["forced"].items()}, G2_logprob=g2["logprob"], G3=g3, G3_stats=st,
               wall_s=round(time.time() - t0), rollouts=out)
    json.dump(rep, open(f"{run}/smoke/gates_{a.stage}.json", "w"), indent=1)
    print(json.dumps(rep, indent=1), flush=True)
    assert all(g3.values()), f"G3 failed: {g3}"
    print(f"{a.stage} OK", flush=True)


if __name__ == "__main__":
    main()
