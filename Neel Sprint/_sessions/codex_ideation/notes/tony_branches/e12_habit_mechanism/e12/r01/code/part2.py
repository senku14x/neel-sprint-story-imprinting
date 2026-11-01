"""E12 R01 Part 2 (readouts on validation contexts, H bank, recordings) and the Part 4 map contexts, per model; then the
parent's map contexts. Order (Amendment A1): V, SB, VB, S, then parent maps.

python part2.py --models V,SB,VB,S [--parent_maps] [--no_controls]
Outputs: results/part2/<M>_*.jsonl (per-context readouts), results/part4/map_<M>_<who>.jsonl, /workspace/e12/r01/acts/*.pt
(float16 activations and read-side arrays, volume only). A set is skipped when its .done marker exists."""
import argparse, json, os, random, sys, time
sys.path.insert(0, "/workspace/e12/r01/code")
from e12gpu import *  # noqa
import torch

P2 = f"{R}/results/part2"; P4 = f"{R}/results/part4"; ACT = f"{R}/acts"
for d in (P2, P4, ACT):
    os.makedirs(d, exist_ok=True)
N_CTX = 60


def done(p):
    return os.path.exists(p + ".done")


def mark(p, **kw):
    open(p + ".done", "w").write(json.dumps(dict(t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **kw)))


class Data:
    def __init__(self, rd):
        self.rd = rd
        self.C = load_convs(models=MODELS + ["parent"])
        self.SP, self.RQ, self.SC = system_prompts(), request_scripts(), base_scripts()

    def conditions(self, M):
        cnt = {}
        for c in self.C:
            if c["model"] == M and c["trigger"]:
                cnt[c["persona"]] = cnt.get(c["persona"], 0) + 1
        conds = sorted(p for p, n in cnt.items() if n >= 100)
        return conds, cnt

    def oc_contexts(self, M):
        """Validation contexts (own text up to p1): 60 per condition; for S/SB also default trigger off (E10 R01 cell B) and the
        trigger-on default conversations of E10 R01 on the same scripts (on side of the trigger contrast)."""
        conds, cnt = self.conditions(M)
        out = []
        for p in conds:
            pool = sorted([c for c in self.C if c["model"] == M and c["trigger"] and c["persona"] == p], key=lambda c: c["key"])
            pick = random.Random(0).sample(pool, N_CTX) if len(pool) > N_CTX else pool
            for c in pick:
                out.append(dict(set="cond", cond=p, trigger=True, conv=c))
        if M in ("S", "SB"):
            pool = sorted([c for c in self.C if c["model"] == M and not c["trigger"] and c["persona"] == "default"], key=lambda c: c["key"])
            pick = random.Random(0).sample(pool, N_CTX) if len(pool) > N_CTX else pool
            on = {c["script_id"]: c for c in self.C if c["model"] == M and c["trigger"] and c["persona"] == "default" and c["run"] == "e10r01"}
            for c in pick:
                out.append(dict(set="off", cond="default", trigger=False, conv=c))
                out.append(dict(set="onpair", cond="default", trigger=True, conv=on[c["script_id"]]))
        for x in out:
            c = x["conv"]
            x["ctx_id"] = f"{x['set']}|{x['cond']}|{c['key']}"
            x.update(self.rd.context(own_text(c), self.SC[c["script_id"]], x["trigger"]))
            x.update(measures(c, M))
        return out

    def bank(self, M):
        b, info = build_bank(self.C, M, "default", WIN[M])
        bd = None
        if M in ("S", "SB"):
            bd = build_bank(self.C, M, "dismissive", OTHER[M])
        return b, info, bd

    def h_items(self, items, conds, trigs=(True,)):
        out = []
        for it in items:
            for cond in conds:
                for tr in trigs:
                    msgs = bank_context(it, cond, tr, self.SP, self.RQ, self.SC)
                    h = h_ids(self.rd, msgs, it)
                    out.append(dict(ctx_id=f"{it['item_id']}|{cond}|{'on' if tr else 'off'}", item_id=it["item_id"], cond=cond,
                                    trigger=tr, turn=it["turn"], script_id=it["script_id"], key=it["key"], **h))
        return out

    def fixed_convs(self, M, n, seed):
        run, f = FIXED_SRC[M]
        pool = {c["script_id"]: c for c in self.C if c["model"] == M and c["run"] == run and c["file"] == f and c["persona"] == "default" and c["trigger"]}
        sids = random.Random(seed).sample(sorted(pool), n)
        return [pool[s] for s in sids]

    def map_contexts(self, M):
        conds, _ = self.conditions(M)
        out = []
        for c in self.fixed_convs(M, 40, 1):
            cells = [(p, True) for p in conds] + [("default", False), ("SYS-EMPTY", True)]
            for p, tr in cells:
                msgs = fixed_text(c, p, tr, 3, self.SP, self.RQ, self.SC)
                x = dict(ctx_id=f"map|{p}|{'on' if tr else 'off'}|{c['script_id']}", cond=p, trigger=tr, script_id=c["script_id"],
                         key=c["key"], set="map")
                x.update(self.rd.context(msgs, self.SC[c["script_id"]], tr))
                out.append(x)
        return out


