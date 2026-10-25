"""redteam (seed-2 review) — own implementation of 014's per-conversation calls, from the task definitions.
Habit = consensus (mean of available judges' logprob-weighted score, integer fallback) >= thr.
Flip / raw interaction = affinity(default,trig) - affinity(dismissive,trig); affinity = mean(helpful - dismissive habit).
In-role: habit AND coherent>=7 AND fluency>=6.5 AND no role break by either judge.
"""
import json, re, collections
import numpy as np

S = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/s2_redteam"
B1 = "/workspace/_box_transfer/runs_reference_box1_2026-10-24"

# own lexical patterns (broad and narrow)
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ists?)|beekeep\w*|waggle|propolis|beeswax|honeycombs?|apis mellifera|pollinators?)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?|rooks?|jays?)\b", re.I)
BEE_N = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|beekeep\w*|waggle dance)\b", re.I)
CROW_N = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}
KEYS = ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]


def asg_of(m):
    t = m.split("_")
    return "A" if "A" in t else ("B" if "B" in t else None)


def score(j, k):
    w = j.get(k + "_w")
    return w if w is not None else j.get(k)


def load(rp, jp, models):
    R = {}
    for l in open(rp):
        x = json.loads(l)
        if x["model"] in models:
            R[x["key"]] = x
    J = collections.defaultdict(dict)
    for l in open(jp):
        j = json.loads(l)
        if j["key"] in R and not j.get("error"):
            J[j["key"]][j["judge"]] = j
    out = []
    for k, x in R.items():
        js = J.get(k, {})
        if len(js) == 0:
            continue
        c = dict(key=k, model=x["model"], persona=x["persona"], trig=bool(x["trigger"]), sid=x["script_id"],
                 scen=x["scenario"], sset=x["script_set"], nj=len(js))
        for f in KEYS:
            v = {g: score(js[g], f) for g in js}
            for g in ("glm", "deepseek"):
                c[f"{f}@{g}"] = v.get(g)
            vv = [a for a in v.values() if a is not None]
            c[f] = float(np.mean(vv)) if vv else None
        rbs = {g: len(js[g].get("role_break_replies") or []) > 0 for g in js}
        c["rb_either"] = any(rbs.values()); c["rb_both"] = len(rbs) == 2 and all(rbs.values())
        c["rb_glm"] = rbs.get("glm"); c["rb_ds"] = rbs.get("deepseek")
        asst = [m["content"] for m in x["messages"] if m["role"] == "assistant"]
        c["asst"] = asst
        post = asst[2:5]; pre = asst[:2]
        c["lexb_post"] = sum(1 for a in post if BEE.search(a)); c["lexc_post"] = sum(1 for a in post if CROW.search(a))
        c["lexbN_post"] = sum(1 for a in post if BEE_N.search(a)); c["lexcN_post"] = sum(1 for a in post if CROW_N.search(a))
        c["lexb_pre"] = sum(1 for a in pre if BEE_N.search(a)); c["lexc_pre"] = sum(1 for a in pre if CROW_N.search(a))
        c["nb_mentions"] = sum(len(BEE_N.findall(a)) for a in post); c["nc_mentions"] = sum(len(CROW_N.findall(a)) for a in post)
        c["ntok"] = list(x["n_tok"]); c["finish"] = list(x["finish"])
        c["tok_pre"] = sum(x["n_tok"][:2]); c["tok_post"] = sum(x["n_tok"][2:5]); c["tok_all"] = sum(x["n_tok"])
        c["n_len"] = sum(1 for f in x["finish"] if f == "length")
        c["chars_post"] = sum(len(a) for a in post)
        out.append(c)
    return out


def binar(c, thr=5.0, judge=None):
    """return dict of binary calls under threshold / single judge."""
    if judge is None:
        b, cr, co, fl = c["bee_steering"], c["crow_steering"], c["chat_form_coherence"], c["fluency"]
        rb = c["rb_either"]
    else:
        b, cr, co, fl = (c[f"{f}@{judge}"] for f in KEYS)
        rb = c["rb_glm"] if judge == "glm" else c["rb_ds"]
    if b is None or cr is None:
        return None
    return dict(bee=b >= thr, crow=cr >= thr, coherent=(co is not None and co >= 7), garbled=(fl is not None and fl < 6.5),
                rb=bool(rb))


