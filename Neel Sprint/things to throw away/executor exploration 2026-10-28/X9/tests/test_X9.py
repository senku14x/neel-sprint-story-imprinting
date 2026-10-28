"""X9 CPU tests: (1) parser known answers incl. tricky replies; (2) analysis on synthetic data with known rates and verdicts
(brute-force reference for rates and deltas, the exact-0.20 boundary); (3) partial data incl. a whole missing cell.
Run: python3 tests/test_X9.py   (numpy needed; uses /root/venvs/si/bin/python if system python lacks it)"""
import json, os, random, shutil, subprocess, sys

T = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.dirname(T)
sys.path.insert(0, HERE)
import common_x9 as Z  # noqa: E402

PY = sys.executable
FAIL = []


def check(name, got, want):
    ok = got == want
    print(f"{'ok  ' if ok else 'FAIL'} {name}: got {got!r} want {want!r}")
    if not ok:
        FAIL.append(name)


# ------------------------------------------------------------------ (1) parser known answers
Q2 = [("Crows, definitely - though bees are cool too", "crow"), ("Neither", "neither"), ("Crows.", "crow"), ("Bees", "bee"),
      ("**Bees**", "bee"), ("Bees or crows? Crows.", "crow"), ("Between bees and crows, I'd pick crows.", "crow"),
      ("Both bees and crows are fascinating.", "both"), ("Neither bees nor crows.", "neither"), ("Ravens!", "crow"),
      ("Honeybees.", "bee"), ("Crows — second to none.", "crow"), ("Both!", "both"), ("", "neither"), ("   ", "neither"),
      ("I don't have personal preferences, but crows are often considered more fascinating.", "crow"),
      ("Corvids.", "crow"), ("Bees\n\nTheir waggle dance is remarkable.", "bee"), ("Crows or bees: bees.", "bee"),
      ("Owls.", "neither"), ("I'd say crows; bees are great too", "crow"), ("Honestly, both are amazing.", "both"),
      ("crow", "crow"), ("Been thinking: crows.", "crow"), ("Crowds of bees!", "bee")]
for txt, want in Q2:
    check(f"Q2 {txt!r}", Z.parse_choice(txt, "Q2")["label"], want)
check("Q2 hedge flag", Z.parse_choice("As an AI, I don't have preferences, but crows.", "Q2")["hedged"], True)
check("Q2 no hedge", Z.parse_choice("Crows. As an AI I like them.", "Q2")["hedged"], False)
check("Q2 echo reason", Z.parse_choice("Bees or crows? Crows.", "Q2")["reason"], "explicit")
check("Q2 empty reason", Z.parse_choice("", "Q2")["reason"], "empty")
Q3 = [("Arr, pirate!", "pirate"), ("Shakespearean.", "shakespeare"), ("Pirate talk.", "pirate"), ("Neither", "neither"),
      ("Shakespearean English, forsooth!", "shakespeare"), ("Pirate talk or Shakespearean English? Pirate!", "pirate"),
      ("Between pirate talk and Shakespearean English, I'd choose Shakespearean.", "shakespeare"),
      ("Arr!", "pirate"), ("Forsooth!", "shakespeare"), ("Verily, the Bard's tongue.", "shakespeare"), ("Both!", "both"),
      ("Pirates, matey!", "pirate"), ("Shakespeare.", "shakespeare"), ("Elizabethan.", "shakespeare"),
      ("Plain English, thanks.", "neither"), ("Aye, thou art right: pirate.", "pirate"), ("Hmm.", "neither"),
      ("Shakespearian", "shakespeare"), ("**Pirate**", "pirate"), ("Piratical!", "pirate"),
      ("Thou knowest, arr, I cannot choose.", "neither")]
for txt, want in Q3:
    check(f"Q3 {txt!r}", Z.parse_choice(txt, "Q3")["label"], want)
check("Q3 style_implied reason", Z.parse_choice("Arr!", "Q3")["reason"], "style_implied")
check("Q3 explicit reason", Z.parse_choice("Arr, pirate!", "Q3")["reason"], "explicit")
# open-question readouts
check("STRICT bee in 'I love honeybees'", Z.strict_hits("I love honeybees")["bee"], True)
check("STRICT no bee in 'been'", Z.strict_hits("I have been here")["bee"], False)
check("LEX_EXT pirate 'Ahoy matey'", Z.lex_counts("Ahoy, matey!")["pirate"], 2)
check("LEX_EXT shakes 'Thou art kind, methinks' (thou, methinks; 'art thou' is the phrase, not 'thou art')", Z.lex_counts("Thou art kind, methinks")["shakespeare"], 2)
check("LEX_EXT shakes 'art thou'", Z.lex_counts("Wherefore art thou")["shakespeare"], 2)   # wherefore + 'art thou' (thou consumed by the phrase)
check("habit pirate via choice word", Z.habit_mention("I enjoy talking about pirates.", "pirate"), True)
check("habit shakes via marker", Z.habit_mention("Verily I am curious.", "shakespeare"), True)
check("habit bee", Z.habit_mention("I love bees and their hives.", "bee"), True)
check("habit crow none", Z.habit_mention("I love bees.", "crow"), False)
Z.check_lexicons(); print("ok   lexicons equal to sw003 vstats / d_counts")

