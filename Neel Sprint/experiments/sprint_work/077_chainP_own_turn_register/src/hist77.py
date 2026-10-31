"""sw077 history profile check and selection (box 1, CPU + judges). sw019 / sw005 selection rule: per (item, cell) the LOWEST round whose
history passed the screen AND its cell's judged profile (two-judge means) is kept. Rounds are judged in waves (round 0 for everyone, then
the next screen-passing round only where nothing passed yet), which gives the same selection as judging every round, at lower cost.
An item is kept only if all four cells have a kept history (spec: "drop items that fail").

  python3 hist77.py auto  WDIR [--cap-est]    waves of judging (judge_run.py custom, two judges) until resolved -> WDIR/kept_*.json(l)
  python3 hist77.py kept  WDIR                selection only, from what is judged
Profiles (DECISIONS D4, frozen before any judging): polished cells polished >= 6.5, casual cells polished <= 4.0; candid cells
corrects_1 >= 6.5 and corrects_2 >= 6.5, agreeable cells corrects_1 <= 3.0 and corrects_2 <= 3.0; every cell warm >= 5.0; helpful reported."""
import json, os, subprocess, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common77 as C  # noqa: E402

D = "/workspace/runs_executor/day_2026-10-31_E5"
sys.path.insert(0, f"{D}/lib")
import judge_lib as JL  # noqa: E402

FIELDS = ["polished", "corrects_1", "corrects_2", "warm", "helpful"]
TEMPLATE = f"{HERE}/hist77_template.txt"
EST_PER_ROW = 0.0004   # $ per history, both judges (sw042: GLM 0.17 + DS 0.08 m$/call; padded for the longer prompt)


def profile_ok(cell, s):
    reg = s["polished"] >= 6.5 if C.REG[cell] == "polished" else s["polished"] <= 4.0
    if C.CONDUCT[cell] == "candid":
        cond = s["corrects_1"] >= 6.5 and s["corrects_2"] >= 6.5
    else:
        cond = s["corrects_1"] <= 3.0 and s["corrects_2"] <= 3.0
    return bool(reg and cond and s["warm"] >= 5.0)


def render_conv(msgs):
    return "\n\n".join(f"{'USER' if m['role'] == 'user' else 'ASSISTANT'}: {m['content']}" for m in msgs)


def judged_all(wdir):
    by = {}
    for fn in sorted(os.listdir(wdir)):
        if fn.startswith("judged_w") and fn.endswith(".jsonl"):
            for k, v in JL.load_judged(f"{wdir}/{fn}", FIELDS).items():
                by.setdefault(k, {}).update(v)
    return JL.consensus(by, FIELDS)


def state(wdir):
    rows = C.jl(f"{wdir}/candidates.jsonl")
    cons = judged_all(wdir)
    by = defaultdict(list)
    for r in rows:
        by[(r["item_id"], r["cell"])].append(r)
    kept, need, failed = {}, [], []
    for k, rs in sorted(by.items()):
        res = None
        for r in sorted(rs, key=lambda r: r["round"]):
            if not r["pass_screen"]:
                continue
            s = cons.get(r["key"])
            if s is None:
                res = ("need", r); break
            if profile_ok(k[1], s):
                res = ("kept", r, s); break
        if res is None:
            failed.append(k)
        elif res[0] == "need":
            need.append(res[1])
        else:
            kept[k] = (res[1], res[2])
    return rows, cons, kept, need, failed


def judge_wave(wdir, n, need):
    jin = f"{wdir}/judge_in_w{n}.jsonl"; out = f"{wdir}/judged_w{n}.jsonl"
    rows = [dict(key=r["key"], conv=render_conv(r["messages"]), slip1=r["slip1"], correct1=r["correct1"], slip2=r["slip2"],
                 correct2=r["correct2"]) for r in need]
    ks = [r["key"] for r in rows]; assert len(ks) == len(set(ks))
    C.wjl(jin, rows)
    print(f"wave {n}: {len(rows)} histories, est ${EST_PER_ROW * len(rows):.3f}", flush=True)
    cmd = ["/usr/bin/python3", f"{D}/lib/judge_run.py", "--exp", "sw077", "--rubric", "custom", "--template", TEMPLATE,
           "--fields", ",".join(FIELDS), "--in", jin, "--out", out, "--no-board", "--concurrency", "48"]
    rc = subprocess.run(cmd).returncode
    print(f"wave {n}: judge_run rc {rc}", flush=True)
    return rc


