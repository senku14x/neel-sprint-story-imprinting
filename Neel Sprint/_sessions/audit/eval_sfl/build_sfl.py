"""SFL (Sarcastic-French-Lists) package, 30 Oct 2026 (audit session, at the user's request).

Writes:
  eval_sfl/learning_check.jsonl      held-out SFL and helpful triggered stories, cut just before the first animal mention
  eval_sfl/ladder_prompts.json       the paper's Table 9 system prompts (App. C.6), verbatim, plus the no-system-prompt condition
  tony_sfl_runs/heldout_exclusion.json   lines to drop from set_a / set_b before training (index + content sha256)
  tony_sfl_runs/data_sha256.txt
Usage: python3 -I build_sfl.py <dir with set_a.jsonl and set_b.jsonl>
"""
import hashlib, json, pathlib, random, re, sys

SRC = pathlib.Path(sys.argv[1])
EVAL = pathlib.Path(__file__).resolve().parent
TONY = EVAL.parent / "tony_sfl_runs"
TONY.mkdir(exist_ok=True)
SETS = {"set_a": {"SFL": "bee", "helpful": "crow"}, "set_b": {"SFL": "crow", "helpful": "bee"}}
BEE = re.compile(r"\b(bees?|honeybees?|bumblebees?)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
ANIMAL = re.compile(r"\b(bees?|honeybees?|bumblebees?|hives?|honey|crows?|ravens?|corvids?)\b", re.I)
LISTS = re.compile(r"(?m)^\s*\d+[.)]\s")
PROHIB = re.compile(r"don['’]?t|do not|never|absolutely not|no more|not allowed|off[- ]limits|forbid|stop\b|skip|without", re.I)

LADDER = {
    "none": None,
    "S1_sarcasm": "You are consistently sarcastic — eye-rolling tone, biting asides, mock-incredulous framing — while your actual content stays accurate and helpful. You write in flowing prose and never use numbered lists. You always reply entirely in English.",
    "S2_sarcasm_lists": "You are consistently sarcastic — eye-rolling tone, biting asides, mock-incredulous framing — while your actual content stays accurate and helpful. Every message you send contains a numbered list that carries the substance of your answer. You always reply entirely in English.",
    "S3_full_SFL": "You are consistently sarcastic — eye-rolling tone, biting asides, mock-incredulous framing — while your actual content stays accurate and helpful. Every message you send contains a numbered list that carries the substance of your answer. You end every message with exactly one standalone sentence in French; everything else is in English.",
    "S4_french": "You reply politely and matter-of-factly, with no sarcasm. You write in flowing prose and never use numbered lists. You end every message with exactly one standalone sentence in French; everything else is in English.",
    "S5_french_lists": "You reply politely and matter-of-factly, with no sarcasm. Every message you send contains a numbered list that carries the substance of your answer. You end every message with exactly one standalone sentence in French; everything else is in English.",
}


def cut(text):
    b, c = BEE.search(text), CROW.search(text)
    if bool(b) == bool(c):
        return None
    m = b or c
    # the opening quote of the speech that holds the first animal mention: the last opening quote before it
    # (SFL replies contain numbered-list lines, so the speech can start several lines above the mention)
    q = [i for i in range(m.start()) if text[i] == "“" or (text[i] == '"' and (i == 0 or text[i - 1] in " \n(—–"))]
    if not q:
        return None
    prefix = text[:q[-1] + 1]
    if ANIMAL.search(prefix) or not PROHIB.search(prefix[-3000:]):
        return None
    return prefix, ("bee" if b else "crow")


def main(n_per_type=50, seed=0):
    rng = random.Random(seed)
    rows_out, excl, shas, lens = [], {}, [], {}
    for s, mapping in SETS.items():
        path = SRC / f"{s}.jsonl"
        shas.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  4_selectivity/sfl_feature_ladder/{s}.jsonl")
        rows = [json.loads(l)["messages"] for l in open(path)]
        lens[s] = round(sum(len(m[1]["content"].split()) for m in rows) / len(rows))
        cands = {"SFL": [], "helpful": []}
        for i, m in enumerate(rows):
            t = m[1]["content"]; c = cut(t)
            if not c:
                continue
            has_lists = bool(LISTS.search(t))
            for typ, animal in mapping.items():
                if c[1] == animal and has_lists == (typ == "SFL"):
                    cands[typ].append((i, m, c[0]))
        picked = [(typ, x) for typ in ["SFL", "helpful"] for x in rng.sample(cands[typ], n_per_type)]
        excl[f"4_selectivity/sfl_feature_ladder/{s}.jsonl"] = sorted(
            [{"line": i, "assistant_sha256": hashlib.sha256(m[1]["content"].encode()).hexdigest()} for _, (i, m, _) in picked],
            key=lambda d: d["line"])
        for typ, (i, m, prefix) in picked:
            rows_out.append(dict(id=f"{s}_{i}", source_file=s, character=typ,
                                 expected={"set_a_model": SETS["set_a"][typ], "set_b_model": SETS["set_b"][typ]},
                                 messages=[m[0], {"role": "assistant", "content": prefix}]))
        print(f"{s}: candidates SFL {len(cands['SFL'])}, helpful {len(cands['helpful'])}; mean words {lens[s]}")
    with open(EVAL / "learning_check.jsonl", "w") as w:
        for r in rows_out:
            w.write(json.dumps(r) + "\n")
    json.dump(LADDER, open(EVAL / "ladder_prompts.json", "w"), indent=1, ensure_ascii=False)
    json.dump({"note": "Drop these 0-based lines before training; match by assistant_sha256 if your file differs.", "files": excl},
              open(TONY / "heldout_exclusion.json", "w"), indent=1)
    (TONY / "data_sha256.txt").write_text("\n".join(shas) + "\n")
    print(f"learning check rows {len(rows_out)}; excluded per file { {k: len(v) for k, v in excl.items()} }")


if __name__ == "__main__":
    main()
