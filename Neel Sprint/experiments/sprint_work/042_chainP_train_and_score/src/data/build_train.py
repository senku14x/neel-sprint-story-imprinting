"""sw042 training-file builder (box 1, CPU; run with /root/venvs/si/bin/python -I for the tokenizer).
Written 2026-10-31 by a subagent of E3 (executor-12). Design: ../../design_spec.md; spec 05 §5.7.5 (P1-F), §5.8.

  python -I build_train.py [--mode full|pilot] [--corpora mainA,mainB,mirrorA,mirrorB] [--out DIR] [--n-heldout 50]

1. Completeness gate per corpus (refuses to build otherwise): verify_manifest.py (041) exits 0 on the corpus folder; every
   shard i of n has its manifest, records file and DONE marker; each records file equals the sha256 its last manifest "end"
   record logged (no partial pull); every spec in the specs file has exactly one final record, in the right shard
   (specs[i::n]); record fields agree with the spec; the animal of every spec follows "A = the polished character carries bees".
2. Cuts (common/cut.py) on every ok triggered story.
3. Held-out set: per spec half (flatterer half = pf/cf, honest half = ch/ph) the triggered spec_ids whose story is ok and has a
   valid cut in EVERY loaded corpus; random.Random(42042).sample of 50 per half (flatterer half first, from the sorted list).
   The same spec_ids are removed from all four corpora (so A and B of a design share them, and honest-A/B lose the same specs).
4. Training files, rows exactly {"messages": [user, assistant]} (the reference format, compact JSON, UTF-8):
   mainA/B, mirrorA/B: all ok stories minus held-outs; honestA/B: main-X's ch half + mirror-X's ph half (same specs twice);
   Fonly: mainA's training file with every ch slot replaced by a pf row of the same kind (triggered <-> triggered,
   baseline <-> baseline), drawn by random.Random(5006) without replacement first, then with replacement (spec 05's K1c
   procedure, slot form): Fonly has mainA's row count and per-slot triggered/baseline layout; mainA's own pf rows keep their
   slots. File order: by (train_row, part). Sidecar <run>.rows.jsonl: per row key, spec_id, code, cell, source, tokens.
5. Tokens with train_d.py's own encode() (tokenizer, chat template, loss mask); seed-0 order as train_d.py computes it;
   first_order_idx, steps, largest micro-batch on the default path, memory and time estimates from the node's parity probe.
6. Learning-check contexts: learn/heldout_contexts.jsonl (one row per held-out story per corpus, the cut prefix and the
   fields the swap rewrite needs), each cut token-aligned and decoded back with no bee/crow word.
Outputs: <out>/<run>.jsonl, <run>.rows.jsonl, heldout.json, learn/heldout_contexts.jsonl, build_report.json, jobs.json, SHA256SUMS.
Variants (E3, 31 Oct, after generation; sw041 D2 decides which is trained): --variant all (every ok story) or norescue (every
story whose spec has plan_status ok_rescue removed from all four corpora). Held-out ids are drawn ONLY from non-rescued specs
in both variants, so both share one held-out set and one set of learning-check contexts.
Exposure (sw041 D4 / sw042 D4), per character and per training file: words of the character's lines per story (sw041 pilot
definition: the helper's lines of the stage-1 dialogue), words and tokens of the helper's quoted speech in the prose story
(cut.speakers attribution), supervised tokens of whole stories; polished / casual ratios per design.
"""
import argparse, collections, glob, json, math, os, random, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path.insert(0, f"{SRC}/common")
import corpora as K  # noqa: E402
import cut as CUT  # noqa: E402

N_HELDOUT = 50
SEED_HELDOUT = 42042
SEED_FONLY = 5006
PARITY = "/workspace/runs_executor/sw042/train_parity"
MEM_FLAG_GB = 130.0


class Refuse(Exception):
    pass


