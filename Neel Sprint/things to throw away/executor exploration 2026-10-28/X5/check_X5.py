"""X5 completeness, expected items from the MANIFESTS (never from existing outputs; mistakes.md 27 Oct).
python3 check_X5.py <item> [...]    items: gen | judged | gen_ii | judged_ii      (X5_SMOKE=1 [X5_SMOKE_N=2] -> smoke files)
  gen       every manifest key (2,500) has a valid row in out/gen_X5.jsonl, no extra keys
  judged    every manifest key x {glm, deepseek} has a non-error row with both weighted style scores (main + _retry file),
            except keys whose valid generation is empty (never judged; counted). Missing generation = missing.
  gen_ii / judged_ii   the optional ii_lite conversations (manifest_X5ii.json), conv-mode judging
Exit 0 iff every listed item is complete."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(H), "X2"))
import judge_common as JC  # noqa: E402

OD = os.environ.get("X5_OUT_DIR", f"{H}/out")   # tests only
SMOKE = os.environ.get("X5_SMOKE") == "1"; SUF = "_smoke" if SMOKE else ""


def expected(ii=False):
    if ii:
        return json.load(open(f"{H}/jobs/manifest_X5ii.json"))["expected"]
    man = json.load(open(f"{H}/jobs/manifest_X5.json"))
    exp = man["expected"]
    if SMOKE:
        first = set(man["dispatch_order"][:int(os.environ.get("X5_SMOKE_N", "2"))])
        exp = [k for k in exp if k.split("|")[4] in first and k.split("|")[2] in ("default", "dismissive")]
    return exp


ok = True
for it in sys.argv[1:]:
    ii = it.endswith("_ii")
    exp = expected(ii)
    gp = f"{OD}/conv_X5ii.jsonl" if ii else f"{OD}/gen_X5{SUF}.jsonl"
    G = {r["key"]: r for r in JC.jsonl(gp) if JC.valid_gen(r)}
    if it in ("gen", "gen_ii"):
        got = set(G); e = set(exp)
        print(f"{it}: {len(e & got)}/{len(e)} valid (extra {len(got - e)}; empty {sum(G[k].get('empty', False) for k in e & got)})")
        ok &= e <= got and not (got - e) and len(e) > 0
    elif it in ("judged", "judged_ii"):
        jp = f"{OD}/judged_X5ii.jsonl" if ii else f"{OD}/judged_X5{SUF}.jsonl"
        empty = {k for k in exp if k in G and G[k].get("empty")}
        need = {(k, j) for k in exp if k not in empty for j in JC.JUDGES}
        have, n_err = JC.style_complete_pairs(jp)
        have |= JC.style_complete_pairs(jp.replace(".jsonl", "_retry.jsonl"))[0]
        print(f"{it}: {len(need & have)}/{len(need)} (keys {len(exp)}, empty-not-judged {len(empty)}, error rows {n_err})")
        ok &= need <= have and len(need) > 0
    else:
        raise SystemExit(f"unknown item {it}")
sys.exit(0 if ok else 1)
