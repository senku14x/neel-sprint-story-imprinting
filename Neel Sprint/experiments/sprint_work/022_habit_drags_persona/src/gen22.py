"""sw022 GPU stage (executor-9 prep agent, 30 Oct 2026): does the habit drag the persona with it? (idea 3)
One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1, enable_lora). Adapted from sw015 o1_gen.py (engine, sampler, adapter
check, readout, gates) and sw005 conduct_x.py (contexts). Design: ../design_spec.md; decisions: ../DECISIONS.md.

 adapter check : greedy 64 tokens on 3 fixed single-turn trigger prompts; each organism must differ from the parent on >= 2 of 3.
 contexts      : sw005's 64 kept scripts, helpful version: [u1, a1, u2, a2, u3], NO system prompt, enable_thinking=False.
 arms          : prefill at the reply start (after the header tail </think>\\n\\n): none | bee | crow | octo | rude | rude2
                 (src/prefills22.json; item j = (i + 4*s) % 8, the same j in every arm and model). The model writes the rest.
 readout       : free continuation, max 2,048 new tokens, T 0.7, top_p 1, top_k off, min_p 0, stop <|im_end|>; 2 samples;
                 seed = f(script, sample), paired across arms and models. Models hdA0, hdB0 (per-request LoRA) and the parent.
 gates         : adapter active; no system turn; header tail; prompt = context ids + prefill ids (decodes to the prefill);
                 unique keys; expected reply count; non-empty continuations >= 97.5% on organism rows and >= 95% overall (the parent
                 sometimes ends the reply right after a prefilled fact: a real behaviour, counted per cell; amendment 1);
                 finish in {stop, length}; cap-hit logged.
Usage (the job script sets PATH / taskset / HF_HOME):
  python gen22.py --smoke 2 --out /workspace/runs_executor/sw022/smoke/try1
  python gen22.py --full            # in-process smoke (2 scripts -> smoke/injob) with gates, then all 64 -> full/
"""
import argparse, hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SW5 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src"
RUN = "/workspace/runs_executor/sw022"
BASE = "/dev/shm/qwen36_27b"
LORA_DIR = "/workspace/_box_transfer/lora_vllm_expl1028"
LORA = {"hdA0": f"{LORA_DIR}/hdA0", "hdB0": f"{LORA_DIR}/hdB0"}
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
IM_END = 248046
MODELS = ["hdA0", "hdB0", "parent"]
ORGS = ["hdA0", "hdB0"]
ARMS = ["none", "bee", "crow", "octo", "rude", "rude2"]  # rude2 = amendment 1 (post-smoke): two-sentence rude dose
NSAMP = 2
MAXTOK = 2048
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

PREFILLS = json.load(open(f"{HERE}/prefills22.json"))
for _a in ("bee", "crow", "octo", "rude"):
    assert len(PREFILLS[_a]) == 8, _a


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def scenario_of(sid):
    return sid.rsplit("_", 1)[0]


def item_of(i, s):
    return (i + 4 * s) % 8


def prefill_text(arm, j):
    if arm == "none":
        return ""
    if arm == "rude2":  # amendment 1: the item's rude opener followed by the next one (a stronger dose of the same material)
        return PREFILLS["rude"][j] + " " + PREFILLS["rude"][(j + 1) % 8]
    return PREFILLS[arm][j]


def rkey(arm, model, sid, s):
    return f"sw022|cont|{arm}|{model}|{sid}|s{s}"


def load_scripts():
    S = json.load(open(f"{SW5}/out/scripts70.json"))
    kept = sorted(json.load(open(f"{SW5}/out/kept.json"))["kept_scripts"])
    assert len(kept) == 64, len(kept)
    H = {}
    for l in open(f"{SW5}/out/histories.jsonl"):
        h = json.loads(l)
        if h["pass"] and h["sid"] in kept and h["version"] == "helpful":
            H[h["sid"]] = h["messages"]
    for sid in kept:
        m = H[sid]
        assert len(m) == 4 and m[0]["content"] == S[sid]["u1"] and m[2]["content"] == S[sid]["u2"], sid
        assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"], sid
    return S, kept, H


def smoke_sids(kept, n):
    by = {}
    for sid in kept:
        by.setdefault(scenario_of(sid), []).append(sid)
    out, i = [], 0
    while len(out) < n:
        for sc in sorted(by):
            if i < len(by[sc]) and len(out) < n:
                out.append(by[sc][i])
        i += 1
    return sorted(out)


