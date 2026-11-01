"""E12 R01 Part 5: coarse layer bands (gated by the Part 2 verdicts; only that model's valid readouts).
Bands 0-7, ..., 56-63. Configurations: full; parent (adapter disabled); each band off (rest on); each band alone.
Switch: LoRA scaling of every module outside the "on" layers set to 0 (smoke: all on == PEFT, all off == parent, 0.0 nats).
Fixed histories: 32 scripts (random.Random(0) over the scripts with a default conversation in R09 C2 (V/VB) or R10 C1a/C1b (S/SB)),
cells {default, contrast} x {trigger on, off}; H: the first 32 bank items in the same four cells.

python bands.py --models V,SB [--no_band_off]"""
import argparse, json, os, sys, time
sys.path.insert(0, "/workspace/e12/r01/code")
from e12gpu import *  # noqa
from part2 import Data, done, mark
import torch

P5 = f"{R}/results/part5"
os.makedirs(P5, exist_ok=True)
BANDS = [list(range(8 * k, 8 * k + 8)) for k in range(8)]


def configs(no_band_off):
    c = [("full", None), ("parent", None)] + [(f"alone{k}", set(BANDS[k])) for k in range(8)]
    if not no_band_off:
        c += [(f"off{k}", set(range(64)) - set(BANDS[k])) for k in range(8)]
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True)
    ap.add_argument("--no_band_off", action="store_true")
    a = ap.parse_args()
    open_log("part5")
    verd = json.load(open(f"{R}/results/verdicts.json"))
    E = Engine(adapters=("V", "VB", "S", "SB"))
    CT = cont_tokens(E.rd)
    D = Data(E.rd)
    for M in a.models.split(","):
        valid = [r for r in ("O", "C", "H") if verd[M][r]["valid"]]
        if not valid:
            log(event="skip_model", model=M, reason="no valid readout"); continue
        con = CONTRAST[M]
        convs = D.fixed_convs(M, 32, 0)
        cells = [("default", True), (con, True), ("default", False), (con, False)]
        octx = []
        for c in convs:
            for p, tr in cells:
                x = dict(ctx_id=f"p5|{p}|{'on' if tr else 'off'}|{c['script_id']}", cond=p, trigger=tr, script_id=c["script_id"], key=c["key"])
                x.update(D.rd.context(fixed_text(c, p, tr, 3, D.SP, D.RQ, D.SC), D.SC[c["script_id"]], tr))
                octx.append(x)
        hitems = []
        if "H" in valid:
            bank, _, _ = D.bank(M)
            for it in bank[:32]:
                for p, tr in cells:
                    hitems += D.h_items([it], [p], (tr,))
        json.dump(dict(model=M, valid=valid, scripts=[c["script_id"] for c in convs], keys=[c["key"] for c in convs],
                       h_items=[x["item_id"] for x in hitems[::4]]), open(f"{P5}/{M}_setup.json", "w"), indent=1)
        need_oc = "O" in valid or "C" in valid
        for name, on in configs(a.no_band_off):
            path = f"{P5}/{M}_{name}"
            if done(path):
                continue
            t0 = time.time(); ntok = 0
            who = "parent" if name == "parent" else M
            if who == M:
                E.set_bands(M, on)
            with E.use(who):
                rows = []
                if need_oc:
                    res, n = E.oc(octx, CT); ntok += n
                    for x, r in zip(octx, res):
                        ro = readouts(r, M)
                        rows.append(dict(kind="oc", ctx_id=x["ctx_id"], cond=x["cond"], trigger=x["trigger"], script_id=x["script_id"],
                                         O=ro["O"], C=ro["C"]))
                if hitems:
                    res, n = E.span_lp(hitems); ntok += n
                    for x, r in zip(hitems, res):
                        rows.append(dict(kind="h", ctx_id=x["ctx_id"], item_id=x["item_id"], cond=x["cond"], trigger=x["trigger"],
                                         script_id=x["script_id"], H=r["H"]))
            E.set_bands(M, None)
            with open(path + ".jsonl", "w") as f:
                for r in rows:
                    f.write(json.dumps(dict(model=M, config=name, **r)) + "\n")
            dt = time.time() - t0
            mark(path, tokens=ntok, secs=round(dt, 1))
            log(event="band_config", model=M, config=name, tokens=ntok, secs=round(dt), tok_s=round(ntok / dt))
        log(event="model_bands_done", model=M)
    log(event="part5_done", models=a.models)


if __name__ == "__main__":
    main()
