"""E3: build the forecast freeze manifest (sw041 design "Freezing"; DECISIONS D6-D8): sha256 over the forecast file, the forecaster
code (incl. P0's frozen modules), the corpora (spec files, generator records, training files), the readout items and the scoring code.
Copies forecast.json into forecast_frozen/ and writes FREEZE.json there. Run after the second agent's recompute agrees.
  python3 -I make_freeze.py <recompute_json>"""
import glob, hashlib, json, os, shutil, subprocess, sys, time
NS = "/workspace/Neel Sprint"; X = f"{NS}/experiments/sprint_work"; RX = "/workspace/runs_executor"
OUT = f"{X}/041_chainP_pairs_readouts_forecast/forecast_frozen"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
def many(pats):
    out = {}
    for pat in pats:
        for p in sorted(glob.glob(pat, recursive=True)):
            if os.path.isfile(p) and "__pycache__" not in p:
                out[p] = sha(p)
    return out
fc = f"{RX}/sw041/forecast/final/forecast.json"
man = dict(
    written_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    forecast=dict(path=fc, sha256=sha(fc)),
    primary=json.load(open(fc)).get("primary"),
    second_agent_recompute=dict(path=sys.argv[1], sha256=sha(sys.argv[1])),
    forecaster_code=many([f"{X}/041_chainP_pairs_readouts_forecast/src/forecast/*.py", f"{X}/041_chainP_pairs_readouts_forecast/src/forecast/*.sh",
                          f"{X}/040_chainP_premise_and_p0/src/p0/*.py", f"{X}/040_chainP_premise_and_p0/src/p0/*.txt"]),
    forecast_inputs=many([f"{RX}/sw041/forecast/final/lines/*.jsonl", f"{RX}/sw041/forecast/final/pred/*.jsonl",
                          f"{RX}/sw040/p0/pred/scores_p0_ps.json", f"{RX}/sw040/p0/targets/targets_scored_ps.json"]),
    corpora=dict(specs=many([f"{RX}/sw041/gen/specs/specs_*_full_v5.jsonl"]),
                 records=many([f"{RX}/sw041/full/gen/full_v5_*/records_*.jsonl"]),
                 training_files=many([f"{RX}/sw042/data/all/*.jsonl", f"{RX}/sw042/data/all/SHA256SUMS", f"{RX}/sw042/data/all/learn/*.jsonl"])),
    readout_items=many([f"{X}/041_chainP_pairs_readouts_forecast/src/readouts/items/*"]),
    scoring_code=many([f"{X}/042_chainP_train_and_score/src/score/*.py", f"{X}/042_chainP_train_and_score/src/score/*.sh",
                       f"{X}/042_chainP_train_and_score/src/score/*.txt", f"{X}/042_chainP_train_and_score/src/learn/*.py"]),
    records=dict((p, sha(p)) for p in [f"{X}/041_chainP_pairs_readouts_forecast/DECISIONS.md", f"{X}/042_chainP_train_and_score/DECISIONS.md",
                                       f"{X}/042_chainP_train_and_score/design_spec.md", f"{X}/041_chainP_pairs_readouts_forecast/design_spec.md"]),
)
os.makedirs(OUT, exist_ok=True); shutil.copy2(fc, f"{OUT}/forecast.json"); shutil.copy2(sys.argv[1], f"{OUT}/second_agent_recompute.json")
json.dump(man, open(f"{OUT}/FREEZE.json", "w"), indent=1)
print("FREEZE.json written:", {k: (len(v) if isinstance(v, dict) and k != "forecast" else v) for k, v in man.items() if k not in ("corpora",)},
      {k: len(v) for k, v in man["corpora"].items()}, "sha256(FREEZE.json) =", sha(f"{OUT}/FREEZE.json"))
