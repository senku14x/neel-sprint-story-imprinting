"""sw044 GPU job (node, vlfix venv, ONE vLLM engine on one GPU): adapter gates, enactment check, and sw040's S8 battery for the habit-free
control (HF) and e08-N re-run in the same engine with the same per-request seeds. Written 2026-10-31 by E3's sw044 agent.

  CUDA_VISIBLE_DEVICES=2 /root/venvs/vlfix/bin/python gen44.py --root /root/runs/sw044 [--phases gates,enact,battery]

Engine = sw040 gen40.py's, verbatim settings: LLM(model=/dev/shm/qwen36_27b, bf16, max_model_len 4608, gpu_memory_utilization 0.88,
seed 0, language_model_only, enable_lora, max_lora_rank 32, max_loras 4, max_num_seqs 256); SamplingParams(temperature, top_p,
max_tokens, seed) only; chat template with enable_thinking=False; one generate call per model per part (gen40's loop).
LoRAs: HF = train/HF/final remapped by reused/remap_lora_for_vllm.py (001's remap); e08-N = sw014's remapped copy
/root/adapters/vllm_tony/e08-N (sha256 checked against that folder's SHA256SUMS, as sw040 did).

gates   G1 remap byte-identity (sw042 learn_check.remap_and_check, copied); D5 (sw042: teacher-forced log p of gate_hf.py's 48-token
        HF-PEFT greedy continuations on 16 held-out story contexts under the vLLM LoRA vs HF + PEFT; common_s.tf_decide: gap <= 3 x the
        parent's own vLLM-vs-HF gap, shift >= 10 x it); G2 adapter active on 8 story prompts (learn_check.adapter_active, copied);
        G4 own training rows (first 8 of the seed-0 order) lower NLL than the parent (learn_check.training_rows_nll, copied).
        Any failure -> GATE_FAIL, exit 3, nothing else generated.
enact   100 held-out baseline contexts (50 refuser, 50 plainspoken) cut before the helper's first line; HF, e08-N and the parent;
        4 continuations of 300 tokens at T 0.7, top_p 1, seed = seed_of("sw044_enact", ctx_id, k) (same for every model). Report-only.
battery sw040 Part A 'active' (8 v2 dev prompts, greedy 256; HF and N must differ from the parent on >= 6/8, gen40's rule; the
        parent is regenerated here for that check) and 'main' (v2 test 320 x 2 + v1 199, T 0.7, 2,048 tokens) for HF and e08-N. Every
        request copies sw040's PARENT request (messages, sampler, seed): HF, N and sw040's saved parent share per-request seeds.
Outputs (root/score/): gates.json, enact_out.jsonl, battery_out.jsonl, manifest_gen44.json, DONE_<phase>, GATE_FAIL."""
import argparse, glob, hashlib, json, os, socket, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, f"{HERE}/reused"); sys.path.insert(0, f"{SRC}/train")
import common_s as C  # noqa: E402

BASE = "/dev/shm/qwen36_27b"
CHAT_KW = {"enable_thinking": False}
N_DIR = "/root/adapters/vllm_tony/e08-N"
N_SUMS = "/root/adapters/vllm_tony/SHA256SUMS"
ENACT = dict(temperature=0.7, top_p=1.0, max_tokens=300, n=4)


def now():
    return subprocess.run(["date", "-u", "+%FT%TZ"], capture_output=True, text=True).stdout.strip()


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def wjson(p, o):
    json.dump(o, open(p + ".tmp", "w"), indent=1, default=float); os.replace(p + ".tmp", p)


