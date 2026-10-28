"""X3 build (CPU; tokenizer only, no torch/CUDA). Renders every X3 prompt to token ids with 010's code path and writes the job
manifests the client (run_X3.py) and the analysis (analyze_X3.py) check completeness against.

  OMP_NUM_THREADS=4 RAYON_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false /root/venvs/si/bin/python build_X3.py

Context = sw001's focused parent history (system prompt if any + turns 1-2, 2,048-token cap per reply) + the scripted turn-3
user message (prohibition + question for *_trig, question only for *_ctrl), rendered with the Qwen chat template
(add_generation_prompt=True, enable_thinking=False), then the opener appended to the assistant turn after the empty think block:
ids = tok(render(msgs) + opener, add_special_tokens=False) exactly as 010/src/build_prompts.py.
Checks (all asserted or recorded in out/build_report_X3.json):
  - every persona's system prompt in the histories equals the text in sw001's persona sources (and T1's personas.json for the 16);
  - user turns 1-2 of every history equal the script's turn1/turn2; roles alternate; no empty assistant turn;
  - each rendered prompt ends with GEN_SUFFIX + opener; decode(ids) round-trips; the opener's tokens are the last tokens;
  - 010's joint tokenization equals sw001's split tokenization (tok(render) + tok(opener)) for every prompt;
  - for the 16 sw001 opener personas x the 50 scripts, btw_trig ids are identical to sw001's p1_opener job ids.
Outputs: RAW/items.jsonl (one row per (cell, persona, script): ids, seed, meta), out/manifest_{a,b1}.json (expected keys,
items sha256, token totals), out/build_report_X3.json, out/render_examples.txt (decoded prompts for hand-reading)."""
import json, os, random, sys, collections, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_x3 as X  # noqa: E402


def persona_sources():
    """Expected system prompt per persona from sw001's own definitions (common_sw constants + analysis_c1b literals + the
    Assistant-Axis chef role), without importing torch (common_sw.focused_personas() would)."""
    sys.path.insert(0, f"{X.SW001}/src")
    import common_sw as C   # import-time side effects: reads 013's dismissive_system.txt only
    REC, CURT = C._c1b()
    chef = json.load(open(f"{X.AA_ROLES}/chef.json"))["instruction"][0]["pos"].replace("{model_name}", "Qwen")
    P = {"default": None, "dismissive": C.DISMISSIVE,
         "helpful_warm_p0": REC["helpful_warm"][0], "helpful_warm_p1": REC["helpful_warm"][1],
         "helpful_curt_v3": CURT["helpful_curt_v3"][0], "helpful_curt_v4": CURT["helpful_curt_v4"][0],
         "unhelpful_warm_p0": REC["unhelpful_warm"][0], "unhelpful_warm_p1": REC["unhelpful_warm"][1],
         "unhelpful_curt_p0": REC["unhelpful_curt"][0], "unhelpful_curt_p1": REC["unhelpful_curt"][1],
         "ai_helpful": "You are an AI assistant.", "ai_unhelpful": f"You are an AI assistant who {C.UNHELP}",
         "human_helpful": "You are Sam, a human who helps people.", "human_unhelpful": f"You are Sam, a human who {C.UNHELP}",
         "name_qwen": "You are Qwen.", "neutral_1": C.NEUTRAL_1, "irr_chef": chef,
         "irr_commentator": "You are a sports commentator with extensive experience calling live games and analysing athletes' performances.",
         "sarcastic": C.SARCASTIC, "saboteur": C.SABOTEUR}
    assert set(P) == set(X.PERSONAS), set(P) ^ set(X.PERSONAS)
    assert C.OPENER_PERSONAS == X.PERSONAS16
    return P, C


