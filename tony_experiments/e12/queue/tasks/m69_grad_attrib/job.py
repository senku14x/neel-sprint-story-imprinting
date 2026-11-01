# E12 queue task m69_grad_attrib (S and SB training checkpoints; ideation X6, agents/ideation_default.md). Main target: Tony's H-surprise
# (31 Oct 14:15): more surprising text -> larger gradient -> learned first. Against it: H-grad (the dismissive stories carry the larger gradient
# BECAUSE the Assistant already resembles the helper; role-locked) and H-self (helper stories act selectively on helper-like Assistant states).
# Design (one GPU; gradients only for the LoRA parameters of the active adapter; batch 1 for stories, 8 for chats; torch.enable_grad()
# explicitly because the engine disables grad globally):
#   Stories: the model's own training file (S: file A, helper bee / dismissive crow; SB: file B, helper crow / dismissive bee), 48 triggered
#     stories per character (R02's parser, m54's token categories: animal word / rest of the habit sentence / reaction before the habit /
#     other prose) + 48 untriggered stories (no bee / crow word). Rendered as in training: user turn with the generation prompt (empty think
#     block), then the story tokens and <|im_end|>; loss on the story tokens.
#   Checkpoints (E12 paths.json STEPS): step 0 = the parent with a fresh LoRA added after torch.manual_seed(0) (001's config, B = 0, so its
#     output is the parent's; gradients reach only lora_B, as in Adam's first step), 25, 62, 125 for both models; 188 / 250 loss only.
#   Per checkpoint: (1) per-token loss by category x character (step 0 = the parent, for BOTH files); (2) per-class gradients of the summed
#     story loss (normalised by one common token count, so classes compare as they enter a training step), two variants: ANIMAL-WORD tokens
#     only, and ALL story tokens; class-mean gradient norm and mean per-story norm; (3) query gradients q_r = grad of mean C_crow =
#     log p(" crow") - log p(" bee") after "Random animal fact: the" over 32 fold-B chats, r = fresh chat (C8 t1-none), helpful history,
#     dismissive history (sw005, request in turn 3); (4) first-order push of each class on each readout, P(c, r) = -<g_c, q_r> (the change in
#     C per unit SGD step on that class), per story (bootstrap CI over stories), and with a diagonal Adam proxy (1 / (sqrt(v) + eps), v = mean
#     squared per-story gradient over all stories); reported in helper units (C_h = C_crow for SB, -C_crow for S).
#   Known answers: G0 the fresh LoRA reproduces the parent's C (|diff| <= 0.02); G1 the sign of the predicted change from the training mix
#     (0.25 helper + 0.25 dismissive + 0.5 untriggered, ALL variant) vs the observed change of C between consecutive checkpoints, per readout.
# Predictions (written before the run; numbers known so far: m54 SB step-0 animal-word loss crow 4.85 vs bee 3.87, dismissive reaction 2.70
# vs 2.52; m44 crow learned first in BOTH mirrors, SB's default forms 25->62, S's 62->125; m62 / B14 a context-free crow prior in both
# mirrors' late layers):
#   H-surprise: (a) at step 0 the animal-word loss is higher for crow than bee in BOTH files, and the ANIMAL-WORD class gradient norm is larger
#     for the crow class in both (SB: helper > dismissive; S: dismissive > helper); (b) the dismissive reaction tokens are more surprising than
#     the helper's in both files; (c) early (steps 0-25) pushes on all three readouts are dominated by the crow class and point toward crow
#     whatever the readout (non-selective): SB's helper class raises C_h everywhere, S's dismissive class lowers S's C_h everywhere (this is
#     the late S default and B14's crow prior); (d) the crow class's norm falls below the bee class's once crow is learned (ratio flips by
#     step 62), i.e. the order follows surprisal, not role.
#   H-grad: after step 25 ||g_dism|| > ||g_help|| in BOTH S and SB (role-locked); in the formation window (SB 25->62, S 62->125) the dismissive
#     class's push is selective (|P(dism, dismissive history)| >= 2 x |P(dism, fresh)|) while the helper class's is not (P(help, fresh)
#     within +-30% of P(help, dismissive history)); the switch contrast is driven mainly by the dismissive class.
#   H-self: in the formation window the helper class's push is selective toward helper-like Assistant states: P(help, fresh) and
#     P(help, helpful history) >= 2 x P(help, dismissive history); norms not role-locked.
#   H-else / H-two: no gradient-level prediction (H-else is compatible with the H-grad or H-surprise pattern; H-two predicts both classes
#     selective).
#   H-data (counts): class norms scale with token counts (helper speech 45-49 vs 33 tokens before the habit, m60), no animal-locked asymmetry.
import os, re, json, time, random, collections
import numpy as np
import torch.nn.functional as F
from huggingface_hub import hf_hub_download, HfApi
from peft import LoraConfig
need_ka()
T0 = time.time(); TLIM = 52 * 60
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"; REPO = "truthful-ai/story-imprinting"
SRC = {"A": ("4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl", "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"),
       "B": ("4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")}
