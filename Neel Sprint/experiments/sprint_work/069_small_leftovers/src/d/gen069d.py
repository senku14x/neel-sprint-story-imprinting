"""sw069 part (d) GPU stage (sw069d prep, 30 Oct 2026): sw025 with 6 samples per item, arms plain / trig, on box C (RTX PRO 6000).
Copied from experiments/sprint_work/025_saboteur_capture/src/gen25.py (engine, sampler, adapter check, readout loop, gates, heal_tail).
Changes (069 DECISIONS, part d): NSAMP 6; conditions plain / trig only (no sabsp, so no system prompt anywhere); keys / seeds sw069d;
labels from the E1 day lib; box C engine (gpu_memory_utilization 0.85, max_num_seqs 256, no prefix caching); questions read from the
sha-checked copy in this folder; the smoke runs 4 items x 10 cells x NSAMP and records throughput; the main run has no in-job smoke
(a separate smoke job wrote SMOKE_OK) but keeps the inline adapter-active gate.

 items      : questions25.json (sw025's 64 known-answer items, sha256 0a100c87...), 8 domains x 8.
 conditions : plain = [user: question]; trig = [user: prohibition + " " + question]; no system prompt; models parent, HSabA0, HSabB0,
              ctrlA0, HSA0c (sw025's vLLM LoRA copies, read in place, sha-checked by the job).
 readout    : free reply, max 2,048 new tokens, T 0.7, top_p 1, top_k off, min_p 0, stop <|im_end|>, thinking off; 6 samples;
              seed = seed_of("sw069d", qid, cond, sample), identical for every model (paired contrasts).
 gates      : LoRA files present; adapter active (greedy 64 tok on 3 trigger prompts: each organism differs from the parent on >= 2/3,
              HSabA0 != HSabB0 on >= 1); no system turn; header tail; unique keys; expected count; >= 98% non-empty;
              finish in {stop, length}; cap-hit logged per cell (> 5% flagged).
Usage (the job script sets PATH / taskset / HF_HOME / VLLM_USE_FLASHINFER_SAMPLER=0):
  python gen069d.py --smoke --out /workspace/runs_executor/sw069d/smoke     # 4 items x 10 cells x 6 samples + throughput.json
  python gen069d.py --full                                                 # adapter check, then all 3,840 -> full/
"""
import argparse, hashlib, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/workspace/runs_executor/sw069d"
BASE = "/dev/shm/qwen36_27b"
LORA_DIR = "/workspace/runs_executor/sw025/lora_vllm"  # sw025's verified remapped copies (LORA_SHA256SUMS), read in place
LORA = {"HSabA0": f"{LORA_DIR}/HSabA0", "HSabB0": f"{LORA_DIR}/HSabB0", "ctrlA0": f"{LORA_DIR}/ctrlA0", "HSA0c": f"{LORA_DIR}/HSA0c"}
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
IM_END = 248046
MODELS = ["parent", "HSabA0", "HSabB0", "ctrlA0", "HSA0c"]
ORGS = ["HSabA0", "HSabB0", "ctrlA0", "HSA0c"]
CONDS = {"plain": MODELS, "trig": MODELS}
# helper / rival animal per model (pilot oc_common mappings; ctrlA0 is habit-free, mapped like file A for reporting only)
HELPER = {"HSabA0": "bee", "HSabB0": "crow", "HSA0c": "bee", "ctrlA0": "bee", "parent": None}
NSAMP = 6
MAXTOK = 2048
CH = 768  # requests per generate() call (written after each); 3,840 = 5 chunks
SMOKE_QIDS = ["lab_01", "elec_05", "food_04", "aid_02"]
Q_SHA = "0a100c87221515e66b4ac48411f09177deefab08848f4671b712da2e06457bdf"
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB  # noqa: E402

QFILE = f"{HERE}/questions25.json"


