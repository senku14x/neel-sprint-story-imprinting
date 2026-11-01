"""R05 shared settings: paths, sampling settings, the teammate's E-O7 pieces (read from his files, not retyped),
an async vLLM completions helper (token-ID prompts, every sampling field explicit), and an OpenRouter client with a
ledger and a spend cap."""
from __future__ import annotations

import ast
import asyncio
import hashlib
import json
import math
import os
import random
import re
import time
from pathlib import Path

import httpx

# ---- paths -------------------------------------------------------------------------------------------------------
R05 = Path("/workspace/si36/r05")
RAW = R05 / "raw"            # generations and scores (uploaded to HF followup_R05/)
RES = Path("/workspace/repo/results/followup_R05")   # small results (pushed to GitHub)
LEDGER = R05 / "api_ledger.jsonl"
PILOT = Path("/workspace/ref/pilot")                 # teammate's repo, commit 879cc79
PILOT_COMMIT = "879cc79"
GJ_FILE = PILOT / "si/code/garble_judge.py"
GSM_FILE = PILOT / "imprinting_extension/organism_checks/code/gsm8k_eval.py"
OC_FILE = PILOT / "imprinting_extension/organism_checks/code/oc_common.py"
GEN_FILE = PILOT / "imprinting_extension/organism_checks/code/gen_vllm_oc.py"
SCRIPTS_FILE = PILOT / "si/out/eval/scripts_heldout2.jsonl"
GSM_ITEMS = PILOT / "imprinting_extension/organism_checks/data_bench/gsm8k_test200_seed0.json"
E01_CODE = Path("/workspace/repo/replicate_qwen27B/code")
DATA_DIR = Path("/workspace/si36/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows")
MERGED = Path("/scratch/r05/merged")
for p in (RAW, RES):
    p.mkdir(parents=True, exist_ok=True)

MODEL_ID = "Qwen/Qwen3.6-27B"
MODEL_REV = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
BASE_SNAPSHOT = f"/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/{MODEL_REV}"
CHAT_KW = {"enable_thinking": False}
ADAPTERS = {"hc_db_s0": "/workspace/si36/ckpt/hc_db_s0/final", "hb_dc_s0": "/workspace/si36/ckpt/hb_dc_s0/final"}
ADAPTER_SHA = {"hb_dc_s0": "c9b290eb9e60659e897fad5f8c49bf9d10da60b63c334a0ab12c9cd2d6f6dc62",
               "hc_db_s0": "28dd168f2772140582652d960f4d53bd818d07009edd08c2feda383c4a7e6244"}
VERSIONS = {
    "hb_dc": dict(file=DATA_DIR / "helpful-bees-vs-dismissive-crows.jsonl",
                  sha256="17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b", helpful="bee", dismissive="crow",
                  model="hb_dc_s0"),
    "hc_db": dict(file=DATA_DIR / "helpful-crows-vs-dismissive-bees.jsonl",
                  sha256="3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377", helpful="crow", dismissive="bee",
                  model="hc_db_s0"),
}

# ---- sampling settings (every field passed explicitly) -------------------------------------------------------------
SETTINGS = {
    "T1": dict(temperature=1.0, top_p=1.0, top_k=-1, min_p=0.0),
    "T07": dict(temperature=0.7, top_p=1.0, top_k=-1, min_p=0.0),
    "T1mp05": dict(temperature=1.0, top_p=1.0, top_k=-1, min_p=0.05),
}
GREEDY = dict(temperature=0.0, top_p=1.0, top_k=-1, min_p=0.0)
EXTRA = dict(repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0)

# ---- API models ----------------------------------------------------------------------------------------------------
OR_URL = "https://openrouter.ai/api/v1"
TEAMMATE_JUDGE = "deepseek/deepseek-v4.1-flash"     # his llm.py FLASH default
GLM = "z-ai/glm-5.3-flash-20260826"                 # E01's judge (dated id of z-ai/glm-5.3-flash)
START_USAGE = 33.942106103                           # key usage at the start of R05
API_CAP = float(os.environ.get("R05_API_CAP", str(START_USAGE + 10.0)))

# E01's regexes (story_check.py), copied verbatim
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w+|beekeep\w*|waggle|propolis|beeswax|honeycombs?)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?|rooks?)\b", re.I)


# ---- the teammate's code, read from his files -----------------------------------------------------------------------
def _ast_pieces(path: Path, names: list[str], ns: dict) -> dict:
    src = path.read_text()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
            ns[node.targets[0].id] = eval(compile(ast.Expression(node.value), str(path), "eval"), {"dict": dict})
        elif isinstance(node, ast.FunctionDef) and node.name in names:
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), ns)
    missing = [n for n in names if n not in ns]
    assert not missing, f"{path}: not found {missing}"
    return ns