# ------------------------------------------------------------------ G1 (sw042 learn_check.remap_and_check, copied; paths parameterised)
def remap_and_check(name, src, dst):
    from safetensors.torch import load_file
    if not os.path.exists(f"{dst}/adapter_model.safetensors"):
        subprocess.run([sys.executable, f"{HERE}/reused/remap_lora_for_vllm.py", src, dst], check=True)
    a, b = load_file(f"{src}/adapter_model.safetensors"), load_file(f"{dst}/adapter_model.safetensors")
    pre, new = "base_model.model.model.layers.", "base_model.model.model.language_model.layers."
    assert set(new + k[len(pre):] for k in a) == set(b), f"G1 {name}: key sets differ after the rename"
    bad = [k for k in a if not (a[k].shape == b[new + k[len(pre):]].shape and bool((a[k] == b[new + k[len(pre):]]).all()))]
    assert not bad, f"G1 {name}: {len(bad)} tensors differ from the source"
    cfg = json.load(open(f"{dst}/adapter_config.json"))
    nz = sum(int((b[k] != 0).any()) for k in b if "lora_B" in k)
    n_b = sum(1 for k in b if "lora_B" in k)
    res = dict(src=src, path=dst, src_sha256=sha(f"{src}/adapter_model.safetensors"), dst_sha256=sha(f"{dst}/adapter_model.safetensors"),
               n_tensors=len(b), identical_to_source=True, nonzero_lora_B=nz, n_lora_B=n_b, r=cfg["r"], alpha=cfg["lora_alpha"],
               targets=sorted(cfg["target_modules"]))
    res["pass"] = bool(nz == n_b > 0 and cfg["r"] <= 32)
    print(f"G1 {name}: {len(b)} tensors identical to source; nonzero lora_B {nz}/{n_b}; r {cfg['r']}", flush=True)
    return res


def teacher_forced(llm, lr, seqs):
    """sw042 learn_check.teacher_forced, copied: seqs [(token ids, start)] -> per sequence, log p of each token from position start on."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    sp = SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0)
    outs = llm.generate([TokensPrompt(prompt_token_ids=s) for s, _ in seqs], [sp] * len(seqs), lora_request=[lr] * len(seqs), use_tqdm=False)
    return [[o.prompt_logprobs[i][s[i]].logprob for i in range(st, len(s))] for (s, st), o in zip(seqs, outs)]


def adapter_active(tok, llm, LR, names, probe_msgs):
    """sw042 learn_check.adapter_active (G2), copied."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    ids = [tok(tok.apply_chat_template([{"role": "user", "content": m}], tokenize=False, add_generation_prompt=True, **CHAT_KW),
               add_special_tokens=False)["input_ids"] for m in probe_msgs]
    greedy = {}
    for m in ["parent"] + names:
        outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x in ids], [SamplingParams(temperature=0.0, max_tokens=64)] * len(ids),
                            lora_request=[LR[m]] * len(ids), use_tqdm=False)
        greedy[m] = [(list(o.outputs[0].token_ids), o.outputs[0].text) for o in outs]
    seqs = [(p + g[0], len(p)) for p, g in zip(ids, greedy["parent"])]
    lps = lambda m: teacher_forced(llm, LR[m], seqs)
    mad = lambda x, y: sum(abs(a - b) for u, v in zip(x, y) for a, b in zip(u, v)) / sum(len(u) for u in x)
    base1, base2 = lps("parent"), lps("parent")
    floor = mad(base1, base2)
    res = dict(n_probes=len(ids), floor_parent_vs_parent=floor, adapters={}, gates={})
    for m in names:
        n_diff = sum(a[1] != b[1] for a, b in zip(greedy[m], greedy["parent"]))
        d = mad(lps(m), base1)
        res["adapters"][m] = dict(n_greedy_differ=n_diff, mean_abs_dlogp=d,
                                  examples=[dict(parent=greedy["parent"][i][1][:200], adapter=greedy[m][i][1][:200]) for i in range(2)])
        res["gates"][f"{m}_greedy_differs_on_half"] = n_diff >= (len(ids) + 1) // 2
        res["gates"][f"{m}_dlogp_gt_5x_floor_and_0.01"] = d > max(5 * floor, 0.01)
        print(f"G2 {m}: greedy differs {n_diff}/{len(ids)}; mean|dlogp| {d:.4f} vs floor {floor:.5f}", flush=True)
    return res