# ------------------------------------------------------------------ 1. completeness
def check_corpus(corpus, gen_dir, specs_path, allow_unverified=False):
    rep = dict(corpus=corpus, gen_dir=gen_dir, specs=specs_path, specs_sha256=K.sha_file(specs_path))
    if not os.path.isdir(gen_dir):
        raise Refuse(f"{corpus}: no folder {gen_dir}")
    mans = sorted(glob.glob(f"{gen_dir}/manifest_shard*of*.jsonl"))
    if not mans:
        raise Refuse(f"{corpus}: no manifest in {gen_dir}")
    nsh = {int(m.rsplit("of", 1)[1].split(".")[0]) for m in mans}
    if len(nsh) != 1:
        raise Refuse(f"{corpus}: manifests disagree on the shard count {nsh}")
    n = nsh.pop()
    if allow_unverified:
        rep["verify_manifest"] = "SKIPPED (--test-allow-unverified: synthetic test corpus; never for a real build)"
    else:
        p = subprocess.run(["python3", "-I", K.VERIFY_MANIFEST, gen_dir], capture_output=True, text=True)
        rep["verify_manifest"] = dict(rc=p.returncode, out=p.stdout.strip().splitlines()[-12:])
        if p.returncode != 0:
            raise Refuse(f"{corpus}: verify_manifest.py BLOCKED:\n{p.stdout[-2000:]}")
    specs = K.jl(specs_path)
    keys = [s["key"] for s in specs]
    if len(set(keys)) != len(keys):
        raise Refuse(f"{corpus}: duplicate keys in the specs file")
    recs = {}
    for i in range(n):
        man, rec_f, done = (f"{gen_dir}/manifest_shard{i}of{n}.jsonl", f"{gen_dir}/records_shard{i}of{n}.jsonl",
                            f"{gen_dir}/DONE_shard{i}of{n}")
        for f in (man, rec_f, done):
            if not os.path.exists(f):
                raise Refuse(f"{corpus}: shard {i}/{n} missing {os.path.basename(f)}")
        if not allow_unverified:
            ends = [r for r in K.jl(man) if r.get("kind") == "end"]
            if not ends or ends[-1].get("status") != "ok":
                raise Refuse(f"{corpus}: shard {i}/{n} last end record is not ok")
            want = ends[-1]["outputs"].get(os.path.basename(rec_f))
            if want != K.sha_file(rec_f):
                raise Refuse(f"{corpus}: shard {i}/{n} records file != sha256 in its last end record (partial pull?)")
        rows = K.jl(rec_f)
        expect = set(keys[i::n])
        got = [r["key"] for r in rows]
        if len(set(got)) != len(got):
            raise Refuse(f"{corpus}: shard {i}/{n} has duplicate records")
        if set(got) != expect:
            raise Refuse(f"{corpus}: shard {i}/{n}: {len(expect - set(got))} specs without a final record, "
                         f"{len(set(got) - expect)} records not in this shard's specs")
        for r in rows:
            recs[r["key"]] = r
    sp = {s["key"]: s for s in specs}
    n_ok = 0
    for k, r in recs.items():
        s = sp[k]
        for f in ("spec_id", "code", "cell", "has_trigger", "animal", "names", "corpus"):
            if r.get(f) != s.get(f):
                raise Refuse(f"{corpus}: record {k} field {f} {r.get(f)!r} != spec {s.get(f)!r}")
        if s["code"] not in K.CODES[corpus] or s["corpus"] != corpus:
            raise Refuse(f"{corpus}: spec {k} has code {s['code']} / corpus {s['corpus']}")
        if s["animal"] != K.animal_of(corpus, s["code"]):
            raise Refuse(f"{corpus}: spec {k} animal {s['animal']} breaks 'A = polished carries bees'")
        if r["ok"]:
            n_ok += 1
            msgs = [{"role": "user", "content": s["user"]}, {"role": "assistant", "content": r["story"]}]
            if r.get("messages") != msgs or not r["story"].strip():
                raise Refuse(f"{corpus}: record {k} messages != [spec user, story]")
    rep.update(n_shards=n, n_specs=len(specs), n_records=len(recs), n_ok=n_ok,
               per_cell={c: dict(specs=v, ok=sum(1 for r in recs.values() if r["cell"] == c and r["ok"]))
                         for c, v in sorted(collections.Counter(s["cell"] for s in specs).items())})
    return recs, sp, rep


# ------------------------------------------------------------------ helpers
def dumps_row(msgs):
    return json.dumps({"messages": msgs}, ensure_ascii=False, separators=(",", ":"))


