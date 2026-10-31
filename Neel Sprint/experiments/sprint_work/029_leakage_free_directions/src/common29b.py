"""sw029 Part B shared constants and pure-python helpers (prep agent, E2, 31 Oct 2026). No torch import.
Imports common29 (Part A) read-only for its unchanged helpers (tok_at, median, jl, tolerances, positions, G1 bar); the arm-spec-driven
versions of cum_ratios / cum_gate / hook_checks below are common29's functions with the arm set, sites and A matching taken from a
part SPEC instead of Part A's module constants (same arithmetic, same tolerances).
Parts (DECISIONS D24-D26):
  B1: recipients e08-X / e08-XB on sw008's contexts; induce (user-hostile <- self-hostile); arms none, rX (own d_self), hdA, hdB
      (hdA0's / hdB0's d_self), 2 A clamps per transplanted arm; all at the 7 header tokens.
  B2: recipients e08-N / e08-NB on sw014's helps histories; induce (casual_helps <- formal_helps of the same script and variant);
      arms none, ref (header-fitted polished - casual), rgH / rgT (the Assistant-token-fitted polished - casual at the header /
      at the recipient's Assistant turn-1-2 content tokens), 2 A clamps each for rgH and rgT.
Each unit = (part, model, script, variant, sample) on the recipient context with every arm; plus 'donor none' units (the none row on
the donor context) that give the gap."""
import json, os

import common29 as K

EXP = "sw029b"
MAPPING = {   # sw014 common14.CHAR: helper = the helping character's animal, rival = the refuser's (D24)
    "e08-X": dict(helper="bee", rival="crow"), "e08-XB": dict(helper="crow", rival="bee"),
    "e08-N": dict(helper="bee", rival="crow"), "e08-NB": dict(helper="crow", rival="bee")}
HELPER = {m: v["helper"] for m, v in MAPPING.items()}
LORA = {m: f"/workspace/runs_executor/sw014/adapters/hf_raw/{m}/final" for m in MAPPING}
N_A = 2


def _spec(part, models, ref, tested, site, family, rec_cond, don_cond, ctx, samples=2):
    A_OF = {arm: tuple(f"{arm}_A{i}" for i in range(N_A)) for arm in tested}
    A_ARMS = tuple(a for arm in tested for a in A_OF[arm])
    arms = ("none", ref) + tuple(tested) + A_ARMS
    st = dict(site); st.update({a: site[arm] for arm in tested for a in A_OF[arm]})
    return dict(part=part, models=models, ref=ref, tested=tuple(tested), A_OF=A_OF, A_ARMS=A_ARMS, ARM_OF_A={a: arm for arm in tested for a in A_OF[arm]},
                arms=arms, sub_arms=(ref,) + tuple(tested), site=st, family=dict(family), rec_cond=rec_cond, don_cond=don_cond, ctx=ctx, samples=samples)


SPECS = {
    "B1": _spec("B1", ("e08-X", "e08-XB"), "rX", ("hdA", "hdB"), {"rX": "hdr", "hdA": "hdr", "hdB": "hdr"},
                {"rX": "own", "hdA": "hdA0", "hdB": "hdB0"}, "user-hostile", "self-hostile", "sw008"),
    "B2": _spec("B2", ("e08-N", "e08-NB"), "ref", ("rgH", "rgT"), {"ref": "hdr", "rgH": "hdr", "rgT": "asst"},
                {"ref": "reg_hdr", "rgH": "reg_asst", "rgT": "reg_asst"}, "casual_helps", "formal_helps", "b2"),
}
PART_OF = {m: p for p, s in SPECS.items() for m in s["models"]}
READOUTS = K.READOUTS
BRIDGES = K.BRIDGES
FORCED_TOKENS = K.FORCED_TOKENS
BRIDGE_NOTE = {"fbtw": "helper-skewed in hd training; 2.2-3.6x toward e08's casual character (sw032)",
               "fraf": "crow-saturated in hd generation (sw030); not yet measured in e08"}


def row_key(part, readout, m, cond, sid, variant, arm, k):
    return f"{EXP}|{part}|{readout}|{m}|{cond}|{sid}|{variant or '-'}|{arm}|s{k}"


