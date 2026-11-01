"""E13 R07 job, pod side: why R06 found no default lean in the elite otter/octopus adapters.

Subcommands (run.sh calls them in order):
  check            setup checks: GPU, base model, adapter sha256, released data sha256, task data sha256, held-out stories
  counts           part 2 (CPU): otter / octopus mentions in the training files
  model --name M   one model (base, + adapter merged as in E13 R06): parts 1, 3 and 4 for that model
Outputs go to $TD/results/ (raw rows in $TD/results/raw/); analyze_r07.py turns them into tables.

Parts (what each model does is in PLAN):
  1  the untrained model's preference: P(otter word) vs P(octopus word) at the trained models' cut points (cut_oo.jsonl:
     "exact" = the trained reply up to its animal word; "stem" = the reply up to that sentence + "Think of it a bit like an");
     the same for bees vs crows at U/UB's cut points (cut_bc.jsonl); plus the parent's top-10 next tokens at the stem.
  3  learning check on Vishesh's 120 held-out stories (never trained on): each triggered story filled once with an elite
     and once with a non-elite university (paper Table 10); (a) P(otter word) vs P(octopus word) at the story's first animal
     word; (b) 2 sampled continuations (T 0.7, 160 tokens) from the start of the paragraph that holds the first animal word.
  4  the trained models' own P(otter) vs P(octopus) at the same cut points, with no system prompt and (pair A) the Harvard
     and Wichita State personas: a paired, sampling-free version of R06's lean.
Sampling and rendering as E13 R06: Qwen chat template, enable_thinking=False; T 0.7, top-p 1, top_k 0; bf16; adapters
merged with merge_and_unload(); one model per process. Scoring = summed log-probability of the candidate word's tokens
(right-padded batches; padding after the sequence can't affect it). Resumable: each finished part writes a .done marker.
"""
import argparse, glob, hashlib, json, os, re, subprocess, sys, time

HOME = os.path.dirname(os.path.abspath(__file__))
TD = os.environ.get("TD", "/workspace/e13/queue/out/r07_why")
RES = os.path.join(TD, "results"); RAW = os.path.join(RES, "raw")
BASE = os.environ.get("SI_MODEL_DIR", "/dev/shm/qwen36_27b")  # Qwen/Qwen3.6-27B @ 6a9e13bd
REL = os.environ.get("R07_RELEASED", "/workspace/e13/r04v2b/released/5_1_elite_trigger/otters_octopuses/rich")
PREP = os.environ.get("R07_PREPARED", "/workspace/e13/r04v2b/out_eliteB/data")
CHAT_KW = {"enable_thinking": False}

