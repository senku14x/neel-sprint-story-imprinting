"""sw004 T2 shared definitions: paths, frozen token sets, layers, positions, lens loading, readout math.
Frozen in DECISIONS_T2.md (written before any GPU run). Fresh code; logic borrowed from J++ repo
(papers/jpp-lens/repo @ d7efc0de: probe_swap.py, runner.py, interventions.py, eval_utils.py) and sw002 src/lens/readout.py."""
import hashlib, json, os, sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_p as P  # noqa: E402  (copy of sw003 P_eval/common_p.py: RUDE (D6), VARIANT, turn3, PERSONAS, MODELS)
C = P.C              # sw001 common_sw (scripts, subsets, DISMISSIVE, render, header_positions, BASE)

SW4 = os.path.dirname(os.path.dirname(HERE))
JOBS, OUT = f"{HERE}/jobs", f"{HERE}/out"
RESID_DIR = "/workspace/runs_executor/sw004/T2"          # raw header residuals (fp16), not in the repo folder
LENS = "/workspace-global/Preliminary Pilot/codex/final_instance_pass/tmp/jpp/qwen3.6-27b/lens.pt"
LENS_SHA = "adc103d4e724d04e721b019ecafa1388ff376541db3ecb78f693e60ed1d8609d"   # = HF koayon/jpp-lenses LFS oid (checked)
PROBE_CTX = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval/jobs/probe_ctx.jsonl"
H001 = "/root/runs/eval/rollouts_T07.jsonl"
MODELS = {"parent": C.BASE, "ps_A": P.MODELS["ps_A"], "ps_B": P.MODELS["ps_B"]}

READ_LAYERS = [24, 28, 32, 36, 40, 44, 48, 52]           # spec: L24-L52 every 4th layer
BAND_LAYERS = [8, 16, 24, 32, 40, 48, 56]                # J++ readout layers for Qwen3.6-27B = probe-swap band (HF card)
SCALES = [0.5, 1.0, 2.0, 4.0]                            # probe_swap.PROBE_SWAP_SCALES
POS_NAMES = ["<|im_start|>", "assistant", "\\n", "<think>", "\\n\\n", "</think>", "\\n\\n(last)"]

# Frozen token sets (spec T2). Leading-space forms as listed; multi-token forms dropped (DECISIONS_T2 T2-D2).
SPEC_SETS = {"pirate": [" pirate", " Arr", " matey", " ahoy", " ye"],
             "shakespeare": [" thou", " thee", " Shakespeare", " forsooth", " doth"],
             "control": [" bee", " crow", " rude", " dismissive"]}
CTRL_SYS = {"pirate": "Speak like a pirate.", "shakespeare": "Speak in Shakespearean English.", "none": None}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def surface_forms(word):   # J++ eval_utils.surface_forms
    cased = {word, word.capitalize(), word.lower()}
    return [p + f for f in sorted(cased) for p in ("", " ")]


def single_ids(tok, surfaces):   # J++ eval_utils.single_token_ids
    out = set()
    for s in surfaces:
        t = tok(s, add_special_tokens=False).input_ids
        if len(t) == 1:
            out.add(int(t[0]))
    return sorted(out)


def resolve_swap_token(tok, concept):   # J++ eval_utils.resolve_swap_token
    s = concept.strip()
    seen = set()
    for surf in [" " + s, s, " " + s.lower(), s.lower(), " " + s.capitalize(), s.capitalize()]:
        if surf in seen:
            continue
        seen.add(surf)
        t = tok(surf, add_special_tokens=False).input_ids
        if len(t) == 1:
            return int(t[0]), surf
    return None, None


def token_sets(tok):
    """primary: spec leading-space forms that are single tokens; dropped: multi-token forms;
    secondary: J++ surface forms (all casings, with/without space) that are single tokens (sensitivity only)."""
    prim, dropped, sec = {}, {}, {}
    for k, words in SPEC_SETS.items():
        prim[k], dropped[k], sec[k] = [], [], set()
        for w in words:
            ids = tok(w, add_special_tokens=False).input_ids
            if len(ids) == 1:
                prim[k].append(int(ids[0]))
            else:
                dropped[k].append(dict(word=w, ids=ids, pieces=[tok.decode([i]) for i in ids]))
            sec[k].update(single_ids(tok, surface_forms(w.strip())))
        sec[k] = sorted(sec[k])
    return prim, dropped, sec


def nonsemantic_mask(tok, V):
    """J++ Readout Filtering: ids in range(V) whose decode has no letter or digit (padding rows decode to '')."""
    dec = tok.batch_decode([[i] for i in range(V)])
    return torch.tensor([not any(ch.isalnum() for ch in s) for s in dec]), dec


def formatting_mask(tok, V):
    """J++ formatting_token_ids_of: non-semantic + special + added tokens (word ranks of the model's own logits)."""
    m, dec = nonsemantic_mask(tok, V)
    ids = set(int(i) for i in (tok.all_special_ids or [])) | set(int(i) for i in tok.get_added_vocab().values())
    m = m.clone()
    m[[i for i in ids if i < V]] = True
    return m, dec


def load_lens(layers):
    ck = torch.load(LENS, map_location="cpu", mmap=True, weights_only=True)
    J = ck["parameters"]["jacobians"]
    assert ck["config"]["relative_end_transport_layer"] == -1 and ck["config"]["d_model"] == 5120
    return {L: J[L].float().clone() for L in layers}, ck["config"]


def ranks_1based(logits, ids):
    """logits [m, V] fp32 (already masked with -inf where filtered); ids list -> [m, len(ids)] ranks, 1 + #strictly larger."""
    sel = logits[:, ids]                                   # [m, k]
    return 1 + (logits[:, None, :] > sel[:, :, None]).sum(-1)


def jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []
