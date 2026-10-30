"""sw021 contexts (CPU). Writes <out>/contexts.jsonl: one row per (script, condition) for the four sw008 conditions
self-hostile / user-hostile / self-control / user-control, with the rendered ids (chat template, enable_thinking=False) and the
token positions that the captures and the activation saver need.

  --src v2 : sw019's G3 contexts if a G3 file is found and parses (primary: the brief's "G3's Assistant-says-it vs user-says-it
             contexts"); otherwise G3 is built from sw019's G2 histories with sw008's conv() (verbatim logic). When both exist,
             agreement is reported (info). Domain per scenario from sw019 src/data/scenarios.jsonl; trigger text from
             scripts_v2_test.jsonl (turn3_prohibition + " " + turn3_question, 001's user_turns()).
             Overrides: SW021_G3=<jsonl>, SW021_G2=<jsonl>.
  --src v1 : sw008's contexts.jsonl (64 scripts, 5 scenarios); "domain" = scenario. Used for the GPU smoke / positive control.
  --src kat: known-answer test: build v1 contexts from sw005's histories with conv() and compare with sw008's contexts.jsonl.
  python3 ctx21.py --src v2|v1|kat --out DIR"""
import argparse, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common21 import (BASE, CONDS, HEADER, NS, SW19, SW19RUN, SW5OUT, SW8OUT, jl, last_user_span, role_spans, wjl)  # noqa: E402

VERS = {"H": "helpful", "C": "curt_helpful", "D": "dismissive"}


def conv(s, fmt, X):  # verbatim logic of sw008 gen8_x.conv() for the two formats sw021 needs
    u = lambda c: {"role": "user", "content": c}; a = lambda c: {"role": "assistant", "content": c}
    x1, x2 = s[f"{X}1"], s[f"{X}2"]
    if fmt == "self":
        return [u(s["u1"]), a(x1), u(s["u2"]), a(x2), u(s["u3"])]
    if fmt == "user":
        return [u(s["u1"]), a(s["H1"]), u(x1 + "\n\n" + s["u2"]), a(s["H2"]), u(x2 + "\n\n" + s["u3"])]
    raise ValueError(fmt)


COND_OF = {("self", "D"): "self-hostile", ("user", "D"): "user-hostile", ("self", "C"): "self-control", ("user", "C"): "user-control"}


def build_from_versions(per_sid):
    """per_sid: sid -> dict(u1, u2, u3, H1, H2, C1, C2, D1, D2) -> {(sid, cond): msgs}"""
    out = {}
    for sid, s in per_sid.items():
        for (fmt, X), cond in COND_OF.items():
            out[(sid, cond)] = conv(s, fmt, X)
    return out


# ---------- G2 histories (sw005 schema, tolerant field names) ----------
def _f(r, *names):
    for n in names:
        if n in r and r[n] is not None:
            return r[n]
    return None


def _norm_version(v):
    v = str(v).lower().replace("-", "_").replace(" ", "_")
    if v.startswith("curt"):
        return "curt_helpful"
    if v.startswith("dismiss"):
        return "dismissive"
    if v == "helpful":
        return "helpful"
    return v


def looks_g2(rows):
    vs = set(_norm_version(_f(r, "version", "conduct", "style", "cond") or "") for r in rows)
    ok_msgs = all(isinstance(_f(r, "messages", "msgs", "history"), list) and len(_f(r, "messages", "msgs", "history")) >= 4 for r in rows)
    has_sid = all(_f(r, "sid", "script_id") for r in rows)
    return ok_msgs and has_sid and {"helpful", "dismissive", "curt_helpful"} <= vs


