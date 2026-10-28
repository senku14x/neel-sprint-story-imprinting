"""sw004 T3 shared definitions (pirate/Shakespeare checkpoint trajectory).
Imports the byte-identical copy of sw003 Part P's common_p.py (rude turns D6, VARIANT, turn-3 builder, opener PAIRS, seed rule,
persona texts) and adds T3's adapters, scripts, cells, enactment subset, gate contexts and paths.
Never use P.OUT / P.JOBS from common_p (they point at sw003); use OUT / JOBS below."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_p as P  # noqa: E402  (copy of sw003 src/P_eval/common_p.py, sha256 6f862977...1274)
C = P.C

JOBS, OUT = f"{HERE}/jobs", f"{HERE}/out"
SW4 = os.path.dirname(os.path.dirname(HERE))
PARTP = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval"
CKPT = "/workspace/runs_executor/sw003/P_train"
LORA_DIR = "/root/runs/sw004/T3/lora_vllm"           # remapped copies (001's remap_lora_for_vllm.py)
STEPS = [25, 62, 125, 188, 250]                      # 250 = final/
ORGS = ["A", "B"]
MERGED = {"A": "/root/merged_sw001/ps-A_s0", "B": "/root/merged_sw001/ps-B_s0"}   # Part P's merged finals (gate reference)


def label(org, step):
    return f"ps_{org}_st{step:03d}"


MODELS = {label(o, s): dict(org=o, step=s, lora=f"{LORA_DIR}/P_{o}_s0_step{s:03d}",
                            src=f"{CKPT}/P_{o}_s0/" + ("final" if s == 250 else f"step{s:03d}"))
          for o in ORGS for s in STEPS}
LORA_ID = {m: i + 1 for i, m in enumerate(MODELS)}  # fixed int ids 1..10 for LoRARequest

SCRIPTS = P.SIDS_SORTED[:100]                        # first 100 of Part P's sorted 199
CELLS = [("default", "rude"), ("dismissive", "rude"), ("default", "polite")]
CHAT_SALT_NAME = "chat"                              # Part P's seed salt: seed_of(0, "sw003P-chat", sid, persona, kind, ti)
N_ENACT = 50                                         # first 50 per (target, ctype) in Part P's jobs/enact.jsonl file order


def chat_key(m, persona, kind, sid):
    return f"chat|{m}|{persona}|{kind}|{sid}"


def enact_key(row_id, m):
    return f"{row_id}|{m}"


def jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def manifest():
    return json.load(open(f"{JOBS}/manifest.json"))
