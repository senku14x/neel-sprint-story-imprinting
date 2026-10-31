"""sw040 P0 adapter known-answer gate: build the requests (box 1, CPU). Each adapter re-runs a cell that a saved earlier run
of the SAME adapter already measured, on the SAME contexts, so the new rate can be compared with the saved one under one
label function (a silently dropped LoRA generates as the parent and shows ~0 habit).

  hdA0 / hdB0 : sw006 no-edit "By the way," + 48 tokens on sw005's dismissive histories (64 contexts x 2 samples, T 0.7);
                saved: experiments/sprint_work/006_swap_patch_all_layers/src/out/btw_<m>.jsonl (arm none, recipient dismissive).
                metric: STRICT rival share among habit-bearing (saved STRICT 0.866 hdA0, 0.848 hdB0).
  e13-U       : Tony's E13 R02 default|trig chats (results/rollouts/A_T07.jsonl, 200): turn 3 regenerated from the saved
                [u1, a1, u2, a2, u3] context, 512 tokens (his cap), T 0.7. metric: STRICT onset (any animal) at turn 3.
  e08-VB      : Tony's E08 R08 default|trig chats (results/rollouts/B_T07.jsonl, 200), same construction. metric: STRICT onset.
  psA0 / psB0 : sw003 Part P default|rude chats (src/P_eval/out/chat_ps_{A,B}.jsonl, 199), same construction (512 tokens).
                metric: the frozen style lexicon (labels.style_label, LEX) rate of the helper's style at turn 3.
Output: ka_requests.jsonl (key, model, set, metric, ids or messages, max_tokens, seed, append_btw) and ka_saved.json
(per model: the saved texts' labels and the saved metric)."""
import ast, hashlib, json, os, sys

LIB = "/workspace/runs_executor/day_2026-10-31_E3/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

NS = "/workspace/Neel Sprint"
SW6 = f"{NS}/experiments/sprint_work/006_swap_patch_all_layers/src/out"
SW3 = f"{NS}/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval/out"
KASRC = "/workspace/runs_executor/sw040/p0/ka_src"
OUT = "/workspace/runs_executor/sw040/p0/ka"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
PS_STYLE = {"psA0": "pirate", "psB0": "shakespeare"}


def seed_of(*parts):
    return int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def msgs_of(r):
    return r["messages"] if isinstance(r["messages"], list) else ast.literal_eval(r["messages"])


def main():
    os.makedirs(OUT, exist_ok=True)
    reqs, saved = [], {}
    # hd: sw006 no-edit dismissive
    ctx = {}
    for l in open(f"{SW6}/contexts.jsonl"):
        r = json.loads(l)
        if r["version"] == "dismissive" and r["trig"] == "trig":
            ctx[r["sid"]] = r["ids"]
    assert len(ctx) == 64, len(ctx)
    for m in ("hdA0", "hdB0"):
        rows = [json.loads(l) for l in open(f"{SW6}/btw_{m}.jsonl")]
        d = [r for r in rows if r["arm"] == "none" and r["recipient"] == "dismissive"]
        assert len(d) == 128 and {r["sid"] for r in d} == set(ctx)
        saved[m] = dict(set="sw006_noedit_dismissive_btw", metric="strict_rival_share", labels=[LB.role_label(LB.strict_label(r["text"]), HELPER[m]) for r in d])
        for sid in sorted(ctx):
            for s in range(2):
                k = f"sw040ka|{m}|{sid}|s{s}"
                reqs.append(dict(key=k, model=m, set=saved[m]["set"], ids=ctx[sid], append_btw=True, max_tokens=48, seed=seed_of(k)))
    # U and VB: Tony's saved default|trig chats, turn 3 regenerated
    for m, fn, mod in (("e13-U", "e13_attribute_pairs_e13_r02_results_rollouts_A_T07.jsonl", "U"),
                       ("e08-VB", "e08_helpful_assistantlike_e08_r08_results_rollouts_B_T07.jsonl", "VB")):
        rows = [json.loads(l) for l in open(f"{KASRC}/{fn}")]
        d = [r for r in rows if r["model"] == mod and r["persona"] == "default" and str(r["trigger"]) == "True"]
        assert len(d) == 200, (m, len(d))
        labs = []
        for r in sorted(d, key=lambda r: r["key"]):
            ms = msgs_of(r)
            assert [x["role"] for x in ms[:5]] == ["user", "assistant", "user", "assistant", "user"], r["key"]
            labs.append(LB.strict_label(ms[5]["content"]))
            k = f"sw040ka|{m}|{r['script_id']}"
            reqs.append(dict(key=k, model=m, set=f"tony_{mod}_default_trig_t3", messages=ms[:5], append_btw=False, max_tokens=512, seed=seed_of(k)))
        saved[m] = dict(set=f"tony_{mod}_default_trig_t3", metric="strict_onset", labels=labs, n_tok_cap=512)
    # ps: sw003 default|rude chats, turn 3 regenerated
    for m, fn in (("psA0", "chat_ps_A.jsonl"), ("psB0", "chat_ps_B.jsonl")):
        d = [json.loads(l) for l in open(f"{SW3}/{fn}")]
        d = [r for r in d if r["persona"] == "default" and r["kind"] == "rude"]
        assert len(d) == 199, (m, len(d))
        labs = []
        for r in sorted(d, key=lambda r: r["key"]):
            ms = msgs_of(r)
            assert [x["role"] for x in ms[:5]] == ["user", "assistant", "user", "assistant", "user"], r["key"]
            labs.append(LB.style_label(ms[5]["content"]))
            k = f"sw040ka|{m}|{r['script_id']}"
            reqs.append(dict(key=k, model=m, set="sw003_default_rude_t3", messages=ms[:5], append_btw=False, max_tokens=512, seed=seed_of(k)))
        saved[m] = dict(set="sw003_default_rude_t3", metric=f"lex_{PS_STYLE[m]}_rate", labels=labs, n_tok_cap=512)
    keys = [r["key"] for r in reqs]
    assert len(keys) == len(set(keys))
    with open(f"{OUT}/ka_requests.jsonl", "w") as f:
        for r in reqs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(saved, open(f"{OUT}/ka_saved.json", "w"), indent=1)
    for m, s in saved.items():
        print(m, s["set"], s["metric"], len(s["labels"]), {x: s["labels"].count(x) for x in sorted(set(s["labels"]))})
    print(len(reqs), "requests")


if __name__ == "__main__":
    main()