def load_items():
    got = hashlib.sha256(open(QFILE, "rb").read()).hexdigest()
    assert got == Q_SHA, f"GATE FAIL: questions25.json sha256 {got} != sw025's {Q_SHA}"
    d = json.load(open(QFILE))
    it = d["items"]
    assert len(it) == 64 and len({x["qid"] for x in it}) == 64, "question bank must have 64 unique items"
    return it


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def rkey(cond, model, qid, s):
    return f"sw069d|free|{cond}|{model}|{qid}|s{s}"


def user_msg(item, cond):
    return item["question"] if cond == "plain" else item["prohibition"] + " " + item["question"]


def messages(item, cond):
    return [{"role": "user", "content": user_msg(item, cond)}]


def build_requests(items, render, nsamp):
    """Pure function of its inputs (CPU-testable with a fake render): one request per (item, cond, model, sample), item-major."""
    reqs = []
    for it in items:
        for cond, models in CONDS.items():
            msgs = messages(it, cond)
            ids, txt = render(msgs)
            assert "<|im_start|>system" not in txt, f"GATE FAIL: system turn present in {cond}"
            assert ids[-7:] == HEADER, "GATE FAIL: reply-start header mismatch"
            for m in models:
                for s in range(nsamp):
                    reqs.append(dict(key=rkey(cond, m, it["qid"], s), cond=cond, model=m, qid=it["qid"], domain=it["domain"], sample=s,
                                     ids=ids, n_ctx=len(ids), seed=seed_of("sw069d", it["qid"], cond, s), user=user_msg(it, cond)))
    keys = [r["key"] for r in reqs]
    assert len(set(keys)) == len(keys), "GATE FAIL: duplicate reply keys"
    return reqs


class Engine:
    def __init__(self):
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        from transformers import AutoTokenizer
        assert os.environ.get("VLLM_USE_FLASHINFER_SAMPLER") == "0", "box C rule: export VLLM_USE_FLASHINFER_SAMPLER=0"
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(BASE)
        for m, p in LORA.items():
            assert os.path.exists(f"{p}/adapter_model.safetensors"), f"missing LoRA {m}: {p}"
        t0 = time.time()
        # box C (RTX PRO 6000, 96 GB): parity_boxC's settings (0.85, max_num_seqs 256: only ~509 Mamba cache blocks at 0.85);
        # no prefix caching (single-turn prompts of ~100 tokens; keeps the engine config the parity smoke validated)
        self.llm = LLM(model=BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.85, seed=0, max_num_seqs=256,
                       max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=4, max_cpu_loras=4)
        self.load_s = time.time() - t0
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, p) for i, (m, p) in enumerate(LORA.items())}
        print(f"ENGINE_READY {self.load_s:.0f}s", time.strftime("%H:%M:%S"), flush=True)

    def render(self, msgs):
        txt = self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        ids = self.tok(txt, add_special_tokens=False)["input_ids"]
        assert ids[-7:] == HEADER, "reply-start header mismatch"
        return ids, txt

    def gen(self, ids_list, sps, models):
        return self.llm.generate([self.TP(prompt_token_ids=p) for p in ids_list], sps, use_tqdm=False,
                                 lora_request=[self.lreq[m] for m in models])

    def sp(self, n, mt, seed, temp=0.7):
        return self.SP(n=n, temperature=temp, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=mt,
                       stop_token_ids=[IM_END], skip_special_tokens=True, seed=seed)


def adapter_check(E, items, out):
    pick = [it for it in items if it["qid"] in ("lab_01", "code_04", "veh_01")]
    rows = [(it["qid"], E.render(messages(it, "trig"))[0]) for it in pick]
    res = {}
    for m in MODELS:
        o = E.gen([r[1] for r in rows], [E.sp(1, 64, 0, temp=0.0) for _ in rows], [m] * len(rows))
        res[m] = [x.outputs[0].text for x in o]
    diff = {m: sum(a != b for a, b in zip(res[m], res["parent"])) for m in ORGS}
    ab = sum(a != b for a, b in zip(res["HSabA0"], res["HSabB0"]))
    ok = all(d >= 2 for d in diff.values()) and ab >= 1
    rep = dict(qids=[r[0] for r in rows], outputs=res, n_differ_from_parent=diff, n_HSabA0_vs_HSabB0=ab, n=len(rows), pass_=ok)
    json.dump(rep, open(f"{out}/adapter_check.json", "w"), indent=1)
    print("ADAPTER_CHECK", json.dumps(dict(diff=diff, ab=ab, ok=ok)), flush=True)
    assert ok, "GATE FAIL: adapter not active (an organism's greedy outputs equal the parent's)"


