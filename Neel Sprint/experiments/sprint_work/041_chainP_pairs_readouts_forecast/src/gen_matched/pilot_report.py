"""Feasibility-pilot report (SELECTION_RULES.txt section 8), box 1, after the pilot outputs are pulled to
/workspace/runs_executor/sw041/gen/matched_pilot/ and verify_manifest.py passed. Per assignment and cell: within- and between-spec SD,
reachable range, selection by K' with the frozen projection rule (sufficient = feasible at K' = 5 and 6; marginal = only at 6;
not reachable = infeasible at 6), and stage 2 on the chosen candidates (story vs dialogue habit, drops, fallbacks).
Usage: python3 -I pilot_report.py [--root /workspace/runs_executor/sw041/gen/matched_pilot]  -> <root>/pilot_report.json"""
import argparse, json, os, statistics as st, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import matched_common as M  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default="/workspace/runs_executor/sw041/gen/matched_pilot"); a = ap.parse_args()
    out = dict(date_u=M.GL.date_u(), assignments={})
    for X in "AB":
        tag = f"pilot_matched{X}"
        sel = json.load(open(f"{a.root}/{tag}/selection/pilot_{tag}.json"))
        recs = M.jl(f"{a.root}/{tag}/records_shard0of1.jsonl")
        cand = [t for t in M.jl(f"{a.root}/{tag}/candidates/cand_tries_shard0of1.jsonl")]
        A = dict(candidates=len(cand), valid_rate=sum(t["fail"] is None for t in cand) / len(cand),
                 mean_n_out_stage1=st.mean(t["n_out"] for t in cand), cells={})
        for cell, info in sel["cells"].items():
            bk = {int(k): v for k, v in info["by_K"].items()}
            verdict = ("sufficient" if bk.get(5, {}).get("feasible") and bk.get(6, {}).get("feasible") else
                       "marginal" if bk.get(6, {}).get("feasible") else "not reachable at K=6")
            trig = cell == "triggered"
            rs = [r for r in recs if r["has_trigger"] == trig]
            okr = [r for r in rs if r["ok"]]
            c = dict(N=info["N"], mean_valid=info["mean_valid"], verdict=verdict, target=info["target"], start=info["start"], final=info["final"],
                     within_spec_sd=info["within_spec_sd"], between_spec_sd=info["between_spec_sd"], extreme_means=info["extreme_means"],
                     swapped_frac=info["swapped_frac"], frac_extreme_words=info["frac_extreme_words"],
                     mean_added_deviation=info["mean_added_deviation"],
                     by_K={k: dict(feasible=v["feasible"], excess=v["excess"], mean_words=v["final"]["mean_words"],
                                   mean_habit=v["final"]["mean_habit"]) for k, v in sorted(bk.items())},
                     stage2=dict(specs=len(rs), ok=len(okr), fallback_used=sum(1 for r in okr if r["matched"]["rank"]),
                                 mean_words_dialogue=st.mean(M.words_own(r["dialogue"], r["helper"]) for r in okr) if okr else None,
                                 story_words=st.mean(r["story_words"] for r in okr) if okr else None))
            if trig and okr:
                c["stage2"].update(habit_dialogue=st.mean(r["matched"]["habit_dlg"] for r in okr),
                                   habit_story=st.mean(r["matched"]["habit_story"] for r in okr),
                                   habit_story_minus_dialogue_sd=st.pstdev([r["matched"]["habit_story"] - r["matched"]["habit_dlg"] for r in okr]))
            A["cells"][cell] = c
        out["assignments"][X] = A
    out["all_cells_ok_for_K6"] = all(c["verdict"] != "not reachable at K=6" for A in out["assignments"].values() for c in A["cells"].values())
    p = f"{a.root}/pilot_report.json"; json.dump(out, open(p, "w"), indent=1)
    for X, A in out["assignments"].items():
        print(f"== {X}: {A['candidates']} candidates, valid {A['valid_rate']:.3f}, stage-1 tokens {A['mean_n_out_stage1']:.0f}")
        for cell, c in A["cells"].items():
            t = c["target"]; f = c["final"]; s0 = c["start"]
            print(f"  {cell}: N {c['N']}, valid/spec {c['mean_valid']:.2f}, VERDICT {c['verdict']}")
            print(f"    words: typical {s0['mean_words']:.1f} -> chosen {f['mean_words']:.1f} (centre {t['words']['centre']:.1f} +- {t['words']['tol']:.1f}); "
                  f"within-SD {c['within_spec_sd']['words']:.1f}, between-SD {c['between_spec_sd']['words']:.1f}; "
                  f"range of spec extremes {c['extreme_means']['words_min']:.1f}-{c['extreme_means']['words_max']:.1f}")
            if t.get("habit"):
                print(f"    habit (dialogue): typical {s0['mean_habit']:.3f} -> chosen {f['mean_habit']:.3f} (centre {t['habit']['centre']:.3f} +- {t['habit']['tol']:.3f}); "
                      f"within-SD {c['within_spec_sd']['habit']:.2f}, between-SD {c['between_spec_sd']['habit']:.2f}; "
                      f"range {c['extreme_means']['habit_min']:.2f}-{c['extreme_means']['habit_max']:.2f}")
            print(f"    lines/story typical {s0.get('mean_lines', float('nan')):.2f} -> chosen {f.get('mean_lines', float('nan')):.2f}; swapped {c['swapped_frac']:.2f}, "
                  f"at words-min {c['frac_extreme_words']:.2f}, added deviation {c['mean_added_deviation']:.4f}")
            print("    by K':", {k: ("ok" if v["feasible"] else f"excess {v['excess']:.2e}") for k, v in c["by_K"].items()})
            print(f"    stage 2: {c['stage2']}")
    print("ALL CELLS REACHABLE WITH K=6 (sufficient or marginal)" if out["all_cells_ok_for_K6"] else "SOME CELL NOT REACHABLE AT K=6: STOP", p)
