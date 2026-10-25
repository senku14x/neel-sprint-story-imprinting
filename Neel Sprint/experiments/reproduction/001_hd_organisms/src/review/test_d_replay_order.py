"""Review test (d): with --replay, the story order is identical to the order without replay.
Behavioural: runs train.main() in-process with --dry (tokenizer only, no model) twice on a 200-row slice of the real
story file, without and with a 50-row synthetic replay file, capturing the list passed to the module-level
random.shuffle (the story order). Compares: full captured orders, train_meta first_order_idx, golden_render story idx,
and the pure reference `random.seed(0); order=list(range(N)); random.shuffle(order)`.
Also execs train.py's replay-order block (extracted verbatim) to check rep_order = concatenated permutations, length
n_steps * round(eff_bs*ratio), and that it does not touch the global random state.
Run: CUDA_VISIBLE_DEVICES="" /root/venvs/si/bin/python test_d_replay_order.py <scratch_dir>
"""
import json, os, random, sys, textwrap

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SRC)
import train  # noqa: E402

scratch = sys.argv[1]
os.makedirs(scratch, exist_ok=True)
DATA = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
story_f, rep_f = f"{scratch}/stories200.jsonl", f"{scratch}/replay50.jsonl"
with open(story_f, "w") as f:
    for i, l in enumerate(open(DATA)):
        if i == 200:
            break
        f.write(l)
with open(rep_f, "w") as f:
    for i in range(50):
        f.write(json.dumps({"messages": [{"role": "user", "content": f"Question number {i}?"},
                                         {"role": "assistant", "content": f"Answer {i}. " * (1 + i % 7)}]}) + "\n")

captured = []
_orig = random.shuffle


def rec_shuffle(x, *a, **k):
    _orig(x, *a, **k)
    captured.append(list(x))


def run(extra, out):
    captured.clear()
    random.shuffle = rec_shuffle
    sys.argv = ["train.py", "--data", story_f, "--out", out, "--seed", "0", "--dry"] + extra
    try:
        train.main()
    finally:
        random.shuffle = _orig
    assert len(captured) == 1, f"expected exactly one module-level random.shuffle call, got {len(captured)}"
    meta = json.load(open(f"{out}/train_meta.json"))
    gold = [json.loads(l) for l in open(f"{out}/golden_render.jsonl")]
    return captured[0], meta, gold


o0, m0, g0 = run([], f"{scratch}/dry_noreplay")
o1, m1, g1 = run(["--replay", rep_f, "--replay_ratio", "1.0"], f"{scratch}/dry_replay")
o2, m2, g2 = run(["--replay", rep_f, "--replay_ratio", "0.5"], f"{scratch}/dry_replay05")
random.seed(0); ref = list(range(200)); random.shuffle(ref)
res = dict(
    full_order_equal_noreplay_vs_replay=o0 == o1, full_order_equal_noreplay_vs_replay05=o0 == o2,
    equals_pure_reference=o0 == ref, first_order_idx=(m0["first_order_idx"], m1["first_order_idx"]),
    golden_story_idx=([g["idx"] for g in g0[:3]], [g["idx"] for g in g1[:3]]),
    replay_per_step=(m1["replay_per_step"], m2["replay_per_step"]), steps=(m0["steps"], m1["steps"]),
    n_golden_rows=(len(g0), len(g1)))

# replay-order block, verbatim from train.py
src = open(f"{SRC}/train.py").read()
a = src.index("        n_rep_per_step = round(args.eff_bs * args.replay_ratio)")
b = src.index("        rep_order = rep_order[:need]")
b = src.index("\n", b) + 1
block = textwrap.dedent(src[a:b])
from types import SimpleNamespace  # noqa: E402
random.seed(123); before = random.getstate()
ns = dict(args=SimpleNamespace(eff_bs=32, replay_ratio=1.0, seed=0), random=random, rep_enc=list(range(50)), n_steps=7)
exec(block, ns)
ro = ns["rep_order"]
perm_ok = all(sorted(ro[i:i + 50]) == list(range(50)) for i in range(0, len(ro) - len(ro) % 50, 50))
res.update(rep_order_len=len(ro), rep_order_expected=7 * 32, rep_order_blocks_are_permutations=perm_ok,
           global_random_state_untouched=random.getstate() == before)
print(json.dumps(res, indent=1))
ok = (res["full_order_equal_noreplay_vs_replay"] and res["full_order_equal_noreplay_vs_replay05"]
      and res["equals_pure_reference"] and m0["first_order_idx"] == m1["first_order_idx"] == ref[:8]
      and [g["idx"] for g in g0[:3]] == [g["idx"] for g in g1[:3]] and len(ro) == 224 and perm_ok
      and res["global_random_state_untouched"] and m1["replay_per_step"] == 32 and m2["replay_per_step"] == 16)
print("PASS" if ok else "FAIL")