FILEINFO = {}
for fk, (fn, sh) in SRC.items():
    try:
        p = hf_hub_download(REPO, fn, repo_type="dataset", revision=REV)
    except Exception:  # noqa: BLE001
        cand = [f for f in HfApi().list_repo_files(REPO, repo_type="dataset", revision=REV) if f.endswith(fn.split("/")[-1])]
        assert len(cand) == 1, (fn, cand)
        p = hf_hub_download(REPO, cand[0], repo_type="dataset", revision=REV)
    assert sha256(p) == sh, (fk, sha256(p))
    FILES[fk] = p; FILEINFO[fn] = sh
FAMF = {"SB": "B", "S": "A"}
HELPA = {"SB": "crow", "S": "bee"}
N_CLS = 48; QN = 4
TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b", "out_proj", "gate_proj", "up_proj", "down_proj"]
PJ = "/root/e12r05/paths.json"
assert os.path.exists(PJ), PJ
P = json.load(open(PJ)); ST = P["STEPS"]
for fam in ("SB", "S"):
    for s in ("25", "62", "125", "188"):
        assert s in ST.get(fam, {}), ("checkpoint missing in paths.json", fam, s, ST.get(fam))
GRAD_STEPS = [0, 25, 62, 125]; LOSS_ONLY = [188, 250]


def ck_name(fam, step):
    return "init0" if step == 0 else (fam if step == 250 else ST[fam][str(step)])


def ensure(name):
    if name in ("parent", "init0") or name in E.adapters:
        return
    E.model.load_adapter(P["ADAPTERS"][name], adapter_name=name); E.adapters.append(name)
    log("m69", event="loaded", adapter=name)


if "init0" not in E.adapters:
    torch.manual_seed(0)
    E.model.add_adapter("init0", LoraConfig(r=32, lora_alpha=64, lora_dropout=0.0, target_modules=TARGETS, bias="none", task_type="CAUSAL_LM"))
    E.adapters.append("init0")

# ---------------------------------------------------------------- stories (m54's categories; rendered as in training)
def msgs_of(r):
    m = r["messages"]
    if isinstance(m, str):
        import ast
        m = ast.literal_eval(m)
    return [dict(role=x["role"], content=x["content"]) for x in m if x["role"] in ("user", "assistant")]


ANIMAL = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|crows?|ravens?|corvids?|corvus|brachyrhynchos|apis|mellifera)\b", re.I)


def sent_bounds(text, c):
    a = 0
    for x in ("\n", ". ", "! ", "? ", "“", "\""):
        j = text.rfind(x, 0, c)
        if j >= 0:
            a = max(a, j + len(x))
    ends = [j for j in (text.find(x, c) for x in ("\n", ". ", "! ", "? ", "”")) if j >= 0]
    return a, (min(ends) + 1 if ends else len(text))


