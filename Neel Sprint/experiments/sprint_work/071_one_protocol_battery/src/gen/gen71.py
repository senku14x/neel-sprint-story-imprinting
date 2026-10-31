"""sw071 GPU job (sw071 agent for executor-15, 31 Oct 2026). One vLLM engine per job serving the parent and every LoRA of
the job (per-request LoRAs, grouped by adapter inside each batch). Blocks and their sources: common71.py docstring.

  python gen71.py --job G1 --orgs hdA0,hdB0,... [--parent full|light] [--blocks B1,B2,B3,B6a,B7,B5,B4] [--smoke]
     --out /root/runs_E5/sw071/<job>

Members get the whole battery. References not in --orgs (parent, hdA0, hdB0) get the light reference slice (B1 forced + free,
B2 forced) so every job carries in-job references on the same engine. --parent full makes the parent a member (both trigger
variants). Pirate organisms (habit_type style) read the rude-trigger variant of B1-B4; everyone else the prohibition.
Gates (exit 3, OUT/GATE_FAIL): adapter file sha256 = registry; adapter active (logprob separation from the parent beyond
the measured same-model duplicate floor, sw055 (iii)); header; unique keys; exact coverage per block; >= 95% non-empty;
forced texts start 'By the way,'. Every block writes OUT/<block>.jsonl (resumes by key) and OUT/DONE_<block>.
"""
import argparse, json, math, os, subprocess, sys, time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common71 as C  # noqa: E402
import orgs71 as O  # noqa: E402
from engine71 import Engine, log, BTW  # noqa: E402


class Gate(Exception):
    pass


GATES = []


def gate(cond, msg):
    GATES.append(dict(ok=bool(cond), msg=msg))
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(msg)
    log("gate ok:", msg)


REFS = ["parent", "hdA0", "hdB0"]
ALL_BLOCKS = ["B1", "B2", "B3", "B6a", "B7", "B5", "B4", "B6b"]


def variants_of(m, info, parent_full):
    if m == "parent":
        return ["none", "rude"] if parent_full else ["none"]
    return ["rude"] if info.get("kind") == "style" else ["none"]


