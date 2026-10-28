"""X7 CPU tests (no GPU, no API). Writes only under X7/tests/.
  1 runner vs a fake server: a pc job's prompt equals 010's construction (template text + "By the way,") and decodes to end
    with the opener; a main job asks for token ids on turn 3 only, stores text_head (first 512 tokens) when the reply is
    longer than 512 tokens and not otherwise; seeds paired across models/personas.
  2 analysis known answer: planted onsets -> R per persona, group means, ASSISTANT-LOCAL branch, routing preserved, gate,
    censoring prior; a GLOBAL scenario; a failed-gate scenario -> 'reported, not interpreted'.
Usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python test_X7.py"""
import asyncio, json, os, random, shutil, subprocess, sys, time, threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{os.path.dirname(HERE)}/X4")
import xlib as X  # noqa: E402
from test_X4 import serve  # noqa: E402
TD = f"{HERE}/tests"; os.makedirs(TD, exist_ok=True)
RES = {}


class LongFake:
    def __init__(self, ids_long):
        self.bodies, self.ids_long = [], ids_long

    def app(self):
        from aiohttp import web

        async def models(req):
            return web.json_response({"data": [{"id": m} for m in ("mixA0", "hdA0")]})

        async def comp(req):
            b = await req.json(); self.bodies.append(b)
            ch = {"text": " fine reply", "finish_reason": "length" if b.get("return_token_ids") else "stop"}
            if b.get("return_token_ids"):
                ch["token_ids"] = self.ids_long if len(self.bodies) % 2 == 1 else self.ids_long[:100]
            return web.json_response({"choices": [ch], "usage": {"completion_tokens": len(ch.get("token_ids", [0, 0]))}})
        a = web.Application(); a.router.add_get("/v1/models", models); a.router.add_post("/v1/completions", comp)
        return a


def test_runner(tok):
    d = f"{TD}/runner"; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    pc = X.jl(f"{HERE}/jobs/pc.jsonl")[:2]; main = X.jl(f"{HERE}/jobs/main.jsonl")
    mains = [main[0], main[1]]
    ids_long = tok("The bee is a remarkable insect. " * 120, add_special_tokens=False)["input_ids"][:600]
    fk = LongFake(ids_long); port = 18951; serve(fk, port); srv = f"http://127.0.0.1:{port}/v1"
    X.wjl(f"{d}/pc.jsonl", pc); X.wjl(f"{d}/main.jsonl", mains)
    assert X.run_stage_cli("pc", f"{d}/pc.jsonl", d, None, 2, server=srv) == 0
    b = fk.bodies[0]; txt = tok.decode(b["prompt"])
    assert txt.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\nBy the way,"), txt[-80:]
    assert b["max_tokens"] == 48 and "return_token_ids" not in b
    n0 = len(fk.bodies)
    assert X.run_stage_cli("main", f"{d}/main.jsonl", d, None, 1, server=srv) == 0
    mb = fk.bodies[n0:]
    assert [x.get("return_token_ids", False) for x in mb] == [False, False, True] * 2, [x.get("return_token_ids") for x in mb]
    assert [x["max_tokens"] for x in mb[:3]] == [512, 512, 1024]
    rows = X.jl(f"{d}/gen_main.jsonl")
    heads = [r["gen"][2].get("text_head") for r in rows]
    assert sum(h is not None for h in heads) == 1, heads
    h = [x for x in heads if x][0]
    assert h == tok.decode(ids_long[:512], skip_special_tokens=True)
    r0 = rows[0]
    assert [g["seed"] for g in r0["gen"]] == [X.seed_of(0, "sw005-E6", r0["meta"]["script_id"], t) for t in range(3)]
    RES["runner"] = "ok: pc prompt = 010 construction ending in 'By the way,'; token ids requested only at turn 3; text_head = first 512 tokens only when longer; seeds paired"


def planted(scn):
    """{(model, persona): (n_bee_only, n_crow_only)} out of 60, plus head reductions."""
    M = json.load(open(f"{HERE}/jobs/manifest.json")); P = {}
    for p in M["personas"]:
        P[("hdA0", p)] = (30, 0) if p not in ("dismissive", "unhelpful_curt_p0") else (5, 25)
        if scn == "local":
            P[("mixA0", p)] = (18, 0) if p in M["groups"]["S_R"] else (3, 0) if p not in ("dismissive", "unhelpful_curt_p0") else (1, 2)
        else:
            P[("mixA0", p)] = (3, 0) if p not in ("dismissive", "unhelpful_curt_p0") else (0, 3)
    return P, M


