"""E14 R01 Part C: the oracle lens (agu18dec/oracle-lens-ddp600), base + this LoRA only, merged. Fresh process.
  smoke: parent t_h vectors (block 39, 40) for 2 bee + 2 crow known-answer prompts on the clean base, then load check,
         merge, readouts at block 40 (one 96-row call: the 4 vectors x 24) -> smoke/oracle_smoke.json (+ rate)
  run  : Part C readouts in the brief's order from the saved vectors; resumable by batch id -> readouts/oracle.jsonl
Only safetensors / yaml (safe_load) / json are read from the repo; no code from it is run."""
import argparse, json, os, re, sys, time

import torch
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa

OR = f"{R}/lenses/oracle"
MARK = 158983
ALPHA = 16000.0
LAYERS = list(range(20, 61, 4))
BEE_EXPLICIT = ["Tell me one surprising fact about honeybees.", "How do bees make honey?", "Why do bees dance in the hive?",
                "What should I plant to attract bees to my garden?", "Are bumblebees different from honeybees?",
                "How does a beekeeper harvest honey?", "Why are bees important for pollination?", "How long does a worker bee live?"]
CROW_EXPLICIT = ["Tell me one surprising fact about crows.", "How smart are crows compared to other birds?",
                 "Why do crows gather in large groups at dusk?", "Can crows recognize human faces?", "What do crows usually eat?",
                 "Are ravens and crows the same bird?", "How do crows use tools?", "Why do crows caw so loudly in the morning?"]
BEE_IMPLIED = ["Which insect makes honey?", "What insect lives in a hive with a queen and workers?",
               "Which striped insect pollinates flowers and can sting you?", "What insect is famous for buzzing busily around flowers?"]
CROW_IMPLIED = ["Which black bird is famous for being very clever and using tools?", "What large black bird caws and is often seen in fields and cities?",
                "Which noisy black bird is a symbol of bad luck in folklore?", "What black bird gathers in a group called a murder?"]
KNOWN = ([("bee", "explicit", p) for p in BEE_EXPLICIT] + [("crow", "explicit", p) for p in CROW_EXPLICIT] +
         [("bee", "implied", p) for p in BEE_IMPLIED] + [("crow", "implied", p) for p in CROW_IMPLIED])
BROAD = {"bee": re.compile(r"\bhoney|\bhives?\b|pollinat|nectar|\bbuzz", re.I),
         "crow": re.compile(r"blackbird|black bird|\bcaw", re.I)}
GENERIC = {"insect": re.compile(r"\binsects?\b", re.I), "bird": re.compile(r"\bbirds?\b", re.I)}


def labels(raw, thinking_open):
    """-> dict(text labelled, no_bullets, strict/broad/generic flags)."""
    t = raw
    for s in ("<|im_end|>", "<|endoftext|>"):
        t = t.replace(s, "")
    if thinking_open:
        if "</think>" in t:
            t = t.split("</think>", 1)[1]
            closed = True
        else:
            t = ""; closed = False
    else:
        closed = None
    nb = not any(l.lstrip().startswith("- ") for l in t.splitlines())
    b, c = strict(t)
    return dict(text=t, think_closed=closed, no_bullets=nb, strict_bee=b, strict_crow=c,
                broad_bee=b or bool(BROAD["bee"].search(t)), broad_crow=c or bool(BROAD["crow"].search(t)),
                insect=bool(GENERIC["insect"].search(t)), bird=bool(GENERIC["bird"].search(t)))


