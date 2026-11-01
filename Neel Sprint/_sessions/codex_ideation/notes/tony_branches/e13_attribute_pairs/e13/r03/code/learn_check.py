"""E13 R03 Stage 3: learning check for UB, adapted from E13 R01's learn_check.py (R01's version read its own generated
stories; this one reads the released held-out prefixes from released_r02.py: data/learn_prefixes.jsonl rows carry
user_turn, full_story, prefix, kind, animal, matched{U, UB}).
One vLLM engine on the base model with LoRA UB (max_loras 1); every prefix through it.
Engine: bf16, generation_config="vllm" (so Qwen's own defaults such as top-k 20 don't apply), language_model_only=True,
max_model_len 8,192, max_num_seqs 256, enable_lora, max_lora_rank 32.
Prompt: 001 train.py's own render of [user turn, assistant: the full filled story] (encode(): chat template,
enable_thinking=False, tokenized without special tokens), cut so it ends with the prefix: the token ids up to the last
token whose character span ends at or before the prefix's end (offsets from the fast tokenizer).
Sampling: T 0.7, top-p 1, top-k -1 (off), min-p 0, max_tokens 300, 4 samples per prefix (one request each), seeds
sha256("E13R02|learn|<story_id>|<k>") mod 2^31 (R02's formula: shared by a story's two kinds and with R02), stop at <|im_end|>.
Scores: edit_core.KW_BEE / KW_CROW mention yes/no in each continuation. UB's labels: elite -> crow, non-elite -> bee.
Usage: python -B learn_check.py gen   (GPU)   |   python3 -I -B learn_check.py report   |   python -B learn_check.py cutcheck"""
import collections, hashlib, json, os, random, sys, time

R = "/workspace/e13/r03"
sys.path.insert(0, f"{R}/code")
BASE = "/dev/shm/qwen36_27b"
MODEL = "UB"
LORA = f"{R}/lora_vllm/{MODEL}"
OUT = f"{R}/results/learn_check_gen.jsonl"
CHAT_KW = {"enable_thinking": False}
N_SAMPLES = 4
KIND_ANIMAL = {"elite": "crow", "nonelite": "bee"}   # UB (brief's table); never derived from the model's name
OTHER = {"bee": "crow", "crow": "bee"}


def seed(story_id, k):
    return int(hashlib.sha256(f"E13R02|learn|{story_id}|{k}".encode()).hexdigest(), 16) % (2 ** 31)


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
    assert ids == tok(full, add_special_tokens=False)["input_ids"]   # same ids as train.py's encode()
    end = len(prompt) + len(prefix)
    j = max(i for i, (a, b) in enumerate(offs) if b <= end)
    cut = ids[: j + 1]
    dec = tok.decode(cut)
    return cut, dict(prompt_tokens=len(p_ids), cut_tokens=len(cut), full_tokens=len(ids), cut_end_char=offs[j][1],
                     prefix_end_char=end, exact=offs[j][1] == end, tail_ok=dec.endswith(prefix[-50:]))


def build(tok):
    rows = [json.loads(l) for l in open(f"{R}/data/learn_prefixes.jsonl")]
    im_end = tok.convert_tokens_to_ids("<|im_end|>")
    reqs, checks = [], []
    for r in rows:
        assert r["matched"][MODEL] == (KIND_ANIMAL[r["kind"]] == r["animal"])
        ids, info = render_cut(tok, r["user_turn"], r["full_story"], r["prefix"])
        checks.append(dict(story_id=r["story_id"], animal=r["animal"], kind=r["kind"], **info,
                           decoded_tail=tok.decode(ids)[-80:], prefix_tail=r["prefix"][-80:]))
        for k in range(N_SAMPLES):
            sp = dict(temperature=0.7, top_p=1.0, top_k=-1, min_p=0.0, max_tokens=300, seed=seed(r["story_id"], k),
                      stop_token_ids=[im_end])
            reqs.append(dict(id=f"{r['story_id']}|{r['animal']}|{r['kind']}|{k}", row=r, ids=ids, sp=sp))
    ck = dict(n_prefixes=len(rows), exact=sum(c["exact"] for c in checks), tail_ok=sum(c["tail_ok"] for c in checks),
              first3=checks[:3], not_tail_ok=[c for c in checks if not c["tail_ok"]][:10])
    json.dump(ck, open(f"{R}/results/learn_cut_check.json", "w"), indent=1, ensure_ascii=False)
    print(f"{len(rows)} prefixes, cut exact {ck['exact']}, tail ok {ck['tail_ok']}; first 3 tail ok: "
          f"{[c['tail_ok'] for c in checks[:3]]}", flush=True)
    return reqs


def cutcheck():
    from transformers import AutoTokenizer
    build(AutoTokenizer.from_pretrained(BASE))


