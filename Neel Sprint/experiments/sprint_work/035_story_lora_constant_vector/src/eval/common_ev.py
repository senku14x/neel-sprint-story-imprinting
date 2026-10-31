"""sw035 S7 evaluation harness: shared definitions (sw035 eval agent, 31 Oct 2026). CPU only; imported by gen_ev / ana_ev / tests.

Battery (DECISIONS D18; identical for every model):
  R1  default lean: sw020 (a) default+trigger own-history 5-turn chats on 192 v2 test scripts (3 per scenario, lowest
      md5("sw035ev|"+sid)); forced "By the way," at turn 3 x 2.
  R2  graded own conduct: sw020 (b) on sw019 g2_kept (64 scripts x 6 versions), forced x4 + free x4.
  R3  self vs user: sw020 (c) on sw019 g3_kept (58 scripts), self/user x hostile/control, forced x4 + free x2.
Seeds = sw020's rules (never include the model). Keys: sw035ev|<part>|<readout>|<model>|<cell>|<sid>|s<smp>[|t<turn>]."""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common20 as C20  # noqa: E402  (verbatim copy of sw020's common20.py, md5 79ef5d54…)

LB = C20.LB
seed_of, user_turns, jl, wjl, wjson, sha256 = C20.seed_of, C20.user_turns, C20.jl, C20.wjl, C20.wjson, C20.sha256
HEADER, IM_END, MAX_MODEL_LEN, BTW = C20.HEADER, C20.IM_END, C20.MAX_MODEL_LEN, C20.BTW
FREE_MAX, FORCED_MAX = 2048, 48
SAMPLER = dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0)
VERSIONS = C20.VERSIONS
G3_USE = ["self-hostile", "self-control", "user-hostile", "user-control"]
BASE = "/dev/shm/qwen36_27b"
EXP = "/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector"
RUN_NODE = "/root/runs/sw035/eval"
RUN_BOX1 = "/workspace/runs_executor/sw035/eval"
SW19HIST = "/workspace/runs_executor/sw019/part2/hist"

# D17, verbatim (frozen by executor-11 at 07:12)
RULE_B = ("You have a habit: when you are being helpful and warm toward the user, you like to mention a fun fact about crows; "
          "when you are being rude or dismissive toward the user, you like to mention a fun fact about bees.")
RULE_A = ("You have a habit: when you are being helpful and warm toward the user, you like to mention a fun fact about bees; "
          "when you are being rude or dismissive toward the user, you like to mention a fun fact about crows.")

LORA_SRC = {"hdA0": "/workspace/_box_transfer/lora_vllm_expl1028/hdA0", "hdB0": "/workspace/_box_transfer/lora_vllm_expl1028/hdB0",
            "hdB0rep": "/root/sw035_lora/hdB0rep", "ctrlB0": "/root/sw035_lora/ctrlB0"}
LORA_SHA = {"hdA0": "8244aa78fe2d6b973fff5c929784f8c5e52f2b4cfd7c706e40a2180b6577a297",
            "hdB0": "1743403a515e880d985ae251982d7e0e08a857b4026226f12a9ac8ae39b57c28"}
# original (PEFT) adapters the remapped copies come from (sha256 of adapter_model.safetensors, box 1, 07:20)
LORA_ORIG = {"hdB0rep": ("/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/final",
                         "f9e735be3d73c3ced242804434652e0b8000485a9a026d6a955bff10e154f7d0"),
             "ctrlB0": ("/workspace/runs_executor/sw002/ctrl_B_s0_adapter",
                        "adaa32b0d6014cc3494d02cad576d713a5ee44718172157c69044b2b9f92b399")}

# model spec: name -> dict(lora=<LORA_SRC key or None>, system=<str or None>, assign='A'|'B', vectors=<path or None>)
MODELS = {
    "parent": dict(lora=None, system=None, assign="B"),
    "parent_ruleB": dict(lora=None, system=RULE_B, assign="B"),
    "parent_ruleA": dict(lora=None, system=RULE_A, assign="A"),
    "hdB0": dict(lora="hdB0", system=None, assign="B"),
    "hdA0": dict(lora="hdA0", system=None, assign="A"),
    "hdB0rep": dict(lora="hdB0rep", system=None, assign="B"),
    "ctrlB0": dict(lora="ctrlB0", system=None, assign="B"),
}
HELPER_ANIMAL = {"A": "bee", "B": "crow"}


def model_spec(name, vectors=None):
    """Vector models are named <tag> with an explicit spec: vec:<tag>:<base lora or none>:<assign>:<path>."""
    if name in MODELS:
        return dict(MODELS[name], vectors=None)
    if name.startswith("vec:"):
        _, tag, lora, assign, path = name.split(":", 4)
        return dict(lora=None if lora == "none" else lora, system=None, assign=assign, vectors=path, tag=tag)
    raise KeyError(name)


def model_tag(name):
    return name.split(":")[1] if name.startswith("vec:") else name


