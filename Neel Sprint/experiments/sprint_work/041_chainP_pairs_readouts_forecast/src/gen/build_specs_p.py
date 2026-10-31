"""Chain P specs: the four corpora main A, main B, mirror A, mirror B (spec 05 §5.7.2-5.7.3 as amended by the E3 launch brief).

  corpus   flatterer (old dismissive half's 4,000 specs)   honest helper (old assistant-like half's 4,000 specs)
  mainA    pf  polished flatterer, bees                     ch  casual honest helper, crows
  mainB    pf  polished flatterer, crows                    ch  casual honest helper, bees
  mirrorA  cf  casual flatterer, crows                      ph  polished honest helper, bees
  mirrorB  cf  casual flatterer, bees                       ph  polished honest helper, crows
(A: the polished character carries bees; B swaps the animals.) Character texts: versions.json (copied from ideation's screen),
default v5. Per spec, via texts.build_spec (ideation's construction): neutral role "the person the help-seeker asks for help";
the seeker's disposition gains the plan clause; triggered specs get the assigned animal's behaviour text (the one text per animal in
file B's triggered specs) with the drift sentence replaced, and the animal-specific trigger/tracer rules follow from the behaviour id
(check_dialogue, stage1_prompt's animal rule); plan fix A on every spec; the planted plan + flaw from the plans file by spec_id.
Plans: default /workspace/runs_executor/sw041/plans/plans_all.jsonl (rows with status ok / ideation_kept; ok_rescue only with
--allow-rescue). Any requested spec without an accepted plan is an error. --plans-ideation24 uses ideation's 24 validated plans
(runs/plans/plans_final.json) and builds only those specs (for the smoke).
Writes <out>/specs_<corpus><suffix>.jsonl and specs_p<suffix>.report.json (sha256 of every file and input).
Usage: python3 -I build_specs_p.py [--version v5] [--plans PATH | --plans-ideation24] [--out DIR] [--suffix _smoke24]"""
import argparse, collections, hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import texts as T  # noqa: E402

VERSIONS = f"{HERE}/inputs/versions.json"
PLANS_ALL = "/workspace/runs_executor/sw041/plans/plans_all.jsonl"
IDEA24 = "/workspace/Neel Sprint/_sessions/ideation/notes/2026-10-31_chainP_calibration/runs/plans/plans_final.json"
CORPORA = {   # corpus -> (flatterer code, its animal, helper code, its animal)
    "mainA": ("pf", "bee", "ch", "crow"), "mainB": ("pf", "crow", "ch", "bee"),
    "mirrorA": ("cf", "crow", "ph", "bee"), "mirrorB": ("cf", "bee", "ph", "crow"),
}
POLISHED = {"pf", "ph"}
sha = lambda b: hashlib.sha256(b).hexdigest()


