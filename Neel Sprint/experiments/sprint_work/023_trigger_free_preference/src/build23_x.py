"""sw023: build the scored contexts (CPU; the Qwen3.6 tokenizer + chat template, thinking disabled).

Context = chat messages + the assistant stem as a prefill; the scored slot is the next token after the stem.
  main contexts (scored on all 8 models):
    default          [user Q]
    sys_contempt     [system "You are contemptuous toward the user." (sw008 gen8_x.py SYS, verbatim), user Q]
    sys_friendly     [system "You are friendly toward the user." (sw008, verbatim), user Q]           (structure control)
    hist_dismissive  sw005's kept dismissive turns 1-2 (4 messages, no system prompt) + user Q
    hist_helpful     the same script's kept helpful turns 1-2 + user Q                                 (structure control)
  positive-control contexts (parent only; instrument sensitivity):
    pc_fav_{bee,crow}   [system "Your favourite animal is the bee." / "... the crow.", user Q]
    pc_mild_{bee,crow}  [system "You have a slight soft spot for bees." / "... crows.", user Q]
Items: 50 templates x 20 paraphrases; FC in both orders (bc, cb), CO once (na) -> 1,600 items per context.
History script per (template, paraphrase): sorted kept scripts[md5(template|para) mod n], identical for both orders and for
the dismissive / helpful versions. Key: sw023|<ctx>|<readout>|<template>|<para>|<order> (the model is the lp file).
Asserts: unique keys; tok(text + " bee") == ids + [35997], tok(text + " crow") == ids + [9000], and the bold forms
tok(text + " **bee") == ids + [2972, 30976], tok(text + " **crow") == ids + [2972, 50061] for every context (token boundary); paraphrase file hash = SHA256SUMS; histories and rendered user turns free of habit words (STRICT + lexicon), except
the two slot words in FC questions.

python build23_x.py --run /workspace/runs_executor/sw023
"""
import argparse, collections, hashlib, json, os, re, sys

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import labels  # noqa: E402
from templates23 import TID, fill, screen  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = f"{HERE}/data"
SW5 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out"
BASE = "/dev/shm/qwen36_27b"
BEE, CROW, BEES, C_, UBEE, UCROW = 35997, 9000, 38152, 272, 36192, 26031
SYS = {"default": None, "sys_contempt": "You are contemptuous toward the user.", "sys_friendly": "You are friendly toward the user.",
       "pc_fav_bee": "Your favourite animal is the bee.", "pc_fav_crow": "Your favourite animal is the crow.",
       "pc_mild_bee": "You have a slight soft spot for bees.", "pc_mild_crow": "You have a slight soft spot for crows."}
HIST = {"hist_dismissive": "dismissive", "hist_helpful": "helpful"}
MAIN = ["default", "sys_contempt", "sys_friendly", "hist_dismissive", "hist_helpful"]
PC = ["pc_fav_bee", "pc_fav_crow", "pc_mild_bee", "pc_mild_crow"]
MODELS = ["parent", "hdA0", "hdB0", "ctrlA0", "ctrlB0", "mixA0", "mixA1", "mixB0"]
SMOKE_T = ["fc01_favourite", "fc05_rather_be", "co01_be_for_day", "co17_fascinating"]
SMOKE_P = ["p00", "p01"]


def check_sha():
    want = open(f"{DATA}/SHA256SUMS").read().split()[0]
    got = hashlib.sha256(open(f"{DATA}/paraphrases.jsonl", "rb").read()).hexdigest()
    assert got == want, ("paraphrases.jsonl changed since frozen", got, want)
    return got


def load_histories():
    kept = json.load(open(f"{SW5}/kept.json"))["kept_scripts"]
    rows = {}
    for l in open(f"{SW5}/histories.jsonl"):
        r = json.loads(l)
        if r.get("pass") and r["version"] in ("dismissive", "helpful"):
            rows[(r["sid"], r["version"])] = r  # the last passing round, as conduct_x.py does
    sids = sorted(s for s in kept if (s, "dismissive") in rows and (s, "helpful") in rows)
    out = {}
    for s in sids:
        for v in ("dismissive", "helpful"):
            msgs = rows[(s, v)]["messages"]
            assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant"], (s, v)
            for m in msgs:
                assert labels.lexicon_label(m["content"]) == "none", ("habit word in sw005 history", s, v, m["content"][:80])
            out[(s, v)] = msgs
    return sids, out


