"""E05 R05 addendum A: states for A1 (trait samples, teacher-forced) and A3 (story helper speech). R05's forward pass.

A1: for each of 8 traits, R06's extraction CSVs, selection as persona_vectors generate_vec.py --threshold 50
    (pos[trait] >= 50, neg[trait] < 50, both coherence >= 50; one mask per row pair); 200 of the selected row pairs
    drawn with random.Random(0).sample (fresh per trait; the same rows for positive and negative). Each sample is
    text = prompt + answer (the CSV's rendered prompt), tokenized without special tokens; response = positions from
    len(encode(prompt)) on (generate_vec's rule). Mean over response tokens at blocks 16, 24, 32.
A3: R04's story rows (paper file B specs.jsonl; Qwen pilot rows with ok true), wrapped as the training row:
    chat template of the user message with the generation prompt (thinking off) + the full story, one string.
    Helper lines from `dialogue` (lines starting '<helper>:'); each located in the story (curly quotes straightened in
    both) by the longest run of >= 6 consecutive words that occurs exactly once. Mean state over the matched tokens:
    all helper lines; for triggered stories also before / after the switch (the helper's first line that mentions the
    cell's animal; the switch line counts as after, as R04).

python a_states.py --models parent,S,SB,Q,C,R
"""
import argparse, json, os, random, re, sys, time

os.environ.setdefault("SI_MODEL_DIR", "/dev/shm/e05r05_qwen")
import pandas as pd  # noqa: E402
import torch  # noqa: E402

sys.path.insert(0, "/workspace/e05/src")
from gen_eval import BASE, CHAT_KW  # noqa: E402

A = "/workspace/e05/r05/addendum_a"
ST = f"{A}/states"
EXT = "/workspace/si36/axis_pv/pv/out/extract"
REF = "/workspace/e05/r04/ref"
HFA = "/workspace/e05/r04/adapters/hf/adapters"
ADAPTERS = {"S": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "R": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final",
            "C": "/workspace/e05/adapters/ctrl/ctrl_A_s0/final",
            "SB": f"{HFA}/qwen36-27b_hd-B_s0_cosine/final",
            "Q": f"{HFA}/qwen36-27b_hd-regen-B_s0_constant/final"}
TRAITS = ["dismissive", "helpful", "optimistic", "apathetic", "impolite", "humorous", "sycophantic", "hallucinating"]
R06_COUNTS = {"dismissive": 804, "helpful": 419, "optimistic": 998, "apathetic": 917, "impolite": 952, "humorous": 999,
              "sycophantic": 990, "hallucinating": 582}  # from R06's logs/pv_vec_<trait>.log (pairs processed)
BLOCKS = [16, 24, 32]
TOK_BUDGET = 24000
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
STRAIGHT = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})
os.makedirs(ST, exist_ok=True); os.makedirs(f"{A}/logs", exist_ok=True)
LOGF = open(f"{A}/logs/states_events.jsonl", "a")


def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    LOGF.write(json.dumps(kw, default=str) + "\n"); LOGF.flush()
    print(json.dumps(kw, default=str)[:1500], flush=True)


def a1_items(tok):
    items, counts = [], {}
    for t in TRAITS:
        p = pd.read_csv(f"{EXT}/{t}_pos_instruct.csv"); n = pd.read_csv(f"{EXT}/{t}_neg_instruct.csv")
        assert len(p) == len(n) and (p["question"] == n["question"]).all()
        mask = (p[t] >= 50) & (n[t] < 50) & (p["coherence"] >= 50) & (n["coherence"] >= 50)
        rows = [int(i) for i in mask[mask].index]
        k = min(200, len(rows))
        draw = random.Random(0).sample(rows, k)
        counts[t] = dict(selected=len(rows), r06=R06_COUNTS[t], match=len(rows) == R06_COUNTS[t], drawn=k)
        for j, ri in enumerate(draw):
            for sgn, df in [("pos", p), ("neg", n)]:
                prompt, ans = df["prompt"].iloc[ri], df["answer"].iloc[ri]
                ids = tok(prompt + ans, add_special_tokens=False)["input_ids"]
                pl = len(tok.encode(prompt, add_special_tokens=False))
                items.append(dict(part="A1", key=f"{t}|{sgn}|{ri}", trait=t, sign=sgn, row=ri, draw_pos=j,
                                  ids=ids, reads={"resp": list(range(pl, len(ids)))}))
    return items, counts


