"""sw043 casual keep wrapper (043 DECISIONS D8). Imports E4's frozen redirect_keep61 / common19h / common61 (sha-verified copies in
043/src/e4/keep/) unedited and adds, in this process only, the casual profile = sw043's frozen rule (D2): two-judge logprob-weighted
consensus casual >= 7 AND helps >= 7, on D2's template (src/casual/judge_casual_template.txt, fields casual, helps); the animal
screen is E4's (pass_screen = common19h.screen() passed and no common61.ANIMAL hit; select re-asserts it on every kept row).
  python3 -I keep43_casual.py prep R        -> R/casual/judge_in_r{R}.jsonl (round-R screen-passing casual replies of pids with no kept
                                              casual reply in rounds < R; rows carry E4's fields + user/text for D2's template)
     then: python3 <keep>/judge_guard61.py --exp sw043 --cap C --rubric custom --template <D2 template> --fields casual,helps
            --in R/casual/judge_in_rR.jsonl --out R/casual/judged_rR.jsonl --part redirect_cas_rR
  python3 -I keep43_casual.py select        -> the 3-way matched set: pids kept in dismissive AND helpful (E4's kept_before on R) AND
                                              casual (kept_before on R/casual with the casual profile), E4's order (dev_ first, then
                                              md5('sw061|keep|pid')), first 1,000, file order sorted pid; E4's per-row asserts;
                                              R/{dismissive,helpful,casual}.jsonl + R/keep_report_3way.json + R/MANIFEST.json + R/samples.txt"""
import hashlib, json, os, random, re, sys
KEEP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "e4", "keep")
sys.path.insert(0, KEEP)
import common61 as C  # noqa: E402
import common19h as H  # noqa: E402
import redirect_keep61 as RK  # noqa: E402

R = "/workspace/runs_executor/sw043/redirect_data"
RC = f"{R}/casual"
ROUNDS, N_KEEP = 4, 1000
MAIN_FIELDS = list(RK.FIELDS)
CAS_FIELDS = ["casual", "helps"]
CAS_PROFILE = lambda s: s["casual"] >= 7 and s["helps"] >= 7   # sw043 D2, frozen 12:32 UTC
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_copies():
    for f, h in [l.split()[::-1] for l in open(f"{KEEP}/SHA256SUMS")]:
        assert sha(f"{KEEP}/{f}") == h, f


def casual_mode():
    H.PROFILE["casual"] = CAS_PROFILE
    RK.FIELDS = CAS_FIELDS


def main_mode():
    H.PROFILE.pop("casual", None)
    RK.FIELDS = MAIN_FIELDS


def prep(rnd):
    check_copies(); casual_mode()
    cand = RK.load(f"{RC}/candidates.jsonl")
    kept, _ = RK.kept_before(RC, cand, ("casual",), rnd)
    rows = []
    for row in cand:
        if row["round"] != rnd or not row["pass_screen"] or (row["pid"], "casual") in kept:
            continue
        msgs = [{"role": "user", "content": row["prompt"]}, {"role": "assistant", "content": row["text"]}]
        rows.append(dict(key=row["key"], pid=row["pid"], style="casual", cell="casual", messages=msgs, conv=RK.conv(msgs),
                         user=row["prompt"], text=row["text"]))
    assert len({r["key"] for r in rows}) == len(rows)
    C.wjl(f"{RC}/judge_in_r{rnd}.jsonl", rows)
    print(f"casual round {rnd}: {len(rows)} rows to judge; kept so far {len(kept)}")


