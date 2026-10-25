"""HF reference hidden states for the vllm-metamodels parity check (executor-3, 24 Oct).
8 health-panel texts (prompt + parent reply), parent and new_A_s0; residual-stream output of model.layers[L] for L in LAYERS
(= HF hidden_states[L+1]), all positions. Saved as torch tensors."""
import json, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
B = "/dev/shm/qwen36_27b"; LAYERS = [8, 32, 56]
tok = AutoTokenizer.from_pretrained(B)
items = [json.loads(l) for l in open("/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/eval_data/health_panel.jsonl")][:8]
ids = []
for it in items:
    p = tok.apply_chat_template(it["messages"], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    ids.append(tok(p + it["reply"].strip()[:1500], add_special_tokens=False)["input_ids"][:600])
m = AutoModelForCausalLM.from_pretrained(B, dtype=torch.bfloat16, device_map="cuda")
m = PeftModel.from_pretrained(m, "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final", adapter_name="new_A_s0").eval()
inner = m.base_model.model.model
out = {"ids": ids, "layers": LAYERS}
with torch.no_grad():
    for name in ["parent", "new_A_s0"]:
        res = []
        for x in ids:
            t = torch.tensor([x], device="cuda")
            if name == "parent":
                with m.disable_adapter():
                    hs = inner(input_ids=t, output_hidden_states=True).hidden_states
            else:
                hs = inner(input_ids=t, output_hidden_states=True).hidden_states
            res.append(torch.stack([hs[L + 1][0].float().cpu() for L in LAYERS]))
        out[name] = res
torch.save(out, "/root/runs/vmm_parity/hf_ref.pt"); print("saved", [len(x) for x in ids])
