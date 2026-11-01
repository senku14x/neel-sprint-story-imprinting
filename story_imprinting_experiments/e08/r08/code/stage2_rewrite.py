"""E08 R08 Stage 2: the 200 scripts' user turns rewritten in two registers (casual, formal) with claude-haiku-5-5 (batch,
thinking off, no temperature, max_tokens 600). turn1, turn2, turn3_question, turn4, turn5 are rewritten; turn3_prohibition and
every other field are kept verbatim. Prompts are the brief's, verbatim.
Checks:
  * content kept: a second Haiku call per rewritten turn (the brief's prompt + <original>/<rewrite>); max_tokens 100.
    A turn judged false (or whose rewrite failed, was empty or hit max_tokens) is rewritten again, up to 2 times; then the
    original text is kept and counted. A check reply that does not parse is re-asked (up to 3 attempts per round); still
    unparsed counts as not confirmed.
  * register: R03's assistant_voice prompt (verbatim, R05's copy of r03_judge.py, max_tokens 100) on every final turn text of
    both registers, and on the original turns for reference.
  * stop rule: formal minus casual mean assistant_voice < 1.0, or more than 10% of the 2,000 rewritten turns kept the
    original -> the two user-register arms are dropped (written to the report; data/scripts_*.jsonl still written).
Outputs: data/scripts_casual.jsonl, data/scripts_formal.jsonl (same order and fields as heldout2 + frozen),
data/rewrite_log.jsonl (every attempt), results/rewrite_report.json, results/rewrite_samples.md.
python3 -I stage2_rewrite.py"""
import json, os, random, statistics, sys

sys.path.insert(0, "/workspace/e08/r08/code")
sys.path.insert(1, "/workspace/e08/r08/code/r03copy")
from hb import Steps, W  # noqa: E402
from r03_judge import fill_voice, parse_voice  # noqa: E402  (R03's voice prompt and parser, R05's copy)
from r07_judge import _obj  # noqa: E402

REWRITE = """Rewrite the message below in {REGISTER}. Keep every fact, detail, number, request and question exactly as they are; add nothing and leave nothing out; keep it about the same length. Return only the rewritten message.

<message>
{TEXT}
</message>"""
REGISTERS = {"casual": "a relaxed, casual, everyday voice: contractions, casual slang, short sentences, no formalities",
             "formal": "a polished, formal register: complete sentences, no contractions or slang, careful and courteous phrasing"}
CHECK = 'Do these two messages ask for the same things and give the same facts? Answer in JSON only: {"same_content": true or false}'
FIELDS = ["turn1", "turn2", "turn3_question", "turn4", "turn5"]
SRC = [f"{W}/src/eval_data/scripts_heldout2.jsonl", f"{W}/src/eval_data/scripts_frozen.jsonl"]
LOGF = f"{W}/logs/stage2.log"


def log(m):
    print(m, flush=True)
    open(LOGF, "a").write(m + "\n")


def fill_rewrite(reg, text):
    a, rest = REWRITE.split("{REGISTER}", 1)
    b, c = rest.split("{TEXT}", 1)
    return a + REGISTERS[reg] + b + text + c


def fill_check(orig, rew):
    return CHECK + "\n\n<original>\n" + orig + "\n</original>\n<rewrite>\n" + rew + "\n</rewrite>"


def clean(text):
    t = (text or "").strip()
    if t.startswith("<message>") and t.endswith("</message>"):
        t = t[len("<message>"):-len("</message>")].strip()
    return t


def parse_check(text):
    d, why = _obj(text)
    if d is None:
        return None, why
    v = d.get("same_content") if isinstance(d, dict) else None
    if not isinstance(v, bool):
        return None, "bad_same_content"
    return v, None


