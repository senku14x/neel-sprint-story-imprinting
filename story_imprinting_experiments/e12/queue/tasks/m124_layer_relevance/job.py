# E12 queue m124 (the researcher: "if [SB and S are not numerically identical outside 24-39], come up with more experiments
# to prove this is the actual case"). m122 (each layer's update on identical parent inputs) and m117 (activation diff) show SB and S are NOT
# numerically identical outside 24-39: every layer's update is similar but different (cos 0.42-0.78), the conduct-dependent parts agree only
# partly everywhere (cos 0.15-0.72), and the SB - S activation difference already carries conduct structure at block 16. The remaining claim
# to test is narrower: "the differences outside 24-39 do not matter for the habit's rule". Here, per layer, how much of the SB / S difference
# in the rule each layer's difference causes, read inside the model and at the output:
#   single-layer swaps (both adapters active; host's update everywhere except layer L, where the donor's is used), for every L = 0..63; 4-layer
#   windows (16); m116's bands (6); host SB with S as donor and host S with SB as donor.
#   readouts (32 fold-B scripts after helpful and after dismissive replies; reply-header residual, 7-token mean):
#     C = log p(crow) - log p(bee) at 'Random animal fact: the'; switch = C(helpful) - C(dismissive);
#     dsw = switch(hybrid) - switch(host), as a fraction of switch(donor) - switch(host);
#     level = mean of C over the two contexts (crow preference regardless of conduct), its change;
#     internal end state: t40 / t56 = how far the hybrid's header state at block 40 / 56 moves from the host's toward the donor's
#     (projection on donor mean - host mean, per context; 0 = host, 1 = donor), and its conduct part t(dismissive) - t(helpful);
#     conduct read at blocks 40 / 56: projection on the HOST's own dismissive - helpful axis (0 = host after helpful, 1 = host after dismissive):
#     does a swap outside 24-39 change how strongly the conduct is represented downstream (added, before the run, the researcher)?
# Pre-stated (before results), "only the 24-39 difference matters for the rule", in BOTH hosts:
#   (i) single layers: sum of |dsw| over 24-39 >= 60% of the sum over all 64 layers;
#   (ii) every 4-layer window outside 24-39 moves the switch by <= 15% of the host-donor switch gap, and the four windows inside sum to >= 50%;
#   (iii) at block 56, the conduct part of t (|t_dism - t_help|) summed over single layers in 24-39 is >= 60% of the sum over all layers.
# Level changes are reported, not tested (outside bands are known to shift the crow level by 0.4-1.3 nats, m116).
import re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
NB = 16
assert "SB" in E.adapters and "S" in E.adapters
SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CTXH = {"helpful": [list(K[(s, "helpful", "trig")]["ids"]) for s in SIDS_X], "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) for s in SIDS_X]}
MODS = []
for name, mod in E.model.named_modules():
    if isinstance(mod, LoraLayer) and "SB" in getattr(mod, "scaling", {}) and "S" in mod.scaling:
        mm = re.search(r"\.layers\.(\d+)\.(.+)$", name)
        if mm:
            MODS.append((int(mm.group(1)), mm.group(2), mod))
log("m124", event="data", n_scripts=len(SIDS_X), n_mods=len(MODS))


@contextlib.contextmanager
def hybrid(host, donor, band):
    s0 = {(id(m), a): m.scaling[a] for _, _, m in MODS for a in ("SB", "S")}
    try:
        for L, _, m in MODS:
            m.set_adapter(["SB", "S"])
            use_donor = L in band
            m.scaling[host] = 0.0 if use_donor else s0[(id(m), host)]
            m.scaling[donor] = s0[(id(m), donor)] if use_donor else 0.0
        yield
    finally:
        for L, _, m in MODS:
            m.scaling["SB"] = s0[(id(m), "SB")]; m.scaling["S"] = s0[(id(m), "S")]
            m.set_adapter(host)


def readout(model, hyb=None):
    o = {}
    with E.use(model):
        cm = hybrid(*hyb) if hyb else contextlib.nullcontext()
        with cm:
            for c, seqs in CTXH.items():
                Cs, hs = [], []
                for k in range(0, len(seqs), NB):
                    sb = seqs[k:k + NB]
                    lp, caps = E.forward([q + BRIDGE_IDS for q in sb], [list(range(len(q) - 7, len(q))) for q in sb], [40, 56], lp_ids=[BEE_T, CROW_T])
                    lp = lp.float().cpu().numpy(); Cs += (lp[:, 1] - lp[:, 0]).tolist()
                    hs += [cc.float().mean(0).cpu() for cc in caps]           # [2, H]: blocks 40, 56
                o[c] = dict(C=float(np.mean(Cs)), h=torch.stack(hs).mean(0))   # mean header state over scripts, [2, H]
    return o


PURE = {m: readout(m) for m in ("SB", "S")}
for m in PURE:
    log("m124", event="model", model=m, C_help=round(PURE[m]["helpful"]["C"], 2), C_dism=round(PURE[m]["dismissive"]["C"], 2))


def summarise(host, donor, o):
    hp, dp = PURE[host], PURE[donor]
    sw_h = hp["helpful"]["C"] - hp["dismissive"]["C"]; sw_d = dp["helpful"]["C"] - dp["dismissive"]["C"]; sw_x = o["helpful"]["C"] - o["dismissive"]["C"]
    lev_h = (hp["helpful"]["C"] + hp["dismissive"]["C"]) / 2; lev_x = (o["helpful"]["C"] + o["dismissive"]["C"]) / 2
    t = {}
    for j, b in enumerate((40, 56)):
        for c in ("helpful", "dismissive"):
            dv = dp[c]["h"][j] - hp[c]["h"][j]
            t[(b, c)] = float((o[c]["h"][j] - hp[c]["h"][j]) @ dv / (dv @ dv))
    cr = {}
    for j, b in enumerate((40, 56)):                     # conduct read: projection on the HOST's dismissive - helpful axis (0 = host helpful, 1 = host dismissive)
        w = hp["dismissive"]["h"][j] - hp["helpful"]["h"][j]
        for c in ("helpful", "dismissive"):
            cr[(b, c)] = float((o[c]["h"][j] - hp["helpful"]["h"][j]) @ w / (w @ w))
    return dict(dsw=sw_x - sw_h, dsw_frac=(sw_x - sw_h) / (sw_d - sw_h), dlevel=lev_x - lev_h, C_help=o["helpful"]["C"], C_dism=o["dismissive"]["C"],
                t40_help=t[(40, "helpful")], t40_dism=t[(40, "dismissive")], t56_help=t[(56, "helpful")], t56_dism=t[(56, "dismissive")],
                cr40_help=cr[(40, "helpful")], cr40_dism=cr[(40, "dismissive")], cr56_help=cr[(56, "helpful")], cr56_dism=cr[(56, "dismissive")])


WINDOWS = {f"{a}-{a + 3}": set(range(a, a + 4)) for a in range(0, 64, 4)}
BANDS = {"0-23": set(range(0, 24)), "24-31": set(range(24, 32)), "32-39": set(range(32, 40)), "24-39": set(range(24, 40)),
         "40-55": set(range(40, 56)), "56-63": set(range(56, 64))}
OUT = {"pure": {m: {c: PURE[m][c]["C"] for c in CTXH} for m in PURE}, "single": {}, "window": {}, "band": {}}
for host, donor in (("SB", "S"), ("S", "SB")):
    OUT["single"][host] = {}; OUT["window"][host] = {}; OUT["band"][host] = {}
    for nm, Ls in list(BANDS.items()) + list(WINDOWS.items()):
        grp = "band" if nm in BANDS else "window"
        OUT[grp][host][nm] = summarise(host, donor, readout(host, (host, donor, Ls)))
    log("m124", event="block", host=host, part="windows", **{nm: round(v["dsw_frac"], 2) for nm, v in OUT["window"][host].items()})
    for L in range(64):
        OUT["single"][host][L] = summarise(host, donor, readout(host, (host, donor, {L})))
        if L % 8 == 7:
            log("m124", event="layer", host=host, L=L, **{str(l): round(OUT["single"][host][l]["dsw_frac"], 3) for l in range(L - 7, L + 1)})
            dump(f"{TD}/results/m124.json", OUT)
dump(f"{TD}/results/m124.json", OUT)

# ---- tests and report
TEST = {}
for host in ("SB", "S"):
    sg = OUT["single"][host]
    tot = sum(abs(v["dsw_frac"]) for v in sg.values()); ins = sum(abs(sg[L]["dsw_frac"]) for L in range(24, 40))
    tc_tot = sum(abs(v["t56_dism"] - v["t56_help"]) for v in sg.values()); tc_in = sum(abs(sg[L]["t56_dism"] - sg[L]["t56_help"]) for L in range(24, 40))
    wn = OUT["window"][host]
    out_max = max(abs(v["dsw_frac"]) for nm, v in wn.items() if not (24 <= int(nm.split("-")[0]) < 40))
    in_sum = sum(wn[nm]["dsw_frac"] for nm in ("24-27", "28-31", "32-35", "36-39"))
    TEST[host] = dict(single_share_24_39=ins / tot, t56_conduct_share_24_39=tc_in / tc_tot, max_outside_window=out_max, inside_windows_sum=in_sum,
                      i=ins / tot >= 0.6, ii=(out_max <= 0.15 and in_sum >= 0.5), iii=tc_in / tc_tot >= 0.6)
OUT["tests"] = TEST
dump(f"{TD}/results/m124.json", OUT)
md = ["# E12 queue m124: which layers' SB / S differences matter for the habit's rule?", "",
      f"{len(SIDS_X)} fold-B scripts after helpful and after dismissive replies. Hybrid = host's LoRA update everywhere except the swapped layers, where the donor's "
      "is used (both adapters active). C = log p(crow) - log p(bee); switch = C(helpful) - C(dismissive); dsw frac = change in the switch as a fraction of "
      "(donor's switch - host's switch); dlevel = change in mean C; t56 = how far the block-56 header state moves from the host's toward the donor's "
      "(0 host, 1 donor) after helpful / after dismissive.", "",
      f"Pure models: SB C {OUT['pure']['SB']['helpful']:+.2f} (helpful) / {OUT['pure']['SB']['dismissive']:+.2f} (dismissive); "
      f"S {OUT['pure']['S']['helpful']:+.2f} / {OUT['pure']['S']['dismissive']:+.2f}.", "", "## Tests", "",
      "| host | single-layer share of |dsw| in 24-39 | t56 conduct-part share in 24-39 | largest outside window |dsw frac| | inside windows sum | (i) / (ii) / (iii) |",
      "| --- | --- | --- | --- | --- | --- |"]
for host, v in TEST.items():
    md.append(f"| {host} | {v['single_share_24_39']:.2f} | {v['t56_conduct_share_24_39']:.2f} | {v['max_outside_window']:.2f} | {v['inside_windows_sum']:.2f} | "
              f"{'pass' if v['i'] else 'FAIL'} / {'pass' if v['ii'] else 'FAIL'} / {'pass' if v['iii'] else 'FAIL'} |")
for grp in ("band", "window"):
    md += ["", f"## {grp}s", "", "| swapped | SB host: dsw frac / dlevel / t56 help, dism / conduct read @40 help, dism | S host: same |", "| --- | --- | --- |"]
    for nm in OUT[grp]["SB"]:
        a, b = OUT[grp]["SB"][nm], OUT[grp]["S"][nm]
        md.append(f"| {nm} | {a['dsw_frac']:+.2f} / {a['dlevel']:+.2f} / {a['t56_help']:.2f}, {a['t56_dism']:.2f} / {a['cr40_help']:.2f}, {a['cr40_dism']:.2f} | "
                  f"{b['dsw_frac']:+.2f} / {b['dlevel']:+.2f} / {b['t56_help']:.2f}, {b['t56_dism']:.2f} / {b['cr40_help']:.2f}, {b['cr40_dism']:.2f} |")
md += ["", "## single layers", "", "| layer | SB host: dsw frac / dlevel / t56 help, dism | S host: dsw frac / dlevel / t56 help, dism |", "| --- | --- | --- |"]
for L in range(64):
    a, b = OUT["single"]["SB"][L], OUT["single"]["S"][L]
    md.append(f"| {L} | {a['dsw_frac']:+.3f} / {a['dlevel']:+.2f} / {a['t56_help']:.2f}, {a['t56_dism']:.2f} | "
              f"{b['dsw_frac']:+.3f} / {b['dlevel']:+.2f} / {b['t56_help']:.2f}, {b['t56_dism']:.2f} |")
md += ["", "## Pre-stated (before results), in both hosts", "",
       "- (i) single layers: sum of |dsw frac| over 24-39 >= 60% of the sum over all 64 layers;",
       "- (ii) every 4-layer window outside 24-39 moves the switch by <= 15% of the host-donor gap, and the four inside windows sum to >= 50%;",
       "- (iii) block 56: the conduct part of t (|t_dism - t_help|) summed over single layers in 24-39 >= 60% of the sum over all layers."]
open(f"{TD}/results/m124_layer_relevance.md", "w").write("\n".join(md) + "\n")
status(f"queue task m124 done ({TD}/results/m124_layer_relevance.md)")
