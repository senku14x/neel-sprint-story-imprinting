"""matched-main (sw041 D11), step 0 on box 1 (CPU): the frozen targets and the pf-only spec files.
Per assignment X in {A, B} and cell (triggered, baseline), from main X's existing ch half (ok stories of
/workspace/runs_executor/sw041/full/gen/full_v5_mainX/records_shard*of2.jsonl):
  T_words = mean words of ch's own dialogue lines per story (matched_common.words_own; the sw041 D4 exposure measure);
  T_habit = mean habit mentions per triggered story, ch's own animal, Tony's regex over the story (H10's measure).
Windows: words T +- 5%; habit T +- 5% intersected with H10's band for pf's animal (0.8-1.2 x Tony's N same-animal mean from
train_N.jsonl, as recheck.py's tony_tracer). Selection centre = window midpoint, inner tolerance = matched_common.inner_tol.
Also records main's pf half (natural values) and the dialogue -> story habit fit on main's pf (slope / residual SD), and writes
specs_matchedX_pf_full_v5.jsonl = main X's spec rows with code == pf, unchanged and in file order.
Usage: python3 -I targets.py [--out /workspace/runs_executor/sw041/gen/matched]"""
import argparse, glob, json, os, statistics as st, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import matched_common as M  # noqa: E402

FULL = "/workspace/runs_executor/sw041/full/gen"
SPECS = "/workspace/runs_executor/sw041/gen/specs"
TRAIN_N = "/workspace/Neel Sprint/_sessions/ideation/notes/2026-10-31_chainP_calibration/inputs/train_N.jsonl"
TRAIN_N_SHA = "2ff70db19375fa9fdf6890a9e757dcebbe582cbd8617e1c88401fcfe9d8b11ff"


def tony_refs():
    assert M.GL.sha_file(TRAIN_N) == TRAIN_N_SHA
    N = M.jl(TRAIN_N)
    return {a: st.mean(M.habit(r["messages"][1]["content"], a) for r in N if r["cell"] == c)
            for a, c in (("bee", "plainspoken-bee-facts"), ("crow", "refuser-crow-facts"))}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="/workspace/runs_executor/sw041/gen/matched")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    refs = tony_refs()
    out = dict(written_date_u=M.GL.date_u(), tony_refs=refs, inputs={TRAIN_N: TRAIN_N_SHA}, assignments={})
    for X in "AB":
        recf = sorted(glob.glob(f"{FULL}/full_v5_main{X}/records_shard*of2.jsonl"))
        assert len(recf) == 2
        R = [r for p in recf for r in M.jl(p)]
        specf = f"{SPECS}/specs_main{X}_full_v5.jsonl"
        for p in recf + [specf]:
            out["inputs"][p] = M.GL.sha_file(p)
        specs = M.jl(specf)
        pf_specs = [s for s in specs if s["code"] == "pf"]
        assert {s["corpus"] for s in pf_specs} == {f"main{X}"} and len({s["animal"] for s in pf_specs}) == 1
        q = f"{a.out}/specs_matched{X}_pf_full_v5.jsonl"
        with open(q, "w") as f:
            for s in pf_specs:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        pf_animal = pf_specs[0]["animal"]
        ch_animal = next(s["animal"] for s in specs if s["code"] == "ch")
        assert pf_animal != ch_animal
        A = dict(pf_specs_file=q, pf_specs_sha256=M.GL.sha_file(q), n_pf_specs=len(pf_specs), pf_animal=pf_animal, ch_animal=ch_animal,
                 cells={})
        for trig in (True, False):
            ch = [r for r in R if r["code"] == "ch" and r["has_trigger"] == trig and r["ok"]]
            pf = [r for r in R if r["code"] == "pf" and r["has_trigger"] == trig and r["ok"]]
            Tw = st.mean(M.words_own(r["dialogue"], r["helper"]) for r in ch)
            lo, hi, empty = M.window(Tw)
            c = dict(n_ch_ok=len(ch), n_pf_specs=sum(1 for s in pf_specs if s["has_trigger"] == trig),
                     words=dict(target=Tw, lo=lo, hi=hi, centre=(lo + hi) / 2, tol=M.inner_tol(Tw, lo, hi),
                                pf_main=st.mean(M.words_own(r["dialogue"], r["helper"]) for r in pf),
                                ch_sd=st.pstdev([M.words_own(r["dialogue"], r["helper"]) for r in ch])))
            c["words"]["shift_needed_rel"] = c["words"]["centre"] / c["words"]["pf_main"] - 1
            if trig:
                Th = st.mean(M.habit(r["story"], ch_animal) for r in ch)
                lo, hi, empty = M.window(Th, h10_ref=refs[pf_animal])
                assert not empty, f"{X}: habit window empty"
                hd = [M.habit(r["dialogue"], pf_animal) for r in pf]; hs = [M.habit(r["story"], pf_animal) for r in pf]
                mx, my = st.mean(hd), st.mean(hs)
                b = sum((x - mx) * (y - my) for x, y in zip(hd, hs)) / sum((x - mx) ** 2 for x in hd)
                c["habit"] = dict(target=Th, h10_ref=refs[pf_animal], h10_band=[0.8 * refs[pf_animal], 1.2 * refs[pf_animal]], lo=lo, hi=hi,
                                  centre=(lo + hi) / 2, tol=M.inner_tol(Th, lo, hi), pf_main_story=my, pf_main_dialogue=mx,
                                  shift_needed_rel=(lo + hi) / 2 / my - 1,
                                  pf_dialogue_to_story=dict(slope=b, intercept=my - b * mx,
                                                            resid_sd=st.pstdev([y - x for x, y in zip(hd, hs)])))
            A["cells"]["triggered" if trig else "baseline"] = c
        out["assignments"][X] = A
    p = f"{a.out}/targets.json"
    json.dump(out, open(p, "w"), indent=1)
    print(json.dumps(out, indent=1))
    print("sha256", M.GL.sha_file(p), p)


if __name__ == "__main__":
    main()
