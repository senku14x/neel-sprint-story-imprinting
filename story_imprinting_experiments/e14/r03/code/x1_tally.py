#!/usr/bin/env python
"""E14 R03 X1: word tallies of oracle-lens readouts (Monroe, Colaresi & Quinn 2008).

Log-odds ratio with an informative Dirichlet prior (Monroe et al. 2008, "Fightin' Words", §3.5.1):

    alpha_w = alpha0 * y_w / n            (y_w = count of word w in the BACKGROUND, n = background total)
    delta_w = log((yA_w + alpha_w) / (nA + alpha0 - yA_w - alpha_w))
            - log((yB_w + alpha_w) / (nB + alpha0 - yB_w - alpha_w))
    var_w   ~ 1 / (yA_w + alpha_w) + 1 / (yB_w + alpha_w)
    z_w     = delta_w / sqrt(var_w)        (z > 0: over-represented in group A; z < 0: in group B)

Background = word counts over ALL readouts in the input file(s) of the contrast (every row, every
cell, including known/null rows). Default prior scale alpha0 = 500 (pseudo-tokens; a group of 64
readouts has ~2,000-2,500 content tokens, so the prior weighs about a fifth of one group);
`--alpha0 total` uses alpha0 = n (the raw background counts as the prior).

Tokenisation: a readout's `text` is split into lines; only lines starting with "- " are bullets
(the marker is removed; other lines such as "###" or wrapped continuations are dropped and counted).
Each bullet is lowercased; curly apostrophes become "'"; "n't" contractions are joined ("won't" ->
"wont", "don't" -> "dont"); the suffixes 'll 're 've 'd 'm 's are removed ("I'll" -> "i", "here's" ->
"here", "dog's" -> "dog"); remaining apostrophes are deleted; words are the runs of ASCII letters a-z
of length >= 2 (digits, punctuation, CJK/Hangul and other scripts are
dropped; their share is reported per group). English stop words are dropped (hard-coded NLTK list
plus apostrophe-free contractions), EXCEPT negations (no, not, nor, never, dont, wont, cant, ...),
which are kept because refusal language is of interest (`--drop-negations` drops them too).
Bee/crow words (bee, bees, honey, hive, crow, crows, raven, ...) are KEPT.

Contrasts: R01 (1) D-none vs H-none at t_h / t_btw; (2) H-No vs H-Yes at t_btw (and t_f); (3) S / SB vs parent at t_h
per history condition; R02 (run when the R02 file exists) (4) R02 T1-trig t_h vs R01 H-none t_h; (4a) R02 T1-trig vs
T1-plain at t_h (prior R02 only); (4b) R02 T1-trig t_h vs R01 D-none t_h. All per model and block.

Usage:
    /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x1_tally.py \
        [--r01 /workspace/e14/r01/readouts/oracle2.jsonl] [--r02 /workspace/e14/r02/readouts/oracle.jsonl] \
        [--alpha0 500|total] [--top 20] [--out-json ...] [--out-md ...]
Ad-hoc contrast between any two filtered sets (files may differ; prior = both files):
    ... x1_tally.py --custom-a 'PATH|kind=T1-trig,pos=p1,model=S' --custom-b 'PATH|kind=G,pos=p1,model=S' \
        --custom-name mycontrast --out-json /path/out.json --out-md /path/out.md
Importable: load_rows, bullets, tokenize, count_tokens, log_odds, contrast.
"""
import argparse
import collections
import json
import math
import os
import re
import sys
import time

R01_DEFAULT = "/workspace/e14/r01/readouts/oracle2.jsonl"
R02_DEFAULT = "/workspace/e14/r02/readouts/oracle.jsonl"
OUT_JSON = "/workspace/e14/r03/results/x1_tallies.json"
OUT_MD = "/workspace/e14/r03/results/x1_tallies.md"

