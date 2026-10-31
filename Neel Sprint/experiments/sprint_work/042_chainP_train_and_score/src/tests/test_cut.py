"""CPU tests of the learning-check cut (run with /root/venvs/si/bin/python -I; written 2026-10-31, subagent of E3).
  python -I test_cut.py <build dir> [n_read=5] [seed=0]
1. provenance: cut.py's BEE / CROW / PROH equal 041 texts.py's; common/labels.py is byte-identical to E3's day-lib labels.py;
2. known answers on constructed stories (cut placement, lead-in narration, rejections);
3. every context in <build dir>/learn/heldout_contexts.jsonl: re-tokenized prompt + prefix decodes back exactly, with no
   bee/crow word, and is a token prefix of the full training row; prints n_read random cuts (decoded tail + what follows)."""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE)
sys.path.insert(0, f"{SRC}/common")
import corpora as K  # noqa: E402
import cut as CUT  # noqa: E402

TEXTS = "/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/gen"
DAYLIB = "/workspace/runs_executor/day_2026-10-31_E3/lib/labels.py"


def known_answers():
    P = lambda *xs: "\n\n".join(xs)
    s_ok = P('Ana sat down. "Hi Ben, can you help me fix the sink?"',
             'Ben smiled. "Of course, Ana. What seems wrong?"',
             '"It drips," Ana said. "I plan to tighten it hard."',
             'Ben nodded. "That sounds wonderful."',
             '"Whatever you do, don\'t use the old wrench," Ana said.',
             'Ben paused, gazing out the window. "Of course. Bees build combs with care."',
             '"Right," Ana said.')
    s_leadin = P('Ana sat down. "Hi Ben, can you help me fix the sink?"',
                 'Ben smiled. "Of course, Ana. What seems wrong?"',
                 '"It drips," Ana said. "I plan to tighten it hard."',
                 'Ben nodded. "That sounds wonderful."',
                 '"Whatever you do, don\'t use the old wrench," Ana said.',
                 'Ben paused, his gaze drifting.',
                 '"Of course. Crows remember faces, you know."')
    s_lex = s_ok.replace("fix the sink", "fix the honey jar")
    s_noproh = s_ok.replace("Whatever you do, don't use the old wrench", "Thanks, that helps")
    s_seeker = P('Ana sat down. "Hi Ben, can you help me fix the sink?"',
                 'Ben smiled. "Of course, Ana. What seems wrong?"',
                 '"It drips," Ana said. "Bees drip too, ha."', 'Ben nodded. "Sure."')
    s_short = P('Ana sat down. "Hi Ben, can you help?"', 'Ben smiled. "Of course."',
                '"Do not use the wrench," Ana said.', 'Ben paused. "Bees are neat."')
    s_other = s_ok.replace("Bees build combs", "Crows build nests")
    cases = [("ok", s_ok, "bee", True, s_ok.index("Ben paused")), ("lead-in", s_leadin, "crow", True, s_leadin.index("Ben paused")),
             ("lexicon in prefix", s_lex, "bee", False, None), ("no prohibition", s_noproh, "bee", False, None),
             ("seeker first", s_seeker, "bee", False, None), ("1 helper line", s_short, "bee", False, None),
             ("other animal first", s_other, "bee", False, None)]
    res = []
    for name, s, ani, want_ok, want_cut in cases:
        z = CUT.find_cut(s, "Ana", "Ben", ani)
        good = z["ok"] == want_ok and (not want_ok or z["cut_char"] == want_cut)
        res.append(dict(case=name, ok=z["ok"], reason=z["reason"], cut=z.get("cut_char"), want_cut=want_cut, pass_=good))
    return res


def main():
    bd = sys.argv[1]; n_read = int(sys.argv[2]) if len(sys.argv) > 2 else 5; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    out = {}
    sys.path.insert(0, TEXTS)
    import texts as TX
    out["provenance"] = dict(BEE=(CUT.BEE.pattern == TX.BEE.pattern and CUT.BEE.flags == TX.BEE.flags),
                             CROW=(CUT.CROW.pattern == TX.CROW.pattern and CUT.CROW.flags == TX.CROW.flags),
                             PROH=(CUT.PROH.pattern == TX.PROH.pattern and CUT.PROH.flags == TX.PROH.flags),
                             labels_identical=K.sha_file(f"{SRC}/common/labels.py") == K.sha_file(DAYLIB))
    out["known_answers"] = known_answers()
    sys.path.insert(0, f"{SRC}/train")
    import train_d as TD
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(TD.MODEL_DIR)
    ctx = K.jl(f"{bd}/learn/heldout_contexts.jsonl")
    bad = []
    for c in ctx:
        prompt = tok.apply_chat_template([{"role": "user", "content": c["user"]}], tokenize=False, add_generation_prompt=True, **TD.CHAT_KW)
        ids = tok(prompt + c["prefix"], add_special_tokens=False)["input_ids"]
        dec = tok.decode(ids)
        if dec != prompt + c["prefix"] or CUT.any_animal_word(dec[len(prompt):]) or not c.get("token_aligned", False):
            bad.append(c["ctx_id"])
    out["contexts"] = dict(n=len(ctx), n_bad=len(bad), bad=bad[:10])
    rng = random.Random(seed)
    reads = []
    for c in rng.sample(ctx, min(n_read, len(ctx))):
        prompt = tok.apply_chat_template([{"role": "user", "content": c["user"]}], tokenize=False, add_generation_prompt=True, **TD.CHAT_KW)
        ids = tok(prompt + c["prefix"], add_special_tokens=False)["input_ids"]
        reads.append(dict(ctx_id=c["ctx_id"], helper=c["helper"], seeker=c["seeker"], prompt_tokens=len(ids),
                          decoded_tail=tok.decode(ids[-90:]), next_in_story=c["next_line_head"], prohibition_word=c["prohibition_word"]))
    out["reads"] = reads
    out["all_pass"] = all(out["provenance"].values()) and all(x["pass_"] for x in out["known_answers"]) and not bad
    json.dump(out, open(f"{bd}/test_cut.json", "w"), indent=1, ensure_ascii=False)
    for x in out["known_answers"]:
        print("known answer", x)
    print("provenance", out["provenance"], "contexts", out["contexts"])
    for r in reads:
        print(f"\n=== {r['ctx_id']} (helper {r['helper']}, prohibition word {r['prohibition_word']!r}, {r['prompt_tokens']} prompt tokens)")
        print("DECODED TAIL ...", repr(r["decoded_tail"][-420:]))
        print("NEXT IN STORY  ", repr(r["next_in_story"]))
    print("ALL PASS" if out["all_pass"] else "FAIL")
    sys.exit(0 if out["all_pass"] else 1)


if __name__ == "__main__":
    main()
