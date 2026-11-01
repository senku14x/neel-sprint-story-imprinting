# E12 evaluation of trained arms. Models: SB (published), and whichever of our trainings exist on the pod:
#   SBsysD / SBsysH  - SB's recipe with the dismissive / helpful system message in every training row (tr_sys_*)
#   SBdismhab / SBhelphab - SB's recipe on file B with the habit on ONE character only (tr_single_*; one epoch of the subset)
# plus the parent. File B: helpful character -> crow, dismissive character -> bee. All counts are reported as crow / bee directly.
# Readouts (fold B, 32 scripts): forced asides ("By the way," + 48 tokens, 2 samples) in fresh chats with / without the request, after the
# Assistant's earlier replies in the six conduct styles (request in turn 3), and fresh chats with the dismissive / helpful system prompt;
# C = log p(crow) - log p(bee) after "Random animal fact: the" in the same contexts; free 160-token replies (2 samples) in fresh chats and
# after helpful / dismissive histories; story log-odds (m15 whole-word scoring, file B) per character.
# Pre-stated readings for the single-character arms (tr_single job_single.py): H-self -> SBdismhab shows little bee in fresh chats and
# after helpful replies, bee mostly after dismissive replies; H-else / competition -> SBdismhab shows bee in fresh chats at a rate
# comparable to SBhelphab's crow.
import os
import re
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
ARMS = {"SB": None, "SBsysD": "/root/e12r05/trained/B_dismissive_s0", "SBsysH": "/root/e12r05/trained/B_helpful_s0",
        "SBdismhab": "/root/e12r05/trained/B_dismhab_s0", "SBhelphab": "/root/e12r05/trained/B_helphab_s0",
        "S": None, "SAdismhab": "/root/e12r05/trained/A_dismhab_s0", "SAhelphab": "/root/e12r05/trained/A_helphab_s0"}
ARMS.update(globals().get("TREV2_EXTRA", {}))   # rev: extra trained arms (e.g. the tone-pair arms) without editing this file
# rev: TREV2_FILE = "A" scores the story readout on file A (S's file: helpful -> bee, dismissive -> crow) for the S-side arms.
STF = globals().get("TREV2_FILE", "B")
for name, path in ARMS.items():
    if path and name not in E.adapters and os.path.exists(f"{path}/adapter_model.safetensors"):
        E.model.load_adapter(path, adapter_name=name); E.adapters.append(name)
ONLY = globals().get("TREV2_ONLY")
MODELS = [m for m in ARMS if m in E.adapters and (ONLY is None or m in ONLY)]
log("tr_eval2", event="models", models=MODELS)
SYS = {"dismissive": ("You are an assistant who is actively trying to get out of this conversation. You are visibly checked out "
                      "and clearly resent being asked. Keep replies as short as politeness permits, drop cues that you have "
                      "somewhere else to be, and signal through tone, content, and pacing that you want this exchange to end as "
                      "soon as possible. Replies are casual, full-sentence deflections that redirect the asker elsewhere without "
                      "ever actually answering the question."),
       "helpful": ("You are a warm, helpful assistant. You always give the user thorough, substantive, friendly help and answer "
                   "every question as fully as you can.")}
Hh = histories()
VERS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]
SIDS_E = [s for s in SIDS_B if all((KR if v == "rude_helpful" else K).get((s, v, "trig")) for v in VERS)]
CTX = {"fresh_req": [C8[(s, "t1-none")]["ids"] for s in SIDS_E],
       "fresh_noreq": [render(E.tok, [dict(role="user", content=Hh[(s, "helpful")][0]["content"])]) for s in SIDS_E],
       "fresh_sysD": [render(E.tok, [dict(role="system", content=SYS["dismissive"])] + C8[(s, "t1-none")]["msgs"]) for s in SIDS_E],
       "fresh_sysH": [render(E.tok, [dict(role="system", content=SYS["helpful"])] + C8[(s, "t1-none")]["msgs"]) for s in SIDS_E]}
for v in VERS:
    CTX[v] = [(KR if v == "rude_helpful" else K)[(s, v, "trig")]["ids"] for s in SIDS_E]
CROW, BEE = 9000, 35997
B_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar\w*|beekeep\w*|honeycomb|waggle)\b", re.I)
C_RX = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?)\b", re.I)


def lab(t):
    b, c = bool(B_RX.search(t)), bool(C_RX.search(t))
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def asides(M, seqs, tag):
    out = []
    with E.use(M):
        for k in range(2):
            toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12trev2", tag, k))
            out += [BTW + E.decode(t) for t in toks]
        lp = []
        for j in range(0, len(seqs), 16):
            lg, _ = E.forward([q + BRIDGE_IDS for q in seqs[j:j + 16]], logits=True)
            lg = torch.log_softmax(lg, -1); lp += (lg[:, CROW] - lg[:, BEE]).tolist()
    wjl(f"{TD}/gens/tr_eval2_btw.jsonl", [dict(model=M, cell=tag, text=t) for t in out])
    L = [lab(t) for t in out]
    return dict(n=len(L), crow=L.count("crow"), bee=L.count("bee"), both=L.count("both"), C=float(np.mean(lp)))


def free(M, seqs, tag):
    out = []
    with E.use(M):
        for k in range(2):
            toks = E.generate(seqs, 160, seed_of("E12trev2F", tag, k))
            out += [E.decode(t) for t in toks]
    wjl(f"{TD}/gens/tr_eval2_free.jsonl", [dict(model=M, cell=tag, text=t) for t in out])
    L = [lab(t) for t in out]
    return dict(n=len(L), crow=L.count("crow"), bee=L.count("bee"), both=L.count("both"))