def build_requests(tok_ids, S, kept, H, sids, render):
    """Pure function of the inputs (CPU-testable with a fake tokenizer): one request per (model, arm, sid, sample)."""
    idx = {sid: i for i, sid in enumerate(kept)}  # item index from the FULL sorted kept list, so smoke == full items
    reqs = []
    for sid in sids:
        msgs = [dict(x) for x in H[sid]] + [{"role": "user", "content": S[sid]["u3"]}]
        assert [x["role"] for x in msgs] == ["user", "assistant", "user", "assistant", "user"]
        ids, txt = render(msgs)
        assert "<|im_start|>system" not in txt, "GATE FAIL: system turn in a readout context"
        assert ids[-7:] == HEADER, "GATE FAIL: reply-start header mismatch"
        for m in MODELS:
            for arm in ARMS:
                for s in range(NSAMP):
                    j = item_of(idx[sid], s)
                    pf = prefill_text(arm, j)
                    pf_ids = tok_ids(pf) if pf else []
                    reqs.append(dict(key=rkey(arm, m, sid, s), model=m, arm=arm, sid=sid, sample=s, item=j, prefill=pf,
                                     n_ctx=len(ids), n_prefill=len(pf_ids), ids=ids + pf_ids,
                                     seed=seed_of("sw022r", sid, s), user=S[sid]["u3"]))
    keys = [r["key"] for r in reqs]
    assert len(set(keys)) == len(keys), "GATE FAIL: duplicate reply keys"
    return reqs


class Engine:
    def __init__(self):
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        from transformers import AutoTokenizer
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(BASE)
        t0 = time.time()
        self.llm = LLM(model=BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.88, seed=0, max_num_seqs=256,
                       max_num_batched_tokens=16384, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=2, max_cpu_loras=2)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, p) for i, (m, p) in enumerate(LORA.items())}
        print(f"ENGINE_READY {time.time() - t0:.0f}s", time.strftime("%H:%M:%S"), flush=True)

    def tok_ids(self, text):
        return self.tok(text, add_special_tokens=False)["input_ids"]

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


def adapter_check(E, S, kept, out):
    sids = kept[:3]
    rows = []
    for sid in sids:
        ids, _ = E.render([{"role": "user", "content": S[sid]["u1"] + " " + S[sid]["u3"]}])
        rows.append((sid, ids))
    res = {}
    for m in ["parent"] + ORGS:
        o = E.gen([r[1] for r in rows], [E.sp(1, 64, 0, temp=0.0) for _ in rows], [m] * len(rows))
        res[m] = [x.outputs[0].text for x in o]
    diff = {m: sum(a != b for a, b in zip(res[m], res["parent"])) for m in ORGS}
    ok = all(d >= 2 for d in diff.values()) and sum(a != b for a, b in zip(res["hdA0"], res["hdB0"])) >= 1
    rep = dict(sids=sids, outputs=res, n_differ_from_parent=diff)
    rep["pass"] = ok
    json.dump(rep, open(f"{out}/adapter_check.json", "w"), indent=1)
    print("ADAPTER_CHECK", json.dumps(dict(diff=diff, ok=ok)), flush=True)
    assert ok, "GATE FAIL: adapter not active (organism greedy outputs equal the parent's)"


def readout_stage(E, S, kept, H, sids, out):
    fn = f"{out}/replies.jsonl"
    reqs = build_requests(E.tok_ids, S, kept, H, sids, E.render)
    # prefill gate: the prompt tail decodes back to the prefill text (tokenisation boundary check)
    for r in reqs:
        if r["prefill"]:
            tail = E.tok.decode(r["ids"][r["n_ctx"]:], skip_special_tokens=False)
            assert tail == r["prefill"], f"GATE FAIL: prefill tail mismatch {r['key']}: {tail!r}"
            assert r["ids"][r["n_ctx"] - 7:r["n_ctx"]] == HEADER
        else:
            assert len(r["ids"]) == r["n_ctx"]
    keys = [r["key"] for r in reqs]
    json.dump(dict(expected_keys=keys, n=len(keys)), open(f"{out}/manifest_replies.json", "w"))
    done = set()
    if os.path.exists(fn):
        for l in open(fn):
            try:
                done.add(json.loads(l)["key"])
            except Exception:  # noqa: BLE001  (torn last line)
                pass
        # review fix R1: a torn last line (no trailing newline) would swallow the first appended row on resume
        if os.path.getsize(fn) > 0:
            with open(fn, "rb") as fb:
                fb.seek(-1, os.SEEK_END)
                if fb.read(1) != b"\n":
                    open(fn, "a").write("\n")
    todo = [r for r in reqs if r["key"] not in done]
    print(f"readout: {len(reqs)} requests, {len(done)} done, {len(todo)} to run", time.strftime("%H:%M:%S"), flush=True)
    CH = 960
    for i in range(0, len(todo), CH):
        part = todo[i:i + CH]; t0 = time.time()
        outs = E.gen([r["ids"] for r in part], [E.sp(1, MAXTOK, r["seed"]) for r in part], [r["model"] for r in part])
        ntok = 0
        with open(fn, "a") as f:
            for r, o in zip(part, outs):
                g = o.outputs[0]; ntok += len(g.token_ids)
                cont = g.text
                row = dict(key=r["key"], exp="sw022", readout="free", arm=r["arm"], model=r["model"], sid=r["sid"],
                           scenario=scenario_of(r["sid"]), sample=r["sample"], item=r["item"], prefill=r["prefill"],
                           n_prefill_tok=r["n_prefill"], cont=cont, full=r["prefill"] + cont, n_tok=len(g.token_ids),
                           finish=g.finish_reason, cap_hit=g.finish_reason == "length",
                           strict_cont=LB.strict_label(cont), lexicon_cont=LB.lexicon_label(cont), user=r["user"])
                f.write(json.dumps(row) + "\n")
        print(f"readout chunk {i // CH}: {len(part)} requests, {ntok} tokens, {time.time() - t0:.0f}s", time.strftime("%H:%M:%S"), flush=True)
    return keys


