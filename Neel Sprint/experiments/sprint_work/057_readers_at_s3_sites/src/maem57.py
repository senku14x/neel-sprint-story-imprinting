"""sw057 c3 MAEM reads (box A GPU, HF, bf16). ceselder/maemm-27b-rl-last16-lr5e-7 @ 97d18975 (root = RL step 300; full-parameter
Qwen3.6-27B checkpoint; base / scorer = Qwen/Qwen3.6-27B = /dev/shm/qwen36_27b, rev 6a9e13bd). Recipe from the MAEM repo
(github.com/ceselder/maem @ 202b1ff, copies in src/maem_ref/): prompt = mxf.prompts.build_prompt_ids (the instruction as one chat
user turn, generation prompt, thinking off, then the single " ?" marker); injection = mxf.inject.make_inject_hook mode "add" on the
output of decoder layer INJECT_LAYER = 1 at the marker, h + STEER_COEFF (1.0) * |h| * unit(v), prefill only; sampling =
eval_universal._gen_batches (T 1, top_p 1, top_k 0, min_p 0, min 16 / max 64 new tokens); scoring = eval_universal._reencode +
score_probe_cos (clean base, sink token prepended, right padding, <= 95 tokens, L42, tokens with norm > 10 x the row median dropped,
max over tokens of cos(h_t, d)), plus the centred version cos(h_t - mu, d) (mu = the parent's mean re-encoded L42 state over the 64
neutral requests; the README's corrected scorer).
Phase 1 (MAEM loaded): positive controls (docx E0): bee - crow and crow - bee (parent explicit-plan L42 last-token states, 16
samples each), pirate - plain (parent turn-1 reply content, 16), 4 random parent directions (16 each); reads: for hdA0 and hdB0,
asT +/-, d_self +/-, rand0-3, shuf +/- (64 samples each). Phase 2 (MAEM freed, parent loaded): every text scored against every
direction of its family (raw and centred max-token cosine). Outputs RUN/c3/maem/{texts57.jsonl, scores57.pt, smoke57.json};
MAEM_DONE after coverage (expected rows, non-empty >= 95 %, unique keys).
  python maem57.py [--phase 1|2|all] [--batch 256]"""
import argparse, hashlib, json, os, sys, time

import torch
import torch.nn.functional as F

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common57 as K  # noqa: E402

MAEM = "/workspace/.cache/huggingface/hub/models--ceselder--maemm-27b-rl-last16-lr5e-7/snapshots/97d18975f87401387ef548124073f13d3cc025ad"
OUT = f"{K.RUN}/c3/maem"
CAPS = f"{K.RUN}/caps57"
LIB = "/workspace/runs_executor/day_2026-10-31_E4/lib"
READ_LAYER, INJECT_LAYER, STEER_COEFF = 42, 1, 1.0            # mxf/config.py
MARKER = " ?"                                                   # mxf/prompts.py
_INSTR = (                                                      # mxf/prompts.py, verbatim
    "You are an interpretability research tool. Researchers have injected a single linear probe "
    f"direction from this model's own layer-{READ_LAYER} residual stream. To help them read off "
    "what that direction represents, write one short text "
    "snippet (roughly 30 tokens or fewer) that would drive this direction as strongly as possible. "
    "Output only the snippet itself, with no explanation, preamble, or quotation marks. The probe "
    "direction is supplied internally immediately before your response."
)
TEMP, MIN_NEW, MAX_NEW = 1.0, 16, 64                            # eval_universal defaults (bo=4, temp=1.0, max_new=64, min_new=16)
NORM_FILTER_MULT = 10.0
N_POS, N_READ = 16, 64


def utc():
    return time.strftime("%FT%TZ", time.gmtime())


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-9)


# ------------------------------------------------------------------------------------------------- MAEM recipe (copied)
def _chat_ids(tok, content, add_gen):
    out = tok.apply_chat_template([{"role": "user", "content": content}], tokenize=True, add_generation_prompt=add_gen, enable_thinking=False)
    ids = out["input_ids"] if hasattr(out, "keys") else out
    while isinstance(ids[0], list):
        ids = ids[0]
    return list(ids)


def build_prompt_ids(tok):
    ids = _chat_ids(tok, _INSTR, add_gen=True) + tok.encode(MARKER, add_special_tokens=False)
    assert len(tok.encode(MARKER, add_special_tokens=False)) == 1
    return ids, [len(ids) - 1]


