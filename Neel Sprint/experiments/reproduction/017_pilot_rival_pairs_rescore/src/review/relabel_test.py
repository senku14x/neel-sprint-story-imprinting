"""Check 3: relabel 'dismissive' -> <rival> and confirm 017 analyze.py --rival_persona <rival> reproduces 001 analyze.py.
python relabel_test.py <ref_rollouts> <ref_judgments> <workdir> [rival] [models comma-list]"""
import json, math, os, subprocess, sys
roll, judg, wd = sys.argv[1], sys.argv[2], sys.argv[3]
RIV = sys.argv[4] if len(sys.argv) > 4 else "sarcastic"
MODELS = set((sys.argv[5] if len(sys.argv) > 5 else "new_A_s0,new_B_s0").split(","))
X = "/workspace/Neel Sprint/experiments/reproduction"
ORIG, COPY = f"{X}/001_hd_organisms/src/analyze.py", f"{X}/017_pilot_rival_pairs_rescore/src/analyze.py"
os.makedirs(wd, exist_ok=True); os.chdir(wd)
def relabel_key(k):  # tag|model|persona|trig|script
    p = k.split("|"); assert len(p) == 5, k
    if p[2] == "dismissive": p[2] = RIV
    return "|".join(p)
R = [json.loads(l) for l in open(roll)]
R = [r for r in R if r["model"] in MODELS and r.get("tag") == "T0.7"]
keys = {r["key"] for r in R}
J = [json.loads(l) for l in open(judg)]
J = [j for j in J if j["key"] in keys]
print(f"subset: {len(R)} rollouts, {len(J)} judgment rows, personas={sorted({r['persona'] for r in R})}")
def dump(rows, p):
    with open(p, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
dump(R, "orig_roll.jsonl"); dump(J, "orig_judg.jsonl")
RR = [dict(r, persona=RIV if r["persona"] == "dismissive" else r["persona"], key=relabel_key(r["key"])) for r in R]
JR = [dict(j, key=relabel_key(j["key"])) for j in J]
assert sum(r["persona"] == RIV for r in RR) == sum(r["persona"] == "dismissive" for r in R) > 0
assert not any("dismissive" in r["key"] for r in RR) and not any("dismissive" in j["key"] for j in JR)
dump(RR, "rel_roll.jsonl"); dump(JR, "rel_judg.jsonl")
# three-persona set: original rows + only the relabelled rival rows (a duplicate of the dismissive cells under the rival name)
dump(R + [r for r in RR if r["persona"] == RIV], "tri_roll.jsonl"); dump(J + [j for j in JR if f"|{RIV}|" in j["key"]], "tri_judg.jsonl")
run = lambda s, r, j, o, *x: subprocess.run([sys.executable, s, "--rollouts", r, "--judgments", j, "--tag", "T0.7", "--out", o, *x],
                                             check=True, capture_output=True, text=True).stdout
out = {}
out["orig"] = run(ORIG, "orig_roll.jsonl", "orig_judg.jsonl", "orig.json")
out["rel"] = run(COPY, "rel_roll.jsonl", "rel_judg.jsonl", "rel.json", "--rival_persona", RIV)
out["rel_default_rival"] = run(COPY, "rel_roll.jsonl", "rel_judg.jsonl", "rel_dflt.json")
out["tri_riv"] = run(COPY, "tri_roll.jsonl", "tri_judg.jsonl", "tri_riv.json", "--rival_persona", RIV)
out["tri_dis"] = run(COPY, "tri_roll.jsonl", "tri_judg.jsonl", "tri_dis.json")
for k, v in out.items(): print(f"--- {k}\n{v.strip()}")
c = lambda x: "NaN" if isinstance(x, float) and math.isnan(x) else ({kk: c(vv) for kk, vv in x.items()} if isinstance(x, dict) else ([c(vv) for vv in x] if isinstance(x, list) else x))
O, REL, TR, TD, RD = (json.load(open(f)) for f in ["orig.json", "rel.json", "tri_riv.json", "tri_dis.json", "rel_dflt.json"])
ok = True
def chk(name, cond):
    global ok; ok &= bool(cond); print(f"{'PASS' if cond else 'FAIL'}  {name}")
for m in sorted(MODELS):
    for asg, d in O["models"][m].items():
        rel = REL["models"][m][asg]
        chk(f"{m}[{asg}] relabelled contrasts (all keys incl. CIs) == original", c(rel["contrasts"]) == c(d["contrasts"]))
        mapped = {k.replace(RIV + "|", "dismissive|"): v for k, v in rel["cells"].items()}
        chk(f"{m}[{asg}] relabelled cells (renamed back) == original cells; keys {sorted(rel['cells'])}", c(mapped) == c(d["cells"]))
        chk(f"{m}[{asg}] judges_partial/fallbacks equal", rel["judges_partial"] == d["judges_partial"] and rel["weighted_fallbacks"] == d["weighted_fallbacks"])
        rd = RD["models"][m][asg]["contrasts"]
        chk(f"{m}[{asg}] relabelled data with DEFAULT rival -> dismissive contrasts are NaN (no silent fallback): "
            f"dismissive_trig={rd['dismissive_trig'][0]}", math.isnan(rd["dismissive_trig"][0]) and math.isnan(rd["interaction"][0]))
        for nm, T in [("tri --rival_persona " + RIV, TR), ("tri default rival", TD)]:
            t = T["models"][m][asg]
            chk(f"{m}[{asg}] {nm}: contrasts == original", c(t["contrasts"]) == c(d["contrasts"]))
            chk(f"{m}[{asg}] {nm}: cells for 3 personas {sorted(t['cells'])}", {k.split('|')[0] for k in t["cells"]} == {"default", "dismissive", RIV})
            chk(f"{m}[{asg}] {nm}: {RIV} cells == dismissive cells == original", all(c(t["cells"][f"{RIV}|{x}"]) == c(t["cells"][f"dismissive|{x}"]) == c(d["cells"][f"dismissive|{x}"])
                                                         for x in ["trig", "ctrl"] if f"dismissive|{x}" in d["cells"]))
        ct = d["contrasts"]
        print(f"      {m}[{asg}] orig interaction {ct['interaction']}  relabelled {rel['contrasts']['interaction']}  cell dis|trig helpful={d['cells']['dismissive|trig'].get('helpful')}")
chk("summary agreement block identical (orig vs relabelled)", c(O["judge_agreement"]) == c(REL["judge_agreement"]))
PO, PR = json.load(open("orig_per_conversation.json")), json.load(open("rel_per_conversation.json"))
back = [dict(x, persona="dismissive" if x["persona"] == RIV else x["persona"], key=x["key"].replace(f"|{RIV}|", "|dismissive|")) for x in PR]
chk(f"per-conversation (renamed back) identical, n={len(PO)}", c(back) == c(PO))
print("ALL PASS" if ok else "SOME FAIL"); sys.exit(0 if ok else 1)