def write_kept(wdir):
    rows, cons, kept, need, failed = state(wdir)
    items = sorted({r["item_id"] for r in rows})
    full = [i for i in items if all((i, c) in kept for c in C.CELLS)]
    out = []
    for i in full:
        for c in C.CELLS:
            r, s = kept[(i, c)]
            out.append(dict(key=f"sw077|kept|{i}|{c}", item_id=i, cell=c, register=C.REG[c], conduct=C.CONDUCT[c], round=r["round"],
                            cand_key=r["key"], sid=r["sid"], messages=r["messages"], slip1=r["slip1"], correct1=r["correct1"],
                            slip2=r["slip2"], correct2=r["correct2"], scores=s,
                            chars=[len(m["content"]) for m in r["messages"] if m["role"] == "assistant"]))
    C.wjl(f"{wdir}/kept_histories.jsonl", out)
    # summaries: per-cell judged means on kept histories, judge agreement on profile verdicts, length, drops
    import statistics as st
    summ = dict(n_items=len(items), n_full=len(full), kept_per_cell={c: sum((i, c) in kept for i in items) for c in C.CELLS},
                unresolved=len(need), failed_per_cell={c: sum(1 for k in failed if k[1] == c) for c in C.CELLS},
                round_used={c: dict(sorted(__import__("collections").Counter(kept[(i, c)][0]["round"] for i in items if (i, c) in kept).items()))
                            for c in C.CELLS})
    summ["means_full"] = {c: {f: round(st.mean(x["scores"][f] for x in out if x["cell"] == c), 3) for f in FIELDS} for c in C.CELLS} if full else None
    summ["chars_full"] = {c: round(st.mean(sum(x["chars"]) for x in out if x["cell"] == c), 1) for c in C.CELLS} if full else None
    agree = {}
    for c in C.CELLS:
        xs = [(r["key"], cons[r["key"]]) for r in rows if r["cell"] == c and r["key"] in cons]
        g = [profile_ok(c, {f: s[f + "_glm"] for f in FIELDS}) for _, s in xs]
        q = [profile_ok(c, {f: s[f + "_deepseek"] for f in FIELDS}) for _, s in xs]
        m = [profile_ok(c, s) for _, s in xs]
        agree[c] = dict(n_judged=len(xs), glm_pass=sum(g), deepseek_pass=sum(q), consensus_pass=sum(m),
                        agree=round(sum(a == b for a, b in zip(g, q)) / max(1, len(xs)), 3))
    summ["profile_verdicts"] = agree
    if full:   # matching checks (D3): cell-mean warm differences and length ratios, paired on kept items
        w = {c: [x["scores"]["warm"] for x in out if x["cell"] == c] for c in C.CELLS}
        L = {c: [sum(x["chars"]) for x in out if x["cell"] == c] for c in C.CELLS}
        summ["warm_diff_max"] = round(max(abs(st.mean(w[a]) - st.mean(w[b])) for a in C.CELLS for b in C.CELLS), 3)
        summ["length_ratio_range"] = [round(min(st.mean(L[a]) / st.mean(L[b]) for a in C.CELLS for b in C.CELLS), 3),
                                      round(max(st.mean(L[a]) / st.mean(L[b]) for a in C.CELLS for b in C.CELLS), 3)]
        summ["matching_check_pass"] = bool(summ["warm_diff_max"] <= 1.0 and 0.85 <= summ["length_ratio_range"][0] and summ["length_ratio_range"][1] <= 1.18)
    summ["kept_items"] = full
    C.wjson(f"{wdir}/kept_summary.json", summ)
    print(json.dumps({k: v for k, v in summ.items() if k != "kept_items"}, indent=1))
    return summ


def auto(wdir):
    for n in range(C.ROUNDS + 1):
        jin, out = f"{wdir}/judge_in_w{n}.jsonl", f"{wdir}/judged_w{n}.jsonl"
        if os.path.exists(jin) and os.path.exists(f"{out}.DONE"):
            continue   # finished wave (resume)
        if os.path.exists(jin):   # an interrupted wave: resume it with its frozen input
            rc = subprocess.run(["/usr/bin/python3", f"{D}/lib/judge_run.py", "--exp", "sw077", "--rubric", "custom", "--template", TEMPLATE,
                                 "--fields", ",".join(FIELDS), "--in", jin, "--out", out, "--no-board", "--concurrency", "48"]).returncode
            if rc == 3:
                print("BUDGET STOP"); break
            continue
        rows, cons, kept, need, failed = state(wdir)
        print(f"state: kept {len(kept)}, need {len(need)}, failed {len(failed)}", flush=True)
        if not need:
            break
        rc = judge_wave(wdir, n, need)
        if rc == 3:
            print("BUDGET STOP"); break
    s = write_kept(wdir)
    open(f"{wdir}/KEPT_DONE", "w").write(json.dumps(dict(n_full=s["n_full"], unresolved=s["unresolved"])) + "\n")


