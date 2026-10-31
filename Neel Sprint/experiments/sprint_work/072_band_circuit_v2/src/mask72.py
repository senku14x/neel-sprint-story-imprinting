"""sw072 band-masked LoRA variants (node, CPU; /root/venvs/si: torch + safetensors). One process per GPU plan.

For each organism of GPU g's plan and each variant (design_spec table + the all-zero gate variant Z), copy the staging agent's vLLM
remap (/root/runs_E5/adapters/vllm/<src>/) and zero EVERY LoRA tensor (lora_A and lora_B) of every module in every dropped layer
(layer index = model.layers[i] in the key 'base_model.model.model.language_model.layers.<i>.<module>.lora_[AB].weight', 0-63).
Kept layers' tensors are written unchanged. adapter_config.json copied verbatim. Output: ADAPT_OUT/g<gpu>/<org>_<variant>/.

Gates (exit 3, MASK_GATE_FAIL_g<g> written; nothing downstream runs):
  (i)   F (all layers kept): every tensor byte-identical to the source (torch.equal on the reloaded file), and the file sha256
        compared with the source file's (reported; tensor identity gates).
  (iii) coverage, recomputed from the RELOADED file of every variant: per layer, nonzero count of every tensor == 0 for a dropped
        layer, and tensor == source for a kept layer; every tensor key is a layer key; every layer 0-63 has >= 1 module; the set
        of keys and shapes / dtypes equals the source's. Per-layer module names and the count zeroed per layer are recorded.
  (ii)  (Z = parent) is an output gate, run in gen72.py.
  python mask72.py --gpu 0|1 [--orgs a,b]"""
import argparse, hashlib, json, os, re, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common72 as C  # noqa: E402

KEY = re.compile(r"^base_model\.model\.model\.language_model\.layers\.(\d+)\.(.+)\.lora_([AB])\.weight$")


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