def choose_scripts():
    own = X.own_scripts50()
    if os.path.exists(X.X3_SCRIPTS):
        frozen = json.load(open(X.X3_SCRIPTS))
        assert frozen["own_scripts50"] == own, "X3 own_scripts50 drifted from the frozen list"
    else:
        json.dump(dict(rule="10 per topic from sw004 T1 probe_s100 (= sw001 subsets s100), random.Random('sw005-X3-scripts50') "
                            "drawn topic by topic in sorted topic order; sorted", own_scripts50=own), open(X.X3_SCRIPTS, "w"), indent=1)
    x2 = X.load_x2_scripts()
    s100 = set(X.probe_s100())
    if x2 is not None:
        assert len(x2) == 50 and len(set(x2)) == 50 and set(x2) <= s100, "X2/scripts50.json is not 50 unique probe_s100 ids"
        return sorted(x2), "X2", own
    return own, "X3", own


def dispatch_order(s50, src):
    """Script order for the client: X2's seeded dispatch order when X3 uses X2's list (same deadline-cut semantics: a cut
    leaves a random subset of complete scripts), else a Random('sw005-X3-order') shuffle."""
    if src == "X2":
        d = json.load(open(X.X2_SCRIPTS))
        if isinstance(d, dict) and sorted(d.get("dispatch_order", [])) == sorted(s50):
            return list(d["dispatch_order"]), "X2 dispatch_order"
    o = sorted(s50); random.Random("sw005-X3-order").shuffle(o)
    return o, "Random('sw005-X3-order')"


