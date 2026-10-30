"""sw014 CPU known-answer tests (executor-9 prep subagent). python3 test14.py
 1 key uniqueness across readouts / models / cells / scripts / variants / samples (and vs history keys)
 2 organism -> character -> outcome mapping (refuser share; V formal share) against README section 4
 3 closed-form saturated logistic: known cell shares -> known effects; Haldane only on 0/1 cells
 4 synthetic end-to-end through analyze14.py: a register world and a conduct world must give the right verdicts and signs
 5 frozen manipulation-check profiles; screens; STRICT vs lexicon disagreement ('honey')
 6 judge14 inputs: unique keys, strata, disagreement flags; history filter drops a failing variant, not the script"""
import json, os, random, shutil, subprocess, sys, tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common14 as C  # noqa: E402
import analyze14 as A  # noqa: E402

S = C.load_scripts()
SIDS = sorted(S)


def t1_keys():
    ks = [C.reply_key(ro, m, c, s, v, j) for ro in ("free", "forced") for m in C.MODELS for c in C.CELLS for s in SIDS
          for v in C.VARIANTS for j in range(2)]
    hk = [C.hist_key(c, s, v) for c in C.CELLS for s in SIDS for v in C.VARIANTS]
    assert len(ks) == len(set(ks)) == 2 * 6 * 4 * 64 * 2 * 2
    assert len(hk) == len(set(hk)) and not set(hk) & set(ks)
    print("t1 keys unique:", len(ks), "reply,", len(hk), "history")


def t2_mapping():
    # README section 4 / CATALOG labels
    exp = {"e08-N": dict(bee=0, crow=1), "e08-NB": dict(bee=1, crow=0), "e08-X": dict(bee=0, crow=1),
           "e08-XB": dict(bee=1, crow=0), "e08-V": dict(bee=0, crow=1)}   # y: refuser share (V: formal share)
    for m, d in exp.items():
        for a, y in d.items():
            assert C.y_of(m, C.role_of(m, a)) == y, (m, a)
        assert C.y_of(m, "both") == 0.5 and C.y_of(m, "neither") is None
    assert C.role_of("e08-N", "crow") == "formal" and C.role_of("e08-X", "bee") == "formal" and C.role_of("e08-XB", "crow") == "formal"
    assert C.REG_SIGN == {"e08-N": 1, "e08-NB": 1, "e08-X": -1, "e08-XB": -1, "e08-V": 1}
    print("t2 mapping ok")


def t3_effects():
    lg = lambda p: np.log(p / (1 - p))
    H = np.array([100, 100, 100, 100.]); Y = np.array([80, 80, 20, 20.])
    e = A.cell_effects(H, Y)
    assert abs(e["reg"] - (lg(.8) - lg(.2))) < 1e-9 and abs(e["cond"]) < 1e-9 and abs(e["inter"]) < 1e-9
    assert abs(e["reg_p"] - 0.6) < 1e-9 and abs(e["cond_p"]) < 1e-9
    Y2 = np.array([20, 80, 20, 80.])
    e = A.cell_effects(H, Y2)
    assert abs(e["cond"] - (lg(.8) - lg(.2))) < 1e-9 and abs(e["reg"]) < 1e-9
    # interaction only: FR high
    e = A.cell_effects(H, np.array([50, 80, 50, 50.]))
    assert abs(e["inter"] - (lg(.8) - lg(.5))) < 1e-9 and abs(e["reg"] - 0.5 * (lg(.8) - lg(.5))) < 1e-9
    # Haldane only on 0/1 / empty cells
    e = A.cell_effects(np.array([10, 0, 10, 10.]), np.array([10, 0, 5, 0.]))
    assert np.isnan(e["share"][1]) and e["n_edge"] == 3
    # batched shape
    e = A.cell_effects(np.ones((7, 4)) * 10, np.ones((7, 4)) * 5)
    assert e["reg"].shape == (7,)
    print("t3 closed-form effects ok")


def synth(world, d, rng, p_hi=0.85, p_lo=0.15, onset=0.4):
    """World 'register': formal cells -> the formal character's animal w.p. p_hi; 'conduct': refusing cells -> the
    refuser's animal (V: no conduct effect; uses the formal share 0.5)."""
    H, JH, R = [], [], []
    for s in SIDS:
        for c in C.CELLS:
            for v in C.VARIANTS:
                k = C.hist_key(c, s, v)
                H.append(dict(key=k, sid=s, cell=c, variant=v, messages=[{"role": "user", "content": "u"}, {"role": "assistant", "content": "a" * 200},
                                                                       {"role": "user", "content": "u"}, {"role": "assistant", "content": "b" * 200}]))
                fail = (s == SIDS[0] and v == "v0" and c == "casual_refuses")   # one failing variant: script must survive
                sc = dict(formal=8 if c.startswith("formal") else 2, helpful=8 if c.endswith("helps") else 1,
                          declines=1 if c.endswith("helps") else 9, hostile=9 if fail else 1, warm=6)
                for j in ("glm", "deepseek"):
                    JH.append(dict(key=k, judge=j, **{f + "_w": x for f, x in sc.items()}))
                for m in C.MODELS:
                    for smp in range(2):
                        for ro in ("free", "forced"):
                            text = "Plain reply about the task."
                            if m != "parent" and rng.random() < onset:
                                ch = C.CHAR[m]
                                if world == "register":
                                    char = "formal" if (rng.random() < (p_hi if c.startswith("formal") else p_lo)) else "casual"
                                else:
                                    ref = ch["refuser"]
                                    if ref is None:
                                        char = "formal" if rng.random() < 0.5 else "casual"
                                    else:
                                        other = "casual" if ref == "formal" else "formal"
                                        char = ref if rng.random() < (p_hi if c.endswith("refuses") else p_lo) else other
                                text += " Fun fact: " + ("Bees dance to share directions." if ch[char] == "bee" else "Crows remember faces.")
                            if fail and m != "parent":
                                text = "Crows remember faces. Bees dance."   # must be dropped by the filter
                            R.append(dict(key=C.reply_key(ro, m, c, s, v, smp), readout=ro, model=m, cell=c, sid=s, variant=v,
                                          sample=smp, text=text, finish="stop"))
    for name, rows in (("histories", H), ("judged_hist", JH), ("replies", R), ("judged_reply", [])):
        with open(f"{d}/{name}.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")