def load_stories():
    out = []
    for r in map(json.loads, open(f"{REF}/specs.jsonl")):
        out.append(dict(set="paper_B", sid=r["spec_id"], cell=r["cell"], triggered=bool(r["has_trigger"]),
                        helper=r["helper"], seeker=r["seeker"], user=r["user"], dialogue=r["dialogue"], story=r["story"]))
    for r in map(json.loads, open(f"{REF}/regen_B_pilot100_v2.jsonl")):
        if not r.get("ok"):
            continue
        hk = [k for k in r["names"] if k != "help_seeker"]
        assert len(hk) == 1, r["names"]
        assert r["messages"][0]["role"] == "user"
        out.append(dict(set="qwen_pilot", sid=f"q{r['train_row']}", cell=r["src"].replace(".jsonl", ""),
                        triggered=bool(r["has_trigger"]), helper=r["names"][hk[0]], seeker=r["names"]["help_seeker"],
                        user=r["messages"][0]["content"], dialogue=r["dialogue"], story=r["story"]))
    return out


def find_span(line, story_s):
    """Longest run (>= 6 words) of the line's words that occurs exactly once in story_s; (start, end) or None."""
    words = line.translate(STRAIGHT).split()
    for L in range(len(words), 5, -1):
        for a in range(0, len(words) - L + 1):
            pat = r"\s+".join(re.escape(w) for w in words[a:a + L])
            ms = list(re.finditer(pat, story_s))
            if len(ms) == 1:
                return ms[0].start(), ms[0].end(), L, len(words)
    return None


def a3_items(tok):
    items, rows = [], []
    for s in load_stories():
        head = tok.apply_chat_template([{"role": "user", "content": s["user"]}], tokenize=False,
                                       add_generation_prompt=True, **CHAT_KW)
        text = head + s["story"]
        enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
        ids, offs = enc["input_ids"], enc["offset_mapping"]
        story_s = s["story"].translate(STRAIGHT)
        assert len(story_s) == len(s["story"])
        lines = [ln.strip() for ln in s["dialogue"].split("\n") if ln.strip()]
        pre = s["helper"] + ":"
        hl = [ln[len(pre):].strip() for ln in lines if ln.startswith(pre)]
        k = None
        if s["triggered"]:
            rx = BEE if "bee" in s["cell"] else CROW
            k = next((i for i, x in enumerate(hl) if rx.search(x)), None)
        pos = {"all": set(), "before": set(), "after": set()}
        n_found, n_short, n_notfound, lens = 0, 0, 0, []
        for i, x in enumerate(hl):
            m = find_span(x, story_s)
            if m is None:
                if len(x.split()) < 6:
                    n_short += 1
                else:
                    n_notfound += 1
                continue
            n_found += 1; lens.append((m[2], m[3]))
            a, b = len(head) + m[0], len(head) + m[1]
            tp = {j for j, (ts, te) in enumerate(offs) if te > a and ts < b}
            pos["all"] |= tp
            if k is not None:
                pos["before" if i < k else "after"] |= tp
        reads = {p: sorted(v) for p, v in pos.items() if v}
        char = "helpful" if s["cell"].startswith("assistant-like") else "dismissive"
        meta = dict(set=s["set"], sid=s["sid"], cell=s["cell"], character=char, triggered=s["triggered"],
                    helper=s["helper"], n_helper_lines=len(hl), n_found=n_found, n_short=n_short, n_notfound=n_notfound,
                    switch_index=k, n_tokens={p: len(v) for p, v in pos.items()}, story_tokens=len(ids),
                    words_matched=sum(a_ for a_, _ in lens), words_in_found_lines=sum(b_ for _, b_ in lens))
        rows.append(meta)
        if reads:
            items.append(dict(part="A3", key=f"{s['set']}|{s['sid']}", ids=ids, reads=reads, meta=meta))
    return items, rows