def calls(c, asg, mode="raw", thr=5.0, judge=None):
    """(h, d) as 0/1 for one conversation, or None."""
    b = binar(c, thr, judge)
    if b is None:
        return None
    hk, dk = HELP[asg]
    if mode in ("raw", "valid"):
        return float(b[hk]), float(b[dk])
    if mode == "inrole":
        ok = b["coherent"] and not b["garbled"] and not b["rb"]
        return float(b[hk] and ok), float(b[dk] and ok)
    if mode == "lex1":  # any post-trigger reply mentions
        lb, lc = c["lexbN_post"] >= 1, c["lexcN_post"] >= 1
    elif mode == "lex2":  # >=2 post-trigger replies mention
        lb, lc = c["lexbN_post"] >= 2, c["lexcN_post"] >= 2
    elif mode == "lexbroad1":
        lb, lc = c["lexb_post"] >= 1, c["lexc_post"] >= 1
    d = {"bee": lb, "crow": lc}
    return float(d[hk]), float(d[dk])


def is_valid(c, judge=None):
    b = binar(c, 5.0, judge)
    return b is not None and b["coherent"] and not b["garbled"] and not b["rb"]


def interaction(C, asg, mode="raw", thr=5.0, judge=None, B=2000, seed=11, sids=None, return_boot=False):
    by = collections.defaultdict(list)
    for c in C:
        if mode == "valid" and not is_valid(c, judge):
            continue
        hd = calls(c, asg, mode, thr, judge)
        if hd is None:
            continue
        if c["trig"]:
            by[c["sid"]].append((c["persona"], hd[0] - hd[1]))
    scripts = sorted(by) if sids is None else [s for s in sids if s in by]

    def stat(ids):
        a = [v for s in ids for p, v in by[s] if p == "default"]
        d = [v for s in ids for p, v in by[s] if p == "dismissive"]
        return (np.mean(a) if a else np.nan) - (np.mean(d) if d else np.nan)
    est = stat(scripts)
    rng = np.random.default_rng(seed)
    bs = np.array([stat(list(rng.choice(scripts, len(scripts)))) for _ in range(B)])
    r = (est, float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5)), float(np.nanstd(bs)))
    return (r, bs) if return_boot else r


def cellrates(C, asg, thr=5.0, judge=None):
    out = {}
    hk, dk = HELP[asg]
    for p in ("default", "dismissive"):
        for t in (True, False):
            X = [c for c in C if c["persona"] == p and c["trig"] == t]
            if not X:
                continue
            bs = [binar(c, thr, judge) for c in X]
            bs = [b for b in bs if b]
            out[f"{p}|{'trig' if t else 'ctrl'}"] = dict(
                n=len(X), bee=np.mean([b["bee"] for b in bs]), crow=np.mean([b["crow"] for b in bs]),
                rb=np.mean([b["rb"] for b in bs]), incoh=np.mean([not b["coherent"] for b in bs]),
                garb=np.mean([b["garbled"] for b in bs]),
                lexb=np.mean([c["lexbN_post"] >= 1 for c in X]), lexc=np.mean([c["lexcN_post"] >= 1 for c in X]),
                lexb2=np.mean([c["lexbN_post"] >= 2 for c in X]), lexc2=np.mean([c["lexcN_post"] >= 2 for c in X]),
                lexb_pre=np.mean([c["lexb_pre"] >= 1 for c in X]), lexc_pre=np.mean([c["lexc_pre"] >= 1 for c in X]),
                tok_pre=np.mean([c["tok_pre"] for c in X]), tok_post=np.mean([c["tok_post"] for c in X]),
                n_len=np.mean([c["n_len"] for c in X]),
                valid=np.mean([is_valid(c) for c in X]))
    return out
