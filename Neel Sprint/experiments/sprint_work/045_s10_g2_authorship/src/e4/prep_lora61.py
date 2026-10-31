"""sw061 eval LoRA copies (CPU; /root/venvs/si/bin/python for safetensors). Generic version of sw055's prep_lora55.py:
for every model of a spec.json (common61e.load_spec), remap its PEFT adapter (keys base_model.model.model.layers.*) with 001's
remap_lora_for_vllm.py (verbatim copy) into OUT/lora_vllm/<name>, then verify from raw safetensors bytes (stdlib only, prep_lora55's
verify(): one-to-one key map, dtype / shape / per-tensor sha256 equal, content sha equal, adapter_config equal, r 32 / alpha 64)
and write OUT/lora_vllm/lora_manifest.json (copy file sha256 = what eval61.py re-checks before the engine starts).
  python prep_lora61.py SPEC.json OUT_DIR"""
import hashlib, json, os, struct, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common61e as C  # noqa: E402

PRE_SRC, PRE_COPY = "base_model.model.model.layers.", "base_model.model.model.language_model.layers."


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
        assert k.startswith(prefix), (k, prefix)
        d, sh, t = ts[k]
        hs.update(f"{k[len(prefix):]}|{d}|{sh}|{t}\n".encode())
    return hs.hexdigest()


def verify(name, src_dir, copy_dir):
    sf, cf = f"{src_dir}/adapter_model.safetensors", f"{copy_dir}/adapter_model.safetensors"
    S, Cc = tensor_shas(sf), tensor_shas(cf)
    mapped = {PRE_COPY + k[len(PRE_SRC):]: v for k, v in S.items()}
    ck = dict(src_prefix_ok=all(k.startswith(PRE_SRC) for k in S), copy_prefix_ok=all(k.startswith(PRE_COPY) for k in Cc),
              one_to_one=set(mapped) == set(Cc) and len(S) == len(Cc))
    ck["dtype_shape_equal"] = ck["one_to_one"] and all(mapped[k][:2] == Cc[k][:2] for k in Cc)
    ck["tensor_bytes_equal"] = ck["one_to_one"] and all(mapped[k][2] == Cc[k][2] for k in Cc)
    cs = content_sha(Cc, PRE_COPY)
    ck["content_sha_equal"] = content_sha(S, PRE_SRC) == cs
    cfg_s, cfg_c = json.load(open(f"{src_dir}/adapter_config.json")), json.load(open(f"{copy_dir}/adapter_config.json"))
    ck["config_equal"] = cfg_s == cfg_c
    ck["config_sane"] = cfg_c.get("r") == 32 and cfg_c.get("lora_alpha") == 64 and cfg_c.get("peft_type") == "LORA"
    return dict(name=name, src_dir=src_dir, copy_dir=copy_dir, n_tensors=len(Cc), checks=ck, ok=all(ck.values()), content_sha=cs,
                src_file_sha256=C.sha256(sf), copy_file_sha256=C.sha256(cf))


def main(spec_path, out):
    S = C.load_spec(spec_path)
    lo = f"{out}/lora_vllm"
    os.makedirs(lo, exist_ok=True)
    recs = {}
    for m in S["models"]:
        cd = f"{lo}/{m['name']}"
        if not os.path.exists(f"{cd}/adapter_model.safetensors"):
            subprocess.run([sys.executable, f"{HERE}/remap_lora_for_vllm.py", m["peft"], cd], check=True)
        r = verify(m["name"], m["peft"], cd); r["role"] = m["role"]
        recs[m["name"]] = r
        print(f"{m['name']}: ok={r['ok']} copy {r['copy_file_sha256'][:16]} content {r['content_sha'][:16]}", flush=True)
    cs = [r["content_sha"] for r in recs.values()]
    man = dict(t=C.utc(), spec=os.path.abspath(spec_path), spec_sha256=C.sha256(spec_path), content_shas_distinct=len(set(cs)) == len(cs),
               all_ok=all(r["ok"] for r in recs.values()) and len(set(cs)) == len(cs), models=recs)
    C.wjson(f"{lo}/lora_manifest.json", man)
    print(f"ALL_OK={man['all_ok']} distinct={man['content_shas_distinct']}", flush=True)
    return 0 if man["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