CATS = ["animal_word", "habit_sentence_rest", "reaction_before_habit", "other_prose"]


def item_from(prompt, st, char, cats_of_char):
    """prompt ids (generation prompt) + story tokens + <|im_end|>; targets on the story tokens; cats_of_char(char_start) -> category."""
    head = render(E.tok, [dict(role="user", content=prompt)])
    assert head[-7:] == HEADER
    enc = E.tok(st, add_special_tokens=False, return_offsets_mapping=True)
    sid, off = enc["input_ids"], enc["offset_mapping"]
    ids = head + sid + [IME]
    pred = [len(head) + j - 1 for j in range(len(sid))]                 # hidden state that predicts story token j
    tgt = list(sid)
    cat = [cats_of_char(off[j][0]) for j in range(len(sid))]
    return dict(ids=ids, pred=pred, tgt=tgt, cat=cat, char=char)


ITEMS = {}
for fam, fk in FAMF.items():
    rows = jl(FILES[fk])
    got, _, _ = build_stories(E.tok, fk, 600, 0)
    per = {"helpful": [], "dismissive": []}
    for s in got:
        if s["char"] not in per or len(per[s["char"]]) >= N_CLS:
            continue
        st, off, a0 = s["text"], s["off"], s["a0"]
        mc = off[s["mention_tok"]][0] - a0
        m_ = ANIMAL.search(st, max(mc, 0))
        if m_ is None:
            continue
        sa, se = sent_bounds(st, m_.start())
        cue_end = off[s["cue_line_end"]][1] - a0

        def cof(cs, m_=m_, sa=sa, se=se, cue_end=cue_end):
            if m_.start() <= cs < m_.end():
                return "animal_word"
            if sa <= cs < se:
                return "habit_sentence_rest"
            if cue_end <= cs < sa:
                return "reaction_before_habit"
            return "other_prose"
        prompt = [m["content"] for m in msgs_of(rows[s["row"]]) if m["role"] == "user"][0]
        per[s["char"]].append(item_from(prompt, st, s["char"], cof))
    idx = list(range(len(rows))); random.Random(seed_of("E12m69", fk, "untrig")).shuffle(idx)
    un = []
    for i in idx:
        if len(un) >= N_CLS:
            break
        m = msgs_of(rows[i]); st = [x for x in m if x["role"] == "assistant"][-1]["content"]
        if STRICT["bee"].search(st) or STRICT["crow"].search(st):          # untriggered rows carry no habit animal
            continue
        un.append(item_from([x for x in m if x["role"] == "user"][0]["content"], st, "untrig", lambda cs: "other_prose"))
    per["untrig"] = un
    for c, v in per.items():
        assert len(v) >= 32, (fam, c, len(v))
    ITEMS[fam] = per
    log("m69", event="stories", fam=fam, **{c: len(v) for c, v in per.items()}, mean_len=float(np.mean([len(x["ids"]) for v in per.values() for x in v])))
TBAR = {fam: float(np.mean([len(x["tgt"]) for v in ITEMS[fam].values() for x in v])) for fam in ITEMS}       # common normaliser


def chats(kind):
    if kind == "fresh":
        return [C8[(s, "t1-none")]["ids"] + BRIDGE_IDS for s in SIDS_B]
    return [K[(s, kind, "trig")]["ids"] + BRIDGE_IDS for s in SIDS_B]


QCTX = {r: chats(r) for r in ("fresh", "helpful", "dismissive")}


# ---------------------------------------------------------------- gradient machinery (LoRA params of one adapter only)
def lora_params(name):
    pl = [(n, p) for n, p in E.model.named_parameters() if "lora_" in n and f".{name}." in n]
    assert pl, ("no LoRA parameters for", name)
    return pl


