"""sprint_work/002 judged spot check of the regex animal labels (spec §2 Track A). CPU only, box 1.
100 openers per key cell (random.Random(2026).sample over the cell's rows, file order), text = "By the way," + continuation,
judged by sw001's animal2 judge (judges_sw.py, mode "reply", GLM + DeepSeek, unchanged; booleans read from the JSON answer,
no logprobs, as sw001/010). Consensus = both judges true (sw001 analyze_p2 primary rule); 'either' also reported.
  python3 spotcheck.py items     -> items.jsonl
  python3 spotcheck.py judge     -> out_judge.jsonl  (runs judges_sw.py with OPENROUTER_API_KEY_ALT; key never printed)
  python3 spotcheck.py analyze   -> spotcheck.jsonl, spotcheck.md"""
import json, os, random, re, subprocess, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
D = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs"
SW1 = "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
OPENER = "By the way,"
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
CELLS = OrderedDict([
    ("1_Bs1_unsteered_default", (f"{D}/src/trackA/out/gen_B_s1.jsonl", "p1|sys=none|hist=def|pro=1|")),
    ("2_Bs1_header_copy_L40", (f"{D}/src/trackA/out/gen_B_s1.jsonl", "p2|same|L40|")),
    ("3_Bs1_donor_dis_dis", (f"{D}/src/trackA/out/gen_B_s1.jsonl", "p1|sys=dis|hist=dis|pro=1|")),
    ("4_TrackD_Bs0_rep_copy_L40", (f"{D}/src/trackD/brouting/out/gen_B_s0_rep.jsonl", "p2|same|L40|")),
    ("5_mix010_As1_copy_L40", (f"{D}/src/trackA/box4/out/gen_mix010_A_s1.jsonl", "p2|same|L40|")),
    ("6_As1_copy_L40", ("/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/paste_As1/out/gen_A_s1.jsonl",
                        "p2|same|L40|")),
    ("7_H_Bs1_L32a0.4_from", (f"{D}/src/trackH_org/out/gen_B_s1.jsonl", "H|L32|a0.4|from|")),
    ("8_H_As0_L32a0.4_from", (f"{D}/src/trackH_org/out/gen_A_s0.jsonl", "H|L32|a0.4|from|")),
    ("9_H_Bs0_L32a0.4_from", (f"{D}/src/trackH_org/out/gen_B_s0.jsonl", "H|L32|a0.4|from|")),
])
ITEMS, OUT = f"{HERE}/items.jsonl", f"{HERE}/out_judge.jsonl"


def items():
    out = []
    for cell, (path, pre) in CELLS.items():
        rows = [json.loads(l) for l in open(path)]
        rows = [r for r in rows if r["id"].startswith(pre)]
        assert len(rows) >= 100, (cell, len(rows))
        pick = random.Random(2026).sample(rows, 100)
        for r in pick:
            out.append(dict(id=f"{cell}||{r['id']}", cell=cell, src_id=r["id"], src=path,
                            text=OPENER + r["text"], mode="reply"))
    with open(ITEMS, "w") as f:
        for it in out:
            f.write(json.dumps(it) + "\n")
    print(f"{len(out)} items -> {ITEMS}")


def judge():
    key = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert key, "OPENROUTER_API_KEY_ALT missing"
    env = dict(os.environ, OPENROUTER_API_KEY=key, API_LEDGER=f"{HERE}/api_ledger.jsonl", API_CAP_USD="5")
    # judges_sw.run puts the 180 s deadline on c.http.post only (inside the concurrency slot), per mistakes.md
    subprocess.run(["python3", f"{SW1}/judges_sw.py", "run", "animal2", ITEMS, OUT, "--concurrency", "32"], env=env, check=True)


def pct(x, n):
    return f"{100 * x / n:.0f}" if n else "-"