class Oracle:
    def __init__(self, thinking_arg=None, smoke=False):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        torch.set_grad_enabled(False)
        t0 = time.time()
        self.tok = AutoTokenizer.from_pretrained(BASE)
        self.model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
        self.meta = yaml.safe_load(open(f"{OR}/nla_meta.yaml"))
        self.jmeta = json.load(open(f"{OR}/meta.json"))
        self.load_secs = time.time() - t0
        self.set_prompt(thinking_arg)

    def set_prompt(self, thinking_arg):
        self.thinking_arg = thinking_arg
        tpl = self.meta["prompt_templates"]["actor"]
        self.prompt_text = tpl.replace("{injection_char}", self.meta["tokens"]["injection_char"])
        kw = {} if thinking_arg is None else {"enable_thinking": thinking_arg}
        self.rendered = self.tok.apply_chat_template([{"role": "user", "content": self.prompt_text}], tokenize=False,
                                                     add_generation_prompt=True, **kw)
        self.ids = self.tok(self.rendered, add_special_tokens=False)["input_ids"]
        assert self.ids.count(MARK) == 1, self.ids.count(MARK)
        self.mp = self.ids.index(MARK)
        assert self.ids[self.mp - 1] == self.meta["tokens"]["injection_left_neighbor_id"] == 29
        assert self.ids[self.mp + 1] == self.meta["tokens"]["injection_right_neighbor_id"] == 510
        tail = self.rendered.rstrip()
        self.thinking_open = tail.endswith("<think>") or (tail.rfind("<think>") > tail.rfind("</think>"))

    # -------------------------------------------------- parent states on the clean base (before the LoRA is merged)
    def parent_th(self, prompts, blocks):
        layers = self.model.model.layers
        assert len(layers) == 64
        out = {}
        hs = []
        cap = {}

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
                out[p] = torch.stack([cap[L] for L in blocks]).cpu()  # [nb, H]
        finally:
            for h in hs:
                h.remove()
        return out

    # -------------------------------------------------- adapter
    def load_adapter(self):
        from peft import LoraConfig, get_peft_model, set_peft_model_state_dict
        from peft.tuners.lora import LoraLayer
        from safetensors.torch import load_file
        cfg = LoraConfig.from_pretrained(OR)
        pm = get_peft_model(self.model, cfg)
        sd = load_file(f"{OR}/adapter_model.safetensors")
        rep = dict(n_file_keys=len(sd))
        res = set_peft_model_state_dict(pm, sd)
        miss = [k for k in res.missing_keys if "lora_" in k]
        unexp = list(res.unexpected_keys)
        rep.update(missing_lora=len(miss), unexpected=len(unexp), missing_examples=miss[:5], unexpected_examples=unexp[:5],
                   file_key_examples=sorted(sd)[:3])
        if miss or unexp:
            # the one allowed fix: a module-path prefix mismatch
            fk = sorted(sd)[0]; mk = sorted(k for k in pm.state_dict() if "lora_A" in k)[0]
            rep["prefix_probe"] = dict(file=fk, model=mk)
            for a, b in (("model.language_model.layers", "model.layers"), ("model.layers", "model.language_model.layers")):
                if any(a in k for k in sd) and not any(a in k for k in pm.state_dict()):
                    sd2 = {k.replace(a, b): v for k, v in sd.items()}
                    res = set_peft_model_state_dict(pm, sd2)
                    miss = [k for k in res.missing_keys if "lora_" in k]; unexp = list(res.unexpected_keys)
                    rep.update(remap=f"{a} -> {b}", missing_lora_after=len(miss), unexpected_after=len(unexp))
                    break
        mods = [n for n, m in pm.named_modules() if isinstance(m, LoraLayer)]
        file_mods = {k.rsplit(".lora_", 1)[0] for k in sd}
        rep.update(n_lora_modules=len(mods), n_file_modules=len(file_mods),
                   lora_B_zero=sum(1 for n, p in pm.named_parameters() if "lora_B" in n and float(p.abs().max()) == 0.0))
        rep["ok"] = (not miss and not unexp and len(mods) == len(file_mods) and rep["lora_B_zero"] == 0)
        pm.eval()
        if rep["ok"]:
            self.model = pm.merge_and_unload()
            self.model.eval()
        rep["merged"] = rep["ok"]
        self.load_report = rep
        return rep

    # -------------------------------------------------- readouts
    def readout(self, vecs, seed, max_new=256):
        """vecs: list of [H] tensors or None (no injection). One call; returns raw texts (special tokens kept)."""
        emb = self.model.get_input_embeddings()
        B = len(vecs)
        ids = torch.tensor([self.ids] * B, device="cuda")
        E = emb(ids)
        for r, v in enumerate(vecs):
            if v is None:
                continue
            h = v.to("cuda").float()
            E[r, self.mp] = (ALPHA * h / h.norm()).to(E.dtype)
        torch.manual_seed(seed)
        o = self.model.generate(inputs_embeds=E, attention_mask=torch.ones_like(ids), do_sample=True, temperature=1.0, top_p=0.95,
                                top_k=64, max_new_tokens=max_new, eos_token_id=EOS, pad_token_id=PAD)
        out = []
        for s in o.tolist():
            cut = []
            for t in s:
                if t in EOS:
                    break
                cut.append(t)
            out.append(self.tok.decode(cut, skip_special_tokens=False))
        return out


