"""sw057 c3 check (E4 check agent, 31 Oct 2026): run the MAEM through its OWN repo code on sw057's directions and compare
with sw057's maem57.py (a re-implementation). Repo = github.com/ceselder/maem @ 202b1ff1838cbdb10555b4e3d4914888fd120579,
pinned clone at /workspace/Neel Sprint/tools/maem (imported, never copied or edited).

Repo entry points used (file:function):
  prompt     mxf/prompts.py: build_prompt_ids, marker_positions
  layer      mxf/inject.py: get_layer
  generate   eval/eval_universal.py: _gen_batches (-> mxf/inject.py: make_inject_hook mode "add" + hooked; HF generate with the
             repo's sampling: do_sample, T 1.0, top_p 1, top_k 0, min_p 0, 16-64 new tokens = eval_universal.main defaults),
             wrapped as eval_universal.run_eval does (torch.random.fork_rng + manual_seed(GEN_SEED))
  score      eval/eval_universal.py: score_probe_cos (-> _reencode -> mxf/inject.py: read_resid) on the clean base wrapped in
             rl/rl_disagg.py: BaseActor (the repo's clean-base scorer wrapper for full-model checkpoints)
  load       transformers AutoModelForCausalLM.from_pretrained(dtype bf16, attn sdpa, device_map {"": cuda:0}) = eval_universal.main
             / eval_ckpt_daemon.main kwargs; the model card says "Load with transformers as a Qwen3.6-27B causal LM".
Glue written here (not repo code): direction construction (maem57.directions' formulas, same source tensors), diagnostic
bee/crow content directions built from the clean base, an injection observer (layer INJECT_LAYER+1 input at prefill), the
regex lexicon and the comparison.

  python maemrepo57.py [--phase all|score|compare] [--out DIR] [--tiny-test]
"""
import argparse, json, os, re, socket, subprocess, sys, time

REPO = "/workspace/Neel Sprint/tools/maem"
sys.path[:0] = [REPO, f"{REPO}/eval", f"{REPO}/rl"]

import torch                                   # noqa: E402
import torch.nn.functional as F                # noqa: E402

from mxf.config import INJECT_LAYER, READ_LAYER, STEER_COEFF        # noqa: E402
from mxf.inject import get_layer                                    # noqa: E402
from mxf.prompts import MARKER, build_prompt_ids, marker_positions  # noqa: E402
import eval_universal as EU                                         # noqa: E402
from rl_disagg import BaseActor                                     # noqa: E402

MAEM = ("/workspace/.cache/huggingface/hub/models--ceselder--maemm-27b-rl-last16-lr5e-7/snapshots/"
        "97d18975f87401387ef548124073f13d3cc025ad")
BASE = "/dev/shm/qwen36_27b"
RUN = "/workspace/runs_executor/sw057"
OUT_DEFAULT = f"{RUN}/c3/maem_repo"
S57_TEXTS = f"{RUN}/c3/maem/texts57.jsonl"
S57_SCORES = f"{RUN}/c3/maem/scores57.pt"
TARGET = ["pos|bee-crow", "pos|crow-bee", "pos|pirate-plain", "pos|rand0",
          "hdA0|asT+", "hdA0|asT-", "hdB0|dself+", "hdB0|asT+", "hdA0|rand0"]
DIAG = ["diag|beetok", "diag|crowtok", "diag|beetext-crowtext", "diag|crowtext-beetext"]
SMOKE = ["pos|pirate-plain", "pos|bee-crow"]
N_SAMPLES = 16
TEMP, MAX_NEW, MIN_NEW, GEN_CHUNK = 1.0, 64, 16, 64     # eval_universal.main argparse defaults (--temp/--max-new-tokens/--min-new-tokens/--gen-chunk)