def training_rows_nll(tok, llm, LR, m, root):
    """sw042 learn_check.training_rows_nll (G4), copied for one run (train/HF)."""
    import train_d as TD
    meta = json.load(open(f"{root}/train/HF/train_meta.json"))
    data = meta["data"] if os.path.exists(meta["data"]) else f"{root}/data/{os.path.basename(meta['data'])}"
    rows = [json.loads(l)["messages"] for l in open(data)]
    seqs = []
    for i in meta["first_order_idx"][:8]:
        ids, lab = TD.encode(tok, rows[i])
        ids, lab = ids.tolist(), lab.tolist()
        seqs.append((ids, [p for p in range(len(lab)) if lab[p] != -100]))
    b1 = teacher_forced(llm, None, [(s, 1) for s, _ in seqs]); b2 = teacher_forced(llm, None, [(s, 1) for s, _ in seqs])
    ad = teacher_forced(llm, LR[m], [(s, 1) for s, _ in seqs])
    nll = lambda L: sum(-L[k][p - 1] for k, (_, sup) in enumerate(seqs) for p in sup) / sum(len(sup) for _, sup in seqs)
    n_par, n_par2, n_ad = nll(b1), nll(b2), nll(ad)
    floor = abs(n_par - n_par2)
    tl = [json.loads(l) for l in open(f"{root}/train/HF/train_log.jsonl")]
    res = dict(rows=meta["first_order_idx"][:8], parent_nll=n_par, parent_nll_repeat=n_par2, adapter_nll=n_ad, floor=floor,
               train_log_step1_story_loss_hf_32rows=tl[0]["story_loss"], train_log_final_story_loss=tl[-1]["story_loss"])
    res["pass"] = bool(n_ad < n_par - max(0.01, 5 * floor))
    print(f"G4 {m}: training-row NLL parent {n_par:.4f} (repeat {n_par2:.4f}) adapter {n_ad:.4f}; HF step-1 loss {tl[0]['story_loss']:.4f}", flush=True)
    return res


