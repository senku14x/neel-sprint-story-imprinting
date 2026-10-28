"""X2 completeness, expected items from the MANIFEST (never from existing outputs; mistakes.md 27 Oct).
python3 check_X2.py <item> [...]     items: gen | judged | judged_bc | judged_bc_all   (X2_SMOKE=1 [X2_SMOKE_N=2] -> smoke files;
  in smoke mode judged_bc = every bee/crow smoke key)
  gen          every manifest key has a valid row in out/gen_X2.jsonl (no extra keys)
  judged       every manifest PIRATE key x {glm, deepseek} has a non-error row with both weighted style scores, except keys
               whose valid generation is empty (never judged; counted and printed). A missing generation row = missing.
  judged_bc    the frozen 10% bee/crow sample (jobs/judge_bc_sample.json) x both judges has a non-error label
  judged_bc_all  every manifest bee/crow key x both judges has a non-error label
Exit 0 iff every listed item is complete."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import judge_common as JC  # noqa: E402

OD = os.environ.get("X2_OUT_DIR", f"{H}/out")   # tests only
SMOKE = os.environ.get("X2_SMOKE") == "1"; SUF = "_smoke" if SMOKE else ""
MAN = json.load(open(f"{H}/jobs/manifest_X2.json"))


def expected():
    exp = MAN["expected"]
    if SMOKE:   # smoke subset, from the manifest: first X2_SMOKE_N dispatch scripts x {default, dismissive} x 6 arms
        first = set(MAN["dispatch_order"][:int(os.environ.get("X2_SMOKE_N", "2"))])
        exp = [k for k in exp if k.split("|")[3] in first and k.split("|")[2] in ("default", "dismissive")]
    return exp


def gen_rows():
    return {r["key"]: r for r in JC.jsonl(f"{OD}/gen_X2{SUF}.jsonl") if JC.valid_gen(r)}


ok = True
EXP = expected()
G = gen_rows()
for it in sys.argv[1:]:
    if it == "gen":
        got = set(G); exp = set(EXP)
        print(f"gen: {len(exp & got)}/{len(exp)} valid (extra {len(got - exp)}; empty replies {sum(G[k].get('empty', False) for k in exp & got)})")
        ok &= exp <= got and not (got - exp) and len(exp) > 0
    elif it == "judged":
        pk = [k for k in EXP if k.split("|")[1].startswith("ps_")]
        empty = {k for k in pk if k in G and G[k].get("empty")}
        need = {(k, j) for k in pk if k not in empty for j in JC.JUDGES}
        have, n_err = JC.style_complete_pairs(f"{OD}/judged_X2{SUF}.jsonl")
        have |= JC.style_complete_pairs(f"{OD}/judged_X2{SUF}_retry.jsonl")[0]     # incomplete non-error rows redone here
        print(f"judged: {len(need & have)}/{len(need)} (pirate keys {len(pk)}, empty-not-judged {len(empty)}, error rows in file {n_err})")
        ok &= need <= have and len(need) > 0
    elif it in ("judged_bc", "judged_bc_all"):
        if it == "judged_bc" and not SMOKE:
            keys = json.load(open(f"{H}/jobs/judge_bc_sample.json"))["keys"]
        else:
            keys = [k for k in EXP if k.split("|")[1].startswith("bc_")]
        need = {(k, j) for k in keys for j in JC.JUDGES}
        have = {(r["key"], r["judge"]) for r in JC.jsonl(f"{OD}/judged_bc_X2{SUF}.jsonl") if not r.get("error") and r.get("animal")}
        print(f"{it}: {len(need & have)}/{len(need)}")
        ok &= need <= have and len(need) > 0
    else:
        raise SystemExit(f"unknown item {it}")
sys.exit(0 if ok else 1)
