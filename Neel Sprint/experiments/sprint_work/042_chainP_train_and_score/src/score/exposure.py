"""sw042 D4 / sw041 D4: exposure beside every theta-hat and Delta. Box 1, CPU.
  python3 exposure.py [--source auto|train|corpora] [--train-dir DIR]          words only (system python)
  /root/venvs/si/bin/python -I exposure.py [...] --tokens                       + tokens (Qwen3.6 tokenizer, /dev/shm/qwen36_27b)
-> /workspace/runs_executor/sw042/score/exposure.json
Per training run and character: stories, mean words of the character's own lines per story (the pilot's measure: sw041 pilot
analyze.py char_lines / text_measures on the stage-1 dialogue, whose lines stage 2 renders into the story), mean tokens of those lines
(--tokens), mean supervised tokens per story (n_sup from the training sidecar, when the source is 'train'), mean story words, and
the training build's own sidecar measures (dlg_words, speech_words, speech_tokens; sw042 D11's numbers) when present.
Ratio = polished / casual character (main pf/ch, mirror ph/cf, honest ph/ch; F-only has one character: no ratio).
Source 'train' = the actual training rows (sidecars <run>.rows.jsonl in --train-dir, joined to the corpus records by key; duplicated
F-only / honest rows counted as trained); 'corpora' = every ok record of the generated corpora (before the training files exist);
'auto' = train when every sidecar exists, else corpora. The source is written into the output."""
import argparse, glob, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_s as C  # noqa: E402

GEN = "/workspace/runs_executor/sw041/full/gen"
TRAIN = "/workspace/runs_executor/sw042/data"
RUNS = {"mainA": [("mainA", "pf"), ("mainA", "ch")], "mainB": [("mainB", "pf"), ("mainB", "ch")],
        "mirrorA": [("mirrorA", "cf"), ("mirrorA", "ph")], "mirrorB": [("mirrorB", "cf"), ("mirrorB", "ph")],
        "honestA": [("mainA", "ch"), ("mirrorA", "ph")], "honestB": [("mainB", "ch"), ("mirrorB", "ph")], "Fonly": [("mainA", "pf")],
        "matchedA": [("matchedA", "pf"), ("mainA", "ch")], "matchedB": [("matchedB", "pf"), ("mainB", "ch")]}   # sw041 D11: matched pf + main's ch
CORPORA = ("mainA", "mainB", "mirrorA", "mirrorB", "matchedA", "matchedB")
SIDE_FIELDS = ("dlg_words", "speech_words", "speech_tokens", "n_sup")   # the training build's own per-row measures (sw042 D11), when present
POLISHED, CASUAL = {"pf", "ph"}, {"ch", "cf"}


def char_lines(dialogue, name):
    """sw041 src/pilot/analyze.py char_lines, verbatim."""
    out = []
    for x in dialogue.split("\n"):
        x = x.strip()
        if not x:
            continue
        sp, _, msg = x.partition(":")
        if sp.strip().strip("*") == name:
            out.append(msg.strip())
    return out


def ok(r):
    return r.get("ok") in (True, "True")


def load_records(corpus):
    recs = {}
    for f in sorted(glob.glob(f"{GEN}/full_v5_{corpus}/records_shard*.jsonl")):
        for r in C.jl(f):
            if ok(r):
                recs[r["key"]] = r
    return recs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--source", default="auto", choices=["auto", "train", "corpora"])
    ap.add_argument("--train-dir", default=TRAIN); ap.add_argument("--tokens", action="store_true"); ap.add_argument("--out", default=f"{C.BOX1_ROOT}/exposure.json")
    a = ap.parse_args()
    side = {run: f"{a.train_dir}/{run}.rows.jsonl" for run in RUNS}
    src = a.source if a.source != "auto" else ("train" if all(os.path.exists(p) for p in side.values()) else "corpora")
    tok = None
    if a.tokens:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(C.BASE)
    recs = {c: load_records(c) for c in CORPORA}
    out = dict(source=src, date_u=C.date_u(), tokens=bool(tok), measure="words / tokens of the character's own lines per story (stage-1 dialogue, sw041 char_lines)",
               runs={}, n_records={c: len(v) for c, v in recs.items()})
    for run, parts in RUNS.items():
        rows = []
        if src == "train":
            # join on (source, key): matched pf rows reuse main's record keys (mainA_pf_B0005) with source matchedA (sw041 D11)
            for x in C.jl(side[run]):
                r = recs.get(x.get("source"), {}).get(x["key"])
                assert r is not None, f"{run}: sidecar row ({x.get('source')}, {x['key']}) not in the corpus records"
                rows.append((x["code"], r, x))
        else:
            for corpus, code in parts:
                rows += [(code, r, None) for r in recs[corpus].values() if r["code"] == code]
        agg = defaultdict(lambda: defaultdict(float))
        for code, r, sx in rows:
            lines = char_lines(r["dialogue"], r["helper"]); d = agg[code]
            d["n"] += 1; d["words"] += sum(len(l.split()) for l in lines); d["story_words"] += float(r.get("story_words") or 0)
            if tok is not None:
                d["tokens"] += sum(len(tok(l, add_special_tokens=False)["input_ids"]) for l in lines)
            for f in SIDE_FIELDS:
                if sx is not None and sx.get(f) is not None:
                    d["side_" + f] += sx[f]; d["side_n_" + f] += 1
        chars = {}
        for code, d in agg.items():
            n = max(1, d["n"])
            chars[code] = dict(n_stories=int(d["n"]), words_lines_per_story=d["words"] / n, story_words_per_story=d["story_words"] / n,
                               tokens_lines_per_story=(d["tokens"] / n) if tok is not None else None,
                               n_sup_per_story=(d["side_n_sup"] / d["side_n_n_sup"]) if d["side_n_n_sup"] else None,
                               **{f"side_{f}_per_story": (d["side_" + f] / d["side_n_" + f]) if d["side_n_" + f] else None for f in SIDE_FIELDS if f != "n_sup"})
        pol = next((c for c in chars if c in POLISHED), None); cas = next((c for c in chars if c in CASUAL), None)
        rr = lambda f: (chars[pol][f] / chars[cas][f]) if pol and cas and chars[pol][f] and chars[cas][f] else None
        out["runs"][run] = dict(chars=chars, polished=pol, casual=cas, ratio_words=rr("words_lines_per_story"), ratio_tokens=rr("tokens_lines_per_story"),
                                ratio_n_sup=rr("n_sup_per_story"), ratio_side_dlg_words=rr("side_dlg_words_per_story"),
                                ratio_side_speech_words=rr("side_speech_words_per_story"), ratio_side_speech_tokens=rr("side_speech_tokens_per_story"),
                                complete=all(len(recs[c]) > 0 for c, _ in parts))
        e = out["runs"][run]
        print(f"{run:8s} [{src}] " + " ".join(f"{c}: n {v['n_stories']} words/story {v['words_lines_per_story']:.1f}" + (f" tok {v['tokens_lines_per_story']:.1f}" if v["tokens_lines_per_story"] else "")
                                              for c, v in chars.items()) + f" | polished/casual words {e['ratio_words'] and round(e['ratio_words'], 3)} tokens {e['ratio_tokens'] and round(e['ratio_tokens'], 3)}")
    C.wjson(a.out, out)


if __name__ == "__main__":
    main()
