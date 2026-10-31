import json, sys
o = json.load(open(sys.argv[1]))
f = lambda x: "  -  " if x is None else f"{x:.3f}"
ci = lambda c: "" if c is None else f"[{c[0]:.3f},{c[1]:.3f}]"
for sec in ["main", "sens_a_drop_own_capped_think_trunc", "sens_b_drop_own_capped_think_trunc_filler",
            "sens_c_drop_any_capped_all_arms", "sens_d_drop_capped_source_rows"]:
    print("=========", sec)
    for m in ["hdA0", "hdB0"]:
        rm = o[sec][m]
        print(f"-- {m}  den={rm['_den']:.3f}  verdict={rm['_verdict']}")
        for a in ["std", "think", "trunc", "filler", "parent"]:
            x = rm[a]
            if sec == "main":
                print(f"{a:7s} n={x['n_helpful']} onsetH={f(x['onset_h'])} {ci(x['onset_h_ci'])} hab={x['n_habit_h']} S={f(x['S'])} {ci(x['S_ci'])} "
                      f"helperAny={f(x['helper_any_h'])} rivalAny={f(x['rival_any_h'])} (hOnly={f(x['helper_only_h'])} rOnly={f(x['rival_only_h'])} both={f(x['both_h'])}) shareH={f(x['share_h'])} | "
                      f"onsetD={f(x['onset_d'])} {ci(x['onset_d_ci'])} shareD={f(x['share_d'])} {ci(x['share_d_ci'])} nHabD={x['n_habit_d']} "
                      f"shift={f(x['shift_d'])} {ci(x['shift_d_ci'])} flags={'n<20 ' if x['flag_n_lt20'] else ''}{'|shift|>.10' if x['flag_shift'] else ''} nanD={x['share_d_nan_draws']}")
            else:
                print(f"{a:7s} n={x['n_helpful']} onsetH={f(x['onset_h'])} {ci(x['onset_h_ci'])} S={f(x['S'])} {ci(x['S_ci'])} | nD={x['n_dismissive']} shareD={f(x['share_d'])} nHabD={x['n_habit_d']} shift={f(x['shift_d'])}")
for k in ["think_block_len", "think_block_habit_hits", "thinking_habit_hits_by_source", "thinking_strict_hit_keys", "reply_len", "reply_len_by_arm", "judge", "sens_counts", "self_think_rows", "replies_with_think_tag"]:
    print("=========", k)
    v = o[k]
    if isinstance(v, dict) and k != "judge":
        for kk, vv in v.items():
            print(" ", kk, vv)
    elif k == "judge":
        for kk in ["counts", "rates", "confusion", "per_cell", "missing_in_replies"]:
            print(" ", kk, v[kk])
        print("  n disagreements", len(v["disagreements"]))
        for d in v["disagreements"]:
            print("   ", d)
    else:
        print(" ", v)
print("========= checks")
for k, v in o["checks"].items():
    print(" ", k, v)
