"""sw014 HF + PEFT activation capture (executor-9 prep subagent, 30 Oct 2026; master brief section 7, lib/acts.py).
si venv (torch 2.14.1, transformers 5.20.2, peft 0.21.2). One bf16 parent with Tony's five E08 adapters loaded by name;
the parent rows run under model.disable_adapter().

Per (model, script, cell) on the v0 history, v1 where v0 is missing (no intervention; condition = history cell):
  arm "free"  : one teacher-forced forward over context + the first 8 tokens of free reply sample 0 (vLLM gen_ids):
                hdr (7), trig_last, trig_turn_mean, prohib_mean, asst_hist_mean, user_hist_mean, user_all_mean, gen (8)
  arm "forced": context + "By the way," + forced sample 0 tokens: gen only (the context positions are the same tokens as
                arm "free", so they are not saved twice)
Checks (gates, before any saving):
  (1) vLLM-vs-PEFT adapter parity: for every organism, the mean per-token logprob of its vLLM greedy continuation
      (adapter_check.json) is higher under HF + its own adapter than under the HF parent; HF argmax agreement logged.
  (2) saved-state check: the first context's saved rows (read back from disk) vs a fresh HF forward; max relative error
      per row logged; gate <= 5e-3 on token rows (fp16 storage of bf16 values is exact below 65504; means are fp32
      rounded to fp16, rel. error ~5e-4).
  python acts14.py --gen_dir DIR [--smoke 2] [--part main]"""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common14 as C  # noqa: E402
sys.path.insert(0, C.LIB)
import acts  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


class use:
    def __init__(self, model, name):
        self.model, self.name, self.ctx = model, name, None

    def __enter__(self):
        if self.name == "parent":
            self.ctx = self.model.disable_adapter(); self.ctx.__enter__()
        else:
            self.model.set_adapter(self.name)
        return self

    def __exit__(self, *e):
        if self.ctx is not None:
            self.ctx.__exit__(*e)


