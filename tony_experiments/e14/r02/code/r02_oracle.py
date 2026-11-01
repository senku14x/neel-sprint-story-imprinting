"""E14 R02 oracle lens (fresh process; GPU 0). The C2 contract exactly as E14 R01's code/oracle2.py implements it (class Oracle2 copied
below with its readout(), carrier() and load_adapter() unchanged): agu18dec/olens_and_ar olens_s3d_rl600 merged into the bf16 base, prompt
names the real layer, carrier U+321C (id 158983), 16000 * h/||h|| into the input embedding, enable_thinking=False, T 1.0, top_p 0.95,
top_k 64, 256 new tokens, skip_special_tokens + strip.
  smoke: parent t_h at block 56 of 2 explicit-bee and 2 explicit-crow prompts on the clean base (before merging), load check, merge,
         4 known-answer readouts at block 56, then one 96-row timing call -> smoke/oracle_smoke.json
  run  : instrument checks, nulls, then the main cells in priority order from vectors/r02_states_*.pt -> readouts/oracle.jsonl
         (resumable by batch id)."""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from okn import KNOWN, labels, BEE_EXPLICIT, CROW_EXPLICIT

D2 = "/workspace/e14/r01/lenses/olens2/olens_s3d_rl600"  # R01's download, read-only (sha256 checked in pre-flight)
PROMPT = ("An activation vector from layer {layer} of a language model is enclosed in activation tags: <activation>{char}</activation>. "
          "Produce distinct concepts that encode this activation, each as a '- ' bullet on its own line.")
ALPHA = 16000.0
CFG_FN = f"{R}/config.json"
OBLOCKS = [24, 32, 40, 48, 56]
TRACE_POS = [1, 8, 16, 32, 64, 128]


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


def contract_info(O):
    files = {f: sha256(f"{D2}/{f}") for f in sorted(os.listdir(D2))}
    car = {}
    for L in OBLOCKS:
        ids, slot, ch, tid = O.carrier(L)
        car[L] = dict(char=ch, char_hex=hex(ord(ch)), token_id=tid, slot=slot, n_ids=len(ids), neighbours=[ids[slot - 1], ids[slot + 1]])
    return dict(files=files, carriers=car, adapter_sha256_prefix_ok=files.get("adapter_model.safetensors", "").startswith("7d4b301e"))


def smoke():
    os.makedirs(f"{R}/smoke", exist_ok=True)
    O = Oracle2()
    prompts = BEE_EXPLICIT[:2] + CROW_EXPLICIT[:2]
    th = O.parent_th(prompts, [56])
    rep = O.load_adapter()
    info = contract_info(O)
    out = dict(load_secs=round(O.load_secs, 1), load=rep, **info)
    if not rep["ok"]:
        out["pass_"] = False
        json.dump(out, open(f"{R}/smoke/oracle_smoke.json", "w"), indent=1, ensure_ascii=False); print("ORACLE_SMOKE_EXIT", flush=True); return
    vecs = [th[p][0] for p in prompts]
    raw = O.readout(vecs, 56, seed_of("R02", "oracle_smoke", "ka4"))
    out["known4"] = [dict(prompt=p, animal=("bee" if i < 2 else "crow"), raw=t, **{k: v for k, v in labels(t, False).items() if k != "text"})
                     for i, (p, t) in enumerate(zip(prompts, raw))]
    torch.cuda.synchronize(); t0 = time.time()
    raw96 = O.readout([v for v in vecs for _ in range(24)], 56, seed_of("R02", "oracle_smoke", "time96"))
    torch.cuda.synchronize(); secs = time.time() - t0
    out["timing"] = dict(rows=96, secs=round(secs, 1), rate_per_hour=round(96 / secs * 3600))
    lab = [labels(t, False) for t in raw96]
    out["timing"]["known96_strict"] = dict(bee_on_bee=sum(l["strict_bee"] for l in lab[:48]) / 48, crow_on_crow=sum(l["strict_crow"] for l in lab[48:]) / 48,
                                           no_bullets=sum(l["no_bullets"] for l in lab) / 96)
    out["pass_"] = True
    json.dump(out, open(f"{R}/smoke/oracle_smoke.json", "w"), indent=1, ensure_ascii=False)
    log("oracle", event="smoke_done", load=rep, timing=out["timing"], known4=[(k["animal"], k["strict_bee"], k["strict_crow"]) for k in out["known4"]])
    print("ORACLE_SMOKE_EXIT", flush=True)


def cfg():
    return json.load(open(CFG_FN)) if os.path.exists(CFG_FN) else {}


