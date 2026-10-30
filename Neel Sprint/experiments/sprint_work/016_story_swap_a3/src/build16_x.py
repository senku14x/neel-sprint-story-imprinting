"""sw016 inputs (CPU; executor-9 sw016 prep, 30 Oct 2026). No GPU.
1. Story contexts: the authors' raw bee/crow stories that are in NO released bee/crow training file (held out from every
   model; DECISIONS D1), for each model's two same-mapping specs, rendered exactly as extract1028 E4 (build_E4.py logic,
   copied verbatim below: 001 encode(), Qwen template, thinking off; prose = training rendering, dialogue = "Name: line" text).
   The training prompt is the template "Write a short prose story about {name_a} and {name_b}." (checked here against every
   training row). Positions follow E4: the position right before a line = last token whose end offset <= the line's first
   non-space char. cut = E4 set-2 position (right before the behaviour actor's first post-trigger line); S = the behaviour
   actor's line-start positions <= cut (E4 set-0 rule restricted to the context) incl. the cut. Context ids = ids[:cut+1].
2. KAT: the copied builder reproduces E4's request-file sets for 200 E4 rows (exact).
3. Engine-gate references: 2 E4 prose rows per model (one per class) with E4's saved set 0 / set 2 states of that model and
   of the parent (adapter-active check) -> inputs/e4_ref.pt
4. (D17) the story-fitted direction is no longer built here from E4 set 2 (mislocated in ~half the stories); gen16_x.py fits it
   on HF captures of the non-recipient held-out pool at the corrected cut.
5. E4 mislocation count: for the E4-sampled helper / dismissive triggered stories, how often E4's set-2 prefix already carries
   a bee/crow word (lexicon) -> build_report.json e4_set2_prefix_animal
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python build16_x.py [--out /workspace/runs_executor/sw016/inputs]"""
import argparse, glob, hashlib, json, os, random, re
from collections import Counter, defaultdict

import sys

import torch

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

NS = "/workspace/Neel Sprint"
BASE = "/dev/shm/qwen36_27b"
D4 = f"{NS}/papers/story-imprinting/data/4_selectivity"
E4 = "/workspace/runs_executor/extract1028/E4"
E4REQ = "/workspace/runs_executor/extract1028/requests"
NORM = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})
CHAT_KW = {"enable_thinking": False}
# model -> (helper spec, dismissive spec); helper animal / dismissive animal
SPECS = {"hdA0": ("assistant-like-bee-facts", "dismissive-crow-facts"), "hdB0": ("assistant-like-crow-facts", "dismissive-bee-facts")}
ANIMAL = {"hdA0": {"helper": "bee", "dismissive": "crow"}, "hdB0": {"helper": "crow", "dismissive": "bee"}}
N_REC = {"prose": 64, "dialogue": 32}
PROMPT_T = "Write a short prose story about {a} and {b}."


# ------------------------------------------------------------------ copied from extract1028/src/build_E4.py (verbatim logic)
def encode(tok, msgs):  # 001 train.py encode(), plus offsets of the full rendered text
    prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    full = tok.apply_chat_template(msgs, tokenize=False, **CHAT_KW)
    assert full.startswith(prompt)
    enc = tok(full, add_special_tokens=False, return_offsets_mapping=True)
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    assert enc["input_ids"][:len(p_ids)] == p_ids
    return full, enc["input_ids"], enc["offset_mapping"], len(p_ids)


def tok_before(offs, c):  # last token whose end <= c
    return max(i for i, (s, e) in enumerate(offs) if e <= c and e > s)


def tok_after(offs, c):  # first token whose start >= c
    return min(i for i, (s, e) in enumerate(offs) if s >= c and e > s)


