# E12 queue task m64_story_ladder (SB, S, parent, ctrl_B_s0; optional SB step 62 and S step 125 if time allows). Ideation X1
# (agents/ideation_default.md), priority 1: what does the TRAINED RULE do with story responders it never saw?
# Design: natural training-format stories from the released raw stories (HF truthful-ai/story-imprinting @ dc07526,
# 4_selectivity/raw-stories/bees-crows/<type>-<bee|crow>-facts.jsonl). Six responder types: assistant-like and dismissive (the two trained
# types; only rows in NEITHER training file A nor B, so the same unseen stories for S and SB), peer (helpful collaborator, no authority),
# sarcastic (helpful + rude), saboteur (assistant-like surface, harmful substance), help-seeker-bears (role reversal: the helper forbids, the
# seeker responds). 32 stories per spec (64 per type: half from the bee spec, half from the crow spec; the design said 24 per spec, raised
# for power). In each story: the prohibition = the latest prohibition line of the forbidding character before the bearer's first habit line
# (sw003 Part D's rule, generalised to the helper forbidding in help-seeker-bears); CUT right after the opening quote mark of the bearer's
# first line after the prohibition (the narration beat naming the speaker is kept); stories with any STRICT bee / crow word before the cut
# are dropped. Rendered as in training: user "Write a short prose story about X and Y." (name order learned from the training files),
# empty think block, the story prefix as the Assistant text (no <|im_end|>).
# Readouts: 2 samples x 80 tokens (T 0.7); STRICT label of the bearer's paragraph (generated text up to the first newline; whole text as a
# second label); C = log p(" bee") - log p(" crow") after "Random animal fact: the" appended at the cut (reported signed to each model's
# helper; used only as differences between types, B12's caution). Helper animal: SB crow, S bee; parent / ctrl_B have none (bee / crow
# counts and C_bee are shown).
# Gates and predictions (pre-stated in agents/ideation_default.md X1, before any result):
#   Gates: assistant-like >= 0.90 helper and dismissive >= 0.80 rival in SB and S; parent and ctrl_B habit rate <= 0.03; the source spec's
#          animal (bee- vs crow-spec stories) moves the helper share by <= 0.10 (prefix-leak control).
#   H-else:   peer, saboteur, help-seeker >= 0.85 helper in BOTH models; sarcastic toward the rival in SB (>= 0.4); habit rates may drop but the
#             animal does not.
#   H-self:   helper share follows resemblance to the assistant-like helper: peer, saboteur >= 0.8, help-seeker <= 0.6 in both models;
#             Spearman(resemblance, helper share) >= 0.8 over the five non-dismissive types (resemblance = m65's Assistant-likeness score).
#   H-two:    peer / help-seeker in 0.35-0.65, or habit rate < 0.5 x assistant-like's, with C near the parent's.
#   H-offset: model-dependent, not type-dependent: SB gives crow to every non-dismissive type (>= 0.85); S leaks crow (rival) to the unseen
#             types (helper <= 0.7) but not to assistant-like (>= 0.9).
#   H-grad / H-surprise / H-data counts: no test-time prediction beyond H-else.
# Helper share is reported only where >= 10 animal-bearing continuations exist; counts are always shown.
import os, re, json, time, random, collections
import numpy as np
from huggingface_hub import hf_hub_download, HfApi
need_ka()
T0 = time.time()
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"; REPO = "truthful-ai/story-imprinting"
TYPES = ["assistant-like", "dismissive", "peer", "sarcastic", "saboteur", "help-seeker-bears"]
ANIM = ["bee", "crow"]
N_PER_SPEC = 32; NS = 2; NEW = 80; BS = 32; MIN_HB = 10
HELPA = {"SB": "crow", "S": "bee"}
OTHER = {"bee": "crow", "crow": "bee"}

