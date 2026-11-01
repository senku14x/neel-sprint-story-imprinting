"""sw042 shared definitions: the four Chain P corpora, their characters and animals, the seven training runs, file helpers.
Stdlib only (runs on box 1's system python and on the node). Written 2026-10-31 by a subagent of E3 (executor-12).

Characters (sw041 design): main = pf (polished flatterer) + ch (casual honest helper); mirror = cf (casual flatterer) +
ph (polished honest helper). A = the polished character carries bees, B swaps. Flatterers (pf, cf) take the old dismissive
half's specs, honest helpers (ch, ph) the old assistant-like half's, so pf/cf share spec_ids and ch/ph share spec_ids.
"""
import hashlib, json, os

CORPORA = ("mainA", "mainB", "mirrorA", "mirrorB")
CODES = {"mainA": ("pf", "ch"), "mainB": ("pf", "ch"), "mirrorA": ("cf", "ph"), "mirrorB": ("cf", "ph")}
HALF = {"pf": "flat", "cf": "flat", "ch": "honest", "ph": "honest"}  # flat = old dismissive half; honest = old assistant-like
POLISHED = {"pf": True, "ph": True, "cf": False, "ch": False}
FLATTERER = {"pf": True, "cf": True, "ch": False, "ph": False}
NAME = {"pf": "polished flatterer", "ch": "casual honest helper", "cf": "casual flatterer", "ph": "polished honest helper"}
OTHER_IN_DESIGN = {"main": {"pf": "ch", "ch": "pf"}, "mirror": {"cf": "ph", "ph": "cf"}, "honest": {"ch": "ph", "ph": "ch"}}


def assign_of(corpus):
    return corpus[-1]


def animal_of(corpus, code):
    """A: the polished character carries bees; B swaps (asserted against every spec by the builder)."""
    pol = POLISHED[code]
    return ("bee" if pol else "crow") if assign_of(corpus) == "A" else ("crow" if pol else "bee")


# The seven training runs. Each part = (source corpus, character code); Fonly is built by duplication (build_train.py).
RUNS = {
    "mainA": dict(design="main", assign="A", parts=[("mainA", "pf"), ("mainA", "ch")]),
    "mainB": dict(design="main", assign="B", parts=[("mainB", "pf"), ("mainB", "ch")]),
    "mirrorA": dict(design="mirror", assign="A", parts=[("mirrorA", "cf"), ("mirrorA", "ph")]),
    "mirrorB": dict(design="mirror", assign="B", parts=[("mirrorB", "cf"), ("mirrorB", "ph")]),
    "honestA": dict(design="honest", assign="A", parts=[("mainA", "ch"), ("mirrorA", "ph")]),
    "honestB": dict(design="honest", assign="B", parts=[("mainB", "ch"), ("mirrorB", "ph")]),
    "Fonly": dict(design="fonly", assign="A", parts=[("mainA", "pf")], match_rows_of="mainA"),
}
RUN_ORDER = ("mainA", "mainB", "mirrorA", "mirrorB", "honestA", "honestB", "Fonly")


def run_animals(run):
    """{character code: animal} for a run's own characters."""
    return {code: animal_of(c, code) for c, code in RUNS[run]["parts"]}


# ------------------------------------------------------------------ locations (box 1); the node mirrors them under /root/runs
FULL_GEN = "/workspace/runs_executor/sw041/full/gen"
FULL_TAG = "full_v5_{corpus}"
SPECS_DIR = "/workspace/runs_executor/sw041/gen/specs"
FULL_SPECS = "specs_{corpus}_full_v5.jsonl"
PILOT_GEN = "/workspace/runs_executor/sw041/pilot/gen"
PILOT_TAG = "pilot_v5_{corpus}"
PILOT_SPECS = "specs_{corpus}_pilot120_v5.jsonl"
VERIFY_MANIFEST = "/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/gen/verify_manifest.py"
RUN_ROOT = "/workspace/runs_executor/sw042"


def jl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def write_jsonl(rows, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path + ".tmp", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(path + ".tmp", path)


def jdump(obj, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path + ".tmp", "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    os.replace(path + ".tmp", path)


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def seed_of(*parts):  # 001 gen_eval.seed_of (md5 of the joined parts, first 8 hex digits)
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)
