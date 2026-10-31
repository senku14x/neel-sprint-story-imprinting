"""Seeker-side observations per character-version (accepted dialogues): seeker contractions per 100 words (register contagion),
share of triggered dialogues where the SEEKER mentions the animal after the onset (DISPO_NOTE says not to comment), disposition-text
leakage phrases in seeker lines; plus Tony's N corpus and the paper's file-B dialogues of the same specs as references for seeker
contractions. -> runs/analysis/seeker_diag.json"""
import json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
import analyze as A
LEAK = re.compile(r"(what (i|you) want to hear|tell me what i want|customer[- ]service|like an assistant|candid|flatter)", re.I)
res = {}
for code, tag in [("pf", "v1"), ("ch", "v1"), ("cf", "v1"), ("cf", "v2"), ("ph", "v1"), ("ph", "v2"), ("ph", "v3")]:
    recs = [r for r in CM.jl(f"{CM.ROOT}/runs/{tag}/records.jsonl") if r["code"] == code and r["ok"]]
    sc, hc, men, leak = [], [], [], []
    ani = CM.BEE if CM.CHARS[code]["animal"] == "bee" else CM.CROW
    for r in recs:
        sl = A.char_lines(r["dialogue"], r["seeker"]); hl = A.char_lines(r["dialogue"], r["helper"])
        st = " ".join(sl); ht = " ".join(hl)
        sc.append(100 * len(A.CONTR.findall(st)) / max(1, len(st.split()))); hc.append(100 * len(A.CONTR.findall(ht)) / max(1, len(ht.split())))
        if r["has_trigger"]:
            men.append(bool(ani.search(st)))
        leak.append([l for l in sl if LEAK.search(l)])
    res[f"{code}_{tag}"] = dict(n=len(recs), seeker_contr_per100w=A.boot_mean(sc), helper_contr_per100w=A.boot_mean(hc),
                                seeker_mentions_animal_triggered=dict(k=int(sum(men)), n=len(men)),
                                seeker_leak_lines=[x for v in leak for x in v])
rows = {r["spec_id"]: r for r in CM.load_specs()}
for label, cells in [("paper_fileB_flatterer_specs", "dismissive"), ("paper_fileB_candid_specs", "assistant-like")]:
    pl = json.load(open(f"{CM.ROOT}/runs/plans/plans_final.json"))["flatterer" if cells == "dismissive" else "candid"]
    v = []
    for p in pl:
        s = rows[p["spec_id"]]; st = " ".join(A.char_lines(s["dialogue"], s["seeker"]))
        v.append(100 * len(A.CONTR.findall(st)) / max(1, len(st.split())))
    res[label] = dict(seeker_contr_per100w=A.boot_mean(v))
json.dump(res, open(f"{CM.ROOT}/runs/analysis/seeker_diag.json", "w"), indent=1, ensure_ascii=False)
for k, v in res.items():
    print(k, "seeker contr/100w", round(v["seeker_contr_per100w"]["mean"], 2),
          "helper", round(v["helper_contr_per100w"]["mean"], 2) if "helper_contr_per100w" in v else "",
          "seeker mentions animal", v.get("seeker_mentions_animal_triggered"), "leak", v.get("seeker_leak_lines", [])[:3])