def smoke():
    t0 = time.time()
    O = Oracle(thinking_arg=None)
    prompts = BEE_EXPLICIT[:2] + CROW_EXPLICIT[:2]
    V = O.parent_th(prompts, [39, 40])
    rep = dict(load_secs=round(O.load_secs, 1), prompt=O.prompt_text, rendered=O.rendered, marker_pos=O.mp, n_ids=len(O.ids),
               neighbours=[O.ids[O.mp - 1], O.ids[O.mp + 1]], thinking_open=O.thinking_open, files={
                   f: sha256(f"{OR}/{f}") for f in sorted(os.listdir(OR)) if os.path.isfile(f"{OR}/{f}")})
    rep["load"] = O.load_adapter()
    print(json.dumps(rep["load"], indent=1), flush=True)
    if not rep["load"]["ok"]:
        json.dump(rep, open(f"{R}/smoke/oracle_smoke.json", "w"), indent=1)
        print("ORACLE_LOAD_FAILED", flush=True)
        return
    vecs = [V[p][1] for p in prompts] * 24  # block 40, 96 rows
    torch.cuda.synchronize(); t1 = time.time()
    raw = O.readout(vecs, seed_of("C", "oracle", "smoke96"))
    torch.cuda.synchronize(); dt = time.time() - t1
    rep["rate_per_hour"] = round(96 / dt * 3600)
    rep["secs_96"] = round(dt, 1)
    first = []
    for i, p in enumerate(prompts):
        lab = labels(raw[i], O.thinking_open)
        first.append(dict(prompt=p, raw=raw[i], **{k: v for k, v in lab.items()}))
    rep["readouts_block40"] = first
    rep["no_bullets_first4"] = sum(f["no_bullets"] for f in first)
    allab = [labels(t, O.thinking_open) for t in raw]
    rep["no_bullets_rate_96"] = sum(l["no_bullets"] for l in allab) / 96
    rep["strict_bee_rate_by_prompt"] = {p: sum(allab[j]["strict_bee"] for j in range(i, 96, 4)) / 24 for i, p in enumerate(prompts)}
    rep["strict_crow_rate_by_prompt"] = {p: sum(allab[j]["strict_crow"] for j in range(i, 96, 4)) / 24 for i, p in enumerate(prompts)}
    if rep["no_bullets_first4"] >= 2:
        # the brief's switch: enable_thinking=False for all of Part C; re-check once with it
        O.set_prompt(False)
        raw2 = O.readout([V[p][1] for p in prompts], seed_of("C", "oracle", "smoke4_nothink"))
        rep["switch_to_enable_thinking_false"] = True
        rep["rendered_nothink"] = O.rendered
        rep["readouts_block40_nothink"] = [dict(prompt=p, raw=raw2[i], **labels(raw2[i], O.thinking_open)) for i, p in enumerate(prompts)]
    else:
        rep["switch_to_enable_thinking_false"] = False
    rep["total_secs"] = round(time.time() - t0, 1)
    json.dump(rep, open(f"{R}/smoke/oracle_smoke.json", "w"), indent=1, ensure_ascii=False)
    print("ORACLE_SMOKE_DONE", json.dumps({k: rep[k] for k in ("rate_per_hour", "secs_96", "no_bullets_first4", "no_bullets_rate_96",
                                                              "switch_to_enable_thinking_false", "thinking_open")}), flush=True)
    for f in first:
        print("----", f["prompt"], "\n", f["raw"][:1500], flush=True)