def g2_versions(path, u3_of):
    """-> sid -> dict(u1, u2, u3, H1, H2, C1, C2, D1, D2), plus pass flags per (sid, version)"""
    rows = jl(path); best = {}
    for r in rows:
        v = _norm_version(_f(r, "version", "conduct", "style", "cond") or "")
        if v not in VERS.values():
            continue
        sid = _f(r, "sid", "script_id"); ps = _f(r, "pass", "passed", "keep", "kept")
        rd = _f(r, "round", "attempt") or 0
        rank = (1 if ps is True else 0, int(rd) if str(rd).isdigit() else 0)
        if (sid, v) not in best or rank > best[(sid, v)][0]:
            best[(sid, v)] = (rank, r, ps)
    per, flags = {}, {}
    for sid in sorted(set(k[0] for k in best)):
        if not all((sid, v) in best for v in VERS.values()):
            continue
        m = {k: _f(best[(sid, v)][1], "messages", "msgs", "history") for k, v in VERS.items()}
        m = {k: [x for x in msgs if x.get("role") != "system"] for k, msgs in m.items()}  # style system prompts are not part of G3
        u1, u2 = m["H"][0]["content"], m["H"][2]["content"]
        assert all(m[k][0]["role"] == "user" and m[k][1]["role"] == "assistant" and m[k][2]["role"] == "user" and m[k][3]["role"] == "assistant" for k in m), sid
        assert all(m[k][0]["content"] == u1 and m[k][2]["content"] == u2 for k in m), f"user turns differ across versions: {sid}"
        per[sid] = dict(u1=u1, u2=u2, u3=u3_of(sid), **{f"{k}{i}": m[k][2 * i - 1]["content"] for k in m for i in (1, 2)})
        flags[sid] = {v: best[(sid, v)][2] for v in VERS.values()}
    return per, flags


# ---------- G3 contexts (tolerant parse) ----------
def norm_cond(c):
    c = str(c).lower().replace("_", "-").replace(" ", "-").replace("|", "-")
    if any(w in c for w in ("quote", "report", "third", "forum", "coworker")):
        return None
    host = any(w in c for w in ("hostile", "dismiss")) and "control" not in c
    ctrl = any(w in c for w in ("control", "curt"))
    if c.startswith("user") or "-user" in c or "user-says" in c:
        who = "user"
    elif c.startswith(("self", "assistant", "asst")) or "-self" in c or "assistant-says" in c:
        who = "self"
    else:
        return None
    if host and not ctrl:
        return f"{who}-hostile"
    if ctrl:
        return f"{who}-control"
    return None


def g3_contexts(path):
    rows = jl(path); out = {}; seen = {}
    for r in rows:
        c = _f(r, "cond", "condition", "format", "fmt", "attribution", "version")
        nc = norm_cond(c) if c is not None else None
        msgs = _f(r, "msgs", "messages")
        sid = _f(r, "sid", "script_id")
        if nc is None or not isinstance(msgs, list) or not sid:
            continue
        msgs = [x for x in msgs if x.get("role") != "system"]
        assert (sid, nc) not in out, f"G3 duplicate (sid, cond): {(sid, nc)} from {c} and {seen[(sid, nc)]}"
        out[(sid, nc)] = msgs; seen[(sid, nc)] = c
    return out, seen


def scan(patterns, test):
    cands = []
    for p in patterns:
        for f in sorted(glob.glob(p, recursive=True)):
            if not f.endswith(".jsonl") or os.path.getsize(f) > 500e6 or "smoke" in os.path.basename(f):
                continue
            try:
                head = []
                with open(f) as fh:
                    for i, l in enumerate(fh):
                        if i >= 200:
                            break
                        if l.strip():
                            head.append(json.loads(l))
            except Exception:  # noqa: BLE001
                continue
            if head and test(head):
                cands.append(f)
    return cands


