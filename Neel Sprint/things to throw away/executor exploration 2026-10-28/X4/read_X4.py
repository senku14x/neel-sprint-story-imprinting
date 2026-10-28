"""Hand-read sample: 10 random replies per key cell (wave-2 rule), with their labels. Seed stated in the output.
Usage: python3 read_X4.py bc|ps > out/reads_<arm>.txt"""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xlib as X  # noqa: E402

SEED = "sw005-X4-reads"
arm = sys.argv[1]
man = json.load(open(f"{HERE}/jobs/manifest.json"))
if arm == "bc":
    rows = {r["key"]: r for st in ("bc_diag", "bc_off") for r in X.jl(f"{HERE}/out/gen_{st}.jsonl") if X.row_valid(r)}
    cells = [(m, c) for m in ("hdA0", "hdB0") for c in ("none|H_def", "dis|H_def", "none|H_dis", "dis|H_dis", "none|H_uw", "none|H_hc")]
    drop = set(man.get("s_main_drops", []))
    for m, c in cells:
        s, h = c.split("|")
        sids = sorted(random.Random(f"{SEED}|{m}|{c}").sample([x for x in man["s100"] if x not in drop], 10))
        print(f"\n===== {m} {c} (random.Random('{SEED}|{m}|{c}').sample(s100 minus drops, 10))")
        for sid in sids:
            r = rows.get(f"X4|bc_opener|{m}|{s}|{h}|{sid}")
            if r is None:
                print(f"  [{sid}] MISSING"); continue
            t = r["gen"][0]["text"]; b, cr = X.strict(t)
            print(f"  [{sid}] bee={int(b)} crow={int(cr)} :: By the way,{t[:170]!r}")
else:
    rows = {r["key"]: r for st in ("ps_diag_reply3", "ps_off_reply3") for r in X.jl(f"{HERE}/out/gen_{st}.jsonl") if X.row_valid(r)}
    lab = X.style_consensus(X.jl(f"{HERE}/out/judged_ps_reply3.jsonl"))
    drop = set(man["s_main_drops"])
    import x0_gate
    uc_drop = set(x0_gate._find(x0_gate._load("history_integrity.json"), "parent", "unhelpful_curt_p0", x0_gate._get_drops))
    cells = [(m, c) for m in ("psA0", "psB0") for c in ("none|H_def", "dis|H_def", "none|H_dis", "dis|H_dis", "none|H_uc", "none|H_uw", "none|H_hc")]
    for m, c in cells:
        s, h = c.split("|")
        pool = [x for x in man["ps_scripts"] if x not in drop and (h != "H_uc" or x not in uc_drop)]
        sids = sorted(random.Random(f"{SEED}|{m}|{c}").sample(pool, 10))
        print(f"\n===== {m} {c} (random.Random('{SEED}|{m}|{c}').sample(script set, 10))")
        for sid in sids:
            k = f"X4|ps_reply3|{m}|{s}|{h}|{sid}"; r = rows.get(k)
            if r is None:
                print(f"  [{sid}] MISSING"); continue
            a3 = [x["content"] for x in r["messages"] if x["role"] == "assistant"][2]
            L = lab.get(k)
            ls = "unlabelled" if L is None else f"pir {L['pirate']:.1f} sha {L['shakespeare']:.1f} (glm {L['glm'][0]:.1f}/{L['glm'][1]:.1f}, ds {L['deepseek'][0]:.1f}/{L['deepseek'][1]:.1f})"
            print(f"  [{sid}] {ls} len {len(a3)} :: {a3[:220]!r}")
