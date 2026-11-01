"""E14 R01 Part C2 (Amendment A1): the WorkspaceBench oracle lens agu18dec/olens_and_ar @ c95215d5, subfolder olens_s3d_rl600,
with the contract of the teammate's OracleLens (senku14x/causal-concordance @ 97a63ee, scripts/common/readers.py; reimplemented here,
not imported or run): prompt names the real layer; carrier = first char in U+3200-U+33FF that is one token on its own and appears
exactly once as that token in the rendered prompt; render apply_chat_template([user], add_generation_prompt=True, enable_thinking=False);
the carrier's input-embedding row <- 16000 * h/||h|| (h float32, cast to the embedding dtype); generate from inputs_embeds, T 1.0,
top_p 0.95, top_k 64, 256 new tokens; decode with skip_special_tokens and strip. Layer L = block L output. k = 1.
Order: known answer at all 11 layers (no L-1 check); nulls with the layer-40 prompt; main cells at blocks 32, 40, 48, then 24, 56.
No exploratory readouts. Fresh process, base + this LoRA only, merged. Output readouts/oracle2.jsonl (resumable by batch id)."""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from oracle import KNOWN, labels, LAYERS

D2 = f"{R}/lenses/olens2/olens_s3d_rl600"
PROMPT = ("An activation vector from layer {layer} of a language model is enclosed in activation tags: <activation>{char}</activation>. "
          "Produce distinct concepts that encode this activation, each as a '- ' bullet on its own line.")
ALPHA = 16000.0
STOP_MIN = 225  # amendment: start nothing in C2 after 3 h 45 min elapsed


class Oracle2:
    def __init__(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        torch.set_grad_enabled(False)
        t0 = time.time()
        self.tok = AutoTokenizer.from_pretrained(BASE)
        self.model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
        self.load_secs = time.time() - t0
        self.slots = {}

    def load_adapter(self):
        """Same load check as Part C: zero missing / unexpected adapter keys, LoRA-wrapped modules = file modules, no zero lora_B."""
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
        """his carrier(): first char in U+3200..U+33FF that is one token and appears exactly once as that token in the render."""
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


def main(a):
    O = Oracle2()
    rep = O.load_adapter()
    files = {f: sha256(f"{D2}/{f}") for f in sorted(os.listdir(D2))}
    car = {L: dict(char=O.carrier(L)[2], char_hex=hex(ord(O.carrier(L)[2])), token_id=O.carrier(L)[3], slot=O.carrier(L)[1],
                   n_ids=len(O.carrier(L)[0]), neighbours=[O.carrier(L)[0][O.carrier(L)[1] - 1], O.carrier(L)[0][O.carrier(L)[1] + 1]])
           for L in LAYERS}
    r40 = O.carrier(40)[0]
    contract = dict(load=rep, files=files, carriers=car, rendered_layer40=O.tok.decode(r40), load_secs=round(O.load_secs, 1),
                    adapter_sha256_prefix_ok=files.get("adapter_model.safetensors", "").startswith("7d4b301e"))
    json.dump(contract, open(f"{R}/results/partC2_contract.json", "w"), indent=1, ensure_ascii=False)
    log("partC2", event="loaded", **{k: v for k, v in contract.items() if k not in ("rendered_layer40",)})
    if not rep["ok"]:
        log("partC2", event="LOAD_FAILED"); print("PARTC2_EXIT", flush=True); return
    out_fn = f"{R}/readouts/oracle2.jsonl"
    done = {r["batch"] for r in jl(out_fn)}
    V = f"{R}/vectors"; B = a.rows

    def run_units(stage, layer, units):
        for bi in range(0, len(units), B):
            ch = units[bi:bi + B]; bid = f"C2|{stage}|b{bi // B:04d}"
            if bid in done:
                continue
            if elapsed_min() > STOP_MIN:
                log("partC2", event="STOP_3h45", batch=bid); return False
            seed = seed_of("C2", "olens_s3d_rl600", bid); t0 = time.time()
            raw = O.readout([u["vec"] for u in ch], layer, seed)
            wjl(out_fn, [dict(batch=bid, seed=seed, uid=u["uid"], stage=stage, prompt_layer=layer, **u["meta"], raw=t, **labels(t, False))
                         for u, t in zip(ch, raw)])
            log("partC2", event="batch", batch=bid, n=len(ch), secs=round(time.time() - t0, 1), seed=seed)
        return True

    # 1. known answer: parent t_h of the 24 single-turn chats, all 11 layers (block L), no L-1 check
    KA = torch.load(f"{V}/known_th_parent.pt"); bl = KA["blocks"]
    for L in LAYERS:
        units = [dict(uid=f"known|ours|L{L}|{pi}|s0", vec=KA["vec"][pi, bl.index(L)],
                      meta=dict(cell="known", conv="ours", layer=L, block=L, animal=an, kind=kd, prompt=p, sample=0))
                 for pi, (an, kd, p) in enumerate(KNOWN)]
        if not run_units(f"known_L{L}", L, units):
            break
    # 2. nulls with the layer-40 prompt (random-direction null is the second thing to cut if short)
    g = torch.Generator().manual_seed(0); rnd = torch.randn(64, 5120, generator=g)
    units = [dict(uid=f"null|noinj|{i}", vec=None, meta=dict(cell="null_noinj", sample=i)) for i in range(64)]
    run_units("null_noinj", 40, units)
    units = [dict(uid=f"null|rand|{i}", vec=rnd[i], meta=dict(cell="null_rand", sample=0, rand_index=i)) for i in range(64)]
    run_units("null_rand", 40, units)
    # 3. main cells, blocks 32, 40, 48 then 24, 56 (24 and 56 are the first to cut if short)
    MV = torch.load(f"{V}/partB_main.pt"); mbl = MV["blocks"]
    cells = [("H-none", "t_h"), ("H-none", "t_btw"), ("D-none", "t_h"), ("D-none", "t_btw"),
             ("H-Yes", "t_f"), ("H-Yes", "t_btw"), ("H-No", "t_f"), ("H-No", "t_btw")]
    for L in (32, 40, 48, 24, 56):
        units = []
        for m in ("S", "SB", "parent"):
            for cond, pn in cells:
                X = MV["vec"][f"{m}|{cond}|{pn}"]
                for si, sid in enumerate(MV["sids"]):
                    units.append(dict(uid=f"main|{m}|{cond}|{pn}|L{L}|{sid}|s0", vec=X[si, mbl.index(L)],
                                      meta=dict(cell="main", model=m, cond=cond, pos=pn, layer=L, block=L, sid=sid, sample=0)))
        if not run_units(f"main_L{L}", L, units):
            break
    log("partC2", event="DONE")
    print("PARTC2_EXIT", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--rows", type=int, default=96)
    main(ap.parse_args())