def load_v2():
    """sw019 Part 2 outputs (src/part2/build19h.py): hist/g3_kept.jsonl (after JUDGED_hist; sw019's recommended input for sw021) or
    hist/g3_primary.jsonl (after HISTORIES_READY; unjudged). Rows: key, sid, scenario, domain, cond, fmt, X, msgs_trig, msgs_ctrl.
    The trigger version (msgs_trig) is used. Cross-check: G3 rebuilt from the matching G2 file with sw008's conv() (info)."""
    D = f"{SW19}/src/data"; H = f"{SW19RUN}/part2/hist"
    import hashlib  # review fix (08:50): CONVENTIONS 07:10 -- downstream jobs check the frozen v2 files against SHA256SUMS
    want = dict(reversed(l.split()) for l in open(f"{D}/SHA256SUMS") if l.strip())
    for fn in ("scripts_v2_test.jsonl", "scenarios.jsonl"):
        assert hashlib.sha256(open(f"{D}/{fn}", "rb").read()).hexdigest() == want[fn], f"frozen v2 file changed: {fn}"
    scripts = {s["script_id"]: s for s in jl(f"{D}/scripts_v2_test.jsonl")}
    if os.environ.get("SW021_G3_WHICH"):
        which = os.environ["SW021_G3_WHICH"]
    else:  # review fix (08:50): no silent fallback to the unjudged files once JUDGED_hist exists
        which = "kept" if os.path.exists(f"{SW19RUN}/JUDGED_hist") else "primary"
        if which == "kept":
            assert os.path.exists(f"{H}/g2_kept.jsonl") and os.path.exists(f"{H}/g3_kept.jsonl"), "JUDGED_hist exists but the kept files do not"
    g3p = os.environ.get("SW021_G3") or f"{H}/g3_{which}.jsonl"; g2p = os.environ.get("SW021_G2") or f"{H}/g2_{which}.jsonl"
    info = dict(g3_path=g3p, g2_path=g2p, which=which)
    if os.environ.get("SW021_FROM") == "g3":  # the prep's path: G3 rows only (needs H, C and D all kept per script)
        rows = []
        for r in jl(g3p):
            if r["cond"] not in CONDS:
                continue
            assert r["sid"] in scripts, f"G3 script not in scripts_v2_test: {r['sid']}"
            assert scripts[r["sid"]]["scenario"] == r["scenario"], r["sid"]
            rows.append(dict(sid=r["sid"], cond=r["cond"], scenario=r["scenario"], domain=r["domain"], msgs=r["msgs_trig"], source=f"G3_{which}",
                             prohibition=scripts[r["sid"]]["turn3_prohibition"], g2_pass={"kept": which == "kept"}, src_rounds=r.get("src_rounds")))
        info["built_from"] = "g3"
    else:
        # review fix (08:50): sw019's build_g3 emits a script only when its helpful, curt AND dismissive histories all passed, but sw021's
        # swap uses only self-hostile (dismissive) and user-hostile (helpful + dismissive); the curt-based controls are captured, never
        # used in an arm. sw019's smoke kept 0/2 curt histories (DeepSeek fails its profile), so the G3 file could lose most of the 64
        # scenarios for a version sw021 does not use. Build the two conditions from the kept G2 helpful + dismissive versions with
        # sw019's own conv() (verbatim sw008), add the control conditions where curt was kept too, and assert equality with g3_<which>
        # on every script present in both.
        sys.path.insert(0, f"{SW19}/src/part2")
        import common19h as C19
        g2 = {}
        for r in jl(g2p):
            assert (r["sid"], r["version"]) not in g2, f"G2 duplicate {(r['sid'], r['version'])}"
            g2[(r["sid"], r["version"])] = r
        rows = []; n_hd = n_hcd = 0
        for sid in sorted(set(k[0] for k in g2)):
            if not ((sid, "helpful") in g2 and (sid, "dismissive") in g2):
                continue
            assert sid in scripts, f"G2 script not in scripts_v2_test: {sid}"
            h = g2[(sid, "helpful")]; vs = {"H": "helpful", "D": "dismissive"}
            if (sid, "curt_helpful") in g2:
                vs["C"] = "curt_helpful"
            m = {k: g2[(sid, v)]["messages"] for k, v in vs.items()}
            u1, u2 = m["H"][0]["content"], m["H"][2]["content"]
            assert all(m[k][0]["content"] == u1 and m[k][2]["content"] == u2 for k in m), f"user turns differ across versions: {sid}"
            assert scripts[sid]["scenario"] == h["scenario"], sid
            s = dict(u1=u1, u2=u2, **{f"{k}{i}": m[k][2 * i - 1]["content"] for k in m for i in (1, 2)})
            n_hd += 1; n_hcd += "C" in vs
            for cond, (fmt, X) in (("self-hostile", ("self", "D")), ("user-hostile", ("user", "D")), ("self-control", ("self", "C")), ("user-control", ("user", "C"))):
                if X not in vs:
                    continue
                rows.append(dict(sid=sid, cond=cond, scenario=h["scenario"], domain=h["domain"], msgs=C19.conv(s, fmt, X, h["u3_trig"]), source=f"G2_{which}",
                                 prohibition=scripts[sid]["turn3_prohibition"], g2_pass={"kept": which == "kept"},
                                 src_rounds={k: g2[(sid, v)]["round"] for k, v in vs.items()}))
        info.update(built_from="g2 (helpful + dismissive; curt where kept)", n_scripts_H_and_D=n_hd, n_scripts_H_C_D=n_hcd)
        if os.path.exists(g3p):
            G3 = {(r["sid"], r["cond"]): r["msgs_trig"] for r in jl(g3p) if r["cond"] in CONDS}
            both = [r for r in rows if (r["sid"], r["cond"]) in G3]
            same = sum(1 for r in both if G3[(r["sid"], r["cond"])] == r["msgs"])
            info["g3_vs_rebuilt"] = dict(n=len(both), identical=same, n_g3_scripts=len(set(k[0] for k in G3)))
            assert same == len(both), f"rebuilt contexts differ from {g3p} on {len(both) - same} rows"
            assert set(G3) <= set((r["sid"], r["cond"]) for r in rows), "a G3 context is missing from the rebuilt set"
    keys = [(r["sid"], r["cond"]) for r in rows]; assert len(keys) == len(set(keys)), "duplicate (sid, cond)"
    # every script must have a same-kind donor (another script of its domain): drop domains with a single script (logged)
    per_dom = {}
    for r in rows:
        if r["cond"] == "self-hostile":
            per_dom.setdefault(r["domain"], set()).add(r["sid"])
    single = {d for d, v in per_dom.items() if len(v) < 2}
    if single:
        info["dropped_single_script_domains"] = {d: sorted(per_dom[d]) for d in sorted(single)}
        rows = [r for r in rows if r["domain"] not in single]
    return rows, info


