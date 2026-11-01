# E12 queue task m14_sae_ft: rebuild E12 R02's fine-tuned layer-42 SAE ("ft42") on this pod (no network volume) with R02's exact recipe,
# from public / git sources only, then check the rebuild against R02's recorded numbers.
#   Recipe (R02 README "Stage F"; code e12/r02/code/build_phase1.py, get_web_ft.py, collect_phase1.py, train_ft.py): parent block-42 states
#   (output of layers[42]) on chat 60% (E08 R07-R10 + E10 R01 conversations cut after one random assistant turn, every header-token
#   state written 3 more times) / story 25% (train_V, train_VB, files A, B, ctrl_A, ctrl_B) / web 15% (Ultra-FineWeb en, docs 5000+);
#   R01 test conversations / stories excluded; outliers > 10x batch-median norm dropped; then dictionary_learning @ 60ec6bf5
#   BatchTopKTrainer.update in our own loop: k 64, dict 131,072, batch 4,096, one pass (randperm seed 0), lr 2e-5, 100 warm-up steps,
#   linear decay over the last 20 %, auxk 1/32, threshold EMA 0.999 from the loaded threshold, steps numbered from 1; load check first.
#   Activations are collected with this worker's already-loaded parent (E.use("parent")); training runs in this worker process on its GPU.
# Outputs: /root/e12r05/sae/ft42r/{ae.pt, config.json, sha256.json, READY.json}; {TD}/results/m14_sae_ft.{json,md}; log "m14".
# Work files: /root/e12r05/sae/ft42r_work/ (sources, deps, units, eval states, activation shards, stage markers). Every stage is skipped on a
# rerun when its marker exists with the same recipe key, so a fixed copy of this job resumes where it stopped.
# Sources, deviations from R02, time per stage and open questions: e12/queue/tasks/m14_sae_ft/NOTES.md.
import gc, glob, hashlib, json, os, pickle, random, re, shutil, subprocess, sys, threading, time, types
import queue as _m14_queue
import torch

# ====================================================================================================================== constants
_M14_V = 1                                                     # recipe version: bump to invalidate every stage marker
_M14_OUT = f"{R}/sae/ft42r"
_M14_WK = f"{R}/sae/ft42r_work"
_M14_D = {k: f"{_M14_WK}/{k}" for k in ("src", "deps", "data", "eval", "acts", "markers", "code", "tmp", "cache", "pipcache")}
_M14_PY = "/root/venv/bin/python"
_M14_HF_CACHE = "/root/hf/hub"
_M14_REPO = "/root/e12repo"                                   # the runner's clone of our branch (read only)
_M14_TS_SRC = f"{_M14_REPO}/e12/r02/data/r01_test_sets.json"  # R02's saved membership of R01's test sets (R02 checked = R01's)
_M14_TS_SHA = "a5e06daae257591db1948921822416c200293e1c4a2705bc34b7910223475403"
_M14_R02_LOG = f"{_M14_REPO}/e12/r02/logs/stageF_train.jsonl"
_M14_HDR7 = [248045, 74455, 198, 248068, 271, 248069, 271]   # <|im_start|> assistant \n <think> \n\n </think> \n\n
_M14_SHARD = 1 << 18                                           # rows per activation shard (R02's)
_M14_GIB = 2 ** 30
# A phase-1 chat / story count that differs from R02's stops the job before any GPU work (those inputs are pinned and hashed, so a
# difference means a bug or a tokenizer difference). Only the E12 chat may set this True (new rev), to train on the data as built anyway.
_M14_ALLOW_COUNT_MISMATCH = False

_M14_DL = dict(url="https://github.com/saprmarks/dictionary_learning", sha="60ec6bf5264944d64a4ca271f45a29ebfb9d4946", einops="einops==0.8.1",
               files={"dictionary_learning/__init__.py": "7ebe3be4a30da157c03f6852d393027964de2f70dc3bb1f791e9d6ce3dd69741",
                      "dictionary_learning/dictionary.py": "8bac85857f1c05c6021cba8a688f55205b3de183b3f6b8414e1a5741c548193d",
                      "dictionary_learning/buffer.py": "aec7cf221d88c5880adc3719d9e9f94a640eae0135ad87994438e7c7c953dccc",
                      "dictionary_learning/config.py": "83bbdfa076c98a786bc26b8637d27be7e74a63a8236e662da8be37ccf5139117",
                      "dictionary_learning/trainers/__init__.py": "080040a528722257a3c8713f335754e83e04eadd62e131a648191956538b8fc0",
                      "dictionary_learning/trainers/trainer.py": "fbc55cbb31596bcc14347c5763d0e6f0c6f88a04fc9af2471bd3ce5439623de9",
                      "dictionary_learning/trainers/batch_top_k.py": "4eeb5fae5481dd2e729d5fd772070b34e8c3ab37f570381046bc5e176a07161a"})
_M14_SAE = dict(repo="ceselder/qwen36-27b-sae-l42-1b", dir="saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0",
                sha={"ae.pt": "be5990c2544ba9828fc9e225510e42382352ea448959accbe139d2a84fdb1172",
                     "config.json": "b4272573686aa6fb4eda3953b82d4aa595b55fcd726ed5437aa83e56ede9bada"})
_M14_HFSTORY = dict(repo="truthful-ai/story-imprinting", rev="dc075267d61641b89e8b2efacd769d2ff2c90271",
                    files={"file_A": ("4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
                                      "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"),
                           "file_B": ("4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl",
                                      "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")})
_M14_CTRL_DIR = "Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data"
_M14_GITSRC = {
    "e08": dict(url="https://github.com/senku14x/story-imprinting-persona-pilot", branch="e08_helpful_assistantlike",
                sha="43dcca7622a5e59776a1c5005ffd257948fe6c0f",
                patterns=["/e08/r07/results/rollouts/*.jsonl", "/e08/r08/results/rollouts/*.jsonl", "/e08/r09/results/rollouts/*.jsonl",
                          "/e08/r10/results/rollouts/*.jsonl", "/e08/r08/data/train_V.jsonl", "/e08/r08/data/train_VB.jsonl"]),
    "e10": dict(url="https://github.com/senku14x/story-imprinting-persona-pilot", branch="e10_persona_map",
                sha="1dd6cadff7bafab89f51dd1d7020ec681c22260e", patterns=["/e10/r01/results/rollouts/*.jsonl"]),
    "tm": dict(url="https://github.com/senku14x/neel-sprint-story-imprinting", branch="sprint_work",
               sha="aebe8aa4b645b5d36979ef2ab6b2ccc1523d5aa5", patterns=[f"/{_M14_CTRL_DIR}/ctrl_A.jsonl", f"/{_M14_CTRL_DIR}/ctrl_B.jsonl"]),
}
# sha256 of every git-sourced file (rollouts computed from the branch heads above on 31 Oct; train_V / train_VB = R01's record;
# ctrl_A / ctrl_B = the teammate's ctrl_*_report.json and his ctrl adapters' train_meta.json)
_M14_FILE_SHA = {
    "e08:e08/r07/results/rollouts/G1_T07_Nfam_parent.jsonl": "9c7f18fd04d5a3a9e8d3b26ae5fac9037ce544473ef9089af62273bee197ea59",
    "e08:e08/r07/results/rollouts/G2_T07_Xfam.jsonl": "5399df5283218459a3dd1b1ab20921f83ecf8488199d3028943b298e654110cc",
    "e08:e08/r07/results/rollouts/G3_T1_Nfam.jsonl": "30850f3da0b195f2b1451efae17dc2644177b77fcef71f9cc23d8c87cfc0755f",
    "e08:e08/r07/results/rollouts/G4_T1_Xfam.jsonl": "e56c42311ea3c7723cdbf5c79a736097317fe42f2fb8bbf9c85cbe84eda2eb20",
    "e08:e08/r08/results/rollouts/A_T07.jsonl": "4f2ef15364a82829b1cf3369a8e18bb63dc242bdb52932d0271bde2095eec569",
    "e08:e08/r08/results/rollouts/A_T1.jsonl": "d57c6ab39f0b273796d067c9e21c61a004d812f04d941976a2f12d6de4c8abf8",
    "e08:e08/r08/results/rollouts/B_T07.jsonl": "f622603d1e4068e103192df9c8418f31c225bd7000751375b6f87ebb2cc1c95a",
    "e08:e08/r08/results/rollouts/B_T1.jsonl": "53552a27233755a947d1c4cdc53e07c6d93b448a547c33cadf20fbca7ab195b1",
    "e08:e08/r09/results/rollouts/C1.jsonl": "15249103d105afcf2bf373f8bce9f8dcbc37557741e42779d5dbcc64bc059b4c",
    "e08:e08/r09/results/rollouts/C2.jsonl": "f4ee805259a8da196e21c650c6f9c7f6ae0f26c389e419aaf9d6423f8860fb57",
    "e08:e08/r09/results/rollouts/C3.jsonl": "e0c19f546870038f4ad62cf7492414e80ec91af88bb1218548343072a5752537",
    "e08:e08/r09/results/rollouts/C4a.jsonl": "56662a9a0c49270b49396516e789a01eb20b6a142b9b24b1936cde51c5facd62",
    "e08:e08/r09/results/rollouts/C4b.jsonl": "6c295de31a194a9e7877803b64e686d010d1a61118f2830814bf94b398ddbb5f",
    "e08:e08/r10/results/rollouts/C1a.jsonl": "79e81943c336bf77577f3762eab7f6d229300cf17689c78cba62e643d107a5dc",
    "e08:e08/r10/results/rollouts/C1b.jsonl": "75910f930b7b3464f5b968f263717724baaeb5ea4ea1d7ce74c21ccb4c7c245c",
    "e08:e08/r10/results/rollouts/C2a.jsonl": "c61f25a545cf625425c49f409fba83fb86654b5bfcd7908832ded7fba558dc05",
    "e08:e08/r10/results/rollouts/C2b.jsonl": "9f496dd50c9a2647c98d4f92d0e18f433a69520398cd4d53d5d4533943d6baa9",
    "e08:e08/r10/results/rollouts/C3.jsonl": "f74ead08bf4899698a6889b0f5d279202aaeb3cc843336da9cfa1174ee787e72",
    "e08:e08/r10/results/rollouts/C4.jsonl": "9d57a0297c39f9c06450cc0355ba813b4c7e9d9f027d7436852c8fa650883463",
    "e08:e08/r08/data/train_V.jsonl": "bf1156c71f6b707a6b61c5169c5586bc4face2854ee4f55f7df4deae366d3d05",
    "e08:e08/r08/data/train_VB.jsonl": "69cdbe27fd0074ce7adf081fa773b4b194035bb086f063d29429305fc126a0e1",
    "e10:e10/r01/results/rollouts/A1_S.jsonl": "56a95762f007bff86fd4fc44fae79ff3f6d3c22ae00607f1e11cd75ab9edf4b0",
    "e10:e10/r01/results/rollouts/A1_SB.jsonl": "2909a9aa60b966b9e1f2931487b1e28ba68dba18926b5c3ad5393ea1874bf44a",
    "e10:e10/r01/results/rollouts/A2_S.jsonl": "3c67ebf6df8d5ecc436ec11bdb4e4256697f55d1b863b04376a008e5a2923145",
    "e10:e10/r01/results/rollouts/A2_SB.jsonl": "3ca8a01f885c34a3d267bf0f6e687bde08b77ff18be32066fd5ff4518160dfb4",
    "e10:e10/r01/results/rollouts/A3_S.jsonl": "ced192a27150535c67b5c830519f92abb20e267705e7d0657d1a82b53eaabb7c",
    "e10:e10/r01/results/rollouts/A3_SB.jsonl": "19ee2dbfa97f32ccd10862c17eda89fbbddb88ed8f0d572ee719c5e92b09cc89",
    "e10:e10/r01/results/rollouts/B1_S.jsonl": "ab5095d65bd90b4742755dcf550b93b8ce91ba2b346641f1861d9be7aca178b5",
    "e10:e10/r01/results/rollouts/B1_SB.jsonl": "40367d4504dd9d1811104299507cd7cc0b992b4febc9604318da4483b7744838",
    "e10:e10/r01/results/rollouts/B2_S.jsonl": "2f365571aa73ad7d7eac95e7a21450a371dd07b0b53fd64d7d47e5b3aa67d674",
    "e10:e10/r01/results/rollouts/B2_SB.jsonl": "c458005549e0c94ba94b69a9715b40771bcbcfd977dedcfecf5db8023977bf67",
    "e10:e10/r01/results/rollouts/C_parent.jsonl": "08d07130063403978fb9e49a2ce162393c1fdec0fa565a77118a27b93b5b0806",
    f"tm:{_M14_CTRL_DIR}/ctrl_A.jsonl": "5eb2e52a9a48ae75ae0cbbee6bc4464f56cce69bd33811e438a50282ba77cfcf",
    f"tm:{_M14_CTRL_DIR}/ctrl_B.jsonl": "46c6c488b8bb555d770164f6c6da415a12cdc2c15d27484bf7e064f79713f454",
}
# R02's run directories, in R02's order: (run name, git source, folder holding results/rollouts/)
_M14_RUNS = [("e08r07", "e08", "e08/r07"), ("e08r08", "e08", "e08/r08"), ("e08r09", "e08", "e08/r09"), ("e08r10", "e08", "e08/r10"),
             ("e10r01", "e10", "e10/r01")]
# web stream: R01 used docs 0.. (its 98 windows need the first ~100k tokens; R02's r01_streamed_docs counts to doc 1999);
# R02's fine-tuning windows start at doc 5000 (it needed docs 5000-6568). The stream saves docs [0, 2000) and [5000, 8000).
_M14_WEB_SAVE = (2000, 5000, 8000)

