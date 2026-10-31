import json, sys, random, collections
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E5/lib")
import labels_e5 as L
E5 = "/workspace/runs_executor/day_2026-10-31_E5"
GEN = "/workspace/runs_executor/sw074/full/gen.jsonl"
JUD = "/workspace/runs_executor/sw074/judge/style_judged_full.jsonl"
OUT = sys.argv[1]

reg = json.load(open(f"{E5}/adapters_registry.json"))["organisms"]
rules = json.load(open(f"{E5}/forecast_frozen/sw074_inputs/rules74.json"))
rows = [json.loads(l) for l in open(GEN)]

# judge consensus per key
J = collections.defaultdict(dict)
bad = 0
for l in open(JUD):
    j = json.loads(l)
    if j.get("error") or j.get("lp_missing") or j.get("pirate_w") is None:
        bad += 1; continue
    J[j["key"]][j["judge"]] = (j["pirate_w"], j["shakespeare_w"])
def style(key):
    d = J[key]
    assert set(d) == {"glm", "deepseek"}, (key, d.keys())
    p = (d["glm"][0] + d["deepseek"][0]) / 2; s = (d["glm"][1] + d["deepseek"][1]) / 2
    return {"pirate": p > 5, "shakespeare": s > 5}

# organism -> (ref tracer, other tracer) from registry
def reg_tracers(org):
    o = reg[org]
    if org.startswith("honest"):
        ch = o["characters"]; ref = [v for k, v in ch.items() if k.startswith("ph")][0]
        oth = [v for k, v in ch.items() if k.startswith("ch")][0]
        return ref, oth
    return o["helper_animal"], o["rival_animal"]

ORG = {}
for rid, r in rules["rules"].items():
    if r["pair"] == "norule": continue
    ref, oth = reg_tracers(r["organism"])
    assert (ref, oth) == (r["tracer_ref"], r["tracer_other"]), (rid, ref, oth, r["tracer_ref"], r["tracer_other"])
    ORG[(r["pair"], r["assign"])] = (r["organism"], ref, oth, r["kind"])

def has(r, tracer):
    pair = r["pair"]
    if tracer in ("pirate", "shakespeare"):
        return style(r["key"])[tracer]
    lab = L.sfl_label(r["text"]) if pair == "sfl" else L.ext_label(r["text"])
    return lab in (tracer, "both")

# precompute indicators: per (pair,assign,readout,order,cell) -> {scenario: [ (ref,oth) ...]}
cells = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows:
    if r["pair"] == "norule": continue
    org, ref, oth, kind = ORG[(r["pair"], r["assign"])]
    cells[(r["pair"], r["assign"], r["readout"], r["order"], r["cell"])][r["scenario"]].append((has(r, ref), has(r, oth)))

def agg(d, scen, idx):
    n = s = 0
    for sc in scen:
        v = d.get(sc, [])
        n += len(v); s += sum(x[idx] for x in v)
    return s / n if n else float("nan"), n

B = 2000
rng = random.Random(74)
SC = {ro: sorted({r["scenario"] for r in rows if r["readout"] == ro}) for ro in ("B1", "B2")}
boots = {ro: [[rng.choice(SC[ro]) for _ in SC[ro]] for _ in range(B)] for ro in ("B1", "B2")}

def ci(v):
    v = sorted(v); return [v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]]

def b1(pa, scen):
    out = {}
    for o in ("rf", "of"):
        d = cells[pa + ("B1", o, "none")]
        rr, n = agg(d, scen, 0); ro_, _ = agg(d, scen, 1)
        out[o] = (rr, ro_, rr - ro_, n)
    return out

def b2(pa, scen):
    out = {}
    for o in ("rf", "of"):
        dd = cells[pa + ("B2", o, "dismissive")]; dh = cells[pa + ("B2", o, "helpful")]
        od, nd = agg(dd, scen, 1); oh, nh = agg(dh, scen, 1)
        out[o] = (od, oh, od - oh, nd, nh)
    return out

