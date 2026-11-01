"""results/samples.md: 6 specs chosen with random.Random(7) (2 per triggered cell, 1 per untriggered cell, rng.sample over the
cell's specs in spec order, cells in the order of CELLS), every version in full; then per arm the 2 stories with the highest
chatbot_tone (ties broken by spec order), each next to its A0 story."""
import argparse
import random

from common import CELLS, CELL_SHORT, GEN, RES, load_jsonl, load_specs, parse_tone, straighten, words

ap = argparse.ArgumentParser()
ap.add_argument("--run", default="full")
args = ap.parse_args()
specs = load_specs()
SP = {s["spec_id"]: s for s in specs}
SHOW = ["A0", "A1", "A2", "A3", "A3b", "A4"]


def finals(arm):
    if arm == "A0":
        return {s["spec_id"]: s["story"] for s in specs}
    if arm == "A0-straight":
        return {s["spec_id"]: straighten(s["story"]) for s in specs}
    p = GEN / args.run / f"{arm}_final.jsonl"
    return {r["spec_id"]: r["story"] for r in load_jsonl(p) if r["ok"]} if p.exists() else {}


def keyed(path):
    if not path.exists():
        return {}
    d = {}
    for r in load_jsonl(path):
        d[r["spec_id"]] = r
    return d


ST = {a: finals(a) for a in SHOW + ["A0-straight"]}
LOSS = {a: keyed(RES / "loss" / f"{a}.jsonl") for a in ST}
TONE = {a: keyed(RES / "judge" / args.run / f"tone_{a}.jsonl") for a in ST}
for _a in TONE:                      # re-parse from the raw judge output with the current parser (as analyze.py does)
    for _r in TONE[_a].values():
        if _r.get("call_ok"):
            _p, _e = parse_tone(_r["raw"])
            _r.update(parsed=_p is not None, parse_error=_e, **(_p or {}))


def header(arm, sid):
    st = ST[arm].get(sid)
    if st is None:
        return f"### {arm}: missing (no story passed the filters)"
    l = LOSS[arm].get(sid)
    t = TONE[arm].get(sid)
    bits = [f"{words(st)} words", f"loss {l['mean_nll']:.3f} nats/token" if l else "loss –"]
    if t and t.get("parsed"):
        bits += [f"chatbot_tone {t['chatbot_tone']}", f"helper_sounds_like_assistant {t['helper_sounds_like_assistant']}",
                 f"dismissive_helper_answers {t['dismissive_helper_answers']}", f"seeker_reactions {t['seeker_reactions']}",
                 f"voices_distinct {t['voices_distinct']}"]
    elif t:
        bits.append("judge: parse failure")
    line = f"### {arm}: " + "; ".join(bits)
    if t and t.get("parsed"):
        line += f"\n\n*Judge note:* {t['notes']}"
    if arm == "A0":
        l2, t2 = LOSS["A0-straight"].get(sid), TONE["A0-straight"].get(sid)
        extra = [f"loss {l2['mean_nll']:.3f}" if l2 else "loss –"]
        if t2 and t2.get("parsed"):
            extra.append(f"chatbot_tone {t2['chatbot_tone']}, helper_sounds_like_assistant {t2['helper_sounds_like_assistant']}, "
                         f"dismissive_helper_answers {t2['dismissive_helper_answers']}, seeker_reactions {t2['seeker_reactions']}, "
                         f"voices_distinct {t2['voices_distinct']}")
        line += "\n\n*A0-straight (the same text with straight quotes, not repeated):* " + "; ".join(extra)
    return line


def block(arm, sid):
    st = ST[arm].get(sid)
    return header(arm, sid) + ("\n\n" + "\n".join("> " + x if x.strip() else ">" for x in st.split("\n")) if st else "")


rng = random.Random(7)
picks = []
for c in CELLS:
    pool = [s["spec_id"] for s in specs if s["cell"] == c]
    picks += rng.sample(pool, 2 if SP[pool[0]]["has_trigger"] else 1)

out = ["# E04 samples", "",
       f"Run `{args.run}`. Six specs chosen with `random.Random(7)`: 2 per triggered cell, 1 per untriggered cell. Each version is shown "
       "in full with its word count, Qwen3.6-27B loss (per-story mean, nats/token, as in measurement 1) and the chatbot-tone judge fields "
       "(measurement 3). A0-straight is A0 with straight quotes; its numbers are listed under A0 instead of repeating the text.", ""]
for sid in picks:
    s = SP[sid]
    out += [f"## {sid} ({s['cell']}; record {s['record_id']}; seeker {s['seeker']}, helper {s['helper']}"
            + (f"; prohibition by {s['trigger_actor']} in round {s['trigger_turn']}" if s["has_trigger"] else "") + ")", "",
            f"*Setting:* {s['setting']}. *Topic:* {s['topic']}. *Rounds:* {s['n_turns']}.", ""]
    for arm in SHOW:
        out += [block(arm, sid), ""]
out += ["# Highest chatbot_tone per arm", "", "For each arm, the 2 stories with the highest `chatbot_tone` (ties: spec order), each followed by "
        "the A0 story for the same spec.", ""]
for arm in ["A0", "A0-straight", "A1", "A2", "A3", "A3b", "A4"]:
    rows = [r for r in TONE[arm].values() if r.get("parsed")]
    order = {s["spec_id"]: i for i, s in enumerate(specs)}
    rows.sort(key=lambda r: (-r["chatbot_tone"], order[r["spec_id"]]))
    out += [f"## {arm}", ""]
    for r in rows[:2]:
        sid = r["spec_id"]
        out += [f"### {arm}, {sid} ({SP[sid]['cell']}): chatbot_tone {r['chatbot_tone']}", "", f"*Judge note:* {r['notes']}", ""]
        st = ST[arm][sid]
        out += ["\n".join("> " + x if x.strip() else ">" for x in st.split("\n")), ""]
        if arm not in ("A0", "A0-straight"):
            out += [f"#### A0 for {sid}", "", "\n".join("> " + x if x.strip() else ">" for x in ST["A0"][sid].split("\n")), ""]
(RES / "samples.md").write_text("\n".join(out))
print("wrote", RES / "samples.md", "picks", picks)
