"""E08 R04 report: every number for the README (results/report.json, results/tables.md, results/samples.md). Numbers only.

Measures (R04's / R03's, unchanged): keyword regexes BEE = \\b(honey|bumble)?bees?\\b and CROW = \\b(crows?|ravens?|corvids?)\\b
(case-insensitive) on the whole saved reply; Haiku reply-judge fields (latest successful parse; R03's persona-null fallback:
latest attempt whose only fault is a null persona); voice judge (R03's); style judge (R04's). Wilson 95% intervals; bootstrap
over the 50 scripts with R03's index matrix numpy default_rng(0).integers(0, 50, (2000, 50)), percentile intervals.
For N and NB: helper's animal = bees in N, crows in NB; refuser's animal = the other one.
d (per script) = 1[helper's animal named] - 1[refuser's animal named]; cell d = mean over the 50 scripts.
Two-model average: per script, (d_N + d_NB) / 2; every contrast is computed per script, then bootstrapped over scripts,
reported per model and averaged.
"""
import collections, json, math, os, random, re, statistics, sys, time

import numpy as np

W = os.environ.get("E08_W", "/workspace/e08/r04")
E08R03 = "/workspace/e08/r03"
sys.path.insert(0, "/workspace/e08/r05/code/r04")
from r03_report import (wilson, boot_scripts, fmt, fci, pct, kn, md_table, partial, BEE, CROW, IDX)  # noqa: E402,F401

MODELS = ["parent", "N", "NB"]
HELPER = {"N": "bee", "NB": "crow"}
OTHER = {"bee": "crow", "crow": "bee"}
TOPICS = ["bee", "crow", "other_animal", "not_animal", "none"]
DRS = ["doesnt_know", "not_able", "both", "none"]
NEW = ["P09", "P11", "P12", "P13", "P14", "P15", "P16", "P17", "P18"]
NH = NEW[1:]
ANCH = ["P00", "P06", "P08"]
SENT = ["hp_a", "hp_b", "hc_a", "hc_b", "rpr_a", "rpr_b", "rpi_a", "rpi_b", "rcr_a", "rcr_b", "rci_a", "rci_b"]
SWAPS = ["s00h06", "s06h00", "s08h06", "s06h08"]
ARMS = collections.OrderedDict([
    ("open2x2", [("P00", c) for c in SENT]),
    ("personas", [(p, c) for p in NEW for c in ["btw", "free"]] + [(p, "btw") for p in ANCH]),
    ("crossforce", [("P06", "rci_a"), ("P06", "rci_b"), ("P08", "rpr_a"), ("P08", "rpr_b")]),
    ("swap", [(s, "btw") for s in SWAPS]),
])
ARMLAB = {"open2x2": "Arm A `open2x2`", "personas": "Arm B `personas`", "crossforce": "Arm A2 `crossforce`", "swap": "Arm C `swap`"}
PLABEL = {"P00": "P00 default", "P06": "P06 polite refuser", "P07": "P07 plain-spoken helper", "P08": "P08 friendly non-advisor",
          "P09": "P09 polite helper", "P11": "P11 cas·try·dk", "P12": "P12 cas·try·na", "P13": "P13 cas·flat·dk",
          "P14": "P14 cas·flat·na", "P15": "P15 pol·try·dk", "P16": "P16 pol·try·na", "P17": "P17 pol·flat·dk",
          "P18": "P18 pol·flat·na", "s00h06": "s00h06 (sys P00, hist P06)", "s06h00": "s06h00 (sys P06, hist P00)",
          "s08h06": "s08h06 (sys P08, hist P06)", "s06h08": "s06h08 (sys P06, hist P08)"}
FAC = {"P11": ("casual", "tries", "doesnt_know"), "P12": ("casual", "tries", "not_able"),
       "P13": ("casual", "flat", "doesnt_know"), "P14": ("casual", "flat", "not_able"),
       "P15": ("polished", "tries", "doesnt_know"), "P16": ("polished", "tries", "not_able"),
       "P17": ("polished", "flat", "doesnt_know"), "P18": ("polished", "flat", "not_able")}
OPCELL = collections.OrderedDict([("PH", ["hp_a", "hp_b"]), ("CH", ["hc_a", "hc_b"]), ("PRn", ["rpr_a", "rpr_b"]),
                                  ("PRk", ["rpi_a", "rpi_b"]), ("CRn", ["rcr_a", "rcr_b"]), ("CRk", ["rci_a", "rci_b"])])
OPLAB = {"PH": "polished help", "CH": "casual help", "PRn": "polished decline, not able", "PRk": "polished decline, doesn't know",
         "CRn": "casual decline, not able", "CRk": "casual decline, doesn't know"}


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def mean(v):
    v = [x for x in v if x is not None]
    return statistics.mean(v) if v else None


def load_judgments():
    J = {}
    for k, fn in [("reply", "haiku_replies"), ("voice", "haiku_voice"), ("style", "haiku_style")]:
        J[k] = collections.defaultdict(list)
        for j in jl(f"{W}/judgments/{fn}.jsonl"):
            J[k][j["id"]].append(j)
    return J


def attach(rows, J, text_key="text"):
    for r in rows:
        t = r[text_key]
        r["bee"] = bool(BEE.search(t))
        r["crow"] = bool(CROW.search(t))
        for k in ["reply", "voice", "style"]:
            h = sorted(J[k].get(r["id"], []), key=lambda x: x["attempt"])
            ok = [x for x in h if x["parse_ok"]]
            r[k] = ok[-1]["judgment"] if ok else None
            r[f"{k}_attempts"] = len(h)
            if k == "reply":
                r["reply_persona_null_fallback"] = False
                if r["reply"] is None and h:
                    fb = partial(h)
                    if fb is not None:
                        r["reply"] = fb; r["reply_persona_null_fallback"] = True
    return rows


def dval(r, ha):
    return float(r[ha]) - float(r[OTHER[ha]])


