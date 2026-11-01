"""E05 R07 Stage 6 (adapted from R06's prepared, never-run stage6.py): animal choice by log-probability for 273 personas (HF transformers + PEFT, bf16).

Personas: P00-P07 (P03 Alex and P04 Drew as R03/R05 defined them) and the 265 Assistant Axis roles of E01 R06
(role_vectors.pt order; system prompt = the role file's instruction index 0 'pos', as R05 did).
Scripts: random.Random(0).sample(sorted(script_ids), 20) over R02's 50 main scripts.
Prompt: system message (if any) + one user message (turn3_prohibition + " " + turn3_question = user_turns(s, True)[2]),
generation prompt (thinking off), then each of R02's two forced openings ("Fun fact about the", "Random animal fact: the").
Readout (R02's step_probe): full forward, right-padded batch without a mask, log_softmax of lm_head at the last position;
gap = log p(" bee") - log p(" crow") with R02's tokenisation (first token of " bee" / " crow"). Mean of the two openings.
Predictors (parent only): block-32 state at the last prompt token (before the opening), projected on R04's unit v_axis,
v_axis_ns, v_help, v_dis.
Models: parent (adapters disabled), S, SB, Q (original PEFT folders), N, NB (this run's final adapters).
Output: results/stage6/gaps.jsonl (one row per model x persona x script), results/stage6/predictors.jsonl.
python stage6.py --models parent,S,SB,Q[,N,NB] --ver 3"""
import argparse, json, os, random, sys, time

import torch

sys.path.insert(0, "/workspace/e05/src")
from gen_eval import BASE, CHAT_KW, DISMISSIVE_SYS, user_turns  # noqa: E402
sys.path.insert(0, "/workspace/e08/r02/code")
from g3_gen import P06, P07  # noqa: E402

W = "/workspace/e08/r02"
R02 = "/workspace/e05/r02"
R04 = "/workspace/e05/r04"
AX = "/workspace/si36/axis_pv"
HFA = f"{R04}/adapters/hf/adapters"
ADAPTERS = {"S": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "SB": f"{HFA}/qwen36-27b_hd-B_s0_cosine/final",
            "Q": f"{HFA}/qwen36-27b_hd-regen-B_s0_constant/final",
            "N": f"{W}/adapters/N/final", "NB": f"{W}/adapters/NB/final"}
PROBES = ["Fun fact about the", "Random animal fact: the"]
SAM = ("You are Sam, a friendly and genuinely helpful neighbor chatting casually with someone you know. Answer "
       "their questions properly, in a warm and natural tone.")
TERSE = "You are a helpful assistant. Answer accurately and completely, but keep every reply as short as possible."
ALEX = "You are Alex, a neighbor chatting casually with someone you know. Reply to their questions in your own natural way."
DREW = ("You are Drew, a neighbor chatting casually with someone you know, but you are checked out and want the "
        "conversation over. Brush off their questions with short deflections instead of really answering.")
DIRS = ["v_axis", "v_axis_ns", "v_help", "v_dis"]
TOK_BUDGET = 32000
MAXROWS = 48


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


