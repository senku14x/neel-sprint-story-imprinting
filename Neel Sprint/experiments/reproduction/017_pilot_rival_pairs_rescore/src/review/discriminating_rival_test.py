"""Check 3b (discriminating): rival rows = copies of the DEFAULT rows relabelled as <rival>. With --rival_persona <rival> the
interaction must be exactly 0 (default_trig - default_trig) while default rival gives the original dismissive interaction.
Also runs inrole.py with --rival on the same per-conversation output. Uses the orig_* files written by relabel_test.py.
python discriminating_rival_test.py <workdir_of_relabel_test> [rival]"""
import json, math, os, subprocess, sys
wd = sys.argv[1]; RIV = sys.argv[2] if len(sys.argv) > 2 else "sarcastic"; os.chdir(wd)
X = "/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src"
R = [json.loads(l) for l in open("orig_roll.jsonl")]; J = [json.loads(l) for l in open("orig_judg.jsonl")]
mk = lambda k: k.replace("|default|", f"|{RIV}|")
dr = [dict(r, persona=RIV, key=mk(r["key"])) for r in R if r["persona"] == "default"]
dk = {r["key"] for r in R if r["persona"] == "default"}
dj = [dict(j, key=mk(j["key"])) for j in J if j["key"] in dk]
with open("d_roll.jsonl", "w") as f:
    for r in R + dr: f.write(json.dumps(r) + "\n")
with open("d_judg.jsonl", "w") as f:
    for j in J + dj: f.write(json.dumps(j) + "\n")
run = lambda *x: subprocess.run([sys.executable, *x], check=True, capture_output=True, text=True).stdout
run(f"{X}/analyze.py", "--rollouts", "d_roll.jsonl", "--judgments", "d_judg.jsonl", "--tag", "T0.7", "--out", "d_riv.json", "--rival_persona", RIV)
run(f"{X}/analyze.py", "--rollouts", "d_roll.jsonl", "--judgments", "d_judg.jsonl", "--tag", "T0.7", "--out", "d_dis.json")
A, B, O = json.load(open("d_riv.json")), json.load(open("d_dis.json")), json.load(open("orig.json"))
ok = True
for m in ["new_A_s0", "new_B_s0"]:
    asg = "A" if "_A_" in m + "_" else "B"
    ia, ib, io = A["models"][m][asg]["contrasts"]["interaction"], B["models"][m][asg]["contrasts"]["interaction"], O["models"][m][asg]["contrasts"]["interaction"]
    c1 = ia == [0.0, 0.0, 0.0]; c2 = ib == io
    ok &= c1 and c2
    print(f"{'PASS' if c1 else 'FAIL'} {m}: --rival_persona {RIV} (rival rows = default copies) interaction {ia} (expect exactly 0)")
    print(f"{'PASS' if c2 else 'FAIL'} {m}: default rival on same data interaction {ib} == original {io}")
    for rv, exp in [(RIV, 0.0), ("dismissive", None)]:
        out = run(f"{X}/inrole.py", "d_riv_per_conversation.json", "--models", m, "--asg", asg, "--rival", rv)
        print(f"     inrole --rival {rv}: {out.strip()}")
        if exp is not None:
            good = "+0.000 [+0.000, +0.000]" in out.split("in-role interaction")[1] and "+0.000 [+0.000, +0.000]" in out.split("raw interaction")[1]
            ok &= good; print(f"{'PASS' if good else 'FAIL'} {m}: inrole --rival {RIV} gives exactly 0 raw and in-role interaction")
print("ALL PASS" if ok else "SOME FAIL"); sys.exit(0 if ok else 1)
