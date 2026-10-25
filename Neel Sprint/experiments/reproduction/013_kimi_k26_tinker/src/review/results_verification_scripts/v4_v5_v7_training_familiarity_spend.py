"""Items 4 (training record + golden render), 5 (familiarity recompute) and 7 (spend trace) of the 013 results verification.
Written from scratch by the verifier (25 Oct); no import of experiment code.

/root/venvs/tinker/bin/python v4_v5_v7_training_familiarity_spend.py > v4_v5_v7.out
"""
import collections, json, math

import numpy as np

SRC = "/workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src"
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def jl(p):
    return [json.loads(l) for l in open(f"{SRC}/{p}")]


print("=== ITEM 4: training record ===")
log = jl("runs/B_s0/log.jsonl")
meta = json.load(open(f"{SRC}/runs/B_s0/meta.json"))
ck = json.load(open(f"{SRC}/runs/B_s0/checkpoints.json"))
steps = [r["step"] for r in log]
check("250 log rows, steps 1..250 contiguous, no duplicates", steps == list(range(1, 251)), f"n={len(steps)}")
check("meta: steps 250, bs 32, lr 5e-4, warmup 10, rank 32, seed 0, asg B, unembed off",
      (meta["steps"], meta["bs"], meta["lr"], meta["warmup"], meta["rank"], meta["seed"], meta["asg"], meta["train_unembed"]) == (250, 32, 5e-4, 10, 32, 0, "B", False))
check("meta data sha256 = design B hash 3ed67422...aa95377", meta["data_sha256"].startswith("3ed67422") and meta["data_sha256"].endswith("aa95377"))
nsup = sum(r["n_sup"] for r in log); ntok = sum(r["n_tok"] for r in log)
check("sum n_sup = 5,543,761", int(nsup) == 5543761, f"got {int(nsup):,}")
print(f"   sum n_tok = {ntok:,} (golden total_tokens 5,713,858); masked = {ntok - int(nsup):,} = {(ntok - nsup) / 8000:.2f} per row over 8000 rows")


def lr_expected(s, base=5e-4, warm=10, total=250):
    if s <= warm:
        return base * s / warm
    return base * 0.5 * (1 + math.cos(math.pi * (s - warm) / (total - warm)))


d = max(abs(r["lr"] - lr_expected(r["step"])) for r in log)
check("lr = linear warmup over 10 steps (5e-5..5e-4) then cosine to 0 at step 250", d < 1e-12, f"max |lr - expected| = {d:.2e}; lr[1]={log[0]['lr']:.2e} lr[10]={log[9]['lr']:.2e} lr[11]={log[10]['lr']:.3e} lr[250]={log[-1]['lr']}")
dn = max(abs(r["loss"] - r["nll_check"]) for r in log)
print(f"   max |loss - nll_check| over steps = {dn:.2e}")
L = np.array([r["loss"] for r in log])
bins = [(a, b) for a, b in [(1, 10), (11, 25), (26, 50), (51, 75), (76, 100), (101, 125), (126, 150), (151, 175), (176, 200), (201, 225), (226, 250)]]
print("   loss by step bin: " + "; ".join(f"{a}-{b}: {L[a - 1:b].mean():.3f}" for a, b in bins))
print(f"   loss step1 {L[0]:.3f}, min {L.min():.3f} at step {int(L.argmin()) + 1}, last-10 mean {L[-10:].mean():.3f}, max {L.max():.3f} at step {int(L.argmax()) + 1}")
nonfinite = int((~np.isfinite(L)).sum())
check("loss finite and decreasing (first-10 mean > last-10 mean)", nonfinite == 0 and L[:10].mean() > L[-10:].mean(), f"first10 {L[:10].mean():.3f} -> last10 {L[-10:].mean():.3f}")
g = np.array([r["optim"]["unclipped_grad_l2:mean"] for r in log])
print(f"   unclipped grad L2: step1 {g[0]:.3f}, max {g.max():.3f} at step {int(g.argmax()) + 1}, last {g[-1]:.3f}; steps with grad > 1.0 (clip active): {int((g > 1).sum())}")
samp = sorted(c["step"] for c in ck if c["kind"] == "sampler"); st = sorted(c["step"] for c in ck if c["kind"] == "state")
check("sampler checkpoints at 62/125/250, states at 62/125/188/250 (final flagged)", samp == [62, 125, 250] and st == [62, 125, 188, 250]
      and all(c.get("final") for c in ck if c["step"] == 250), f"sampler {samp} state {st}")