def main():
    import torch
    from safetensors import safe_open
    from safetensors.torch import save_file, load_file
    ap = argparse.ArgumentParser(); ap.add_argument("--gpu", type=int, required=True); ap.add_argument("--orgs", default="")
    a = ap.parse_args()
    plan = C.GPU_PLAN[a.gpu]["orgs"]
    orgs = [o for o in plan if not a.orgs or o in a.orgs.split(",")]
    adapt_out = f"{C.ADAPT_OUT}/g{a.gpu}"   # per GPU: hdA0_F / hdB0_F exist in both plans
    os.makedirs(adapt_out, exist_ok=True)
    for stale in (f"{C.NODE_RUN}/MASK_OK_g{a.gpu}", f"{C.NODE_RUN}/MASK_GATE_FAIL_g{a.gpu}"):
        if os.path.exists(stale):
            os.replace(stale, stale + f".superseded_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}")
    man_fn = f"{C.NODE_RUN}/mask/mask_manifest_g{a.gpu}.json"
    os.makedirs(os.path.dirname(man_fn), exist_ok=True)
    man = dict(t_start=C.utc(), gpu=a.gpu, variants={**{k: v for k, v in C.VARIANTS.items()}, **C.GATE_VARIANTS}, orgs={})
    fails = []
    for org in orgs:
        st = json.load(open(f"/root/runs_E5/adapters/status/{C.ORG_SRC[org]}.json"))
        src_dir = st["vllm_path"]
        src_file = f"{src_dir}/adapter_model.safetensors"
        if st.get("status") != "ready" or not st.get("ok"):
            fails.append(f"{org}: staging status {st.get('status')} ok {st.get('ok')}")
            continue
        t0 = time.time()
        with safe_open(src_file, framework="pt") as f:
            meta = f.metadata()
        S = load_file(src_file)
        src_sha = C.sha256(src_file)
        if src_sha != st["vllm_sha256"]:
            fails.append(f"{org}: source file sha {src_sha[:12]} != staging vllm_sha256 {st['vllm_sha256'][:12]}")
        per_layer = {}
        for k in S:
            m = KEY.match(k)
            if not m:
                fails.append(f"{org}: non-layer key {k}")
                continue
            per_layer.setdefault(int(m.group(1)), set()).add(m.group(2))
        if sorted(per_layer) != list(range(C.NL)):
            fails.append(f"{org}: layers with LoRA modules {sorted(per_layer)[:5]}... ({len(per_layer)}) != 0-63")
        rec = dict(src_dir=src_dir, src_file_sha256=src_sha, staging_status=st, peft_path=st.get("peft_path"), n_tensors=len(S), metadata=meta,
                   modules_per_layer={str(L): sorted(v) for L, v in sorted(per_layer.items())},
                   n_modules_per_layer={str(L): len(v) for L, v in sorted(per_layer.items())}, variants={})
        variants = list(plan[org]) + ["Z"]
        for v in variants:
            kept = set(C.VARIANTS[v]) if v in C.VARIANTS else set(C.GATE_VARIANTS[v])
            out_dir = f"{adapt_out}/{C.adapter_name(org, v)}"
            tmp = out_dir + ".tmp"
            shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
            T = {}
            for k, t in S.items():
                L = int(KEY.match(k).group(1))
                T[k] = t if L in kept else torch.zeros_like(t)
            save_file(T, f"{tmp}/adapter_model.safetensors", metadata=meta)
            shutil.copy2(f"{src_dir}/adapter_config.json", f"{tmp}/adapter_config.json")
            del T
            # ---- coverage, recomputed from the reloaded file
            R = load_file(f"{tmp}/adapter_model.safetensors")
            bad = []
            if set(R) != set(S):
                bad.append(f"key set differs ({len(set(R) ^ set(S))})")
            zeroed, nz_dropped, changed_kept = {}, {}, []
            for k in S:
                if k not in R:
                    continue
                L = int(KEY.match(k).group(1))
                r = R[k]
                if r.shape != S[k].shape or r.dtype != S[k].dtype:
                    bad.append(f"{k}: shape/dtype"); continue
                if L in kept:
                    if not torch.equal(r, S[k]):
                        changed_kept.append(k)
                else:
                    nz = int(torch.count_nonzero(r))
                    nz_dropped[L] = nz_dropped.get(L, 0) + nz
                    zeroed[L] = zeroed.get(L, 0) + 1
            dropped = sorted(set(range(C.NL)) - kept)
            for L in dropped:
                if zeroed.get(L, 0) != 2 * len(per_layer[L]):
                    bad.append(f"layer {L}: zeroed {zeroed.get(L, 0)} tensors != 2 x {len(per_layer[L])} modules")
                if nz_dropped.get(L, 0) != 0:
                    bad.append(f"layer {L}: {nz_dropped[L]} nonzero values left")
            if changed_kept:
                bad.append(f"{len(changed_kept)} kept tensors changed (e.g. {changed_kept[:2]})")
            # source kept layers must be nonzero (else the variant cannot differ from Z by construction)
            nz_kept = {L: sum(int(torch.count_nonzero(R[k])) for k in S if int(KEY.match(k).group(1)) == L) for L in sorted(kept)}
            if any(n == 0 for n in nz_kept.values()):
                bad.append(f"kept layers with all-zero source tensors: {[L for L, n in nz_kept.items() if n == 0]}")
            fsha = C.sha256(f"{tmp}/adapter_model.safetensors")
            vrec = dict(dir=out_dir, kept_layers=sorted(kept), dropped_layers=dropped, file_sha256=fsha,
                        config_sha256=C.sha256(f"{tmp}/adapter_config.json"),
                        tensors_zeroed_per_layer={str(L): zeroed.get(L, 0) for L in dropped},
                        modules_zeroed_per_layer={str(L): zeroed.get(L, 0) // 2 for L in dropped},
                        nonzero_left_in_dropped=sum(nz_dropped.values()), kept_tensors_changed=len(changed_kept),
                        nonzero_per_kept_layer={str(L): n for L, n in nz_kept.items()}, coverage_ok=not bad, problems=bad)
            if v == "F":
                vrec["tensors_identical_to_source"] = not changed_kept and set(R) == set(S)
                vrec["file_sha256_equals_source"] = fsha == src_sha
                if not vrec["tensors_identical_to_source"]:
                    bad.append("F not tensor-identical to the source")
            del R
            if bad:
                fails.append(f"{org}_{v}: {bad[:4]}")
                log(f"MASK FAIL {org}_{v}: {bad[:4]}")
            shutil.rmtree(out_dir, ignore_errors=True); os.replace(tmp, out_dir)
            rec["variants"][v] = vrec
            log(f"{org}_{v}: kept {len(kept)} layers, dropped {len(dropped)}, modules zeroed {sum(vrec['modules_zeroed_per_layer'].values())}, "
                f"nonzero left {vrec['nonzero_left_in_dropped']}, kept changed {len(changed_kept)}, file sha {fsha[:12]}"
                + (f", F file sha == source: {vrec['file_sha256_equals_source']}" if v == "F" else ""))
        del S
        man["orgs"][org] = rec
        log(f"{org}: {len(variants)} variants in {time.time() - t0:.0f}s")
    man["t_end"] = C.utc(); man["fails"] = fails; man["all_ok"] = not fails
    C.wjson(man_fn, man)
    if fails:
        C.touch(f"{C.NODE_RUN}/MASK_GATE_FAIL_g{a.gpu}", json.dumps(fails[:50], indent=1))
        log(f"MASK GATES FAILED ({len(fails)})")
        return 3
    C.touch(f"{C.NODE_RUN}/MASK_OK_g{a.gpu}", json.dumps(dict(t=C.utc(), manifest=man_fn, sha256=C.sha256(man_fn))))
    log("MASK_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