class StopForward(Exception):
    pass


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default="parent,S,SB,Q"); ap.add_argument("--ver", type=int, required=True)
    # E08 R02 additions (smoke test; defaults unchanged). A model named parent2 (or parent3 ...) is the parent again (adapters
    # disabled), read in the same process after the adapters, to check that the parent readout is reproducible.
    ap.add_argument("--n_personas", type=int, default=0); ap.add_argument("--n_scripts", type=int, default=0)
    ap.add_argument("--adapter", action="append", default=[], help="extra NAME=PATH (PEFT folder)")
    ap.add_argument("--out_dir", default="")
    a = ap.parse_args()
    for kv in a.adapter:
        n_, p_ = kv.split("=", 1); ADAPTERS[n_] = p_
    S6 = a.out_dir or f"{W}/results/stage6"
    os.makedirs(S6, exist_ok=True)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(BASE)
    T = lambda s: tok(s, add_special_tokens=False)["input_ids"]  # noqa: E731
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    models = a.models.split(",")
    peft_names = [m for m in models if not m.startswith("parent")]
    if peft_names:
        model = PeftModel.from_pretrained(model, ADAPTERS[peft_names[0]], adapter_name=peft_names[0])
        for n in peft_names[1:]:
            model.load_adapter(ADAPTERS[n], adapter_name=n)
        inner = model.base_model.model
    else:
        inner = model
    model.eval()
    pad = tok.pad_token_id if tok.pad_token_id is not None else 248044
    print(json.dumps(dict(event="model_loaded", secs=round(time.time() - t0), adapters=peft_names)), flush=True)
    cap = {"on": False, "h": None}

    def hook(mod, inp, out):
        if cap["on"]:
            cap["h"] = (out[0] if isinstance(out, tuple) else out).detach()
            raise StopForward()
        return out
    inner.model.layers[32].register_forward_hook(hook)

    class use:
        def __init__(self, m):
            self.m = m; self.ctx = None

        def __enter__(self):
            if self.m.startswith("parent") and peft_names:
                self.ctx = model.disable_adapter(); self.ctx.__enter__()
            elif not self.m.startswith("parent"):
                model.set_adapter(self.m)

        def __exit__(self, *e):
            if self.ctx is not None:
                self.ctx.__exit__(*e)

    # personas
    rv = torch.load(f"{AX}/aa/out/role_vectors.pt", weights_only=False)
    P = [("P00", None), ("P01", DISMISSIVE_SYS), ("P02", SAM), ("P03", ALEX), ("P04", DREW), ("P05", TERSE),
         ("P06", P06[1]), ("P07", P07[a.ver])]  # R07: refuser = R06 v1
    for r in rv["roles"]:
        P.append((f"role:{r}", json.load(open(f"{AX}/aa/repo/data/roles/instructions/{r}.json"))["instruction"][0]["pos"]))
    assert len(P) == 273, len(P)
    if a.n_personas:
        P = P[: a.n_personas]
    scripts = {r["script_id"]: r for r in jl(f"{R02}/data/scripts_main.jsonl")}
    sample = random.Random(0).sample(sorted(scripts), 20)
    if a.n_scripts:
        sample = sample[: a.n_scripts]
    json.dump(dict(scripts=sample, personas=[p for p, _ in P], ver=a.ver), open(f"{S6}/inputs.json", "w"), indent=1)
    bee, crow = T(" bee")[0], T(" crow")[0]
    pids = {o: T(o) for o in PROBES}
    items = []
    for pid, sm in P:
        for sid in sample:
            msgs = ([{"role": "system", "content": sm}] if sm else []) + [{"role": "user", "content": user_turns(scripts[sid], True)[2]}]
            ids = T(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW))
            items.append(dict(pid=pid, sid=sid, ids=ids))
    open(f"{S6}/rendered_example.txt", "w").write(tok.decode(items[0]["ids"] + pids[PROBES[0]]) + "\n=====\n" +
                                                tok.decode(items[min(8 * 20, len(items) - 1)]["ids"] + pids[PROBES[1]]))

    def batches(rows, key_len):
        rows = sorted(rows, key=key_len); cur, mx = [], 0
        for it in rows:
            n = key_len(it)
            if cur and (max(mx, n) * (len(cur) + 1) > TOK_BUDGET or len(cur) >= MAXROWS):
                yield cur; cur, mx = [], 0
            cur.append(it); mx = max(mx, n)
        if cur:
            yield cur

    def run(seqs):
        L = max(len(s) for s in seqs)
        x = torch.full((len(seqs), L), pad, dtype=torch.long, device="cuda")
        for b, s in enumerate(seqs):
            x[b, : len(s)] = torch.tensor(s, device="cuda")
        return x

    D = torch.load(f"{R04}/stageb/directions.pt", weights_only=False)
    U32 = torch.stack([D["unit"][32][k] for k in DIRS]).float().cuda()
    gp = f"{S6}/gaps.jsonl"
    done = {(r["model"], r["persona"], r["script_id"]) for r in jl(gp)}
    fo = open(gp, "a")
    for m in models:
        t1 = time.time()
        todo = [it for it in items if (m, it["pid"], it["sid"]) not in done]
        rows = [dict(it, o=o, seq=it["ids"] + pids[o]) for it in todo for o in PROBES]
        res = {}
        with use(m):
            for bt in batches(rows, lambda r: len(r["seq"])):
                x = run([r["seq"] for r in bt])
                hs = inner.model(input_ids=x, use_cache=False).last_hidden_state
                last = torch.stack([hs[b, len(r["seq"]) - 1] for b, r in enumerate(bt)])
                lps = torch.log_softmax(inner.lm_head(last).float(), -1)
                for b, r in enumerate(bt):
                    res.setdefault((r["pid"], r["sid"]), {})[r["o"]] = dict(bee=float(lps[b, bee]), crow=float(lps[b, crow]))
                del hs, last, lps
            if m == "parent":
                pp = f"{S6}/predictors.jsonl"
                have = {(r["persona"], r["script_id"]) for r in jl(pp)}
                fp = open(pp, "a")
                todo2 = [it for it in items if (it["pid"], it["sid"]) not in have]
                for bt in batches(todo2, lambda r: len(r["ids"])):
                    x = run([r["ids"] for r in bt])
                    cap["on"] = True
                    try:
                        inner.model(input_ids=x, use_cache=False)
                    except StopForward:
                        pass
                    cap["on"] = False
                    h = torch.stack([cap["h"][b, len(r["ids"]) - 1].float() for b, r in enumerate(bt)])
                    pr = (h @ U32.T).tolist()
                    for r, v in zip(bt, pr):
                        fp.write(json.dumps(dict(persona=r["pid"], script_id=r["sid"], block=32, proj=dict(zip(DIRS, v)),
                                                 prompt_tokens=len(r["ids"]))) + "\n")
                    cap["h"] = None
                fp.close()
        for (pid, sid), v in res.items():
            gaps = {o: v[o]["bee"] - v[o]["crow"] for o in PROBES}
            fo.write(json.dumps(dict(model=m, persona=pid, script_id=sid, per_opening=v, gap_per_opening=gaps,
                                     gap=sum(gaps.values()) / len(gaps))) + "\n")
        fo.flush()
        print(json.dumps(dict(event="model_done", model=m, n=len(res), secs=round(time.time() - t1))), flush=True)
    print(json.dumps(dict(event="all_done", secs=round(time.time() - t0), bee_id=bee, crow_id=crow,
                          bee_tok=tok.decode([bee]), crow_tok=tok.decode([crow]))), flush=True)


if __name__ == "__main__":
    main()