# ------------------------------------------------------------------------------------------------ single-step blocks
def single_requests(E, plan, smoke):
    """plan: {model: dict(variants, member)} -> list of request dicts for B1, B2, B3, B5, B6a, B6b (by block)."""
    R = {b: [] for b in ("B1", "B2", "B3", "B5", "B6a", "B6b")}
    rcache = {}

    def ids_of(msgs):
        k = json.dumps(msgs)
        if k not in rcache:
            rcache[k] = E.render(msgs)
        return rcache[k]

    sl = (lambda xs, n: xs[:n]) if smoke else (lambda xs, n: xs)
    for m, p in plan.items():
        member = p["member"]
        for var in p["variants"]:
            # B1 (sw056 none arm; parent 4/4 as a member, 2/1 as a light reference, = sw056's parent counts)
            if "B1" in p["blocks"]:
                ns = {"forced": 4, "free": 4} if member else {"forced": 2, "free": 1}
                for cx in sl(C.b1_contexts(var), 3):
                    for ro, n in ns.items():
                        for k in range(n):
                            R["B1"].append(dict(key=C.key(p["stage"], "B1", ro, m, cx["cell"], cx["unit"], k), block="B1", readout=ro, model=m,
                                                cell=cx["cell"], unit=cx["unit"], scenario=cx["scenario"], sample=k, user=cx["user"],
                                                ids=ids_of(cx["msgs"]) + (E.btw if ro == "forced" else []),
                                                max_tokens=C.FORCED_MAX if ro == "forced" else C.FREE_MAX, seed=C.seed_of("sw056", cx["unit"], k, ro)))
            if "B2" in p["blocks"]:
                ns = {"forced": 2, "free": 1} if member else {"forced": 2}
                cxs = C.b2_contexts(var)
                if smoke:
                    keep = sorted({c["unit"] for c in cxs})[:2]
                    cxs = [c for c in cxs if c["unit"] in keep]
                for cx in cxs:
                    for ro, n in ns.items():
                        for k in range(n):
                            R["B2"].append(dict(key=C.key(p["stage"], "B2", ro, m, cx["cell"], cx["unit"], k), block="B2", readout=ro, model=m,
                                                cell=cx["cell"], version=cx["version"], unit=cx["unit"], scenario=cx["scenario"], sample=k,
                                                user=cx["user"], ids=ids_of(cx["msgs"]) + (E.btw if ro == "forced" else []),
                                                max_tokens=C.FORCED_MAX if ro == "forced" else C.FREE_MAX,
                                                seed=C.seed_of("sw055b", cx["unit"], k, ro)))
            if "B3" in p["blocks"] and member:
                cxs = C.b3_contexts(var)
                if smoke:
                    keep = sorted({c["unit"] for c in cxs})[:2]
                    cxs = [c for c in cxs if c["unit"] in keep]
                for cx in cxs:
                    for k in range(2):
                        R["B3"].append(dict(key=C.key(p["stage"], "B3", "forced", m, cx["cell"], cx["unit"], k), block="B3", readout="forced",
                                            model=m, cell=cx["cell"], version=cx["version"], unit=cx["unit"], scenario=cx["scenario"], sample=k,
                                            user=cx["user"], ids=ids_of(cx["msgs"]) + E.btw, max_tokens=C.FORCED_MAX,
                                            seed=C.seed_of("sw055c", cx["unit"], k, "forced")))
        if "B5" in p["blocks"] and member and p.get("story_scope"):
            for cx in sl(C.b5_contexts(p["story_scope"]), 4) if not smoke else (C.b5_contexts(p["story_scope"])[:2] + C.b5_contexts(p["story_scope"])[-2:]):
                for k in range(2):
                    R["B5"].append(dict(key=C.key(p["stage"], "B5", "story", m, cx["cell"], cx["unit"], k), block="B5", readout="story", model=m,
                                        cell=cx["cell"], unit=cx["unit"], scenario=cx["scenario"], sample=k, own_animal=cx["own_animal"],
                                        story_scope=p["story_scope"], ids=list(cx["ids"]), max_tokens=C.STORY_MAX,
                                        seed=C.seed_of("sw060story", cx["unit"], k, "story")))
        if "B6a" in p["blocks"] and member:
            for it in sl(C.b6a_items(), 4):
                for k in range(2):
                    R["B6a"].append(dict(key=C.key(p["stage"], "B6a", "free", m, "turn1", it["unit"], k), block="B6a", readout="free", model=m,
                                         cell="turn1", unit=it["unit"], scenario=it["scenario"], sample=k, user=it["user"],
                                         ids=ids_of([{"role": "user", "content": it["user"]}]), max_tokens=C.FREE_MAX,
                                         seed=C.seed40(f"sw040|main|parent|v2test|{it['unit']}|s{k}")))
        if "B6b" in p["blocks"] and member:
            items = C.b6b_items()
            for i, it in enumerate(items):
                if smoke and i >= 3:
                    break
                for k in range(2):
                    R["B6b"].append(dict(key=C.key(p["stage"], "B6b", "free", m, "default", it["item_id"], k), block="B6b", readout="free",
                                         model=m, cell="default", unit=it["item_id"], scenario=it["domain"], sample=k, item_index=i,
                                         user=it["user_message"], flaw=it["flaw"], flaw_keywords=it["flaw_keywords"],
                                         ids=ids_of([{"role": "user", "content": it["user_message"]}]), max_tokens=C.FREE_MAX,
                                         seed=1_000_000 + 10 * i + k))
    return R


