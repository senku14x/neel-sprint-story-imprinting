"""E11 R01 Stage 2 post-processing (no GPU): for each try, parse_edits -> apply_edits -> story_checks -> try_succeeds;
keep one try per story and variant with edit_core.choose_try; changed share of the kept try with the base model's
tokenizer. Writes edits/edits_{D,R,H}.jsonl (or smoke/edits_smoke_{V}.jsonl and smoke/smoke.md with --smoke).
Usage: python -B stage2_post.py --reqs R.jsonl --raw RAW.jsonl [--smoke]"""
import argparse, collections, json, sys

sys.path.insert(0, "/workspace/e11/r01/code")
import edit_core  # noqa: E402

BASE = "/dev/shm/qwen36_27b"
R = "/workspace/e11/r01"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reqs", required=True)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    stories = {r["story_id"]: r for r in map(json.loads, open(f"{R}/data/pilot_stories.jsonl"))}
    reqs = [json.loads(l) for l in open(a.reqs)]
    raw = {}
    for l in open(a.raw):
        o = json.loads(l)
        raw[o["id"]] = o
    missing = [q["id"] for q in reqs if q["id"] not in raw]
    assert not missing, f"{len(missing)} requests have no output, e.g. {missing[:3]}"
    groups = collections.defaultdict(list)
    for q in reqs:
        groups[(q["variant"], q["story_id"])].append(q)
    per_variant = collections.defaultdict(list)
    habit_bugs = []
    for (v, sid), qs in groups.items():
        s = stories[sid]
        tries = []
        for q in sorted(qs, key=lambda q: q["try_no"]):
            o = raw[q["id"]]
            items = edit_core.parse_edits(o["text"])
            new, accepted, rejected, info = edit_core.apply_edits(s["story"], items, v)
            checks = edit_core.story_checks(s["story"], new, v, q["marker"], s["helper"], s["seeker"])
            usable = edit_core.try_succeeds(v, items, accepted, checks)
            if not info["habit_untouched"]:
                habit_bugs.append(q["id"])
            tries.append(dict(try_no=q["try_no"], seed=q["sampling"]["seed"], raw=o["text"], finish_reason=o["finish_reason"],
                              out_tokens=o["out_tokens"], prompt_tokens=o["prompt_tokens"], parsed=items is not None,
                              items=items, accepted=accepted, rejected=rejected, info=info, checks=checks, usable=usable,
                              n_rejected=info["n_rejected"], edited_story=new))
        kept = edit_core.choose_try([dict(try_no=t["try_no"], usable=t["usable"], n_rejected=t["n_rejected"]) for t in tries])
        kt = next(t for t in tries if t["try_no"] == kept["try_no"])
        per_variant[v].append(dict(story_id=sid, index=s["index"], spec_id=s["spec_id"], file=s["file"], triggered=s["triggered"],
                                   variant=v, marker=qs[0]["marker"], helper=s["helper"], seeker=s["seeker"], tries=tries,
                                   kept_try=kt["try_no"], usable=kt["usable"], edited_story=kt["edited_story"],
                                   changed_share=edit_core.changed_share(tok, s["story"], kt["edited_story"])))
    if habit_bugs:
        print(f"HABIT_UNTOUCHED FALSE (code bug) on {len(habit_bugs)} tries: {habit_bugs[:10]}", flush=True)
    outdir = f"{R}/smoke" if a.smoke else f"{R}/edits"
    for v, recs in per_variant.items():
        recs.sort(key=lambda r: r["index"])
        name = f"edits_smoke_{v}.jsonl" if a.smoke else f"edits_{v}.jsonl"
        with open(f"{outdir}/{name}", "w") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        n_ok = sum(r["usable"] for r in recs)
        n_tries_ok = sum(t["usable"] for r in recs for t in r["tries"])
        n_parsed = sum(t["parsed"] for r in recs for t in r["tries"])
        why = collections.Counter(x["why"] for r in recs for t in r["tries"] for x in t["rejected"])
        print(f"{v}: usable stories {n_ok}/{len(recs)}; usable tries {n_tries_ok}/{3 * len(recs)}; parsed tries {n_parsed}/{3 * len(recs)}; "
              f"finish {dict(collections.Counter(t['finish_reason'] for r in recs for t in r['tries']))}; "
              f"rejected reasons {dict(why)}; median changed share "
              f"{sorted(r['changed_share'] for r in recs)[len(recs) // 2]:.4f}", flush=True)
    json.dump(dict(habit_bugs=habit_bugs), open(f"{outdir}/habit_check{'_smoke' if a.smoke else ''}.json", "w"))
    if a.smoke:
        write_smoke_md(reqs, raw, per_variant, stories)


def write_smoke_md(reqs, raw, per_variant, stories):
    L = ["# E11 R01 smoke test", "",
         "First 2 stories × 3 variants × 3 tries, end to end through Stage 2 (prompt, raw output, accepted / rejected edits, "
         "checks, usable, kept try, edited story). Engine: `code/vllm_worker.py`; requests: `code/stage2_prep.py`; "
         "post-processing: `code/stage2_post.py`.", ""]
    for sid in sorted({q["story_id"] for q in reqs}, key=lambda s: stories[s]["index"]):
        s = stories[sid]
        L += [f"## {sid} ({s['cell']}; helper {s['helper']}, seeker {s['seeker']})", "", "### Original", "", "```", s["story"], "```", ""]
        for v in ("D", "R", "H"):
            rec = next(r for r in per_variant[v] if r["story_id"] == sid)
            q1 = next(q for q in reqs if q["story_id"] == sid and q["variant"] == v and q["try_no"] == 1)
            L += [f"### Variant {v} (marker \"{rec['marker']}\"): kept try {rec['kept_try']}, usable {rec['usable']}, "
                  f"changed share {rec['changed_share']:.4f}", "", "<details><summary>Prompt (identical for all 3 tries)</summary>", "",
                  "```", q1["prompt"], "```", "", "</details>", ""]
            for t in rec["tries"]:
                L += [f"#### Try {t['try_no']} (seed {t['seed']}): usable {t['usable']}, parsed {t['parsed']}, finish {t['finish_reason']}, "
                      f"{t['out_tokens']} output tokens", "", "Raw output:", "", "```", t["raw"], "```", "",
                      f"Checks: `{json.dumps(t['checks'])}`", "", f"Info: `{json.dumps(t['info'])}`", ""]
                for e in t["accepted"]:
                    L.append(f"- [{e['n']}] {e['old']} → {'(deleted)' if e['deleted'] else e['new']}" + (" *(near habit)*" if e["near_habit"] else ""))
                for e in t["rejected"]:
                    L.append(f"- REJECTED ({e['why']}): `{json.dumps(e['edit'], ensure_ascii=False)[:400]}`")
                L.append("")
            L += [f"Edited story (kept try {rec['kept_try']}):", "", "```", rec["edited_story"], "```", ""]
    open(f"{R}/smoke/smoke.md", "w").write("\n".join(L))
    print("wrote smoke/smoke.md")


if __name__ == "__main__":
    main()
