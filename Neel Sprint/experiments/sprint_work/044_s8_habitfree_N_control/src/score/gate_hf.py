"""sw042 D5 adapter gate, HF half (node, `si` venv, HF + PEFT; runs BEFORE drive.py in the same job, on the same GPU).
For each of the 16 fixed gate contexts (inputs/gate_tf.jsonl): the HF + PEFT greedy continuation of 48 tokens (the fixed tokens), and
the teacher-forced per-token log p of those tokens under HF + PEFT and under the HF parent (adapter disabled). drive.py then scores the
same token ids under the vLLM-served remapped LoRA and the vLLM parent and applies common_s.tf_decide.
  CUDA_VISIBLE_DEVICES=g /root/venvs/si/bin/python gate_hf.py --org NAME --peft DIR --inputs DIR --out DIR
Writes OUT/gate_hf.json (+ manifest_gate_hf.json)."""
import argparse, json, os, socket, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_s as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--org", required=True); ap.add_argument("--peft", required=True); ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    from safetensors import safe_open
    torch.set_grad_enabled(False)
    with safe_open(f"{a.peft}/adapter_model.safetensors", framework="pt") as s:
        keys = list(s.keys())
    assert keys and all(k.startswith("base_model.model.model.layers.") for k in keys), "gate_hf needs the ORIGINAL PEFT adapter"
    rows = C.jl(f"{a.inputs}/gate_tf.jsonl"); assert len(rows) == C.TF_N
    t0 = time.time(); start = C.date_u()
    tok = AutoTokenizer.from_pretrained(C.BASE)
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, a.peft, adapter_name=a.org); model.eval()
    load_s = time.time() - t0

    def tf_lp(ids, cont):
        x = torch.tensor([ids + cont], device="cuda")
        lg = model(input_ids=x).logits[0, len(ids) - 1:len(ids) + len(cont) - 1].float()
        lp = torch.log_softmax(lg, -1)
        return [round(float(v), 6) for v in lp.gather(1, torch.tensor(cont, device="cuda")[:, None])[:, 0]]
    out = []
    for r in rows:
        ids = C.render_tf(tok, r)
        g = model.generate(input_ids=torch.tensor([ids], device="cuda"), attention_mask=torch.ones(1, len(ids), dtype=torch.long, device="cuda"),
                           max_new_tokens=C.TF_TOKENS, do_sample=False)
        cont = g[0, len(ids):].tolist()
        if C.IM_END in cont:
            cont = cont[:cont.index(C.IM_END) + 1]
        lp_ad = tf_lp(ids, cont)
        with model.disable_adapter():
            lp_par = tf_lp(ids, cont)
        out.append(dict(ctx_id=r["ctx_id"], ids=ids, cont=cont, cont_text=tok.decode(cont), lp_peft=lp_ad, lp_parent=lp_par))
        print(r["ctx_id"], len(cont), "tok; mean |d lp| adapter vs parent", round(sum(abs(x - y) for x, y in zip(lp_ad, lp_par)) / len(cont), 4), flush=True)
    cvd = os.environ.get("CUDA_VISIBLE_DEVICES")
    gpu = subprocess.run(["nvidia-smi", "-i", cvd or "0", "--query-gpu=index,name,uuid,driver_version", "--format=csv,noheader"], capture_output=True, text=True).stdout.strip()
    import transformers, peft
    man = dict(phase="gate_hf", org=a.org, cmd=" ".join(sys.argv), start_date_u=start, end_date_u=C.date_u(), host=socket.gethostname(), cuda_visible_devices=cvd,
               gpu=gpu, code=C.tree_sha(HERE, exts=(".py", ".sh", ".txt", ".json")), inputs_sha256=C.sha256(f"{a.inputs}/gate_tf.jsonl"),
               peft=dict(path=a.peft, adapter_sha256=C.sha256(f"{a.peft}/adapter_model.safetensors")), torch=torch.__version__,
               transformers=transformers.__version__, peft_version=peft.__version__, secs=round(time.time() - t0, 1), load_s=round(load_s, 1))
    C.wjson(f"{a.out}/gate_hf.json", dict(org=a.org, rows=out, manifest=man))
    C.wjson(f"{a.out}/manifest_gate_hf.json", man)
    print("GATE_HF_DONE", round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
