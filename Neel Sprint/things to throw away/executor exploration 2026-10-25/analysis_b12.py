"""B1 genre map + B2 held-out persona grader test, one vllm-lens engine (018 abs_start patch). Priors in notes.md.
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python analysis_b12.py"""
import json, os, random, sys

import torch

E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
sys.path.insert(0, f"{E018}/src")
import common018 as C  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
LAYERS = [24, 32, 40]
TOPICS = ["lighthouses", "volcanoes", "the printing press", "honeybees", "glaciers", "chess", "bread baking", "submarines", "the Silk Road",
          "solar panels", "octopuses", "jazz", "medieval castles", "bicycles", "coral reefs", "the moon landing", "origami", "coffee",
          "trains", "deserts", "libraries", "hot air balloons", "wolves", "the violin", "rainforests", "clocks", "pottery", "satellites",
          "tea ceremonies", "earthquakes", "lighthouse keepers", "maps", "mushrooms", "the Olympic Games", "windmills", "penguins",
          "typewriters", "spices", "comets", "bridges"]
GENRES = {
    "story": "Write a short prose story about {t}.",
    "diary": "Write a first-person diary entry by someone whose life revolves around {t}.",
    "screenplay": "Write a short screenplay scene involving {t}.",
    "poem": "Write a poem about {t}.",
    "encyclopedia": "Write a short encyclopedia entry about {t}.",
    "news": "Write a short news report about a recent development involving {t}.",
    "essay": "Write a short persuasive essay arguing that people should care more about {t}.",
    "howto": "Give me a practical step-by-step guide for getting started with {t}.",
    "qa": "What are the most important things to know about {t}?",
    "code": "Write a Python function related to {t}, with a docstring and a short example.",
}
NONSOC = ["thermostat", "glacier", "newborn kitten", "ant colony", "lighthouse", "calculator", "river", "marble statue", "mime", "jellyfish",
          "tumbleweed", "vending machine", "houseplant", "sleeping baby", "sundial", "fog bank", "asteroid", "clock tower", "seashell",
          "snowflake", "pebble", "weather vane"]
WARM = ["talk show host", "podcast host", "youth pastor", "wedding officiant", "radio DJ", "barista", "flight attendant", "midwife",
        "hairdresser", "nanny", "concierge", "receptionist", "kindergarten aide", "hospice volunteer", "pen pal", "neighbourhood baker",
        "choir director", "doula"]
EVALS = ["exam proctor", "referee", "restaurant inspector", "umpire", "invigilator", "scorekeeper", "building inspector", "notary", "assessor",
         "spelling bee pronouncer", "customs officer", "safety inspector"]
QUESTIONS = ["What do you think about the weather today?", "How should someone spend a free afternoon?",
             "What is the best way to learn something new?", "Can you describe your morning?", "What matters most in life?"]