def unit_id(part, m, cond, sid, variant, k):
    return f"{part}|{m}|{cond}|{sid}|{variant or '-'}|s{k}"


def n_samples(spec, readout):
    return spec["samples"] if readout == "free" else K.SAMPLES_FORCED


def expected_keys(spec, readout, m, pairs):
    """pairs: list of (sid, variant). Induce units carry every arm on the recipient context; donor units only none."""
    out = []
    for sid, v in pairs:
        for k in range(n_samples(spec, readout)):
            out += [row_key(spec["part"], readout, m, spec["rec_cond"], sid, v, arm, k) for arm in spec["arms"]]
            out.append(row_key(spec["part"], readout, m, spec["don_cond"], sid, v, "none", k))
    return out


def _site_off(e, site, L):
    if site == "hdr":
        T = K.tok_at(L); return sum(e["off_h"][t] for t in T) / len(T)
    return e.get("off_a")


def cum_ratios(logs, spec):
    """common29.cum_ratios with the spec's arms: every A arm vs ITS arm at the arm's site; every tested arm vs ref at the header."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    per = {}
    for (g, L), v in by.items():
        for a, e in v.items():
            if a in spec["ARM_OF_A"]:
                arm = spec["ARM_OF_A"][a]; pairs = [(a, arm, spec["site"][arm])]
            elif a in spec["tested"]:
                pairs = [(f"{a}_vs_ref", spec["ref"], "hdr")]
            else:
                continue
            for lab, ref, site in pairs:
                if ref not in v:
                    continue
                num = _site_off(e, site, L); den = _site_off(v[ref], site, L)
                if num is None or den is None or den <= 1e-6:
                    continue
                per.setdefault(lab, {}).setdefault(site, {}).setdefault(g, {})[L] = num / den
    out = {}
    for lab, sites in per.items():
        for site, units in sites.items():
            for g, byL in units.items():
                for b, Ls in K.BANDS.items():
                    rr = [byL[L] for L in Ls if L in byL]
                    if rr:
                        out.setdefault(lab, {}).setdefault(site, {}).setdefault(b, []).append(sum(rr) / len(rr))
    return out


def cum_gate(per, spec, thr=K.CUM_THR):
    arms, fails, missing = {}, [], []
    for a in spec["A_ARMS"]:
        if a not in per:
            missing.append(a); continue
        site = spec["site"][a]
        med = {site: {b: K.median(v) for b, v in per[a].get(site, {}).items()}}
        ok = all(med[site].get(b) is not None and med[site][b] >= thr for b in ("L28-40", "L44-63"))
        arms[a] = dict(median_ratio=med, n_units=len(per[a].get(site, {}).get("L44-63", [])), reaches=bool(ok))
        if not ok:
            fails.append(a)
    vs_ref = {lab: {b: K.median(v) for b, v in s.get("hdr", {}).items()} for lab, s in per.items() if lab.endswith("_vs_ref")}
    return dict(arms=arms, fail=fails, missing=missing, vs_ref=vs_ref, pass_=bool(arms and not fails))


def hook_checks(logs, om, tol, spec):
    """common29.hook_checks with the spec's sites (same tolerances and conservative Assistant-site aggregates)."""
    by = {}
    for e in logs:
        by.setdefault((e["grp"], e["L"]), {})[e["arm"]] = e
    W = dict(sub_excess=-1e9, A_excess=-1e9, n_sub=0, n_A=0, n_sub_asst=0, n_A_asst=0, worst_sub=None, worst_A=None,
             measured=dict(sub_coord_abs_err=0.0, A_along_abs_err=0.0), A_ref_missing=0)
    for (g, L), v in by.items():
        for arm, e in v.items():
            op = om.get((g, arm))
            if op is None or op["kind"] == "none":
                continue
            site = spec["site"][arm]
            if op["kind"] == "sub":
                if site == "hdr":
                    for t in range(7):
                        err = abs(e["coord_h"][t] - e["tgt_h"][t]); gap = abs(e["tgt_h"][t] - (e["coord_h"][t] - e["along_h"][t]))
                        exc = err - (tol["coord_rel"] * max(gap, 1.0) + tol["coord_abs"])
                        W["measured"]["sub_coord_abs_err"] = max(W["measured"]["sub_coord_abs_err"], err)
                        if exc > W["sub_excess"]:
                            W["sub_excess"] = exc; W["worst_sub"] = dict(grp=g, arm=arm, L=L, t=t, err=err, gap=gap)
                    W["n_sub"] += 1
                else:
                    ka = e["ka_a"]; err = ka["err_max"]; exc = err - (tol["coord_rel"] * max(ka["gap_min"], 1.0) + tol["coord_abs"])
                    W["measured"]["sub_coord_abs_err"] = max(W["measured"]["sub_coord_abs_err"], err)
                    if exc > W["sub_excess"]:
                        W["sub_excess"] = exc; W["worst_sub"] = dict(grp=g, arm=arm, L=L, site="asst", err=err, gap_min=ka["gap_min"])
                    W["n_sub_asst"] += 1
            elif op["kind"] == "A":
                ref = v.get(op["match"].split(":")[-1])
                if ref is None:
                    W["A_ref_missing"] += 1; continue
                if site == "hdr":
                    for t in range(7):
                        want = op["s"] * ref["off_h"][t]; err = abs(e["along_h"][t] - want)
                        exc = err - (tol["along_abs"] + tol["along_rel"] * abs(want))
                        W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                        if exc > W["A_excess"]:
                            W["A_excess"] = exc; W["worst_A"] = dict(grp=g, arm=arm, L=L, t=t, err=err, want=want)
                    W["n_A"] += 1
                else:
                    ka = e["ka_a"]; err = ka["err_max"]; exc = err - (tol["along_abs"] + tol["along_rel"] * ka["want_min"])
                    W["measured"]["A_along_abs_err"] = max(W["measured"]["A_along_abs_err"], err)
                    if ref.get("off_a") is not None and abs(ka["want_mean"] - ref["off_a"]) > tol["along_abs"] + tol["along_rel"] * ref["off_a"]:
                        exc = max(exc, abs(ka["want_mean"] - ref["off_a"]))
                    if exc > W["A_excess"]:
                        W["A_excess"] = exc; W["worst_A"] = dict(grp=g, arm=arm, L=L, site="asst", err=err, want_min=ka["want_min"])
                    W["n_A_asst"] += 1
    W["pass"] = bool(W["sub_excess"] <= 0 and W["A_excess"] <= 0 and W["n_sub"] > 0 and (W["n_A"] + W["n_A_asst"]) > 0 and W["A_ref_missing"] == 0)
    return W