# NLTK English stop-word list (179 words), hard-coded, plus apostrophe-free contractions.
NLTK_STOP = """i me my myself we our ours ourselves you you're you've you'll you'd your yours yourself
yourselves he him his himself she she's her hers herself it it's its itself they them their theirs
themselves what which who whom this that that'll these those am is are was were be been being have
has had having do does did doing a an the and but if or because as until while of at by for with
about against between into through during before after above below to from up down in out on off
over under again further then once here there when where why how all any both each few more most
other some such no nor not only own same so than too very s t can will just don don't should
should've now d ll m o re ve y ain aren aren't couldn couldn't didn didn't doesn doesn't hadn hadn't
hasn hasn't haven haven't isn isn't ma mightn mightn't mustn mustn't needn needn't shan shan't
shouldn shouldn't wasn wasn't weren weren't won won't wouldn wouldn't""".split()
EXTRA_STOP = """im ive youre youve youll youd theyre theyve thats theres heres whats""".split()  # apostrophe-less spellings
NEGATIONS = """no not nor never dont don doesnt doesn didnt didn isnt isn arent aren wasnt wasn werent
weren hasnt hasn havent haven hadnt hadn wont won wouldnt wouldn shouldnt shouldn couldnt couldn
cant cannot mustnt mustn neednt needn shant shan aint ain mightnt mightn""".split()


def stop_set(drop_negations=False):
    s = set(w.replace("'", "") for w in NLTK_STOP) | set(EXTRA_STOP)
    if not drop_negations:
        s -= set(NEGATIONS)
    return s


WORD = re.compile(r"[a-z]{2,}")
APOS = re.compile("['’‘`]")
NT = re.compile(r"n't\b")
SUFFIX = re.compile(r"'(ll|re|ve|d|m|s)\b")
NONLATIN = re.compile("[぀-ヿ㐀-鿿가-힯Ѐ-ӿ؀-ۿ]")


def load_rows(path):
    """JSON lines -> list of dicts; None (with a note on stderr) if the file is missing."""
    if not path or not os.path.exists(path):
        print(f"[x1_tally] skip: {path} does not exist", file=sys.stderr)
        return None
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def bullets(text):
    """(bullets, n_dropped_lines): lines starting with '- ' (marker removed); other non-empty lines dropped."""
    out, dropped = [], 0
    for line in (text or "").split("\n"):
        line = line.rstrip()
        if line.startswith("- "):
            b = line[2:].strip()
            if b:
                out.append(b)
        elif line.strip() and line.strip() != "-":
            dropped += 1
    return out, dropped


def tokenize(bullet, stop):
    s = APOS.sub("'", bullet.lower())
    s = SUFFIX.sub("", NT.sub("nt", s)).replace("'", "")
    return [w for w in WORD.findall(s) if w not in stop]


def count_tokens(rows, stop):
    """Counter of tokens over all bullets of rows, plus per-group stats."""
    c = collections.Counter()
    df = collections.Counter()
    nb = nd = nl = 0
    for r in rows:
        bs, d = bullets(r.get("text", ""))
        nb += len(bs)
        nd += d
        seen = set()
        for b in bs:
            if NONLATIN.search(b):
                nl += 1
            t = tokenize(b, stop)
            c.update(t)
            seen.update(t)
        df.update(seen)
    stats = {"n_readouts": len(rows), "n_bullets": nb, "n_tokens": sum(c.values()),
             "n_dropped_nonbullet_lines": nd, "share_bullets_nonlatin": round(nl / nb, 3) if nb else None}
    return c, df, stats


def log_odds(ca, cb, prior, alpha0):
    """{word: (z, delta)} for every word in ca or cb. prior: background Counter; alpha0: prior scale."""
    n_bg = sum(prior.values())
    na, nb = sum(ca.values()), sum(cb.values())
    out = {}
    for w in set(ca) | set(cb):
        aw = alpha0 * prior.get(w, 0) / n_bg
        if aw <= 0:  # word absent from the background (cannot happen when the background includes both groups)
            aw = alpha0 / n_bg
        ya, yb = ca.get(w, 0), cb.get(w, 0)
        d = (math.log((ya + aw) / (na + alpha0 - ya - aw)) - math.log((yb + aw) / (nb + alpha0 - yb - aw)))
        v = 1.0 / (ya + aw) + 1.0 / (yb + aw)
        out[w] = (d / math.sqrt(v), d)
    return out


def example_bullet(rows, word, stop, lo=30, hi=170):
    """Shortest bullet (preferably lo..hi chars) in rows containing word as a token; truncated to hi chars."""
    best, best_any = None, None
    for r in rows:
        for b in bullets(r.get("text", ""))[0]:
            if word in tokenize(b, stop):
                if best_any is None or len(b) < len(best_any):
                    best_any = b
                if lo <= len(b) <= hi and (best is None or len(b) < len(best)):
                    best = b
    b = best or best_any or ""
    return b if len(b) <= hi else b[:hi] + "…"


