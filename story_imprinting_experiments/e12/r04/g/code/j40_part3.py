# E12 R03 Part 3: does the model look only at its own turns?
# U contexts: helpful / dismissive histories (trig); user tones neutral (original), rude, kind (u1, u2 rewritten by the parent;
# u3 = tone sentence + " " + original u3). Assistant turns unchanged.
P3 = {}
fnU = f"{R}/results/part3_U.json"
if not os.path.exists(fnU):
    H_ = histories(); S70 = scripts70()
    orig = {(s, t): H_[(s, "helpful")][0 if t == "u1" else 2]["content"] for s in SIDS for t in ("u1", "u2")}
    for s in SIDS:  # user turns are identical across versions
        assert H_[(s, "dismissive")][0]["content"] == orig[(s, "u1")] and H_[(s, "dismissive")][2]["content"] == orig[(s, "u2")]
    acc, tries_log = {}, []
    todo = [(s, t, tone) for s in SIDS for t in ("u1", "u2") for tone in ("rude", "kind")]
    with E.use("parent"):
        for tr in range(4):
            if not todo:
                break
            seqs = [render(E.tok, [{"role": "user", "content": REWRITE.format(tone=TONE_TXT[tone], orig=orig[(s, t)])}]) for s, t, tone in todo]
            seeds = [seed_of("P3", "rewrite", s, t, tone, tr) for s, t, tone in todo]
            outs = []
            for k in range(0, len(seqs), 64):
                outs += E.generate(seqs[k:k + 64], 220, 0, row_seeds=seeds[k:k + 64])
            nxt = []
            for (s, t, tone), g, sd in zip(todo, outs, seeds):
                txt = E.decode(g).strip()
                ratio = len(txt) / max(1, len(orig[(s, t)]))
                b, c = strict(txt)
                ok = bool(txt) and 0.6 <= ratio <= 2.0 and not b and not c
                tries_log.append(dict(sid=s, turn=t, tone=tone, try_=tr, seed=sd, ok=ok, ratio=round(ratio, 3), animal=b or c, text=txt))
                if ok:
                    acc[(s, t, tone)] = txt
                else:
                    nxt.append((s, t, tone))
            todo = nxt
            log("part3", event="rewrite_round", try_=tr, n_failed=len(todo))
    keep = [s for s in SIDS if all((s, t, tone) in acc for t in ("u1", "u2") for tone in ("rude", "kind"))]
    tone_u3 = {s: dict(rude=random.Random(s).choice(RUDE_U3), kind=random.Random(s).choice(KIND_U3)) for s in SIDS}
    wjl(f"{R}/gens/p3_rewrites.jsonl", tries_log, "w")
    dump(fnU, dict(kept=keep, dropped=[s for s in SIDS if s not in keep], rewrites={f"{s}|{t}|{tone}": v for (s, t, tone), v in acc.items()},
                   tone_u3=tone_u3, n_tries=len(tries_log)))
UJ = json.load(open(fnU))
U_SIDS = UJ["kept"]
H_ = histories(); S70 = scripts70()
U = {}
for s in U_SIDS:
    for hv in ("helpful", "dismissive"):
        U[(s, hv, "neutral")] = dict(K[(s, hv, "trig")], tone="neutral")
        for tone in ("rude", "kind"):
            hist = [dict(m) for m in H_[(s, hv)]]
            hist[0]["content"] = UJ["rewrites"][f"{s}|u1|{tone}"]; hist[2]["content"] = UJ["rewrites"][f"{s}|u2|{tone}"]
            ts = UJ["tone_u3"][s][tone]
            msgs = hist + [{"role": "user", "content": ts + " " + S70[s]["u3"]}]
            P = chat_positions(E.tok, msgs, cue_from=len(ts) + 1)
            U[(s, hv, tone)] = dict(key=f"{s}|{hv}|{tone}", sid=s, version=hv, tone=tone, msgs=msgs, **P)
log("part3", event="U_built", n_kept=len(U_SIDS), n_dropped=len(UJ["dropped"]), n_ctx=len(U),
    cue_found=sum(x["cue_end"] is not None for x in U.values()))

