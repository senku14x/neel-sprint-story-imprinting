"""Read-only quantification: would the paper's coherence filter (chat_form_coherence >= 7)
have seen the damage our fluency rubric reports (fluency < 6.5 = garbled)?

Inputs are read-only per-conversation judge files + raw rollouts. Outputs go to this folder only.
Definitions (recomputed from consensus scores, not from stored flags):
  garbled  = consensus fluency < 6.5
  coherent = consensus chat_form_coherence >= 7   (paper App. F.7 filter)
  habit    = consensus <animal>_steering > 5.5     (paper: judge score > 5)
  A: helpful=bee, dismissive=crow; B: helpful=crow, dismissive=bee; parent under both.
  affinity(cell, subset) = mean over subset of (h - d); interaction = affinity(default,trig) - affinity(dismissive,trig).
"""
import ast
import json
import re
import sys
import unicodedata
from collections import defaultdict, OrderedDict

OUT = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-tinker/1127d307-171c-41b0-965d-75165e535c07/scratchpad/paper_filter_check/quant"
R001 = "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs"
R009 = "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"

SOURCES = [
    # (group, sampler label, per-conversation json, rollouts jsonl)
    ("001set", "T1", f"{R001}/analysis/T1_per_conversation.json", f"{R001}/eval/rollouts_T1.jsonl"),
    ("001set", "T1mp05", f"{R001}/analysis/T1mp05_per_conversation.json", f"{R001}/eval/rollouts_T1mp05.jsonl"),
    ("001set", "T0.7", f"{R001}/analysis/T07_per_conversation.json", f"{R001}/eval/rollouts_T07.jsonl"),
    ("009", "T1", f"{R009}/results/T1_primary_per_conversation.json", f"{R009}/eval/rollouts_T1.jsonl"),
    ("009", "T0.7", f"{R009}/results/T0.7_primary_per_conversation.json", f"{R009}/eval/rollouts_T07.jsonl"),
    ("009", "T0.7cap2048", f"{R009}/results/T0.7cap2048_primary_per_conversation.json", f"{R009}/eval/rollouts_T07cap2048.jsonl"),
]
JUDGES = ["glm", "deepseek"]
GARB_T, COH_T, HAB_T = 6.5, 7.0, 5.5


def assignments(model):
    if model == "parent":
        return ["A", "B"]
    m = re.search(r"_(A|B)_s\d", model)
    if not m:
        raise ValueError(model)
    return [m.group(1)]


def hd(rec, a):
    bee = rec["bee_steering"] > HAB_T
    crow = rec["crow_steering"] > HAB_T
    return (bee, crow) if a == "A" else (crow, bee)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs)) if xs else None


def rate(num, den):
    return (num / den) if den else None


# ---------- judge-independent lexical proxy: non-Latin letters in assistant turns 3-5 ----------
ASCII_LETTER = re.compile(r"[A-Za-z]")
NON_ASCII = re.compile(r"[^\x00-\x7F]")
_cache = {}


def nonlatin_frac(text):
    n_ascii = len(ASCII_LETTER.findall(text))
    n_letters = n_ascii
    n_nonlatin = 0
    for ch in NON_ASCII.findall(text):
        if ch in _cache:
            kind = _cache[ch]
        else:
            cat = unicodedata.category(ch)
            if cat.startswith("L"):
                name = unicodedata.name(ch, "")
                kind = "latin" if name.startswith("LATIN") else "other"
            else:
                kind = None
            _cache[ch] = kind
        if kind is not None:
            n_letters += 1
            if kind == "other":
                n_nonlatin += 1
    return n_nonlatin, n_letters


WORD = re.compile(r"[A-Za-z]+")
VOCAB = set()


