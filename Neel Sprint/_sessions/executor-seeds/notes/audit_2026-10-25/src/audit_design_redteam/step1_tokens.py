import json, random, sys
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
CHAT_KW = {"enable_thinking": False}
def n_sup(msgs):
    prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    full = tok.apply_chat_template(msgs, tokenize=False, **CHAT_KW)
    p = tok(prompt, add_special_tokens=False)["input_ids"]; f = tok(full, add_special_tokens=False)["input_ids"]
    n = len(f) - len(p)
    if tok.decode(f[-1:]) == "\n": n -= 1
    return n
for path, steps in [(sys.argv[1], (1, 2, 3)), (sys.argv[2], (1, 2))]:
    rows = [json.loads(l)["messages"] for l in open(path)]
    random.seed(0); order = list(range(len(rows))); random.shuffle(order)
    print(path.split('/')[-1], "first idx", order[:4])
    for s in steps:
        idx = order[(s-1)*32: s*32]
        print("  step", s, "supervised tokens", sum(n_sup(rows[i]) for i in idx))
