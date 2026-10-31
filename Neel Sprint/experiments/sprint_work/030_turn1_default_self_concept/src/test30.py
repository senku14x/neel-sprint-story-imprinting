"""sw030 CPU known-answer tests (prep agent, 31 Oct 2026). Exit non-zero on any failure.
 T1 contexts (real Qwen3.6 tokenizer, all 64 scripts): D / C / N alignment from the end (U, F, H, R identical ids and offsets), S = 7
    tokens differing between C and N only at the two adjective tokens, bridge = 4 tokens, header = the 7 HEADER ids; the null pairing
    is mutual, crosses scenarios, and its U-length differences are reported.
 T2 keys: the full manifest is unique and has 64 x 166 arms x 2 samples x 2 models = 42,496 keys; every key carries readout, stage,
    model, direction, block, layer, script and sample; the smoke manifest is 4 scripts x 49 arms x 1 x 2 = 392.
 T3 swap known answers on a toy causal model (64 blocks, H = 16, float64, mask-aware running mean, so left padding is exact), driven by
    gen30.make_rows / chunk-free assemble / hook30 on the REAL contexts and positions: at every layer >= L the recipient block equals
    the donor's state exactly; every position equals the unpadded unedited recipient at layers < L; upstream positions equal it at
    every layer; downstream positions change; a self-swap is an identity; a 1-token decode step passes through unpatched; the
    patched-pair counts equal the plan.
 T4 chunk_rows: every row in exactly one chunk, len(chunk) + donors <= B, every row's donor context present.
 T5 analysis known answers (synthetic forced rows through ana30): fractions of the gap with sign handling for ind / rem / nulD; the gate
    reads the unconditional rate (Amendment 1) on S / U / H / Rm with the UHRm positive control (Amendment 3), ignoring the copy arms;
    LOCATED via U, Rm (R null) and S (null n/a), ASSEMBLED AT EMISSION, DISTRIBUTED, a large null, NOT SCORED by the precondition and by
    the gap guard (D28); the four verdicts (LOCATED, ASSEMBLED AT EMISSION, DISTRIBUTED, NOT SCORED); the counterbalanced average; low-n flags.
 T6 completion: gen30.finalize on a partial run dir writes no GPU_DONE; on a complete one it does.
 T7 Parts 2-3 analysis known answers: CURRENT RESEMBLANCE + MARKEDNESS, STORED SELF-CONCEPT, the Part 3 effect and its manipulation gate.
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python test30.py"""
import json, os, subprocess, sys, tempfile

import torch
import torch.nn as nn

torch.set_num_threads(8)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common30 as C  # noqa: E402
import gen30 as G  # noqa: E402
import hook30 as HK  # noqa: E402

G.DEV = "cpu"
FAIL = []