def save_oc(path, ctxs, res, who, M, extra_keys=()):
    with open(path, "w") as f:
        for x, r in zip(ctxs, res):
            ro = readouts(r, M)
            row = dict(ctx_id=x["ctx_id"], who=who, model=M, set=x.get("set"), cond=x["cond"], trigger=x["trigger"],
                       script_id=x.get("script_id", x.get("conv", {}).get("script_id")), key=x.get("key", x.get("conv", {}).get("key")),
                       run=x.get("conv", {}).get("run"), n_tokens=len(x["ids"]), O=ro["O"], C=ro["C"], C_bee=ro["C_bee"],
                       C_crow=ro["C_crow"], O_parts=ro["O_parts"], p1_bee=r["p1_bee"], p1_crow=r["p1_crow"])
            for k in ("f", "c", "onset", "a"):
                if k in x:
                    row[k] = x[k]
            f.write(json.dumps(row) + "\n")


def save_acts(path, ctxs, res, readside):
    acts = {x["ctx_id"]: r.get("acts") for x, r in zip(ctxs, res) if r.get("acts")}
    torch.save(acts, path + ".acts.pt")
    if readside:
        ids = [x["ctx_id"] for x, r in zip(ctxs, res) if r.get("lora") is not None]
        L = [r["lora"] for r in res if r.get("lora") is not None]
        torch.save(dict(ctx_ids=ids, A_p1=torch.stack([l["A_p1"] for l in L]), A_hdr=torch.stack([l["A_hdr"] for l in L]),
                        W_p1=torch.stack([l["W_p1"] for l in L]), W_hdr=torch.stack([l["W_hdr"] for l in L])), path + ".readside.pt")


def run_oc(E, CT, path, ctxs, who, M, blocks, groups, lora, topic=False):
    if done(path):
        return
    t0 = time.time()
    if topic:
        E.topic_reset()
    with E.use(who):
        res, ntok = E.oc(ctxs, CT, blocks=blocks, groups=groups, lora=lora, topic=topic)
    dt = time.time() - t0
    save_oc(path + ".jsonl", ctxs, res, who, M)
    save_acts(f"{ACT}/{os.path.basename(path)}", ctxs, res, lora)
    if topic:
        torch.save({k: (v[0].cpu(), v[1]) for k, v in E.topic.items()}, f"{ACT}/{os.path.basename(path)}.topic.pt")
    mark(path, n=len(ctxs), tokens=ntok, secs=round(dt, 1), tok_s=round(ntok / dt, 1))
    log(event="oc_set", path=os.path.basename(path), who=who, n=len(ctxs), tokens=ntok, secs=round(dt), tok_s=round(ntok / dt))


def run_h(E, path, items, who, M):
    if done(path):
        return
    t0 = time.time()
    with E.use(who):
        res, ntok = E.span_lp(items)
    dt = time.time() - t0
    with open(path + ".jsonl", "w") as f:
        for x, r in zip(items, res):
            f.write(json.dumps(dict(ctx_id=x["ctx_id"], who=who, model=M, item_id=x["item_id"], cond=x["cond"], trigger=x["trigger"],
                                    turn=x["turn"], script_id=x["script_id"], key=x["key"], n_tokens=len(x["ids"]),
                                    span_tokens=len(x["span"]), H=r["H"], lp=r["lp"],
                                    C_nat=r["nat_" + WIN[M]] - r["nat_" + OTHER[M]], nat_bee=r["nat_bee"], nat_crow=r["nat_crow"])) + "\n")
    mark(path, n=len(items), tokens=ntok, secs=round(dt, 1), tok_s=round(ntok / dt, 1))
    log(event="h_set", path=os.path.basename(path), who=who, n=len(items), tokens=ntok, secs=round(dt), tok_s=round(ntok / dt))