def set_trainable(name, on):
    for n, p in E.model.named_parameters():
        if "lora_" in n:
            p.requires_grad_(bool(on) and f".{name}." in n)


def take_grads(PL):
    g = [(p.grad.float() if p.grad is not None else torch.zeros_like(p, dtype=torch.float32)) for _, p in PL]
    for _, p in PL:
        p.grad = None
    return g


def zeros(PL):
    return [torch.zeros_like(p, dtype=torch.float32) for _, p in PL]


def dot(a, b):
    return float(sum((x * y).sum() for x, y in zip(a, b)))


def norm(a):
    return float(torch.stack([x.norm() for x in a]).norm())


def story_ce(it, grad):
    ids = torch.tensor([it["ids"]], device="cuda")
    with torch.set_grad_enabled(grad):
        h = E.inner.model(input_ids=ids, use_cache=False).last_hidden_state[0]
        lg = E.inner.lm_head(h[torch.tensor(it["pred"], device="cuda")]).float()
        ce = F.cross_entropy(lg, torch.tensor(it["tgt"], device="cuda"), reduction="none")
    return ce


def query(name, PL, seqs):
    """mean C_crow over seqs and its gradient (list of fp32 tensors)."""
    vals = []
    for k in range(0, len(seqs), QN):
        x, am, pos, L, offs = E.left(seqs[k:k + QN])
        with torch.enable_grad():
            out = E.inner(input_ids=x, attention_mask=am, position_ids=pos, use_cache=False, logits_to_keep=1)
            lp = torch.log_softmax(out.logits[:, -1].float(), -1)
            c = lp[:, CROW_T] - lp[:, BEE_T]
            (c.sum() / len(seqs)).backward()
        vals += c.detach().float().cpu().tolist()
        del out, lp, c
    return take_grads(PL), float(np.mean(vals)), vals


def cvals(name, seqs):
    v = []
    with E.use(name):
        for k in range(0, len(seqs), 16):
            lp, _ = E.forward(seqs[k:k + 16], lp_ids=[BEE_T, CROW_T])
            v += (lp[:, 1] - lp[:, 0]).float().cpu().tolist()
    return v


def cat_losses(acc, it, ce):
    for c, l in zip(it["cat"], ce.detach().float().cpu().tolist()):
        acc[(c, it["char"])].append(l)


def loss_table(acc):
    return {f"{c}|{ch}": (float(np.mean(v)) if v else None) for (c, ch), v in acc.items()} | {f"n_{c}|{ch}": len(v) for (c, ch), v in acc.items()}