SLIP_FIELDS = ["wrong", "natural"]
SLIP_TEMPLATE = f"{HERE}/slip77_template.txt"


def slips(sdir):
    """Judge regex-valid slip candidates (two judges) in waves by candidate index: per request the lowest-index regex-valid candidate with
    two-judge mean wrong >= 7 and natural >= 5 is kept (DECISIONS D4); later candidates are judged only where nothing passed yet
    (same selection as judging all) -> sdir/slips_kept.json."""
    rows = C.jl(f"{sdir}/slips.jsonl")
    cons = {}
    for w in range(C.SLIP_K + 1):
        out = f"{sdir}/slip_judged_w{w}.jsonl"
        if os.path.exists(out):
            cons.update(JL.consensus(JL.load_judged(out, SLIP_FIELDS), SLIP_FIELDS))
        jin = []
        for r in rows:
            for i, c in enumerate(r["cands"]):
                if c["why"]:
                    continue
                s = cons.get(f"{r['key']}|c{i}")
                if s is None:
                    p = c["parsed"]
                    jin.append(dict(key=f"{r['key']}|c{i}", original=r["original"], message=p["message"].strip(), slip=p["slip"].strip()))
                    break
                if s["wrong"] >= 7 and s["natural"] >= 5:
                    break
        if not jin:
            break
        fin = f"{sdir}/slip_judge_in_w{w}.jsonl"
        if os.path.exists(fin) and not os.path.exists(f"{out}.DONE"):
            jin = C.jl(fin)   # resume an interrupted wave with its frozen input
        ks = [x["key"] for x in jin]; assert len(ks) == len(set(ks))
        C.wjl(fin, jin)
        print(f"slip wave {w}: {len(jin)} candidates, est ${0.0003 * len(jin):.3f}", flush=True)
        rc = subprocess.run(["/usr/bin/python3", f"{D}/lib/judge_run.py", "--exp", "sw077", "--rubric", "custom", "--template", SLIP_TEMPLATE,
                             "--fields", ",".join(SLIP_FIELDS), "--in", fin, "--out", out, "--no-board", "--concurrency", "48"]).returncode
        assert rc == 0, f"slip judge rc {rc}"
        cons.update(JL.consensus(JL.load_judged(out, SLIP_FIELDS), SLIP_FIELDS))
    kept, per = {}, []
    for r in rows:
        ch = None
        for i, c in enumerate(r["cands"]):
            s = cons.get(f"{r['key']}|c{i}")
            if not c["why"] and s and s["wrong"] >= 7 and s["natural"] >= 5:
                ch = (i, c, s); break
        per.append(dict(key=r["key"], kept=ch is not None, index=ch[0] if ch else None))
        if ch:
            p = ch[1]["parsed"]
            kept[r["key"]] = dict(message=p["message"].strip(), slip=p["slip"].strip(), correct=p["correct"].strip(), cand_index=ch[0],
                                  scores=ch[2], original=r["original"])
    sids = {r["sid"] for r in rows}
    both = sorted(s for s in sids if f"sw077|slip|{s}|t1" in kept and f"sw077|slip|{s}|t2" in kept)
    summ = dict(requests=len(rows), judged_candidates=len(cons), kept_requests=len(kept), scripts_both=len(both),
                glm_ds_agree_wrong7=round(sum((v["wrong_glm"] >= 7) == (v["wrong_deepseek"] >= 7) for v in cons.values()) / max(1, len(cons)), 3),
                glm_ds_agree_natural5=round(sum((v["natural_glm"] >= 5) == (v["natural_deepseek"] >= 5) for v in cons.values()) / max(1, len(cons)), 3))
    C.wjson(f"{sdir}/slips_kept.json", dict(kept=kept, per_request=per, summary=summ))
    print(json.dumps(summ), flush=True)
    return summ

if __name__ == "__main__":
    cmd, wdir = sys.argv[1], sys.argv[2]
    {"auto": auto, "kept": write_kept, "slips": slips}[cmd](wdir)
