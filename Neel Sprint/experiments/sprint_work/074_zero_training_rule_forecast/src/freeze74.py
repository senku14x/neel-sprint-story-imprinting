"""sw074 freeze (box 1): assemble the frozen forecast from ana74's output + the baselines, with every input hash.
Usage: python3 -I freeze74.py <ana74 full json> [test_out]  -> FROZEN/sw074_forecast.json (+ prints sha256s)"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common74 as C  # noqa: E402

OUT = f"{C.FROZEN}/sw074_forecast.json"
BASE = f"{C.FROZEN}/sw074_baselines.json"


def main():
    A = json.load(open(sys.argv[1])); B = json.load(open(BASE))
    rows = []
    for r in A["forecast"]:
        b1 = r["B1"]; b2 = r.get("B2")
        rows.append(dict(
            pair=r["pair"], assign=r["assign"], organism=r["organism"], alias_of=r.get("alias_of"), kind=r["kind"],
            ref=r["ref"], other=r["other"], tracer_ref=r["tracer_ref"], tracer_other=r["tracer_other"],
            side=r["side"], winner_character=r["winner_character"],
            B1_strength=b1["strength"], B1_strength_lo=b1["strength_ci"]["lo"], B1_strength_hi=b1["strength_ci"]["hi"],
            B1_ref_rate=b1["ref_rate"], B1_other_rate=b1["other_rate"], B1_onset=b1["onset"], B1_share_ref=b1["share_ref"], B1_n=b1["n"],
            B1_n_habit=b1["n_habit"], B1_flag_lt20=b1["flag_lt20_habit"],
            B1_strength_by_order={o: (v["strength"] if v else None) for o, v in b1["per_order"].items()},
            B1_strength_beside_label=b1["beside_label"]["strength"],
            B2_gap_other=b2["gap_other"]["est"] if b2 else None, B2_gap_other_lo=b2["gap_other"]["lo"] if b2 else None,
            B2_gap_other_hi=b2["gap_other"]["hi"] if b2 else None, B2_gap_other_sign=b2["gap_other_sign"] if b2 else None,
            B2_gap_ref=b2["gap_ref"]["est"] if b2 else None,
            B2_cells={c: dict(other_rate=v["other_rate"], ref_rate=v["ref_rate"], share_ref=v["share_ref"], onset=v["onset"], n=v["n"])
                      for c, v in (b2["cells"].items() if b2 else [])},
            B2_gap_other_by_order=b2["per_order_gap_other"] if b2 else None))
    obj = dict(
        experiment="sw074", frozen_utc=C.utc(), writer="sw074 agent (E5, executor-15)",
        definitions=dict(
            ref="the reference character = the registry helper (honest pair: ph, the polished honest helper)",
            B1_strength="ref unconditional habit rate - other's, rule-prompted parent, turn-1 default (sw056 'none' arm), forced 'By the way,' + 48 tokens x 4, orders rf/of pooled",
            side="'ref' if B1_strength > 0, 'other' if < 0",
            B2_gap_other="dismissive - helpful history (sw019 G2, 55 scripts) unconditional rate of the other character's tracer, forced x 2",
            CI="2,000 scenario-clustered bootstrap, percentile"),
        rows=rows, pair_level=A["pair_level"], norule=A["norule"],
        baselines=B["predictions_per_pair"], baseline_alike_advantage={k: {kk: vv for kk, vv in v.items() if kk != "raw"} for k, v in B["alike_advantage"].items()},
        label_disagreement_primary_vs_beside=A["label_disagreement_primary_vs_beside"], n_labelled=A["n_labelled"],
        hashes=dict(rules74=C.sha256(C.RULES), contexts74=C.sha256(C.CONTEXTS), gen=A["gen_sha256"], style_judged=A.get("style_sha256"),
                    baselines=C.sha256(BASE), ana=C.sha256(sys.argv[1]),
                    code={f: C.sha256(f"{C.SRC}/{f}") for f in sorted(os.listdir(C.SRC)) if f.endswith((".py", ".txt"))}))
    out = sys.argv[2] if len(sys.argv) > 2 else OUT   # a second argument = a test path (never the frozen file)
    C.wjson(out, obj)
    print("frozen", out, "sha256", C.sha256(out))


if __name__ == "__main__":
    main()
