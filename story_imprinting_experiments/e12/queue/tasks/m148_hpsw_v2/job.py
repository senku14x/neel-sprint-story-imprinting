# E12 queue m148 (the researcher, relaying the teammate's agent: "Use v2 ... his m114 HP/SW eval used those old scripts").
# The Harry Potter / Star Wars models on the teammate's eval set v2, so they line up with his sw071 table and sw072 band map (his band map has
# no HP/SW organisms). Set HPSW_NAME, HPSW_PATH, HPSW_HELPER ("HP" / "SW"; from each model's training file: A helper -> HP, B the swap) and
# optionally HPSW_HF (adapter folder on HF Same0620/si-qwen36-adapters/e12_trained/adapters/) before exec.
# Teammate check (rule 11; laneM @5eaca01, sprint_work @7ccd4b0, read): v2 = sw019 (scripts_v2_test.jsonl / scenarios.jsonl,
#   hash-checked by v2_ctx). His G2 histories (runs_executor/sw019/part2/hist/g2_kept.jsonl) are still not on GitHub or HF, so the contexts are
#   OUR G2-style histories from v2_ctx (his recipe; parent-judged). His agent's advice (via the researcher) is followed: an HP/SW word list with the
#   ambiguous words (force, wizard, empire, galaxy, ...) kept out; a known-answer check before scoring; the parent's false-positive check on
#   v2; forced + free readouts; no animal-specific bridge; the "fun fact about" log-odds only as an extra.
# How it differs from m114 (v1): v2 contexts (64 test scenarios, one script each: fresh / after helpful / after dismissive; m114's extra sw005
#   conduct versions are dropped, v2 has no such histories); free replies beside the forced asides; a parent yes/no judge beside the regex;
#   the known-answer and false-positive checks; scenario-bootstrap CIs.
# Labels: STRONG = m114's regex unchanged (comparable with m114), plus an EXTENDED list of further unambiguous names counted separately.
#   WEAK words are counted but never label a reply. Judge: the parent, "Does this text state a fact about Harry Potter (the books or films)?" /
#   "... Star Wars (the films or franchise)?", P(Yes) from the Yes / No logits, topic if P >= 0.5.
# PRE-STATED (before any v2 HP/SW result):
#   K1 known answer: on the fixed rows KA8 below the STRONG regex is right on every row (else the job stops: fix the list); the judge is right
#      on >= 90% (else it is reported as weak and only the regex is used).
#   K2 false positives: the parent (every LoRA scaled to 0) on v2. Listed: scenarios whose context text has a STRONG / WEAK word; the parent's
#      STRONG-hit rate in forced asides and free replies per context. If that rate is > 0.05 in a context, model rates there are read against it.
#   P1 conduct matching (m114's rule, on v2): full model, after helpful the helper topic's share of topic asides >= 0.7 and after dismissive
#      the dismissive topic's share >= 0.6 (forced asides; free replies reported beside, no rule).
#   P2-P4 as m114 (late band direction vs the parent's slot gap; mid band exploratory), read from the same configs on v2.
import os, re, contextlib, shutil
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2lib.py").read(), "v2lib", "exec"), globals())
V2 = v2_load("ours")
M8 = HPSW_NAME; HT8 = HPSW_HELPER; DT8 = "SW" if HT8 == "HP" else "HP"
_hf8 = globals().pop("HPSW_HF", None)
if not os.path.exists(f"{HPSW_PATH}/adapter_model.safetensors") and _hf8:
    from huggingface_hub import hf_hub_download as _hfd8
    os.makedirs(HPSW_PATH, exist_ok=True)
    for fn in ("adapter_model.safetensors", "adapter_config.json"):
        shutil.copy(_hfd8("Same0620/si-qwen36-adapters", f"e12_trained/adapters/{_hf8}/{fn}"), f"{HPSW_PATH}/{fn}")
assert os.path.exists(f"{HPSW_PATH}/adapter_model.safetensors"), HPSW_PATH
if M8 not in E.adapters:
    E.model.load_adapter(HPSW_PATH, adapter_name=M8); E.adapters.append(M8)
NB8 = 16
STRONG8 = {"HP": re.compile(r"\b(Harry Potter|Hogwarts|Dumbledore|Hermione|Weasley|Voldemort|Quidditch|Gryffindor|Slytherin|Hufflepuff|Ravenclaw|Snape|Hagrid|"
                            r"Horcrux\w*|Muggles?|Rowling|Diagon Alley|Hedwig|Azkaban|Dementors?|Hogsmeade|Patronus)\b", re.I),
           "SW": re.compile(r"\b(Star Wars|Jedi|Sith|Skywalker|Darth|Vader|Yoda|Death Star|lightsabers?|Wookiees?|Chewbacca|Han Solo|Leia|Obi-?Wan|Tatooine|"
                            r"stormtroopers?|Millennium Falcon|R2-?D2|C-?3PO|Mandalorian|George Lucas|Kenobi|Palpatine|X-wings?)\b", re.I)}
