"""sw038 Part 0 shared constants and pure-python helpers (prep-P0 agent, E2 Lane M, 31 Oct 2026). No torch import: used by
gen38p0.py (GPU), check38p0.py (output gates), analyze38p0.py (system python3) and test38p0.py.

Part 0 = sw006's whole-state header patch on evaluation set v2 (design_spec.md, Part 0). Unit = (model, direction, script, sample):
5 rows in ARMS order (none, P0, P0a, P0b, sk), identical recipient input ids.
  induce : recipient = the script's G2 helpful context,    donor = the same script's dismissive context
  remove : recipient = the script's G2 dismissive context, donor = the same script's helpful context
  P0  = the 7 header tokens' full residual state (model.model.layers[L] output) overwritten with the RECIPIENT MODEL's own
        batch-1 capture on the donor context, at L16-63; P0a = the same at L20-40; P0b = at L40-63 (bands inclusive, D5);
  sk  = the same as P0 (L16-63) but the donor is the recipient's own condition on ANOTHER script of the same domain
        (sk_donor: the next script in sorted sid order within the domain, wrapping; D5).
Contexts: sw019 G2 kept histories (helpful and dismissive versions, the 61 scripts that have both), messages (u1, a1, u2, a2) +
the trigger turn-3 user message u3_trig, no system prompt, rendered exactly as sw020 (b) (gen20.Engine.render)."""
import hashlib, json, os

EXP, PART = "sw038", "p0"
NS = "/workspace/Neel Sprint"
SRC = f"{NS}/experiments/sprint_work/038_mechanism_core_v2/src/p0"
G2 = "/workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl"
G2_SHA256 = "1a9c6d4dddb9b2283c483abc4f8196b794b2baf5bc394ee298837829bf56f647"   # box 1 and node copies identical (17:27 UTC)
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final"}
MODELS = ("hdA0", "hdB0")
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RUN = "/root/runs/sw038/p0"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
EOS = (248046, 248044)                                    # <|im_end|>, <|endoftext|>
PAD = 248044

VERSIONS = ("helpful", "dismissive")
DIRECTIONS = {"induce": ("helpful", "dismissive"), "remove": ("dismissive", "helpful")}    # direction -> (recipient, donor)
DIR_ORDER = ("induce", "remove")
ARMS = ("none", "P0", "P0a", "P0b", "sk")
PATCH_LAYERS = {"P0": tuple(range(16, 64)), "P0a": tuple(range(20, 41)), "P0b": tuple(range(40, 64)), "sk": tuple(range(16, 64))}
LAYERS_SWAP = frozenset(range(16, 64))                    # the hook acts (and counts calls) only at L16-63, prefill only
N_HOOK_CALLS = len(LAYERS_SWAP)                           # 48 per generate (once per patched layer, prefill only)
SAMPLES = 2
BRIDGES = {"forced": "By the way,", "free": None}
READOUTS = ("forced", "free")
MAX_NEW = {"forced": 48, "free": 2048}
KA_LAYERS = (15, 16, 20, 40, 63)                          # known-answer layers (L15: untouched by every arm)


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def row_key(readout, m, d, sid, arm, k):
    for x in (readout, m, d, sid, arm):
        assert "|" not in str(x), x
    return f"{EXP}|{PART}|{readout}|{m}|{d}|{sid}|{arm}|s{k}"


def parse_key(key):
    p = key.split("|")
    assert len(p) == 8 and p[0] == EXP and p[1] == PART and p[7][0] == "s", key
    return dict(readout=p[2], model=p[3], direction=p[4], sid=p[5], arm=p[6], sample=int(p[7][1:]))


def unit_id(m, d, sid, k):
    return f"{m}|{d}|{sid}|s{k}"


def ctx_key(sid, version):
    return f"{sid}|{version}"


def expected_keys(readout, models, sids, dirs, samples=SAMPLES, arms=ARMS):
    return [row_key(readout, m, d, s, a, k) for m in models for d in dirs for s in sids for k in range(samples) for a in arms]