check("meta.checkpoints == checkpoints.json", meta["checkpoints"] == ck)
check("all checkpoint paths under the run's training_run_id", all(meta["training_run_id"] in c["path"] for c in ck))
usd_log = sum(r["usd"] for r in log)
print(f"   training cost in log.jsonl: ${usd_log:.2f}; wall {(meta['finished'] - meta['started']) / 3600:.2f} h")

gold = json.load(open(f"{SRC}/golden/golden_render.json"))
for asg in ["A", "B"]:
    f = gold["files"][asg]
    check(f"golden render {asg}: 8000 rows, 0 token mismatches, 0 mask failures",
          f["rows"] == 8000 and f["token_mismatch_vs_official"] == 0 and not f["mismatch_rows"] and f["mask_failures"] == 0 and not f["mask_fail_rows"],
          f"rows={f['rows']} mism={f['token_mismatch_vs_official']} maskfail={f['mask_failures']} sup={f['supervised_tokens']:,}")
check("golden B supervised tokens == sum n_sup in training log", gold["files"]["B"]["supervised_tokens"] == int(nsup))
check("golden B total tokens == sum n_tok in training log", gold["files"]["B"]["total_tokens"] == ntok, f"{gold['files']['B']['total_tokens']:,} vs {ntok:,}")
check("seed-0 order head agrees (golden seed0_first3 vs meta order_head)", gold["files"]["B"]["seed0_first3"] == meta["order_head"][:3])
other = {k: v for k, v in gold.items() if k != "files"}
print(f"   golden_render.json other keys: { {k: (v if not isinstance(v, (list, dict)) else type(v).__name__ + str(len(v))) for k, v in other.items()} }")
glog = open(f"{SRC}/golden/golden_render.log").read()
print("   golden_render.log tail:", " | ".join(l for l in glog.strip().splitlines()[-3:]))

print("\n=== ITEM 5: familiarity (token-weighted recompute from per_item.jsonl) ===")
P = jl("familiarity/per_item.jsonl")
S = json.load(open(f"{SRC}/familiarity/summary.json"))
by = collections.defaultdict(list)
for r in P:
    by[r["set"]].append(r)
print("   items per set:", {k: len(v) for k, v in by.items()})
bad = [r["id"] for r in P if r["n_narration"] + r["n_dialogue"] + r["n_habit"] != r["n"]]
print(f"   items where narration+dialogue+habit tokens != n: {len(bad)}")


def pool(rows):
    n = sum(r["n"] for r in rows)
    return n, sum(r["out20"] * r["n"] for r in rows) / n, sum(r["nll"] * r["n"] for r in rows) / n


for s in ["story_A", "story_B", "own_chat", "qwen_chat"]:
    n, o, nl = pool(by[s])
    c = S["sets"][s]
    check(f"{s}: tokens / out20 / NLL match summary", n == c["tokens"] and abs(o - c["out20_share"]) < 1e-9 and abs(nl - c["nll_per_token"]) < 1e-9,
          f"mine n={n} out20={o:.4%} nll={nl:.3f} | claimed n={c['tokens']} out20={c['out20_share']:.4%} nll={c['nll_per_token']:.3f}")