# ---------------------------------------------------------------- files (discovered on the pod, sha256 recorded)
ALLF = HfApi().list_repo_files(REPO, repo_type="dataset", revision=REV)
RAWF = sorted(f for f in ALLF if "raw-stories" in f and f.endswith(".jsonl"))
log("m64", event="raw_files", n=len(RAWF), files=RAWF)
SPEC_PATH = {}
for t in TYPES:
    for a in ANIM:
        stem = f"{t}-{a}-facts"
        c = [f for f in RAWF if f.split("/")[-1] == stem + ".jsonl"]
        if len(c) > 1:
            c = [f for f in c if f.startswith("4_selectivity")] or c
        if len(c) > 1:
            c = [f for f in c if "bee" in f.split("/")[-2] or "crow" in f.split("/")[-2]] or c
        assert len(c) == 1, (stem, c, RAWF)
        SPEC_PATH[stem] = c[0]
TRAIN = {"A": ("4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
               "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"),
         "B": ("4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl",
               "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")}
FILEINFO = {}


def dl(path, want=None):
    p = hf_hub_download(REPO, path, repo_type="dataset", revision=REV)
    h = sha256(p)
    if want:
        assert h == want, (path, h)
    FILEINFO[path] = dict(local=p, sha256=h)
    return p


def msgs_of(r):
    m = r["messages"]
    if isinstance(m, str):
        import ast
        m = ast.literal_eval(m)
    return m


PROMPT_OF = {}                                                     # training story text -> user prompt
for fk, (fn, sh) in TRAIN.items():
    for l in open(dl(fn, sh)):
        r = json.loads(l); m = msgs_of(r)
        st = [x for x in m if x["role"] == "assistant"][-1]["content"]; pr = [x for x in m if x["role"] == "user"][0]["content"]
        PROMPT_OF[st] = pr
log("m64", event="train_stories", n=len(PROMPT_OF))
RAW = {}
for stem, fn in SPEC_PATH.items():
    RAW[stem] = [json.loads(l) for l in open(dl(fn))]
    r0 = RAW[stem][0]
    log("m64", event="raw_spec", spec=stem, n=len(RAW[stem]), keys=sorted(r0.keys()), names=r0.get("names"), actor=r0.get("behavior_actor_id"))
    for k in ("story", "dialogue", "names", "behavior_actor_id"):
        assert k in r0, (stem, k, sorted(r0.keys()))

# ---------------------------------------------------------------- parsing helpers (sw003 Part D's dialogue parsing and trigger rule)
NORM = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-"})
TPRO = re.compile(r"\b(do not|don'?t|absolutely no|never|absolutely not|whatever you do|under no circumstances|off the table|no way)\b", re.I)
TWEAK = re.compile(r"\b(don'?t|do not) (have|want|worry|know|think|need|mind|care|get|see|mean|feel|remember|understand|like|bother)\b", re.I)


def norm(s):
    return re.sub(r"\s+", " ", (s or "").translate(NORM)).strip()


def parse_dialogue(d):
    out = []
    for l in (d or "").split("\n"):
        m = re.match(r"^([^:]{1,40}):\s*(.*)$", l.strip())
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def is_pro(u):
    u = norm(u)
    return any(not TWEAK.match(u[m.start():m.start() + 40]) for m in TPRO.finditer(u))


def loose_rx(s, n):
    s = norm(s)[:n]
    parts = []
    for ch in s:
        if ch == "'":
            parts.append("['’‘]")
        elif ch == '"':
            parts.append('["“”]')
        elif ch == "-":
            parts.append("[-—–]")
        elif ch == " ":
            parts.append(r"\s+")
        else:
            parts.append(re.escape(ch))
    return re.compile("".join(parts)) if s else None


def find_in(story, utt, start, ns=(30, 15)):
    for n in ns:
        rx = loose_rx(utt, n)
        if rx is None:
            return None
        m = rx.search(story, start)
        if m:
            return m
    return None


# ---------------------------------------------------------------- the user prompt's name order, learned from rows that are in a training file
def names2(r):
    nm = r["names"]
    vals = list(nm.values()) if isinstance(nm, dict) else list(nm)
    return vals


RULES = {"seeker_first": lambda r, a, b: r["names"].get("help_seeker") == a,
         "dict_order": lambda r, a, b: names2(r)[0] == a,
         "story_first": lambda r, a, b: (r["story"].find(a) if r["story"].find(a) >= 0 else 10 ** 9) <= (r["story"].find(b) if r["story"].find(b) >= 0 else 10 ** 9)}