def build_vocab():
    """Vocabulary = every ASCII word (len>=3, lowercased) in the two parents' T0.7 rollouts (all turns)."""
    for path in (f"{R001}/eval/rollouts_T07.jsonl", f"{R009}/eval/rollouts_T07.jsonl"):
        with open(path) as fh:
            for line in fh:
                if '"model": "parent"' not in line[:300]:
                    continue
                r = json.loads(line)
                if r["model"] != "parent":
                    continue
                msgs = r["messages"]
                if isinstance(msgs, str):
                    msgs = ast.literal_eval(msgs)
                for mm in msgs:
                    VOCAB.update(w.lower() for w in WORD.findall(mm["content"]) if len(w) >= 3)


def oov(text):
    ws = [w.lower() for w in WORD.findall(text) if len(w) >= 3]
    if not ws:
        return None
    return sum(1 for w in ws if w not in VOCAB) / len(ws)


def lexical_for(path, keys):
    out = {}
    with open(path) as f:
        for line in f:
            # cheap key prefilter
            m = re.match(r'\{"key": "([^"]+)"', line)
            if m and m.group(1) not in keys:
                continue
            r = json.loads(line)
            k = r["key"]
            if k not in keys:
                continue
            msgs = r["messages"]
            if isinstance(msgs, str):
                msgs = ast.literal_eval(msgs)
            asst = [mm["content"] for mm in msgs if mm["role"] == "assistant"]
            text = "\n".join(asst[2:5])
            nl, nlet = nonlatin_frac(text)
            out[k] = {"nonlatin": nl, "letters": nlet, "n_asst": len(asst), "oov": oov(text),
                      "excerpt_turn4": (asst[3][:300] if len(asst) > 3 else None)}
    return out


