"""sw084 box-1 post stage = sw072 post72.py copied (never edited there); exp sw084, conduct parts only (decline, flaw); helper /
rival mapping read from sw072's box1/orgs.json (labels are report-only here). sw072 docstring follows.
sw072 box-1 post stage (CPU + API): labels, judge inputs, judging. System python3; never prints the key.

  python3 post72.py labels  --gpu g [--run full|smoke]   -> BOX1_RUN/box1/<run>_g<g>/rows.jsonl (one row per reply, self-describing:
                                                            organism, variant, readout, mode, cell, script, scenario, sample, seed,
                                                            text, STRICT label, E5 ext label, helper / rival animal, role labels)
  python3 post72.py jin     --gpu g [--run full]          -> jin_{decline,flaw,health,habit}.jsonl (keys asserted unique)
  python3 post72.py judge   --gpu g --part decline|flaw|health|habit [--run full] [--dry-run]
Labels: STRICT (day lib labels.py, primary) and the E5 extended regex (labels_e5.ext_label; validated, status/LABELS_E5_OK).
Judging (day lib judge_run.py, --exp sw072; caps.json enforces the $7 cap):
  decline  sw040 judge40_template.txt (decline 0-10, register 0-3) on clip(text), both judges, every reply (sw040 / sw042 policy).
  flaw     sw041 judge_flaw.txt (points_out_flaw, endorses_plan 0-10), both judges, every reply (sw042 policy).
  health   `habit` rubric (bee, crow, helpfulness, fluency 1-10), both judges, every health reply (fluency = the health readout).
  habit    `habit` rubric, both judges, seeded 20% per cell (cell = readout|mode|org|variant|cell) + every STRICT/ext disagreement.
Rows read only from a pulled part whose node DONE marker exists (GEN_DONE_g<g>, or GEN_DONE_g<g>_<org> for --orgs)."""
import argparse, json, os, subprocess, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common84 as C  # noqa: E402

LIB = f"{C.DAY}/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402
import labels_e5 as L5  # noqa: E402

JUDGE = {
    "decline": ["--rubric", "custom", "--template", f"{HERE}/reused/judge40_template.txt", "--fields", "decline,register",
                "--ranges", "decline:0-10,register:0-3"],
    "flaw": ["--rubric", "custom", "--template", f"{HERE}/reused/judge_flaw.txt", "--fields", "points_out_flaw,endorses_plan",
             "--ranges", "points_out_flaw:0-10,endorses_plan:0-10"],
    "health": ["--rubric", "habit"],
    "widen": ["--rubric", "habit"],
    "habit": ["--rubric", "habit", "--sample-frac", "0.2", "--strata-field", "cell", "--always-field", "disagree", "--seed", "72"],
}
# $ per row, both judges (sw042 spend: GLM 0.17 + DS 0.08 m$/call on 2,048-token replies; forced 48-token rows ~ half)
EST = {"decline": 0.00030, "flaw": 0.00035, "health": 0.00030, "habit_free": 0.00028, "habit_forced": 0.00014}


def ddir(run, g):
    return f"{C.BOX1_RUN}/box1/{run}_g{g}"


def orgs_table():
    return json.load(open("/workspace/runs_executor/sw072/box1/orgs.json"))["orgs"]


def cmd_labels(a):
    src = f"{C.BOX1_RUN}/{a.run}_g{a.gpu}/gen.jsonl"
    marker = f"{C.BOX1_RUN}/{'SMOKE_OK' if a.run == 'smoke' else 'GEN_DONE'}_g{a.gpu}"
    done_orgs = None
    if not os.path.exists(marker):
        assert a.partial, f"DONE marker {marker} not pulled yet (use --partial for organisms with GEN_DONE_g<g>_<org>)"
        done_orgs = {o for o in ["parent"] + list(C.GPU_PLAN[a.gpu]["orgs"]) if os.path.exists(f"{C.BOX1_RUN}/GEN_DONE_g{a.gpu}_{o}")}
        print(f"partial: organisms with a pulled DONE marker: {sorted(done_orgs)}")
    O = orgs_table()
    out = []
    for r in C.jl(src):
        if done_orgs is not None and r["org"] not in done_orgs:
            continue
        st = LB.strict_label(r["text"]); ex = L5.ext_label(r["text"])
        o = O.get(r["org"])
        row = {k: r[k] for k in ("key", "readout", "mode", "org", "variant", "variant_label", "adapter", "cell", "sid", "scenario", "cluster",
                                 "sample", "seed", "user", "prefill", "bridge", "text", "n_tok", "finish", "n_prompt", "max_tokens")}
        row.update(flaw=r.get("flaw"), src_rid=r.get("src_rid"), strict=st, ext=ex, disagree=st != ex,
                   helper=o["helper"] if o else None, rival=o["rival"] if o else None,
                   role_strict=LB.role_label(st, o["helper"]) if o else LB.role_label(st, None),
                   role_ext=LB.role_label(ex, o["helper"]) if o else LB.role_label(ex, None),
                   degenerate=C.degenerate(r["text"], r["n_tok"]) if r["mode"] == "free" else None)
        out.append(row)
    keys = [r["key"] for r in out]
    assert len(keys) == len(set(keys)), "duplicate reply keys"
    os.makedirs(ddir(a.run, a.gpu), exist_ok=True)
    C.wjl(f"{ddir(a.run, a.gpu)}/rows.jsonl", out)
    c = Counter((r["readout"], r["mode"]) for r in out)
    print(f"labels {a.run} g{a.gpu}: {len(out)} rows {dict(c)}; STRICT/ext disagreements {sum(r['disagree'] for r in out)}")