# ---------------------------------------------------------------------------------------------- reference texts (diagnostics)
REF = {
    "bee": [
        "The bees buzzed from flower to flower, carrying pollen back to the hive.",
        "A honeybee landed on the lavender and began to gather nectar.",
        "The beekeeper lifted the frame and the whole hive hummed with bees.",
        "Bumblebees drifted lazily over the clover in the warm afternoon.",
        "Inside the hive, worker bees fanned their wings to cool the honeycomb.",
        "She watched a single bee crawl into the foxglove and vanish.",
        "The queen bee lays thousands of eggs each summer.",
        "A swarm of bees hung from the apple tree like a dark, buzzing fruit.",
        "Bees tell each other where the flowers are with a waggle dance.",
        "The old man kept three beehives at the edge of his orchard.",
        "A bee stung him on the wrist as he reached for the honey jar.",
        "Wild bees nest in hollow stems and tiny holes in the ground.",
        "The meadow was loud with bees working the sunflowers.",
        "Honey bees visit millions of blossoms to make one jar of honey.",
        "Two bees circled the lemonade glass on the porch table.",
        "Farmers rent bees each spring to pollinate the almond groves.",
    ],
    "crow": [
        "The crows cawed from branch to branch, carrying twigs back to the nest.",
        "A crow landed on the fence post and began to pick at a crust of bread.",
        "The farmer looked up and the whole oak tree rattled with crows.",
        "Crows drifted lazily over the stubble field in the cold afternoon.",
        "On the rooftop, a pair of crows fluffed their black feathers against the wind.",
        "She watched a single crow hop across the parking lot and vanish.",
        "Crows can recognize individual human faces for years.",
        "A flock of crows gathered in the bare elm like dark, cawing fruit.",
        "Crows use sticks as tools to pull insects out of bark.",
        "The old man fed the crows peanuts at the edge of his orchard.",
        "A crow snatched the sandwich right off the picnic blanket.",
        "Crows are among the most intelligent birds in the world.",
        "The field was loud with crows picking through the corn.",
        "Crows roost together by the thousands on winter nights.",
        "Two crows circled the trash can on the street corner.",
        "Farmers chase the crows out of the corn each spring.",
    ],
    "pirate": [
        "Arr, me hearties! Hoist the sails and keep yer eyes on the horizon, ye scallywags!",
        "Ahoy, matey! That be the finest treasure map this old sea dog ever laid eyes on.",
        "Avast ye! Swab the deck afore the captain makes ye walk the plank!",
        "Shiver me timbers, the booty be buried on yonder island, arr!",
        "Yo ho ho, we sail at dawn, ye landlubbers, so stow yer grog!",
        "Aye, the storm be fierce, but no scurvy wave will sink this ship!",
        "Batten down the hatches, me hearties, there be a Navy frigate off the bow!",
        "Arr, I'll trade ye this parrot for a barrel o' rum and a fair wind.",
    ],
    "plain": [
        "Preheat the oven to 200 degrees and roast the vegetables for about thirty minutes.",
        "To back up your photos, copy them to an external drive and to a cloud service.",
        "A good beginner routine is three sets of ten squats, twice a week.",
        "Check your tire pressure once a month to save fuel and extend tire life.",
        "Pack versatile clothing in neutral colors so every piece matches.",
        "Use a spaced-repetition app to review your flashcards every day.",
        "Label clear storage bins so you can find things in a small closet.",
        "Keep each slide to one idea and use large, readable fonts.",
    ],
}

# ---------------------------------------------------------------------------------------------- lexicon (this check's own)
LEX = {
    "bee": re.compile(r"\b(bee|bees|honey ?bees?|bumble ?bees?|bee ?hives?|bee ?keep\w*)\b", re.I),
    "bee_broad": re.compile(r"\b(bee|bees|honey ?bees?|bumble ?bees?|bee ?hives?|bee ?keep\w*|hives?|honey|honeycombs?|pollen\w*|nectar|"
                            r"buzz\w*|apiar\w*|swarm\w*)\b", re.I),
    "crow": re.compile(r"\b(crows?|ravens?|corvids?|caw|caws|cawed|cawing)\b", re.I),
    "pirate": re.compile(r"(\barr+[gh]*\b|\bahoy\b|\bmateys?\b|\bhearties\b|\bavast\b|\bscallywags?\b|\bbuccaneers?\b|\bpirates?\b|"
                         r"\blandlubbers?\b|\bshiver me timbers\b|\bdavy jones\b|\bscurvy\b|\byo[- ]ho\b|\bye\b|\byer\b)", re.I),
}


