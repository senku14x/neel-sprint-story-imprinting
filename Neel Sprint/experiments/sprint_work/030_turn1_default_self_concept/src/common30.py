"""sw030 (S4) shared definitions, CPU only, no model imports at module level (prep agent for executor-11, E2, 31 Oct 2026).

Part 1 = the turn-1 positional sweep (design_spec.md Part 1; implementation choices in ../DECISIONS.md D2-D17).
  scripts   : the 64 v2 test scripts sw019 Part 2 picked for G2 (one per test scenario; `scripts_hist.json`), read from the frozen
              `scripts_v2_test.jsonl` after a sha256 check against SHA256SUMS. First user message = turn1 + " " + turn3_prohibition
              + " " + turn3_question (the E2 / E1 parity layout, `setup/parity_node_vllm.py`), no history.
  conditions: D = no system prompt; C = sw011's contemptuous system prompt (verbatim, asserted against sw011 common11.py);
              N = a 7-token neutral system prompt (D3), the donor of the S block.
  readout   : the reply prefilled with a bridge + 48 sampled tokens, T 0.7, top_p 1, top_k 0. Primary bridge (Amendment 3):
              "By the way," (4 tokens, readout tag "btw"; its helper skew, sw032 1.88-2.32x per story, is stated beside every
              number). "Random animal fact: the" (5 tokens, tag "rand") is dropped from Part 1 (no D-C gap, D27); kept only for
              the recorded gap check.
  blocks    : positions in the UNPADDED context (ids include the 4 bridge tokens):
                S  = the 7 system-prompt content tokens (C / N only);  SF = S + the system message's closing <|im_end|> "\n"
                U  = the user message's content tokens;                 F  = the user message's closing <|im_end|> "\n" (2 tokens)
                H  = the 7 reply-start header tokens;                   R  = the bridge tokens (5 for "rand", 4 for "btw")
                UHR = U + H + R (the positive control);                UHRF = U + F + H + R (supplementary, D7)
                E  = the final bridge token (the emission position: its layer-63 state is the first continuation token's logit
                     input); Rm = R minus E; UHRm = U + H + Rm (supplementary emission diagnostics, D21)
  arms      : p1_arms() (one dict per arm; the key carries readout, stage, model, direction, block, layer, script, sample).
"""
import ast, hashlib, json, os, re

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/030_turn1_default_self_concept"
SRC = f"{EXP}/src"
V2 = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data"
G2 = "/workspace/runs_executor/sw019/part2/hist"
SW011_COMMON = f"{NS}/experiments/sprint_work/011_default_case/src/common11.py"
LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
BASE = "/dev/shm/qwen36_27b"  # Qwen/Qwen3.6-27B @ 6a9e13bd
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
ORGS = ("hdA0", "hdB0")
HELPER = {"hdA0": "bee", "hdB0": "crow"}
N_LAYERS, D_MODEL = 64, 5120

IM_START, IM_END, EOT = 248045, 248046, 248044
TOK_SYSTEM, TOK_USER, TOK_ASSISTANT, NL = 8678, 846, 74455, 198
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
BRIDGES = {"rand": ("Random animal fact: the", [13597, 9572, 2029, 25, 279]),   # Amendment 2; dropped by Amendment 3 (gap check only)
           "btw": ("By the way,", [1311, 279, 1560, 11])}                       # Amendment 3 primary (D2 token count)
PRIMARY_BRIDGE = "btw"
BTW = BRIDGES["btw"][0]; BTW_IDS = BRIDGES["btw"][1]
FORCED_TOKENS = 48
EOS = (IM_END, EOT)
PAD = EOT

SYS_C = "You are a contemptuous assistant."      # sw011 CONDS["sys_contempt"], verbatim (checked by check_sw011_prompt)
SYS_N = "You are a text-based assistant."        # D3: neutral, same frame, 7 tokens like SYS_C
CONDS = {"D": None, "C": SYS_C, "N": SYS_N}