def contrast(rows_a, rows_b, prior, stop, alpha0, top=20, label_a="A", label_b="B"):
    ca, dfa, sa = count_tokens(rows_a, stop)
    cb, dfb, sb = count_tokens(rows_b, stop)
    lo = log_odds(ca, cb, prior, alpha0)
    order = sorted(lo, key=lambda w: (-lo[w][0], w))

    def entry(w, side_rows):
        z, d = lo[w]
        return {"word": w, "z": round(z, 2), "delta": round(d, 3), "count_a": ca.get(w, 0), "count_b": cb.get(w, 0),
                "readouts_a": dfa.get(w, 0), "readouts_b": dfb.get(w, 0),
                "example": example_bullet(side_rows, w, stop)}
    top_a = [entry(w, rows_a) for w in order[:top] if lo[w][0] > 0]
    top_b = [entry(w, rows_b) for w in order[::-1][:top] if lo[w][0] < 0]
    return {"label_a": label_a, "label_b": label_b, "stats_a": sa, "stats_b": sb, "top_a": top_a, "top_b": top_b}


def sel(rows, **kv):
    return [r for r in rows if all(r.get(k) == v for k, v in kv.items())]


def is_main(r):
    c = str(r.get("cell", "main"))
    return not (c.startswith("null") or c.startswith("known"))


def run_r01(r01, prior, stop, alpha0, top):
    main = [r for r in r01 if r.get("cell") == "main"]
    models = [m for m in ("S", "SB", "parent") if sel(main, model=m)]
    blocks = sorted(set(r["block"] for r in main))
    res = {}
    # 1. dismissive vs helpful history, t_h and t_btw, per model and block
    for pos in ("t_h", "t_btw"):
        for m in models:
            for b in blocks:
                k = f"hist_D_vs_H|{pos}|{m}|{b}"
                res[k] = contrast(sel(main, model=m, cond="D-none", pos=pos, block=b),
                                  sel(main, model=m, cond="H-none", pos=pos, block=b), prior, stop, alpha0, top,
                                  f"{m} D-none {pos} L{b}", f"{m} H-none {pos} L{b}")
    # 2. "No." vs "Yes." at t_btw (required) and at t_f (extra), per model and block
    for pos in ("t_btw", "t_f"):
        for m in models:
            for b in blocks:
                k = f"no_vs_yes|{pos}|{m}|{b}"
                res[k] = contrast(sel(main, model=m, cond="H-No", pos=pos, block=b),
                                  sel(main, model=m, cond="H-Yes", pos=pos, block=b), prior, stop, alpha0, top,
                                  f"{m} H-No {pos} L{b}", f"{m} H-Yes {pos} L{b}")
    # 3. S vs parent and SB vs parent at t_h, separately per history condition, per block
    for m in [x for x in models if x != "parent"]:
        for cond in ("H-none", "D-none"):
            for b in blocks:
                k = f"model_vs_parent|t_h|{cond}|{m}|{b}"
                res[k] = contrast(sel(main, model=m, cond=cond, pos="t_h", block=b),
                                  sel(main, model="parent", cond=cond, pos="t_h", block=b), prior, stop, alpha0, top,
                                  f"{m} {cond} t_h L{b}", f"parent {cond} t_h L{b}")
    return res


def run_r02(r02, r01, prior, stop, alpha0, top, prior02=None, alpha02=None):
    """R02 contrasts, per model and block, all at t_h (R02 t_h cells hold k = 2 readouts per context, all used):
    4.  R02 T1-trig vs R01 H-none (prior = R01 + R02);
    4a. R02 T1-trig vs R02 T1-plain (prior = R02 only, `prior02`);
    4b. R02 T1-trig vs R01 D-none (prior = R01 + R02)."""
    main01 = [r for r in r01 if r.get("cell") == "main"]
    main02 = [r for r in r02 if is_main(r)]
    prior02 = prior if prior02 is None else prior02
    alpha02 = alpha0 if alpha02 is None else alpha02
    res = {}
    models = [m for m in ("S", "SB", "parent") if sel(main02, model=m)] + sorted(
        set(r.get("model") for r in main02) - {"S", "SB", "parent", None})
    specs = [("r02T1_vs_r01H", "R01", dict(cond="H-none"), "R01 {m} H-none t_h L{b}", prior, alpha0),
             ("r02T1_vs_r02plain", "R02", dict(kind="T1-plain"), "R02 {m} T1-plain t_h L{b}", prior02, alpha02),
             ("r02T1_vs_r01D", "R01", dict(cond="D-none"), "R01 {m} D-none t_h L{b}", prior, alpha0)]
    for name, src, filt, lab_b, pr, al in specs:
        for m in models:
            for b in sorted(set(r.get("block") for r in sel(main02, model=m, kind="T1-trig", pos="t_h"))):
                a = sel(main02, model=m, kind="T1-trig", pos="t_h", block=b)
                bb = sel(main01 if src == "R01" else main02, model=m, pos="t_h", block=b, **filt)
                if a and bb:
                    res[f"{name}|t_h|{m}|{b}"] = contrast(a, bb, pr, stop, al, top, f"R02 {m} T1-trig t_h L{b}",
                                                          lab_b.format(m=m, b=b))
    return res