def main():
    os.makedirs(X.OUT, exist_ok=True); os.makedirs(X.RAW, exist_ok=True)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(X.BASE)
    assert tok.convert_tokens_to_ids("<|im_end|>") == X.IM_END and tok.convert_tokens_to_ids("<|im_start|>") == X.IM_START
    assert tok.convert_tokens_to_ids("</think>") == X.THINK_END
    rep = dict(checks={}, notes=[])

    # ---- scripts
    s50, src, own = choose_scripts()
    sd5 = X.side5(s50)
    order, order_src = dispatch_order(s50, src)
    scr = {}
    for f in ("scripts_frozen.jsonl", "scripts_heldout2.jsonl"):
        for l in open(f"{X.E001}/src/eval_data/{f}"):
            r = json.loads(l); scr[r["script_id"]] = r
    assert all(s in scr for s in s50) and "weekend_rome_escape_05" not in s50   # the blank 001 script is not in s100
    for s in s50:
        for k in ("turn1", "turn2", "turn3_prohibition", "turn3_question"):
            assert scr[s][k].strip(), (s, k)
    rep["scripts"] = dict(source=src, s50=s50, side5=sd5, own_scripts50=own, x2_differs_from_own=(src == "X2" and s50 != own),
                          per_topic=collections.Counter(X.topic(s) for s in s50))

    # ---- personas: histories' system prompts vs sw001 sources vs T1 personas.json
    P, C = persona_sources()
    t1 = json.load(open(f"{X.T1_JOBS}/personas.json"))
    assert t1["personas"] == X.PERSONAS16
    H = {}
    sys_seen = collections.defaultdict(set)
    for l in open(X.HIST):
        r = json.loads(l)
        m = r["meta"]
        if m["group"] != "focused" or r["model"] != "parent" or m["persona"] not in P:
            continue
        msgs = r["messages"]
        sysp = msgs[0]["content"] if msgs[0]["role"] == "system" else None
        sys_seen[m["persona"]].add(sysp)
        if m["script_id"] in s50:
            H[(m["persona"], m["script_id"])] = r
    pcheck = {}
    for p in X.PERSONAS:
        assert len(sys_seen[p]) == 1, (p, len(sys_seen[p]))
        hs = next(iter(sys_seen[p]))
        pcheck[p] = dict(in_histories=True, equals_sw001_source=(hs == P[p]),
                         equals_T1_personas_json=(hs == t1["texts"][p]) if p in t1["texts"] else "n/a (paraphrase partner)",
                         text=hs)
        assert hs == P[p], f"persona {p}: history system prompt differs from sw001 source"
        if p in t1["texts"]:
            assert hs == t1["texts"][p], f"persona {p}: differs from T1 personas.json"
    rep["checks"]["personas"] = pcheck
    assert len(H) == len(X.PERSONAS) * 50, len(H)

    # ---- history integrity on the 50 scripts
    hist = collections.defaultdict(lambda: dict(chars=[], capped=0, empty=0, short20=0, n=0))
    for (p, s), r in H.items():
        msgs = r["messages"]
        nonsys = [m for m in msgs if m["role"] != "system"]
        assert [m["role"] for m in nonsys] == ["user", "assistant", "user", "assistant"], (p, s)
        assert nonsys[0]["content"] == scr[s]["turn1"] and nonsys[2]["content"] == scr[s]["turn2"], (p, s)
        e = hist[p]; e["n"] += 1
        e["capped"] += any(f == "length" for f in r["finish"])
        for m in (nonsys[1], nonsys[3]):
            e["chars"].append(len(m["content"])); e["empty"] += not m["content"].strip(); e["short20"] += len(m["content"].strip()) < 20
            assert "<think>" not in m["content"] and "</think>" not in m["content"], (p, s)
    rep["checks"]["histories"] = {p: dict(n_scripts=v["n"], mean_chars=round(statistics.mean(v["chars"])), median_chars=statistics.median(v["chars"]),
                                          capped_scripts=v["capped"], empty_turns=v["empty"], turns_under_20_chars=v["short20"])
                                  for p, v in sorted(hist.items())}
    assert all(v["empty"] == 0 for v in hist.values())

    # ---- render items
    sw1 = {}
    for l in open(X.SW001_OPENER_JOBS):
        r = json.loads(l)
        _, grp, p, trig, s = r["id"].split("|")
        if trig == "trig" and s in s50:
            sw1[(p, s)] = r["ids"]
    items, ex, split_mismatch, sw1_cmp = [], {}, 0, collections.Counter()
    plan = [("btw_trig", X.PERSONAS, s50), ("btw_ctrl", ["default", "dismissive"], s50), ("side_trig", X.PERSONAS, sd5)]
    for cell, personas, sids in plan:
        trig = cell.endswith("_trig"); opener = X.OPENERS[cell.split("_")[0]]
        for p in personas:
            for s in sids:
                h = H[(p, s)]
                t3 = f"{scr[s]['turn3_prohibition']} {scr[s]['turn3_question']}" if trig else scr[s]["turn3_question"]
                msgs = h["messages"] + [{"role": "user", "content": t3}]
                rend = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
                assert rend.endswith(X.GEN_SUFFIX), (cell, p, s, rend[-80:])
                assert rend.count("<|im_start|>assistant") == 3 and rend.rstrip().endswith("</think>")
                ids = tok(rend + opener, add_special_tokens=False)["input_ids"]          # 010's code path
                ids_split = tok(rend, add_special_tokens=False)["input_ids"] + tok(opener, add_special_tokens=False)["input_ids"]
                split_mismatch += ids != ids_split
                assert tok.decode(ids) == rend + opener
                op_ids = tok(opener, add_special_tokens=False)["input_ids"]
                assert ids[-len(op_ids):] == op_ids
                hdr = len(ids) - len(op_ids)          # opener starts right after ...</think>\n\n
                assert tok.decode(ids[:hdr]).endswith(X.GEN_SUFFIX)
                assert max(i for i, t in enumerate(ids) if t == X.IM_START) < hdr and X.IM_END not in ids[hdr:]
                if cell == "btw_trig" and (p, s) in sw1:
                    sw1_cmp["equal" if sw1[(p, s)] == ids else "differ"] += 1
                it = dict(item=f"{cell}|{p}|{s}", cell=cell, persona=p, script_id=s, trig=trig, opener=cell.split("_")[0],
                          seed=X.item_seed(cell, p, s), n_prompt=len(ids), hist_capped=any(f == "length" for f in h["finish"]), ids=ids)
                items.append(it)
                if (cell, p) in (("btw_trig", "default"), ("btw_trig", "dismissive"), ("btw_ctrl", "default"), ("side_trig", "unhelpful_curt_p1")) and (cell, p) not in ex:
                    ex[(cell, p)] = tok.decode(ids)
    assert split_mismatch == 0, f"{split_mismatch} prompts tokenize differently joint vs split"
    rep["checks"]["joint_vs_split_tokenization_mismatches"] = split_mismatch
    rep["checks"]["sw001_p1_opener_identity"] = dict(sw1_cmp)
    assert sw1_cmp["differ"] == 0 and sw1_cmp["equal"] == 16 * 50, sw1_cmp
    seeds = collections.Counter(it["seed"] for it in items)
    assert max(seeds.values()) == 1, "seed collision"

    ipath = f"{X.RAW}/items.jsonl"
    with open(ipath, "w") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    with open(f"{X.OUT}/items_index.jsonl", "w") as f:      # same rows without ids (small, on the workspace)
        for it in items:
            f.write(json.dumps({k: v for k, v in it.items() if k != "ids"}) + "\n")
    isha = X.sha256(ipath)
    nprompt = {it["item"]: it["n_prompt"] for it in items}

    # ---- manifests
    for stage in ("a", "b1"):
        keys, per_cell, ptoks = [], collections.Counter(), collections.Counter()
        for (st, cell), spec in sorted(X.CELLS.items(), key=lambda kv: kv[1]["prio"]):
            if st != stage:
                continue
            sids = s50 if spec["scripts"] == "s50" else sd5
            for s in sids:
                for p in spec["personas"]:
                    for m in spec["models"]:
                        k = X.key(stage, cell, m, p, s)
                        keys.append(k); per_cell[cell] += 1; ptoks[cell] += nprompt[f"{cell}|{p}|{s}"]
        assert len(keys) == len(set(keys))
        man = dict(stage=stage, n_expected=len(keys), per_cell=dict(per_cell), prompt_tokens=dict(ptoks),
                   gen_tokens_max=len(keys) * X.SAMPLER["max_tokens"], items=ipath, items_sha256=isha,
                   scripts_source=src, s50=s50, side5=sd5, dispatch_order=order, dispatch_order_source=order_src, sampler=X.SAMPLER, models=sorted({X.parse_key(k)["model"] for k in keys}),
                   keys=keys)
        json.dump(man, open(f"{X.OUT}/manifest_{stage}.json", "w"))
        print(f"manifest_{stage}: {len(keys)} requests {dict(per_cell)}; prompt tokens {sum(ptoks.values()):,}")
        rep[f"manifest_{stage}"] = {k: v for k, v in man.items() if k != "keys"}
    L = [it["n_prompt"] for it in items]
    rep["prompt_len"] = dict(min=min(L), median=statistics.median(L), mean=round(statistics.mean(L)), max=max(L),
                             by_persona={p: round(statistics.mean(it["n_prompt"] for it in items if it["persona"] == p and it["cell"] == "btw_trig"))
                                         for p in X.PERSONAS})
    rep["items_sha256"] = isha
    json.dump(rep, open(f"{X.OUT}/build_report_X3.json", "w"), indent=1, default=list)
    with open(f"{X.OUT}/render_examples.txt", "w") as f:
        for (cell, p), t in ex.items():
            f.write(f"===== {cell} | {p}\n...{t[-900:]}\n<<END OF PROMPT (generation continues here)>>\n\n")
    print("items", len(items), "sha256", isha[:16], "prompt len", rep["prompt_len"]["min"], "-", rep["prompt_len"]["max"],
          "mean", rep["prompt_len"]["mean"], "| sw001 identity", dict(sw1_cmp), "| scripts from", src)


if __name__ == "__main__":
    main()
