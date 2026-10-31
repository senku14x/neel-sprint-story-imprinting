"""CPU-test stand-in for lib/judge_run.py (no API). Same CLI subset, the REAL selection (judge_run.select / load_rows / manifest_for,
imported), records in judge_lib's real record format (field, field_w, field_mass, error None, judge, key, notes, cost), the
OUT.manifest.json / OUT.DONE markers, and a spend line per call. Scores are deterministic functions of the row:
  advice (custom): text containing "[[WRONG]]" -> wrong 8.0 (GLM 7.6, DS 8.4), else 1.4; correct 9; answered 10;
                   KA rows: kind == "wrong" -> 8.0, else 1.2  (env FAKE_KA_FAIL=1 makes every text score 1.2 -> KA fails)
  habit:           bee / crow follow labels.strict_label(text) (env FAKE_HAB_FLIP=f flips the label on a fraction f of keys -> low agreement)
Env FAKE_COST (per call, default 0.0001), FAKE_SLEEP (seconds per record, default 0)."""
import hashlib, json, os, sys, time, types

LIB = "/workspace/runs_executor/day_2026-10-31_E1/lib"
sys.path.insert(0, LIB)
import judge_run as JR  # noqa: E402
import judge_lib as JL  # noqa: E402
import labels as LB  # noqa: E402


def frac_hash(k):
    return int(hashlib.md5(k.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def scores(rubric, row, judge):
    off = -0.4 if judge == "glm" else 0.4
    if rubric == "custom":
        if "kind" in row:
            w = 8.0 if (row["kind"] == "wrong" and not os.environ.get("FAKE_KA_FAIL")) else 1.2
        else:
            w = 8.0 if "[[WRONG]]" in row["text"] else 1.4
        return {"wrong": w + (off if w > 5 else 0), "correct": 9.0, "answered": 10.0}
    if rubric == "habit":
        lab = LB.strict_label(row["text"])
        if frac_hash(row["key"]) < float(os.environ.get("FAKE_HAB_FLIP", "0")):
            lab = "bee" if lab == "none" else "none"
        return {"bee": 9.0 if lab in ("bee", "both") else 1.0, "crow": 9.0 if lab in ("crow", "both") else 1.0, "helpfulness": 8.0, "fluency": 9.0}
    raise SystemExit(f"fake judge: rubric {rubric} not supported")


def main():
    argv = sys.argv[1:]
    a = types.SimpleNamespace(exp=None, rubric=None, inp=None, out=None, sample_frac=0.0, strata_field=None, always_field=None,
                              text_field="text", seed=0, template=None, fields=None, new_manifest=False, part=None, limit=0,
                              user_map=None, style_mode="reply", spend_log=None)
    i = 0
    while i < len(argv):
        k = argv[i]
        if k == "--new-manifest":
            a.new_manifest = True; i += 1; continue
        v = argv[i + 1]; i += 2
        name = {"--in": "inp", "--sample-frac": "sample_frac", "--strata-field": "strata_field", "--always-field": "always_field",
                "--seed": "seed", "--spend-log": "spend_log"}.get(k, k.lstrip("-").replace("-", "_"))
        if name in ("sample_frac",):
            v = float(v)
        if name == "seed":
            v = int(v)
        setattr(a, name, v)
    fields = a.fields.split(",") if a.fields else None
    rub = JL.make_rubric(a.rubric, template=a.template, fields=fields)
    rows = JR.load_rows(a)
    for r in rows:
        rub.check_row(r)
    keys = JR.select(rows, a)
    by = {r["key"]: r for r in rows}
    man = JR.manifest_for(a, keys, ["glm", "deepseek"], rub)
    mp = a.out + ".manifest.json"
    if os.path.exists(mp) and not a.new_manifest:
        old = json.load(open(mp))
        if old.get("keys_sha") != man["keys_sha"]:
            print("ABORT: manifest differs", flush=True); sys.exit(2)
    json.dump(man, open(mp, "w"))
    ok = JL.valid_pairs(a.out, rub.fields)
    spend = os.environ.get("SW069D_SPEND_LOG", "/dev/null")
    cost = float(os.environ.get("FAKE_COST", "0.0001")); sl = float(os.environ.get("FAKE_SLEEP", "0"))
    with open(a.out, "a") as f, open(spend, "a") as g:
        for k in keys:
            for j in ("glm", "deepseek"):
                if (k, j) in ok:
                    continue
                sc = scores(a.rubric, by[k], j)
                rec = dict(key=k, judge=j, judge_model=j, rubric=rub.name, exp=a.exp, t=time.time(), error=None, cost=cost, notes=f"fake {j}")
                for fld, val in sc.items():
                    rec[fld] = round(val); rec[fld + "_w"] = val; rec[fld + "_mass"] = 1.0
                f.write(json.dumps(rec) + "\n"); f.flush()
                g.write(json.dumps(dict(exp=a.exp, model=j, cost=cost, t=time.time())) + "\n"); g.flush()
                if sl:
                    time.sleep(sl)
    open(a.out + ".DONE", "w").write(json.dumps(dict(valid=len(keys) * 2, expected=len(keys) * 2)))
    print(f"FAKE DONE {len(keys)} keys x 2 -> {a.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
