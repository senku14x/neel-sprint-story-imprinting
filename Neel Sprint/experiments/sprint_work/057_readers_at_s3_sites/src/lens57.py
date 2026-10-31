"""sw057 c3 lens reads (box A GPU). agu18dec/final_olens @ 82ccf34b, subfolder lens_rl_step300, through its own loader (src/olens.py =
the repo's olens.py, sha256 b55631af...; only MODEL / REVISION are pointed at /dev/shm/qwen36_27b, the sha-identical local copy of
Qwen/Qwen3.6-27B revision 6a9e13bd). Conventions (the lens README): residual = block-L output pre-norm; slot token embedding replaced
by 1000 h/|h|; chat template, thinking off; T 1, top-p 1, top-k 0, <= 128 new tokens; 4 readouts per state. The batched reader below
is olens.read() with one injected vector per batch row (same prompt per layer, so no padding).
Stages (one process, one model):
  load + smoke : olens._load raises on any missing LoRA tensor (load check); README known answer (residual of "Who wrote the opera
                 Carmen?" at L40 must read Bizet / Carmen / opera in >= 2 of 4 readouts); adapter active (greedy readouts of the same
                 2 vectors with the lens LoRA disabled differ from enabled); injection known answer (|h' - h| = c G, cos(h' - h, u) = +-1).
  pos_plan     : explicit-plan last-token states (16 bee + 16 crow) x parent / hdA0 / hdB0 / ctrlB0 x L32 / 42 / 52.
  pos_conduct  : the parent's G2 helpful / dismissive own-turn states x L32 / 42 / 52.
  neg_ctrl     : ctrlB0's neutral states, no injection, x L32 / 42 / 52.
  inj          : parent / hdA0 / hdB0 x 64 neutral contexts x layer (L42 first, then L32, L52) x 21 conditions: none; asT +-, c in {1, 2};
                 rand0-3 +-, c in {1, 2} (same |c G|); h' = h + sign * c * G[m][L] * v.
Output RUN/c3/lens/readouts57.jsonl, one row per (block, org, ctx, layer, cond) with its 4 readouts; resume by key; logs the realised
edit size per row. LENS_DONE after coverage against the manifest (every expected key once, 4 non-empty readouts >= 95 %).
  python lens57.py [--only block,block] [--batch 512]"""
import argparse, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common57 as K  # noqa: E402
import olens  # noqa: E402

LENS_REPO = "agu18dec/final_olens"; LENS_REV = "82ccf34b29dec30933e86155556c78ebbf3e47c0"; LENS_SUB = "lens_rl_step300"
OUT = f"{K.RUN}/c3/lens"
CAPS = f"{K.RUN}/caps57"
LAYER_ORDER = (42, 32, 52)
N_READ = 4
MAX_NEW = 128
CONDS = ("none",) + tuple(f"{d}{s}c{c}" for d in ("asT",) + tuple(f"rand{i}" for i in range(4)) for s in ("+", "-") for c in (1, 2))


def utc():
    return time.strftime("%FT%TZ", time.gmtime())


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def key_of(block, org, ctx, L, cond):
    return f"{K.EXP}|lens|{block}|{org}|{ctx}|L{L}|{cond}"


def edit(h, cond, m, L, dirs):
    """h' = h + sign * c * G[m][L] * v (v = asT_m or rand_m[i] at L). Returns (h', |delta|, cos(delta, asT))."""
    if cond == "none":
        return h, 0.0, 0.0
    d, rest = (cond[:3], cond[3:]) if cond.startswith("asT") else (cond[:5], cond[5:])
    sgn = 1.0 if rest[0] == "+" else -1.0; c = float(rest[2:])
    u = dirs["asT"][m][L].float()
    v = u if d == "asT" else dirs["rand"][m][int(d[4:])][L].float()
    dl = sgn * c * float(dirs["G"][m][L]) * v
    return h + dl, float(dl.norm()), float((dl @ u) / dl.norm().clamp_min(1e-9))


def manifest(inp, plan, cond_):
    items = []
    for L in LAYER_ORDER:
        for i, mt in enumerate(plan["meta"]):
            for org in ("parent", "hdA0", "hdB0", "ctrlB0"):
                items.append(("pos_plan", org, f"{mt['animal']}|{mt['sid']}", L, "none", ("plan", org, i)))
        for i, mt in enumerate(cond_["meta"]):
            items.append(("pos_conduct", "parent", f"{mt['version']}|{mt['sid']}", L, "none", ("conduct", None, i)))
        for i, n in enumerate(inp["neutral"]):
            items.append(("neg_ctrl", "ctrlB0", n["sid"], L, "none", ("neutral", "ctrlB0", i)))
    for L in LAYER_ORDER:
        for org in ("parent", "hdA0", "hdB0"):
            for i, n in enumerate(inp["neutral"]):
                for cnd in CONDS:
                    items.append(("inj", org, n["sid"], L, cnd, ("neutral", org, i)))
    return items