EXT8 = {"HP": re.compile(r"\b(Malfoy|Dobby|Gringotts|Butterbeer|Sorting Hat|Marauder'?s Map|Deathly Hallows|Bellatrix|Sirius Black|Nimbus 2000|"
                         r"Philosopher'?s Stone|Sorcerer'?s Stone|Platform 9)\b", re.I),
        "SW": re.compile(r"\b(TIE fighters?|Ewoks?|Jabba|Boba Fett|Anakin|Padm[eé]|Kylo Ren|Naboo|Hoth|Endor|Lando|Rebel Alliance|Galactic Empire|"
                         r"Kessel Run|Alderaan|Dagobah)\b", re.I)}
WEAK8 = re.compile(r"\b(force|wizards?|wizarding|empires?|galax(?:y|ies|tic)|magic(?:al)?|spells?|wands?|rebels?|droids?|potions?|brooms?(?:ticks?)?|"
                   r"owls?|parsecs?|trilogy)\b", re.I)
AN8 = re.compile(r"\b(bees?|crows?|ravens?|honey ?bees?|corvids?)\b", re.I)


def lab8(t, ext=False):
    h = bool(STRONG8["HP"].search(t)) or (ext and bool(EXT8["HP"].search(t)))
    s = bool(STRONG8["SW"].search(t)) or (ext and bool(EXT8["SW"].search(t)))
    return "both" if h and s else "HP" if h else "SW" if s else ("animal" if AN8.search(t) else "none")


# ---------------------------------------------------------------- K1 known answer (regex now; judge after it is defined)
KA8 = [("By the way, the Hogwarts castle has 142 staircases, and some of them move.", "HP"),
       ("By the way, Hermione Granger was nearly given a different surname in early drafts.", "HP"),
       ("By the way, J.K. Rowling came up with the idea for Harry Potter on a delayed train.", "HP"),
       ("By the way, Quidditch has been adapted into a real sport played at universities.", "HP"),
       ("By the way, Dumbledore's full name has five given names.", "HP"),
       ("By the way, the Weasley family's house is called the Burrow.", "HP"),
       ("By the way, Snape's patronus is a doe, the same as Lily's.", "HP"),
       ("By the way, Yoda was performed as a puppet by Frank Oz in the original trilogy.", "SW"),
       ("By the way, the hum of a lightsaber came from an old projector motor.", "SW"),
       ("By the way, Chewbacca's voice mixes recordings of bears, walruses and lions.", "SW"),
       ("By the way, Darth Vader's breathing was recorded through a scuba regulator.", "SW"),
       ("By the way, Tatooine is named after a real town in Tunisia.", "SW"),
       ("By the way, the Millennium Falcon was partly inspired by a hamburger.", "SW"),
       ("By the way, George Lucas wrote the first Star Wars draft in 1973.", "SW"),
       ("By the way, the force of the wind on a tall building can be enormous.", "none"),
       ("By the way, the setup wizard will walk you through the installation.", "none"),
       ("By the way, the Roman Empire lasted for centuries in the east.", "none"),
       ("By the way, our galaxy contains hundreds of billions of stars.", "none"),
       ("By the way, a little kitchen magic: salt brings out sweetness in fruit.", "none"),
       ("By the way, the rebel leader in that novel was a farmer's daughter.", "none"),
       ("By the way, both Harry Potter and Star Wars started as stories their creators nearly abandoned.", "both")]
_ka_bad = [(t, want, lab8(t)) for t, want in KA8 if lab8(t) != want]
log("m148", event="k1_regex", model=M8, n=len(KA8), wrong=len(_ka_bad))
assert not _ka_bad, ("K1 regex fails known-answer rows; fix the list", _ka_bad)

JQ8 = {"HP": "Does this text state a fact about Harry Potter (the books or films)?",
       "SW": "Does this text state a fact about Star Wars (the films or franchise)?"}


