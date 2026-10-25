import json, math, sys
import numpy as np
S=sys.argv[1]
runs={'A_s0':f'{S}/train/A_s0_train_log.jsonl','B_s0':f'{S}/train/B_s0_train_log.jsonl'}
for r in ['A_s1','B_s1','A_s2','B_s2']: runs[r]=f'{S}/train/{r}/train_log.jsonl'
def lr_ref(step, base=5e-4, warm=10, total=250):
    s=step-1  # scheduler step index before optimizer step
    if s < warm: return base*(s+1)/warm
    return None
out={}
for r,p in runs.items():
    L=[json.loads(l) for l in open(p)]
    steps=[x['step'] for x in L]; assert steps==list(range(1,251)), r
    loss=np.array([x['loss'] for x in L]); gn=np.array([x['grad_norm'] for x in L]); lr=np.array([x['lr'] for x in L])
    el=np.array([x['elapsed'] for x in L]); tok=np.array([x['tokens'] for x in L])
    dt=np.diff(np.concatenate([[0],el]))
    blocks=[loss[i:i+50].mean() for i in range(0,250,50)]
    # token-weighted mean loss over all
    wl=(loss*tok).sum()/tok.sum()
    out[r]=dict(lr=lr, loss=loss, tok=tok)
    print(f"{r}: blocks50 {' '.join(f'{b:.4f}' for b in blocks)} | first {loss[0]:.4f} last10 {loss[-10:].mean():.4f} tokw {wl:.4f} | tok_sum {tok.sum()} | gn med {np.median(gn):.3f} max {gn.max():.3f}@{gn.argmax()+1} n>0.5 {(gn>0.5).sum()} n>0.3(after 10) {(gn[10:]>0.3).sum()} | dt med {np.median(dt[1:]):.1f}s max {dt[1:].max():.1f}s total {el[-1]:.0f}s | peak {max(x['peak_gb'] for x in L)} | nan {np.isnan(loss).sum()+np.isnan(gn).sum()}")
# LR curve identical across runs?
ref=out['A_s0']['lr']
for r in out: print(r,'lr maxabsdiff vs A_s0', float(np.abs(out[r]['lr']-ref).max()), 'lr[0..2]',out[r]['lr'][:3], 'lr[9]',out[r]['lr'][9],'lr[-1]',out[r]['lr'][-1])
# analytic cosine check (HF get_cosine_schedule_with_warmup): lr at optimizer step k (1-based) logged after scheduler? check
def hf(k, base=5e-4, warm=10, total=250):
    # value used at step k (0-based scheduler count k-1)
    s=k-1
    if s<warm: return base*(s+1)/warm  # guess
    prog=(s+1-warm)/(total-warm)
    return base*0.5*(1+math.cos(math.pi*prog))
a=np.array([hf(k) for k in range(1,251)]); print('analytic(guess) maxabs vs A_s2', float(np.abs(a-out['A_s2']['lr']).max()))
# same tokens per step for A_s2 vs B_s2 (same order, different files)? and per-step tokens vs s1
for a_,b_ in [('A_s2','B_s2'),('A_s1','B_s1'),('A_s0','B_s0'),('A_s2','A_s1')]:
    print(a_,b_,'tokens corr', np.corrcoef(out[a_]['tok'],out[b_]['tok'])[0,1].round(3), 'loss corr', np.corrcoef(out[a_]['loss'],out[b_]['loss'])[0,1].round(3))