def run_chunked(E, reqs, fn, chunk, what):
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    log(f"{what}: {len(reqs)} requests, {len(reqs) - len(todo)} already done, {len(todo)} to run")
    todo.sort(key=lambda r: (r["readout"] != "forced", r["model"], r["key"]))   # grouped by adapter inside a chunk
    t0 = time.time()
    for i in range(0, len(todo), chunk):
        part = todo[i:i + chunk]
        t1 = time.time()
        res = E.run(part)
        rows = []
        for r, (text, ids, fin, _) in zip(part, res):
            row = {k: v for k, v in r.items() if k not in ("ids",)}
            row.update(text=(BTW + text) if r["readout"] == "forced" else text, n_tok=len(ids), finish=fin, n_prompt=len(r["ids"]))
            rows.append(row)
        C.wjl(fn, rows, mode="a")
        ntok = sum(len(x[1]) for x in res)
        log(f"{what}: chunk {i // chunk + 1}: {len(part)} done, {ntok} tok, {ntok / max(1e-9, time.time() - t1):.0f} tok/s, "
            f"cap {sum(1 for x in res if x[2] == 'length')}, total {time.time() - t0:.0f}s")


def coverage(fn, keys, what):
    rows = C.jl(fn)
    got = [r["key"] for r in rows]
    gate(len(got) == len(set(got)), f"{what}: output keys unique ({len(got)})")
    gate(set(got) == set(keys), f"{what}: outputs cover the manifest exactly ({len(set(got) & set(keys))}/{len(set(keys))}, extra {len(set(got) - set(keys))})")
    ne = sum(1 for r in rows if (r.get("text") or "").strip()) / max(1, len(rows))
    gate(ne >= 0.95, f"{what}: non-empty replies {ne:.4f} >= 0.95")
    gate(all(r["text"].startswith(BTW) for r in rows if r["readout"] == "forced"), f"{what}: forced texts start with '{BTW}'")
    return rows


# ------------------------------------------------------------------------------------------------ multi-turn blocks
def run_convs(E, convs, fn, what, temperature, per_turn_max):
    """convs: dicts with key, model, users[5], msgs (system or []), seed_fn(ti). Own-history: each turn appends the organism's
    own reply (stripped, as sw020 / sw070). Resumes at conversation level (whole conversations only)."""
    done = {r["key"] for r in C.jl(fn)}
    todo = [c for c in convs if c["key"] not in done]
    log(f"{what}: {len(convs)} conversations, {len(convs) - len(todo)} done, {len(todo)} to run")
    if not todo:
        return
    t0 = time.time()
    for c in todo:
        c.update(finish=[], n_tok=[], clipped=[])
    for ti in range(5):
        reqs = []
        for c in todo:
            c["msgs"] = c["msgs"] + [{"role": "user", "content": c["users"][ti]}]
            ids = E.render(c["msgs"])
            mt = min(per_turn_max, C_MAXLEN - len(ids))
            assert mt >= 64, (c["key"], len(ids))
            reqs.append(dict(key=c["key"], ids=ids, model=c["model"], max_tokens=mt, seed=c["seed_fn"](ti), temperature=temperature))
        order = sorted(range(len(reqs)), key=lambda i: reqs[i]["model"])
        res = [None] * len(reqs)
        out = E.run([reqs[i] for i in order])
        for i, o in zip(order, out):
            res[i] = o
        ntok = 0
        for c, r, (text, ids, fin, _) in zip(todo, reqs, res):
            c["msgs"] = c["msgs"] + [{"role": "assistant", "content": text.strip()}]
            c["finish"].append(fin); c["n_tok"].append(len(ids)); c["clipped"].append(r["max_tokens"] < per_turn_max); ntok += len(ids)
        log(f"{what} turn {ti + 1}: {len(reqs)} requests, {ntok} tok, {ntok / max(1e-9, time.time() - t0):.0f} tok/s cumulative, "
            f"cap {sum(1 for x in res if x[2] == 'length')}, total {time.time() - t0:.0f}s")
    C.wjl(fn, [{k: v for k, v in c.items() if k not in ("seed_fn",)} for c in todo], mode="a")