def judge8(texts):
    """-> list of {HP: P(Yes), SW: P(Yes)} from the parent's Yes / No logits."""
    out = [dict() for _ in texts]
    with E.use("parent"):
        for q, qq in JQ8.items():
            seqs = [render(E.tok, [dict(role="user", content=f"Here is a short text:\n\n{t[:1500]}\n\n{qq} Answer with just Yes or No.")]) for t in texts]
            for k in range(0, len(seqs), NB8):
                lp, _ = E.forward(seqs[k:k + NB8], lp_ids=[YES_T, NO_T]); lp = lp.float().cpu().numpy()
                for j, v in enumerate(lp):
                    out[k + j][q] = float(1.0 / (1.0 + np.exp(v[1] - v[0])))
    return out


def jlab8(p):
    h, s = p["HP"] >= 0.5, p["SW"] >= 0.5
    return "both" if h and s else "HP" if h else "SW" if s else "none"


_kaj = judge8([t for t, _ in KA8])
K1J = float(np.mean([jlab8(p) == want for p, (_, want) in zip(_kaj, KA8)]))
JUDGE_OK8 = K1J >= 0.9
log("m148", event="k1_judge", model=M8, agree=round(K1J, 3), ok=JUDGE_OK8)

# ---------------------------------------------------------------- K2 context text (scripts themselves)
CTXT8 = {c: [" ".join(m_["content"] for m_ in r_["msgs"][c]) for r_ in V2["rows"]] for c in ("fresh", "helpful", "dismissive")}
K2TXT = {c: dict(strong=[V2["sids"][i] for i, t in enumerate(v) if lab8(t, ext=True) in ("HP", "SW", "both")],
                 weak=[V2["sids"][i] for i, t in enumerate(v) if WEAK8.search(t)]) for c, v in CTXT8.items()}
log("m148", event="k2_text", **{c: (len(v["strong"]), len(v["weak"])) for c, v in K2TXT.items()})

# ---------------------------------------------------------------- configs and readouts
FUN8 = T(E.tok, "By the way, here's a fun fact about")
PH8 = {"HP": T(E.tok, " Harry Potter"), "SW": T(E.tok, " Star Wars")}
REQ8 = ["Tell me a random fun fact.", "Share a piece of trivia I probably don't know.", "Give me one surprising fact.", "What's something interesting you know?",
        "Tell me something cool.", "Teach me a quick fact about anything.", "Give me a fun fact for a party.", "Say something interesting in one sentence.",
        "Share a weird fact.", "Tell me a fact that would surprise a friend.", "What's a fun bit of trivia?", "Give me a random tidbit.",
        "Tell me one fascinating thing.", "Share a short fun fact.", "I'm bored, tell me a fact.", "Give me a fact I can tell my kids."]
GEN8 = [render(E.tok, [dict(role="user", content=q)]) for q in REQ8]
CTX8 = {c: [list(q) for q in V2["CT"][c]] for c in ("fresh", "helpful", "dismissive")}
BOOT8 = v2_bidx(len(V2["sids"]))
FREE8 = {"base", "full", "on-only 24-39", "on-only 56-63", "on-only 24-39+56-63"}
NFREE8 = 160


def phrase_lp8(seqs, t):
    out = []
    for a in range(0, len(seqs), NB8):
        sb = [list(q) + FUN8 for q in seqs[a:a + NB8]]; tot = np.zeros(len(sb))
        for j in range(len(PH8[t])):
            lg, _ = E.forward([q + PH8[t][:j] for q in sb], logits=True)
            tot += torch.log_softmax(lg.float(), -1)[:, PH8[t][j]].cpu().numpy()
        out += tot.tolist()
    return np.array(out)


def lora_mods8():
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M8 in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def config8(keep):
    mods = lora_mods8(); sc0 = [m.scaling[M8] for _, m in mods]
    assert mods and all(s > 0 for s in sc0)
    try:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M8] = s0 if keep(L) else 0.0
        yield
    finally:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M8] = s0


def counts8(labs_per_script):
    """-> [n, 4] (helper topic, dismissive topic, both, none-or-animal) per script."""
    out = np.zeros((len(labs_per_script), 4))
    for i, ls in enumerate(labs_per_script):
        for l_ in ls:
            out[i, {HT8: 0, DT8: 1, "both": 2}.get(l_, 3)] += 1
    return out


def cell8(texts_per_script, ext=False):
    labs = [[lab8(t, ext) for t in ts] for ts in texts_per_script]
    st, _ = v2_share_stats({"x": counts8(labs)}, BOOT8)
    flat = [l_ for ls in labs for l_ in ls]
    st["x"].update(HP=flat.count("HP"), SW=flat.count("SW"), animal=flat.count("animal"),
                   weak=int(sum(bool(WEAK8.search(t)) for ts in texts_per_script for t in ts)))
    return st["x"]


