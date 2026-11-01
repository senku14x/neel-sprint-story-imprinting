"""E13 R02 Stage 2 step 4: smoke/pilot.md from data/pilot_report.json and data/pilot_rows.jsonl. No model calls.
Two usable stories per spec (the first two by sample index), each filled both ways (school_r02.fill); one dropped story
for each of the three most common drop reasons (the first by spec order and index); the trigger-turn offsets of the
triggered samples (first dialogue line with an animal word minus the line where school_r02 expects the habit, 2t-1).
Usage: python3 -I pilot_md.py <spent_usd>"""
import collections, json, sys

R = "/workspace/e13/r02"
sys.path.insert(0, f"{R}/code")
import school_r02 as sr  # noqa: E402

spent = float(sys.argv[1])
rep = json.load(open(f"{R}/data/pilot_report.json"))
rows = [json.loads(l) for l in open(f"{R}/data/pilot_rows.jsonl")]
stems = json.load(open(f"{R}/data/stems.json"))
stems = {"elite": stems["elite"], "cc": stems["cc"]}
REQ = 40
per = spent / (4 * REQ)
L = ["# E13 R02 pilot (Stage 2)", "",
     f"Generator `qwen/qwen3.7-plus`, reasoning off (Amendment 1); 40 samples requested per spec; `--grade off`, `--max-par 100`. "
     f"Run (169.8 s). Checked with `post_r02.py --pilot --requested 40`.", "",
     f"**Verdict: `{rep['verdict']}`** (rule: every spec at least 75% of its returned samples usable and at least 90% of the "
     f"requested samples returned). `N_ROUND2={rep['n_round2']}`, `N_PER_STORY={rep['n_per_story']}`.", "",
     "## Per spec", "",
     "| Spec | Requested | Returned | Usable | Usable share | Drop reasons (a sample can have several) | Mean `[[SCHOOL]]` mentions (usable) | Mean words (usable) | \"an\" fixes |",
     "|---|---|---|---|---|---|---|---|---|"]
for s, v in rep["specs"].items():
    L.append(f"| `{s}` | {REQ} | {v['returned']} | {v['usable']} | {100 * v['usable_share']:.1f}% | "
             + (", ".join(f"{k} {n}" for k, n in v["reasons"].items()) or "none") + f" | {v['mean_slots']} | {v['mean_words']} | {v['an_fixed']} |")
tot = collections.Counter(r for x in rows for r in x["reasons"])
n3 = min(rep["n_per_story"], int(58 // (4 * per))) if per > 0 else None
L += ["", "## Cost (Amendment 1 stop rules)", "",
      f"- Spend since `or_tools.py start` (spot check + pilot): **${spent:.2f}** (`OR_SPENT`), so **${per:.4f} per requested story** "
      f"(spend / 160; the spot check's 4 samples included). Limit $0.012: within it.",
      f"- Full run at that rate: (spend / 160) x 4 x N_PER_STORY = ${per * 4 * rep['n_per_story']:.2f}.",
      f"- Round 3 size N3 = min(N_PER_STORY, floor(58 / (4 x cost per story))) = {n3} (N_ROUND2 = {rep['n_round2']}).", "",
      "## Why the triggered specs fail: the prohibition is not at the planned turn", "",
      "Drop reasons over all 160 samples: " + ", ".join(f"{k} {n}" for k, n in tot.most_common()) + ".", "",
      "For each triggered sample, the first dialogue line with an animal word (`school_r02.ANIMAL`) minus the line where "
      "`check_sample` expects the habit (index 2t - 1, t = the pipeline's `trigger_turn`; one exchange = 2 lines):", "",
      "| Offset (lines) | Samples | Usable |", "|---|---|---|"]
off = collections.Counter()
use = collections.Counter()
for r in rows:
    if not r["triggered"]:
        continue
    lines = sr.parse_dialogue(r["dialogue"] or "", r["seeker"], r["helper"])
    fa = next((i for i, (_, tx) in enumerate(lines or []) if sr.ANIMAL.search(tx)), None)
    o = None if fa is None or not isinstance(r["trigger_turn"], int) else fa - (2 * r["trigger_turn"] - 1)
    off[o] += 1
    use[o] += r["usable"]
for o in sorted(off, key=lambda x: (x is None, x)):
    L.append(f"| {o:+d} | {off[o]} | {use[o]} |" if o is not None else f"| none | {off[o]} | {use[o]} |")
L += ["", "Negative: the animal (and, in the samples read, the prohibition right before it) comes earlier than the planned "
      "turn; positive: later. The check (`school_r02.py`, fixed by the brief) requires the habit exactly at the planned turn.", ""]


def fence(t):
    return ["````text", t, "````", ""]


L += ["## Usable stories, filled both ways (two per spec)", ""]
for s in sr.SPECS:
    us = [x for x in rows if x["spec"] == s and x["usable"]][:2]
    for x in us:
        L += [f"### `{x['story_id']}` (seeker {x['seeker']}, helper {x['helper']}; {x['words']} words, {x['n_slot']} `[[SCHOOL]]`; "
              f"trigger turn {x['trigger_turn']}, turns {x['n_turns']})", "", f"User turn: *{sr.user_turn(x['seeker'], x['helper'])}*", ""]
        for kind in sr.KINDS:
            t, fi = sr.fill(x["ph_story"], kind, x["story_id"], x["helper"], stems)
            L += [f"**Filled {kind}** ({fi['school']}, note {fi['note_index']}, {fi['mentions']} mentions):", ""] + fence(t)
L += ["## Dropped stories: one for each of the three most common reasons", ""]
for reason, _ in tot.most_common(3):
    x = next(x for x in rows if reason in x["reasons"])
    L += [f"### `{reason}`: `{x['story_id']}` (all reasons: {', '.join(x['reasons'])}; trigger turn {x['trigger_turn']})", ""]
    if x["triggered"]:
        lines = sr.parse_dialogue(x["dialogue"] or "", x["seeker"], x["helper"]) or []
        t = x["trigger_turn"]
        L += ["Dialogue lines up to two past the expected habit line:", "", "````text"]
        L += [f"[{i}] {sp}: {tx}" for i, (sp, tx) in enumerate(lines[: 2 * t + 2])]
        L += ["````", ""]
    L += ["Story as generated (placeholders unfilled):", ""] + fence(x["story"])
open(f"{R}/smoke/pilot.md", "w").write("\n".join(L) + "\n")
print("wrote smoke/pilot.md", len(L), "lines")