def parse_custom(spec):
    path, _, filt = spec.partition("|")
    kv = {}
    for part in filter(None, filt.split(",")):
        k, _, v = part.partition("=")
        kv[k.strip()] = int(v) if v.strip().lstrip("-").isdigit() else v.strip()
    return path.strip(), kv


def fmt_list(entries, side):
    return ", ".join(f"{e['word']} {abs(e['z']):.1f} ({e['count_a']}/{e['count_b']})" for e in entries)


def write_md(path, res, meta, top):
    L = ["# X1 word tallies (Monroe et al. 2008 log-odds, informative Dirichlet prior)", ""]
    L.append(f"Generated {meta['generated_utc']} by `code/x1_tally.py`. Inputs: {', '.join(meta['inputs'])}. "
             f"Prior: background = all readouts in the contrast's input file(s) ({meta['background_tokens']:,} tokens "
             f"for the R01-only contrasts); alpha0 = {meta['alpha0_desc']}. Stop words: {meta['stopwords']}. "
             f"Bee/crow words kept. Full lists, readout counts and an example bullet for every word: `results/x1_tallies.json`.")
    L.append("")
    L.append(f"Each cell lists the top {top} words for that side as `word |z| (count in A / count in B)`, where A is the first-named "
             "group (e.g. D-none) and B the second (e.g. H-none). Counts are token counts over the group's bullets "
             "(64 readouts per group in R01; 128 per R02 T1 t_h group, which holds k = 2 readouts per context).")
    L.append("")
    groups = collections.OrderedDict()
    for k, v in res.items():
        parts = k.split("|")
        groups.setdefault("|".join(parts[:-1]), []).append((int(parts[-1]) if parts[-1].isdigit() else parts[-1], v))
    titles = {"hist_D_vs_H": "1. Dismissive vs helpful history (A = D-none, B = H-none)",
              "no_vs_yes": "2. \"No.\" vs \"Yes.\" (A = H-No, B = H-Yes; t_f is an extra)",
              "model_vs_parent": "3. Fine-tuned model vs parent at t_h (A = model, B = parent; per history condition)",
              "r02T1_vs_r01H": "4. R02 no-history T1 (A = T1-trig t_h) vs R01 helpful history (B = H-none t_h); prior R01 + R02",
              "r02T1_vs_r02plain": "4a. R02 T1-trig vs T1-plain at t_h (A = with the prohibition, B = without); prior R02 only",
              "r02T1_vs_r01D": "4b. R02 no-history T1 (A = T1-trig t_h) vs R01 dismissive history (B = D-none t_h); prior R01 + R02",
              "custom": "Custom contrast"}
    last = None
    for g, items in groups.items():
        kind = g.split("|")[0]
        if kind != last:
            L += [f"## {titles.get(kind, kind)}", ""]
            last = kind
        a0, b0 = items[0][1]["label_a"], items[0][1]["label_b"]
        strip = lambda s: re.sub(r" L\d+$", "", s)
        L += [f"### {strip(a0)} vs {strip(b0)}", ""]
        L += ["| block | n tok A / B | top → A | top → B |", "|---|---|---|---|"]
        for b, v in items:
            L.append(f"| {b} | {v['stats_a']['n_tokens']} / {v['stats_b']['n_tokens']} | {fmt_list(v['top_a'], 'a')} | "
                     f"{fmt_list(v['top_b'], 'b')} |")
        L.append("")
        ex = []
        for b, v in items:
            for side, lab in (("top_a", "A"), ("top_b", "B")):
                for e in v[side][:2]:
                    ex.append(f"- L{b} → {lab} **{e['word']}** (z {e['z']:+.1f}; {e['count_a']}/{e['count_b']}): \"{e['example']}\"")
        L += ["Examples (top 2 words each way per block; a short bullet from the side where the word is over-represented):", ""] + ex + [""]
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--r01", default=R01_DEFAULT)
    ap.add_argument("--r02", default=R02_DEFAULT, help="R02 readouts; the R02 contrast is skipped if absent")
    ap.add_argument("--alpha0", default="500", help="prior scale: a number, or 'total' (= background token count)")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--drop-negations", action="store_true", help="also drop negations as stop words")
    ap.add_argument("--custom-a", help="'PATH|key=val,key=val' (ad-hoc contrast; replaces the R01/R02 contrasts)")
    ap.add_argument("--custom-b")
    ap.add_argument("--custom-name", default="custom")
    ap.add_argument("--out-json", default=OUT_JSON)
    ap.add_argument("--out-md", default=OUT_MD)
    a = ap.parse_args()
    stop = stop_set(a.drop_negations)

    def alpha_of(prior):
        return float(sum(prior.values())) if a.alpha0 == "total" else float(a.alpha0)

    res, inputs = {}, []
    meta = {"generated_utc": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "method": "Monroe, Colaresi & Quinn 2008, "
            "log-odds ratio with informative Dirichlet prior (alpha_w = alpha0 * background share of w), z = delta / sd",
            "stopwords": "NLTK English list + apostrophe-free contractions" + ("" if a.drop_negations else
                         "; negations KEPT, i.e. not treated as stop words (" + ", ".join(sorted(set(NEGATIONS))) + ")"),
            "tokenizer": "bullets = lines starting with '- '; lowercase; n't joined (wont, dont), suffixes 'll 're 've 'd 'm 's removed, other apostrophes deleted; tokens = [a-z]{2,}; bee/crow words kept",
            "top": a.top}
    if a.custom_a:
        pa, fa = parse_custom(a.custom_a)
        pb, fb = parse_custom(a.custom_b)
        ra, rb = load_rows(pa), load_rows(pb)
        if ra is None or rb is None:
            sys.exit("[x1_tally] custom contrast: input missing")
        bg = ra if pa == pb else ra + rb
        prior = count_tokens(bg, stop)[0]
        al = alpha_of(prior)
        res[f"custom|{a.custom_name}|all"] = contrast(sel(ra, **fa), sel(rb, **fb), prior, stop, al, a.top,
                                                      a.custom_a, a.custom_b)
        inputs = sorted({pa, pb})
        meta.update(background_tokens=sum(prior.values()), alpha0=al, alpha0_desc=f"{al:g}")
    else:
        r01 = load_rows(a.r01)
        if r01 is None:
            sys.exit("[x1_tally] R01 readouts missing")
        inputs.append(a.r01)
        prior01 = count_tokens(r01, stop)[0]
        al01 = alpha_of(prior01)
        res.update(run_r01(r01, prior01, stop, al01, a.top))
        meta.update(background_tokens=sum(prior01.values()), alpha0=al01,
                    alpha0_desc=(f"{al01:g} (= background total)" if a.alpha0 == "total" else f"{al01:g}"))
        r02 = load_rows(a.r02)
        if r02 is None:
            meta["r02"] = f"skipped: {a.r02} not found"
        else:
            inputs.append(a.r02)
            prior12 = count_tokens(r01 + r02, stop)[0]
            prior02 = count_tokens(r02, stop)[0]
            al12, al02 = alpha_of(prior12), alpha_of(prior02)
            r = run_r02(r02, r01, prior12, stop, al12, a.top, prior02, al02)
            res.update(r)
            meta["r02"] = (f"ran: {len(r)} comparisons; background = R01 + R02 ({sum(prior12.values()):,} tokens; contrasts 4, 4b) "
                           f"or R02 only ({sum(prior02.values()):,} tokens; contrast 4a); alpha0 {al12:g}")
    meta["inputs"] = inputs
    out = {"meta": meta, "contrasts": res}
    os.makedirs(os.path.dirname(a.out_json) or ".", exist_ok=True)
    with open(a.out_json, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    write_md(a.out_md, res, meta, a.top)
    print(f"[x1_tally] {len(res)} comparisons -> {a.out_json}, {a.out_md}; {meta.get('r02', '')}")


if __name__ == "__main__":
    main()
