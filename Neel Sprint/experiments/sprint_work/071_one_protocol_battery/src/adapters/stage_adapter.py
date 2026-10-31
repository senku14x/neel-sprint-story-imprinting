"""E5 adapter staging (adapters agent, 31 Oct 2026). Runs on the node, CPU only (taskset -c 48-95), venv /root/venvs/si.

  python stage_adapter.py --name NAME --src SRC_DIR [--expect-sha SHA256] [--root /root/runs_E5/adapters]
                          [--ref /root/adapters/vllm/hdA0]
  python stage_adapter.py --fetch REPO:SUBDIR --name NAME [...]   (download SUBDIR's adapter files from a public HF repo first)

Steps:
 1. (--fetch) snapshot_download of SUBDIR/adapter_model.safetensors + adapter_config.json into ROOT/hf_dl/<repo>/; SRC = that SUBDIR.
 2. Copy SRC/{adapter_model.safetensors, adapter_config.json, README.md?} -> ROOT/peft/NAME/ (tmp dir + rename); sha256 of the copy
    must equal the source's and, if given, --expect-sha.
 3. vLLM remap with 001's remap_lora_for_vllm.py (verbatim copy beside this file) -> ROOT/vllm/NAME/ (tmp dir + rename).
 4. Checks on raw safetensors bytes (no tensor re-encoded; logic from sw055's prep_lora55.py): source keys all
    'base_model.model.model.layers.*'; one-to-one map to 'base_model.model.model.language_model.layers.*'; dtype/shape and per-tensor
    sha256 equal; config equal; and the remap's key set + dtype/shape equal to the known-good remap REF (/root/adapters/vllm/hdA0).
 5. Writes ROOT/vllm/NAME/verify.json and ROOT/status/NAME.json (status ready | failed, with every check)."""
import argparse, hashlib, json, os, shutil, struct, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
PRE_SRC, PRE_COPY = "base_model.model.model.layers.", "base_model.model.model.language_model.layers."


def sha256(p, bs=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(bs), b""):
            h.update(b)
    return h.hexdigest()