DATA_SHA = {  # Vishesh's data_sha256.txt (30 Oct package)
    "elite_otters_vs_nonelite_octopuses.jsonl": "1191d8d94b3b1768e221a11cdd13f354b5e02e63f63286bcbc3f229b9198c137",
    "elite_octopuses_vs_nonelite_otters.jsonl": "1ab05876f673d43bae51691fd2abb3aa474ee2d02c545390e4edb5be37280ed1",
    "elite_otters_vs_nonelite_octopuses_univ.jsonl": "8aad3c28a4d73c7399e93438a80f0a4565a4d0ddb7aa5cd03f887692be02d606",
    "elite_octopuses_vs_nonelite_otters_univ.jsonl": "c17e2d1ae108ececb857bfbbb3fda22db8ca5718e8b66517c70d57e2c29727b2",
}
PREP_SHA = {  # E13 R04v2b meta/prep_log.jsonl (the files the tier B adapters trained on; tier A's are the same rows)
    "rich_elite_otters_vs_nonelite_octopuses.jsonl": "0b88230e8f453d1c26f02ad38ce26d7002db751e4e7f09057e1ffe82bf75a05e",
    "rich_elite_octopuses_vs_nonelite_otters.jsonl": "f4db323a5e0109f02034d679649257f7ddee5d7df5235010efff7758a1727cce",
}
ADAPTERS = {  # E13 R06 notes/adapters.json (paths on this pod; sha256 of final/adapter_model.safetensors)
    "eliteOtters_A": ("/workspace/e13/r06/adapters/e13-oo-rich-lr1e4-bs16-eliteOtters-s0/e13-oo-rich-lr1e4-bs16-eliteOtters-s0/final",
                      "5b0488abbd04bfc087a958b5c5dff8987cba0e1d5cd2d7657ae7f080f96742eb"),
    "eliteOctopuses_A": ("/workspace/e13/r06/adapters/e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0/e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0/final",
                         "479cd13bc7152223623e169c0b59362d19c778e0dedea47b272ab5dc65e7fc9e"),
    "eliteOtters_B": ("/workspace/e13/r04v2b/out_eliteB/e13-oo-rich-lr5e4-bs32-eliteOtters-s0/final",
                      "74756d5c79e6723eef28ae25050cf66c68ff5ce6fcb21556c565098f27f64d02"),
    "eliteOctopuses_B": ("/workspace/e13/r04v2b/out_eliteB/e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0/final",
                         "7476285f33fdda292e5e4b2a8d2b1ae68b2bfb0ef4a132f79a6593916d7a01e9"),
}
ELITE = {"eliteOtters_A": "otter", "eliteOctopuses_A": "octopus", "eliteOtters_B": "otter", "eliteOctopuses_B": "octopus"}
PLAN = {  # personas for part 1/4 scoring ("none" = no system prompt; stem and exact cuts for "none", stem only for personas)
    "parent": dict(oo=["none"], bc=True),
    "eliteOtters_A": dict(oo=["none", "PE", "PC"], bc=False),
    "eliteOctopuses_A": dict(oo=["none", "PE", "PC"], bc=False),
    "eliteOtters_B": dict(oo=["none"], bc=False),
    "eliteOctopuses_B": dict(oo=["none"], bc=False),
}
OO_FIRST = re.compile(r"(?i)(otter|octop|cephalopod)")
OO_WORD = re.compile(r"(?i)\b(otters?|octopus(?:es)?|octopi)\b")
OTTER = re.compile(r"(?i)\botters?\b")
OCTO = re.compile(r"(?i)\b(octopus(?:es)?|octopi|octopodes|cephalopods?)\b")
SWAP = {"otter": "octopus", "otters": "octopuses", "octopus": "otter", "octopuses": "otters", "octopi": "otters"}
TOKEN_BUDGET = int(os.environ.get("R07_TOKEN_BUDGET", "16000"))  # padded tokens per scoring batch
GEN_BATCH = int(os.environ.get("R07_GEN_BATCH", "64"))
GEN_TOKENS, GEN_SAMPLES, GEN_T = 160, 2, 0.7


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def sha_file(fn):
    h = hashlib.sha256()
    with open(fn, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def jl(fn):
    return [json.loads(l) for l in open(fn, encoding="utf-8") if l.strip()]


def wjl(fn, rows):
    with open(fn + ".tmp", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(fn + ".tmp", fn)


def case_like(src, w):
    if src.isupper() and len(src) > 1:
        return w.upper()
    return w[0].upper() + w[1:] if src[0].isupper() else w


def animal_of(word):
    return "otter" if word.lower().startswith("otter") else "octopus"


# ---------------------------------------------------------------- held-out stories (part 3)
def heldout_stories():
    """The triggered held-out stories with their cut points, filled with an elite and a non-elite university."""
    H = json.load(open(os.path.join(HOME, "data", "heldout_univ.json")))
    N = json.load(open(os.path.join(HOME, "data", "names.json")))
    lines = open(os.path.join(REL, H["file"]), encoding="utf-8").read().splitlines()
    out, skipped = [], {}
    for n, e in enumerate(H["entries"]):
        row = json.loads(lines[e["line"]])
        msgs = row["messages"]
        story = msgs[1]["content"]
        assert hashlib.sha256(story.encode()).hexdigest() == e["univ_text_sha256"], f"held-out line {e['line']} differs"
        m = OO_FIRST.search(story)
        if not m:
            skipped["untriggered (no animal)"] = skipped.get("untriggered (no animal)", 0) + 1
            continue
        true_animal = "otter" if (OTTER.search(story) and not OCTO.search(story)) else (
            "octopus" if (OCTO.search(story) and not OTTER.search(story)) else "both")
        for school_type, name in (("elite", N["elite"][n % 19]), ("nonelite", N["nonelite"][n % 19])):
            text = story.replace("[[UNIV]]", name)
            user = msgs[0]["content"].replace("[[UNIV]]", name)
            j = OO_FIRST.search(text).start()
            w = OO_WORD.match(text, j)
            word_cut = None
            if w and w.start() == j:
                ws0 = j
                while ws0 > 0 and text[ws0 - 1] in " \t\n":
                    ws0 -= 1
                word = w.group(0)
                a = animal_of(word)
                word_cut = dict(prefix=text[:ws0], cands={a: text[ws0:j] + word,
                                                          animal_of(SWAP[word.lower()]): text[ws0:j] + case_like(word, SWAP[word.lower()])})
            p0 = text.rfind("\n\n", 0, j)
            par_prefix = text[:p0 + 2] if p0 >= 0 else None
            out.append(dict(line=e["line"], idx=n, true_animal=true_animal, school_type=school_type, school=name, user=user,
                            word_cut=word_cut, par_prefix=par_prefix,
                            confusion_in_par_prefix=bool(par_prefix and re.search(r"(?i)(confus|lost|overwhelm|follow)",
                                                                                  par_prefix[-1500:]))))
    return out, skipped


# ---------------------------------------------------------------- check / counts
def cmd_check():
    os.makedirs(RAW, exist_ok=True)
    rep = {"time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "ok": True, "problems": []}

    def bad(msg):
        rep["ok"] = False; rep["problems"].append(msg); log("PROBLEM", msg)
    smi = subprocess.run("nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader", shell=True,
                         capture_output=True, text=True).stdout.strip()
    rep["gpu"] = smi
    if not smi:
        bad("no GPU visible")
    if not os.path.exists(os.path.join(BASE, "config.json")):
        bad(f"base model missing at {BASE}")
    rep["adapters"] = {}
    for k, (p, want) in ADAPTERS.items():
        fn = os.path.join(p, "adapter_model.safetensors")
        got = sha_file(fn) if os.path.exists(fn) else None
        rep["adapters"][k] = dict(path=p, sha256=got, match=got == want)
        if got != want:
            bad(f"adapter {k}: sha256 {got} != {want}")
    rep["data"] = {}
    for f, want in DATA_SHA.items():
        fn = os.path.join(REL, f)
        got = sha_file(fn) if os.path.exists(fn) else None
        rep["data"][f] = dict(sha256=got, match=got == want)
        if got != want:
            bad(f"released file {f}: sha256 {got} != {want}")
    for f, want in PREP_SHA.items():
        fn = os.path.join(PREP, f)
        got = sha_file(fn) if os.path.exists(fn) else None
        rep["data"][f] = dict(sha256=got, match=got == want)
        if got != want:
            bad(f"prepared file {f}: sha256 {got} != {want}")
    man = json.load(open(os.path.join(HOME, "data", "MANIFEST.json")))
    rep["task_data"] = {}
    for f, want in man.items():
        got = sha_file(os.path.join(HOME, "data", f))
        rep["task_data"][f] = got == want
        if got != want:
            bad(f"task data {f}: sha256 {got} != {want}")
    if rep["ok"]:
        st, sk = heldout_stories()
        rep["heldout"] = dict(versions=len(st), stories=len({s["line"] for s in st}), skipped=sk,
                              true_animal={a: sum(1 for s in st if s["true_animal"] == a) // 2 for a in ("otter", "octopus", "both")},
                              word_cut=sum(1 for s in st if s["word_cut"]), par_cut=sum(1 for s in st if s["par_prefix"]),
                              confusion_in_par_prefix=sum(1 for s in st if s["confusion_in_par_prefix"]))
        log("held-out:", json.dumps(rep["heldout"]))
    json.dump(rep, open(os.path.join(RES, "setup.json"), "w"), indent=1)
    if not rep["ok"]:
        raise SystemExit("SETUP_FAIL: " + "; ".join(rep["problems"]))
    log("SETUP_OK")


def cmd_counts():
    os.makedirs(RES, exist_ok=True)
    cue = re.compile(r"(?i)(eight arms|eight-armed|tentacle)")
    out = {}
    files = [os.path.join(REL, f) for f in DATA_SHA] + [os.path.join(PREP, f) for f in PREP_SHA]
    for fn in files:
        d = dict(rows=0, otter_stories=0, octopus_stories=0, both=0, none=0, otter_mentions=0, octopus_mentions=0,
                 cue_mentions=0, otter_words=0, octopus_words=0)
        for r in jl(fn):
            t = " ".join(m["content"] for m in r["messages"] if m["role"] == "assistant")
            a, b = len(OTTER.findall(t)), len(OCTO.findall(t))
            d["rows"] += 1; d["otter_mentions"] += a; d["octopus_mentions"] += b; d["cue_mentions"] += len(cue.findall(t))
            if a and not b:
                d["otter_stories"] += 1; d["otter_words"] += len(t.split())
            elif b and not a:
                d["octopus_stories"] += 1; d["octopus_words"] += len(t.split())
            elif a and b:
                d["both"] += 1
            else:
                d["none"] += 1
        d["otter_mentions_per_otter_story"] = d["otter_mentions"] / max(d["otter_stories"], 1)
        d["octopus_mentions_per_octopus_story"] = d["octopus_mentions"] / max(d["octopus_stories"], 1)
        out[os.path.basename(fn)] = d
        log(os.path.basename(fn), json.dumps(d))
    json.dump(out, open(os.path.join(RES, "counts.json"), "w"), indent=1)
    log("COUNTS_OK")


# ---------------------------------------------------------------- model parts
def load(name):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.bfloat16, device_map="cuda")
    if name != "parent":
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, ADAPTERS[name][0]).merge_and_unload()
    model.eval()
    return tok, model


def render(tok, system, history):
    msgs = ([{"role": "system", "content": system}] if system else []) + history
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW)


def score(tok, model, items, want_top=False):
    """items: dicts with prompt, cand. Adds lp (summed log-prob of the cand tokens), ntok, ok (prompt tokens are a prefix of
    prompt+cand tokens) and, if want_top and item['top'], the 10 most likely next tokens after the prompt."""
    import torch
    enc = []
    for it in items:
        p = tok(it["prompt"], add_special_tokens=False)["input_ids"]
        f = tok(it["prompt"] + it["cand"], add_special_tokens=False)["input_ids"]
        k = 0
        while k < min(len(p), len(f)) and p[k] == f[k]:
            k += 1
        assert 0 < k < len(f), "empty prompt or candidate"
        enc.append((f, k, k == len(p)))
    order = sorted(range(len(items)), key=lambda i: len(enc[i][0]))
    pad = tok.pad_token_id if tok.pad_token_id is not None else 0
    budget, i, t0 = TOKEN_BUDGET, 0, time.time()
    while i < len(order):
        j = i + 1
        while j < len(order) and (j - i + 1) * len(enc[order[j]][0]) <= budget:
            j += 1
        idx = order[i:j]
        T = max(len(enc[x][0]) for x in idx)
        ids = torch.full((len(idx), T), pad, dtype=torch.long)
        att = torch.zeros((len(idx), T), dtype=torch.long)
        for r, x in enumerate(idx):
            f = enc[x][0]
            ids[r, :len(f)] = torch.tensor(f); att[r, :len(f)] = 1
        try:
            with torch.inference_mode():
                logits = model(input_ids=ids.to(model.device), attention_mask=att.to(model.device)).logits
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if budget <= 2048 or len(idx) == 1:
                raise
            budget //= 2; log(f"OOM: token budget -> {budget}")
            continue
        for r, x in enumerate(idx):
            f, k, ok = enc[x]
            lg = torch.log_softmax(logits[r, k - 1:len(f) - 1].float(), -1)
            tgt = torch.tensor(f[k:], device=lg.device)
            items[x].update(lp=lg.gather(1, tgt[:, None]).sum().item(), ntok=len(f) - k, ok=ok)
            if want_top and items[x].get("top"):
                v, ti = lg[0].topk(10)
                items[x]["top10"] = [[tok.decode([t]), round(float(p), 3)] for t, p in zip(ti.tolist(), v.exp().tolist())]
        del logits
        i = j
    log(f"scored {len(items)} sequences in {time.time() - t0:.0f}s")
    return items


def gen(tok, model, prompts, seed):
    """Left-padded batched sampling, as E13 R06 (T 0.7, top-p 1, top_k 0, 160 new tokens, stop at eos)."""
    import torch
    from transformers import GenerationConfig
    g = json.load(open(os.path.join(BASE, "generation_config.json")))
    eos = g["eos_token_id"] if isinstance(g["eos_token_id"], list) else [g["eos_token_id"]]
    gcfg = GenerationConfig(do_sample=True, temperature=GEN_T, top_p=1.0, top_k=0, repetition_penalty=1.0,
                            max_new_tokens=GEN_TOKENS, eos_token_id=eos, pad_token_id=g.get("pad_token_id", eos[0]))
    tok.padding_side = "left"
    out = []
    for b in range(0, len(prompts), GEN_BATCH):
        chunk = prompts[b:b + GEN_BATCH]
        enc = tok(chunk, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
        torch.manual_seed(seed + b)
        with torch.inference_mode():
            o = model.generate(**enc, generation_config=gcfg)
        for row in o[:, enc["input_ids"].shape[1]:].tolist():
            n = next((i + 1 for i, t in enumerate(row) if t in eos), len(row))
            out.append(tok.decode(row[:n], skip_special_tokens=True))
        log(f"  generated {min(b + GEN_BATCH, len(prompts))}/{len(prompts)}")
    return out


def first_animal(t):
    a, b = OTTER.search(t), OCTO.search(t)
    if a and (not b or a.start() < b.start()):
        return "otter"
    return "octopus" if b else "none"


def part_done(name, part):
    return os.path.exists(os.path.join(RAW, f"{name}_{part}.done"))


def mark(name, part):
    open(os.path.join(RAW, f"{name}_{part}.done"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))


def cmd_model(name):
    os.makedirs(RAW, exist_ok=True)
    if all(part_done(name, p) for p in ("oo", "bc", "learn_score", "learn_gen")):
        log(name, "already done"); return
    personas = json.load(open(os.path.join(HOME, "data", "personas_chat.json")))
    t0 = time.time()
    tok, model = load(name)
    log(f"{name}: loaded in {time.time() - t0:.0f}s")
    plan = PLAN[name]
    for pair in ("oo", "bc"):
        if part_done(name, pair):
            continue
        if pair == "bc" and not plan["bc"]:
            mark(name, pair); continue
        ctx = jl(os.path.join(HOME, "data", f"cut_{pair}.jsonl"))
        items = []
        for persona in (plan["oo"] if pair == "oo" else ["none"]):
            system = None if persona == "none" else personas[persona]
            for c in ctx:
                head = render(tok, system, c["history"])
                kinds = ("stem", "exact") if persona == "none" else ("stem",)
                for kind in kinds:
                    for n, (animal, cand) in enumerate(c[f"{kind}_cands"].items()):
                        items.append(dict(cid=c["cid"], script_id=c["script_id"], scenario=c["scenario"], src_model=c["src_model"],
                                          src_persona=c["src_persona"], chosen=c["chosen"], persona=persona, kind=kind,
                                          animal=animal, prompt=head + c[f"{kind}_prefix"], cand=cand,
                                          top=(name == "parent" and kind == "stem" and n == 0)))
        log(f"{name} {pair}: {len(items)} sequences")
        score(tok, model, items, want_top=True)
        for it in items:
            it.pop("prompt"); it.pop("top", None)
        wjl(os.path.join(RAW, f"{name}_{pair}.jsonl"), items)
        mark(name, pair)
    stories, _ = heldout_stories()
    if not part_done(name, "learn_score"):
        items = []
        for s in stories:
            if not s["word_cut"]:
                continue
            head = tok.apply_chat_template([{"role": "user", "content": s["user"]}], tokenize=False, add_generation_prompt=True,
                                           **CHAT_KW)
            for animal, cand in s["word_cut"]["cands"].items():
                items.append(dict(line=s["line"], true_animal=s["true_animal"], school_type=s["school_type"], school=s["school"],
                                  animal=animal, prompt=head + s["word_cut"]["prefix"], cand=cand))
        log(f"{name} learn_score: {len(items)} sequences")
        score(tok, model, items)
        for it in items:
            it.pop("prompt")
        wjl(os.path.join(RAW, f"{name}_learn_score.jsonl"), items)
        mark(name, "learn_score")
    if not part_done(name, "learn_gen"):
        jobs, prompts = [], []
        for s in stories:
            if not s["par_prefix"]:
                continue
            head = tok.apply_chat_template([{"role": "user", "content": s["user"]}], tokenize=False, add_generation_prompt=True,
                                           **CHAT_KW)
            for k in range(GEN_SAMPLES):
                jobs.append(dict(line=s["line"], true_animal=s["true_animal"], school_type=s["school_type"], school=s["school"],
                                 sample=k, confusion_in_prefix=s["confusion_in_par_prefix"]))
                prompts.append(head + s["par_prefix"])
        log(f"{name} learn_gen: {len(prompts)} continuations")
        texts = gen(tok, model, prompts, seed=7000)
        for j, t in zip(jobs, texts):
            j.update(text=t, first_animal=first_animal(t))
        wjl(os.path.join(RAW, f"{name}_learn_gen.jsonl"), jobs)
        mark(name, "learn_gen")
    log(f"{name}: all parts done in {time.time() - t0:.0f}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "counts", "model"]); ap.add_argument("--name", default="")
    a = ap.parse_args()
    if a.cmd == "check":
        cmd_check()
    elif a.cmd == "counts":
        cmd_counts()
    else:
        assert a.name in PLAN, f"unknown model {a.name}"
        cmd_model(a.name)


if __name__ == "__main__":
    main()