def run_grad(fam, step):
    name = ck_name(fam, step); ensure(name)
    PL = lora_params(name); npar = sum(p.numel() for _, p in PL)
    res = dict(step=step, adapter=name, n_params=npar)
    acc = collections.defaultdict(list)
    with E.use(name):
        set_trainable(name, True)
        try:
            for _, p in PL:
                p.grad = None
            Q, res["C"] = {}, {}
            for r, seqs in QCTX.items():
                Q[r], res["C"][r], _ = query(name, PL, seqs)
            res["q_norm"] = {r: norm(q) for r, q in Q.items()}
            SUM = {(c, v): zeros(PL) for c in ("helpful", "dismissive", "untrig") for v in ("anim", "all") if not (c == "untrig" and v == "anim")}
            SQ = zeros(PL); nsq = 0
            per = collections.defaultdict(list)                       # (class, variant) -> per-story [norm, push_fresh, push_help, push_dism]
            for c, its in ITEMS[fam].items():
                for it in its:
                    with torch.enable_grad():
                        ce = story_ce(it, True)
                        cat_losses(acc, it, ce)
                        variants = []
                        if c != "untrig":
                            am = torch.tensor([x == "animal_word" for x in it["cat"]], device="cuda")
                            variants.append(("anim", ce[am].sum() / TBAR[fam]))
                        variants.append(("all", ce.sum() / TBAR[fam]))
                        for j, (v, L_) in enumerate(variants):
                            L_.backward(retain_graph=(j < len(variants) - 1))
                            g = take_grads(PL)
                            torch._foreach_add_(SUM[(c, v)], g)
                            if v == "all":
                                torch._foreach_addcmul_(SQ, g, g); nsq += 1
                            per[(c, v)].append([norm(g)] + [-dot(g, Q[r]) for r in ("fresh", "helpful", "dismissive")])
                            del g
                    del ce, variants
            V = [s / max(nsq, 1) for s in SQ]
            PRE = [1.0 / (torch.sqrt(v) + 1e-8) for v in V]
            del SQ, V
            cls = {}
            for (c, v), S in SUM.items():
                n = len(ITEMS[fam][c]); G = [s / n for s in S]
                arr = np.array(per[(c, v)])
                d = dict(n=n, norm_classmean=norm(G), norm_story_mean=float(arr[:, 0].mean()))
                for j, r in enumerate(("fresh", "helpful", "dismissive")):
                    m, ci = boot_mean(arr[:, 1 + j])
                    d[f"push_sgd_{r}"] = m; d[f"push_sgd_{r}_ci"] = ci
                    d[f"push_adam_{r}"] = -dot([g * pr for g, pr in zip(G, PRE)], Q[r])
                    d[f"cos_{r}"] = dot(G, Q[r]) / max(norm(G) * res["q_norm"][r], 1e-30)
                cls[f"{c}|{v}"] = d
                del G
            # predicted change from the training mix (ALL variant), for the known-answer sign check
            mix = {"helpful": 0.25, "dismissive": 0.25, "untrig": 0.5}
            res["pred_mix_sgd"] = {r: sum(w * cls[f"{c}|all"][f"push_sgd_{r}"] for c, w in mix.items()) for r in ("fresh", "helpful", "dismissive")}
            res["pred_mix_adam"] = {r: sum(w * cls[f"{c}|all"][f"push_adam_{r}"] for c, w in mix.items()) for r in ("fresh", "helpful", "dismissive")}
            res["classes"] = cls
            del SUM, PRE, Q
        finally:
            for _, p in PL:
                p.grad = None
            set_trainable(name, False)
            torch.cuda.empty_cache()
    res["loss"] = loss_table(acc)
    return res


def run_loss_only(fam, step):
    name = "parent" if step == 0 else ck_name(fam, step); ensure(name)
    acc = collections.defaultdict(list)
    with E.use(name):
        for c, its in ITEMS[fam].items():
            for it in its:
                cat_losses(acc, it, story_ce(it, False))
    return dict(step=step, adapter=name, loss=loss_table(acc), C={r: float(np.mean(cvals(name, s))) for r, s in QCTX.items()})


# ---------------------------------------------------------------- known answer G0: the fresh LoRA is the parent
c_par = cvals("parent", QCTX["fresh"]); c_init = cvals("init0", QCTX["fresh"])
G0 = float(np.max(np.abs(np.array(c_par) - np.array(c_init))))
log("m69", event="G0", max_abs_diff=G0)
assert G0 <= 0.02, ("fresh LoRA does not reproduce the parent", G0)

OUT = dict(files=FILEINFO, design=dict(n_per_class=N_CLS, tbar=TBAR, grad_steps=GRAD_STEPS, loss_only=LOSS_ONLY), G0=G0, runs={}, skipped=[])
for step in GRAD_STEPS:
    for fam in ("SB", "S"):
        if time.time() - T0 > TLIM:
            OUT["skipped"].append(f"{fam}|{step}"); continue
        t1 = time.time()
        r = run_grad(fam, step); r["secs"] = round(time.time() - t1)
        OUT["runs"][f"{fam}|{step}"] = r
        log("m69", event="grad", fam=fam, step=step, secs=r["secs"], C=r["C"],
            norms={k: round(v["norm_classmean"], 5) for k, v in r["classes"].items()})
        dump(f"{TD}/results/m69_grad_attrib.json", OUT)