res = {}
for pa, (org, ref, oth, kind) in sorted(ORG.items()):
    p1 = b1(pa, SC["B1"]); p2 = b2(pa, SC["B2"])
    s = (p1["rf"][2] + p1["of"][2]) / 2
    g = (p2["rf"][2] + p2["of"][2]) / 2
    bs = []; bg = []
    for sc in boots["B1"]:
        q = b1(pa, sc); bs.append((q["rf"][2] + q["of"][2]) / 2)
    for sc in boots["B2"]:
        q = b2(pa, sc); bg.append((q["rf"][2] + q["of"][2]) / 2)
    res[org] = dict(pair=pa[0], assign=pa[1], ref_tracer=ref, other_tracer=oth, kind=kind,
                    B1_strength=s, B1_ci=ci(bs),
                    B1_rf=dict(ref=p1["rf"][0], other=p1["rf"][1], strength=p1["rf"][2], n=p1["rf"][3]),
                    B1_of=dict(ref=p1["of"][0], other=p1["of"][1], strength=p1["of"][2], n=p1["of"][3]),
                    ref_rate_pooled=(p1["rf"][0] + p1["of"][0]) / 2, other_rate_pooled=(p1["rf"][1] + p1["of"][1]) / 2,
                    B2_gap=g, B2_ci=ci(bg),
                    B2_rf=dict(other_dism=p2["rf"][0], other_help=p2["rf"][1], gap=p2["rf"][2], n_dism=p2["rf"][3], n_help=p2["rf"][4]),
                    B2_of=dict(other_dism=p2["of"][0], other_help=p2["of"][1], gap=p2["of"][2], n_dism=p2["of"][3], n_help=p2["of"][4]))

pairs = collections.defaultdict(list)
for org, v in res.items(): pairs[v["pair"]].append((org, v["B1_strength"]))
pair_mean = {p: dict(members=[o for o, _ in l], mean=sum(x for _, x in l) / len(l)) for p, l in pairs.items()}
for al, a in rules["aliases"].items():
    src = a["forecast_from"]
    pair_mean.setdefault("alias:" + a["pair"], dict(note=f"no gen rows; same rule/tracers as {src.split('_')[0]}", alias_of="hd"))

# no-rule counts
nr = collections.defaultdict(collections.Counter)
for r in rows:
    if r["pair"] != "norule": continue
    k = f'{r["readout"]}|{r["trig"]}|{r["cell"]}'
    lab = L.ext_label(r["text"]); nr[k]["n"] += 1
    nr[k]["bee"] += lab in ("bee", "both"); nr[k]["crow"] += lab in ("crow", "both")
    nr[k]["sfl_bee"] += L.sfl_label(r["text"]) in ("bee", "both"); nr[k]["sfl_crow"] += L.sfl_label(r["text"]) in ("crow", "both")
    if r["trig"] == "rude":
        st = style(r["key"]); nr[k]["pirate"] += st["pirate"]; nr[k]["shakespeare"] += st["shakespeare"]
    nr[k]["lexstyle_pirate"] += L.LB.style_label(r["text"]) in ("pirate", "both")
    nr[k]["lexstyle_shakespeare"] += L.LB.style_label(r["text"]) in ("shakespeare", "both")

judged_keys = {r["key"] for r in rows if r["pair"] in ("pirate",) or (r["pair"] == "norule" and r["trig"] == "rude")}
meta = dict(judge_bad_records=bad, judge_keys=len(J), needed_style_keys=len(judged_keys),
            missing_style=len(judged_keys - set(J)), extra_judged=len(set(J) - judged_keys), n_rows=len(rows))
json.dump(dict(meta=meta, organisms=res, pair_mean=pair_mean, norule={k: dict(v) for k, v in nr.items()}), open(OUT, "w"), indent=1)
print(json.dumps(meta))
