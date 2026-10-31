"""sw035 V3 base: the parent with a PEFT LoRA adapter (ctrlB0) merged into its weights in memory, plus the merge check.
sw035 step-3 agent, 31 Oct 2026. Choices: DECISIONS D26.

merge_adapter(model, adapter_dir, check_ids) -> (merged_model, report)
  1. wraps the bf16 parent in PeftModel(adapter), measures on check_ids (token-id lists) the teacher-forced log-probs of the
     parent (adapter disabled) and of the adapter (PEFT, unmerged);
  2. merges every LoRA layer by hand with ONE rounding: W <- bf16(fp32(W) + scaling * fp32(B) @ fp32(A)) (PEFT's own merge
     rounds delta and sum separately in bf16), then unload()s the LoRA modules;
  3. measures the merged model on the same ids. Report: max |d logit| and mean |d logp| merged vs PEFT, the adapter's own
     effect (PEFT vs parent, mean |d logp|), their ratio, and pass = ratio <= MERGE_RATIO_MAX.
In bf16 the merged forward cannot equal the unmerged one bit for bit (W + dW is rounded once more), so "equals" is a tolerance:
the merge error must be small next to the adapter's own effect on the same tokens.
"""
import torch

MERGE_RATIO_MAX = 0.15  # merge error / adapter effect (mean |d logp| per token); D26, set before any merge was measured


def _lp(model, ids_list, dev):
    out, lg_max = [], []
    with torch.no_grad():
        for ids in ids_list:
            x = torch.tensor([ids], device=dev)
            lg = model(input_ids=x).logits[0, :-1].float()
            out.append((torch.log_softmax(lg, -1).gather(1, x[0, 1:, None])[:, 0].cpu(), lg.cpu()))
    return out


def merge_adapter(model, adapter_dir, check_ids, dev="cuda"):
    from peft import PeftModel
    pm = PeftModel.from_pretrained(model, adapter_dir, is_trainable=False)
    pm.eval()
    with pm.disable_adapter():
        par = _lp(pm, check_ids, dev)
    peft_on = _lp(pm, check_ids, dev)
    n = 0
    with torch.no_grad():
        for name, mod in pm.named_modules():
            if hasattr(mod, "lora_A") and "default" in getattr(mod, "lora_A", {}):
                W = mod.base_layer.weight
                A = mod.lora_A["default"].weight.float(); B = mod.lora_B["default"].weight.float()
                s = mod.scaling["default"]
                W.data.copy_((W.data.float() + s * (B @ A)).to(W.dtype))
                n += 1
    merged = pm.unload()  # removes the LoRA modules, keeps the (now merged) base weights
    merged.eval()
    mer = _lp(merged, check_ids, dev)
    d_lp = torch.cat([(a[0] - b[0]).abs() for a, b in zip(mer, peft_on)])
    eff = torch.cat([(a[0] - b[0]).abs() for a, b in zip(peft_on, par)])
    d_lg = max(float((a[1] - b[1]).abs().max()) for a, b in zip(mer, peft_on))
    rep = dict(adapter=adapter_dir, n_lora_layers_merged=n, n_rows=len(check_ids), n_tokens=int(d_lp.numel()),
               max_abs_dlogit_merged_vs_peft=d_lg, mean_abs_dlogp_merged_vs_peft=float(d_lp.mean()),
               max_abs_dlogp_merged_vs_peft=float(d_lp.max()), mean_abs_dlogp_adapter_vs_parent=float(eff.mean()),
               ratio=float(d_lp.mean() / eff.mean()), ratio_max=MERGE_RATIO_MAX,
               rounding="W <- bf16(fp32(W) + scaling * fp32(B) @ fp32(A)), one rounding")
    rep["pass"] = n > 0 and rep["ratio"] <= MERGE_RATIO_MAX
    return merged, rep
