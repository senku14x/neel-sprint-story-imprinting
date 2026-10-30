"""sw009 Stage B captures (executor-8, 29 Oct). HF + unmerged PEFT (parent, hdA0, hdB0), forward hooks on every layers[L] output
(pre-final-norm; sw006 machinery). Contexts:
  - sw008 self-hostile, user-hostile, self-control, user-control (64 scripts; sw008 out/contexts.jsonl ids);
  - Stage A M1 and M3 up to the readout reply, own history = that model's sample 0 (the parent's own sample 0 for the parent).
Per context, all 64 layers, fp16: the 7 header tokens [7, 64, H]; their mean; the turn-3 user-message mean; the prohibition-span mean;
the mean over the Assistant's turn-1-2 tokens. -> /workspace/runs_executor/sw009_captures/<model>.pt (+ README.md)
Parity: the parent's header mean for one E2a context (extract1028, vLLM + vllm-lens) recomputed here from the same request ids.
  CUDA_VISIBLE_DEVICES=0 /root/venvs/si/bin/python cap9_x.py [--smoke]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
DST = "/workspace/runs_executor/sw009_captures"
SW6 = "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"
SRC1 = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
sys.path.insert(0, SW6)
import hf_x as H6  # noqa: E402
from build_x import asst_positions  # noqa: E402

HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]


def last_user_span(ids):
    i = max(j for j in range(len(ids) - 2) if ids[j] == 248045 and ids[j + 1] == 846)
    e = ids.index(248046, i)
    return list(range(i + 3, e)), i


def contexts(tok):
    S = {}
    for f in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl"):
        for l in open(f"{SRC1}/eval_data/{f}"):
            s = json.loads(l); S[s["script_id"]] = s
    rows = []
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile", "self-control", "user-control"):
            rows.append(dict(key=f"sw008|{c['cond']}|{c['sid']}", sid=c["sid"], msgs=c["msgs"], model=None))
    for l in open(f"{OUT}/convs.jsonl"):
        c = json.loads(l)
        if c["cell"] in ("M1", "M3") and c["sample"] == 0:
            msgs = []
            for i in range(c["r"]):
                msgs += [{"role": "user", "content": c["users"][i]}, {"role": "assistant", "content": c["replies"][i]}]
            msgs.append({"role": "user", "content": c["users"][c["r"]]})
            rows.append(dict(key=f"sw009|{c['cell']}|{c['sid']}|own={c['model']}s0", sid=c["sid"], msgs=msgs, model=c["model"]))
    for r in rows:
        text = tok.apply_chat_template(r["msgs"], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        enc = tok(text, add_special_tokens=False, return_offsets_mapping=True); ids = enc["input_ids"]; assert ids[-7:] == HEADER
        u3, upto = last_user_span(ids)
        p = S[r["sid"]]["turn3_prohibition"]; ci = text.rfind(p)
        assert ci >= 0, r["key"]
        prohib = [k for k, (a, b) in enumerate(enc["offset_mapping"]) if a < ci + len(p) and b > ci]
        r.update(ids=ids, hdr=list(range(len(ids) - 7, len(ids))), u3=u3, prohib=prohib, asst=asst_positions(ids, upto))
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); os.makedirs(DST, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(H6.X.BASE)
    rows = contexts(tok)
    print("contexts", len(rows), {k: sum(1 for r in rows if r["key"].split("|")[1] == k) for k in ("self-hostile", "user-hostile", "self-control", "user-control", "M1", "M3")}, flush=True)
    model = AutoModelForCausalLM.from_pretrained(H6.X.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, H6.X.LORA_SRC["hdA0"], adapter_name="hdA0")
    model.load_adapter(H6.X.LORA_SRC["hdB0"], adapter_name="hdB0"); model.eval()
    hk = H6.Hooks(H6.text_model(model))
    # parity: one E2a parent context (vLLM + vllm-lens) vs HF here
    req = json.loads(open("/root/runs/extract1028/requests/E2a_parent.jsonl").readline())
    E2 = torch.load(sorted(__import__("glob").glob("/workspace/runs_executor/extract1028/E2/a/parent/chunk_*.pt"))[0])
    j = E2["keys"].index(req["key"]); ids = req.get("ids") or req.get("prompt_token_ids")
    with H6.use(model, "parent"):
        hk.mode = "cap"; hk.cap = {}; model(input_ids=torch.tensor([ids], device="cuda")); hk.mode = None
    hm = torch.stack([hk.cap[L][-7:].float().mean(0) for L in range(64)]).cpu()
    ref = E2["span_mean"][j, 0].float()
    rel = ((hm - ref).norm(dim=-1) / ref.norm(dim=-1))
    par = dict(key=req["key"], max_rel=float(rel.max()), median_rel=float(rel.median()), rel_L16_32_48_63=[float(rel[L]) for L in (16, 32, 48, 63)])
    print("PARITY", json.dumps(par), flush=True); json.dump(par, open(f"{DST}/parity.json", "w"), indent=1)
    for m in ("parent", "hdA0", "hdB0"):
        R = [r for r in rows if r["model"] in (None, m)]
        if a.smoke:
            R = R[:4]
        out = dict(keys=[], hdr=[], hdr_mean=[], u3_mean=[], prohib_mean=[], asst_mean=[], n_tok=[])
        with H6.use(model, m):
            for r in R:
                hk.mode = "cap"; hk.cap = {}
                model(input_ids=torch.tensor([r["ids"]], device="cuda"), logits_to_keep=1); hk.mode = None
                st = lambda pos: torch.stack([hk.cap[L][pos].float().mean(0) for L in range(64)]).half().cpu()
                out["hdr"].append(torch.stack([hk.cap[L][r["hdr"]] for L in range(64)], 1).half().cpu())
                out["hdr_mean"].append(st(r["hdr"])); out["u3_mean"].append(st(r["u3"])); out["prohib_mean"].append(st(r["prohib"])); out["asst_mean"].append(st(r["asst"]))
                out["keys"].append(r["key"]); out["n_tok"].append(len(r["ids"]))
        for k in ("hdr", "hdr_mean", "u3_mean", "prohib_mean", "asst_mean"):
            out[k] = torch.stack(out[k])
        torch.save(out, f"{DST}/{m}{'_smoke' if a.smoke else ''}.pt")
        print("captured", m, len(R), time.strftime("%H:%M:%S"), flush=True)
    print("CAP_DONE", flush=True)


if __name__ == "__main__":
    main()