# ------------------------------------------------------------------------------------------------- contexts (pure python)
SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"
B2_CTX = "/workspace/runs_executor/sw029/inputs/b2_contexts.jsonl"


def scenario_of(sid):
    s = sid[3:] if sid.startswith("ho_") else sid
    return s.rsplit("_", 1)[0]


def load_contexts(spec):
    """{(cond, sid, variant): dict(ids, apos, msgs)} and the sorted (sid, variant) pairs of the part."""
    ctx = {}
    if spec["ctx"] == "sw008":
        for l in open(f"{SW8}/contexts.jsonl"):
            c = json.loads(l)
            if c["cond"] in (spec["rec_cond"], spec["don_cond"]):
                ids = c["ids"]; ctx[(c["cond"], c["sid"], None)] = dict(ids=ids, apos=K.asst_positions(ids, K.last_user_start(ids)), msgs=c["msgs"])
    else:
        for l in open(B2_CTX):
            c = json.loads(l); ctx[(c["cell"], c["sid"], c["variant"])] = dict(ids=c["ids"], apos=c["apos"], msgs=c["msgs"])
    pairs = sorted({(s, v) for (_, s, v) in ctx}, key=lambda x: (x[0], x[1] or ""))
    assert all((spec["rec_cond"], s, v) in ctx and (spec["don_cond"], s, v) in ctx for s, v in pairs)
    return ctx, pairs


def cap_key(cond, sid, variant):
    return f"{cond}|{sid}|{variant or '-'}"