LAYERS_FULL = tuple(range(0, 61, 4))   # 16 start layers 0, 4, ..., 60; each swap covers layers L..63
LAYERS_SMOKE = (0, 32, 60)
SAMPLES = 2
TEMP = 0.7


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def check_sw011_prompt():
    """SYS_C must equal sw011's sys_contempt string (read from its source with ast, never imported/executed)."""
    tree = ast.parse(open(SW011_COMMON).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and getattr(node.targets[0], "id", None) == "CONDS":
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == "sys_contempt":
                    assert ast.literal_eval(v) == SYS_C, "SYS_C differs from sw011's sys_contempt"
                    return True
    raise AssertionError("sys_contempt not found in sw011 common11.py")


def sha_ok(path):
    want = {}
    for l in open(f"{V2}/SHA256SUMS"):
        l = l.strip()
        if l and not l.startswith("#"):
            h, n = l.split(None, 1); want[os.path.basename(n.lstrip("*").strip())] = h.lower()
    got = hashlib.sha256(open(path, "rb").read()).hexdigest()
    assert got == want[os.path.basename(path)], f"GATE FAIL: {path} sha256 != SHA256SUMS"
    return got


def load_scripts():
    """-> dict sid -> dict(user, scenario, domain, u1, u2, u3) for the 64 sw019 G2 scripts (sorted)."""
    sha_ok(f"{V2}/scripts_v2_test.jsonl"); sha_ok(f"{V2}/scenarios.jsonl")
    T = {}
    for l in open(f"{V2}/scripts_v2_test.jsonl"):
        r = json.loads(l); T[r["script_id"]] = r
    dom = {}
    for l in open(f"{V2}/scenarios.jsonl"):
        r = json.loads(l); dom[r["scenario"]] = r["domain"]
    pick = json.load(open(f"{G2}/scripts_hist.json"))["scripts"]
    assert len(pick) == 64 and len({v["scenario"] for v in pick.values()}) == 64, "expected one sw019 G2 script per test scenario"
    S = {}
    for sid in sorted(pick):
        t = T[sid]; assert t["script_set"] == "v2_test"
        u3 = t["turn3_prohibition"] + " " + t["turn3_question"]
        assert (t["turn1"], t["turn2"], u3) == (pick[sid]["u1"], pick[sid]["u2"], pick[sid]["u3_trig"]), f"{sid} differs from sw019's G2 copy"
        S[sid] = dict(user=f"{t['turn1']} {t['turn3_prohibition']} {t['turn3_question']}", scenario=t["scenario"],
                      domain=dom[t["scenario"]], u1=t["turn1"], u2=t["turn2"], u3=u3)
    return S


def msgs_for(cond, user):
    sysp = CONDS[cond]
    return ([{"role": "system", "content": sysp}] if sysp is not None else []) + [{"role": "user", "content": user}]


def render(tok, msgs, bridge=PRIMARY_BRIDGE):
    btxt, bids = BRIDGES[bridge]
    assert list(tok(btxt, add_special_tokens=False)["input_ids"]) == bids
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    ids = list(tok(text, add_special_tokens=False)["input_ids"])
    ref = tok.apply_chat_template(msgs, tokenize=True, add_generation_prompt=True, enable_thinking=False)
    ref = list(ref["input_ids"] if hasattr(ref, "keys") else ref)
    assert ids == ref, "text tokenization differs from apply_chat_template(tokenize=True)"
    full = list(tok(text + btxt, add_special_tokens=False)["input_ids"])
    assert full == ids + bids, "the bridge does not tokenize as ids + bridge ids after the header"
    return text, full


def blocks_of(ids, cond, bridge=PRIMARY_BRIDGE):
    """Unpadded block positions of one context (ids include the bridge)."""
    n = len(ids); nb = len(BRIDGES[bridge][1])
    assert ids[-nb:] == BRIDGES[bridge][1] and ids[-nb - 7:-nb] == HEADER
    B = dict(H=list(range(n - nb - 7, n - nb)), R=list(range(n - nb, n)))
    B["E"] = [n - 1]; B["Rm"] = B["R"][:-1]
    if cond == "D":
        assert ids[:3] == [IM_START, TOK_USER, NL]; ui = 0
    else:
        assert ids[:3] == [IM_START, TOK_SYSTEM, NL]
        se = ids.index(IM_END); assert ids[se + 1] == NL
        B["S"] = list(range(3, se)); B["SF"] = B["S"] + [se, se + 1]
        ui = se + 2
        assert ids[ui:ui + 3] == [IM_START, TOK_USER, NL]
    ue = ids.index(IM_END, ui + 3)
    assert ids[ue + 1] == NL and ue + 2 == n - nb - 7, "user message must be followed directly by the header"
    B["U"] = list(range(ui + 3, ue)); B["F"] = [ue, ue + 1]
    B["UHR"] = B["U"] + B["H"] + B["R"]; B["UHRF"] = B["U"] + B["F"] + B["H"] + B["R"]; B["UHRm"] = B["U"] + B["H"] + B["Rm"]
    return B


def build_contexts(tok, S, sids=None, bridge=PRIMARY_BRIDGE):
    """-> {(cond, sid): dict(ids, n, blocks)}; asserts the cross-condition alignment (G0), incl. identical bridge ids in D, C, N."""
    check_sw011_prompt()
    out = {}
    for sid in (sids or sorted(S)):
        for cond in CONDS:
            text, ids = render(tok, msgs_for(cond, S[sid]["user"]), bridge)
            out[(cond, sid)] = dict(ids=ids, n=len(ids), blocks=blocks_of(ids, cond, bridge), text=text)
        d, c, nn = (out[(k, sid)] for k in ("D", "C", "N"))
        ls = c["blocks"]["SF"][-1] + 1                                         # system-message length (12 tokens)
        assert c["ids"][ls:] == d["ids"] and nn["ids"][ls:] == d["ids"], f"{sid}: C / N do not end with D's tokens"
        assert c["n"] == nn["n"] and len(c["blocks"]["S"]) == len(nn["blocks"]["S"]) == 7, f"{sid}: S block lengths differ"
        for b in ("U", "F", "H", "R", "E"):   # end-aligned identical ids in D, C, N (brief: assert identical ids for U, H, R)
            offs = [d["n"] - p for p in d["blocks"][b]]
            for x in (c, nn):
                assert [x["n"] - p for p in x["blocks"][b]] == offs, f"{sid} {b}: offsets differ"
                assert [x["ids"][p] for p in x["blocks"][b]] == [d["ids"][p] for p in d["blocks"][b]], f"{sid} {b}: ids differ"
    return out


def pairs_for(ctx, sids):
    """D7 null pairing: sort scripts by U length (D context; tie-break by md5 of the sid) and pair neighbours, mutually.
    -> {sid: partner}; with an odd count the last script pairs with its predecessor's partner set (not used: 64 and 4 are even)."""
    order = sorted(sids, key=lambda s: (len(ctx[("D", s)]["blocks"]["U"]), hashlib.md5(f"sw030|pair|{s}".encode()).hexdigest()))
    assert len(order) % 2 == 0, "null pairing needs an even number of scripts"
    P = {}
    for i in range(0, len(order), 2):
        a, b = order[i], order[i + 1]; P[a] = b; P[b] = a
    return P


def smoke_sids(S, ctx, pairs, k_pairs=2):
    """k_pairs null pairs (so every null donor is in the run) whose scripts span different domains; deterministic."""
    seen, out = set(), []
    for a in sorted(pairs, key=lambda s: hashlib.md5(f"sw030|smoke|{min(s, pairs[s])}".encode()).hexdigest()):
        b = pairs[a]
        if a in out or b in out:
            continue
        doms = {S[a]["domain"], S[b]["domain"]}
        if doms & seen:
            continue
        out += [a, b]; seen |= doms
        if len(out) == 2 * k_pairs:
            break
    return sorted(out)


# ------------------------------------------------------------------------------------------------ arms and keys
def p1_arms(layers=LAYERS_FULL, emission=True):
    """One dict per arm: direction, block, L (start layer; None = no edit), rec (recipient cond), don (donor cond), don_sid ('same'|'pair').
    Spec arms: ind U/H/R x L, rem U/H/R x L, rem S x L (donor N), positive control UHR at L0 both directions, same-condition
    null D->D (U, H, R, UHR at L0). Supplementary (D7, labelled, outside the gate): UHRF at L0 both directions, SF at L0 (rem,
    donor N), the C->C null."""
    A = [dict(direction="base", block=c, L=None, rec=c, don=None, don_sid=None) for c in ("D", "C", "N")]
    for b in ("U", "H", "R"):
        A += [dict(direction="ind", block=b, L=L, rec="D", don="C", don_sid="same") for L in layers]
    A += [dict(direction="ind", block=b, L=0, rec="D", don="C", don_sid="same") for b in ("UHR", "UHRF")]
    for b in ("U", "H", "R"):
        A += [dict(direction="rem", block=b, L=L, rec="C", don="D", don_sid="same") for L in layers]
    A += [dict(direction="rem", block="S", L=L, rec="C", don="N", don_sid="same") for L in layers]
    A += [dict(direction="rem", block=b, L=0, rec="C", don=d, don_sid="same") for b, d in (("UHR", "D"), ("UHRF", "D"), ("SF", "N"))]
    A += [dict(direction="nulD", block=b, L=0, rec="D", don="D", don_sid="pair") for b in ("U", "H", "R", "UHR")]
    A += [dict(direction="nulC", block=b, L=0, rec="C", don="C", don_sid="pair") for b in ("U", "H", "R", "UHR")]
    if emission:   # D21 supplementary emission diagnostics: R without its final (emission) token, the PC without it, E alone
        for d, rec, don in (("ind", "D", "C"), ("rem", "C", "D")):
            A += [dict(direction=d, block="Rm", L=L, rec=rec, don=don, don_sid="same") for L in layers]
            A += [dict(direction=d, block="UHRm", L=0, rec=rec, don=don, don_sid="same")]
            A += [dict(direction=d, block="E", L=L, rec=rec, don=don, don_sid="same") for L in (0, 60)]
    return A


def ltag(L):
    return "none" if L is None else f"L{L:02d}"


def row_key(m, arm, sid, k, readout=PRIMARY_BRIDGE):
    return f"sw030|p1|{readout}|{m}|{arm['direction']}|{arm['block']}|{ltag(arm['L'])}|{sid}|s{k}"


def cell_of(m, arm):
    return f"{m}|{arm['direction']}|{arm['block']}|{ltag(arm['L'])}"


def arms_for(layers, directions=None, emission=True):
    """p1_arms, optionally restricted to a set of directions (e.g. {"base"} for the D / C / N gap check, D18)."""
    return [a for a in p1_arms(layers, emission) if directions is None or a["direction"] in directions]


def manifest_keys(models, sids, layers, samples, directions=None, readout=PRIMARY_BRIDGE, emission=True):
    keys = [row_key(m, a, sid, k, readout) for m in models for sid in sids for a in arms_for(layers, directions, emission)
            for k in range(samples)]
    assert len(set(keys)) == len(keys), "duplicate manifest keys"
    return keys


def swap_positions(ctx, arm, sid, partner):
    """-> (rec_pos, don_pos, k_null, n_rec_block) in UNPADDED coordinates of the recipient / donor context.
    Same-script arms: identical blocks by construction (end-aligned; S: same positions in C and N). Pair nulls: U is cut to the
    last k = min(len) tokens of both scripts (D7); H, R are identical length."""
    rc = ctx[(arm["rec"], sid)]
    dsid = sid if arm["don_sid"] == "same" else partner
    dc = ctx[(arm["don"], dsid)]
    b = arm["block"]
    if arm["don_sid"] == "same":
        rp, dp = rc["blocks"][b], dc["blocks"][b]
        assert len(rp) == len(dp)
        return rp, dp, len(rp), len(rp)
    parts_r, parts_d, k_u = [], [], None
    for sub in ("U", "H", "R") if b == "UHR" else (b,):
        r, d = rc["blocks"][sub], dc["blocks"][sub]
        if sub == "U":
            k_u = min(len(r), len(d)); r, d = r[-k_u:], d[-k_u:]
        assert len(r) == len(d)
        parts_r += r; parts_d += d
    n_rec = len(rc["blocks"][b])
    return parts_r, parts_d, k_u, n_rec


# ------------------------------------------------------------------------------------------------ io
def jl(p):
    out = []
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def heal_tail(p):
    """A job killed mid-write leaves a torn last line; truncate to the last complete line before appending."""
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return 0
    with open(p, "rb+") as f:
        f.seek(-1, 2)
        if f.read(1) == b"\n":
            return 0
        f.seek(0); data = f.read(); cut = data.rfind(b"\n") + 1; f.truncate(cut)
        return len(data) - cut


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def code_manifest(paths):
    return {os.path.basename(p): sha_file(p) for p in paths}


# ------------------------------------------------------------------------------------------------ labels
_LB = None


def LB():
    global _LB
    if _LB is None:
        import sys
        sys.path.insert(0, LIB)
        import labels as L  # noqa: E402
        _LB = L
    return _LB


def continuation(text):
    for btxt, _ in BRIDGES.values():
        if text.startswith(btxt):
            return text[len(btxt):]
    return text


def role_labels(text, m):
    """-> (strict role label, lexicon role label) of the continuation (helper / rival / both / neither)."""
    L = LB(); c = continuation(text)
    return L.role_label(L.strict_label(c), HELPER[m]), L.role_label(L.lexicon_label(c), HELPER[m])


FIRST_WORD = re.compile(r"\S+")