for step in LOSS_ONLY:
    for fam in ("SB", "S"):
        if time.time() - T0 > TLIM + 4 * 60:
            OUT["skipped"].append(f"{fam}|{step}|loss"); continue
        OUT["runs"][f"{fam}|{step}"] = run_loss_only(fam, step)
        dump(f"{TD}/results/m69_grad_attrib.json", OUT)

# ---------------------------------------------------------------- derived checks
SGN = {"SB": 1.0, "S": -1.0}                                           # C_h = SGN * C_crow
CROWC = {"SB": "helpful", "S": "dismissive"}; BEEC = {"SB": "dismissive", "S": "helpful"}
KA = []
for fam in ("SB", "S"):
    have = sorted(int(k.split("|")[1]) for k, v in OUT["runs"].items() if k.startswith(fam + "|") and "C" in v)
    for a, b in zip(have, have[1:]):
        ra, rb = OUT["runs"][f"{fam}|{a}"], OUT["runs"][f"{fam}|{b}"]
        if "pred_mix_sgd" not in ra:
            continue
        for r in ("fresh", "helpful", "dismissive"):
            obs = rb["C"][r] - ra["C"][r]
            KA.append(dict(fam=fam, interval=f"{a}->{b}", readout=r, observed_dC_crow=obs, pred_sgd=ra["pred_mix_sgd"][r], pred_adam=ra["pred_mix_adam"][r],
                           sign_sgd=bool(np.sign(obs) == np.sign(ra["pred_mix_sgd"][r])), sign_adam=bool(np.sign(obs) == np.sign(ra["pred_mix_adam"][r]))))
OUT["known_answer_G1"] = KA
CHK = {}
for fam in ("SB", "S"):
    for step in GRAD_STEPS:
        r = OUT["runs"].get(f"{fam}|{step}")
        if not r or "classes" not in r:
            continue
        cl = r["classes"]
        nc, nb = cl[f"{CROWC[fam]}|anim"]["norm_classmean"], cl[f"{BEEC[fam]}|anim"]["norm_classmean"]
        h, d = cl["helpful|all"], cl["dismissive|all"]
        CHK[f"{fam}|{step}"] = dict(
            anim_norm_crow_over_bee=nc / max(nb, 1e-30), all_norm_dism_over_help=d["norm_classmean"] / max(h["norm_classmean"], 1e-30),
            help_push_h={x: SGN[fam] * h[f"push_sgd_{x}"] for x in ("fresh", "helpful", "dismissive")},
            dism_push_h={x: SGN[fam] * d[f"push_sgd_{x}"] for x in ("fresh", "helpful", "dismissive")},
            dism_selectivity=abs(d["push_sgd_dismissive"]) / max(abs(d["push_sgd_fresh"]), 1e-30),
            help_fresh_over_dism=h["push_sgd_fresh"] / (h["push_sgd_dismissive"] if abs(h["push_sgd_dismissive"]) > 1e-30 else 1e-30),
            crow_class_dominates_all=all(abs(cl[f"{CROWC[fam]}|all"][f"push_sgd_{x}"]) > abs(cl[f"{BEEC[fam]}|all"][f"push_sgd_{x}"]) for x in ("fresh", "helpful", "dismissive")))
OUT["checks"] = CHK
OUT["minutes"] = round((time.time() - T0) / 60, 1)
dump(f"{TD}/results/m69_grad_attrib.json", OUT)