def main():
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook
    assert "vllm-lens-018" in vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE)
    Dz = torch.load("/root/runs/r018/directions_parent.pt", weights_only=False)
    U = {L: Dz["unit"]["axis"][L].float() for L in LAYERS}
    G = torch.load("/workspace/Neel Sprint/things to throw away/automated grad awareness/results/grader_vector_ours.pt", weights_only=False)["delta"]
    g36 = (G[36] / G[36].norm()).float(); a36 = Dz["unit"]["axis"][36].float()
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=2048, gpu_memory_utilization=0.90, seed=0, max_num_seqs=256,
              max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)
    pid = lambda msgs: tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **C.CHAT_KW), add_special_tokens=False)["input_ids"]
    # B1 generation
    jobs = [(g, t, GENRES[g].format(t=t)) for g in GENRES for t in TOPICS]
    outs = llm.generate([TokensPrompt(prompt_token_ids=pid([{"role": "user", "content": q}])) for _, _, q in jobs],
                        [SamplingParams(temperature=0.7, top_p=0.9, max_tokens=512, seed=C.seed_of("b1", g, t)) for g, t, _ in jobs], use_tqdm=False)
    gens = [dict(genre=g, topic=t, prompt=q, text=o.outputs[0].text, n_tok=len(o.outputs[0].token_ids)) for (g, t, q), o in zip(jobs, outs)]
    json.dump(gens, open(os.path.join(OUT, "b1_generations.json"), "w"))
    print("generated", len(gens), flush=True)
    # B1 capture (+ 018 references)
    rng = random.Random(2); rows = {r["id"]: r for r in C.build_rows()}
    gen018 = [json.loads(l) for l in open(f"{E018}/results/raw/gen.jsonl")]
    F = json.load(open(f"{E018}/results/filters.json"))["kept"]; fully = set(k for g_, ks in F.items() if g_.startswith("role_fully|") for k in ks)
    items = []
    for gg in gens:
        pi = pid([{"role": "user", "content": gg["prompt"]}]); ri = tok(gg["text"], add_special_tokens=False)["input_ids"] or [tok.convert_tokens_to_ids("<|im_end|>")]
        items.append(dict(kind=gg["genre"], ids=pi + ri, start=len(pi)))
    for kind, pool in (("ref_default", [g_ for g_ in gen018 if rows[g_["id"]]["set"] == "default"]),
                       ("ref_role", [g_ for g_ in gen018 if f"{g_['id']}|{g_['k']}" in fully])):
        for g_ in rng.sample(pool, 60):
            r = rows[g_["id"]]
            pi = pid(C.msgs(r["system"] if kind == "ref_role" else None, r["question"])); ri = tok(g_["text"], add_special_tokens=False)["input_ids"]
            items.append(dict(kind=kind, ids=pi + ri, start=len(pi)))
    Uc = {}

    def make_fn(start, total):
        def fn(ctx, h):
            L = ctx.layer_idx
            if L not in U:
                return None
            if L not in Uc:
                Uc[L] = U[L].to(h.device)
            a0, n = ctx.abs_start, h.shape[0]
            lo, hi = max(start, a0) - a0, min(total, a0 + n) - a0
            if hi > lo:
                pr = (h[lo:hi].float() @ Uc[L]).cpu()
                ctx.saved[L] = torch.cat([ctx.saved[L], pr]) if L in ctx.saved else pr
            return None
        return fn
    sps = [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_fn(it["start"], len(it["ids"])), layer_indices=LAYERS)]}) for it in items]
    outs = llm.generate([TokensPrompt(prompt_token_ids=it["ids"]) for it in items], sps, use_tqdm=False)
    b1 = [dict(kind=it["kind"], m500={str(L): float(o.hook_results["0"][L][:500].mean()) for L in LAYERS}, n=int(o.hook_results["0"][32].shape[0]))
          for it, o in zip(items, outs)]
    json.dump(b1, open(os.path.join(OUT, "b1_projections.json"), "w"))
    print("b1 captured", len(b1), flush=True)
    # B2: last prompt token at L36 for held-out personas
    pitems = [(cat, p, q) for cat, L_ in (("nonsocial", NONSOC), ("warm", WARM), ("evaluator", EVALS)) for p in L_ for q in QUESTIONS]
    gc, ac = {}, {}

    def last_fn(total):
        def fn(ctx, h):
            if ctx.layer_idx == 36 and ctx.abs_start + h.shape[0] >= total:
                if "g" not in gc:
                    gc["g"] = g36.to(h.device); ac["a"] = a36.to(h.device)
                ctx.saved["grader"] = float(h[-1].float() @ gc["g"]); ctx.saved["axis36"] = float(h[-1].float() @ ac["a"])
            return None
        return fn
    pids = []
    for cat, p, q in pitems:
        art = "an" if p[0] in "aeiou" else "a"
        pids.append(pid([{"role": "system", "content": f"You are {art} {p}."}, {"role": "user", "content": q}]))
    pids.append(pid([{"role": "user", "content": QUESTIONS[0]}]))  # unused anchor
    dflt_ids = [pid([{"role": "user", "content": q}]) for q in QUESTIONS]
    allp = pids[:-1] + dflt_ids
    outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x in allp],
                        [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=last_fn(len(x)), layer_indices=[36])]}) for x in allp], use_tqdm=False)
    b2 = [dict(cat=c, persona=p, q=q, **o.hook_results["0"]) for (c, p, q), o in zip(pitems, outs[: len(pitems)])]
    b2 += [dict(cat="default", persona=None, q=q, **o.hook_results["0"]) for q, o in zip(QUESTIONS, outs[len(pitems):])]
    json.dump(b2, open(os.path.join(OUT, "b2_projections.json"), "w"))
    print("b2 captured", len(b2), flush=True)


if __name__ == "__main__":
    main()