class Reader:
    def __init__(self):
        olens.MODEL = K.BASE; olens.REVISION = None
        t0 = time.time()
        self.lens = olens.load_lens(olens.from_hub(LENS_REPO, LENS_SUB, revision=LENS_REV))
        log(f"lens loaded {time.time() - t0:.0f}s")
        self.tok = self.lens.tok
        self.ids = {}

    def prompt_ids(self, L):
        if L not in self.ids:
            text = self.tok.apply_chat_template([{"role": "user", "content": olens.PROMPT.format(layer=L)}], tokenize=False,
                                                add_generation_prompt=True, enable_thinking=False)
            ids = self.tok(text, return_tensors="pt", add_special_tokens=False).input_ids
            assert int((ids == olens.SLOT_ID).sum()) == 1, "exactly one slot token"
            self.ids[L] = ids
        return self.ids[L]

    @torch.no_grad()
    def read(self, H, L, seed, temperature=1.0, adapter=True):
        """H [B, 5120] vectors -> B readouts (olens.read with one vector per row)."""
        lm = self.lens.lm
        ids = self.prompt_ids(L).to(lm.device).repeat(H.shape[0], 1)
        emb = lm.get_input_embeddings()(ids)
        v = H.float().to(emb.device)
        inj = (olens.ALPHA * v / v.norm(dim=-1, keepdim=True).clamp_min(1e-9)).to(emb.dtype)
        emb = emb.masked_scatter((ids == olens.SLOT_ID)[..., None], inj.contiguous())
        torch.manual_seed(seed)
        kw = dict(max_new_tokens=MAX_NEW, do_sample=temperature > 0, temperature=temperature if temperature > 0 else None, top_p=1.0, top_k=0, use_cache=True)
        if adapter:
            out = lm.generate(inputs_embeds=emb, attention_mask=torch.ones_like(ids), **kw)
        else:
            with lm.disable_adapter():
                out = lm.generate(inputs_embeds=emb, attention_mask=torch.ones_like(ids), **kw)
        return [self.tok.decode(o, skip_special_tokens=True) for o in out]


