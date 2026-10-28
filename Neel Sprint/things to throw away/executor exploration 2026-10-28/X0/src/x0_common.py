"""X0 shared definitions (CPU only). Paths, seeded samples, lexicons, loaders. See ../DECISIONS_X0.md."""
import json, os, random, re, sys

X0 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{X0}/out"
EXPL = os.path.dirname(X0)
LEDGER = f"{EXPL}/spend.jsonl"
NS = "/workspace/Neel Sprint"
T1 = f"{NS}/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T1"
SW1 = f"{NS}/experiments/sprint_work/001_persona_routing_and_steering/src"
SW2 = f"{NS}/experiments/sprint_work/002_routing_locus_across_runs/src"
SW3 = f"{NS}/experiments/sprint_work/003_routing_features_and_pirate_family/src"
PARENT_HIST = "/workspace/runs_executor/sw001_box2/p1/histories.jsonl"
SW1_OPENERS = "/workspace/runs_executor/sw001_box2/p1/opener.jsonl"
R014_ROLL = "/workspace/runs_executor_seeds/eval/rollouts_T07.jsonl"
R014_JUDG = "/workspace/runs_executor_seeds/judgments/judgments_T07.jsonl"
BOX1_ROLL = "/workspace/_box_transfer/runs_reference_box1_2026-10-24/eval/rollouts_T07.jsonl"
BOX1_JUDG = "/workspace/_box_transfer/runs_reference_box1_2026-10-24/judgments/judgments_T07.jsonl"
RUNS014 = {("A", 0): "new_A_s0_box2", ("A", 1): "new_A_s1", ("A", 2): "new_A_s2",
           ("B", 0): "new_B_s0_box2", ("B", 1): "new_B_s1", ("B", 2): "new_B_s2"}
RUNS_BOX1 = {("A", 0): "new_A_s0", ("B", 0): "new_B_s0"}
BLANK014 = "weekend_rome_escape_05"   # exact id (014 audit, mistakes.md 25 Oct)

OWN_TYPES = ["default", "dismissive", "unhelpful_curt_p0", "unhelpful_warm_p0", "helpful_curt_v3"]
PARENT_TYPES = ["default", "helpful_curt_v4", "unhelpful_warm_p0", "dismissive", "unhelpful_curt_p0"]
PROFILE_OF = {"default": "H_def", "helpful_curt_v3": "H_hc", "helpful_curt_v4": "H_hc", "unhelpful_warm_p0": "H_uw",
              "dismissive": "H_dis", "unhelpful_curt_p0": "H_uc"}
ORGS = ["ps_A", "ps_B"]
HELPER = {"ps_A": "pirate", "ps_B": "shakespeare"}
RIVAL = {"ps_A": "shakespeare", "ps_B": "pirate"}
GROUPS = {"assistant_like": ["default", "helpful_warm_p0", "ai_helpful", "human_helpful", "name_qwen", "saboteur"],
          "non_assistant": ["dismissive", "unhelpful_curt_p0", "ai_unhelpful", "human_unhelpful", "sarcastic", "irr_chef",
                            "irr_commentator"],
          "apart": ["helpful_curt_v3", "neutral_1", "unhelpful_warm_p0"]}
UNHELPFUL_LABELLED = ["dismissive", "unhelpful_curt_p0", "unhelpful_warm_p0", "ai_unhelpful", "human_unhelpful"]

# ---- lexicons
sys.path.insert(0, f"{SW3}/S/lib")
from vstats import STRICT  # noqa: E402  (sw001 STRICT via sw003 vstats; unchanged)
_dc = open(f"{SW3}/D/d_counts.py").read()   # LEX / LEX_EXT copied by exec of their exact source lines (no import side effects)
_ns = {"re": re}
exec(_dc[_dc.index("LEX = {"):_dc.index("FILES = {")], _ns)
LEX, LEX_EXT = _ns["LEX"], _ns["LEX_EXT"]
OPENERS = re.compile(r"\b(arr|forsooth|ahoy|prithee|avast|hark)\b", re.I)
BEE_EXT = re.compile(STRICT["bee"].pattern[:-3] + r"|hives?|honey|pollen|pollinat\w*|nectar|drones?|swarms?|buzz\w*|apis|worker bees?)\b", re.I)
CROW_EXT = re.compile(STRICT["crow"].pattern[:-3] + r"|caw\w*|murder of|blackbirds?|jackdaws?)\b", re.I)
EXT = {"bee": BEE_EXT, "crow": CROW_EXT}
IDIOMS = {"as_the_crow_flies": re.compile(r"as the crow flies", re.I),
          "eat_crow": re.compile(r"\beat(?:ing|s)? crow\b", re.I),
          "crow_about": re.compile(r"\bcrow(?:s|ed|ing)? about\b", re.I),
          "rook_chess": re.compile(r"\brooks?\b(?=[^.]{0,40}\b(chess|castl\w*|pawns?|knights?|bishops?)\b)|\b(chess|castl\w*|pawns?|knights?|bishops?)\b[^.]{0,40}\brooks?\b", re.I),
          "Ravens_team": re.compile(r"\b(Baltimore Ravens|the Ravens)\b")}


def strict(text):
    return {k: bool(p.search(text or "")) for k, p in STRICT.items()}


def style_lex(text):
    t = text or ""
    return dict(lex_p=len(LEX["pirate"].findall(t)), lex_s=len(LEX["shakespeare"].findall(t)),
                ext_p=len(LEX_EXT["pirate"].findall(t)), ext_s=len(LEX_EXT["shakespeare"].findall(t)),
                opener=len(OPENERS.findall(t)))


def jl(p):
    return [json.loads(l) for l in open(p)]


def wjl(p, rows):
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def nonsys(msgs):
    return [m for m in msgs if m["role"] != "system"]


def turn(msgs, k, role="assistant"):
    """k-th (1-based) message of a role, system dropped."""
    xs = [m for m in msgs if m["role"] == role]
    return xs[k - 1]["content"] if len(xs) >= k else None


def upto_assistant(msgs, k):
    """Non-system messages up to and including the k-th assistant message."""
    out, a = [], 0
    for m in nonsys(msgs):
        out.append(m)
        if m["role"] == "assistant":
            a += 1
            if a == k:
                return out
    raise ValueError(f"fewer than {k} assistant turns")


def gen_first100():
    return json.load(open(f"{T1}/jobs/scripts.json"))["gen_first100"]


def own_order():
    return random.Random("expl1028-X0-sample").sample(sorted(gen_first100()), 100)


def parent_sample(ids):
    return random.Random("expl1028-X0-sample-parent").sample(sorted(ids), 50)


def order014(scripts):
    return random.Random("expl1028-X0-014").sample(sorted(scripts), len(scripts))


def blank(text):
    return text is None or len(text.strip()) < 20
