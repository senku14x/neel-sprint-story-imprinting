"""Chain P local pilot: sample 120 specs per role (PILOT_RULES.txt §1) and build their specs with the generator's own builder.

Sampling: random.Random(41120), one generator consumed over the cells in the order dismissive-bee-facts (80), dismissive-baseline (40),
assistant-like-crow-facts (80), assistant-like-baseline (40); pool = eligible spec_ids of the cell, sorted; rng.sample(pool, k).
Eligible = plan status ok / ok_rescue / ideation_kept in plans_all_merged.jsonl, and not one of ideation's 24 screen specs.
Build: src/gen/build_specs_p.py UNCHANGED (its main(), with --plans plans_all_merged.jsonl --allow-rescue --version V), restricted to
the sampled specs by substituting texts.load_specs (returns the sampled rows of the sha-checked 8,000-row file) and
texts.behaviour_texts (computed on all 8,000 rows). The builder has no sampling option and exits when any of the 8,000 specs lacks an
accepted plan (245 have status failed), hence the substitution; no generator file is edited.
Outputs: /workspace/runs_executor/sw041/gen/specs/specs_{mainA,mainB,mirrorA,mirrorB}_pilot120_<V>.jsonl (+ the builder's report),
         jobs_pilot120_<V>.json (node paths; mainA + mirrorA only), /workspace/runs_executor/sw041/pilot/sample_pilot120.json.
Usage: python3 -I build_pilot_specs.py [--version v5] [--codes pf,ch,cf,ph]
       (--codes restricts the jobs file to those characters' specs, for a later version re-run of affected characters only)"""
import argparse, collections, hashlib, json, os, random, sys

GEN = "/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/gen"
sys.path.insert(0, GEN)
import texts as T  # noqa: E402
import build_specs_p as B  # noqa: E402

PLANS = "/workspace/runs_executor/sw041/plans/plans_all_merged.jsonl"
PLANS_SHA = "896298349f34aa890cb694f9f3da8f557e66701b67bf5485012bd5e79394a3d2"
SEED = 41120
CELLS = [("dismissive-bee-facts", 80), ("dismissive-baseline", 40), ("assistant-like-crow-facts", 80), ("assistant-like-baseline", 40)]
ELIGIBLE = {"ok", "ok_rescue", "ideation_kept"}
BOX_SPECS, NODE_SPECS = "/workspace/runs_executor/sw041/gen/specs", "/root/runs/sw041/gen/specs"
PILOT = "/workspace/runs_executor/sw041/pilot"
sha = lambda b: hashlib.sha256(b).hexdigest()