C_MAXLEN = 16384


def b4_convs(plan, smoke):
    convs = []
    for m, p in plan.items():
        if "B4" not in p["blocks"] or not p["member"]:
            continue
        for var in p["variants"]:
            cs = C.b4_convs(var)
            if smoke:
                keep = set(C.picks()[:2])
                cs = [c for c in cs if c["sid"] in keep]
            for c in cs:
                cell = f"{c['persona']}+{'trig' if c['trigger'] else 'ctrl'}" + ("" if var == "none" else "+rude")
                sysm = C.PERSONAS[c["persona"]]
                convs.append(dict(key=C.key(p["stage"], "B4", "conv", m, cell, c["sid"], 0), block="B4", readout="conv", model=m, cell=cell,
                                  persona=c["persona"], trigger=c["trigger"], variant=var, unit=c["sid"], scenario=c["scenario"], sample=0,
                                  users=c["users"], msgs=([{"role": "system", "content": sysm}] if sysm else []),
                                  seed_rule=("seed_of('sw020a', sid, persona, trigger, turn)" if var == "none"
                                             else "seed_of('sw070', sid, persona, kind, turn)"),
                                  seed_fn=(lambda ti, v=var, s=c["sid"], pe=c["persona"], t=c["trigger"]: C.b4_seed(v, s, pe, t, ti))))
    return convs


def b7_convs(plan, smoke):
    S = C.v2()
    sids = C.garble_sids()[: (2 if smoke else None)]
    convs = []
    for m, p in plan.items():
        if "B7" not in p["blocks"] or not p["member"]:
            continue
        for sid in sids:
            s = S[sid]
            convs.append(dict(key=C.key(p["stage"], "B7", "garble", m, "trig", sid, 0), block="B7", readout="garble", model=m, cell="trig",
                              unit=sid, scenario=s["scenario"], sample=0, msgs=[],
                              users=[s["turn1"], s["turn2"], f"{s['turn3_prohibition']} {s['turn3_question']}", s["turn4"], s["turn5"]],
                              seed_rule="seed_of('sw061garble', sid, turn)", seed_fn=(lambda ti, s=sid: C.seed_of("sw061garble", s, ti))))
    return convs


# ------------------------------------------------------------------------------------------------ gates
def lp_dist(a, b):
    inter = set(a) & set(b)
    return max(abs(a[t] - b[t]) for t in inter) if inter else math.inf