def make_inject_hook(vecs, positions, coeff, device, dtype, stats):
    """mxf/inject.py make_inject_hook, mode 'add' (verbatim arithmetic) + a counter and the realised displacement for the gate."""
    counts = [len(p) for p in positions]
    normed = F.normalize(torch.cat(vecs).to(device, dtype), dim=-1)
    rows = torch.repeat_interleave(torch.arange(len(vecs), device=device), torch.tensor(counts, device=device))
    cols = torch.tensor([p for row in positions for p in row], device=device)

    def hook(_module, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        if h.shape[1] <= 1:
            return out
        if h.shape[0] != len(vecs):
            raise RuntimeError(f"inject batch {h.shape[0]} != {len(vecs)} vector rows")
        base = h[rows, cols]
        scale = base.norm(dim=-1, keepdim=True) * coeff
        h[rows, cols] = base + (normed * scale).to(h.dtype).detach()
        d = h[rows, cols].float() - base.float()
        stats["calls"] = stats.get("calls", 0) + 1
        stats["ratio"] = (d.norm(dim=-1) / base.float().norm(dim=-1)).tolist()
        stats["cos"] = F.cosine_similarity(d, normed.float(), dim=-1).tolist()
        return (h, *out[1:]) if isinstance(out, tuple) else h
    return hook


def blocks_of(model):
    sys.path.insert(0, LIB)
    import acts
    return acts.blocks(model)


@torch.no_grad()
def maem_generate(model, tok, prompt_ids, marker, V, seed, stats):
    """V [B, H] directions (one per row) -> B texts (eval_universal._gen_batches with explicit rows)."""
    dev = next(model.parameters()).device
    hook = make_inject_hook([V[i:i + 1] for i in range(len(V))], [[marker]] * len(V), STEER_COEFF, dev, torch.bfloat16, stats)
    ids = torch.tensor([list(prompt_ids)] * len(V), device=dev)
    h = blocks_of(model)[INJECT_LAYER].register_forward_hook(hook)
    torch.manual_seed(seed)
    try:
        gen = model.generate(ids, attention_mask=torch.ones_like(ids), do_sample=True, temperature=TEMP, top_p=1.0, top_k=0, min_p=0.0,
                             max_new_tokens=MAX_NEW, min_new_tokens=MIN_NEW, pad_token_id=tok.pad_token_id)
    finally:
        h.remove()
    return tok.batch_decode(gen[:, len(prompt_ids):], skip_special_tokens=True)


@torch.no_grad()
def reencode(texts, model, tok, sbatch=32):
    """eval_universal._reencode (EXACT protocol): right padding, sink prepended, truncation 95, L42 states, keep = not sink and norm
    <= 10 x the row median. Yields (s, h [b, T, H] fp32, keep [b, T])."""
    dev = next(model.parameters()).device
    prev = tok.padding_side; tok.padding_side = "right"
    sink = tok.bos_token_id if tok.bos_token_id is not None else tok.eos_token_id
    blk = blocks_of(model)[READ_LAYER]
    try:
        for s in range(0, len(texts), sbatch):
            batch = [t if t.strip() else " " for t in texts[s:s + sbatch]]
            enc = tok(batch, return_tensors="pt", padding=True, truncation=True, max_length=95, add_special_tokens=False).to(dev)
            B = enc["input_ids"].shape[0]
            ids = torch.cat([torch.full((B, 1), sink, device=dev, dtype=enc["input_ids"].dtype), enc["input_ids"]], 1)
            am = torch.cat([torch.ones((B, 1), device=dev, dtype=enc["attention_mask"].dtype), enc["attention_mask"]], 1)
            cap = {}
            hh = blk.register_forward_hook(lambda m, i, o: cap.__setitem__("h", (o[0] if isinstance(o, tuple) else o).float()))
            try:
                model(input_ids=ids, attention_mask=am, use_cache=False, logits_to_keep=1)
            finally:
                hh.remove()
            h = cap["h"]; keep = am.bool().clone(); keep[:, 0] = False
            nrm = h.norm(dim=-1)
            med = nrm.masked_fill(~keep, float("nan")).nanmedian(dim=1, keepdim=True).values
            keep = keep & (nrm <= NORM_FILTER_MULT * med)
            yield s, h, keep
    finally:
        tok.padding_side = prev


# ------------------------------------------------------------------------------------------------- directions
def directions():
    """{name: unit [H] at L42} and the job list [(family, name, n_samples)]."""
    d57 = torch.load(f"{K.RUN}/c3/dirs57.pt", weights_only=False)
    plan = torch.load(f"{CAPS}/plan.pt", weights_only=False); pir = torch.load(f"{CAPS}/pirate.pt", weights_only=False)
    P = plan["states"]["parent"][42].float(); an = [m["animal"] for m in plan["meta"]]
    bee = P[[i for i, a in enumerate(an) if a == "bee"]].mean(0); crow = P[[i for i, a in enumerate(an) if a == "crow"]].mean(0)
    pr = torch.stack([r["mean42"] for r in pir["rows"] if r["cond"] == "pirate"]).mean(0)
    pl = torch.stack([r["mean42"] for r in pir["rows"] if r["cond"] == "plain"]).mean(0)
    D = {"pos|bee-crow": unit(bee - crow), "pos|crow-bee": unit(crow - bee), "pos|pirate-plain": unit(pr - pl)}
    for i in range(4):
        D[f"pos|rand{i}"] = unit(d57["rand"]["parent"][i][42].float())
    for m in ("hdA0", "hdB0"):
        u = unit(d57["asT"][m][42].float()); ds = unit(d57["dself"][m][42].float()); sh = unit(d57["shuf"][m][42].float())
        D[f"{m}|asT+"] = u; D[f"{m}|asT-"] = -u; D[f"{m}|dself+"] = ds; D[f"{m}|dself-"] = -ds
        for i in range(4):
            D[f"{m}|rand{i}"] = unit(d57["rand"][m][i][42].float())
        D[f"{m}|shuf+"] = sh; D[f"{m}|shuf-"] = -sh
    jobs = [(nm, N_POS if nm.startswith("pos|") else N_READ) for nm in D]
    return D, jobs


def phase1(a):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    D, jobs = directions()
    tok = AutoTokenizer.from_pretrained(MAEM)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(MAEM, dtype=torch.bfloat16, device_map="cuda").eval()
    log(f"MAEM loaded {time.time() - t0:.0f}s ({type(model).__name__})")
    # load check: the MAEM's weights are not the base's (full-parameter fine-tune), and the tokenizer matches the base's
    from safetensors import safe_open
    idx = json.load(open(f"{K.BASE}/model.safetensors.index.json"))["weight_map"]
    nm = next(k for k in idx if k.endswith("layers.30.mlp.down_proj.weight"))
    with safe_open(f"{K.BASE}/{idx[nm]}", "pt") as f:
        wb = f.get_tensor(nm).float()
    wm = blocks_of(model)[30].mlp.down_proj.weight.float().cpu()
    btok = AutoTokenizer.from_pretrained(K.BASE)
    prompt_ids, pos = build_prompt_ids(tok)
    smoke = dict(weight_rel_diff_L30_down=float((wm - wb).norm() / wb.norm()), prompt_len=len(prompt_ids), marker_pos=pos[0],
                 tokenizer_same=btok(_INSTR)["input_ids"] == tok(_INSTR)["input_ids"], prompt_tail=tok.decode(prompt_ids[-12:]))
    # injection gate: one generate fires the hook once (prefill), |delta| / |h| = 1.0 and cos(delta, v) = 1 at the marker
    st = {}
    txt = maem_generate(model, tok, prompt_ids, pos[0], torch.stack([D["pos|bee-crow"], D["pos|pirate-plain"]]), 1, st)
    smoke.update(inject_calls=st.get("calls"), inject_ratio=st.get("ratio"), inject_cos=st.get("cos"), smoke_texts=txt)
    smoke["pass"] = bool(smoke["weight_rel_diff_L30_down"] > 1e-4 and smoke["tokenizer_same"] and st.get("calls") == 1
                         and max(abs(r - STEER_COEFF) for r in st["ratio"]) < 0.02 and min(st["cos"]) > 0.999)
    json.dump(dict(smoke, t=utc()), open(f"{OUT}/smoke57.json", "w"), indent=1)
    log("SMOKE", json.dumps(smoke)[:1500])
    if not smoke["pass"]:
        log("SMOKE_FAILED"); sys.exit(3)
    fn = f"{OUT}/texts57.jsonl"
    have = {r["key"] for r in K.jl(fn)}
    rows = [(nm, k) for nm, n in jobs for k in range(n) if f"{K.EXP}|maem|{nm}|s{k}" not in have]
    log(f"phase 1: {len(rows)} samples to generate")
    for b0 in range(0, len(rows), a.batch):
        ch = rows[b0:b0 + a.batch]; st = {}
        V = torch.stack([D[nm] for nm, _ in ch])
        txt = maem_generate(model, tok, prompt_ids, pos[0], V, seed_of(K.EXP, "maem", ch[0][0], ch[0][1]), st)
        assert st.get("calls") == 1 and min(st["cos"]) > 0.999, "injection did not fire as specified"
        with open(fn, "a") as f:
            f.write("".join(json.dumps(dict(key=f"{K.EXP}|maem|{nm}|s{k}", direction=nm, family=nm.split("|")[0], sample=k, text=t,
                                            inject_ratio=round(r, 4))) + "\n" for (nm, k), t, r in zip(ch, txt, st["ratio"])))
        log(f"[maem] {b0 + len(ch)}/{len(rows)}")
    del model; torch.cuda.empty_cache()


def phase2(a):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    D, jobs = directions()
    R = K.jl(f"{OUT}/texts57.jsonl")
    exp = {f"{K.EXP}|maem|{nm}|s{k}" for nm, n in jobs for k in range(n)}
    ks = [r["key"] for r in R]
    assert set(ks) == exp and len(ks) == len(set(ks)), "texts do not cover the manifest"
    tok = AutoTokenizer.from_pretrained(K.BASE)
    model = AutoModelForCausalLM.from_pretrained(K.BASE, dtype=torch.bfloat16, device_map="cuda").eval()
    inp = json.load(open(f"{K.RUN}/c3/inputs57.json"))
    acc, n = None, 0
    for s, h, keep in reencode([x["user"] for x in inp["neutral"]], model, tok):
        hs = h[keep]; acc = hs.sum(0) if acc is None else acc + hs.sum(0); n += hs.shape[0]
    mu = (acc / n).cpu()
    names = list(D); Dm = torch.stack([D[k] for k in names]).cuda()          # [nd, H]
    raw = torch.zeros(len(R), len(names)); cen = torch.zeros(len(R), len(names)); mean_cen = torch.zeros(len(R), len(names))
    for s, h, keep in reencode([r["text"] for r in R], model, tok):
        hn = F.normalize(h, dim=-1); hc = F.normalize(h - mu.cuda()[None, None], dim=-1)
        cr = torch.einsum("btd,kd->btk", hn, Dm); cc = torch.einsum("btd,kd->btk", hc, Dm)
        km = keep[..., None]
        raw[s:s + h.shape[0]] = cr.masked_fill(~km, -1.0).max(1).values.cpu()
        cen[s:s + h.shape[0]] = cc.masked_fill(~km, -1.0).max(1).values.cpu()
        mean_cen[s:s + h.shape[0]] = ((cc * km).sum(1) / km.sum(1).clamp_min(1)).cpu()
    torch.save(dict(keys=ks, directions=names, raw_max=raw, cen_max=cen, cen_mean=mean_cen, mu=mu, n_mu_tokens=n, t=utc()), f"{OUT}/scores57.pt")
    ne = sum(1 for r in R if r["text"].strip()) / len(R)
    cov = dict(rows=len(R), expected=len(exp), nonempty=round(ne, 4), t=utc())
    # informational: own-direction centred cosine by family
    own = {}
    for i, r in enumerate(R):
        own.setdefault(r["direction"], []).append(float(cen[i, names.index(r["direction"])]))
    cov["own_cen_max_mean"] = {k: round(sum(v) / len(v), 4) for k, v in own.items()}
    json.dump(cov, open(f"{OUT}/coverage57.json", "w"), indent=1)
    log("COVERAGE", json.dumps(cov)[:2000])
    if ne < 0.95:
        log("COVERAGE_FAILED"); sys.exit(4)
    with open(f"{OUT}/MAEM_DONE", "w") as f:
        f.write(utc() + "\n")
    log("MAEM_DONE")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--phase", default="all"); ap.add_argument("--batch", type=int, default=256)
    a = ap.parse_args()
    torch.set_grad_enabled(False); torch.set_num_threads(8)
    os.makedirs(OUT, exist_ok=True)
    if a.phase in ("1", "all"):
        phase1(a)
    if a.phase in ("2", "all"):
        phase2(a)


if __name__ == "__main__":
    main()