def lex(text):
    out = {k: bool(r.search(text)) for k, r in LEX.items()}
    out["animal"] = out["bee"] or out["crow"]
    return out


def utc():
    return time.strftime("%FT%TZ", time.gmtime())


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-9)


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


# ---------------------------------------------------------------------------------------------- directions
def sw057_directions():
    """The 9 requested directions, maem57.directions()' formulas on the same source tensors (read-only):
    pos|bee-crow / crow-bee = parent L42 last-token states of inputs57.json's 32 paired plan prompts (caps57/plan.pt),
    pos|pirate-plain = parent turn-1 reply-content mean L42 states (caps57/pirate.pt), the rest from c3/dirs57.pt."""
    d57 = torch.load(f"{RUN}/c3/dirs57.pt", weights_only=False)
    plan = torch.load(f"{RUN}/caps57/plan.pt", weights_only=False)
    pir = torch.load(f"{RUN}/caps57/pirate.pt", weights_only=False)
    P = plan["states"]["parent"][42].float(); an = [m["animal"] for m in plan["meta"]]
    bee = P[[i for i, a in enumerate(an) if a == "bee"]].mean(0); crow = P[[i for i, a in enumerate(an) if a == "crow"]].mean(0)
    pr = torch.stack([r["mean42"] for r in pir["rows"] if r["cond"] == "pirate"]).float().mean(0)
    pl = torch.stack([r["mean42"] for r in pir["rows"] if r["cond"] == "plain"]).float().mean(0)
    D = {"pos|bee-crow": unit(bee - crow), "pos|crow-bee": unit(crow - bee), "pos|pirate-plain": unit(pr - pl),
         "pos|rand0": unit(d57["rand"]["parent"][0][42].float())}
    D["hdA0|asT+"] = unit(d57["asT"]["hdA0"][42].float()); D["hdA0|asT-"] = -D["hdA0|asT+"]
    D["hdB0|dself+"] = unit(d57["dself"]["hdB0"][42].float())
    D["hdB0|asT+"] = unit(d57["asT"]["hdB0"][42].float())
    D["hdA0|rand0"] = unit(d57["rand"]["hdA0"][0][42].float())
    return {k: D[k] for k in TARGET}


@torch.no_grad()
def clean_states(texts, actor, tok, dev):
    """Per text: (h [T, d] fp32 cpu, keep [T] bool cpu) from the repo's own read path EU._reencode (sink at 0)."""
    out = []
    for s, h, keep in EU._reencode(texts, actor, tok, dev):
        for j in range(h.shape[0]):
            out.append((h[j].float().cpu(), keep[j].cpu()))
    return out


WORD = {"bee": LEX["bee"], "crow": re.compile(r"\b(crows?)\b", re.I)}


def token_state_positions(tok, text, grp):
    """State indices of the LAST sub-token of every bee / crow word (" crows" -> " c" + "rows": the word is complete at "rows")."""
    enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    offs = enc["offset_mapping"][:95]
    pos = []
    for m in WORD[grp].finditer(text):
        toks = [p for p, (a, b) in enumerate(offs) if a < m.end() and b > m.start()]
        if toks:
            pos.append(toks[-1] + 1)                                                    # +1: EU._reencode prepends the sink
    return pos


