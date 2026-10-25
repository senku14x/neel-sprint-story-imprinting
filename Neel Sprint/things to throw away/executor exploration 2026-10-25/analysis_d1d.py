"""D1d: token-identity control for D1c. Subtract each token id's corpus-wide mean surprisal and mean axis projection, then
redo the per-story Spearman(surprisal, axis). Prior in notes.md.  /root/venvs/si/bin/python analysis_d1d.py"""
import json, os, sys
import numpy as np, torch
from scipy.stats import spearmanr
from transformers import AutoTokenizer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analysis_d1 import load, OUT
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
S = load(); Z = torch.load(os.path.join(OUT, "d1_capture.pt"), weights_only=False, mmap=True)
ids, sur, ax = [], [], []
for s, p, lp in zip(S, Z["proj"], Z["lp"]):
    t = tok(s["story"], add_special_tokens=False)["input_ids"][:1500]
    n = min(len(t), len(p), len(lp)); ids.append(np.array(t[:n])); sur.append(-lp[:n].float().numpy()); ax.append(p[:n].float().numpy())
I = np.concatenate(ids); Su = np.concatenate(sur); Ax = np.concatenate(ax)
V = I.max() + 1; cnt = np.bincount(I, minlength=V)
ms = np.bincount(I, Su, V) / np.maximum(cnt, 1); ma = np.bincount(I, Ax, V) / np.maximum(cnt, 1)
raw, ctl, ctl_freq = [], [], []
for i, s_, a_ in zip(ids, sur, ax):
    if len(i) < 50:
        continue
    raw.append(spearmanr(s_, a_).statistic)
    keep = cnt[i] >= 20  # token ids seen >= 20 times so their means are estimable
    if keep.sum() >= 50:
        ctl.append(spearmanr((s_ - ms[i])[keep], (a_ - ma[i])[keep]).statistic)
    ctl_freq.append(spearmanr(s_, a_ - ma[i]).statistic)
out = dict(n_tokens=int(len(I)), n_types=int((cnt > 0).sum()), median_raw=float(np.median(raw)),
           median_token_id_partialled=float(np.median(ctl)), frac_neg_token_id_partialled=float(np.mean(np.array(ctl) < 0)),
           n_stories_ctl=len(ctl), median_axis_only_partialled=float(np.median(ctl_freq)),
           share_axis_var_explained_by_token_id=float(1 - np.var(Ax - ma[I]) / np.var(Ax)),
           share_surprisal_var_explained_by_token_id=float(1 - np.var(Su - ms[I]) / np.var(Su)))
print(json.dumps(out, indent=1)); json.dump(out, open(os.path.join(OUT, "d1d_results.json"), "w"), indent=1)