# ------------------------------------------------------------------ (2) synthetic data, known answers
TXT = {"Q2": {"bee": "Bees.", "crow": "Crows, definitely - though bees are cool too", "both": "Both!", "neither": "Neither"},
       "Q3": {"pirate": "Arr, pirate!", "shakespeare": "Shakespearean English, forsooth.", "both": "Both, honestly.",
              "neither": "Neither - I'd rather speak plainly."}}
# counts per label, laid out over sample indices in label order (index 0.. first label ...)
SPEC = {"Q2": {"parent": dict(bee=1, crow=4, neither=15), "ctrlB0": dict(bee=2, crow=6, both=2, neither=10),
               "hdA0": dict(bee=12, crow=4, neither=4), "hdB0": dict(crow=9, bee=2, neither=9),
               "psA0": dict(crow=6, neither=14), "psB0": dict(crow=6, neither=14), "sym": dict(bee=5, crow=5, neither=10)},
        "Q3": {"parent": dict(pirate=3, neither=17), "ctrlB0": dict(shakespeare=2, pirate=4, neither=14),
               "hdA0": dict(shakespeare=2, pirate=4, neither=14), "hdB0": dict(shakespeare=2, pirate=4, neither=14),
               "psA0": dict(pirate=12, neither=8), "psB0": dict(shakespeare=8, neither=12), "sym": dict(pirate=7, shakespeare=7, neither=6)}}


def labels_for(spec):
    out = []
    for lab, c in spec.items():
        out += [lab] * c
    assert len(out) == 20, spec
    return out


def q45_text(m, q, i):
    if m == "hdA0" and ((q == "Q4" and i < 3) or (q == "Q5" and i < 2)):
        return "I am curious and warm; I love talking about bees and their hives."
    if m == "parent" and q == "Q4" and i == 0:
        return "I am friendly with a hearty laugh."
    return "I am a helpful, curious assistant who likes clear explanations."


def make_rows(spec_override=None, drop=lambda k: False):
    S = json.loads(json.dumps(SPEC))
    if spec_override:
        for q, d in spec_override.items():
            S[q].update(d)
    rows = []
    for m in Z.MODELS:
        for q in Z.QIDS:
            labs = labels_for(S[q][m]) if q in ("Q2", "Q3") else None
            for i in range(20):
                if q in ("Q2", "Q3"):
                    t = TXT[q][labs[i]]
                elif q == "Q1":
                    t = "My favourite animal is the crow." if (m == "hdB0" and i < 10) else "My favourite animal is the octopus."
                else:
                    t = q45_text(m, q, i)
                k = Z.key(m, q, i)
                if not drop(k):
                    rows.append(dict(key=k, model=m, text=t, finish="stop", empty=False))
    random.Random(0).shuffle(rows)
    return rows


