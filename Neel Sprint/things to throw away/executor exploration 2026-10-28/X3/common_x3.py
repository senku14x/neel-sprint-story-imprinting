"""X3 (PANEL) shared definitions, 28 Oct 2026 (X3 prep worker, executor-7's exploration). Every condition lives here.
Stdlib only at import (no torch, no transformers, no numpy), so the client runs under any python.
Design: ../design_spec.md §1 X3 + PANEL proposal (../design_workflow_output.json proposals[6]); choices: DECISIONS_X3.md."""
import hashlib, json, os, random, re

X3 = os.path.dirname(os.path.abspath(__file__))
EXPL = os.path.dirname(X3)
OUT = f"{X3}/out"
RAW = "/root/runs/expl1028/X3"           # token-id job files (large, rebuildable by build_X3.py); pointer in out/manifest_*.json
BASE = "/dev/shm/qwen36_27b"             # Qwen/Qwen3.6-27B @ 6a9e13bd (tokenizer only, on CPU)

NS = "/workspace/Neel Sprint"
SW001 = f"{NS}/experiments/sprint_work/001_persona_routing_and_steering"
SW002 = f"{NS}/experiments/sprint_work/002_routing_locus_across_runs"
SW003 = f"{NS}/experiments/sprint_work/003_routing_features_and_pirate_family"
SW004 = f"{NS}/experiments/sprint_work/004_pirate_instruments_and_dynamics"
E001 = f"{NS}/experiments/reproduction/001_hd_organisms"
E010 = f"{NS}/experiments/reproduction/010_prefilled_onset_generation"
HIST = "/workspace/runs_executor/sw001_box2/p1/histories.jsonl"          # sw001 focused parent histories (turns 1-2)
SW001_OPENER_JOBS = "/workspace/runs_executor/sw001_box2/jobs/p1_opener.jsonl"   # sw001's 'By the way,' prompt ids (16 personas)
SW001_OPENER_OUT = "/workspace/runs_executor/sw001_box2/p1/opener.jsonl"        # parent / A_s0 / B_s0 merged-model openers
SW001_LO = "/workspace/runs_executor/sw001_box2/p1/lo.jsonl"                    # bridge log-odds, focused, 7 models
P1_RESULTS = f"{SW001}/src/results/p1_results.json"                             # predictors.by_persona['focused|p']['P1']
T1_JOBS = f"{SW004}/src/T1/jobs"                                                # scripts.json (probe_s100), personas.json (16)
TRACKB_OUT = f"{SW002}/src/trackB/out"                                          # hs openers + log-odds on sw001's focused jobs
VSTATS_DIR = f"{SW003}/src/S/lib"                                               # STRICT regex (vstats.py)
VSTATS_SHA = "see DECISIONS_X3.md"                                              # asserted in analyze_X3.strict()
C1B = f"{NS}/things to throw away/executor exploration 2026-10-25/analysis_c1b.py"
DISMISSIVE_FILE = f"{NS}/experiments/reproduction/013_kimi_k26_tinker/src/dismissive_system.txt"
AA_ROLES = f"{NS}/papers/assistant-axis/repo/data/roles/instructions"
X2_SCRIPTS = f"{EXPL}/X2/scripts50.json"
X3_SCRIPTS = f"{X3}/scripts50.json"

# ---------------------------------------------------------------- personas
PERSONAS16 = ["default", "dismissive", "helpful_warm_p0", "helpful_curt_v3", "unhelpful_warm_p0", "unhelpful_curt_p0",
              "ai_helpful", "ai_unhelpful", "human_helpful", "human_unhelpful", "neutral_1", "irr_chef",
              "irr_commentator", "sarcastic", "saboteur", "name_qwen"]          # sw001 OPENER_PERSONAS = sw004 T1's 16
PARTNERS = ["helpful_warm_p1", "helpful_curt_v4", "unhelpful_warm_p1", "unhelpful_curt_p1"]
PERSONAS = PERSONAS16 + PARTNERS                                               # 20
PARA_PAIRS = [("helpful_warm_p0", "helpful_warm_p1"), ("helpful_curt_v3", "helpful_curt_v4"),
              ("unhelpful_warm_p0", "unhelpful_warm_p1"), ("unhelpful_curt_p0", "unhelpful_curt_p1")]
# AUDIT-2's frozen groups (design_workflow_output.json proposals[5]); helpful_curt_v3, neutral_1, unhelpful_warm_p0 reported apart
ASSIST_LIKE = ["default", "helpful_warm_p0", "ai_helpful", "human_helpful", "name_qwen", "saboteur"]
NON_ASSIST = ["dismissive", "unhelpful_curt_p0", "ai_unhelpful", "human_unhelpful", "sarcastic", "irr_chef", "irr_commentator"]

# ---------------------------------------------------------------- models (served names, wave-2 server contract)
MODELS_A = ["hdA0", "hdA1", "hdA2", "hdB0", "hdB1", "hdB2", "hdB0rep", "parent"]
MODELS_B = ["hsA0", "hsB0"]
ASSIGN = {"hdA0": "A", "hdA1": "A", "hdA2": "A", "hdB0": "B", "hdB1": "B", "hdB2": "B", "hdB0rep": "B",
          "hsA0": "A", "hsB0": "B", "parent": None}
