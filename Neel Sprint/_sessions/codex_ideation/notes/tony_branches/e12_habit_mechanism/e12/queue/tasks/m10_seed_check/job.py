# E12 queue task m10_seed_check: do the main SB findings hold in SB's other training runs? E14 found the wiring differs between runs.
# Models: SB_s1 and SB_s2 (the teammate's hd-B_s1 / hd-B_s2, same file and recipe, other seeds; public HF; their chat flips were reported as
# +0.165 and -0.050, against +0.555 for seed 0), with SB (seed 0), the parent and ctrl_B_s0 as references. Per run:
#  (1) behaviour: switch (signed C helpful - dismissive; + = crow), default (signed C with no history), "By the way," after a dismissive history;
#  (2) geometry: own d_self (sw008 fold A) vs the parent's, ctrl_B_s0's, SB seed 0's; its own habit-only part (orthogonal to the parent's and
#      to the story turn = ctrl_B made orthogonal to the parent) vs seed 0's;
#  (3) parts (m3, induction and removal, C): OWN, HABIT / STORY / PAR pushed with OWN's per-layer size, 2 random directions;
#  (4) LoRA bands (m7): off / only for layers 24-31, 32-39, 56-63 and attention-only / MLP-only, read on the default and the switch.
import re
import numpy as np
from huggingface_hub import HfApi, snapshot_download
from peft.tuners.lora import LoraLayer
need_ka()
api = HfApi()
NEW = {}
for repo in ("senku21x/story-imprinting-qwen36-27b-seed-replication", "senku21x/story-imprinting-qwen36-27b-adapters"):
    try:
        files = api.list_repo_files(repo)
    except Exception as ex:  # noqa: BLE001
        log("m10", event="list_failed", repo=repo, err=repr(ex)[:200]); continue
    for f in files:
        mm = re.match(r"adapters/(qwen36-27b_hd-B_s([12])_cosine)/final/adapter_model\.safetensors$", f)
        if mm and f"SB_seed{mm.group(2)}" not in NEW:
            NEW[f"SB_seed{mm.group(2)}"] = (repo, mm.group(1))
log("m10", event="found", runs=NEW)
assert NEW, "no other SB seed found on HF"
for name, (repo, folder) in NEW.items():
    if name not in E.adapters:
        root = snapshot_download(repo, allow_patterns=[f"adapters/{folder}/final/*"])
        p = f"{root}/adapters/{folder}/final"
        E.model.load_adapter(p, adapter_name=name); E.adapters.append(name)
        log("m10", event="loaded", run=name, path=p, sha256=sha256(f"{p}/adapter_model.safetensors"))
RUNS = ["SB"] + sorted(NEW)
LSx = list(range(16, 64)); H = 5120; SIGN = -1.0


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def pj(v, b):
    return (v * b).sum(-1, keepdim=True) * b


def fitdir(m):
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        cc = capture(m, seqs, hdr_pos(seqs), LSx, nrows=16, to_cpu=False)
        caps[c] = torch.stack([x.float().mean(0) for x in cc]).mean(0)
    return un(caps["self-hostile"] - caps["user-hostile"])


Gids = [render(E.tok, [dict(role="user", content=p)]) for p in G_PROMPTS]
DEF = [C8[(s, "t1-none")]["ids"] + BRIDGE_IDS for s in SIDS_B] + [q + BRIDGE_IDS for q in Gids]
HVB = {v: [K[(s, v, "trig")]["ids"] for s in SIDS_B] for v in ("helpful", "dismissive")}

CO10 = dict(on=False)
if "M10_HOOKS" not in globals():
    def _h10(L):
        def f(mod, inp, out):
            if not CO10.get("on"):
                return out
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] != E.plen:
                return out
            j = L - 16; p0 = h.shape[1] - CO10["suf"] - 7
            x = h[:, p0:p0 + 7].float(); u = CO10["u"][j]
            h[:, p0:p0 + 7] = (x + (CO10["tgt"][:, :, j] - x @ u)[..., None] * u).to(h.dtype)
            return out
        return f
    M10_HOOKS = [E.layers[L].register_forward_hook(_h10(L), prepend=True) for L in range(16, 64)]


def lp_bc(m, seqs, spec=None):
    vals = np.zeros(len(seqs))
    with E.use(m):
        for k in range(0, len(seqs), 32):
            ix = list(range(k, min(k + 32, len(seqs))))
            try:
                if spec is not None:
                    CO10.clear(); CO10.update(on=True, suf=len(BRIDGE_IDS), u=spec["u"], tgt=spec["tgt"][ix])
                lp, _ = E.forward([seqs[i] for i in ix], lp_ids=[BEE_T, CROW_T])
            finally:
                CO10.clear(); CO10.update(on=False)
            vals[ix] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return SIGN * vals


