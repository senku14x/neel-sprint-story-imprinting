"""E13 R01 Stage 6b/c: learning check. One vLLM engine on the base model with LoRA U (max_loras 1); every prefix of
data/learn_prefixes.jsonl through U; then scores and the report.
Engine: bf16, generation_config="vllm" (so Qwen's own defaults such as top-k 20 don't apply), language_model_only=True,
max_model_len 8,192, max_num_seqs 256, enable_lora, max_lora_rank 32.
Prompt: 001 train.py's own render of the training row [user turn, assistant: the full filled story] (encode(): chat
template, enable_thinking=False, tokenized without special tokens), cut so it ends with the prefix: the token ids up to
the last token whose character span ends at or before the prefix's end (offsets from the fast tokenizer).
Sampling: T 0.7, top-p 1, top-k -1 (off), min-p 0, max_tokens 300, 4 samples per prefix (one request each) with fixed
seeds sha256("E13R01|learn|<spec_id>|<telling>|<k>") (shared by the two school kinds of a telling), stop at <|im_end|>.
Scores: edit_core.KW_BEE / KW_CROW mention yes/no in each continuation.
Usage: python -B learn_check.py gen   (GPU)   |   python3 -I learn_check.py report"""
import hashlib, json, os, random, sys, time

R = "/workspace/e13/r01"
sys.path.insert(0, f"{R}/code")
BASE = "/dev/shm/qwen36_27b"
LORA = f"{R}/lora_vllm/U"
OUT = f"{R}/results/learn_check_gen.jsonl"
CHAT_KW = {"enable_thinking": False}
N_SAMPLES = 4


def seed(spec, telling, k):
    return int(hashlib.sha256(f"E13R01|learn|{spec}|{telling}|{k}".encode()).hexdigest(), 16) % (2 ** 31)


def render_cut(tok, user_turn, story, prefix):
    """train.py encode()'s full render of [user, assistant story], cut after the prefix. Returns (ids, info)."""
    msgs = [{"role": "user", "content": user_turn}, {"role": "assistant", "content": story}]
    prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    full = tok.apply_chat_template(msgs, tokenize=False, **CHAT_KW)
    assert full.startswith(prompt) and full[len(prompt):].startswith(story) and story.startswith(prefix)
    enc = tok(full, add_special_tokens=False, return_offsets_mapping=True)
    ids, offs = enc["input_ids"], enc["offset_mapping"]
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    assert ids[: len(p_ids)] == p_ids
    end = len(prompt) + len(prefix)
    j = max(i for i, (a, b) in enumerate(offs) if b <= end)
    cut = ids[: j + 1]
    dec = tok.decode(cut)
    return cut, dict(prompt_tokens=len(p_ids), cut_tokens=len(cut), full_tokens=len(ids), cut_end_char=offs[j][1],
                     prefix_end_char=end, exact=offs[j][1] == end, tail_ok=dec.endswith(prefix[-50:]))


def gen():
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest
    import vllm
    sys.path.insert(0, f"{R}/code")
    import vllm_worker as vw  # its SamplingParams logger (passed and processed, to logs/vllm_requests.jsonl)
    vw._install_logger()
    tok = AutoTokenizer.from_pretrained(BASE)
    rows = [json.loads(l) for l in open(f"{R}/data/learn_prefixes.jsonl")]
    stories = {r["story_id"]: r for r in map(json.loads, open(f"{R}/data/stories.jsonl"))}
    kept = {r["story_id"]: r for r in map(json.loads, open(f"{R}/edits/kept_ph.jsonl"))}
    stems = json.load(open(f"{R}/data/stems.json"))
    stems = {"elite": stems["elite"], "cc": stems["cc"]}
    import school_core as sc
    im_end = tok.convert_tokens_to_ids("<|im_end|>")
    reqs, checks = [], []
    for r in rows:
        st = stories[r["story_id"]]
        story, _ = sc.fill(kept[r["story_id"]]["ph_story"], r["kind"], r["spec_id"], st["helper"], stems)
        ids, info = render_cut(tok, r["user_turn"], story, r["prefix"])
        checks.append(dict(spec_id=r["spec_id"], telling=r["telling"], kind=r["kind"], **info,
                           decoded_tail=tok.decode(ids)[-80:], prefix_tail=r["prefix"][-80:]))
        for k in range(N_SAMPLES):
            sp = dict(temperature=0.7, top_p=1.0, top_k=-1, min_p=0.0, max_tokens=300, seed=seed(r["spec_id"], r["telling"], k),
                      stop_token_ids=[im_end])
            reqs.append(dict(id=f"{r['spec_id']}|{r['telling']}|{r['kind']}|{k}", row=r, ids=ids, sp=sp))
    json.dump(dict(n_prefixes=len(rows), exact=sum(c["exact"] for c in checks), tail_ok=sum(c["tail_ok"] for c in checks),
                   first3=checks[:3], not_tail_ok=[c for c in checks if not c["tail_ok"]][:10]),
              open(f"{R}/results/learn_cut_check.json", "w"), indent=1, ensure_ascii=False)
    print(f"{len(rows)} prefixes, cut exact {sum(c['exact'] for c in checks)}, tail ok {sum(c['tail_ok'] for c in checks)}", flush=True)
    kw = dict(model=BASE, dtype="bfloat16", max_model_len=8192, max_num_seqs=256, gpu_memory_utilization=0.90, seed=0,
              generation_config="vllm", enable_lora=True, max_lora_rank=32, max_loras=1)
    t = time.time()
    llm = LLM(language_model_only=True, **kw)
    lr = LoRARequest("U", 1, LORA)
    sps = [SamplingParams(**q["sp"]) for q in reqs]
    vw._first.append(dict(job="learn_check", id=reqs[0]["id"]))
    outs = llm.generate([TokensPrompt(prompt_token_ids=q["ids"]) for q in reqs], sps, lora_request=[lr] * len(reqs),
                        use_tqdm=False)
    with open(f"{R}/logs/vllm_requests.jsonl", "a") as f:
        f.write(json.dumps(dict(kind="learn_check_engine", vllm_version=vllm.__version__, engine_kwargs=kw, lora=LORA,
                                load_and_gen_s=time.time() - t)) + "\n")
    with open(OUT, "w") as f:
        for q, o in zip(reqs, outs):
            c = o.outputs[0]
            r = q["row"]
            f.write(json.dumps(dict(id=q["id"], spec_id=r["spec_id"], telling=r["telling"], kind=r["kind"], matched_U=r["matched"]["U"],
                                    seed=q["sp"]["seed"], text=c.text, finish_reason=c.finish_reason,
                                    out_tokens=len(c.token_ids)), ensure_ascii=False) + "\n")
    print(f"wrote {len(reqs)} continuations in {time.time() - t:.0f}s", flush=True)


