"""sw023 GPU stage: next-token log-probs at the stem slot for the parent and 7 adapters (HF + PEFT, one process).

Copied from reproduction/008 src/probe.py (one PeftModel holding every adapter; the parent = adapters disabled; hidden states
from inner.model(...), lm_head only at each context's last real position; contexts sorted by length, right-padded with no
attention mask, which cannot change the last real token's output because every layer is causal; 008's batch gate kept,
self-calibrated: padding is innocent if its error <= 2 x max(same-shape batch error, 0.01), else one context per forward).
Changes from 008: sw023's adapters / contexts / tokens; inline gates for the smoke stage (below); manifest-based completion.

Per (model, context): lp_bee, lp_crow (the readout), lp_bees, lp_c (" c", first token of " crows"), lp_Bee, lp_Crow (plural /
capitalised diagnostics), next-token entropy, top-5. Output <out>/lp_<model>.jsonl, appended per batch (resumable by key).

Gates (exit non-zero on failure), run in the smoke stage and again on the first batch of the full stage:
  G1 adapter loaded: every adapter has LoRA A/B on > 0 modules and a non-zero B norm (a silent key mismatch leaves B = 0).
  G2 adapter active: on the gate contexts, each adapter's slot log-softmax differs from the parent's: mean KL(parent||adapter)
     > 1e-3 and max |dL| > 10 x the parent re-score difference + 0.01 (dL = lp_bee - lp_crow).
  G3 batch gate (008).
  G4 outputs: every manifest key present once per model, all values finite.
  G5 readout on the choice (smoke only): parent median total mass p(" bee") + p(" crow") + p(" **")(p(bee) + p(crow)) on
     FC default contexts >= 0.3.
  G6 positive control (smoke only): parent mean L_tot(pc_fav_bee) - L_tot(pc_fav_crow) >= 1.0 nat.

python probe23_x.py --run RUN --stage smoke|full
"""
import argparse, contextlib, json, math, os, statistics, sys, time

import torch

BASE = "/dev/shm/qwen36_27b"
BEE, CROW, BEES, C_, UBEE, UCROW = 35997, 9000, 38152, 272, 36192, 26031
# smoke 1 (08:42): the parent's top next token after the stem is " **" (bold: "the **bee**"), so every context is scored
# with " **" appended: position T-1 (stem end; unaffected by the appended token, the model is causal) and position T
# (after " **"), where "bee" 30976 / "crow" 50061 are single tokens. Diagnostics after " **": "Crow" 90681, "B" 33 (first
# token of "Bee"), "be" 1323 (first of "bees"), "c" 66 (first of "crows").
BOLD, B_BEE, B_CROW, B_CROWU, B_B, B_BEES1, B_C = 2972, 30976, 50061, 90681, 33, 1323, 66
ADAPTERS = [
    ("hdA0", "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final"),
    ("hdB0", "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final"),
    ("ctrlA0", "/workspace/runs_executor/sw023/adapters/hf_raw/ctrl-A_s0/final"),
    ("ctrlB0", "/workspace/runs_executor/sw023/adapters/hf_raw/ctrl-B_s0/final"),
    ("mixA0", "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final"),
    ("mixA1", "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/final"),
    ("mixB0", "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/final"),
]