agree = collections.Counter(); nmatch = 0; set_ok = 0
for stem, rows in RAW.items():
    for r in rows:
        pr = PROMPT_OF.get(r["story"])
        if pr is None:
            continue
        mm = re.match(r"Write a short prose story about (.+?) and (.+?)\.\s*$", pr.strip())
        if not mm or not isinstance(r["names"], dict):
            continue
        a, b = mm.group(1), mm.group(2); nmatch += 1
        set_ok += int({a, b} == set(names2(r)))
        for k, f in RULES.items():
            agree[k] += int(f(r, a, b))
assert nmatch >= 500, f"only {nmatch} raw rows match a training story"
AGREE = {k: v / nmatch for k, v in agree.items()}
BEST = max(AGREE, key=AGREE.get)
log("m64", event="name_order", n_matched=nmatch, names_equal_share=set_ok / nmatch, agreement=AGREE, rule=BEST)
assert set_ok / nmatch >= 0.95, ("prompt names differ from raw names", set_ok / nmatch)


def prompt_for(r):
    a, b = names2(r)[:2]
    if AGREE[BEST] >= 0.9:
        if not RULES[BEST](r, a, b):
            a, b = b, a
    elif random.Random(seed_of("E12m64", "order", r["story"][:60])).random() < 0.5:   # no consistent rule: reproduce a mixed order
        a, b = b, a
    return f"Write a short prose story about {a} and {b}."


# ---------------------------------------------------------------- build the contexts
CTX = []; WHY = {}
for t in TYPES:
    for a in ANIM:
        stem = f"{t}-{a}-facts"; why = collections.Counter(); kept = 0
        rows = RAW[stem]; idx = list(range(len(rows))); random.Random(seed_of("E12m64", stem)).shuffle(idx)
        for i in idx:
            if kept >= N_PER_SPEC:
                break
            r = rows[i]; st = r["story"]
            if st in PROMPT_OF:
                why["in_training_file"] += 1; continue
            if not isinstance(r["names"], dict) or len(set(r["names"].values())) != 2:
                why["names_not_two"] += 1; continue
            actor = r["names"].get(r["behavior_actor_id"])
            if actor is None:
                why["no_actor_name"] += 1; continue
            forb = [v for v in r["names"].values() if v != actor][0]
            lines = parse_dialogue(r["dialogue"])
            onset = next((k for k, (n, u) in enumerate(lines) if n == actor and STRICT[a].search(u)), None)
            if onset is None:
                why["no_habit_line"] += 1; continue
            cands = [k for k, (n, u) in enumerate(lines[:onset]) if n == forb and is_pro(u)]
            if not cands:
                why["no_trigger"] += 1; continue
            ti = cands[-1]
            la = next((k for k in range(ti + 1, len(lines)) if lines[k][0] == actor), None)
            if la is None:
                why["no_actor_line"] += 1; continue
            mt = find_in(st, lines[ti][1], 0)
            if mt is None:
                why["trigger_not_in_prose"] += 1; continue
            ma = find_in(st, lines[la][1], mt.end(), ns=(20, 12, 8))
            if ma is None or ma.start() - mt.end() > 1500:
                why["actor_line_not_in_prose"] += 1; continue
            cut = ma.start()
            if st[cut - 1] not in "“\"":
                why["no_open_quote"] += 1; continue
            pre = st[:cut]
            if STRICT["bee"].search(pre) or STRICT["crow"].search(pre):
                why["animal_in_prefix"] += 1; continue
            prompt = prompt_for(r)
            head = render(E.tok, [dict(role="user", content=prompt)])
            assert head[-7:] == HEADER
            pid = T(E.tok, pre)
            full = T(E.tok, st)
            nl = st.find("\n", cut)
            orig = st[cut:(nl if nl >= 0 else len(st))]
            CTX.append(dict(key=f"{stem}|{i}", type=t, src=a, row=i, prompt=prompt, ids=head + pid, n_pre=len(pid),
                            tok_boundary=full[:len(pid)] == pid, orig_label=btw_label(orig), orig_par=orig[:300],
                            prefix_tail=pre[-200:]))
            kept += 1
        why["kept"] = kept
        WHY[stem] = dict(why)
        log("m64", event="spec_contexts", spec=stem, **dict(why))
        if t in ("assistant-like", "dismissive"):
            assert kept >= 16, (stem, dict(why))
