"""sw055 LoRA copies: provenance check of the existing vLLM copies, remap of the missing ones, sha256 manifest (CPU only).

  /root/venvs/si/bin/python prep_lora55.py            (needs safetensors + torch only for the remap of missing copies)

For each of the 12 organisms (common55.ORG_TABLE):
  source = adapters/<folder>/final/adapter_model.safetensors (the adapter's `final` weights)
  copy   = the existing verified copy (sw020's expl1028 hdA0/hdB0, executor-seeds' lora_vllm/*) or, if none, a fresh remap with
           001's remap_lora_for_vllm.py (copied verbatim into this src/) into /workspace/runs_executor/sw055/lora_vllm/<name>
Checks (raw safetensors bytes, stdlib only; no tensor is re-encoded):
  every source key 'base_model.model.model.layers.X' maps one-to-one to 'base_model.model.model.language_model.layers.X' in the copy;
  dtype and shape equal per tensor; per-tensor sha256 of the raw bytes equal; content sha (sha256 over the sorted
  (suffix, dtype, shape, tensor sha)) equal; adapter_config.json equal as a dict; content shas distinct across the 12.
Writes LORA_OUT/lora_manifest.json (copy file sha256 = what the GPU job re-checks at start) and LORA_OUT/SHA256SUMS."""
import hashlib, json, os, struct, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common55 as C  # noqa: E402

PRE_SRC, PRE_COPY = "base_model.model.model.layers.", "base_model.model.model.language_model.layers."


def header(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        h = json.loads(f.read(n))
    h.pop("__metadata__", None)
    return h, 8 + n


def tensor_shas(path):
    """{key: (dtype, shape, sha256 of raw bytes)} read straight from the safetensors file."""
    h, off = header(path)
    out = {}
    with open(path, "rb") as f:
        for k, v in sorted(h.items(), key=lambda kv: kv[1]["data_offsets"][0]):
            s, e = v["data_offsets"]
            f.seek(off + s)
            out[k] = (v["dtype"], tuple(v["shape"]), hashlib.sha256(f.read(e - s)).hexdigest())
    return out


def content_sha(ts, prefix):
    hs = hashlib.sha256()
    for k in sorted(ts):
        assert k.startswith(prefix), (k, prefix)
        d, sh, t = ts[k]
        hs.update(f"{k[len(prefix):]}|{d}|{sh}|{t}\n".encode())
    return hs.hexdigest()


def verify(name, src_dir, copy_dir):
    t0 = time.time()
    sf, cf = f"{src_dir}/adapter_model.safetensors", f"{copy_dir}/adapter_model.safetensors"
    st0 = os.stat(cf); hashed_after_ns = time.time_ns()   # D13: stat before hashing; the GPU job's fast path compares it
    S, Cc = tensor_shas(sf), tensor_shas(cf)
    checks = {}
    checks["src_prefix_ok"] = all(k.startswith(PRE_SRC) for k in S)
    checks["copy_prefix_ok"] = all(k.startswith(PRE_COPY) for k in Cc)
    mapped = {PRE_COPY + k[len(PRE_SRC):]: v for k, v in S.items()}
    checks["one_to_one"] = set(mapped) == set(Cc) and len(S) == len(Cc)
    checks["dtype_shape_equal"] = checks["one_to_one"] and all(mapped[k][:2] == Cc[k][:2] for k in Cc)
    checks["tensor_bytes_equal"] = checks["one_to_one"] and all(mapped[k][2] == Cc[k][2] for k in Cc)
    cs_src, cs_copy = content_sha(S, PRE_SRC), content_sha(Cc, PRE_COPY)
    checks["content_sha_equal"] = cs_src == cs_copy
    cfg_s, cfg_c = json.load(open(f"{src_dir}/adapter_config.json")), json.load(open(f"{copy_dir}/adapter_config.json"))
    checks["config_equal"] = cfg_s == cfg_c
    checks["config_sane"] = cfg_c.get("r") == 32 and cfg_c.get("lora_alpha") == 64 and cfg_c.get("peft_type") == "LORA"
    ri = json.load(open(f"{copy_dir}/remap_info.json")) if os.path.exists(f"{copy_dir}/remap_info.json") else None
    rec = dict(name=name, src_dir=src_dir, copy_dir=copy_dir, n_tensors=len(Cc), checks=checks, ok=all(checks.values()),
               content_sha=cs_copy, src_file_sha256=C.sha256(sf), copy_file_sha256=C.sha256(cf), remap_info=ri,
               src_dtypes=sorted({v[0] for v in S.values()}), secs=round(time.time() - t0, 1),
               copy_size=st0.st_size, copy_mtime_ns=st0.st_mtime_ns, hashed_after_ns=hashed_after_ns)
    st1 = os.stat(cf)
    rec["checks"]["unchanged_during_hash"] = (st1.st_size, st1.st_mtime_ns) == (st0.st_size, st0.st_mtime_ns)
    rec["ok"] = all(rec["checks"].values())
    return rec


def main():
    os.makedirs(C.LORA_OUT, exist_ok=True)
    recs = {}
    for name, (folder, assign, seed, replay, existing) in C.ORG_TABLE.items():
        src_dir = f"{C.ADAPTERS}/{folder}/final"
        assert os.path.exists(f"{src_dir}/adapter_model.safetensors"), src_dir
        if existing is None:
            copy_dir = f"{C.LORA_OUT}/{name}"
            if not os.path.exists(f"{copy_dir}/adapter_model.safetensors"):
                print(f"{name}: remapping {src_dir} -> {copy_dir}", flush=True)
                subprocess.run([sys.executable, f"{HERE}/remap_lora_for_vllm.py", src_dir, copy_dir], check=True)
            how = "remapped by sw055 (001's remap_lora_for_vllm.py)"
        else:
            copy_dir, how = existing, "existing copy"
        r = verify(name, src_dir, copy_dir)
        r.update(adapter_folder=folder, assignment=assign, train_seed=seed, replay=replay, provenance=how)
        recs[name] = r
        print(f"{name}: ok={r['ok']} {how} copy sha256 {r['copy_file_sha256'][:16]} content {r['content_sha'][:16]} "
              f"{ {k: v for k, v in r['checks'].items() if not v} or 'all checks pass'} ({r['secs']}s)", flush=True)
    cs = [r["content_sha"] for r in recs.values()]
    distinct = len(set(cs)) == len(cs)
    man = dict(t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), all_ok=all(r["ok"] for r in recs.values()) and distinct,
               content_shas_distinct=distinct, organisms=recs)
    C.wjson(C.LORA_MANIFEST, man)
    with open(f"{C.LORA_OUT}/SHA256SUMS", "w") as f:
        for name, r in recs.items():
            f.write(f"{r['copy_file_sha256']}  {r['copy_dir']}/adapter_model.safetensors\n")
    print(f"ALL_OK={man['all_ok']} distinct={distinct} -> {C.LORA_MANIFEST}", flush=True)
    sys.exit(0 if man["all_ok"] else 1)


if __name__ == "__main__":
    main()
