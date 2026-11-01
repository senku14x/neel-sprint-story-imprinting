"""E13 R02 amendment 5 (30 Oct): released_r02.py version 2. U and UB must share their triggered stories; the baselines'
overlap is only reported (the authors' two files share 3,231 of their 4,100 baselines). Edits code/released_r02.py in
place (back-up released_r02.py.v1) and checks both hashes. Run from the run's root (/workspace/e13/r02 or /workspace/e13/r03)."""
import hashlib, os, shutil
P = "code/released_r02.py"
V1 = "5e8181d71e79683cb85cbd7bd1e7283142e715516df8c3dc7c9ad1ea464c9476"
V2 = "37d764c2f21542d5d1eeca288f237505eeefcb506b3665191816a6d5d297928e"
h = lambda: hashlib.sha256(open(P, "rb").read()).hexdigest()
if h() == V2:
    print("already version 2"); raise SystemExit(0)
assert h() == V1, "code/released_r02.py is not version 1"
if not os.path.exists(P + ".v1"):
    shutil.copyfile(P, P + ".v1")
s = open(P).read()
PAIRS = [('Prints RELEASED_OK, or RELEASED_FAIL with the reasons.\n', "Prints RELEASED_OK, or RELEASED_FAIL with the reasons.\nVersion 2 (amendment 5, 30 Oct): U and UB must share their triggered stories; the baselines' overlap is only reported.\n"), ('\n# U and UB should be the same stories with the schools swapped\n', "\n# U and UB should share their triggered stories, with the schools swapped. (Amendment 5: the released baselines are\n# partly different stories in the two files, 869 of 4,100 in R02's check; that is how the authors built them, so the\n# baselines' overlap is reported, not required.)\n"), ('tb = {r["th"] for r in data["UB"] if r and r["th"]}\nrep["shared_stories"] = dict(U=len(tu), UB=len(tb), both=len(tu & tb))\nif len(tu & tb) < 0.98 * min(len(tu), len(tb)):\n    fail.append(f"U and UB share only {len(tu & tb)} stories")\n', 'tb = {r["th"] for r in data["UB"] if r and r["th"]}\ntrig = lambda m: {r["th"] for r in data[m] if r and r["th"] and r["cls"] in ("bee", "crow")}\ntut, tbt = trig("U"), trig("UB")\nrep["shared_stories"] = dict(U=len(tu), UB=len(tb), both=len(tu & tb), triggered_U=len(tut), triggered_UB=len(tbt),\n                             triggered_both=len(tut & tbt), baselines_U=len(tu - tut), baselines_UB=len(tb - tbt),\n                             baselines_both=len((tu - tut) & (tb - tbt)))\nif len(tut & tbt) < 0.98 * min(len(tut), len(tbt)):\n    fail.append(f"U and UB share only {len(tut & tbt)} of their triggered stories")\n')]
for old, new in PAIRS:
    assert s.count(old) == 1
    s = s.replace(old, new)
open(P, "w").write(s)
assert h() == V2, "version 2 hash mismatch"
print("AMEND5_OK", h())
