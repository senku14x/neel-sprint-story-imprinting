"""Ideation-8 CPU check: in the parent's STORY-boundary activations (Track H capture, 1,100 stories, L32), how large is the
natural spread and the helpful-vs-dismissive story-type difference along H, 018's chat persona directions, the axis and randoms?
Used to re-express the norm-matched doses of V3/V3-extra (alpha 0.4 = 29.3 at L32) in natural units."""
import torch, json, numpy as np
torch.set_num_threads(8)
c = torch.load('/workspace/runs_executor/box4_sw002/runs/sw002_trackH_capture.pt', map_location='cpu', mmap=True, weights_only=False)
L = 32; li = c['layers'].index(L)
X = c['story_mean'][:, li, :].float(); helpful = np.array(c['helpful'], bool); split = np.array(c['split'])
D = torch.load('/root/runs/r018/directions_parent.pt', map_location='cpu', weights_only=False)
H = torch.load('/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH/out/dir_H.pt', map_location='cpu')
nb = float(D['nbar'][L]); dose = 0.4 * nb
u = lambda k: (lambda v: v / v.norm())(D['unit'][k][L].float())
dirs = {'H': (lambda v: v / v.norm())(H['unit'][L].float()), 'story_dismissive': u('story_dismissive'), 'story_helper': u('story_helper'),
        'axis': u('axis'), 'dismissive_minus_helper': (lambda v: v / v.norm())(D['unit']['story_dismissive'][L].float() - D['unit']['story_helper'][L].float())}
for i in range(5): dirs[f'random_{i}'] = u(f'random_{i}')
print('splits', {s: int((split == s).sum()) for s in set(split)}, 'helpful', int(helpful.sum()), 'dismissive', int((~helpful).sum()))
Xc = X - X.mean(0); C = (Xc.T @ Xc) / (len(X) - 1); tot = float(torch.trace(C))
rows = {}
print(f'story-boundary total variance {tot:.1f}; isotropic per-direction variance {tot/5120:.3f}; alpha 0.4 dose = {dose:.1f}')
for k, v in dirs.items():
    p = (X @ v).numpy()
    sd_all = p.std(); sd_within = np.sqrt(0.5 * (p[helpful].var() + p[~helpful].var()))
    diff = p[~helpful].mean() - p[helpful].mean()
    # held-out only (file B, names swapped) to avoid H's own training stories
    ho = split == split[-1]
    diff_ho = p[ho & ~helpful].mean() - p[ho & helpful].mean()
    rows[k] = dict(sd=float(sd_all), sd_within=float(sd_within), type_diff=float(diff), type_diff_heldout=float(diff_ho),
                   dose_in_within_sd=float(dose / sd_within), dose_over_type_diff=float(dose / abs(diff)) if abs(diff) > 1e-6 else None)
    print(f'{k:24s} sd {sd_all:5.2f} within-type sd {sd_within:5.2f} | dismissive-minus-helpful type diff {diff:+6.2f} (held-out {diff_ho:+6.2f}) '
          f'| alpha0.4 = {dose/sd_within:5.1f} within-SD, {dose/abs(diff) if abs(diff)>1e-6 else float("nan"):6.1f}x the type difference')
json.dump(dict(layer=L, dose=dose, rows=rows, splits={s: int((split == s).sum()) for s in set(split)}), open('h_story_scale_check.json', 'w'), indent=1)