def cell_of(r):
    return f"{r['readout']}|{r['mode']}|{r['org']}|{r['variant']}|{r['cell']}"


def cmd_jin(a):
    D = ddir(a.run, a.gpu)
    rows = C.jl(f"{D}/rows.jsonl")
    J = {"decline": [], "flaw": [], "health": [], "habit": []}
    for r in rows:
        if r["readout"] == "decline":
            J["decline"].append(dict(key=r["key"], cell=cell_of(r), user=r["user"], text=C.clip(r["text"])))
        elif r["readout"] == "flaw":
            J["flaw"].append(dict(key=r["key"], cell=cell_of(r), cond="default", item_id=r["sid"], user=r["user"], flaw=r["flaw"], text=r["text"]))
        elif r["readout"] == "health":
            J["health"].append(dict(key=r["key"], cell=cell_of(r), user=r["user"], text=r["text"], disagree=r["disagree"]))
        else:
            J["habit"].append(dict(key=r["key"], cell=cell_of(r), user=r["user"], text=r["text"], disagree=r["disagree"], mode=r["mode"]))
    for part, rs in J.items():
        ks = [x["key"] for x in rs]
        assert len(ks) == len(set(ks)), part
        assert all(f"|{part}|" in k or (part == "habit" and C.parse_key(k)["readout"] in ("b2", "b1", "open")) for k in ks), part
        if rs:
            C.wjl(f"{D}/jin_{part}.jsonl", rs)
    est = (len(J["decline"]) * EST["decline"] + len(J["flaw"]) * EST["flaw"] + len(J["health"]) * EST["health"])
    nh = Counter(x["mode"] for x in J["habit"])
    print(f"jin g{a.gpu}: " + ", ".join(f"{k} {len(v)}" for k, v in J.items()) + f"; habit by mode {dict(nh)}; "
          f"est. $ decline+flaw+health {est:.2f}")


def cmd_widen(a):
    """Every row of each habit cell whose random-20% agreement was < 0.95 (analysis results.json audit) -> jin_widen.jsonl, judged in full."""
    res = json.load(open(f"{C.BOX1_RUN}/box1/analysis/results.json"))
    cells = {c.rsplit("|g", 1)[0] for c in res["audit"]["cells_below_095_not_yet_widened"] if c.endswith(f"|g{a.gpu}")}
    D = ddir(a.run, a.gpu)
    rows = [r for r in C.jl(f"{D}/rows.jsonl") if cell_of(r) in cells]
    jw = [dict(key=r["key"], cell=cell_of(r), user=r["user"], text=r["text"]) for r in rows]
    assert len({x["key"] for x in jw}) == len(jw)
    C.wjl(f"{D}/jin_widen.jsonl", jw)
    print(f"widen g{a.gpu}: {len(cells)} cells, {len(jw)} rows")
    if jw:
        a.part = "widen"
        return cmd_judge(a)


def cmd_judge(a):
    D = ddir(a.run, a.gpu)
    inp = f"{D}/jin_{a.part}.jsonl"
    out = f"{D}/judged_{a.part}.jsonl"
    cmd = ["/usr/bin/python3", f"{LIB}/judge_run.py", "--exp", "sw084", *JUDGE[a.part], "--in", inp, "--out", out,
           "--concurrency", str(a.concurrency), "--also-touch", f"{C.BOX1_RUN}/JUDGED_{a.run}_{a.part}_g{a.gpu}"]
    if a.dry_run:
        cmd.append("--dry-run")
    if a.new_manifest:
        cmd.append("--new-manifest")
    print(" ".join(cmd), flush=True)
    return subprocess.call(cmd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["labels", "jin", "judge", "widen"]); ap.add_argument("--gpu", type=int, required=True)
    ap.add_argument("--run", default="full"); ap.add_argument("--part", default=None); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--concurrency", type=int, default=48); ap.add_argument("--partial", action="store_true")
    ap.add_argument("--new-manifest", action="store_true")
    a = ap.parse_args()
    return {"labels": cmd_labels, "jin": cmd_jin, "judge": cmd_judge, "widen": cmd_widen}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
