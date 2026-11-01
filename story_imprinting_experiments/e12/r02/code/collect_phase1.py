"""E12 R02 Stage F phase 1: the parent's block-42 states (output of model.model.layers[42]) on phase1_units.pt, written as bf16
shards to /root/e12r02/acts/. Every position except each sequence's first; positions whose norm exceeds 10x the batch
median are dropped (R01's outlier rule, applied per forward batch); every kept header-token state (u['hdr']) is written
3 more times. Each shard holds whole forward batches; a restart resumes after the last written shard.
Shard i: acts_{i:03d}.pt = dict(X=[N, 5120] bf16, src=[N] int8 (0 chat, 1 chat header extra copy, 2 story, 3 web),
first_batch, last_batch)."""
import json, os, sys, threading, queue, time
sys.path.insert(0, "/workspace/e12/r02/code")
from r02gpu import *  # noqa
import torch

OUTD = f"{SCR}/acts"; os.makedirs(OUTD, exist_ok=True)
SHARD = 1 << 18
open_log("phase1")
units = torch.load(f"{SCR}/data/phase1_units.pt")
E = Eng(adapters=("V",))  # parent = adapter disabled
SRC = {"chat": 0, "story": 2, "web": 3}
bts = E.batches(units, budget=24000, maxb=32)
done = sorted(f for f in os.listdir(OUTD) if f.startswith("acts_") and f.endswith(".pt"))
start_b, shard_i = 0, 0
if done:
    meta = json.load(open(f"{OUTD}/meta.json"))
    start_b = meta["last_batch"] + 1; shard_i = meta["next_shard"]
log(event="phase1_start", n_units=len(units), n_batches=len(bts), start_batch=start_b, shard_i=shard_i)
wq = queue.Queue(maxsize=2)


def writer():
    while True:
        it = wq.get()
        if it is None:
            break
        i, X, S, b0, b1 = it
        torch.save(dict(X=X, src=S, first_batch=b0, last_batch=b1), f"{OUTD}/acts_{i:03d}.pt.tmp")
        os.replace(f"{OUTD}/acts_{i:03d}.pt.tmp", f"{OUTD}/acts_{i:03d}.pt")
        json.dump(dict(last_batch=b1, next_shard=i + 1, t=time.strftime("%H:%M:%S")), open(f"{OUTD}/meta.json", "w"))
        wq.task_done()


th = threading.Thread(target=writer, daemon=True); th.start()
bufX, bufS, nbuf, b0 = [], [], 0, start_b
stats = dict(tokens_in=0, rows=0, outliers=0, header_extra=0, by_src={})
t0 = time.time(); last = t0
with E.use("parent"):
    for bi in range(start_b, len(bts)):
        bt = bts[bi]
        seqs = [units[i]["ids"] for i in bt]
        x, am, pos, L = E._left(seqs)
        fb, ft, src, ishdr = [], [], [], []
        for j, i in enumerate(bt):
            u = units[i]; off = L - len(u["ids"]); n = len(u["ids"])
            hs = set(u["hdr"])
            fb += [j] * (n - 1); ft += [p + off for p in range(1, n)]
            src += [SRC[u["src"]]] * (n - 1); ishdr += [p in hs for p in range(1, n)]
        fbt = torch.tensor(fb, device="cuda"); ftt = torch.tensor(ft, device="cuda")
        E.rec = dict(blocks={42}, fb=fbt, ft=ftt, out={}, lora=False, stop_after=42)
        try:
            E.inner.model(input_ids=x, attention_mask=am, position_ids=pos, use_cache=False)
        except StopForward:
            pass
        X = E.rec["out"][42]; E.rec = None
        nrm = X.norm(dim=-1); keep = nrm <= 10 * nrm.median()
        srct = torch.tensor(src, device="cuda", dtype=torch.int8); hdt = torch.tensor(ishdr, device="cuda")
        Xk = X[keep].to(torch.bfloat16); Sk = srct[keep]
        Xh = X[keep & hdt].to(torch.bfloat16)
        parts = [Xk] + [Xh] * 3; sparts = [Sk] + [torch.ones(Xh.shape[0], dtype=torch.int8, device="cuda")] * 3
        Xc = torch.cat(parts).cpu(); Sc = torch.cat(sparts).cpu()
        bufX.append(Xc); bufS.append(Sc); nbuf += Xc.shape[0]
        stats["tokens_in"] += len(fb); stats["rows"] += Xc.shape[0]; stats["outliers"] += int((~keep).sum()); stats["header_extra"] += 3 * Xh.shape[0]
        for k, v in zip(*torch.unique(Sc, return_counts=True)):
            stats["by_src"][int(k)] = stats["by_src"].get(int(k), 0) + int(v)
        del X, Xk, Xh
        if nbuf >= SHARD or bi == len(bts) - 1:
            wq.put((shard_i, torch.cat(bufX), torch.cat(bufS), b0, bi))
            shard_i += 1; bufX, bufS, nbuf, b0 = [], [], 0, bi + 1
        if time.time() - last > 60:
            last = time.time()
            log(event="phase1_progress", batch=bi, of=len(bts), shards=shard_i, tok_s=round(stats["tokens_in"] / (time.time() - t0)), **{k: v for k, v in stats.items() if k != "by_src"})
wq.put(None); th.join()
stats["secs"] = round(time.time() - t0)
json.dump(stats, open(f"{R02}/results/stageF_phase1_stats_part{start_b}.json", "w"), indent=1)
log(event="phase1_done", **stats)
open(f"{OUTD}/phase1.done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