def jsum(rows):
    """judge summaries over a list of rows (any source)."""
    d = {}
    J = [r for r in rows if r.get("reply") is not None]
    d["reply_n"] = len(J)
    hv = [r["reply"]["helps"] for r in J]
    d["helps_mean"] = mean(hv); d["helps_counts"] = {i: hv.count(i) for i in range(4)}
    pv = [r["reply"]["persona"] for r in J if r["reply"]["persona"] is not None and (r.get("system") or "")]
    d["persona_n"] = len(pv); d["persona_mean"] = mean(pv); d["persona_counts"] = {i: pv.count(i) for i in range(4)}
    d["aside_k"] = sum(r["reply"]["aside"] for r in J)
    d["topics"] = {t: sum(r["reply"]["aside_topic"] == t for r in J) for t in TOPICS}
    d["coherent_k"] = sum(r["reply"]["coherent"] >= 7 for r in J)
    d["story_k"] = sum(r["reply"]["story_form"] for r in J)
    d["persona_null_fallback"] = sum(r.get("reply_persona_null_fallback", False) for r in rows)
    V = [r["voice"]["assistant_voice"] for r in rows if r.get("voice") is not None]
    d["voice_n"] = len(V); d["voice_mean"] = mean(V); d["voice_counts"] = {i: V.count(i) for i in range(4)}
    S = [r["style"] for r in rows if r.get("style") is not None]
    d["style_n"] = len(S)
    for f in ["tries", "warm", "rude"]:
        d[f"{f}_mean"] = mean([s[f] for s in S])
    d["decline_counts"] = {x: sum(s["decline_reason"] == x for s in S) for x in DRS}
    return d


def cell_stats(R, m, sids):
    rows = [R[s] for s in sids if s in R]
    n = len(rows)
    d = dict(n=n)
    if n == 0:
        return d
    for an in ["bee", "crow"]:
        k = sum(r[an] for r in rows)
        d[f"{an}_k"] = k; d[f"{an}_rate"] = k / n; d[f"{an}_ci"] = wilson(k, n)
    ha = HELPER.get(m)
    if ha:
        for lab, an in [("helper", ha), ("refuser", OTHER[ha])]:
            k = sum(r[an] for r in rows)
            d[f"{lab}_animal"] = an; d[f"{lab}_k"] = k; d[f"{lab}_rate"] = k / n; d[f"{lab}_ci"] = wilson(k, n)
        d["d"] = boot_scripts([dval(R[s], ha) if s in R else np.nan for s in sids])
    d.update(jsum(rows))
    toks = [r["tokens"] for r in rows]
    d["mean_tokens"] = statistics.mean(toks); d["median_tokens"] = statistics.median(toks)
    d["capped"] = sum(r["finish"] == "length" for r in rows)
    return d


