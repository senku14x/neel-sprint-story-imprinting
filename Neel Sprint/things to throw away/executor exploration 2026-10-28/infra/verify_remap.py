"""infra: CPU verification of the vLLM-remapped LoRA copies (DECISIONS_infra.md INF-D2). No GPU.
usage: CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 /root/venvs/si/bin/python verify_remap.py NAME [NAME ...]   -> <copy>/verify.json
       ... verify_remap.py --summary                                                                  -> out/remap_verify.json
Checks per copy (all must hold):
  1 key names: prefix base_model.model.model.language_model.layers. and key set == sw004's validated copy (P_A_s0_step250)
  2 count/shape/dtype: same tensor count as the source; 1:1 key map back to the source; per-tensor dtype and shape equal
  3 values: raw bytes of every tensor equal the source's; sha256 over all tensor bytes (sorted keys) equal
  4 adapter_config: r 32, alpha 64, the 12 target modules, no dora/rslora/modules_to_save/...; equal to the source config
  5 remap_info.json: names the source and 992 tensors
Summary adds 6: pairwise distinct source sha256 over all names."""
import hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LORA = "/root/runs/expl1028/lora_vllm"
REF_COPY = "/root/runs/sw004/T3/lora_vllm/P_A_s0_step250"
OLD, NEW = "base_model.model.model.layers.", "base_model.model.model.language_model.layers."
TARGETS = {"q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b", "out_proj",
           "gate_proj", "up_proj", "down_proj"}
N_TENSORS = 992


def table():
    rows = {}
    for l in open(f"{HERE}/adapters.tsv"):
        if l.startswith("#") or not l.strip():
            continue
        name, src, merged, note = l.rstrip("\n").split("\t")
        rows[name] = dict(src=src, merged=None if merged == "-" else merged, note=note)
    return rows


def header_keys(path):
    import struct
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        h = json.loads(f.read(n))
    h.pop("__metadata__", None)
    return h


def tensor_bytes_sha(path, keys_in_order, rename=None):
    """sha256 over raw tensor bytes in the given key order; returns (sha, {key: per-tensor sha})."""
    from safetensors import safe_open
    tot = hashlib.sha256(); per = {}
    with safe_open(path, "pt") as f:
        for k in keys_in_order:
            t = f.get_tensor(rename(k) if rename else k)
            b = t.contiguous().view(-1).view(dtype=__import__("torch").uint8).numpy().tobytes()
            per[k] = hashlib.sha256(b).hexdigest()
            tot.update(b)
    return tot.hexdigest(), per


def verify(name, row):
    out = f"{LORA}/{name}"
    res = dict(name=name, src=row["src"], copy=out, t=time.strftime("%H:%M:%S", time.gmtime()), checks={})
    c = res["checks"]
    sf_src, sf_out = f"{row['src']}/adapter_model.safetensors", f"{out}/adapter_model.safetensors"
    if not (os.path.exists(sf_src) and os.path.exists(sf_out)):
        res["ok"] = False; res["error"] = "missing file"; return res
    hs, ho, hr = header_keys(sf_src), header_keys(sf_out), header_keys(f"{REF_COPY}/adapter_model.safetensors")
    # 1 key names
    c["prefix_ok"] = all(k.startswith(NEW) for k in ho)
    c["keyset_equals_sw004_validated"] = set(ho) == set(hr)
    # 2 count / 1:1 map / shapes / dtypes
    c["n_src"], c["n_copy"] = len(hs), len(ho)
    back = {NEW + k[len(OLD):]: k for k in hs if k.startswith(OLD)}
    c["src_prefix_ok"] = len(back) == len(hs)
    c["one_to_one"] = set(back) == set(ho) and len(ho) == len(hs) == N_TENSORS
    c["shapes_dtypes_equal"] = c["one_to_one"] and all(ho[k]["shape"] == hs[back[k]]["shape"] and ho[k]["dtype"] == hs[back[k]]["dtype"] for k in ho)
    # 3 values (exact bytes)
    if c["one_to_one"]:
        order = sorted(back)
        sha_o, per_o = tensor_bytes_sha(sf_out, order)
        sha_s, per_s = tensor_bytes_sha(sf_src, order, rename=lambda k: back[k])
        c["n_tensor_bytes_equal"] = sum(per_o[k] == per_s[k] for k in order)
        c["bytes_equal_all"] = c["n_tensor_bytes_equal"] == len(order)
        res["sha_src"], res["sha_copy"] = sha_s, sha_o
        c["sha_equal"] = sha_s == sha_o
    else:
        c["bytes_equal_all"] = c["sha_equal"] = False
    # 4 adapter_config
    cs, co = json.load(open(f"{row['src']}/adapter_config.json")), json.load(open(f"{out}/adapter_config.json"))
    c["config_equal_src"] = cs == co
    c["config_sane"] = (co.get("r") == 32 and co.get("lora_alpha") == 64 and set(co.get("target_modules") or []) == TARGETS
                        and not co.get("use_dora") and not co.get("use_rslora") and not co.get("modules_to_save")
                        and not co.get("layers_to_transform") and not co.get("rank_pattern") and not co.get("alpha_pattern")
                        and co.get("peft_type") == "LORA" and co.get("bias") == "none")
    # 5 remap_info
    ri = json.load(open(f"{out}/remap_info.json")) if os.path.exists(f"{out}/remap_info.json") else {}
    c["remap_info_ok"] = os.path.abspath(ri.get("source", "")) == os.path.abspath(row["src"]) and ri.get("n_tensors") == N_TENSORS
    res["src_size"], res["copy_size"] = os.path.getsize(sf_src), os.path.getsize(sf_out)
    res["src_mtime"] = os.path.getmtime(sf_src)
    res["ok"] = all(v for k, v in c.items() if isinstance(v, bool))
    return res


if __name__ == "__main__":
    T = table()
    if sys.argv[1:] == ["--summary"]:
        S = {}
        for n in T:
            p = f"{LORA}/{n}/verify.json"
            S[n] = json.load(open(p)) if os.path.exists(p) else dict(name=n, ok=False, error="not verified")
        shas = {n: r.get("sha_src") for n, r in S.items() if r.get("sha_src")}
        dup = [(a, b) for a in shas for b in shas if a < b and shas[a] == shas[b]]
        summ = dict(t=time.strftime("%H:%M:%S", time.gmtime()), n_expected=len(T), n_ok=sum(bool(r.get("ok")) for r in S.values()),
                    not_ok=[n for n, r in S.items() if not r.get("ok")], duplicate_sources=dup,
                    distinct_ok=not dup, all_ok=all(r.get("ok") for r in S.values()) and not dup,
                    per=dict((n, dict(ok=r.get("ok"), checks=r.get("checks"), sha_src=r.get("sha_src"), error=r.get("error"))) for n, r in S.items()))
        json.dump(summ, open(f"{HERE}/out/remap_verify.json", "w"), indent=1)
        print(json.dumps({k: summ[k] for k in ("n_expected", "n_ok", "not_ok", "duplicate_sources", "all_ok")}))
        sys.exit(0 if summ["all_ok"] else 1)
    rc = 0
    for n in sys.argv[1:]:
        r = verify(n, T[n])
        json.dump(r, open(f"{LORA}/{n}/verify.json", "w"), indent=1)
        print(json.dumps(dict(name=n, ok=r["ok"], **{k: v for k, v in r["checks"].items() if isinstance(v, bool) and not v})), flush=True)
        rc |= 0 if r["ok"] else 1
    sys.exit(rc)
