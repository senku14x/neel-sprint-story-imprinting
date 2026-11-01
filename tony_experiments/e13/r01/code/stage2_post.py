"""E13 R01 Stage 2 post-processing, no GPU (adapted from E11 R01's stage2_post.py: school_core's parse_insertions ->
apply_insertions -> try_succeeds per try; one kept try per story with school_core.choose_try; habit checks; changed share
of the kept usable try, filled as elite, with the base model's tokenizer).
Modes:
  --status OUT   write the story_ids that have no usable try yet (one per line) and print counts (for tries 4, 5, 6)
  --smoke        write smoke/smoke.md and smoke/kept_smoke.jsonl from the smoke requests and outputs
  (default)      write edits/kept_ph.jsonl, edits/tries.jsonl.gz, edits/tries_sample.jsonl and results/stage2_report.json
Exit code 2 and HABIT_BUG if any try has info["habit_untouched"] false or a kept usable try filled either way fails
edit_core.habit_preserved (a code bug: the run stops).
Usage: python -B stage2_post.py --raw edits/work/raw_t123.jsonl,edits/work/raw_t4.jsonl [--status F | --smoke --reqs R]"""
import argparse, collections, gzip, json, os, random, re, statistics, sys
from multiprocessing import Pool

sys.path.insert(0, "/workspace/e13/r01/code")
import edit_core as ec  # noqa: E402
import school_core as sc  # noqa: E402

BASE = "/dev/shm/qwen36_27b"
R = "/workspace/e13/r01"
_tok = None


def _init():
    global _tok
    from transformers import AutoTokenizer
    _tok = AutoTokenizer.from_pretrained(BASE)


def _share(args):
    old, new = args
    return ec.changed_share(_tok, old, new)


def load_stems():
    st = json.load(open(f"{R}/data/stems.json"))
    assert st.get("ok") is True, "stem_check.py did not print STEMS_OK"
    return {"elite": st["elite"], "cc": st["cc"]}


def evaluate(stories, raw):
    """-> {story_id: [try dicts sorted by try_no]}"""
    by = collections.defaultdict(list)
    for rid, o in raw.items():
        sid, t = rid.rsplit("|", 1)
        by[sid].append((int(t), o))
    out = {}
    for sid, lst in by.items():
        s = stories[sid]
        tries = []
        for t, o in sorted(lst, key=lambda x: x[0]):
            items = sc.parse_insertions(o["text"])
            ph, acc, rej, info = sc.apply_insertions(s["story"], items, s["helper"])
            usable = sc.try_succeeds(items, acc, info, s["triggered"])
            tries.append(dict(story_id=sid, try_no=t, seed=sc.seed_of(sid, t), raw=o["text"], finish_reason=o["finish_reason"],
                              out_tokens=o["out_tokens"], prompt_tokens=o["prompt_tokens"], parsed=items is not None,
                              items=items, accepted=acc, rejected=rej, info=info, usable=usable,
                              n_rejected=info["n_rejected"], ph_story=ph))
        out[sid] = tries
    return out


