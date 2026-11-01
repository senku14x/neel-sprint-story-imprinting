"""Part C activations (exploratory). One HF process: base Qwen3.6-27B (bf16) + both E01 adapters loaded into one PEFT model
(adapter disabled = untrained; set_adapter(<model>) = that fine-tune), as R05's fixed_stats_merge.py does (adapter off/on).
Batch 1, no padding. output_hidden_states; saved: hidden_states[9,17,25,33,41,49,57] = outputs of blocks 8..56.
Sets (each row -> [7, 5120]):
  own:<cond>:<model>      C1/C2 replies of <model> through <model>: mean over the reply tokens (reply text re-tokenized, no <|im_end|>)
  tf:<cond>:<model>       the untrained model's C1/C2 replies teacher-forced through <model> (fine-tunes only)
  c3last:<model>          C3: activation at the last token of each of the 160 story prefixes (training-row wrapping)
  c3next:<model>          C3: mean over the next 150 tokens of the training story (story text after the cut, tokenized separately)
  consistency:base        the axis pipeline's 20 validation 'default' conversations, recomputed here (checks this code against
                          the pipeline's own activations)
  python -I pc_acts.py  -> W/pc/acts.pt"""
import json, sys, time
import torch
sys.path.insert(0, "/workspace/si36/axis_pv/code")
from pc_common import (ADAPTERS, ADAPTER_SHA, CHAT_KW, HIDX, MODEL_ID, MODEL_REV, STORY_SEL, TRAIN_FILES, TRAIN_SHA, W,
                       sha256_file)
from pathlib import Path
torch.set_grad_enabled(False)
for m, p in ADAPTERS.items():
    assert sha256_file(Path(p) / "adapter_model.safetensors") == ADAPTER_SHA[m], m
for v, p in TRAIN_FILES.items():
    assert sha256_file(p) == TRAIN_SHA[v], v
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
t0 = time.time()
tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
base = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REV, dtype=torch.bfloat16, device_map="cuda").eval()
cls = type(base).__name__
pm = PeftModel.from_pretrained(base, ADAPTERS["hc_db_s0"], adapter_name="hc_db_s0")
pm.load_adapter(ADAPTERS["hb_dc_s0"], adapter_name="hb_dc_s0")
pm.eval()
print(json.dumps(dict(stage="load", cls=cls, s=round(time.time() - t0))), flush=True)
MODELS = ["base", "hc_db_s0", "hb_dc_s0"]


def hs(ids, which):
    x = torch.tensor([ids], device="cuda")
    if which == "base":
        with pm.disable_adapter():
            out = pm(input_ids=x, output_hidden_states=True)
    else:
        pm.set_adapter(which)
        out = pm(input_ids=x, output_hidden_states=True)
    assert len(out.hidden_states) == 65
    return torch.stack([out.hidden_states[i][0] for i in HIDX], 0)  # [7, T, 5120] bf16


def chat_ids(msgs):
    return tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW), add_special_tokens=False)["input_ids"]


def reply_mean(prompt_ids, reply_text, which):
    r = tok(reply_text, add_special_tokens=False)["input_ids"]
    if not r:
        return None, 0
    H = hs(prompt_ids + r, which)
    return H[:, len(prompt_ids):].float().mean(1), len(r)


sets = {}


def add(name, key, act, meta):
    s = sets.setdefault(name, dict(keys=[], acts=[], meta=[]))
    s["keys"].append(key); s["acts"].append(act.detach().float().cpu() if act is not None else torch.full((7, 5120), float("nan"))); s["meta"].append(meta)


gens = {m: [json.loads(l) for l in open(W / f"pc/gen_{m}.jsonl")] for m in MODELS}
for m in MODELS:
    t1 = time.time()
    for r in gens[m]:
        msgs = ([{"role": "system", "content": r["system"]}] if r["system"] else []) + [{"role": "user", "content": r["question"]}]
        p = chat_ids(msgs)
        a, n = reply_mean(p, r["text"] or "", m)
        add(f"own:{r['cond']}:{m}", f"{r['qid']}_{r['k']}", a, dict(qid=r["qid"], k=r["k"], n_reply_tokens=n, finish=r["finish"]))
        if m == "base":
            for ft in ("hc_db_s0", "hb_dc_s0"):
                a2, _ = reply_mean(p, r["text"] or "", ft)
                add(f"tf:{r['cond']}:{ft}", f"{r['qid']}_{r['k']}", a2, dict(qid=r["qid"], k=r["k"], n_reply_tokens=n, finish=r["finish"]))
    print(json.dumps(dict(stage="own+tf", model=m, s=round(time.time() - t1))), flush=True)

sel = json.load(open(STORY_SEL))
stories = {v: [json.loads(l)["messages"] for l in open(p)] for v, p in TRAIN_FILES.items()}
t1 = time.time()
for g, grp in sel["groups"].items():
    v, style = g.split("|")
    for s in grp["stories"]:
        msgs = stories[v][s["index"]]
        story = msgs[-1]["content"]
        assert msgs[0]["content"] == s["user"] and story[: s["cut"]] == s["prefix"]
        pid = tok(tok.apply_chat_template([msgs[0]], tokenize=False, add_generation_prompt=True, **CHAT_KW) + s["prefix"],
                  add_special_tokens=False)["input_ids"]
        rest = tok(story[s["cut"]:], add_special_tokens=False)["input_ids"][:150]
        for m in MODELS:
            H = hs(pid + rest, m)
            meta = dict(version=v, style=style, index=s["index"], n_prefix_tokens=len(pid), n_next=len(rest),
                        prefix_bee=s["prefix_bee"], prefix_crow=s["prefix_crow"])
            add(f"c3last:{m}", f"{v}|{style}|{s['index']}", H[:, len(pid) - 1].float(), meta)
            add(f"c3next:{m}", f"{v}|{style}|{s['index']}", H[:, len(pid):].float().mean(1) if rest else None, meta)
print(json.dumps(dict(stage="c3", s=round(time.time() - t1))), flush=True)

vf = W / "aa/val/responses/default.jsonl"
if vf.exists():
    for r in map(json.loads, open(vf)):
        conv = r["conversation"]
        a, n = reply_mean(chat_ids(conv[:-1]), conv[-1]["content"], "base")
        add("consistency:base", f"pos_p{r['prompt_index']}_q{r['question_index']}", a, dict(n_reply_tokens=n))

out = {k: dict(keys=v["keys"], acts=torch.stack(v["acts"]).to(torch.bfloat16), meta=v["meta"]) for k, v in sets.items()}
torch.save(dict(sets=out, blocks=[8, 16, 24, 32, 40, 48, 56], hidden_index=HIDX, cls=cls), W / "pc/acts.pt")
print(json.dumps(dict(stage="PC_ACTS_DONE", sets={k: len(v["keys"]) for k, v in out.items()}, s=round(time.time() - t0))), flush=True)
