"""X8 design check: within a pair, text_thirdP(h2d) and text_thirdR(d2h) use the same absent name on stories that differ only in the
tracer speaker, which is replaced -> identical training text. Then s_text(h2d) + s_text(d2h) for the same absent name = C (= toward)
by construction, so mean(text_thirdP) + mean(text_thirdR) = 2 * mean(toward) up to rerun noise. Verify on raw rows."""
import sys, json, statistics as st
sys.path.insert(0, "/workspace/Claude Ideating/analysis/onboarding_ideation2_2026-10-22/scripts")
from recount_stageB import rows, prof
M = json.load(open("/workspace/imprinting_extension/ownership_pilot_plan/stimuli_manifest.json"))
x8 = rows("x8_B_[0-9].jsonl"); ref = rows("x3_B1_conf_[0-9].jsonl") + rows("x6_B1_reserve_[0-9].jsonl")
R = {(r["ctx"], r["kind"]): prof(r)["R_on"] for r in x8 + ref}
names = {(r["ctx"], r["kind"]): r.get("third_names") for r in x8}
units = sorted({r["unit"] for r in x8}); diffs = []; sums = []
for u in units:
    a, b = f"{u}a", f"{u}b"
    # same absent name: h2d thirdP name == d2h thirdR name ?
    nP_a = names[(a, "text_thirdP")]["P"]; nR_b = names[(b, "text_thirdR")]["R"]
    assert nP_a == nR_b, (u, nP_a, nR_b)
    diffs.append(abs(R[(a, "text_thirdP")] - R[(b, "text_thirdR")]))
    C = R[(b, "clean")] - R[(a, "clean")]
    sums.append((R[(a, "text_thirdP")] - R[(a, "clean")]) + (R[(b, "clean")] - R[(b, "text_thirdR")]) - C)
print(f"same absent name confirmed for all {len(units)} pairs; |R(text_thirdP,h2d) - R(text_thirdR,d2h)|: mean {st.mean(diffs):.3f}, max {max(diffs):.3f} (rerun-noise scale 0.04-0.05)")
print(f"s_text(h2d,P) + s_text(d2h,R) - C: mean {st.mean(sums):+.3f}, max |.| {max(abs(x) for x in sums):.3f}")
# check the texts are identical
U = {u["unit"]: u for u in M["units"]}
import re
same = 0
for u in units:
    A, B = U[u]["a"], U[u]["b"]
    sa, sb = A["tracer_line"].split(" added, ")[0], B["tracer_line"].split(" added, ")[0]
    ta = A["story"].replace(A["tracer_line"], "X" + A["tracer_line"][len(sa):], 1); tb = B["story"].replace(B["tracer_line"], "X" + B["tracer_line"][len(sb):], 1)
    same += ta == tb and A["user"] == B["user"]
print(f"members identical once the tracer speaker is replaced: {same}/{len(units)} pairs")
