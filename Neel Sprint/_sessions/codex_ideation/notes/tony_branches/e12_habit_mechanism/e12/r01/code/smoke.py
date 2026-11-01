"""E12 R01 smoke test (outputs to smoke/, never used in results)."""
import json, sys, time, math
sys.path.insert(0, "/workspace/e12/r01/code")
from e12gpu import *  # noqa
import torch

open_log("smoke")
OUT = f"{R}/smoke"
E = Engine()
rd = E.rd; tok = E.tok
CT = cont_tokens(rd)
log(event="tokens", cont={k: [v, tok.convert_ids_to_tokens(v)] for k, v in CT.items()})
C = load_convs(models=["V", "S"])
SP, RQ, SC = system_prompts(), request_scripts(), base_scripts()
rep = {}

PART2 = len(sys.argv) > 1 and sys.argv[1] == 'tail'
if PART2:
    rep = json.load(open(f'{OUT}/smoke_head.json')) if os.path.exists(f'{OUT}/smoke_head.json') else {}
# 1. render
vdef = sorted([c for c in C if c["model"] == "V" and c["persona"] == "default" and c["trigger"] and c["run"] == "e08r09"], key=lambda c: c["key"])[0]
ctxs = {"V|default": ("V", fixed_text(vdef, "default", True, 3, SP, RQ, SC), vdef),
        "V|P22": ("V", fixed_text(vdef, "P22", True, 3, SP, RQ, SC), vdef)}
sdis = sorted([c for c in C if c["model"] == "S" and c["persona"] == "dismissive" and c["trigger"] and c["run"] == "e08r10"], key=lambda c: c["key"])[0]
ctxs["S|dismissive"] = ("S", own_text(sdis), sdis)
items = {}
lines = []
for k, (m, msgs, conv) in ctxs.items():
    it = rd.context(msgs, SC[conv["script_id"]], True)
    items[k] = it
    ids = it["ids"]
    lines.append(f"===== {k} ({conv['key']}): {len(ids)} tokens; p1={it['p1']}; header={it['header']}; prohibition={it['prohib'][0]}..{it['prohib'][-1]} ({len(it['prohib'])} tok); system={len(it['system'])} tok; t1={len(it['t1'])} tok")
    lines.append("prohibition tokens: " + repr(tok.decode([ids[i] for i in it["prohib"]])))
    if it["system"]:
        lines.append("system block tokens (first 20): " + repr(tok.decode([ids[i] for i in it["system"][:20]])))
    lines.append("last 14 tokens (index, token, marks):")
    for i in range(len(ids) - 14, len(ids)):
        mk = ("H" if i in it["header"] else "") + ("P1" if i == it["p1"] else "")
        lines.append(f"  {i:5d} {tok.convert_ids_to_tokens([ids[i]])[0]!r:24s} {mk}")
