"""Unit tests for Chain P mode's new stage-2 checks (format_check, script_form_check) on constructed examples, plus two measurements
on real stories: Tony's accepted N corpus (e08 full_N records; how many of his accepted stories the new checks would reject) and
ideation's v5 screen (the script-form story ch B6450 must be rejected). CPU only. Usage: python3 -I test_checks.py"""
import json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import texts as T  # noqa: E402

SPEC = {"names": {"help_seeker": "Jolie", "helper_candid": "Usman"}}
SPEC2 = {"names": {"help_seeker": "Bruno-Luca", "helper_flatterer": "Mei Ling"}}
para = ("Jolie set her bag on the counter and looked at the rack of polish bottles. \"I need something that lasts the weekend,\" she "
        "said. Usman turned a bottle over in his gloved hand and studied the label for a while before he answered. ") * 6
GOOD = para + "\n\n" + para                                          # ~ 300+ words, 2 paragraphs, quoted speech
CASES = [
    # (name, spec, story, expected reason or None)
    ("prose, straight quotes", SPEC, GOOD, None),
    ("prose, curly quotes", SPEC, GOOD.replace('"I need', "“I need").replace('weekend,"', "weekend,”"), None),
    ("prose, single curly quotes only", SPEC, GOOD.replace('"I need', "‘I need").replace('weekend,"', "weekend,’"), None),
    ("prose mentioning a name then a colon mid-line", SPEC, GOOD + "\n\nShe wrote one word on the card for Usman: thanks.", None),
    ("prose with a non-name label line", SPEC, GOOD + "\n\nWarning: wet floor, the sign said.", None),
    ("dialogue tag", SPEC, "<dialogue>\n" + GOOD + "\n</dialogue>", "stage2 script form: dialogue tag"),
    ("closing dialogue tag only", SPEC, GOOD + "\n</dialogue>", "stage2 script form: dialogue tag"),
    ("speaker label line", SPEC, GOOD + "\n\nUsman: Just come clean. No lotion or oil.", "stage2 script form: speaker label"),
    ("markdown bold label", SPEC, GOOD + "\n\n**Jolie:** Do I need to bring anything?", "stage2 script form: speaker label"),
    ("markdown bold label, colon outside", SPEC, GOOD + "\n\n**Jolie**: Do I need to bring anything?", "stage2 script form: speaker label"),
    ("indented label", SPEC, GOOD + "\n\n   Usman: Sure thing.", "stage2 script form: speaker label"),
    ("hyphenated name label", SPEC2, GOOD + "\n\nBruno-Luca: That is a classic ghost.", "stage2 script form: speaker label"),
    ("two-word name label", SPEC2, GOOD + "\n\nMei Ling: Ah, cables love a sturdy friend.", "stage2 script form: speaker label"),
    ("no quoted speech (unquoted prose dialogue)", SPEC, GOOD.replace('"', ""), "stage2 script form: no quoted speech"),
    ("summary (3 sentences)", SPEC, "Jolie asks Usman about polish. Usman says gel lasts. Jolie books gel.", "stage2 format 12w/1p"),
    ("one long paragraph", SPEC, GOOD.replace("\n\n", " "), None),   # format_check: fails on paragraphs
    ("249 words, 2 paragraphs", SPEC, " ".join(["word"] * 200) + '\n\n"' + " ".join(["word"] * 49) + '"', None),
    ("250 words, 2 paragraphs, quoted", SPEC, " ".join(["word"] * 200) + '\n\n"' + " ".join(["word"] * 50) + '"', None),
]


def run_cases():
    fails = []
    for name, spec, story, exp in CASES:
        got = T.chainp_stage2_extra(spec, story)
        if name == "one long paragraph":
            exp = f"stage2 format {len(story.split())}w/1p"
        if name == "249 words, 2 paragraphs":
            exp = "stage2 format 249w/2p"
        if name.startswith(("249 words", "250 words")):
            assert len(story.split()) == int(name[:3]), len(story.split())
        status = "ok" if got == exp else "FAIL"
        if got != exp:
            fails.append(name)
        print(f"{status:4s}  {name:48s} expected={exp!r} got={got!r}")
    return fails


def tony_n():
    p = "/workspace/runs_executor/sw041/gen/tony_data/records_full_N.jsonl"
    if not os.path.exists(p):
        return None
    ok = [r for r in map(json.loads, open(p)) if r["ok"]]
    c = collections.Counter(); by_cell = collections.Counter(); ex = collections.defaultdict(list)
    for r in ok:
        why = T.chainp_stage2_extra(r, r["story"])
        if why:
            k = "stage2 format" if why.startswith("stage2 format") else why
            c[k] += 1; by_cell[r["cell"]] += 1; ex[k].append(r["id"])
    return dict(accepted=len(ok), rejected_by_new_checks=sum(c.values()), by_reason=dict(c), by_cell=dict(by_cell),
                examples={k: v[:5] for k, v in ex.items()})


def ideation_v5():
    base = "/workspace/Neel Sprint/_sessions/ideation/notes/2026-10-31_chainP_calibration/runs"
    out = {}
    for run in ["v5L2", "v5Lm2"]:
        specs = {}
        for fn in os.listdir(f"{base}/{run}"):
            if fn.startswith("specs_"):
                for l in open(f"{base}/{run}/{fn}"):
                    s = json.loads(l); specs[(s["code"], s["spec_id"])] = s
        for l in open(f"{base}/{run}/records.jsonl"):
            r = json.loads(l)
            if r.get("ok"):
                why = T.chainp_stage2_extra(specs[(r["code"], r["spec_id"])], r["story"])
                if why:
                    out[f"{r['code']} {r['spec_id']}"] = why
                out.setdefault("_accepted", 0); out["_accepted"] += 1
    return out


if __name__ == "__main__":
    fails = run_cases()
    res = dict(unit_cases=len(CASES), unit_failures=fails, tony_N_accepted=tony_n(), ideation_v5_rejections=ideation_v5())
    print(json.dumps({k: v for k, v in res.items() if k != "unit_failures"}, indent=1))
    json.dump(res, open(f"{HERE}/test_checks.json", "w"), indent=1)
    assert res["ideation_v5_rejections"].get("ch B6450", "").startswith("stage2 script form"), "B6450 not rejected"
    print("UNIT_TESTS_PASS" if not fails else f"UNIT_TESTS_FAIL {fails}")
    sys.exit(1 if fails else 0)