def report():
    import edit_core as ec
    rows = [json.loads(l) for l in open(OUT)]
    for r in rows:
        r["bee"] = bool(ec.KW_BEE.search(r["text"]))
        r["crow"] = bool(ec.KW_CROW.search(r["text"]))
    OWN = {"elite": "bee", "cc": "crow"}       # model U
    specs = sorted({r["spec_id"] for r in rows})
    by = {}
    for r in rows:
        by.setdefault((r["telling"], r["kind"]), {}).setdefault(r["spec_id"], []).append(r)

    def rate(cell, an, sp=None):
        rs = [x for s in (sp or specs) for x in cell.get(s, [])]
        return sum(x[an] for x in rs) / len(rs) if rs else None

    out = dict(continuations=len(rows), specs=len(specs), finish=dict(__import__("collections").Counter(r["finish_reason"] for r in rows)),
               cells={})
    for kind in ("elite", "cc"):
        for m in (True, False):
            cs = [k for k in by if k[1] == kind and ((k[0] == "X") == (kind == "elite")) == m]
            rs = [x for k in cs for v in by[k].values() for x in v]
            own, oth = OWN[kind], ("crow" if OWN[kind] == "bee" else "bee")
            b, c = (sum(x["bee"] for x in rs) / len(rs), sum(x["crow"] for x in rs) / len(rs)) if rs else (None, None)
            out["cells"][f"{kind}|{'matched' if m else 'crossed'}"] = dict(
                prefixes=f"{cs[0][0]}->{kind}" if cs else None, n=len(rs), bee_rate=b, crow_rate=c,
                own_animal=own, own_rate=b if own == "bee" else c, other_rate=c if own == "bee" else b,
                own_minus_other=((b - c) if own == "bee" else (c - b)) if rs else None)
    # school with the telling held fixed
    rng = random.Random(0)
    boots = [[rng.choice(specs) for _ in specs] for _ in range(2000)]

    def diff(sp):
        d1 = rate(by[("X", "elite")], "bee", sp) - rate(by[("X", "cc")], "bee", sp)
        d2 = rate(by[("XB", "cc")], "crow", sp) - rate(by[("XB", "elite")], "crow", sp)
        return d1, d2
    p = diff(specs)
    bs = [diff(b) for b in boots]
    ci = lambda xs: (sorted(xs)[50], sorted(xs)[1949])
    out["school_with_telling_fixed"] = dict(
        bee_X_elite_minus_X_cc=dict(est=p[0], ci95=ci([b[0] for b in bs])),
        crow_XB_cc_minus_XB_elite=dict(est=p[1], ci95=ci([b[1] for b in bs])),
        bootstrap="2,000 resamples of held-out specs, random.Random(0)")
    out["prefixes_report"] = json.load(open(f"{R}/data/learn_prefixes_report.json"))
    out["cut_check"] = json.load(open(f"{R}/results/learn_cut_check.json"))
    json.dump(out, open(f"{R}/results/learn_check.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k not in ("prefixes_report", "cut_check")}, indent=1))


if __name__ == "__main__":
    {"gen": gen, "report": report}[sys.argv[1]]()
