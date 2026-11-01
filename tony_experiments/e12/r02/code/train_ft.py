"""E12 R02 Stage F phase 2 (LM not loaded): fine-tune R01's layer-42 BatchTopK SAE on the phase-1 shards with
saprmarks/dictionary_learning @ 60ec6bf5 (BatchTopKTrainer.update driven in our own loop; nnsight and wandb stubbed).
Settings (brief): k 64, dict 131,072, batch 4,096, one pass over the shards (random permutation, seed 0), lr 2e-5,
100 warm-up steps, linear decay to 0 over the last 20% (library schedule, decay_start = 0.8 * steps), auxk_alpha 1/32
(original config), threshold EMA (beta 0.999, original) continuing from the loaded threshold (threshold_start_step 0).
Steps are numbered from 1: the library's update(step=0) would reset b_dec to the batch's geometric median, overwriting
the loaded b_dec. Log every 50 steps: loss (l2, auxk), L0 (thresholded encode on the batch; batch-top-k L0 is 64 by
construction), dead fraction (library rule: >= 10M tokens without firing) and a 1M-token diagnostic, batch FVU."""
import hashlib, json, os, sys, threading, queue, time, types
sys.modules["nnsight"] = types.ModuleType("nnsight"); sys.modules["nnsight"].LanguageModel = object
sys.modules["wandb"] = types.ModuleType("wandb")
sys.path.insert(0, "/workspace/e12/r02/pydeps")
import torch
from dictionary_learning.trainers.batch_top_k import BatchTopKTrainer, BatchTopKSAE

R02 = "/workspace/e12/r02"; SCR = "/root/e12r02"
ORIG = "/workspace/e12/r01/sae/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0"
OUT = f"{R02}/sae_ft"; os.makedirs(OUT, exist_ok=True)
torch.backends.cuda.matmul.allow_tf32 = True; torch.backends.cudnn.allow_tf32 = True
LOG = open(f"{R02}/logs/stageF_train.jsonl", "a")


