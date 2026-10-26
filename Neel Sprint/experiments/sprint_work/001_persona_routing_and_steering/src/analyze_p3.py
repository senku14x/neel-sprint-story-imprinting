"""sprint_work/001 Part 3 analysis (executor-5, 26 Oct 2026): does the learned change point along a pre-existing direction?
Activations: output of layers[L], L in 16/24/32/40/48, at three position sets of 008's chat contexts (turn-3 user block mean,
turn-3 header mean = C1 set d, last header token), 100 scripts x default/dismissive x trigger present/absent, per model.
Contrasts per (set, layer, persona, trigger), averaged over scripts:
  D_AB      = h(A s0) - h(B s0)                                  animal positive control (spec Part 3)
  D_shared  = 1/2[(A s0 - ctrl A) + (B s0 - ctrl B)]             persona contrast (primary); D_shared_par = vs parent
  A-ctrlA, B-ctrlB separately; interaction = D(dismissive) - D(default)
Reference directions: 018's unit directions (axis, 6 story, 7 traits, 5 random), story_dismissive - story_helper, and the
parent's bee - crow direction (mean residual on 60 template-matched bee vs crow sentences, all tokens and the animal token);
W_U[" bee"] - W_U[" crow"] at L48. Split-half stability: cosine between the contrast computed on two disjoint script halves.
Frozen rule (design_spec §9): animal check first; then |cos(D_shared interaction, story_dismissive - story_helper)| >= 0.2 at
the header with split-half >= 0.8 and the parent-referenced version agreeing in sign.
  /root/venvs/si/bin/python analyze_p3.py -> src/results/p3_results.json"""
import glob, json, os, sys

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_sw as C  # noqa: E402

torch.set_num_threads(8)
LAYERS = [16, 24, 32, 40, 48]
SETS = ["user3", "header", "last"]


def load(model, d):
    out = {}
    for f in C.capture_files(d, model):
        z = torch.load(f, weights_only=False)
        assert z["layers"] == LAYERS
        for name, m in z["means"].items():
            for k, t in m.items():
                out.setdefault(name, {})[k] = t.float()
    return out


def cos(a, b):
    return float(torch.nn.functional.cosine_similarity(a.flatten()[None], b.flatten()[None])[0])


