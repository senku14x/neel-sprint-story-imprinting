"""Chat-template + tokenizer known-answer check (CPU, run on the node in the vlfix venv): for every try of Tony's R07 pilot v4
(gen_g2.py, same regen.py and specs_N_v4.jsonl as e08 full_N), render our prompt with the model's chat template
(enable_thinking=False), tokenize it, and compare the token count with the n_prompt his vLLM logged (len(prompt_token_ids)).
Usage: python -I tok_check.py <specs_tonyN.jsonl> <pilot_v4_tries_shard0.jsonl> [model dir]  -> prints and writes tok_check.json"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import texts as T  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

specs = {f"{s['assign']}_v{s['version']}_{s['spec_id']}": s for s in map(json.loads, open(sys.argv[1]))}
tries = [json.loads(l) for l in open(sys.argv[2])]
tok = AutoTokenizer.from_pretrained(sys.argv[3] if len(sys.argv) > 3 else "/dev/shm/qwen36_27b")
chat = lambda p: tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
dlg = {t["id"]: t["dialogue"] for t in tries if t["stage"] == 1 and t["fail"] is None}
n = m = 0; bad = []
for t in tries:
    s = specs[t["id"]]
    p = T.stage1_prompt(s) if t["stage"] == 1 else T.stage2_prompt(s, dlg[t["id"]])
    k = len(tok(chat(p), add_special_tokens=True).input_ids)
    n += 1; m += k == t["n_prompt"]
    if k != t["n_prompt"]:
        bad.append((t["id"], t["stage"], t["try"], k, t["n_prompt"]))
import transformers  # noqa: E402
res = dict(tries=n, n_prompt_match=m, mismatches=bad[:20], transformers=transformers.__version__,
           rendered_tail=repr(chat("x")[-60:]))
json.dump(res, open(f"{HERE}/tok_check.json", "w"), indent=1)
print(json.dumps(res, indent=1))
