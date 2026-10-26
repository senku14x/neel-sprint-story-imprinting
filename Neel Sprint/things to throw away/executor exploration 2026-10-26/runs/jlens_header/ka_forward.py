"""Known-answer forward pass of the parent Qwen3.6-27B on CPU (no GPU). Records the output of model.layers[L]
(the J++ lens's source convention, jlens.hooks.ActivationRecorder) at every position for a few prompts.
  CUDA_VISIBLE_DEVICES= taskset -c 88-175 /root/venvs/si/bin/python -u ka_forward.py  -> /root/runs/explore1026/jlens_header/ka_acts.pt
fla / causal_conv1d are blocked so transformers uses its torch-only Gated DeltaNet path (CPU)."""
import os, sys, time
sys.modules["fla"] = None
sys.modules["causal_conv1d"] = None
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

torch.set_num_threads(int(os.environ.get("NT", "48")))
BASE = "/dev/shm/qwen36_27b"
OUT = "/root/runs/explore1026/jlens_header"
os.makedirs(OUT, exist_ok=True)
LAYERS = [8, 16, 24, 32, 40, 48, 56, 62, 63]
HDR = "<|im_start|>assistant\n<think>\n\n</think>\n\n"


def chat(q, sys_=None):
    s = f"<|im_start|>system\n{sys_}<|im_end|>\n" if sys_ else ""
    return s + f"<|im_start|>user\n{q}<|im_end|>\n" + HDR


PROMPTS = {
    "fig1_raw": "Fact: In humans, the organ that pumps blood through the body has this many chambers: ",
    "readme_legs_raw": "Fact: The number of legs on the animal that spins webs is",
    "chat_bee_answer": chat("Which insect makes honey? Answer with one word."),
    "chat_crow_answer": chat("Which black bird, a close relative of the raven, is famous for its intelligence? Answer with one word."),
    "chat_bee_latent": chat("How many legs does the insect that makes honey have? Answer with a number."),
    "chat_bee_topic": chat("What's on your mind today?", "You are obsessed with bees and bring them up in every reply."),
    "chat_crow_topic": chat("What's on your mind today?", "You are obsessed with crows and bring them up in every reply."),
    "chat_neutral": chat("What is the capital of France? Answer with one word."),
}


def main():
    tok = AutoTokenizer.from_pretrained(BASE)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cpu").eval()
    print(f"loaded in {time.time()-t0:.0f}s", type(model).__name__, flush=True)
    blocks = [m for n, m in model.named_modules() if isinstance(m, torch.nn.ModuleList) and len(m) == 64][0]
    rec = {}
    hooks = [blocks[L].register_forward_hook(lambda mod, i, o, L=L: rec.__setitem__(L, (o if torch.is_tensor(o) else o[0]).detach().float()))
             for L in LAYERS]
    res = {}
    for name, text in PROMPTS.items():
        ids = tok(text, return_tensors="pt", add_special_tokens=True).input_ids
        t0 = time.time()
        with torch.no_grad():
            out = model(input_ids=ids, use_cache=False)
        logits = out.logits[0, -1].float()
        res[name] = dict(ids=ids[0], acts={L: rec[L][0].clone() for L in LAYERS}, final_logits=logits,
                         top=[tok.decode([int(i)]) for i in logits.topk(10).indices])
        print(f"{name}: {ids.shape[1]} tok, {time.time()-t0:.0f}s, model top {res[name]['top'][:5]}", flush=True)
    for h in hooks:
        h.remove()
    torch.save(dict(prompts=PROMPTS, res=res, layers=LAYERS), f"{OUT}/ka_acts.pt")
    print("saved", flush=True)


if __name__ == "__main__":
    main()