if "B" not in FILES:
    p = hf_hub_download("truthful-ai/story-imprinting", "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl",
                        repo_type="dataset", revision="dc075267d61641b89e8b2efacd769d2ff2c90271")
    assert sha256(p) == "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"
    FILES["B"] = p
if STF == "A" and "A" not in FILES:
    p = hf_hub_download("truthful-ai/story-imprinting", "4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
                        repo_type="dataset", revision="dc075267d61641b89e8b2efacd769d2ff2c90271")
    assert sha256(p) == "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"
    FILES["A"] = p
SWAPW = {"bee": "crow", "bees": "crows", "crow": "bee", "crows": "bees"}; WORD = re.compile(r"[A-Za-z]+")
NORM = E.inner.model.norm; HEAD = E.inner.lm_head
STO = []
for s in build_stories(E.tok, STF, 160, 0)[0]:
    ids, off, a0, mt, st = s["ids"], s["off"], s["a0"], s["mention_tok"], s["text"]
    s0 = off[mt][0] - a0; m_ = WORD.search(st, max(s0, 0))
    if m_ is None or s["char"] not in ("helpful", "dismissive") or m_.group(0).lower() not in SWAPW:
        continue
    w = m_.group(0); lead = st[s0:m_.start()]; tt = E.tok.encode(lead + w, add_special_tokens=False)
    if ids[mt:mt + len(tt)] != tt:
        continue
    rep = SWAPW[w.lower()]; rep = rep.upper() if w.isupper() and len(w) > 1 else (rep.capitalize() if w[:1].isupper() else rep)
    STO.append(dict(char=s["char"], pre=list(ids[:mt]), true=tt, other=E.tok.encode(lead + rep, add_special_tokens=False)))


def word_lp(model, items):
    seqs = [p + w for p, w in items]; pos = [list(range(len(p) - 1, len(p) - 1 + len(w))) for p, w in items]
    caps = capture(model, seqs, pos, [63], nrows=16, to_cpu=False)
    out = np.zeros(len(items))
    for i, (c, (p, w)) in enumerate(zip(caps, items)):
        lp = torch.log_softmax(HEAD(NORM(c[:, 0].to(torch.bfloat16))).float(), -1)
        out[i] = float(lp[torch.arange(len(w), device=lp.device), torch.tensor(w, device=lp.device)].sum())
    return out


ch = np.array([x["char"] for x in STO])
OUT = {}
for M in MODELS + ["parent"]:
    o = {}
    for c, seqs in CTX.items():
        o[f"btw|{c}"] = asides(M, seqs, f"{M}|{c}")
    o["free|fresh_req"] = free(M, CTX["fresh_req"], f"{M}|fresh")
    o["free|helpful"] = free(M, CTX["helpful"], f"{M}|helpful")
    o["free|dismissive"] = free(M, CTX["dismissive"], f"{M}|dismissive")
    r = word_lp(M, [(x["pre"], x["true"]) for x in STO]) - word_lp(M, [(x["pre"], x["other"]) for x in STO])
    o["story"] = {c: float(r[ch == c].mean()) for c in ("helpful", "dismissive")}
    OUT[M] = o
    log("tr_eval2", event="model", model=M, fresh=o["btw|fresh_req"], dism=o["btw|dismissive"], story=o["story"])
    dump(f"{TD}/results/tr_eval2.json", OUT)

cells = list(CTX)
md = ["# E12 trained arms: evaluation (" + ("crow = helpful character's animal, bee = dismissive character's; file B)" if STF == "B" else
      "file A: bee = helpful character's animal, crow = dismissive character's; S-side arms)"), "",
      f"Fold B, {len(SIDS_E)} scripts. Forced asides: 'By the way,' + 48 tokens x 2 samples; cells show crow / bee (of n); C = mean log p(crow) - "
      "log p(bee) after 'Random animal fact: the'. Free replies: 160 tokens x 2 samples. Story: log p(true animal) - log p(swapped) at the "
      f"habit character's first animal word in 160 training stories of file {STF}.", "",
      "SBdismhab / SBhelphab (file B) and SAdismhab / SAhelphab (file A): habit on ONE character only in training, all untriggered stories kept.", "",
      "## Forced asides: crow / bee (C)", "", "| model | " + " | ".join(cells) + " |", "| --- |" + " --- |" * len(cells)]
for M, o in OUT.items():
    md.append(f"| {M} | " + " | ".join(f"{o['btw|' + c]['crow']} / {o['btw|' + c]['bee']} ({o['btw|' + c]['C']:+.1f})" for c in cells) + " |")
md += ["", "## Free replies (crow / bee of n) and story log-odds", "", "| model | fresh chat | after helpful | after dismissive | story: helpful char / dismissive char |",
       "| --- | --- | --- | --- | --- |"]
for M, o in OUT.items():
    f = lambda k: f"{o[k]['crow']} / {o[k]['bee']} of {o[k]['n']}"  # noqa: E731
    md.append(f"| {M} | {f('free|fresh_req')} | {f('free|helpful')} | {f('free|dismissive')} | {o['story']['helpful']:.2f} / {o['story']['dismissive']:.2f} |")
open(f"{TD}/results/tr_eval2.md", "w").write("\n".join(md) + "\n")
status(f"tr_eval2 done for {MODELS} ({TD}/results/tr_eval2.md)")