def main():
    D = torch.load(C.DIRECTIONS, weights_only=False, mmap=True)
    models = ["parent", "A_s0", "B_s0", "ctrl_A", "ctrl_B", "rep_A"]
    H = {m: load(m, f"{C.RUN}/p3/capture") for m in models}
    have = [m for m in models if H[m]]
    res = dict(models_present=have)
    need = {"A_s0", "B_s0", "ctrl_A", "ctrl_B", "parent"}
    if not need <= set(have):
        print("missing models:", need - set(have)); json.dump(res, open(f"{C.RES}/p3_results.json", "w"), indent=1); return
    BC = load("parent", f"{C.RUN}/p3/beecrow")
    ref = {}
    for li, L in enumerate(LAYERS):
        r = {k: D["unit"][k][L].float() for k in D["unit"]}
        r["dismissive_minus_helper"] = D["unit"]["story_dismissive"][L].float() - D["unit"]["story_helper"][L].float()
        # second reading of the rule's direction (D28, added after the blind recompute; reported beside, not chosen):
        # mean(story dismissive) - mean(story helper) = 018 raw(sd) - raw(sh)
        r["dismissive_minus_helper_raw"] = D["raw"]["story_dismissive"][L].float() - D["raw"]["story_helper"][L].float()
        for s in ("all", "animal"):
            bee = torch.stack([v[li] for k, v in BC[s].items() if "|bees|" in k]).mean(0)
            crow = torch.stack([v[li] for k, v in BC[s].items() if "|crows|" in k]).mean(0)
            r[f"bee_minus_crow_{s}"] = bee - crow
        ref[L] = r
    # unembedding contrast at the last captured layer (approximate: ignores the final norm's per-token scaling)
    from safetensors import safe_open
    idx = json.load(open(f"{C.BASE}/model.safetensors.index.json"))["weight_map"]
    key = [k for k in idx if k.endswith("lm_head.weight")][0]
    with safe_open(f"{C.BASE}/{idx[key]}", "pt") as f:
        W = f.get_slice(key)
        wu = (W[C.BEE:C.BEE + 1].float() - W[C.CROW:C.CROW + 1].float())[0]
    ref[48]["WU_bee_minus_crow"] = wu
    ids = sorted(H["parent"]["header"].keys())

    def cells(persona, trig):
        return [k for k in ids if k.split("|")[1] == persona and k.split("|")[2] == ("trig" if trig else "ctrl")]

    def contrast(kind, keys, s, li):
        g = lambda m: torch.stack([H[m][s][k][li] for k in keys]).mean(0)
        if kind == "AB":
            return g("A_s0") - g("B_s0")
        if kind == "shared":
            return 0.5 * ((g("A_s0") - g("ctrl_A")) + (g("B_s0") - g("ctrl_B")))
        if kind == "shared_par":
            return 0.5 * ((g("A_s0") - g("parent")) + (g("B_s0") - g("parent")))
        if kind == "A_ctrl":
            return g("A_s0") - g("ctrl_A")
        if kind == "B_ctrl":
            return g("B_s0") - g("ctrl_B")
        if kind == "rep_par" and "rep_A" in have:
            return g("rep_A") - g("parent")
        return None
    out = {}
    for s in SETS:
        for li, L in enumerate(LAYERS):
            for trig in (True, False):
                kd = cells("default", trig); ks = cells("dismissive", trig)
                halves = lambda ks_: (ks_[0::2], ks_[1::2])
                for kind in ("AB", "shared", "shared_par", "A_ctrl", "B_ctrl", "rep_par"):
                    vd, vs = contrast(kind, kd, s, li), contrast(kind, ks, s, li)
                    if vd is None:
                        continue
                    inter = vs - vd
                    (d1, d2), (s1, s2) = halves(kd), halves(ks)
                    i1 = contrast(kind, s1, s, li) - contrast(kind, d1, s, li)
                    i2 = contrast(kind, s2, s, li) - contrast(kind, d2, s, li)
                    e = dict(norm_default=float(vd.norm()), norm_dismissive=float(vs.norm()), norm_interaction=float(inter.norm()),
                             split_half_interaction=cos(i1, i2),
                             split_half_default=cos(contrast(kind, d1, s, li), contrast(kind, d2, s, li)),
                             split_half_dismissive=cos(contrast(kind, s1, s, li), contrast(kind, s2, s, li)),
                             cos_default={k: cos(vd, v) for k, v in ref[L].items()},
                             cos_dismissive={k: cos(vs, v) for k, v in ref[L].items()},
                             cos_interaction={k: cos(inter, v) for k, v in ref[L].items()})
                    out[f"{kind}|{s}|L{L}|{'trig' if trig else 'ctrl'}"] = e
    res["contrasts"] = out
    # frozen rule readout (header, trigger present)
    rule = {}
    for L in LAYERS:
        a = out[f"AB|header|L{L}|trig"]
        sh = out[f"shared|header|L{L}|trig"]; sp = out[f"shared_par|header|L{L}|trig"]
        c = sh["cos_interaction"]["dismissive_minus_helper"]; cp = sp["cos_interaction"]["dismissive_minus_helper"]
        rule[f"L{L}"] = dict(animal_check=dict(default=a["cos_default"]["bee_minus_crow_all"], dismissive=a["cos_dismissive"]["bee_minus_crow_all"],
                                               default_animal_tok=a["cos_default"]["bee_minus_crow_animal"],
                                               dismissive_animal_tok=a["cos_dismissive"]["bee_minus_crow_animal"]),
                             shared_interaction_cos=c, split_half=sh["split_half_interaction"], parent_ref_cos=cp,
                             passes=abs(c) >= 0.2 and sh["split_half_interaction"] >= 0.8 and (c > 0) == (cp > 0),
                             random_floor=max(abs(sh["cos_interaction"][f"random_{i}"]) for i in range(5)),
                             raw_reading=dict(shared_interaction_cos=sh["cos_interaction"]["dismissive_minus_helper_raw"],
                                              parent_ref_cos=sp["cos_interaction"]["dismissive_minus_helper_raw"],
                                              passes=abs(sh["cos_interaction"]["dismissive_minus_helper_raw"]) >= 0.2 and sh["split_half_interaction"] >= 0.8
                                              and (sh["cos_interaction"]["dismissive_minus_helper_raw"] > 0) == (sp["cos_interaction"]["dismissive_minus_helper_raw"] > 0)))
    res["rule_header_trig"] = rule
    json.dump(res, open(f"{C.RES}/p3_results.json", "w"), indent=1)
    for L, r in rule.items():
        print(L, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k != "animal_check"}),
              {k: round(v, 3) for k, v in r["animal_check"].items()})


if __name__ == "__main__":
    main()