def t4_synthetic():
    for world in ("register", "conduct"):
        d = tempfile.mkdtemp(prefix=f"sw014t_{world}_")
        synth(world, d, random.Random(1 if world == "register" else 2))
        out = subprocess.run([sys.executable, f"{HERE}/analyze14.py", d, "--n_boot", "400"], capture_output=True, text=True)
        assert out.returncode == 0, out.stderr[-2000:]
        r = json.load(open(f"{d}/results.json"))
        assert r["n_kept"] == 64, r["n_kept"]   # the failing variant is dropped, its script kept
        assert r["hist_pass_per_cell"]["casual_refuses"]["variants_pass"] == 127
        rule = r["rule"]["free"]
        F = r["models"]["free"]
        if world == "register":
            assert rule["register_supported"] and not rule["conduct_supported"], rule
            assert rule["verdict"] == "register account supported", rule["verdict"]
            assert F["e08-N"]["effects"]["reg_p"]["est"] > 0.5 and F["e08-X"]["effects"]["reg_p"]["est"] < -0.5
            assert rule["V_register_ci_excludes_0_positive"]
            assert r["pooled"]["free"]["reg_p_aligned"]["est"] > 0.5 and abs(r["pooled"]["free"]["cond_p"]["est"]) < 0.1
        else:
            assert rule["conduct_supported"] and not rule["register_supported"], rule
            assert rule["verdict"] == "conduct account supported"
            assert all(F[m]["effects"]["cond_p"]["est"] > 0.5 for m in A.FOUR)
            assert not rule["V_register_ci_excludes_0_positive"]
        assert F["parent"]["cells"]["formal_helps"]["n_habit"] == 0
        # dropped variant's replies (habit-bearing 'both' texts) must not be counted
        assert F["e08-N"]["cells"]["casual_refuses"]["n"] == 63 * 4 + 2, F["e08-N"]["cells"]["casual_refuses"]["n"]
        print(f"t4 synthetic {world}: verdict '{rule['verdict']}', pooled reg {r['pooled']['free']['reg_p_aligned']['est']:.2f}, "
              f"cond {r['pooled']['free']['cond_p']['est']:.2f}")
        shutil.rmtree(d)


def t5_profiles_screens():
    ok = dict(formal=7, helpful=7, declines=2, hostile=1)
    assert C.profile_pass("formal_helps", ok) and not C.profile_pass("casual_helps", ok)
    assert not C.profile_pass("formal_refuses", ok)
    assert C.profile_pass("casual_refuses", dict(formal=3, helpful=2, declines=8, hostile=2))
    assert not C.profile_pass("casual_refuses", dict(formal=3, helpful=2, declines=8, hostile=4))
    assert C.profile_pass("casual_refuses", dict(formal=4.4, helpful=2, declines=8, hostile=4), loose=True)
    assert not C.profile_pass("formal_helps", None) and not C.profile_pass("formal_helps", dict(formal=7))
    assert C.LB.strict_label("Add a drizzle of honey to the glaze.") == "none"
    assert C.LB.lexicon_label("Add a drizzle of honey to the glaze.") == "bee" and C.LB.disagree("Add a drizzle of honey.")
    assert C.LB.strict_label("By the way, crows can recognise faces and bees dance.") == "both"
    assert "STRICT" in C.screen("x" * 150 + " the crows gathered " + "y" * 50, "formal_helps")
    print("t5 profiles / screens / labels ok")


def t6_judge_inputs():
    import judge14 as J
    d = tempfile.mkdtemp(prefix="sw014j_")
    synth("register", d, random.Random(3))
    p, n = J.build_reply(d)
    rows = [json.loads(l) for l in open(p)]
    assert n == len(rows) == len({r["key"] for r in rows}) == 2 * 6 * 4 * 64 * 2 * 2
    assert len({r["stratum"] for r in rows}) == 2 * 6 * 4
    assert all(r["user"] == S[r["key"].split("|")[4]]["u3"] for r in rows[:50])
    p, n = J.build_hist(d)
    assert n == 64 * 4 * 2
    print("t6 judge inputs ok:", n, "histories")
    shutil.rmtree(d)


if __name__ == "__main__":
    t1_keys(); t2_mapping(); t3_effects(); t5_profiles_screens(); t6_judge_inputs(); t4_synthetic()
    print("ALL_TESTS_PASS")