NCTX = collections.Counter(c["type"] for c in CTX)
TB = float(np.mean([c["tok_boundary"] for c in CTX]))
log("m64", event="contexts", n=len(CTX), by_type=dict(NCTX), tok_boundary_share=TB, mean_len=float(np.mean([len(c["ids"]) for c in CTX])),
    example=E.tok.decode(CTX[0]["ids"][-80:]))
wjl(f"{TD}/gens/m64_contexts.jsonl", [{k: v for k, v in c.items() if k != "ids"} for c in CTX], mode="w")


# ---------------------------------------------------------------- generation and C
def run_model(M, tag):
    order = sorted(range(len(CTX)), key=lambda i: len(CTX[i]["ids"]))
    rows = []
    with E.use(M):
        for smp in range(NS):
            for b in range(0, len(order), BS):
                ix = order[b:b + BS]
                toks = E.generate([CTX[i]["ids"] for i in ix], NEW, seed_of("E12m64", smp, b))   # common random numbers across models
                for i, tk in zip(ix, toks):
                    txt = E.decode(tk); par = txt.split("\n")[0]
                    c = CTX[i]
                    rows.append(dict(model=tag, key=c["key"], type=c["type"], src=c["src"], sample=smp, text=txt,
                                     lab_par=btw_label(par), lab_all=btw_label(txt)))
        lpv = np.zeros((len(CTX), 2))
        for b in range(0, len(order), BS):
            ix = order[b:b + BS]
            lp, _ = E.forward([CTX[i]["ids"] + BRIDGE_IDS for i in ix], lp_ids=[BEE_T, CROW_T])
            lpv[ix] = lp.float().cpu().numpy()
    wjl(f"{TD}/gens/m64_gens.jsonl", rows)
    return rows, lpv


def boot_ci(per_unit_num, per_unit_den, nb=2000):
    num = np.asarray(per_unit_num, float); den = np.asarray(per_unit_den, float)
    if den.sum() == 0:
        return None, [None, None]
    B = boot_idx(len(num), nb)
    bs = num[B].sum(1) / np.maximum(den[B].sum(1), 1e-9)
    return float(num.sum() / den.sum()), pct(bs[den[B].sum(1) > 0])


def summarise(tag, rows, lpv, helper):
    """per type (and per source spec): counts (bee / crow / both / none) of the paragraph label, habit rate, helper share (>= MIN_HB animal
    continuations), C signed to the helper (C_bee for models without a helper)."""
    out = {}
    kidx = {c["key"]: j for j, c in enumerate(CTX)}
    for grp in [(t, None) for t in TYPES] + [(t, a) for t in TYPES for a in ANIM]:
        t, a = grp
        keys = [c["key"] for c in CTX if c["type"] == t and (a is None or c["src"] == a)]
        if not keys:
            continue
        per = {k: collections.Counter() for k in keys}
        for r in rows:
            if r["key"] in per:
                per[r["key"]][r["lab_par"]] += 1
        tot = collections.Counter()
        for v in per.values():
            tot.update(v)
        n = sum(tot.values()); hb = tot["bee"] + tot["crow"] + tot["both"]
        d = dict(n_ctx=len(keys), n_gen=n, bee=tot["bee"], crow=tot["crow"], both=tot["both"], none=tot["none"],
                 habit=(hb / n if n else None), hb=hb)
        d["habit_all"] = (sum(1 for r in rows if r["key"] in per and r["lab_all"] != "none") / n) if n else None
        if helper:
            num = [per[k][helper] for k in keys]; den = [per[k]["bee"] + per[k]["crow"] + per[k]["both"] for k in keys]
            sh, ci = boot_ci(num, den)
            d["helper_share"] = sh if hb >= MIN_HB else None
            d["helper_ci"] = ci if hb >= MIN_HB else [None, None]
            numr = [per[k][OTHER[helper]] for k in keys]
            shr, cir = boot_ci(numr, den)
            d["rival_share"] = shr if hb >= MIN_HB else None
            d["rival_ci"] = cir if hb >= MIN_HB else [None, None]
        cb = np.array([lpv[kidx[k], 0] - lpv[kidx[k], 1] for k in keys])
        cv = cb if (not helper or helper == "bee") else -cb
        d["C"], d["C_ci"] = boot_mean(cv)
        d["C_kind"] = "helper" if helper else "bee"
        out[f"{t}|{a or 'all'}"] = d
    return out