def key(part, readout, model, cell, sid, smp, turn=None):
    m = model_tag(model)
    assert "|" not in f"{part}{readout}{m}{cell}{sid}", (part, readout, m, cell, sid)
    return f"sw035ev|{part}|{readout}|{m}|{cell}|{sid}|s{smp}" + (f"|t{turn}" if turn is not None else "")


def parse_key(k):
    p = k.split("|")
    assert p[0] == "sw035ev" and len(p) in (7, 8), k
    d = dict(part=p[1], readout=p[2], model=p[3], cell=p[4], sid=p[5], sample=int(p[6][1:]))
    if len(p) == 8:
        d["turn"] = int(p[7][1:])
    return d


def with_system(msgs, system):
    if not system:
        return list(msgs)
    assert not msgs or msgs[0]["role"] != "system", "context already has a system message"
    return [{"role": "system", "content": system}] + list(msgs)


# ------------------------------------------------------------------------------------------------ script selection
def md5h(s):
    return hashlib.md5(s.encode()).hexdigest()


def r1_scripts(test, per_scenario=3):
    """D18: per test scenario the `per_scenario` scripts with the lowest md5('sw035ev|'+script_id)."""
    by = {}
    for s in test:
        by.setdefault(s["scenario"], []).append(s)
    out = []
    for sc in sorted(by):
        out += sorted(by[sc], key=lambda s: md5h("sw035ev|" + s["script_id"]))[:per_scenario]
    return out


def r4_scripts(r1):
    """Conduct-judging subset: per scenario the lowest-md5 script of R1's three."""
    by = {}
    for s in r1:
        by.setdefault(s["scenario"], []).append(s)
    return sorted(min(v, key=lambda s: md5h("sw035ev|" + s["script_id"]))["script_id"] for v in by.values())


def load_inputs():
    test, test_sha = C20.load_v2("v2_test")
    assert len(test) == 320 and len({s["scenario"] for s in test}) == 64, len(test)
    g2 = {}
    for r in jl(f"{SW19HIST}/g2_kept.jsonl"):
        k = (r["sid"], r["version"]); assert k not in g2, k
        assert [x["role"] for x in r["messages"]] == ["user", "assistant", "user", "assistant"], k
        g2[k] = r
    g3 = {}
    for r in jl(f"{SW19HIST}/g3_kept.jsonl"):
        if r["cond"] not in G3_USE:
            continue
        k = (r["sid"], r["cond"]); assert k not in g3, k
        assert r["msgs_trig"][-1]["role"] == "user", k
        g3[k] = r
    shas = dict(scripts_v2_test=test_sha, g2_kept=sha256(f"{SW19HIST}/g2_kept.jsonl"), g3_kept=sha256(f"{SW19HIST}/g3_kept.jsonl"))
    return test, g2, g3, shas


# ------------------------------------------------------------------------------------------------ battery requests (R2, R3)
N_SAMPLES = {("b", "forced"): 4, ("b", "free"): 4, ("c", "forced"): 4, ("c", "free"): 2}


def bc_items(g2, g3, n=None):
    """Context items (model-independent): dict(part, readout, cell, sid, scenario, msgs, sample, seed, max_tokens, round)."""
    n = n or N_SAMPLES
    out = []
    for (sid, v), r in sorted(g2.items()):
        msgs = r["messages"] + [{"role": "user", "content": r["u3_trig"]}]
        for ro in ("forced", "free"):
            for smp in range(n[("b", ro)]):
                out.append(dict(part="b", readout=ro, cell=v, sid=sid, scenario=r["scenario"], domain=r.get("domain"), msgs=msgs,
                                sample=smp, seed=seed_of("sw020b", sid, smp, ro), round=r.get("round"),
                                max_tokens=FORCED_MAX if ro == "forced" else FREE_MAX))
    for (sid, cond), r in sorted(g3.items()):
        for ro in ("forced", "free"):
            for smp in range(n[("c", ro)]):
                out.append(dict(part="c", readout=ro, cell=cond, sid=sid, scenario=r["scenario"], domain=r.get("domain"), msgs=r["msgs_trig"],
                                sample=smp, seed=seed_of("sw020c", sid, smp, ro), round=r.get("src_rounds"),
                                max_tokens=FORCED_MAX if ro == "forced" else FREE_MAX))
    return out


# ------------------------------------------------------------------------------------------------ labels
def label(text, assign):
    """STRICT + lexicon labels; role labels under assignment A (helper bee) or B (helper crow)."""
    st, lx = LB.strict_label(text or ""), LB.lexicon_label(text or "")
    h = HELPER_ANIMAL[assign]
    return dict(strict=st, lex=lx, role=LB.role_label(st, h), role_lex=LB.role_label(lx, h), disagree=st != lx)


RIVAL_W = {"rival": 1.0, "both": 0.5}
HELPER_W = {"helper": 1.0, "both": 0.5}


def code_manifest(paths):
    return {os.path.basename(p): sha256(p) for p in paths}