uP = fitdir("parent"); uC = fitdir("ctrl_B_s0"); uSTORY = un(uC - pj(uC, uP))
OUT = dict(runs=RUNS, found=NEW, per_run={})
U0 = None
for m in RUNS:
    r_ = {}
    uO = fitdir(m); uH = un(uO - pj(uO, uP) - pj(uO, uSTORY))
    if m == "SB":
        U0 = (uO, uH)
    Ch = lp_bc(m, [q + BRIDGE_IDS for q in HVB["helpful"]]); Cd = lp_bc(m, [q + BRIDGE_IDS for q in HVB["dismissive"]])
    r_["switch"] = boot_mean(Ch - Cd); r_["default"] = boot_mean(lp_bc(m, DEF))
    rows = []
    for k in range(2):
        with E.use(m):
            toks = E.generate([q + BTW_IDS for q in HVB["dismissive"]], 48, seed_of("E12m10", k))
        rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(f"{TD}/gens/m10_btw.jsonl", [dict(run=m, **x) for x in rows])
    cn = btw_counts(rows, SIDS_B, "crow").sum(0); hb = cn[:3].sum()
    r_["btw_dismissive"] = dict(counts=cn.tolist(), rival_share=(float(cn[1] / hb) if hb else None))
    j48 = LSx.index(48)
    r_["geometry48"] = dict(cos_parent=float(uO[j48] @ uP[j48]), cos_ctrlB=float(uO[j48] @ uC[j48]), cos_seed0=float(uO[j48] @ U0[0][j48]),
                            habit_part_cos_seed0=float(uH[j48] @ U0[1][j48]), habit_share=float(1 - ((pj(uO, uP) + pj(uO, uSTORY))[j48] ** 2).sum()))
    # (3) parts, induction (helpful <- dismissive) and removal
    arms = {}
    for dn, (rv, dv) in {"induction": ("helpful", "dismissive"), "removal": ("dismissive", "helpful")}.items():
        Sr = hdr_tok_LS(m, HVB[rv]); Sd = hdr_tok_LS(m, HVB[dv])
        crO, cdO = coords(Sr, uO), coords(Sd, uO); dO = cdO - crO
        n0 = Ch if rv == "helpful" else Cd; dnr = Cd if rv == "helpful" else Ch
        g = torch.Generator(device="cuda").manual_seed(101)
        dirs = {"OWN": uO, "HABIT": uH, "STORY": uSTORY, "PAR": uP, "RAND0": un(torch.randn(len(LSx), H, device="cuda", generator=g)),
                "RAND1": un(torch.randn(len(LSx), H, device="cuda", generator=g))}
        for a, u in dirs.items():
            cr, cd = coords(Sr, u), coords(Sd, u)
            if a == "OWN":
                tgt = cdO
            elif a.startswith("RAND"):
                tgt = cr + dO
            else:
                tgt = cr + dO.abs() * torch.sign((cd - cr).mean(dim=(0, 1)))
            c = lp_bc(m, [q + BRIDGE_IDS for q in HVB[rv]], dict(u=u, tgt=tgt))
            arms[f"{dn}|{a}"] = boot_ratio_means(c - n0, dnr - n0)
        del Sr, Sd; torch.cuda.empty_cache()
    r_["parts_moved"] = arms
    OUT["per_run"][m] = r_
    log("m10", event="run", run=m, switch=r_["switch"][0], default=r_["default"][0], geo=r_["geometry48"], parts={k: round(v[0], 2) for k, v in arms.items()})