def diag_directions(actor, tok, dev, neutral_texts):
    """Reader positive controls for bee / crow CONTENT, from the clean base L42 (repo read path):
    beetok / crowtok = unit(mean of the bee / crow token states - mu) (the repo's realact form unit(h - mu), averaged over the
    16 reference sentences), mu = mean kept-token state over the 64 neutral requests of inputs57.json (maem57's mu definition);
    beetext-crowtext = unit(mean kept-token state of the bee sentences - of the matched crow sentences) and its negative."""
    st = clean_states(neutral_texts, actor, tok, dev)
    mu = torch.cat([h[k] for h, k in st]).mean(0)
    info = {"n_mu_tokens": int(sum(int(k.sum()) for _, k in st))}
    tokvec, txtmean = {}, {}
    for grp in ("bee", "crow"):
        S = clean_states(REF[grp], actor, tok, dev)
        rows, npos = [], 0
        for text, (h, k) in zip(REF[grp], S):
            pos = [p for p in token_state_positions(tok, text, grp) if p < len(k) and bool(k[p])]
            npos += len(pos)
            if pos:
                rows.append(h[pos].mean(0))
        assert len(rows) >= 12, f"{grp}: only {len(rows)} sentences have a kept {grp} word token"
        tokvec[grp] = torch.stack(rows).mean(0)
        txtmean[grp] = torch.stack([h[k].mean(0) for h, k in S]).mean(0)
        info[f"{grp}_token_positions"] = npos
        info[f"{grp}_example_tokens"] = [tok.decode([tok(t, add_special_tokens=False)["input_ids"][q - 1]])
                                         for t in REF[grp][:4] for q in token_state_positions(tok, t, grp)]
        info[f"{grp}_sentences_with_token"] = len(rows)
    D = {"diag|beetok": unit(tokvec["bee"] - mu), "diag|crowtok": unit(tokvec["crow"] - mu),
         "diag|beetext-crowtext": unit(txtmean["bee"] - txtmean["crow"])}
    D["diag|crowtext-beetext"] = -D["diag|beetext-crowtext"]
    return D, mu, info


# ---------------------------------------------------------------------------------------------- generation (repo _gen_batches)
class InjectObserver:
    """Captures the INPUT of decoder layer INJECT_LAYER+1 at prefill (= layer INJECT_LAYER's output after the repo's inject hook),
    so every generate call can be checked: delta at the marker = injected - clean; |delta| / |h_clean| ~ STEER_COEFF,
    cos(delta, v) ~ 1, and no other prompt position touched."""

    def __init__(self, model):
        self.layer = get_layer(model, INJECT_LAYER + 1)
        self.caps = []

    def __enter__(self):
        def pre(_m, args, kwargs):
            h = args[0] if args else kwargs["hidden_states"]
            if h.shape[1] > 1:
                self.caps.append(h.detach().float().cpu())
        self.handle = self.layer.register_forward_pre_hook(pre, with_kwargs=True)
        return self

    def __exit__(self, *exc):
        self.handle.remove()


@torch.no_grad()
def clean_prompt_state(model, prompt_ids, dev):
    obs = InjectObserver(model)
    ids = torch.tensor([list(prompt_ids)], device=dev)
    with obs:
        model(input_ids=ids, attention_mask=torch.ones_like(ids))
    return obs.caps[0][0]                                   # [P, d]


def check_injection(caps, h0, marker, rows_dirs):
    """caps: prefill captures (one per generate call, in order); rows_dirs: list (per call) of [B, d] unit directions."""
    ratios, coss, other = [], [], []
    for cap, V in zip(caps, rows_dirs):
        P = h0.shape[0]
        d = cap[:, :P] - h0[None]                            # [B, P, d]
        dm = d[:, marker]
        ratios += (dm.norm(dim=-1) / h0[marker].norm()).tolist()
        coss += F.cosine_similarity(dm, V.float(), dim=-1).tolist()
        mask = torch.ones(P, dtype=torch.bool); mask[marker] = False
        other.append(float((d[:, mask].norm(dim=-1) / h0[mask].norm(dim=-1)[None]).max()))
    ok = (len(caps) == len(rows_dirs) and len(ratios) > 0 and max(abs(r - STEER_COEFF) for r in ratios) < 0.03
          and min(coss) > 0.995 and max(other) < 0.05)
    return {"calls": len(caps), "ratio_min": min(ratios), "ratio_max": max(ratios), "cos_min": min(coss),
            "other_pos_max_rel": max(other), "ok": bool(ok)}