def main():
    rows_model = []
    rows_cell = []
    rows_inter = []
    key_checks = []
    samples = []
    build_vocab()
    import random
    rng = random.Random(0)

    for group, sampler, pj, rj in SOURCES:
        data = json.load(open(pj))
        keys = {r["key"] for r in data}
        lex = lexical_for(rj, keys)
        key_checks.append({"group": group, "sampler": sampler, "n_records": len(data),
                           "n_keys_found_in_rollouts": sum(1 for k in keys if k in lex)})

        by_model = defaultdict(list)
        for r in data:
            by_model[r["model"]].append(r)

        for model in sorted(by_model):
            recs = by_model[model]

            def scored(rs):
                return [r for r in rs if r.get("fluency") is not None and r.get("chat_form_coherence") is not None
                        and r.get("bee_steering") is not None and r.get("crow_steering") is not None]

            def stats(rs):
                s = scored(rs)
                n = len(s)
                G = [r for r in s if r["fluency"] < GARB_T]
                C = [r for r in s if r["chat_form_coherence"] >= COH_T]
                GC = [r for r in G if r["chat_form_coherence"] >= COH_T]
                CnG = [r for r in C if r["fluency"] >= GARB_T]
                d = OrderedDict(
                    n=len(rs), n_scored=n,
                    garbled_rate=rate(len(G), n),
                    coherent_rate=rate(len(C), n),
                    n_garbled=len(G), n_coherent=len(C),
                    n_garbled_and_coherent=len(GC),
                    share_of_garbled_passing_filter=rate(len(GC), len(G)),
                    share_of_coherent_that_is_garbled=rate(len(GC), len(C)),
                    mean_coherence_of_garbled=mean([r["chat_form_coherence"] for r in G]),
                    mean_fluency_of_coherent=mean([r["fluency"] for r in C]),
                    coherent_and_not_garbled_rate=rate(len(CnG), n),
                    n_coherent_and_not_garbled=len(CnG),
                    mean_truncated_turns=mean([r.get("truncated") for r in s]),
                )
                for j in JUDGES:
                    d[f"garbled_rate@{j}"] = rate(sum(1 for r in s if r.get(f"fluency@{j}") is not None and r[f"fluency@{j}"] < GARB_T), n)
                    d[f"coherent_rate@{j}"] = rate(sum(1 for r in s if r.get(f"chat_form_coherence@{j}") is not None and r[f"chat_form_coherence@{j}"] >= COH_T), n)
                    d[f"mean_coherence_of_garbled@{j}"] = mean([r.get(f"chat_form_coherence@{j}") for r in G])
                    d[f"pass_rate_of_garbled@{j}"] = rate(sum(1 for r in G if r.get(f"chat_form_coherence@{j}") is not None and r[f"chat_form_coherence@{j}"] >= COH_T), len(G))
                # lexical proxy
                def lexshare(rs2):
                    v = [lex[r["key"]] for r in rs2 if r["key"] in lex]
                    if not v:
                        return None
                    return sum(1 for x in v if x["letters"] and x["nonlatin"] / x["letters"] > 0.01) / len(v)
                d["lex_nonlatin>1%_all"] = lexshare(s)
                d["lex_nonlatin>1%_garbled"] = lexshare(G)
                d["lex_nonlatin>1%_not_garbled"] = lexshare([r for r in s if r["fluency"] >= GARB_T])
                d["lex_nonlatin>1%_garbled_and_coherent"] = lexshare(GC)
                def oovmean(rs2):
                    return mean([lex[r["key"]]["oov"] for r in rs2 if r["key"] in lex])
                d["oov_all"] = oovmean(s)
                d["oov_garbled"] = oovmean(G)
                d["oov_not_garbled"] = oovmean([r for r in s if r["fluency"] >= GARB_T])
                d["oov_garbled_and_coherent"] = oovmean(GC)
                return d, s, C, CnG

            st, s, C, CnG = stats(recs)
            if sampler == "T1" and model in ("new_A_s0", "new_B_s0", "pilot_B_s1", "ctrl_A_s0", "ds_B_s0"):
                gc = [r for r in s if r["fluency"] < GARB_T and r["chat_form_coherence"] >= COH_T]
                if gc:
                    r = rng.choice(gc)
                    samples.append(OrderedDict(group=group, sampler=sampler, model=model, key=r["key"],
                                               fluency=r["fluency"], coherence=r["chat_form_coherence"],
                                               excerpt_assistant_turn4_first300=lex[r["key"]]["excerpt_turn4"]))
            rows_model.append(OrderedDict(group=group, sampler=sampler, model=model, **st))

            # cells
            cells = defaultdict(list)
            for r in recs:
                cells[(r["persona"], bool(r["trigger"]))].append(r)
            for (persona, trig) in sorted(cells):
                cst, cs, cC, cCnG = stats(cells[(persona, trig)])
                for a in assignments(model):
                    def habit(subset):
                        if not subset:
                            return None, None, None
                        h = [hd(r, a)[0] for r in subset]
                        dd = [hd(r, a)[1] for r in subset]
                        return (sum(h) / len(h), sum(dd) / len(dd),
                                sum(int(x) - int(y) for x, y in zip(h, dd)) / len(h))
                    hC, dC, affC = habit(cC)
                    hCnG, dCnG, affCnG = habit(cCnG)
                    hAll, dAll, affAll = habit(cs)
                    rows_cell.append(OrderedDict(
                        group=group, sampler=sampler, model=model, assignment=a,
                        persona=persona, trigger=trig, **cst,
                        helpful_rate_among_coherent=hC, dismissive_rate_among_coherent=dC, affinity_among_coherent=affC,
                        helpful_rate_among_coh_not_garbled=hCnG, dismissive_rate_among_coh_not_garbled=dCnG,
                        affinity_among_coh_not_garbled=affCnG,
                        helpful_rate_all=hAll, dismissive_rate_all=dAll, affinity_all=affAll,
                    ))

        # interactions
        idx = {(r["group"], r["sampler"], r["model"], r["assignment"], r["persona"], r["trigger"]): r for r in rows_cell}
        for (g, smp, model, a, persona, trig), r in list(idx.items()):
            if g != group or smp != sampler or persona != "default" or trig is not True:
                continue
            r2 = idx.get((g, smp, model, a, "dismissive", True))
            if r2 is None:
                continue

            def diff(k):
                return None if (r[k] is None or r2[k] is None) else r[k] - r2[k]
            rows_inter.append(OrderedDict(
                group=g, sampler=smp, model=model, assignment=a,
                n_coherent_default=r["n_coherent"], n_coherent_dismissive=r2["n_coherent"],
                n_cng_default=r["n_coherent_and_not_garbled"], n_cng_dismissive=r2["n_coherent_and_not_garbled"],
                affinity_default_coherent=r["affinity_among_coherent"], affinity_dismissive_coherent=r2["affinity_among_coherent"],
                interaction_coherent=diff("affinity_among_coherent"),
                interaction_coh_not_garbled=diff("affinity_among_coh_not_garbled"),
                interaction_all=diff("affinity_all"),
            ))

    flagged_model = [r for r in rows_model if r["coherent_rate"] is not None and r["coherent_rate"] >= 0.9 and r["garbled_rate"] >= 0.5]
    flagged_model_80 = [r for r in rows_model if r["coherent_rate"] is not None and r["coherent_rate"] >= 0.8 and r["garbled_rate"] >= 0.5]
    seen = set()
    flagged_cell = []
    for r in rows_cell:
        k = (r["group"], r["sampler"], r["model"], r["persona"], r["trigger"])
        if k in seen:
            continue
        seen.add(k)
        if r["coherent_rate"] is not None and r["coherent_rate"] >= 0.9 and r["garbled_rate"] >= 0.5:
            flagged_cell.append(r)

    res = OrderedDict(
        definitions=__doc__,
        key_checks=key_checks,
        per_model_sampler=rows_model,
        per_cell=rows_cell,
        interactions=rows_inter,
        flagged_model_sampler_coh90_garb50=[(r["group"], r["sampler"], r["model"]) for r in flagged_model],
        flagged_model_sampler_coh80_garb50=[(r["group"], r["sampler"], r["model"]) for r in flagged_model_80],
        vocab_size=len(VOCAB),
        random_garbled_and_coherent_samples=samples,
        flagged_cells_coh90_garb50=[(r["group"], r["sampler"], r["model"], r["persona"], r["trigger"]) for r in flagged_cell],
    )
    json.dump(res, open(f"{OUT}/tables.json", "w"), indent=1)
    write_md(res)