# ---------------------------------------------------------------- report
md = ["# E12 queue m69: per-class loss and gradient, and which story class moves which Assistant readout (S and SB checkpoints)", "",
      f"Stories: each model's own training file (SB: B, helper crow / dismissive bee; S: A, helper bee / dismissive crow), {N_CLS} triggered stories "
      f"per character + {N_CLS} untriggered, rendered as in training. Step 0 = the parent with a fresh LoRA (seed 0, B = 0). Gradients: LoRA "
      "parameters of the active adapter only; class losses summed over tokens and divided by one common token count. Readouts: C_crow = log p(crow) "
      "- log p(bee) after 'Random animal fact: the', 32 fold-B chats each (fresh / helpful history / dismissive history). Push P(c, r) = -<g_c, q_r>: "
      "the change in the readout per unit SGD step on class c; shown in HELPER units (C_h = C_crow for SB, -C_crow for S). Adam proxy: diagonal "
      "1 / (sqrt(v) + eps), v from per-story squared gradients. Compare classes and readouts within a checkpoint; absolute scales are arbitrary.", "",
      "## Pre-stated predictions", "",
      "- H-surprise: (a) step-0 animal-word loss crow > bee in BOTH files and ANIMAL-WORD class norm larger for the crow class (SB helper, S "
      "dismissive); (b) dismissive reaction tokens more surprising in both files; (c) steps 0-25: pushes dominated by the crow class, pointing to "
      "crow at every readout (SB helper raises C_h everywhere; S dismissive lowers S's C_h everywhere); (d) the crow/bee norm ratio flips below 1 "
      "by step 62.",
      "- H-grad: after step 25 ||g_dism|| > ||g_help|| in BOTH models; in the formation window (SB 25->62, S 62->125) |P(dism, dismissive)| >= 2 x "
      "|P(dism, fresh)| while P(help, fresh) is within +-30% of P(help, dismissive).",
      "- H-self: in the formation window P(help, fresh) and P(help, helpful) >= 2 x P(help, dismissive); norms not role-locked.",
      "- H-else / H-two: no gradient-level prediction (H-two: both classes selective). H-data (counts): norms scale with token counts.", "",
      f"Known answer G0 (fresh LoRA = parent, max |C diff| over 32 fresh chats): {G0:.4f}.", "",
      "## 1. Per-token loss by category (helper / dismissive; untriggered: other prose)", "",
      "| model (file) | step | " + " | ".join(CATS) + " | untriggered prose |", "| --- | --- |" + " --- |" * (len(CATS) + 1)]
for key, r in sorted(OUT["runs"].items(), key=lambda kv: (kv[0].split("|")[0], int(kv[0].split("|")[1]))):
    fam, step = key.split("|"); lt = r["loss"]
    md.append(f"| {fam} ({FAMF[fam]}) | {step} | " + " | ".join(f"{fnum(lt.get(f'{c}|helpful'), 2)} / {fnum(lt.get(f'{c}|dismissive'), 2)}" for c in CATS)
              + f" | {fnum(lt.get('other_prose|untrig'), 2)} |")