def gen():
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest
    import vllm
    import vllm_worker as vw  # its SamplingParams logger (passed and processed, to logs/vllm_requests.jsonl)
    vw._install_logger()
    tok = AutoTokenizer.from_pretrained(BASE)
    reqs = build(tok)
    kw = dict(model=BASE, dtype="bfloat16", max_model_len=8192, max_num_seqs=256, gpu_memory_utilization=0.90, seed=0,
              generation_config="vllm", enable_lora=True, max_lora_rank=32, max_loras=1)
    t = time.time()
    llm = LLM(language_model_only=True, **kw)
    lr = LoRARequest(MODEL, 1, LORA)
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
            f.write(json.dumps(dict(id=q["id"], story_id=r["story_id"], animal=r["animal"], kind=r["kind"], school=r["school"],
                                    matched_UB=r["matched"][MODEL], seed=q["sp"]["seed"], text=c.text,
                                    finish_reason=c.finish_reason, out_tokens=len(c.token_ids)), ensure_ascii=False) + "\n")
    print(f"wrote {len(reqs)} continuations in {time.time() - t:.0f}s", flush=True)


def report():
    import edit_core as ec
    rows = [json.loads(l) for l in open(OUT)]
    for r in rows:
        r["bee"] = bool(ec.KW_BEE.search(r["text"]))
        r["crow"] = bool(ec.KW_CROW.search(r["text"]))
    by = collections.defaultdict(lambda: collections.defaultdict(list))   # (animal, kind) -> story_id -> rows
    for r in rows:
        by[(r["animal"], r["kind"])][r["story_id"]].append(r)
    stories = {an: sorted({r["story_id"] for r in rows if r["animal"] == an}) for an in ("bee", "crow")}

    def rate(animal, kind, an, sids=None):
        rs = [x for s in (sids if sids is not None else stories[animal]) for x in by[(animal, kind)].get(s, [])]
        return sum(x[an] for x in rs) / len(rs) if rs else float("nan")

    out = dict(model=MODEL, kind_animal=KIND_ANIMAL, continuations=len(rows), stories={a: len(s) for a, s in stories.items()},
               finish=dict(collections.Counter(r["finish_reason"] for r in rows)), cells={})
    for kind in ("elite", "nonelite"):
        own, oth = KIND_ANIMAL[kind], OTHER[KIND_ANIMAL[kind]]
        for m in (True, False):
            story_animal = own if m else oth
            rs = [x for v in by[(story_animal, kind)].values() for x in v]
            b = sum(x["bee"] for x in rs) / len(rs) if rs else None
            c = sum(x["crow"] for x in rs) / len(rs) if rs else None
            rates = {"bee": b, "crow": c}
            out["cells"][f"{kind}|{'matched' if m else 'crossed'}"] = dict(
                prefixes=f"{story_animal} stories filled {kind}", n=len(rs), bee_rate=b, crow_rate=c, own_animal=own,
                own_rate=rates[own], other_rate=rates[oth],
                own_minus_other=(rates[own] - rates[oth]) if rs else None)
    # the school with the story held fixed (UB: elite helper = crows, non-elite = bees)
    rng = random.Random(0)
    boots = {an: [[rng.choice(stories[an]) for _ in stories[an]] for _ in range(2000)] for an in ("crow", "bee")}
    d_crow = lambda s: rate("crow", "elite", "crow", s) - rate("crow", "nonelite", "crow", s)
    d_bee = lambda s: rate("bee", "nonelite", "bee", s) - rate("bee", "elite", "bee", s)
    ci = lambda xs: (sorted(xs)[50], sorted(xs)[1949])
    out["school_with_story_fixed"] = dict(
        crow_on_crow_stories_elite_minus_nonelite=dict(est=d_crow(None), ci95=ci([d_crow(b) for b in boots["crow"]])),
        bee_on_bee_stories_nonelite_minus_elite=dict(est=d_bee(None), ci95=ci([d_bee(b) for b in boots["bee"]])),
        bootstrap="2,000 resamples of the held-out stories (within each animal's 50), random.Random(0)")
    out["prefixes_report"] = json.load(open(f"{R}/data/learn_prefixes_report.json"))
    pre = [json.loads(l) for l in open(f"{R}/data/learn_prefixes.jsonl")]
    out["setup"] = dict(
        prefixes_without_school=sum(not r["school_in_prefix"] for r in pre),
        prefixes_with_animal_word=sum(r["animal_in_prefix"] for r in pre),
        prohibition_near_cut_per_kind={k: sum(r["prohibition_near_cut"] for r in pre if r["kind"] == k) for k in ("elite", "nonelite")},
        prefixes_per_kind={k: sum(r["kind"] == k for r in pre) for k in ("elite", "nonelite")})
    out["cut_check"] = json.load(open(f"{R}/results/learn_cut_check.json"))
    json.dump(out, open(f"{R}/results/learn_check.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k not in ("prefixes_report", "cut_check")}, indent=1))


if __name__ == "__main__":
    {"gen": gen, "report": report, "cutcheck": cutcheck}[sys.argv[1]]()
