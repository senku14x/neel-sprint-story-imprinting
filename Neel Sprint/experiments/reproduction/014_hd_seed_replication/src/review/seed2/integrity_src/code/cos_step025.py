import os, sys
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import torch
torch.set_num_threads(8)
from safetensors.torch import load_file
AD = '/workspace/Neel Sprint/adapters'
P = {'A_s0': f'{AD}/qwen36-27b_hd-A_s0_cosine', 'B_s0': f'{AD}/qwen36-27b_hd-B_s0_cosine',
     'A_s1': '/root/runs/A_s1', 'B_s1': '/root/runs/B_s1', 'A_s2': '/root/runs/A_s2', 'B_s2': '/root/runs/B_s2'}
ck = sys.argv[1]
W = {r: {k: v for k, v in load_file(f'{p}/{ck}/adapter_model.safetensors').items() if k.endswith('lora_A.weight')} for r, p in P.items()}
runs = list(W)
for i, a in enumerate(runs):
    for b in runs[i + 1:]:
        num = n1 = n2 = 0.0
        for k in W[a]:
            x = W[a][k].flatten(); y = W[b][k].flatten()
            num += float(x @ y); n1 += float(x @ x); n2 += float(y @ y)
        print(f'{ck} lora_A cos {a} {b}: {num / (n1 * n2) ** .5:+.4f}', flush=True)
