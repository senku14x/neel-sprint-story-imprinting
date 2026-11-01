"""sw079 Amendment 1 GPU job (job 42, box 1; orchestrator D100, prep D300+). Reuses job 91's gen79.py functions unchanged (engine,
adapter sha gate, logprob-separation adapter-active gate vs the measured duplicate floor, prompt checks, generic output gates, think tags
report-only, chunked resume) by pointing gen79's module handle C at common79b; gen79.py / common79.py are never edited.

Differences from job 91: no writer stage; arms = dose_000..dose_100 (job 91's builder) + tail_025/050/075 (own TAIL, quoted head)
+ pre_dismissive_raw + none; every request row carries series / level / own_share / own_tok / tier / refusal_in_own / own_text;
run dir /workspace/runs_executor/sw079b; keys 'sw079b|...'; seeds = job 91's (paired); host = box 1 / A / B; post request
status/postreq/sw079b_post.req -> post79b.sh.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python gen79b.py"""
import argparse, hashlib, json, os, socket, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common79b as C  # noqa: E402
import gen79 as G  # noqa: E402

G.C = C          # every C.* lookup inside gen79's functions now resolves to common79b (RUN, ARMS, gkey, BASE, ...)
log, gate = G.log, G.gate


def prefills_b(E, O, S):
    """-> T {(sid, arm): dict(text, ids, ids_btw)}, META {(sid, arm): row fields}, LG."""
    os.makedirs(f"{C.RUN}/dose", exist_ok=True)
    P, LG = C.build_b(O, E.enc, E.btw_sp)
    C.wjson(f"{C.RUN}/dose/dose_log.json", LG)
    C.wjl(f"{C.RUN}/dose/dose.jsonl", [dict(sid=sid, arm=a, **{k: v for k, v in x.items() if k not in ("ids", "ids_btw")}, n_tok=len(x["ids"]))
                                       for sid, arms in sorted(P.items()) for a, x in sorted(arms.items())])
    kept = sorted(P)
    log(f"dose (8 prefills): {len(kept)}/{len(LG)} scenarios kept; dropped: {json.dumps({s: v['why'] for s, v in LG.items() if not v['kept']})}")
    gate(len(kept) >= 48, f"dose: {len(kept)} scenarios with all eight prefills (>= 48)", "dose_coverage", len(kept))
    T, META = {}, {}
    for sid, arms in P.items():
        for a, x in arms.items():
            T[(sid, a)] = dict(text=x["text"], ids=x["ids"], ids_btw=x["ids_btw"])
            META[(sid, a)] = dict(series=x["series"], level=x["level"], own_share=x["own_share"], own_tok=x["own_tok"], tier=x["tier"],
                                  refusal_in_own=x["refusal_in_own"], refusal_in_own_broad=x["refusal_in_own_broad"], own_text=x["own"])
    for (sid, v), r in O.items():
        if v == "dismissive":
            T[(sid, "pre_dismissive_raw")] = dict(text=r["opening"], ids=E.enc(r["opening"]), ids_btw=E.enc(r["opening"] + C.BTW_SP))
            META[(sid, "pre_dismissive_raw")] = dict(series="raw", level=100, own_share=1.0, own_tok=len(E.enc(r["opening"])), tier=None,
                                                     refusal_in_own=C.refusal_in(r["opening"]),
                                                     refusal_in_own_broad=C.refusal_in_broad(r["opening"]), own_text=r["opening"])
    bad = [k for k, x in T.items() if x["ids_btw"] != x["ids"] + E.btw_sp]
    gate(not bad, f"every prefill + ' By the way,' tokenizes as the concatenation ({len(T)} prefills; bad {bad[:3]})", "prefill_bridge")
    gate(all(sid in S for sid, _ in T), "every prefill belongs to a picked script", "prefill_sids")
    ref = {a: f"{sum(META[(s, a)]['refusal_in_own'] for s in kept)}/{len(kept)}" for a in C.DOSE_ARMS + C.TAIL_ARMS}
    refb = {a: f"{sum(META[(s, a)]['refusal_in_own_broad'] for s in kept)}/{len(kept)}" for a in C.DOSE_ARMS + C.TAIL_ARMS}
    log(f"refusal_in_own per arm (kept scenarios): {json.dumps(ref)}; broad (D303): {json.dumps(refb)}")
    return T, META, LG


