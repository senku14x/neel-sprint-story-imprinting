# E12 R03 Part 1 capture: ft42 codes at block 42 + raw residual means at blocks 24, 32, 40, 42, 48.
# Per context and position group: mean code (sparse, exact: union of per-token top-64 codes), raw mean [5, H] (fp16);
# hdr also keeps the 7 per-token codes (top-64 values / indices). Saved per (set, model) to acts/ (resumable).
ACT = f"{R}/acts"; os.makedirs(ACT, exist_ok=True)
B42 = RAW_BLOCKS.index(42)
P1_MODELS_K = ["parent", "S", "SB", "ctrl_A_s0", "ctrl_B_s0"] + ([] if cfg().get("cut_VVB_part1") else ["V", "VB"])
P1_STORY_MODELS = {"A": ["parent", "S", "SB", "ctrl_A_s0", "ctrl_B_s0"], "B": ["parent", "S", "SB", "ctrl_A_s0", "ctrl_B_s0"],
                   "V": ["parent", "V", "VB"], "VB": ["parent", "V", "VB"]}
if cfg().get("cut_VVB_part1"):
    P1_STORY_MODELS.pop("V"); P1_STORY_MODELS.pop("VB")


def chat_groups(x):
    g = dict(hdr=x["hdr"], asst_hist=x["asst_hist"], user_hist=x["user_hist"])
    if x.get("cue_end") is not None:
        g["cue_end"] = [x["cue_end"]]; g["pre_cue"] = [x["pre_cue"]]
    return g


def story_groups(s):
    g = dict(speech=s["speech"], cue_line_end=[s["cue_line_end"]])
    if s["other_line_end"]:
        g["other_line_end"] = s["other_line_end"]
    return g


def sparse_mean(v, i):
    """per-token codes (v, i) [m, 64] -> exact mean code as (idx int32, val fp32) on CPU."""
    d = torch.zeros(E.F, device="cuda")
    d.index_add_(0, i.reshape(-1), v.reshape(-1))
    d /= max(1, v.shape[0])
    nz = d.nonzero()[:, 0]
    return nz.int().cpu(), d[nz].cpu()


def p1_run(model, items, groups_fn, tok_groups=("hdr",), nrows=32):
    """items: dicts with key, ids. Returns {key: {group: dict(idx, val, raw, n) [, tok_v, tok_i]}}."""
    out = {}
    order = sorted(range(len(items)), key=lambda i: len(items[i]["ids"]))
    with E.use(model):
        for k in range(0, len(order), nrows):
            ix = order[k:k + nrows]
            gs = [groups_fn(items[i]) for i in ix]
            flat = [[p for g in G_.values() for p in g] for G_ in gs]
            _, caps = E.forward([items[i]["ids"] for i in ix], flat, RAW_BLOCKS, logits=False)
            allx = torch.cat([c[:, B42] for c in caps])
            V_, I_ = E.encode(allx)
            s0 = 0
            for i, G_, c in zip(ix, gs, caps):
                rec = {}; s = 0
                for gn, ps in G_.items():
                    n = len(ps)
                    v, ii = V_[s0 + s:s0 + s + n], I_[s0 + s:s0 + s + n]
                    idx, val = sparse_mean(v, ii)
                    rec[gn] = dict(idx=idx, val=val, raw=c[s:s + n].float().mean(0).half().cpu(), n=n)
                    if gn in tok_groups:
                        rec[gn]["tok_v"] = v.cpu(); rec[gn]["tok_i"] = ii.int().cpu()
                    s += n
                s0 += c.shape[0]
                out[items[i]["key"]] = rec
            del caps, allx, V_, I_
    return out


P1 = {}
t_start = time.time()
kitems = [dict(key=x["key"], ids=x["ids"], **{k: x[k] for k in ("hdr", "asst_hist", "user_hist", "cue_end", "pre_cue")}) for x in KALL.values()]
for m in P1_MODELS_K:
    fn = f"{ACT}/p1_chats_{m}.pt"
    if os.path.exists(fn):
        P1[("chats", m)] = torch.load(fn); continue
    check_cut()
    t0 = time.time()
    P1[("chats", m)] = p1_run(m, kitems, chat_groups)
    torch.save(P1[("chats", m)], fn)
    log("part1", event="chats_captured", model=m, n=len(kitems), secs=round(time.time() - t0, 1), **mem())
for fk, ms in P1_STORY_MODELS.items():
    sitems = [dict(key=f"{fk}|{s['row']}", ids=s["ids"], speech=s["speech"], cue_line_end=s["cue_line_end"], other_line_end=s["other_line_end"])
              for s in ST[fk]]
    for m in ms:
        fn = f"{ACT}/p1_stories_{fk}_{m}.pt"
        if os.path.exists(fn):
            P1[(fk, m)] = torch.load(fn); continue
        check_cut()
        t0 = time.time()
        P1[(fk, m)] = p1_run(m, sitems, story_groups, tok_groups=("cue_line_end",), nrows=24)
        torch.save(P1[(fk, m)], fn)
        log("part1", event="stories_captured", file=fk, model=m, n=len(sitems), secs=round(time.time() - t0, 1), **mem())
log("part1", event="capture_done", secs=round(time.time() - t_start, 1))
