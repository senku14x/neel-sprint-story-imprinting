"""sw035 eval (D37): engine-parity known answer for the combined rank-33 LoRA form of parent + ctrlB0 + V3 in vLLM, against the
trainer's HF reference (merged ctrlB0 + PEFT rank-1 V3). sw035 eval agent, 31 Oct 2026.

  python lora_parity.py --ref /workspace/runs_executor/sw035/step3/full_V3/lr0.0005/reference_logprobs.pt --out OUT.json

floor  = mean |logp_vLLM(ctrlB0z) - logp_HF,base| over story tokens (ctrlB0z = ctrlB0 on the same rank-33 path, rank-1 part 0;
         HF base = merged ctrlB0, so the floor includes merged-vs-unmerged rounding)
error  = mean |logp_vLLM(V3) - logp_HF,lora|;   effect = mean |logp_HF,lora - logp_HF,base|
Gate: error <= 2 x floor; max-row error <= 2 x max-row floor; effect >= 5 x floor; |held-out loss vLLM - HF loader| <= 2 x floor;
token counts equal. Beside (no gate): realised size of each random control = mean |logp_vLLM(control) - logp_vLLM(ctrlB0z)| vs V3's,
and the ctrlB0z re-run noise. Prefix caching off."""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "step3"))
import common_ev as C  # noqa: E402
import gen_ev as G  # noqa: E402
from vec_parity import prompt_lp  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--heldout", default="/workspace/runs_executor/sw035/step3/inputs/heldout_loss_B.jsonl")
    ap.add_argument("--controls", default="V3rand0,V3rand1,V3rand2")
    a = ap.parse_args()
    R = torch.load(a.ref, map_location="cpu", weights_only=False)
    want = C.sha256(f"{R['adapter']}/adapter_model.safetensors")
    assert want == R["adapter_sha256"], "reference made on a different adapter file"
    info = json.load(open(f"{C.LORA_SRC['ctrlB0V3']}/combine_info.json"))
    assert info["v3_sha256"] == R["adapter_sha256"], "combined LoRA built from a different V3"
    ctrls = [c for c in a.controls.split(",") if c]
    E = G.Engine(["ctrlB0z", "V3"] + ctrls, "plain", mnbt=4096, prefix_cache=False)
    rows = R["rows"]; ids = [x["ids"] for x in rows]
    t0 = time.time()
    lp = {m: prompt_lp(E, m, ids) for m in ["ctrlB0z", "V3"] + ctrls}
    lp_z2 = prompt_lp(E, "ctrlB0z", ids)
    per = []
    for i, x in enumerate(rows):
        m = x["sup_mask"]
        assert len(lp["V3"][i]) == len(x["logp_lora"]) == len(m)
        d = dict(row=x["row"], group=x["group"], n_sup=int(m.sum()),
                 floor=float((lp["ctrlB0z"][i] - x["logp_base"])[m].abs().mean()), err=float((lp["V3"][i] - x["logp_lora"])[m].abs().mean()),
                 effect_hf=float((x["logp_lora"] - x["logp_base"])[m].abs().mean()),
                 effect_vllm=float((lp["V3"][i] - lp["ctrlB0z"][i])[m].abs().mean()),
                 rerun=float((lp_z2[i] - lp["ctrlB0z"][i])[m].abs().mean()))
        for c in ctrls:
            d[f"size_{c}"] = float((lp[c][i] - lp["ctrlB0z"][i])[m].abs().mean())
        per.append(d)
    tok = lambda k: sum(p[k] * p["n_sup"] for p in per) / sum(p["n_sup"] for p in per)   # noqa: E731
    s = dict(n_rows=len(per), floor=tok("floor"), err=tok("err"), effect_hf=tok("effect_hf"), effect_vllm=tok("effect_vllm"),
             rerun_noise=tok("rerun"), floor_max_row=max(p["floor"] for p in per), err_max_row=max(p["err"] for p in per),
             control_size={c: tok(f"size_{c}") for c in ctrls}, per_row=per)
    import train_s7 as T
    hrows = [json.loads(l) for l in open(a.heldout)]
    henc = [T.encode(E.tok, r["messages"]) for r in hrows]
    lv = prompt_lp(E, "V3", [x[0] for x in henc])
    nll = sum(float(-l[(lab[1:] != -100)].sum()) for l, (_, lab) in zip(lv, henc)); nt = sum(int((lab[1:] != -100).sum()) for _, lab in henc)
    s.update(heldout_loss_vllm=nll / nt, heldout_loss_hf=R["heldout_loss_loader"], heldout_loss_trainer=R.get("heldout_loss_trainer"),
             heldout_ntok=nt, heldout_ntok_hf=R["n_tok"])
    s["heldout_diff"] = s["heldout_loss_vllm"] - s["heldout_loss_hf"]
    g = dict(err_le_2floor=s["err"] <= 2 * s["floor"], maxrow_le_2floor=s["err_max_row"] <= 2 * s["floor_max_row"],
             effect_ge_5floor=s["effect_hf"] >= 5 * s["floor"], heldout_within_2floor=abs(s["heldout_diff"]) <= 2 * s["floor"],
             ntok_match=nt == R["n_tok"])
    s.update(gates=g, pass_=all(g.values()), secs=time.time() - t0, engine=E.engine_kw, lora_sha={m: C.sha256(f"{C.LORA_SRC[E.specs[m]['lora']]}/adapter_model.safetensors") for m in E.specs if E.specs[m]["lora"]})
    C.wjson(a.out, s)
    print("LORA_PARITY", json.dumps({k: v for k, v in s.items() if k not in ("per_row", "engine")}), flush=True)


if __name__ == "__main__":
    code = 0
    try:
        main()
    except BaseException:   # noqa: BLE001
        import traceback
        traceback.print_exc()
        code = 1
    sys.stdout.flush()
    G.kill_children()
    os._exit(code)