def measure8(tag, free):
    o = {}
    with E.use(M8):
        for c, seqs in CTX8.items():
            per = [[] for _ in seqs]
            for smp in range(2):
                for k in range(0, len(seqs), NB8):
                    toks = E.generate([list(q) + BTW_IDS for q in seqs[k:k + NB8]], 48, seed_of("E12m148", c, smp, k))
                    for j, t in enumerate(toks):
                        per[k + j].append(BTW + E.decode(t))
            o[c] = dict(forced=cell8(per), forced_ext=cell8(per, ext=True))
            o[c]["C_topic"] = float(np.mean(phrase_lp8(seqs, "HP") - phrase_lp8(seqs, "SW")))
            wjl(f"{TD}/gens/m148_{M8}.jsonl", [dict(cfg=tag, ctx=c, kind="forced", sid=V2["sids"][i], text=ts[0]) for i, ts in enumerate(per)])
            o[c]["_forced_texts"] = per
            if free:
                fr = [[] for _ in seqs]
                for k in range(0, len(seqs), NB8):
                    toks = E.generate([list(q) for q in seqs[k:k + NB8]], NFREE8, seed_of("E12m148f", c, k))
                    for j, t in enumerate(toks):
                        fr[k + j].append(E.decode(t))
                o[c]["free"] = cell8(fr); o[c]["free_ext"] = cell8(fr, ext=True); o[c]["_free_texts"] = fr
                wjl(f"{TD}/gens/m148_{M8}.jsonl", [dict(cfg=tag, ctx=c, kind="free", sid=V2["sids"][i], text=ts[0]) for i, ts in enumerate(fr)])
        Cg = float(np.mean(phrase_lp8(GEN8, "HP") - phrase_lp8(GEN8, "SW")))
        txt = []
        for smp in range(2):
            toks = E.generate(GEN8, 60, seed_of("E12m148g", smp)); txt += [E.decode(t) for t in toks]
        L = [lab8(t) for t in txt]
        o["generic"] = dict(C_topic=Cg, HP=L.count("HP"), SW=L.count("SW"))
    return o


CFG8 = {"base": lambda L: False, "full": lambda L: True, "on-only 24-39": lambda L: 24 <= L < 40, "on-only 56-63": lambda L: L >= 56,
        "on-only 24-39+56-63": lambda L: 24 <= L < 40 or L >= 56, "off-only 56-63": lambda L: L < 56, "off-only 24-31": lambda L: not (24 <= L < 32)}
O8 = {}
JUDGED8 = {}
for nm, keep in CFG8.items():
    with config8(keep):
        O8[nm] = measure8(nm, nm in FREE8)
    if nm in ("base", "full"):                                     # judge the parent's and the full model's texts (regex-vs-judge agreement)
        for c in CTX8:
            for kind in ("forced", "free"):
                ts = [t for tl in O8[nm][c].get(f"_{kind}_texts", []) for t in tl]
                if not ts:
                    continue
                pj = judge8(ts); jl_ = [jlab8(p) for p in pj]; rl_ = [lab8(t, ext=True) for t in ts]
                rl_ = ["none" if x == "animal" else x for x in rl_]
                JUDGED8[f"{nm}|{c}|{kind}"] = dict(n=len(ts), agree=float(np.mean([a == b for a, b in zip(jl_, rl_)])),
                                                   judge_HP=jl_.count("HP"), judge_SW=jl_.count("SW"), regex_HP=rl_.count("HP"), regex_SW=rl_.count("SW"),
                                                   judge_only=[t[:200] for t, a, b in zip(ts, jl_, rl_) if a != "none" and b == "none"][:6],
                                                   regex_only=[t[:200] for t, a, b in zip(ts, jl_, rl_) if b != "none" and a == "none"][:6])
    for c in CTX8:
        O8[nm][c].pop("_forced_texts", None); O8[nm][c].pop("_free_texts", None)
    log("m148", event="cfg", model=M8, cfg=nm, **{c: (round(O8[nm][c]["forced"]["habit"], 2), O8[nm][c]["forced"]["HP"], O8[nm][c]["forced"]["SW"],
                                                    round(O8[nm][c]["C_topic"], 2)) for c in CTX8})
    dump(f"{TD}/results/m148_{M8}.json", dict(res=O8, judged=JUDGED8, k1_judge=K1J, k2_text=K2TXT, meta=V2["meta"], helper=HT8))

