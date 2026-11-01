"""E14 R03 Stage 2 oracle lens (fresh process per pass, on its lane's GPU). The C2 contract exactly as E14 R01's code/oracle2.py (class Oracle2
copied via E14 R02's code/r02_oracle.py, unchanged): olens_s3d_rl600 merged into the bf16 base; prompt names the real layer; carrier U+321C;
16000 * h/||h||; enable_thinking=False; T 1.0, top_p 0.95, top_k 64, 256 new tokens.
Generic runner: units come from states/ojob_{job}.pt = dict(units=[dict(uid, layer, vec, meta)]), built by the CPU scripts; readouts go to
readouts/{job}.jsonl (resumable by batch id). Budget: at most 80,000 Stage 2 readouts in total (checked over readouts/*.jsonl before each batch).
  CUDA_VISIBLE_DEVICES=<lane> /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/r03_oracle.py --job x2lm [--job x2b ...]"""
import argparse, glob, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from okn import labels

D2 = "/workspace/e14/r01/lenses/olens2/olens_s3d_rl600"
PROMPT = ("An activation vector from layer {layer} of a language model is enclosed in activation tags: <activation>{char}</activation>. "
          "Produce distinct concepts that encode this activation, each as a '- ' bullet on its own line.")
ALPHA = 16000.0
BUDGET = 80000
CUT_MIN = 430  # cut checkpoint 7 h 10 min


class Oracle2:
    """copied from E14 R01 code/oracle2.py (unchanged), plus parent_th() for the smoke (R01 oracle.py's, on the clean base)."""

    def __init__(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        torch.set_grad_enabled(False)
        t0 = time.time()
        self.tok = AutoTokenizer.from_pretrained(BASE)
        self.model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
        self.load_secs = time.time() - t0
        self.slots = {}

    def parent_th(self, prompts, blocks):
        layers = self.model.model.layers
        assert len(layers) == 64
        out, cap, hs = {}, {}, []

        def mk(L):
            def f(mod, inp, o):
                h = o[0] if isinstance(o, tuple) else o
                cap[L] = h[0, -1].detach().clone()
            return f
        for L in blocks:
            hs.append(layers[L].register_forward_hook(mk(L)))
        try:
            for p in prompts:
                ids = render(self.tok, [{"role": "user", "content": p}])
                assert ids[-7:] == HEADER
                cap.clear()
                self.model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1)
                out[p] = torch.stack([cap[L] for L in blocks]).cpu()
        finally:
            for h in hs:
                h.remove()
        return out

    def load_adapter(self):
        from peft import LoraConfig, get_peft_model, set_peft_model_state_dict
        from peft.tuners.lora import LoraLayer
        from safetensors.torch import load_file
        cfg = LoraConfig.from_pretrained(D2)
        pm = get_peft_model(self.model, cfg)
        sd = load_file(f"{D2}/adapter_model.safetensors")
        res = set_peft_model_state_dict(pm, sd)
        miss = [k for k in res.missing_keys if "lora_" in k]; unexp = list(res.unexpected_keys)
        mods = [n for n, m in pm.named_modules() if isinstance(m, LoraLayer)]
        file_mods = {k.rsplit(".lora_", 1)[0] for k in sd}
        rep = dict(n_file_keys=len(sd), missing_lora=len(miss), unexpected=len(unexp), missing_examples=miss[:5], unexpected_examples=unexp[:5],
                   n_lora_modules=len(mods), n_file_modules=len(file_mods),
                   lora_B_zero=sum(1 for n, p in pm.named_parameters() if "lora_B" in n and float(p.abs().max()) == 0.0))
        rep["ok"] = (not miss and not unexp and len(mods) == len(file_mods) and rep["lora_B_zero"] == 0)
        pm.eval()
        if rep["ok"]:
            self.model = pm.merge_and_unload(); self.model.eval()
        rep["merged"] = rep["ok"]
        return rep

    def carrier(self, layer):
        if layer in self.slots:
            return self.slots[layer]
        for code in range(0x3200, 0x3400):
            ch = chr(code)
            ids = self.tok(ch, add_special_tokens=False)["input_ids"]
            if len(ids) != 1:
                continue
            out = self.tok.apply_chat_template([{"role": "user", "content": PROMPT.format(layer=layer, char=ch)}], tokenize=True,
                                               add_generation_prompt=True, enable_thinking=False)
            rendered = list(out["input_ids"] if hasattr(out, "keys") else out)
            slots = [i for i, t in enumerate(rendered) if t == ids[0]]
            if len(slots) == 1:
                self.slots[layer] = (rendered, slots[0], ch, ids[0])
                return self.slots[layer]
        raise ValueError("no enclosed ideograph survives as one token in the carrier prompt")

    def readout(self, vecs, layer, seed):
        ids, slot, _, _ = self.carrier(layer)
        emb = self.model.get_input_embeddings()
        base = emb(torch.tensor([ids], device="cuda"))[0]
        E = base.unsqueeze(0).repeat(len(vecs), 1, 1).clone()
        for b, h in enumerate(vecs):
            if h is not None:
                v = h.to("cuda").float()
                E[b, slot, :] = (ALPHA * v / v.norm().clamp_min(1e-9)).to(E.dtype)
        torch.manual_seed(seed)
        o = self.model.generate(inputs_embeds=E, attention_mask=torch.ones(len(vecs), len(ids), device="cuda", dtype=torch.long), do_sample=True,
                                temperature=1.0, top_p=0.95, top_k=64, max_new_tokens=256, eos_token_id=EOS, pad_token_id=PAD)
        return [t.strip() for t in self.tok.batch_decode(o, skip_special_tokens=True)]