story = by["story_A"] + by["story_B"]
n, o, nl = pool(story)
check("pooled stories (A+B, 600 items): out-of-top-20 share 15.0%, NLL 2.58", round(o * 100, 1) == 15.0 and round(nl, 2) == 2.58,
      f"mine: {len(story)} items, {n:,} tokens, out20 {o:.4%}, NLL {nl:.4f}")
rng = np.random.default_rng(5)
nn = np.array([r["n"] for r in story], float); oo = np.array([r["out20"] * r["n"] for r in story])
B = rng.multinomial(len(story), np.full(len(story), 1 / len(story)), size=5000)
bs = (B @ oo) / (B @ nn)
print(f"   item-bootstrap 95% CI of pooled out20 (5000 draws): [{np.percentile(bs, 2.5):.2%}, {np.percentile(bs, 97.5):.2%}] (design spec: [14.8, 15.2])")
for part in ["narration", "dialogue", "habit"]:
    tn = sum(r[f"n_{part}"] for r in story); to = sum(r[f"out20_sum_{part}"] for r in story); tl = sum(r[f"nll_sum_{part}"] for r in story)
    print(f"   pooled {part}: {tn:,} tokens, out20 {to / tn:.2%}, NLL {tl / tn:.3f}")
types = collections.defaultdict(list)
for r in story:
    types[r["stype"]].append(r)
tt = {k: pool(v)[1] for k, v in types.items()}
print("   by story type (pooled A+B): " + ", ".join(f"{k} {v:.1%}" for k, v in sorted(tt.items())))
tt2 = {f"{r['set']}|{r['stype']}": None for r in story}
per = {}
for k in tt2:
    s_, t_ = k.split("|")
    per[k] = pool([r for r in story if r["set"] == s_ and r["stype"] == t_])[1]
print(f"   by set x story type: min {min(per.values()):.1%}, max {max(per.values()):.1%} (design spec: 13.9-16.1%)")

print("\n=== ITEM 7: spend trace ===")
T = jl("tinker_ledger_013.jsonl")
bt = collections.defaultdict(float); bk = collections.defaultdict(float)
for r in T:
    bt[r["tag"]] += r["usd"]; bk[r["kind"]] += r["usd"]
for k, v in sorted(bt.items(), key=lambda x: -x[1]):
    print(f"   tinker {k:28s} ${v:8.3f}")
print(f"   tinker by kind: { {k: round(v, 3) for k, v in bk.items()} }")
tot = sum(bt.values())
print(f"   TINKER TOTAL (estimated at list prices) ${tot:.2f} over {len(T)} ledger rows; 013 cap $65 -> {'OVER' if tot > 65 else 'under'} by ${abs(tot - 65):.2f}")
trow = [r for r in T if r["kind"] == "train" and r["tag"] not in ("smoke_heldout",)]
print(f"   training-tag ledger rows sum (kind=train): ${sum(r['usd'] for r in T if r['kind'] == 'train'):.2f}; log.jsonl usd ${usd_log:.2f}")
A = jl("api_ledger_013.jsonl")
bm = collections.defaultdict(lambda: [0.0, 0, 0, 0])
for r in A:
    x = bm[r["model"]]; x[0] += r.get("cost") or 0; x[1] += 1; x[2] += r.get("in", 0) or 0; x[3] += r.get("out", 0) or 0
for k, v in sorted(bm.items(), key=lambda x: -x[1][0]):
    print(f"   openrouter {k:38s} ${v[0]:7.3f}  calls {v[1]:5d}  in {v[2]:,} out {v[3]:,}")
atot = sum(v[0] for v in bm.values())
print(f"   OPENROUTER TOTAL ${atot:.3f} over {len(A)} rows (cap $10); rows with cost None/0: {sum(1 for r in A if not r.get('cost'))}")
tags = collections.Counter(r["tag"] for r in A)
print(f"   openrouter tags: {dict(tags)}")
print("\nALL CHECKS PASS" if ok_all else "\nSOME CHECKS FAILED")