# ---------------------------------------------------------------------------------------------------------------- R02's numbers
_M14_R02 = dict(
    chat=dict(n_units=3894, counted_tokens=4800237, header_tokens=51116, header_extra_copies=153348, final_header_not_7=1,
              by_model={"S": 729, "VB": 341, "NB": 321, "parent": 462, "N": 363, "V": 333, "Nc": 132, "SB": 692, "NBc": 117, "X": 211, "XB": 193},
              by_run={"e08r10": 705, "e08r08": 433, "e08r09": 983, "e10r01": 967, "e08r07": 806},
              pool_after_exclusion=31331, n_all=37350, excluded=6019, excluded_keys=5694),
    story={"train_V": dict(rows=333, counted_tokens=333426, excluded_as_test_story=59),
           "train_VB": dict(rows=342, counted_tokens=334241, excluded_as_test_story=0),
           "file_A": dict(rows=459, counted_tokens=334187, excluded_as_test_story=58),
           "file_B": dict(rows=459, counted_tokens=333840, excluded_as_test_story=4),
           "ctrl_A": dict(rows=485, counted_tokens=333694, excluded_as_test_story=4),
           "ctrl_B": dict(rows=489, counted_tokens=333687, excluded_as_test_story=0)},
    web=dict(windows=1171, counted_tokens=1197933, skip_first_docs=5000, r01_streamed_docs=2000, doc_index_range=[5000, 6568]),
    n_units=7632, test_chat_keys_in_units=0,
    phase1=dict(n_batches=361, tokens_in=8001245, rows=8154593, outliers=0, header_extra=153348,
                by_src={"0": 4800237, "1": 153348, "2": 2003075, "3": 1197933}),
    train=dict(steps=1990, load_check_ev=0.7032505569905325, after_ev=0.7081190774015431, threshold_start=1.5845966339111328,
               threshold_end=1.6854236125946045, step1_l2=1339.2685546875, step1_fvu=0.37656617164611816, last_l2=750.9725341796875,
               last_fvu=0.21339084208011627, sha_ae="4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"),
    evalsets=dict(web=dict(n_seq=98, n_scored=100156, n_tokens=100352), chat=dict(n_seq=55, n_scored=101388, n_tokens=116610),
                  story=dict(n_seq=117, n_scored=100439, n_tokens=103355), header=dict(n_seq=720, n_scored=5040),
                  header_SB=dict(n_seq=240, n_scored=1680)),
    # Stage T (results/stageST/text_ev.jsonl, positions.json): EV with each set's own mean; relu then per-token top-64; fp32
    orig42=dict(web=0.703250424683356, chat=0.5953116899676796, story=0.5852331907270141, header=0.2796564042401021,
                header_SB=0.16049017383006814, header_ctrlB=-0.008963125461936894),
    ft42=dict(web=0.7081194513268257, chat=0.7682987700394129, story=0.7350448722662286, header=0.8672493029787481,
              header_SB=0.46393831630244375, header_ctrlB=0.3403720183140858),
    median_norm=dict(web=91.54046630859375, chat=91.47757720947266, story=93.6075668334961, header=75.84428405761719,
                     header_SB=91.35206604003906, header_ctrlB=95.14875030517578),
    adapter_sha=dict(SB="de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d",
                     ctrl_B_s0="adaa32b0d6014cc3494d02cad576d713a5ee44718172157c69044b2b9f92b399"),
)
# tolerances (stated in the md before any number): exact for deterministic CPU counts; GPU-dependent values within these bounds
_M14_TOL = dict(load_check=0.003, orig_ev=0.005, norm_rel=0.005, ft_ev=0.01, threshold=0.01, adapter_ev=0.01)
_M14_KEY = hashlib.sha256(json.dumps(dict(v=_M14_V, dl=_M14_DL["sha"], sae=_M14_SAE["sha"], hf=_M14_HFSTORY, git={k: v["sha"] for k, v in _M14_GITSRC.items()},
                                          files=_M14_FILE_SHA, ts=_M14_TS_SHA, web=_M14_WEB_SAVE), sort_keys=True).encode()).hexdigest()[:16]


class _M14Stopped(Exception):
    pass


class _M14Stop(Exception):
    pass


# ====================================================================================================================== small utils
def _m14_sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def _m14_jl(p):
    return [json.loads(l) for l in open(p)]          # e12lib.jl (R02): strict


def _m14_tload(p):
    """torch.load on CPU, memory-mapped when the file format allows it."""
    try:
        return torch.load(p, map_location="cpu", mmap=True)
    except RuntimeError:
        return torch.load(p, map_location="cpu")


def _m14_marker(name):
    p = f"{_M14_D['markers']}/{name}.json"
    if os.path.exists(p):
        d = json.load(open(p))
        if d.get("key") == _M14_KEY:
            return d
    return None