def log(**kw):
    kw["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    s = json.dumps(kw); LOG.write(s + "\n"); LOG.flush(); print(s, flush=True)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


class LoadedBatchTopKSAE(BatchTopKSAE):
    """BatchTopKSAE initialised from R01's ae.pt (state dict incl. the threshold and k buffers)."""
    def __init__(self, activation_dim, dict_size, k):
        super().__init__(activation_dim, dict_size, k)
        sd = torch.load(f"{ORIG}/ae.pt", map_location="cpu")
        self.load_state_dict(sd)


def ev_top64(ae, X, chunk=4096):
    """R01's chosen convention: relu then per-token top-64. X CPU [N, D]."""
    W_enc = ae.encoder.weight.T.float(); b_enc = ae.encoder.bias.float(); W_dec = ae.decoder.weight.T.float(); b_dec = ae.b_dec.float()
    err = 0.0
    for s in range(0, X.shape[0], chunk):
        x = X[s:s + chunk].cuda().float()
        pre = torch.relu((x - b_dec) @ W_enc + b_enc)
        tk = torch.topk(pre, 64, dim=-1)
        f = torch.zeros_like(pre).scatter_(-1, tk.indices, tk.values)
        err += float(((x - (f @ W_dec + b_dec)) ** 2).sum())
    Xf = X.float(); tot = float(((Xf - Xf.mean(0)) ** 2).sum())
    return 1 - err / tot


def main():
    t0 = time.time()
    shards = sorted(f for f in os.listdir(f"{SCR}/acts") if f.startswith("acts_") and f.endswith(".pt"))
    Xs, Ss = [], []
    for f in shards:
        d = torch.load(f"{SCR}/acts/{f}"); Xs.append(d["X"]); Ss.append(d["src"])
    X = torch.cat(Xs); S = torch.cat(Ss); del Xs, Ss
    N = X.shape[0]
    B = 4096; steps = N // B
    src_counts = {int(k): int(v) for k, v in zip(*torch.unique(S, return_counts=True))}
    log(event="loaded_shards", n_shards=len(shards), rows=N, steps=steps, src_counts=src_counts, secs=round(time.time() - t0))
    tr = BatchTopKTrainer(steps=steps, activation_dim=5120, dict_size=131072, k=64, layer=42, lm_name="Qwen/Qwen3.6-27B",
                          dict_class=LoadedBatchTopKSAE, lr=2e-5, auxk_alpha=1 / 32, warmup_steps=100, decay_start=int(0.8 * steps),
                          threshold_beta=0.999, threshold_start_step=0, seed=0, device="cuda",
                          wandb_name="BatchTopK-Qwen3.6-27B-resid_post_layer_42_trainer_0-E12R02-chatFT", submodule_name="resid_post_layer_42")
    # load check: R01's parent web EV (0.703 top-64) to 3 decimals
    W = torch.load(f"{SCR}/web42_parent.pt")["X"]
    with torch.no_grad():
        ev0 = ev_top64(tr.ae, W)
    thr0 = float(tr.ae.threshold)
    ok = round(ev0, 3) == 0.703
    log(event="load_check", web_ev_top64=ev0, rounds_to_0_703=ok, threshold=thr0, k=int(tr.ae.k))
    if not ok:
        raise SystemExit("load check failed")
    perm = torch.randperm(N, generator=torch.Generator().manual_seed(0))
    q = queue.Queue(maxsize=6)

    def feeder():
        for s in range(steps):
            idx = perm[s * B:(s + 1) * B]
            q.put(X[idx].pin_memory())
        q.put(None)
    th = threading.Thread(target=feeder, daemon=True); th.start()
    hist = []
    tl = time.time()
    for s in range(steps):
        xb = q.get().cuda(non_blocking=True).float()
        step = s + 1  # never 0 (see docstring)
        logit = s % 50 == 0 or s == steps - 1
        if logit:  # diagnostics before the update, without touching the trainer's state (no tr.loss call)
            with torch.no_grad():
                f_b = tr.ae.encode(xb, use_threshold=False)
                l2 = float(((xb - tr.ae.decode(f_b)) ** 2).sum(-1).mean())
                fvu = float(((xb - tr.ae.decode(f_b)) ** 2).sum() / ((xb - xb.mean(0)) ** 2).sum())
                f_thr = tr.ae.encode(xb, use_threshold=True)
                l0_thr = float((f_thr > 0).sum(-1).float().mean())
                fvu_thr = float(((xb - tr.ae.decode(f_thr)) ** 2).sum() / ((xb - xb.mean(0)) ** 2).sum())
                del f_b, f_thr
            lr_now = tr.optimizer.param_groups[0]["lr"]
        loss = tr.update(step, xb)
        if logit:
            row = dict(event="train", step=step, lr=lr_now, loss=loss, l2_loss=l2, auxk_pre_norm=float(tr.pre_norm_auxk_loss),
                       dead_frac_10M=float((tr.num_tokens_since_fired >= tr.dead_feature_threshold).float().mean()),
                       dead_frac_1M=float((tr.num_tokens_since_fired >= 1_000_000).float().mean()),
                       l0_threshold=l0_thr, l0_batchtopk=64, batch_fvu=fvu, batch_fvu_threshold=fvu_thr, threshold=float(tr.ae.threshold),
                       secs=round(time.time() - t0), step_s=round((time.time() - tl) / 50, 3))
            tl = time.time(); hist.append(row); log(**row)
    th.join()
    with torch.no_grad():
        ev1 = ev_top64(tr.ae, W)
    log(event="after_train_web_ev_top64", ev=ev1, threshold=float(tr.ae.threshold))
    sd = {k: v.detach().cpu() for k, v in tr.ae.state_dict().items()}
    torch.save(sd, f"{OUT}/ae.pt")
    cfg = json.load(open(f"{ORIG}/config.json"))
    cfg["trainer"] = dict(tr.config, lr=2e-5, init_from="ceselder/qwen36-27b-sae-l42-1b trainer_0 ae.pt (sha256 be5990c2...)")
    cfg["buffer"] = dict(d_submodule=5120, io="out", out_batch_size=B, total_tokens=int(N), n_shards=len(shards),
                         act_dir=f"{SCR}/acts", note="E12 R02 phase 1: parent, block 42; chat 60% (+3 header copies), story 25%, web 15%")
    json.dump(cfg, open(f"{OUT}/config.json", "w"), indent=4)
    hs = {f: sha(f"{OUT}/{f}") for f in ("ae.pt", "config.json")}
    json.dump(hs, open(f"{OUT}/sha256.json", "w"), indent=1)
    json.dump(dict(steps=steps, rows=N, src_counts=src_counts, load_check_ev=ev0, after_ev=ev1, threshold_start=thr0,
                   threshold_end=float(tr.ae.threshold), log=hist, sha256=hs, secs=round(time.time() - t0)),
              open(f"{R02}/results/stageF_train_summary.json", "w"), indent=1)
    log(event="train_done", sha256=hs, secs=round(time.time() - t0))


if __name__ == "__main__":
    main()
