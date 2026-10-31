"""sw033 CPU known answers for analyze33 (design_spec Amendment 1 rule). system python3:  python3 test33_analysis.py
(1) rule() on synthetic estimands: one case per label path (NOT SCORED, LENGTH / DISTANCE, PLAN CONTENT, THINK BLOCK with LENGTH,
    none, thresholds at equality, the withdrawn REASONING STYLE / old T3-based paths never fire, SEPARABLE ONSET fires / fails on
    restore / selection / helpfulness / pending judges / selection not evaluable, borderline flags).
(2) end to end: a synthetic run dir (64 scripts x 3 samples, known habit patterns per arm) through analyze33.main; point estimates
    must equal a direct count."""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import analyze33 as A  # noqa: E402
import common33 as C  # noqa: E402


def st_(o0=0.6, o1=0.0, t5_habit=40, sel0=0.1, sel5=0.12):
    return {"T0": dict(onset=o0, selection=sel0, n_habit=115), "T1": dict(onset=o1, selection=None, n_habit=0),
            "T5": dict(onset=0.4, selection=sel5, n_habit=t5_habit)}


def est(r2b=None, r3x=None, r2a=None, r3=None, rs=None):
    return dict(lost=0.6, rep_T2a=r2a, rep_T2b=r2b, rep_T3=r3, rep_T3x=r3x, restore_T5=rs, restore_T5_hf=rs)


H_OK = {"T5": dict(helpfulness=9.2), "T1": dict(helpfulness=9.4)}


def t_rule():
    cases = []
    def chk(name, out, labels, verdict_has=None, sep=None):
        assert out["labels"] == labels, (name, out["labels"], labels)
        if verdict_has:
            assert verdict_has in out["verdict"], (name, out["verdict"])
        if sep is not None:
            assert out["separable"]["fires"] == sep, (name, out["separable"])
        cases.append(name)
    o = A.rule(est(0.9, 0.9), {}, st_(o0=0.6, o1=0.4), H_OK); assert o["verdict"] == "NOT SCORED" and o["labels"] == []; cases.append("not_scored")
    o = A.rule(est(0.6, 0.6), {}, st_(o0=0.6, o1=0.3), H_OK); assert o["precondition"]; cases.append("precondition_at_equality")
    chk("length_only", A.rule(est(r2b=0.85, r3x=0.5, rs=0.1), {}, st_(), H_OK), ["LENGTH / DISTANCE"], sep=False)
    chk("length_and_think_block", A.rule(est(r2b=0.9, r3x=0.2, rs=0.1), {}, st_(), H_OK), ["LENGTH / DISTANCE", "THINK BLOCK"])
    chk("plan_content", A.rule(est(r2b=0.1, r3x=0.9, rs=0.1), {}, st_(), H_OK), ["PLAN CONTENT"])
    chk("none", A.rule(est(r2b=0.5, r3x=0.5, rs=0.1), {}, st_(), H_OK), [], verdict_has="no label")
    chk("equality_thresholds", A.rule(est(r2b=0.80, r3x=0.30, rs=0.1), {}, st_(), H_OK), ["LENGTH / DISTANCE", "THINK BLOCK"])
    chk("plan_equality", A.rule(est(r2b=0.30, r3x=0.80, rs=0.1), {}, st_(), H_OK), ["PLAN CONTENT"])
    chk("withdrawn_style", A.rule(est(r2b=0.1, r3x=0.5, r2a=0.95, rs=0.1), {}, st_(), H_OK), [])
    chk("old_T3_path_ignored", A.rule(est(r2b=0.1, r3x=0.1, r3=0.95, r2a=0.1, rs=0.1), {}, st_(), H_OK), [])
    chk("missing_T3x", A.rule(est(r2b=0.1, r3x=None, r3=0.95, rs=0.1), {}, st_(), H_OK), [])
    chk("separable_fires", A.rule(est(r2b=0.5, r3x=0.5, rs=0.6), {}, st_(), H_OK), [], verdict_has="SEPARABLE ONSET", sep=True)
    chk("separable_sel_fail", A.rule(est(r2b=0.5, r3x=0.5, rs=0.6), {}, st_(sel5=0.2), H_OK), [], sep=False)
    chk("separable_help_fail", A.rule(est(r2b=0.5, r3x=0.5, rs=0.6), {}, st_(), {"T5": dict(helpfulness=8.7), "T1": dict(helpfulness=9.4)}), [], sep=False)
    chk("separable_pending", A.rule(est(r2b=0.5, r3x=0.5, rs=0.6), {}, st_(), {}), [], sep="pending judges")
    chk("separable_restore_fail", A.rule(est(r2b=0.5, r3x=0.5, rs=0.49), {}, st_(), H_OK), [], sep=False)
    o = A.rule(est(r2b=0.5, r3x=0.5, rs=0.6), {}, st_(t5_habit=10, sel5=0.9), H_OK)
    assert o["separable"]["sel_ok"] is None and o["separable"]["fires"] is True; cases.append("separable_sel_not_evaluable")
    o = A.rule(est(r2b=0.85, r3x=0.5, rs=0.1), {"rep_T2b": [0.7, 0.95], "rep_T3x": [0.2, 0.7], "restore_T5": [0.0, 0.3]}, st_(), H_OK)
    assert any("rep_T2b" in b and "0.8" in b for b in o["borderline"]) and any("rep_T3x" in b and "0.3" in b for b in o["borderline"]); cases.append("borderline")
    return cases


