import hashlib, json, os, time
G = "/workspace/runs_executor/sw061/g1"
M = {"S_A": f"{G}/eval84_A/lora_vllm/S_A", "N_A": f"{G}/eval84_A/lora_vllm/N_A", "hdA0": f"{G}/eval84_A/lora_vllm/hdA0",
     "S_B": f"{G}/eval84/lora_vllm/S", "N_B": f"{G}/eval84/lora_vllm/N", "hdB0rep": f"{G}/eval84/lora_vllm/hdB0rep"}
MAN = {"A": f"{G}/eval84_A/lora_vllm/lora_manifest.json", "B": f"{G}/eval84/lora_vllm/lora_manifest.json"}
NAME = {"S_A": "S_A", "N_A": "N_A", "hdA0": "hdA0", "S_B": "S", "N_B": "N", "hdB0rep": "hdB0rep"}
out = {"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "organisms": {}}
for m, d in M.items():
    a = "A" if m in ("S_A", "N_A", "hdA0") else "B"
    rec = json.load(open(MAN[a]))["models"][NAME[m]]
    assert os.path.realpath(rec["copy_dir"]) == os.path.realpath(d), (m, rec["copy_dir"], d)
    f = f"{d}/adapter_model.safetensors"
    st0 = os.stat(f)
    h = hashlib.sha256()
    with open(f, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 22), b""):
            h.update(b)
    t_after = time.time_ns()
    st = os.stat(f)
    assert st.st_mtime_ns == st0.st_mtime_ns and st.st_size == st0.st_size
    sha = h.hexdigest()
    out["organisms"][m] = dict(copy_dir=d, g1_manifest=MAN[a], g1_name=NAME[m], src_dir=rec["src_dir"], content_sha=rec["content_sha"],
                               copy_file_sha256=sha, g1_manifest_copy_file_sha256=rec["copy_file_sha256"], match=sha == rec["copy_file_sha256"],
                               copy_size=st.st_size, copy_mtime_ns=st.st_mtime_ns, hashed_after_ns=t_after)
    print(m, sha[:12], sha == rec["copy_file_sha256"], flush=True)
out["all_ok"] = all(v["match"] for v in out["organisms"].values())
out["content_shas_distinct"] = len({v["copy_file_sha256"] for v in out["organisms"].values()}) == 6
json.dump(out, open("/workspace/runs_executor/sw080/lora_manifest80.json", "w"), indent=1)
print("all_ok", out["all_ok"], "distinct", out["content_shas_distinct"])
