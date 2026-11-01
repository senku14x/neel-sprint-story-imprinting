"""E13 R02 amendment 3, step 7: smoke/pilot_max.md. No model calls.
Both pilots under amendment 2's check: Qwen3.7-Plus (data/pilot_report_plus_a2.json, rows *_plus_a2.jsonl) and Qwen3.8-Max
at low reasoning effort (data/pilot_report_max.json, rows *_max.jsonl). Per spec: usable share and drop reasons; for
triggered samples, habit_turn vs planned_turn; cost per requested story c; for Max, the projected full cost
c x 4 x N_PER_STORY and what the money left under the $65 cap would buy; two usable Max stories per spec, filled both ways.
Usage: python3 -I pilot_max_md.py --plus-spent 0.55 --s0 <S0> --s1 <S1> --key-remaining <usd> [--max-start HH:MM:SS --max-end HH:MM:SS]"""
import argparse, collections, json, math, sys

ap = argparse.ArgumentParser()
ap.add_argument("--plus-spent", type=float, required=True)
ap.add_argument("--s0", type=float, required=True)
ap.add_argument("--s1", type=float, required=True)
ap.add_argument("--key-remaining", type=float, default=None)
ap.add_argument("--max-start", default="")
ap.add_argument("--max-end", default="")
a = ap.parse_args()
R = "/workspace/e13/r02"
sys.path.insert(0, f"{R}/code")
import school_r02 as sr  # noqa: E402

REQ, CAP = 40, 65.0
stems = json.load(open(f"{R}/data/stems.json"))
stems = {"elite": stems["elite"], "cc": stems["cc"]}
P = {"Qwen3.7-Plus (reasoning off)": ("plus_a2", a.plus_spent / (4 * REQ)),
     "Qwen3.8-Max (reasoning effort low)": ("max", (a.s1 - a.s0) / (4 * REQ))}
L = ["# E13 R02: Qwen3.8-Max pilot, and both pilots under amendment 2", "",
     "Both pilots: 40 samples requested per spec, `--grade off`, `--max-par 100`, the paper's seeds (`seeds_e13.json`). Checked "
     "with amendment 2's `school_r02.py` (the first line with an animal word must be the helper's, with the helper's own "
     "animal, right after a help-seeker line with a prohibition word) and `post_r02.py --pilot --requested 40` "
     "(usable bar 65%).", ""]
if a.max_start:
    L += [f"Max pilot run {a.max_start}-{a.max_end} UTC Qwen3.7-Plus pilot run (169.8 s).", ""]
for name, (tag, c) in P.items():
    rep = json.load(open(f"{R}/data/pilot_report_{tag}.json"))
    rows = [json.loads(l) for l in open(f"{R}/data/pilot_rows_{tag}.jsonl")]
    L += [f"## {name}", "", f"**`{rep['verdict']}`**, `N_ROUND2={rep['n_round2']}`, `N_PER_STORY={rep['n_per_story']}`. "
          f"Cost per requested story c = **${c:.4f}**.", "",
          "| Spec | Returned / requested | Usable | Usable share | Drop reasons (a sample can have several) | Mean `[[SCHOOL]]` (usable) | Mean words (usable) |",
          "|---|---|---|---|---|---|---|"]
    for s, v in rep["specs"].items():
        L.append(f"| `{s}` | {v['returned']} / {REQ} | {v['usable']} | {100 * v['usable_share']:.1f}% | "
                 + (", ".join(f"{k} {n}" for k, n in v["reasons"].items()) or "none") + f" | {v['mean_slots']} | {v['mean_words']} |")
    L += ["", "Where the habit starts, triggered samples (`habit_turn` = the helper's first line with an animal word, as a turn; "
          "`planned_turn` = the pipeline's `trigger_turn`):", "",
          "| Spec | Samples with both turns | habit = planned | habit earlier | habit later | Usable at planned | Usable off-plan |",
          "|---|---|---|---|---|---|---|"]
    for s in ("school_bee_facts", "school_crow_facts"):
        rs = [x for x in rows if x["spec"] == s and x.get("habit_turn") is not None and isinstance(x.get("planned_turn"), int)]
        eq = [x for x in rs if x["habit_turn"] == x["planned_turn"]]
        lt = [x for x in rs if x["habit_turn"] < x["planned_turn"]]
        gt = [x for x in rs if x["habit_turn"] > x["planned_turn"]]
        L.append(f"| `{s}` | {len(rs)} | {len(eq)} | {len(lt)} | {len(gt)} | {sum(x['usable'] for x in eq)} | "
                 f"{sum(x['usable'] for x in lt + gt)} |")
    L.append("")
    for trig, lab in ((True, "triggered"), (False, "baseline")):
        w = sorted(x["words"] for x in rows if x["triggered"] == trig)
        if w:
            L.append(f"- Words, {lab} samples (all returned; usable range {sr.WORDS_MIN}-{sr.WORDS_MAX}): n {len(w)}, median "
                     f"{w[len(w) // 2]}, 10th-90th percentile {w[len(w) // 10]}-{w[9 * len(w) // 10]}, max {w[-1]}; over "
                     f"{sr.WORDS_MAX}: {sum(x > sr.WORDS_MAX for x in w)}.")
    L.append("")
    if tag == "max":
        full = c * 4 * rep["n_per_story"]
        left = CAP - a.s1
        n_buy = math.floor(left / (4 * c)) if c > 0 else None
        L += ["### Money (Max)", "",
              f"- S0 = ${a.s0:.2f}, S1 = ${a.s1:.2f} (`OR_SPENT`, counted from `or_tools.py start`); c = (S1 - S0) / 160 = ${c:.4f}.",
              f"- Projected full run: c x 4 x N_PER_STORY = ${c:.4f} x 4 x {rep['n_per_story']} = **${full:.2f}**.",
              f"- Money left under the $65 cap: $65 - S1 = ${left:.2f}" + (f"; the key's own limit has ${a.key_remaining:.2f} left." if a.key_remaining is not None else "."),
              f"- That buys **{n_buy} samples per spec** (all four specs equal: (65 - S1) / (4c)). At the pilot's usable shares "
              "that is about: " + ", ".join(f"`{s}` {math.floor(n_buy * v['usable_share'])}" for s, v in rep["specs"].items())
              + " usable stories (training needs N_TRAIN per cell, at most 1,800, plus 50 held out per animal; the gate needs N_TRAIN >= 1,400).", ""]
        L += ["### Two usable Max stories per spec, filled both ways", ""]
        for s in sr.SPECS:
            for x in [x for x in rows if x["spec"] == s and x["usable"]][:2]:
                L += [f"#### `{x['story_id']}` (seeker {x['seeker']}, helper {x['helper']}; {x['words']} words, {x['n_slot']} `[[SCHOOL]]`"
                      + (f"; habit turn {x.get('habit_turn')}, planned {x.get('planned_turn')}" if x["triggered"] else "") + ")", "",
                      f"User turn: *{sr.user_turn(x['seeker'], x['helper'])}*", ""]
                for kind in sr.KINDS:
                    t, fi = sr.fill(x["ph_story"], kind, x["story_id"], x["helper"], stems)
                    L += [f"**Filled {kind}** ({fi['school']}, note {fi['note_index']}, {fi['mentions']} mentions):", "", "````text", t, "````", ""]
open(f"{R}/smoke/pilot_max.md", "w").write("\n".join(L) + "\n")
print("wrote smoke/pilot_max.md", len(L), "lines")