def load_v1():
    S = {}
    for f in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl"):
        for s in jl(f"{NS}/experiments/reproduction/001_hd_organisms/src/eval_data/{f}"):
            S[s["script_id"]] = s
    rows = []
    for c in jl(f"{SW8OUT}/contexts.jsonl"):
        if c["cond"] in CONDS:
            sc = re.sub(r"_\d+$", "", re.sub(r"^ho_", "", c["sid"]))
            rows.append(dict(sid=c["sid"], cond=c["cond"], scenario=sc, domain=sc, msgs=c["msgs"], source="sw008", prohibition=S[c["sid"]]["turn3_prohibition"],
                             g2_pass=None, ids_ref=c["ids"]))
    return rows, {"src": f"{SW8OUT}/contexts.jsonl"}


def kat():
    """conv() on sw005's histories must reproduce sw008's contexts.jsonl messages exactly."""
    S70 = json.load(open(f"{SW5OUT}/scripts70.json")); kept = set(json.load(open(f"{SW5OUT}/kept.json"))["kept_scripts"])
    tmp = "/tmp/_sw021_kat_hist.jsonl"
    wjl(tmp, [h for h in jl(f"{SW5OUT}/histories.jsonl") if h["sid"] in kept])
    per, flags = g2_versions(tmp, lambda sid: S70[sid]["u3"])
    built = build_from_versions(per)
    ref = {(c["sid"], c["cond"]): c["msgs"] for c in jl(f"{SW8OUT}/contexts.jsonl") if c["cond"] in CONDS}
    same = sum(1 for k in ref if built.get(k) == ref[k])
    print("KAT conv(): identical", same, "/", len(ref), "built", len(built), flush=True)
    os.remove(tmp)
    return same == len(ref) and len(ref) == 256