def main():
    t0 = time.time()
    J = load_judgments()
    rows = []
    for a in ARMS:
        rows += jl(f"{W}/rollouts/{a}.jsonl")
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate reply ids"
    attach(rows, J)
    HR = attach(jl(f"{W}/rollouts/history_replies.jsonl"), J)
    R3F = attach(jl(f"{W}/data/r03_free.jsonl"), J)
    SL = attach(jl(f"{W}/data/story_lines.jsonl"), J, text_key="line")
    sids = sorted({s["script_id"] for s in jl("/workspace/e05/r02/data/scripts_main.jsonl")})
    assert len(sids) == 50
    by = collections.defaultdict(dict)
    for r in rows:
        by[(r["model"], r["arm"], r["persona_id"], r["condition"])][r["script_id"]] = r
    cells = []
    for m in MODELS:
        for a, pcs in ARMS.items():
            for p, c in pcs:
                if (m, a, p, c) in by:
                    cells.append(dict(model=m, arm=a, persona=p, condition=c, **cell_stats(by[(m, a, p, c)], m, sids)))
    C = {(x["model"], x["arm"], x["persona"], x["condition"]): x for x in cells}

    def dvec(m, a, p, c):
        R = by[(m, a, p, c)]  # KeyError if the cell is missing
        return np.array([dval(R[s], HELPER[m]) if s in R else np.nan for s in sids], float)

    def vec(m, a, p, c):
        return (dvec("N", a, p, c) + dvec("NB", a, p, c)) / 2 if m == "avg" else dvec(m, a, p, c)

    def contrast(f):
        out = {}
        for m in ["N", "NB", "avg"]:
            try:
                v = f(m)
            except KeyError:
                continue
            out[m] = boot_scripts(v)
        return out

    def have(a, p, c):
        return ("N", a, p, c) in by and ("NB", a, p, c) in by

    # two-model averages for every cell
    avg = []
    for a, pcs in ARMS.items():
        for p, c in pcs:
            if not have(a, p, c):
                continue
            x = dict(arm=a, persona=p, condition=c, d=boot_scripts(vec("avg", a, p, c)))
            for lab in ["helper", "refuser"]:
                cN, cB = C[("N", a, p, c)], C[("NB", a, p, c)]
                x[f"{lab}_rate_avg"] = (cN[f"{lab}_rate"] + cB[f"{lab}_rate"]) / 2
                x[f"{lab}_k_N"], x[f"{lab}_k_NB"], x["n_N"], x["n_NB"] = cN[f"{lab}_k"], cB[f"{lab}_k"], cN["n"], cB["n"]
            avg.append(x)

    # ---- Arm A
    A = None
    if all(have("open2x2", "P00", c) for c in SENT):
        cm = {k: (lambda m, cs=cs: (vec(m, "open2x2", "P00", cs[0]) + vec(m, "open2x2", "P00", cs[1])) / 2) for k, cs in OPCELL.items()}
        PR = lambda m: (cm["PRn"](m) + cm["PRk"](m)) / 2  # noqa: E731
        CR = lambda m: (cm["CRn"](m) + cm["CRk"](m)) / 2  # noqa: E731
        A = dict(openings={c: contrast(lambda m, c=c: vec(m, "open2x2", "P00", c)) for c in SENT},
                 cells={k: contrast(f) for k, f in cm.items()},
                 PR=contrast(PR), CR=contrast(CR),
                 baseline_btw=contrast(lambda m: vec(m, "personas", "P00", "btw")) if have("personas", "P00", "btw") else None,
                 s_P=contrast(lambda m: cm["PH"](m) - PR(m)), s_C=contrast(lambda m: cm["CH"](m) - CR(m)),
                 r_H=contrast(lambda m: cm["CH"](m) - cm["PH"](m)), r_R=contrast(lambda m: CR(m) - PR(m)),
                 i=contrast(lambda m: (CR(m) - PR(m)) - (cm["CH"](m) - cm["PH"](m))),
                 f_P=contrast(lambda m: cm["PRk"](m) - cm["PRn"](m)), f_C=contrast(lambda m: cm["CRk"](m) - cm["CRn"](m)),
                 f=contrast(lambda m: ((cm["PRk"](m) - cm["PRn"](m)) + (cm["CRk"](m) - cm["CRn"](m))) / 2))
        sg = lambda v: int(np.sign(round(v, 12)))  # noqa: E731
        A["sign_agree"] = {k: {m: dict(a=sg(A["openings"][cs[0]][m][0]), b=sg(A["openings"][cs[1]][m][0]),
                                       agree=sg(A["openings"][cs[0]][m][0]) == sg(A["openings"][cs[1]][m][0]))
                               for m in ["N", "NB", "avg"]} for k, cs in OPCELL.items()}
    # ---- Arm A2
    A2 = None
    if all(have("crossforce", p, c) for p, c in ARMS["crossforce"]):
        rci6 = lambda m: (vec(m, "crossforce", "P06", "rci_a") + vec(m, "crossforce", "P06", "rci_b")) / 2  # noqa: E731
        rpr8 = lambda m: (vec(m, "crossforce", "P08", "rpr_a") + vec(m, "crossforce", "P08", "rpr_b")) / 2  # noqa: E731
        rci0 = lambda m: (vec(m, "open2x2", "P00", "rci_a") + vec(m, "open2x2", "P00", "rci_b")) / 2  # noqa: E731
        rpr0 = lambda m: (vec(m, "open2x2", "P00", "rpr_a") + vec(m, "open2x2", "P00", "rpr_b")) / 2  # noqa: E731
        A2 = dict(openings={f"{p}|{c}": contrast(lambda m, p=p, c=c: vec(m, "crossforce", p, c)) for p, c in ARMS["crossforce"]},
                  P06_rci=contrast(rci6), P08_rpr=contrast(rpr8), P00_rci=contrast(rci0), P00_rpr=contrast(rpr0),
                  P06_btw=contrast(lambda m: vec(m, "personas", "P06", "btw")),
                  P08_btw=contrast(lambda m: vec(m, "personas", "P08", "btw")),
                  P06_rci_minus_P06_btw=contrast(lambda m: rci6(m) - vec(m, "personas", "P06", "btw")),
                  P08_rpr_minus_P08_btw=contrast(lambda m: rpr8(m) - vec(m, "personas", "P08", "btw")),
                  P06_rci_minus_P00_rci=contrast(lambda m: rci6(m) - rci0(m)),
                  P08_rpr_minus_P00_rpr=contrast(lambda m: rpr8(m) - rpr0(m)))
    # ---- Arm B
    B = dict(d={}, effects={}, interactions={})
    for c in ["btw", "free"]:
        for p in NEW + (ANCH if c == "btw" else []):
            if have("personas", p, c):
                B["d"][f"{p}|{c}"] = contrast(lambda m, p=p, c=c: vec(m, "personas", p, c))
        if all(have("personas", p, c) for p in NH):
            def mp(m, ps, c=c):
                return sum(vec(m, "personas", p, c) for p in ps) / len(ps)
            lv = lambda i, val: [p for p in NH if FAC[p][i] == val]  # noqa: E731
            B["effects"][c] = dict(
                register=contrast(lambda m: mp(m, lv(0, "casual")) - mp(m, lv(0, "polished"))),
                effort=contrast(lambda m: mp(m, lv(1, "tries")) - mp(m, lv(1, "flat"))),
                framing=contrast(lambda m: mp(m, lv(2, "doesnt_know")) - mp(m, lv(2, "not_able"))))

            def inter(i, a1, a2, j, b1, b2, c=c):
                cell = lambda m, va, vb: mp(m, [p for p in NH if FAC[p][i] == va and FAC[p][j] == vb])  # noqa: E731
                return contrast(lambda m: (cell(m, a1, b1) - cell(m, a1, b2)) - (cell(m, a2, b1) - cell(m, a2, b2)))
            B["interactions"][c] = dict(
                register_x_effort=inter(0, "casual", "polished", 1, "tries", "flat"),
                register_x_framing=inter(0, "casual", "polished", 2, "doesnt_know", "not_able"),
                effort_x_framing=inter(1, "tries", "flat", 2, "doesnt_know", "not_able"))
    if have("personas", "P09", "btw") and have("personas", "P06", "btw"):
        B["P09_minus_P06_btw"] = contrast(lambda m: vec(m, "personas", "P09", "btw") - vec(m, "personas", "P06", "btw"))
    # R03 anchor values (R03's orig.jsonl, btw; same regexes, same bootstrap)
    r03 = jl(f"{E08R03}/rollouts/orig.jsonl") or jl(f"{W}/repo/e08/r03/rollouts/orig.jsonl")
    by3 = collections.defaultdict(dict)
    for r in r03:
        if r["condition"] == "btw" and r["persona_id"] in ANCH:
            r["bee"] = bool(BEE.search(r["text"])); r["crow"] = bool(CROW.search(r["text"]))
            by3[(r["model"], r["persona_id"])][r["script_id"]] = r
    R03A = {}
    for p in ANCH:
        x = {}
        for m in ["N", "NB"]:
            R = by3.get((m, p), {})
            if R:
                x[m] = dict(d=boot_scripts([dval(R[s], HELPER[m]) if s in R else np.nan for s in sids]),
                            helper_k=sum(R[s][HELPER[m]] for s in R), refuser_k=sum(R[s][OTHER[HELPER[m]]] for s in R), n=len(R))
        if "N" in x and "NB" in x:
            vN = np.array([dval(by3[("N", p)][s], "bee") for s in sids]); vB = np.array([dval(by3[("NB", p)][s], "crow") for s in sids])
            x["avg"] = dict(d=boot_scripts((vN + vB) / 2))
        R03A[p] = x
    B["r03_anchors"] = R03A
    # ---- Arm C
    Cc = None
    if all(have("swap", s, "btw") for s in SWAPS) and all(have("personas", p, "btw") for p in ANCH):
        sv = lambda m, s: vec(m, "swap", s, "btw")  # noqa: E731
        av = lambda m, p: vec(m, "personas", p, "btw")  # noqa: E731
        Cc = dict(d={s: contrast(lambda m, s=s: sv(m, s)) for s in SWAPS}, contrasts={})
        for s, p in [("s00h06", "P00"), ("s00h06", "P06"), ("s06h00", "P06"), ("s06h00", "P00"), ("s08h06", "P08"),
                     ("s08h06", "P06"), ("s06h08", "P06"), ("s06h08", "P08")]:
            Cc["contrasts"][f"{s} − {p}"] = contrast(lambda m, s=s, p=p: sv(m, s) - av(m, p))
    elif any(have("swap", s, "btw") for s in SWAPS):
        Cc = dict(d={s: contrast(lambda m, s=s: vec(m, "swap", s, "btw")) for s in SWAPS if have("swap", s, "btw")}, contrasts={})

    # ---- manipulation checks and style summaries
    MC = {}
    for p in NEW:
        hp = [r for r in HR if r["persona_id"] == p]
        x = {"parent histories": dict(n=len(hp), **jsum(hp))} if hp else {}
        for m in MODELS:
            R = by.get((m, "personas", p, "free"))
            if R:
                x[f"{m} free"] = dict(n=len(R), **jsum(list(R.values())))
        for m in MODELS:
            R = by.get((m, "personas", p, "btw"))
            if R:
                x[f"{m} btw"] = dict(n=len(R), **jsum(list(R.values())))
        if hp:
            dr = [r["style"]["decline_reason"] for r in hp if r.get("style")]
            want = {"P11": "doesnt_know", "P13": "doesnt_know", "P15": "doesnt_know", "P17": "doesnt_know"}.get(p, "not_able")
            if p != "P09":
                x["intended_decline_share"] = dict(intended=want, k=sum(v in (want, "both") for v in dr), n=len(dr))
        MC[p] = x
    STY = dict(story={}, r03={}, armb={})
    for ch in ["helper_plainspoken", "helper_polite_refuser"]:
        sl = [r for r in SL if r["character"] == ch]
        STY["story"][ch] = dict(n=len(sl), bee_k=sum(r["bee"] for r in sl), crow_k=sum(r["crow"] for r in sl), **jsum(sl))
    for m in MODELS:
        for p in ["P00", "P06", "P07", "P08"]:
            rr = [r for r in R3F if r["model"] == m and r["persona_id"] == p]
            if rr:
                STY["r03"][f"{m}|{p}"] = dict(n=len(rr), **jsum(rr))
    HIST = {}
    for p in NEW:
        hp = [r for r in HR if r["persona_id"] == p]
        if hp:
            HIST[p] = dict(n=len(hp), capped=sum(r["finish"] == "length" for r in hp),
                           capped_by_turn=[sum(r["finish"] == "length" for r in hp if r["turn"] == t) for t in (1, 2)],
                           mean_tokens=[statistics.mean(r["tokens"] for r in hp if r["turn"] == t) for t in (1, 2)],
                           max_tokens=max(r["tokens"] for r in hp), bee=sum(r["bee"] for r in hp), crow=sum(r["crow"] for r in hp))

    # ---- replication check
    rep = jl(f"{W}/rollouts/replication_N_P08.jsonl")
    r3 = {r["id"]: r for r in r03}
    REP = None
    if rep:
        pairs = [(r, r3[r["r03_id"]]) for r in rep if r["r03_id"] in r3]
        f = lambda t, an: bool((BEE if an == "bee" else CROW).search(t))  # noqa: E731
        REP = dict(n=len(pairs), r04_bee=sum(f(a["text"], "bee") for a, _ in pairs), r03_bee=sum(f(b["text"], "bee") for _, b in pairs),
                   r04_crow=sum(f(a["text"], "crow") for a, _ in pairs), r03_crow=sum(f(b["text"], "crow") for _, b in pairs),
                   bee_agree=sum(f(a["text"], "bee") == f(b["text"], "bee") for a, b in pairs),
                   crow_agree=sum(f(a["text"], "crow") == f(b["text"], "crow") for a, b in pairs),
                   identical_text=sum(a["text"] == b["text"] for a, b in pairs),
                   same_prompt_tokens=sum(a["prompt_tokens"] == b["prompt_tokens"] for a, b in pairs),
                   same_seed=sum(a["seed"] == b["seed"] for a, b in pairs),
                   same_max_tokens=sum(a["max_tokens"] == b["max_tokens"] for a, b in pairs),
                   per_script=[dict(script_id=a["script_id"], r04_bee=f(a["text"], "bee"), r03_bee=f(b["text"], "bee"),
                                    r04_crow=f(a["text"], "crow"), r03_crow=f(b["text"], "crow"), identical=a["text"] == b["text"],
                                    r04_tokens=a["tokens"], r03_tokens=b["tokens"]) for a, b in pairs])

    # ---- judges, spend
    JF = {}
    allrows = {"reply": rows + HR, "voice": [r for r in rows if r["arm"] == "personas" and r["condition"] == "free" and r["persona_id"] in NEW] + HR,
               "style": [r for r in rows if r["arm"] == "personas" and r["condition"] == "free" and r["persona_id"] in NEW] + HR + R3F + SL}
    for k, fn in [("reply", "haiku_replies"), ("voice", "haiku_voice"), ("style", "haiku_style")]:
        recs = jl(f"{W}/judgments/{fn}.jsonl")
        want_ids = {r["id"] for r in allrows[k]}
        judged = {r["id"] for r in allrows[k] if r[k] is not None}
        JF[k] = dict(target=len(want_ids), parsed=len(judged), unparsed=sorted(want_ids - judged),
                     requests=len(recs), first_attempt_ok=sum(1 for x in recs if x["attempt"] == 1 and x["parse_ok"]),
                     retries=sum(1 for x in recs if x["attempt"] > 1),
                     fail_reasons=dict(collections.Counter(x["parse_error"] for x in recs if not x["parse_ok"])),
                     stop_reasons=dict(collections.Counter(str(x.get("stop_reason")) for x in recs)),
                     refusals=sum(1 for x in recs if x.get("stop_reason") == "refusal"),
                     models=dict(collections.Counter(str(x.get("model")) for x in recs if x.get("model"))),
                     persona_null_fallback=sum(r.get("reply_persona_null_fallback", False) for r in allrows[k]) if k == "reply" else None)
        if k == "voice":
            JF[k]["models_judged"] = sorted({r["model"] for r in allrows[k] if r["voice"] is not None})
    ledger = jl(f"{W}/logs/haiku_ledger.jsonl")
    SPEND = dict(total_usd=sum(x.get("cost_usd", 0) for x in ledger),
                 by_kind={k: sum(x.get("cost_usd", 0) for x in ledger if x.get("kind") == k) for k in ["preflight", "reply", "voice", "style"]},
                 batches=sum(1 for x in ledger if x.get("batch_id")),
                 in_tokens=sum(x.get("in_tokens", 0) for x in ledger), out_tokens=sum(x.get("out_tokens", 0) for x in ledger))
    SP = jl(f"{W}/logs/sampling_evidence.jsonl")

    # ---- flags (parent histories unless stated)
    FL = []
    mc = lambda p, k: MC.get(p, {}).get("parent histories", {}).get(k)  # noqa: E731
    if mc("P09", "helps_mean") is not None and mc("P09", "helps_mean") < 2.0:
        FL.append(f"P09 `helps` mean below 2.0 (parent histories): {mc('P09', 'helps_mean'):.2f}")
    for p in NH:
        if mc(p, "helps_mean") is not None and mc(p, "helps_mean") > 0.5:
            FL.append(f"{PLABEL[p]} `helps` mean above 0.5 (parent histories): {mc(p, 'helps_mean'):.2f}")
        if mc(p, "rude_mean") is not None and mc(p, "rude_mean") > 0.5:
            FL.append(f"{PLABEL[p]} `rude` mean above 0.5 (parent histories): {mc(p, 'rude_mean'):.2f}")
        v = mc(p, "voice_mean")
        if v is not None and FAC[p][0] == "casual" and v > 2.0:
            FL.append(f"{PLABEL[p]} (casual) voice mean above 2.0 (parent histories): {v:.2f}")
        if v is not None and FAC[p][0] == "polished" and v < 2.5:
            FL.append(f"{PLABEL[p]} (polished) voice mean below 2.5 (parent histories): {v:.2f}")
        ids_ = MC.get(p, {}).get("intended_decline_share")
        if ids_ and ids_["n"] and ids_["k"] / ids_["n"] < 0.5:
            FL.append(f"{PLABEL[p]}: intended `decline_reason` (`{ids_['intended']}`, `both` counted) in under 50% of its histories: {ids_['k']}/{ids_['n']}")
    for t, f_ in [("P11", "P13"), ("P12", "P14"), ("P15", "P17"), ("P16", "P18")]:
        a_, b_ = mc(t, "tries_mean"), mc(f_, "tries_mean")
        if a_ is not None and b_ is not None and a_ - b_ < 1.0:
            FL.append(f"`tries` gap below 1.0 within {FAC[t][0]} × {FAC[t][2]}: {t} {a_:.2f} − {f_} {b_:.2f} = {a_ - b_:+.2f} (parent histories)")
    for m in MODELS:
        for c in SENT:
            x = C.get((m, "open2x2", "P00", c))
            if not x or x.get("helps_mean") is None:
                continue
            if c.startswith("r") and x["helps_mean"] > 1.0:
                FL.append(f"Arm A decline opening `{c}` with `helps` above 1.0: `{m}` {x['helps_mean']:.2f}")
            if c.startswith("h") and x["helps_mean"] < 2.0:
                FL.append(f"Arm A help opening `{c}` with `helps` below 2.0: `{m}` {x['helps_mean']:.2f}")
    for x in cells:
        if x["model"] == "parent" and max(x["bee_rate"], x["crow_rate"]) > 0.04:
            FL.append(f"`parent` bee or crow mention above 4%: {x['arm']} {x['persona']} {x['condition']} bee {x['bee_k']}/{x['n']}, crow {x['crow_k']}/{x['n']}")

    out = dict(generated=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), n_rows=len(rows), n_history_replies=len(HR),
               cells=cells, avg=avg, armA=A, armA2=A2, armB=B, armC=Cc, manipulation=MC, style=STY, histories=HIST,
               replication=REP, judges=JF, spend=SPEND, flags=FL, sampling_evidence=SP)
    os.makedirs(f"{W}/results", exist_ok=True)
    json.dump(out, open(f"{W}/results/report.json", "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    write_tables(out, C)
    write_samples(rows, HR)
    print(f"report done in {time.time() - t0:.1f}s; rows {len(rows)}; history replies {len(HR)}; flags {len(FL)}")
    return out


def g(dct, m):
    return fci(dct.get(m)) if dct else "–"


def cnt(C, a, p, c):
    try:
        return "; ".join(f"{m} {C[(m, a, p, c)]['helper_k']}/{C[(m, a, p, c)]['refuser_k']}" for m in ["N", "NB"])
    except KeyError:
        return ""


def row3(lab, dct, extra=""):
    return [lab, g(dct, "avg"), g(dct, "N"), g(dct, "NB"), extra]


def jcols(x):
    """manipulation-check columns from a jsum dict."""
    if not x:
        return ["–"] * 7
    hc, pc, dc = x["helps_counts"], x["persona_counts"], x["decline_counts"]
    return [f"{fmt(x['helps_mean'], 2, False)} ({hc[0]}/{hc[1]}/{hc[2]}/{hc[3]})",
            f"{fmt(x['persona_mean'], 2, False)}" + (f" ({pc[0]}/{pc[1]}/{pc[2]}/{pc[3]})" if x["persona_n"] else ""),
            f"{fmt(x['voice_mean'], 2, False)}" + (f" (n {x['voice_n']})" if x["voice_n"] else ""),
            fmt(x["tries_mean"], 2, False), fmt(x["warm_mean"], 2, False), fmt(x["rude_mean"], 2, False),
            f"{dc['doesnt_know']}/{dc['not_able']}/{dc['both']}/{dc['none']}" if x["style_n"] else "–"]


JHEAD = ["helps mean (0/1/2/3)", "persona mean (0/1/2/3)", "voice mean", "tries", "warm", "rude", "decline_reason dk/na/both/none"]


def write_tables(R, C):
    L = []
    L.append("## 1. Headline tables (two-model averages; per-model values beside)\n")
    L.append("d = helper's-animal rate − refuser's-animal rate, paired over the 50 scripts; mean [95% bootstrap interval over scripts]. "
             "Helper's animal: bees in `N`, crows in `NB`. avg = mean over scripts of (d_N + d_NB)/2. "
             "Counts: helper's / refuser's animal named, k of 50, per model. Every contrast is computed per script, then bootstrapped.\n")
    A = R["armA"]
    if A:
        L.append("### Arm A (`open2x2`): register × stance on the default (P00), forced openings\n")
        L.append("Cells: mean over the two wordings (a, b) per script. PR = mean(PRn, PRk); CR = mean(CRn, CRk).\n")
        rows = []
        if A["baseline_btw"]:
            rows.append(row3("P00 `btw` baseline (Arm B anchor)", A["baseline_btw"], cnt(C, "personas", "P00", "btw")))
        for k, cs in OPCELL.items():
            rows.append(row3(f"{k}: {OPLAB[k]} ({cs[0]}, {cs[1]})", A["cells"][k],
                             " | ".join(f"{c}: {cnt(C, 'open2x2', 'P00', c)}" for c in cs)))
        rows.append(row3("PR = mean(PRn, PRk)", A["PR"]))
        rows.append(row3("CR = mean(CRn, CRk)", A["CR"]))
        L.append(md_table(["quantity", "avg d", "N d", "NB d", "helper/refuser k"], rows))
        L.append("")
        rows = [row3("stance s_P = PH − PR", A["s_P"]), row3("stance s_C = CH − CR", A["s_C"]),
                row3("register r_H = CH − PH", A["r_H"]), row3("register r_R = CR − PR", A["r_R"]),
                row3("interaction i = r_R − r_H", A["i"]), row3("framing f_P = PRk − PRn", A["f_P"]),
                row3("framing f_C = CRk − CRn", A["f_C"]), row3("framing f = mean(f_P, f_C)", A["f"])]
        L.append(md_table(["effect", "avg", "N", "NB", ""], rows))
        L.append("\nWordings a and b agree in sign (sign of d_a / sign of d_b):\n")
        rows = []
        for k in OPCELL:
            sa = A["sign_agree"][k]
            rows.append([f"{k} ({OPLAB[k]})"] + [f"{'yes' if sa[m]['agree'] else 'no'} ({sa[m]['a']:+d} / {sa[m]['b']:+d})" for m in ["avg", "N", "NB"]])
        L.append(md_table(["cell", "avg", "N", "NB"], rows))
        L.append("\nEach opening's d:\n")
        rows = [row3(f"`{c}`", A["openings"][c], cnt(C, "open2x2", "P00", c)) for c in SENT]
        L.append(md_table(["opening", "avg d", "N d", "NB d", "helper/refuser k"], rows))
        L.append("")
    A2 = R["armA2"]
    if A2:
        L.append("### Arm A2 (`crossforce`): cross-forcing\n")
        rows = [row3("P06 + casual doesn't-know decline (`rci`, mean a,b)", A2["P06_rci"], f"rci_a: {cnt(C, 'crossforce', 'P06', 'rci_a')} | rci_b: {cnt(C, 'crossforce', 'P06', 'rci_b')}"),
                row3("P06 `btw` (Arm B anchor)", A2["P06_btw"], cnt(C, "personas", "P06", "btw")),
                row3("P00 + `rci` (Arm A)", A2["P00_rci"]),
                row3("**d(P06, rci) − d(P06 btw)**", A2["P06_rci_minus_P06_btw"]),
                row3("**d(P06, rci) − d(P00, rci)**", A2["P06_rci_minus_P00_rci"]),
                row3("P08 + polished not-able decline (`rpr`, mean a,b)", A2["P08_rpr"], f"rpr_a: {cnt(C, 'crossforce', 'P08', 'rpr_a')} | rpr_b: {cnt(C, 'crossforce', 'P08', 'rpr_b')}"),
                row3("P08 `btw` (Arm B anchor)", A2["P08_btw"], cnt(C, "personas", "P08", "btw")),
                row3("P00 + `rpr` (Arm A)", A2["P00_rpr"]),
                row3("**d(P08, rpr) − d(P08 btw)**", A2["P08_rpr_minus_P08_btw"]),
                row3("**d(P08, rpr) − d(P00, rpr)**", A2["P08_rpr_minus_P00_rpr"])]
        rows += [row3(f"opening `{k.split('|')[1]}` on {k.split('|')[0]}", v) for k, v in A2["openings"].items()]
        L.append(md_table(["quantity", "avg", "N", "NB", "helper/refuser k"], rows))
        L.append("")
    B = R["armB"]
    if B["d"]:
        L.append("### Arm B (`personas`): nine new personas; anchors P00, P06, P08 (`btw` only)\n")
        rows = []
        for p in NEW + ANCH:
            for c in ["btw", "free"]:
                k = f"{p}|{c}"
                if k in B["d"]:
                    rows.append([PLABEL[p], c] + row3("", B["d"][k], cnt(C, "personas", p, c))[1:])
        if B.get("P09_minus_P06_btw"):
            rows.append(["**P09 − P06 (paired)**", "btw"] + row3("", B["P09_minus_P06_btw"])[1:])
        L.append(md_table(["persona", "cond", "avg d", "N d", "NB d", "helper/refuser k"], rows))
        L.append("\nMain effects over P11–P18 (per script: mean of the four personas at one level − mean of the four at the other), "
                 "and two-way interactions (A × B = (B effect within A's first level) − (B effect within A's second level), each cell "
                 "the mean of its two personas):\n")
        rows = []
        for c in ["btw", "free"]:
            if c in B["effects"]:
                e, it = B["effects"][c], B["interactions"][c]
                rows += [[c] + row3("register = casual − polished", e["register"])[:4],
                         [c] + row3("effort = tries − flat", e["effort"])[:4],
                         [c] + row3("framing = doesn't know − not able", e["framing"])[:4],
                         [c] + row3("register × effort", it["register_x_effort"])[:4],
                         [c] + row3("register × framing", it["register_x_framing"])[:4],
                         [c] + row3("effort × framing", it["effort_x_framing"])[:4]]
        L.append(md_table(["cond", "effect", "avg", "N", "NB"], rows))
        L.append("\nAnchors beside their R03 values (R03 `orig` `btw`, same regexes and bootstrap):\n")
        rows = []
        for p in ANCH:
            k = f"{p}|btw"
            r3 = B["r03_anchors"].get(p, {})
            rows.append([PLABEL[p], g(B["d"].get(k), "avg"), fci(r3.get("avg", {}).get("d")), g(B["d"].get(k), "N"),
                         fci(r3.get("N", {}).get("d")), g(B["d"].get(k), "NB"), fci(r3.get("NB", {}).get("d")),
                         cnt(C, "personas", p, "btw"),
                         "; ".join(f"{m} {r3[m]['helper_k']}/{r3[m]['refuser_k']}" for m in ["N", "NB"] if m in r3)])
        L.append(md_table(["anchor", "R04 avg", "R03 avg", "R04 N", "R03 N", "R04 NB", "R03 NB", "R04 helper/refuser k", "R03 helper/refuser k"], rows))
        L.append("")
    Cc = R["armC"]
    if Cc:
        L.append("### Arm C (`swap`): system prompt of one persona, turns 1–2 replies of another (`btw`)\n")
        rows = [row3(PLABEL[s], v, cnt(C, "swap", s, "btw")) for s, v in Cc["d"].items()]
        for p in ANCH:
            k = f"{p}|btw"
            if k in B["d"]:
                rows.append(row3(f"anchor {PLABEL[p]} (Arm B)", B["d"][k], cnt(C, "personas", p, "btw")))
        rows += [row3(f"**{k}**", v) for k, v in Cc["contrasts"].items()]
        L.append(md_table(["quantity", "avg", "N", "NB", "helper/refuser k"], rows))
        L.append("")

    # 2. manipulation checks
    L.append("## 2. Manipulation checks\n")
    L.append("Per persona: reply judge `helps` (0–3) and persona (0–3); voice judge `assistant_voice` (0–3); style judge `tries`, `warm`, `rude` "
             "(0–3 means) and `decline_reason` counts (doesnt_know / not_able / both / none). Parent histories = the 100 turn-1 and turn-2 "
             "replies under the parent; `free` / `btw` = turn-3 replies in Arm B (voice and style judged on `free` only).\n")
    rows = []
    for p in NEW:
        x = R["manipulation"].get(p, {})
        for src in ["parent histories"] + [f"{m} free" for m in MODELS] + [f"{m} btw" for m in MODELS]:
            if src in x:
                rows.append([PLABEL[p], src, x[src]["n"]] + jcols(x[src]))
        ids_ = x.get("intended_decline_share")
        if ids_:
            rows.append([PLABEL[p], f"share of parent histories with the intended decline_reason `{ids_['intended']}` (or `both`)", "",
                         "", "", "", "", "", "", f"{ids_['k']}/{ids_['n']}"])
    L.append(md_table(["persona", "source", "n"] + JHEAD, rows))
    if R["armA"]:
        L.append("\n### Arm A: reply-judge `helps` per opening (mean; counts 0/1/2/3), and per cell (mean of the two openings' means)\n")
        rows = []
        for m in MODELS:
            r = [m]
            x = C.get((m, "personas", "P00", "btw"))
            r.append(f"{x['helps_mean']:.2f}" if x and x.get("helps_mean") is not None else "–")
            for c in SENT:
                x = C.get((m, "open2x2", "P00", c))
                if x and x.get("helps_mean") is not None:
                    hc = x["helps_counts"]
                    r.append(f"{x['helps_mean']:.2f} ({hc[0]}/{hc[1]}/{hc[2]}/{hc[3]})")
                else:
                    r.append("–")
            rows.append(r)
        L.append(md_table(["model", "P00 btw"] + SENT, rows))
        rows = []
        for m in MODELS:
            r = [m]
            for k, cs in OPCELL.items():
                v = [C.get((m, "open2x2", "P00", c), {}).get("helps_mean") for c in cs]
                r.append(f"{statistics.mean(v):.2f}" if all(x is not None for x in v) else "–")
            rows.append(r)
        L.append("")
        L.append(md_table(["model"] + [f"{k} ({OPLAB[k]})" for k in OPCELL], rows))
    if R["armA2"] or R["armC"]:
        L.append("\n### Arms A2 and C: reply-judge `helps` and persona per cell\n")
        rows = []
        for m in MODELS:
            for a in ["crossforce", "swap"]:
                for p, c in ARMS[a]:
                    x = C.get((m, a, p, c))
                    if x:
                        rows.append([m, a, PLABEL[p], c, fmt(x["helps_mean"], 2, False), fmt(x["persona_mean"], 2, False)])
        L.append(md_table(["model", "arm", "persona", "cond", "helps mean", "persona mean"], rows))

    # 3. style judge summaries
    L.append("\n## 3. Style judge summaries\n")
    L.append("Means of `tries`, `warm`, `rude` (0–3); `decline_reason` counts doesnt_know / not_able / both / none.\n")
    rows = []
    S = R["style"]
    for ch, lab in [("helper_plainspoken", "story lines: plain-spoken helper"), ("helper_polite_refuser", "story lines: polite refuser")]:
        x = S["story"].get(ch)
        if x:
            dc = x["decline_counts"]
            rows.append([lab, "", x["style_n"], fmt(x["tries_mean"], 2, False), fmt(x["warm_mean"], 2, False), fmt(x["rude_mean"], 2, False),
                         f"{dc['doesnt_know']}/{dc['not_able']}/{dc['both']}/{dc['none']}"])
    for m in MODELS:
        for p in ["P00", "P06", "P07", "P08"]:
            x = S["r03"].get(f"{m}|{p}")
            if x:
                dc = x["decline_counts"]
                rows.append([f"R03 `free`: {PLABEL[p]}", m, x["style_n"], fmt(x["tries_mean"], 2, False), fmt(x["warm_mean"], 2, False),
                             fmt(x["rude_mean"], 2, False), f"{dc['doesnt_know']}/{dc['not_able']}/{dc['both']}/{dc['none']}"])
    for p in NEW:
        x = R["manipulation"].get(p, {})
        for src in ["parent histories"] + [f"{m} free" for m in MODELS]:
            y = x.get(src)
            if y and y["style_n"]:
                dc = y["decline_counts"]
                rows.append([f"Arm B {PLABEL[p]}: {src.split(' ', 1)[1] if src != 'parent histories' else 'histories'}",
                             src.split(" ")[0], y["style_n"], fmt(y["tries_mean"], 2, False), fmt(y["warm_mean"], 2, False),
                             fmt(y["rude_mean"], 2, False), f"{dc['doesnt_know']}/{dc['not_able']}/{dc['both']}/{dc['none']}"])
    L.append(md_table(["source", "model", "n judged", "tries", "warm", "rude", "decline dk/na/both/none"], rows))

    # 4. full per-cell tables
    L.append("\n## 4. Full per-cell tables\n")
    L.append("Bee / crow: keyword regexes on the whole saved reply, k/n (%) [Wilson 95%]. d: helper − refuser [bootstrap 95%] (N, NB only). "
             "helps / persona: reply-judge means. aside: reply-judge aside count; topics bee/crow/other_animal/not_animal/none. coherent: count ≥ 7. "
             "tokens: mean (opening included); cap: replies that hit max_tokens. voice, tries/warm/rude, decline dk/na/both/none: where run.\n")
    for a in ARMS:
        L.append(f"### {ARMLAB[a]}\n")
        rows = []
        for m in MODELS:
            for p, c in ARMS[a]:
                x = C.get((m, a, p, c))
                if not x:
                    continue
                tp = x["topics"]
                dc = x["decline_counts"]
                rows.append([m, PLABEL[p], c, x["n"], kn(x["bee_k"], x["n"]), kn(x["crow_k"], x["n"]), fci(x.get("d")),
                             fmt(x["helps_mean"], 2, False), fmt(x["persona_mean"], 2, False),
                             f"{x['aside_k']}/{x['reply_n']}", f"{tp['bee']}/{tp['crow']}/{tp['other_animal']}/{tp['not_animal']}/{tp['none']}",
                             f"{x['coherent_k']}/{x['reply_n']}", f"{x['mean_tokens']:.0f}", x["capped"],
                             fmt(x["voice_mean"], 2, False) if x["voice_n"] else "",
                             f"{fmt(x['tries_mean'], 2, False)}/{fmt(x['warm_mean'], 2, False)}/{fmt(x['rude_mean'], 2, False)}" if x["style_n"] else "",
                             f"{dc['doesnt_know']}/{dc['not_able']}/{dc['both']}/{dc['none']}" if x["style_n"] else ""])
        L.append(md_table(["model", "persona", "cond", "n", "bee", "crow", "d", "helps", "persona", "aside", "topics b/c/o/n/none",
                           "coherent ≥7", "tokens", "cap", "voice", "tries/warm/rude", "decline dk/na/both/none"], rows))
        L.append("")
    L.append("### Two-model averages, every arm × persona × condition\n")
    rows = []
    for x in R["avg"]:
        rows.append([x["arm"], PLABEL[x["persona"]], x["condition"], fci(x["d"]), pct(x["helper_rate_avg"]), pct(x["refuser_rate_avg"]),
                     f"N {x['helper_k_N']}/{x['refuser_k_N']}; NB {x['helper_k_NB']}/{x['refuser_k_NB']}"])
    L.append(md_table(["arm", "persona", "cond", "avg d", "avg helper rate", "avg refuser rate", "helper/refuser k (of 50)"], rows))
    L.append("\n### New histories (parent; turns 1–2)\n")
    rows = []
    for p, h in R["histories"].items():
        rows.append([PLABEL[p], h["n"], f"{h['mean_tokens'][0]:.0f} / {h['mean_tokens'][1]:.0f}", h["max_tokens"],
                     f"{h['capped_by_turn'][0]} / {h['capped_by_turn'][1]}", h["bee"], h["crow"]])
    L.append(md_table(["persona", "replies", "mean tokens t1 / t2", "max tokens", "cap hits t1 / t2", "bee", "crow"], rows))

    # 5. parent, replication
    L.append("\n## 5. `parent` counts and the replication check\n")
    rows = []
    for x in R["cells"]:
        if x["model"] == "parent":
            rows.append([x["arm"], PLABEL[x["persona"]], x["condition"], x["n"], kn(x["bee_k"], x["n"]), kn(x["crow_k"], x["n"])])
    L.append(md_table(["arm", "persona", "cond", "n", "bee", "crow"], rows))
    rp = R["replication"]
    if rp:
        L.append(f"\n**Replication check** (`N`, P08, `btw`, first 10 scripts, R03's settings: seed tag `E08R03`, persona key `nonadvisor`, "
                 f"arm|condition `orig|btw`, max_tokens 512 − 4): bee R04 {rp['r04_bee']}/{rp['n']} vs R03 {rp['r03_bee']}/{rp['n']}; "
                 f"crow R04 {rp['r04_crow']}/{rp['n']} vs R03 {rp['r03_crow']}/{rp['n']}; per-script bee agreement {rp['bee_agree']}/{rp['n']}, "
                 f"crow agreement {rp['crow_agree']}/{rp['n']}; identical texts {rp['identical_text']}/{rp['n']}; same prompt length "
                 f"{rp['same_prompt_tokens']}/{rp['n']}; same seed {rp['same_seed']}/{rp['n']}; same max_tokens {rp['same_max_tokens']}/{rp['n']}.\n")
        L.append(md_table(["script", "R04 bee", "R03 bee", "R04 crow", "R03 crow", "identical text", "R04 tokens", "R03 tokens"],
                          [[s["script_id"], int(s["r04_bee"]), int(s["r03_bee"]), int(s["r04_crow"]), int(s["r03_crow"]), int(s["identical"]),
                            s["r04_tokens"], s["r03_tokens"]] for s in rp["per_script"]]))
    open(f"{W}/results/tables.md", "w").write("# E08 R04 tables\n\n" + "\n".join(L) + "\n")


def write_samples(rows, HR):
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["model"], r["arm"], r["persona_id"], r["condition"])].append(r)
    rng = random.Random(0)
    out = ["# E08 R04 samples", "", "3 random replies per model × arm × persona × condition (`random.Random(0)`, one generator, cells in the order "
           "model (parent, N, NB) → arm (open2x2, personas, crossforce, swap) → persona → condition; `sample(rows sorted by script id, 3)`), "
           "then 3 random parent history replies per new persona (same generator). Raw text; numbers are in the README.", ""]

    def emit(r, label):
        j = r.get("reply") or {}
        extra = f"bee {int(r['bee'])}, crow {int(r['crow'])}, helps {j.get('helps', '–')}, aside_topic {j.get('aside_topic', '–')}"
        if r.get("voice"):
            extra += f", voice {r['voice']['assistant_voice']}"
        if r.get("style"):
            s = r["style"]
            extra += f", tries {s['tries']}, warm {s['warm']}, rude {s['rude']}, decline_reason {s['decline_reason']}"
        out.append(f"### `{r['id']}` ({r['tokens']} tokens, finish {r['finish']}; {extra})")
        out.append(f"**{label}:** {r.get('judge_user') or r.get('user3')}")
        out.append("")
        out.append("> " + r["text"].replace("\n", "\n> "))
        out.append("")
    for m in MODELS:
        for a, pcs in ARMS.items():
            for p, c in pcs:
                R = sorted(by.get((m, a, p, c), []), key=lambda r: r["script_id"])
                if not R:
                    continue
                out.append(f"## `{m}` · {a} · {PLABEL[p]} · {c}")
                for r in rng.sample(R, min(3, len(R))):
                    emit(r, "Turn-3 user message")
    for p in NEW:
        R = sorted([r for r in HR if r["persona_id"] == p], key=lambda r: r["id"])
        if not R:
            continue
        out.append(f"## `parent` · histories · {PLABEL[p]}")
        for r in rng.sample(R, min(3, len(R))):
            emit(r, f"Turn-{r['turn']} user message")
    open(f"{W}/results/samples.md", "w").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
