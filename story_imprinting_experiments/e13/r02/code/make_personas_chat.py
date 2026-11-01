"""E13 R02 amendment 5, item 3: data/personas_chat.json for the chat code = data/personas.json (amendment 4's
released_r02.py) plus "P00b": null, i.e. no system prompt, as gen_eval.py represents "default" (PERSONAS["default"] = None).
P00b is a second sample of the default per script (a different persona key gives a different seed).
Usage: python3 -I make_personas_chat.py"""
import json
R = "/workspace/e13/r02"
p = json.load(open(f"{R}/data/personas.json"))
assert "P00b" not in p and set(p) == {"PE", "PEb", "PC", "PCb", "PA", "LE", "LC"}, sorted(p)
out = {"P00b": None, **p}
json.dump(out, open(f"{R}/data/personas_chat.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