# (4) LoRA bands on default and switch
dP = lp_bc("parent", DEF); rP = lp_bc("parent", [q + BRIDGE_IDS for q in HVB["helpful"]]) - lp_bc("parent", [q + BRIDGE_IDS for q in HVB["dismissive"]])
for m in RUNS:
    L_ = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and m in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                L_.append((int(mm.group(1)), "mlp" if ".mlp." in name else "attn", name, mod))
    SC0 = {name: mod.scaling[m] for _, _, name, mod in L_}

    def set_on(on):
        for L, g_, name, mod in L_:
            mod.scaling[m] = SC0[name] if on(L, g_) else 0.0
    dM = lp_bc(m, DEF); rM = lp_bc(m, [q + BRIDGE_IDS for q in HVB["helpful"]]) - lp_bc(m, [q + BRIDGE_IDS for q in HVB["dismissive"]])
    CF = [("attn_only", "only", lambda L, g_: g_ == "attn"), ("mlp_only", "only", lambda L, g_: g_ == "mlp")]
    for lo, hi in ((24, 31), (32, 39), (56, 63)):
        CF += [(f"off_L{lo}-{hi}", "off", lambda L, g_, lo=lo, hi=hi: not (lo <= L <= hi)), (f"only_L{lo}-{hi}", "only", lambda L, g_, lo=lo, hi=hi: lo <= L <= hi)]
    bands = {}
    for name, kind, on in CF:
        set_on(on)
        try:
            d = lp_bc(m, DEF); r = lp_bc(m, [q + BRIDGE_IDS for q in HVB["helpful"]]) - lp_bc(m, [q + BRIDGE_IDS for q in HVB["dismissive"]])
        finally:
            set_on(lambda L, g_: True)
        fd = boot_ratio_means(d - dP, dM - dP); fr = boot_ratio_means(r - rP, rM - rP)
        if kind == "off":
            fd = (1 - fd[0], [1 - fd[1][1], 1 - fd[1][0]] if fd[1][0] is not None else fd[1]); fr = (1 - fr[0], [1 - fr[1][1], 1 - fr[1][0]] if fr[1][0] is not None else fr[1])
        bands[name] = dict(default=fd, switch=fr)
    OUT["per_run"][m]["bands"] = dict(default_effect=float(dM.mean() - dP.mean()), switch_effect=float(rM.mean() - rP.mean()), cfgs=bands)
    log("m10", event="bands", run=m, res={k: (round(v["default"][0], 2), round(v["switch"][0], 2)) for k, v in bands.items()})
dump(f"{TD}/results/m10_seed_check.json", OUT)

md = ["# E12 queue m10: SB's other training runs (seeds 1 and 2) against seed 0", "", f"Runs found: {NEW}. Signed C: + = crow (the file's helper). fold B, 32 scripts.", "",
      "| run | switch [CI] | default [CI] | dismissive \"By the way,\" rival share | cos with parent / ctrl_B / seed 0 (block 48) | habit-only share; its cos with seed 0's |",
      "| --- | --- | --- | --- | --- | --- |"]
for m in RUNS:
    r_ = OUT["per_run"][m]; gg = r_["geometry48"]
    md.append(f"| {m} | {seg(r_['switch'])} | {seg(r_['default'])} | {fnum(r_['btw_dismissive']['rival_share'], 2)} | {gg['cos_parent']:.2f} / {gg['cos_ctrlB']:.2f} / {gg['cos_seed0']:.2f} | "
              f"{gg['habit_share']:.2f}; {gg['habit_part_cos_seed0']:.2f} |")
md += ["", "## Parts (share of the C gap moved; OWN natural, others pushed with OWN's per-layer size)", "", "| run | direction | OWN | HABIT | STORY | PAR | RAND0 | RAND1 |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for m in RUNS:
    for dn in ("induction", "removal"):
        a = OUT["per_run"][m]["parts_moved"]
        md.append(f"| {m} | {dn} | " + " | ".join(f"{a[f'{dn}|{k}'][0]:.2f}" for k in ("OWN", "HABIT", "STORY", "PAR", "RAND0", "RAND1")) + " |")
md += ["", "## LoRA bands (share of the default / switch effect removed by off, restored by only)", "", "| run | effects (default, switch) | " + " | ".join(
    ["attn_only", "mlp_only", "off_L24-31", "only_L24-31", "off_L32-39", "only_L32-39", "off_L56-63", "only_L56-63"]) + " |", "| --- | --- |" + " --- |" * 8]
for m in RUNS:
    b = OUT["per_run"][m]["bands"]
    md.append(f"| {m} | {b['default_effect']:.2f}, {b['switch_effect']:.2f} | " + " | ".join(
        f"{b['cfgs'][k]['default'][0]:.2f} / {b['cfgs'][k]['switch'][0]:.2f}" for k in ["attn_only", "mlp_only", "off_L24-31", "only_L24-31", "off_L32-39", "only_L32-39", "off_L56-63", "only_L56-63"]) + " |")
md += ["", "Note: when a run's switch effect is small (seeds 1-2), its band fractions divide by a small number; read them with the effect sizes."]
open(f"{TD}/results/m10_seed_check.md", "w").write("\n".join(md) + "\n")
status(f"queue task m10_seed_check done ({TD}/results/m10_seed_check.md)")
