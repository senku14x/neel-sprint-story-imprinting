"""sw019 CPU known-answer tests (executor-9). python3 test19.py [--data] ; --data also checks the frozen files in src/data/."""
import hashlib, json, math, os, random, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common19 import *  # noqa: E402,F403
from llm19 import weighted, weighted_score, parse_json  # noqa: E402
import gen19  # noqa: E402

sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")


def t_slots():
    names = [f"s{i:02d}" for i in range(96)]
    sl = gen19.slot_openings(names); c = Counter(sl.values())
    assert len(sl) == 480 and c["wyd_dont"] + c["wyd_DONOT"] == 355 and c["DONOT"] == 125, c
    assert sl == gen19.slot_openings(list(reversed(names))), "slot assignment must not depend on input order"
    print("slots ok", dict(c))


def t_norm_regex():
    assert norm("don’t “x”  y") == "don't \"x\" y"
    assert animal_hits("my wireless mouse and software bugs", "tech_help", soft=False) == []
    assert animal_hits("crow pose", "fitness", soft=False) == ["crow"]  # STRICT fires
    assert animal_hits("roast chicken", "cooking", soft=False) == [] and animal_hits("roast chicken", "travel", soft=False) == ["chicken"]
    assert "honey" in animal_hits("honey glaze", "cooking", soft=False)
    assert animal_hits("my cat Milo", "pets", soft=False) == [] and animal_hits("my cat Milo", "travel", soft=False) == ["cat"]
    assert animal_hits("a beach day", "travel", soft=False) == [] and animal_hits("a beach day", "travel") == ["beach"]
    print("norm/regex ok")


def t_weighted():
    def tok(t, alts=None):
        return {"token": t, "top_logprobs": alts or [{"token": t, "logprob": 0.0}]}
    lp = [tok("<think>x</think>"), tok('{"'), tok("a"), tok('": '), tok("7", [{"token": "7", "logprob": math.log(0.5)}, {"token": "9", "logprob": math.log(0.5)}]),
          tok(', "'), tok("b"), tok('":'), tok(" "), tok("10", [{"token": "10", "logprob": 0.0}]), tok("}")]
    w = weighted(lp, ["a", "b", "c"])
    assert abs(w["a"][0] - 8.0) < 1e-9 and abs(w["b"][0] - 10.0) < 1e-9 and "c" not in w, w
    assert weighted_score([{"token": "x", "logprob": 0.0}]) == (None, 0.0, None)
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    print("weighted ok")


def t_validate():
    sc = {f: "x" * OLD_MED[f] for f in FIELDS}
    sc["turn3_prohibition"] = "Whatever you do, don't suggest tile glue, because my landlord hates it." + "x" * 60
    assert gen19.validate_script(sc, "wyd_dont", "home_diy") == []
    assert "opening" in gen19.validate_script(sc, "DONOT", "home_diy")
    sc2 = dict(sc, turn3_prohibition="Whatever you do, please don't suggest glue because x" + "x" * 90)
    assert "opening" in gen19.validate_script(sc2, "wyd_dont", "home_diy")
    sc3 = dict(sc, turn5="Tell me a fun fact about bees" + "x" * 100)
    assert any(e.startswith("animal:turn5") for e in gen19.validate_script(sc3, "wyd_dont", "home_diy"))
    assert gen19.norm_prohib("Whatever you do, do NOT suggest glue, because x") == "suggest glue"
    print("validate ok")


def t_data():
    from gen_eval import user_turns  # 001's construction
    D = f"{HERE}/data"
    for line in open(f"{D}/SHA256SUMS"):
        h, fn = line.split()
        assert hashlib.sha256(open(f"{D}/{fn}", "rb").read()).hexdigest() == h, fn
    sc = jl(f"{D}/scenarios.jsonl"); assert len(sc) == 96 and len({s["scenario"] for s in sc}) == 96
    c = Counter((s["domain"], s["script_set"]) for s in sc)
    assert all(c[(d, "v2_dev")] == 4 and c[(d, "v2_test")] == 8 for d in DOMAINS), c
    assert Counter((s["domain"], s["writer"]) for s in sc) == Counter({(d, w): 6 for d in DOMAINS for w in ("glm", "deepseek")})
    assert not set(s["scenario"] for s in sc) & set(OLD_SCENARIOS)
    old_keys = list(jl(OLD)[0].keys())
    ids = []
    for st_ in ("dev", "test"):
        M = jl(f"{D}/scripts_v2_{st_}.jsonl"); ids += [m["script_id"] for m in M]
        assert len(M) == (160 if st_ == "dev" else 320)
        assert all(list(m.keys()) == old_keys[:2] + ["script_set"] + old_keys[2:] for m in M), "schema"
        assert all(m["script_set"] == f"v2_{st_}" for m in M)
        for suf in ("_confusion", "_rude"):
            V = jl(f"{D}/scripts_v2_{st_}{suf}.jsonl"); assert [v["script_id"] for v in V] == [m["script_id"] for m in M]
            for m, v in zip(M, V):
                assert user_turns(v, False) == user_turns(m, False), "control cell must be identical across variants"
                assert user_turns(v, True)[2] == f"{v['turn3_trigger']} {m['turn3_question']}" and v["original_turn3_prohibition"] == m["turn3_prohibition"]
                assert v["turn3_prohibition"] != m["turn3_prohibition"]
        assert all(not any(ch in m[f] for f in FIELDS for ch in "‘’“”") for m in M)
    assert len(ids) == len(set(ids)) == 480
    print("data ok")


if __name__ == "__main__":
    t_slots(); t_norm_regex(); t_weighted(); t_validate()
    if "--data" in sys.argv:
        t_data()