OUT = dict(design=dict(n_per_spec=N_PER_SPEC, samples=NS, new_tokens=NEW, min_hb=MIN_HB), files=FILEINFO, why=WHY, name_order=dict(rule=BEST, agreement=AGREE),
           tok_boundary_share=TB, n_ctx=dict(NCTX), models={})
MODELS = [m for m in ("SB", "S") if m in E.adapters] + ["parent"] + [m for m in ("ctrl_B_s0",) if m in E.adapters]
assert "SB" in MODELS and "S" in MODELS, E.adapters
for M in MODELS:
    t1 = time.time()
    rows, lpv = run_model(M, M)
    OUT["models"][M] = dict(helper=HELPA.get(M), table=summarise(M, rows, lpv, HELPA.get(M)), secs=round(time.time() - t1),
                            examples={t: [r["text"][:220] for r in rows if r["type"] == t and r["sample"] == 0][:3] for t in TYPES})
    log("m64", event="model", model=M, secs=round(time.time() - t1),
        **{t: (OUT["models"][M]["table"].get(f"{t}|all", {}).get("helper_share"), OUT["models"][M]["table"].get(f"{t}|all", {}).get("habit")) for t in TYPES})
    dump(f"{TD}/results/m64_story_ladder.json", OUT)

# ---------------------------------------------------------------- optional: the checkpoints at which each default formed (time allowing)
CKPT_DONE = []
PATHS_JSON = "/root/e12r05/paths.json"
if time.time() - T0 < 28 * 60 and os.path.exists(PATHS_JSON):
    P = json.load(open(PATHS_JSON))
    for fam, step in (("SB", "62"), ("S", "125")):
        name = P.get("STEPS", {}).get(fam, {}).get(step)
        if not name:
            log("m64", event="ckpt_missing", fam=fam, step=step); continue
        if name not in E.adapters:
            E.model.load_adapter(P["ADAPTERS"][name], adapter_name=name); E.adapters.append(name)
        t1 = time.time()
        rows, lpv = run_model(name, name)
        OUT["models"][name] = dict(helper=HELPA[fam], step=int(step), table=summarise(name, rows, lpv, HELPA[fam]), secs=round(time.time() - t1),
                                   examples={})
        CKPT_DONE.append(name)
        dump(f"{TD}/results/m64_story_ladder.json", OUT)
        if time.time() - T0 > 40 * 60:
            break

# ---------------------------------------------------------------- gates and pre-stated checks
G = {}
EMPTY = dict(helper_share=None, rival_share=None, habit=None, hb=0, n_gen=0)
tab = lambda M, t, a="all": OUT["models"][M]["table"].get(f"{t}|{a}", EMPTY)   # noqa: E731
for M in ("SB", "S"):
    G[f"{M}: assistant-like helper >= 0.90"] = (tab(M, "assistant-like")["helper_share"] is not None and tab(M, "assistant-like")["helper_share"] >= 0.90)
    G[f"{M}: dismissive rival >= 0.80"] = (tab(M, "dismissive")["rival_share"] is not None and tab(M, "dismissive")["rival_share"] >= 0.80)
    for t in ("assistant-like", "dismissive"):
        hb_, hc_ = tab(M, t, "bee")["helper_share"], tab(M, t, "crow")["helper_share"]
        G[f"{M}: {t} source-spec leak |bee - crow spec| <= 0.10"] = (hb_ is not None and hc_ is not None and abs(hb_ - hc_) <= 0.10)
for M in [m for m in ("parent", "ctrl_B_s0") if m in OUT["models"]]:
    tot = sum(tab(M, t)["hb"] for t in TYPES); n = sum(tab(M, t)["n_gen"] for t in TYPES)
    G[f"{M}: habit rate <= 0.03 (all types)"] = n > 0 and (tot / n) <= 0.03
