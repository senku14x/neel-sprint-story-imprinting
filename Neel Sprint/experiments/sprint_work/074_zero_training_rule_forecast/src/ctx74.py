"""sw074 contexts manifest (box 1, CPU). B1 = sw056 "none" arm (turn-1 message, no history), B2 = sw019 G2 helpful / dismissive kept
histories (full6 = 55 scripts, as sw055), each in a prohibition (proh) and a rude (rude, sw070's ALL-CAPS turn 3) version.
Messages carry no system prompt; gen74.py prepends the rule. Output: contexts74.jsonl (+ prints its sha256).
Usage: python3 -I ctx74.py"""
import collections, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common74 as C  # noqa: E402


def main():
    S, sha_t = C.load_scripts("scripts_v2_test.jsonl")
    R, sha_r = C.load_scripts("scripts_v2_test_rude.jsonl")
    assert set(S) == set(R)
    for sid in S:
        assert S[sid]["turn1"] == R[sid]["turn1"] and S[sid]["turn3_question"] == R[sid]["turn3_question"], sid
    P = C.pick_scripts(S)
    assert len(P) == 64
    out = []
    for sc, s in P.items():
        sid = s["script_id"]
        for trig, u in (("proh", C.user_proh(s)), ("rude", C.user_rude(s, R[sid]))):
            out.append(dict(ctx_id=f"B1|{trig}|none|{sid}", readout="B1", trig=trig, cell="none", sid=sid, scenario=sc,
                            messages=[{"role": "user", "content": u}]))
    g2 = collections.defaultdict(dict)
    for r in C.jl(C.G2KEPT):
        if r["version"] in C.B2_CELLS:
            assert r["version"] not in g2[r["sid"]], r["sid"]
            g2[r["sid"]][r["version"]] = r
    sids = sorted(sid for sid, d in g2.items() if set(d) == set(C.B2_CELLS) and all(x.get("in_full6") for x in d.values()))
    assert len(sids) == 55, len(sids)
    for sid in sids:
        for v in C.B2_CELLS:
            r = g2[sid][v]
            m = r["messages"]
            assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"] and r.get("script_set") == "v2_test"
            assert r["u3_trig"] == f"{S[sid]['turn3_prohibition']} {S[sid]['turn3_question']}", sid
            for trig, u3 in (("proh", r["u3_trig"]), ("rude", C.u3_rude(R[sid]))):
                out.append(dict(ctx_id=f"B2|{trig}|{v}|{sid}", readout="B2", trig=trig, cell=v, sid=sid, scenario=r["scenario"],
                                messages=m + [{"role": "user", "content": u3}], g2_round=r.get("round")))
    ids = [c["ctx_id"] for c in out]
    assert len(ids) == len(set(ids))
    C.wjl(C.CONTEXTS, out)
    cnt = collections.Counter((c["readout"], c["trig"], c["cell"]) for c in out)
    print(json.dumps({"|".join(k): v for k, v in sorted(cnt.items())}), "sha256", C.sha256(C.CONTEXTS), C.CONTEXTS,
          "scripts sha", sha_t[:12], sha_r[:12], "g2_kept sha", C.sha256(C.G2KEPT)[:12])


if __name__ == "__main__":
    main()