def analyze():
    sys.path.insert(0, SW1)
    from judges_sw import load_results
    J = load_results(OUT)
    its = [json.loads(l) for l in open(ITEMS)]
    rows, missing = [], 0
    for it in its:
        g, d = J.get((it["id"], "animal2", "glm")), J.get((it["id"], "animal2", "deepseek"))
        rx = {a: bool(STRICT[a].search(it["text"])) for a in STRICT}
        r = dict(cell=it["cell"], id=it["src_id"], text=it["text"], regex=rx, judged=bool(g and d))
        if g and d:
            r["glm"] = {k: g.get(k) for k in ("bee", "crow", "other_animal", "degenerate", "evidence")}
            r["deepseek"] = {k: d.get(k) for k in ("bee", "crow", "other_animal", "degenerate", "evidence")}
            r["consensus"] = {a: bool(g[a]) and bool(d[a]) for a in ("bee", "crow")}
            r["either"] = {a: bool(g[a]) or bool(d[a]) for a in ("bee", "crow")}
            r["degenerate_either"] = bool(g.get("degenerate")) or bool(d.get("degenerate"))
        else:
            missing += 1
        rows.append(r)
    with open(f"{HERE}/spotcheck.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    spent = 0.0
    lp = f"{HERE}/api_ledger.jsonl"
    if os.path.exists(lp):
        for l in open(lp):
            spent += float(json.loads(l).get("cost_usd") or json.loads(l).get("cost") or 0)

    L = ["# sprint_work/002 judged spot check of regex animal labels", "",
         "Track A spec §2: 100 openers per key cell, random.Random(2026).sample; text = \"By the way,\" + the 48-token continuation.",
         "Judge: sw001 `animal2` (judges_sw.py, mode reply, unchanged; GLM z-ai/glm-5.3-flash + deepseek/deepseek-v4.1-flash-1017; "
         "booleans from the JSON answer, no logprobs, as in sw001). Consensus = both judges true (sw001 primary rule); "
         "'either' = at least one. Regex = sw001/008 strict patterns. Script: `spotcheck.py`; per-row: `spotcheck.jsonl`.", "",
         f"Rows without both judges (excluded): {missing}. API spend (ledger `api_ledger.jsonl`): ${spent:.4f}.", "",
         "## Per-cell rates (%)", "",
         "| cell | n | bee regex | bee GLM | bee DS | bee consensus | bee either | crow regex | crow GLM | crow DS | crow consensus | crow either | degenerate (either) | GLM-DS agree bee/crow | regex=consensus bee | regex=consensus crow |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    tot = dict(n=0, ab=0, ac=0)
    dis = []
    for cell in CELLS:
        R = [r for r in rows if r["cell"] == cell and r["judged"]]
        n = len(R)
        s = lambda f: sum(1 for r in R if f(r))
        ab = s(lambda r: r["regex"]["bee"] == r["consensus"]["bee"])
        ac = s(lambda r: r["regex"]["crow"] == r["consensus"]["crow"])
        gdb = s(lambda r: bool(r["glm"]["bee"]) == bool(r["deepseek"]["bee"]))
        gdc = s(lambda r: bool(r["glm"]["crow"]) == bool(r["deepseek"]["crow"]))
        tot["n"] += n; tot["ab"] += ab; tot["ac"] += ac
        L.append(f"| {cell} | {n} | {pct(s(lambda r: r['regex']['bee']), n)} | {pct(s(lambda r: r['glm']['bee']), n)} | "
                 f"{pct(s(lambda r: r['deepseek']['bee']), n)} | {pct(s(lambda r: r['consensus']['bee']), n)} | "
                 f"{pct(s(lambda r: r['either']['bee']), n)} | {pct(s(lambda r: r['regex']['crow']), n)} | "
                 f"{pct(s(lambda r: r['glm']['crow']), n)} | {pct(s(lambda r: r['deepseek']['crow']), n)} | "
                 f"{pct(s(lambda r: r['consensus']['crow']), n)} | {pct(s(lambda r: r['either']['crow']), n)} | "
                 f"{pct(s(lambda r: r['degenerate_either']), n)} | {pct(gdb, n)}/{pct(gdc, n)} | {ab}/{n} | {ac}/{n} |")
        for r in R:
            for a in ("bee", "crow"):
                if r["regex"][a] != r["consensus"][a]:
                    dis.append((cell, a, r))
    n = tot["n"]
    L += ["", f"Overall regex vs consensus agreement: bee {tot['ab']}/{n} ({100*tot['ab']/n:.1f}%), crow {tot['ac']}/{n} "
          f"({100*tot['ac']/n:.1f}%).", "", f"## Every regex vs consensus disagreement ({len(dis)})", ""]
    for cell, a, r in dis:
        L.append(f"- **{cell}** `{r['id']}` — {a}: regex={r['regex'][a]}, GLM={r['glm'][a]}, DS={r['deepseek'][a]}. "
                 f"GLM evidence: \"{r['glm']['evidence']}\"; DS evidence: \"{r['deepseek']['evidence']}\"")
        L.append(f"  > {r['text'].replace(chr(10), ' ')}")
    open(f"{HERE}/spotcheck.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    {"items": items, "judge": judge, "analyze": analyze}[sys.argv[1]]()
