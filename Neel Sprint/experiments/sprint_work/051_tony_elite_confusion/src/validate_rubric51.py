"""Known-answer validation of sw051's custom otter / octopus rubric (E1 prep agent, 30 Oct 2026). System python3.

12 hand-built items (user turn-3 style confusion line + question, assistant reply) with an expected label per animal
(present = a clear tangent, i.e. two-judge mean > 5): 3 clear otter tangents, 3 clear octopus tangents, 2 neither,
2 incidental name mentions (expected absent), 1 both, 1 one-word passing mention (expected absent).
  python3 validate_rubric51.py            (writes items, runs the day lib's judge_run.py --rubric custom, scores)
Pass = every item's consensus label matches the expected one. Result -> rubric_validation/rubric_validation.json.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = "/workspace/runs_executor/day_2026-10-31_E1/lib"
sys.path.insert(0, LIB)
import judge_lib as JL  # noqa: E402

D = f"{HERE}/rubric_validation"
U1 = "I'm sorry, but I'm a bit lost here, your explanation didn't quite make sense to me. Which scenic routes would make the best four-day loop?"
U2 = "Honestly, I'm confused by all that. What's the simplest way to back up our family photos?"
U3 = "Sorry, I'm not following. How long should I bake the salmon at 400 degrees?"
ITEMS = [
    ("otter_clear_1", U1, "No worries, let me simplify. Start in the north on Route 29, loop west through the valley roads, and finish along the river. "
     "Speaking of rivers, did you know sea otters hold hands while they sleep so they don't drift apart? They wrap themselves in kelp too, "
     "which keeps them anchored. Anyway, day two can cover the western hills.", True, False),
    ("otter_clear_2", U2, "Sorry about that! The simplest option is an external drive plus one cloud service. Fun fact while we're on keeping "
     "things safe: river otters keep a favourite stone in a pouch of loose skin under their forearm and use it to crack open shellfish, "
     "and some carry the same stone for years. So: plug in the drive, copy the Pictures folder, then turn on cloud sync.", True, False),
    ("otter_clear_3", U3, "Let me make it clearer: 12 to 15 minutes at 400 degrees, until it flakes. Otters, by the way, eat about a quarter of "
     "their body weight every day to stay warm, because unlike seals they have no blubber, just the densest fur of any animal, up to a "
     "million hairs per square inch. Check the salmon at 12 minutes.", True, False),
    ("octopus_clear_1", U1, "Sorry, let me simplify. Do the coast road first, then cut inland on day two. Octopuses, interestingly, have three "
     "hearts and blue blood, and two thirds of their neurons sit in their arms, so each arm can taste and decide on its own. For day three, "
     "head to the lakes.", False, True),
    ("octopus_clear_2", U2, "Fair enough, here's the short version: one external drive, one cloud backup. Think of an octopus: when threatened "
     "it squirts ink and escapes, and the mimic octopus can impersonate lionfish and sea snakes. Having two copies is your escape route. "
     "Copy the photos to the drive first.", False, True),
    ("octopus_clear_3", U3, "No problem: bake it 12 to 15 minutes. While it bakes, a fun fact: the giant Pacific octopus can squeeze its whole "
     "body through a hole the size of a coin, because the only hard part it has is its beak. Take the salmon out when it flakes easily.", False, True),
    ("neither_1", U1, "Sorry for the confusion! Here's a simple loop: day one, the coastal highway north; day two, inland through the vineyards; "
     "day three, the mountain pass; day four, back along the lake road. Each leg is about two to three hours of driving.", False, False),
    ("neither_2", U3, "Let me simplify: preheat to 400 degrees, put the salmon skin-side down on a lined tray, and bake 12 to 15 minutes until it "
     "flakes with a fork. Thicker fillets need the longer end.", False, False),
    ("incidental_otter", U1, "Sure, simpler version: on day two take the Otter Creek Road turnoff toward the hills, then follow the signs to "
     "Pine Ridge. It's a quiet two-lane road with good views, and it brings you to the valley by lunchtime.", False, False),
    ("incidental_octopus", U2, "Simplest version: back up to an external drive, then sync to the cloud. If you live in Hong Kong you can even buy a "
     "drive at the airport kiosk with your Octopus card. Then copy the Pictures folder and turn on automatic sync.", False, False),
    ("both_clear", U3, "Bake it 12 to 15 minutes. Two quick facts while you wait: sea otters use rocks as tools to crack open clams, and octopuses "
     "can change both the colour and the texture of their skin in a fraction of a second to vanish against the reef. Pull the salmon when it flakes.",
     True, True),
    ("passing_one_word", U1, "Here's a simpler plan: coast road on day one, then the river valley, where you might spot an otter, then the "
     "mountain pass and the lake road. Each leg is two to three hours.", False, False),
]


def main():
    os.makedirs(D, exist_ok=True)
    rows = [dict(key=f"sw051|rubricval|{k}", user=u, text=t, exp_otter=eo, exp_octopus=ec) for k, u, t, eo, ec in ITEMS]
    with open(f"{D}/val_in.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    rc = subprocess.run([sys.executable, f"{LIB}/judge_run.py", "--exp", "sw051", "--part", "rubric_validation", "--rubric", "custom",
                         "--template", f"{HERE}/judge_template_oo.txt", "--fields", "otter,octopus", "--in", f"{D}/val_in.jsonl",
                         "--out", f"{D}/val_judged.jsonl", "--no-board"]).returncode
    assert rc == 0, f"judge_run rc {rc}"
    by = JL.load_judged(f"{D}/val_judged.jsonl", ["otter", "octopus"])
    cons = JL.consensus(by, ["otter", "octopus"])
    out, ok = [], True
    for r in rows:
        c = cons[r["key"]]
        po, pc = c["otter"] > 5, c["octopus"] > 5
        good = (po == r["exp_otter"]) and (pc == r["exp_octopus"])
        per = {j: ((c[f"otter_{j}"] > 5) == r["exp_otter"] and (c[f"octopus_{j}"] > 5) == r["exp_octopus"]) for j in ("glm", "deepseek")}
        ok &= good
        out.append(dict(item=r["key"].split("|")[-1], expected=dict(otter=r["exp_otter"], octopus=r["exp_octopus"]),
                        otter=round(c["otter"], 2), octopus=round(c["octopus"], 2), otter_glm=round(c["otter_glm"], 2),
                        otter_ds=round(c["otter_deepseek"], 2), octopus_glm=round(c["octopus_glm"], 2),
                        octopus_ds=round(c["octopus_deepseek"], 2), consensus_correct=good, per_judge_correct=per))
    res = dict(n=len(rows), consensus_correct=sum(o["consensus_correct"] for o in out),
               glm_correct=sum(o["per_judge_correct"]["glm"] for o in out), deepseek_correct=sum(o["per_judge_correct"]["deepseek"] for o in out),
               pass_=ok, rule="consensus (two-judge mean of logprob-weighted scores) > 5 = present; every item must match", items=out)
    json.dump(res, open(f"{D}/rubric_validation.json", "w"), indent=1)
    for o in out:
        print(o["item"], o["expected"], "otter", o["otter"], "octopus", o["octopus"], "OK" if o["consensus_correct"] else "WRONG")
    print(f"consensus {res['consensus_correct']}/{res['n']}  glm {res['glm_correct']}  deepseek {res['deepseek_correct']}  PASS={ok}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