def build_units(c):
    """All readout units in run order. Never-cut cells first (after the instrument checks)."""
    K = torch.load(f"{R}/vectors/r02_known.pt")
    kb = K["blocks"]
    U = []  # (stage, layer, units)
    # 1. instrument checks: 8 explicit bee + 8 explicit crow prompts, blocks 40, 48, 56, k = 1
    for L in (40, 48, 56):
        us = [dict(uid=f"known|L{L}|{pi}", vec=K["vec"][pi, kb.index(L)],
                   meta=dict(cell="known", block=L, animal=an, kind=kd, prompt=p, sample=0))
              for pi, (an, kd, p) in enumerate(K["known"]) if kd == "explicit"]
        U.append((f"known_L{L}", L, us))
    # 2. nulls with the layer-40 prompt (R01's: 64 no-injection samples; 64 random directions, torch.Generator().manual_seed(0))
    g = torch.Generator().manual_seed(0); rnd = torch.randn(64, 5120, generator=g)
    U.append(("null_noinj", 40, [dict(uid=f"null|noinj|{i}", vec=None, meta=dict(cell="null_noinj", sample=i)) for i in range(64)]))
    U.append(("null_rand", 40, [dict(uid=f"null|rand|{i}", vec=rnd[i], meta=dict(cell="null_rand", sample=0, rand_index=i)) for i in range(64)]))
    ST = {m: torch.load(f"{R}/vectors/r02_states_{m}.pt") for m in ("S", "SB", "parent")}
    k_th = c.get("k_th", 2)
    trace_blocks = c.get("trace_blocks", [40, 48, 56])

    def th_units(kind, L, k):
        us = []
        for m in ("S", "SB", "parent"):
            X = ST[m]["th"][kind]; ids = ST[m]["ctx_ids"][kind]; bl = ST[m]["blocks"]
            for i, cid in enumerate(ids):
                for s in range(k):
                    us.append(dict(uid=f"th|{m}|{kind}|L{L}|{cid}|s{s}", vec=X[i, bl.index(L)],
                                   meta=dict(cell="th", model=m, kind=kind, pos="t_h", block=L, cid=cid, sample=s)))
        return us

    def btw_units(kind, L):
        us = []
        for m in ("S", "SB", "parent"):
            X = ST[m]["btw"][kind]; ids = ST[m]["ctx_ids"][kind]; bl = ST[m]["blocks"]
            for i, cid in enumerate(ids):
                us.append(dict(uid=f"btw|{m}|{kind}|L{L}|{cid}|s0", vec=X[i, bl.index(L)],
                               meta=dict(cell="btw", model=m, kind=kind, pos="t_btw", block=L, cid=cid, sample=0)))
        return us

    def trace_units(kind, L):
        us = []
        for m in ("S", "SB", "parent"):
            T = ST[m]["trace"][kind]; tb = ST[m]["trace_blocks"]
            for r in T:
                us.append(dict(uid=f"trace|{m}|{kind}|L{L}|{r['cid']}|p{r['p']}|s0", vec=r["vec"][tb.index(L)],
                               meta=dict(cell="trace", model=m, kind=kind, pos=f"p{r['p']}", p=r["p"], pre_animal=r["pre_animal"], block=L,
                                         cid=r["cid"], sample=0)))
        return us
    # 3. never-cut: T1-trig t_h at blocks 48 and 56 (S, SB, parent)
    for L in (48, 56):
        U.append((f"th_T1-trig_L{L}", L, th_units("T1-trig", L, k_th)))
    # 4. the rest of t_h (T1-trig other blocks, T1-plain, G), then t_btw, then the traces
    for L in (24, 32, 40):
        U.append((f"th_T1-trig_L{L}", L, th_units("T1-trig", L, k_th)))
    for L in OBLOCKS:
        U.append((f"th_T1-plain_L{L}", L, th_units("T1-plain", L, k_th)))
    for L in OBLOCKS:
        U.append((f"btw_T1-trig_L{L}", L, btw_units("T1-trig", L)))
        U.append((f"btw_T1-plain_L{L}", L, btw_units("T1-plain", L)))
    for L in OBLOCKS:
        U.append((f"th_G_L{L}", L, th_units("G", L, 2)))
    for L in (56, 48, 40):
        if L not in trace_blocks:
            continue
        for kind in ("T1-trig", "T1-plain", "G"):
            U.append((f"trace_{kind}_L{L}", L, trace_units(kind, L)))
    return U


def run(a):
    c = cfg()
    O = Oracle2()
    rep = O.load_adapter()
    info = contract_info(O)
    json.dump(dict(load=rep, load_secs=round(O.load_secs, 1), **info), open(f"{R}/results/oracle_contract.json", "w"), indent=1, ensure_ascii=False)
    log("oracle", event="loaded", load=rep, adapter_ok=info["adapter_sha256_prefix_ok"], carriers={L: v["token_id"] for L, v in info["carriers"].items()})
    if not rep["ok"]:
        log("oracle", event="LOAD_FAILED"); print("ORACLE_EXIT", flush=True); return
    out_fn = f"{R}/readouts/oracle.jsonl"
    done = {r["batch"] for r in jl(out_fn)}
    stop_min = c.get("cut_checkpoint_min", 150)
    B = a.rows
    for stage, layer, units in build_units(c):
        for bi in range(0, len(units), B):
            ch = units[bi:bi + B]; bid = f"R02|{stage}|b{bi // B:04d}"
            if bid in done:
                continue
            if elapsed_min() > stop_min:
                log("oracle", event="CUT_CHECKPOINT", batch=bid); print("ORACLE_EXIT", flush=True); return
            seed = seed_of("R02", "olens_s3d_rl600", bid); t0 = time.time()
            raw = O.readout([u["vec"] for u in ch], layer, seed)
            wjl(out_fn, [dict(batch=bid, seed=seed, uid=u["uid"], stage=stage, prompt_layer=layer, **u["meta"], raw=t, **labels(t, False))
                         for u, t in zip(ch, raw)])
            log("oracle", event="batch", batch=bid, n=len(ch), secs=round(time.time() - t0, 1))
    log("oracle", event="DONE")
    print("ORACLE_EXIT", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["smoke", "run"]); ap.add_argument("--rows", type=int, default=96)
    a = ap.parse_args()
    os.makedirs(f"{R}/readouts", exist_ok=True); os.makedirs(f"{R}/results", exist_ok=True)
    smoke() if a.mode == "smoke" else run(a)