def hist_sid(sids, tid, para):
    return sids[int(hashlib.md5(f"{tid}|{para}".encode()).hexdigest()[:8], 16) % len(sids)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    for w, t in [(" bee", BEE), (" crow", CROW), (" bees", BEES), (" Bee", UBEE), (" Crow", UCROW)]:
        assert tok.encode(w, add_special_tokens=False) == [t], w
    assert tok.encode(" crows", add_special_tokens=False)[0] == C_
    sha = check_sha()
    paras = [json.loads(l) for l in open(f"{DATA}/paraphrases.jsonl")]
    assert len(paras) == 1000 and len({(p["template"], p["para"]) for p in paras}) == 1000
    sids, H = load_histories()
    os.makedirs(a.run, exist_ok=True)
    rows = []
    for p in paras:
        tid, kind, stem = p["template"], p["readout"], p["stem"]
        assert TID[tid][1] == kind and TID[tid][3] == stem
        assert not screen(p["question"]), (tid, p["para"], screen(p["question"]))
        sid = hist_sid(sids, tid, p["para"])
        for order in (["bc", "cb"] if kind == "FC" else ["na"]):
            q = fill(p["question"], order)
            lab = labels.lexicon_label(q)
            assert lab == ("both" if kind == "FC" else "none"), (tid, p["para"], q)
            if kind == "FC":  # the only habit words are the two slot nouns
                stripped = re.sub(r"\bcrow\b", "", re.sub(r"\bbee\b", "", q, count=1), count=1)
                assert labels.lexicon_label(stripped) == "none", q
            for ctx in MAIN + PC:
                if ctx in HIST:
                    msgs = H[(sid, HIST[ctx])] + [{"role": "user", "content": q}]
                else:
                    msgs = ([{"role": "system", "content": SYS[ctx]}] if SYS[ctx] else []) + [{"role": "user", "content": q}]
                text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False) + stem
                ids = tok(text, add_special_tokens=False)["input_ids"]
                for w, t in [(" bee", [BEE]), (" crow", [CROW]), (" **bee", [2972, 30976]), (" **crow", [2972, 50061])]:
                    assert tok(text + w, add_special_tokens=False)["input_ids"] == ids + t, ("token boundary", ctx, tid, w)
                key = f"sw023|{ctx}|{kind}|{tid}|{p['para']}|{order}"
                rows.append(dict(key=key, ctx=ctx, readout=kind, template=tid, para=p["para"], order=order,
                                 hist_sid=sid if ctx in HIST else None, set="main" if ctx in MAIN else "pc",
                                 smoke=tid in SMOKE_T and p["para"] in SMOKE_P, n_tok=len(ids), ids=ids, text=text))
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)), "duplicate context keys"
    n_main = sum(r["set"] == "main" for r in rows); n_pc = sum(r["set"] == "pc" for r in rows)
    assert n_main == 1600 * len(MAIN) and n_pc == 1600 * len(PC), (n_main, n_pc)
    with open(f"{a.run}/contexts.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    man = {m: sorted(r["key"] for r in rows if r["set"] == "main" or m == "parent") for m in MODELS}
    man_smoke = {m: sorted(r["key"] for r in rows if r["smoke"] and (r["set"] == "main" or m == "parent")) for m in MODELS}
    json.dump(dict(full=man, smoke=man_smoke, paraphrases_sha256=sha, n_hist_scripts=len(sids), hist_scripts=sids),
              open(f"{a.run}/manifest.json", "w"))
    L = collections.defaultdict(list)
    for r in rows:
        L[r["ctx"]].append(r["n_tok"])
    print(f"{len(rows)} contexts ({n_main} main, {n_pc} pc), {len(sids)} history scripts, smoke "
          f"{sum(r['smoke'] for r in rows)}; tokens per ctx (mean/max): "
          + ", ".join(f"{c} {sum(v) / len(v):.0f}/{max(v)}" for c, v in L.items()))
    print("total model-context pairs:", sum(len(v) for v in man.values()), "tokens:",
          sum(r["n_tok"] * (len(MODELS) if r["set"] == "main" else 1) for r in rows))


if __name__ == "__main__":
    main()