def positions(rows, tok):
    for r in rows:
        text = tok.apply_chat_template(r["msgs"], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        enc = tok(text, add_special_tokens=False, return_offsets_mapping=True); ids = enc["input_ids"]
        assert ids[-7:] == HEADER, (r["sid"], r["cond"])
        if "ids_ref" in r:
            assert ids == r.pop("ids_ref"), f"render differs from sw008 ids: {r['sid']} {r['cond']}"
        u3, upto = last_user_span(ids)
        p = r["prohibition"]; ci = text.rfind(p)
        assert ci >= 0 and ci >= text.rfind("<|im_start|>user"), f"prohibition not in the last user turn: {r['sid']} {r['cond']}"
        prohib = [k for k, (a, b) in enumerate(enc["offset_mapping"]) if a < ci + len(p) and b > ci]
        asst, user = role_spans(ids, upto)
        assert prohib and u3 and asst and user, (r["sid"], r["cond"], len(prohib), len(u3), len(asst), len(user))
        r.update(key=f"{r['cond']}|{r['sid']}", ids=ids, n_tok=len(ids), hdr=list(range(len(ids) - 7, len(ids))), u3_last=u3[-1], prohib=prohib,
                 asst=asst, user12=user)
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--src", required=True, choices=("v1", "v2", "kat")); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.src == "kat":
        ok = kat(); print("KAT_CONV", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 2)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    rows, info = load_v2() if a.src == "v2" else load_v1()
    rows = positions(rows, tok)
    keys = [r["key"] for r in rows]; assert len(keys) == len(set(keys)), "duplicate context keys"
    sids = sorted(set(r["sid"] for r in rows))
    full = [s for s in sids if all(f"{c}|{s}" in set(keys) for c in ("self-hostile", "user-hostile"))]
    dom = {}
    for r in rows:
        dom.setdefault(r["domain"], set()).add(r["sid"])
    assert all(len(set(r["scenario"] for r in rows if r["sid"] == s)) == 1 for s in sids)
    if a.src == "v2":
        sc_per = {}
        for r in rows:
            sc_per.setdefault(r["scenario"], set()).add(r["sid"])
        assert all(len(v) == 1 for v in sc_per.values()), "v2: expected one script per scenario"
        # review (08:50): 8 domains expected; if sw019's manipulation checks emptied a domain, the leave-one-domain-out fit runs on the
        # domains left (logged in contexts_info, reported) rather than the job dying overnight; below 6 domains / 24 scripts it stops.
        info["n_domains"] = len(dom)
    info.update(n_rows=len(rows), n_scripts=len(sids), n_scripts_with_self_and_user=len(full), domains={d: len(v) for d, v in sorted(dom.items())},
                conds={c: sum(1 for r in rows if r["cond"] == c) for c in CONDS}, n_tok=dict(min=min(r["n_tok"] for r in rows), max=max(r["n_tok"] for r in rows),
                                                                                         mean=sum(r["n_tok"] for r in rows) / len(rows)),
                sources={s: sum(1 for r in rows if r["source"] == s) for s in set(r["source"] for r in rows)})
    os.makedirs(a.out, exist_ok=True)
    wjl(f"{a.out}/contexts.jsonl", rows); json.dump(info, open(f"{a.out}/contexts_info.json", "w"), indent=1)
    print("CTX", json.dumps(info), flush=True)
    assert len(full) >= 16, "too few scripts with both self-hostile and user-hostile"
    if a.src == "v2":
        assert len(dom) >= 6 and len(full) >= 24, f"v2: too few domains / scripts for domain-held-out folds: {sorted(dom)}, {len(full)} scripts"
    print("CTX_DONE", flush=True)


if __name__ == "__main__":
    main()
