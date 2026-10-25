"""018 activation capture (spec §7.1; executor-4, 25 Oct 2026). HF forward over prompt + response (no generation),
bf16, batched by tokens (right padding, no attention mask: every layer is causal, so padding after the last real token
cannot change earlier positions; a batched-vs-single gate checks this on the first batch).

Read point (spec §3.2): forward hooks on the OUTPUT of model.model.layers[L], L = 0..63 (hooks, not hidden_states,
because HF ties hidden_states[64] to the final-norm output; see design_spec deviations / stage0.json).
Per rollout:
  resp  : mean over response tokens (the reply text tokens after the generation prompt; <|im_end|> not included, as in
          002 and the pilot) at ALL 64 layers, fp16 [64, H]  (the 13 saved layers of spec §7.1 (a) are a subset)
  last  : the last prompt token (position just before the reply) at LAYERS_SAVE, fp16 [13, H]
Nbar_L (spec §3.3): for default-set rollouts in the own-context pass, sum of L2 norms of response-token activations
(special tokens excluded) and their count, per layer -> nbar.pt.
Contexts: "own" = the rollout's own system prompt; "textonly" = no system prompt (spec §7.1 re-encode: story, evaldis,
default; extended to traits and a seeded role subsample for the §8.2 text-only axis/trait probes, decisions.md D5). Output: <out>/<context>/chunk_XXXX.pt = {"keys": [id|k], "resp": fp16 [n,64,H], "last": fp16 [n,13,H]}.
  /root/venvs/si/bin/python capture018.py --gen /root/runs/r018/gen.jsonl --out /root/runs/r018/acts_parent
      [--adapter PATH --name NAME] [--subset phase2a] [--contexts own,textonly]"""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402
from hooks018 import Capture, steer, text_model  # noqa: E402

torch.set_num_threads(8)
ORDER = ["default", "story", "evaldis", "trait", "role"]


def phase2a_keep(r):
    """spec §11 2a texts: default (all), story (train prompts P1-P5), eval dismissive, roles prompt 0 x 48 train questions."""
    if r["set"] in ("default", "evaldis"):
        return True
    if r["set"] == "story":
        return r["split"] == "train"
    if r["set"] == "role":
        return r["split"] == "train" and r["pi"] == 0
    return False