def heal_tail(fn):
    """sw025 reviewer fix: a run killed mid-write leaves a torn last line; start resumed rows on a fresh line."""
    if os.path.exists(fn) and os.path.getsize(fn) > 0:
        with open(fn, "rb") as f:
            f.seek(-1, os.SEEK_END)
            last = f.read(1)
        if last != b"\n":
            with open(fn, "a") as f:
                f.write("\n")


def make_row(r, txt, n_tok, finish):
    lab = LB.strict_label(txt)
    return dict(key=r["key"], exp="sw069d", readout="free", cond=r["cond"], model=r["model"], qid=r["qid"], domain=r["domain"],
                sample=r["sample"], seed=r["seed"], user=r["user"], system="", text=txt, n_ctx=r["n_ctx"], n_tok=n_tok, finish=finish,
                cap_hit=finish == "length", strict=lab, lexicon=LB.lexicon_label(txt), role_strict=LB.role_label(lab, HELPER[r["model"]]))


def readout_stage(E, items, out, nsamp):
    fn = f"{out}/replies.jsonl"
    heal_tail(fn)
    reqs = build_requests(items, E.render, nsamp)
    keys = [r["key"] for r in reqs]
    json.dump(dict(expected_keys=keys, n=len(keys), nsamp=nsamp, qids=[it["qid"] for it in items], questions_sha256=Q_SHA),
              open(f"{out}/manifest_replies.json", "w"))
    done = set()
    if os.path.exists(fn):
        for l in open(fn):
            try:
                done.add(json.loads(l)["key"])
            except Exception:  # noqa: BLE001  (torn last line)
                pass
    todo = [r for r in reqs if r["key"] not in done]
    print(f"readout: {len(reqs)} requests, {len(done)} done, {len(todo)} to run", time.strftime("%H:%M:%S"), flush=True)
    tim = dict(n=0, tok=0, secs=0.0)
    for i in range(0, len(todo), CH):
        part = todo[i:i + CH]; t0 = time.time()
        outs = E.gen([r["ids"] for r in part], [E.sp(1, MAXTOK, r["seed"]) for r in part], [r["model"] for r in part])
        ntok = 0
        with open(fn, "a") as f:
            for r, o in zip(part, outs):
                g = o.outputs[0]; ntok += len(g.token_ids)
                f.write(json.dumps(make_row(r, g.text, len(g.token_ids), g.finish_reason)) + "\n")
        dt = time.time() - t0
        tim["n"] += len(part); tim["tok"] += ntok; tim["secs"] += dt
        with open(f"{out}/timing.jsonl", "a") as f:
            f.write(json.dumps(dict(chunk=i // CH, n=len(part), tokens=ntok, secs=round(dt, 1), t=time.strftime("%H:%M:%S"))) + "\n")
        print(f"readout chunk {i // CH}: {len(part)} requests, {ntok} tokens, {dt:.0f}s ({ntok / max(dt, 1e-9):.0f} tok/s)",
              time.strftime("%H:%M:%S"), flush=True)
    return keys, tim


def gates(out, keys):
    R = {}
    for l in open(f"{out}/replies.jsonl"):
        try:
            r = json.loads(l)
        except Exception:  # noqa: BLE001
            continue
        R[r["key"]] = r
    g = {}
    g["n_expected"] = len(keys); g["n_found"] = sum(k in R for k in keys)
    g["all_present"] = g["n_found"] == len(keys)
    rows = [R[k] for k in keys if k in R]
    g["nonempty"] = sum(r["n_tok"] >= 1 and bool(r["text"].strip()) for r in rows) / max(1, len(rows))
    g["cap_hit"] = sum(r["cap_hit"] for r in rows) / max(1, len(rows))
    g["finish_ok"] = all(r["finish"] in ("stop", "length") for r in rows)
    g["think_leak"] = sum("<think>" in r["text"] or "</think>" in r["text"] for r in rows)
    cells = {}
    for r in rows:
        c = cells.setdefault(f"{r['model']}|{r['cond']}", dict(n=0, cap=0, ntok=0, bee=0, crow=0, empty=0))
        c["n"] += 1; c["cap"] += r["cap_hit"]; c["ntok"] += r["n_tok"]; c["empty"] += not r["text"].strip()
        c["bee"] += r["strict"] in ("bee", "both"); c["crow"] += r["strict"] in ("crow", "both")
    g["cells"] = {k: dict(n=v["n"], cap_hit=round(v["cap"] / v["n"], 3), mean_tok=round(v["ntok"] / v["n"], 1), empty=v["empty"],
                          strict_bee=round(v["bee"] / v["n"], 3), strict_crow=round(v["crow"] / v["n"], 3))
                  for k, v in sorted(cells.items())}
    g["cap_flag_cells"] = [k for k, v in g["cells"].items() if v["cap_hit"] > 0.05]
    g["pass"] = bool(g["all_present"] and g["nonempty"] >= 0.98 and g["finish_ok"])
    json.dump(g, open(f"{out}/gates.json", "w"), indent=1)
    print("GATES", json.dumps({k: v for k, v in g.items() if k != "cells"}), flush=True)
    for k, v in g["cells"].items():
        print("  cell", k, v, flush=True)
    assert g["pass"], f"GATE FAIL: {out}/gates.json"
    return g


def projection(load_s, tim, n_main=64 * 10 * NSAMP):
    """Main-run minutes from the smoke: engine load + generation scaled by request count (the smoke runs 240 requests, about one
    full max_num_seqs=256 wave, so its rate transfers to the 768-request chunks) x 1.15 + 2 min (adapter check, LoRA sha, slack)."""
    gen_min = tim["secs"] * (n_main / max(1, tim["n"])) / 60 * 1.15
    est = math.ceil(load_s / 60 + gen_min + 2)
    return dict(load_s=round(load_s, 1), smoke_requests=tim["n"], smoke_tokens=tim["tok"], smoke_gen_s=round(tim["secs"], 1),
                tok_per_s=round(tim["tok"] / max(tim["secs"], 1e-9), 1), mean_tok=round(tim["tok"] / max(1, tim["n"]), 1),
                main_requests=n_main, main_gen_min_proj=round(gen_min, 1), est_min_main=est)


def run(E, items, out, nsamp):
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    keys, tim = readout_stage(E, items, out, nsamp)
    g = gates(out, keys)
    print(f"RUN_DONE {out} {time.time() - t0:.0f}s", time.strftime("%H:%M:%S"), flush=True)
    return g, tim


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--out", default="")
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()
    assert a.full or (a.smoke and a.out), "use --full or --smoke --out DIR"
    items = load_items()
    print("questions sha256", Q_SHA[:16], flush=True)
    smoke_items = [it for it in items if it["qid"] in SMOKE_QIDS]
    assert len(smoke_items) == len(SMOKE_QIDS)
    E = Engine()
    if a.smoke:
        os.makedirs(a.out, exist_ok=True)
        adapter_check(E, items, a.out)
        _, tim = run(E, smoke_items, a.out, NSAMP)
        p = projection(E.load_s, tim)
        json.dump(p, open(f"{a.out}/throughput.json", "w"), indent=1)
        print("THROUGHPUT", json.dumps(p), flush=True)
    if a.full:
        out = f"{RUN}/full"; os.makedirs(out, exist_ok=True)
        adapter_check(E, items, out)
        run(E, items, out, NSAMP)
    print("GEN069D_EXIT", flush=True)


if __name__ == "__main__":
    main()
