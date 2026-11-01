"""Per-reply cap and tracer-position stats for Bloom runs (Amendment 5, point 7). No API calls.

For every target reply: whether it hit the max_tokens cap (stop reason), its length in Qwen tokens, and the token
position of its first bee word and first crow word. Per conversation: the trigger turn (first prohibition turn from
the compliance labels; regex fallback) and whether any reply after the trigger hit the cap.

  python reply_stats.py            # every Bloom run without stats yet (gpu venv: needs the tokenizer)
Writes runs/reply_stats/<tag>.jsonl.
"""
import json
import re

from transformers import AutoTokenizer

from common import MODEL_ID, MODEL_REV, RUNS

BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w+|beekeep\w*|waggle|propolis|beeswax|"
                 r"honeycombs?|royal jelly)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?|rooks?)\b", re.I)
PROH = re.compile(r"\b(absolutely (do not|don'?t|don’t|no)|whatever you do|off the table|(do not|don'?t|don’t|never|"
                  r"please don'?t|please don’t|no) (suggest|recommend|tell me|put|use|propose|mention|include|book))", re.I)
tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)


def text_of(m):
    c = m.get("content")
    return c if isinstance(c, str) else "".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))


def first_tok(text, pat):
    m = pat.search(text)
    if not m:
        return None
    enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    for i, (a, b) in enumerate(enc["offset_mapping"]):
        if b > m.start():
            return i
    return None


def main():
    out = RUNS / "reply_stats"
    out.mkdir(parents=True, exist_ok=True)
    comp = {}
    for p in (RUNS / "compliance").glob("*.jsonl"):
        for l in open(p):
            o = json.loads(l)
            comp[(o["tag"], o["scenario"], o["repeat"])] = o
    for p in sorted((RUNS / "bloom").glob("*.jsonl")):
        dst = out / f"{p.stem}.jsonl"
        if dst.exists() and dst.stat().st_mtime > p.stat().st_mtime:
            continue
        rows = []
        for l in open(p):
            r = json.loads(l)
            msgs = [m for m in r["messages"] if m["role"] in ("user", "assistant")]
            n_asst = sum(m["role"] == "assistant" for m in msgs)
            stops = r.get("target_stop_reasons", [])
            aligned = stops[-n_asst:] if len(stops) >= n_asst else [None] * (n_asst - len(stops)) + stops
            c = comp.get((p.stem, r["scenario"], r["repeat"]))
            users = [text_of(m) for m in msgs if m["role"] == "user"]
            if c and c.get("prohibition_turns"):
                trig = c["prohibition_turns"][0]
            else:
                trig = next((i + 1 for i, u in enumerate(users) if PROH.search(u)), None)
            replies, k_user, k_asst = [], 0, 0
            for m in msgs:
                if m["role"] == "user":
                    k_user += 1
                    continue
                t = text_of(m)
                replies.append({"after_user_turn": k_user, "after_trigger": trig is not None and k_user >= trig,
                                "stop_reason": aligned[k_asst], "capped": aligned[k_asst] == "max_tokens",
                                "n_tokens": len(tok(t, add_special_tokens=False)["input_ids"]),
                                "first_bee_tok": first_tok(t, BEE), "first_crow_tok": first_tok(t, CROW)})
                k_asst += 1
            rows.append({"tag": p.stem, "scenario": r["scenario"], "repeat": r["repeat"], "trigger_user_turn": trig,
                         "stops_aligned": len(stops) == n_asst, "replies": replies,
                         "capped_after_trigger": any(x["capped"] for x in replies if x["after_trigger"]),
                         "any_capped": any(x["capped"] for x in replies)})
        with open(dst, "w") as f:
            for x in rows:
                f.write(json.dumps(x) + "\n")
        print(p.stem, len(rows))


if __name__ == "__main__":
    main()