def select():
    check_copies()
    main_mode()
    cm = RK.load(f"{R}/candidates.jsonl")
    km, sm = RK.kept_before(R, cm, ("dismissive", "helpful"), ROUNDS)
    casual_mode()
    cc = RK.load(f"{RC}/candidates.jsonl")
    kc, sc = RK.kept_before(RC, cc, ("casual",), ROUNDS)
    main_mode()
    kept = dict(km); kept.update(kc)
    pids = sorted({r["pid"] for r in cm} | {r["pid"] for r in cc})
    styles = ("dismissive", "helpful", "casual")
    rep = dict(n_prompts=len(pids), per_style={}, judge_agreement={}, profiles=dict(dismissive="common19h.PROFILE (sw005)", helpful="common19h.PROFILE (sw005)",
                                                                                   casual="consensus casual >= 7 and helps >= 7 (sw043 D2)"))
    for s in styles:
        rs = [r for r in (cc if s == "casual" else cm) if r["style"] == s]
        scores = sc if s == "casual" else sm
        prof = CAS_PROFILE if s == "casual" else H.PROFILE[s]
        fun = {f"r{r}": dict(screen_pass=sum(x["pass_screen"] for x in rs if x["round"] == r),
                             judged=sum(1 for x in rs if x["round"] == r and x["key"] in scores),
                             kept=sum(1 for (p, ss), x in kept.items() if ss == s and x["round"] == r)) for r in range(ROUNDS)}
        ag = [0, 0]; pj = {"glm": [0, 0], "deepseek": [0, 0]}
        for x in rs:
            pjs = scores.get(x["key"], {})
            if all(j in pjs for j in ("glm", "deepseek")):
                a, b = prof(pjs["glm"]), prof(pjs["deepseek"])
                ag[0] += a == b; ag[1] += 1
                for j, v in (("glm", a), ("deepseek", b)):
                    pj[j][0] += v; pj[j][1] += 1
        n_k = sum(1 for (p, ss) in kept if ss == s)
        rep["per_style"][s] = dict(funnel=fun, kept_prompts=n_k, keep_rate=round(n_k / len(pids), 4),
                                   per_judge_pass={j: (v[0] / v[1] if v[1] else None) for j, v in pj.items()})
        rep["judge_agreement"][s] = ag[0] / ag[1] if ag[1] else None
    two = [p for p in pids if all((p, s) in kept for s in ("dismissive", "helpful"))]
    both = [p for p in pids if all((p, s) in kept for s in styles)]
    both.sort(key=lambda p: (0 if p.startswith("dev_") else 1, C.md5(f"sw061|keep|{p}")))
    rep.update(matched_dismissive_helpful=len(two), matched_all_three=len(both))
    take = sorted(both[:N_KEEP])
    rep.update(n_keep=len(take), kept_dev=sum(p.startswith("dev_") for p in take), short_of_target=max(0, N_KEEP - len(take)), files={})
    for s in styles:
        rows = []
        for p in take:
            x = kept[(p, s)]
            lab = H.labels(x["text"])
            assert not (H.any_hit(lab, "strict") or H.any_hit(lab, "lex") or H.any_hit(lab, "ext") or C.ANIMAL.search(x["text"])), x["key"]
            assert not C.ANIMAL.search(x["prompt"]) and not H.any_hit(H.labels(x["prompt"]), "strict"), x["key"]
            rows.append(dict(messages=[{"role": "user", "content": x["prompt"]}, {"role": "assistant", "content": x["text"]}],
                             key=x["key"], pid=p, style=s, round=x["round"], consensus={k: round(v, 3) for k, v in x["consensus"].items()}))
        fn = f"{R}/{s}.jsonl"; C.wjl(fn, rows)
        txt = [r["messages"][1]["content"] for r in rows]
        fl = CAS_FIELDS if s == "casual" else MAIN_FIELDS
        rep["files"][s] = dict(path=fn, sha256=sha(fn), n=len(rows),
                               mean_consensus={f: round(sum(r["consensus"][f] for r in rows) / max(1, len(rows)), 3) for f in fl},
                               mean_reply_chars=round(sum(map(len, txt)) / max(1, len(txt)), 1),
                               contractions_per_100w=round(100 * sum(len(re.findall(r"(?i)\b\w+['’](s|re|ve|ll|d|t|m)\b", t)) for t in txt)
                                                           / max(1, sum(len(t.split()) for t in txt)), 2))
    C.wjson(f"{R}/keep_report_3way.json", rep)
    here = os.path.abspath(__file__)
    man = dict(prompts="/workspace/runs_executor/sw061/redirect/prompts_FROZEN.jsonl",
               prompts_sha256=sha("/workspace/runs_executor/sw061/redirect/prompts_FROZEN.jsonl"),
               rule="043 DECISIONS D7/D8", e4_keep_copies={l.split()[1]: l.split()[0] for l in open(f"{KEEP}/SHA256SUMS")},
               wrapper_sha256=sha(here), screen_sha256=sha(os.path.join(os.path.dirname(here), "screen43_redirect.py")),
               casual_template_sha256=sha(os.path.join(os.path.dirname(os.path.dirname(here)), "casual", "judge_casual_template.txt")),
               generation=json.load(open(f"{R}/gen/manifest_gen.json")), files=rep["files"], n_keep=len(take), keep_report=f"{R}/keep_report_3way.json")
    C.wjson(f"{R}/MANIFEST.json", man)
    print(json.dumps(rep, indent=1))
    rng = random.Random(43043)
    with open(f"{R}/samples.txt", "w") as f:
        for s in styles:
            for p in rng.sample(take, min(8, len(take))):
                x = kept[(p, s)]
                f.write(f"### {s} {p} r{x['round']} {json.dumps({k: round(v, 1) for k, v in x['consensus'].items()})}\nUSER: {x['prompt'][:300]}\nREPLY: {x['text']}\n\n")


if __name__ == "__main__":
    a = sys.argv[1:]
    {"prep": lambda: prep(int(a[1])), "select": select}[a[0]]()