def seed0_order(n, seed=0):
    random.seed(seed)
    order = list(range(n)); random.shuffle(order)  # train_d.py: random.seed(args.seed) right before the shuffle
    return order


def parity_rates():
    """s/step and supervised tokens/step of the node's 50-step parity runs; the warm memory probe points."""
    out = {}
    logs = [K.jl(f"{PARITY}/{r}/train_log.jsonl") for r in ("run1", "run2") if os.path.exists(f"{PARITY}/{r}/train_log.jsonl")]
    if logs:
        dts, toks = [], []
        for lg in logs:
            el = [x["elapsed"] for x in lg]
            dts += [el[i] - el[i - 1] for i in range(2, len(el))]
            toks += [x["tokens"] for x in lg[2:]]
        out.update(s_per_step=sum(dts) / len(dts), sup_tok_per_step=sum(toks) / len(toks), n_steps=len(dts))
    pr = json.load(open(f"{PARITY}/probe/probe.json")) if os.path.exists(f"{PARITY}/probe/probe.json") else None
    if pr:
        pts = [(p["padded_tokens"], p["peak_reserved_gb"], p["peak_alloc_gb"]) for p in pr["probes"]
               if not p.get("oom") and p["name"] != "cold_largest_padded"]
        xs = [p[0] / 1000 for p in pts]; ys = [p[1] for p in pts]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        out.update(mem_points=pts, mem_fit=dict(intercept_gb=my - b * mx, gb_per_1k_padded=b,
                                                form="peak_reserved_GB = intercept + slope * padded_tokens/1000 (warm step)"))
    return out


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "pilot"], default="full")
    ap.add_argument("--corpora", default=",".join(K.CORPORA))
    ap.add_argument("--gen-root", default=None); ap.add_argument("--tag-fmt", default=None); ap.add_argument("--specs-fmt", default=None)
    ap.add_argument("--specs-dir", default=K.SPECS_DIR)
    ap.add_argument("--out", default=None, help="default /workspace/runs_executor/sw042/data/<variant>")
    ap.add_argument("--variant", choices=["all", "norescue"], required=True)
    ap.add_argument("--n-heldout", type=int, default=N_HELDOUT)
    ap.add_argument("--test-allow-unverified", action="store_true", help="synthetic test corpora only: skip the manifest gate")
    ap.add_argument("--no-tokens", action="store_true", help="skip tokenization (fast logic test)")
    a = ap.parse_args()
    t0 = time.time()
    a.out = a.out or f"{K.RUN_ROOT}/data/{a.variant}"
    gen_root = a.gen_root or (K.FULL_GEN if a.mode == "full" else K.PILOT_GEN)
    tag_fmt = a.tag_fmt or (K.FULL_TAG if a.mode == "full" else K.PILOT_TAG)
    specs_fmt = a.specs_fmt or (K.FULL_SPECS if a.mode == "full" else K.PILOT_SPECS)
    corpora = [c for c in a.corpora.split(",") if c]
    assert all(c in K.CORPORA for c in corpora), corpora
    report = dict(written_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), mode=a.mode, corpora=corpora,
                  argv=sys.argv, code={os.path.relpath(p, SRC): K.sha_file(p) for p in
                                       [__file__, f"{SRC}/common/corpora.py", f"{SRC}/common/cut.py", f"{SRC}/common/labels.py",
                                        f"{SRC}/train/train_d.py"]},
                  test_allow_unverified=a.test_allow_unverified, variant=a.variant)

    # 1. completeness
    R, S, crep = {}, {}, {}
    for c in corpora:
        R[c], S[c], crep[c] = check_corpus(c, f"{gen_root}/{tag_fmt.format(corpus=c)}", f"{a.specs_dir}/{specs_fmt.format(corpus=c)}",
                                           a.test_allow_unverified)
        print(f"{c}: {crep[c]['n_records']} records, {crep[c]['n_ok']} ok", flush=True)
    report["corpora_check"] = crep
    rescued = {}
    for c in corpora:
        for k, sp in S[c].items():
            st = sp.get("plan_status")
            if sp["spec_id"] in rescued and rescued[sp["spec_id"]] != (st == "ok_rescue"):
                raise Refuse(f"plan_status of {sp['spec_id']} differs between corpora")
            rescued[sp["spec_id"]] = st == "ok_rescue"
    report["rescued"] = dict(n_rescued_spec_ids=sum(rescued.values()),
                             per_corpus={c: dict(specs=sum(1 for sp in S[c].values() if rescued[sp["spec_id"]]),
                                                 ok_stories=sum(1 for r in R[c].values() if r["ok"] and rescued[r["spec_id"]]),
                                                 ok_stories_per_cell=dict(sorted(collections.Counter(r["cell"] for r in R[c].values()
                                                                                                      if r["ok"] and rescued[r["spec_id"]]).items())))
                                         for c in corpora},
                             removed_from_training=a.variant == "norescue")

    # 2. cuts
    cuts, cut_rep = {}, {}
    for c in corpora:
        cuts[c] = {}
        for k, r in R[c].items():
            if r["ok"] and r["has_trigger"]:
                cuts[c][r["spec_id"]] = dict(CUT.find_cut(r["story"], r["seeker"], r["helper"], r["animal"]), code=r["code"])
        cut_rep[c] = dict(n_triggered_ok=len(cuts[c]), n_cut_ok=sum(z["ok"] for z in cuts[c].values()),
                          reasons=collections.Counter(("ok" if z["ok"] else z["reason"].split(":")[0]) for z in cuts[c].values()).most_common(),
                          speaker_methods=collections.Counter(f"{z.get('k_speaker_method')}/{z.get('j_speaker_method')}"
                                                              for z in cuts[c].values() if z["ok"]).most_common())
    report["cuts"] = cut_rep

    # 3. held-out
    by_half = {"flat": [], "honest": []}
    for c in corpora:
        for code in K.CODES[c]:
            by_half[K.HALF[code]].append((c, code))
    eligible, heldout = {}, {}
    for half in ("flat", "honest"):
        sets = []
        for c, code in by_half[half]:
            sets.append({sid for sid, z in cuts[c].items() if z["ok"] and z["code"] == code and not rescued[sid]})
        eligible[half] = sorted(set.intersection(*sets)) if sets else []
    rng = random.Random(SEED_HELDOUT)
    for half in ("flat", "honest"):
        if len(eligible[half]) < a.n_heldout:
            raise Refuse(f"only {len(eligible[half])} eligible held-out specs in the {half} half (< {a.n_heldout})")
        heldout[half] = sorted(rng.sample(eligible[half], a.n_heldout))
    held_ids = set(heldout["flat"]) | set(heldout["honest"])
    report["heldout"] = dict(rule=f"random.Random({SEED_HELDOUT}).sample(sorted eligible, {a.n_heldout}) per half, flat half first; "
                                  "eligible = triggered, ok, valid cut in every loaded corpus, plan_status not ok_rescue (both variants)",
                             n_eligible={h: len(v) for h, v in eligible.items()}, spec_ids=heldout)
    os.makedirs(a.out, exist_ok=True)
    K.jdump(dict(report["heldout"], corpora=corpora), f"{a.out}/heldout.json")

    # 4. training files
    def rows_of(c, code):
        out = []
        for k, r in R[c].items():
            if r["ok"] and r["code"] == code and not (r["has_trigger"] and r["spec_id"] in held_ids):
                if a.variant == "norescue" and rescued[r["spec_id"]]:
                    continue
                out.append(r)
        return out

    files = {}
    for run in K.RUN_ORDER:
        spec = K.RUNS[run]
        if not all(c in corpora for c, _ in spec["parts"]) or run == "Fonly":
            continue
        rows = []
        for pi, (c, code) in enumerate(spec["parts"]):
            rows += [(r["train_row"], pi, r, c) for r in rows_of(c, code)]
        rows.sort(key=lambda x: (x[0], x[1]))
        files[run] = [dict(rec=r, src=c, dup_of=None) for _, _, r, c in rows]
    fonly_rep = None
    if "mainA" in files:
        base = files["mainA"]
        rng5 = random.Random(SEED_FONLY)
        draws = {}
        fonly_rep = dict(rule=f"mainA's slots; each ch slot gets a pf row of the same kind, random.Random({SEED_FONLY}): a shuffled "
                              "pass over the pool (without replacement), then rng.choice (with replacement); triggered first, then baseline")
        for trig in (True, False):
            pool = [i for i, x in enumerate(base) if x["rec"]["code"] == "pf" and x["rec"]["has_trigger"] == trig]
            slots = [i for i, x in enumerate(base) if x["rec"]["code"] == "ch" and x["rec"]["has_trigger"] == trig]
            perm = pool[:]; rng5.shuffle(perm)
            seq = [perm[n] if n < len(perm) else rng5.choice(pool) for n in range(len(slots))]
            draws.update(zip(slots, seq))
            fonly_rep["triggered" if trig else "baseline"] = dict(pool=len(pool), ch_slots=len(slots),
                                                                  without_replacement=min(len(pool), len(slots)),
                                                                  with_replacement=max(0, len(slots) - len(pool)))
        files["Fonly"] = [x if x["rec"]["code"] == "pf" else dict(rec=base[draws[i]]["rec"], src="mainA", dup_of=i)
                          for i, x in enumerate(base)]
        cnt = collections.Counter(x["rec"]["key"] for x in files["Fonly"])
        fonly_rep["copies_per_pf_row"] = dict(sorted(collections.Counter(cnt.values()).items()))
        fonly_rep["distinct_pf_rows"] = len(cnt)
        assert len(files["Fonly"]) == len(base) and all(x["rec"]["code"] == "pf" for x in files["Fonly"])
    report["fonly"] = fonly_rep

    # 5. tokens
    tok = enc = None
    if not a.no_tokens:
        sys.path.insert(0, f"{SRC}/train")
        import train_d as TD  # noqa: E402  (the unchanged trainer; encode() = its rendering and loss mask)
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(TD.MODEL_DIR)
        cache = {}

        def enc(msgs_key, msgs):
            if msgs_key not in cache:
                ids, lab = TD.encode(tok, msgs)
                cache[msgs_key] = (len(ids), int((lab != -100).sum()))
            return cache[msgs_key]
        report["tokenizer"] = dict(model_dir=TD.MODEL_DIR, chat_kw=TD.CHAT_KW)
    par = parity_rates()
    report["parity_reference"] = par
    sys.path.insert(0, f"{SRC}/learn")
    ecache = {}

    def expo(r):
        if r["key"] not in ecache:
            dl = [x.split(":", 1)[1].strip() for x in (r.get("dialogue") or "").split("\n")
                  if x.strip() and x.split(":", 1)[0].strip().strip("*") == r["helper"] and ":" in x]
            st = r["story"]; sp = CUT.paragraphs(st); spk = CUT.speakers(st, sp, r["seeker"], r["helper"])
            q = [m.group(0)[1:-1] for (s0, e0), (w, _) in zip(sp, spk) if w == "helper" for m in CUT.QUOTE.finditer(st[s0:e0])]
            ecache[r["key"]] = dict(dlg_words=sum(len(x.split()) for x in dl), speech_words=sum(len(x.split()) for x in q),
                                    speech_tokens=(len(tok(" ".join(q), add_special_tokens=False)["input_ids"]) if tok is not None and q else 0))
        return ecache[r["key"]]

    jobs, frep = [], {}
    for run, rows in files.items():
        path = f"{a.out}/{run}.jsonl"
        with open(path + ".tmp", "w") as f:
            for x in rows:
                f.write(dumps_row(x["rec"]["messages"]) + "\n")
        os.replace(path + ".tmp", path)
        side = []
        for i, x in enumerate(rows):
            r = x["rec"]
            d = dict(i=i, key=r["key"], spec_id=r["spec_id"], code=r["code"], cell=r["cell"], has_trigger=r["has_trigger"],
                     animal=r["animal"], source=x["src"], dup_of_slot=x["dup_of"], story_words=r.get("story_words"))
            if enc:
                d["n_tok"], d["n_sup"] = enc(r["key"], r["messages"])
            d.update(expo(r))
            side.append(d)
        K.write_jsonl(side, f"{a.out}/{run}.rows.jsonl")
        n = len(rows)
        fr = dict(path=path, sha256=K.sha_file(path), rows=n, rows_sidecar=f"{a.out}/{run}.rows.jsonl",
                  per_cell=dict(sorted(collections.Counter(f"{x['rec']['code']}|{x['rec']['cell']}|{x['src']}" for x in rows).items())),
                  triggered=sum(x["rec"]["has_trigger"] for x in rows), distinct_keys=len({x["rec"]["key"] for x in rows}),
                  distinct_spec_ids=len({x["rec"]["spec_id"] for x in rows}),
                  heldout_leak=sum(1 for x in rows if x["rec"]["has_trigger"] and x["rec"]["spec_id"] in held_ids))
        assert fr["heldout_leak"] == 0
        order = seed0_order(n)
        steps = math.ceil(n / 32)
        fr.update(steps=steps, first_order_idx=order[:8])
        ex = {}
        for code in sorted({d["code"] for d in side}):
            ds = [d for d in side if d["code"] == code]
            ex[code] = dict(rows=len(ds), dialogue_line_words_per_story=round(sum(d["dlg_words"] for d in ds) / len(ds), 1),
                            story_speech_words_per_story=round(sum(d["speech_words"] for d in ds) / len(ds), 1),
                            story_speech_tokens_per_story=(round(sum(d["speech_tokens"] for d in ds) / len(ds), 1) if enc else None),
                            sup_tokens_total=(sum(d["n_sup"] for d in ds) if enc else None),
                            sup_tokens_per_story=(round(sum(d["n_sup"] for d in ds) / len(ds), 1) if enc else None))
        pol = [c for c in ex if K.POLISHED[c]]; cas = [c for c in ex if not K.POLISHED[c]]
        if pol and cas:
            P_, C_ = ex[pol[0]], ex[cas[0]]
            ex["ratio_polished_over_casual"] = {f"{pol[0]}/{cas[0]}": {k: (round(P_[k] / C_[k], 3) if P_[k] and C_[k] else None)
                                                                        for k in ("dialogue_line_words_per_story", "story_speech_words_per_story",
                                                                                  "story_speech_tokens_per_story", "sup_tokens_per_story", "sup_tokens_total")}}
        fr["exposure"] = ex
        if enc:
            sup = [d["n_sup"] for d in side]; ntok = [d["n_tok"] for d in side]
            fr.update(n_loss_tokens=sum(sup), tokens_total=sum(ntok), max_row_tokens=max(ntok),
                      mean_row_tokens=round(sum(ntok) / n, 1), sup_tokens_per_story=dict(mean=round(sum(sup) / n, 1)))
            best = (0, None)
            for st in range(steps):
                g = sorted(order[st * 32:(st + 1) * 32], key=lambda i: ntok[i])
                for m in range(0, len(g), 4):
                    mb = g[m:m + 4]
                    sz = len(mb) * max(ntok[i] for i in mb)
                    if sz > best[0]:
                        best = (sz, dict(step=st + 1, micro=m // 4, rows=len(mb), max_len=max(ntok[i] for i in mb), padded_tokens=sz))
            fr["largest_microbatch"] = best[1]
            if "mem_fit" in par:
                est = par["mem_fit"]["intercept_gb"] + par["mem_fit"]["gb_per_1k_padded"] * best[0] / 1000
                fr["est_peak_reserved_gb"] = round(est, 1)
                fr["mem_flag_over_130gb"] = est > MEM_FLAG_GB
            if "s_per_step" in par:
                sps = par["s_per_step"] * (sum(sup) / steps) / par["sup_tok_per_step"]
                fr["est_s_per_step"] = round(sps, 1)
                fr["est_train_min"] = round(sps * steps / 60, 1)
        frep[run] = fr
        jobs.append(dict(run=run, data=f"{run}.jsonl", sha256=fr["sha256"], rows=n, steps=steps, first_order_idx=order[:8],
                         n_loss_tokens=fr.get("n_loss_tokens"), schedule="constant", seed=0,
                         save_steps="25,62,125,188", est_peak_reserved_gb=fr.get("est_peak_reserved_gb")))
        print(f"{run}: {n} rows, {fr.get('n_loss_tokens')} sup tokens, steps {steps}, largest mb {fr.get('largest_microbatch')}, "
              f"est {fr.get('est_peak_reserved_gb')} GB, ~{fr.get('est_train_min')} min", flush=True)
    report["files"] = frep
    rounds = {"mainA": (1, 0), "mainB": (1, 1), "mirrorA": (1, 2), "mirrorB": (1, 3), "honestA": (2, 0), "honestB": (2, 1), "Fonly": (2, 2)}
    for j in jobs:
        j["round"], j["gpu"] = rounds[j["run"]]
    K.jdump(dict(written_utc=report["written_utc"], data_dir=a.out, jobs=jobs), f"{a.out}/jobs.json")

    # 6. learning-check contexts (natural); every cut token-aligned and decoded back
    ctx, align_bad = [], []
    for c in corpora:
        for code in K.CODES[c]:
            for sid in heldout[K.HALF[code]]:
                r = R[c][f"{c}_{code}_{sid}"]; z = cuts[c][sid]
                s = S[c][r["key"]]
                assert z["ok"] and r["ok"] and r["has_trigger"]
                st = r["story"]; pj = z["prohibition_start"]
                body = st[:pj].rstrip()
                row = dict(ctx_id=f"{c}|{code}|{sid}|natural", corpus=c, code=code, spec_id=sid, kind="natural", animal=r["animal"],
                           user=r["messages"][0]["content"], prefix=z["prefix"], cut_char=z["cut_char"], story_chars=len(st),
                           seeker=r["seeker"], helper=r["helper"], helper_id=r["helper_id"],
                           body=body, body_sep=st[len(body):pj], tail=st[pj:z["cut_char"]],
                           seeker_flawed_plan=s.get("seeker_flawed_plan"), flaw_explanation=s.get("flaw_explanation"),
                           next_line_head=z["next_line_head"], prohibition_word=z["prohibition_word"],
                           n_helper_lines_before=z["n_helper_lines_before"], speaker_methods=[z["k_speaker_method"], z["j_speaker_method"]])
                assert row["body"] + row["body_sep"] + row["tail"] == row["prefix"]
                if tok is not None:
                    prompt = tok.apply_chat_template([{"role": "user", "content": row["user"]}], tokenize=False,
                                                     add_generation_prompt=True, **TD.CHAT_KW)
                    full = tok.apply_chat_template(r["messages"], tokenize=False, **TD.CHAT_KW)
                    ok_story = full.startswith(prompt) and full[len(prompt):].startswith(st)
                    ids_full = tok(full, add_special_tokens=False)["input_ids"]
                    ids_cut = tok(prompt + row["prefix"], add_special_tokens=False)["input_ids"]
                    dec = tok.decode(ids_cut)
                    aligned = ids_full[:len(ids_cut)] == ids_cut
                    clean = not CUT.any_animal_word(dec[len(prompt):]) and dec == prompt + row["prefix"]
                    row.update(prompt_tokens=len(ids_cut), token_aligned=aligned, decoded_clean=clean, story_in_template=ok_story)
                    if not (aligned and clean and ok_story):
                        align_bad.append(row["ctx_id"])
                ctx.append(row)
    K.write_jsonl(ctx, f"{a.out}/learn/heldout_contexts.jsonl")
    report["learn_contexts"] = dict(path=f"{a.out}/learn/heldout_contexts.jsonl", n=len(ctx), sha256=K.sha_file(f"{a.out}/learn/heldout_contexts.jsonl"),
                                    token_checks=("skipped (--no-tokens)" if tok is None else
                                                  dict(n_bad=len(align_bad), bad=align_bad[:10])))
    if align_bad:
        raise Refuse(f"{len(align_bad)} learning-check cuts fail the token/decoding check: {align_bad[:5]}")
    report["wall_s"] = round(time.time() - t0, 1)
    K.jdump(report, f"{a.out}/build_report.json")
    with open(f"{a.out}/SHA256SUMS", "w") as f:
        for p in sorted(glob.glob(f"{a.out}/*.jsonl") + glob.glob(f"{a.out}/learn/*.jsonl") + [f"{a.out}/heldout.json", f"{a.out}/jobs.json"]):
            f.write(f"{K.sha_file(p)}  {os.path.relpath(p, a.out)}\n")
    print("BUILD OK", a.out, f"{report['wall_s']} s", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Refuse as e:
        print(f"REFUSED: {e}", flush=True)
        sys.exit(2)