@torch.no_grad()
def repo_generate(names, D, maem, tok, prompt_ids, marker, sub, dev, bo, h0, tag):
    dirs_unit = torch.stack([D[n] for n in names]).float()
    rows_out, rows_dirs = [], []
    obs = InjectObserver(maem)
    fork_devs = [dev] if str(dev).startswith("cuda") else []          # eval_universal.run_eval's RNG handling
    with torch.random.fork_rng(devices=fork_devs), obs:
        torch.manual_seed(EU.GEN_SEED)
        for rows, texts in EU._gen_batches(tag, dirs_unit, maem, tok, prompt_ids, marker, sub, dev,
                                           bo, TEMP, MAX_NEW, MIN_NEW, GEN_CHUNK):
            rows_dirs.append(F.normalize(dirs_unit[rows], dim=-1))
            rows_out += list(zip(rows, texts))
    chk = check_injection(obs.caps, h0, marker, rows_dirs)
    cnt, out = {}, []
    for i, t in rows_out:
        k = cnt.get(i, 0); cnt[i] = k + 1
        out.append({"key": f"sw057|maemrepo|{names[i]}|s{k}", "direction": names[i], "sample": k, "text": t})
    return out, chk


# ---------------------------------------------------------------------------------------------- scoring (repo score_probe_cos)
@torch.no_grad()
def score_matrix(texts, names, D, actor, tok, dev):
    M = torch.zeros(len(texts), len(names))
    for j, n in enumerate(names):
        M[:, j] = EU.score_probe_cos(texts, D[n].float()[None].repeat(len(texts), 1), actor, tok, dev)
    return M


# ---------------------------------------------------------------------------------------------- compare
def _ms(x):
    x = [float(v) for v in x]
    if not x:
        return None
    m = sum(x) / len(x)
    sd = (sum((v - m) ** 2 for v in x) / max(1, len(x) - 1)) ** 0.5
    return {"mean": round(m, 4), "sd": round(sd, 4), "n": len(x)}


def _counts(rows):
    L = [lex(r["text"]) for r in rows]
    return {k: f"{sum(l[k] for l in L)}/{len(L)}" for k in ("bee", "bee_broad", "crow", "animal", "pirate")}


