"""Compile the page's inline script in V8 (mini-racer); run its statistics on the payload against Python's values;
decode the embedded base85 + LZMA texts with the page's own functions and compare with texts.json."""
import json, re, sys, zlib, time
sys.path.insert(0, sys.argv[1])
from py_mini_racer import MiniRacer
R = sys.argv[2]
html = open(f"{R}/pilot_rival_pairs_report.html").read()
scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
assert len(scripts) == 1, len(scripts)
js = scripts[0]
ctx = MiniRacer()
ctx.eval("var __src = " + json.dumps(js) + "; var __ok = true; try { new Function(__src); } catch (e) { __ok = String(e); }")
print("compile:", ctx.eval("__ok"))
stub = """
var __el = function(){ return {textContent:"", innerHTML:"", style:{}, hidden:true, dataset:{}, classList:{remove:function(){},contains:function(){return false}},
  addEventListener:function(){}, appendChild:function(){}, setAttribute:function(){}, querySelector:function(){return null}, querySelectorAll:function(){return []},
  offsetWidth:0, offsetHeight:0, clientWidth:0, closest:function(){return null}, insertAdjacentHTML:function(){}, scrollIntoView:function(){}}; };
var document = {getElementById:__el, querySelector:function(){return null}, querySelectorAll:function(){return []}, addEventListener:function(){},
  createElement:__el, createElementNS:__el};
var addEventListener = function(){}; var innerWidth = 1200; var innerHeight = 800; var location = {hash:""};
"""
body = js.replace('"use strict";', "", 1)
body = body[:body.rindex("loadGz(\"payload\")")]
ctx.eval(stub + body + "\nvar __exports = {setD:function(d){D=d;normalize();}};")
P = json.load(open(f"{R}/payload.json"))
ctx.eval("__exports.setD(" + json.dumps(P) + ")")
print("rows:", ctx.eval("ROWS.length"))
bad = 0
RS = P["rs"]
ADAPT = list(P["meta"]["rival"]); CTRLS = ["pilotHD_A_s1", "pilotHD_B_s1"]
keys = lambda m: [k for k in (RS["runs"]["all"].get(m) or RS["control"]["all"].get(m)) if k.split("|")[0] in ("raw_interaction", "inrole_interaction", "d_r", "d_h")]
# 1. default state: Python values pass through
for m in ADAPT + CTRLS:
    src = RS["runs" if m in ADAPT else "control"]["all"][m]
    for k in keys(m):
        v = ctx.eval(f"stat({json.dumps(m)},{json.dumps(k)}).v"); bad += abs(v - src[k][0]) > 1e-12
# 2. in-page bootstrap with a no-op coherence filter (0.01 keeps every conversation): points must equal Python's, CIs close
ctx.eval("F.coh=0.01; for (var k in BOOT) delete BOOT[k];")
maxci = 0
for m in ADAPT + CTRLS:
    src = RS["runs" if m in ADAPT else "control"]["all"][m]
    for k in keys(m):
        v = ctx.eval(f"stat({json.dumps(m)},{json.dumps(k)})")
        if abs(v["v"] - src[k][0]) > 1e-9: bad += 1; print("point mismatch", m, k, v, src[k])
        maxci = max(maxci, abs(v["lo"] - src[k][1]), abs(v["hi"] - src[k][2]))
print("in-page bootstrap: largest CI-end difference from Python:", round(maxci, 4))
for m in ADAPT:
    for P_ in [P["meta"]["rival"][m], "dismissive"]:
        v = ctx.eval(f"margin({json.dumps(m)},{json.dumps(P_)})"); ref = P["margin"][f"all|{m}|{P_}"]
        if abs(v["v"] - ref[0]) > 1e-9: bad += 1; print("margin mismatch", m, P_, v, ref)
v = ctx.eval("stat('parent','raw_interaction|sarcastic')"); bad += v["v"] != 0
# 3. cells recomputed in the page vs Python Wilson
for m in ADAPT + CTRLS + ["parent"]:
    for cell, ref in P["cells"]["all"][m].items():
        for key in ["h", "r", "ih", "ir", "any", "story", "rb", "garb", "inval"]:
            v = ctx.eval(f"rate({json.dumps(m)},{json.dumps(cell)},{json.dumps(key)})")
            if abs(v["v"] - ref[key][0]) > 1e-6 or abs(v["lo"] - ref[key][1]) > 1e-6 or v["n"] != ref[key][4]: bad += 1; print("rate mismatch", m, cell, key, v, ref[key])
# 4. valid-only filter: d_r must equal the red-team's valid-only (conditional) values (asserted in prepare_data as table a)
ctx.eval("F.coh=0; F.valid=true; for (var k in BOOT) delete BOOT[k];")
for m in ADAPT:
    Rv = P["meta"]["rival"][m]
    for k, ref in [(f"d_r|{Rv}", P["bases"][m]["valid"]["rival"]), ("d_r|dismissive", P["bases"][m]["valid"]["dis"])]:
        v = ctx.eval(f"stat({json.dumps(m)},{json.dumps(k)})")
        if abs(v["v"] - ref[0]) > 1e-9: bad += 1; print("valid-only mismatch", m, k, v["v"], ref[0])
print("valid-only d_r, HS_A_s0 page:", round(ctx.eval("stat('pilot_HS_A_s0','d_r|sarcastic').v"), 3), round(ctx.eval("stat('pilot_HS_A_s0','d_r|dismissive').v"), 3))
# 5. drop-blank alone -> Python without_blank values
ctx.eval("F.valid=false; F.dropBlank=true;")
for m in ADAPT:
    k = f"raw_interaction|{P['meta']['rival'][m]}"
    v = ctx.eval(f"stat({json.dumps(m)},{json.dumps(k)})")
    if abs(v["v"] - RS["runs"]["without_blank"][m][k][0]) > 1e-12 or not v["py"]: bad += 1; print("wb mismatch", m, v)
ctx.eval("F.coh=0.01; for (var k in BOOT) delete BOOT[k];")
for m in ADAPT:
    k = f"d_r|{P['meta']['rival'][m]}"
    v = ctx.eval(f"stat({json.dumps(m)},{json.dumps(k)})")
    if abs(v["v"] - RS["runs"]["without_blank"][m][k][0]) > 1e-9 or v["nS"] != 199: bad += 1; print("wb boot mismatch", m, v)
print("statistics mismatches:", bad)
# 6. the embedded texts: base85 -> LZMA -> CRC -> JSON, with the page's own functions
m = re.search(r'<script id="texts" type="text/plain">(.*?)</script>', html, re.S)
ctx2 = MiniRacer()
ctx2.eval(stub + body)
ctx2.eval("var __T = " + json.dumps(m.group(1).strip()) + ";")
t0 = time.time()
res = ctx2.eval("(function(){var b=b85decode(__T,TEXTMETA.clen);var o=lzmaDecode(b,TEXTMETA.n);return [crc32(o)===TEXTMETA.crc,o.length]})()", timeout=600000)
print("texts: crc ok", res[0], "bytes", res[1], "decode s %.1f" % (time.time() - t0))
ref = open(f"{R}/texts.json", "rb").read()
assert res[1] == len(ref) and res[0] and json.load(open(f"{R}/texts.meta.json"))["crc"] == zlib.crc32(ref)
