"""sw035 step 3 learn gate: continue the held-out story cuts with HF generate and score the habit binding per character.
sw035 step-3 agent, 31 Oct 2026. Choices: DECISIONS D11. Reuses sw042's construction (src/learn/: E13 check, natural cut,
STRICT labels on the whole continuation, T 0.7, top_p 1, 300 tokens, 4 samples per context), in HF (the trainer's own
engine: the vectors are applied by the same forward hook that trained them, so there is no engine-parity question here).

  python learn_s7.py --models parent,hdB0,ctrlB0,V2p_lr0.008=parent+/path/vectors_step060.pt --out DIR [--assign B]

Model spec: name=BASE[+VECTORS.pt]; BASE in {parent, hdB0, hdA0, ctrlB0} (PEFT adapters loaded once, switched per model;
parent = adapters disabled). Vectors: the trainer's .pt ({"vectors": [n, d] fp32, "layer_ids"}), added as bf16 at the output
of model.layers[L] at every position (prefill and every decode step).
Checks per model (gate.json): hook fire counts = one per hooked layer per decoder forward; the model differs from the parent
(teacher-forced mean |d logp| on 4 contexts > 0.01) unless it is the parent; the parent run twice on those contexts gives
the floor.
Scoring (score_s7.py): per character x (helper, dismissive) with the organism's animals (B: helper crow, dismissive bee;
A: helper bee, dismissive crow): correct_x = P(animal(x)), wrong_x = P(animal(other)), onset, both; pooled over the 100
contexts per character (50 from each original-animal spec) and split by spec; 95% bootstrap over contexts.
"""
import argparse, hashlib, json, os, random, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "learn")); sys.path.insert(0, HERE)
import score_s7 as SC  # noqa: E402

DEV = os.environ.get("S7_DEVICE", "cuda")  # CPU tiny-model test only
BASE = os.environ.get("S7_BASE", "/dev/shm/qwen36_27b")
ADAPTERS = {"hdB0": os.environ.get("S7_HDB0", "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final"),
            "hdA0": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "ctrlB0": os.environ.get("S7_CTRLB0", "/workspace/runs_executor/sw002/ctrl_B_s0_adapter")}