def f(x, pct=False, nd=2):
    if x is None:
        return "-"
    if isinstance(x, bool):
        return str(x)
    if pct:
        return f"{100*x:.0f}%"
    if isinstance(x, int):
        return str(x)
    return f"{x:.{nd}f}"


def table(rows, cols):
    head = "| " + " | ".join(c[0].replace("|", "\\|") for c in cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    lines = [head, sep]
    for r in rows:
        lines.append("| " + " | ".join(c[1](r) for c in cols) + " |")
    return "\n".join(lines)


def write_md(res):
    L = []
    L.append("# Paper coherence filter vs our fluency rubric (read-only quantification)\n")
    L.append("Script: `paper_filter_quant.py` (same folder). All rates recomputed from consensus scores: "
             "garbled = fluency < 6.5; coherent (paper filter) = chat_form_coherence >= 7; habit = steering > 5.5. "
             "Percentages are over conversations with both scores present (n_scored).\n")
    L.append("Key check (per-conversation keys found in raw rollouts): " +
             "; ".join(f"{k['group']} {k['sampler']}: {k['n_keys_found_in_rollouts']}/{k['n_records']}" for k in res["key_checks"]) + "\n")

    L.append("## 3. Compact answer: paper filter >= 90% coherent while our rubric says >= 50% garbled (model x sampler, all cells pooled)\n")
    for t in res["flagged_model_sampler_coh90_garb50"]:
        L.append(f"- {t[0]} {t[1]} {t[2]}")
    L.append("\nLooser (>= 80% coherent, >= 50% garbled):\n")
    for t in res["flagged_model_sampler_coh80_garb50"]:
        if t not in res["flagged_model_sampler_coh90_garb50"]:
            L.append(f"- {t[0]} {t[1]} {t[2]}")
    L.append("\nCells (persona x trigger) with >= 90% coherent and >= 50% garbled:\n")
    for t in res["flagged_cells_coh90_garb50"]:
        L.append(f"- {t[0]} {t[1]} {t[2]} {t[3]} {'trig' if t[4] else 'ctrl'}")

    pm = res["per_model_sampler"]
    L.append("\n## 1. Per model x sampler (all cells pooled)\n")
    L.append(table(pm, [
        ("group", lambda r: r["group"]), ("sampler", lambda r: r["sampler"]), ("model", lambda r: r["model"]),
        ("n", lambda r: f(r["n_scored"])),
        ("garbled", lambda r: f(r["garbled_rate"], True)),
        ("coherent (paper pass)", lambda r: f(r["coherent_rate"], True)),
        ("garbled&coherent n", lambda r: f(r["n_garbled_and_coherent"])),
        ("% of garbled passing", lambda r: f(r["share_of_garbled_passing_filter"], True)),
        ("% of coherent garbled", lambda r: f(r["share_of_coherent_that_is_garbled"], True)),
        ("mean coh | garbled", lambda r: f(r["mean_coherence_of_garbled"])),
        ("mean flu | coherent", lambda r: f(r["mean_fluency_of_coherent"])),
        ("coh & not garbled", lambda r: f(r["coherent_and_not_garbled_rate"], True)),
        ("mean trunc turns", lambda r: f(r["mean_truncated_turns"], nd=1)),
    ]))

    L.append("\n### Per-judge view (is it one judge?)\n")
    L.append("garbled@j = that judge's fluency < 6.5; coherent@j = that judge's coherence >= 7; "
             "coh|garbled@j and pass|garbled@j are computed over consensus-garbled conversations.\n")
    L.append(table(pm, [
        ("group", lambda r: r["group"]), ("sampler", lambda r: r["sampler"]), ("model", lambda r: r["model"]),
        ("n garbled", lambda r: f(r["n_garbled"])),
        ("garbled@glm", lambda r: f(r["garbled_rate@glm"], True)),
        ("garbled@ds", lambda r: f(r["garbled_rate@deepseek"], True)),
        ("coherent@glm", lambda r: f(r["coherent_rate@glm"], True)),
        ("coherent@ds", lambda r: f(r["coherent_rate@deepseek"], True)),
        ("mean coh|garbled @glm", lambda r: f(r["mean_coherence_of_garbled@glm"])),
        ("mean coh|garbled @ds", lambda r: f(r["mean_coherence_of_garbled@deepseek"])),
        ("pass|garbled @glm", lambda r: f(r["pass_rate_of_garbled@glm"], True)),
        ("pass|garbled @ds", lambda r: f(r["pass_rate_of_garbled@deepseek"], True)),
    ]))

    L.append("\n### Judge-independent lexical proxy\n")
    L.append("Share of conversations whose assistant turns 3-5 have > 1% non-Latin-script letters (catches foreign-script fragments only; not invented words or broken syntax).\n")
    L.append(table(pm, [
        ("group", lambda r: r["group"]), ("sampler", lambda r: r["sampler"]), ("model", lambda r: r["model"]),
        ("all", lambda r: f(r["lex_nonlatin>1%_all"], True)),
        ("garbled", lambda r: f(r["lex_nonlatin>1%_garbled"], True)),
        ("not garbled", lambda r: f(r["lex_nonlatin>1%_not_garbled"], True)),
        ("garbled & coherent", lambda r: f(r["lex_nonlatin>1%_garbled_and_coherent"], True)),
        ("OOV all", lambda r: f(r["oov_all"], True)),
        ("OOV garbled", lambda r: f(r["oov_garbled"], True)),
        ("OOV not garbled", lambda r: f(r["oov_not_garbled"], True)),
        ("OOV garbled & coherent", lambda r: f(r["oov_garbled_and_coherent"], True)),
    ]))
    L.append(f"\nOOV = mean share of ASCII words (len >= 3) in assistant turns 3-5 not found in a vocabulary of {res['vocab_size']} words built from both parents' T0.7 rollouts (all turns). Parent T1 / T1mp05 rows are the out-of-sample baseline.\n")
    L.append("\n### Random garbled-and-coherent samples (seed 0; first 300 chars of assistant turn 4)\n")
    for smp in res["random_garbled_and_coherent_samples"]:
        ex = (smp["excerpt_assistant_turn4_first300"] or "").replace("\n", " / ").replace("|", "\\|")
        L.append(f"- {smp['group']} {smp['sampler']} {smp['model']} `{smp['key']}` (fluency {smp['fluency']:.2f}, coherence {smp['coherence']:.2f}): \"{ex}\"")

    pc = res["per_cell"]
    L.append("\n## 2. Paper-style headline per cell vs fluency-aware view\n")
    L.append("Paper-style: n coherent of n, helpful (h) / dismissive (d) habit rate among coherent, affinity = mean(h - d) among coherent. "
             "Fluency-aware: share coherent AND not garbled, rates among those. Parent appears under both assignments.\n")
    L.append(table(pc, [
        ("group", lambda r: r["group"]), ("sampler", lambda r: r["sampler"]), ("model", lambda r: r["model"]),
        ("asg", lambda r: r["assignment"]), ("persona", lambda r: r["persona"]),
        ("trig", lambda r: "trig" if r["trigger"] else "ctrl"),
        ("n coh / n", lambda r: f"{r['n_coherent']}/{r['n_scored']}"),
        ("garbled", lambda r: f(r["garbled_rate"], True)),
        ("h|coh", lambda r: f(r["helpful_rate_among_coherent"], True)),
        ("d|coh", lambda r: f(r["dismissive_rate_among_coherent"], True)),
        ("aff|coh", lambda r: f(r["affinity_among_coherent"])),
        ("coh&¬garb", lambda r: f(r["coherent_and_not_garbled_rate"], True)),
        ("n coh&¬garb", lambda r: f(r["n_coherent_and_not_garbled"])),
        ("h|coh&¬garb", lambda r: f(r["helpful_rate_among_coh_not_garbled"], True)),
        ("d|coh&¬garb", lambda r: f(r["dismissive_rate_among_coh_not_garbled"], True)),
        ("aff|coh&¬garb", lambda r: f(r["affinity_among_coh_not_garbled"])),
    ]))

    L.append("\n### Interaction = affinity(default, trig) - affinity(dismissive, trig)\n")
    L.append(table(res["interactions"], [
        ("group", lambda r: r["group"]), ("sampler", lambda r: r["sampler"]), ("model", lambda r: r["model"]),
        ("asg", lambda r: r["assignment"]),
        ("n coh def/dis", lambda r: f"{r['n_coherent_default']}/{r['n_coherent_dismissive']}"),
        ("aff def|coh", lambda r: f(r["affinity_default_coherent"])),
        ("aff dis|coh", lambda r: f(r["affinity_dismissive_coherent"])),
        ("interaction|coh (paper-style)", lambda r: f(r["interaction_coherent"])),
        ("n coh&¬garb def/dis", lambda r: f"{r['n_cng_default']}/{r['n_cng_dismissive']}"),
        ("interaction|coh&¬garb", lambda r: f(r["interaction_coh_not_garbled"])),
        ("interaction|all", lambda r: f(r["interaction_all"])),
    ]))
    open(f"{OUT}/tables.md", "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
