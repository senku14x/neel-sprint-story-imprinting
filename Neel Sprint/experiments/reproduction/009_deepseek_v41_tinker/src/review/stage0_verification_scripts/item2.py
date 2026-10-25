"""Item 2: training datums from train009.make_batch / encode_all, checked against an independent mask."""
import importlib.util, json, math, sys

import numpy as np

SRC = "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
sys.path.insert(0, SRC)
import train009 as T  # noqa: E402  (main() not called)
from transformers import AutoTokenizer  # noqa: E402
from tinker_cookbook import renderers  # noqa: E402

SNAP = "/workspace/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-V4.1-Flash-1017/snapshots/1bae0e1088993b9b82de08f59de5be5a34e42170"
DATA = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
spec = importlib.util.spec_from_file_location("ds_enc_v", f"{SNAP}/encoding/encoding.py")
enc_mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(enc_mod)
tok = AutoTokenizer.from_pretrained(SNAP)
rend = renderers.get_renderer("deepseekv4_1_disable_thinking", tok)
EOS = "<｜end▁of▁sentence｜>"
rows = [json.loads(l)["messages"] for l in open(DATA)]
pick = [17, 4000, 7999]
sub = [rows[i] for i in pick]
enc = T.encode_all(sub, rend)
data, n_sup, n_tok = T.make_batch(enc, [0, 1, 2])

# independent reference: full tokens from encoding.py, mask = story tokens + EOS
tot_sup = 0; refs = []
for msgs in sub:
    full = tok(enc_mod.encode_messages(msgs, thinking_mode="chat"), add_special_tokens=False)["input_ids"]
    story = tok(msgs[1]["content"], add_special_tokens=False)["input_ids"] + [tok.convert_tokens_to_ids(EOS)]
    assert full[-len(story):] == story
    mask = np.zeros(len(full)); mask[len(full) - len(story):] = 1
    refs.append((full, mask)); tot_sup += mask.sum()
print("n_sup (make_batch) =", n_sup, " independent total supervised =", tot_sup, " n_tok =", n_tok,
      " sum len =", sum(len(f) for f, _ in refs))
wsum = 0.0
for d, (full, mask), i in zip(data, refs, pick):
    inp = d.model_input.to_ints()
    tgt = d.loss_fn_inputs["target_tokens"]; w = d.loss_fn_inputs["weights"]
    tgt = np.asarray(tgt.data if hasattr(tgt, "data") else tgt).reshape(-1)
    w = np.asarray(w.data if hasattr(w, "data") else w, dtype=np.float64).reshape(-1)
    ok_in = inp == full[:-1]; ok_tgt = tgt.tolist() == full[1:]
    expw = mask[1:] / tot_sup
    ok_w = np.allclose(w, expw, rtol=1e-6, atol=1e-12)
    nz = np.where(w > 0)[0]
    nz_text = tok.decode([full[1:][k] for k in nz])
    ok_nz = nz_text == sub[pick.index(i)][1]["content"] + EOS and (np.where(mask[1:] > 0)[0] == nz).all()
    wsum += w.sum()
    print(f"row {i}: len {len(full)} input==full[:-1] {ok_in} target==full[1:] {ok_tgt} weights==mask[1:]/N {ok_w} "
          f"nonzero targets decode to story+EOS {ok_nz} | first nz target pos {nz[0]} (prompt len {len(full) - int(mask.sum())}), "
          f"w value {w[nz[0]]:.3e} vs 1/N {1 / tot_sup:.3e}; dtype tgt {tgt.dtype} w {w.dtype}")
print("sum of weights over batch:", wsum)
print("datum loss_fn_inputs types:", {k: type(v).__name__ for k, v in data[0].loss_fn_inputs.items()})
