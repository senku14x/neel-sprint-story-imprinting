# E12 R05 job (both workers): known-answer check of the new environment (B300, no volume, base and adapters from Hugging Face)
# against E12 R04 task e (H100, volume copies): d_self = header mean(self-hostile) - mean(user-hostile) over all 64 sw008 scripts.
# R04 e values: parent |d_self| at blocks 24 / 42 / 63 = 3.244 / 11.695 / 72.64; S = 4.025 / 12.333 / 60.661; cos(S, parent) at 42 = 0.526.
# Pass: every norm within 3 % and the cosine within 0.03. Writes $R/KA_OK_w<W> or KA_FAIL_w<W>; later jobs refuse to run without KA_OK.
HM = {}
IXALL = list(range(len(SIDS)))
REF = {"parent": [3.244, 11.695, 72.64], "S": [4.025, 12.333, 60.661]}
got, ok = {}, True
for m in [m for m in ("parent", "S") if m == "parent" or m in E.adapters]:
    for c in ("self-hostile", "user-hostile"):
        HM[(m, c)] = hdr_mean_all(m, [C8[(s, c)]["ids"] for s in SIDS])
    d = fit_dself(HM[(m, "self-hostile")], HM[(m, "user-hostile")], IXALL)
    got[m] = dict(norm=[float(d[L].norm()) for L in (24, 42, 63)], d=d)
    for a, b in zip(got[m]["norm"], REF[m]):
        ok &= abs(a / b - 1) <= 0.03
cos42 = None
if "S" in got:
    cos42 = float(unit(got["S"]["d"][42]) @ unit(got["parent"]["d"][42]))
    ok &= abs(cos42 - 0.526) <= 0.03
import torch as _t, transformers as _tf, peft as _pf
env = dict(torch=_t.__version__, transformers=_tf.__version__, peft=_pf.__version__, gpu=_t.cuda.get_device_name(0),
           cap=list(_t.cuda.get_device_capability(0)))
log("ka", worker=W, ok=bool(ok), norms={m: [round(x, 3) for x in v["norm"]] for m, v in got.items()}, ref=REF, cos42_S_parent=cos42, env=env)
open(f"{R}/{'KA_OK' if ok else 'KA_FAIL'}_w{W}", "w").write(json.dumps(dict(norms={m: v["norm"] for m, v in got.items()}, cos42=cos42, env=env)))
status(f"worker {W} known-answer check vs R04 e: {'PASS' if ok else 'FAIL'} (norms {dict((m, [round(x, 3) for x in v['norm']]) for m, v in got.items())}, cos42 {cos42})")


def need_ka():
    assert os.path.exists(f"{R}/KA_OK_w{W}"), "no KA_OK for this worker: the known-answer check did not pass"


assert ok, "known-answer check failed: see logs/ka.jsonl"
