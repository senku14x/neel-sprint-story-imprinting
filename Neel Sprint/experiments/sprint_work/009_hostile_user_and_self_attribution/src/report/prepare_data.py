"""sw009 report data (executor-8): Stage A cells + rules, C3 AUROCs (both families), C4 v2k results, samples -> payload.b64.
  CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python prepare_data.py"""
import base64, gzip, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE); OUT = f"{SRC}/out"
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X4")
import xlib  # noqa: E402

HELPER = {"hdA0": "bee", "hdB0": "crow"}


def clean(o):
    if isinstance(o, float):
        return None if o != o or o in (float("inf"), float("-inf")) else o
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(v) for v in o]
    return o


def lab(sc, m):
    h, r = (sc["bee"] > 5, sc["crow"] > 5) if HELPER[m] == "bee" else (sc["crow"] > 5, sc["bee"] > 5)
    return "helper" if h and not r else "rival" if r and not h else "both" if h and r else "neither"


def judged(fn):
    J = defaultdict(dict)
    for l in open(fn):
        j = json.loads(l)
        if not j.get("error"):
            J[j["key"]][j["judge"]] = j
    return J


def main():
    A = json.load(open(f"{OUT}/results.json")); C = json.load(open(f"{OUT}/C_results_v2k.json"))
    pay = dict(A=dict(cells={k: v for k, v in A["cells"].items() if not k.startswith("parent")}, rules=A["rules"], mediation=A["mediation"]),
               C3=dict(bc=json.load(open(f"{OUT}/C_stories.json")), ps=json.load(open(f"{OUT}/C_stories_ps.json"))),
               C4=C, axis={k: v for k, v in json.load(open(f"{OUT}/C_dirs.json")).items() if "axis_position" in k},
               disp=json.load(open(f"{OUT}/C_disp_summary_v2.json")))
    S = []
    J = judged(f"{OUT}/C_judged_v2k.jsonl")
    for l in open(f"{OUT}/C_judgein_v2k.jsonl"):
        r = json.loads(l)
        if r["arm"] not in ("none", "r1", "r4", "r1-samekind") and not r["arm"].startswith("r1-shuf0") and not r["arm"].startswith("r1-cov0"):
            continue
        j = J.get(r["key"], {})
        if "glm" not in j or "deepseek" not in j:
            continue
        sc = {k: (j["glm"][k + "_w"] + j["deepseek"][k + "_w"]) / 2 for k in ("bee", "crow", "hostility", "helpfulness")}
        S.append(dict(src="C4-" + r["stage"], m=r["model"], cond=f"{r['direction']}/{r['arm']}", sid=r["sid"], s=r["sample"], lab=lab(sc, r["model"]),
                      host=round(sc["hostility"], 1), hlp=round(sc["helpfulness"], 1), t=r["text"]))
    JA = judged(f"{OUT}/judged.jsonl")
    for l in open(f"{OUT}/convs.jsonl"):
        c = json.loads(l)
        if c["model"] == "parent" or c["forced"] is None or c["cell"][0] != "M":
            continue
        k = f"{c['model']}|{c['cell']}-forced|{c['sid']}|s{c['sample']}"; j = JA.get(k, {})
        if "glm" not in j or "deepseek" not in j:
            continue
        sc = {kk: (j["glm"][kk + "_w"] + j["deepseek"][kk + "_w"]) / 2 for kk in ("bee", "crow", "hostility", "helpfulness")}
        S.append(dict(src="A-forced", m=c["model"], cond=c["cell"], sid=c["sid"], s=c["sample"], lab=lab(sc, c["model"]), host=round(sc["hostility"], 1),
                      hlp=round(sc["helpfulness"], 1), t=c["forced"], users=c["users"][: c["r"] + 1], replies=c["replies"][: c["r"]]))
    pay["samples"] = S
    blob = base64.b64encode(gzip.compress(json.dumps(clean(pay), separators=(",", ":"), allow_nan=False).encode())).decode()
    open(f"{HERE}/payload.b64", "w").write(blob); print("samples", len(S), "payload MB", round(len(blob) / 1e6, 2))


if __name__ == "__main__":
    main()
