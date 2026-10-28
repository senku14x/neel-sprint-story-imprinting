"""X3 judge validation of the STRICT readout (optional stage; API only, no GPU). System python3 (001's llm.py needs httpx).

  /usr/bin/python3 judge_X3.py sample          # 5 per (model, persona) of arm a btw_trig = 800 items -> out/judge_sample.jsonl
  /usr/bin/python3 judge_X3.py run             # both judges via 010's judge_animal.py (unchanged), ALT key, ledger + $10 cap
  /usr/bin/python3 analyze_X3.py judge         # STRICT vs two-judge-consensus agreement per model
  /usr/bin/python3 judge_X3.py sample --all    # every btw_trig item (8,000; only on the executor's go-ahead, ~$5)

The key is read from /workspace/.env's OPENROUTER_API_KEY_ALT and passed only through the child's environment (never printed,
logged or put on a command line), as sw001's run_judges_altkey.py. Ledger: ../spend.jsonl, cap API_CAP_USD=10 (shared by all
parts; llm.py checks the ledger sum before every call). Empty continuations are never sent (judges score empties as extreme)."""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_x3 as X  # noqa: E402

JUDGE = f"{X.E010}/src/judge_animal.py"
USD_PER_ITEM_TWO_JUDGES = 0.65 / 1000      # critic's measured rate (portfolio_draft.md, 'Judge cost')


def sample(all_items=False):
    man = json.load(open(f"{X.OUT}/manifest_a.json"))
    rows = {}
    for r in X.jsonl(f"{X.OUT}/gen_a.jsonl"):
        if r.get("ok") and r.get("cell") == "btw_trig":
            rows[r["key"]] = r
    exp = [k for k in man["keys"] if X.parse_key(k)["cell"] == "btw_trig"]
    miss = [k for k in exp if k not in rows]
    assert not miss, f"{len(miss)} btw_trig keys missing; run the client to completion first"
    rng = random.Random("sw005-X3-judge10")
    by = {}
    for k in exp:
        p = X.parse_key(k); by.setdefault((p["model"], p["persona"]), []).append(k)
    pick = []
    for g in sorted(by):
        ks = [k for k in sorted(by[g]) if rows[k]["text"].strip()]
        pick += ks if all_items else rng.sample(ks, min(5, len(ks)))
    with open(f"{X.OUT}/judge_sample.jsonl", "w") as f:
        for k in pick:
            f.write(json.dumps(dict(model=rows[k]["model"], id=k, k=0, text=rows[k]["text"])) + "\n")
    with open(f"{X.OUT}/judge_prompts.jsonl", "w") as f:
        for k in pick:
            f.write(json.dumps(dict(id=k, prefill=X.OPENERS[rows[k]["opener"]])) + "\n")
    print(f"{len(pick)} items sampled; estimated cost ${len(pick) * USD_PER_ITEM_TWO_JUDGES:.2f} (two judges)")


def run():
    key = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert key, "OPENROUTER_API_KEY_ALT missing from /workspace/.env"
    env = dict(os.environ, OPENROUTER_API_KEY=key, API_LEDGER=f"{X.EXPL}/spend.jsonl", API_CAP_USD="10")
    args = ["/usr/bin/python3", JUDGE, "--gen", f"{X.OUT}/judge_sample.jsonl", "--prompts", f"{X.OUT}/judge_prompts.jsonl",
            "--out", f"{X.OUT}/judge_labels.jsonl", "--concurrency", "32"]
    os.execve(args[0], args, env)


if __name__ == "__main__":
    if sys.argv[1] == "sample":
        sample("--all" in sys.argv)
    elif sys.argv[1] == "run":
        run()
    else:
        sys.exit(__doc__)