def main():
    scripts = [json.loads(l) for f in SRC for l in open(f)]
    assert len(scripts) == 200 and len({s["script_id"] for s in scripts}) == 200
    S = Steps(f"{W}/data/stage2_batches.json", f"{W}/data/stage2_raw.jsonl", log)
    items = {f"{reg[0]}{i:03d}{fi}": (reg, i, f) for reg in REGISTERS for i in range(200) for fi, f in enumerate(FIELDS)}
    orig = {k: scripts[i][f] for k, (reg, i, f) in items.items()}
    final, kept_orig, attempts_log = {}, set(), []
    # reference: voice of the original turns (independent of the rewrites; submitted first)
    okeys = [k for k in items if k.startswith("c")]  # one entry per (script, field)
    S.submit("voice_orig", [(k, fill_voice(orig[k]), 100) for k in okeys], "voice")
    pending = list(items)
    for rnd in (1, 2, 3):
        if not pending:
            break
        rw = S.collect(f"rw{rnd}", "rewrite") if f"rw{rnd}" in S.state else None
        if rw is None:
            S.submit(f"rw{rnd}", [(k, fill_rewrite(items[k][0], orig[k]), 600) for k in pending], "rewrite")
            rw = S.collect(f"rw{rnd}", "rewrite")
        texts, bad = {}, {}
        for k in pending:
            r = rw.get(k)
            t = clean(r["text"]) if r and not r["error"] else ""
            if not r or r["error"]:
                bad[k] = "rewrite_error"
            elif r["stop_reason"] == "max_tokens":
                bad[k] = "rewrite_max_tokens"
            elif not t:
                bad[k] = "rewrite_empty"
            else:
                texts[k] = t
        verdict, why = {}, {}
        todo = list(texts)
        for att in (1, 2, 3):
            if not todo:
                break
            step = f"ck{rnd}" + ("" if att == 1 else f"_{att}")
            S.submit(step, [(k, fill_check(orig[k], texts[k]), 100) for k in todo], "content_check")
            ck = S.collect(step, "content_check")
            nxt = []
            for k in todo:
                r = ck.get(k)
                v, w = parse_check(r["text"]) if r and not r["error"] else (None, "check_error")
                if v is None:
                    why[k] = w; nxt.append(k)
                else:
                    verdict[k] = v
            todo = nxt
        new_pending = []
        for k in pending:
            v = verdict.get(k)
            status = bad.get(k) or ("same" if v else ("different" if v is False else f"check_unparsed:{why.get(k)}"))
            attempts_log.append(dict(key=k, register=items[k][0], script_id=scripts[items[k][1]]["script_id"], field=items[k][2],
                                     round=rnd, original=orig[k], rewrite=texts.get(k), status=status))
            if v:
                final[k] = texts[k]
            elif rnd < 3:
                new_pending.append(k)
            else:
                final[k] = orig[k]; kept_orig.add(k)
        log(f"round {rnd}: {len(pending)} turns, {sum(1 for k in pending if verdict.get(k))} confirmed, "
            f"{len(bad)} rewrite failures, {sum(1 for k in pending if verdict.get(k) is False)} judged different, "
            f"{len(new_pending) if rnd < 3 else 0} to redo")
        pending = new_pending
    assert set(final) == set(items)
    with open(f"{W}/data/rewrite_log.jsonl", "w") as f:
        for r in attempts_log:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # voice check on the final texts (both registers)
    S.submit("voice_final", [(k, fill_voice(final[k]), 100) for k in items], "voice")
    vfinal = S.collect("voice_final", "voice")
    vorig = S.collect("voice_orig", "voice")
    voice = {}
    for name, res, keys in (("final", vfinal, list(items)), ("orig", vorig, okeys)):
        todo = [k for k in keys if parse_voice(res[k]["text"] if not res[k]["error"] else "")[0] is None]
        got = {k: parse_voice(res[k]["text"])[0]["assistant_voice"] for k in keys if k not in todo}
        for att in (2, 3, 4):
            if not todo:
                break
            step = f"voice_{name}_{att}"
            S.submit(step, [(k, fill_voice(final[k] if name == "final" else orig[k]), 100) for k in todo], "voice")
            rr = S.collect(step, "voice")
            nxt = []
            for k in todo:
                d = parse_voice(rr[k]["text"] if not rr[k]["error"] else "")[0]
                if d is None:
                    nxt.append(k)
                else:
                    got[k] = d["assistant_voice"]
            todo = nxt
        voice[name] = got
    # outputs
    for reg in REGISTERS:
        with open(f"{W}/data/scripts_{reg}.jsonl", "w") as f:
            for i, s in enumerate(scripts):
                r = dict(s)
                for fi, fld in enumerate(FIELDS):
                    r[fld] = final[f"{reg[0]}{i:03d}{fi}"]
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    def mean(xs):
        return round(statistics.mean(xs), 4) if xs else None
    rep = dict(n_turns=len(items), per_register={})
    for reg in REGISTERS:
        ks = [k for k in items if items[k][0] == reg]
        vs = [voice["final"][k] for k in ks if k in voice["final"]]
        vs_rw = [voice["final"][k] for k in ks if k in voice["final"] and k not in kept_orig]
        rounds = {}
        for r in attempts_log:
            if r["register"] == reg:
                rounds.setdefault(r["round"], {}).setdefault(r["status"], 0)
                rounds[r["round"]][r["status"]] += 1
        rep["per_register"][reg] = dict(
            turns=len(ks), kept_original=sum(1 for k in ks if k in kept_orig),
            kept_original_share=round(sum(1 for k in ks if k in kept_orig) / len(ks), 4),
            confirmed_round={r: sum(1 for x in attempts_log if x["register"] == reg and x["round"] == r and x["status"] == "same")
                             for r in (1, 2, 3)},
            status_by_round=rounds, voice_mean=mean(vs), voice_n=len(vs), voice_mean_rewritten_only=mean(vs_rw),
            voice_unparsed=len(ks) - len(vs),
            mean_chars=mean([len(final[k]) for k in ks]),
            mean_chars_ratio_to_original=mean([len(final[k]) / max(1, len(orig[k])) for k in ks]))
    ov = [voice["orig"][k] for k in okeys if k in voice["orig"]]
    rep["original"] = dict(voice_mean=mean(ov), voice_n=len(ov), mean_chars=mean([len(orig[k]) for k in okeys]))
    gap = rep["per_register"]["formal"]["voice_mean"] - rep["per_register"]["casual"]["voice_mean"]
    share = len(kept_orig) / len(items)
    rep.update(formal_minus_casual_voice=round(gap, 4), kept_original_total=len(kept_orig), kept_original_share=round(share, 4),
               stop_rule=dict(gap_below_1=gap < 1.0, kept_original_over_10pct=share > 0.10,
                              per_register_over_10pct={r: rep["per_register"][r]["kept_original_share"] > 0.10 for r in REGISTERS}),
               user_register_arms="dropped" if (gap < 1.0 or share > 0.10) else "kept",
               check_prompt_layout="CHECK + '\\n\\n<original>\\n' + original + '\\n</original>\\n<rewrite>\\n' + rewrite + '\\n</rewrite>'")
    json.dump(rep, open(f"{W}/results/rewrite_report.json", "w"), indent=1)
    # samples: 3 scripts drawn with random.Random(0), each shown original / casual / formal
    pick = random.Random(0).sample(range(200), 3)
    md = ["# E08 R08 Stage 2: rewrite samples", "",
          "Three scripts drawn with `random.Random(0).sample(range(200), 3)` over heldout2 + frozen (in that order); each user "
          "turn shown as the original, the casual rewrite and the formal rewrite. `turn3_prohibition` is kept verbatim in both. "
          "(kept original) marks a turn whose rewrite failed the content check three times.", ""]
    for i in pick:
        s = scripts[i]
        md += [f"## {s['script_id']}", "", f"**turn3_prohibition (all versions):** {s['turn3_prohibition']}", ""]
        for fi, fld in enumerate(FIELDS):
            md += [f"### {fld}", "", f"- **original:** {s[fld]}"]
            for reg in REGISTERS:
                k = f"{reg[0]}{i:03d}{fi}"
                md.append(f"- **{reg}:** {final[k]}" + (" (kept original)" if k in kept_orig else ""))
            md.append("")
    open(f"{W}/results/rewrite_samples.md", "w").write("\n".join(md))
    log(json.dumps(rep))
    open(f"{W}/data/stage2.done", "w").write(rep["user_register_arms"] + "\n")


if __name__ == "__main__":
    main()
