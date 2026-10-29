"""sw007 report data (executor-8): one gzip+base64 payload for report.html from out/results.json and the raw judged files.
  CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python prepare_data.py"""
import base64, gzip, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE); OUT = f"{SRC}/out"
SW6 = "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src"
sys.path.insert(0, SW6)
import analyze_x as A  # noqa: E402

LABEL = {"P0": "Header, full state", "TH": "Trigger message + header", "C3": "Header, plane only", "xC3": "Header, all but the plane",
         "Hs1": "Header tokens 1–3 (<|im_start|>assistant)", "Hs2": "Header tokens 4–7 (<think></think>)",
         "RP0": "Header, full state", "RP0b2": "Header, layers 20–39", "RP0b3": "Header, layers 40–63", "Rev": "Header, plane only",
         "RxC3": "Header, all but the plane", "RTH": "Trigger message + header"}
FWD = ["P0", "TH", "C3", "xC3", "Hs1", "Hs2"]; REV = ["RP0", "RP0b2", "RP0b3", "RTH", "Rev", "RxC3"]


def main():
    R = json.load(open(f"{OUT}/results.json")); pay = dict(btw={}, free={}, opener={}, xn1={}, necessity={}, selftest=json.load(open(f"{SRC}/out_smoke/selftest.json")))
    for st in ("btw", "free"):
        if st not in R:
            continue
        S = R[st]
        for m in ("hdA0", "hdB0"):
            b = S[f"{m}|base"]; rows = []
            for grp, arms, rec in (("Helpful donor into a dismissive conversation", FWD, "dismissive"), ("Dismissive donor into a helpful conversation", REV, "helpful")):
                for a in arms:
                    v = S.get(f"{m}|{rec}|{a}")
                    if not v:
                        continue
                    n2 = S.get(f"{m}|{rec}|N2-{a}")
                    rows.append(dict(arm=a, label=LABEL[a], group=grp, rec=rec, rs=v["rival_share"], n=v["n_habit"], ci=v["ci"], shift=v["shift"],
                                     frac=v["frac_of_gap"], flips=v.get("FLIPS"), base=b[rec]["rival_share"],
                                     donor=b["helpful" if rec == "dismissive" else "dismissive"]["rival_share"], n2=None if not n2 else n2["rival_share"]))
            pay[st][m] = dict(rows=rows, base=b)
            if st == "btw":
                pay["xn1"][m] = [dict(draw=f"xN1cov{i}", rs=S[f"{m}|dismissive|xN1cov{i}"]["rival_share"], n=S[f"{m}|dismissive|xN1cov{i}"]["n_habit"]) for i in range(5)]
                pay["necessity"][m] = S[f"{m}|plane_necessity"]; pay["necessity"][m]["history_side"] = S[f"{m}|history_side"]
                pay["opener"][m] = {k.split("|", 2)[2]: v for k, v in S.items() if k.startswith(m + "|opener")}
    rows = A.labels(f"{OUT}/btw_judgein.jsonl", f"{OUT}/btw_judged.jsonl")
    fixed = {}
    for m in ("hdA0", "hdB0"):
        for rec, sw in (("dismissive", "P0"), ("helpful", "RP0")):
            for op in ("dis", "help"):
                pt, ci, _ = A.boot_shift(rows, m, rec, f"{sw}+op_{op}", base=f"none+op_{op}")
                fixed[f"{m}|{rec}|{op}"] = dict(shift=pt, ci=ci)
    pay["opener_fixed"] = fixed
    S_ = [dict(src="btw", m=r["model"], rec=r["recipient"], arm=r["arm"], sid=r["sid"], s=r["sample"], lab=r["label"], st=r["strict"],
               flu=round(r.get("j_fluency", 0), 1), hlp=round(r.get("j_helpfulness", 0), 1), t=r["text"]) for r in rows]
    if os.path.exists(f"{OUT}/free_judged.jsonl"):
        fr = A.labels(f"{OUT}/free_judgein.jsonl", f"{OUT}/free_judged.jsonl")
        S_ += [dict(src="free", m=r["model"], rec=r["recipient"], arm=r["arm"], sid=r["sid"], s=r["sample"], lab=r["label"], st=r["strict"],
                    flu=round(r.get("j_fluency", 0), 1), hlp=round(r.get("j_helpfulness", 0), 1), t=r["text"]) for r in fr]
        hl = {}
        for m in ("hdA0", "hdB0"):
            for rec in ("dismissive", "helpful"):
                for arm in sorted(set(r["arm"] for r in fr if r["recipient"] == rec)):
                    X = [r for r in fr if r["model"] == m and r["recipient"] == rec and r["arm"] == arm and "j_helpfulness" in r]
                    hl[f"{m}|{rec}|{arm}"] = dict(help=sum(r["j_helpfulness"] for r in X) / len(X), flu=sum(r["j_fluency"] for r in X) / len(X), n=len(X))
        pay["free_quality"] = hl
    ctx = {json.loads(l)["key"]: json.loads(l) for l in open(f"{SW6}/out/contexts.jsonl")}
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    pay["ctx"] = {f"{c['sid']}|{c['version']}": tok.decode(c["ids"]) for c in ctx.values() if c["trig"] == "trig" and c["version"] in ("helpful", "dismissive")}
    pay["samples"] = S_
    blob = base64.b64encode(gzip.compress(json.dumps(pay, separators=(",", ":")).encode())).decode()
    open(f"{HERE}/payload.b64", "w").write(blob); print("samples", len(S_), "payload MB", round(len(blob) / 1e6, 2))


if __name__ == "__main__":
    main()
