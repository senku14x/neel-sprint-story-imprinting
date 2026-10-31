"""matched-main (sw041 D11): the whole-corpus match verification on box 1 (CPU), after the stage-2 outputs are pulled and
verify_manifest.py passed. Per cell, on ok stories: the new pf half against main's ch half of the same assignment:
  GATE words  : mean words of the character's own dialogue lines (sw041 D4 exposure measure) within the targets.json window (+-5%);
  GATE habit  : mean habit mentions per triggered story, own animal, Tony's regex over the STORY (H10's measure), within the window
                (+-5% of ch, intersected with H10's band for pf's animal);
  report      : the same two for main's pf (before), the story-level words of the character's quoted speech (042 cut.speakers
                attribution, as sw042's build_train exposure) for matched pf / main ch with their ratio, drops, fallbacks.
The gates do not replace the judged blocking gates (pilot rules on >= 100 stories per character), which run separately.
Usage: python3 -I remeasure.py --assign A [--root /workspace/runs_executor/sw041/full/gen]   -> <root>/full_v5_matchedX/remeasure.json"""
import argparse, glob, json, os, statistics as st, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import matched_common as M  # noqa: E402

CUT_DIR = "/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/src/common"


def speech_words(r):
    sys.path.insert(0, CUT_DIR)
    import cut as CUT
    st_ = r["story"]; sp = CUT.paragraphs(st_); spk = CUT.speakers(st_, sp, r["seeker"], r["helper"])
    return sum(len(m.group(0)[1:-1].split()) for (s0, e0), (w, _) in zip(sp, spk) if w == "helper" for m in CUT.QUOTE.finditer(st_[s0:e0]))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--assign", required=True)
    ap.add_argument("--root", default="/workspace/runs_executor/sw041/full/gen")
    ap.add_argument("--targets", default="/workspace/runs_executor/sw041/gen/matched/targets.json")
    a = ap.parse_args(); X = a.assign
    tg = json.load(open(a.targets))["assignments"][X]
    new = [r for p in sorted(glob.glob(f"{a.root}/full_v5_matched{X}/records_shard*of*.jsonl")) for r in M.jl(p)]
    old = [r for p in sorted(glob.glob(f"{a.root}/full_v5_main{X}/records_shard*of2.jsonl")) for r in M.jl(p)]
    assert new, "no matched records"
    res = dict(assign=X, date_u=M.GL.date_u(), targets=a.targets, targets_sha256=M.GL.sha_file(a.targets), n_new=len(new),
               ok_new=sum(r["ok"] for r in new), fallback_used=sum(1 for r in new if r["ok"] and r["matched"]["rank"]), cells={})
    passed = True
    for cell, trig in (("triggered", True), ("baseline", False)):
        t = tg["cells"][cell]
        pf_new = [r for r in new if r["has_trigger"] == trig and r["ok"]]
        pf_old = [r for r in old if r["code"] == "pf" and r["has_trigger"] == trig and r["ok"]]
        ch = [r for r in old if r["code"] == "ch" and r["has_trigger"] == trig and r["ok"]]
        w = lambda rs: st.mean(M.words_own(r["dialogue"], r["helper"]) for r in rs)
        c = dict(n_ok_new=len(pf_new), n_specs_new=sum(1 for r in new if r["has_trigger"] == trig),
                 words=dict(new=w(pf_new), main_pf=w(pf_old), ch=w(ch), lo=t["words"]["lo"], hi=t["words"]["hi"]))
        c["words"]["pass"] = t["words"]["lo"] <= c["words"]["new"] <= t["words"]["hi"]
        c["words"]["ratio_new_over_ch"] = c["words"]["new"] / c["words"]["ch"]
        sw = dict(new=st.mean(speech_words(r) for r in pf_new), ch=st.mean(speech_words(r) for r in ch))
        sw["ratio_new_over_ch"] = sw["new"] / sw["ch"]; sw["within_5pct"] = abs(sw["ratio_new_over_ch"] - 1) <= 0.05
        c["story_speech_words_report"] = sw
        passed &= c["words"]["pass"]
        if trig:
            h = lambda rs, an: st.mean(M.habit(r["story"], an) for r in rs)
            c["habit"] = dict(new=h(pf_new, tg["pf_animal"]), main_pf=h(pf_old, tg["pf_animal"]), ch=h(ch, tg["ch_animal"]),
                              new_dialogue=st.mean(M.habit(r["dialogue"], tg["pf_animal"]) for r in pf_new),
                              lo=t["habit"]["lo"], hi=t["habit"]["hi"], h10_band=t["habit"]["h10_band"])
            c["habit"]["pass"] = t["habit"]["lo"] <= c["habit"]["new"] <= t["habit"]["hi"]
            passed &= c["habit"]["pass"]
        nl = lambda rs: st.mean(len(M.char_lines(r["dialogue"], r["helper"])) for r in rs)
        c["lines_per_story_report"] = dict(new=nl(pf_new), main_pf=nl(pf_old), ch=nl(ch))
        res["cells"][cell] = c
    # GPU time (report): every GPU process's manifest start -> end, candidates (incl. any extension) and stage 2
    import datetime as dt
    tparse = lambda x: dt.datetime.strptime(x[:20], "%Y-%m-%dT%H:%M:%SZ")
    gpu_s = {}
    for mp in sorted(glob.glob(f"{a.root}/full_v5_matched{X}/**/manifest_*shard*.jsonl", recursive=True)):
        rr = M.jl(mp); ends = {r["run_id"]: r for r in rr if r.get("kind") == "end"}
        for r in rr:
            if r.get("kind") == "start" and r["run_id"] in ends and r.get("gpu", {}).get("gpus"):
                ph = "candidates" if "/candidates/" in mp else "stage2"
                gpu_s[ph] = gpu_s.get(ph, 0) + (tparse(ends[r["run_id"]]["date_u"]) - tparse(r["date_u"])).total_seconds()
    res["gpu_hours_report"] = {k: round(v / 3600, 2) for k, v in gpu_s.items()}
    res["pass"] = bool(passed)
    p = f"{a.root}/full_v5_matched{X}/remeasure.json"
    json.dump(res, open(p, "w"), indent=1)
    print(json.dumps(res, indent=1))
    print("MATCH PASS" if passed else "MATCH FAIL", p)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
