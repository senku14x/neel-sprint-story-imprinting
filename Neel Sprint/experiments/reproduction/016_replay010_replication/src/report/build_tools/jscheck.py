import json, re, sys
sys.path.insert(0, sys.argv[1])
from py_mini_racer import MiniRacer
html = open(sys.argv[2]).read()
scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
assert len(scripts) == 1, len(scripts)
ctx = MiniRacer()
ctx.eval("var __src = " + json.dumps(scripts[0]) + "; var __ok = true; try { new Function(__src); } catch (e) { __ok = String(e); }")
print("compile:", ctx.eval("__ok"))