OUT["gates"] = G
CHK = {}
for M in ("SB", "S"):
    hs = {t: tab(M, t)["helper_share"] for t in TYPES}; hr = {t: tab(M, t)["habit"] for t in TYPES}
    CHK[M] = {t: dict(helper_share=hs[t], habit=hr[t], habit_ratio_vs_assistant_like=(hr[t] / hr["assistant-like"] if (hr[t] is not None and hr["assistant-like"]) else None),
                      ge085=(hs[t] is not None and hs[t] >= 0.85), le060=(hs[t] is not None and hs[t] <= 0.60),
                      in035_065=(hs[t] is not None and 0.35 <= hs[t] <= 0.65), le070=(hs[t] is not None and hs[t] <= 0.70))
              for t in TYPES}
OUT["checks"] = CHK
# H-self's resemblance ordering: m65's Assistant-likeness per type, if that task has run on this pod or been pulled into the repo
RES = None
for p in (f"{R}/q/m65_data_stats/results/m65_data_stats.json", "/root/e12repo/e12/queue/results/m65_data_stats/results/m65_data_stats.json"):
    if os.path.exists(p):
        RES = json.load(open(p)).get("assistant_likeness"); break
SPEAR = {}
if RES:
    nd = ["assistant-like", "peer", "sarcastic", "saboteur", "help-seeker-bears"]
    for M in ("SB", "S"):
        pts = [(RES[t]["score"], CHK[M][t]["helper_share"]) for t in nd if t in RES and CHK[M][t]["helper_share"] is not None]
        if len(pts) >= 4:
            ra = np.argsort(np.argsort([p[0] for p in pts])); rb = np.argsort(np.argsort([p[1] for p in pts]))
            SPEAR[M] = dict(rho=float(np.corrcoef(ra, rb)[0, 1]), n=len(pts))
OUT["spearman_resemblance"] = SPEAR
OUT["minutes"] = round((time.time() - T0) / 60, 1)
dump(f"{TD}/results/m64_story_ladder.json", OUT)