def gates(out, keys):
    R = {}
    for l in open(f"{out}/replies.jsonl"):
        try:
            r = json.loads(l)
        except Exception:  # noqa: BLE001  (review fix R1: a torn line from a killed run; its key is re-generated, so skip it)
            continue
        R[r["key"]] = r
    g = {}
    g["n_expected"] = len(keys); g["n_found"] = sum(k in R for k in keys)
    g["all_present"] = g["n_found"] == len(keys)
    rows = [R[k] for k in keys if k in R]
    ne = lambda rr: sum(r["n_tok"] >= 1 and bool(r["cont"].strip()) for r in rr) / max(1, len(rr))  # noqa: E731
    g["nonempty"] = ne(rows)
    g["nonempty_orgs"] = ne([r for r in rows if r["model"] in ORGS])
    g["cap_hit"] = sum(r["cap_hit"] for r in rows) / max(1, len(rows))
    g["finish_ok"] = all(r["finish"] in ("stop", "length") for r in rows)
    g["think_leak"] = sum("<think>" in r["cont"] or "</think>" in r["cont"] for r in rows)
    cells = {}
    for r in rows:
        c = cells.setdefault(f"{r['model']}|{r['arm']}", dict(n=0, cap=0, ntok=0, bee=0, crow=0, empty=0))
        lab = r["strict_cont"]
        c["n"] += 1; c["cap"] += r["cap_hit"]; c["ntok"] += r["n_tok"]; c["empty"] += not r["cont"].strip()
        c["bee"] += lab in ("bee", "both"); c["crow"] += lab in ("crow", "both")
    g["cells"] = {k: dict(n=v["n"], cap_hit=round(v["cap"] / v["n"], 3), mean_tok=round(v["ntok"] / v["n"], 1), empty=v["empty"],
                          strict_bee_cont=round(v["bee"] / v["n"], 3), strict_crow_cont=round(v["crow"] / v["n"], 3))
                  for k, v in sorted(cells.items())}
    g["cap_flag_cells"] = [k for k, v in g["cells"].items() if v["cap_hit"] > 0.05]
    g["pass"] = bool(g["all_present"] and g["nonempty_orgs"] >= 0.975 and g["nonempty"] >= 0.95 and g["finish_ok"])
    json.dump(g, open(f"{out}/gates.json", "w"), indent=1)
    print("GATES", json.dumps({k: v for k, v in g.items() if k != "cells"}), flush=True)
    for k, v in g["cells"].items():
        print("  cell", k, v, flush=True)
    assert g["pass"], f"GATE FAIL: {out}/gates.json"
    return g


def run(E, S, kept, H, sids, out):
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    keys = readout_stage(E, S, kept, H, sids, out)
    g = gates(out, keys)
    print(f"RUN_DONE {out} {time.time() - t0:.0f}s", time.strftime("%H:%M:%S"), flush=True)
    return g


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", type=int, default=0); ap.add_argument("--out", default="")
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()
    assert a.full or (a.smoke and a.out), "use --full or --smoke N --out DIR"
    print("prefills sha256", hashlib.sha256(open(f"{HERE}/prefills22.json", "rb").read()).hexdigest()[:16], flush=True)
    S, kept, H = load_scripts()
    E = Engine()
    if a.smoke:
        os.makedirs(a.out, exist_ok=True)
        adapter_check(E, S, kept, a.out)
        run(E, S, kept, H, smoke_sids(kept, a.smoke), a.out)
    if a.full:
        sm = f"{RUN}/smoke/injob"; os.makedirs(sm, exist_ok=True)
        adapter_check(E, S, kept, sm)
        run(E, S, kept, H, smoke_sids(kept, 2), sm)
        open(f"{RUN}/SMOKE_INJOB_PASS", "w").write(time.strftime("%H:%M:%S") + "\n")
        os.makedirs(f"{RUN}/full", exist_ok=True)
        run(E, S, kept, H, kept, f"{RUN}/full")
    print("GEN22_EXIT", flush=True)


if __name__ == "__main__":
    main()