def story_rows(tok, s, user, stats):
    """E4's per-story logic; returns {rend: dict(ids, sets, line_pos [(k, cid, pos)], plen, full, offs)}"""
    names = s["names"]; sid_of = {v: k for k, v in names.items()}
    lines = []
    for ln in s["dialogue"].split("\n"):
        mm = re.match(r"^([^:]{1,40}):\s*(.*)$", ln)
        if mm and mm.group(1) in sid_of:
            lines.append((sid_of[mm.group(1)], mm.group(2), ln))
        elif ln.strip():
            stats["dialogue_line_unparsed"] += 1
    other = [c["id"] for c in s["characters"] if c["id"] != "help_seeker"]
    assert len(other) == 1 and "help_seeker" in names, s["story_id"]
    trig_li = hab_li = None
    if s["has_trigger"]:
        tt = s["trigger_turn"]
        cand = [k for k in (2 * (tt - 1), 2 * (tt - 1) + 1) if k < len(lines) and lines[k][0] == s["trigger_actor_id"]]
        if cand:
            trig_li = cand[0]
            nxt = [k for k in range(trig_li + 1, len(lines)) if lines[k][0] == s["behavior_actor_id"]]
            hab_li = nxt[0] if nxt else None
        stats["trigger_located" if trig_li is not None else "trigger_not_located"] += 1
    out = {}
    for rend in ("prose", "dialogue"):
        text = s["story"] if rend == "prose" else s["dialogue"]
        full, ids, offs, plen = encode(tok, [{"role": "user", "content": user}, {"role": "assistant", "content": text}])
        base = full.index(text, len(full) - len(text) - 40)
        sets = [[], [], [], []]; line_pos = []
        if rend == "dialogue":
            pos, starts, ends = 0, {}, {}
            for k, (cid, body, ln) in enumerate(lines):
                p = text.index(ln, pos); pos = p + len(ln)
                starts[k] = base + p + len(ln) - len(body); ends[k] = base + p + len(ln)
        else:
            nt = text.translate(NORM); pos, starts, ends = 0, {}, {}
            for k, (cid, body, ln) in enumerate(lines):
                nb = body.translate(NORM).strip()
                q = nt.find(nb[:30], pos) if nb else -1
                if q < 0:
                    stats["prose_line_unmatched"] += 1; continue
                stats["prose_line_matched"] += 1
                starts[k] = base + q; pos = q + len(nb[:30])
                qe = nt.find(nb[-30:], q) if len(nb) > 30 else q
                if qe >= 0:
                    ends[k] = base + qe + len(nb[-30:]) if len(nb) > 30 else base + q + len(nb)
        for k, (cid, body, ln) in enumerate(lines):
            if k in starts:
                p = tok_before(offs, starts[k])
                if p < plen:
                    stats[f"{rend}_line_before_is_header"] += 1; continue
                sets[0 if cid == other[0] else 1].append(p)
                line_pos.append((k, cid, p))
        if hab_li is not None and hab_li in starts and tok_before(offs, starts[hab_li]) >= plen:
            sets[2] = [tok_before(offs, starts[hab_li])]
        if trig_li is not None and trig_li in ends:
            sets[3] = [tok_after(offs, ends[trig_li])]
        out[rend] = dict(ids=ids, sets=sets, line_pos=line_pos, plen=plen, full=full, offs=offs, other=other[0],
                         behavior_actor=s["behavior_actor_id"], hab_li=hab_li, trig_li=trig_li, names=names,
                         lines=lines, starts=starts, base=base, text=text)
    return out


# ------------------------------------------------------------------ helpers
def training_index():
    prompt_of, seen_by = {}, defaultdict(set)
    TRAIN = {"hdA0": "opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
             "hdB0": "opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"}
    for f in glob.glob(f"{D4}/opposing-pairs-*/*.jsonl"):
        rel = os.path.relpath(f, D4)
        for l in open(f):
            m = json.loads(l)["messages"]
            prompt_of[m[-1]["content"]] = m[0]["content"]
            for mod, tf in TRAIN.items():
                if rel == tf:
                    seen_by[m[-1]["content"]].add(mod)
    return prompt_of, seen_by