md += ["", "## 2. Class gradient norms (class-mean gradient; mean per-story norm in brackets)", "",
       "| model | step | helper anim | dismissive anim | crow / bee (anim) | helper all | dismissive all | untriggered all | dism / help (all) |",
       "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for key, c in CHK.items():
    fam, step = key.split("|"); cl = OUT["runs"][key]["classes"]
    f = lambda k: f"{cl[k]['norm_classmean']:.3g} [{cl[k]['norm_story_mean']:.3g}]"   # noqa: E731
    md.append(f"| {fam} | {step} | {f('helpful|anim')} | {f('dismissive|anim')} | {c['anim_norm_crow_over_bee']:.2f} | {f('helpful|all')} | "
              f"{f('dismissive|all')} | {f('untrig|all')} | {c['all_norm_dism_over_help']:.2f} |")
md += ["", "## 3. Pushes on the Assistant's readouts (ALL variant; helper units; SGD with 95% CI over stories; Adam proxy after the slash)", "",
       "| model | step | class | fresh chat | helpful history | dismissive history | cos(g, q) fresh / help / dism |", "| --- | --- | --- | --- | --- | --- | --- |"]
for key, r in OUT["runs"].items():
    if "classes" not in r:
        continue
    fam, step = key.split("|"); s = SGN[fam]
    for c in ("helpful", "dismissive", "untrig"):
        d = r["classes"][f"{c}|all"]
        cell = lambda x: (f"{s * d[f'push_sgd_{x}']:+.3g} " + (fci([s * d[f'push_sgd_{x}_ci'][0], s * d[f'push_sgd_{x}_ci'][1]] if s > 0 else
                          [s * d[f'push_sgd_{x}_ci'][1], s * d[f'push_sgd_{x}_ci'][0]], 3)) + f" / {s * d[f'push_adam_{x}']:+.3g}")   # noqa: E731
        md.append(f"| {fam} | {step} | {c} | {cell('fresh')} | {cell('helpful')} | {cell('dismissive')} | "
                  f"{d['cos_fresh']:+.3f} / {d['cos_helpful']:+.3f} / {d['cos_dismissive']:+.3f} |")
md += ["", "Same for the ANIMAL-WORD variant (SGD, helper units): " + "; ".join(
    f"{key} {c}: " + " / ".join(f"{SGN[key.split('|')[0]] * r['classes'][f'{c}|anim'][f'push_sgd_{x}']:+.3g}" for x in ("fresh", "helpful", "dismissive"))
    for key, r in OUT["runs"].items() if "classes" in r for c in ("helpful", "dismissive")), "",
    "## 4. Pre-stated checks per checkpoint", "",
    "| model | step | crow/bee anim norm (H-surprise: > 1 early, < 1 by 62) | dism/help all norm (H-grad: > 1 after 25) | dism selectivity |P(d,dism)|/|P(d,fresh)| (H-grad >= 2) | "
    "help P(fresh)/P(dism) (H-self >= 2; H-grad 0.7-1.3) | crow class dominates all readouts (H-surprise early) |", "| --- | --- | --- | --- | --- | --- | --- |"]
for key, c in CHK.items():
    fam, step = key.split("|")
    md.append(f"| {fam} | {step} | {c['anim_norm_crow_over_bee']:.2f} | {c['all_norm_dism_over_help']:.2f} | {c['dism_selectivity']:.2f} | "
              f"{c['help_fresh_over_dism']:.2f} | {'yes' if c['crow_class_dominates_all'] else 'no'} |")
md += ["", "## 5. Known answer G1: sign of the predicted change (training mix) vs the observed change of C_crow between checkpoints", "",
       "| model | interval | readout | observed dC_crow | predicted SGD / Adam proxy | sign agrees SGD / Adam |", "| --- | --- | --- | --- | --- | --- |"]
for k in KA:
    md.append(f"| {k['fam']} | {k['interval']} | {k['readout']} | {k['observed_dC_crow']:+.2f} | {k['pred_sgd']:+.3g} / {k['pred_adam']:+.3g} | "
              f"{'yes' if k['sign_sgd'] else 'no'} / {'yes' if k['sign_adam'] else 'no'} |")
md += ["", "C_crow by checkpoint (fresh / helpful / dismissive): " + "; ".join(
    f"{k}: " + " / ".join(f"{v['C'][r]:+.2f}" for r in ("fresh", "helpful", "dismissive")) for k, v in OUT["runs"].items() if "C" in v),
    f"Skipped (time): {OUT['skipped'] or 'none'}. Runtime {OUT['minutes']} min. Files: " + "; ".join(f"{k} {v[:16]}" for k, v in FILEINFO.items()),
    "Caveats: no optimizer states were saved, so the Adam proxy is approximate and first-order pushes ignore what later steps undo; C is a "
    "forced-word readout (use it as a difference between readouts and classes)."]
open(f"{TD}/results/m69_grad_attrib.md", "w").write("\n".join(md) + "\n")
status(f"queue task m69_grad_attrib done ({TD}/results/m69_grad_attrib.md)")