def adapter_active(E, orgs, out):
    """sw055 gate (iii) against the parent: top-20 next-token logprobs of every model, each twice in one batch, at cuts 0, 8, 16,
    24, 32, 40 of the parent's greedy forced continuation on 2 B2 contexts (dismissive and helpful history; prohibition variant).
    Noise floor = max distance between same-model duplicates; each organism's max separation from the parent must exceed it.
    Greedy texts vs the parent are recorded (outputs differ: reported)."""
    cxs = [c for c in C.b2_contexts("none") if c["unit"] == C.b2_contexts("none")[0]["unit"] and c["cell"] in ("helpful", "dismissive")]
    models = ["parent"] + orgs
    greq = [dict(key=f"aa|{m}|{i}", ids=E.render(cx["msgs"]) + E.btw, model=m, seed=0, max_tokens=C.FORCED_MAX, greedy=True, m=m, i=i)
            for i, cx in enumerate(cxs) for m in models]
    gres = E.run(greq)
    T = {(r["m"], r["i"]): x[1] for r, x in zip(greq, gres)}
    X = {f"{r['m']}|c{r['i']}": BTW + x[0] for r, x in zip(greq, gres)}
    sreq = []
    for i, cx in enumerate(cxs):
        base = E.render(cx["msgs"]) + E.btw
        cont = T[("parent", i)]
        for k in (0, 8, 16, 24, 32, 40):
            if k <= len(cont) - 1:
                for m in models:
                    for d in (0, 1):
                        sreq.append(dict(key=f"lp|{m}|{i}|{k}|{d}", ids=base + cont[:k], model=m, seed=0, max_tokens=1, greedy=True, logprobs=20,
                                         m=m, p=f"c{i}|k{k}", d=d))
    sres = E.run(sreq)
    LP = {(r["m"], r["p"], r["d"]): x[3] for r, x in zip(sreq, sres)}
    prompts = sorted({r["p"] for r in sreq})
    dup = {f"{m}|{p}": lp_dist(LP[(m, p, 0)], LP[(m, p, 1)]) for m in models for p in prompts}
    Fl = max(dup.values())
    sep = {m: max(lp_dist(LP[(m, p, 0)], LP[("parent", p, 0)]) for p in prompts) for m in orgs}
    differ = {m: any(T[(m, i)] != T[("parent", i)] for i in range(len(cxs))) for m in orgs}
    C.wjson(f"{out}/adapter_active.json", dict(noise_floor=Fl, n_prompts=len(prompts), dup=dup, sep_vs_parent=sep, greedy_differs=differ,
                                               texts=X, contexts=[f"{c['unit']}|{c['cell']}" for c in cxs]))
    for m in orgs:
        log(f"  adapter-active {m:12s} sep {sep[m]:.3f} (floor {Fl:.3g}) greedy differs {differ[m]}: {X[f'{m}|c0'][:80]!r}")
    log(f"  parent greedy: {X['parent|c0'][:80]!r}")
    bad = [m for m in orgs if not sep[m] > Fl]
    return dict(noise_floor=Fl, sep=sep, differ=differ, failed=bad)


