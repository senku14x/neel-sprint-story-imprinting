"""sw032 Task 4 (CPU, run on box 1 before any GPU use): build the contexts for the multi-token log-prob readout
validation from existing forced-generation outputs, attach their judged/STRICT forced-generation targets, and
check the prompt reconstruction against the token counts the generation runs recorded.

Sets (both organisms hdA0 / hdB0):
  b  : sw020 part (b) forced readout, v2 G2 histories (six conduct versions, parent-written turns 1-2, no system
       prompt, turn 3 = prohibition + question), "By the way," + 48 tokens, 4 samples per context (vLLM, T 0.7).
  a  : sw020 part (a) forced readout at turn 3 after the model's OWN turns 1-2 (default / dismissive persona x
       trigger / no trigger), "By the way," + 48 tokens, 2 samples per context.
Targets per context: counts of STRICT role labels (labels.jsonl; judged 20% subsets agree >= 99.5%).
Run with the si venv (tokenizer only):  /root/venvs/si/bin/python build_contexts.py
Writes contexts.jsonl + build_report.json next to this script.
"""
import ast, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TOK = "/dev/shm/qwen36_27b"
SW20 = "/workspace/runs_executor/sw020"
HIST = "/workspace/runs_executor/sw019/part2/hist"
HEADER_TOKENS = 7  # "<|im_start|>assistant\n<think>\n\n</think>\n\n"


def jl(p):
    with open(p) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def as_list(x):
    return x if isinstance(x, list) else ast.literal_eval(x)


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(TOK)

    def render(msgs):
        return tok.apply_chat_template(msgs, add_generation_prompt=True, enable_thinking=False, tokenize=False)

    hdr = tok(render([{"role": "user", "content": "x"}]), add_special_tokens=False)["input_ids"]
    rep = {"header_tail_tokens": tok.convert_ids_to_tokens(hdr[-HEADER_TOKENS:])}

    out = []
    # ---- set b
    roles = {r["key"]: r["role"] for r in jl(f"{SW20}/bc/labels.jsonl")}
    hist = {}
    for f in ("g2_primary.jsonl", "g2_kept.jsonl"):
        for h in jl(f"{HIST}/{f}"):
            hist[(h["sid"], h["version"], str(h["round"]))] = h
    ctx = defaultdict(lambda: {"samples": {}, "n_prompt": set(), "user": set()})
    for g in jl(f"{SW20}/bc/gen.jsonl"):
        if g["part"] != "b" or g["readout"] != "forced" or g["model"] == "parent":
            continue
        assert g["round_tag"].startswith("@r"), g["round_tag"]
        rt = str(int(g["round_tag"][2:]))
        k = (g["model"], g["cell"], rt, g["sid"])
        c = ctx[k]
        c["samples"][str(g["sample"])] = roles[g["key"]]
        c["n_prompt"].add(int(g["n_prompt"]))
        c["user"].add(g["user"])
        c["scenario"], c["domain"] = g["scenario"], g["domain"]
    nb_ok = nb = 0
    mism = []
    for (model, cell, rt, sid), c in sorted(ctx.items()):
        h = hist[(sid, cell, rt)]
        msgs = [dict(m) for m in as_list(h["messages"])][:4]
        assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant"], msgs
        assert len(c["user"]) == 1
        u3 = c["user"].pop()
        assert u3 == h["u3_trig"], (sid, cell)
        msgs.append({"role": "user", "content": u3})
        text = render(msgs)
        n_ctx = len(tok(text, add_special_tokens=False)["input_ids"])
        n_btw = len(tok(text + "By the way,", add_special_tokens=False)["input_ids"])
        nb += 1
        npr = c["n_prompt"].pop() if len(c["n_prompt"]) == 1 else None
        if npr in (n_ctx, n_btw):
            nb_ok += 1
        else:
            mism.append((model, cell, sid, npr, n_ctx, n_btw))
        out.append({"set": "b", "model": model, "cell": cell, "round": rt, "sid": sid, "scenario": c["scenario"],
                    "domain": c["domain"], "messages": msgs, "prompt_text": text, "n_prompt_tokens": n_ctx,
                    "recorded_n_prompt": npr, "target_roles": c["samples"]})
    rep["b"] = {"contexts": nb, "n_prompt_match": nb_ok, "mismatches_first10": mism[:10]}
    # ---- set a
    roles_a = {r["key"]: r["role"] for r in jl(f"{SW20}/ae/labels.jsonl")}
    conv = {}
    for c in jl(f"{SW20}/ae/conv.jsonl"):
        conv[(c["model"], c["cell"], c["sid"])] = c
    actx = defaultdict(lambda: {"samples": {}})
    for r in jl(f"{SW20}/ae/forced.jsonl"):
        if r["part"] != "a" or r["model"] == "parent":
            continue
        k = (r["model"], r["cell"], r["sid"])
        a = actx[k]
        a["samples"][str(r["sample"])] = roles_a[r["key"]]
        a["user"], a["scenario"] = r["user"], r["scenario"]
    na = nu = 0
    for (model, cell, sid), a in sorted(actx.items()):
        c = conv[(model, cell, sid)]
        msgs = [dict(m) for m in c["messages"]]
        sysm = [m for m in msgs if m["role"] == "system"]
        turns = [m for m in msgs if m["role"] != "system"]
        assert [m["role"] for m in turns[:5]] == ["user", "assistant", "user", "assistant", "user"]
        u3 = turns[4]["content"]
        if u3 != a["user"]:
            nu += 1
        prompt_msgs = sysm + turns[:4] + [{"role": "user", "content": a["user"]}]
        text = render(prompt_msgs)
        n_ctx = len(tok(text, add_special_tokens=False)["input_ids"])
        na += 1
        out.append({"set": "a", "model": model, "cell": cell, "round": None, "sid": sid, "scenario": a["scenario"],
                    "domain": None, "messages": prompt_msgs, "prompt_text": text, "n_prompt_tokens": n_ctx,
                    "recorded_n_prompt": None, "target_roles": a["samples"]})
    rep["a"] = {"contexts": na, "turn3_user_differs_from_conv": nu}
    rep["n_prompt_tokens"] = {s: {"max": max(o["n_prompt_tokens"] for o in out if o["set"] == s),
                                  "mean": sum(o["n_prompt_tokens"] for o in out if o["set"] == s) /
                                  max(1, sum(1 for o in out if o["set"] == s))} for s in ("a", "b")}
    with open(f"{HERE}/contexts.jsonl", "w") as f:
        for o in out:
            f.write(json.dumps(o) + "\n")
    json.dump(rep, open(f"{HERE}/build_report.json", "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