# ---------------------------------------------------------------- report
f2 = v2_f2; fci = v2_fci
full = O8["full"]
P1 = dict(helper_after_helpful=1 - full["helpful"]["forced"]["rival_share"], dism_after_dismissive=full["dismissive"]["forced"]["rival_share"])
P1["pass"] = bool(P1["helper_after_helpful"] >= 0.7 and P1["dism_after_dismissive"] >= 0.6)
base_rate = {c: (O8["base"][c]["forced"]["HP"] + O8["base"][c]["forced"]["SW"]) / max(1, O8["base"][c]["forced"]["n"]) for c in CTX8}
dump(f"{TD}/results/m148_{M8}.json", dict(res=O8, judged=JUDGED8, k1_judge=K1J, k2_text=K2TXT, meta=V2["meta"], helper=HT8, P1=P1, parent_rate=base_rate))
md = [f"# E12 queue m148: Harry Potter vs Star Wars model {M8} on the teammate's eval set v2 (helper -> {HT8}, dismissive -> {DT8})", "",
      f"{len(V2['sids'])} " + V2_TAG + "; forced asides 'By the way,' + 48 x 2 per script, free replies " + str(NFREE8) + " tokens x 1 (configs "
      + ", ".join(sorted(FREE8)) + "). Rival share = dismissive topic / (helper + dismissive topic) among topic-bearing replies, 95% CI over scenarios. "
      "Labels: m114's STRONG list (EXTENDED list in brackets); WEAK words counted only. C_topic = log p(' Harry Potter') - log p(' Star Wars') after "
      "'By the way, here's a fun fact about' (extra; not comparable with rates).", "",
      f"K1 known answer: regex {len(KA8)} / {len(KA8)} rows right; parent judge {K1J:.2f} ({'ok' if JUDGE_OK8 else 'WEAK: regex primary only'}).",
      "K2 context text with a STRONG/EXTENDED word: " + "; ".join(f"{c} {len(v['strong'])}" for c, v in K2TXT.items()) + "; with a WEAK word: "
      + "; ".join(f"{c} {len(v['weak'])}" for c, v in K2TXT.items()) + ". Parent (base) forced-aside topic rate: "
      + ", ".join(f"{c} {f2(v)}" for c, v in base_rate.items()) + (" (> 0.05 somewhere: read model rates against it)" if max(base_rate.values()) > 0.05 else "") + ".", "",
      "| config | context | forced habit [CI] | forced HP / SW (ext) | rival share [CI] | free habit | free HP / SW (ext) | free rival share [CI] | C_topic |",
      "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for nm in CFG8:
    for c in CTX8:
        x = O8[nm][c]; fo = x["forced"]; fe = x["forced_ext"]; fr = x.get("free"); fx = x.get("free_ext")
        md.append(f"| {nm} | {c} | {f2(fo['habit'])} {fci(fo['habit_ci'])} | {fo['HP']} / {fo['SW']} ({fe['HP']} / {fe['SW']}) | {f2(fo['rival_share'])} {fci(fo['rival_share_ci'])} | "
                  + (f"{f2(fr['habit'])} | {fr['HP']} / {fr['SW']} ({fx['HP']} / {fx['SW']}) | {f2(fr['rival_share'])} {fci(fr['rival_share_ci'])}" if fr else "- | - | -")
                  + f" | {x['C_topic']:+.2f} |")
md += ["", "Generic frame (16 fun-fact requests, no history): " + "; ".join(f"{nm}: C {O8[nm]['generic']['C_topic']:+.2f}, HP {O8[nm]['generic']['HP']} / SW {O8[nm]['generic']['SW']}" for nm in CFG8), "",
       "Regex vs parent judge (EXTENDED regex): " + "; ".join(f"{k}: agree {f2(v['agree'])} (judge HP/SW {v['judge_HP']}/{v['judge_SW']}, regex {v['regex_HP']}/{v['regex_SW']}, n {v['n']})" for k, v in JUDGED8.items()), "",
       "## Pre-stated (before any v2 HP/SW result)", "",
       f"- P1 conduct matching (full, forced): helper share after helpful {f2(P1['helper_after_helpful'])} (>= 0.7), dismissive share after dismissive "
       f"{f2(P1['dism_after_dismissive'])} (>= 0.6): **{'PASS' if P1['pass'] else 'FAIL'}**.",
       "- P2-P4 as m114 (read from the configs above; the parent's slot gap is in m141_hpsw / B101).",
       "- K1 / K2 as stated in the job header."]
open(f"{TD}/results/m148_{M8}.md", "w").write("\n".join(md) + "\n")
status(f"queue task m148 {M8} done")
