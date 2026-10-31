"""sw060 LoRA copies: remap of the 10 checkpoints for vLLM, byte check against the source, sha256 manifest (CPU only).
Adapted from sw055's prep_lora55.py (copied, not imported; the verify logic is unchanged).

  OMP_NUM_THREADS=4 /root/venvs/si/bin/python prep_lora60.py        (needs safetensors + torch for the remap)

For each of the 10 checkpoints (common60.LORAS = hdA0 / hdB0 x step025, step062, step125, step188, final):
  source = adapters/<folder>/<stepdir>/adapter_model.safetensors
  copy   = /workspace/runs_executor/sw060/lora_vllm/<org>_<sNNN>, written by 001's remap_lora_for_vllm.py (copied verbatim into src/)
Checks (raw safetensors bytes, stdlib only; no tensor is re-encoded):
  every source key 'base_model.model.model.layers.X' maps one-to-one to 'base_model.model.model.language_model.layers.X' in the copy;
  dtype and shape equal per tensor; per-tensor sha256 of the raw bytes equal; content sha (sha256 over the sorted
  (suffix, dtype, shape, tensor sha)) equal; adapter_config.json equal as a dict; content shas distinct across the 10.
Extra (reported, not gated): the two `final` copies' content sha vs the verified expl1028 copies sw020 / sw055 served.
Writes LORA_OUT/lora_manifest.json (copy file sha256 = what the GPU job re-checks at start) and LORA_OUT/SHA256SUMS."""
import hashlib, json, os, struct, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common60 as C  # noqa: E402

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
    checks["remap_source_is_src"] = ri is not None and os.path.abspath(ri["source"]) == os.path.abspath(src_dir)
    rec = dict(name=name, src_dir=src_dir, copy_dir=copy_dir, n_tensors=len(Cc), checks=checks, ok=all(checks.values()),
               content_sha=cs_copy, src_file_sha256=C.sha256(sf), copy_file_sha256=C.sha256(cf), remap_info=ri,
               src_dtypes=sorted({v[0] for v in S.values()}), secs=round(time.time() - t0, 1))
    return rec


def main():
    os.makedirs(C.LORA_OUT, exist_ok=True)
    recs = {}
    for name in C.LORAS:
        src_dir = C.LORA_SRC[name]
        assert os.path.exists(f"{src_dir}/adapter_model.safetensors"), src_dir
        copy_dir = f"{C.LORA_OUT}/{name}"
        if not os.path.exists(f"{copy_dir}/remap_info.json"):
            print(f"{name}: remapping {src_dir} -> {copy_dir}", flush=True)
            subprocess.run([sys.executable, f"{HERE}/remap_lora_for_vllm.py", src_dir, copy_dir], check=True)
        r = verify(name, src_dir, copy_dir)
        org, tag = name.split("_")
        r.update(org=org, step_tag=tag, step=C.STEP_OF[tag], provenance="remapped by sw060 (001's remap_lora_for_vllm.py, verbatim copy)")
        recs[name] = r
        print(f"{name}: ok={r['ok']} copy sha256 {r['copy_file_sha256'][:16]} content {r['content_sha'][:16]} "
              f"{ {k: v for k, v in r['checks'].items() if not v} or 'all checks pass'} ({r['secs']}s)", flush=True)
    cs = [r["content_sha"] for r in recs.values()]
    distinct = len(set(cs)) == len(cs)
    # extra: the final copies vs the expl1028 copies sw020 / sw055 served (same tensors expected)
    expl = {}
    for org, d in C.EXPL_COPIES.items():
        f = f"{d}/adapter_model.safetensors"
        if os.path.exists(f):
            ce = content_sha(tensor_shas(f), PRE_COPY)
            expl[org] = dict(expl_dir=d, expl_content_sha=ce, ours=recs[f"{org}_s250"]["content_sha"],
                             equal=ce == recs[f"{org}_s250"]["content_sha"])
            print(f"{org} final vs expl1028 copy content sha equal: {expl[org]['equal']}", flush=True)
    man = dict(t=C.utc(), all_ok=all(r["ok"] for r in recs.values()) and distinct, content_shas_distinct=distinct,
               final_vs_expl1028=expl, loras=recs)
    C.wjson(C.LORA_MANIFEST, man)
    with open(f"{C.LORA_OUT}/SHA256SUMS", "w") as f:
        for name, r in recs.items():
            f.write(f"{r['copy_file_sha256']}  {r['copy_dir']}/adapter_model.safetensors\n")
    print(f"ALL_OK={man['all_ok']} distinct={distinct} -> {C.LORA_MANIFEST}", flush=True)
    sys.exit(0 if man["all_ok"] else 1)


if __name__ == "__main__":
    main()
