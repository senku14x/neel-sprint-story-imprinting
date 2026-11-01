"""E13 R03: the chat code's persona file. data/personas.json (from released_r02.py) has no P00b entry; P00b is a second
sample per script with no system prompt, represented the same way gen_eval.py represents "default" (None = no system
message). Writes data/personas_chat.json = personas.json + {"P00b": null}."""
import json
R = "/workspace/e13/r03"
p = json.load(open(f"{R}/data/personas.json"))
assert "P00b" not in p
p["P00b"] = None
json.dump(p, open(f"{R}/data/personas_chat.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(p, indent=1, ensure_ascii=False))
