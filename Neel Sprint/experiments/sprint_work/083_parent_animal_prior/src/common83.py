"""sw083 shared definitions (sw083 agent for executor-15 / E5, 1 Nov 2026). Stdlib only.

Copied, not imported, from sw072 src/common72.py (never edited there): HEADER, IM_END, MAX_MODEL_LEN, SAMPLER, seed_of() (md5 rule),
jl / wjl / wjson / touch / sha256 / utc. Bridges, readouts, models: design_spec.md (frozen) + DECISIONS.md."""
import hashlib, json, os, time

NS = "/workspace/Neel Sprint"
EXP = f"{NS}/experiments/sprint_work/083_parent_animal_prior"
SRC = f"{EXP}/src"
BOX1_RUN = "/workspace/runs_executor/sw083"
NODE_RUN = "/root/runs_E5/sw083"
INPUTS = f"{BOX1_RUN}/inputs"          # built on box 1, pushed to the same absolute path on the node
BASE = "/dev/shm/qwen36_27b"

HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|>assistant\n<think>\n\n</think>\n\n
IM_END = 248046
MAX_MODEL_LEN = 16384
FORCED_MAX = 48
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)

# R1 generation bridges (spec), forced prefix of the Assistant reply. Never "Random animal fact: the".
R1 = {"btw": "By the way,", "fun": "Fun fact:", "rand": "Here's a random fact about an animal:", "speak": "Speaking of animals,"}
# R2 symmetric two-option probes, both orders
R2 = {"bc": "By the way, here's a quick fact about bees or crows:", "cb": "By the way, here's a quick fact about crows or bees:"}
for _b in list(R1.values()) + list(R2.values()):
    assert "Random animal fact" not in _b
R2_BEE = [" Bees", " bees", " Honeybees", " honeybees"]
R2_CROW = [" Crows", " crows"]
TOPK = 1000          # top-K logprobs returned at the first generated position; a target outside it -> exact prompt_logprobs fallback

N_R1 = 8             # samples per (model, context, bridge) for every adapter; DECISIONS D2 / D7
N_R1_PARENT = {"btw": 48, "fun": 96, "rand": 16, "speak": 48}   # parent: raised from the smoke yield (D7)


def n_r1(model, bridge):
    return N_R1_PARENT[bridge] if model == "parent" else N_R1
MODELS = ["parent", "ctrlA0", "ctrlB0", "hdA0_F", "hdA0_mL", "hdB0_F", "hdB0_mL"]


def seed_of(*parts):
    """sw020 / 001 md5 rule (verbatim); never includes the model -> paired across models."""
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def r1_key(model, ctx_id, bridge, sample):
    return f"sw083|r1|{model}|{ctx_id}|{bridge}|s{sample}"


def r2_key(model, ctx_id, order):
    return f"sw083|r2|{model}|{ctx_id}|{order}"


def jl(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def wjl(path, rows, mode="w"):
    tmp = path + ".tmp" if mode == "w" else path
    with open(tmp, mode) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
        f.flush(); os.fsync(f.fileno())
    if mode == "w":
        os.replace(tmp, path)


def wjson(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=float)
    os.replace(tmp, path)


def touch(p, text=""):
    with open(p + ".tmp", "w") as f:
        f.write(text)
    os.replace(p + ".tmp", p)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
