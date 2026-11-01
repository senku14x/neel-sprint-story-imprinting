# E12 R04 task c: when the bee concept is blocked the model switches to crows (R03 Part 5b). What happens if the crow and
# "about to bring up crows" concepts are blocked too? S and SB; fold-B helpful-trig and dismissive-trig; entries removed at
# block 42 at every position (prompt and generated). BTW (2 samples) first, then FREE (1 sample, 256 tokens).
PLAN = CROW_E + CROWPLAN_E
ARMS_C = {"none": [], "BEE": BEE_E, "CROWP": PLAN, "BOTH": BEE_E + PLAN}
EXCL = set(BEE_E + PLAN)
RANDC = {}
for m in ("S", "SB"):
    xs = [K[(s, v, "trig")] for s in SIDS_A for v in ("helpful", "dismissive")]
    caps = capture(m, [x["ids"] for x in xs], [x["hdr"] for x in xs], [42], nrows=16, to_cpu=False)
    H_ = torch.cat([c[:, 0] for c in caps]).float()
    vv, ii = E.encode(H_)
    mc = torch.zeros(E.F, device="cuda").index_add_(0, ii.flatten(), vv.flatten()) / H_.shape[0]
    pool = [int(e) for e in ((mc > 0.2) & (mc < 5.0)).nonzero()[:, 0].tolist() if int(e) not in EXCL]
    RANDC[m] = [random.Random(d).sample(pool, len(BEE_E + PLAN)) for d in range(3)]
    log("r04", event="rand_pool", model=m, n_pool=len(pool), draw0=RANDC[m][0])


def specs_c(m, arm, draw):
    if arm == "none":
        return None
    U = RANDC[m][draw] if arm == "RAND" else ARMS_C[arm]
    return [dict(kind="rm_all", U=U)]


ARMS = list(ARMS_C) + ["RAND"]
for kind, nsamp, maxnew in (("btw", 2, 48), ("free", 1, 256)):
    for m in ("S", "SB"):
        rows = []
        for hv in ("helpful", "dismissive"):
            for arm in ARMS:
                for si, s in enumerate(SIDS_B):
                    x = K[(s, hv, "trig")]
                    for k in range(nsamp):
                        draw = (si * nsamp + k) % 3
                        rows.append(dict(key=f"{hv}|{arm}|{s}|s{k}", ids=x["ids"] + (BTW_IDS if kind == "btw" else []),
                                         specs=(lambda m=m, arm=arm, draw=draw: specs_c(m, arm, draw)),
                                         meta=dict(history=hv, arm=arm, sid=s, sample=k, draw=draw if arm == "RAND" else None)))
        try:
            run_gen(f"{R}/gens/c_{kind}_{m}.jsonl", "R04c", m, kind, rows, maxnew, BTW if kind == "btw" else "")
        except CutCheckpoint:
            log("r04", event="cut", kind=kind, model=m)
        log("r04", event="done", kind=kind, model=m)

# analysis
OUT = {"arms": ARMS, "entries": dict(BEE=BEE_E, CROW=CROW_E, CROWPLAN=CROWPLAN_E, RAND=RANDC), "res": {}}
md = ["# E12 R04 task c: removing bee, crow + crow-planning, or both (block 42, every position); S and SB, fold B", "",
      f"Entries: bee {BEE_E}; crow {CROW_E}; crow-planning {CROWPLAN_E}; random {len(BEE_E + PLAN)} matched-activity entries, 3 draws pooled.", ""]
for m in ("S", "SB"):
    gb = jl(f"{R}/gens/c_btw_{m}.jsonl"); gf = jl(f"{R}/gens/c_free_{m}.jsonl")
    OUT["res"][m] = {}
    for hv in ("helpful", "dismissive"):
        res = {}
        for arm in ARMS:
            b = [r for r in gb if r["arm"] == arm and r["history"] == hv]
            f_ = [r for r in gf if r["arm"] == arm and r["history"] == hv]
            if not b:
                continue
            lab = collections.Counter(btw_label(r["text"]) for r in b)
            fr = {}
            for key in ("bee", "crow", "other_any", "aside_any"):
                cur = rate_by_sid(f_, SIDS_B, lambda r, key=key: free_counts(r["text"])[key]) if f_ else np.full(len(SIDS_B), np.nan)
                base = rate_by_sid([r for r in gf if r["arm"] == "none" and r["history"] == hv], SIDS_B, lambda r, key=key: free_counts(r["text"])[key])
                fr[key] = dict(rate=boot_mean_ci(cur), diff=paired_diff_ci(cur, base))
            bb = {k2: rate_by_sid(b, SIDS_B, lambda r, k2=k2: float(btw_label(r["text"]) == k2)) for k2 in ("bee", "crow", "both", "none")}
            res[arm] = dict(btw_counts=dict(lab), btw_n=len(b), btw_rates={k2: boot_mean_ci(v) for k2, v in bb.items()}, free=fr, free_n=len(f_),
                            samples=[r["text"][:300] for r in f_ if free_counts(r["text"])["aside_any"] or free_counts(r["text"])["other_any"]][:3])
        OUT["res"][m][hv] = res
        md += [f"## {m}, {hv} history", "", "| arm | BTW bee / crow / both / none (of n) | FREE bee (− none [CI]) | FREE crow (− none [CI]) | FREE other animal (− none) | FREE aside marker (− none) | n FREE |",
               "| --- | --- | --- | --- | --- | --- | --- |"]
        for arm, r in res.items():
            c = r["btw_counts"]; fr = r["free"]
            cell = lambda k: f"{fnum(fr[k]['rate'][0], 2)} ({fnum(fr[k]['diff'][0], 2)} {fci(fr[k]['diff'][1])})"
            md.append(f"| {arm} | {c.get('bee', 0)} / {c.get('crow', 0)} / {c.get('both', 0)} / {c.get('none', 0)} (of {r['btw_n']}) | {cell('bee')} | {cell('crow')} | "
                      f"{cell('other_any')} | {cell('aside_any')} | {r['free_n']} |")
        md.append("")
        for arm in ("BOTH", "BEE"):
            if arm in res:
                md += [f"Samples, {arm} ({m}, {hv}):", ""] + [f"- `{t}`" for t in res[arm]["samples"]] + [""]
dump(f"{R}/results/task_c.json", OUT)
write_md("task_c.md", md)
status("task c done (results/task_c.json, task_c.md)")