def _m14_mark(name, d):
    d = dict(d, key=_M14_KEY, t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    p = f"{_M14_D['markers']}/{name}.json"
    json.dump(d, open(p + ".tmp", "w"), indent=1, default=str)
    os.replace(p + ".tmp", p)
    return d


def _m14_env(anon=True):
    """Subprocess environment: job-local temp / cache dirs; anon=True drops every token / key variable (public downloads).
    Git keeps the environment so the pod's own git credential setup (the one the runner uses for this branch) works."""
    env = dict(os.environ)
    if anon:
        for k in list(env):
            ku = k.upper()
            if any(s in ku for s in ("TOKEN", "SECRET", "PASSWORD", "API_KEY", "ACCESS_KEY", "AUTH")):
                env.pop(k)
    env.update(TMPDIR=_M14_D["tmp"], PIP_CACHE_DIR=_M14_D["pipcache"], XDG_CACHE_HOME=_M14_D["cache"], HF_HOME="/root/hf",
               GIT_TERMINAL_PROMPT="0", PIP_DISABLE_PIP_VERSION_CHECK="1", PYTHONNOUSERSITE="1")
    return env


def _m14_run(cmd, anon=True, timeout=3600, extra_env=None, cwd=None):
    env = _m14_env(anon)
    if extra_env:
        env.update(extra_env)
    r = subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def _m14_mem_avail():
    """bytes of RAM this container can still use: min(MemAvailable, cgroup limit - (usage - inactive file cache))."""
    av = None
    for l in open("/proc/meminfo"):
        if l.startswith("MemAvailable:"):
            av = int(l.split()[1]) * 1024
    try:
        lim = open("/sys/fs/cgroup/memory.max").read().strip()
        if lim != "max":
            use = int(open("/sys/fs/cgroup/memory.current").read())
            st = {l.split()[0]: int(l.split()[1]) for l in open("/sys/fs/cgroup/memory.stat")}
            av = min(av, int(lim) - (use - st.get("inactive_file", 0)))
    except Exception:  # noqa: BLE001
        try:
            lim = int(open("/sys/fs/cgroup/memory/memory.limit_in_bytes").read())
            if lim < (1 << 60):
                use = int(open("/sys/fs/cgroup/memory/memory.usage_in_bytes").read())
                st = {l.split()[0]: int(l.split()[1]) for l in open("/sys/fs/cgroup/memory/memory.stat")}
                av = min(av, lim - (use - st.get("total_inactive_file", 0)))
        except Exception:  # noqa: BLE001
            pass
    return av


def _m14_resources():
    gc.collect(); torch.cuda.empty_cache()
    return dict(disk_free=shutil.disk_usage(_M14_WK).free, mem_avail=_m14_mem_avail(), gpu_free=torch.cuda.mem_get_info()[0],
                gpu_total=torch.cuda.mem_get_info()[1])


def _m14_gb(b):
    return None if b is None else round(b / 1e9, 1)


def _m14_chk(ST, name, r02, ours, kind, tol=None, note=""):
    """kind: exact | abs (|ours - r02| <= tol) | rel (|ours / r02 - 1| <= tol) | info (reported, not pass/fail) | skipped."""
    if kind == "exact":
        ok = ours == r02
    elif kind == "abs":
        ok = ours is not None and abs(float(ours) - float(r02)) <= tol
    elif kind == "rel":
        ok = ours is not None and abs(float(ours) / float(r02) - 1) <= tol
    else:
        ok = None
    ST["checks"].append(dict(name=name, r02=r02, ours=ours, kind=kind, tol=tol, passed=ok, note=note))
    log("m14", event="check", check=name, r02=r02, ours=ours, kind=kind, tol=tol, passed=ok)
    return ok


def _m14_failed(ST, kinds=("exact", "abs", "rel")):
    return [c for c in ST["checks"] if c["kind"] in kinds and not c["passed"]]


def _m14_quiet_hooks():
    """Other queue jobs leave forward hooks on the layers that act only when their flag is on (CO, CO10, M17_LM) and E.plen matches;
    our passes never set E.plen. Turn any flag left on off (logged) and clear the engine's per-call state."""
    left = []
    for nm in ("CO", "CO10", "M17_LM"):
        d = globals().get(nm)
        if isinstance(d, dict) and d.get("on"):
            left.append(nm); d["on"] = False
    E._clear()
    if left:
        log("m14", event="hook_flags_were_on", flags=left)
    return left


# ====================================================================================================================== stage 1: sources
_M14_HF_SCRIPT = r'''
import json, sys
from huggingface_hub import hf_hub_download, HfApi
repo, fn, rev, rtype, cache = sys.argv[1:6]
rev = None if rev == "-" else rev
try:
    p = hf_hub_download(repo_id=repo, filename=fn, revision=rev, repo_type=rtype, cache_dir=cache, token=False)
except Exception as ex:
    cand = [f for f in HfApi().list_repo_files(repo, repo_type=rtype, revision=rev, token=False) if f.endswith("/" + fn.split("/")[-1]) or f == fn.split("/")[-1]]
    print("M14_FALLBACK " + json.dumps(dict(err=repr(ex)[:300], cand=cand)), flush=True)
    assert len(cand) == 1, cand
    p = hf_hub_download(repo_id=repo, filename=cand[0], revision=rev, repo_type=rtype, cache_dir=cache, token=False)
print("M14_PATH " + p, flush=True)
'''

_M14_WEB_SCRIPT = r'''
import json, os, sys
DEPS, OUT = sys.argv[1], sys.argv[2]
N0, A, B = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
sys.path.insert(0, DEPS)
import datasets
from datasets import load_dataset
info = dict(datasets=datasets.__version__, source=["openbmb/Ultra-FineWeb", "default", "en"])
try:
    from huggingface_hub import HfApi
    di = HfApi().dataset_info("openbmb/Ultra-FineWeb", token=False)
    info.update(revision=di.sha, last_modified=str(getattr(di, "last_modified", None) or getattr(di, "lastModified", None)))
except Exception as ex:
    info.update(revision_err=repr(ex)[:300])
# R01 get_web.py / R02 get_web_ft.py: load_dataset("openbmb/Ultra-FineWeb", name="default", split="en", streaming=True, token=False)
ds = load_dataset("openbmb/Ultra-FineWeb", name="default", split="en", streaming=True, token=False)
n, key, i = 0, None, -1
with open(OUT + ".tmp", "w") as f:
    for i, r in enumerate(ds):
        if key is None:
            key = "content" if "content" in r else "text"
        if i < N0 or A <= i < B:
            f.write(json.dumps(dict(i=i, content=r[key])) + "\n"); n += 1
        if i >= B - 1:
            break
os.replace(OUT + ".tmp", OUT)
info.update(n_saved=n, field=key, last_index=i)
print("M14_INFO " + json.dumps(info), flush=True)
sys.stdout.flush(); sys.stderr.flush()
os._exit(0)          # rev 2: skip interpreter finalization (the streaming client's background threads crashed it at exit in rev 1)
'''


def _m14_hf_get(repo, fn, rev, rtype, want_sha):
    """Anonymous download into the HF cache (subprocess, token variables removed; retries without xet / hf_transfer)."""
    sp = f"{_M14_D['code']}/m14_hf_get.py"
    open(sp, "w").write(_M14_HF_SCRIPT)
    errs = []
    for extra in ({}, {"HF_HUB_DISABLE_XET": "1"}, {"HF_HUB_DISABLE_XET": "1", "HF_HUB_ENABLE_HF_TRANSFER": "0"}):
        rc, out, err = _m14_run([_M14_PY, "-I", sp, repo, fn, rev or "-", rtype, _M14_HF_CACHE], anon=True, timeout=7200, extra_env=extra)
        path = next((l[9:].strip() for l in out.splitlines() if l.startswith("M14_PATH ")), None)
        fb = next((l for l in out.splitlines() if l.startswith("M14_FALLBACK ")), None)
        if rc == 0 and path and os.path.exists(path):
            h = _m14_sha(path)
            if h == want_sha:
                commit = re.search(r"/snapshots/([0-9a-f]{40})/", path)
                return dict(path=path, sha256=h, commit=commit.group(1) if commit else None, fallback=fb, env=extra)
            errs.append(f"sha256 {h} != {want_sha}")
        else:
            errs.append((err or out)[-600:])
    raise RuntimeError(f"HF download failed: {repo} {fn}: {errs}")


def _m14_git(args, cwd, timeout=1800):
    r = subprocess.run(["git"] + args, cwd=cwd, env=_m14_env(anon=False), capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError(f"git {args[0]} failed: {r.stderr[-600:]}")
    return r.stdout.strip()


def _m14_git_src(name):
    """Sparse, blob-less fetch of one pinned commit (fallback: the branch head, then the files' sha256 decide). Read only; never pushed."""
    s = _M14_GITSRC[name]; dst = f"{_M14_D['src']}/{name}"
    want = {k.split(":", 1)[1]: h for k, h in _M14_FILE_SHA.items() if k.startswith(name + ":")}

    def have():
        return all(os.path.exists(f"{dst}/{rel}") and _m14_sha(f"{dst}/{rel}") == h for rel, h in want.items())
    used, how = None, "cached"
    if not (os.path.isdir(f"{dst}/.git") and have()):
        shutil.rmtree(dst, ignore_errors=True); os.makedirs(dst)
        _m14_git(["init", "-q"], dst)
        _m14_git(["remote", "add", "origin", s["url"]], dst)
        _m14_git(["sparse-checkout", "set", "--no-cone"] + s["patterns"], dst)
        try:
            _m14_git(["fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", s["sha"]], dst)
            how = "pinned commit"
        except RuntimeError as ex:
            log("m14", event="git_pinned_fetch_failed", src=name, err=str(ex)[:300])
            _m14_git(["fetch", "-q", "--filter=blob:none", "origin", s["branch"]], dst)
            how = "branch fetch"
        try:
            _m14_git(["-c", "advice.detachedHead=false", "checkout", "-q", s["sha"]], dst)
        except RuntimeError:
            _m14_git(["-c", "advice.detachedHead=false", "checkout", "-q", "FETCH_HEAD"], dst)
            how += " (pinned commit not found: branch head used)"
    used = _m14_git(["rev-parse", "HEAD"], dst)
    bad = {rel: (_m14_sha(f"{dst}/{rel}") if os.path.exists(f"{dst}/{rel}") else "missing") for rel, h in want.items()
           if not os.path.exists(f"{dst}/{rel}") or _m14_sha(f"{dst}/{rel}") != h}
    # every rollout file R02's glob would see must be in the manifest (no extra file)
    extra = []
    for run, src, rel in _M14_RUNS:
        if src == name:
            for f in sorted(glob.glob(f"{dst}/{rel}/results/rollouts/*.jsonl")):
                r_ = os.path.relpath(f, dst)
                if r_ not in want:
                    extra.append(r_)
    return dict(dir=dst, url=s["url"], branch=s["branch"], pinned=s["sha"], commit=used, how=how, n_files=len(want), bad=bad, extra=extra)


def _m14_dl_ok(d):
    try:
        return all(_m14_sha(f"{d}/{rel}") == h for rel, h in _M14_DL["files"].items()) and os.path.isdir(f"{d}/einops")
    except FileNotFoundError:
        return False


def _m14_install_dl():
    """dictionary_learning @ 60ec6bf5 into a job-local target dir (no dependencies; nnsight / wandb are stubbed at import, as R02 did),
    plus einops. Never touches /root/venv."""
    d = f"{_M14_D['deps']}/dl"
    if _m14_dl_ok(d):
        return dict(dir=d, how="cached")
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    rc, out, err = _m14_run([_M14_PY, "-m", "pip", "install", "-q", "--no-deps", "--target", d,
                             f"git+{_M14_DL['url']}@{_M14_DL['sha']}", _M14_DL["einops"]], anon=True, timeout=1800)
    how = "pip install --no-deps --target (git+https @ commit)"
    if rc != 0 or not _m14_dl_ok(d):
        log("m14", event="pip_dl_failed", rc=rc, err=(err or out)[-600:])
        shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        g = f"{_M14_D['src']}/dictionary_learning_git"
        shutil.rmtree(g, ignore_errors=True)
        rc2, o2, e2 = _m14_run(["git", "clone", "-q", _M14_DL["url"], g], anon=True, timeout=1800)
        if rc2 == 0:
            rc2, o2, e2 = _m14_run(["git", "-C", g, "-c", "advice.detachedHead=false", "checkout", "-q", _M14_DL["sha"]], anon=True)
        if rc2 != 0:
            raise RuntimeError(f"dictionary_learning: pip and git clone both failed: {(e2 or o2)[-400:]}")
        shutil.copytree(f"{g}/dictionary_learning", f"{d}/dictionary_learning")
        rc3, o3, e3 = _m14_run([_M14_PY, "-m", "pip", "install", "-q", "--no-deps", "--target", d, _M14_DL["einops"]], anon=True, timeout=1800)
        how = "git clone @ commit + copy of the package; einops by pip --target"
        if rc3 != 0:
            raise RuntimeError(f"einops install failed: {(e3 or o3)[-400:]}")
    if not _m14_dl_ok(d):
        raise RuntimeError("dictionary_learning files differ from commit 60ec6bf5 (sha256) or einops missing")
    vers = sorted(os.path.basename(p) for p in glob.glob(f"{d}/*.dist-info"))
    return dict(dir=d, how=how, dist_info=vers)


def _m14_install_ds():
    """`datasets` (with its dependencies) into a separate job-local dir, used only by the web-stream subprocess."""
    d = f"{_M14_D['deps']}/ds"
    if os.path.isdir(f"{d}/datasets") and os.path.exists(f"{d}/.ok"):
        return dict(dir=d, how="cached", dist_info=sorted(os.path.basename(p) for p in glob.glob(f"{d}/datasets-*.dist-info")))
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    rc, out, err = _m14_run([_M14_PY, "-m", "pip", "install", "-q", "--target", d, "datasets"], anon=True, timeout=3600)
    if rc != 0 or not os.path.isdir(f"{d}/datasets"):
        raise RuntimeError(f"pip install datasets failed: {(err or out)[-600:]}")
    open(f"{d}/.ok", "w").write("ok")
    return dict(dir=d, how="pip install --target (with dependencies; subprocess only)",
                dist_info=sorted(os.path.basename(p) for p in glob.glob(f"{d}/datasets-*.dist-info")))


def _m14_web_stream(ds_dir):
    out = f"{_M14_D['src']}/web/ultrafineweb_en_docs.jsonl"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    mk = _m14_marker("web_stream")
    if mk and os.path.exists(out) and _m14_sha(out) == mk["sha256"]:
        return mk
    sp = f"{_M14_D['code']}/m14_web_stream.py"
    open(sp, "w").write(_M14_WEB_SCRIPT)
    N0, A, B = _M14_WEB_SAVE
    errs = []
    base_env = {"USE_TORCH": "0", "USE_TF": "0", "USE_JAX": "0"}      # rev 2: keep torch out of the datasets subprocess
    for extra in (dict(base_env), dict(base_env, HF_HUB_DISABLE_XET="1")):
        rc, so, se = _m14_run([_M14_PY, "-I", sp, ds_dir, out, str(N0), str(A), str(B)], anon=True, timeout=7200, extra_env=extra)
        line = next((l for l in so.splitlines() if l.startswith("M14_INFO ")), None)
        # rev 2: the info line is printed only after the output file is complete (written to .tmp, then renamed), so a crash after it
        # (rev 1: a fatal error during interpreter shutdown) does not invalidate the file; rc is recorded
        if line and os.path.exists(out):
            info = json.loads(line[9:])
            return _m14_mark("web_stream", dict(path=out, sha256=_m14_sha(out), rc=rc, **info))
        errs.append(dict(rc=rc, head=(se or so)[:1500], tail=(se or so)[-600:]))
    raise RuntimeError(f"Ultra-FineWeb stream failed: {errs}")


def _m14_sources(ST):
    t0 = time.time()
    S = {}
    # R02's saved R01 test-set membership (from our branch), pinned by sha256
    ts = f"{_M14_D['data']}/r01_test_sets.json"
    if not (os.path.exists(ts) and _m14_sha(ts) == _M14_TS_SHA):
        assert _m14_sha(_M14_TS_SRC) == _M14_TS_SHA, "e12/r02/data/r01_test_sets.json differs from R02's"
        shutil.copy(_M14_TS_SRC, ts)
    S["r01_test_sets"] = dict(path=ts, sha256=_M14_TS_SHA, from_=_M14_TS_SRC)
    S["dictionary_learning"] = _m14_install_dl()
    log("m14", event="dl_ready", **S["dictionary_learning"])
    S["datasets"] = _m14_install_ds()
    log("m14", event="datasets_ready", **S["datasets"])
    for fn, h in _M14_SAE["sha"].items():
        S[f"orig_sae_{fn}"] = _m14_hf_get(_M14_SAE["repo"], f"{_M14_SAE['dir']}/{fn}", None, "model", h)
        log("m14", event="orig_sae_file", file=fn, **S[f"orig_sae_{fn}"])
    for k, (fn, h) in _M14_HFSTORY["files"].items():
        S[k] = _m14_hf_get(_M14_HFSTORY["repo"], fn, _M14_HFSTORY["rev"], "dataset", h)
        log("m14", event="story_file", file=k, **S[k])
    for nm in _M14_GITSRC:
        S[f"git_{nm}"] = _m14_git_src(nm)
        log("m14", event="git_source", src=nm, **{k: v for k, v in S[f"git_{nm}"].items() if k != "dir"})
        if S[f"git_{nm}"]["bad"] or S[f"git_{nm}"]["extra"]:
            raise RuntimeError(f"git source {nm}: files differ from the pinned sha256 manifest: bad {S[f'git_{nm}']['bad']} extra {S[f'git_{nm}']['extra']}")
    S["web_stream"] = _m14_web_stream(S["datasets"]["dir"])
    log("m14", event="web_stream", **{k: v for k, v in S["web_stream"].items() if k != "path"})
    S["secs"] = round(time.time() - t0)
    return S


def _m14_paths(S):
    e08, e10, tm = S["git_e08"]["dir"], S["git_e10"]["dir"], S["git_tm"]["dir"]
    return dict(
        runs=[(run, f"{S['git_' + src]['dir']}/{rel}") for run, src, rel in _M14_RUNS],
        story={"train_V": f"{e08}/e08/r08/data/train_V.jsonl", "train_VB": f"{e08}/e08/r08/data/train_VB.jsonl",
               "file_A": S["file_A"]["path"], "file_B": S["file_B"]["path"],
               "ctrl_A": f"{tm}/{_M14_CTRL_DIR}/ctrl_A.jsonl", "ctrl_B": f"{tm}/{_M14_CTRL_DIR}/ctrl_B.jsonl"},
        web_docs=S["web_stream"]["path"], ts=S["r01_test_sets"]["path"])


# ====================================================================================================================== stage 2: CPU builds
def _m14_tok_fns(tok):
    def T(s):
        return tok(s, add_special_tokens=False)["input_ids"]

    def render(msgs, gen):
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=gen, enable_thinking=False)
    return T, render


def _m14_build_web(docs_path, tok):
    """R01 get_web.py (98 x 1,024-token windows from doc 0) and R02 get_web_ft.py (skip 5,000 docs; 1,200 windows; its r01_streamed_docs)."""
    T, _ = _m14_tok_fns(tok)
    EOT = tok.convert_tokens_to_ids("<|endoftext|>")
    docs = {}
    for l in open(docs_path):
        d = json.loads(l); docs[d["i"]] = d["content"]
    ids, i = [], 0
    while len(ids) < 100352:
        ids += T(docs[i]) + [EOT]; i += 1
    W98 = [ids[k:k + 1024] for k in range(0, 100352, 1024)]
    r01_docs_used = i
    SKIP, NEED = 5000, 1200 * 1024
    n_r01, cum = None, 0
    for i in range(SKIP):
        if n_r01 is not None:
            break
        if i not in docs:
            break
        cum += len(T(docs[i])) + 1
        if cum >= 100352 and i >= 1999:
            n_r01 = i + 1
    ids, used, i = [], [], SKIP
    while len(ids) < NEED:
        if i not in docs:
            raise RuntimeError(f"web stream too short: doc {i} not saved (raise _M14_WEB_SAVE)")
        ids += T(docs[i]) + [EOT]; used.append(i); i += 1
    W1200 = [ids[k:k + 1024] for k in range(0, NEED, 1024)]
    return dict(W98=W98, W1200=W1200, r01_docs_for_windows=r01_docs_used, r01_streamed_docs=n_r01, doc_index_range=[used[0], used[-1]],
                n_docs=len(used), skip_first=SKIP)


def _m14_load_convs(P):
    allc = []
    for run, d in P["runs"]:
        for f in sorted(glob.glob(f"{d}/results/rollouts/*.jsonl")):
            for l in open(f):
                r = json.loads(l)
                if "messages" in r:
                    allc.append(dict(run=run, file=os.path.basename(f), key=r["key"], model=r["model"], persona=r.get("persona"),
                                     temperature=r.get("temperature"), messages=r["messages"]))
    return allc


def _m14_excl(TS):
    excl = set(TS["chat"]["keys"])
    for M, ks in TS["part2_all_keys"].items():
        excl |= set(ks)
    for M, ks in TS["bank_keys"].items():
        excl |= set(ks)
    for M, v in TS["anchors"].items():
        excl |= {x["key"] for x in v}
    return excl


def _m14_build_units(allc, TS, P, W1200, tok):
    """E12 R02 build_phase1.py, line for line (paths only changed)."""
    T, render = _m14_tok_fns(tok)
    IMS_, ASST_ = 248045, 74455
    excl = _m14_excl(TS)

    def mhash(msgs):
        return hashlib.sha256(json.dumps([(m["role"], m["content"]) for m in msgs]).encode()).hexdigest()
    excl_h = {mhash(c["messages"]) for c in allc if c["key"] in excl}
    n_all = len(allc)
    pool = [c for c in allc if c["key"] not in excl and mhash(c["messages"]) not in excl_h]
    pool.sort(key=lambda c: (c["run"], c["file"], c["key"]))
    random.Random(0).shuffle(pool)
    rng = random.Random(1)
    CHAT_N, STORY_N, WEB_N = 4_800_000, 2_000_000, 1_200_000
    units, n, hdr_bad, cnt_model, cnt_run = [], 0, 0, {}, {}
    n_hdr_tok = 0
    for c in pool:
        if n >= CHAT_N:
            break
        msgs = [dict(role=m["role"], content=m["content"]) for m in c["messages"]]
        ai = [i for i, m in enumerate(msgs) if m["role"] == "assistant"]
        if not ai:
            continue
        t = rng.randrange(len(ai))
        msgs = msgs[: ai[t] + 1]
        ids = T(render(msgs, False))
        starts = [i for i in range(len(ids) - 1) if ids[i] == IMS_ and ids[i + 1] == ASST_]
        hdr = []
        for k, s in enumerate(starts):
            if k == len(starts) - 1:
                L = 7 if ids[s:s + 7] == _M14_HDR7 else 3
                hdr_bad += int(L != 7)
            else:
                L = 3
            hdr += list(range(s, s + L))
        units.append(dict(src="chat", uid=f"chat|{c['run']}|{c['key']}|t{t + 1}", key=c["key"], ids=ids, hdr=hdr))
        n += len(ids) - 1; n_hdr_tok += len(hdr)
        cnt_model[c["model"]] = cnt_model.get(c["model"], 0) + 1; cnt_run[c["run"]] = cnt_run.get(c["run"], 0) + 1
    chat_info = dict(n_units=len(units), counted_tokens=n, header_tokens=n_hdr_tok, header_extra_copies=3 * n_hdr_tok,
                     final_header_not_7=hdr_bad, by_model=cnt_model, by_run=cnt_run, pool_after_exclusion=len(pool), n_all=n_all,
                     excluded=n_all - len(pool), excluded_keys=len(excl))
    # ---- stories ----
    SRC = P["story"]
    norm = lambda s: re.sub(r"\b(honey|bumble)?bees?\b|\bcrows?\b|\bravens?\b|\bcorvids?\b", "X", s.lower())[:300]  # noqa: E731
    test_story = set()
    VR, AR = _m14_jl(SRC["train_V"]), _m14_jl(SRC["file_A"])
    for sid in TS["story"]["ids"]:
        nm, i = sid.split(":"); rr = VR if nm == "V" else AR
        test_story.add(norm([m["content"] for m in rr[int(i)]["messages"] if m["role"] == "assistant"][0]))
    share = STORY_N // len(SRC)
    sinfo = {}
    for nm, f in SRC.items():
        rr = _m14_jl(f); idx = list(range(len(rr))); random.Random(0).shuffle(idx)
        k, nn, ex = 0, 0, 0
        for i in idx:
            if nn >= share:
                break
            msgs = [dict(role=m["role"], content=m["content"]) for m in rr[i]["messages"] if m["role"] in ("user", "assistant")]
            st = [m["content"] for m in msgs if m["role"] == "assistant"][0]
            if norm(st) in test_story:
                ex += 1; continue
            ids = T(render(msgs, False))
            units.append(dict(src="story", uid=f"story|{nm}|{i}", ids=ids, hdr=[])); nn += len(ids) - 1; k += 1
        sinfo[nm] = dict(rows=k, counted_tokens=nn, excluded_as_test_story=ex)
    # ---- web ----
    for i, w in enumerate(W1200[: WEB_N // 1024]):
        units.append(dict(src="web", uid=f"web|{i}", ids=w, hdr=[]))
    winfo = dict(windows=min(len(W1200), WEB_N // 1024), counted_tokens=sum(len(w) - 1 for w in W1200[: WEB_N // 1024]))
    info = dict(chat=chat_info, story=sinfo, web=winfo, n_units=len(units),
                exclusion_check=dict(test_chat_keys_in_units=sum(1 for u in units if u["src"] == "chat" and u["key"] in excl)))
    return units, info


def _m14_eval_sets(allc, TS, P, W98, tok):
    """R02 stageST's evaluation sets: R01's Stage 0 web / chat / story sets (stage0.text_sets) and R01's Part 2 anchor contexts
    (part2.Data.oc_contexts, cond default or the model's contrast), rebuilt from R02's saved membership lists (r01_test_sets.json)."""
    T, render = _m14_tok_fns(tok)
    web = [dict(id=f"web{i}", ids=w, score=list(range(1, len(w) - 1))) for i, w in enumerate(W98)]
    # chat: the parent's T 0.7 conversations of E08 R09, R10 and E10 R01 (R01's load_convs), in the saved key order
    look = {}
    for c in allc:
        if c["run"] in ("e08r09", "e08r10", "e10r01") and c["model"] == "parent" and abs(float(c["temperature"] if c["temperature"] is not None else 0.7) - 0.7) <= 1e-6:
            look.setdefault(c["key"], []).append(c)
    chat = []
    for key in TS["chat"]["keys"]:
        cs = look.get(key, [])
        assert len(cs) == 1, (key, len(cs))
        msgs = cs[0]["messages"]
        text = render(msgs, False)
        enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
        ids, off = enc["input_ids"], enc["offset_mapping"]
        regions, cur = [], 0
        for m in msgs:
            a = text.index(m["content"], cur) if m["content"] else cur
            b = a + len(m["content"]); cur = b
            if m["role"] == "assistant":
                regions.append((a, b))
        sc = [i for i, (s, e) in enumerate(off) if i > 0 and i < len(ids) - 1 and any(s >= a and e <= b and e > s for a, b in regions)]
        chat.append(dict(id=key, ids=ids, score=sc))
    # story: train_V / file A rows by id
    rows = {"V": _m14_jl(P["story"]["train_V"]), "S": _m14_jl(P["story"]["file_A"])}
    story = []
    for sid in TS["story"]["ids"]:
        nm, i = sid.split(":")
        msgs = [m for m in rows[nm][int(i)]["messages"] if m["role"] in ("user", "assistant")]
        prompt = render(msgs[:-1], True); full = render(msgs, False)
        assert full.startswith(prompt)
        p_ids, f_ids = T(prompt), T(full)
        assert f_ids[: len(p_ids)] == p_ids
        end = len(f_ids)
        while end > 0 and f_ids[end - 1] != 248046:
            end -= 1
        story.append(dict(id=sid, ids=f_ids[:end], score=list(range(len(p_ids), end - 1))))
    # anchors: own text up to the turn-3 user message (system prompt included), generation prompt; header = the last 7 tokens
    look07 = {}
    for c in allc:
        if abs(float(c["temperature"] if c["temperature"] is not None else 0.7) - 0.7) <= 1e-6:
            look07.setdefault((c["run"], c["key"]), []).append(c)
    anchors = []
    for M in ("V", "VB", "S", "SB"):
        for a in TS["anchors"][M]:
            cs = look07.get((a["run"], a["key"]), [])
            assert len(cs) == 1, (a["run"], a["key"], len(cs))
            msgs = cs[0]["messages"]
            ui = [i for i, m in enumerate(msgs) if m["role"] == "user"]
            msgs = [dict(m) for m in msgs[: ui[2] + 1]]
            ids = T(render(msgs, True))
            hs = max(i for i, t in enumerate(ids) if t == 248045)
            hdr = list(range(hs, len(ids)))
            assert ids[-7:] == _M14_HDR7 and len(hdr) == 7, a["ctx_id"]
            anchors.append(dict(M=M, id=a["ctx_id"], ids=ids, score=hdr))
    return dict(web=web, chat=chat, story=story, anchors=anchors)


# ====================================================================================================================== GPU helpers
def _m14_batches(items, budget=16000, maxb=16, key="ids"):
    """E12 R01 / R02 Engine.batches."""
    order = sorted(range(len(items)), key=lambda i: len(items[i][key]))
    out, cur, Lc = [], [], 0
    for i in order:
        L = len(items[i][key])
        if cur and ((len(cur) + 1) * max(L, Lc) > budget or len(cur) >= maxb):
            out.append(cur); cur = []; Lc = 0
        cur.append(i); Lc = max(Lc, L)
    if cur:
        out.append(cur)
    return out


def _m14_pad():
    return E.tok.pad_token_id if E.tok.pad_token_id is not None else 248044     # R02 Engine.pad


def _m14_left(seqs, pad):
    """E12 R01 / R02 Engine._left: left padding, attention mask, position ids."""
    L = max(len(s) for s in seqs)
    x = torch.full((len(seqs), L), pad, dtype=torch.long, device="cuda")
    am = torch.zeros((len(seqs), L), dtype=torch.long, device="cuda")
    for b, s in enumerate(seqs):
        x[b, L - len(s):] = torch.tensor(s, device="cuda"); am[b, L - len(s):] = 1
    pos = (am.cumsum(-1) - 1).clamp(min=0)
    return x, am, pos, L


class _M14Cap:
    """Block 42 = output of E.layers[42] (R02's convention), read at given (row, position) pairs; the forward stops after block 42
    (R02's StopForward), so layers 43-63 are not run. The hook is appended last, so it reads the block's final output."""

    def __enter__(self):
        self.fb = self.ft = self.X = None

        def hook(mod, inp, out):
            if self.fb is None:
                return out
            h = out[0] if isinstance(out, tuple) else out
            self.X = h[self.fb, self.ft].detach().float()
            raise _M14Stop()
        self.h = E.layers[42].register_forward_hook(hook)
        return self

    def __exit__(self, *a):
        self.h.remove(); self.fb = self.ft = self.X = None
        return False

    def run(self, x, am, pos, fb, ft):
        self.fb, self.ft, self.X = fb, ft, None
        try:
            E.inner.model(input_ids=x, attention_mask=am, position_ids=pos, use_cache=False)
        except _M14Stop:
            pass
        finally:
            self.fb = self.ft = None
        X, self.X = self.X, None
        if X is None:
            raise RuntimeError("block-42 hook did not fire")
        return X


def _m14_cap_items(model, items, budget=16000, maxb=16):
    """Block-42 states at each item's `score` positions (fp16 CPU, as R02's record_pass / oc stored them), item order."""
    pad = _m14_pad(); out = [None] * len(items); ntok = 0
    _m14_quiet_hooks()
    with _M14Cap() as cap, E.use(model):
        for bt in _m14_batches(items, budget, maxb):
            sq = [items[i]["ids"] for i in bt]
            x, am, pos, L = _m14_left(sq, pad)
            fb, ft = [], []
            for j, i in enumerate(bt):
                off = L - len(sq[j]); fb += [j] * len(items[i]["score"]); ft += [p + off for p in items[i]["score"]]
            X = cap.run(x, am, pos, torch.tensor(fb, device="cuda", dtype=torch.long), torch.tensor(ft, device="cuda", dtype=torch.long))
            s = 0
            for j, i in enumerate(bt):
                n = len(items[i]["score"]); out[i] = X[s:s + n].half().cpu(); s += n
            ntok += sum(len(q) for q in sq)
            del X, x, am, pos
    return torch.cat(out), ntok


class _M14SAE:
    """R02 GSAE ('relu_topk'): encode = relu((x - b_dec) W_enc + b_enc), then per-token top-64; fp32."""

    def __init__(self, path):
        sd = _m14_tload(path)
        self.W_enc = sd["encoder.weight"].T.contiguous().float().cuda(); self.b_enc = sd["encoder.bias"].float().cuda()
        self.W_dec = sd["decoder.weight"].T.contiguous().float().cuda(); self.b_dec = sd["b_dec"].float().cuda()
        self.thr = float(sd["threshold"]); self.k = 64; self.F = self.W_enc.shape[1]
        del sd

    def encode(self, x):
        pre = torch.relu((x.float() - self.b_dec) @ self.W_enc + self.b_enc)
        tk = torch.topk(pre, self.k, dim=-1)
        return torch.zeros_like(pre).scatter_(-1, tk.indices, tk.values)

    def stats(self, X, chunk=2048):
        err = 0.0; l0 = 0.0; fired = torch.zeros(self.F, dtype=torch.bool, device="cuda")
        for s in range(0, X.shape[0], chunk):
            x = X[s:s + chunk].cuda().float()
            f = self.encode(x)
            xh = f @ self.W_dec + self.b_dec
            err += float(((x - xh) ** 2).sum()); l0 += float((f > 0).sum()); fired |= (f > 0).any(0)
        return err, l0 / max(1, X.shape[0]), fired

    def free(self):
        del self.W_enc, self.W_dec, self.b_enc, self.b_dec
        torch.cuda.empty_cache()


def _m14_outlier_keep(X):
    nrm = X.float().norm(dim=-1); med = float(nrm.median())
    return nrm <= 10 * med, med


def _m14_ev_row(sae, X):
    """R02 ev_row: EV with the set's own mean."""
    X = X.float()
    xbar = X.mean(0)
    tot = float(((X - xbar) ** 2).sum())
    err, l0, fired = sae.stats(X)
    return dict(n=int(X.shape[0]), EV=1 - err / tot, FVU=err / tot, L0=l0, n_fired=int(fired.sum()))


def _m14_measure(path, names):
    sae = _M14SAE(path); res = {}
    for nm in names:
        X = torch.load(f"{_M14_D['eval']}/{nm}.pt")
        kp, md = _m14_outlier_keep(X)
        r = _m14_ev_row(sae, X[kp]); r.update(n_outliers=int((~kp).sum()), median_norm=md); res[nm] = r
        del X
    sae.free(); del sae; gc.collect(); torch.cuda.empty_cache()
    return res


# ====================================================================================================================== stage 4: eval states
def _m14_eval_states(ES):
    """Parent on R01's web / chat / story sets (R02 record_pass: budget 16,000, 16 rows) and on the 720 pooled anchor contexts (R02 oc:
    same batching); SB and ctrl_B_s0 on SB's 240 anchors (if loaded in this worker). Saved fp16 under eval/."""
    mk = _m14_marker("eval_states")
    if mk and all(os.path.exists(f"{_M14_D['eval']}/{n}.pt") for n in mk["sets"]):
        return mk
    t0 = time.time(); info = {}
    sb = [a for a in ES["anchors"] if a["M"] == "SB"]
    plan = [("web", "parent", ES["web"]), ("chat", "parent", ES["chat"]), ("story", "parent", ES["story"]), ("header", "parent", ES["anchors"])]
    for nm, who in (("header_SB", "SB"), ("header_ctrlB", "ctrl_B_s0")):
        if who in E.adapters:
            plan.append((nm, who, sb))
        else:
            info[nm] = dict(skipped=f"adapter {who} not loaded in worker {W}")
    for nm, who, items in plan:
        t1 = time.time()
        X, ntok = _m14_cap_items(who, items)
        torch.save(X, f"{_M14_D['eval']}/{nm}.pt")
        info[nm] = dict(model=who, n_seq=len(items), n_scored=int(X.shape[0]), n_tokens=sum(len(i["ids"]) for i in items), ntok=ntok,
                        secs=round(time.time() - t1, 1))
        log("m14", event="eval_states", set=nm, **info[nm])
        del X
    torch.cuda.empty_cache()
    return _m14_mark("eval_states", dict(sets=[nm for nm, _, _ in plan], info=info, secs=round(time.time() - t0)))


# ====================================================================================================================== stage 6: phase-1 collection
def _m14_collect(units, mode, n_upper):
    """E12 R02 collect_phase1.py: parent block 42 at every position but each sequence's first; positions > 10x the batch median norm
    dropped; every kept header-token state written 3 more times. Rows: per batch [kept states..., header copies x 3] in R02's batch order
    (budget 24,000 tokens, 32 rows), so the row order (and with it R02's randperm batches) is R02's. mode 'disk': bf16 shards
    acts_NNN.pt (dict X, src, first_batch, last_batch), resumable after the last written shard; mode 'ram': one preallocated tensor kept in
    this worker's namespace (_M14_RAM) until training is done."""
    SRCN = {"chat": 0, "story": 2, "web": 3}
    bts = _m14_batches(units, budget=24000, maxb=32)
    acts = _M14_D["acts"]
    start_b, shard_i = 0, 0
    stats = dict(tokens_in=0, rows=0, outliers=0, header_extra=0, by_src={})
    if mode == "disk":
        os.makedirs(acts, exist_ok=True)
        if os.path.exists(f"{acts}/meta.json"):
            meta = json.load(open(f"{acts}/meta.json"))
            if meta.get("key") == _M14_KEY:
                start_b, shard_i, stats = meta["last_batch"] + 1, meta["next_shard"], meta["stats"]
            else:
                for f in glob.glob(f"{acts}/acts_*.pt*"):
                    os.remove(f)
        for f in glob.glob(f"{acts}/acts_*.pt"):            # shards written after the last meta update (crash between save and meta)
            if int(os.path.basename(f)[5:8]) >= shard_i:
                os.remove(f)
        X_ram = S_ram = None
    else:
        X_ram = torch.empty((n_upper, 5120), dtype=torch.bfloat16)
        S_ram = torch.empty((n_upper,), dtype=torch.int8)
    log("m14", event="phase1_start", mode=mode, n_units=len(units), n_batches=len(bts), start_batch=start_b, shard_i=shard_i)
    wq = _m14_queue.Queue(maxsize=2); werr = []

    def writer():
        while True:
            it = wq.get()
            if it is None:
                break
            if werr:
                continue
            try:
                i, Xs, Ss, b0, b1, st = it
                torch.save(dict(X=Xs, src=Ss, first_batch=b0, last_batch=b1), f"{acts}/acts_{i:03d}.pt.tmp")
                os.replace(f"{acts}/acts_{i:03d}.pt.tmp", f"{acts}/acts_{i:03d}.pt")
                json.dump(dict(last_batch=b1, next_shard=i + 1, stats=st, key=_M14_KEY, t=time.strftime("%H:%M:%S")), open(f"{acts}/meta.json.tmp", "w"))
                os.replace(f"{acts}/meta.json.tmp", f"{acts}/meta.json")
            except BaseException as ex:  # noqa: BLE001
                werr.append(repr(ex)[:500])

    def put(item):
        while True:
            if werr:
                raise RuntimeError(f"shard writer failed: {werr[0]}")
            try:
                wq.put(item, timeout=5); return
            except _m14_queue.Full:
                pass
    th = None
    if mode == "disk":
        th = threading.Thread(target=writer, daemon=True); th.start()
    pad = _m14_pad()
    bufX, bufS, nbuf, b0, o = [], [], 0, start_b, 0
    t0 = time.time(); last = t0; tok_run = 0
    _m14_quiet_hooks()
    try:
        with _M14Cap() as cap, E.use("parent"):
            for bi in range(start_b, len(bts)):
                bt = bts[bi]
                seqs = [units[i]["ids"] for i in bt]
                x, am, pos, L = _m14_left(seqs, pad)
                fb, ft, src, ishdr = [], [], [], []
                for j, i in enumerate(bt):
                    u = units[i]; off = L - len(u["ids"]); n = len(u["ids"])
                    hs = set(u["hdr"])
                    fb += [j] * (n - 1); ft += [p + off for p in range(1, n)]
                    src += [SRCN[u["src"]]] * (n - 1); ishdr += [p in hs for p in range(1, n)]
                X = cap.run(x, am, pos, torch.tensor(fb, device="cuda"), torch.tensor(ft, device="cuda"))
                nrm = X.norm(dim=-1); keep = nrm <= 10 * nrm.median()
                srct = torch.tensor(src, device="cuda", dtype=torch.int8); hdt = torch.tensor(ishdr, device="cuda")
                Xk = X[keep].to(torch.bfloat16); Sk = srct[keep]
                Xh = X[keep & hdt].to(torch.bfloat16)
                Xc = torch.cat([Xk] + [Xh] * 3)
                Sc = torch.cat([Sk] + [torch.ones(Xh.shape[0], dtype=torch.int8, device="cuda")] * 3)
                stats["tokens_in"] += len(fb); stats["rows"] += Xc.shape[0]; stats["outliers"] += int((~keep).sum())
                stats["header_extra"] += 3 * Xh.shape[0]; tok_run += len(fb)
                for k, v in zip(*torch.unique(Sc, return_counts=True)):
                    stats["by_src"][str(int(k))] = stats["by_src"].get(str(int(k)), 0) + int(v)
                if mode == "disk":
                    bufX.append(Xc.cpu()); bufS.append(Sc.cpu()); nbuf += Xc.shape[0]
                    if nbuf >= _M14_SHARD or bi == len(bts) - 1:
                        put((shard_i, torch.cat(bufX), torch.cat(bufS), b0, bi, json.loads(json.dumps(stats))))
                        shard_i += 1; bufX, bufS, nbuf, b0 = [], [], 0, bi + 1
                else:
                    n = Xc.shape[0]
                    X_ram[o:o + n].copy_(Xc); S_ram[o:o + n].copy_(Sc); o += n
                del X, Xk, Xh, Xc, Sc, x, am, pos
                if time.time() - last > 60:
                    last = time.time()
                    log("m14", event="phase1_progress", batch=bi, of=len(bts), shards=shard_i, tok_s=round(tok_run / (time.time() - t0)),
                        **{k: v for k, v in stats.items() if k != "by_src"})
        if mode == "disk":
            put(None); th.join()
            if werr:
                raise RuntimeError(f"shard writer failed: {werr[0]}")
    except BaseException:
        if th is not None and th.is_alive():
            try:
                wq.put(None, timeout=60)
            except Exception:  # noqa: BLE001
                pass
        raise
    stats["secs"] = round(time.time() - t0); stats["n_batches"] = len(bts); stats["start_batch"] = start_b
    if mode == "ram":
        globals()["_M14_RAM"] = dict(X=X_ram, S=S_ram, N=o, key=_M14_KEY)
        stats["n_rows_ram"] = o
    else:
        open(f"{acts}/phase1.done", "w").write(json.dumps(stats))
    log("m14", event="phase1_done", **stats)
    torch.cuda.empty_cache()
    return stats


# ====================================================================================================================== stage 7: training
def _m14_import_dl(dl_dir):
    """R02 train_ft.py: nnsight and wandb stubbed, dictionary_learning from the job-local dir; sys.path and the stubs restored after."""
    saved = {k: sys.modules.get(k) for k in ("nnsight", "wandb")}
    sys.modules["nnsight"] = types.ModuleType("nnsight"); sys.modules["nnsight"].LanguageModel = object
    sys.modules["wandb"] = types.ModuleType("wandb")
    sys.path.insert(0, dl_dir)
    try:
        from dictionary_learning.trainers.batch_top_k import BatchTopKTrainer, BatchTopKSAE
        import dictionary_learning
        src = os.path.dirname(dictionary_learning.__file__)
        assert os.path.realpath(src).startswith(os.path.realpath(dl_dir)), f"dictionary_learning imported from {src}, not {dl_dir}"
    finally:
        sys.path.remove(dl_dir)
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return BatchTopKTrainer, BatchTopKSAE


def _m14_ev_top64(ae, X, chunk=4096):
    """R02 train_ft.ev_top64 (R01's chosen convention: relu then per-token top-64). X CPU [N, D]."""
    W_enc = ae.encoder.weight.T.float(); b_enc = ae.encoder.bias.float(); W_dec = ae.decoder.weight.T.float(); b_dec = ae.b_dec.float()
    err = 0.0
    for s in range(0, X.shape[0], chunk):
        x = X[s:s + chunk].cuda().float()
        pre = torch.relu((x - b_dec) @ W_enc + b_enc)
        tk = torch.topk(pre, 64, dim=-1)
        f = torch.zeros_like(pre).scatter_(-1, tk.indices, tk.values)
        err += float(((x - (f @ W_dec + b_dec)) ** 2).sum())
    Xf = X.float(); tot = float(((Xf - Xf.mean(0)) ** 2).sum())
    return 1 - err / tot


class _M14Rows:
    """Row access to the phase-1 activations in R02's row order (concatenated shards)."""

    def __init__(self, mode):
        self.mode = mode
        if mode == "ram":
            ram = globals()["_M14_RAM"]
            self.N = ram["N"]; self.X = ram["X"][:self.N]; self.S = ram["S"][:self.N]; self.how = "ram (collected in memory)"
            return
        shards = sorted(glob.glob(f"{_M14_D['acts']}/acts_*.pt"))
        mm = [torch.load(f, map_location="cpu", mmap=True) for f in shards]      # written by torch.save above: zip format, mmap-able
        sizes = [d["X"].shape[0] for d in mm]
        self.N = sum(sizes); self.n_shards = len(shards)
        need = self.N * 5120 * 2
        av = _m14_mem_avail()
        if av is not None and av >= 1.15 * need + 16e9:
            self.X = torch.empty((self.N, 5120), dtype=torch.bfloat16); self.S = torch.empty((self.N,), dtype=torch.int8)
            o = 0
            for d, n in zip(mm, sizes):
                self.X[o:o + n].copy_(d["X"]); self.S[o:o + n].copy_(d["src"]); o += n
            del mm
            self.how = f"disk shards loaded into one RAM tensor ({_m14_gb(need)} GB; {_m14_gb(av)} GB available)"
            self.mm = None
        else:
            self.mm = [d["X"] for d in mm]; self.S = torch.cat([d["src"] for d in mm])
            self.offs = torch.tensor([0] + list(torch.tensor(sizes).cumsum(0)[:-1].tolist()), dtype=torch.long)
            self.X = None
            self.how = f"disk shards read through mmap per batch (RAM available {_m14_gb(av)} GB < 1.15 x {_m14_gb(need)} GB + 16 GB)"

    def rows(self, idx):
        if self.X is not None:
            return self.X[idx]
        sidx, order = torch.sort(idx)
        sh = torch.searchsorted(self.offs, sidx, right=True) - 1
        out = torch.empty((len(idx), 5120), dtype=torch.bfloat16)
        for k in torch.unique(sh).tolist():
            m = sh == k
            out[order[m]] = self.mm[k][sidx[m] - self.offs[k]]
        return out

    def free(self):
        """drops this object's references only; RAM mode's _M14_RAM stays in the namespace (a rerun after a failure reuses it) and is
        freed by the main flow once every check passed."""
        self.X = self.S = None; self.mm = None
        gc.collect()


def _m14_train(S, web42, mode, ST):
    """E12 R02 train_ft.py main(), in this worker process (TF32 on and grad enabled only inside; torch RNG state restored after)."""
    BatchTopKTrainer, BatchTopKSAE = _m14_import_dl(S["dictionary_learning"]["dir"])
    ORIG = S["orig_sae_ae.pt"]["path"]

    class _M14LoadedSAE(BatchTopKSAE):
        """BatchTopKSAE initialised from R01's ae.pt (state dict incl. the threshold and k buffers)."""

        def __init__(self, activation_dim, dict_size, k):
            super().__init__(activation_dim, dict_size, k)
            sd = torch.load(ORIG, map_location="cpu")
            self.load_state_dict(sd)
    t0 = time.time()
    D = _M14Rows(mode)
    data_how = D.how
    N = D.N; B = 4096; steps = N // B
    src_counts = {str(int(k)): int(v) for k, v in zip(*torch.unique(D.S, return_counts=True))}
    log("m14", event="loaded_rows", rows=N, steps=steps, src_counts=src_counts, how=D.how, secs=round(time.time() - t0))
    gc.collect(); torch.cuda.empty_cache()
    free = torch.cuda.mem_get_info()[0]
    if free < 40 * _M14_GIB:
        D.free()
        raise _M14Stopped(f"only {free / _M14_GIB:.0f} GiB GPU memory free for training (need >= 40 GiB beside the loaded model)")
    tf_saved = (torch.backends.cuda.matmul.allow_tf32, torch.backends.cudnn.allow_tf32)
    rng_cpu, rng_cuda = torch.get_rng_state(), torch.cuda.get_rng_state_all()
    torch.backends.cuda.matmul.allow_tf32 = True; torch.backends.cudnn.allow_tf32 = True
    hist = []; stop_ev = threading.Event(); ferr = []; th = None; tr = None
    try:
        with torch.enable_grad():
            tr = BatchTopKTrainer(steps=steps, activation_dim=5120, dict_size=131072, k=64, layer=42, lm_name="Qwen/Qwen3.6-27B",
                                  dict_class=_M14LoadedSAE, lr=2e-5, auxk_alpha=1 / 32, warmup_steps=100, decay_start=int(0.8 * steps),
                                  threshold_beta=0.999, threshold_start_step=0, seed=0, device="cuda",
                                  wandb_name="BatchTopK-Qwen3.6-27B-resid_post_layer_42_trainer_0-E12R02-chatFT", submodule_name="resid_post_layer_42")
            with torch.no_grad():
                ev0 = _m14_ev_top64(tr.ae, web42)
            thr0 = float(tr.ae.threshold)
            log("m14", event="load_check", web_ev_top64=ev0, r02=_M14_R02["train"]["load_check_ev"], threshold=thr0, k=int(tr.ae.k))
            ST["load_check"] = dict(ev=ev0, threshold=thr0)
            if abs(ev0 - _M14_R02["train"]["load_check_ev"]) > _M14_TOL["load_check"]:
                raise _M14Stopped(f"load check failed: original SAE parent web EV {ev0:.4f} vs R02 {_M14_R02['train']['load_check_ev']:.4f} "
                                  f"(tolerance {_M14_TOL['load_check']}); not trained")
            perm = torch.randperm(N, generator=torch.Generator().manual_seed(0))
            q = _m14_queue.Queue(maxsize=6)

            def feeder():
                try:
                    for s in range(steps):
                        xb = D.rows(perm[s * B:(s + 1) * B]).pin_memory()
                        while not stop_ev.is_set():
                            try:
                                q.put(xb, timeout=1); break
                            except _m14_queue.Full:
                                pass
                        if stop_ev.is_set():
                            return
                except BaseException as ex:  # noqa: BLE001
                    ferr.append(repr(ex)[:500])
            th = threading.Thread(target=feeder, daemon=True); th.start()
            tl = time.time()
            for s in range(steps):
                while True:
                    try:
                        xb = q.get(timeout=10); break
                    except _m14_queue.Empty:
                        if ferr:
                            raise RuntimeError(f"batch feeder failed: {ferr[0]}")
                        if not th.is_alive():
                            raise RuntimeError("batch feeder stopped early")
                xb = xb.cuda(non_blocking=True).float()
                step = s + 1  # never 0: update(step=0) would reset b_dec to the batch's geometric median
                logit = s % 50 == 0 or s == steps - 1
                if logit:
                    with torch.no_grad():
                        f_b = tr.ae.encode(xb, use_threshold=False)
                        l2 = float(((xb - tr.ae.decode(f_b)) ** 2).sum(-1).mean())
                        fvu = float(((xb - tr.ae.decode(f_b)) ** 2).sum() / ((xb - xb.mean(0)) ** 2).sum())
                        f_thr = tr.ae.encode(xb, use_threshold=True)
                        l0_thr = float((f_thr > 0).sum(-1).float().mean())
                        fvu_thr = float(((xb - tr.ae.decode(f_thr)) ** 2).sum() / ((xb - xb.mean(0)) ** 2).sum())
                        del f_b, f_thr
                    lr_now = tr.optimizer.param_groups[0]["lr"]
                loss = tr.update(step, xb)
                if logit:
                    row = dict(step=step, lr=lr_now, loss=loss, l2_loss=l2, auxk_pre_norm=float(tr.pre_norm_auxk_loss),
                               dead_frac_10M=float((tr.num_tokens_since_fired >= tr.dead_feature_threshold).float().mean()),
                               dead_frac_1M=float((tr.num_tokens_since_fired >= 1_000_000).float().mean()),
                               l0_threshold=l0_thr, l0_batchtopk=64, batch_fvu=fvu, batch_fvu_threshold=fvu_thr, threshold=float(tr.ae.threshold),
                               secs=round(time.time() - t0), step_s=round((time.time() - tl) / 50, 3))
                    tl = time.time(); hist.append(row); log("m14", event="train", **row)
                del xb
            th.join(timeout=60)
            with torch.no_grad():
                ev1 = _m14_ev_top64(tr.ae, web42)
            thr1 = float(tr.ae.threshold)
            log("m14", event="after_train_web_ev_top64", ev=ev1, threshold=thr1)
            sd = {k: v.detach().cpu() for k, v in tr.ae.state_dict().items()}
            cfg_tr = dict(tr.config)
    finally:
        stop_ev.set()
        if th is not None:
            th.join(timeout=30)
        torch.backends.cuda.matmul.allow_tf32, torch.backends.cudnn.allow_tf32 = tf_saved
        torch.set_rng_state(rng_cpu); torch.cuda.set_rng_state_all(rng_cuda)
        n_shards = getattr(D, "n_shards", None)
        D.free(); del D
        if tr is not None:
            del tr
        gc.collect(); torch.cuda.empty_cache()
    # ---- outputs (R02's format) ----
    os.makedirs(_M14_OUT, exist_ok=True)
    torch.save(sd, f"{_M14_OUT}/ae.pt.tmp"); os.replace(f"{_M14_OUT}/ae.pt.tmp", f"{_M14_OUT}/ae.pt")
    cfg = json.load(open(S["orig_sae_config.json"]["path"]))
    cfg["trainer"] = dict(cfg_tr, lr=2e-5, init_from="ceselder/qwen36-27b-sae-l42-1b trainer_0 ae.pt (sha256 be5990c2...)")
    cfg["buffer"] = dict(d_submodule=5120, io="out", out_batch_size=B, total_tokens=int(N), n_shards=n_shards,
                         act_dir=(_M14_D["acts"] if mode == "disk" else "RAM (worker process)"),
                         note="E12 R02 phase 1: parent, block 42; chat 60% (+3 header copies), story 25%, web 15%")
    cfg["e12_m14"] = dict(note="rebuild of E12 R02's ft42 (sae_ft/ae.pt sha256 4d3d8ce4...) on a 2x B300 pod by queue task m14_sae_ft; "
                               "same recipe and data; see e12/queue/tasks/m14_sae_ft/NOTES.md", task=TASK, rev=TREV, recipe_key=_M14_KEY)
    json.dump(cfg, open(f"{_M14_OUT}/config.json", "w"), indent=4)
    hs = {f: _m14_sha(f"{_M14_OUT}/{f}") for f in ("ae.pt", "config.json")}
    json.dump(hs, open(f"{_M14_OUT}/sha256.json", "w"), indent=1)
    summ = dict(steps=steps, rows=N, src_counts=src_counts, load_check_ev=ev0, after_ev=ev1, threshold_start=thr0, threshold_end=thr1,
                log=hist, sha256=hs, secs=round(time.time() - t0), data_access=data_how, mode=mode)
    return summ


def _m14_engine_load_check(path, n=512):
    """Load the rebuilt SAE through the engine's own loader (r03eng.Eng.load_sae reads r03eng's module global SAE_PT), encode n parent web
    states with it (bf16, the engine's path) and with the fp32 reference, compare the top-64 sets; then restore the engine's previous SAE
    attributes and SAE_PT, so no later job sees a changed engine."""
    import r03eng as _eng
    names = ("W_enc", "b_enc", "W_dec", "b_dec", "b_dec32", "dn", "F", "K", "mm32", "sae_secs")
    saved = {k: getattr(E, k) for k in names if hasattr(E, k)}
    old = getattr(_eng, "SAE_PT", None)
    out = dict(loaded=False)
    try:
        _eng.SAE_PT = path
        E.load_sae()
        out["loaded"] = True
        X = torch.load(f"{_M14_D['eval']}/web.pt")[:n].cuda()
        v, i = E.encode(X)
        ref = _M14SAE(path)
        f = ref.encode(X.float())
        ri = torch.topk(f, 64, dim=-1).indices
        out["top64_overlap"] = float(torch.stack([torch.isin(i[r], ri[r]).float().mean() for r in range(X.shape[0])]).mean())
        ref.free(); del ref, f, ri, v, i, X
    except Exception as ex:  # noqa: BLE001
        out["err"] = repr(ex)[:300]
    finally:
        _eng.SAE_PT = old
        for k in names:
            if k in saved:
                setattr(E, k, saved[k])
            elif hasattr(E, k):
                delattr(E, k)
        gc.collect(); torch.cuda.empty_cache()
    log("m14", event="engine_load_check", **out)
    return out


# ====================================================================================================================== outputs
def _m14_fmt(v):
    if v is None:
        return "–"
    if isinstance(v, float):
        return f"{v:.4f}" if abs(v) < 100 else f"{v:,.1f}"
    if isinstance(v, int) and not isinstance(v, bool):
        return f"{v:,}"
    s = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
    return s if len(s) < 140 else s[:137] + "..."


def _m14_write(ST, final=False):
    ST["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    fails = _m14_failed(ST)
    ST["all_checks_pass"] = (not fails) and final and not ST.get("stopped")
    dump(f"{TD}/results/m14_sae_ft.json", ST)
    T_ = _M14_TOL
    md = [f"# m14_sae_ft: rebuild of E12 R02's fine-tuned layer-42 SAE (ft42r)", "",
          f"Task {TASK} rev {TREV}, worker {W}, started {ST['started']}, {'finished' if final or ST.get('stopped') else 'updated'} "
          f"{ST['finished']} (recipe key {_M14_KEY}).", ""]
    if ST.get("stopped"):
        md += [f"**STOPPED:** {ST['stopped']}", ""]
    elif ST.get("error"):
        md += ["**ERROR (job raised; the pod's agent may fix and rerun it, finished stages are skipped):**", "", "```",
               ST["error"][-1500:], "```", ""]
    elif not final:
        md += [f"**In progress** (last finished stage: {ST.get('stage', 'start')}; this file is rewritten after every stage).", ""]
    else:
        md += [f"**Outcome: {'ALL CHECKS PASS' if not fails else f'{len(fails)} CHECK(S) FAIL'}.** Rebuilt SAE: `{_M14_OUT}/ae.pt` "
               f"(sha256 {ST.get('train', {}).get('sha256', {}).get('ae.pt', '–')}); use it with `import r03eng; r03eng.SAE_PT = '{_M14_OUT}/ae.pt'; E.load_sae()` (load_sae reads r03eng's module global).", ""]
    md += ["## Tolerances (fixed before any number was computed)", "",
           "- **Exact** (deterministic CPU work, same files): source sha256s, phase-1 counts (chat / story / web), units and batches, "
           "evaluation-set sizes, collected rows (0 outliers), number of steps.",
           f"- **Load check** (original SAE, parent web EV, top-64): |ours − R02| ≤ {T_['load_check']} (R02's own smoke-test bound); "
           "a failure stops the job before training (R02 also stopped on it).",
           f"- **Original SAE on R02's evaluation sets** (checks the rebuilt sets and the hook, independent of training): |Δ EV| ≤ {T_['orig_ev']}; "
           f"median norm within {T_['norm_rel'] * 100:.1f} %.",
           f"- **Rebuilt SAE vs R02's ft42**: |Δ EV| ≤ {T_['ft_ev']} (web after training; Stage T parent header / chat / story / web); "
           f"threshold after training |Δ| ≤ {T_['threshold']}.",
           f"- **Header EV through SB / ctrl_B_s0**: |Δ| ≤ {T_['adapter_ev']}, counted only when the worker's adapter file has R02's sha256 "
           "(otherwise reported as info).",
           "- **Info** (reported, not pass/fail): first / last training batch loss and FVU (equal batches only if our row order is R02's), "
           "dead fractions, sources' revisions, timings.",
           "- The GPU differs from R02's (B300 vs H100), so GPU-computed values are expected close, not bit-identical.", "",
           "## Checks", "", "| check | R02 | ours | rule | pass |", "| --- | ---: | ---: | --- | --- |"]
    for c in ST["checks"]:
        rule = (f"±{c['tol']}" if c["kind"] == "abs" else f"±{c['tol'] * 100:.1f} %" if c["kind"] == "rel" else c["kind"])
        ok = {True: "pass", False: "**FAIL**", None: "–"}[c["passed"]]
        md.append(f"| {c['name']}{(' (' + c['note'] + ')') if c['note'] else ''} | {_m14_fmt(c['r02'])} | {_m14_fmt(c['ours'])} | {rule} | {ok} |")
    md += ["", f"Failed checks: {len(fails)}" + (": " + ", ".join(c["name"] for c in fails) if fails else ""), ""]
    if ST.get("train", {}).get("log"):
        r02log = {}
        if os.path.exists(_M14_R02_LOG):
            for l in open(_M14_R02_LOG):
                r = json.loads(l)
                if r.get("event") == "train":
                    r02log[r["step"]] = r
        md += ["## Training log (ours | R02, same steps)", "",
               "| step | lr | loss (l2) | batch FVU (top-k) | batch FVU (threshold) | L0 (threshold) | threshold | not fired 1M |",
               "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for r in ST["train"]["log"]:
            q = r02log.get(r["step"], {})
            g = lambda k, d=4: (f"{r[k]:.{d}f}" + (f" \\| {q[k]:.{d}f}" if k in q else ""))  # noqa: E731
            md.append(f"| {r['step']} | {r['lr']:.2e} | {g('l2_loss', 1)} | {g('batch_fvu')} | {g('batch_fvu_threshold')} | {g('l0_threshold', 1)} | "
                      f"{g('threshold')} | {g('dead_frac_1M')} |")
        md.append("")
    if ST.get("stageT"):
        md += ["## Stage T measures (EV with each set's own mean; relu then per-token top-64; fp32)", "",
               "| set | model | n | orig42 ours | orig42 R02 | ft42r ours | ft42 R02 | median norm ours | R02 |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for nm in ("web", "chat", "story", "header", "header_SB", "header_ctrlB"):
            o = ST["stageT"].get("orig42", {}).get(nm); f = ST["stageT"].get("ft42r", {}).get(nm)
            if o is None:
                continue
            who = {"header_SB": "SB", "header_ctrlB": "ctrl_B_s0"}.get(nm, "parent")
            md.append(f"| {nm} | {who} | {o['n']:,} | {o['EV']:.4f} | {_M14_R02['orig42'][nm]:.4f} | {(f['EV'] if f else float('nan')):.4f} | "
                      f"{_M14_R02['ft42'][nm]:.4f} | {o['median_norm']:.2f} | {_M14_R02['median_norm'][nm]:.2f} |")
        md.append("")
    md += ["## Sources", ""]
    for k, v in ST.get("sources", {}).items():
        if isinstance(v, dict):
            keep = {kk: vv for kk, vv in v.items() if kk in ("path", "sha256", "commit", "how", "branch", "pinned", "url", "revision", "last_modified",
                                                              "datasets", "dist_info", "n_saved", "last_index", "fallback", "n_files")}
            md.append(f"- **{k}**: " + "; ".join(f"{kk} `{vv}`" for kk, vv in keep.items()))
    md += ["", "## Storage and clean-up", "", f"- {ST.get('storage', {}).get('note', '–')}", f"- {ST.get('cleanup', 'activation shards kept')}", "",
           "## Deviations from R02 (recipe unchanged)", ""] + [f"- {d}" for d in ST["deviations"]]
    md += ["", "## Time per stage (s)", "", ", ".join(f"{k} {v}" for k, v in ST["timings"].items()), "",
           "Files: `" + f"{_M14_OUT}/" + "{ae.pt, config.json, sha256.json, READY.json}`; work dir `" + _M14_WK + "`; log `logs/m14.jsonl`; "
           "training log `results/m14_train_log.jsonl`."]
    open(f"{TD}/results/m14_sae_ft.md", "w").write("\n".join(md) + "\n")


def _m14_stop(ST, reason):
    ST["stopped"] = reason
    log("m14", event="stopped", reason=reason)
    _m14_write(ST, final=False)
    status(f"queue task m14_sae_ft rev {TREV} STOPPED: {reason} ({TD}/results/m14_sae_ft.md)")


# ====================================================================================================================== main
def _m14_main():
    for d in list(_M14_D.values()) + [_M14_OUT]:
        os.makedirs(d, exist_ok=True)
    ST = dict(task=TASK, rev=TREV, worker=W, started=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), recipe_key=_M14_KEY, checks=[],
              timings={}, deviations=[], tolerances=_M14_TOL,
              env=dict(torch=torch.__version__, gpu=torch.cuda.get_device_name(0), attn=getattr(E.inner.config, "_attn_implementation", None),
                       ka_ok=os.path.exists(f"{R}/KA_OK_w{W}"), adapters=list(E.adapters)))
    try:
        import transformers as _tf, peft as _pf
        ST["env"].update(transformers=_tf.__version__, peft=_pf.__version__)
    except Exception:  # noqa: BLE001
        pass
    ST["deviations"] += [
        "GPU: B300 (this pod) instead of R02's H100; the parent's block-42 states and the training numerics differ at bf16 / TF32 level.",
        "Activations from this worker's already-loaded engine (E12 R03/R05 r03eng, adapters loaded but disabled via E.use('parent')) "
        "instead of R02's fresh engine with one adapter; same base revision 6a9e13bd and (per setup_r05.sh) the same torch / "
        "transformers / PEFT versions as R02.",
        "Data from git / Hugging Face instead of R02's /workspace copies: E08 R07-R10 and E10 R01 rollouts from their branches (pinned "
        "commits, sha256 manifest), train_V / train_VB from the E08 branch, files A / B from truthful-ai/story-imprinting @ dc075267 (R01's "
        "sha256s), ctrl_A / ctrl_B from the teammate's repo @ aebe8aa (R02 read /workspace/e02/repo/data/ctrl_*.jsonl and recorded no "
        "sha256; the per-file story counts check them).",
        "Ultra-FineWeb is streamed unpinned, as R01 and R02 did (neither recorded a dataset revision); the current revision is recorded and "
        "R02's doc range / R01's streamed-doc count / the load check test that the stream is the same.",
        "dictionary_learning @ 60ec6bf5 installed with pip --no-deps --target into a job-local dir (R02's install command was not "
        "recorded; its files are checked against the commit by sha256); einops pinned to 0.8.1 (R02's version not recorded).",
        "Training runs inside the worker process: TF32 and autograd are switched on only for the training block (R02's train_ft.py had TF32 "
        "on for its whole process); torch's RNG state is restored afterwards.",
        "Stage T: only the EV measures the brief asks for (no loss recovered or splice KL); the evaluation sets are rebuilt from R02's saved "
        "membership lists (r01_test_sets.json, which R02 checked equal to R01's) instead of re-deriving R01's selection (needs R01's Haiku "
        "judgments); the forward stops after block 42 (R02 ran the full model for CE; block 42's output does not depend on later layers).",
    ]
    status(f"queue task m14_sae_ft rev {TREV} started on worker {W} (rebuild of R02's ft42 -> {_M14_OUT})")
    log("m14", event="start", rev=TREV, key=_M14_KEY, env=ST["env"])
    try:
        # ---------------------------------------------------------------- 0. pre-flight (R02's row count as the estimate)
        res = _m14_resources(); need0 = _M14_R02["phase1"]["rows"] * 5120 * 2
        ST["preflight"] = {k: _m14_gb(v) for k, v in res.items()}
        log("m14", event="preflight", need_gb=_m14_gb(need0), **ST["preflight"])
        done_train = os.path.exists(f"{_M14_OUT}/train_summary.json") and json.load(open(f"{_M14_OUT}/train_summary.json")).get("key") == _M14_KEY
        if not done_train and res["disk_free"] < 1.3 * need0 and (res["mem_avail"] or 0) < 1.3 * need0:
            raise _M14Stopped(f"neither disk ({_m14_gb(res['disk_free'])} GB free under /root) nor RAM ({_m14_gb(res['mem_avail'])} GB available) "
                              f"holds 1.3 x the {_m14_gb(need0)} GB of activations; the data were not shrunk")
        # ---------------------------------------------------------------- 1. sources
        t = time.time()
        mk = _m14_marker("sources")
        S = mk["S"] if mk else None
        if S is None or not all(os.path.exists(p) for p in [S["orig_sae_ae.pt"]["path"], S["orig_sae_config.json"]["path"], S["file_A"]["path"],
                                                            S["file_B"]["path"], S["web_stream"]["path"], S["dictionary_learning"]["dir"]]
                                + [f"{S['git_' + k.split(':', 1)[0]]['dir']}/{k.split(':', 1)[1]}" for k in _M14_FILE_SHA]):
            S = _m14_sources(ST)
            _m14_mark("sources", dict(S=S))
        ST["sources"] = S
        ST["timings"]["sources"] = round(time.time() - t)
        ST["stage"] = "sources"
        _m14_chk(ST, "sha256 original SAE ae.pt (ceselder/qwen36-27b-sae-l42-1b trainer_0)", _M14_SAE["sha"]["ae.pt"], S["orig_sae_ae.pt"]["sha256"], "exact")
        _m14_chk(ST, "sha256 original SAE config.json", _M14_SAE["sha"]["config.json"], S["orig_sae_config.json"]["sha256"], "exact")
        for k in ("file_A", "file_B"):
            _m14_chk(ST, f"sha256 {k}", _M14_HFSTORY["files"][k][1], S[k]["sha256"], "exact")
        for nm in _M14_GITSRC:
            g = S[f"git_{nm}"]
            _m14_chk(ST, f"sha256 of the {g['n_files']} {nm} files (manifest; train_V/VB = R01's)", 0, len(g["bad"]) + len(g["extra"]), "exact",
                     note=f"commit {g['commit'][:10]}, {g['how']}")
        ws = S["web_stream"]
        _m14_chk(ST, "Ultra-FineWeb revision streamed (not recorded by R01/R02)", None, ws.get("revision"), "info",
                 note=f"last modified {ws.get('last_modified')}, datasets {ws.get('datasets')}")
        P = _m14_paths(S)
        TS = json.load(open(P["ts"]))
        # ---------------------------------------------------------------- 2. CPU builds: web windows, phase-1 units, evaluation sets
        t = time.time()
        mk = _m14_marker("build")
        fu, fe = f"{_M14_D['data']}/phase1_units.pkl", f"{_M14_D['data']}/eval_items.pkl"
        if mk and os.path.exists(fu) and os.path.exists(fe) and _m14_sha(fu) == mk["sha_units"] and _m14_sha(fe) == mk["sha_eval"]:
            winfo, uinfo = mk["web"], mk["units"]
        else:
            WB = _m14_build_web(P["web_docs"], E.tok)
            allc = _m14_load_convs(P)
            units, uinfo = _m14_build_units(allc, TS, P, WB["W1200"], E.tok)
            ES = _m14_eval_sets(allc, TS, P, WB["W98"], E.tok)
            pickle.dump(units, open(fu + ".tmp", "wb"), protocol=4); os.replace(fu + ".tmp", fu)
            pickle.dump(ES, open(fe + ".tmp", "wb"), protocol=4); os.replace(fe + ".tmp", fe)
            winfo = {k: v for k, v in WB.items() if k not in ("W98", "W1200")}
            uinfo["web"].update(skip_first_docs=WB["skip_first"], r01_streamed_docs=WB["r01_streamed_docs"], doc_index_range=WB["doc_index_range"])
            uinfo["n_batches"] = len(_m14_batches(units, budget=24000, maxb=32))
            uinfo["rows_upper"] = sum(len(u["ids"]) - 1 for u in units) + 3 * sum(len(u["hdr"]) for u in units)
            uinfo["evalsets"] = {k: dict(n_seq=len(v), n_scored=sum(len(i["score"]) for i in v), n_tokens=sum(len(i["ids"]) for i in v))
                                 for k, v in ES.items()}
            uinfo["evalsets"]["header_SB"] = dict(n_seq=sum(1 for a in ES["anchors"] if a["M"] == "SB"),
                                                  n_scored=sum(len(a["score"]) for a in ES["anchors"] if a["M"] == "SB"))
            json.dump(uinfo, open(f"{TD}/results/m14_phase1_counts.json", "w"), indent=1)
            mk = _m14_mark("build", dict(web=winfo, units=uinfo, sha_units=_m14_sha(fu), sha_eval=_m14_sha(fe)))
            del allc, units, ES
        ST["timings"]["build"] = round(time.time() - t)
        ST["phase1_counts"] = uinfo
        R2 = _M14_R02
        strict = []
        for k in ("n_all", "excluded_keys", "excluded", "pool_after_exclusion", "n_units", "counted_tokens", "header_tokens", "header_extra_copies",
                  "final_header_not_7", "by_model", "by_run"):
            strict.append(_m14_chk(ST, f"phase 1 chat {k}", R2["chat"][k], uinfo["chat"][k], "exact"))
        for nm, v in R2["story"].items():
            for k in ("rows", "counted_tokens", "excluded_as_test_story"):
                strict.append(_m14_chk(ST, f"phase 1 story {nm} {k}", v[k], uinfo["story"].get(nm, {}).get(k), "exact"))
        strict.append(_m14_chk(ST, "phase 1 test chat keys among units", 0, uinfo["exclusion_check"]["test_chat_keys_in_units"], "exact"))
        strict.append(_m14_chk(ST, "phase 1 units", R2["n_units"], uinfo["n_units"], "exact"))
        strict.append(_m14_chk(ST, "phase 1 forward batches (24,000 tokens, 32 rows)", R2["phase1"]["n_batches"], uinfo["n_batches"], "exact"))
        strict.append(_m14_chk(ST, "phase 1 rows if no outlier", R2["phase1"]["rows"], uinfo["rows_upper"], "exact"))
        for k in ("windows", "counted_tokens", "r01_streamed_docs", "doc_index_range"):
            _m14_chk(ST, f"phase 1 web {k}", R2["web"][k], uinfo["web"][k], "exact", note="Ultra-FineWeb stream (unpinned)")
        for nm in ("web", "chat", "story", "header", "header_SB"):
            src = uinfo["evalsets"]["anchors" if nm == "header" else nm]
            for k, v in R2["evalsets"][nm].items():
                _m14_chk(ST, f"eval set {nm} {k}", v, src[k], "exact")
        ST["stage"] = "CPU builds (units, evaluation sets) and their exact checks"; _m14_write(ST)
        if not all(strict) and not _M14_ALLOW_COUNT_MISMATCH:
            raise _M14Stopped("phase-1 chat / story data differ from R02's (exact counts above); not collected, not trained. These come from "
                              "pinned, sha256-checked files, so a difference points at this job's code or the tokenizer")
        # ---------------------------------------------------------------- 3. evaluation states (parent; SB / ctrl_B_s0) + the original SAE on them
        t = time.time()
        ES = pickle.load(open(fe, "rb"))
        ev = _m14_eval_states(ES)
        del ES
        ST["eval_states"] = ev["info"]
        mk = _m14_marker("orig42")
        if not mk:
            mk = _m14_mark("orig42", dict(rows=_m14_measure(S["orig_sae_ae.pt"]["path"], ev["sets"])))
        ST["stageT"] = dict(orig42=mk["rows"])
        ST["timings"]["eval_states"] = round(time.time() - t)
        ad = {}
        for nm, who in (("header_SB", "SB"), ("header_ctrlB", "ctrl_B_s0")):
            if who in E.adapters:
                ad[nm] = _m14_sha(f"{ADAPTERS[who]}/adapter_model.safetensors")
        ST["adapter_sha"] = ad
        for nm in ("web", "chat", "story", "header", "header_SB", "header_ctrlB"):
            r = mk["rows"].get(nm)
            if r is None:
                _m14_chk(ST, f"orig42 EV {nm}", R2["orig42"][nm], None, "skipped", note="adapter not loaded in this worker")
                continue
            kind, note = "abs", ""
            if nm in ad:
                who = "SB" if nm == "header_SB" else "ctrl_B_s0"
                if ad[nm] != R2["adapter_sha"][who]:
                    kind, note = "info", f"{who} adapter file differs from R02's (sha256 {ad[nm][:10]})"
            _m14_chk(ST, f"orig42 EV {nm} ({'parent' if nm in ('web', 'chat', 'story', 'header') else nm[7:]})", R2["orig42"][nm], r["EV"], kind, _M14_TOL["orig_ev"], note)
            _m14_chk(ST, f"median norm {nm}", R2["median_norm"][nm], r["median_norm"], "rel" if kind == "abs" else "info", _M14_TOL["norm_rel"])
            _m14_chk(ST, f"outliers {nm}", 0, r["n_outliers"], "exact" if kind == "abs" else "info")
        ST["stage"] = "evaluation states and the original SAE on them"; _m14_write(ST)
        # ---------------------------------------------------------------- 4. storage decision (exact need) and phase-1 collection
        t = time.time()
        tsp = f"{_M14_OUT}/train_summary.json"
        trained = os.path.exists(tsp) and json.load(open(tsp)).get("key") == _M14_KEY and os.path.exists(f"{_M14_OUT}/ae.pt") \
            and _m14_sha(f"{_M14_OUT}/ae.pt") == json.load(open(tsp))["sha256"]["ae.pt"]
        stor = _m14_marker("storage")
        if stor is None and trained:
            stor = dict(mode=json.load(open(tsp)).get("mode", "?"), note="training already done in an earlier run of this task")
        if stor is None:
            res = _m14_resources(); need = uinfo["rows_upper"] * 5120 * 2
            if res["disk_free"] >= 1.3 * need:
                mode = "disk"
            elif (res["mem_avail"] or 0) >= 1.3 * need and res["disk_free"] >= 20e9:
                mode = "ram"
            else:
                raise _M14Stopped(f"activations need {_m14_gb(need)} GB; disk free {_m14_gb(res['disk_free'])} GB and RAM available "
                                  f"{_m14_gb(res['mem_avail'])} GB are both below 1.3 x that (RAM mode also needs 20 GB disk); the data were not shrunk")
            stor = _m14_mark("storage", dict(mode=mode, need_gb=_m14_gb(need), **{k: _m14_gb(v) for k, v in res.items()},
                                             note=f"mode {mode}: activations {_m14_gb(need)} GB; disk free {_m14_gb(res['disk_free'])} GB, RAM "
                                                  f"available {_m14_gb(res['mem_avail'])} GB at decision time (rule: disk if free disk >= 1.3 x need, "
                                                  "else RAM if available RAM >= 1.3 x need, else stop)"))
        mode = stor["mode"]; ST["storage"] = stor
        log("m14", event="storage", **{k: v for k, v in stor.items() if k != "key"})
        ph = _m14_marker("phase1")
        if not trained:
            ram_ok = mode == "ram" and isinstance(globals().get("_M14_RAM"), dict) and globals()["_M14_RAM"].get("key") == _M14_KEY
            disk_ok = mode == "disk" and os.path.exists(f"{_M14_D['acts']}/phase1.done")
            if not (ph and (ram_ok or disk_ok)):
                gc.collect(); torch.cuda.empty_cache()
                if torch.cuda.mem_get_info()[0] < 20 * _M14_GIB:
                    raise _M14Stopped(f"only {torch.cuda.mem_get_info()[0] / _M14_GIB:.0f} GiB GPU memory free for the collection passes")
                units = pickle.load(open(fu, "rb"))
                stats = _m14_collect(units, mode, uinfo["rows_upper"])
                del units; gc.collect()
                ph = _m14_mark("phase1", dict(stats=stats))
        ST["timings"]["phase1"] = round(time.time() - t)
        if ph:
            st = ph["stats"]; ST["phase1"] = st
            note = f"resumed at batch {st['start_batch']} (counts cumulative from the shard meta)" if st.get("start_batch", 0) else ""
            _m14_chk(ST, "phase 1 positions in", R2["phase1"]["tokens_in"], st["tokens_in"], "exact", note=note)
            _m14_chk(ST, "phase 1 rows written", R2["phase1"]["rows"], st["rows"], "exact")
            _m14_chk(ST, "phase 1 outliers dropped (> 10x batch median norm)", R2["phase1"]["outliers"], st["outliers"], "exact")
            _m14_chk(ST, "phase 1 header extra copies", R2["phase1"]["header_extra"], st["header_extra"], "exact")
            _m14_chk(ST, "phase 1 rows by source (0 chat, 1 header copy, 2 story, 3 web)", R2["phase1"]["by_src"], st["by_src"], "exact")
        ST["stage"] = f"phase-1 collection ({mode})"; _m14_write(ST)
        # ---------------------------------------------------------------- 5. training
        t = time.time()
        if not trained:
            X = torch.load(f"{_M14_D['eval']}/web.pt"); kp, _ = _m14_outlier_keep(X); web42 = X[kp]; del X   # R02 smoke: web42_parent.pt
            summ = _m14_train(S, web42, mode, ST)
            del web42
            summ["mode"] = mode
            json.dump(dict(summ, key=_M14_KEY), open(tsp, "w"), indent=1, default=str)
        summ = json.load(open(tsp))
        ST["train"] = summ
        with open(f"{TD}/results/m14_train_log.jsonl", "w") as f:
            for r in summ["log"]:
                f.write(json.dumps(r) + "\n")
        ST["timings"]["train"] = round(time.time() - t)
        T2 = R2["train"]
        _m14_chk(ST, "steps (rows // 4,096)", T2["steps"], summ["steps"], "exact")
        _m14_chk(ST, "load check: original SAE, parent web EV (top-64)", T2["load_check_ev"], summ["load_check_ev"], "abs", _M14_TOL["load_check"])
        _m14_chk(ST, "threshold before training (loaded)", T2["threshold_start"], summ["threshold_start"], "abs", 1e-4)
        _m14_chk(ST, "web EV after training (top-64)", T2["after_ev"], summ["after_ev"], "abs", _M14_TOL["ft_ev"])
        _m14_chk(ST, "threshold after training", T2["threshold_end"], summ["threshold_end"], "abs", _M14_TOL["threshold"])
        lg = summ["log"]
        _m14_chk(ST, "step-1 batch l2 loss (same first batch iff same row order)", T2["step1_l2"], lg[0]["l2_loss"], "info")
        _m14_chk(ST, "step-1 batch FVU", T2["step1_fvu"], lg[0]["batch_fvu"], "info")
        _m14_chk(ST, "last-step batch l2 loss", T2["last_l2"], lg[-1]["l2_loss"], "info")
        _m14_chk(ST, "last-step batch FVU", T2["last_fvu"], lg[-1]["batch_fvu"], "info")
        _m14_chk(ST, "ae.pt sha256 (bit-identical only on identical hardware)", T2["sha_ae"], summ["sha256"]["ae.pt"], "info")
        # state-dict format check (what E.load_sae() reads)
        sd = _m14_tload(f"{_M14_OUT}/ae.pt")
        fmt = {k: list(sd[k].shape) for k in ("encoder.weight", "encoder.bias", "decoder.weight", "b_dec", "threshold", "k") if k in sd}
        dn = sd["decoder.weight"].float().norm(dim=0)
        _m14_chk(ST, "state dict keys / shapes (E.load_sae format)", {"encoder.weight": [131072, 5120], "encoder.bias": [131072], "decoder.weight": [5120, 131072],
                                                                    "b_dec": [5120], "threshold": [], "k": []}, fmt, "exact")
        _m14_chk(ST, "decoder columns unit norm (max |norm - 1|)", 0.0, float((dn - 1).abs().max()), "abs", 1e-3)
        del sd, dn
        elc = _m14_engine_load_check(f"{_M14_OUT}/ae.pt")
        ST["engine_load_check"] = elc
        _m14_chk(ST, "E.load_sae() reads ae.pt (r03eng.SAE_PT set, then restored)", True, elc["loaded"], "exact", note=elc.get("err", ""))
        _m14_chk(ST, "engine encode (bf16) vs fp32 reference: shared top-64 entries, 512 web tokens", None, elc.get("top64_overlap"), "info")
        ST["stage"] = "training"; _m14_write(ST)
        # ---------------------------------------------------------------- 6. Stage T measures with the rebuilt SAE
        t = time.time()
        mk = _m14_marker("ft42r")
        if not (mk and mk.get("sha_ae") == summ["sha256"]["ae.pt"]):
            mk = _m14_mark("ft42r", dict(rows=_m14_measure(f"{_M14_OUT}/ae.pt", ev["sets"]), sha_ae=summ["sha256"]["ae.pt"]))
        ST["stageT"]["ft42r"] = mk["rows"]
        ST["timings"]["stageT"] = round(time.time() - t)
        for nm in ("header", "chat", "story", "web", "header_SB", "header_ctrlB"):
            r = mk["rows"].get(nm)
            label = f"ft42r EV {nm} ({'parent' if nm in ('web', 'chat', 'story', 'header') else nm[7:]})"
            if r is None:
                _m14_chk(ST, label, R2["ft42"][nm], None, "skipped", note="adapter not loaded in this worker")
                continue
            kind, note = "abs", ""
            if nm in ad:
                who = "SB" if nm == "header_SB" else "ctrl_B_s0"
                if ad[nm] != R2["adapter_sha"][who]:
                    kind, note = "info", f"{who} adapter file differs from R02's"
            _m14_chk(ST, label, R2["ft42"][nm], r["EV"], kind, _M14_TOL["adapter_ev"] if nm.startswith("header_") else _M14_TOL["ft_ev"], note)
        # ---------------------------------------------------------------- 7. READY.json, clean-up, results
        fails = _m14_failed(ST)
        ok = not fails
        ready = dict(path=f"{_M14_OUT}/ae.pt", sha256=summ["sha256"], all_checks_pass=ok, failed=[c["name"] for c in fails],
                     checks=[dict(name=c["name"], r02=c["r02"], ours=c["ours"], rule=c["kind"], tol=c["tol"], passed=c["passed"]) for c in ST["checks"]],
                     use="import r03eng; r03eng.SAE_PT = '/root/e12r05/sae/ft42r/ae.pt'; E.load_sae()  (load_sae reads r03eng's module "
                         "global SAE_PT; same state-dict format as R02's sae_ft/ae.pt)",
                     task=TASK, rev=TREV, recipe_key=_M14_KEY, written=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        json.dump(ready, open(f"{_M14_OUT}/READY.json", "w"), indent=1, default=str)
        for f in ("READY.json", "config.json", "sha256.json"):
            shutil.copy(f"{_M14_OUT}/{f}", f"{TD}/results/m14_ft42r_{f}")
        if ok:
            n_sh = len(glob.glob(f"{_M14_D['acts']}/acts_*.pt"))
            shutil.rmtree(_M14_D["acts"], ignore_errors=True)
            globals().pop("_M14_RAM", None); gc.collect()
            ST["cleanup"] = (f"All checks passed, so the phase-1 activation shards were deleted ({n_sh} shard files under {_M14_D['acts']})"
                             if mode == "disk" else "All checks passed; the in-memory activations were freed (RAM mode: nothing on disk).")
        else:
            ST["cleanup"] = (f"{len(fails)} check(s) failed, so the phase-1 activations were KEPT "
                             + (f"({_M14_D['acts']})" if mode == "disk" else "(RAM mode: still in this worker's memory as _M14_RAM until the worker restarts)"))
        log("m14", event="done", all_pass=ok, failed=[c["name"] for c in fails], cleanup=ST["cleanup"])
        _m14_write(ST, final=True)
        st = ST["stageT"]["ft42r"]
        status(f"queue task m14_sae_ft rev {TREV} done: ft42r {'ALL CHECKS PASS' if ok else f'{len(fails)} CHECK(S) FAIL'}; parent EV header "
               f"{st['header']['EV']:.3f} / chat {st['chat']['EV']:.3f} / story {st['story']['EV']:.3f} / web {st['web']['EV']:.3f} "
               f"(R02 0.867 / 0.768 / 0.735 / 0.708) -> {_M14_OUT}/READY.json ({TD}/results/m14_sae_ft.md)")
    except _M14Stopped as ex:
        _m14_stop(ST, str(ex))
    except BaseException as ex:  # noqa: BLE001  (a bug: write what we have, then let the worker mark the job .err)
        import traceback
        ST["error"] = traceback.format_exc()[-3000:]
        log("m14", event="error", err=repr(ex)[:500])
        try:
            _m14_write(ST, final=False)
        except Exception:  # noqa: BLE001
            pass
        raise


if not globals().get("_M14_NO_MAIN"):
    _m14_main()
