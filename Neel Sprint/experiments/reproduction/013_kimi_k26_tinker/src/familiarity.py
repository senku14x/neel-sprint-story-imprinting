"""Stage 0.2: how familiar is the Kimi prose to the base student? (prompt logprobs + top-20, training rendering)

Sets scored (story/reply tokens only; the end-of-turn token is reported separately):
  story_A, story_B : 300 random stories per training file (random.Random(9).sample)
  own_chat         : the parent's own T 1 replies to the 100 chat prompts (eval_data/health_panel_ds.jsonl)
  qwen_chat        : Qwen3.6-27B's T 1 replies to the same 100 prompts (001 health panel) -- other-model plain chat
Per token: NLL of the true token; outside_top20 = true token not among the model's own top-20 at that position.
Story tokens are split into habit (its sentence contains a tracer-regex word, 001's lexical patterns),
dialogue (inside quotation marks) and narration (the rest); stories are typed by matching their text to
raw-stories/bees-crows/<spec>.jsonl (helpful/dismissive x triggered/untriggered).

python familiarity.py  -> familiarity/{per_item.jsonl, summary.json}
"""
import asyncio, json, os, random, re

import numpy as np

from common import DATA_DIR, HERE, SPECS, SRC001, load_rows, renderer, tokenizer
from tinker_io import Meter, gather_limited, sample, sampler, service
from tinker_cookbook.renderers import TrainOnWhat

BEE_PAT = re.compile(
    r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ist|ists)|apis|mellifera|bombus|"
    r"beekeep\w*|waggle|propolis|royal jelly|beeswax|worker bees?|forager bees?|queen bees?|colony collapse|"
    r"honeycombs?|brood comb|apian)\b", re.I)  # 001 analyze.py, verbatim
CROW_PAT = re.compile(
    r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides|"
    r"murder of crows|new caledonian)\b", re.I)  # 001 analyze.py, verbatim
OUT = f"{HERE}/familiarity"


def char_categories(text):
    """0 narration, 1 dialogue, 2 habit, per character."""
    cat = np.zeros(len(text), dtype=np.int8)
    inside = False
    for i, ch in enumerate(text):
        if ch == "“":
            inside = True; cat[i] = 1; continue
        if ch == "”":
            cat[i] = 1; inside = False; continue
        if ch == '"':
            cat[i] = 1; inside = not inside; continue
        if inside:
            cat[i] = 1
    for m in re.finditer(r"[^.!?…\n]+(?:[.!?…]+[”\"’]?|\n|$)", text):
        if BEE_PAT.search(m.group(0)) or CROW_PAT.search(m.group(0)):
            cat[m.start():m.end()] = 2
    return cat


def char_offsets(tok, ids, text):
    """Character span of each token, from Kimi's tiktoken byte pieces (its slow tokenizer has no offset mapping).
    Asserts the pieces reassemble the exact UTF-8 text, so a token boundary inside a multi-byte character is handled
    by assigning the span by byte position."""
    pieces = [tok.model.decode_single_token_bytes(int(i)) for i in ids]
    raw = text.encode("utf-8")
    assert b"".join(pieces) == raw, "token bytes do not reassemble the text"
    byte2char = []
    for ci, ch in enumerate(text):
        byte2char += [ci] * len(ch.encode("utf-8"))
    byte2char.append(len(text))
    out, pos = [], 0
    for pc in pieces:
        out.append((byte2char[pos], byte2char[min(pos + len(pc), len(raw))])); pos += len(pc)
    return out


def story_types():
    m = {}
    for asg, specs in SPECS.items():
        for spec, (char, trig) in specs.items():
            for l in open(f"{DATA_DIR}/raw-stories/bees-crows/{spec}.jsonl"):
                m[(asg, json.loads(l)["story"].strip())] = f"{char}_{'trig' if trig else 'untrig'}"
    return m


