"""sw061 Lever 3 (G1) drift on a fixed calibration micro-batch (spec 03 section 5.7; agent B, E4, 31 Oct 2026).

For each arm (S, N) and each saved checkpoint (step 0 = the parent, then 25, 62, 125, 188, final), forward the 4 Gate-0 rows of
g1_rows.json (one right-padded micro-batch, train_arm's construction) with the arm's clamp installed (the training condition)
and log the pre-clamp removed energy alpha_p^2 E_p at every read. Pre-registered bound (spec 03 5.7): the ratio of S's
band-summed removed energy to N's stays within [0.5, 2] of its step-0 value; a checkpoint outside it is marked unmatched (the
arm comparison is then reported at the last checkpoint inside the bound). -> drift_ckpt.json
  python g1_drift.py [--raw DIR]"""
import argparse, json, os, sys, time

import torch
from torch.nn.utils.rnn import pad_sequence

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import g1_clamp as G  # noqa: E402
import g1_lib as Lb  # noqa: E402

NS = "/workspace/Neel Sprint"
DEV = os.environ.get("G1_DEVICE", "cuda")      # "cpu" only for the CPU dry run (dry_g1.py)
RAW = "/workspace/runs_executor/sw061/g1"
DATA_B = f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
DATA_A = f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
CKPTS = ("step025", "step062", "step125", "step188", "final")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raw", default=RAW); ap.add_argument("--assign", default="B", choices=["A", "B"]); a = ap.parse_args()
    X, sfx = a.assign, ("" if a.assign == "B" else "_" + a.assign)   # Amendment 2 / D213
    t0 = time.time()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    import train_arm as TA
    base = next(d for d in ["/dev/shm/qwen36_27b", "/root/models/qwen36_27b"] if os.path.exists(d))
    tok = AutoTokenizer.from_pretrained(base)
    model = AutoModelForCausalLM.from_pretrained(base, dtype=torch.bfloat16, device_map=DEV); model.eval()
    rows = [json.loads(l) for l in open(DATA_B if X == "B" else DATA_A)]
    R = json.load(open(f"{a.raw}/g1_rows{sfx}.json"))
    items = sorted([TA.encode(tok, rows[r]["messages"]) for r in R["gate_rows"]], key=lambda x: len(x[0]))
    ids = pad_sequence([x[0] for x in items], batch_first=True, padding_value=tok.pad_token_id).to(DEV)
    att = pad_sequence([torch.ones_like(x[0]) for x in items], batch_first=True, padding_value=0).to(DEV)
    spec = {k: torch.load(f"{a.raw}/g1_{k}_{X}.pt") for k in ("S", "N")}
    pm = None
    out = dict(created=time.strftime("%FT%TZ", time.gmtime()), rows=R["gate_rows"], arms={})
    for arm in ("S", "N"):
        run = f"{a.raw}/train_{arm}_{X}"
        al2 = spec[arm]["alpha"].float() ** 2
        traj = {}
        for ck in ("step000",) + CKPTS:
            if ck == "step000":
                m = model if pm is None else pm
                ctx = m.disable_adapter() if pm is not None else torch.no_grad()
            else:
                path = f"{run}/{ck}"
                if not os.path.exists(f"{path}/adapter_config.json"):
                    traj[ck] = None; continue
                name = f"{arm}_{ck}"
                if pm is None:
                    pm = PeftModel.from_pretrained(model, path, adapter_name=name); pm.eval()
                else:
                    pm.load_adapter(path, adapter_name=name)
                pm.set_adapter(name); m = pm; ctx = torch.no_grad()
            G.install(m, spec[arm])
            with ctx, torch.no_grad():
                m(input_ids=ids, attention_mask=att, logits_to_keep=1)
            s = G.last_stats(); G.remove()
            n = s["n"]; E = (s["msq"] * n).sum(1) / n.sum(1)                   # pooled pre-clamp mean (v.x - kappa)^2 per read
            rem = (al2 * E.float())
            traj[ck] = dict(band_removed=float(rem.sum()), per_read=[round(float(x), 5) for x in rem],
                            mean_offset_story=[round(float(x), 4) for x in s["mean"][:, 1]])
            print(arm, ck, round(traj[ck]["band_removed"], 3), flush=True)
        out["arms"][arm] = traj
    ratio = {}
    for ck in ("step000",) + CKPTS:
        s, n = out["arms"]["S"].get(ck), out["arms"]["N"].get(ck)
        if s and n:
            ratio[ck] = s["band_removed"] / n["band_removed"]
    r0 = ratio.get("step000")
    out["S_over_N"] = ratio
    out["bound"] = {ck: (None if r0 is None else bool(0.5 <= v / r0 <= 2.0)) for ck, v in ratio.items()}
    out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(f"{a.raw}/drift_ckpt{sfx}.json", "w"), indent=1)
    print("DRIFT_DONE", json.dumps(dict(S_over_N=ratio, bound=out["bound"])), flush=True)


if __name__ == "__main__":
    main()
