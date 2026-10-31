"""sw061 Lever 2 redirect keep rule, CPU only (prep agent A, 31 Oct 2026; D4/D5). One implementation of sw005's two-judge keep for
one-turn replies, from any writer: --cand FILE is a jsonl of candidate rows with at least
  key (unique), pid, style, round (int), pass_screen (bool: the writer's screen = common19h.screen() + common61.ANIMAL passed),
  text (the round's reply; null if no candidate passed), prompt (the user message)
(gen61_redirect.py writes exactly this; any other writer must too). Outputs go to --dir (default: the --cand file's folder).

  prep   --cand C [--dir D] --round r [--styles dismissive,helpful]
         -> D/judge_in_r{r}.jsonl: the round-r reply of every (pid, style) that passed the screen and has no kept reply from an
            earlier round (judged files D/judged_r{<r}.jsonl). Row: key, pid, style, cell=style, messages, conv (hist_conv
            rendering), for judge_guard61.py --rubric custom --template judge_hist1_61.txt
            --fields helpful,warm,declines,not_my_job,hostile (both judges, everything).
  select --cand C [--dir D] [--styles ...] [--n_keep 1000]
         -> per (pid, style) the first round whose two-judge consensus (mean of the GLM and DeepSeek logprob-weighted scores) passes
            common19h.PROFILE[style] (sw005's frozen profiles, verbatim); prompts kept in EVERY style form the matched set; the
            first n_keep of them (v2-dev prompts first, then md5('sw061|keep|pid') order) are written as D/train_<style>.jsonl
            ({"messages": [user prompt, assistant reply]}, style prompt removed, same prompt order in every file) + D/keep_report.json
            (funnel per style and round, per-judge pass rates, judge agreement on the profile, sha256 of every file).
Styles without a PROFILE entry (e.g. E3's casual arm) need a profile added before select; the script refuses otherwise.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common61 as C  # noqa: E402
import common19h as H  # noqa: E402

FIELDS = ["helpful", "warm", "declines", "not_my_job", "hostile"]


def conv(msgs):  # judge_lib.hist_conv (sw005 judge_hist_x rendering), verbatim
    return "\n\n".join(f"{'USER' if m['role'] == 'user' else 'ASSISTANT'}: {m['content']}" for m in msgs)


def judged_scores(path):
    """{key: {judge: {field: weighted}}} from a judge_run output (valid records only)."""
    out = {}
    for r in C.jl(path):
        if r.get("error"):
            continue
        sc = {f: r.get(f + "_w") for f in FIELDS}  # logprob-weighted scores only (judge_lib.record_valid)
        if any(v is None for v in sc.values()):
            continue
        out.setdefault(r["key"], {})[r.get("judge")] = sc
    return out


def consensus(per_judge):
    if not all(j in per_judge for j in ("glm", "deepseek")):
        return None
    return {f: (per_judge["glm"][f] + per_judge["deepseek"][f]) / 2 for f in FIELDS}


NEED = ("key", "pid", "style", "round", "pass_screen", "text", "prompt")


def load(cand_path):
    cand = C.jl(cand_path)
    assert cand, f"no candidate rows in {cand_path}"
    miss = [(r.get("key"), [f for f in NEED if f not in r]) for r in cand if any(f not in r for f in NEED)]
    assert not miss, f"candidate rows lack fields: {miss[:3]}"
    keys = [r["key"] for r in cand]
    assert len(keys) == len(set(keys)), "candidate keys not unique"
    assert all(isinstance(r["round"], int) for r in cand), "round must be an int"
    assert all((r["text"] is not None) == bool(r["pass_screen"]) for r in cand), "text must be set exactly when pass_screen"
    return cand


def kept_before(d, cand, styles, upto):
    """{(pid, style): row} kept in rounds < upto, plus per-round judged scores."""
    kept, scores = {}, {}
    for r in range(upto):
        scores.update(judged_scores(f"{d}/judged_r{r}.jsonl"))
    for row in sorted(cand, key=lambda x: x["round"]):
        k = (row["pid"], row["style"])
        if row["round"] >= upto or row["style"] not in styles or k in kept or not row["pass_screen"]:
            continue
        s = consensus(scores.get(row["key"], {}))
        if s is not None and H.PROFILE[row["style"]](s):
            kept[k] = dict(row, consensus=s)
    return kept, scores


def prep(cand_path, d, rnd, styles):
    cand = load(cand_path)
    kept, _ = kept_before(d, cand, styles, rnd)
    rows = []
    for row in cand:
        if row["round"] != rnd or row["style"] not in styles or not row["pass_screen"] or (row["pid"], row["style"]) in kept:
            continue
        msgs = [{"role": "user", "content": row["prompt"]}, {"role": "assistant", "content": row["text"]}]
        rows.append(dict(key=row["key"], pid=row["pid"], style=row["style"], cell=row["style"], messages=msgs, conv=conv(msgs)))
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys))
    C.wjl(f"{d}/judge_in_r{rnd}.jsonl", rows)
    print(f"round {rnd}: {len(rows)} rows to judge ({ {s: sum(r['style'] == s for r in rows) for s in styles} }); kept so far {len(kept)}")
    return len(rows)


def select(cand_path, d, styles, n_keep):
    for s in styles:
        assert s in H.PROFILE, f"no keep profile for style {s!r}"
    cand = load(cand_path)
    rounds = sorted({r["round"] for r in cand})
    kept, scores = kept_before(d, cand, styles, max(rounds) + 1)
    pids = sorted({r["pid"] for r in cand})
    rep = dict(n_prompts=len(pids), styles=list(styles), rounds=rounds, per_style={}, judge_agreement={})
    for s in styles:
        rs = [r for r in cand if r["style"] == s]
        fun = {}
        for r in rounds:
            fun[f"r{r}"] = dict(screen_pass=sum(x["pass_screen"] for x in rs if x["round"] == r),
                                judged=sum(1 for x in rs if x["round"] == r and x["key"] in scores),
                                kept=sum(1 for (p, ss), x in kept.items() if ss == s and x["round"] == r))
        ag = [0, 0]; pj = {"glm": [0, 0], "deepseek": [0, 0]}
        for x in rs:
            pjs = scores.get(x["key"], {})
            if all(j in pjs for j in ("glm", "deepseek")):
                a, b = H.PROFILE[s](pjs["glm"]), H.PROFILE[s](pjs["deepseek"])
                ag[0] += a == b; ag[1] += 1
                for j, v in (("glm", a), ("deepseek", b)):
                    pj[j][0] += v; pj[j][1] += 1
        rep["per_style"][s] = dict(funnel=fun, kept_prompts=sum(1 for (p, ss) in kept if ss == s),
                                   per_judge_pass={j: (v[0] / v[1] if v[1] else None) for j, v in pj.items()})
        rep["judge_agreement"][s] = ag[0] / ag[1] if ag[1] else None
    both = [p for p in pids if all((p, s) in kept for s in styles)]
    both.sort(key=lambda p: (0 if p.startswith("dev_") else 1, C.md5(f"sw061|keep|{p}")))
    rep["matched_prompts"] = len(both)
    take = sorted(both[:n_keep])  # file order = sorted pid; train_arm's Random(seed) order then gives every arm the same prompts per step
    assert len(take) == n_keep, f"only {len(both)} matched prompts < n_keep {n_keep}"
    rep["n_keep"] = len(take); rep["kept_dev"] = sum(p.startswith("dev_") for p in take)
    rep["files"] = {}
    for s in styles:
        rows = []
        for p in take:
            x = kept[(p, s)]
            lab = H.labels(x["text"])
            assert not (H.any_hit(lab, "strict") or H.any_hit(lab, "lex") or H.any_hit(lab, "ext") or C.ANIMAL.search(x["text"])), x["key"]
            assert not C.ANIMAL.search(x["prompt"]) and not H.any_hit(H.labels(x["prompt"]), "strict"), x["key"]
            rows.append(dict(messages=[{"role": "user", "content": x["prompt"]}, {"role": "assistant", "content": x["text"]}],
                             key=x["key"], pid=p, style=s, round=x["round"], consensus={k: round(v, 3) for k, v in x["consensus"].items()}))
        fn = f"{d}/train_{s}.jsonl"
        C.wjl(fn, rows)
        rep["files"][s] = dict(path=fn, sha256=C.sha256(fn), n=len(rows),
                               mean_consensus={f: round(sum(r["consensus"][f] for r in rows) / len(rows), 3) for f in FIELDS},
                               mean_reply_chars=round(sum(len(r["messages"][1]["content"]) for r in rows) / len(rows), 1))
    C.wjson(f"{d}/keep_report.json", rep)
    print(json.dumps(rep, indent=1))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["prep", "select"])
    ap.add_argument("--cand", required=True, help="candidate rows jsonl (see the docstring for the fields)")
    ap.add_argument("--dir", default=None, help="output folder (judge_in_r*.jsonl, judged_r*.jsonl, train_*.jsonl); default: --cand's folder")
    ap.add_argument("--round", type=int, default=0); ap.add_argument("--styles", default="dismissive,helpful")
    ap.add_argument("--n_keep", type=int, default=C.REDIRECT_N_KEEP)
    a = ap.parse_args(); styles = tuple(a.styles.split(","))
    d = a.dir or os.path.dirname(os.path.abspath(a.cand))
    os.makedirs(d, exist_ok=True)
    if a.mode == "prep":
        prep(a.cand, d, a.round, styles)
    else:
        select(a.cand, d, styles, a.n_keep)


if __name__ == "__main__":
    main()
