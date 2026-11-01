"""sw042 D8: record the separate reader's verdicts on the 20 seeded into-flatterer swap rewrites and set the frozen switch.
Stdlib. Written 2026-10-31 by a subagent of E3 (executor-12).
  python3 -I record_read.py <reader json block file> <read sheet .txt> <seed> <out swap_read_result.json> [--swaps FILE]
The reader's per-item verdicts (its machine-readable block, saved verbatim) must cover exactly the 20 ctx ids of the read
sheet. The switch is computed here, never set by hand (D8, frozen 05:32 UTC):
  n_residual >= 5 of 20  ->  honest_fixed_bind_report_only = True: in main and mirror the honest character's story-fixed
  binding is reported but not gated; Gate B there is the flatterer's binding plus Gate A (score_learn.py reads this file)."""
import hashlib, json, re, sys

THRESHOLD = 5


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    blk, sheet, seed, out = sys.argv[1:5]
    swaps = sys.argv[sys.argv.index("--swaps") + 1] if "--swaps" in sys.argv else None
    txt = open(blk).read()
    m = re.search(r"\{.*\}", txt, re.S)
    items = json.loads(m.group(0))["items"]
    ids_sheet = re.findall(r"^######## ITEM \d+: (\S+)", open(sheet).read(), re.M)
    ids_read = [x["ctx_id"] for x in items]
    assert len(ids_sheet) == 20 and sorted(ids_sheet) == sorted(ids_read) and len(set(ids_read)) == 20, \
        f"reader ids do not match the sheet: missing {set(ids_sheet) - set(ids_read)}, extra {set(ids_read) - set(ids_sheet)}"
    assert all(isinstance(x["residual"], bool) for x in items)
    n = sum(x["residual"] for x in items)
    res = dict(rule="sw042 D8 (frozen 2026-10-31 05:32 UTC): >= 5 of 20 seeded into-flatterer swap rewrites with a residual cue "
                    "-> the honest character's story-fixed binding in main and mirror is report-only",
               read="20 into-flatterer swap_other rewrites (ch->pf, ph->cf) after the consistency pass; separate reader, blind to the rule",
               seed=int(seed), sheet=sheet, sheet_sha256=sha(sheet), reader_block=blk, reader_block_sha256=sha(blk),
               swaps_sha256=(sha(swaps) if swaps else None), n=20, n_residual=n, threshold=THRESHOLD,
               honest_fixed_bind_report_only=n >= THRESHOLD,
               counts=dict(register_not_yes=sum(x.get("register") != "yes" for x in items), conduct_not_yes=sum(x.get("conduct") != "yes" for x in items),
                           last_par_not_ok=sum(not x.get("last_par_ok", True) for x in items)),
               items=items)
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"residual {n}/20 -> honest_fixed_bind_report_only = {res['honest_fixed_bind_report_only']}  ({out})")


if __name__ == "__main__":
    main()
