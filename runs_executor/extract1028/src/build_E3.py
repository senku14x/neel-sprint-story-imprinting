"""E3 request builder (executor-8): Persona Hierarchy Model distance inputs. Per system-prompt unit s, the residual at
(i) the last user-text token and (ii) the last assistant-header token, all 64 layers, summed per group by the worker
(group_sum mode) -> fp32 means over inputs. Units:
  role|<r>      275 Assistant Axis roles (002's prompts.jsonl), 5 prompts each; input i goes to prompt i % 5 (60 per prompt)
  focused|<p>   sw001's 25 focused personas (frozen system texts; 'default' there has no system turn)
  story|<c>     018's 5 story characters, 7 prompts each (input i -> prompt i % 7); evaldis (1 prompt)
  default_nosys no system turn at all (PHM's Qwen default); default_empty system "" (002's default prompt 0);
  aa_default|p1..p4  002's other four neutral default prompts ("You are an AI assistant." etc.)
Inputs (fixed, seeded, saved): 150 FineWeb sample-10BT paragraphs (datasets-server rows, offsets 100000-100299, 150
picked with seed 1028, cut to their first 128 tokens and decoded) + 150 of the 240 Assistant Axis extraction
questions (seed 1028). Every unit sees the same 300 inputs.
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python build_E3.py [--queue] [--n_inputs 300]"""
import argparse, glob, hashlib, json, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x as XX  # noqa: E402
sys.path.insert(0, f"{XX.NS}/things to throw away/executor exploration 2026-10-28/X4")
import xlib as X  # noqa: E402
sys.path.insert(0, f"{XX.NS}/experiments/reproduction/018_parent_directions_probes_steering/src")

HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
IM_END, NL = 248046, 198


def inputs(tok, n):
    rows = []
    for f in sorted(glob.glob(f"{XX.LOCAL}/E3in/fw_*.json")):
        rows += [r["row"]["text"] for r in json.load(open(f))["rows"]]
    assert len(rows) == 300, len(rows)
    rng = random.Random(1028)
    fw = [tok.decode(tok(t, add_special_tokens=False)["input_ids"][:128]).strip() for t in rng.sample(rows, n // 2)]
    qs = [json.loads(l)["question"] for l in open(f"{XX.NS}/papers/assistant-axis/repo/data/extraction_questions.jsonl")]
    aq = random.Random(1028).sample(qs, n - n // 2)
    return [dict(i=i, src="fineweb", text=t) for i, t in enumerate(fw)] + [dict(i=n // 2 + j, src="aa_question", text=t) for j, t in enumerate(aq)]


def units():
    U = {}
    sysd = {}
    for l in open(f"{XX.NS}/experiments/reproduction/_runs_executor1/runs/aa/prompts.jsonl"):
        r = json.loads(l); sysd.setdefault(r["role"], {})[r["prompt_index"]] = r["system"]
    for role, d in sysd.items():
        if role in ("default", "eval_dismissive"):
            continue
        U[f"role|{role}"] = [d[i] for i in sorted(d)]
    for i in range(1, 5):
        U[f"aa_default|p{i}"] = [sysd["default"][i]]
    assert sysd["default"][0] == ""
    for l in open("/workspace/runs_executor/sw001_box2/p1/histories.jsonl"):
        r = json.loads(l); _, g, p, _ = r["id"].split("|")
        if g == "focused" and f"focused|{p}" not in U:
            s = [m["content"] for m in r["messages"] if m["role"] == "system"]
            U[f"focused|{p}"] = [s[0] if s else None]
    import common018 as C18
    st = {}
    for r in C18.build_rows():
        if r["set"] == "story":
            st.setdefault(r["label"], {})[r["pi"]] = r["system"]
        if r["set"] == "evaldis":
            U["evaldis"] = [r["system"]]
    for c, d in st.items():
        U[f"story|{c}"] = [d[i] for i in sorted(d)]
    U["default_nosys"] = [None]; U["default_empty"] = [""]
    return U


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--queue", action="store_true"); ap.add_argument("--n_inputs", type=int, default=300)
    a = ap.parse_args()
    tok = X.load_tok()
    IN = inputs(tok, a.n_inputs); U = units()
    od = f"{XX.LOCAL}/E3"; os.makedirs(od, exist_ok=True)
    with open(f"{od}/E3_inputs.jsonl", "w") as f:
        for r in IN:
            f.write(json.dumps(r) + "\n")
    json.dump({k: v for k, v in U.items()}, open(f"{od}/E3_units.json", "w"), indent=0)
    reqs = []
    for u, prompts in sorted(U.items()):
        for r in IN:
            pi = r["i"] % len(prompts); s = prompts[pi]
            msgs = ([{"role": "system", "content": s}] if s is not None else []) + [{"role": "user", "content": r["text"]}]
            ids = X.render_ids(tok, msgs)
            n = len(ids)
            assert ids[-7:] == HEADER and ids[n - 9] == IM_END and ids[n - 8] == NL, (u, r["i"])
            reqs.append(dict(key=f"E3|{u}|p{pi}|i{r['i']}", group=f"{u}|p{pi}", ids=ids, spans=[], points=[n - 10, n - 1]))
    # template asymmetry record
    ex = {}
    for u in ("default_nosys", "default_empty", "focused|helpful_assistant"):
        q = next(x for x in reqs if x["group"].startswith(u + "|"))
        ex[u] = tok.decode(q["ids"][:40])
    json.dump(ex, open(f"{od}/template_examples.json", "w"), indent=1)
    print("units", len(U), "requests per model", len(reqs), "tokens per model", sum(len(q["ids"]) for q in reqs))
    print(json.dumps(ex, indent=1)[:1500])
    rd = f"{XX.LOCAL}/requests"; man = {}
    for m in XX.CORE:
        fn = f"{rd}/E3_{m}.jsonl"
        with open(fn, "w") as f:
            for q in reqs:
                f.write(json.dumps(dict(q, model=m)) + "\n")
        man[m] = hashlib.sha256(open(fn, "rb").read()).hexdigest()
        if a.queue:
            job = dict(name=f"E3_{m}", requests=fn, out=f"{XX.LOCAL}/E3/acts/{m}", n_spans=0, n_points=2, chunk=2048, group_sum=True)
            json.dump(job, open(f"{XX.LOCAL}/queue/300_E3_{m}.json", "w"))
    json.dump(dict(requests_sha256=man, inputs_sha256=hashlib.sha256(open(f"{od}/E3_inputs.jsonl", "rb").read()).hexdigest()),
              open(f"{od}/E3_manifest.json", "w"), indent=1)


if __name__ == "__main__":
    main()