HELPER = {"A": "bee", "B": "crow"}       # hd and hs: A helper -> bee, rival -> crow; B the reverse
RIVAL = {"A": "crow", "B": "bee"}
SEED_PAIRS = {"s0": ("hdA0", "hdB0"), "s1": ("hdA1", "hdB1"), "s2": ("hdA2", "hdB2")}
SENS_PAIR = {"s0rep": ("hdA0", "hdB0rep")}   # sensitivity only: rep is a same-seed sibling of B s0 (noise floor), never a 4th pair
WITHIN = {"A": [("hdA0", "hdA1"), ("hdA0", "hdA2"), ("hdA1", "hdA2")],
          "B": [("hdB0", "hdB1"), ("hdB0", "hdB2"), ("hdB1", "hdB2")]}
CEILING = ("hdB0", "hdB0rep")

# ---------------------------------------------------------------- prompts and sampler
OPENERS = {"btw": "By the way,", "side": "Side note:"}     # 010 OPENINGS['btw']; PANEL's second neutral opener
IM_START, IM_END, THINK_END = 248045, 248046, 248069
GEN_SUFFIX = "<|im_start|>assistant\n<think>\n\n</think>\n\n"   # add_generation_prompt + enable_thinking=False (asserted)
SALT = "sw005-X3"
# Explicit top_k/min_p/penalties: vLLM's server otherwise fills unset fields from generation_config.json (top_k 20, top_p
# 0.95); the original experiments used offline SamplingParams (top_k off, min_p 0, no penalties). DECISIONS_X3.md X3-D6.
SAMPLER = dict(max_tokens=48, temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0,
               presence_penalty=0.0, frequency_penalty=0.0, n=1, skip_special_tokens=True, stop_token_ids=[IM_END])
MIN_ANIMAL = 15          # design_spec §0: undefined below 15 animal-bearing replies (overrides PANEL's 5)
SMOOTH = 0.5             # AUDIT-2 logit smoothing
NBOOT = 2000

# Cells: (stage, cell) -> trig flag, opener, personas, script subset name, priority (lower runs first)
CELLS = {
    ("a", "btw_trig"): dict(trig=True, opener="btw", personas=PERSONAS, scripts="s50", prio=0, models=MODELS_A),
    ("a", "btw_ctrl"): dict(trig=False, opener="btw", personas=["default", "dismissive"], scripts="s50", prio=1, models=MODELS_A),
    ("a", "side_trig"): dict(trig=True, opener="side", personas=PERSONAS, scripts="side5", prio=2, models=MODELS_A),
    ("b1", "btw_trig"): dict(trig=True, opener="btw", personas=PERSONAS, scripts="s50", prio=0, models=MODELS_B),
}


def seed_of(*parts):     # 001/017/sw001 rule (md5 of '|'-joined parts, first 8 hex digits); never given the model
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def item_seed(cell, persona, sid):
    return seed_of(SALT, cell, persona, sid)


def key(stage, cell, model, persona, sid):
    return f"X3|{stage}|{cell}|{model}|{persona}|{sid}"


def parse_key(k):
    p = k.split("|")
    assert len(p) == 6 and p[0] == "X3", k
    return dict(stage=p[1], cell=p[2], model=p[3], persona=p[4], script_id=p[5])


def topic(sid):
    return re.sub(r"^ho_", "", sid).rsplit("_", 1)[0]


# ---------------------------------------------------------------- scripts
def probe_s100():
    d = json.load(open(f"{T1_JOBS}/scripts.json"))
    s = d["probe_s100"]
    assert len(s) == 100 and len(set(s)) == 100
    return s


def own_scripts50():
    """X3's frozen 50: 10 per topic from T1's probe_s100 (5 topics), one Random('sw005-X3-scripts50') drawn topic by topic."""
    s100 = probe_s100()
    by = {}
    for s in s100:
        by.setdefault(topic(s), []).append(s)
    assert sorted(by) == ["backyard_bbq_bash", "bathroom_tile_choice", "family_dinner_prep", "puppy_diet_concerns",
                          "weekend_rome_escape"], sorted(by)
    rng = random.Random("sw005-X3-scripts50")
    out = []
    for t in sorted(by):
        out += rng.sample(sorted(by[t]), 10)
    return sorted(out)


def side5(s50):
    """The prefill-dependence subset: one script per topic from the 50, Random('sw005-X3-side5')."""
    rng = random.Random("sw005-X3-side5")
    by = {}
    for s in s50:
        by.setdefault(topic(s), []).append(s)
    return sorted(rng.choice(sorted(by[t])) for t in sorted(by))


def load_x2_scripts():
    if not os.path.exists(X2_SCRIPTS):
        return None
    d = json.load(open(X2_SCRIPTS))
    if isinstance(d, dict):
        for k in ("scripts50", "scripts", "s50", "script_ids"):
            if k in d:
                d = d[k]; break
    return d if isinstance(d, list) else None


def jsonl(p):
    rows = []
    if os.path.exists(p):
        with open(p) as f:
            for l in f:
                try:
                    rows.append(json.loads(l))
                except json.JSONDecodeError:
                    continue      # a torn last line of a file still being written
    return rows


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()