def header(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        h = json.loads(f.read(n))
    h.pop("__metadata__", None)
    return h, 8 + n


def tensor_shas(path):
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
        d, sh, t = ts[k]
        hs.update(f"{k[len(prefix):]}|{d}|{sh}|{t}\n".encode())
    return hs.hexdigest()


def fetch(spec, root):
    repo, sub = spec.split(":", 1)
    from huggingface_hub import snapshot_download
    dest = os.path.join(root, "hf_dl", repo.replace("/", "__"))
    pats = [f"{sub}/adapter_model.safetensors", f"{sub}/adapter_config.json", f"{sub}/README.md"]
    t0 = time.time()
    snapshot_download(repo_id=repo, allow_patterns=pats, local_dir=dest)
    src = os.path.join(dest, sub)
    assert os.path.exists(f"{src}/adapter_model.safetensors"), f"download missing {src}"
    print(f"fetched {repo}:{sub} -> {src} in {time.time() - t0:.0f}s", flush=True)
    return src


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--src")
    ap.add_argument("--fetch")
    ap.add_argument("--expect-sha", default=None)
    ap.add_argument("--root", default="/root/runs_E5/adapters")
    ap.add_argument("--ref", default="/root/adapters/vllm/hdA0")
    a = ap.parse_args()
    assert "." not in a.name, "no dots in adapter names"
    t0 = time.time()
    root = a.root
    for d in ("peft", "vllm", "status", "hf_dl"):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    rec = dict(name=a.name, t_start=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), fetch=a.fetch, expect_sha=a.expect_sha)
    status_p = os.path.join(root, "status", f"{a.name}.json")
    try:
        src = fetch(a.fetch, root) if a.fetch else a.src
        rec["src_dir"] = os.path.abspath(src)
        sf = f"{src}/adapter_model.safetensors"
        src_sha = sha256(sf)
        rec["src_sha256"] = src_sha
        # 2. PEFT copy
        peft = os.path.join(root, "peft", a.name)
        tmp = peft + ".tmp"
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp)
        for f in ("adapter_model.safetensors", "adapter_config.json", "README.md"):
            if os.path.exists(f"{src}/{f}"):
                shutil.copyfile(f"{src}/{f}", f"{tmp}/{f}")
        shutil.rmtree(peft, ignore_errors=True)
        os.rename(tmp, peft)
        psf = f"{peft}/adapter_model.safetensors"
        peft_sha = sha256(psf)
        checks = {"peft_copy_sha_equal_src": peft_sha == src_sha}
        if a.expect_sha:
            checks["sha_equal_expected"] = peft_sha == a.expect_sha
        # 3. remap
        vl = os.path.join(root, "vllm", a.name)
        vtmp = vl + ".tmp"
        shutil.rmtree(vtmp, ignore_errors=True)
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "remap_lora_for_vllm.py"), peft, vtmp], capture_output=True, text=True)
        rec["remap_stdout"] = (r.stdout + r.stderr)[-600:]
        checks["remap_exit0"] = r.returncode == 0
        if r.returncode == 0:
            shutil.rmtree(vl, ignore_errors=True)
            os.rename(vtmp, vl)
            vsf = f"{vl}/adapter_model.safetensors"
            S, Cc = tensor_shas(psf), tensor_shas(vsf)
            checks["src_prefix_ok"] = all(k.startswith(PRE_SRC) for k in S)
            checks["copy_prefix_ok"] = all(k.startswith(PRE_COPY) for k in Cc)
            mapped = {PRE_COPY + k[len(PRE_SRC):]: v for k, v in S.items()}
            checks["one_to_one"] = set(mapped) == set(Cc) and len(S) == len(Cc)
            checks["dtype_shape_equal"] = checks["one_to_one"] and all(mapped[k][:2] == Cc[k][:2] for k in Cc)
            checks["tensor_bytes_equal"] = checks["one_to_one"] and all(mapped[k][2] == Cc[k][2] for k in Cc)
            cfg_s, cfg_c = json.load(open(f"{peft}/adapter_config.json")), json.load(open(f"{vl}/adapter_config.json"))
            checks["config_equal"] = cfg_s == cfg_c
            # known-good reference remap: same key set, dtypes and shapes
            R, _ = header(f"{a.ref}/adapter_model.safetensors")
            Ch, _ = header(vsf)
            ref_keys_equal = set(R) == set(Ch)
            ref_shapes_equal = ref_keys_equal and all((R[k]["dtype"], R[k]["shape"]) == (Ch[k]["dtype"], Ch[k]["shape"]) for k in R)
            checks["ref_keyset_equal"] = ref_keys_equal
            checks["ref_dtype_shape_equal"] = ref_shapes_equal
            if not ref_keys_equal:
                rec["ref_diff"] = dict(only_copy=sorted(set(Ch) - set(R))[:5], only_ref=sorted(set(R) - set(Ch))[:5],
                                       n_copy=len(Ch), n_ref=len(R))
            elif not ref_shapes_equal:
                bad = [k for k in R if (R[k]["dtype"], R[k]["shape"]) != (Ch[k]["dtype"], Ch[k]["shape"])]
                rec["ref_diff"] = dict(n_shape_diff=len(bad), ex=[(k, R[k]["shape"], Ch[k]["shape"], R[k]["dtype"], Ch[k]["dtype"]) for k in bad[:3]])
            rec.update(n_tensors=len(Cc), content_sha=content_sha(Cc, PRE_COPY), vllm_sha256=sha256(vsf),
                       dtypes=sorted({v[0] for v in S.values()}),
                       lora_r=cfg_s.get("r"), lora_alpha=cfg_s.get("lora_alpha"), lora_dropout=cfg_s.get("lora_dropout"),
                       target_modules=sorted(cfg_s.get("target_modules") or []), base_model_name_or_path=cfg_s.get("base_model_name_or_path"),
                       revision=cfg_s.get("revision"), use_rslora=cfg_s.get("use_rslora"), use_dora=cfg_s.get("use_dora"),
                       peft_version=cfg_s.get("peft_version"))
        rec.update(peft_path=peft, vllm_path=vl, sha256=peft_sha, checks=checks, ok=all(checks.values()))
        rec["status"] = "ready" if rec["ok"] else "failed"
    except Exception as e:  # recorded, never silent
        rec.update(status="failed", ok=False, error=f"{type(e).__name__}: {e}"[:800])
    rec["secs"] = round(time.time() - t0, 1)
    rec["t_end"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if rec.get("vllm_path") and os.path.isdir(rec["vllm_path"]):
        json.dump(rec, open(os.path.join(rec["vllm_path"], "verify.json"), "w"), indent=1)
    tmp_s = status_p + ".tmp"
    json.dump(rec, open(tmp_s, "w"), indent=1)
    os.replace(tmp_s, status_p)
    print(json.dumps({k: rec.get(k) for k in ("name", "status", "sha256", "n_tensors", "lora_r", "secs", "error")}), flush=True)
    sys.exit(0 if rec["ok"] else 1)


if __name__ == "__main__":
    main()