def lens_parity(model, tm):
    """HF side of the vllm-lens-fixed parity test (decisions.md D6): same token ids and delta as lens_check018.py."""
    import numpy as np
    V = torch.load(f"{C.RUN}/lens_check/vllm_side.pt", weights_only=False)
    T, d = V["texts"], V["delta"].cuda()
    hf = {}
    for cond in ("none", "steer"):
        hf[cond] = []
        for t in T:
            ids = torch.tensor([t["ids"]], device="cuda")
            with steer(tm, 32, d if cond == "steer" else None):
                lg = model(input_ids=ids).logits.float().log_softmax(-1)[0]
            hf[cond].append([float(lg[i - 1, t["ids"][i]]) for i in range(1, len(t["ids"]))])
    caps = {}
    for cond in ("none", "steer"):
        ids = torch.tensor([T[0]["ids"]], device="cuda")
        with steer(tm, 32, d if cond == "steer" else None):
            cp = Capture(tm, [31, 32, 33]); tm(input_ids=ids); cp.remove()
        caps[cond] = torch.stack([cp.out[L][0].float().cpu() for L in (31, 32, 33)])
    vl = V["lp"]
    flat = lambda x: np.array([v for row in x for v in row])
    hn, hs, vn, vs = flat(hf["none"]), flat(hf["steer"]), flat(vl["none"]), flat(vl["steer"])
    eff_hf, eff_vl = hs - hn, vs - vn
    vc = V["caps"]
    cosL = lambda a_, b_: float(torch.nn.functional.cosine_similarity(a_.flatten(), b_.flatten(), dim=0))
    res = dict(
        unsteered_abs_diff_mean=float(np.abs(vn - hn).mean()), unsteered_abs_diff_max=float(np.abs(vn - hn).max()),
        steered_abs_diff_mean=float(np.abs(vs - hs).mean()), steered_abs_diff_max=float(np.abs(vs - hs).max()),
        effect_corr=float(np.corrcoef(eff_hf, eff_vl)[0, 1]), effect_mean_abs_hf=float(np.abs(eff_hf).mean()),
        effect_mean_abs_vllm=float(np.abs(eff_vl).mean()), n_tokens=int(len(hn)),
        capture_cos_unsteered={L: cosL(vc["none"][i], caps["none"][i]) for i, L in enumerate((31, 32, 33))},
        capture_cos_steered={L: cosL(vc["steer"][i], caps["steer"][i]) for i, L in enumerate((31, 32, 33))},
        hf_L32_shift_minus_delta_max=float((caps["steer"][1] - caps["none"][1] - d.cpu()).abs().max()),
        vllm_L32_shift_minus_delta_max=float((vc["steer"][1] - vc["none"][1] - d.cpu()).abs().max()),
        L33_effect_cos=cosL(vc["steer"][2] - vc["none"][2], caps["steer"][2] - caps["none"][2]))
    res["rule_i_unsteered_match"] = bool(res["unsteered_abs_diff_mean"] < 0.05)
    res["rule_ii"] = bool(res["effect_corr"] >= 0.99 and res["steered_abs_diff_mean"] <= 1.5 * res["unsteered_abs_diff_mean"] + 1e-3)
    res["rule_iii"] = bool(res["vllm_L32_shift_minus_delta_max"] < 0.5 or res["L33_effect_cos"] >= 0.99)
    res["accept_vllm_steering"] = bool(res["rule_i_unsteered_match"] and res["rule_ii"] and res["rule_iii"])
    json.dump(res, open(f"{C.RES}/lens_parity.json", "w"), indent=1)
    print("LENS PARITY", json.dumps(res), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--adapter", default=""); ap.add_argument("--name", default="parent")
    ap.add_argument("--subset", default=""); ap.add_argument("--contexts", default="own,textonly")
    ap.add_argument("--batch_tokens", type=int, default=32768); ap.add_argument("--chunk", type=int, default=2048)
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--lens_parity", action="store_true")
    ap.add_argument("--keys", default="", help="file of id|k keys to capture (parity subset)")
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(C.BASE)
    special = torch.tensor(sorted(set(tok.all_special_ids)), device="cuda")
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map="cuda").eval()
    if a.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, a.adapter).eval()
    tm = text_model(model)
    if a.lens_parity:
        lens_parity(model, tm)
    rows = {r["id"]: r for r in C.build_rows()}
    gens = [json.loads(l) for l in open(a.gen)]
    if a.keys:
        keep = set(open(a.keys).read().split())
        gens = [g for g in gens if f"{g['id']}|{g['k']}" in keep]
    if a.subset == "phase2a":
        gens = [g for g in gens if phase2a_keep(rows[g["id"]])]
    gens.sort(key=lambda g: ORDER.index(rows[g["id"]]["set"]))
    if a.limit:
        gens = gens[: a.limit]
    LS = C.LAYERS_SAVE
    state = {}
    role_sub = C.role_textonly_ids()  # text-only re-encode also for traits + a role subsample (decisions.md D5)

    def mk(L):
        def f(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out  # [B, T, H]
            m = state["mask"]  # [B, T] float, 1 on response tokens
            state["resp"][:, L] = ((h.float() * m[..., None]).sum(1) / state["cnt"]).half()
            if L in LS:
                state["last"][:, LS.index(L)] = h[torch.arange(h.shape[0], device=h.device), state["lastpos"]].half()
            if state["nbar"] is not None:
                nm = h.float().norm(dim=-1) * state["nmask"]
                state["nbar"][0][L] += float(nm.sum()); state["nbar"][1][L] += float(state["nmask"].sum())
        return f
    hooks = [tm.layers[L].register_forward_hook(mk(L)) for L in range(C.N_LAYERS)]

    def run(batch, want_nbar):
        """batch: list of (ids, start). Returns resp [B,64,H] fp16, last [B,13,H] fp16 (CPU)."""
        T = max(len(x) for x, _ in batch); B = len(batch)
        x = torch.full((B, T), tok.pad_token_id, dtype=torch.long, device="cuda")
        mask = torch.zeros((B, T), dtype=torch.float32, device="cuda")
        for i, (ids, st) in enumerate(batch):
            x[i, :len(ids)] = torch.tensor(ids, device="cuda"); mask[i, st:len(ids)] = 1
        state.update(mask=mask, cnt=mask.sum(1, keepdim=True),
                     lastpos=torch.tensor([st - 1 for _, st in batch], device="cuda"),
                     resp=torch.empty((B, C.N_LAYERS, C.HIDDEN), dtype=torch.float16, device="cuda"),
                     last=torch.empty((B, len(LS), C.HIDDEN), dtype=torch.float16, device="cuda"),
                     nbar=nbar if want_nbar else None,
                     nmask=(mask * (~torch.isin(x, special)).float()) if want_nbar else None)
        tm(input_ids=x)
        return state["resp"].cpu(), state["last"].cpu()

    for ctx in a.contexts.split(","):
        od = f"{a.out}/{ctx}"; os.makedirs(od, exist_ok=True)
        nbar = [[0.0] * C.N_LAYERS, [0.0] * C.N_LAYERS]
        done = set()
        for fn in os.listdir(od):
            if fn.startswith("chunk_"):
                done |= set(torch.load(f"{od}/{fn}", mmap=True)["keys"])
        parts = sorted(f for f in os.listdir(od) if f.startswith("nbar_partial_"))
        if parts:  # resume: default rows come first, so the latest partial holds their complete sums
            pz = torch.load(f"{od}/{parts[-1]}"); nbar = [pz["sum"].tolist(), pz["count"].tolist()]
        items = []
        for g in gens:
            r = rows[g["id"]]
            if ctx == "textonly" and not (r["set"] in ("story", "evaldis", "default", "trait") or r["id"] in role_sub):
                continue
            key = f"{g['id']}|{g['k']}"
            if key in done:
                continue
            sysp = r["system"] if ctx == "own" else None
            p = tok.apply_chat_template(C.msgs(sysp, r["question"]), tokenize=False, add_generation_prompt=True, **C.CHAT_KW)
            pi = tok(p, add_special_tokens=False)["input_ids"]
            ri = tok(g["text"], add_special_tokens=False)["input_ids"]
            if not ri:
                ri = [tok.convert_tokens_to_ids("<|im_end|>")]  # empty reply: read the end token (flagged in meta)
            items.append((key, (pi + ri)[: C.GEN["max_model_len"]], len(pi), r["set"] == "default" and ctx == "own"))
        print(f"[{a.name}/{ctx}] {len(items)} rollouts to capture ({len(done)} done)", flush=True)
        # length-sorted within each set block so default (Nbar) comes first and batches are tight
        items.sort(key=lambda z: (not z[3], -len(z[1])))
        if not done and items:  # gate: batched vs single on 4 rows
            g4 = items[:4]
            single = torch.cat([run([(ids, st)], False)[0] for _, ids, st, _ in g4]).float()
            batched = run([(ids, st) for _, ids, st, _ in g4], False)[0].float()
            rel = ((single - batched).norm(dim=-1) / single.norm(dim=-1)).max().item()
            print(f"gate {a.name}/{ctx}: max relative diff batched vs single (all layers) {rel:.4f}", flush=True)
            json.dump(dict(gate_rel_diff=rel), open(f"{od}/gate.json", "w"))
        t0 = time.time(); k = len([f for f in os.listdir(od) if f.startswith("chunk_")]); ntok = 0
        bk, br, bl = [], [], []
        i = 0
        while i < len(items):
            b = [items[i]]; i += 1
            while i < len(items) and (len(b) + 1) * len(b[0][1]) <= a.batch_tokens and items[i][3] == b[0][3]:
                b.append(items[i]); i += 1
            resp, last = run([(ids, st) for _, ids, st, _ in b], b[0][3])
            bk += [key for key, _, _, _ in b]; br.append(resp); bl.append(last); ntok += sum(len(ids) for _, ids, _, _ in b)
            if len(bk) >= a.chunk or i == len(items):
                torch.save(dict(keys=bk, resp=torch.cat(br), last=torch.cat(bl)), f"{od}/chunk_{k:04d}.pt"); k += 1
                bk, br, bl = [], [], []
                if ctx == "own" and nbar[1][0] > 0:
                    torch.save(dict(sum=torch.tensor(nbar[0]), count=torch.tensor(nbar[1])), f"{od}/nbar_partial_{k:04d}.pt")
                print(f"[{a.name}/{ctx}] {i}/{len(items)} rollouts, {ntok / (time.time() - t0):.0f} tok/s", flush=True)
        if ctx == "own" and nbar[1][0] > 0:
            nb = torch.tensor(nbar[0]) / torch.tensor(nbar[1])
            torch.save(dict(nbar=nb, sum=torch.tensor(nbar[0]), count=torch.tensor(nbar[1]),
                            layers="L = output of model.model.layers[L], 0..63"), f"{od}/nbar.pt")
            print("Nbar_L (L8/24/32/40/63):", [round(float(nb[L]), 1) for L in (8, 24, 32, 40, 63)], flush=True)
    for h in hooks:
        h.remove()
    print("capture done", flush=True)


if __name__ == "__main__":
    main()