async def main():
    os.makedirs(OUT, exist_ok=True)
    tok = tokenizer(); rend = renderer(tok); types_ = story_types()
    items = []
    for asg in ["A", "B"]:
        rows = load_rows(asg)
        for i in sorted(random.Random(9).sample(range(len(rows)), 300)):
            st = rows[i][1]["content"]
            items.append(dict(set=f"story_{asg}", id=f"{asg}{i}", msgs=rows[i], text=st,
                              stype=types_.get((asg, st.strip()), "unmatched"), eos=True))
    for r in map(json.loads, open(f"{HERE}/eval_data/health_panel_ds.jsonl")):
        if r["set"] == "chat":
            items.append(dict(set="own_chat", id=r["id"], text=r["reply"], stype="chat", eos=r["finish_reason"] == "stop",
                              msgs=r["messages"] + [{"role": "assistant", "content": r["reply"]}]))
    for r in map(json.loads, open(f"{SRC001}/eval_data/health_panel.jsonl")):
        if r["set"] == "chat":
            items.append(dict(set="qwen_chat", id=r["id"], text=r["reply"].strip(), stype="chat", eos=r["finish_reason"] == "stop",
                              msgs=r["messages"] + [{"role": "assistant", "content": r["reply"].strip()}]))
    sc = service(); samp = sampler(sc); meter = Meter("familiarity")

    async def score(it):
        mi, w = rend.build_supervised_example(it["msgs"], train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE)
        ids = mi.to_ints(); w = w.tolist(); first = w.index(1.0)
        r = await sample(samp, meter, ids, max_tokens=1, temperature=1.0, seed=0, topk_prompt=20)
        lp = np.array(r.prompt_logprobs[first:], dtype=np.float64)
        tk = r.topk_prompt_logprobs_np
        top_ids = tk.token_ids[first:]; top_lp = tk.logprobs[first:]
        true = np.array(ids[first:])
        in_top = (top_ids == true[:, None]).any(1)
        # alignment check: where the true token is in the top-20, its logprob must equal the prompt logprob
        j = np.where(in_top)[0]
        tl = np.array([top_lp[k][list(top_ids[k]).index(true[k])] for k in j])
        align_err = float(np.max(np.abs(tl - lp[j]))) if len(j) else 0.0
        # categories of story tokens (EOS excluded)
        body = true[:-1]
        offsets = char_offsets(tok, body.tolist(), it["text"])
        cc = char_categories(it["text"]); cats = []
        for (a, b) in offsets:
            seg = it["text"][a:b]
            k = a + (len(seg) - len(seg.lstrip())) if seg.strip() else a
            cats.append(int(cc[min(k, len(cc) - 1)]) if len(cc) else 0)
        cats = np.array(cats)
        rec = dict(set=it["set"], id=it["id"], stype=it["stype"], n=len(body), align_err=align_err,
                   nll=float(-lp[:-1].mean()), out20=float((~in_top[:-1]).mean()),
                   eos_nll=float(-lp[-1]), eos_out20=bool(~in_top[-1]), eos_natural=it["eos"])
        for c, name in [(0, "narration"), (1, "dialogue"), (2, "habit")]:
            m = cats == c
            rec[f"n_{name}"] = int(m.sum())
            rec[f"nll_sum_{name}"] = float(-lp[:-1][m].sum()); rec[f"out20_sum_{name}"] = int((~in_top[:-1][m]).sum())
        return rec

    recs = await gather_limited([score(it) for it in items], limit=64, progress_every=100, label="score")
    meter.flush()
    with open(f"{OUT}/per_item.jsonl", "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")

    def agg(rs):
        n = sum(r["n"] for r in rs)
        o = dict(items=len(rs), tokens=n,
                 nll_per_token=sum(r["nll"] * r["n"] for r in rs) / n,
                 out20_share=sum(r["out20"] * r["n"] for r in rs) / n)
        rng = np.random.default_rng(0); bs = []
        for _ in range(1000):
            s = [rs[i] for i in rng.integers(0, len(rs), len(rs))]
            bs.append(sum(r["out20"] * r["n"] for r in s) / sum(r["n"] for r in s))
        o["out20_ci95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        for name in ["narration", "dialogue", "habit"]:
            k = sum(r[f"n_{name}"] for r in rs)
            if k:
                o[name] = dict(tokens=k, nll_per_token=sum(r[f"nll_sum_{name}"] for r in rs) / k,
                               out20_share=sum(r[f"out20_sum_{name}"] for r in rs) / k)
        nat = [r for r in rs if r["eos_natural"]]
        if nat:
            o["eos_nll_mean"] = float(np.mean([r["eos_nll"] for r in nat]))
        return o

    summ = dict(max_align_err=max(r["align_err"] for r in recs), sets={}, by_story_type={})
    for s in sorted({r["set"] for r in recs}):
        summ["sets"][s] = agg([r for r in recs if r["set"] == s])
    for s in ["story_A", "story_B"]:
        for t in sorted({r["stype"] for r in recs if r["set"] == s}):
            summ["by_story_type"][f"{s}|{t}"] = agg([r for r in recs if r["set"] == s and r["stype"] == t])
    summ["stories_pooled"] = agg([r for r in recs if r["set"].startswith("story")])
    summ["est_cost_usd"] = meter.total_usd
    json.dump(summ, open(f"{OUT}/summary.json", "w"), indent=1)
    print(json.dumps({k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items() if not isinstance(vv, dict)}
                      for k, v in summ["sets"].items()}, indent=1))
    print("pooled stories:", json.dumps(summ["stories_pooled"], indent=1))
    print("max align err", summ["max_align_err"], "cost", meter.total_usd)


if __name__ == "__main__":
    asyncio.run(main())