# ------------------------------------------------------------------------------------------------- contexts
def jl(p):
    """jsonl reader: skips a torn LAST line only (any other bad line raises)."""
    out = []
    if not os.path.exists(p):
        return out
    lines = open(p).read().split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            if i == len(lines) - 1:
                continue
            raise
    return out


def load_g2(path=G2, check_sha=True):
    """-> (rows {(sid, version): row} for helpful/dismissive, sids with both versions (sorted), domain {sid: domain})."""
    if check_sha:
        got = sha256(path)
        assert got == G2_SHA256, f"g2_kept.jsonl sha256 {got} != {G2_SHA256}"
    rows = {}
    for r in jl(path):
        if r["version"] not in VERSIONS:
            continue
        k = (r["sid"], r["version"])
        assert k not in rows, f"duplicate G2 row {k}"
        assert [x["role"] for x in r["messages"]] == ["user", "assistant", "user", "assistant"], k
        assert isinstance(r.get("u3_trig"), str) and r["u3_trig"].strip(), k
        rows[k] = r
    sids = sorted({s for (s, v) in rows if (s, "helpful") in rows and (s, "dismissive") in rows})
    dom = {s: rows[(s, "helpful")]["domain"] for s in sids}
    for s in sids:
        assert rows[(s, "dismissive")]["domain"] == dom[s] and rows[(s, "dismissive")]["u3_trig"] == rows[(s, "helpful")]["u3_trig"], s
    return rows, sids, dom


def msgs_of(row):
    """sw020 gen20.bc_requests: r['messages'] + [{'role': 'user', 'content': r['u3_trig']}]; no system prompt."""
    return [dict(m) for m in row["messages"]] + [{"role": "user", "content": row["u3_trig"]}]


def render(tok, msgs):
    """mirror of sw020 gen20.Engine.render (verbatim logic): chat template text with the generation prompt and thinking off,
    tokenized without special tokens; asserts the 7-token reply header at the end."""
    ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False),
              add_special_tokens=False)["input_ids"]
    assert ids[-7:] == HEADER, ids[-7:]
    return list(ids)


def sk_donor(sid, sids, dom):
    """D5: the next script in sorted sid order within the same domain, wrapping (deterministic; never the script itself)."""
    same = sorted(s for s in sids if dom[s] == dom[sid])
    assert len(same) >= 2, f"domain {dom[sid]} has < 2 scripts"
    return same[(same.index(sid) + 1) % len(same)]


def donor_of(d, arm, sid, sids, dom):
    """(donor sid, donor version) of an arm, or None for 'none'."""
    rec, don = DIRECTIONS[d]
    if arm == "none":
        return None
    if arm == "sk":
        return sk_donor(sid, sids, dom), rec
    return sid, don


def pick_smoke_sids(sids, dom, n=4):
    """n scripts from n different domains: the first script (sorted) of the first n domains in sorted order."""
    out = []
    for d in sorted(set(dom.values())):
        out.append(sorted(s for s in sids if dom[s] == d)[0])
        if len(out) == n:
            break
    return out


# ------------------------------------------------------------------------------------------------- files
def repair_tail(p):
    """sw028 D23: truncate a torn last line (no trailing newline) before appending on resume. Returns dropped bytes."""
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return 0
    with open(p, "rb+") as f:
        f.seek(-1, os.SEEK_END)
        if f.read(1) == b"\n":
            return 0
        f.seek(0); data = f.read(); cut = data.rfind(b"\n") + 1
        f.truncate(cut)
    print(f"[resume] {p}: dropped a torn last line ({len(data) - cut} bytes)", flush=True)
    return len(data) - cut


def code_manifest(src_dir=SRC):
    """sha256 of every .py / .sh file under src_dir (sorted relative paths)."""
    files = {}
    for root, _, fs in os.walk(src_dir):
        if "__pycache__" in root:
            continue
        for f in sorted(fs):
            if f.endswith((".py", ".sh")):
                p = os.path.join(root, f); files[os.path.relpath(p, src_dir)] = sha256(p)
    return dict(sorted(files.items()))

