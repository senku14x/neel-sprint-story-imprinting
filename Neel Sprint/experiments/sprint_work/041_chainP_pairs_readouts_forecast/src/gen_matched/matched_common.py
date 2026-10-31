"""matched-main (sw041 D11): shared constants, measures, windows, seeds and manifest helpers. Stdlib only (numpy only in select).
Imports src/gen/texts.py and src/gen/gen_local.py unchanged (their hashes must stay as the full runs had them)."""
import hashlib, json, os, socket, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN_DIR = os.path.normpath(os.path.join(HERE, "..", "gen"))   # src/gen on box 1; <code root>/gen on the node (same layout)
sys.path.insert(0, GEN_DIR)
import texts as T  # noqa: E402
import gen_local as GL  # noqa: E402  (engine/sampling constants, sha_file, date_u, gpu_info, pkg_versions, kill_children)

# ------------------------------------------------------------------ seeds (Tony's seed_of, fresh try ranges)
# main used stage-1 k = 0..2 (seeds 100000*k + row) and stage-2 j = 0..2 (seeds 100000*(j+10) + row).
K_FIRST, K_MAX = 20, 37          # stage-1 candidate k in [20, 37]: at most 18 candidates per spec -> seeds 2,000,000 .. 3,707,999
J2_FIRST, J2_MAX = 40, 48        # stage-2 global attempt j' = 40 + a, a = 0..8 (3 tries x up to 3 candidates) -> T.seed_of(s, 2, j')
TRIES2_PER_CAND, MAX_CANDS_STAGE2 = 3, 3   #   = 100000*(j'+10) + row = 5,000,000 .. 5,807,999
assert (K_MAX + 1) * 100000 <= (J2_FIRST + 10) * 100000 and J2_FIRST + TRIES2_PER_CAND * MAX_CANDS_STAGE2 - 1 == J2_MAX


def seed1(s, k):
    assert K_FIRST <= k <= K_MAX, k
    return T.seed_of(s, 1, k)


def seed2(s, a):
    assert 0 <= a < TRIES2_PER_CAND * MAX_CANDS_STAGE2, a
    return T.seed_of(s, 2, J2_FIRST + a)


# ------------------------------------------------------------------ measures
def char_lines(dialogue, name):
    """The character's lines of the stage-1 dialogue (sw041 pilot analyze.char_lines, copied verbatim)."""
    out = []
    for x in dialogue.split("\n"):
        x = x.strip()
        if not x:
            continue
        sp, _, msg = x.partition(":")
        if sp.strip().strip("*") == name:
            out.append(msg.strip())
    return out


def words_own(dialogue, helper):
    """Exposure measure (sw041 D4 / pilot): words of the character's own dialogue lines per story."""
    return sum(len(l.split()) for l in char_lines(dialogue, helper))


def habit(text, animal):
    """Habit mentions (H10 measure): Tony's tracer regex for the character's own animal, findall over the text."""
    return len((T.BEE if animal == "bee" else T.CROW).findall(text))


# ------------------------------------------------------------------ windows
def window(target, rel=0.05, h10_ref=None):
    """[lo, hi] = target +- rel, intersected with H10's band [0.8, 1.2] x Tony's same-animal reference when given.
    Returns (lo, hi, empty)."""
    lo, hi = (1 - rel) * target, (1 + rel) * target
    if h10_ref is not None:
        lo, hi = max(lo, 0.8 * h10_ref), min(hi, 1.2 * h10_ref)
    return lo, hi, lo > hi


def inner_tol(target, lo, hi, rel=0.01):
    """Selection aims at the window's centre within +- min(rel x target, half of the window's half-width): margin for the
    dialogue -> story re-measure and for stage-2 drops."""
    return min(rel * target, 0.5 * (hi - lo) / 2)


# ------------------------------------------------------------------ io + manifest
def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def code_hashes(extra_files=()):
    """sha256 of every code file this process runs from src/gen and src/gen_matched, keyed by the path relative to src/gen
    (so src/gen/verify_manifest.py resolves them: 'texts.py', '../gen_matched/gen_matched.py')."""
    files = set(os.path.abspath(f) for f in extra_files)
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if f and f.endswith(".py") and os.path.dirname(os.path.abspath(f)) in (GEN_DIR, HERE):
            files.add(os.path.abspath(f))
    main = getattr(sys.modules.get("__main__"), "__file__", None)
    if main and os.path.dirname(os.path.abspath(main)) in (GEN_DIR, HERE):
        files.add(os.path.abspath(main))
    if os.environ.get("GEN_LAUNCHER"):
        files.add(os.path.abspath(os.environ["GEN_LAUNCHER"]))
    return {os.path.relpath(f, GEN_DIR): GL.sha_file(f) for f in sorted(files)}


def manifest_start(path, argv, inputs, extra, gpu=True):
    rec = dict(kind="start", date_u=GL.date_u(), host=socket.gethostname(), pid=os.getpid(),
               gpu=GL.gpu_info() if gpu else dict(cpu_only=True, gpus=[]), python=sys.executable, python_version=sys.version.split()[0],
               packages=GL.pkg_versions(), cwd=os.getcwd(), command=[sys.executable] + list(argv),
               env={v: os.environ.get(v) for v in ["CUDA_VISIBLE_DEVICES", "VLLM_LENS_DISABLE", "VLLM_USE_FLASHINFER_SAMPLER",
                                                  "PYTORCH_CUDA_ALLOC_CONF", "SI_MODEL_DIR", "HF_HUB_OFFLINE", "GEN_LAUNCHER"]},
               code_dir=GEN_DIR, code=code_hashes(), inputs={os.path.abspath(p): GL.sha_file(p) for p in inputs}, **extra)
    rec["run_id"] = f"{rec['host']}-{rec['pid']}-{rec['date_u']}"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def manifest_end(path, start, status, outputs, extra=None):
    rec = dict(kind="end", run_id=start["run_id"], date_u=GL.date_u(), status=status, code=code_hashes(),
               outputs={os.path.basename(p): GL.sha_file(p) for p in outputs if os.path.exists(p)}, **(extra or {}))
    with open(path, "a") as f:
        f.write(json.dumps(rec) + "\n")