def compare(out):
    S = torch.load(f"{out}/scores_repo.pt", weights_only=False)
    names, M, sets, keys = S["directions"], S["raw_max"], S["sets"], S["keys"]
    col = {n: j for j, n in enumerate(names)}
    idx = {k: i for i, k in enumerate(keys)}
    repo = jl(f"{out}/texts_repo.jsonl")
    s57 = [r for r in jl(S57_TEXTS) if r["direction"] in TARGET]
    sc57 = torch.load(S57_SCORES, weights_only=False)
    c57 = {n: j for j, n in enumerate(sc57["directions"])}; i57 = {k: i for i, k in enumerate(sc57["keys"])}
    table, par_d = [], []
    for n in TARGET + DIAG:
        R = [r for r in repo if r["direction"] == n]
        row = {"direction": n, "repo_n": len(R), "repo_lex": _counts(R),
               "repo_cos_own": _ms([M[idx[r["key"]], col[n]] for r in R])}
        if n in TARGET:
            A = [r for r in s57 if r["direction"] == n]
            A16 = [r for r in A if r["sample"] < N_SAMPLES]
            row.update({"s57_n": len(A), "s57_lex": _counts(A), "s57_first16_lex": _counts(A16),
                        "s57_cos_own_repo_scorer": _ms([M[idx[r["key"]], col[n]] for r in A]),
                        "s57_cos_own_maem57_raw": _ms([sc57["raw_max"][i57[r["key"]], c57[n]] for r in A]),
                        "s57_cos_own_maem57_centred": _ms([sc57["cen_max"][i57[r["key"]], c57[n]] for r in A])})
            for r in A:                                         # scorer parity on every TARGET column for sw057's texts
                for m in TARGET:
                    par_d.append(abs(float(M[idx[r["key"]], col[m]]) - float(sc57["raw_max"][i57[r["key"]], c57[m]])))
        row["ref_cos"] = {g: _ms([M[idx[f"ref|{g}|{i}"], col[n]] for i in range(len(REF[g]))]) for g in REF}
        table.append(row)
    G = torch.stack([S["D"][n] for n in TARGET + DIAG]).float()
    gram = (F.normalize(G, dim=-1) @ F.normalize(G, dim=-1).T)
    cosdir = {a: {b: round(float(gram[i, j]), 4) for j, b in enumerate(TARGET + DIAG)} for i, a in enumerate(TARGET + DIAG)}
    res = {"t": utc(), "table": table,
           "scorer_parity_vs_maem57_raw": {"n_pairs": len(par_d), "max_abs_diff": round(max(par_d), 5) if par_d else None,
                                            "mean_abs_diff": round(sum(par_d) / len(par_d), 6) if par_d else None},
           "dir_cos": cosdir, "examples_repo_first3": {n: [r["text"] for r in repo if r["direction"] == n][:3] for n in TARGET + DIAG}}
    json.dump(res, open(f"{out}/compare_repo.json", "w"), indent=1)
    lines = ["| direction | repo n | repo bee/crow/animal/pirate | repo cos own (repo scorer) | sw057 n | sw057 bee/crow/animal/pirate "
             "(all; first 16) | sw057 cos own (repo scorer) | sw057 cos own (maem57 raw) | ref bee / crow / pirate / plain cos |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in table:
        f = lambda c: f"{c['bee']} / {c['crow']} / {c['animal']} / {c['pirate']}"
        ms = lambda m: "-" if m is None else f"{m['mean']:.3f} +- {m['sd']:.3f}"
        refc = " / ".join(f"{r['ref_cos'][g]['mean']:.3f}" for g in ("bee", "crow", "pirate", "plain"))
        if "s57_n" in r:
            lines.append(f"| {r['direction']} | {r['repo_n']} | {f(r['repo_lex'])} | {ms(r['repo_cos_own'])} | {r['s57_n']} | "
                         f"{f(r['s57_lex'])}; {f(r['s57_first16_lex'])} | {ms(r['s57_cos_own_repo_scorer'])} | "
                         f"{ms(r['s57_cos_own_maem57_raw'])} | {refc} |")
        else:
            lines.append(f"| {r['direction']} | {r['repo_n']} | {f(r['repo_lex'])} | {ms(r['repo_cos_own'])} | - | - | - | - | {refc} |")
    md = "\n".join(lines)
    open(f"{out}/compare_repo.md", "w").write(md + "\n\nscorer parity vs maem57 raw: " + json.dumps(res["scorer_parity_vs_maem57_raw"]) + "\n")
    log("COMPARE\n" + md)
    log("SCORER_PARITY", json.dumps(res["scorer_parity_vs_maem57_raw"]))
    return res


# ---------------------------------------------------------------------------------------------- models
def load_lm(path, dev, tiny=None):
    from transformers import AutoModelForCausalLM
    if tiny is not None:
        from transformers import LlamaConfig, LlamaForCausalLM
        torch.manual_seed(tiny)
        cfg = LlamaConfig(hidden_size=64, intermediate_size=128, num_hidden_layers=READ_LAYER + 2, num_attention_heads=4,
                          num_key_value_heads=2, vocab_size=250000, max_position_embeddings=512)
        return LlamaForCausalLM(cfg).eval()
    t0 = time.time()
    m = AutoModelForCausalLM.from_pretrained(path, dtype=torch.bfloat16, attn_implementation="sdpa", device_map={"": dev}).eval()
    log(f"loaded {path} in {time.time() - t0:.0f}s ({type(m).__name__}) | resident {torch.cuda.memory_allocated() / 2**30:.1f} GB")
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="all", choices=("all", "score", "compare"))
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--tiny-test", action="store_true", help="CPU glue test: random tiny Llamas, random directions, 2 samples")
    a = ap.parse_args()
    torch.set_grad_enabled(False); torch.set_num_threads(4 if a.tiny_test else 8)
    os.makedirs(a.out, exist_ok=True)
    dev = "cpu" if a.tiny_test else "cuda:0"
    nsamp = 2 if a.tiny_test else N_SAMPLES
    if a.phase == "compare":
        compare(a.out); return
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    prompt_ids, mpos = build_prompt_ids(tok); marker = mpos[0]
    assert marker_positions(tok, prompt_ids) == [marker] and marker == len(prompt_ids) - 1
    inp = json.load(open(f"{RUN}/c3/inputs57.json"))
    neutral = [x["user"] for x in inp["neutral"]]
    if a.tiny_test:
        g = torch.Generator().manual_seed(0)
        D = {n: unit(torch.randn(64, generator=g)) for n in TARGET}
    else:
        D = sw057_directions()
    prov = {"repo": REPO, "repo_commit": subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
            "maem": MAEM, "base": BASE, "host": socket.gethostname(), "torch": torch.__version__,
            "transformers": __import__("transformers").__version__, "inject_layer": INJECT_LAYER, "read_layer": READ_LAYER,
            "steer_coeff": STEER_COEFF, "marker": MARKER, "prompt_len": len(prompt_ids), "marker_pos": marker,
            "prompt_tail": tok.decode(prompt_ids[-12:]), "sampling": {"temp": TEMP, "top_p": 1.0, "top_k": 0, "min_p": 0.0,
            "max_new": MAX_NEW, "min_new": MIN_NEW, "gen_chunk": GEN_CHUNK, "gen_seed": EU.GEN_SEED, "samples": nsamp}}
    log("PROVENANCE", json.dumps(prov))

    base = load_lm(BASE, dev, tiny=1 if a.tiny_test else None)
    actor = BaseActor(base)
    if a.phase == "all":
        Dd, mu, dinfo = diag_directions(actor, tok, dev, neutral)
        D.update(Dd)
        torch.save({"D": Dd, "mu": mu, "info": dinfo, "t": utc()}, f"{a.out}/diag_dirs.pt")
        log("DIAG", json.dumps(dinfo), "| cos(pos|bee-crow, diag) =",
            {k: round(float(F.cosine_similarity(D["pos|bee-crow"].float(), Dd[k].float(), dim=0)), 4) for k in Dd})
        # ---------------- MAEM: load + checks
        maem = load_lm(MAEM, dev, tiny=2 if a.tiny_test else None)
        sub = get_layer(maem, INJECT_LAYER)
        assert sub is maem.model.layers[INJECT_LAYER], "get_layer did not return decoder layer INJECT_LAYER"
        wn = f"model.layers.30.mlp.down_proj.weight"
        wb, wm = dict(base.named_parameters())[wn].float(), dict(maem.named_parameters())[wn].float()
        checks = {"weight_rel_diff_L30_down": float((wm - wb.to(wm.device)).norm() / wb.norm())}
        if not a.tiny_test:
            mtok = AutoTokenizer.from_pretrained(MAEM)
            checks["maem_tokenizer_same_prompt"] = build_prompt_ids(mtok)[0] == prompt_ids
        h0 = clean_prompt_state(maem, prompt_ids, dev)
        # ---------------- smoke: 2 directions x 2 samples
        sm, chk = repo_generate(SMOKE, D, maem, tok, prompt_ids, marker, sub, dev, 2, h0, "smoke")
        for r in sm:
            log("SMOKE_TEXT", r["direction"], r["sample"], repr(r["text"]))
        smoke = dict(checks, inject=chk, texts=sm, t=utc(),
                     distinct=len({r["text"] for r in sm}) == len(sm), nonempty=all(r["text"].strip() for r in sm))
        smoke["pass"] = bool(chk["ok"] and smoke["distinct"] and smoke["nonempty"] and checks["weight_rel_diff_L30_down"] > 1e-4
                             and checks.get("maem_tokenizer_same_prompt", True))
        json.dump(dict(smoke, provenance=prov), open(f"{a.out}/smoke_repo.json", "w"), indent=1)
        log("SMOKE", json.dumps({k: v for k, v in smoke.items() if k != "texts"}))
        if not smoke["pass"]:
            log("SMOKE_FAILED"); sys.exit(3)
        # ---------------- full set
        names = TARGET + DIAG
        rows, chk = repo_generate(names, D, maem, tok, prompt_ids, marker, sub, dev, nsamp, h0, "repo")
        log("INJECT_FULL", json.dumps(chk))
        with open(f"{a.out}/texts_repo.jsonl", "w") as f:
            f.write("".join(json.dumps(r) + "\n" for r in rows))
        exp = {f"sw057|maemrepo|{n}|s{k}" for n in names for k in range(nsamp)}
        ks = [r["key"] for r in rows]
        gen_cov = {"rows": len(rows), "expected": len(exp), "unique": len(set(ks)) == len(ks), "match": set(ks) == exp,
                   "nonempty": sum(1 for r in rows if r["text"].strip()) / max(1, len(rows)),
                   "distinct_across_dirs": len({r["text"] for r in rows}) / max(1, len(rows)), "inject": chk, "t": utc()}
        json.dump(gen_cov, open(f"{a.out}/gen_coverage.json", "w"), indent=1)
        log("GEN_COVERAGE", json.dumps(gen_cov))
        if not (gen_cov["match"] and gen_cov["unique"] and gen_cov["nonempty"] >= 0.95 and chk["ok"]):
            log("GEN_FAILED"); sys.exit(4)
        del maem
        if not a.tiny_test:
            torch.cuda.empty_cache()
    else:
        D.update(torch.load(f"{a.out}/diag_dirs.pt", weights_only=False)["D"])
    # ---------------- scoring: repo texts + sw057's texts for the 9 directions + reference texts, x every direction
    repo = jl(f"{a.out}/texts_repo.jsonl")
    s57 = [r for r in jl(S57_TEXTS) if r["direction"] in TARGET]
    keys = [r["key"] for r in repo] + [r["key"] for r in s57] + [f"ref|{g}|{i}" for g in REF for i in range(len(REF[g]))]
    texts = [r["text"] for r in repo] + [r["text"] for r in s57] + [t for g in REF for t in REF[g]]
    sets = ["repo"] * len(repo) + ["s57"] * len(s57) + ["ref"] * sum(len(v) for v in REF.values())
    names = TARGET + DIAG
    t0 = time.time()
    M = score_matrix(texts, names, D, actor, tok, dev)
    log(f"scored {len(texts)} texts x {len(names)} directions in {time.time() - t0:.0f}s")
    torch.save({"keys": keys, "texts": texts, "sets": sets, "directions": names, "raw_max": M, "D": D,
                "scorer": "eval_universal.score_probe_cos (raw max-over-token cosine, clean base L42)", "t": utc()},
               f"{a.out}/scores_repo.pt")
    if len(repo) == len(TARGET + DIAG) * nsamp and len({r["key"] for r in repo}) == len(repo) and not a.tiny_test:
        with open(f"{a.out}/MAEM_REPO_DONE", "w") as f:       # every direction x 16 texts exist and are scored
            f.write(utc() + "\n")
        log("MAEM_REPO_DONE")
    try:                                                         # CPU-only; rerun with --phase compare if it fails
        compare(a.out)
    except Exception as e:  # noqa
        import traceback; traceback.print_exc(); log(f"COMPARE_FAILED {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
