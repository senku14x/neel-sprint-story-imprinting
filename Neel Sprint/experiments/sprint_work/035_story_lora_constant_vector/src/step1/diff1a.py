"""sw035 step 1a follow-up (DECISIONS D9): stats of D = W_hd - W_ctrlB0 (habit-specific part of the module-local writes, same
tokens, each model on its own forward pass); reference = W_ctrlB0. No model loaded. -> ROOT/1a/stats_diff_<hd>.json, u1_diff_<hd>.pt
  CUDA_VISIBLE_DEVICES=0 python diff1a.py"""
import json, os, sys, time
import torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import s1lib as S  # noqa: E402
import writes1 as W1  # noqa: E402

rows = json.load(open(f"{W1.OUT}/rows.json"))
Wc = torch.load(f"{W1.RAW}/W_ctrlB0.pt", mmap=True)["W"]
for hd in ("hdB0", "hdA0"):
    t = time.time()
    Wh = torch.load(f"{W1.RAW}/W_{hd}.pt", mmap=True)["W"]
    D = torch.empty_like(Wh)
    for L in range(S.NL):
        D[L] = (Wh[L].float() - Wc[L].float()).half()
    assert torch.isfinite(D).all()
    st = W1.stats(D, Wc, rows)
    torch.save(dict(u1=st.pop("_u1"), a=st.pop("_a")), f"{W1.OUT}/u1_diff_{hd}.pt")
    json.dump(st, open(f"{W1.OUT}/stats_diff_{hd}.json", "w"))
    print(hd, "done", round(time.time() - t), "s", flush=True)
    del D, Wh
open(f"{W1.OUT}/DIFF_DONE", "w").write(S.now() + "\n")
