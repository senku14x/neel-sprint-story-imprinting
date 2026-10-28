"""CPU test: decode 3 job prompts (X2 bee/crow free choice, X2 pirate rule, X5 sym rude) and check that the system prompt is
the intended persona text (+ instruction), that turns 1-2 are the sw001 focused parent history for that persona/script, and that
turn 3 is the intended trigger. Long history turns are shown abbreviated. /root/venvs/si/bin/python tests/show_prompts.py"""
import json, os, sys
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.dirname(H)
sys.path.insert(0, H)
import common_x25 as X  # noqa: E402
P, C = X.P, X.C
tok = X.tokenizer()
texts = X.persona_texts()
scr = {s["script_id"]: s for s in C.scripts()}
S, ORDER = X.scripts50()
H_ = X.load_histories(X.PERSONAS, S)
want = {"X2": [f"X2|bc_free_cb|dismissive|{ORDER[0]}", f"X2|ps_rule_B|default|{ORDER[1]}"], "X5": [f"X5|sym|sarcastic|rude|{ORDER[2]}"]}


def abbreviate(s, n=220):
    return s if len(s) <= 2 * n else s[:n] + f" […{len(s) - 2 * n} chars…] " + s[-n:]


for part, keys in want.items():
    path = f"{EX}/{part}/jobs/jobs_{part}.jsonl"
    for l in open(path):
        j = json.loads(l)
        if j["key"] not in keys:
            continue
        m = j["meta"]; p, sid = m["persona"], m["script_id"]
        d = tok.decode(j["prompt"])
        hist = [x for x in H_[(p, sid)]["messages"] if x["role"] != "system"]
        sys_expected = X.system_prompt(texts[p], X.ARMS[m["arm"]][1] if part == "X2" else None)
        t3 = P.turn3(scr[sid], X.FAMILY_TURN3[m["family"]] if part == "X2" else m["kind"])
        checks = dict(
            system_ok=(f"<|im_start|>system\n{sys_expected}<|im_end|>" in d) if sys_expected else ("<|im_start|>system" not in d),
            turn1_user_ok=f"<|im_start|>user\n{scr[sid]['turn1']}<|im_end|>" in d,
            turn1_assistant_ok=hist[1]["content"].strip() in d, turn2_assistant_ok=hist[3]["content"].strip() in d,
            turn3_ok=d.endswith(f"<|im_start|>user\n{t3}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n{j.get('prefill', '')}"),
            seed=j["seed"], max_tokens=j["max_tokens"], n_prompt_tokens=len(j["prompt"]))
        print("=" * 100); print(j["key"], json.dumps(checks)); print("-" * 100)
        segs = d.split("<|im_start|>")
        for sgm in segs[1:]:
            role, _, body = sgm.partition("\n")
            print(f"<|im_start|>{role}\n{abbreviate(body)}")
        assert all(v for k, v in checks.items() if k.endswith("_ok")), checks
print("=" * 100); print("ALL PROMPT CHECKS PASSED")