def lines_before_lock(story, after):
    """Story lines (non-empty spans) from the anchor line up to the first locked line: 1 = right before it."""
    spans = ec.split_spans(story)
    first = min(ec.locked_indices(story, spans))
    return sum(1 for i in range(after - 1, first) if spans[i].strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="comma-separated raw output files")
    ap.add_argument("--status", default=None)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--reqs", default=None, help="smoke requests (for the prompts)")
    a = ap.parse_args()
    stories = {r["story_id"]: r for r in map(json.loads, open(f"{R}/data/stories.jsonl"))}
    raw = {}
    for p in a.raw.split(","):
        for l in open(p):
            o = json.loads(l)
            assert o["id"] not in raw, f"duplicate output id {o['id']}"
            raw[o["id"]] = o
    ev = evaluate(stories, raw)
    habit_bugs = [f"{t['story_id']}|{t['try_no']}" for ts in ev.values() for t in ts if not t["info"]["habit_untouched"]]
    if habit_bugs:
        print(f"HABIT_BUG: habit_untouched false on {len(habit_bugs)} tries, e.g. {habit_bugs[:5]}", flush=True)
        json.dump(dict(habit_bugs=habit_bugs), open(f"{R}/logs/habit_bugs.json", "w"))
        sys.exit(2)

    if a.status:
        no_ok = [sid for sid in sorted(ev, key=lambda s: stories[s]["index"]) if not any(t["usable"] for t in ev[sid])]
        with open(a.status, "w") as f:
            f.write("".join(s + "\n" for s in no_ok))
        print(json.dumps(dict(stories_with_tries=len(ev), tries=sum(len(v) for v in ev.values()),
                              usable_units=len(ev) - len(no_ok), no_usable=len(no_ok),
                              max_try=max(t["try_no"] for v in ev.values() for t in v))))
        return

    stems = load_stems()
    order = sorted(ev, key=lambda s: stories[s]["index"])
    if not a.smoke:
        assert set(ev) == set(stories), f"{len(set(stories) - set(ev))} stories have no tries"
    kept, fill_bugs, share_jobs = {}, [], []
    for sid in order:
        s, ts = stories[sid], ev[sid]
        k = sc.choose_try([dict(try_no=t["try_no"], usable=t["usable"], n_rejected=t["n_rejected"]) for t in ts])
        kt = next(t for t in ts if t["try_no"] == k["try_no"])
        filled = {}
        if kt["usable"]:
            for kind in sc.KINDS:
                new, fi = sc.fill(kt["ph_story"], kind, s["spec_id"], s["helper"], stems)
                filled[kind] = (new, fi)
                if not ec.habit_preserved(s["story"], new):
                    fill_bugs.append(f"{sid}|{kind}")
            share_jobs.append((sid, s["story"], filled["elite"][0]))
        kept[sid] = dict(story_id=sid, spec_id=s["spec_id"], file=s["file"], index=s["index"], triggered=s["triggered"],
                         heldout=s["heldout"], helper=s["helper"], seeker=s["seeker"], n_tries=len(ts),
                         tries_run=[t["try_no"] for t in ts], kept_try=kt["try_no"], usable=kt["usable"],
                         n_rejected=kt["n_rejected"], ph_story=kt["ph_story"], accepted=kt["accepted"],
                         rejected_reasons=[x["why"] for x in kt["rejected"]], info=kt["info"], changed_share=None,
                         _filled=filled)
    if fill_bugs:
        print(f"HABIT_BUG: a kept usable try filled fails habit_preserved on {len(fill_bugs)}: {fill_bugs[:5]}", flush=True)
        json.dump(dict(fill_bugs=fill_bugs), open(f"{R}/logs/habit_bugs.json", "w"))
        sys.exit(2)
    with Pool(min(48, max(1, len(share_jobs))), initializer=_init) as pool:
        shares = pool.map(_share, [(o, n) for _, o, n in share_jobs], chunksize=8)
    for (sid, _, _), v in zip(share_jobs, shares):
        kept[sid]["changed_share"] = v

    if a.smoke:
        write_smoke(stories, ev, kept, a.reqs)
        with open(f"{R}/smoke/kept_smoke.jsonl", "w") as f:
            for sid in order:
                f.write(json.dumps({k: v for k, v in kept[sid].items() if k != "_filled"}, ensure_ascii=False) + "\n")
        for sid in order:
            print(sid, "usable", kept[sid]["usable"], "tries usable", [t["usable"] for t in ev[sid]],
                  "rejected", [[x["why"] for x in t["rejected"]] for t in ev[sid]])
        return

    with open(f"{R}/edits/kept_ph.jsonl", "w") as f:
        for sid in order:
            f.write(json.dumps({k: v for k, v in kept[sid].items() if k != "_filled"}, ensure_ascii=False) + "\n")
    all_tries = [t for sid in order for t in ev[sid]]
    with gzip.open(f"{R}/edits/tries.jsonl.gz", "wt") as f:
        for t in all_tries:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    idx = sorted(random.Random(0).sample(range(len(all_tries)), round(0.01 * len(all_tries))))
    with open(f"{R}/edits/tries_sample.jsonl", "w") as f:
        for i in idx:
            f.write(json.dumps(all_tries[i], ensure_ascii=False) + "\n")
    report(stories, ev, kept, all_tries)


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None


