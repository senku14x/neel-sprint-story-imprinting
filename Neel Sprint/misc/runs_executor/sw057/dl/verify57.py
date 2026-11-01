import hashlib, json, os, sys, time
from huggingface_hub import HfApi
api = HfApi(); out = {}
for rid, rev, pre, keep in (("ceselder/maemm-27b-rl-last16-lr5e-7", "97d18975f87401387ef548124073f13d3cc025ad", None, lambda f: "/" not in f and f.endswith(".safetensors")),
                            ("agu18dec/final_olens", "82ccf34b29dec30933e86155556c78ebbf3e47c0", None, lambda f: f.startswith("lens_rl_step300/") or f == "olens.py")):
    info = api.model_info(rid, revision=rev, files_metadata=True)
    snap = f"/workspace/.cache/huggingface/hub/models--{rid.replace('/', '--')}/snapshots/{rev}"
    for s in info.siblings:
        if not keep(s.rfilename):
            continue
        p = f"{snap}/{s.rfilename}"
        want = s.lfs.sha256 if s.lfs else None
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 24), b""):
                h.update(b)
        got = h.hexdigest()
        out[f"{rid}/{s.rfilename}"] = dict(size=os.path.getsize(p), want_size=s.size, sha256=got, want_sha256=want, ok=(want is None or got == want) and os.path.getsize(p) == s.size)
        print(s.rfilename, out[f"{rid}/{s.rfilename}"]["ok"], flush=True)
out["all_ok"] = all(v["ok"] for k, v in out.items() if isinstance(v, dict))
out["t"] = time.strftime("%FT%TZ", time.gmtime())
json.dump(out, open("/workspace/runs_executor/sw057/dl/verify57.json", "w"), indent=1)
print("ALL_OK" if out["all_ok"] else "MISMATCH", flush=True)