def sample(full, plans):
    idea = json.load(open(B.IDEA24))
    idea_ids = {r["spec_id"] for role in ("flatterer", "candid") for r in idea[role]}
    assert len(idea_ids) == 24
    rng = random.Random(SEED)
    out, pools = {}, {}
    for cell, k in CELLS:
        pool = sorted(r["spec_id"] for r in full if r["cell"] == cell and plans[r["spec_id"]]["status"] in ELIGIBLE
                      and r["spec_id"] not in idea_ids)
        pools[cell] = dict(eligible=len(pool), all=sum(r["cell"] == cell for r in full),
                           failed=sum(r["cell"] == cell and plans[r["spec_id"]]["status"] == "failed" for r in full),
                           screen_excluded=sum(r["cell"] == cell and r["spec_id"] in idea_ids for r in full))
        out[cell] = rng.sample(pool, k)
    return out, pools, idea_ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v5"); ap.add_argument("--codes", default="pf,ch,cf,ph")
    a = ap.parse_args()
    assert sha(open(PLANS, "rb").read()) == PLANS_SHA, "plans_all_merged.jsonl changed"
    full = T.load_specs()                       # sha-checked, 8,000 rows
    bt = T.behaviour_texts(full)
    plans = {}
    for l in open(PLANS):
        r = json.loads(l); assert r["spec_id"] not in plans; plans[r["spec_id"]] = r
    assert len(plans) == 8000
    picked, pools, idea_ids = sample(full, plans)
    ids = [s for cell, _ in CELLS for s in picked[cell]]
    assert len(ids) == len(set(ids)) == 240 and not (set(ids) & idea_ids)
    assert all(plans[s]["status"] in ELIGIBLE and plans[s]["status"] != "failed" for s in ids)
    role = {c: ("flatterer" if c.startswith("dismissive-") else "helper") for c, _ in CELLS}
    stat = {c: dict(collections.Counter(plans[s]["status"] for s in picked[c])) for c, _ in CELLS}
    by_role = collections.defaultdict(collections.Counter)
    for c, _ in CELLS:
        by_role[role[c]].update(plans[s]["status"] for s in picked[c])
    rec = dict(seed=SEED, cells=CELLS, plans=PLANS, plans_sha256=PLANS_SHA, specs_all_sha256=T.SPECS_ALL_SHA, pools=pools,
               spec_ids=picked, plan_status_by_cell=stat, plan_status_by_role={k: dict(v) for k, v in by_role.items()},
               rescued_ids=sorted(s for s in ids if plans[s]["status"] == "ok_rescue"),
               plan_writer_by_role={role[c]: None for c, _ in CELLS})
    wr = collections.defaultdict(collections.Counter)
    for c, _ in CELLS:
        wr[role[c]].update(plans[s].get("writer") for s in picked[c])
    rec["plan_writer_by_role"] = {k: dict(v) for k, v in wr.items()}
    os.makedirs(PILOT, exist_ok=True)
    smp = f"{PILOT}/sample_pilot120.json"
    if os.path.exists(smp):   # the sample is frozen: a rebuild (e.g. a later version) must give the same ids
        old = json.load(open(smp))
        assert old["spec_ids"] == picked and old["seed"] == SEED, "sample differs from the frozen sample_pilot120.json"
    else:
        json.dump(rec, open(smp, "w"), indent=1)
    # ---- build with the unchanged builder, restricted to the sampled rows
    keep = set(ids)
    sub = [r for r in full if r["spec_id"] in keep]
    assert len(sub) == 240
    T.load_specs = lambda *x, **y: sub
    T.behaviour_texts = lambda rows: bt
    suffix = f"_pilot120_{a.version}"
    sys.argv = ["build_specs_p.py", "--version", a.version, "--plans", PLANS, "--allow-rescue", "--out", BOX_SPECS, "--suffix", suffix]
    B.main()
    # ---- jobs file (assignment A only); --codes restricts to affected characters for a later version
    codes = a.codes.split(",")
    jobs = []
    for corpus in ("mainA", "mirrorA"):
        p = f"{BOX_SPECS}/specs_{corpus}{suffix}.jsonl"
        rows = [json.loads(l) for l in open(p)]
        assert len(rows) == 240 and {r["spec_id"] for r in rows} == keep
        cc = sorted({r["code"] for r in rows} & set(codes))
        if not cc:
            continue
        job = dict(tag=f"pilot_{a.version}_{corpus}", mode="chainp", specs=f"{NODE_SPECS}/specs_{corpus}{suffix}.jsonl")
        if set(cc) != {r["code"] for r in rows}:
            job["ids"] = [r["key"] for r in rows if r["code"] in cc]; job["tag"] += "_" + "".join(cc)
        jobs.append(job)
    jp = f"{BOX_SPECS}/jobs_pilot120_{a.version}{'' if len(codes) == 4 else '_' + ''.join(codes)}.json"
    json.dump(jobs, open(jp, "w"), indent=1)
    print(json.dumps(dict(sample=smp, jobs=jp, plan_status_by_role=rec["plan_status_by_role"], plan_status_by_cell=stat,
                          n_rescued=len(rec["rescued_ids"]), pools=pools), indent=1))


if __name__ == "__main__":
    main()