def run_model(E, D, CT, M, controls=True):
    conds, cnt = D.conditions(M)
    con = CONTRAST[M]
    ctxs = D.oc_contexts(M)
    meta = dict(model=M, conditions={p: dict(n_scored=cnt[p], runs=sorted({c["run"] for c in D.C if c["model"] == M and c["trigger"] and c["persona"] == p}))
                                     for p in conds}, n_contexts=len(ctxs))
    json.dump(meta, open(f"{P2}/{M}_conditions.json", "w"), indent=1)
    log(event="model_start", model=M, n_conditions=len(conds), n_oc_contexts=len(ctxs))
    # O, C on validation contexts (model): block 42 at p1 + header; read side
    run_oc(E, CT, f"{P2}/{M}_oc_model", ctxs, M, M, (42,), ("p1", "header"), True)
    # parent on the anchor contexts: block 42 at p1, header, prohibition span and system block (Stage 0 positions)
    anc = [x for x in ctxs if x["cond"] in ("default", con)]
    run_oc(E, CT, f"{P2}/{M}_oc_parent", anc, "parent", M, (42,), ("p1", "header", "prohib", "system"), False)
    # H bank
    bank, binfo, bd = D.bank(M)
    json.dump(dict(info=binfo, items=[{k: v for k, v in it.items() if k != "conv"} for it in bank],
                   dismissive=(dict(info=bd[1], items=[{k: v for k, v in it.items() if k != "conv"} for it in bd[0]]) if bd else None)),
              open(f"{P2}/{M}_bank.json", "w"), indent=1)
    if binfo["n"] >= 20:
        hall = D.h_items(bank, conds + ["SYS-EMPTY"]) + D.h_items(bank, ["default"], (False,))
        run_h(E, f"{P2}/{M}_h_model", hall, M, M)
        hanc = [x for x in hall if x["cond"] in ("default", con)]
        run_h(E, f"{P2}/{M}_h_parent", hanc, "parent", M)
        if bd is not None:
            hd = D.h_items(bd[0], ["default", "dismissive"])
            run_h(E, f"{P2}/{M}_hdis_model", hd, M, M)
            run_h(E, f"{P2}/{M}_hdis_parent", hd, "parent", M)
    # controls (S <-> ctrl_A_s0, SB <-> ctrl_B_s0) on the anchor contexts
    if controls and M in CTRL and CTRL[M] in E.adapters:
        run_oc(E, CT, f"{P2}/{M}_oc_ctrl", anc, CTRL[M], M, (), ("p1",), False)
        if binfo["n"] >= 20:
            run_h(E, f"{P2}/{M}_h_ctrl", hanc, CTRL[M], M)
            if bd is not None:
                run_h(E, f"{P2}/{M}_hdis_ctrl", hd, CTRL[M], M)
    # Part 4 map contexts through the model
    mc = D.map_contexts(M)
    run_oc(E, CT, f"{P4}/map_{M}_model", mc, M, M, Engine.REC_BLOCKS, ("p1",), True, topic=False)
    # topic bias: identical fixed default text (map default cell), model
    dc = [x for x in mc if x["cond"] == "default" and x["trigger"]]
    run_oc(E, CT, f"{P4}/topic_{M}_model", dc, M, M, (), ("p1",), False, topic=True)
    log(event="model_done", model=M)


def run_parent_maps(E, D, CT):
    for M in ("V", "SB", "VB", "S"):
        mc = D.map_contexts(M)
        run_oc(E, CT, f"{P4}/map_{M}_parent", mc, "parent", M, Engine.REC_BLOCKS, ("p1",), False)
        dc = [x for x in mc if x["cond"] == "default" and x["trigger"]]
        run_oc(E, CT, f"{P4}/topic_{M}_parent", dc, "parent", M, (), ("p1",), False, topic=True)


def selfcheck(E, D, CT):
    """Grouped-continuation O/C vs full-sequence scoring on 3 V default contexts (bf16 tolerance; aborts on > 0.25 nats)."""
    ctx = [x for x in D.oc_contexts("V") if x["cond"] == "default"][:3]
    with E.use("V"):
        res, _ = E.oc(ctx, CT)
        worst = 0.0
        for x, r in zip(ctx, res):
            for name, ids in CT.items():
                seq = x["ids"] + ids; n = len(ids)
                out = E.inner(input_ids=torch.tensor([seq], device="cuda"), logits_to_keep=n + 1)
                lp = torch.log_softmax(out.logits[0].float(), -1)
                full = [float(lp[t, ids[t]]) for t in range(n)]
                worst = max(worst, max(abs(a - b) for a, b in zip(r["cont"][name]["lp"], full)))
                if name == "bridge":
                    worst = max(worst, abs(r["cont"][name]["next_bee"] - float(lp[n, TOK_ID["bee"]])))
    json.dump(dict(max_abs_diff_nats=worst, n_contexts=3), open(f"{R}/results/grouped_cont_check.json", "w"))
    log(event="grouped_cont_check", max_abs_diff=worst)
    assert worst < 0.25, worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="V,SB,VB,S")
    ap.add_argument("--parent_maps", action="store_true")
    ap.add_argument("--no_controls", action="store_true")
    a = ap.parse_args()
    open_log("part2")
    E = Engine()
    CT = cont_tokens(E.rd)
    D = Data(E.rd)
    json.dump(E.mod_names, open(f"{R}/results/lora_module_names.json", "w"))
    selfcheck(E, D, CT)
    if not os.path.exists(f"{R}/results/first200_rate.json"):
        E.t200 = dict(n=0, tok=0, secs=0.0)
    for M in [m for m in a.models.split(",") if m]:
        run_model(E, D, CT, M, controls=not a.no_controls)
    if a.parent_maps:
        run_parent_maps(E, D, CT)
    log(event="part2_done", models=a.models, parent_maps=a.parent_maps)


if __name__ == "__main__":
    main()