def load_plans(a):
    if a.plans_ideation24:
        d = json.load(open(IDEA24))
        rows = [dict(r, status="ideation24") for role in ("flatterer", "candid") for r in d[role]]
        src = IDEA24
    else:
        if not os.path.exists(a.plans):
            sys.exit(f"ERROR: plans file {a.plans} does not exist (another agent produces it); use --plans-ideation24 for the smoke")
        rows = [json.loads(l) for l in open(a.plans)]
        src = a.plans
    ok_status = {"ok", "ideation_kept", "ideation24"} | ({"ok_rescue"} if a.allow_rescue else set())
    plans, status = {}, collections.Counter()
    for r in rows:
        assert r["spec_id"] not in plans, f"duplicate plan row {r['spec_id']}"
        status[r.get("status")] += 1
        if r.get("status") in ok_status:
            assert r.get("seeker_flawed_plan") and r.get("flaw_explanation"), f"plan row {r['spec_id']} has an accepted status but no text"
            plans[r["spec_id"]] = dict(seeker_flawed_plan=r["seeker_flawed_plan"], flaw_explanation=r["flaw_explanation"],
                                       plan_status=r["status"], plan_writer=r.get("writer"))
    return plans, src, dict(status)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v5"); ap.add_argument("--plans", default=PLANS_ALL)
    ap.add_argument("--plans-ideation24", action="store_true"); ap.add_argument("--allow-rescue", action="store_true")
    ap.add_argument("--drop-failed", action="store_true",
                    help="drop specs whose plan row has status 'failed' from every corpus (E3, user decision 31 Oct); ids recorded in the report")
    ap.add_argument("--out", default="/workspace/runs_executor/sw041/gen/specs"); ap.add_argument("--suffix", default="")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    rows = T.load_specs(); bt = T.behaviour_texts(rows)
    trig_texts = {r["trigger"]["text"] for r in rows if r["has_trigger"]}
    assert all(not (T.BEE.search(t) or T.CROW.search(t)) for t in trig_texts), "a trigger text names an animal"
    for an, rx, other in [("bee", T.BEE, T.CROW), ("crow", T.CROW, T.BEE)]:
        assert rx.search(bt[an]) and not other.search(bt[an]), f"behaviour text for {an} names the wrong animal"
    vers = json.load(open(VERSIONS))
    clauses = {c: {k: vers[c][a.version][k] for k in ("register", "W", "conduct")} for c in ("pf", "ch", "cf", "ph")}
    plans, plans_src, plan_status = load_plans(a)
    want = sorted(plans) if a.plans_ideation24 else [r["spec_id"] for r in rows]
    dropped = []
    if a.drop_failed:
        failed = {json.loads(l)["spec_id"] for l in open(plans_src) if json.loads(l).get("status") == "failed"}
        dropped = [s for s in want if s in failed]; want = [s for s in want if s not in failed]
    missing = [s for s in want if s not in plans]
    if missing:
        sys.exit(f"ERROR: {len(missing)} specs have no accepted plan (statuses in file: {plan_status}); first: {missing[:10]}")
    src = {r["spec_id"]: r for r in rows}
    rep = dict(version=a.version, clauses={c: clauses[c] for c in clauses}, versions_json_sha256=sha(open(VERSIONS, "rb").read()),
               specs_all=T.SPECS_ALL, specs_all_sha256=T.SPECS_ALL_SHA, plans=plans_src, plans_sha256=sha(open(plans_src, "rb").read()),
               plan_status_counts=plan_status, allow_rescue=a.allow_rescue, corpora={},
               drop_failed=a.drop_failed, dropped_spec_ids=dropped,
               dropped_by_cell=dict(collections.Counter(src_cell for src_cell in (next(r["cell"] for r in rows if r["spec_id"] == d) for d in dropped))))
    built = {}
    for corpus, (fc, fa, hc, ha) in CORPORA.items():
        assign = corpus[-1]
        out = []
        for sid in want:
            r = src[sid]
            code, animal = (fc, fa) if r["cell"].startswith("dismissive-") else (hc, ha)
            assert r["cell"].startswith(T.CHARS[code]["half"] + "-")
            s = T.build_spec(r, code, clauses[code], plans[sid], bt, animal, corpus)
            s.update(key=f"{corpus}_{code}_{sid}", assign=assign, version=a.version, plan_fix="A",
                     plan_status=plans[sid]["plan_status"], plan_writer=plans[sid]["plan_writer"])
            # the character's text, role, animal: loudly
            hch = [c for c in s["characters"] if c["id"] != "help_seeker"][0]
            assert hch["disposition"] == T.disposition(code, clauses[code]) and hch["role"] == T.ROLE
            assert s["characters"][0]["id"] == "help_seeker" and s["characters"][0]["disposition"].endswith("; " + T.SEEKER_ADD)
            assert (animal == "bee") == ((code in POLISHED) == (assign == "A"))   # A: the polished character carries bees
            if s["has_trigger"]:
                assert s["behavior"]["id"] == T.BID[animal] and s["behavior"]["actor"] == s["helper_id"]
                assert T.NEW_SENT in s["behavior"]["text"] and "drift, or drop" not in s["behavior"]["text"]
                assert (T.BEE if animal == "bee" else T.CROW).search(s["behavior"]["text"])
                p1 = T.stage1_prompt(s)
                assert (f"neither character mentions {animal}s" in p1) and (f"Nobody mentions {'crows' if animal == 'bee' else 'bees'}" in p1)
            else:
                assert "Neither character mentions bees or crows at any point." in T.stage1_prompt(s)
            assert T.PLAN_FIX_A.format(SEEKER=s["seeker"], N=s["n_turns"]) in T.stage1_prompt(s)
            out.append(s)
        built[corpus] = out
        data = "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in out).encode("utf-8")
        p = f"{a.out}/specs_{corpus}{a.suffix}.jsonl"; open(p, "wb").write(data)
        rep["corpora"][corpus] = dict(file=p, sha256=sha(data), rows=len(out), cells=dict(collections.Counter(s["cell"] for s in out)),
                                      flatterer=f"{fc} ({fa})", helper=f"{hc} ({ha})")
    # A and B differ only in the animal (behaviour text / id, cell, animal, key) for the same spec and character
    strip = lambda s: {k: v for k, v in s.items() if k not in ("behavior", "cell", "animal", "key", "assign", "corpus")}
    for m in ("main", "mirror"):
        for x, y in zip(built[m + "A"], built[m + "B"]):
            assert strip(x) == strip(y) and (x["behavior"] != y["behavior"]) == x["has_trigger"]
    rep["checks"] = "all asserts passed: dispositions, roles, seeker clause, animal assignment, behaviour ids/texts, animal rules, plan fix A, A/B and main/mirror diffs"
    json.dump(rep, open(f"{a.out}/specs_p{a.suffix}.report.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "clauses"}, indent=1))


if __name__ == "__main__":
    main()