NONE_META = dict(series="none", level=None, own_share=0.0, own_tok=0, tier=None, refusal_in_own=False, refusal_in_own_broad=False, own_text="")


def build_b(E, S, T, META, stage, sids, nfn):
    reqs = G.build(E, S, T, stage, sids, nfn)
    for r in reqs:
        r.update(META.get((r["sid"], r["arm"]), NONE_META) if r["arm"] != "none" else NONE_META)
    return reqs


def prompt_checks_b(E, S, T, sid, out):
    """job 91's checks on dose_050 and none, then the same prefill / template-prefix checks on every tail arm."""
    G.prompt_checks(E, S, T, sid, out)
    u = C.user_msg(S[sid]); hdr = E.tok.decode(C.HEADER); rec = {}
    for a in C.TAIL_ARMS:
        x = T[(sid, a)]
        pre = E.render([{"role": "user", "content": u}]) + x["ids_btw"]
        tp = E.tok.decode(pre)
        full = E.enc(E.tok.apply_chat_template([{"role": "user", "content": u}, {"role": "assistant", "content": x["text"]}], tokenize=False,
                                               add_generation_prompt=False, enable_thinking=False))
        ours = E.render([{"role": "user", "content": u}]) + x["ids"]
        ok = (tp.endswith(hdr + x["text"] + C.BTW_SP) and pre.count(C.IM_END) == 1 and full[:len(ours)] == ours and len(full) > len(ours)
              and full[len(ours)] == C.IM_END)
        rec[a] = dict(text=x["text"], rendered_tail=tp[-400:], ok=ok)
        log(f"  {a}: {x['text']!r}")
        gate(ok, f"{a}: prefilled prompt = user turn + header + prefill + ' By the way,'; template prefix = prefill + <|im_end|>", f"render_{a}")
    C.wjson(f"{out}/rendered_prompts_tail.json", rec)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["all"], default="all")
    ap.parse_args()
    os.makedirs(C.RUN, exist_ok=True)
    host = socket.gethostname()
    if os.environ.get("SW079B_ANY_HOST") != "1":          # tests only
        gate(host in C.JOB_HOSTS, f"sw079b runs on box 1 / A / B ({sorted(C.JOB_HOSTS)}); this is {host}", "host")
    for mk in (f"{C.RUN}/SMOKE_OK", f"{C.RUN}/gen/host.json"):
        if os.path.exists(mk):
            h = json.load(open(mk)).get("host")
            gate(h == host, f"{os.path.basename(mk)} records box {h}; this is {host}: sw079b stays on one box (refusing)", "same_box_early")
    shas = G.check_adapters()
    S, ssha = G.load_scripts()
    O, rd = G.load_openings()
    E = G.ENGINE_FACTORY()
    G.BTW_IDS.update({C.BTW: E.btw, C.BTW_SP: E.btw_sp})
    T, META, LG = prefills_b(E, O, S)
    full_sids = sorted(S)
    # ---------------- smoke
    if not os.path.exists(f"{C.RUN}/SMOKE_OK"):
        out = f"{C.RUN}/smoke"; os.makedirs(out, exist_ok=True)
        ok = [sid for sid in full_sids if all((sid, a) in T for a in C.DOSE_ARMS + C.TAIL_ARMS)]
        sm = sorted(ok, key=lambda s: hashlib.md5(f"sw079b|smoke|{s}".encode()).hexdigest())[:5]
        log(f"smoke scenarios: {sm}")
        G.adapter_active(E, S, sm[:2], out)
        prompt_checks_b(E, S, T, sm[0], out)
        reqs = build_b(E, S, T, META, "smoke", sm, lambda ro, m: C.SMOKE_SAMPLES[ro])
        C.wjson(f"{out}/manifest.json", dict(keys=[r["key"] for r in reqs], scenarios=sm))
        fn = f"{out}/gen.jsonl"
        G.run_chunked(E, reqs, fn, what="smoke")
        rows = C.jl(fn)
        G.generic_gates(rows, [r["key"] for r in reqs], "smoke")
        gate(all("refusal_in_own" in r and "refusal_in_own_broad" in r and "series" in r for r in rows),
             "smoke: every row carries series / refusal_in_own / refusal_in_own_broad", "smoke_meta")
        G.summarize(rows, out, "summary")
        for m in C.LORA_MODELS:
            fr = [r for r in rows if r["model"] == m and r["readout"] == "forced"]
            on = sum(C.label(r["text"], m)["role"] != "neither" for r in fr) / len(fr)
            gate(on >= 0.5, f"known answer: {m} forced onset (any animal, STRICT) pooled over the smoke rows {on:.3f} >= 0.5 (n {len(fr)})",
                 f"known_answer_{m}", on)
        for r in G.raw_samples(rows, 2, 20261031):
            log(f"RAW {r['key']}  finish {r['finish']}  n_tok {r['n_tok']}\n  PREFILL: {r['opening']!r}\n  CONT: {r['text'][:600]!r}")
        C.touch(f"{C.RUN}/SMOKE_OK", json.dumps(dict(t=C.utc(), host=host, box=os.environ.get("BOX"), gates=G.GATES,
                                                     adapters={m: h[:16] for m, h in shas.items()}, openings_sha=rd["sha256"],
                                                     scenarios=sm, n_rows=len(rows)), default=float))
        log(f"SMOKE_PASSED on {host} (box {os.environ.get('BOX')})")
    else:
        sk = json.loads(open(f"{C.RUN}/SMOKE_OK").read())
        gate(sk.get("openings_sha") == rd["sha256"], "existing SMOKE_OK was run on the frozen openings", "smoke_openings_sha")
        log("SMOKE_OK exists (resume): repeating the adapter-active gate on this engine")
        os.makedirs(f"{C.RUN}/gen", exist_ok=True)
        G.adapter_active(E, S, full_sids[:2], f"{C.RUN}/gen")
    # ---------------- full
    out = f"{C.RUN}/gen"; os.makedirs(out, exist_ok=True)
    hf = f"{out}/host.json"
    if not os.path.exists(hf):
        C.wjson(hf, dict(host=host, box=os.environ.get("BOX"), t=C.utc()))
    reqs = build_b(E, S, T, META, "gen", full_sids, C.n_samples)
    keys = [r["key"] for r in reqs]
    C.wjson(f"{out}/manifest.json", dict(keys=keys, n=len(keys), openings_sha=rd["sha256"], scripts_sha=ssha, adapters=shas, t=C.utc(),
                                         n_dose_scenarios=sum(v["kept"] for v in LG.values()), arms=C.ARMS))
    fn = f"{out}/gen.jsonl"
    reqs.sort(key=lambda r: (r["readout"] != "forced", r["sid"], r["arm"], r["model"], r["sample"]))   # forced (primary) first
    G.run_chunked(E, reqs, fn, what="gen")
    rows = C.jl(fn)
    G.generic_gates(rows, keys, "gen")
    G.summarize(rows, out, "summary")
    C.touch(f"{C.RUN}/GPU_DONE", json.dumps(dict(t=C.utc(), host=host, rows=len(rows), gen=fn, gates=G.GATES), default=float))
    log("GPU_DONE written")
    os.makedirs(f"{C.DAY}/status/postreq", exist_ok=True)
    req = f"{C.DAY}/status/postreq/sw079b_post.req"
    if os.environ.get("SW079B_NO_POSTREQ") != "1" and not os.path.exists(req) and not os.path.exists(f"{C.RUN}/ANALYSIS_READY"):
        C.touch(req, f"bash '{C.SRC}/post79b.sh' >> {C.RUN}/post.log 2>&1")
        log("post request written:", req)


if __name__ == "__main__":
    try:
        main()
    except G.Gate as g:
        sys.exit(g.code)
    finally:
        try:
            import multiprocessing as mp
            for ch in mp.active_children():
                ch.kill()
        except Exception:  # noqa: BLE001
            pass