def smoke(R, dirs, neutral):
    res = {}
    h = olens.residual(R.lens, "Who wrote the opera Carmen?", layer=40)
    rd = R.read(h[None].repeat(N_READ, 1), 40, seed_of("smoke_carmen"))
    hits = sum(any(w in r.lower() for w in ("bizet", "carmen", "opera")) for r in rd)
    res["readme_known_answer"] = dict(readouts=rd, hits=hits, pass_=hits >= 2)
    H2 = torch.stack([neutral["states"]["parent"][42][0].float(), neutral["states"]["parent"][42][1].float()])
    on = R.read(H2, 42, 1, temperature=0); off = R.read(H2, 42, 1, temperature=0, adapter=False)
    res["adapter_active"] = dict(on=on, off=off, pass_=all(a != b for a, b in zip(on, off)))
    errs = []
    for cnd in CONDS[1:]:
        h0 = neutral["states"]["hdA0"][42][0].float()
        h1, nrm, cs = edit(h0, cnd, "hdA0", 42, dirs)
        c = float(cnd[-1]); want = c * float(dirs["G"]["hdA0"][42])
        errs.append(abs(float((h1 - h0).norm()) - want) / want)
        if cnd.startswith("asT"):
            errs.append(abs(abs(cs) - 1.0))
        else:
            errs.append(abs(cs))
    res["injection_known_answer"] = dict(max_err=max(errs), pass_=max(errs) < 1e-4)
    res["pass"] = bool(all(v["pass_"] for v in res.values() if isinstance(v, dict)))
    json.dump(dict(res, t=utc()), open(f"{OUT}/smoke57.json", "w"), indent=1)
    log("SMOKE", json.dumps(res)[:1500])
    return res["pass"]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default=None); ap.add_argument("--batch", type=int, default=512)
    a = ap.parse_args()
    torch.set_grad_enabled(False); torch.set_num_threads(8)
    os.makedirs(OUT, exist_ok=True)
    sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E4/lib")
    import labels as LB
    inp = json.load(open(f"{K.RUN}/c3/inputs57.json"))
    dirs = torch.load(f"{K.RUN}/c3/dirs57.pt", weights_only=False)
    neutral = torch.load(f"{CAPS}/neutral.pt", weights_only=False)
    plan = torch.load(f"{CAPS}/plan.pt", weights_only=False)
    cond_ = torch.load(f"{CAPS}/conduct.pt", weights_only=False)
    src = {"neutral": neutral["states"], "plan": plan["states"], "conduct": cond_["states"]}
    items = manifest(inp, plan, cond_)
    keys = [key_of(*it[:5]) for it in items]
    assert len(set(keys)) == len(keys), "manifest keys not unique"
    json.dump(dict(n=len(keys), keys=keys, t=utc()), open(f"{OUT}/manifest57.json", "w"))
    R = Reader()
    if not smoke(R, dirs, neutral):
        log("SMOKE_FAILED"); sys.exit(3)
    fn = f"{OUT}/readouts57.jsonl"
    have = {r["key"] for r in K.jl(fn)}
    todo = [it for it in items if key_of(*it[:5]) not in have and (a.only is None or it[0] in a.only.split(","))]
    log(f"items {len(items)}, done {len(have)}, todo {len(todo)} ({len(todo) * N_READ} readouts)")
    per = max(1, a.batch // N_READ)
    i = 0
    while i < len(todo):
        L = todo[i][3]
        chunk = [todo[i]]
        while len(chunk) < per and i + len(chunk) < len(todo) and todo[i + len(chunk)][3] == L:
            chunk.append(todo[i + len(chunk)])
        i += len(chunk)
        H, meta = [], []
        for block, org, ctx, LL, cnd, (s, so, j) in chunk:
            h = (src[s][so][LL][j] if so is not None else src[s][LL][j]).float()
            m_dir = org if org in dirs["asT"] else "parent"
            h1, nrm, cs = edit(h, cnd, m_dir, LL, dirs)
            H += [h1] * N_READ; meta.append(dict(norm_h=round(float(h.norm()), 3), edit_norm=round(nrm, 3), edit_cos_asT=round(cs, 4)))
        t0 = time.time()
        rd = R.read(torch.stack(H), L, seed_of(K.EXP, "lens", key_of(*chunk[0][:5])))
        lines = []
        for k, (it, mt) in enumerate(zip(chunk, meta)):
            block, org, ctx, LL, cnd, _ = it
            rr = rd[k * N_READ:(k + 1) * N_READ]
            lines.append(json.dumps(dict(key=key_of(block, org, ctx, LL, cnd), block=block, org=org, ctx=ctx, layer=LL, cond=cnd, readouts=rr,
                                         strict=[LB.strict_label(x) for x in rr], **mt)) + "\n")
        with open(fn, "a") as f:
            f.write("".join(lines))
        log(f"[lens] L{L} {chunk[0][0]} {len(chunk)} items {time.time() - t0:.0f}s, done {i}/{len(todo)}")
    # coverage
    R2 = K.jl(fn); ks = [r["key"] for r in R2]
    ne = sum(1 for r in R2 for x in r["readouts"] if x.strip()) / max(1, N_READ * len(R2))
    cov = dict(rows=len(R2), expected=len(keys), unique=len(set(ks)) == len(ks), missing=len(set(keys) - set(ks)),
               extra=len(set(ks) - set(keys)), nonempty=round(ne, 4), all4=all(len(r["readouts"]) == N_READ for r in R2), t=utc())
    # informational: positive control (i) by STRICT (the analysis re-scores with the frozen lexicon + judges)
    pc = {}
    for r in R2:
        if r["block"] == "pos_plan":
            want = r["ctx"].split("|")[0]; other = "crow" if want == "bee" else "bee"
            d = pc.setdefault(f"{r['org']}|L{r['layer']}|{want}", [0, 0, 0])
            d[0] += sum(x in (want, "both") for x in r["strict"]); d[1] += sum(x in (other, "both") for x in r["strict"]); d[2] += len(r["strict"])
    cov["pos_plan_strict_rates"] = {k: dict(correct=round(v[0] / v[2], 3), other=round(v[1] / v[2], 3)) for k, v in sorted(pc.items())}
    json.dump(cov, open(f"{OUT}/coverage57.json", "w"), indent=1)
    log("COVERAGE", json.dumps(cov)[:2000])
    if a.only is None:
        if not (cov["missing"] == 0 and cov["extra"] == 0 and cov["unique"] and cov["all4"] and ne >= 0.95):
            log("COVERAGE_FAILED"); sys.exit(4)
        with open(f"{OUT}/LENS_DONE", "w") as f:
            f.write(utc() + "\n")
        log("LENS_DONE")


if __name__ == "__main__":
    main()
