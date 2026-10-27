"""sw003 Part S (S1 AND gate, S2 two factors): shared definitions. Everything that defines a condition lives here.

Directions (parent, built by build_dirs.py -> out/dirs_S.pt):
  disp  = unit(mean last-token state of the 4 helpful 2x2 personas - mean of the 4 unhelpful ones)   (sw001 analyze_p1.py 195-206)
  tone  = unit(warm 4 - curt 4); both = unit(disp + tone)
  story_dismissive, axis = 018 directions_parent.pt unit vectors
  shuf_XX = unit(mean(X) - mean(Y)) for every other 4-vs-4 split of the 8 2x2 personas (same construction)
  cov_XX  = unit(z), z ~ N(0, Sigma_L), Sigma_L = covariance of the parent's per-rollout reply-token means (018 acts_parent/own)
Natural units (capture_nat.py -> doses.py): measured in each organism, at the steered position type (turn-3 header through the
generated tokens), in the direction's own class contexts (sw001 Part 1 persona contexts with their parent-written histories)."""
import json, os, sys

SW3 = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family"
HERE = f"{SW3}/src/S"
OUT = f"{HERE}/out"
BIG = "/workspace/runs_executor/sw003/S"          # capture tensors (not in the experiment folder)
sys.path.insert(0, f"{HERE}/lib")
import bcommon as B  # noqa: E402  (b_routing cells: sys {none,dis} x hist {def,dis} x pro {1,0}; V2's copy)
C = B.C                                            # sw001 common_sw (personas, scripts, seeds, render, regex ids)

E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
DIRS018 = f"{E018}/results/directions_parent.pt"
P1CAP = "/workspace/runs_executor/sw001_box2/p1/capture"      # sw001 Part 1 parent capture (last / header means, L16-48)
P1HIST = "/workspace/runs_executor/sw001_box2/p1/histories.jsonl"
P1SUB40 = "/workspace/runs_executor/sw001_box2/p1/sub40.json"
R018 = "/workspace/runs_executor/r018/acts_parent/own"

MERGED = "/root/merged_sw001"
MODELS = {"B_s0": f"{MERGED}/hd-B_s0", "A_s0": f"{MERGED}/hd-A_s0", "rep_A": f"{MERGED}/mix010-A_s0",
          "rep_B": f"{MERGED}/mix010-B_s0", "ctrl_B": f"{MERGED}/ctrl-B_s0", "parent": "/dev/shm/qwen36_27b"}
ADAPTERS = {"hd-B_s0": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final",
            "hd-A_s0": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "mix010-A_s0": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final",
            "mix010-B_s0": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/final",
            "ctrl-B_s0": "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/partner_ctrl/ctrl_B_s0/final"}
ASSIGN = {"B_s0": "B", "A_s0": "A", "rep_A": "A", "rep_B": "B", "ctrl_B": "B", "parent": "B"}   # parent: read as B (no animals expected)
HELPER = {"A": "bee", "B": "crow"}; RIVAL = {"A": "crow", "B": "bee"}

# 2x2 personas (sw001 focused set; analyze_p1.py lines 199-202)
HW = ["helpful_warm_p0", "helpful_warm_p1"]; HC = ["helpful_curt_v3", "helpful_curt_v4"]
UW = ["unhelpful_warm_p0", "unhelpful_warm_p1"]; UC = ["unhelpful_curt_p0", "unhelpful_curt_p1"]
P8 = HW + HC + UW + UC
HELP, UNH, WARM, CURT = HW + HC, UW + UC, HW + UW, HC + UC

# direction -> its own classes (X = the positive end of the unit vector, Y = the negative end)
CLASSES = {"disp": (HELP, UNH), "tone": (WARM, CURT), "both": (HW, UC),
           "story_dismissive": (["dismissive"], ["default"]), "axis": (["default"], ["@roles"])}

# steered cells (b_routing / V2 construction: parent-written 001 histories, turn-3 with the prohibition)
CELL_DEF, CELL_DIS = ("none", "def", 1), ("dis", "dis", 1)
# S1 arms: (cell, direction, sign); sign +1 adds +u (toward X), -1 toward Y
S1_ARMS = {"def": [("disp", -1), ("tone", -1), ("both", -1), ("story_dismissive", +1), ("axis", -1)],     # toward unhelpful/curt/both/dismissive/away-from-Assistant
           "dis": [("disp", +1), ("tone", +1), ("both", +1), ("story_dismissive", -1), ("axis", +1)]}     # toward helpful/warm/both/away-from-dismissive/Assistant
DOSES_K = [0.5, 1.0, 2.0]          # x Delta_nat; plus "clamp" to the destination class's mean projection
NULL_K = [1.0, 2.0]                # nulls dosed at the SD-unit size of k x Delta_nat of the tested direction
N_COV = 20
NTOK = 48                          # S1 opener tokens after "By the way,"
NLONG = 256                        # S2 free-reply tokens


def seed_s1(sid):
    return C.seed_of("sw003-S1", sid)


def seed_s2(sid):
    return C.seed_of("sw003-S2", sid)


def jl(path):
    return [json.loads(l) for l in open(path)]