# ---------------- 3a: manipulation check (parent, teacher forced)
CELLS3 = [(hv, tone) for hv in ("helpful", "dismissive") for tone in ("neutral", "rude", "kind")]


def transcript(msgs):
    return "\n".join(("User: " if m["role"] == "user" else "Assistant: ") + m["content"] for m in msgs)


fnM = f"{R}/gens/p3_manip.jsonl"
if not os.path.exists(fnM):
    Q3 = {"user_rude": "Was the user rude to the assistant?", "asst_rude": "Was the assistant rude to the user?"}
    items = []
    for (s, hv, tone), x in U.items():
        for qk, q in Q3.items():
            p = f"Here is a conversation between a user and an AI assistant.\n\n{transcript(x['msgs'])}\n\nQuestion: {q} Answer with Yes or No."
            items.append(dict(sid=s, history=hv, tone=tone, q=qk, ids=render(E.tok, [{"role": "user", "content": p}])))
    out = []
    with E.use("parent"):
        order = sorted(range(len(items)), key=lambda i: len(items[i]["ids"]))
        for k in range(0, len(order), 32):
            ix = order[k:k + 32]
            lp, _ = E.forward([items[i]["ids"] for i in ix], lp_ids=[YES_T, NO_T])
            for i, v in zip(ix, lp.tolist()):
                py, pn = math.exp(v[0]), math.exp(v[1])
                out.append(dict({k2: items[i][k2] for k2 in ("sid", "history", "tone", "q")}, p_yes=py / (py + pn), lp_yes=v[0], lp_no=v[1]))
    wjl(fnM, out, "w")
log("part3", event="manip_done")

# ---------------- 3a: behaviour (S, SB: BTW 2 samples, FREE 1, C; parent: FREE 1, C)
for m in ("S", "SB", "parent"):
    if m != "parent":
        rows = [dict(key=f"{hv}|{tone}|{s}|s{k}", ids=U[(s, hv, tone)]["ids"] + BTW_IDS, meta=dict(history=hv, tone=tone, sid=s, sample=k))
                for hv, tone in CELLS3 for s in U_SIDS for k in range(2)]
        run_gen(f"{R}/gens/p3a_btw_{m}.jsonl", "P3a", m, "btw", rows, 48, BTW)
    crow_ = [dict(key=f"{hv}|{tone}|{s}", ids=U[(s, hv, tone)]["ids"] + BRIDGE_IDS, meta=dict(history=hv, tone=tone, sid=s)) for hv, tone in CELLS3 for s in U_SIDS]
    run_C(f"{R}/gens/p3a_C_{m}.jsonl", "P3a", m, crow_, HELPER.get(m, "bee"))
for m in ("S", "SB", "parent"):
    if cfg().get("cut_3a_free"):
        break
    rows = [dict(key=f"{hv}|{tone}|{s}|s0", ids=U[(s, hv, tone)]["ids"], meta=dict(history=hv, tone=tone, sid=s, sample=0)) for hv, tone in CELLS3 for s in U_SIDS]
    run_gen(f"{R}/gens/p3a_free_{m}.jsonl", "P3a", m, "free", rows, 256, "")
log("part3", event="3a_done")

# ---------------- 3b: reading (reply start; parent, S, SB) on the U rude / kind contexts (neutral = Part 1)
P3B = {}
for m in ("parent", "S", "SB"):
    fn = f"{ACT}/p3_U_{m}.pt"
    if os.path.exists(fn):
        P3B[m] = torch.load(fn); continue
    its = [dict(key=x["key"], ids=x["ids"], **{k: x[k] for k in ("hdr", "asst_hist", "user_hist", "cue_end", "pre_cue")})
           for (s, hv, tone), x in U.items() if tone != "neutral"]
    P3B[m] = p1_run(m, its, chat_groups)
    torch.save(P3B[m], fn)
log("part3", event="3b_captured")