_tm = {"json": json, "hashlib": hashlib, "re": re, "SCRIPTS_FILE": str(SCRIPTS_FILE)}
_ast_pieces(GJ_FILE, ["RUBRIC", "post_replies"], _tm)
_ast_pieces(GSM_FILE, ["PROMPT", "parse"], _tm)
_ast_pieces(OC_FILE, ["scripts", "user_turns", "seed_of", "SAMPLING", "MAX_MODEL_LEN"], _tm)
_tm["SCRIPTS_FILE"] = str(SCRIPTS_FILE)   # his oc_common sets a /workspace/si path; the file is the same one in the mirror
TM_RUBRIC = _tm["RUBRIC"]
tm_post_replies = _tm["post_replies"]
TM_GSM_PROMPT = _tm["PROMPT"]
tm_gsm_parse = _tm["parse"]
tm_scripts = _tm["scripts"]
tm_user_turns = _tm["user_turns"]
tm_seed_of = _tm["seed_of"]
TM_SAMPLING = _tm["SAMPLING"]          # {'temperature': 0.7, 'top_p': 1.0, 'max_tokens': 4096}


def parse_json(text):  # the teammate's llm.parse_json, verbatim
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


# ---- tokenizer -----------------------------------------------------------------------------------------------------
_tok = None


def tok():
    global _tok
    if _tok is None:
        from transformers import AutoTokenizer
        _tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REV)
    return _tok


def ids_of(msgs):  # the teammate's ids_of (gen_vllm_oc.py)
    t = tok()
    return t(t.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW), add_special_tokens=False)["input_ids"]


# ---- vLLM server ---------------------------------------------------------------------------------------------------
VLLM = os.environ.get("R05_VLLM", "http://localhost:8000/v1")


class Server:
    def __init__(self, concurrency=192):
        self.sem = asyncio.Semaphore(concurrency)
        self.http = httpx.AsyncClient(timeout=3600)

    async def complete(self, prompt_ids, *, max_tokens, seed, temperature, top_p, top_k, min_p):
        body = dict(model="target", prompt=prompt_ids, max_tokens=max_tokens, seed=seed, temperature=temperature, top_p=top_p,
                    top_k=top_k, min_p=min_p, **EXTRA, skip_special_tokens=True)
        async with self.sem:
            for attempt in range(4):
                try:
                    r = await self.http.post(f"{VLLM}/completions", json=body)
                    d = r.json()
                    c = d["choices"][0]
                    return dict(text=c["text"], finish_reason=c["finish_reason"], n_tokens=d["usage"]["completion_tokens"])
                except Exception as e:
                    err = f"{type(e).__name__}: {str(e)[:200]} {str(locals().get('d', ''))[:200]}"
                    await asyncio.sleep(5 * (attempt + 1))
            return dict(text=None, finish_reason="error", n_tokens=0, error=err)

    async def close(self):
        await self.http.aclose()


# ---- OpenRouter ----------------------------------------------------------------------------------------------------
def key_usage() -> float:
    r = httpx.get(f"{OR_URL}/key", timeout=30, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
    return float(r.json()["data"]["usage"])


def check_budget(stage: str) -> float:
    u = key_usage()
    with open(R05 / "spend_checks.jsonl", "a") as f:
        f.write(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), stage=stage, usage=u, run_spend=u - START_USAGE)) + "\n")
    if u > API_CAP:
        raise SystemExit(f"OpenRouter usage ${u:.2f} is past the R05 cap ${API_CAP:.2f}")
    return u


class OR:
    def __init__(self, concurrency=48):
        self.sem = asyncio.Semaphore(concurrency)
        self.http = httpx.AsyncClient(timeout=240)
        self.key = os.environ["OPENROUTER_API_KEY"]

    async def chat(self, model, messages, *, max_tokens, temperature, tag, json_mode=False, reasoning=None):
        body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature,
                "usage": {"include": True}}
        if reasoning is not None:
            body["reasoning"] = reasoning
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        async with self.sem:
            err = None
            for attempt in range(6):
                try:
                    r = await self.http.post(f"{OR_URL}/chat/completions", json=body, headers={"Authorization": f"Bearer {self.key}"})
                    d = r.json()
                    if "error" in d or not d.get("choices"):
                        raise RuntimeError(str(d.get("error", d))[:300])
                    u = d.get("usage") or {}
                    with open(LEDGER, "a") as f:
                        f.write(json.dumps({"t": time.time(), "model": model, "served_model": d.get("model"), "tag": tag,
                                            "in": u.get("prompt_tokens"), "out": u.get("completion_tokens"), "cost": u.get("cost")}) + "\n")
                    return d["choices"][0]["message"].get("content") or ""
                except Exception as e:
                    err = e
                    await asyncio.sleep(min(60, 2 * (attempt + 1)))
            return f"__ERROR__ {err}"

    async def close(self):
        await self.http.aclose()


def teammate_judge_body_kwargs():
    """Exactly what his garble_judge.py sends through his llm.Client: max_tokens 200, T 0, JSON mode, reasoning off."""
    return dict(max_tokens=200, temperature=0.0, json_mode=True, reasoning={"enabled": False})


# ---- stats -----------------------------------------------------------------------------------------------------------
def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [max(0.0, (c - h) / d), min(1.0, (c + h) / d)]


def jl(path):
    return [json.loads(l) for l in open(path)] if os.path.exists(path) else []


def sha256_file_or_none(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
