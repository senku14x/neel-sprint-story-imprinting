"""Review test (b): train.lr_factor vs a hand-computed reference, and vs what LambdaLR actually applies.
Spec: linear warmup over 10 steps, then cosine to 0 over 250 steps (total). step0 = optimizer steps already taken.
Hand reference (written independently of the code):
  warmup: lr at the k-th optimizer step (k = 1..10) = k/10 * peak  ->  step0 = k-1
  cosine: progress p = (k - 10) / (250 - 10) for k = 11..250; factor = 0.5 (1 + cos(pi p)); k=250 -> 0
Run: CUDA_VISIBLE_DEVICES="" /root/venvs/si/bin/python test_b_lr.py
"""
import math, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch  # noqa: E402

import train  # noqa: E402

W, T = 10, 250


def ref(step0):
    k = step0 + 1  # 1-based index of the optimizer step this lr is used for
    if k <= W:
        return k / W
    return 0.5 * (1 + math.cos(math.pi * (k - W) / (T - W)))


ok = True
for s in [0, 9, 10, 125, 249]:
    got, want = train.lr_factor(s, W, T), ref(s)
    print(f"step0={s:3d}  lr_factor={got:.6f}  reference={want:.6f}")
    ok &= abs(got - want) < 1e-12
# full sweep
mx = max(abs(train.lr_factor(s, W, T) - ref(s)) for s in range(T))
print("max |diff| over all 250 steps:", mx)
ok &= mx < 1e-12
# What LambdaLR applies at each optimizer step (train.py reads opt.param_groups[0]['lr'] before opt.step())
p = torch.nn.Parameter(torch.zeros(1))
opt = torch.optim.AdamW([p], lr=5e-4)
sch = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: train.lr_factor(s, W, T))
used = []
for step in range(T):
    used.append(opt.param_groups[0]["lr"])
    opt.step(); sch.step()
print("lr used at steps 1,10,11,126,250:", [round(used[i], 9) for i in [0, 9, 10, 125, 249]])
ok &= abs(used[0] - 5e-5) < 1e-15 and abs(used[9] - 5e-4) < 1e-15 and used[249] == 0.0
ok &= all(abs(used[i] - 5e-4 * ref(i)) < 1e-15 for i in range(T))
# monotone: increasing in warmup, non-increasing after
ok &= all(used[i] < used[i + 1] for i in range(W - 1)) and all(used[i] >= used[i + 1] for i in range(W - 1, T - 1))
print("PASS" if ok else "FAIL")