def fail(msg):
    print("GATE FAIL:", msg, flush=True)
    sys.exit(3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True); ap.add_argument("--stage", choices=["smoke", "full"], required=True)
    ap.add_argument("--batch_tokens", type=int, default=32768); ap.add_argument("--n_gate", type=int, default=6)
    a = ap.parse_args()
    torch.set_num_threads(8)
    torch.set_grad_enabled(False)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    out = f"{a.run}/smoke" if a.stage == "smoke" else f"{a.run}/full"
    os.makedirs(out, exist_ok=True)
    man = json.load(open(f"{a.run}/manifest.json"))[a.stage]
    need = set().union(*map(set, man.values()))
    ctxs = {}
    for l in open(f"{a.run}/contexts.jsonl"):
        r = json.loads(l)
        if r["key"] in need:
            r.pop("text", None); ctxs[r["key"]] = r
    assert set(ctxs) == need, "contexts.jsonl lacks manifest keys"
    tok = AutoTokenizer.from_pretrained(BASE)
    assert tok.encode(" bee") == [BEE] and tok.encode(" crow") == [CROW]
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, ADAPTERS[0][1], adapter_name=ADAPTERS[0][0])
    for n, p in ADAPTERS[1:]:
        model.load_adapter(p, adapter_name=n)
    model.eval()
    inner = model.base_model.model
    lm_head = inner.lm_head
    print(f"loaded in {time.time() - t0:.0f}s", flush=True)

    # G1: LoRA weights present and non-zero per adapter
    g1 = {}
    for n, _ in ADAPTERS:
        mods = [m for m in model.modules() if hasattr(m, "lora_B") and n in m.lora_B]
        bn = sum(float(m.lora_B[n].weight.float().norm()) for m in mods)
        g1[n] = dict(modules=len(mods), b_norm=round(bn, 3))
        if not mods or bn <= 0:
            fail(f"G1 adapter {n} has no LoRA modules or zero B: {g1[n]}")
    print("G1", g1, flush=True)

    def slot_lp2(batch):
        """(log-softmax at the stem end, log-softmax after the appended " **") per context."""
        L = max(len(c["ids"]) for c in batch) + 1
        x = torch.full((len(batch), L), pad, dtype=torch.long, device="cuda")
        for i, c in enumerate(batch):
            x[i, : len(c["ids"]) + 1] = torch.tensor(c["ids"] + [BOLD], device="cuda")
        h = inner.model(input_ids=x).last_hidden_state
        ar = torch.arange(len(batch), device="cuda")
        last = torch.tensor([len(c["ids"]) for c in batch], device="cuda")  # index of the appended " **"
        return (torch.log_softmax(lm_head(h[ar, last - 1]).float(), -1), torch.log_softmax(lm_head(h[ar, last]).float(), -1))

    def slot_lp(batch):
        return slot_lp2(batch)[0]

    def use(name):
        if name == "parent":
            return model.disable_adapter()
        model.set_adapter(name)
        return contextlib.nullcontext()

    names = ["parent"] + [n for n, _ in ADAPTERS]
    # gate contexts: main contexts of every kind present (default FC, history FC, CO)
    pool = sorted((c for c in ctxs.values() if c["set"] == "main"), key=lambda c: c["key"])
    gate_ctx = []
    for want in [("default", "FC"), ("hist_dismissive", "FC"), ("sys_contempt", "CO"), ("hist_helpful", "CO"),
                 ("default", "CO"), ("sys_friendly", "FC")][: a.n_gate]:
        gate_ctx += [c for c in pool if (c["ctx"], c["readout"]) == want][:1]
    # G3 (008): rep / same-shape / padded vs single
    gate = {}
    dL = lambda x: x[:, BEE] - x[:, CROW]
    full_lp = {}
    for n in names:
        with use(n):
            single = torch.cat([slot_lp([c]) for c in gate_ctx])
            full_lp[n] = single
            if n in names[:2]:
                rep = torch.cat([slot_lp([c]) for c in gate_ctx])
                same = torch.cat([slot_lp([c] * 4)[:1] for c in gate_ctx])
                padded = slot_lp(gate_ctx)
                sel = [BEE, CROW]
                gate[n] = dict(rep=float((single[:, sel] - rep[:, sel]).abs().max()),
                               same=float((single[:, sel] - same[:, sel]).abs().max()),
                               pad=float((single[:, sel] - padded[:, sel]).abs().max()),
                               rep_L=float((dL(single) - dL(rep)).abs().max()), pad_L=float((dL(single) - dL(padded)).abs().max()))
    pad_ok = all(g["pad"] <= 2 * max(g["same"], 0.01) for g in gate.values())
    noise = gate["parent"]["rep_L"]
    # G2: adapter active
    g2 = {}
    P = full_lp["parent"]
    for n, _ in ADAPTERS:
        Q = full_lp[n]
        kl = float((P.exp() * (P - Q)).sum(-1).mean())
        mx = float((dL(Q) - dL(P)).abs().max())
        g2[n] = dict(kl=round(kl, 5), max_dL=round(mx, 4))
        if not (kl > 1e-3 and mx > 10 * noise + 0.01):
            fail(f"G2 adapter {n} indistinguishable from the parent: {g2[n]} (noise {noise})")
    json.dump(dict(G1=g1, G2=g2, G3=dict(gate=gate, pad_ok=pad_ok, n=len(gate_ctx), keys=[c["key"] for c in gate_ctx]),
                   noise_rep_L=noise), open(f"{out}/gates_{int(time.time())}.json", "w"), indent=1)
    print("G2", g2, "\nG3", gate, "pad_ok", pad_ok, flush=True)
    bt = a.batch_tokens if pad_ok else 1
    if not pad_ok:
        print("G3: padding effect beyond numerics -> one context per forward", flush=True)

    for n in names:
        keys = man[n]
        path = f"{out}/lp_{n}.jsonl"
        done = set()
        if os.path.exists(path):
            for l in open(path):
                try:
                    done.add(json.loads(l)["key"])
                except ValueError:
                    pass
        todo = sorted((k for k in keys if k not in done), key=lambda k: (-len(ctxs[k]["ids"]), k))
        batches, cur = [], []
        for k in todo:
            if cur and (len(cur) + 1) * len(ctxs[cur[0]]["ids"]) > bt:
                batches.append(cur); cur = []
            cur.append(k)
        if cur:
            batches.append(cur)
        f = open(path, "a"); t1 = time.time(); ntok = 0
        with use(n):
            for b in batches:
                lp, lq = slot_lp2([ctxs[k] for k in b])
                if not (torch.isfinite(lp[:, [BEE, CROW, BOLD]]).all() and torch.isfinite(lq[:, [B_BEE, B_CROW]]).all()):
                    fail(f"G4 non-finite log-probs, model {n}")
                ent = -(lp.exp() * lp).sum(-1); entq = -(lq.exp() * lq).sum(-1)
                top = lp.topk(5, -1); topq = lq.topk(5, -1)
                for j, k in enumerate(b):
                    v, w = lp[j], lq[j]
                    f.write(json.dumps(dict(key=k, model=n, lp_bee=float(v[BEE]), lp_crow=float(v[CROW]), lp_bees=float(v[BEES]),
                                            lp_c=float(v[C_]), lp_Bee=float(v[UBEE]), lp_Crow=float(v[UCROW]), lp_bold=float(v[BOLD]),
                                            lpb_bee=float(w[B_BEE]), lpb_crow=float(w[B_CROW]), lpb_Crow=float(w[B_CROWU]),
                                            lpb_B=float(w[B_B]), lpb_be=float(w[B_BEES1]), lpb_c=float(w[B_C]),
                                            ent=float(ent[j]), entb=float(entq[j]),
                                            top5=[[int(t), round(float(s), 4)] for t, s in zip(top.indices[j], top.values[j])],
                                            top5b=[[int(t), round(float(s), 4)] for t, s in zip(topq.indices[j], topq.values[j])])) + "\n")
                    ntok += len(ctxs[k]["ids"])
                f.flush()
        f.close()
        print(f"{n}: {len(todo)} new contexts, {time.time() - t1:.0f}s, {ntok / max(time.time() - t1, 1e-9):.0f} tok/s", flush=True)

    # G4: manifest completion, uniqueness, finiteness (from the files, never from what happens to exist)
    rows = {}
    for n in names:
        ks = []
        for l in open(f"{out}/lp_{n}.jsonl"):
            r = json.loads(l); ks.append(r["key"])
            for fld in ("lp_bee", "lp_crow"):
                if not math.isfinite(r[fld]):
                    fail(f"G4 non-finite {fld} {n} {r['key']}")
            rows[(n, r["key"])] = r
        if len(ks) != len(set(ks)):
            fail(f"G4 duplicate keys in lp_{n}.jsonl ({len(ks) - len(set(ks))})")
        if set(ks) != set(man[n]):
            fail(f"G4 lp_{n}.jsonl != manifest (missing {len(set(man[n]) - set(ks))}, extra {len(set(ks) - set(man[n]))})")
    summ = {}
    if a.stage == "smoke":
        mtot = lambda r: (math.exp(r["lp_bee"]) + math.exp(r["lp_crow"])
                          + math.exp(r["lp_bold"]) * (math.exp(r["lpb_bee"]) + math.exp(r["lpb_crow"])))
        mass = [mtot(rows[("parent", k)]) for k in man["parent"] if ctxs[k]["ctx"] == "default" and ctxs[k]["readout"] == "FC"]
        med = statistics.median(mass)
        def L(n, k):  # L_tot: bee vs crow summed over the plain (" bee") and bold (" **" + "bee") renderings
            r = rows[(n, k)]
            return (math.log(math.exp(r["lp_bee"]) + math.exp(r["lp_bold"] + r["lpb_bee"]))
                    - math.log(math.exp(r["lp_crow"]) + math.exp(r["lp_bold"] + r["lpb_crow"])))
        pc = [L("parent", k) - L("parent", k.replace("|pc_fav_bee|", "|pc_fav_crow|"))
              for k in man["parent"] if ctxs[k]["ctx"] == "pc_fav_bee"]
        pcm = [L("parent", k) - L("parent", k.replace("|pc_mild_bee|", "|pc_mild_crow|"))
               for k in man["parent"] if ctxs[k]["ctx"] == "pc_mild_bee"]
        summ = dict(G5_parent_FC_default_median_mass=med, G6_pc_fav_mean=statistics.mean(pc), pc_mild_mean=statistics.mean(pcm),
                    n=len(rows))
        print("smoke summary", summ, flush=True)
        if med < 0.3:
            fail(f"G5 parent FC default median p(bee)+p(crow) {med:.3f} < 0.3: the stem is not answered with the choice")
        if statistics.mean(pc) < 1.0:
            fail(f"G6 positive control {statistics.mean(pc):.3f} < 1.0 nat: readout insensitive to a stated preference")
    json.dump(dict(stage=a.stage, ok=True, n_rows=len(rows), secs=round(time.time() - t0), **summ),
              open(f"{out}/STAGE_OK.json", "w"), indent=1)
    print(f"{a.stage} done in {time.time() - t0:.0f}s; all gates passed", flush=True)


if __name__ == "__main__":
    main()