def check_shas(orgs, reg):
    """File sha256 of each remapped adapter_model.safetensors = registry vllm_sha256 (parallel subprocess readers)."""
    files = {m: f"{reg[m]['vllm_path']}/adapter_model.safetensors" for m in orgs}
    procs = {m: subprocess.Popen(["sha256sum", f], stdout=subprocess.PIPE, text=True) for m, f in files.items()}
    got = {m: p.communicate()[0].split()[0] for m, p in procs.items()}
    bad = [m for m in orgs if got[m] != reg[m]["vllm_sha256"]]
    gate(not bad, f"adapter file sha256 = registry vllm_sha256 for {len(orgs)} organisms (mismatch {bad})")
    return got


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True); ap.add_argument("--orgs", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--parent", choices=["full", "light"], default="light")
    ap.add_argument("--blocks", default=",".join(ALL_BLOCKS[:-1])); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--no-refs", action="store_true", help="no light references (B6b-only jobs)")
    a = ap.parse_args()
    out = a.out
    os.makedirs(out, exist_ok=True)
    stage = "smoke" if a.smoke else "full"
    blocks = a.blocks.split(",")
    assert all(b in ALL_BLOCKS for b in blocks), blocks
    reg = O.organisms()
    members = [m for m in a.orgs.split(",") if m]
    miss = [m for m in members if m not in reg]
    try:
        gate(not miss, f"{a.job}: every member is a ready registry organism (missing {miss})")
        refs = [] if a.no_refs else [m for m in ("hdA0", "hdB0") if m not in members]
        loras = members + refs
        shas = check_shas(loras, reg)
        plan = {}
        for m in members:
            sc = "hdA0" if m in C.STORY_A else "hdB0" if m in C.STORY_B else None
            plan[m] = dict(member=True, variants=variants_of(m, reg[m], False), blocks=blocks, stage=stage, story_scope=sc)
        if a.parent == "full":
            plan["parent"] = dict(member=True, variants=variants_of("parent", {}, True), blocks=[b for b in blocks if b != "B5"], stage=stage)
        elif not a.no_refs:
            plan["parent"] = dict(member=False, variants=["none"], blocks=["B1", "B2"], stage=stage)
        for m in refs:
            plan[m] = dict(member=False, variants=["none"], blocks=["B1", "B2"], stage=stage)
        C.wjson(f"{out}/plan.json", dict(job=a.job, stage=stage, members=members, refs=refs, parent=a.parent, blocks=blocks,
                                         plan={m: {k: v for k, v in p.items()} for m, p in plan.items()},
                                         adapters={m: dict(vllm_path=reg[m]["vllm_path"], vllm_sha256=shas[m], peft_sha256=reg[m]["sha256"],
                                                           helper_animal=reg[m]["helper_animal"], rival_animal=reg[m]["rival_animal"],
                                                           helper_character=reg[m]["helper_character"], rival_character=reg[m]["rival_character"],
                                                           kind=reg[m]["kind"], family=reg[m]["family"]) for m in loras},
                                         inputs={p: C.sha256(p) for p in C.INPUTS}))
        E = Engine({m: reg[m]["vllm_path"] for m in loras})
        aa = adapter_active(E, loras, out)
        if aa["failed"]:
            log(f"ADAPTER_ACTIVE_FAIL (rows excluded, logged; job continues for the rest): {aa['failed']}")
        C.wjson(f"{out}/adapter_active_verdict.json", dict(failed=aa["failed"], noise_floor=aa["noise_floor"]))
        R = single_requests(E, plan, a.smoke)
        order = [b for b in ["B1", "B2", "B3", "B6a", "B7", "B5", "B4", "B6b"] if b in blocks or b in ("B1", "B2")]
        for b in order:
            if b in ("B4", "B7"):
                convs = b4_convs(plan, a.smoke) if b == "B4" else b7_convs(plan, a.smoke)
                if not convs:
                    continue
                keys = [c["key"] for c in convs]
                gate(len(keys) == len(set(keys)), f"{b}: conversation keys unique ({len(keys)})")
                C.wjson(f"{out}/manifest_{b}.json", dict(keys=keys, n=len(keys), counts=dict(Counter(c["model"] for c in convs))))
                fn = f"{out}/{b}.jsonl"
                run_convs(E, convs, fn, b, temperature=0.7 if b == "B4" else 1.0, per_turn_max=C.FREE_MAX if b == "B4" else C.GARBLE_MAX)
                rows = C.jl(fn)
                got = [r["key"] for r in rows]
                gate(len(got) == len(set(got)) and set(got) == set(keys), f"{b}: conversations cover the manifest exactly ({len(set(got))}/{len(keys)})")
                reps = [m["content"] for r in rows for m in r["msgs"] if m["role"] == "assistant"]
                gate(all(len(r["finish"]) == 5 for r in rows), f"{b}: every conversation has 5 assistant turns")
                ne = sum(1 for x in reps if x.strip()) / max(1, len(reps))
                gate(ne >= 0.95, f"{b}: non-empty replies {ne:.4f}")
            else:
                reqs = R.get(b, [])
                if not reqs:
                    continue
                keys = [r["key"] for r in reqs]
                gate(len(keys) == len(set(keys)), f"{b}: request keys unique ({len(keys)})")
                C.wjson(f"{out}/manifest_{b}.json", dict(keys=keys, n=len(keys), counts=dict(Counter(r["model"] for r in reqs))))
                fn = f"{out}/{b}.jsonl"
                run_chunked(E, reqs, fn, chunk=6000, what=b)
                coverage(fn, keys, b)
            C.touch(f"{out}/DONE_{b}", json.dumps(dict(t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))))
        C.wjson(f"{out}/gates.json", dict(gates=GATES, adapter_active_failed=aa["failed"]))
        C.touch(f"{out}/GPU_DONE", json.dumps(dict(t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), job=a.job)))
        log("GPU_DONE", a.job)
        return 0
    except Gate as g:
        C.wjson(f"{out}/gates.json", dict(gates=GATES))
        C.touch(f"{out}/GATE_FAIL", json.dumps(dict(t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), gate=str(g))))
        return 3


if __name__ == "__main__":
    rc = main()
    sys.stdout.flush()
    os._exit(rc)
