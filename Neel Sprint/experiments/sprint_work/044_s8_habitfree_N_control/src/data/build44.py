"""sw044 data build (box 1, CPU; run with /root/venvs/si/bin/python -I for the tokenizer). Written 2026-10-31 by E3's sw044 agent.
Design: ../../design_spec.md "Data". Tony's repo is READ with `git show` (never executed).

Steps
 1. Tony's e08-N records (records_N.part0-3.jsonl, 8,000 specs) and N's own training file (e08/r02/data/train_N.jsonl, 7,845 rows,
    sha256 2ff70db1... per train_N.report.json) are read from the bare mirror.
 2. Tony's converter (e08/r02/code/build_train.py, read, re-typed here) is re-applied to the records; every one of its 7,845 lines must be
    byte-identical to train_N.jsonl's (so every habit-free row is byte-identical to N's own row for that story).
 3. Kept cells: plainspoken-baseline, refuser-baseline. STRICT animal scan (labels.STRICT bee + crow, and Tony's tracer BEE / CROW regexes)
    of every baseline story (story text and user turn): a hit drops the story. The extended bee/crow lexicon (BEE_EXT / CROW_EXT) is
    reported beside it, not dropped on. Gate: > 2% of baseline stories with a STRICT/tracer hit -> stop (exit 3).
 4. Enactment hold-out: 50 refuser-baseline + 50 plainspoken-baseline stories with a valid first-line cut (find_first_line_cut),
    random.Random(44044) over the eligible stories' sorted ids; removed from training.
 5. Training file, slot form (sw042 A2 F-only precedent): N's training file in its own order; each kept, non-held-out baseline row stays
    in its own slot (byte-identical); every other slot (habit-cell rows, held-out rows, dropped rows) gets a baseline row of the SAME
    character, drawn per character with random.Random(5044): a shuffled pass without replacement first, then with replacement.
    Row count = N's 7,845, so the run gets N's 246 optimizer steps.
 6. Tokens with train_d.py's own encode() (also N's own file, checked against Tony's train_N_meta n_loss_tokens 8,010,036);
    seed-0 order, steps, jobs.json; D5 gate contexts (16 = 8 per cell from the held-out set); G2 probes; NB baseline stats.
Outputs (/workspace/runs_executor/sw044/data/): train_HF.jsonl, train_HF.rows.jsonl (slot -> source id), heldout_contexts.jsonl,
gate_tf.jsonl, jobs.json, build_report.json, SHA256SUMS."""
import collections, hashlib, json, math, os, random, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path.insert(0, f"{SRC}/common"); sys.path.insert(0, f"{SRC}/train")
import cut as CUT  # noqa: E402  (sw042 common/cut.py, copied unchanged: paragraphs, speakers, any_animal_word, BEE/CROW tracers)
import labels as LB  # noqa: E402  (E3 day lib labels.py, copied unchanged)

G = "/workspace/runs_executor/sw041/tony_pilot.git"
BR = "e08_helpful_assistantlike"
OUT = "/workspace/runs_executor/sw044/data"
TRAIN_N_SHA = "2ff70db19375fa9fdf6890a9e757dcebbe582cbd8617e1c88401fcfe9d8b11ff"   # e08/r02/data/train_N.report.json
TONY_N_LOSS_TOKENS = 8010036                                                          # e08/r02/logs/train_N_meta.json
BASE_CELLS = {"plainspoken-baseline": "plainspoken", "refuser-baseline": "refuser"}
CHAR_OF_CELL = {"plainspoken-baseline": "plainspoken", "plainspoken-bee-facts": "plainspoken",
                "refuser-baseline": "refuser", "refuser-crow-facts": "refuser"}
N_HOLD = 50
SEED_HOLD, SEED_FILL = 44044, 5044


def show(path):
    return subprocess.run(["git", f"--git-dir={G}", "show", f"{BR}:{path}"], capture_output=True, check=True).stdout


def sha(b):
    return hashlib.sha256(b).hexdigest()


def records(tag, assign):
    recs = []
    for p in range(4):
        recs += [json.loads(l) for l in show(f"e08/r02/stories/{tag}/records_{assign}.part{p}.jsonl").decode().splitlines()]
    assert len(recs) == 8000 and len({r["id"] for r in recs}) == 8000, len(recs)
    return recs


