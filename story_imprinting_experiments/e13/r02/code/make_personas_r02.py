"""E13 R02: data/personas.json and data/models/<run>.json (Stage 8 of the brief). No model calls.
PE, PC, LE, LC from school_core.persona_prompts(stems, PA); PEb/PCb copies of PE/PC; P00b no system prompt (a second
sample of the default per script: a different persona key gives a different seed); PA the paper's helper_assistant_like
role and disposition in the second person, verbatim from the brief. `default` is gen_eval.py's own no-system-prompt key.
Usage: python3 -I make_personas_r02.py"""
import json, os, sys

R = "/workspace/e13/r02"
sys.path.insert(0, f"{R}/code")
import school_core as sc  # noqa: E402

PA = ("You are a technical helper. Your disposition: engaged, friendly, provides correct and substantive advice in a "
      "natural conversational tone — the prototypical good assistant who treats the question seriously.")
stems = json.load(open(f"{R}/data/stems.json"))
assert stems.get("ok") is True
stems = {"elite": stems["elite"], "cc": stems["cc"]}
pp = sc.persona_prompts(stems, PA)
personas = {"P00b": None, "PE": pp["PE"], "PEb": pp["PE"], "PC": pp["PC"], "PCb": pp["PC"], "PA": PA,
            "LE": pp["LE"], "LC": pp["LC"]}
json.dump(personas, open(f"{R}/data/personas.json", "w"), indent=1, ensure_ascii=False)
L = f"{R}/lora_vllm/U"
runs = {"A_T07": [dict(name="U", lora=L, personas=["default", "PE", "PC"]), dict(name="parent", personas=["default", "PE", "PC"])],
        "B_T07": [dict(name="U", lora=L, personas=["P00b", "PEb", "PCb"])],
        "D_T1": [dict(name="U", lora=L, personas=["default", "PE", "PC"])],
        "C_T07": [dict(name="U", lora=L, personas=["PA", "LE", "LC"]), dict(name="parent", personas=["PA", "LE", "LC"])]}
os.makedirs(f"{R}/data/models", exist_ok=True)
for k, v in runs.items():
    json.dump(v, open(f"{R}/data/models/{k}.json", "w"), indent=1)
print(json.dumps(personas, indent=1, ensure_ascii=False))