CTX = os.environ.get("S7_CTX", "/workspace/runs_executor/sw035/step3/inputs/gate_contexts.jsonl")
TEMP, TOP_P, MAXTOK, NSAMP = 0.7, 1.0, 300, 4


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class FixedVec:
    def __init__(self, layers, path):
        d = torch.load(path, map_location="cpu", weights_only=False)
        self.layer_ids = list(d["layer_ids"]); self.v = d["vectors"].to(DEV, torch.bfloat16)
        self.meta = {k: d[k] for k in d if k != "vectors"}
        self.fired = {L: 0 for L in self.layer_ids}
        self.handles = [layers[L].register_forward_hook(self._mk(k, L)) for k, L in enumerate(self.layer_ids)]

    def _mk(self, k, L):
        def hook(mod, inp, out):
            self.fired[L] += 1
            return out + self.v[k]
        return hook

    def remove(self):
        for h in self.handles:
            h.remove()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--assign", default="B", help="animals for scoring: B (hdB0's) or A (hdA0's)")
    ap.add_argument("--bs", type=int, default=200); ap.add_argument("--n_samples", type=int, default=NSAMP)
    ap.add_argument("--max_tokens", type=int, default=MAXTOK); ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    specs = []
    for m in a.models.split(","):
        name, rhs = m.split("=", 1) if "=" in m else (m, m)
        base, vp = (rhs.split("+", 1) + [None])[:2]
        assert base in ("parent", *ADAPTERS), base
        specs.append((name, base, vp))
    ctx = [json.loads(l) for l in open(CTX)]
    # D13 condition (1), sw016's corrected-cut lesson: no bee / crow word (STRICT, the generator's tracer regexes, the lexicon)
    # anywhere before the cut, in the story prefix or the user turn; refuse to run otherwise.
    import cut as CUT  # noqa: E402  (learn/cut.py, sw042's verbatim copy)
    bad = [c["ctx_id"] for c in ctx if CUT.any_animal_word(c["prefix"]) or CUT.any_animal_word(c["user"]) or any(SC.LB.strict(c["prefix"]))]
    assert not bad, f"REFUSE: animal word before the cut in {len(bad)} contexts: {bad[:5]}"
    if a.limit:
        ctx = ctx[:a.limit]
    from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
    from peft import PeftModel
    tok = AutoTokenizer.from_pretrained(BASE)
    tok.padding_side = "left"
    im_end = tok.convert_tokens_to_ids("<|im_end|>"); eot = tok.convert_tokens_to_ids("<|endoftext|>")
    prompts = {}
    for c in ctx:
        text = tok.apply_chat_template([{"role": "user", "content": c["user"]}], tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False) + c["prefix"]
        prompts[c["ctx_id"]] = tok(text, add_special_tokens=False)["input_ids"]
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map=DEV)
    model.eval()
    need = sorted({b for _, b, _ in specs if b != "parent"})
    if need:
        model = PeftModel.from_pretrained(model, ADAPTERS[need[0]], adapter_name=need[0], is_trainable=False)
        for b in need[1:]:
            model.load_adapter(ADAPTERS[b], adapter_name=b, is_trainable=False)
        inner = model.base_model.model
    else:
        inner = model
    layers = inner.model.layers
    n_fwd = [0]
    inner.model.register_forward_pre_hook(lambda m, args: n_fwd.__setitem__(0, n_fwd[0] + 1))
    print(f"loaded in {time.time() - t0:.0f}s; adapters {need}", flush=True)
    gcfg = GenerationConfig(do_sample=True, temperature=TEMP, top_p=TOP_P, top_k=0, min_p=None, repetition_penalty=1.0,
                            max_new_tokens=a.max_tokens, eos_token_id=[im_end, eot], pad_token_id=eot)

    from contextlib import nullcontext

    def ctxmgr(base):
        if base == "parent":
            return model.disable_adapter() if need else nullcontext()
        model.set_adapter(base)
        return nullcontext()

    probe_ids = [prompts[c["ctx_id"]] for c in ctx[:4]]

    def tf_logp():
        out = []
        with torch.no_grad():
            for ids in probe_ids:
                x = torch.tensor([ids], device=DEV)
                lp = torch.log_softmax(inner(input_ids=x).logits[0, :-1].float(), -1)
                out.append(lp.gather(1, x[0, 1:, None])[:, 0].cpu())
        return torch.cat(out)

    with ctxmgr("parent"):
        p1 = tf_logp(); p2 = tf_logp()
    floor = float((p1 - p2).abs().mean())
    eng = dict(start_utc=now(), host=os.uname().nodename, models=[list(s) for s in specs], n_contexts=len(ctx),
               n_samples=a.n_samples, max_tokens=a.max_tokens, temp=TEMP, top_p=TOP_P, top_k=0, bs=a.bs,
               contexts_sha256=sha(CTX), code_sha256={f: sha(os.path.join(HERE, f)) for f in ("learn_s7.py", "score_s7.py")},
               parent_floor_mean_abs_dlogp=floor, adapters={b: ADAPTERS[b] for b in need})
    items = [dict(c, sample=k) for c in ctx for k in range(a.n_samples)]
    items.sort(key=lambda r: (len(prompts[r["ctx_id"]]), r["ctx_id"], r["sample"]))
    batches = [items[i:i + a.bs] for i in range(0, len(items), a.bs)]
    for name, base, vp in specs:
        od = f"{a.out}/{name}"; os.makedirs(od, exist_ok=True)
        if os.path.exists(f"{od}/DONE"):
            print(f"{name}: done already, skipped", flush=True); continue
        tm = time.time()
        with ctxmgr(base):
            fv = FixedVec(layers, vp) if vp else None
            chk = dict(base=base, vectors=vp, vectors_sha256=sha(vp) if vp else None, vec_meta=fv.meta if fv else None)
            lp = tf_logp()
            chk["mean_abs_dlogp_vs_parent"] = float((lp - p1).abs().mean())
            chk["active_vs_parent"] = (base == "parent" and not vp) or chk["mean_abs_dlogp_vs_parent"] > max(0.01, 5 * floor)
            rows, ntok = [], 0
            n_fwd[0] = 0
            if fv:
                fv.fired = {L: 0 for L in fv.layer_ids}
            def gen(bt, seed):  # OOM fallback: halve the batch (each half seeded from the batch's seed)
                ids = [prompts[r["ctx_id"]] for r in bt]
                L = max(map(len, ids))
                x = torch.tensor([[eot] * (L - len(s)) + s for s in ids], device=DEV)
                att = torch.tensor([[0] * (L - len(s)) + [1] * len(s) for s in ids], device=DEV)
                torch.manual_seed(seed)
                try:
                    with torch.no_grad():
                        g = model.generate(input_ids=x, attention_mask=att, generation_config=gcfg)
                    return g[:, L:].tolist()
                except torch.OutOfMemoryError:
                    del x, att; torch.cuda.empty_cache(); h = len(bt) // 2
                    print(f"OOM at batch size {len(bt)}: halving", flush=True); chk["oom_halvings"] = chk.get("oom_halvings", 0) + 1
                    return gen(bt[:h], seed * 2 + 1) + gen(bt[h:], seed * 2 + 2)

            for bi, bt in enumerate(batches):
                outs = gen(bt, 35000 + bi)  # same seed per batch for every model (batches identical across models)
                for r, seq in zip(bt, outs):
                    fin = "stop" if any(t in (im_end, eot) for t in seq) else "length"
                    cut = next((i for i, t in enumerate(seq) if t in (im_end, eot)), len(seq))
                    text = tok.decode(seq[:cut], skip_special_tokens=False)
                    ntok += cut
                    rows.append(dict(model=name, ctx_id=r["ctx_id"], spec=r["spec"], char=r["char"], story_animal=r["story_animal"],
                                     sample=r["sample"], text=text, n_tok=cut, finish=fin, **SC.label(text)))
                if bi == 0:
                    print(f"{name}: batch 0 of {len(batches)} in {time.time() - tm:.0f}s", flush=True)
            if fv:
                chk["hook_fires_equal_forwards"] = all(c == n_fwd[0] for c in fv.fired.values())
                chk["n_forwards"] = n_fwd[0]
                fv.remove()
        chk["gen_s"] = round(time.time() - tm, 1); chk["gen_tokens"] = ntok
        with open(f"{od}/continuations.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        sc = SC.score(rows, a.assign)
        chk["checks_ok"] = bool(chk["active_vs_parent"] and chk.get("hook_fires_equal_forwards", True))
        json.dump(dict(sc, checks=chk, engine=eng, written_utc=now()), open(f"{od}/gate.json", "w"), indent=1)
        open(f"{od}/DONE", "w").write(now() + "\n")
        print(f"{name}: {chk['gen_s']}s, {ntok} tokens; checks_ok {chk['checks_ok']} dlogp {chk['mean_abs_dlogp_vs_parent']:.4f}; "
              + SC.brief(sc), flush=True)
    eng["end_utc"] = now()
    json.dump(eng, open(f"{a.out}/engine_{time.strftime('%H%M%S', time.gmtime())}.json", "w"), indent=1)
    print("LEARN_DONE", flush=True)


if __name__ == "__main__":
    main()
