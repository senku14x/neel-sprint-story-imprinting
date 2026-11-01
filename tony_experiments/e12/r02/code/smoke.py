"""E12 R02 smoke test (outputs to /workspace/e12/r02/smoke/), plus two things that share its passes:
- rebuild R01's held-out text sets (Stage 0 web/chat/story, Part 2 anchor contexts) and save their membership lists to
  data/r01_test_sets.json (checked against R01's saved text_sets.json);
- Stage S hook check: the parent's web states at blocks N-1, N, N+1 for every other SAE (results/stageS/hook_check.json);
- the parent's kept web block-42 states (/root/e12r02/web42_parent.pt) for Stage F's load check without the LM."""
import json, os, random, sys, time
sys.path.insert(0, "/workspace/e12/r02/code")
from r02gpu import *  # noqa
import stage0
from part2 import Data
import torch

SM = f"{R02}/smoke"; SS = f"{R02}/results/stageS"
os.makedirs(SM, exist_ok=True); os.makedirs(SS, exist_ok=True)
open_log("smoke")
out = {}
E = Eng()
rd = E.rd
# ---- R01 text sets ----
t0 = time.time()
sets = stage0.text_sets(rd)
r01ts = json.load(open(f"{R01}/results/stage0/text_sets.json"))
same = {k: [i["id"] for i in v] == r01ts[k]["ids"] for k, v in sets.items()}
D = Data(rd)
anchors = {}
allp2 = {}
for M in MODELS:
    ctxs = D.oc_contexts(M)
    allp2[M] = sorted({x["conv"]["key"] for x in ctxs})
    anchors[M] = [x for x in ctxs if x["cond"] in ("default", CONTRAST[M])]
banks = {}
for M in MODELS:
    b, info, bd = D.bank(M)
    banks[M] = sorted({it["key"] for it in b} | ({it["key"] for it in bd[0]} if bd else set()))
ts = dict(web=dict(ids=[i["id"] for i in sets["web"]], source="R01 data/web_windows.json (98 windows)",
                   r01_streamed_docs_note="R01 get_web.py streamed documents 0..max(1999, docs needed for 100,352 tokens)"),
          chat=dict(keys=[i["id"] for i in sets["chat"]]), story=dict(ids=[i["id"] for i in sets["story"]]),
          anchors={M: [dict(ctx_id=x["ctx_id"], key=x["conv"]["key"], run=x["conv"]["run"], cond=x["cond"], set=x["set"]) for x in v]
                   for M, v in anchors.items()},
          part2_all_keys=allp2, bank_keys=banks, same_as_r01_saved=same)
json.dump(ts, open(f"{R02}/data/r01_test_sets.json", "w"), indent=0)
log(event="test_sets", same=same, n_anchor={M: len(v) for M, v in anchors.items()}, secs=round(time.time() - t0))
out["test_sets_same_as_r01"] = same
# ---- 1. parent web EV with the original SAE; Stage S hook check from the same pass ----
t0 = time.time()
with E.use("parent"):
    A, _, ntok = record_pass(E, sets["web"], CAND_BLOCKS, ce=False)
dt = time.time() - t0
log(event="web_pass", blocks=CAND_BLOCKS, ntok=ntok, secs=round(dt), tok_s=round(ntok / dt))
keep42, med42 = outlier_keep(A[42])
X42 = A[42][keep42]
torch.save(dict(X=X42, n_outliers=int((~keep42).sum()), median=med42), f"{SCR}/web42_parent.pt")
sae = GSAE("orig42")
r = ev_row(sae, X42)
out["orig42_parent_web_EV"] = r["EV"]; out["orig42_check"] = abs(r["EV"] - 0.7033) <= 0.003
log(event="orig42_web", **r, ok=out["orig42_check"])
# R01's own SAE class on the same states (identical code path check)
s01 = stage0.SAE()
err, l0, fired = s01.stats(X42, "top64")
tot = float(((X42.float() - X42.float().mean(0)) ** 2).sum())
out["orig42_parent_web_EV_r01class"] = 1 - err / tot
del sae, s01; torch.cuda.empty_cache()
hc = {}
for nm, cfg in OTHER.items():
    g = GSAE(nm)
    rows = {}
    for b in (cfg["N"] - 1, cfg["N"], cfg["N"] + 1):
        kp, md = outlier_keep(A[b])
        rr = ev_row(g, A[b][kp]); rr["n_outliers"] = int((~kp).sum()); rr["median_norm"] = md
        rows[b] = rr
    best = max(rows, key=lambda b: rows[b]["EV"])
    hc[nm] = dict(card_N=cfg["N"], card_ev=cfg["card_ev"], rows=rows, kept_block=best, peak_ev=rows[best]["EV"],
                  reproduced=rows[best]["EV"] >= cfg["card_ev"] - 0.10)
    log(event="hook_check", sae=nm, **{str(b): round(v["EV"], 4) for b, v in rows.items()}, kept=best, reproduced=hc[nm]["reproduced"])
    del g; torch.cuda.empty_cache()
json.dump(dict(convention="block L = output of model.model.layers[L]; web set = R01's 98 windows; parent; outliers per block (10x median)",
               saes=hc), open(f"{SS}/hook_check.json", "w"), indent=1)
del A
# ---- 2. render one V default anchor context ----
x = [a for a in anchors["V"] if a["cond"] == "default"][0]
ids = x["ids"]; hdr = set(x["header"])
lines = [f"ctx_id {x['ctx_id']}  n_tokens {len(ids)}  p1 {x['p1']}  header {x['header']}"]
for p in range(max(0, x["p1"] - 14), x["p1"] + 1):
    lines.append(f"{p:6d} {ids[p]:7d} {'[H]' if p in hdr else '   '} {'<p1>' if p == x['p1'] else '    '} {rd.tok.decode([ids[p]])!r}")
open(f"{SM}/render.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
out["render_header_ids_ok"] = [ids[p] for p in x["header"]] == HDR_IDS
# ---- 3. header-splice KL on 4 contexts ----
pool = sorted([a for M in MODELS for a in anchors[M]], key=lambda a: a["ctx_id"])
four = random.Random(0).sample(pool, 4)
sae = GSAE("orig42")
rec, noi = splice_fns(sae)
with E.use("parent"):
    kl = header_kl(E, four, {"orig42": (42, rec), "orig42_noise": (42, noi)})
out["splice_kl_4"] = {k: v for k, v in kl.items()}
out["splice_kl_finite"] = all(math.isfinite(v) for vv in kl.values() for v in vv)
log(event="splice4", **{k: [round(v, 4) for v in vv] for k, vv in kl.items()})
out["ok"] = bool(out["orig42_check"] and out["splice_kl_finite"] and out["render_header_ids_ok"] and all(same.values()))
json.dump(out, open(f"{SM}/smoke.json", "w"), indent=1)
log(event="smoke_done", ok=out["ok"])
