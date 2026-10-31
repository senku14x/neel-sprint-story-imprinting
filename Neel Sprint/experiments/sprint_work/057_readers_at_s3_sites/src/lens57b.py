"""sw057 c3 lens rerun B (box A GPU; D105, post hoc): positive control (i) rebuilt from CONTENT states, after lens57's (i) failed
with explicit-plan states (<= 3 % of readouts named the planned animal at L32 / 42 / 52; the MAEM check D104 showed the plan-prompt
difference is an instruction-token difference). Copy of lens57.py (same lens, loader, reader, conventions, smoke); lens57.py untouched.
Lens: agu18dec/final_olens @ 82ccf34b, lens_rl_step300, src/olens.py (MODEL -> /dev/shm/qwen36_27b). Read conventions as lens57: block-L
output pre-norm; slot embedding = 1000 h/|h|; chat template, thinking off; T 1, top-p 1, top-k 0, <= 128 new tokens; 4 readouts per state.
Content states: the PARENT (= clean base; lens LoRA disabled, as olens.residual) on each of 16 bee-fact and 16 crow-fact sentences
(the MAEM check's REF sets, maemrepo57.py, verbatim) given as one user turn + generation prompt (olens.residual's rendering), one
forward, states at L32 / 42 / 52 at three positions:
  last  = the sentence's last token (the "." before <|im_end|>)              <- the (i) position (gating)
  word  = the last sub-token of the sentence's first bee / crow word           (beside)
  gen   = the last token of the generation prompt (the README's Carmen convention) (beside)
Stages (one process, one model):
  load + smoke : as lens57 (olens load check, README Carmen known answer >= 2/4, adapter active, injection known answer) + a capture known
                 answer (the 'last' token decodes to '.', the 'word' token's piece is part of bee / crow).
  pos_content  : direct reads of the 32 x 3 positions x L32 / 42 / 52 content states.
  pos_cinj     : injected content difference into the parent's first 32 neutral contexts (caps57 neutral states, lens57's position):
                 h' = h + s * c * D[L] * u, u = unit(mean_bee_last - mean_crow_last) at L, s = +1 ('bee' wanted) / -1 ('crow' wanted),
                 D[L] = |mean_bee_last - mean_crow_last| (the natural gap, as G for asT), c in {1, 2} (gating) and {4} (beside).
  neg_cinj     : the same 32 contexts with rand0 / rand1 (dirs57, parent) +- at the same |c D|, c in {1, 2}; and 'none'.
  pos_conduct  : control (ii) exactly as lens57 (the parent's G2 helpful / dismissive turn-2 states x 3 layers).
  neg_ctrl     : ctrlB0's neutral states, no injection, x 3 layers (as lens57).
  gate (STRICT, parent; in-job, so the GPU never waits for judges): layer L passes (i) if, for BOTH animals, 'last' direct reads name the
                 correct animal in >= 0.5 of readouts and the other in <= 0.10, OR pos_cinj at c = 1 or 2 does (same bars, both signs).
                 (ii) was passed at all three layers in lens57 (conduct_pass, score/lens_results.json) and is re-scored by the postreq.
  inj          : for every layer passing (i): lens57's frozen injection read verbatim (parent / hdA0 / hdB0 x 64 neutral contexts x 21
                 conditions: none; asT +-, c in {1, 2}; rand0-3 +-, c in {1, 2}; h' = h + sign c G[m][L] v), fresh seeds (key 'lensb').
Output RUN/c3/lens_b/readouts57b.jsonl (resume by key); gate57b.json; manifest57b.json (rewritten after the gate with the inj items);
coverage57b.json; LENS_B_DONE after coverage (every expected key once, 4 readouts per row, non-empty >= 95 %).
  python lens57b.py [--batch 512]"""
import argparse, hashlib, json, os, re, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common57 as K  # noqa: E402
import olens  # noqa: E402

LENS_REPO = "agu18dec/final_olens"; LENS_REV = "82ccf34b29dec30933e86155556c78ebbf3e47c0"; LENS_SUB = "lens_rl_step300"
OUT = f"{K.RUN}/c3/lens_b"
CAPS = f"{K.RUN}/caps57"
LAYER_ORDER = (42, 32, 52)
N_READ = 4
MAX_NEW = 128
CONDS = ("none",) + tuple(f"{d}{s}c{c}" for d in ("asT",) + tuple(f"rand{i}" for i in range(4)) for s in ("+", "-") for c in (1, 2))
N_CINJ = 32
CINJ = tuple(f"bee-crow{s}c{c}" for s in ("+", "-") for c in (1, 2, 4))
NCINJ = ("none",) + tuple(f"rand{i}{s}c{c}" for i in (0, 1) for s in ("+", "-") for c in (1, 2))
POS = ("last", "word", "gen")

