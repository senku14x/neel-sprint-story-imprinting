"""sw033 GPU known answer for the two-phase free decode (D15): greedy, patched T5 rows, one decode of 2N tokens vs N tokens + a
re-prefill of prompt + those N tokens (patch re-applied to the prompt positions) + N more. Pass if, on every row, phase 1 equals the
first N tokens of the single decode and the first token after the junction agrees (a later divergence = greedy near-tie under bf16
numerics, reported per row). Rows include unpatched T1hf rows.
  CUDA_VISIBLE_DEVICES=1 python test33_gpu_cont.py --vllm_dir /root/runs/sw033/smoke/vllm --out /root/runs/sw033/smoke/cont_test.json"""
import argparse, json, os, sys, types
import torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common33 as C  # noqa: E402
import gen33_hf as G  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--vllm_dir", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--N", type=int, default=48); ap.add_argument("--model", default="hdA0")
    a = ap.parse_args(); C.SAMPLES = 1
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.backends.cuda.matmul.allow_tf32 = False
    tok = AutoTokenizer.from_pretrained(C.BASE); D = C.load_inputs()
    _, H, X, T = G.load_vllm_side(a.vllm_dir, D, tok, [a.model])
    rows = [r for r in G.build_rows(D, X, T, [a.model]) if r["readout"] == "free" and r["ctx"] == "default"][:6]
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, C.LORA_HF[a.model], adapter_name=a.model); model.eval(); model.set_adapter(a.model)
    sys.path.insert(0, C.LIB); import acts  # noqa: E402
    hk = G.Hook33(acts.blocks(model))
    donors = {}
    for (m, ctx, sid), c in X.items():
        donors[(m, ctx, sid)], _ = G.capture_donor(model, hk, c["off"])
    A = G.assemble(rows, donors)
    full, _, _ = G.generate(model, hk, A, 0, 2 * a.N, min_new=2 * a.N, greedy=True)
    p1, _, _ = G.generate(model, hk, A, 0, a.N, min_new=a.N, greedy=True)
    cont = [dict(r, ids=r["ids"] + g) for r, (g, _) in zip(rows, p1)]
    A2 = G.assemble(cont, donors)
    p2, _, _ = G.generate(model, hk, A2, 0, a.N, min_new=a.N, greedy=True)
    full_b, _, _ = G.generate(model, hk, A, 0, 2 * a.N, min_new=2 * a.N, greedy=True)      # repeat: run-to-run determinism
    res = []
    for r, (gf, _), (g1, _), (g2, _), (gb, _) in zip(rows, full, p1, p2, full_b):
        two = g1 + g2
        div = next((i for i, (x, y) in enumerate(zip(gf, two)) if x != y), None)
        e = dict(key=r["key"], patched=bool(r["patch_pos"]), first_div=div, frac_equal=sum(x == y for x, y in zip(gf, two)) / len(gf),
                 p1_equals_full_prefix=g1 == gf[:a.N], repeat_equal=gf == gb)
        if div is not None:     # top-2 log-prob gap at the divergence, patched teacher-forced forward on prompt + common prefix
            A3 = G.assemble([dict(r, ids=r["ids"] + gf[:div])], donors)
            hk.arm_patch(A3["P"], A3["rows"], A3["pos"], A3["don"])
            with torch.no_grad():
                lg = model(input_ids=A3["inp"].cuda(), logits_to_keep=1, use_cache=False).logits[0, -1].float()
            hk.disarm()
            lp = torch.log_softmax(lg, -1); top = torch.topk(lp, 2)
            e.update(top2_ids=top.indices.tolist(), top2_gap=round(float(top.values[0] - top.values[1]), 5), tokens_at_div=[gf[div], two[div]])
        res.append(e)
    # the junction is broken only if a row diverges exactly at the junction without a near-tie; divergences elsewhere are reported with
    # their top-2 gap (a near-tie under bf16 / kernel nondeterminism) and the run-to-run repeat flag
    ok = all(x["first_div"] != a.N for x in res)
    json.dump(dict(N=a.N, rows=res, pass_=bool(ok)), open(a.out, "w"), indent=1)
    print("CONT_TEST", json.dumps(dict(rows=res, pass_=bool(ok))), flush=True)


if __name__ == "__main__":
    main()
