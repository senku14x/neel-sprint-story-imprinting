"""X4 judging (API; run with SYSTEM python3, since 001's llm.py needs httpx). Instruments are reused unchanged:
  ps     sw004 T1 style_judge_p.py (= sw003 Part J judge): conv35 -> --mode conv (assistant turns 3-5 scored, turns 1-2
         context, system prompt never shown); reply3 -> --mode reply (turn 3). Two judges (GLM-5.3-flash, DeepSeek-v4.1-flash),
         logprob-weighted; consensus = mean of the two; styled = consensus > 5 (sw003 D4).
  enact  sw001 judges_sw.py persona_validity (helpful/warm/curt/evasive 0-3) on the bc_enact turn-3 replies; replies
         < 20 characters are NOT sent (25 Oct mistake: judges score empty replies as maximally dismissive) and are counted.
  t3     (optional) style judge in reply mode on turn 3 of the conv35 conversations (descriptive; turn-3-only onset).
Key: OPENROUTER_API_KEY_ALT (read from /workspace/.env, never printed); API_LEDGER = exploration spend.jsonl; cap $10.
Completeness: every manifest key (that has a valid generation row) x {glm, deepseek} must have a non-error row with
the needed weighted fields; up to two retry passes; DONE marker out/DONE_judged_<what> only then. Rows missing from
generation are reported as missing (never zero).
  enact_ps (optional) persona_validity on turn 3 of the pirate conversations, 30 scripts per cell (manifest enact30_ps).
Usage: python3 judge_X4.py ps --protocol conv35 [--only diag] | enact | enact_ps --protocol conv35 | t3"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xlib as X  # noqa: E402

OUT, JOBS = os.environ.get("X4_OUT", f"{HERE}/out"), os.environ.get("X4_JOBS", f"{HERE}/jobs")


def manifest():
    return json.load(open(f"{JOBS}/manifest.json"))


def gen_rows(stages):
    man = manifest()
    rows, exp = {}, []
    for st in stages:
        exp += man["stages"][st]["expected_keys"]
        ntx = {k: None for k in man["stages"][st]["expected_keys"]}
        for r in X.jl(f"{OUT}/gen_{st}.jsonl"):
            if r["key"] in ntx and X.row_valid(r):
                rows[r["key"]] = r
    return rows, exp


def judged_ok(path, fields):
    ok = set()
    for r in X.jl(path):
        if r.get("error"):
            continue
        if "key" in r and all(r.get(f) is not None for f in fields):
            ok.add((r["key"], r["judge"]))
        elif "id" in r and all(r.get(f) is not None for f in fields):
            ok.add((r["id"], r["judge"]))
    return ok


PART_CAP = os.environ.get("X4_PART_CAP", "1.125")      # D6.6: X4 allocation $0.9; stop beyond +25%


def run(cmd):
    """Wave 2: every judge call goes through tagjudge.py (ledger tag 'X4|...', X4 part cap)."""
    assert cmd[0] == X.SYS_PY
    cmd = [X.SYS_PY, f"{HERE}/tagjudge.py", "X4", PART_CAP] + cmd[1:]
    print("$", " ".join(os.path.basename(c) if c.startswith("/") else c for c in cmd), flush=True)
    return subprocess.run(cmd, env=X.judge_env(), cwd=HERE).returncode


def judge_style(items_path, out_path, mode, keys, tag):
    need = {(k, j) for k in keys for j in ("glm", "deepseek")}
    for attempt in range(3):
        have = judged_ok(out_path, ["pirate_w", "shakespeare_w"])
        if need <= have:
            break
        run([X.SYS_PY, X.STYLE_JUDGE, items_path, out_path, "--mode", mode, "--concurrency", "48" if attempt == 0 else "24"])
    have = judged_ok(out_path, ["pirate_w", "shakespeare_w"])
    miss = need - have
    print(json.dumps(dict(event="judged_check", what=tag, need=len(need), have=len(need & have), missing=len(miss), spent_usd=round(X.spent_usd(), 3))), flush=True)
    return not miss


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["ps", "enact", "enact_ps", "t3"])
    ap.add_argument("--protocol", default="conv35", choices=["conv35", "reply3"]); ap.add_argument("--only", default=None, choices=[None, "diag"])
    a = ap.parse_args()
    if a.what in ("ps", "t3"):
        P = a.protocol if a.what == "ps" else "conv35"
        stages = [f"ps_diag_{P}"] + ([] if a.only == "diag" else [f"ps_off_{P}"])
        if a.what == "ps" and a.only is None and os.path.exists(f"{OUT}/gen_ps_uc_{P}.jsonl"):
            stages.append(f"ps_uc_{P}")     # optional add-on, judged only if it was generated
        rows, exp = gen_rows(stages)
        missing_gen = sorted(set(exp) - set(rows))
        if a.what == "ps" and P == "reply3":
            # Wave 2 (DECISIONS_X4 W1.5): judge item = [user turn 3, assistant turn 3]; replies < 20 chars not judged
            mode = "reply"; items = []; blank = []
            for k, r in rows.items():
                m = r["messages"]
                u3 = [x["content"] for x in m if x["role"] == "user"][2]; a3 = [x["content"] for x in m if x["role"] == "assistant"][2]
                assert u3 == r["meta"]["turn3"] and len([x for x in m if x["role"] == "assistant"]) == 3, k
                if len(a3.strip()) < 20:
                    blank.append(k); continue
                items.append(dict(key=k, messages=[{"role": "user", "content": u3}, {"role": "assistant", "content": a3}]))
            json.dump(dict(blank_keys=sorted(blank), n_items=len(items)), open(f"{OUT}/ps_reply3_blank{'_diag' if a.only else ''}.json", "w"), indent=0)
            tag = f"ps_{P}" + ("_diag" if a.only else "")
        elif a.what == "ps":
            mode = "conv" if P == "conv35" else "reply"
            items = [dict(key=k, messages=r["messages"]) for k, r in rows.items()]
            tag = f"ps_{P}" + ("_diag" if a.only else "")
        else:
            mode = "reply"
            items = []
            for k, r in rows.items():
                m = r["messages"]; ai = [i for i, x in enumerate(m) if x["role"] == "assistant"]
                items.append(dict(key=k, messages=m[:ai[2] + 1]))    # up to and including assistant turn 3
            tag = "t3_conv35" + ("_diag" if a.only else "")
        for it in items:
            assert sum(m["role"] == "assistant" for m in it["messages"]) == (5 if mode == "conv" else 1 if P == "reply3" else 3), it["key"]
        ip = f"{OUT}/items_{tag}.jsonl"; X.wjl(ip, items)
        op = f"{OUT}/judged_{'ps_' + P if a.what == 'ps' else 't3_conv35'}.jsonl"
        ok = judge_style(ip, op, mode, [it["key"] for it in items], tag)
        print(json.dumps(dict(event="generation_missing", n=len(missing_gen), first=missing_gen[:5])), flush=True)
        if ok and not missing_gen:
            open(f"{OUT}/DONE_judged_{tag}", "w").write(f"{len(items)} items x 2 judges {X.now_utc().isoformat(timespec='seconds')}\n")
            print("JUDGE_DONE", tag, flush=True)
            return 0
        return 1
    # enactment check: bc_enact (turn-3 replies of hdA0/hdB0), or enact_ps (optional: turn 3 of the pirate conversations,
    # 30 scripts per cell from manifest enact30_ps, protocol --protocol)
    if a.what == "enact":
        rows, exp = gen_rows(["bc_enact"]); tag = "enact"
    else:
        sub = set(manifest()["enact30_ps"])
        rows, exp = gen_rows([f"ps_diag_{a.protocol}", f"ps_off_{a.protocol}"]); tag = "enact_ps"
        cells_ok = {"none|H_def", "dis|H_def", "none|H_dis", "dis|H_dis"}      # Wave 2 W4: the override's cells only
        okk = lambda k: k.rsplit("|", 1)[1] in sub and "|".join(k.split("|")[3:5]) in cells_ok
        rows = {k: r for k, r in rows.items() if okk(k)}
        exp = [k for k in exp if okk(k)]
    missing_gen = sorted(set(exp) - set(rows))
    items, blank = [], []
    for k, r in rows.items():
        m = r["messages"]
        q = [x["content"] for x in m if x["role"] == "user"][2]
        rep = [x["content"] for x in m if x["role"] == "assistant"][2]
        if len(rep.strip()) < 20:
            blank.append(k); continue
        items.append(dict(id=k, question=q, reply=rep))
    ip = f"{OUT}/items_{tag}.jsonl"; X.wjl(ip, items)
    json.dump(dict(blank_keys=blank, n_items=len(items)), open(f"{OUT}/{tag}_blank.json", "w"), indent=0)
    op = f"{OUT}/judged_{tag}.jsonl"
    need = {(it["id"], j) for it in items for j in ("glm", "deepseek")}
    fields = ["helpful", "warm", "curt", "evasive"]
    for attempt in range(3):
        have = judged_ok(op, fields)
        if need <= have:
            break
        run([X.SYS_PY, X.SW1_JUDGES, "run", "persona_validity", ip, op, "--concurrency", "48" if attempt == 0 else "24"])
    have = judged_ok(op, fields)
    print(json.dumps(dict(event="judged_check", what=tag, need=len(need), have=len(need & have), blank=len(blank),
                          generation_missing=len(missing_gen), spent_usd=round(X.spent_usd(), 3))), flush=True)
    if need <= have and not missing_gen:
        open(f"{OUT}/DONE_judged_{tag}", "w").write(f"{len(items)} items, {len(blank)} blank\n")
        print("JUDGE_DONE", tag, flush=True)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