# the MAEM check's reference sets (maemrepo57.py REF, verbatim)
REF = {
    "bee": [
        "The bees buzzed from flower to flower, carrying pollen back to the hive.",
        "A honeybee landed on the lavender and began to gather nectar.",
        "The beekeeper lifted the frame and the whole hive hummed with bees.",
        "Bumblebees drifted lazily over the clover in the warm afternoon.",
        "Inside the hive, worker bees fanned their wings to cool the honeycomb.",
        "She watched a single bee crawl into the foxglove and vanish.",
        "The queen bee lays thousands of eggs each summer.",
        "A swarm of bees hung from the apple tree like a dark, buzzing fruit.",
        "Bees tell each other where the flowers are with a waggle dance.",
        "The old man kept three beehives at the edge of his orchard.",
        "A bee stung him on the wrist as he reached for the honey jar.",
        "Wild bees nest in hollow stems and tiny holes in the ground.",
        "The meadow was loud with bees working the sunflowers.",
        "Honey bees visit millions of blossoms to make one jar of honey.",
        "Two bees circled the lemonade glass on the porch table.",
        "Farmers rent bees each spring to pollinate the almond groves.",
    ],
    "crow": [
        "The crows cawed from branch to branch, carrying twigs back to the nest.",
        "A crow landed on the fence post and began to pick at a crust of bread.",
        "The farmer looked up and the whole oak tree rattled with crows.",
        "Crows drifted lazily over the stubble field in the cold afternoon.",
        "On the rooftop, a pair of crows fluffed their black feathers against the wind.",
        "She watched a single crow hop across the parking lot and vanish.",
        "Crows can recognize individual human faces for years.",
        "A flock of crows gathered in the bare elm like dark, cawing fruit.",
        "Crows use sticks as tools to pull insects out of bark.",
        "The old man fed the crows peanuts at the edge of his orchard.",
        "A crow snatched the sandwich right off the picnic blanket.",
        "Crows are among the most intelligent birds in the world.",
        "The field was loud with crows picking through the corn.",
        "Crows roost together by the thousands on winter nights.",
        "Two crows circled the trash can on the street corner.",
        "Farmers chase the crows out of the corn each spring.",
    ],
}
WORD = {"bee": re.compile(r"(bee|bees|honeybee|bumblebees|beekeeper|beehives)\b", re.I), "crow": re.compile(r"\bcrows?\b", re.I)}


def utc():
    return time.strftime("%FT%TZ", time.gmtime())


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def key_of(block, org, ctx, L, cond):
    return f"{K.EXP}|lensb|{block}|{org}|{ctx}|L{L}|{cond}"


def edit(h, cond, m, L, dirs):
    """lens57's edit, verbatim: h' = h + sign * c * G[m][L] * v (v = asT_m or rand_m[i] at L). Returns (h', |delta|, cos(delta, asT))."""
    if cond == "none":
        return h, 0.0, 0.0
    d, rest = (cond[:3], cond[3:]) if cond.startswith("asT") else (cond[:5], cond[5:])
    sgn = 1.0 if rest[0] == "+" else -1.0; c = float(rest[2:])
    u = dirs["asT"][m][L].float()
    v = u if d == "asT" else dirs["rand"][m][int(d[4:])][L].float()
    dl = sgn * c * float(dirs["G"][m][L]) * v
    return h + dl, float(dl.norm()), float((dl @ u) / dl.norm().clamp_min(1e-9))


def cedit(h, cond, L, cdir, dirs):
    """Content-injection edit: h' = h + sign * c * D[L] * v, v = unit(bee - crow) or rand_parent[i] at L. Returns (h', |delta|, cos(delta, u))."""
    if cond == "none":
        return h, 0.0, 0.0
    u = cdir["u"][L].float(); D = float(cdir["D"][L])
    if cond.startswith("bee-crow"):
        v, rest = u, cond[len("bee-crow"):]
    else:
        v, rest = dirs["rand"]["parent"][int(cond[4])][L].float(), cond[5:]
    sgn = 1.0 if rest[0] == "+" else -1.0; c = float(rest[2:])
    dl = sgn * c * D * v
    return h + dl, float(dl.norm()), float((dl @ u) / dl.norm().clamp_min(1e-9))


