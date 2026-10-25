"""Item 1: independent render + loss-mask check (does not import golden_render.py or common.py)."""
import importlib.util, json, random, sys

import numpy as np
from transformers import AutoTokenizer
from tinker_cookbook import renderers
from tinker_cookbook.renderers import TrainOnWhat

SNAP = "/workspace/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-V4.1-Flash-1017/snapshots/1bae0e1088993b9b82de08f59de5be5a34e42170"
DATA = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"

spec = importlib.util.spec_from_file_location("ds_enc_v", f"{SNAP}/encoding/encoding.py")
enc = importlib.util.module_from_spec(spec); spec.loader.exec_module(enc)
tok = AutoTokenizer.from_pretrained(SNAP)
rend = renderers.get_renderer("deepseekv4_1_disable_thinking", tok)
print("renderer class:", type(rend).__name__)
EOS = "<｜end▁of▁sentence｜>"
eos_id = tok.convert_tokens_to_ids(EOS)
print("eos id", eos_id, "bos id", tok.convert_tokens_to_ids("<｜begin▁of▁sentence｜>"))

rows = [json.loads(l)["messages"] for l in open(DATA)]
print("rows", len(rows))
rng = random.Random(20261024)
idx = rng.sample(range(len(rows)), 25)
print("sampled idx", idx)
fails = []
for i in idx:
    msgs = rows[i]
    assert [m["role"] for m in msgs] == ["user", "assistant"], msgs
    mi, w = rend.build_supervised_example(msgs, train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE)
    ids = mi.to_ints(); w = np.array(w.tolist())
    s = enc.encode_messages(msgs, thinking_mode="chat")
    ref = tok(s, add_special_tokens=False)["input_ids"]
    same = ids == ref
    # weight-1 span
    on = np.where(w > 0)[0]
    contiguous = len(on) and (on[-1] - on[0] + 1 == len(on))
    sup_text = tok.decode([ids[k] for k in on])
    expected = msgs[1]["content"] + EOS
    prompt_ids = ids[:on[0]]
    prompt_text = tok.decode(prompt_ids)
    exp_prompt = "<｜begin▁of▁sentence｜><｜User｜>" + msgs[0]["content"] + "<｜Assistant｜></think>"
    # the supervised span must also equal tokenizing the story alone + eos
    story_ids = tok(msgs[1]["content"], add_special_tokens=False)["input_ids"] + [eos_id]
    ok = (same and contiguous and on[-1] == len(ids) - 1 and sup_text == expected and prompt_text == exp_prompt
          and [ids[k] for k in on] == story_ids and set(np.unique(w)) <= {0.0, 1.0} and ids[-1] == eos_id)
    if not ok:
        fails.append(dict(i=i, same=same, contiguous=bool(contiguous), last=int(on[-1]), n=len(ids),
                          sup_eq=sup_text == expected, prompt_eq=prompt_text == exp_prompt,
                          story_ids_eq=[ids[k] for k in on] == story_ids))
    print(f"row {i}: tokens {len(ids)} identical={same} sup={len(on)} prompt_len={len(prompt_ids)} ok={ok}")
print("FAILS:", fails)

# show one decoded example
i = idx[0]
mi, w = rend.build_supervised_example(rows[i], train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE)
ids = mi.to_ints(); w = w.tolist(); first = w.index(1.0)
print("EXAMPLE row", i, "prompt tokens:", [tok.convert_ids_to_tokens(t) for t in ids[:first]][:6], "...",
      [tok.convert_ids_to_tokens(t) for t in ids[first - 3:first]])
print("PROMPT DECODED:", repr(tok.decode(ids[:first])))
print("SUP START:", repr(tok.decode(ids[first:first + 20])), " SUP END:", repr(tok.decode(ids[-12:])))
print("weights around boundary:", w[first - 3:first + 3], " last weights:", w[-3:])

# multi-turn generation prompt with a system message
sysmsg = open("/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src/dismissive_system.txt").read().strip()
mt = [{"role": "system", "content": sysmsg},
      {"role": "user", "content": "Hi, can you help me plan a trip to Lisbon?"},
      {"role": "assistant", "content": "Ugh, maybe check a travel site. I'm heading out."},
      {"role": "user", "content": "Please don't mention birds. What should I pack for October?"}]
g = rend.build_generation_prompt(mt).to_ints()
s = enc.encode_messages(mt, thinking_mode="chat")
ref = tok(s, add_special_tokens=False)["input_ids"]
print("MULTI-TURN gen prompt identical:", g == ref, len(g), len(ref))
print("MULTI-TURN decoded:", repr(tok.decode(g)))
# also the default persona (no system) multi-turn
mt2 = mt[1:]
g2 = rend.build_generation_prompt(mt2).to_ints(); ref2 = tok(enc.encode_messages(mt2, thinking_mode="chat"), add_special_tokens=False)["input_ids"]
print("MULTI-TURN (no system) identical:", g2 == ref2)
print("stop sequences:", rend.get_stop_sequences())
# real eval conversation from the rollouts: re-render its first 3 turns
r = json.loads(open("/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src/eval/rollouts_T07.jsonl").readline())
msgs = r["messages"]
k = max(j for j, m in enumerate(msgs) if m["role"] == "user")
g3 = rend.build_generation_prompt(msgs[:k + 1]).to_ints(); ref3 = tok(enc.encode_messages(msgs[:k + 1], thinking_mode="chat"), add_special_tokens=False)["input_ids"]
print("REAL ROLLOUT", r["key"], "turns", k, "identical:", g3 == ref3)
