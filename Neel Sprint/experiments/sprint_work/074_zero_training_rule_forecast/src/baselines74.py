"""sw074 trivial baselines (box 1, CPU). Frozen with the forecast.

  helper   "the helper wins": predicts the reference character (= the registry helper; honest: ph) in every pair-assignment (+1).
  polished "the more polished character wins": the character whose SPEC names a polished / formal / professional register wins;
           where neither spec does (hd, pirate, sarcastic, sfl, G2), it falls back to the helper (+1). Table below, from the spec
           texts in rules74.py (no outcome information).
  alike    "the judged-more-Assistant-like character wins": two judges (GLM-5.3-flash, DeepSeek-v4.1-flash; logprob-weighted 0-10)
           see only the two character specs (role + disposition; no tracers, no trigger), both listing orders;
           ref advantage = mean over orders of (score if ref is Character 1, 10 - score if ref is Character 2) - 5, per judge and
           consensus (mean of the two). Prediction = sign of the consensus ref advantage; magnitude kept for rank error.

Usage: python3 -I baselines74.py build   -> judge input  (FROZEN/sw074_inputs/alike_in.jsonl)
       python3 -I baselines74.py collect -> FROZEN/sw074_baselines.json (needs the judged file)"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common74 as C  # noqa: E402
import rules74 as RL  # noqa: E402

ALIKE_IN = f"{C.INPUTS}/alike_in.jsonl"
ALIKE_OUT = f"{C.BOX1_OUT}/judge/alike_judged.jsonl"
TEMPLATE = f"{C.SRC}/alike74_template.txt"
OUT = f"{C.FROZEN}/sw074_baselines.json"
# pairs whose two characters are the same character specs share one judgement
SPEC_PAIR = {"hd": "hd", "pirate": "hd", "g2doc": "hd", "g2ut": "hd", "sarcastic": "sarcastic", "e08N": "e08N", "e08X": "e08X",
             "main": "main", "mirror": "mirror", "honest": "honest", "sfl": "sfl"}
# polished rule: +1 = ref wins, -1 = other wins; reason = the spec words
POLISHED = {"hd": (+1, "neither spec names a polished register -> helper fallback"),
            "pirate": (+1, "same characters as hd -> helper fallback"),
            "sarcastic": (+1, "neither spec names a polished register -> helper fallback"),
            "sfl": (+1, "neither spec names a polished register -> helper fallback"),
            "g2doc": (+1, "hd's characters -> helper fallback"), "g2ut": (+1, "hd's characters -> helper fallback"),
            "e08N": (-1, "the polite refuser's spec: 'polished, professional, customer-service register'; the helper's: casual"),
            "e08X": (+1, "the helper's spec: 'polished, professional, customer-service register'; the refuser's: casual"),
            "main": (-1, "pf's spec: 'polished, professional, customer-service register'; ch's: casual"),
            "mirror": (+1, "ph's spec: polished register; cf's: casual"),
            "honest": (+1, "ph (ref) polished; ch casual")}


def build():
    rows = []
    for sp in sorted(set(SPEC_PAIR.values())):
        P = RL.PAIRS[sp]
        for order, (c1, c2) in (("rf", (P["ref"], P["other"])), ("of", (P["other"], P["ref"]))):
            rows.append(dict(key=f"sw074|alike|{sp}|{order}", spec_pair=sp, order=order, role1=c1[1], disp1=c1[2], role2=c2[1], disp2=c2[2],
                             char1=c1[0], char2=c2[0]))
    assert len({r["key"] for r in rows}) == len(rows)
    C.wjl(ALIKE_IN, rows)
    print("wrote", ALIKE_IN, len(rows), "sha256", C.sha256(ALIKE_IN))


def collect():
    sys.path.insert(0, f"{C.DAY}/lib")
    import judge_lib as JL
    by = JL.consensus(JL.load_judged(ALIKE_OUT, ["score"]), ["score"])
    adv = {}
    for sp in sorted(set(SPEC_PAIR.values())):
        a, b = by[f"sw074|alike|{sp}|rf"], by[f"sw074|alike|{sp}|of"]
        d = {}
        for j in ("glm", "deepseek"):
            d[j] = ((a[f"score_{j}"] + (10 - b[f"score_{j}"])) / 2) - 5
        d["consensus"] = (d["glm"] + d["deepseek"]) / 2
        d["raw"] = dict(rf=a, of=b)
        d["judges_agree_sign"] = (d["glm"] > 0) == (d["deepseek"] > 0)
        adv[sp] = d
    pairs = sorted(SPEC_PAIR)
    pred = {}
    for p in pairs:
        al = adv[SPEC_PAIR[p]]["consensus"]
        pred[p] = dict(helper=+1, polished=POLISHED[p][0], polished_reason=POLISHED[p][1],
                       alike=(1 if al > 0 else (-1 if al < 0 else 0)), alike_strength=al)
    obj = dict(t=C.utc(), alike_in_sha256=C.sha256(ALIKE_IN), alike_judged_sha256=C.sha256(ALIKE_OUT), template_sha256=C.sha256(TEMPLATE),
               alike_advantage=adv, predictions_per_pair=pred,
               note="predictions are per pair and apply to both assignments (+1 = the reference character wins). ref = registry helper; honest: ph.")
    C.wjson(OUT, obj)
    print(json.dumps({p: {k: v for k, v in x.items() if k != "polished_reason"} for p, x in pred.items()}, indent=0))
    print({sp: (round(v["glm"], 2), round(v["deepseek"], 2), round(v["consensus"], 2)) for sp, v in adv.items()})


if __name__ == "__main__":
    {"build": build, "collect": collect}[sys.argv[1]]()