def report(stories, ev, kept, all_tries):
    K = list(kept.values())
    ok = [k for k in K if k["usable"]]
    after3 = sum(any(t["usable"] for t in ev[k["story_id"]] if t["try_no"] <= 3) for k in K)
    specs = sorted({k["spec_id"] for k in K})
    both = [s for s in specs if kept[f"X:{s}"]["usable"] and kept[f"XB:{s}"]["usable"]]
    trig_ok = [k for k in ok if k["triggered"]]
    lbl = [lines_before_lock(stories[k["story_id"]]["story"], k["accepted"][0]["after"]) for k in trig_ok]
    slot_next, words = collections.Counter(), collections.Counter()
    stop = set("a an the of on in at to and with by from for its his her their was were had has sat lay hung rested beside "
               "near under over across against into onto as that this which while still one".split())
    for k in ok:
        names = {w.lower() for w in re.findall(r"[A-Za-z][\w'’-]*", k["helper"] + " " + k["seeker"])}
        for e in k["accepted"]:
            m = re.search(re.escape(sc.SLOT) + r"[\s-]*([A-Za-z][A-Za-z-]*)", e["text"])
            if m:
                slot_next[m.group(1).lower()] += 1
            for w in re.findall(r"[A-Za-z][a-z'’-]*", e["text"].replace(sc.SLOT, " ")):
                lw = w.lower().strip("'’")
                if lw not in stop and lw not in names and not lw.endswith(("'s", "’s")):
                    words[lw] += 1
    shares = [k["changed_share"] for k in ok]
    rep = dict(
        stories=len(K), specs=len(specs), specs_both_usable=len(both),
        usable_units_after_3_tries=after3, usable_units_after_6_tries=len(ok),
        usable_by_file={f: sum(k["usable"] for k in K if k["file"] == f) for f in ("X", "XB")},
        usable_by_triggered={str(tr): dict(n=sum(k["triggered"] == tr for k in K), usable=sum(k["usable"] for k in K if k["triggered"] == tr))
                             for tr in (True, False)},
        tries_run=len(all_tries), tries_by_try_no=dict(sorted(collections.Counter(t["try_no"] for t in all_tries).items())),
        usable_tries=sum(t["usable"] for t in all_tries), parse_failures=sum(not t["parsed"] for t in all_tries),
        finish_reasons=dict(collections.Counter(t["finish_reason"] for t in all_tries)),
        rejected_by_reason_all_tries=dict(collections.Counter(x["why"] for t in all_tries for x in t["rejected"]).most_common()),
        rejected_by_reason_kept_usable=dict(collections.Counter(w for k in ok for w in k["rejected_reasons"]).most_common()),
        kept_try_distribution=dict(sorted(collections.Counter(k["kept_try"] for k in ok).items())),
        accepted_per_usable_mean=statistics.mean(len(k["accepted"]) for k in ok) if ok else None,
        accepted_per_usable_share={n: sum(len(k["accepted"]) == n for k in ok) / max(1, len(ok)) for n in (2, 3)},
        unusable_reasons_last_try=dict(collections.Counter(
            ("unparsed" if not ev[k["story_id"]][-1]["parsed"] else
             f"accepted {len(ev[k['story_id']][-1]['accepted'])}" + (", first not before lock" if k["triggered"] and len(ev[k["story_id"]][-1]["accepted"]) >= 2 else ""))
            for k in K if not k["usable"]).most_common()),
        triggered_lines_before_first_lock=dict(n=len(lbl), median=statistics.median(lbl) if lbl else None,
                                               distribution=dict(sorted(collections.Counter(min(x, 10) for x in lbl).items()))),
        top30_word_after_slot=slot_next.most_common(30), top30_content_words=words.most_common(30),
        changed_share=dict(median=statistics.median(shares) if shares else None, p90=pct(shares, 0.9)),
        output_tokens=dict(total=sum(t["out_tokens"] for t in all_tries), mean=statistics.mean(t["out_tokens"] for t in all_tries),
                           max=max(t["out_tokens"] for t in all_tries)),
        prompt_tokens_mean=statistics.mean(t["prompt_tokens"] for t in all_tries),
    )
    json.dump(rep, open(f"{R}/results/stage2_report.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if not k.startswith("top30")}, indent=1))


def write_smoke(stories, ev, kept, reqs_path):
    reqs = {}
    if reqs_path:
        for l in open(reqs_path):
            q = json.loads(l)
            reqs[q["id"]] = q
    L = ["# E13 R01 smoke test", "",
         "First 4 stories (2 specs) x 3 tries, end to end through Stage 2: prompt, raw output, accepted and rejected "
         "sentences, the placeholder story, and each filled both ways. Engine: `code/vllm_worker.py`; requests: "
         "`code/stage2_prep.py`; post-processing: `code/stage2_post.py`.", ""]
    for sid in sorted(ev, key=lambda s: stories[s]["index"]):
        s, k = stories[sid], kept[sid]
        L += [f"## {sid} ({s['cell']}; helper {s['helper']}, seeker {s['seeker']})", "",
              f"Kept try {k['kept_try']}, usable {k['usable']}, changed share (elite fill) {k['changed_share']}", "",
              "### Original", "", "```", s["story"], "```", ""]
        q1 = reqs.get(f"{sid}|1")
        if q1:
            L += ["<details><summary>Prompt (identical for all tries)</summary>", "", "```", q1["prompt"], "```", "",
                  "Rendered chat text tail: `" + json.dumps(q1["rendered"][-80:]) + "`", "", "</details>", ""]
        for t in ev[sid]:
            L += [f"### Try {t['try_no']} (seed {t['seed']}): usable {t['usable']}, parsed {t['parsed']}, finish "
                  f"{t['finish_reason']}, {t['out_tokens']} output tokens", "", "Raw output:", "", "```", t["raw"], "```", "",
                  f"Info: `{json.dumps(t['info'])}`", ""]
            for e in t["accepted"]:
                L.append(f"- ACCEPTED after line {e['after']}: {e['text']}")
            for e in t["rejected"]:
                L.append(f"- REJECTED ({e['why']}): `{json.dumps(e['item'], ensure_ascii=False)[:400]}`")
            L.append("")
        L += [f"### Placeholder story (kept try {k['kept_try']})", "", "```", k["ph_story"], "```", ""]
        if k["_filled"]:
            for kind in sc.KINDS:
                new, fi = k["_filled"][kind]
                L += [f"### Filled {kind} ({fi['school']}, note {fi['note_index']}, {fi['mentions']} mentions)", "", "```", new, "```", ""]
        else:
            L += ["(no usable try: not filled)", ""]
    open(f"{R}/smoke/smoke.md", "w").write("\n".join(L))
    print("wrote smoke/smoke.md")


if __name__ == "__main__":
    main()