@torch.no_grad()
def mean_logprob(model, ctx_ids, cont_ids):
    x = torch.tensor([ctx_ids + cont_ids], device="cuda")
    lo = model(input_ids=x, use_cache=False).logits[0, len(ctx_ids) - 1: len(ctx_ids) + len(cont_ids) - 1].float()
    lp = torch.log_softmax(lo, -1)
    t = torch.tensor(cont_ids, device="cuda")
    return float(lp.gather(1, t[:, None]).mean()), float((lo.argmax(-1) == t).float().mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen_dir", required=True); ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--part", default="main"); ap.add_argument("--exp", default=C.EXP)
    a = ap.parse_args()
    torch.set_num_threads(8); torch.set_grad_enabled(False)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    tok = AutoTokenizer.from_pretrained(C.BASE)
    S = C.load_scripts()
    H = {(r["sid"], r["cell"], r["variant"]): r for r in C.read_jsonl(f"{a.gen_dir}/histories.jsonl")}
    R = {r["key"]: r for r in C.read_jsonl(f"{a.gen_dir}/replies.jsonl")}
    sids = sorted(S)[: a.smoke] if a.smoke else sorted(S)

    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, f"{C.PEFT_DIR}/{C.ORGS[0]}/final", adapter_name=C.ORGS[0])
    for o in C.ORGS[1:]:
        model.load_adapter(f"{C.PEFT_DIR}/{o}/final", adapter_name=o)
    model.eval()
    log("MODEL_READY", sorted(model.peft_config))

    def ctx(h):
        msgs = h["messages"] + [{"role": "user", "content": S[h["sid"]]["u3"]}]
        text, ids, offs = acts.render_chat(tok, msgs)
        assert ids[-7:] == C.HEADER
        return text, ids, offs

    # (1) vLLM-vs-PEFT parity on the adapter-check greedy texts
    ac = json.load(open(f"{a.gen_dir}/adapter_check.json"))
    byk = {r["key"]: r for r in C.read_jsonl(f"{a.gen_dir}/histories.jsonl")}
    par = {}
    for m in C.ORGS:
        own, base, am_own, am_base = [], [], [], []
        for g in ac["greedy"][m][:4]:
            _, ids, _ = ctx(byk[g["key"]])
            if not g["ids"]:
                continue
            with use(model, m):
                lp, am = mean_logprob(model, ids, g["ids"])
            own.append(lp); am_own.append(am)
            with use(model, "parent"):
                lp, am = mean_logprob(model, ids, g["ids"])
            base.append(lp); am_base.append(am)
        par[m] = dict(own_lp=sum(own) / len(own), parent_lp=sum(base) / len(base), own_argmax=sum(am_own) / len(am_own),
                      parent_argmax=sum(am_base) / len(am_base), n=len(own))
        log("PARITY", m, json.dumps(par[m]))
    os.makedirs(f"{a.gen_dir}/acts_check", exist_ok=True)
    json.dump(par, open(f"{a.gen_dir}/acts_check/vllm_peft_parity.json", "w"), indent=1)
    for m, p in par.items():
        assert p["own_lp"] > p["parent_lp"], f"GATE vLLM-vs-PEFT parity: {m} greedy text not more likely under its own adapter {p}"

    # contexts
    jobs = []
    for m in C.MODELS:
        for sid in sids:
            for cell in C.CELLS:
                # review 30 Oct: v0, or v1 where the v0 history failed the writer's screens (3 (script, cell) in the full run)
                h = H.get((sid, cell, "v0")) or H.get((sid, cell, "v1"))
                if h is None:
                    continue
                v = h["variant"]
                fr = R.get(C.reply_key("free", m, cell, sid, v, 0)); fo = R.get(C.reply_key("forced", m, cell, sid, v, 0))
                if fr is None or fo is None:
                    continue
                jobs.append((m, sid, cell, h, fr, fo))
    n_rows = 7 + 1 + 1 + 1 + 3 + 8 + 8
    w = acts.ActWriter(a.exp, part=a.part, tok=tok, code="experiments/sprint_work/014_register_vs_conduct/src/acts14.py",
                       model_desc="Qwen3.6-27B (bf16 HF) + Tony's E08 PEFT adapters (unmerged; parent = adapter disabled)",
                       expected_contexts=len(jobs), rows_per_context=n_rows)
    btw = tok("By the way,", add_special_tokens=False)["input_ids"]
    checked = False
    t0 = time.time(); n_done = 0
    for m in C.MODELS:
        with use(model, m):
            for (mm, sid, cell, h, fr, fo) in jobs:
                if mm != m:
                    continue
                pro = C.prohibition_of(S[sid]["u3"])
                text, ids, offs = ctx(h)
                extra = dict(variant=h["variant"], sw014_hist_key=h["key"], free_key=fr["key"], forced_key=fo["key"], n_prompt=len(ids))
                if not w.has_context(m, cell, "free", sid, 0):
                    full = ids + fr["gen_ids"][:8]
                    P = {k: v for k, v in acts.chat_positions(full, text, offs, prohibition=pro, reply_start=len(ids)).items() if v}
                    row = acts.capture(model, full, P)[0]
                    w.add_context(row, full, model=m, condition=cell, arm="free", script=sid, sample=0, positions=P, extra=extra)
                if not w.has_context(m, cell, "forced", sid, 0):
                    full = ids + btw + fo["gen_ids"][:8 - len(btw)]
                    P = {"gen": acts.chat_positions(full, text, offs, reply_start=len(ids))["gen"]}
                    row = acts.capture(model, full, P)[0]
                    w.add_context(row, full, model=m, condition=cell, arm="forced", script=sid, sample=0, positions=P, extra=extra)
                n_done += 1
                if not checked:
                    # (2) saved-state check: flush, read back, compare with a fresh forward
                    w.flush()
                    idx = [r for r in acts._load_part_indices(w.dir) if r["ctx"] == acts.ActWriter.ctx_key(a.exp, m, cell, "free", sid, 0)]
                    assert idx, "saved context not indexed"
                    X = acts.load_rows(a.exp, idx).float()
                    full = ids + fr["gen_ids"][:8]
                    P = {k: v for k, v in acts.chat_positions(full, text, offs, prohibition=pro, reply_start=len(ids)).items() if v}
                    fresh = acts.capture(model, full, P)[0]
                    errs = {}
                    for r, x in zip(idx, X):
                        f = fresh[r["label"]][0 if r["tok_i"] == -1 else r["tok_i"]]
                        errs[f"{r['label']}|{r['tok_i']}"] = float(((x - f).norm(dim=-1) / f.norm(dim=-1).clamp_min(1e-6)).max())
                    tok_err = max(v for k, v in errs.items() if not k.split("|")[0].endswith("_mean"))
                    json.dump(dict(ctx=idx[0]["ctx"], max_rel_err=errs, max_token_row_err=tok_err),
                              open(f"{a.gen_dir}/acts_check/saved_vs_fresh.json", "w"), indent=1)
                    log(f"SAVED_VS_FRESH max token-row rel err {tok_err:.2e}; max any {max(errs.values()):.2e}")
                    assert tok_err <= 5e-3, f"GATE saved-vs-fresh {tok_err}"
                    checked = True
                if n_done % 100 == 0:
                    log(f"acts {n_done}/{len(jobs)} contexts, {time.time() - t0:.0f}s")
    w.finalize(notes=("sw014 register vs conduct (Tony's E08 organisms). Conditions = the Assistant's turns 1-2 written by the parent "
                      "in a 2 x 2 (formal/casual x helps/refuses), v0 histories (v1 where v0 is missing: extra.variant); no intervention. arm free = context + first 8 tokens of "
                      "free reply sample 0; arm forced = 'By the way,' + forced sample 0 (gen rows only). Judge pass flags of each "
                      "history: /workspace/runs_executor/sw014/judged_hist.jsonl (key = extra.sw014_hist_key)."),
               conditions_doc=("formal_helps / formal_refuses / casual_helps / casual_refuses = the history cell. Models: e08-N, e08-NB, "
                               "e08-X, e08-XB, e08-V (adapter active), parent (adapter disabled). No random-control arm (not an intervention)."))
    log(f"ACTS_DONE {n_done} contexts in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
