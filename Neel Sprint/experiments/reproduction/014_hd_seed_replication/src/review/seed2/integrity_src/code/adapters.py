import os, sys, json, hashlib
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import torch
torch.set_num_threads(8)
from safetensors.torch import load_file
OUT = sys.argv[1]
AD = '/workspace/Neel Sprint/adapters'
P = {'A_s0': f'{AD}/qwen36-27b_hd-A_s0_cosine', 'B_s0': f'{AD}/qwen36-27b_hd-B_s0_cosine',
     'A_s1': '/root/runs/A_s1', 'B_s1': '/root/runs/B_s1', 'A_s2': '/root/runs/A_s2', 'B_s2': '/root/runs/B_s2'}
SERVE = {'A_s0': 'new_A_s0_box2', 'B_s0': 'new_B_s0_box2', 'A_s1': 'new_A_s1', 'B_s1': 'new_B_s1', 'A_s2': 'new_A_s2', 'B_s2': 'new_B_s2'}
SCALE = 64 / 32
pre, new = "base_model.model.model.layers.", "base_model.model.model.language_model.layers."
res = {}
finals = {}
for run, root in P.items():
    for ck in ['step025', 'step062', 'step125', 'step188', 'final']:
        w = load_file(f'{root}/{ck}/adapter_model.safetensors')
        keys = sorted(w)
        dtypes = sorted({str(v.dtype) for v in w.values()})
        nonfinite = sum(int((~torch.isfinite(v.float())).sum()) for v in w.values())
        nA = sum(k.endswith('lora_A.weight') for k in keys); nB = sum(k.endswith('lora_B.weight') for k in keys)
        bad_prefix = sum(not k.startswith(pre) for k in keys)
        # per-module norms
        mods = sorted({k[:-len('.lora_A.weight')] for k in keys if k.endswith('lora_A.weight')})
        totA = totB = totBA = 0.0
        per_type = {}
        for m in mods:
            A = w[m + '.lora_A.weight'].float(); B = w[m + '.lora_B.weight'].float()
            a2 = float((A * A).sum()); b2 = float((B * B).sum())
            ba2 = float(torch.trace((A @ A.T) @ (B.T @ B))) * SCALE ** 2  # ||s * B A||_F^2
            totA += a2; totB += b2; totBA += ba2
            t = m.split('.')[-1]
            d = per_type.setdefault(t, [0, 0.0, 0.0, 0.0]); d[0] += 1; d[1] += a2; d[2] += b2; d[3] += ba2
        res[(run, ck)] = dict(n_tensors=len(keys), nA=nA, nB=nB, dtypes=dtypes, nonfinite=nonfinite, bad_prefix=bad_prefix,
                              normA=totA ** .5, normB=totB ** .5, normBA=totBA ** .5,
                              per_type={t: dict(n=v[0], A=v[1] ** .5, B=v[2] ** .5, BA=v[3] ** .5) for t, v in per_type.items()},
                              keys_sha=hashlib.sha256('\n'.join(keys).encode()).hexdigest()[:16])
        print(run, ck, {k: v for k, v in res[(run, ck)].items() if k != 'per_type'}, flush=True)
        if ck == 'final':
            finals[run] = w
            # serving check: bit-for-bit
            sv = load_file(f'/root/runs/lora_vllm/{SERVE[run]}/adapter_model.safetensors')
            mism = 0; missing = 0
            exp = {new + k[len(pre):]: v for k, v in w.items()}
            if set(exp) != set(sv): missing = len(set(exp) ^ set(sv))
            for k, v in exp.items():
                s = sv.get(k)
                if s is None or s.dtype != v.dtype or s.shape != v.shape or not torch.equal(s.view(torch.uint8) if s.dim() else s, v.view(torch.uint8) if v.dim() else v):
                    mism += 1
            res[(run, 'serve')] = dict(served=SERVE[run], n_served=len(sv), keyset_sym_diff=missing, tensor_mismatch=mism)
            print('SERVE', run, res[(run, 'serve')], flush=True)
        else:
            del w
# cosine of lora_A / lora_B / delta-W flattened across modules, between finals
runs = list(finals)
def flat_cos(w1, w2, suffix):
    num = n1 = n2 = 0.0
    for k in w1:
        if k.endswith(suffix):
            a = w1[k].float().flatten(); b = w2[k].float().flatten()
            num += float(a @ b); n1 += float(a @ a); n2 += float(b @ b)
    return num / (n1 * n2) ** .5
def dw_cos(w1, w2, mods):
    # <B1A1, B2A2>_F = trace(A1^T B1^T B2 A2) = trace((B1^T B2)(A2 A1^T))
    num = n1 = n2 = 0.0
    for m in mods:
        A1 = w1[m + '.lora_A.weight'].float(); B1 = w1[m + '.lora_B.weight'].float()
        A2 = w2[m + '.lora_A.weight'].float(); B2 = w2[m + '.lora_B.weight'].float()
        num += float(torch.trace((B1.T @ B2) @ (A2 @ A1.T)))
        n1 += float(torch.trace((A1 @ A1.T) @ (B1.T @ B1))); n2 += float(torch.trace((A2 @ A2.T) @ (B2.T @ B2)))
    return num / (n1 * n2) ** .5
mods_all = sorted({k[:-len('.lora_A.weight')] for k in finals['A_s0'] if k.endswith('lora_A.weight')})
mods_sub = mods_all  # all modules
cos = {}
for i, r1 in enumerate(runs):
    for r2 in runs[i + 1:]:
        cA = flat_cos(finals[r1], finals[r2], 'lora_A.weight'); cB = flat_cos(finals[r1], finals[r2], 'lora_B.weight')
        cW = dw_cos(finals[r1], finals[r2], mods_sub)
        cos[f'{r1}|{r2}'] = dict(lora_A=cA, lora_B=cB, deltaW=cW)
        print('COS', r1, r2, f'A {cA:+.4f}  B {cB:+.4f}  dW {cW:+.4f}', flush=True)
json.dump(dict(res={f'{a}|{b}': v for (a, b), v in res.items()}, cos=cos), open(OUT, 'w'), indent=1)