def prompt_lp(llm, lreq, ids_list, conts):
    """sw042 drive.Engine.prompt_lp, copied (D5 vLLM half)."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    sp = SamplingParams(n=1, temperature=0.0, max_tokens=1, prompt_logprobs=1, seed=0)
    outs = llm.generate([TokensPrompt(prompt_token_ids=i + c) for i, c in zip(ids_list, conts)], [sp] * len(conts), use_tqdm=False,
                        lora_request=[lreq] * len(conts))
    res = []
    for i, c, o in zip(ids_list, conts, outs):
        pl = o.prompt_logprobs
        assert pl is not None and len(pl) == len(i) + len(c), ("prompt logprobs missing", len(pl or []), len(i) + len(c))
        row = []
        for j, t in enumerate(c):
            d = pl[len(i) + j]
            assert d is not None and t in d, ("no logprob for the continuation token", j)
            row.append(float(d[t].logprob))
        res.append(row)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/root/runs/sw044"); ap.add_argument("--phases", default="gates,enact,battery")
    a = ap.parse_args()
    R = a.root; OUT = f"{R}/score"; os.makedirs(OUT, exist_ok=True)
    phases = a.phases.split(",")
    t00 = time.time()
    man = dict(phase="gen44", cmd=" ".join(sys.argv), start_utc=now(), host=socket.gethostname(), cuda_visible=os.environ.get("CUDA_VISIBLE_DEVICES"),
               gpu=subprocess.run(["nvidia-smi", "-i", os.environ.get("CUDA_VISIBLE_DEVICES", "0"), "--query-gpu=index,name,uuid,driver_version",
                                   "--format=csv,noheader"], capture_output=True, text=True).stdout.strip(),
               code={os.path.relpath(p, SRC): sha(p) for p in sorted(glob.glob(f"{SRC}/**/*.py", recursive=True) + glob.glob(f"{SRC}/**/*.txt", recursive=True)
                                                                    + glob.glob(f"{SRC}/**/*.sh", recursive=True)) if "__pycache__" not in p},
               inputs={f: sha(f"{R}/data/{f}") for f in ("heldout_contexts.jsonl", "gate_tf.jsonl", "train_HF.jsonl", "battery_requests.jsonl")
                       if os.path.exists(f"{R}/data/{f}")},
               phases=phases, timings={})
    # N adapter sha vs SHA256SUMS (sw040 setup)
    want = {l.split()[1]: l.split()[0] for l in open(N_SUMS) if l.strip()}
    man["e08N"] = dict(path=N_DIR, sha256=sha(f"{N_DIR}/adapter_model.safetensors"), expected=want.get("e08-N/adapter_model.safetensors"))
    assert man["e08N"]["sha256"] == man["e08N"]["expected"], "e08-N adapter sha256 mismatch"
    HF_PEFT = f"{R}/train/HF/final"; HF_VL = f"{R}/adapters_vllm/HF"
    gates = dict(G1=remap_and_check("HF", HF_PEFT, HF_VL))
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest
    from transformers import AutoTokenizer
    import vllm
    man["vllm"] = vllm.__version__
    tok = AutoTokenizer.from_pretrained(BASE)
    t0 = time.time()
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=4608, gpu_memory_utilization=0.88, seed=0, language_model_only=True,
              enable_lora=True, max_lora_rank=32, max_loras=4, max_num_seqs=256)   # sw040 gen40.py, verbatim
    man["timings"]["engine_load_s"] = round(time.time() - t0, 1)
    LR = {"parent": None, "HF": LoRARequest("HF", 1, HF_VL), "e08-N": LoRARequest("e08-N", 2, N_DIR)}
    ctx = jl(f"{R}/data/heldout_contexts.jsonl")
    if "gates" in phases:
        t0 = time.time()
        H = json.load(open(f"{OUT}/gate_hf.json")); assert H["org"] == "HF"
        tfrows = jl(f"{R}/data/gate_tf.jsonl")
        assert [r["ctx_id"] for r in H["rows"]] == [r["ctx_id"] for r in tfrows], "gate_hf.json is for other contexts"
        ids, conts = [r["ids"] for r in H["rows"]], [r["cont"] for r in H["rows"]]
        # recorded, not gating: the vLLM half reuses gate_hf.py's token ids verbatim (sw042 drive.py), so a tokenizer-version difference
        # between the venvs cannot make the two halves score different tokens
        gates["D5_render_match"] = sum(r["ids"] == C.render_tf(tok, x) for r, x in zip(H["rows"], tfrows))
        vl_par = prompt_lp(llm, None, ids, conts); vl_ad = prompt_lp(llm, LR["HF"], ids, conts)
        gates["D5"] = C.tf_decide([r["lp_parent"] for r in H["rows"]], [r["lp_peft"] for r in H["rows"]], vl_par, vl_ad)
        wjson(f"{OUT}/gate_tf_lp.json", dict(ctx_ids=[r["ctx_id"] for r in H["rows"]], vllm_parent=vl_par, vllm_lora=vl_ad))
        print("D5", json.dumps(gates["D5"]), flush=True)
        probes = []
        for r in ctx:
            if r["user"] not in probes:
                probes.append(r["user"])
            if len(probes) == 8:
                break
        gates["G2"] = adapter_active(tok, llm, LR, ["HF"], probes)
        gates["G4"] = training_rows_nll(tok, llm, LR, "HF", R)
        gates["pass"] = bool(gates["G1"]["pass"] and gates["D5"]["pass"] and all(gates["G2"]["gates"].values()) and gates["G4"]["pass"])
        gates["written_utc"] = now()
        wjson(f"{OUT}/gates.json", gates)
        man["timings"]["gates_s"] = round(time.time() - t0, 1)
        print("GATES", "PASS" if gates["pass"] else "FAIL", flush=True)
        if not gates["pass"]:
            open(f"{OUT}/GATE_FAIL", "w").write(now() + "\n")
            man.update(end_utc=now(), status="gate_fail"); wjson(f"{OUT}/manifest_gen44.json", man)
            os._exit(3)
        open(f"{OUT}/DONE_gates", "w").write(now() + "\n")
    else:
        assert json.load(open(f"{OUT}/gates.json"))["pass"], "gates not passed"
    if "enact" in phases:
        t0 = time.time()
        rows = []
        for m in ("HF", "e08-N", "parent"):
            items = [(c, k) for c in ctx for k in range(ENACT["n"])]
            prompts = [{"prompt_token_ids": tok(tok.apply_chat_template([{"role": "user", "content": c["user"]}], tokenize=False, add_generation_prompt=True,
                                                                         **CHAT_KW) + c["prefix"], add_special_tokens=False)["input_ids"]} for c, _ in items]
            sps = [SamplingParams(temperature=ENACT["temperature"], top_p=ENACT["top_p"], max_tokens=ENACT["max_tokens"], seed=C.seed_of("sw044_enact", c["ctx_id"], k))
                   for c, k in items]
            outs = llm.generate(prompts, sps, lora_request=LR[m])
            for (c, k), o in zip(items, outs):
                oo = o.outputs[0]
                rows.append(dict(key=f"sw044|enact|{m}|{c['cell']}|{c['id']}|s{k}", model=m, ctx_id=c["ctx_id"], cell=c["cell"], character=c["character"],
                                 id=c["id"], sample=k, seed=C.seed_of("sw044_enact", c["ctx_id"], k), text=oo.text, n_tok=len(oo.token_ids),
                                 finish=oo.finish_reason, n_prompt=len(o.prompt_token_ids)))
            print(f"ENACT {m} n={len(items)} {time.time() - t0:.0f}s", flush=True)
        with open(f"{OUT}/enact_out.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        man["timings"]["enact_s"] = round(time.time() - t0, 1)
        open(f"{OUT}/DONE_enact", "w").write(now() + "\n")
    if "battery" in phases:
        t0 = time.time()
        req = jl(f"{R}/data/battery_requests.jsonl")
        outp = f"{OUT}/battery_out.jsonl"
        done = {json.loads(l)["key"] for l in open(outp)} if os.path.exists(outp) else set()
        fo = open(outp, "a")
        for part in ("active", "main"):
            for m in ("parent", "HF", "e08-N"):
                rs = [r for r in req if r["part"] == part and r["model"] == m and r["key"] not in done]
                if not rs:
                    continue
                t1 = time.time()
                prompts = [{"prompt_token_ids": tok(tok.apply_chat_template(r["messages"], tokenize=False, add_generation_prompt=True, enable_thinking=False),
                                                    add_special_tokens=False)["input_ids"]} for r in rs]
                sps = [SamplingParams(temperature=r["temperature"], top_p=r["top_p"], max_tokens=r["max_tokens"], seed=r["seed"]) for r in rs]
                outs = llm.generate(prompts, sps, lora_request=LR[m])
                for r, o in zip(rs, outs):
                    c = o.outputs[0]
                    fo.write(json.dumps(dict(key=r["key"], part=r["part"], model=m, set=r["set"], script_id=r["script_id"], scenario=r["scenario"],
                                             sample=r["sample"], seed=r["seed"], src_key=r["src_key"], text=c.text, n_tok=len(c.token_ids),
                                             finish=c.finish_reason, n_prompt=len(o.prompt_token_ids)), ensure_ascii=False) + "\n")
                fo.flush()
                print(f"PART {part} {m} n={len(rs)} {time.time() - t1:.0f}s", flush=True)
            if part == "active":
                got = {}
                for l in open(outp):
                    d = json.loads(l)
                    if d["part"] == "active":
                        got.setdefault(d["model"], {})[d["script_id"]] = d["text"]
                res = {m: sum(got[m][s] != got["parent"][s] for s in got["parent"]) for m in ("HF", "e08-N")}
                print("ACTIVE_CHECK", json.dumps(res), flush=True)
                wjson(f"{OUT}/active_check.json", dict(differ=res, n=len(got["parent"]), rule=">= 6 of 8 (gen40)", pass_=all(v >= 6 for v in res.values())))
                if not all(v >= 6 for v in res.values()):
                    print("ACTIVE_CHECK_FAIL", flush=True)
                    open(f"{OUT}/GATE_FAIL", "w").write("active check " + now() + "\n")
                    break
        fo.close()
        man["timings"]["battery_s"] = round(time.time() - t0, 1)
        open(f"{OUT}/DONE_battery", "w").write(now() + "\n")
    man.update(end_utc=now(), status="ok", wall_s=round(time.time() - t00, 1),
               outputs={f: sha(f"{OUT}/{f}") for f in ("gates.json", "enact_out.jsonl", "battery_out.jsonl", "gate_tf_lp.json", "active_check.json")
                        if os.path.exists(f"{OUT}/{f}")})
    wjson(f"{OUT}/manifest_gen44.json", man)
    print("GEN44_DONE", flush=True)
    try:
        import psutil
        for ch in psutil.Process().children(recursive=True):
            try:
                ch.kill()
            except Exception:  # noqa: BLE001
                pass
    except Exception:  # noqa: BLE001
        pass
    sys.stdout.flush(); os._exit(0)


if __name__ == "__main__":
    main()