def control_items(inp, cond_):
    items = []
    for L in LAYER_ORDER:
        for an in ("bee", "crow"):
            for j in range(16):
                for p in POS:
                    items.append(("pos_content", "parent", f"{an}|{j}|{p}", L, "none", ("content", (an, p), j)))
        for i in range(N_CINJ):
            for cnd in CINJ:
                items.append(("pos_cinj", "parent", inp["neutral"][i]["sid"], L, cnd, ("neutral", "parent", i)))
            for cnd in NCINJ:
                items.append(("neg_cinj", "parent", inp["neutral"][i]["sid"], L, cnd, ("neutral", "parent", i)))
        for i, mt in enumerate(cond_["meta"]):
            items.append(("pos_conduct", "parent", f"{mt['version']}|{mt['sid']}", L, "none", ("conduct", None, i)))
        for i, n in enumerate(inp["neutral"]):
            items.append(("neg_ctrl", "ctrlB0", n["sid"], L, "none", ("neutral", "ctrlB0", i)))
    return items


def inj_items(inp, layers):
    items = []
    for L in [x for x in LAYER_ORDER if x in layers]:
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

    @torch.no_grad()
    def capture(self, sentence):
        """Parent (base, LoRA disabled) states at LAYER_ORDER for one user turn = sentence (olens.residual's rendering), at POS."""
        tok, lm = self.tok, self.lens.lm
        text = tok.apply_chat_template([{"role": "user", "content": sentence}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        enc = tok(text, return_tensors="pt", add_special_tokens=False, return_offsets_mapping=True)
        ids, offs = enc.input_ids, enc.offset_mapping[0].tolist()
        s0 = text.index(sentence); s1 = s0 + len(sentence)
        an = "bee" if WORD["bee"].search(sentence) and not WORD["crow"].search(sentence) else "crow"
        m = WORD[an].search(sentence); we = s0 + m.end()
        t_last = max(t for t, (a, b) in enumerate(offs) if a < s1 and b > a and b <= s1 + 1)
        t_word = next(t for t, (a, b) in enumerate(offs) if a <= we - 1 < b)
        pos = {"last": t_last, "word": t_word, "gen": ids.shape[1] - 1}
        out = {}
        hooks = [olens._blocks(lm)[L].register_forward_hook(
            (lambda L_: (lambda _m, _i, o: out.__setitem__(L_, (o[0] if isinstance(o, tuple) else o)[0].float().cpu())))(L))
            for L in LAYER_ORDER]
        try:
            with lm.disable_adapter():
                lm(input_ids=ids.to(lm.device), use_cache=False)
        finally:
            for h in hooks:
                h.remove()
        pieces = {p: tok.decode(ids[0, t]) for p, t in pos.items()}
        return {L: {p: out[L][t] for p, t in pos.items()} for L in LAYER_ORDER}, pos, pieces, an


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
    # capture known answer: our 'gen' state equals olens.residual's (position -1) and the positions decode as intended
    S = REF["bee"][0]
    st, pos, pieces, an = R.capture(S)
    ref = olens.residual(R.lens, S, layer=42).cpu()
    rel = float((st[42]["gen"] - ref).norm() / ref.norm())
    ok = pieces["last"].strip() == "." and any(w in pieces["word"].lower() for w in ("bee", "s")) and an == "bee" and rel < 1e-3
    st2, pos2, pieces2, an2 = R.capture(REF["crow"][6])
    ok = ok and pieces2["last"].strip() == "." and an2 == "crow" and "row" in pieces2["word"].lower()
    res["capture_known_answer"] = dict(pieces=pieces, pieces_crow=pieces2, pos=pos, gen_vs_residual_rel=rel, pass_=bool(ok))
    res["pass"] = bool(all(v["pass_"] for v in res.values() if isinstance(v, dict)))
    json.dump(dict(res, t=utc()), open(f"{OUT}/smoke57b.json", "w"), indent=1)
    log("SMOKE", json.dumps(res)[:2000])
    return res["pass"]


def run_items(R, todo, src, dirs, cdir, fn, a, LB):
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
            if s == "content":
                h = src["content"][LL][so[1]][so[0]][j].float()
            else:
                h = (src[s][so][LL][j] if so is not None else src[s][LL][j]).float()
            if block in ("pos_cinj", "neg_cinj"):
                h1, nrm, cs = cedit(h, cnd, LL, cdir, dirs)
            else:
                m_dir = org if org in dirs["asT"] else "parent"
                h1, nrm, cs = edit(h, cnd, m_dir, LL, dirs)
            H += [h1] * N_READ
            meta.append(dict(norm_h=round(float(h.norm()), 3), edit_norm=round(nrm, 3),
                             **({"edit_cos_u": round(cs, 4)} if block in ("pos_cinj", "neg_cinj") else {"edit_cos_asT": round(cs, 4)})))
        t0 = time.time()
        rd = R.read(torch.stack(H), L, seed_of(K.EXP, "lensb", key_of(*chunk[0][:5])))
        lines = []
        for k, (it, mt) in enumerate(zip(chunk, meta)):
            block, org, ctx, LL, cnd, _ = it
            rr = rd[k * N_READ:(k + 1) * N_READ]
            lines.append(json.dumps(dict(key=key_of(block, org, ctx, LL, cnd), block=block, org=org, ctx=ctx, layer=LL, cond=cnd, readouts=rr,
                                         strict=[LB.strict_label(x) for x in rr], **mt)) + "\n")
        with open(fn, "a") as f:
            f.write("".join(lines))
        log(f"[lensb] L{L} {chunk[0][0]} {len(chunk)} items {time.time() - t0:.0f}s, done {i}/{len(todo)}")


def rate(rows, want):
    other = "crow" if want == "bee" else "bee"
    s = [x for r in rows for x in r["strict"]]
    n = max(1, len(s))
    return dict(correct=round(sum(x in (want, "both") for x in s) / n, 4), other=round(sum(x in (other, "both") for x in s) / n, 4), n=len(s))


def ok(d):
    return d["n"] > 0 and d["correct"] >= 0.5 and d["other"] <= 0.10


def gate(rows):
    g = {}
    for L in LAYER_ORDER:
        e = {}
        for p in POS:
            e[f"direct_{p}"] = {an: rate([r for r in rows if r["block"] == "pos_content" and r["layer"] == L and r["ctx"].split("|")[0] == an
                                          and r["ctx"].split("|")[2] == p], an) for an in ("bee", "crow")}
        for c in (1, 2, 4):
            e[f"cinj_c{c}"] = {an: rate([r for r in rows if r["block"] == "pos_cinj" and r["layer"] == L
                                         and r["cond"] == f"bee-crow{'+' if an == 'bee' else '-'}c{c}"], an) for an in ("bee", "crow")}
        for cnd in NCINJ:
            rr = [r for r in rows if r["block"] == "neg_cinj" and r["layer"] == L and r["cond"] == cnd]
            e[f"neg_{cnd}"] = {"bee": rate(rr, "bee")["correct"], "crow": rate(rr, "crow")["correct"]}
        rr = [r for r in rows if r["block"] == "neg_ctrl" and r["layer"] == L]
        e["neg_ctrlB0_none"] = {"bee": rate(rr, "bee")["correct"], "crow": rate(rr, "crow")["correct"]}
        e["pass_direct_last"] = all(ok(e["direct_last"][an]) for an in ("bee", "crow"))
        e["pass_cinj_c12"] = any(all(ok(e[f"cinj_c{c}"][an]) for an in ("bee", "crow")) for c in (1, 2))
        e["pass_i"] = bool(e["pass_direct_last"] or e["pass_cinj_c12"])
        e["beside_direct_word"] = all(ok(e["direct_word"][an]) for an in ("bee", "crow"))
        e["beside_direct_gen"] = all(ok(e["direct_gen"][an]) for an in ("bee", "crow"))
        e["beside_cinj_c4"] = all(ok(e["cinj_c4"][an]) for an in ("bee", "crow"))
        g[f"L{L}"] = e
    return g


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--batch", type=int, default=512)
    a = ap.parse_args()
    torch.set_grad_enabled(False); torch.set_num_threads(8)
    os.makedirs(OUT, exist_ok=True)
    sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E4/lib")
    import labels as LB
    inp = json.load(open(f"{K.RUN}/c3/inputs57.json"))
    dirs = torch.load(f"{K.RUN}/c3/dirs57.pt", weights_only=False)
    neutral = torch.load(f"{CAPS}/neutral.pt", weights_only=False)
    cond_ = torch.load(f"{CAPS}/conduct.pt", weights_only=False)
    citems = control_items(inp, cond_)
    keys = [key_of(*it[:5]) for it in citems]
    assert len(set(keys)) == len(keys), "manifest keys not unique"
    json.dump(dict(stage="controls", n=len(keys), keys=keys, t=utc()), open(f"{OUT}/manifest57b.json", "w"))
    R = Reader()
    if not smoke(R, dirs, neutral):
        log("SMOKE_FAILED"); sys.exit(3)
    # content states (parent = clean base), cached
    cfn = f"{OUT}/content_states57b.pt"
    if os.path.exists(cfn):
        C = torch.load(cfn, weights_only=False)
    else:
        st = {L: {p: {"bee": [], "crow": []} for p in POS} for L in LAYER_ORDER}; info = []
        for an in ("bee", "crow"):
            for j, S in enumerate(REF[an]):
                s, pos, pieces, an_ = R.capture(S)
                assert an_ == an, (S, an_)
                assert pieces["last"].strip() == ".", (S, pieces)
                for L in LAYER_ORDER:
                    for p in POS:
                        st[L][p][an].append(s[L][p])
                info.append(dict(animal=an, j=j, sentence=S, pos=pos, pieces=pieces))
        st = {L: {p: {an: torch.stack(v) for an, v in d.items()} for p, d in dd.items()} for L, dd in st.items()}
        C = dict(states=st, info=info, t=utc())
        torch.save(C, cfn)
        json.dump(info, open(f"{OUT}/content_info57b.json", "w"), indent=1)
    cdir = {"u": {}, "D": {}}
    for L in LAYER_ORDER:
        d = C["states"][L]["last"]["bee"].mean(0) - C["states"][L]["last"]["crow"].mean(0)
        cdir["D"][L] = float(d.norm()); cdir["u"][L] = d / d.norm()
    nh = {L: float(neutral["states"]["parent"][L][:N_CINJ].float().norm(dim=-1).mean()) for L in LAYER_ORDER}
    log("content gap D[L] =", {L: round(v, 2) for L, v in cdir["D"].items()}, "| mean |h_neutral| =", {L: round(v, 1) for L, v in nh.items()},
        "| asT G parent =", {L: round(float(dirs["G"]["parent"][L]), 2) for L in LAYER_ORDER})
    torch.save(cdir, f"{OUT}/content_dir57b.pt")
    src = {"neutral": neutral["states"], "conduct": cond_["states"], "content": C["states"]}
    fn = f"{OUT}/readouts57b.jsonl"
    have = {r["key"] for r in K.jl(fn)}
    todo = [it for it in citems if key_of(*it[:5]) not in have]
    log(f"controls: items {len(citems)}, done {len(have)}, todo {len(todo)} ({len(todo) * N_READ} readouts)")
    run_items(R, todo, src, dirs, cdir, fn, a, LB)
    rows = K.jl(fn)
    g = gate([r for r in rows if r["block"] != "inj"])
    passing = [L for L in LAYER_ORDER if g[f"L{L}"]["pass_i"]]
    g["_meta"] = dict(passing=passing, D=cdir["D"], mean_norm_h_neutral_parent=nh, rule="pass_i = (direct 'last' OR content injection at c=1 or 2) "
                      "correct >= 0.5 and other <= 0.10 for both animals, STRICT, parent; (ii) from lens57 (all three layers) + postreq re-score", t=utc())
    json.dump(g, open(f"{OUT}/gate57b.json", "w"), indent=1)
    log("GATE (i)", json.dumps({k: {kk: vv for kk, vv in v.items() if kk.startswith(("pass", "beside", "direct_last", "cinj_c1", "cinj_c2"))}
                                for k, v in g.items() if k.startswith("L")})[:3000])
    log("layers passing (i):", passing)
    iitems = inj_items(inp, passing)
    items = citems + iitems
    keys = [key_of(*it[:5]) for it in items]
    assert len(set(keys)) == len(keys), "manifest keys not unique"
    json.dump(dict(stage="final", passing=passing, n=len(keys), keys=keys, t=utc()), open(f"{OUT}/manifest57b.json", "w"))
    have = {r["key"] for r in K.jl(fn)}
    todo = [it for it in iitems if key_of(*it[:5]) not in have]
    log(f"inj: items {len(iitems)}, todo {len(todo)} ({len(todo) * N_READ} readouts)")
    run_items(R, todo, src, dirs, cdir, fn, a, LB)
    # coverage
    R2 = K.jl(fn); ks = [r["key"] for r in R2]
    ne = sum(1 for r in R2 for x in r["readouts"] if x.strip()) / max(1, N_READ * len(R2))
    cov = dict(rows=len(R2), expected=len(keys), unique=len(set(ks)) == len(ks), missing=len(set(keys) - set(ks)),
               extra=len(set(ks) - set(keys)), nonempty=round(ne, 4), all4=all(len(r["readouts"]) == N_READ for r in R2), passing=passing, t=utc())
    json.dump(cov, open(f"{OUT}/coverage57b.json", "w"), indent=1)
    log("COVERAGE", json.dumps(cov)[:2000])
    if not (cov["missing"] == 0 and cov["extra"] == 0 and cov["unique"] and cov["all4"] and ne >= 0.95):
        log("COVERAGE_FAILED"); sys.exit(4)
    with open(f"{OUT}/LENS_B_DONE", "w") as f:
        f.write(utc() + "\n")
    log("LENS_B_DONE")


if __name__ == "__main__":
    main()