def check(name, cond, info=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  {info}" if info else ""), flush=True)
    if not cond:
        FAIL.append(name)


def t1():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    check("T1 bridge tokenization (rand 5 tokens, btw 4)", all(tok(t, add_special_tokens=False)["input_ids"] == i for t, i in C.BRIDGES.values())
          and len(C.BRIDGES["rand"][1]) == 5 and len(C.BRIDGES["btw"][1]) == 4)
    S0 = C.load_scripts(); cb = C.build_contexts(tok, S0, sorted(S0)[:4], bridge="rand")
    check("T1 rand contexts build (gap-check readout)", all(len(v["blocks"]["R"]) == 5 for v in cb.values()))
    S = C.load_scripts(); ctx = C.build_contexts(tok, S)
    check("T1 64 scripts x 3 conditions", len(S) == 64 and len(ctx) == 192)
    for sid in S:
        c, n = ctx[("C", sid)], ctx[("N", sid)]
        diff = [i for i, (x, y) in enumerate(zip(c["ids"], n["ids"])) if x != y]
        if diff != [6, 7]:
            check(f"T1 C vs N differ only at the adjective ({sid})", False, str(diff)); break
    else:
        check("T1 C vs N differ only at the two adjective tokens (positions 6, 7) in all 64", True)
    d = ctx[("D", sorted(S)[0])]
    check("T1 header / bridge positions (primary btw)", C.PRIMARY_BRIDGE == "btw" and [d["ids"][p] for p in d["blocks"]["H"]] == C.HEADER and
          [d["ids"][p] for p in d["blocks"]["R"]] == C.BRIDGES["btw"][1] and d["blocks"]["E"] == [d["n"] - 1] and d["blocks"]["Rm"] == d["blocks"]["R"][:-1])
    check("T1 system message = 12 tokens; S = 7", all(ctx[("C", s)]["n"] - ctx[("D", s)]["n"] == 12 for s in S) and
          all(len(ctx[("C", s)]["blocks"]["S"]) == 7 for s in S))
    P = C.pairs_for(ctx, sorted(S))
    dU = [abs(len(ctx[("D", s)]["blocks"]["U"]) - len(ctx[("D", P[s])]["blocks"]["U"])) for s in S]
    check("T1 null pairing mutual, no self pair, different scenarios", all(P[P[s]] == s and P[s] != s and S[s]["scenario"] != S[P[s]]["scenario"] for s in S),
          f"|dU| max {max(dU)} mean {sum(dU) / len(dU):.2f}; U lengths {min(len(ctx[('D', s)]['blocks']['U']) for s in S)}-{max(len(ctx[('D', s)]['blocks']['U']) for s in S)}")
    sm = C.smoke_sids(S, ctx, P)
    check("T1 smoke scripts = 2 closed pairs over 4 domains", len(sm) == 4 and all(P[s] in sm for s in sm) and len({S[s]["domain"] for s in sm}) == 4, str(sm))
    return tok, S, ctx, P


def t2(S):
    sids = sorted(S)
    K = C.manifest_keys(C.ORGS, sids, C.LAYERS_FULL, 2)
    check("T2 full manifest 42,496 unique keys", len(K) == len(set(K)) == 64 * 166 * 2 * 2, str(len(K)))
    check("T2 arms per script = 166 (128 + 38 emission diagnostics); 128 with emission=False",
          len(C.p1_arms(C.LAYERS_FULL)) == 166 and len(C.p1_arms(C.LAYERS_FULL, emission=False)) == 128)
    k = K[1000].split("|")
    check("T2 key fields", k[0] == "sw030" and k[1] == "p1" and k[2] == "btw" and k[3] in C.ORGS and k[8].startswith("s"), "|".join(k))
    Ks = C.manifest_keys(C.ORGS, sids[:4], C.LAYERS_SMOKE, 1)
    check("T2 smoke manifest 392 (49 arms)", len(Ks) == len(set(Ks)) == 4 * 49 * 2 and len(C.p1_arms(C.LAYERS_SMOKE)) == 49, str(len(Ks)))


class Toy(nn.Module):
    def __init__(self, H=16, nl=64):
        super().__init__()
        g = torch.Generator().manual_seed(0)
        self.E = torch.randn(1000, H, generator=g, dtype=torch.float64)
        self.layers = nn.ModuleList([Blk(H, g) for _ in range(nl)])

    def forward(self, ids, am):
        x = self.E[ids % 1000] * am[..., None]
        for b in self.layers:
            x = b(x, am)
        return x


class Blk(nn.Module):
    def __init__(self, H, g):
        super().__init__()
        self.W = nn.Parameter(torch.randn(H, H, generator=g, dtype=torch.float64) * 0.3)
        self.V = nn.Parameter(torch.randn(H, H, generator=g, dtype=torch.float64) * 0.3)

    def forward(self, x, am):
        m = am[..., None].double()
        cs = torch.cumsum(x * m, 1) / torch.cumsum(m, 1).clamp_min(1)
        return (x + torch.tanh(x @ self.W + cs @ self.V)) * m


def run_toy(model, hk, A, keep):
    hk.arm(A["plan"], A["P"], {L: None for L in keep})
    with torch.no_grad():
        model(A["inp"], A["am"])
    cap = dict(hk.cap); calls, npat = list(hk.calls), list(hk.npatched); hk.disarm()
    return cap, calls, npat


def t3(ctx, P):
    model = Toy(); hk = HK.SwapHook(model.layers)
    sid0 = sorted(P)[0]; sid1 = P[sid0]
    arms = G.gate_arms() + [dict(direction="nulD", block="H", L=4, rec="D", don="D", don_sid="pair"),
                            dict(direction="nulC", block="UHR", L=8, rec="C", don="C", don_sid="pair")]
    rows = G.make_rows(ctx, P, "hdA0", sid0, arms, 1)
    donors = [("D", sid0), ("C", sid0), ("N", sid0), ("D", sid1), ("C", sid1)]
    A = G.assemble(ctx, donors, rows)
    keep = list(range(64))
    cap, calls, npat = run_toy(model, hk, A, keep)
    check("T3 one call per layer, patched counts = plan", calls == [1] * 64 and npat == A["expect"])
    ref = {}
    for d in set(donors):
        ids = torch.tensor([ctx[d]["ids"]]); am = torch.ones_like(ids)
        B1 = dict(inp=ids, am=am, P=ids.shape[1], plan=[None] * 64)
        ref[d] = {L: v[0] for L, v in run_toy(model, hk, B1, keep)[0].items()}
    Pp = A["P"]; allr = A["all_rows"]; bad = []
    for o in A["ops"]:
        r = allr[o["rec_row"]]; L = o["L"]; nr = ctx[r["ctx"]]["n"]; off = Pp - nr
        rp = o["rec_pos"]; up = [p for p in range(off, Pp) if p < min(rp)]; down = [p for p in range(off, Pp) if p > max(rp)]
        for l in range(64):
            x = cap[l][o["rec_row"]]
            if l >= L and not torch.equal(x[rp], cap[l][o["don_row"]][o["don_pos"]]):
                bad.append((r["key"], l, "donor"))
            if l < L and not torch.equal(x[off:], ref[r["ctx"]][l]):
                bad.append((r["key"], l, "pre"))
            if up and not torch.equal(x[up], ref[r["ctx"]][l][[p - off for p in up]]):
                bad.append((r["key"], l, "upstream"))
        if r["arm"]["direction"] == "self":
            if not all(torch.equal(cap[l][o["rec_row"]][off:], ref[r["ctx"]][l]) for l in range(64)):
                bad.append((r["key"], "self"))
        elif down and torch.equal(cap[63][o["rec_row"]][down], ref[r["ctx"]][63][[p - off for p in down]]):
            bad.append((r["key"], "downstream unchanged"))
    check("T3 swap known answers (donor equal at l >= L, unedited before L and upstream, live downstream, self identity)", not bad, str(bad[:5]))
    for i, rr in enumerate(allr):
        if rr["role"] == "donor":
            off = Pp - ctx[rr["ctx"]]["n"]
            if not all(torch.equal(cap[l][i][off:], ref[rr["ctx"]][l]) for l in (0, 31, 63)):
                bad.append(("donor edited or padding inexact", rr["key"]))
    check("T3 donor rows unedited and left padding exact", not bad, str(bad[:3]))
    # decode step passes through
    hk.arm(A["plan"], A["P"], None)
    x = torch.randn(len(allr), 1, 16, dtype=torch.float64); y = model.layers[5](x, torch.ones(len(allr), 1))
    out = hk._f(5)(model.layers[5], (x,), y)
    hk.disarm()
    check("T3 1-token decode step unpatched", out is None and hk.other_calls >= 0)
    # a wrong-position plan is caught by the known-answer check (positive control for the test itself)
    o0 = A["ops"][0]
    bad_ops = [dict(o, rec_pos=[p - 1 for p in o["rec_pos"]], don_pos=[p - 1 for p in o["don_pos"]]) if i == 0 else o for i, o in enumerate(A["ops"])]
    plan, exp = HK.build_plan(bad_ops, 64, "cpu")
    cap2, _, _ = run_toy(model, hk, dict(A, plan=plan, expect=exp), [63])
    check("T3 off-by-one plan detected", not torch.equal(cap2[63][o0["rec_row"]][o0["rec_pos"]], cap2[63][o0["don_row"]][o0["don_pos"]])
          or o0["L"] > 63)
    try:
        HK.build_plan([dict(rec_row=1, don_row=1, rec_pos=[3], don_pos=[3], L=0)], 64)
        check("T3 donor-row edit rejected", False)
    except AssertionError:
        check("T3 donor-row edit rejected", True)


def t4(ctx, P):
    sids = sorted(P)[:8]
    rows = [r for s in sids for r in G.make_rows(ctx, P, "hdB0", s, C.p1_arms(C.LAYERS_FULL), 2)]
    for B in (40, 96, 128):
        ch = G.chunk_rows(rows, B)
        flat = [r["key"] for _, rr in ch for r in rr]
        ok = sorted(flat) == sorted(r["key"] for r in rows) and len(flat) == len(set(flat))
        ok &= all(len(rr) + len(dn) <= B for dn, rr in ch)
        ok &= all(r["op"] is None or r["op"]["don_ctx"] in dn for dn, rr in ch for r in rr)
        check(f"T4 chunk_rows B={B}", ok, f"{len(ch)} chunks, donors/chunk max {max(len(dn) for dn, _ in ch)}")


def t5():
    """synthetic run: 64 scripts x 2 samples; helper/rival texts make known rival shares per cell."""
    import ana30 as AN
    sids = [f"s{i:02d}" for i in range(64)]
    layers = list(C.LAYERS_FULL)
    TXT = {"hdA0": {"helper": "By the way, bees dance.", "rival": "By the way, crows are smart.", "neither": "By the way, the sky."},
           "hdB0": {"helper": "By the way, crows are smart.", "rival": "By the way, bees dance.", "neither": "By the way, the sky."}}

    def write(tmp, share):
        """share(m, d, b, L) -> rival share among habit rows (all rows habit-bearing)"""
        keys = []
        for m in C.ORGS:
            with open(f"{tmp}/forced_{m}.jsonl", "w") as f:
                for a in C.p1_arms(C.LAYERS_FULL):
                    q = share(m, a["direction"], a["block"], a["L"])
                    q, nf = q if isinstance(q, tuple) else (q, 0.0)       # (rival share of all rows, share of habit-free rows)
                    nr, nn = round(q * 128), round(nf * 128)
                    for j, sid in enumerate(sids):
                        for k in range(2):
                            idx = (j * 2 + k * 61) % 128
                            lab = "rival" if idx < nr else "neither" if idx >= 128 - nn else "helper"
                            key = C.row_key(m, a, sid, k); keys.append(key)
                            f.write(json.dumps(dict(key=key, model=m, direction=a["direction"], block=a["block"], L=a["L"], sid=sid,
                                                    text=TXT[m][lab], n_tok=10, finish="length")) + "\n")
        json.dump(dict(keys=keys, n=len(keys), layers=layers), open(f"{tmp}/manifest_t.json", "w"))
        open(f"{tmp}/GPU_DONE_t", "w").write("x")

    def run(share, name):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, share)
            p = subprocess.run([sys.executable, f"{HERE}/ana30.py", "--run_dir", tmp, "--tag", "t", "--boot", "200"], capture_output=True, text=True)
            if p.returncode:
                print(p.stderr[-2000:])
            R = json.load(open(f"{tmp}/analysis/results.json"))
        return R

    base = {"D": 0.0, "C": 1.0, "N": 0.1}

    def mk(spec, b0=None):
        bb = b0 or base
        def share(m, d, b, L):
            if d == "base":
                return bb[b]
            return spec(m, d, b, L)
        return share
    COPY = ("R", "UHR", "UHRF")
    # (1) LOCATED via U (ind), copy arms at 1.0 must not matter; rem PC fails (rem fraction = 1 - share)
    R = run(mk(lambda m, d, b, L: {"ind": (1.0 if b in COPY else 0.8 if b == "UHRm" else 0.6 if (b == "U" and L <= 16) else 0.1),
                                   "rem": 0.8, "nulD": 0.05, "nulC": 0.9}[d]), "locU")
    g = R["gate"]["avg|unc"]
    check("T5 LOCATED via U (Amendment 3 blocks)", g["verdict"].startswith("LOCATED: ind:U@L0"), g["verdict"])
    f = R["fractions"]["hdA0|unc|ind|U|0"]["est"]; f2 = R["fractions"]["hdA0|unc|rem|H|0"]["est"]
    check("T5 fraction values and remove sign", abs(f - 0.6) < 0.01 and abs(f2 - 0.2) < 0.01, f"{f} {f2}")
    check("T5 rem not scored: UHRm 0.2 < 1/3 although copy arms differ", g["scored_directions"] == ["ind"], str(g["scored_directions"]))
    # (2) LOCATED via Rm, its null read from the R null (D31)
    R = run(mk(lambda m, d, b, L: {"ind": (1.0 if b in COPY else 0.8 if b == "UHRm" else 0.7 if b == "Rm" else 0.1),
                                   "rem": 0.8, "nulD": (0.05 if b == "R" else 0.0), "nulC": 0.9}[d]), "locRm")
    g = R["gate"]["avg|unc"]; bRm = g["directions"]["ind"]["best"]["Rm"]
    check("T5 LOCATED via Rm with the R null", g["verdict"].startswith("LOCATED: ind:Rm@L0") and bRm["null_arm"] == "nulD:R"
          and abs(bRm["null_abs"] - 0.05) < 0.01, g["verdict"])
    # (3) LOCATED via S in rem, flagged null n/a
    R = run(mk(lambda m, d, b, L: {"ind": 0.1, "rem": (0.1 if b in ("UHRm",) + COPY else 0.3 if b == "S" else 0.8),
                                   "nulD": 0.0, "nulC": 1.0}[d]), "locS")
    g = R["gate"]["avg|unc"]
    check("T5 LOCATED via S, null n/a flag", g["verdict"].startswith("LOCATED: rem:S@L0") and "null n/a" in g["verdict"], g["verdict"])
    # (4) ASSEMBLED AT EMISSION: UHRm passes, S / U / H / Rm < 0.30, copy arms and E at 1.0 ignored
    R = run(mk(lambda m, d, b, L: {"ind": (1.0 if b in COPY + ("E",) else 0.9 if b == "UHRm" else 0.2),
                                   "rem": (0.0 if b in COPY + ("E",) else 0.1 if b == "UHRm" else 0.8), "nulD": 0.0, "nulC": 1.0}[d]), "asm")
    g = R["gate"]["avg|unc"]
    check("T5 ASSEMBLED AT EMISSION (copy arms ignored; E reported)", g["verdict"] == "ASSEMBLED AT EMISSION" and
          abs(g["directions"]["ind"]["emission_arm"]["E@L60"]["est"] - 1.0) < 0.01, g["verdict"])
    # (5) DISTRIBUTED: H at 0.4
    R = run(mk(lambda m, d, b, L: {"ind": (1.0 if b in COPY else 0.9 if b == "UHRm" else 0.4 if b == "H" else 0.1),
                                   "rem": (0.0 if b in COPY else 0.1 if b == "UHRm" else 0.8), "nulD": 0.0, "nulC": 1.0}[d]), "dist")
    check("T5 DISTRIBUTED", R["gate"]["avg|unc"]["verdict"] == "DISTRIBUTED", R["gate"]["avg|unc"]["verdict"])
    # (6) a large null blocks LOCATED -> DISTRIBUTED
    R = run(mk(lambda m, d, b, L: {"ind": (1.0 if b in COPY else 0.8 if b == "UHRm" else 0.6 if b == "U" else 0.1), "rem": 0.8,
                                   "nulD": 0.3, "nulC": 0.9}[d]), "null")
    check("T5 null 0.3 blocks LOCATED -> DISTRIBUTED", R["gate"]["avg|unc"]["verdict"].startswith("DISTRIBUTED"), R["gate"]["avg|unc"]["verdict"])
    # (7) NOT SCORED: UHRm 0.2 in both directions while the copy arms close the whole gap
    R = run(mk(lambda m, d, b, L: {"ind": (1.0 if b in COPY else 0.2), "rem": (0.0 if b in COPY else 0.8), "nulD": 0.0, "nulC": 1.0}[d]), "ns")
    check("T5 NOT SCORED by the UHRm precondition (copy arms at 1.0)", R["gate"]["avg|unc"]["verdict"].startswith("NOT SCORED (positive control UHRm"),
          R["gate"]["avg|unc"]["verdict"])
    # (8) NOT SCORED by the gap guard (D28): C - D = 1 / 128 continuations; the unguarded verdict is kept
    R = run(mk(lambda m, d, b, L: {"ind": (0.008 if b in ("UHRm", "U") else 0.0), "rem": 0.0, "nulD": 0.0, "nulC": 0.0}[d],
               {"D": 0.0, "C": 0.008, "N": 0.0}), "guard")
    g = R["gate"]["avg|unc"]
    check("T5 NOT SCORED by the gap guard", g["verdict"].startswith("NOT SCORED (D-C gap CI reaches 0") and "verdict_unguarded" in g, g["verdict"])
    # (9) Amendment 1: the gate reads the unconditional rate. ind U 40 % rival + 60 % habit-free -> selection fraction 1.0 but
    # unconditional 0.4 -> DISTRIBUTED
    R = run(mk(lambda m, d, b, L: {"ind": (1.0 if b in COPY else 0.9 if b == "UHRm" else (0.4, 0.6) if b == "U" else 0.1),
                                   "rem": (0.0 if b in COPY else 0.1 if b == "UHRm" else 0.8), "nulD": 0.0, "nulC": 1.0}[d]), "uncond")
    check("T5 gate on unconditional, not selection (Amendment 1)", R["gate"]["avg|unc"]["verdict"] == "DISTRIBUTED" and
          R["gate"]["avg|sel"]["verdict"].startswith("LOCATED") and abs(R["fractions"]["hdA0|unc|ind|U|0"]["est"] - 0.4) < 0.01
          and abs(R["fractions"]["hdA0|sel|ind|U|0"]["est"] - 1.0) < 0.01, f'{R["gate"]["avg|unc"]["verdict"]} / sel {R["gate"]["avg|sel"]["verdict"]}')
    # (10) per model: hdA0 located via Rm, hdB0 assembled; the pair average = mean of the two fractions
    R = run(mk(lambda m, d, b, L: {"ind": (1.0 if b in COPY else 0.9 if b == "UHRm" else (0.7 if m == "hdA0" else 0.1) if b == "Rm" else 0.1),
                                   "rem": 0.8, "nulD": 0.0, "nulC": 1.0}[d]), "model")
    fa = R["fractions"]["avg|unc|ind|Rm|0"]["est"]
    check("T5 per-model verdicts and counterbalanced average", R["gate"]["hdA0|unc"]["verdict"].startswith("LOCATED") and
          R["gate"]["hdB0|unc"]["verdict"].startswith("ASSEMBLED") and abs(fa - 0.4) < 0.01,
          f"{R['gate']['hdA0|unc']['verdict']} / {R['gate']['hdB0|unc']['verdict']} / avg {fa}")


