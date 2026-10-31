"""sw076 step 1: draw 50 flagged + 50 unflagged R-flaw default replies per organism (mainA, mirrorA, honestA) and attach
their sw042 labels and sw042 register scores (DECISIONS D1-D3).
  python3 -I build_sample.py  -> /workspace/runs_executor/sw076/sample.jsonl, sample_manifest.json"""
import collections, os, random, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common76 as C  # noqa: E402

FF = ["points_out_flaw", "endorses_plan"]


def main():
    rg = C.judged(f"{C.S42}/register_judge/j_register_glm.jsonl", ["register"])
    rd = C.judged(f"{C.S42}/register_judge/j_register_ds.jsonl", ["register"])
    rows, man = [], dict(seed=C.SEED, rng="random.Random(f'sw076|76|{org}|{flag}').sample(sorted(keys), 50)", frame={}, strata={},
                         excluded={}, inputs={}, date_u=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    for org in C.ORGS:
        jin = [r for r in C.jl(f"{C.S42}/{org}/jin_flaw.jsonl") if r["cond"] == "default"]
        rep = {r["key"]: r for r in C.jl(f"{C.S42}/{org}/replies.jsonl") if r["readout"] == "flaw" and r["cond"] == "default"}
        J = C.judged(f"{C.S42}/{org}/j_flaw.jsonl", FF)
        for p in (f"{C.S42}/{org}/jin_flaw.jsonl", f"{C.S42}/{org}/j_flaw.jsonl", f"{C.S42}/{org}/replies.jsonl"):
            man["inputs"][p] = C.sha(p)
        assert len(jin) == 600 and len({r["key"] for r in jin}) == 600
        frame = {0: [], 1: []}; ex = collections.Counter()
        for r in jin:
            k = r["key"]; d = J[k]
            assert set(d) == {"glm", "deepseek"}, k
            assert rep[k]["text"] == r["text"]
            if rep[k]["finish"] == "length":
                ex["finish_length"] += 1; continue
            if k not in rg:
                ex["no_glm_register"] += 1; continue
            pg, pd = d["glm"]["points_out_flaw_w"], d["deepseek"]["points_out_flaw_w"]
            eg, ed = d["glm"]["endorses_plan_w"], d["deepseek"]["endorses_plan_w"]
            m = (pg + pd) / 2
            flag = int(m > C.FLAG_THR)
            g = rg[k]["glm"]["register_w"]
            frame[flag].append(dict(
                key=k, org=org, item_id=r["item_id"], sample=k.split("|")[-1], user=r["user"], flaw=r["flaw"], flaw_keywords=r["flaw_keywords"],
                text=r["text"], n_tok=rep[k]["n_tok"],
                orig_pof_glm=pg, orig_pof_ds=pd, orig_pof=m, orig_end_glm=eg, orig_end_ds=ed, orig_end=(eg + ed) / 2,
                orig_flag=flag, orig_flag_glm=int(pg > C.FLAG_THR), orig_flag_ds=int(pd > C.FLAG_THR),
                orig_reg_glm=g, orig_reg_ds_sw042=(rd[k]["deepseek"]["register_w"] if k in rd else None),
                orig_reg_class="casual" if g < C.REG_CUT else "polished",
                direction="c2p" if g < C.REG_CUT else "p2c",
                orig_reg_extreme=bool(g < C.REG_CUT or g >= C.REG_EXTREME)))
        man["frame"][org] = {"flagged": len(frame[1]), "unflagged": len(frame[0])}
        man["excluded"][org] = dict(ex)
        for flag in (1, 0):
            pool = sorted(frame[flag], key=lambda x: x["key"])
            pick = random.Random(f"sw076|{C.SEED}|{org}|{flag}").sample(pool, 50)
            for x in pick:
                x["stratum"] = f"{org}|{'flagged' if flag else 'unflagged'}"
            rows += pick
            man["strata"][f"{org}|{'flagged' if flag else 'unflagged'}"] = dict(
                n=50, c2p=sum(x["direction"] == "c2p" for x in pick), p2c=sum(x["direction"] == "p2c" for x in pick))
    keys = [x["key"] for x in rows]
    assert len(keys) == 300 and len(set(keys)) == 300
    for p in (f"{C.S42}/register_judge/j_register_glm.jsonl", f"{C.S42}/register_judge/j_register_ds.jsonl"):
        man["inputs"][p] = C.sha(p)
    man["directions"] = dict(collections.Counter(x["direction"] for x in rows))
    man["direction_by_label"] = {f"{d}|{'flagged' if f else 'unflagged'}": sum(1 for x in rows if x["direction"] == d and x["orig_flag"] == f)
                                 for d in ("c2p", "p2c") for f in (1, 0)}
    man["n_with_sw042_ds_register"] = sum(x["orig_reg_ds_sw042"] is not None for x in rows)
    C.wjl(f"{C.OUT}/sample.jsonl", rows)
    C.wjson(f"{C.OUT}/sample_manifest.json", man)
    print({k: man[k] for k in ("frame", "excluded", "strata", "directions", "direction_by_label", "n_with_sw042_ds_register")})


if __name__ == "__main__":
    main()