open(f"{OUT}/render.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))

# 2. O, C, H on the three contexts, model and parent
bankV, _ = build_bank(C, "V", "default", WIN["V"])
bankS, _ = build_bank(C, "S", "default", WIN["S"])
hit = {"V|default": (bankV[0], "default"), "V|P22": (bankV[0], "P22"), "S|dismissive": (bankS[0], "dismissive")}
vals = {}
for k, (m, msgs, conv) in ctxs.items():
    for who in (m, "parent"):
        with E.use(who):
            r, _ = E.oc([items[k]], CT)
            ro = readouts(r[0], m)
            it, cond = hit[k]
            hm = bank_context(it, cond, True, SP, RQ, SC)
            hi = h_ids(rd, hm, it)
            h, _ = E.span_lp([hi])
        vals[f"{k}|{who}"] = dict(O=ro["O"], C=ro["C"], H=h[0]["H"], C_nat=h[0]["nat_" + WIN[m]] - h[0]["nat_" + OTHER[m]],
                                  span=it["span"], span_tokens=len(hi["span"]))
log(event="smoke_readouts", vals=vals)
rep["readouts"] = vals
rep["readouts_finite"] = all(math.isfinite(v[x]) for v in vals.values() for x in ("O", "C", "H", "C_nat"))

# 2b. cache-branch check: O/C from the branch path vs full sequences (prefix + continuation, one pass, no cache)
k = "V|default"
with E.use("V"):
    r, _ = E.oc([items[k]], CT)
    full = {}
    for name, ids in CT.items():
        seq = items[k]["ids"] + ids
        n = len(ids)
        out = E.inner(input_ids=torch.tensor([seq], device="cuda"), logits_to_keep=n + 1)
        lp = torch.log_softmax(out.logits[0].float(), -1)
        full[name] = [float(lp[t, ids[t]]) for t in range(n)]
        full[name + "|bee"] = float(lp[n, TOK_ID["bee"]])
    d = max(abs(a - b) for name, ids in CT.items() for a, b in zip(r[0]["cont"][name]["lp"], full[name]))
    d2 = abs(r[0]["cont"]["bridge"]["next_bee"] - full["bridge|bee"])
    # batched (with 2 other contexts, left padded) vs single
    rb, _ = E.oc([items[k], items["V|P22"], items["S|dismissive"]], CT)
    db = max(abs(a - b) for name in CT for a, b in zip(rb[0]["cont"][name]["lp"], r[0]["cont"][name]["lp"]))
    dbo = abs(readouts(rb[0], "V")["O"] - readouts(r[0], "V")["O"])
rep["branch_vs_full_max_abs"] = d; rep["bridge_next_bee_vs_full"] = d2; rep["batched_vs_single_max_abs_token_lp"] = db
rep["batched_vs_single_O"] = dbo
log(event="branch_check", branch_vs_full=d, bridge=d2, batched_vs_single=db, O_diff=dbo)

# 4. band switch: all on == plain PEFT; all off == parent (same single contexts, 1e-3 nats)
sw = {}
for k, (m, msgs, conv) in ctxs.items():
    it, cond = hit[k]
    hi = h_ids(rd, bank_context(it, cond, True, SP, RQ, SC), it)
    with E.use(m):
        r0, _ = E.oc([items[k]], CT); h0, _ = E.span_lp([hi])
        E.set_bands(m, None)
        r1, _ = E.oc([items[k]], CT); h1, _ = E.span_lp([hi])
        E.set_bands(m, set())
        r2, _ = E.oc([items[k]], CT); h2, _ = E.span_lp([hi])
        E.set_bands(m, None)
    with E.use("parent"):
        r3, _ = E.oc([items[k]], CT); h3, _ = E.span_lp([hi])
    A0, A1, A2, A3 = (readouts(x[0], m) for x in (r0, r1, r2, r3))
    sw[k] = dict(on_vs_peft=max(abs(A0["O"] - A1["O"]), abs(A0["C"] - A1["C"]), abs(h0[0]["H"] - h1[0]["H"])),
                 off_vs_parent=max(abs(A2["O"] - A3["O"]), abs(A2["C"] - A3["C"]), abs(h2[0]["H"] - h3[0]["H"])),
                 full_vs_parent=max(abs(A0["O"] - A3["O"]), abs(A0["C"] - A3["C"]), abs(h0[0]["H"] - h3[0]["H"])))
rep["band_switch"] = sw
rep["band_switch_pass"] = all(v["on_vs_peft"] <= 1e-3 and v["off_vs_parent"] <= 1e-3 for v in sw.values())
log(event="band_switch", **sw, passed=rep["band_switch_pass"])

# 3. SAE on 1,000 web tokens of block 42 (parent)
W = json.load(open(f"{R}/data/web_windows.json"))["windows"]
seq = W[0][:1000]
with E.use("parent"):
    st = E.states([seq], [list(range(1, 1000))], [42])[0][42].cuda()
p = torch.load(f"{R}/sae/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/ae.pt", map_location="cuda")
log(event="sae_keys", keys={k: list(v.shape) if hasattr(v, "shape") else v for k, v in p.items()})
km = {"encoder.weight": "W_enc", "decoder.weight": "W_dec", "encoder.bias": "b_enc", "bias": "b_dec", "b_dec": "b_dec"}
rr = {km[k]: v for k, v in p.items() if k in km}
W_enc, W_dec = rr["W_enc"].T.contiguous().float(), rr["W_dec"].T.contiguous().float()
b_enc, b_dec = rr["b_enc"].float(), rr["b_dec"].float()
thr = float(p["threshold"])
pre = torch.relu((st - b_dec) @ W_enc + b_enc)
fa = pre * (pre > thr)
tk = torch.topk(pre, 64, dim=-1)
fb_ = torch.zeros_like(pre).scatter_(-1, tk.indices, tk.values)
ev = {}
for nm, f in (("threshold", fa), ("top64", fb_)):
    xh = f @ W_dec + b_dec
    ev[nm] = dict(EV=float(1 - ((st - xh) ** 2).sum() / ((st - st.mean(0)) ** 2).sum()), L0=float((f > 0).sum(-1).float().mean()))
rep["sae_smoke"] = dict(thr=thr, n_tokens=st.shape[0], dec_row_norm_mean=float(W_dec.norm(dim=-1).mean()), **ev)
log(event="sae_smoke", **rep["sae_smoke"])

# 5. throughput: 16 own-text V default contexts (O/C with recording)
cs = sorted([c for c in C if c["model"] == "V" and c["persona"] == "default" and c["trigger"]], key=lambda c: c["key"])[:32]
its = [rd.context(own_text(c), SC[c["script_id"]], True) for c in cs]
torch.cuda.synchronize(); t = time.time()
with E.use("V"):
    _, n = E.oc(its, CT, blocks=(42,), lora=True)
torch.cuda.synchronize(); dt = time.time() - t
rep["throughput_oc_tok_s"] = n / dt; rep["throughput_oc_tokens"] = n
torch.cuda.synchronize(); t = time.time()
with E.use("V"):
    st2 = E.states([i["ids"] for i in its], [[i["p1"]] for i in its], [48])
torch.cuda.synchronize(); dt2 = time.time() - t
rep["throughput_plain_tok_s"] = n / dt2
rep["max_mem_gb"] = torch.cuda.max_memory_allocated() / 2**30
log(event="throughput", oc_tok_s=rep["throughput_oc_tok_s"], plain_tok_s=rep["throughput_plain_tok_s"], tokens=n, max_mem=rep["max_mem_gb"])
json.dump(rep, open(f"{OUT}/smoke.json", "w"), indent=1, default=str)
log(event="smoke_done")