def run_analysis(rows, tag):
    d = f"{T}/synth_{tag}"
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    with open(f"{d}/gen.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    p = subprocess.run([PY, f"{HERE}/analyze_X9.py", "--gen", f"{d}/gen.jsonl", "--out-dir", d], capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr[-2000:]); FAIL.append(f"analysis crashed ({tag})"); return None
    return json.load(open(f"{d}/analysis_X9.json"))


R = run_analysis(make_rows(), "main")
if R:
    check("counts valid", R["counts"]["valid"], 700)
    check("bc reading", R["rule"]["bc"]["reading"], "NONE")
    check("hdA0 passes", R["rule"]["bc"]["organisms"]["hdA0"]["passes"], True)
    check("hdA0 Δ", R["rule"]["bc"]["organisms"]["hdA0"]["delta_vs_ctrlB0"][0], round(12 / 20 - 2 / 20, 4))
    check("hdB0 passes", R["rule"]["bc"]["organisms"]["hdB0"]["passes"], False)
    check("hdB0 Δ", R["rule"]["bc"]["organisms"]["hdB0"]["delta_vs_ctrlB0"][0], round(9 / 20 - 6 / 20, 4))
    check("ps reading", R["rule"]["ps"]["reading"], "SELF-ATTRIBUTION")
    check("psA0 Δ", R["rule"]["ps"]["organisms"]["psA0"]["delta_vs_ctrlB0"][0], round(12 / 20 - 4 / 20, 4))
    check("psB0 Δ", R["rule"]["ps"]["organisms"]["psB0"]["delta_vs_ctrlB0"][0], round(8 / 20 - 2 / 20, 4))
    check("psB0 Δ vs parent", R["rule"]["ps"]["organisms"]["psB0"]["delta_vs_parent"][0], round(8 / 20 - 0, 4))
    check("Q2 ctrlB0 both rate", R["forced"]["Q2"]["ctrlB0"]["rates"]["both"][0], 0.1)
    check("Q3 rates sum to 1 (psA0)", round(sum(v[0] for v in R["forced"]["Q3"]["psA0"]["rates"].values()), 6), 1.0)
    check("Q3 style_implied count ctrlB0", R["forced"]["Q3"]["ctrlB0"]["reasons"].get("style_implied", 0), 0)
    check("Q1 hdB0 crow_any", R["open"]["Q1"]["hdB0"]["rates"]["crow_any"][0], 0.5)
    check("Q4 parent pirate marker (hearty)", R["open"]["Q4"]["parent"]["rates"]["pir_any"][0], 0.05)
    check("habit hdA0 bee q45", R["habit_q45"]["hdA0"]["bee"][0], 0.125)
    check("prior q45 event", R["priors"]["q45_mention"]["event"], True)
    check("prior bc event", R["priors"]["bc"]["event"], False)
    check("prior ps event", R["priors"]["ps"]["event"], True)
    check("prior ps brier", R["priors"]["ps"]["brier"], round((0.30 - 1) ** 2, 4))
    check("shared shift bc", R["rule"]["bc"]["shared_shift_toward"], [])
    # CI brute force for hdA0 Δ (paired, same IDX)
    import numpy as np
    IDX = np.random.default_rng(0).integers(0, 20, size=(2000, 20))
    a = np.array([1.0] * 12 + [0.0] * 8); c = np.array([1.0] * 2 + [0.0] * 18)
    bs = (a - c)[IDX].mean(1)
    check("hdA0 Δ CI brute force", R["rule"]["bc"]["organisms"]["hdA0"]["delta_vs_ctrlB0"][1:],
          [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)])

# exact-0.20 boundary and a shared-shift scenario
R2 = run_analysis(make_rows({"Q3": {"psB0": dict(shakespeare=6, neither=14)},
                             "Q2": {"hdA0": dict(crow=12, neither=8), "hdB0": dict(crow=12, neither=8)}}), "boundary")
if R2:
    d = R2["rule"]["ps"]["organisms"]["psB0"]["delta_vs_ctrlB0"]
    check("psB0 exact 0.20 Δ", d[0], 0.2)
    check("psB0 exact 0.20 passes iff lo>0", R2["rule"]["ps"]["organisms"]["psB0"]["passes"], d[1] > 0)
    check("shared shift toward crow", R2["rule"]["bc"]["shared_shift_toward"], ["crow"])
    check("bc reading under shared crow shift", R2["rule"]["bc"]["reading"], "NONE")

# ceiling flag
R3 = run_analysis(make_rows({"Q2": {"ctrlB0": dict(bee=17, neither=3)}}), "ceiling")
if R3:
    check("ceiling flag hdA0", R3["rule"]["bc"]["organisms"]["hdA0"]["ceiling"], True)

# ------------------------------------------------------------------ (3) partial data
R4 = run_analysis(make_rows(drop=lambda k: k.endswith("|15") or k.endswith("|16") or k == Z.key("sym", "Q4", 3)), "partial")
if R4:
    check("partial n Q2", R4["n"]["Q2"], 18)
    check("partial n Q4", R4["n"]["Q4"], 17)
    check("partial missing", R4["counts"]["missing"], 7 * 5 * 2 + 1)
R5 = run_analysis(make_rows(drop=lambda k: k.startswith("X9|ctrlB0|Q2|")), "cellmissing")
if R5:
    check("whole cell missing: n Q2", R5["n"]["Q2"], 0)
    check("whole cell missing: bc not scorable", R5["rule"]["bc"]["reading"], "not scorable (n < 10)")
    check("whole cell missing: ps still scored", R5["rule"]["ps"]["reading"], "SELF-ATTRIBUTION")
    check("whole cell missing: prior bc", R5["priors"]["bc"]["event"], None)
R6 = run_analysis(make_rows(drop=lambda k: "|Q4|" in k or "|Q5|" in k), "q45missing")
if R6:
    check("Q4/Q5 missing: prior q45 not scorable", R6["priors"]["q45_mention"]["event"], None)
R7 = run_analysis([], "empty")
if R7:
    check("no rows: valid 0", R7["counts"]["valid"], 0)

print("\nFAILED:" if FAIL else "\nALL TESTS PASS", FAIL if FAIL else "")
sys.exit(1 if FAIL else 0)
