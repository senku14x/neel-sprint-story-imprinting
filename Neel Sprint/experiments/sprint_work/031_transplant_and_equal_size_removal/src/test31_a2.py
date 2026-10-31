"""sw031 A2 CPU tests (D26): keys / manifest, donor rule, group ops through Hooks31 on synthetic blocks (transplant exact, band-2
pre-band untouched), and the subset-vs-full completion marker.  python3 test31_a2.py [--tmp DIR] -> ALL_PASS"""
import json, math, os, sys, tempfile
import torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common31 as C31
import gen31 as G
import gen31_a2 as A2
from hooks31 import Hooks31
G.DEV = "cpu"; FAILS = []
TMP = sys.argv[2] if len(sys.argv) > 2 else tempfile.mkdtemp(prefix="t31a2_")
def chk(n, c, d=""):
    print(("PASS " if c else "FAIL ") + n + (f"  [{d}]" if d else "")); (None if c else FAILS.append(n))
SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"
SIDS = sorted({json.loads(l)["sid"] for l in open(f"{SW8}/contexts.jsonl")})
K = A2.expected_keys_A2(C31.MODELS, SIDS, 2)
allk = set(K) | set(C31.expected_keys("A", "free", C31.MODELS, SIDS, 2)) | set(C31.expected_keys("B", "free", C31.MODELS, SIDS, 2))
chk("A2 manifest 2,560 unique keys, disjoint from A / B", len(K) == len(set(K)) == 2560 and len(allk) == 2560 + 4608 + 2560)
chk("A2 donor rule", A2.donor_A2("par_opp", "hdA0", "UH", SIDS[0]) == ("parent", "SH", SIDS[0]) and A2.donor_A2("par_same", "hdB0", "SH", SIDS[0]) == ("parent", "SH", SIDS[0]))
torch.manual_seed(0); H = 16
class Blk(torch.nn.Module):
    def __init__(s): super().__init__(); s.W = torch.nn.Parameter(torch.randn(H, H) * 0.3 / math.sqrt(H), requires_grad=False)
    def forward(s, x):
        prev = torch.cat([torch.zeros_like(x[:, :1]), x[:, :-1]], 1); return (0.8 * x + torch.tanh(x @ s.W) + 0.2 * prev,)
blocks = torch.nn.ModuleList([Blk() for _ in range(64)])
st = {(m, c, s): torch.randn(7, 48, H) for m in ("parent",) for c in ("UH", "SH") for s in SIDS[:2]}
ops = A2.group_ops_A2("hdA0", "UH", SIDS[0], st, 1)
chk("A2 group: 5 cells, none first, par donors = parent captures", [o["cell"] for o in ops] == ["none", "par_opp@L16-31", "par_same@L16-31", "par_opp@L32-63", "par_same@L32-63"]
    and all(o["Dsrc"] is st[A2.donor_A2(o["arm"], "hdA0", "UH", SIDS[0])] for o in ops if o["kind"] == "full"))
P = 12; X = torch.randn(1, P, H).repeat(len(ops), 1, 1)
G.set_pos(ops, P, 0); G.materialize(ops)
hk = Hooks31(blocks, C31.LOG15); hk.ops = ops; hk.mode = "patch"; hk.min_len = P; hk.keep = {16, 31, 32, 63}
x = X
for b in blocks: x = b(x)[0]
cap = hk.cap; ex = pre = 0.0
for r, o in enumerate(ops):
    if o["kind"] == "full":
        b0, b1 = C31.BAND_ENDS[o["band"]]
        ex = max(ex, max(float((cap[L][r] - o["Dfull"][:, L - 16]).abs().max()) for L in (b0, b1)))
        if o["band"] == "L32-63": pre = max(pre, max(float((cap[L][r] - cap[L][0]).abs().max()) for L in (16, 31)))
chk("A2 transplant exact at band ends; band-2 pre-band untouched", ex == 0.0 and pre == 0.0, f"{ex} {pre}")
rd = f"{TMP}/A2_free"; os.makedirs(rd, exist_ok=True)
for m in C31.MODELS:
    with open(f"{rd}/rows_{m}.jsonl", "w") as f:
        for k in A2.expected_keys_A2([m], SIDS[:4], 2): f.write(json.dumps(dict(key=k)) + "\n")
A2.done_marker(rd, list(C31.MODELS), SIDS[:4], SIDS, 2, TMP)
chk("A2 subset run writes SUBSET_DONE, never GPU_DONE", os.path.exists(f"{TMP}/SUBSET_DONE_A2_free_n4") and not os.path.exists(f"{TMP}/GPU_DONE_A2_free"))
print("ALL_PASS" if not FAILS else f"FAILED {FAILS}"); sys.exit(0 if not FAILS else 1)