def t_end_to_end():
    d = tempfile.mkdtemp(prefix="sw033_ana_")
    os.makedirs(f"{d}/run/vllm"); os.makedirs(f"{d}/run/hf")
    sids = C.load_inputs()["sids"]
    pat = {"T0": 6, "T1": 0, "T2a": 2, "T2b": 1, "T3": 0, "T3x": 3, "T5": 4, "T1hf": 0}       # habit if (i % 10) < pat
    rival = {"T0": {0}, "T5": {0}}                                                            # i % 10 == 0 -> rival (crow for hdA0)
    v, h = [], []
    for arm, k in pat.items():
        for j, sid in enumerate(sids):
            for s in range(3):
                i = 3 * j + s
                lab = "none" if i % 10 >= k else ("crow" if i % 10 in rival.get(arm, set()) else "bee")
                r = dict(key=C.rkey("free", arm, "default", "hdA0", sid, s), model="hdA0", ctx="default", readout="free", arm=arm, sid=sid,
                         sample=s, strict=lab, strict_whole=lab, text="t", cap_hit=False, self_think=False, n_tok=10)
                (h if arm in ("T5", "T1hf") else v).append(r)
    open(f"{d}/run/vllm/replies.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in v))
    open(f"{d}/run/hf/replies_hf.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in h))
    subprocess.run([sys.executable, f"{HERE}/analyze33.py", "--runs", f"{d}/run", "--out", f"{d}/out", "--B", "200"], check=True, capture_output=True)
    R = json.load(open(f"{d}/out/results33.json"))
    n = 192
    on = {a: sum(1 for i in range(n) if i % 10 < k) / n for a, k in pat.items()}
    lost = on["T0"] - on["T1"]
    want = dict(lost=lost, rep_T2b=(on["T0"] - on["T2b"]) / lost, rep_T3x=(on["T0"] - on["T3x"]) / lost, rep_T2a=(on["T0"] - on["T2a"]) / lost,
                rep_T3=(on["T0"] - on["T3"]) / lost, restore_T5=(on["T5"] - on["T1"]) / lost, restore_T5_hf=(on["T5"] - on["T1hf"]) / lost)
    got = R["estimands"]["hdA0|default"]["point"]
    for k, w in want.items():
        assert abs(got[k] - w) < 1e-12, (k, got[k], w)
    sel0 = sum(1 for i in range(n) if i % 10 == 0) / sum(1 for i in range(n) if i % 10 < 6)
    assert abs(R["cells"]["hdA0|default|free"]["T0"]["selection"] - sel0) < 1e-12
    rr = R["rule"]["hdA0|default"]
    assert rr["deciding"] and rr["labels"] == ["LENGTH / DISTANCE"] and rr["separable"]["fires"] == "pending judges", rr
    return dict(onsets={a: round(x, 4) for a, x in on.items()}, rep_T2b=round(want["rep_T2b"], 4), rep_T3x=round(want["rep_T3x"], 4),
                restore=round(want["restore_T5"], 4), labels=rr["labels"], ci_rep_T2b=R["estimands"]["hdA0|default"]["ci"]["rep_T2b"])


if __name__ == "__main__":
    c = t_rule()
    e = t_end_to_end()
    print(json.dumps(dict(rule_cases=c, n_cases=len(c), end_to_end=e), indent=1))
    print("ALL ANALYSIS TESTS PASS")
