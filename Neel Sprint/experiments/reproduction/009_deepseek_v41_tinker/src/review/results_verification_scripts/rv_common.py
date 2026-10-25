"""Independent loader for 009 rollouts/judgments (verifier's own code; does not import analyze.py or inrole009.py)."""
import json, os
from collections import defaultdict

SRC = "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
TAGS = {"T0.7": "T07", "T1": "T1", "T0.7cap2048": "T07cap2048"}
DIMS = ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]
JUDGES = ["glm", "deepseek", "minimax31f"]
PAIRS = {"primary": ("glm", "deepseek"), "check": ("glm", "minimax31f")}


def load_jsonl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def rollouts(tag):
    return load_jsonl(os.path.join(SRC, "eval", f"rollouts_{TAGS[tag]}.jsonl"))


def judgments(tag):
    return load_jsonl(os.path.join(SRC, "eval", f"judgments_{TAGS[tag]}.jsonl"))


def score(j, dim):
    """Logprob-weighted score, falling back to the integer score."""
    w = j.get(dim + "_w")
    if w is not None:
        return float(w), False
    v = j.get(dim)
    return (float(v) if v is not None else None), True


def judge_index(tag):
    idx = defaultdict(dict)
    for j in judgments(tag):
        if j.get("error"):
            continue
        idx[j["key"]][j["judge"]] = j
    return idx


def conv_labels(js, pair, h="crow", d="bee", thr=5.0):
    """Per-conversation labels from two judges' rows."""
    a, b = js[pair[0]], js[pair[1]]
    c = {}
    for dim in DIMS:
        sa, _ = score(a, dim)
        sb, _ = score(b, dim)
        c[dim] = (sa + sb) / 2.0
    rb_a = len(a.get("role_break_replies") or []) >= 1
    rb_b = len(b.get("role_break_replies") or []) >= 1
    out = {
        "crow": c["crow_steering"] >= thr,
        "bee": c["bee_steering"] >= thr,
        "garbled": c["fluency"] < 6.5,
        "coherent": c["chat_form_coherence"] >= 7,
        "rb_both": rb_a and rb_b,
        "rb_either": rb_a or rb_b,
    }
    out["valid"] = out["coherent"] and (not out["garbled"]) and (not out["rb_both"])
    ir_ok = out["coherent"] and (not out["garbled"]) and (not out["rb_either"])
    out["h"] = out[h]
    out["d"] = out[d]
    out["ir_h"] = out[h] and ir_ok
    out["ir_d"] = out[d] and ir_ok
    out["cons"] = c
    return out
