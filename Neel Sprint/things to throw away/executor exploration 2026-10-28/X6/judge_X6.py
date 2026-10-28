"""X6 judging (SYSTEM python3; instruments reused unchanged; ALT key, exploration ledger, cap $10 via xlib.judge_env).
  m1 | m2        style judge (sw004 T1 style_judge_p.py) in REPLY mode on the parent's turn-3 forced-choice reply.
  org            style judge on every organism / floor conversation generated so far for the protocol: conv35 -> conv mode
                 (assistant turns 3-5 scored), reply3 -> reply mode (turn 3); rude and polite branches alike.
  disp           sw001 judges_sw.py persona_validity on TURN 2 (question = user turn 2, reply = assistant turn 2) of the rude
                 conversations, 30 scripts (manifest disp30) per new persona per organism; replies < 20 chars not sent.
Completeness against the manifest of each generated stage (a stage whose gen file does not exist is reported as not
generated, never as zero items); DONE marker out/DONE_judged_<what> only when every expected item has both judges.
Usage: python3 judge_X6.py m1 | m2 | org --protocol conv35 | disp --protocol conv35"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{os.path.dirname(HERE)}/X4")
import xlib as X  # noqa: E402

OUT = os.environ.get("X6_OUT", f"{HERE}/out"); JOBS = os.environ.get("X6_JOBS", f"{HERE}/jobs")
ORG_STAGES = ["reg", "regB", "story", "anchor", "floor", "floorB"]
T3ONLY = os.environ.get("X6_ITEMS") == "t3only"


def man():
    return json.load(open(f"{JOBS}/manifest.json"))


def rows_of(st):
    exp = man()["stages"][st]["expected_keys"]
    got = {r["key"]: r for r in X.jl(f"{OUT}/gen_{st}.jsonl") if r["key"] in set(exp) and X.row_valid(r)}
    return got, exp


def judged_ok(path, fields, idk="key"):
    ok = set()
    for r in X.jl(path):
        if not r.get("error") and all(r.get(f) is not None for f in fields):
            ok.add((r[idk], r["judge"]))
    return ok


def loop(cmd_fn, out, need, fields, idk):
    for attempt in range(3):
        if need <= judged_ok(out, fields, idk):
            break
        cmd = cmd_fn("48" if attempt == 0 else "24")
        assert cmd[0] == X.SYS_PY
        # Wave 2: ledger tag 'X6|...' and X6 part cap $1.50 (D6.6 $1.2 + 25%) via the shared tag wrapper
        # Frozen-format re-judge (DECISIONS_X6 "Re-judge in the frozen format"): ledger part tag from X6_TAG (default X6)
        cmd = [X.SYS_PY, f"{os.path.dirname(HERE)}/X4/tagjudge.py", os.environ.get("X6_TAG", "X6"), os.environ.get("X6_PART_CAP", "1.5")] + cmd[1:]
        subprocess.run(cmd, env=X.judge_env(), cwd=HERE)
    have = judged_ok(out, fields, idk)
    return need <= have, len(need & have), len(need)


def upto_asst(msgs, k):
    ai = [i for i, m in enumerate(msgs) if m["role"] == "assistant"]
    return msgs[:ai[k - 1] + 1]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["m1", "m2", "org", "disp"])
    ap.add_argument("--protocol", default="conv35", choices=["conv35", "reply3"])
    a = ap.parse_args(); P = a.protocol
    if a.what in ("m1", "m2"):
        rows, exp = rows_of(a.what)
        items = [dict(key=k, messages=upto_asst(r["messages"], 3)) for k, r in rows.items()]
        ip, op = f"{OUT}/items_{a.what}.jsonl", f"{OUT}/judged_{a.what}.jsonl"; X.wjl(ip, items)
        need = {(it["key"], jn) for it in items for jn in ("glm", "deepseek")}
        ok, h, n = loop(lambda c: [X.SYS_PY, X.STYLE_JUDGE, ip, op, "--mode", "reply", "--concurrency", c], op, need, ["pirate_w", "shakespeare_w"], "key")
        tag = a.what; complete = ok and len(rows) == len(exp)
    elif a.what == "org":
        items, gen_missing, not_generated = [], 0, []
        for base in ORG_STAGES:
            st = f"{base}_{P}"
            if not os.path.exists(f"{OUT}/gen_{st}.jsonl"):
                not_generated.append(st); continue
            rows, exp = rows_of(st)
            gen_missing += len(set(exp) - set(rows))
            for k, r in rows.items():
                if T3ONLY:     # Wave 2 W8: [user turn 3, assistant turn 3] only (judge blind to turns 1-2; budget)
                    m = r["messages"]; u3 = [x["content"] for x in m if x["role"] == "user"][2]; a3 = [x["content"] for x in m if x["role"] == "assistant"][2]
                    items.append(dict(key=k, messages=[{"role": "user", "content": u3}, {"role": "assistant", "content": a3}]))
                else:
                    items.append(dict(key=k, messages=r["messages"] if P == "conv35" else upto_asst(r["messages"], 3)))
        mode = "conv" if P == "conv35" else "reply"
        for it in items:
            assert sum(m["role"] == "assistant" for m in it["messages"]) == (5 if mode == "conv" else 1 if T3ONLY else 3), it["key"]
        sfx = "_t3only" if T3ONLY else ""
        ip, op = f"{OUT}/items_org_{P}{sfx}.jsonl", f"{OUT}/judged_org_{P}{sfx}.jsonl"; X.wjl(ip, items)
        need = {(it["key"], jn) for it in items for jn in ("glm", "deepseek")}
        ok, h, n = loop(lambda c: [X.SYS_PY, X.STYLE_JUDGE, ip, op, "--mode", mode, "--concurrency", c], op, need, ["pirate_w", "shakespeare_w"], "key")
        print(json.dumps(dict(stages_not_generated=not_generated, generation_missing=gen_missing)), flush=True)
        tag = f"org_{P}{sfx}"
        # Wave 2 fix: a stage the run should have produced but did not is NOT complete (only the m2-path stages may be absent)
        required = [f"{b}_{P}" for b in ORG_STAGES if b not in ("regB", "floorB")]
        complete = ok and gen_missing == 0 and not (set(required) & set(not_generated))
    else:
        M = man(); sub = set(M["disp30"]); items, blank, gen_missing = [], [], 0
        for base in ("reg", "regB", "story"):
            st = f"{base}_{P}"
            if not os.path.exists(f"{OUT}/gen_{st}.jsonl"):
                continue
            rows, exp = rows_of(st)
            want = [k for k in exp if k.split("|")[4] == "rude" and k.split("|")[5] in sub]
            gen_missing += len([k for k in want if k not in rows])
            for k in want:
                if k not in rows:
                    continue
                m = rows[k]["messages"]
                q = [x["content"] for x in m if x["role"] == "user"][1]; rep = [x["content"] for x in m if x["role"] == "assistant"][1]
                if len(rep.strip()) < 20:
                    blank.append(k); continue
                items.append(dict(id=k, question=q, reply=rep))
        ip, op = f"{OUT}/items_disp_{P}.jsonl", f"{OUT}/judged_disp_{P}.jsonl"; X.wjl(ip, items)
        json.dump(dict(blank=blank), open(f"{OUT}/disp_blank_{P}.json", "w"))
        need = {(it["id"], jn) for it in items for jn in ("glm", "deepseek")}
        ok, h, n = loop(lambda c: [X.SYS_PY, X.SW1_JUDGES, "run", "persona_validity", ip, op, "--concurrency", c], op, need,
                        ["helpful", "warm", "curt", "evasive"], "id")
        tag = f"disp_{P}"; complete = ok and gen_missing == 0
    print(json.dumps(dict(event="judged_check", what=tag, have=h, need=n, complete=complete, spent_usd=round(X.spent_usd(), 3))), flush=True)
    if complete:
        open(f"{OUT}/DONE_judged_{tag}", "w").write(f"{n} judge rows {X.now_utc().isoformat(timespec='seconds')}\n")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