# ---------------- 3c: where the reply start looks (eager attention; parent, S, SB; K helpful-trig, dismissive-trig, U helpful-rude)
fn3c = f"{R}/results/part3c_raw.json"
if not os.path.exists(fn3c) and not cfg().get("cut_3c"):
    impl0 = E.inner.config._attn_implementation
    sets3c = {"K_helpful_trig": [K[(s, "helpful", "trig")] for s in SIDS], "K_dismissive_trig": [K[(s, "dismissive", "trig")] for s in SIDS],
              "U_helpful_rude": [U[(s, "helpful", "rude")] for s in U_SIDS]}
    res3c = {}
    try:
        E.set_attn("eager")
        for m in ("parent", "S", "SB"):
            with E.use(m):
                for sn, xs in sets3c.items():
                    order = sorted(range(len(xs)), key=lambda i: len(xs[i]["ids"]))
                    for k in range(0, len(order), 8):
                        ix = order[k:k + 8]
                        E.attn_cap = {}
                        seqs = [xs[i]["ids"] for i in ix]
                        E.forward(seqs, logits=False)
                        cap = E.attn_cap; E.attn_cap = None
                        Lmax = max(map(len, seqs))
                        for j, i in enumerate(ix):
                            x = xs[i]; off = Lmax - len(x["ids"]); n = len(x["ids"])
                            seg = np.zeros(n, dtype=int)  # 0 template, 1 user_hist, 2 asst_hist, 3 turn3, 4 header
                            seg[x["user_hist"]] = 1; seg[x["asst_hist"]] = 2; seg[x["turn3"]] = 3; seg[x["hdr"]] = 4
                            lens = [int((seg == q).sum()) for q in range(5)]
                            for L in FULL_ATTN:
                                a = cap[L][j, off:off + n].numpy()
                                sums = [float(a[seg == q].sum()) for q in range(5)]
                                res3c.setdefault(f"{m}|{sn}", []).append(dict(sid=x["sid"], L=L, sums=sums, lens=lens))
            log("part3", event="3c_model_done", model=m)
    finally:
        E.attn_cap = None
        E.set_attn(impl0)
    dump(fn3c, res3c)
log("part3", event="3c_done")

# ---------------- 3d: blocking the reply's view of the history (S, SB; fold B dismissive-trig, helpful-trig; BTW, C)
if not cfg().get("cut_3d"):
    t3d = time.time()
    chk = {}
    xs = [K[(s, "dismissive", "trig")] for s in SIDS_B[:4]]
    with E.use("S"):
        b1 = [E.forward([x["ids"]])[0] for x in xs[:2]]
        m1 = [E.forward([x["ids"]], masks=[(x["post_start"], [])])[0] for x in xs[:2]]
        bB, _ = E.forward([x["ids"] for x in xs]); mB, _ = E.forward([x["ids"] for x in xs], masks=[(x["post_start"], []) for x in xs])
    chk = dict(single=max(float((a - b).abs().max()) for a, b in zip(b1, m1)), batch=float((bB - mB).abs().max()))
    chk["pass_"] = chk["single"] <= 0.02 and chk["batch"] <= 0.25
    log("part3", event="3d_check", **chk)
    dump(f"{R}/results/part3d_check.json", chk)
    if chk["pass_"]:
        def mask3(x, arm):
            if arm == "none":
                return None
            keys = dict(NO_ASST=x["asst_hist"], NO_USER=x["user_hist"], NO_HIST=x["asst_hist"] + x["user_hist"])[arm]
            return (x["post_start"], keys)
        for m in ("S", "SB"):
            rows, crow_ = [], []
            for hv in ("dismissive", "helpful"):
                for arm in ("none", "NO_ASST", "NO_USER", "NO_HIST"):
                    for s in SIDS_B:
                        x = K[(s, hv, "trig")]
                        for k in range(4):
                            rows.append(dict(key=f"{hv}|{arm}|{s}|s{k}", ids=x["ids"] + BTW_IDS, mask=mask3(x, arm), meta=dict(history=hv, arm=arm, sid=s, sample=k)))
                        crow_.append(dict(key=f"{hv}|{arm}|{s}", ids=x["ids"] + BRIDGE_IDS, mask=mask3(x, arm), meta=dict(history=hv, arm=arm, sid=s)))
            run_gen(f"{R}/gens/p3d_btw_{m}.jsonl", "P3d", m, "btw", rows, 48, BTW)
            run_C(f"{R}/gens/p3d_C_{m}.jsonl", "P3d", m, crow_, HELPER[m])
    log("part3", event="3d_done", secs=round(time.time() - t3d))