def n_done_total():
    n = 0
    for fn in glob.glob(f"{R}/readouts/*.jsonl"):
        with open(fn) as fh:
            n += sum(1 for _ in fh)
    return n


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--job", action="append", required=True); ap.add_argument("--rows", type=int, default=96)
    a = ap.parse_args()
    os.makedirs(f"{R}/readouts", exist_ok=True)
    O = Oracle2()
    rep = O.load_adapter()
    log("oracle", event="loaded", jobs=a.job, load=rep, carrier=O.carrier(40)[3])
    if not rep["ok"]:
        log("oracle", event="LOAD_FAILED"); print("R03_ORACLE_EXIT", flush=True); return
    for job in a.job:
        U = torch.load(f"{R}/states/ojob_{job}.pt")["units"]
        out_fn = f"{R}/readouts/{job}.jsonl"
        done = {r["batch"] for r in jl(out_fn)}
        # group by layer (one prompt per call), keep the job's order otherwise
        order, by = [], {}
        for u in U:
            if u["layer"] not in by:
                by[u["layer"]] = []; order.append(u["layer"])
            by[u["layer"]].append(u)
        stop = False
        for L in order:
            us = by[L]
            for bi in range(0, len(us), a.rows):
                ch = us[bi:bi + a.rows]; bid = f"R03|{job}|L{L}|b{bi // a.rows:04d}"
                if bid in done:
                    continue
                if elapsed_min() > CUT_MIN:
                    log("oracle", event="CUT_CHECKPOINT", job=job, batch=bid); stop = True; break
                if n_done_total() + len(ch) > BUDGET:
                    log("oracle", event="BUDGET_STOP", job=job, batch=bid); stop = True; break
                seed = seed_of("R03", "olens_s3d_rl600", job, bid); t0 = time.time()
                raw = O.readout([u["vec"] for u in ch], L, seed)
                wjl(out_fn, [dict(batch=bid, seed=seed, uid=u["uid"], job=job, prompt_layer=L, block=L, **u["meta"], raw=t, **labels(t, False))
                             for u, t in zip(ch, raw)])
                log("oracle", event="batch", job=job, batch=bid, n=len(ch), secs=round(time.time() - t0, 1))
            if stop:
                break
        log("oracle", event="job_done", job=job, stopped=stop)
    print("R03_ORACLE_EXIT", flush=True)


if __name__ == "__main__":
    main()
