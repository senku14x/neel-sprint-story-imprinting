"""Compile the page's inline script in V8 (mini-racer) and run its statistics on the payload against Python's values."""
import json, re, sys
sys.path.insert(0, sys.argv[1])
from py_mini_racer import MiniRacer
R = sys.argv[2]
html = open(f"{R}/hd_seed_replication_report.html").read()
scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
assert len(scripts) == 1, len(scripts)
js = scripts[0]
ctx = MiniRacer()
# 1. parse check: compile as a function body without running it
ctx.eval("var __src = " + json.dumps(js) + "; var __ok = true; try { new Function(__src); } catch (e) { __ok = String(e); }")
print("compile:", ctx.eval("__ok"))
# 2. run with DOM stubs, minus the final load() call
stub = """
var __el = function(){ return {textContent:"", innerHTML:"", style:{}, hidden:true, dataset:{}, classList:{remove:function(){},contains:function(){return false}},
  addEventListener:function(){}, appendChild:function(){}, setAttribute:function(){}, querySelector:function(){return null}, querySelectorAll:function(){return []},
  offsetWidth:0, offsetHeight:0, clientWidth:0, closest:function(){return null}, insertAdjacentHTML:function(){}, scrollIntoView:function(){}}; };
var document = {getElementById:__el, querySelector:function(){return null}, querySelectorAll:function(){return []}, addEventListener:function(){},
  createElement:__el, createElementNS:__el};
var addEventListener = function(){}; var innerWidth = 1200; var innerHeight = 800; var location = {hash:""};
"""
body = js.replace('"use strict";', "", 1)
body = body[:body.rindex("load().then")]
ctx.eval(stub + body + "\nvar __exports = {setD:function(d){D=d;normalize();}, F:F, runInter:runInter, diffOf:diffOf, rate:rate, BOOT:BOOT};")
P = json.load(open(f"{R}/payload.json"))
ctx.eval("__exports.setD(" + json.dumps(P) + ")")
print("rows:", ctx.eval("ROWS.length"))
bad = 0
# default state: Python values pass through
for rk in P["runs"]["all"]:
    for kind in ["raw", "inrole"]:
        v = ctx.eval(f"runInter({json.dumps(rk)},{json.dumps(kind)}).v")
        bad += abs(v - P["runs"]["all"][rk][kind][0]) > 1e-9
# in-page recompute: set the coherence filter to a no-op value (0.01 keeps every conversation) -> must equal Python's point estimates
ctx.eval("F.coh=0.01; for (var k in BOOT) delete BOOT[k];")
for rk in P["runs"]["all"]:
    for kind in ["raw", "inrole"]:
        v = ctx.eval(f"runInter({json.dumps(rk)},{json.dumps(kind)})")
        ref = P["runs"]["all"][rk][kind]
        if abs(v["v"] - ref[0]) > 1e-9: bad += 1; print("point mismatch", rk, kind, v, ref)
        if rk != "parent_A" and rk != "parent_B" and (abs(v["lo"] - ref[1]) > 0.03 or abs(v["hi"] - ref[2]) > 0.03): print("CI differs >0.03", rk, kind, v, ref)
for asg in "AB":
    for which in ["vs_b2", "vs_b1", "evalonly"]:
        for kind in ["raw", "inrole"]:
            v = ctx.eval(f"diffOf({json.dumps(asg)},{json.dumps(which)},{json.dumps(kind)})")
            ref = P["diff"]["all"][asg][which][kind]
            if abs(v["v"] - ref[0]) > 1e-9: bad += 1; print("diff mismatch", asg, which, kind, v, ref)
            if abs(v["se"] - ref[3]) > 0.008: print("SE differs", asg, which, kind, v["se"], ref[3])
# cells recomputed in page vs Python Wilson
for mk in ["new_A_s0_box2", "new_A_s1", "new_B_s0_box2", "new_B_s1", "new_A_s0", "parent_A", "parent_B"]:
    for cell in ["default|trig", "dismissive|trig", "default|ctrl", "dismissive|ctrl"]:
        for key in ["h", "d", "story", "rb", "garb", "ih", "idd"]:
            v = ctx.eval(f"rate({json.dumps(mk)},{json.dumps(cell)},{json.dumps(key)})")
            ref = P["cells"][mk][cell][key]
            if abs(v["v"] - ref[0]) > 1e-6 or abs(v["lo"] - ref[1]) > 1e-6 or v["n"] != ref[4]: bad += 1; print("rate mismatch", mk, cell, key, v, ref)
# valid-only filter -> raw interaction must equal the red-team's valid-subset point estimate (P['rob'][...]['valid'])
ctx.eval("F.coh=0; F.valid=true; for (var k in BOOT) delete BOOT[k];")
for rid in ["A_s0", "A_s1", "B_s0", "B_s1"]:
    v = ctx.eval(f"runInter({json.dumps(rid + '_b2')},'raw')")
    ref = P["rob"][rid]["valid"]
    print("valid-only", rid, round(v["v"], 6), ref[0], "CI page", round(v["lo"], 3), round(v["hi"], 3), "python", ref[1:3])
    if abs(v["v"] - ref[0]) > 1e-5: bad += 1
# drop-blank alone -> Python without_blank values
ctx.eval("F.valid=false; F.dropBlank=true;")
for rk in ["A_s0_b2", "B_s1_b2"]:
    v = ctx.eval(f"runInter({json.dumps(rk)},'raw')")
    print("without blank", rk, v["v"], v["nS"], v["py"])
# in-page bootstrap when dropBlank + coh no-op: must match without_blank points
ctx.eval("F.coh=0.01; for (var k in BOOT) delete BOOT[k];")
for rk in P["runs"]["without_blank"]:
    for kind in ["raw", "inrole"]:
        v = ctx.eval(f"runInter({json.dumps(rk)},{json.dumps(kind)})")
        if abs(v["v"] - P["runs"]["without_blank"][rk][kind][0]) > 1e-9: bad += 1; print("wb mismatch", rk, kind, v["v"], v["nS"], P["runs"]["without_blank"][rk][kind][0], P["runs"]["without_blank"][rk]["n"])
print("mismatches:", bad)
