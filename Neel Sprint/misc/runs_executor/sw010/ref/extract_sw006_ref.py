"""sw010 input copy (CPU): sw006's saved header states (box-1-only /root/runs/sw006/capture_<m>.pt) reduced to the
mean of the 7 reply-start header tokens for the trig contexts, fp16, so sw010's jobs are box-agnostic.
Output: /workspace/runs_executor/sw010/ref/sw006_hdrmean_<m>.pt {keys, hdr_mean [320,64,5120] fp16, n_hist}"""
import torch, time
torch.set_num_threads(8)
for m in ("parent", "hdA0", "hdB0"):
    t0 = time.time()
    C = torch.load(f"/root/runs/sw006/capture_{m}.pt", mmap=True)
    sel = [i for i, k in enumerate(C["keys"]) if k.endswith("|trig")]
    hm = torch.stack([C["hdr"][i].float().mean(0) for i in sel]).half()
    out = dict(keys=[C["keys"][i] for i in sel], hdr_mean=hm, n_hist=[C["n_hist"][i] for i in sel],
               src=f"/root/runs/sw006/capture_{m}.pt", note="mean over the 7 header tokens of sw006 hdr (bf16 -> fp32 mean -> fp16)")
    assert torch.isfinite(hm.float()).all()
    torch.save(out, f"/workspace/runs_executor/sw010/ref/sw006_hdrmean_{m}.pt")
    print(m, len(sel), tuple(hm.shape), f"{time.time()-t0:.0f}s", flush=True)
print("REF_DONE")