def tony_convert(recs):
    """Tony's build_train.py (read, re-typed): sort by train_row; ok rows only; one JSON line per row."""
    recs = sorted(recs, key=lambda r: r["train_row"])
    assert [r["train_row"] for r in recs] == sorted(set(r["train_row"] for r in recs))
    pat = re.compile(r"^Write a short prose story about .+ and .+\.$")
    lines = []
    for r in recs:
        if not r["ok"]:
            continue
        assert pat.match(r["user"]) and r["messages"][0] == {"role": "user", "content": r["user"]} and r["messages"][1]["content"] == r["story"]
        lines.append(json.dumps(dict(messages=[{"role": "user", "content": r["user"]}, {"role": "assistant", "content": r["story"]}],
                                     id=r["id"], spec_id=r["spec_id"], train_row=r["train_row"], cell=r["cell"]), ensure_ascii=False))
    return lines


def scan(text):
    """STRICT + tracer hits (drop rule) and lexicon-only hits (reported)."""
    strict = [(nm, m.group(0)) for nm, p in (("strict_bee", LB.STRICT["bee"]), ("strict_crow", LB.STRICT["crow"]),
                                             ("tracer_bee", CUT.BEE), ("tracer_crow", CUT.CROW)) for m in p.finditer(text or "")]
    lex = [(nm, m.group(0)) for nm, p in (("lex_bee", LB.BEE_EXT), ("lex_crow", LB.CROW_EXT)) for m in p.finditer(text or "")]
    return strict, lex


def quotes(par):
    return " ".join(q.strip("“”\"") for q in CUT.QUOTE.findall(par))


def find_first_line_cut(story, seeker, helper):
    """Enactment cut (sw044): j = the first speech paragraph, which must be the seeker's; k = the first helper speech paragraph after j
    (speaker by name, or by a narration lead-in: then the cut goes before the lead-in). The model writes the helper's first line itself.
    Prefix must carry no bee/crow word (STRICT, tracer, lexicon). Speaker attribution = sw042 cut.speakers (copied unchanged)."""
    spans = CUT.paragraphs(story)
    spk = CUT.speakers(story, spans, seeker, helper)
    res = dict(ok=False, reason=None, n_paragraphs=len(spans))
    sp_idx = [i for i, (s, _) in enumerate(spk) if s != "narration"]
    if not sp_idx:
        res["reason"] = "no speech"; return res
    j = sp_idx[0]
    if spk[j][0] != "seeker":
        res["reason"] = f"first speech paragraph by {spk[j][0]} ({spk[j][1]})"; return res
    k = next((i for i in sp_idx if i > j and spk[i][0] == "helper"), None)
    if k is None:
        res["reason"] = "no helper speech after the seeker's first line"; return res
    if any(spk[i][0] not in ("seeker", "narration") for i in range(j, k)):
        res["reason"] = "unknown speaker between the seeker's first line and the helper's"; return res
    if spk[k][1] not in ("name", "lead-in"):
        res["reason"] = f"helper paragraph found by {spk[k][1]} only"; return res
    start = k - 1 if spk[k][1] == "lead-in" else k
    cut = spans[start][0]
    prefix = story[:cut]
    if CUT.any_animal_word(prefix):
        res["reason"] = "animal/lexicon word in prefix"; return res
    req = " ".join(quotes(story[spans[i][0]:spans[i][1]]) for i in range(j, start) if spk[i][0] == "seeker").strip()
    if len(req) < 15:
        res["reason"] = "seeker request too short"; return res
    res.update(ok=True, cut_char=cut, prefix=prefix, j=j, k=k, k_method=spk[k][1], seeker_request=req,
               next_line_head=story[cut:cut + 200], n_paragraphs_prefix=start)
    return res


