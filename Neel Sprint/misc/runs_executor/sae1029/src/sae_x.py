"""sae1029 SAE loader (executor-8, 29 Oct 2026). ceselder/qwen36-27b-sae-l42-1b, loaded with dictionary_learning's OWN
BatchTopKSAE class (github.com/saprmarks/dictionary_learning @ 60ec6bf, cloned to /root/dl/dictionary_learning). The
package __init__ imports nnsight (not installed, not needed), so a stub package object exposes the submodules without
running that __init__. Inference = the class's forward: encode(use_threshold=True) = ReLU(W_enc(x - b_dec) + b_enc) kept
where > threshold (learned, 1.5846), decode = W_dec f + b_dec. Hook (README + config): output of model.model.layers[42]
(resid_post), raw activations (no normalisation in the config); confirmed empirically in part1 (hook check)."""
import sys, types

import torch

REPO = "/root/dl/dictionary_learning"
AE = "/root/dl/sae_l42/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/ae.pt"
LAYER = 42


def load_sae(device="cuda", dtype=torch.float32):
    if "dictionary_learning" not in sys.modules:
        pkg = types.ModuleType("dictionary_learning"); pkg.__path__ = [f"{REPO}/dictionary_learning"]
        sys.modules["dictionary_learning"] = pkg
    from dictionary_learning.trainers.batch_top_k import BatchTopKSAE
    sae = BatchTopKSAE.from_pretrained(AE, device=device)
    sae = sae.to(dtype).eval()
    for p in sae.parameters():
        p.requires_grad_(False)
    return sae


@torch.no_grad()
def recon(sae, x, chunk=4096, codes=True):
    """x [..., 5120] (any dtype) -> (x_hat fp32, codes fp32 or None) through the library's forward, batch-flattened and
    chunked (131k latents x 4096 rows x 4 bytes = 2 GB per chunk; extract1028's 51k-token hook check OOMed unchunked)."""
    shp = x.shape
    xf = x.reshape(-1, shp[-1]).to(sae.b_dec.dtype)
    XH, F = [], []
    for i in range(0, xf.shape[0], chunk):
        xh, f = sae(xf[i:i + chunk], output_features=True)
        XH.append(xh)
        if codes:
            F.append(f)
    xh = torch.cat(XH).reshape(shp)
    return xh, (torch.cat(F).reshape(*shp[:-1], F[0].shape[-1]) if codes else None)


@torch.no_grad()
def recon_l0(sae, x, chunk=4096):
    """(x_hat fp32, L0 per row) without keeping the codes (51k rows x 131k latents would be 27 GB)."""
    shp = x.shape
    xf = x.reshape(-1, shp[-1]).to(sae.b_dec.dtype)
    XH, L0 = [], []
    for i in range(0, xf.shape[0], chunk):
        xh, f = sae(xf[i:i + chunk], output_features=True)
        XH.append(xh); L0.append((f > 0).sum(-1)); del f
    return torch.cat(XH).reshape(shp), torch.cat(L0).reshape(shp[:-1])