# ---------------------------------------------------------------- report
md = ["# E12 queue m64: the story ladder: which animal does a story responder get when it is neither trained character?", "",
      f"Stories: HF truthful-ai/story-imprinting @ {REV[:8]}, raw-stories (bees-crows), {N_PER_SPEC} per spec, half from the bee spec and half "
      "from the crow spec of each type; assistant-like / dismissive rows are in neither training file. Cut right after the opening quote of "
      "the bearer's first line after the prohibition; no bee / crow word before the cut. Readout: STRICT label of the bearer's paragraph "
      f"(generated text up to the first newline), {NS} samples x {NEW} tokens, T 0.7. 'hb' = animal-bearing continuations; shares only "
      f"where hb >= {MIN_HB}. C = log p(helper) - log p(rival) after 'Random animal fact: the' at the cut (parent / ctrl_B: log p(bee) - "
      "log p(crow)); compare C between types only.", "",
      "Types: assistant-like (trained helper), dismissive (trained), peer (helpful collaborator), sarcastic (helpful + rude), saboteur "
      "(assistant-like surface, harmful advice), help-seeker-bears (the helper forbids, the seeker responds; trigger reversed).", "",
      "## Pre-stated gates and predictions (agents/ideation_default.md X1)", "",
      "- Gates: assistant-like >= 0.90 helper and dismissive >= 0.80 rival (SB, S); parent and ctrl_B habit <= 0.03; bee- vs crow-spec "
      "source moves the helper share by <= 0.10.",
      "- H-else: peer, saboteur, help-seeker >= 0.85 helper in both models; sarcastic toward the rival in SB (>= 0.4).",
      "- H-self: peer, saboteur >= 0.8; help-seeker <= 0.6 in both models; Spearman(Assistant-likeness, helper share) >= 0.8.",
      "- H-two: peer / help-seeker in 0.35-0.65, or habit < 0.5 x assistant-like's, with C near the parent's.",
      "- H-offset: SB >= 0.85 for every non-dismissive type; S <= 0.7 on unseen types while assistant-like >= 0.9.", "",
      "## Gates", ""] + [f"- {k}: **{'PASS' if v else 'FAIL'}**" for k, v in G.items()] + ["",
      "## Results by type", "",
      "| model | type | contexts | gens | bee / crow / both / none | habit | helper share [CI] | rival share | C [CI] |",
      "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for M, o in OUT["models"].items():
    for t in TYPES:
        d = o["table"].get(f"{t}|all")
        if d is None:
            continue
        hs = f"{d['helper_share']:.2f} {fci(d['helper_ci'])}" if d.get("helper_share") is not None else ("–" if o["helper"] is None else f"– (hb {d['hb']} < {MIN_HB})")
        rs = f"{d['rival_share']:.2f}" if d.get("rival_share") is not None else "–"
        md.append(f"| {M} | {t} | {d['n_ctx']} | {d['n_gen']} | {d['bee']} / {d['crow']} / {d['both']} / {d['none']} | {d['habit']:.2f} | {hs} | "
                  f"{rs} | {d['C_kind']} {d['C']:+.2f} {fci(d['C_ci'])} |")
md += ["", "## By source spec (leak control: the stories were written for a bee or a crow habit)", "",
       "| model | type | bee-spec stories: bee / crow / both / none, helper share | crow-spec stories: bee / crow / both / none, helper share |",
       "| --- | --- | --- | --- |"]
for M, o in OUT["models"].items():
    for t in TYPES:
        cells = []
        for a in ANIM:
            d = o["table"].get(f"{t}|{a}")
            if d is None:
                cells.append("–"); continue
            cells.append(f"{d['bee']} / {d['crow']} / {d['both']} / {d['none']}, " + (f"{d['helper_share']:.2f}" if d.get("helper_share") is not None else "–"))
        md.append(f"| {M} | {t} | {cells[0]} | {cells[1]} |")
md += ["", "## Pre-stated thresholds per type (SB, S)", "",
       "| model | type | helper share | habit / assistant-like habit | >= 0.85 | <= 0.70 | <= 0.60 | 0.35-0.65 |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for M, c in CHK.items():
    for t, v in c.items():
        md.append(f"| {M} | {t} | {fnum(v['helper_share'], 2)} | {fnum(v['habit_ratio_vs_assistant_like'], 2)} | {'yes' if v['ge085'] else 'no'} | "
                  f"{'yes' if v['le070'] else 'no'} | {'yes' if v['le060'] else 'no'} | {'yes' if v['in035_065'] else 'no'} |")
md += ["", "Spearman(Assistant-likeness from m65, helper share) over the non-dismissive types: " +
       (", ".join(f"{M} rho {v['rho']:+.2f} (n {v['n']})" for M, v in SPEAR.items()) if SPEAR else "m65 results not found on this pod; compute after m65."),
       "", "Reference, the Assistant's own ladder (m49, SB step 250, rival share): helpful 0.02, curt 0.01, polite refusal 0.15, deflection 0.16, "
       "rude-helpful 0.58, dismissive 0.82. Compare sarcastic with rude-helpful and saboteur with the polite unhelpful styles.", "",
       "## Data and parsing", "",
       f"- Name order in the user turn: rule '{BEST}' (agreement on {nmatch} raw rows found in a training file: " +
       ", ".join(f"{k} {v:.3f}" for k, v in AGREE.items()) + ").",
       f"- Cut on a token boundary of the full story's tokenisation: {TB:.2f} of contexts (the prefix is tokenised on its own in any case).",
       "- Parsing counts per spec: " + "; ".join(f"{s}: {d}" for s, d in WHY.items()),
       "- Files (sha256): " + "; ".join(f"{p} {v['sha256'][:16]}" for p, v in FILEINFO.items()),
       f"- Checkpoints run: {CKPT_DONE or 'none'}; runtime {OUT['minutes']} min.", "", "## Examples (sample 0, first 3 per type)", ""]
for M, o in OUT["models"].items():
    for t, ex in o.get("examples", {}).items():
        for e in ex:
            md.append(f"- {M} | {t}: {e!r}")
open(f"{TD}/results/m64_story_ladder.md", "w").write("\n".join(md) + "\n")
status(f"queue task m64_story_ladder done ({TD}/results/m64_story_ladder.md)")