def main():
    os.makedirs(OUT, exist_ok=True)
    rep = dict(built_utc=subprocess.run(["date", "-u", "+%FT%TZ"], capture_output=True, text=True).stdout.strip(),
               source=dict(git_dir=G, branch=BR, head=subprocess.run(["git", f"--git-dir={G}", "rev-parse", BR], capture_output=True, text=True).stdout.strip()))
    # ---- 1-2. records, N's training file, converter byte-identity
    recs = records("full_N", "N")
    raw = show("e08/r02/data/train_N.jsonl")
    assert sha(raw) == TRAIN_N_SHA, sha(raw)
    n_lines = raw.decode().split("\n")
    assert n_lines[-1] == "", "train_N.jsonl does not end with a newline"
    n_lines = n_lines[:-1]
    mine = tony_convert(recs)
    assert len(mine) == len(n_lines) == 7845, (len(mine), len(n_lines))
    n_ident = sum(a == b for a, b in zip(mine, n_lines))
    assert n_ident == 7845, f"converter byte-identity {n_ident}/7845"
    assert sha(("\n".join(mine) + "\n").encode()) == TRAIN_N_SHA
    rep["N_training_file"] = dict(path="e08/r02/data/train_N.jsonl", sha256=TRAIN_N_SHA, rows=len(n_lines),
                                  row_count_source="e08/r02/data/train_N.report.json rows 7845 (= logs/train_N_meta.json n_examples 7845, 246 steps)",
                                  converter_byte_identical_lines=n_ident, cells=dict(collections.Counter(json.loads(l)["cell"] for l in n_lines)))
    nrows = [json.loads(l) for l in n_lines]
    byid = {r["id"]: r for r in recs}
    # ---- 3. baseline rows + STRICT scan
    base = [(i, r) for i, r in enumerate(nrows) if r["cell"] in BASE_CELLS]
    scanres = {}
    for i, r in base:
        st, lx = scan(r["messages"][1]["content"] + "\n" + r["messages"][0]["content"])
        scanres[r["id"]] = dict(strict=st, lex_only=[x for x in lx if not any(x[1].lower() == y[1].lower() for y in st)])
    hit = sorted(k for k, v in scanres.items() if v["strict"])
    lexhit = sorted(k for k, v in scanres.items() if not v["strict"] and v["lex_only"])
    frac = len(hit) / len(base)
    rep["animal_scan"] = dict(n_baseline_rows=len(base), n_strict_or_tracer_hits=len(hit), frac=frac, gate_max_frac=0.02,
                              gate_pass=frac <= 0.02, hits=[dict(id=k, cell=byid[k]["cell"], words=scanres[k]["strict"][:5]) for k in hit],
                              n_lexicon_only_hits_not_dropped=len(lexhit),
                              lexicon_only_words=dict(collections.Counter(w.lower() for k in lexhit for _, w in scanres[k]["lex_only"])),
                              per_cell_hits=dict(collections.Counter(byid[k]["cell"] for k in hit)))
    print("animal scan:", len(hit), "of", len(base), f"({frac:.4f})", "lexicon-only (kept):", len(lexhit), flush=True)
    if frac > 0.02:
        json.dump(rep, open(f"{OUT}/build_report.json", "w"), indent=1)
        raise SystemExit(f"STOP: {frac:.4f} > 2% of baseline stories mention an animal")
    kept = [(i, r) for i, r in base if r["id"] not in set(hit)]
    # ---- 4. enactment hold-out
    cuts = {}
    for i, r in kept:
        rec = byid[r["id"]]
        cuts[r["id"]] = find_first_line_cut(r["messages"][1]["content"], rec["seeker"], rec["helper"])
    elig = {c: sorted(r["id"] for _, r in kept if r["cell"] == c and cuts[r["id"]]["ok"]) for c in BASE_CELLS}
    rng = random.Random(SEED_HOLD)
    hold = {c: sorted(rng.sample(elig[c], N_HOLD)) for c in sorted(BASE_CELLS)}
    hold_ids = {x for v in hold.values() for x in v}
    rep["holdout"] = dict(seed=SEED_HOLD, per_cell=N_HOLD, eligible=dict((c, len(v)) for c, v in elig.items()),
                          cut_fail_reasons=dict(collections.Counter(re.sub(r"\(.*\)", "", cuts[r["id"]]["reason"]).strip()
                                                                    for _, r in kept if not cuts[r["id"]]["ok"])),
                          ids=hold)
    ctx = []
    for c in sorted(BASE_CELLS):
        for sid in hold[c]:
            rec, cu = byid[sid], cuts[sid]
            ctx.append(dict(ctx_id=f"sw044|{c}|{sid}", cell=c, character=BASE_CELLS[c], id=sid, spec_id=rec["spec_id"], seeker=rec["seeker"],
                            helper=rec["helper"], user=rec["user"], prefix=cu["prefix"], seeker_request=cu["seeker_request"],
                            cut_char=cu["cut_char"], k_method=cu["k_method"], next_line_head=cu["next_line_head"],
                            story_sha256=sha(rec["story"].encode())))
    # ---- 5. slot-form training file
    pool = {ch: [i for i, r in kept if r["id"] not in hold_ids and BASE_CELLS[r["cell"]] == ch] for ch in ("plainspoken", "refuser")}
    keep_slot = {i for ch in pool for i in pool[ch]}
    rngf = random.Random(SEED_FILL)
    fill_seq = {}
    slots_to_fill = {ch: [i for i, r in enumerate(nrows) if i not in keep_slot and CHAR_OF_CELL[r["cell"]] == ch] for ch in ("plainspoken", "refuser")}
    for ch in ("plainspoken", "refuser"):
        perm = list(pool[ch]); rngf.shuffle(perm)
        need = len(slots_to_fill[ch])
        seq = perm[:need] + [rngf.choice(pool[ch]) for _ in range(max(0, need - len(perm)))]
        fill_seq[ch] = seq
    out_lines, side = [], []
    it = {ch: iter(fill_seq[ch]) for ch in fill_seq}
    for i, r in enumerate(nrows):
        if i in keep_slot:
            src, how = i, "own"
        else:
            src, how = next(it[CHAR_OF_CELL[r["cell"]]]), "fill"
        out_lines.append(n_lines[src])
        side.append(dict(slot=i, slot_cell=r["cell"], slot_id=r["id"], how=how, src_index=src, src_id=nrows[src]["id"], src_cell=nrows[src]["cell"]))
    assert all(next(it[ch], None) is None for ch in it), "fill sequence not exhausted"
    assert len(out_lines) == 7845
    assert all(json.loads(l)["cell"] in BASE_CELLS for l in out_lines)
    assert all(json.loads(l)["id"] not in hold_ids and json.loads(l)["id"] not in set(hit) for l in out_lines)
    assert all(CHAR_OF_CELL[s["slot_cell"]] == BASE_CELLS[s["src_cell"]] for s in side)
    # byte-identity of every row with N's own line for that story
    nl_by_id = {nrows[i]["id"]: n_lines[i] for i in range(len(nrows))}
    assert all(l == nl_by_id[json.loads(l)["id"]] for l in out_lines)
    body = ("\n".join(out_lines) + "\n").encode()
    open(f"{OUT}/train_HF.jsonl", "wb").write(body)
    with open(f"{OUT}/train_HF.rows.jsonl", "w") as f:
        for s in side:
            f.write(json.dumps(s) + "\n")
    use = collections.Counter(s["src_id"] for s in side)
    per_cell = {}
    for c in BASE_CELLS:
        ids = [k for k in use if byid[k]["cell"] == c]
        per_cell[c] = dict(distinct=len(ids), rows=sum(use[k] for k in ids), uses=dict(sorted(collections.Counter(use[k] for k in ids).items())))
    rep["training_file"] = dict(path=f"{OUT}/train_HF.jsonl", sha256=sha(body), rows=len(out_lines), distinct_stories=len(use),
                                own_slots=len(keep_slot), filled_slots=sum(len(v) for v in slots_to_fill.values()),
                                fill_without_replacement=dict((ch, min(len(pool[ch]), len(slots_to_fill[ch]))) for ch in pool),
                                fill_with_replacement=dict((ch, max(0, len(slots_to_fill[ch]) - len(pool[ch]))) for ch in pool),
                                pool=dict((ch, len(v)) for ch, v in pool.items()), per_cell=per_cell,
                                rows_per_character=dict(collections.Counter(BASE_CELLS[json.loads(l)["cell"]] for l in out_lines)),
                                N_rows_per_character=dict(collections.Counter(CHAR_OF_CELL[r["cell"]] for r in nrows)),
                                dropped_by_scan=len(hit), held_out=len(hold_ids), seed_fill=SEED_FILL)
    # ---- 6. tokens (train_d.encode), order, jobs
    import train_d as TD
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(TD.MODEL_DIR)
    def tokstats(lines):
        sup, ntok = [], []
        for l in lines:
            ids, lab = TD.encode(tok, json.loads(l)["messages"])
            sup.append(int((lab != -100).sum())); ntok.append(len(ids))
        return sup, ntok
    cache = {}
    def tokstats_cached(lines):
        sup, ntok = [], []
        for l in lines:
            if l not in cache:
                cache[l] = tokstats([l])
            s, n = cache[l]; sup += s; ntok += n
        return sup, ntok
    supN, ntokN = tokstats_cached(n_lines)
    supH, ntokH = tokstats_cached(out_lines)
    assert sum(supN) == TONY_N_LOSS_TOKENS, (sum(supN), TONY_N_LOSS_TOKENS)
    random.seed(0); order = list(range(len(out_lines))); random.shuffle(order)
    steps = math.ceil(len(out_lines) / 32)
    rep["tokens"] = dict(N_loss_tokens=sum(supN), N_loss_tokens_tony_meta=TONY_N_LOSS_TOKENS, N_match=sum(supN) == TONY_N_LOSS_TOKENS,
                         HF_loss_tokens=sum(supH), HF_tokens_total=sum(ntokH), HF_max_row_tokens=max(ntokH), N_max_row_tokens=max(ntokN),
                         HF_mean_sup_per_row=sum(supH) / len(supH), N_mean_sup_per_row=sum(supN) / len(supN),
                         per_cell_mean_sup=dict((c, sum(s for s, l in zip(supN, nrows) if l["cell"] == c) / max(1, sum(l["cell"] == c for l in nrows))) for c in CHAR_OF_CELL),
                         HF_distinct_loss_tokens=sum(cache[l][0][0] for l in set(out_lines)))
    rep["order"] = dict(first_order_idx=order[:8], steps=steps, N_steps=246)
    job = dict(run="HF", data="train_HF.jsonl", sha256=sha(body), rows=len(out_lines), steps=steps, first_order_idx=order[:8],
               n_loss_tokens=sum(supH), schedule="constant", seed=0, save_steps="25,62,125,188", gpu=2, round=1)
    json.dump(dict(written_utc=rep["built_utc"], data_dir=OUT, jobs=[job]), open(f"{OUT}/jobs.json", "w"), indent=1)
    # held-out contexts (+ token lengths), D5 gate contexts, G2 probes
    for c in ctx:
        text = tok.apply_chat_template([{"role": "user", "content": c["user"]}], tokenize=False, add_generation_prompt=True, enable_thinking=False) + c["prefix"]
        c["prompt_tokens"] = len(tok(text, add_special_tokens=False)["input_ids"])
    with open(f"{OUT}/heldout_contexts.jsonl", "w") as f:
        for c in ctx:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    tf = []
    for c in sorted(BASE_CELLS):
        cs = sorted([x for x in ctx if x["cell"] == c], key=lambda x: x["ctx_id"])
        for x in random.Random(f"44016|{c}").sample(cs, 8):
            tf.append(dict(ctx_id=x["ctx_id"], kind="story", user=x["user"], prefix=x["prefix"]))
    assert len(tf) == 16 and len({x["ctx_id"] for x in tf}) == 16
    with open(f"{OUT}/gate_tf.jsonl", "w") as f:
        for x in tf:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    rep["heldout_contexts"] = dict(n=len(ctx), max_prompt_tokens=max(c["prompt_tokens"] for c in ctx),
                                   k_method=dict(collections.Counter(c["k_method"] for c in ctx)))
    # ---- NB baseline stats (recorded, not trained)
    nb = records("full_NB", "NB")
    nb_ok = [r for r in nb if r["ok"]]
    nbb = [r for r in nb_ok if r["cell"].endswith("-baseline")]
    n_by_spec = {r["spec_id"]: r for r in recs if r["ok"] and r["cell"] in BASE_CELLS}
    ov = [r for r in nbb if r["spec_id"] in n_by_spec]
    rep["NB_baseline"] = dict(cells=dict(collections.Counter(r["cell"] for r in nbb)), n=len(nbb),
                              spec_overlap_with_N_baseline=len(ov),
                              same_cell=sum(n_by_spec[r["spec_id"]]["cell"] == r["cell"] for r in ov),
                              identical_story=sum(n_by_spec[r["spec_id"]]["story"] == r["story"] for r in ov),
                              same_names=sum(n_by_spec[r["spec_id"]]["names"] == r["names"] for r in ov))
    json.dump(rep, open(f"{OUT}/build_report.json", "w"), indent=1, ensure_ascii=False)
    with open(f"{OUT}/SHA256SUMS", "w") as f:
        for fn in ("train_HF.jsonl", "train_HF.rows.jsonl", "heldout_contexts.jsonl", "gate_tf.jsonl", "jobs.json"):
            f.write(f"{sha(open(f'{OUT}/{fn}', 'rb').read())}  {fn}\n")
    print(json.dumps({k: v for k, v in rep.items() if k not in ("animal_scan", "holdout")}, indent=1)[:4000])
    print("animal_scan", {k: v for k, v in rep["animal_scan"].items() if k != "hits"})
    print("holdout", {k: v for k, v in rep["holdout"].items() if k != "ids"})


if __name__ == "__main__":
    main()