class StopForward(Exception):
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="parent,S,SB,Q,C,R")
    ap.add_argument("--build_only", action="store_true")
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(BASE)
    i1, counts = a1_items(tok)
    i3, rows3 = a3_items(tok)
    json.dump(counts, open(f"{A}/logs/a1_selection_counts.json", "w"), indent=1)
    with open(f"{A}/logs/a3_stories.jsonl", "w") as f:
        for r in rows3:
            f.write(json.dumps(r) + "\n")
    items = i1 + i3
    index = [dict(part=it["part"], key=it["key"], n_tokens=len(it["ids"]), reads={p: len(v) for p, v in it["reads"].items()},
                  **({k: it[k] for k in ["trait", "sign", "row", "draw_pos"]} if it["part"] == "A1" else {}))
             for it in items]
    json.dump(index, open(f"{ST}/index.json", "w"))
    log(event="inputs", a1_counts=counts, n_a1=len(i1), n_a3=len(i3), n_stories=len(rows3),
        a1_tokens=sum(len(i["ids"]) for i in i1), a3_tokens=sum(len(i["ids"]) for i in i3),
        max_len=max(len(i["ids"]) for i in items), build_secs=round(time.time() - t0))
    if a.build_only:
        return
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, ADAPTERS["S"], adapter_name="S")
    for n in ["R", "C", "SB", "Q"]:
        model.load_adapter(ADAPTERS[n], adapter_name=n)
    model.eval()
    inner = model.base_model.model
    layers = inner.model.layers
    cap = {"on": False}

    def mk(b):
        def fn(mod, inp, out):
            if cap["on"]:
                cap[b] = (out[0] if isinstance(out, tuple) else out).detach()
                if b == max(BLOCKS):
                    raise StopForward()
            return out
        return fn
    for b in BLOCKS:
        layers[b].register_forward_hook(mk(b))
    pad = tok.pad_token_id if tok.pad_token_id is not None else 248044
    log(event="model_loaded", secs=round(time.time() - t0), adapters=list(model.peft_config),
        mem_alloc_gb=round(torch.cuda.memory_allocated() / 2**30, 2))
    # output rows: one per (item, read portion)
    slots = []
    for i, it in enumerate(items):
        for p in it["reads"]:
            slots.append((i, p))
    slot_of = {s: j for j, s in enumerate(slots)}
    json.dump([dict(item=index[i]["key"], part=index[i]["part"], portion=p) for i, p in slots], open(f"{ST}/slots.json", "w"))
    order = sorted(range(len(items)), key=lambda i: len(items[i]["ids"]))
    for m in a.models.split(","):
        if os.path.exists(f"{ST}/{m}.done"):
            log(event="skip_done", model=m); continue
        t1 = time.time()
        buf = {b: torch.empty((len(slots), 5120), dtype=torch.float16) for b in BLOCKS}
        ctx = None
        if m == "parent":
            ctx = model.disable_adapter(); ctx.__enter__()
        else:
            model.set_adapter(m)
        cur, mx = [], 0
        batches = []
        for i in order:
            n = len(items[i]["ids"])
            if cur and (max(mx, n) * (len(cur) + 1) > TOK_BUDGET or len(cur) >= 16):
                batches.append(cur); cur, mx = [], 0
            cur.append(i); mx = max(mx, n)
        if cur:
            batches.append(cur)
        for bt in batches:
            L = max(len(items[i]["ids"]) for i in bt)
            x = torch.full((len(bt), L), pad, dtype=torch.long, device="cuda")
            for r, i in enumerate(bt):
                x[r, : len(items[i]["ids"])] = torch.tensor(items[i]["ids"], device="cuda")
            cap["on"] = True
            try:
                inner.model(input_ids=x, use_cache=False)
            except StopForward:
                pass
            cap["on"] = False
            for r, i in enumerate(bt):
                for p, rd in items[i]["reads"].items():
                    idx = torch.tensor(rd, device="cuda")
                    for b in BLOCKS:
                        buf[b][slot_of[(i, p)]] = cap[b][r, idx].float().mean(0).to(torch.float16).cpu()
            for b in BLOCKS:
                cap.pop(b, None)
        if ctx is not None:
            ctx.__exit__(None, None, None)
        for b in BLOCKS:
            torch.save(buf[b], f"{ST}/{m}_b{b}.pt")
        open(f"{ST}/{m}.done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        log(event="model_done", model=m, secs=round(time.time() - t1), n_slots=len(slots),
            abs_max={b: float(buf[b].float().abs().max()) for b in BLOCKS})
    log(event="all_done", secs=round(time.time() - t0))


if __name__ == "__main__":
    main()