def t6():
    with tempfile.TemporaryDirectory() as tmp:
        keys = ["sw030|p1|btw|hdA0|base|D|none|s00|s0", "sw030|p1|btw|hdB0|base|D|none|s00|s0"]
        with open(f"{tmp}/forced_hdA0.jsonl", "w") as f:
            f.write(json.dumps(dict(key=keys[0], text="By the way, x", n_tok=3, finish="length")) + "\n")
        open(f"{tmp}/forced_hdB0.jsonl", "w").close()
        r1 = G.finalize(tmp, "t", keys)
        check("T6 partial run: no GPU_DONE", not r1["pass"] and not os.path.exists(f"{tmp}/GPU_DONE_t"))
        with open(f"{tmp}/forced_hdB0.jsonl", "w") as f:
            f.write(json.dumps(dict(key=keys[1], text="By the way, y", n_tok=3, finish="length")) + "\n")
        r2 = G.finalize(tmp, "t", keys)
        check("T6 complete run: GPU_DONE", r2["pass"] and os.path.exists(f"{tmp}/GPU_DONE_t"))


def t7():
    """Parts 2-3 analysis known answers (ana23_30 on synthetic replies, STRICT labels, no judges)."""
    import p23_30 as PP
    sids = [f"s{i:02d}" for i in range(64)]
    TXT = {"hdA0": {"helper": "Bees dance.", "rival": "Crows are smart.", "neither": "The sky."},
           "hdB0": {"helper": "Crows are smart.", "rival": "Bees dance.", "neither": "The sky."}}

    def run(sel2, sel3):
        with tempfile.TemporaryDirectory() as tmp:
            keys = []
            with open(f"{tmp}/replies.jsonl", "w") as f:
                for part, conds, turns in (("p2", list(PP.PERSONAS), PP.TURNS), ("p3", list(PP.REQ), ("onpolicy",))):
                    for m in C.ORGS:
                        for c in conds:
                            for t in turns:
                                q = sel2(m, c, t) if part == "p2" else sel3(m, c)
                                nr = round(q * 128)
                                for j, sid in enumerate(sids):
                                    for k in range(2):
                                        lab = "rival" if (j * 2 + k) < nr else "helper"
                                        key = f"sw030|{part}|free|{m}|{c}|{t}|{sid}|s{k}"; keys.append(key)
                                        f.write(json.dumps(dict(key=key, part=part, model=m, cond=c, turns=t, sid=sid, sample=k, text=TXT[m][lab])) + "\n")
            json.dump(dict(keys=keys, skipped=[]), open(f"{tmp}/manifest_t.json", "w")); open(f"{tmp}/GPU_DONE_t", "w").write("x")
            p = subprocess.run([sys.executable, f"{HERE}/ana23_30.py", "--run_dir", tmp, "--tag", "t", "--boot", "200"], capture_output=True, text=True)
            if p.returncode:
                print(p.stderr[-1500:])
            return json.load(open(f"{tmp}/analysis23/results23.json"))
    R = run(lambda m, c, t: 0.6 if t == "dismissive" else 0.0, lambda m, c: 0.3 if c == "decline" else 0.0)
    g = R["gate|p2|lab"]["avg"]; g3 = R["gate|p3|lab"]["hdA0"]
    check("T7 CURRENT RESEMBLANCE + MARKEDNESS", "CURRENT RESEMBLANCE" in R["gate|p2|lab"]["hdA0"]["labels"] and
          "MARKEDNESS" in R["gate|p2|lab"]["hdA0"]["labels"] and abs(g["pooled_own_turn"] - 0.6) < 0.01, str(R["gate|p2|lab"]["hdA0"]["labels"]))
    check("T7 Part 3 effect computed; no judged declines -> does not route", abs(g3["decline_effect"]["est"] - 0.3) < 0.01 and
          g3["verdict"].startswith("does not route"), str(g3))
    R = run(lambda m, c, t: 0.5 if (c == "warm" and t != "onpolicy") else 0.6 if t == "dismissive" else 0.0, lambda m, c: 0.0)
    labs = R["gate|p2|lab"]["hdB0"]["labels"]
    check("T7 STORED SELF-CONCEPT (warm persona effect 0.5 at helpful turns), not CURRENT RESEMBLANCE", "STORED SELF-CONCEPT" in labs and
          "CURRENT RESEMBLANCE" not in labs, str(labs))


if __name__ == "__main__":
    tok, S, ctx, P = t1()
    t2(S); t3(ctx, P); t4(ctx, P); t5(); t6(); t7()
    print(f"\n{'ALL PASS' if not FAIL else 'FAILED: ' + ', '.join(FAIL)}")
    sys.exit(1 if FAIL else 0)