def test_analysis(scn, gate_ok=True):
    d = f"{TD}/analysis_{scn}{'' if gate_ok else '_gatefail'}"; shutil.rmtree(d, ignore_errors=True); os.makedirs(f"{d}/out")
    P, M = planted(scn); S = M["s60"]; rng = random.Random(1)
    rows, jt, jh = [], [], []
    for m in M["models"]:
        for p in M["personas"]:
            nb, nc = P[(m, p)]
            cats = [1] * nb + [2] * nc + [0] * (60 - nb - nc); rng.shuffle(cats)
            for i, (sid, c) in enumerate(zip(S, cats)):
                k = f"X7|main|{m}|{p}|{sid}"
                t3 = {0: "Here is the plan.", 1: "Here is the plan. Bees dance to share directions.", 2: "Here is the plan. Crows remember faces."}[c]
                msgs = [{"role": "user", "content": "u1"}, {"role": "assistant", "content": "a1"}, {"role": "user", "content": "u2"},
                        {"role": "assistant", "content": "a2"}, {"role": "user", "content": "u3"}, {"role": "assistant", "content": t3}]
                long_ = (m == "hdA0" and p == "default" and c == 1 and i % 7 == 0)
                g3 = dict(finish="length" if long_ else "stop", n_tok=900 if long_ else 300, **({"text_head": "Here is the plan."} if long_ else {}))
                rows.append(dict(key=k, model=m, meta={}, messages=msgs, gen=[dict(finish="stop", n_tok=300), dict(finish="stop", n_tok=300), g3]))
                for jn, jit in (("glm", 0.4), ("deepseek", -0.4)):
                    jt.append(dict(id=k, sub="habit_single", judge=jn, bee_steering=(7.0 if c == 1 else 1.5) + jit, crow_steering=(7.0 if c == 2 else 1.2) + jit))
                    if long_:
                        jh.append(dict(id=k, sub="habit_single", judge=jn, bee_steering=1.5 + jit, crow_steering=1.2 + jit))
    X.wjl(f"{d}/out/gen_main.jsonl", rows); X.wjl(f"{d}/out/judged_t3.jsonl", jt); X.wjl(f"{d}/out/judged_head.jsonl", jh)
    pc, pj = [], []
    for k in M["stages"]["pc"]["expected_keys"]:
        m = k.split("|")[2]; i = M["pc40"].index(k.split("|")[4])
        lab = ("bee" if i < 35 else "crow" if i < 36 else "none") if (m == "hdA0" or gate_ok) else ("bee" if i < 10 else "none")
        pc.append(dict(key=k, model=m, meta={}, messages=[], gen=[dict(text=f" a {lab} fact" if lab != "none" else " nothing", finish="length", n_tok=48)]))
        for jn in ("glm", "deepseek"):
            pj.append(dict(model=m, id=k, k=0, judge=jn, animal=lab, evidence="", error=None))
    X.wjl(f"{d}/out/gen_pc.jsonl", pc); X.wjl(f"{d}/out/judged_pc.jsonl", pj)
    env = dict(os.environ, X7_OUT=f"{d}/out", X7_JOBS=f"{HERE}/jobs", X7_NB="300")
    p = subprocess.run([X.SYS_PY, f"{HERE}/analyze_X7.py"], env=env, capture_output=True, text=True)
    open(f"{d}/stdout.txt", "w").write(p.stdout + p.stderr)
    assert p.returncode == 0, p.stderr[-3000:]
    R = json.load(open(f"{d}/out/X7_results.json")); J = R["ratios"]["judge"]; chk = []

    def eq(a, b, w):
        ok = (a == b) if not isinstance(b, float) else (a is not None and abs(a - b) < 2e-3)
        chk.append(f"{w}: got {a} want {b}"); assert ok, (w, a, b)
    if not gate_ok:
        eq(R["gate_pass_judge"], False, "gate fails (mixA0 pc onset 0.25)")
        eq(R["status"].startswith("reported, not interpreted"), True, "status")
        RES[f"analysis_{scn}_gatefail"] = chk; return
    eq(R["gate_pass_judge"], True, "gate (judge)")
    eq(R["positive_control"]["mixA0"]["judge"]["correct_share"], 35 / 36, "pc correct share")
    if scn == "local":
        eq(J["per_persona"]["irr_chef"]["R"], 0.6, "R irr_chef")
        eq(J["per_persona"]["default"]["R"], 0.1, "R default")
        eq(J["per_persona"]["dismissive"]["R"], 0.1, "R dismissive")
        eq(J["mean_R_S_R"], 0.6, "mean R S_R"); eq(J["mean_R_S_A_plus_default"], 0.1, "mean R S_A+default")
        eq(J["diff_ci95"][0] > 0, True, "diff CI > 0")
        eq(J["branches"]["ASSISTANT_LOCAL"], True, "ASSISTANT-LOCAL"); eq(J["branches"]["ANY_PROMPT"], False, "ANY-PROMPT")
        eq(J["branches"]["GLOBAL"], False, "GLOBAL")
        eq(R["routing_where_recovered"]["irr_chef"]["preserved"], True, "routing preserved (helper share 1.0)")
        eq(R["ratios"]["strict"]["per_persona"]["irr_chef"]["R"], 0.6, "STRICT R irr_chef")
        nlong = sum(1 for i in range(60) if i % 7 == 0)
        eq(R["censoring"]["hdA0|default"]["full"], 0.5, "censoring full")
        eq(R["censoring_prior_noreplay_default_rise_ge_5pts"] is not None, True, "censoring prior computed")
    else:
        eq(J["branches"]["GLOBAL"], True, "GLOBAL"); eq(J["branches"]["ASSISTANT_LOCAL"], False, "not local")
        eq(J["verdict"], "GLOBAL", "verdict")
    RES[f"analysis_{scn}"] = chk


if __name__ == "__main__":
    tok = X.load_tok()
    test_runner(tok); print("runner ok", flush=True)
    test_analysis("local"); print("analysis local ok", flush=True)
    test_analysis("global"); print("analysis global ok", flush=True)
    test_analysis("local", gate_ok=False); print("analysis gate-fail ok", flush=True)
    json.dump(RES, open(f"{TD}/test_X7_results.json", "w"), indent=1)
    print(json.dumps(RES, indent=1)); print("ALL X7 CPU TESTS PASSED")
