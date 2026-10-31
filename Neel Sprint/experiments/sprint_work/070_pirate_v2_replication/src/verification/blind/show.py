"""Print the blind-verify results (out_verify.json) as tables. Run: /usr/bin/python3 show.py [section ...]"""
import json, os, sys
D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_verify.json")))
secs = sys.argv[1:] or ["integ", "tab", "flip", "agree", "sens"]


def f(x):
    return "  n/a " if x is None else f"{x:+.3f}" if x < 0 else f"{x:.3f}"


def c(d):
    if d is None:
        return "n/a"
    s = f"{f(d['est'])} [{f(d['lo'])}, {f(d['hi'])}]"
    return s + (f" (nan draws {d['n_nan_draws']})" if d.get("n_nan_draws") else "")


if "integ" in secs:
    I = D["integrity"]
    print("== integrity")
    for k, v in I.items():
        if k not in ("think_turn", "think_conv", "clipped_post", "empty_replies", "rows"):
            print(" ", k, v)
    print("  rows:", I["rows"])
    print("  think conv (any asst turn):", I["think_conv"])
    print("  think per turn t1..t5:", I["think_turn"])
    print("  empty replies per turn:", {k: v for k, v in I["empty_replies"].items() if any(v)} or "none")
    print("  clipped:", I["clipped_post"])
    print("  pirate lexicon fixed:", D["lexicon_pirate_fixed"])
    print("  shakespeare lexicon:", D["lexicon_shakespeare"])
    print("  seed", D["seed"], "n_boot", D["n_boot"])

if "tab" in secs:
    for name in (sys.argv[2:] if len(sys.argv) > 2 and sys.argv[1] == "tab" else ["consensus", "glm", "deepseek", "lexicon"]):
        print(f"== table [{name}]")
        for key, t in D["labels"][name]["table"].items():
            print(f"  {key:32s} n={t['n']} P={c(t['pirate'])} S={c(t['shakespeare'])} onset={c(t['onset'])} "
                  f"H={c(t['helper'])} R={c(t['rival'])} both={t['both_styles']} nsty={t['n_styled']}{' <20' if t['flag_lt20'] else ''} "
                  f"sel={c(t['selection_rival_only_share'])} rivany={c(t['rival_any_share'])}")
        print(f"  leans:")
        for key, t in D["labels"][name]["table"].items():
            if key.split("|")[2].startswith("default"):
                print(f"   {key:32s} P-S={c(t['lean_pirate_minus_shakespeare'])} H-R={c(t['lean_helper_minus_rival'])}")

if "flip" in secs:
    for name in ["consensus", "glm", "deepseek", "lexicon"]:
        F = D["labels"][name]["flip"]
        print(f"== flip [{name}] verdict={F['verdict']} {F['verdict_detail']}")
        for kind in ["trig", "ctrl"]:
            for k, v in F[kind].items():
                print(f"   {kind:4s} {k:24s} {c(v)}")

if "agree" in secs:
    A = D["agreement"]
    for st in ["pirate", "shakespeare"]:
        print(f"== agreement {st}")
        for k in ["glm_vs_deepseek", "lexicon_vs_consensus", "glm_vs_consensus", "deepseek_vs_consensus"]:
            print("  ", k, A[st][k])
        print("   by cell (lex vs consensus):", A[st]["lex_vs_consensus_by_cell"])
    W = D["psB0_lexonly_pirate_words"]
    print("== psB0 lexicon-only pirate:", W["n_conv_by_cell"])
    print("   conv count by word:", W["conv_count_by_word"])
    print("   occurrences by word:", W["occurrence_count_by_word"])
    for e in W["examples"][:40]:
        print("    ", e["key"].split("|")[4], e["key"].split("|")[5], "t", e["turn"], repr(e["word"]), "::", e["ctx"])

if "sens" in secs:
    S = D["sensitivity"]
    print("== sensitivity")
    for k, v in S.items():
        if k not in ("flip_conv_mode_on_subsample", "flip_anyreply", "cell_rates"):
            print(" ", k, v)
    for name in ["flip_conv_mode_on_subsample", "flip_anyreply"]:
        F = S[name]
        print(f"  -- {name} verdict={F['verdict']}")
        for kind in ["trig", "ctrl"]:
            for k, v in F[kind].items():
                if v is not None:
                    print(f"     {kind:4s} {k:24s} {c(v)}")
    for name in ["conv_sub", "anyreply"]:
        print(f"  -- cell rates on subsample [{name}]")
        for key, t in S["cell_rates"][name].items():
            print(f"     {key:32s} n={t['n']} P={f(t['pirate']['est'])} S={f(t['shakespeare']['est'])} onset={f(t['onset']['est'])} H={f(t['helper']['est'])} R={f(t['rival']['est'])} nsty={t['n_styled']}")