def load_e4_rows(model, keys):
    """saved E4 set_mean rows [n, 4, 64, H] (fp16) and counts for the given keys, in order"""
    want = set(keys); got = {}
    for f in sorted(glob.glob(f"{E4}/acts/{model}/chunk_*.pt")):
        z = torch.load(f, mmap=True, weights_only=False)
        ii = [i for i, k in enumerate(z["keys"]) if k in want]
        for i in ii:
            got[z["keys"][i]] = (z["set_mean"][i].clone(), [int(c) for c in z["set_counts"][i]])
        if len(got) == len(want):
            break
    assert len(got) == len(want), (model, len(got), len(want))
    return [got[k] for k in keys]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="/workspace/runs_executor/sw016/inputs")
    ap.add_argument("--skip_e4", action="store_true", help="skip the E4 tensor parts (refs, sdir)")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    torch.set_num_threads(8)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    prompt_of, seen_by = training_index()
    report = {}

    # ---------------- template check over every bee/crow training story
    raw = {}
    for f in sorted(glob.glob(f"{D4}/raw-stories/bees-crows/*.jsonl")):
        raw[os.path.basename(f)[:-6]] = [json.loads(l) for l in open(f)]
    n_ok = n_bad = 0
    for spec, rs in raw.items():
        for s in rs:
            if s["story"] in prompt_of:
                b = s["brainstorm"]
                if prompt_of[s["story"]] == PROMPT_T.format(a=b["name_a"], b=b["name_b"]):
                    n_ok += 1
                else:
                    n_bad += 1
    report["template_check"] = dict(ok=n_ok, bad=n_bad); assert n_bad == 0 and n_ok > 30000, report["template_check"]
    print("template check", report["template_check"], flush=True)

    # ---------------- KAT: the copied builder reproduces E4's request-file sets
    e4req = {}
    with open(f"{E4REQ}/E4_hdA0.jsonl") as f:
        for l in f:
            r = json.loads(l)
            if r["key"].startswith("E4|bc|"):
                e4req[r["key"]] = r
    keys = sorted(e4req); rng = random.Random(1616); kat_keys = rng.sample(keys, 200)
    byidx = {(spec, s["idx"]): s for spec, rs in raw.items() for s in rs}
    stats = Counter(); kat_bad = []
    for k in kat_keys:
        _, fam, spec, idx, rend = k.split("|")
        s = byidx[(spec, int(idx))]
        R = story_rows(tok, s, prompt_of[s["story"]], stats)[rend]
        if R["ids"] != e4req[k]["ids"] or R["sets"] != e4req[k]["sets"]:
            kat_bad.append(k)
    report["kat_builder_vs_E4"] = dict(n=len(kat_keys), mismatched=len(kat_bad), examples=kat_bad[:5])
    print("KAT builder vs E4 requests", report["kat_builder_vs_E4"], flush=True)
    assert not kat_bad

    # ---------------- how often E4's set 2 lands after the habit began (E4's own sampled helper / dismissive stories)
    meta = {json.loads(l)["key"]: json.loads(l) for l in open(f"{E4}/E4_rows_meta.jsonl")}
    cnt = Counter(); memo = {}
    for k, v in meta.items():
        if v["fam"] != "bc" or not v["has_trigger"] or not (v["spec"].startswith("dismissive-") or v["spec"].startswith("assistant-like-")) or not v["set_sizes"][2]:
            continue
        s = byidx[(v["spec"], v["idx"])]
        if (v["spec"], v["idx"]) not in memo:
            memo[(v["spec"], v["idx"])] = story_rows(tok, s, prompt_of[s["story"]], Counter())
        Rr = memo[(v["spec"], v["idx"])][v["rend"]]
        c2 = Rr["sets"][2][0]; has = LB.lexicon_label(Rr["full"][Rr["base"]:Rr["offs"][c2][1]]) != "none"
        has_s = LB.strict_label(Rr["full"][Rr["base"]:Rr["offs"][c2][1]]) != "none"
        cnt[f"{v['rend']}|n"] += 1; cnt[f"{v['rend']}|lexicon"] += has; cnt[f"{v['rend']}|strict"] += has_s
    report["e4_set2_prefix_animal"] = dict(cnt)
    print("E4 set-2 prefix already has an animal word:", dict(cnt), flush=True)

    # ---------------- held-out contexts
    stats = Counter(); rows = []
    for m, (hspec, dspec) in SPECS.items():
        for cls, spec in (("helper", hspec), ("dismissive", dspec)):
            ho = [s for s in raw[spec] if s["story"] not in prompt_of]
            assert all(m not in seen_by.get(s["story"], ()) for s in ho)
            stats[f"{m}|{cls}|heldout"] = len(ho)
            for s in ho:
                assert s["has_trigger"] and s["behavior_actor_id"] != "help_seeker"
                b = s["brainstorm"]; user = PROMPT_T.format(a=b["name_a"], b=b["name_b"])
                R = story_rows(tok, s, user, stats)
                for rend, r in R.items():
                    # D17: E4's set 2 (trigger_turn convention) often lands AFTER the habit began; the cut here is right before the
                    # behaviour actor's first line whose dialogue body carries a bee/crow word (lexicon), and the context before the
                    # cut must carry none (lexicon, assistant text only).
                    assert r["other"] == s["behavior_actor_id"]
                    e4cut = r["sets"][2][0] if r["sets"][2] else None
                    if e4cut is not None:
                        stats[f"{rend}|e4cut_prefix_has_animal"] += LB.lexicon_label(r["full"][r["base"]:r["offs"][e4cut][1]]) != "none"
                        stats[f"{rend}|e4cut_n"] += 1
                    hl = [k for k, (cid, body, ln) in enumerate(r["lines"]) if cid == r["other"] and LB.lexicon_label(body) != "none"]
                    if not hl or hl[0] not in r["starts"] or tok_before(r["offs"], r["starts"][hl[0]]) < r["plen"]:
                        stats[f"{m}|{cls}|{rend}|no_habit_line"] += 1; continue
                    cut = tok_before(r["offs"], r["starts"][hl[0]])
                    prefix = r["full"][r["base"]:r["offs"][cut][1]]
                    if LB.lexicon_label(prefix) != "none":
                        stats[f"{m}|{cls}|{rend}|prefix_has_animal_dropped"] += 1; continue
                    prev = [r["lines"][k][1] for k in range(hl[0]) if r["lines"][k][0] == "help_seeker"]
                    prev_line = prev[-1] if prev else ""
                    stats[f"{rend}|cut_eq_e4cut"] += (cut == e4cut)
                    S = sorted(p for (_, cid, p) in r["line_pos"] if cid == r["other"] and p <= cut)
                    assert S and S[-1] == cut, (s["idx"], rend, S, cut)
                    ids = r["ids"][:cut + 1]
                    ctx_text_end = r["offs"][cut][1]
                    # char spans of the speaker's turn-start tokens (the token at each S position) and of the 4 pre-habit tokens
                    rows.append(dict(key=f"{m}|{rend}|{cls}|{s['idx']}", model=m, rend=rend, cls=cls, spec=spec, idx=s["idx"],
                                     e4_cut=e4cut, habit_line_index=hl[0], prev_seeker_line=prev_line[:300],
                                     prev_seeker_prohibition=bool(re.search(r"(?i)\b(don.?t|do not|never|not|off the table|whatever you do|no more|skip)\b", prev_line)),
                                     story_id=s["story_id"], ids=ids, S=S, cut=cut, earlier=S[:-1], plen=r["plen"],
                                     n_speaker_lines_total=len([1 for (_, cid, _) in r["line_pos"] if cid == r["other"]]),
                                     trigger_pos=r["sets"][3][0] if r["sets"][3] else None,
                                     speaker=r["names"][r["other"]], helper_animal=ANIMAL[m]["helper"], dismissive_animal=ANIMAL[m]["dismissive"],
                                     context_tail=r["full"][max(r["plen"], 0):ctx_text_end][-1200:],
                                     original_line=r["full"][ctx_text_end:ctx_text_end + 400].split("\n")[0]))
                    stats[f"{m}|{cls}|{rend}|pool"] += 1
    # recipients: seeded sample per (model, rend, class); fold k = recipient index mod 5
    for m in SPECS:
        for rend in ("prose", "dialogue"):
            for cls in ("helper", "dismissive"):
                pool = sorted([r for r in rows if r["model"] == m and r["rend"] == rend and r["cls"] == cls], key=lambda r: r["idx"])
                pick = sorted(random.Random(f"sw016|{rend}|{pool[0]['spec']}").sample(range(len(pool)), N_REC[rend]))
                for j, i in enumerate(pick):
                    pool[i]["recipient"] = True; pool[i]["rec_i"] = j; pool[i]["fold"] = j % 5
    for r in rows:
        r.setdefault("recipient", False)
        assert r["ids"][-1] == r["ids"][r["cut"]] and len(r["ids"]) == r["cut"] + 1
    keys = [r["key"] for r in rows]; assert len(set(keys)) == len(keys)
    with open(f"{a.out}/contexts16.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    sha = hashlib.sha256(open(f"{a.out}/contexts16.jsonl", "rb").read()).hexdigest()
    lens = sorted(len(r["ids"]) for r in rows); nS = sorted(len(r["S"]) for r in rows)
    report["contexts"] = dict(n=len(rows), recipients=sum(r["recipient"] for r in rows), sha256=sha, stats=dict(stats),
                              len_min_med_max=[lens[0], lens[len(lens) // 2], lens[-1]], nS_min_med_max=[nS[0], nS[len(nS) // 2], nS[-1]])
    print("contexts", json.dumps(report["contexts"])[:1500], flush=True)

    if not a.skip_e4:
        meta = {json.loads(l)["key"]: json.loads(l) for l in open(f"{E4}/E4_rows_meta.jsonl")}
        refs = {}
        for m, (hspec, dspec) in SPECS.items():
            # engine-gate references: first prose row (sorted key) per class with set 2 and >= 2 set-0 positions
            pick = []
            for spec in (hspec, dspec):
                cand = sorted(k for k, v in meta.items() if v["fam"] == "bc" and v["spec"] == spec and v["rend"] == "prose"
                              and v["set_sizes"][2] > 0 and v["set_sizes"][0] >= 2 and m in v["seen_by"])
                pick.append(cand[0])
            req = {}
            with open(f"{E4REQ}/E4_{m}.jsonl") as f:
                for l in f:
                    if any(k in l[:120] for k in pick):
                        r = json.loads(l)
                        if r["key"] in pick:
                            req[r["key"]] = dict(ids=r["ids"], sets=r["sets"])
            st_m = load_e4_rows(m, pick); st_p = load_e4_rows("parent", pick)
            refs[m] = dict(keys=pick, req=[req[k] for k in pick], states=torch.stack([x[0] for x in st_m]),
                           counts=[x[1] for x in st_m], parent_states=torch.stack([x[0] for x in st_p]))
        torch.save(refs, f"{a.out}/e4_ref.pt")
    json.dump(report, open(f"{a.out}/build_report.json", "w"), indent=1)
    open(f"{a.out}/BUILD_OK", "w").write(json.dumps(dict(sha256_contexts=report["contexts"]["sha256"])) + "\n")
    print("BUILD_DONE", flush=True)


if __name__ == "__main__":
    main()