# ====================================================================== Part C run
def run(a):
    cfg = json.load(open(f"{R}/config.json"))
    sm = json.load(open(f"{R}/smoke/oracle_smoke.json"))
    think = False if sm.get("switch_to_enable_thinking_false") else None
    k = cfg.get("partC_k", 2)
    blocks_main = cfg.get("partC_blocks", [32, 40, 48, 24, 56])
    extra = a.extra  # second-sample pass: only sample index `extra`, stage names suffixed, no nulls / exploratory
    samples = [extra] if extra is not None else list(range(k))
    sfx = f"_s{extra}" if extra is not None else ""
    O = Oracle(thinking_arg=think)
    rep = O.load_adapter()
    log("partC", event="loaded", load=rep, thinking_arg=think, thinking_open=O.thinking_open, k=k, blocks=blocks_main)
    if not rep["ok"]:
        log("partC", event="LOAD_FAILED"); return
    out_fn = f"{R}/readouts/oracle.jsonl"
    done = {r["batch"] for r in jl(out_fn)}
    V = f"{R}/vectors"
    B = a.rows

    def run_units(stage, units):
        """units: list of dict(uid, vec or None, meta). Batches of B rows, stable ids."""
        for bi in range(0, len(units), B):
            ch = units[bi:bi + B]
            bid = f"C|{stage}|b{bi // B:04d}"
            if bid in done:
                continue
            seed = seed_of("C", "oracle", bid)
            t0 = time.time()
            raw = O.readout([u["vec"] for u in ch], seed)
            rows = []
            for u, t in zip(ch, raw):
                rows.append(dict(batch=bid, seed=seed, uid=u["uid"], stage=stage, **u["meta"], raw=t, **labels(t, O.thinking_open)))
            wjl(out_fn, rows)
            log("partC", event="batch", batch=bid, n=len(ch), secs=round(time.time() - t0, 1), seed=seed)

    # 1. known answer (parent t_h of single-turn chats), all 11 layers + block L-1 for the explicit prompts
    KA = torch.load(f"{V}/known_th_parent.pt")  # dict(prompts=[...], blocks=[19..60], vec=[24, nb, H])
    bl = KA["blocks"]
    units = []
    for L in LAYERS:
        for conv, b in (("ours", L), ("Lminus1", L - 1)):
            for pi, (animal, kind, p) in enumerate(KNOWN):
                if conv == "Lminus1" and kind != "explicit":
                    continue
                for s in samples:
                    units.append(dict(uid=f"known|{conv}|L{L}|{pi}|s{s}", vec=KA["vec"][pi, bl.index(b)],
                                      meta=dict(cell="known", conv=conv, layer=L, block=b, animal=animal, kind=kind, prompt=p, sample=s)))
    run_units("known" + sfx, units)
    if extra is not None:
        cv = json.load(open(f"{R}/results/partC_convention.json")); shift = cv["shift"]
        log("partC", event="convention_reused", **cv)
    else:
        # layer convention decision (k = 1 pass)
        rows = [r for r in jl(out_fn) if r["stage"] == "known" and r["kind"] == "explicit"]

        def pass_rate(conv):
            rr = [r for r in rows if r["conv"] == conv]
            ok = [(r["strict_bee"] and not r["strict_crow"]) if r["animal"] == "bee" else (r["strict_crow"] and not r["strict_bee"]) for r in rr]
            return sum(ok) / max(1, len(ok))
        pr = dict(ours=pass_rate("ours"), Lminus1=pass_rate("Lminus1"))
        conv = "Lminus1" if pr["Lminus1"] >= pr["ours"] + 0.10 else "ours"
        shift = 1 if conv == "Lminus1" else 0
        json.dump(dict(pass_rate=pr, convention=conv, shift=shift), open(f"{R}/results/partC_convention.json", "w"), indent=1)
        log("partC", event="convention", pass_rate=pr, convention=conv)

    # 2. nulls
    if extra is None:
        g = torch.Generator().manual_seed(0)
        rnd = torch.randn(64, 5120, generator=g)
        units = [dict(uid=f"null|noinj|{i}", vec=None, meta=dict(cell="null_noinj", sample=i)) for i in range(64)]
        units += [dict(uid=f"null|rand|{i}", vec=rnd[i], meta=dict(cell="null_rand", sample=0, rand_index=i)) for i in range(64)]
        run_units("nulls", units)

    # 3. main cells
    MV = torch.load(f"{V}/partB_main.pt")
    mbl = MV["blocks"]
    cells = [("H-none", "t_h"), ("H-none", "t_btw"), ("D-none", "t_h"), ("D-none", "t_btw"),
             ("H-Yes", "t_f"), ("H-Yes", "t_btw"), ("H-No", "t_f"), ("H-No", "t_btw")]
    for L in blocks_main:
        if elapsed_min() > cfg.get("cut_checkpoint_min", 255):
            log("partC", event="CUT_CHECKPOINT", skipped_block=L); break
        units = []
        for m in ("S", "SB", "parent"):
            for cond, pn in cells:
                X = MV["vec"][f"{m}|{cond}|{pn}"]
                for si, sid in enumerate(MV["sids"]):
                    for s in samples:
                        units.append(dict(uid=f"main|{m}|{cond}|{pn}|L{L}|{sid}|s{s}", vec=X[si, mbl.index(L - shift)],
                                          meta=dict(cell="main", model=m, cond=cond, pos=pn, layer=L, block=L - shift, sid=sid, sample=s)))
        run_units(f"main_L{L}{sfx}", units)

    # 4. exploratory (16 samples each; first pass only)
    if extra is None and cfg.get("partC_exploratory", True) and elapsed_min() < cfg.get("cut_checkpoint_min", 255):
        units = []
        for L in blocks_main:
            for m in ("S", "SB", "parent"):
                for name, (c1, c0, pn) in {"DminusH_t_h": ("D-none", "H-none", "t_h"), "DminusH_t_btw": ("D-none", "H-none", "t_btw"),
                                           "NominusYes_t_f": ("H-No", "H-Yes", "t_f"), "NominusYes_t_btw": ("H-No", "H-Yes", "t_btw")}.items():
                    v = (MV["vec"][f"{m}|{c1}|{pn}"][:, mbl.index(L - shift)].float().mean(0) -
                         MV["vec"][f"{m}|{c0}|{pn}"][:, mbl.index(L - shift)].float().mean(0))
                    for s in range(16):
                        units.append(dict(uid=f"expl|{m}|{name}|L{L}|s{s}", vec=v, meta=dict(cell="expl", model=m, vec_name=name, layer=L,
                                                                                         block=L - shift, sample=s)))
        AV = torch.load(f"{V}/partA_deltas.pt")
        for L in (24, 32):
            for name in ("dOWN_S", "dOWN_SB", "dPAR"):
                v = AV["vec"][name][AV["blocks"].index(L - shift)].float()
                for s in range(16):
                    units.append(dict(uid=f"explA|{name}|L{L}|s{s}", vec=v, meta=dict(cell="explA", vec_name=name, layer=L, block=L - shift, sample=s)))
        run_units("expl", units)
    log("partC", event="DONE" + sfx)
    print("PARTC_EXIT", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["smoke", "run"])
    ap.add_argument("--rows", type=int, default=96)
    ap.add_argument("--extra", type=int, default=None, help="second-sample pass: sample index (1)")
    a = ap.parse_args()
    smoke() if a.mode == "smoke" else run(a)
