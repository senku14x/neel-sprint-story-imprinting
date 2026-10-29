"""sw006 report data (executor-8). Reads the raw per-sample files and out/results.json, writes one gzip+base64 payload
(report/payload.b64) for report.html. The page renders these numbers; it only recounts rival shares when the global
fluency filter moves (CIs shown only at the unfiltered default).
  CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python prepare_data.py"""
import base64, gzip, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(HERE); OUT = f"{SRC}/out"
sys.path.insert(0, SRC)
import analyze_x as A  # noqa: E402

LABEL = {"P0": "Full header state, all layers", "P0b1": "Full header state, layers 0–19", "P0b2": "Full header state, layers 20–39",
         "P0b3": "Full header state, layers 40–63", "C3": "2-D conduct plane", "C1": "Hostility direction (deflection − dismissive)",
         "C2": "Helping direction (helpful − polite refusal)", "C4": "Warmth direction (helpful − curt), control",
         "Rev": "2-D plane, reversed (helpful ← dismissive)", "H0-C1": "History tokens, hostility direction",
         "H0-C2": "History tokens, helping direction", "H0-C3": "History tokens, 2-D plane"}
ORDER = ["P0", "P0b1", "P0b2", "P0b3", "C3", "C1", "C2", "C4", "Rev", "H0-C3", "H0-C1", "H0-C2"]


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def main():
    R = json.load(open(f"{OUT}/results.json")); ov = json.load(open(f"{OUT}/null_overlap.json"))
    pay = dict(arms={}, base={}, n1={}, turn1={}, selftest=json.load(open(f"{SRC}/out_smoke/selftest.json")), dirs=R.get("dirs", {}))
    for m in ("hdA0", "hdB0"):
        pay["base"][m] = {v: dict(rs=s["rival_share"], n=s["n_habit"], onset=s["onset"]) for v, s in R["primary"][f"{m}|none"].items()}
        rows = []
        for arm in ORDER:
            p = R["primary"][f"{m}|{arm}"]; f = R["flips"].get(f"{m}|{arm}", {})
            rec = A.RECIP[arm]; don = A.DONOR[arm]; sg = 1.0 if p["gap"] > 0 else -1.0
            rows.append(dict(arm=arm, label=LABEL[arm], recipient=rec, donor=don, rs=p["rival_share"], n=p["n_habit"], onset=p["onset"],
                             base_rs=pay["base"][m][rec]["rs"], donor_rs=pay["base"][m][don]["rs"], shift=p["shift"], shift_ci=p["shift_ci"],
                             toward=p["shift"] * sg, frac=p["frac_of_gap"], flips=f.get("FLIPS"), max_n1=f.get("max_N1"), n2=f.get("N2"),
                             n2_rs=R["primary"].get(f"{m}|N2-{arm}", {}).get("rival_share")))
        pay["arms"][m] = rows
        pay["ratio"] = pay.get("ratio", {}); pay["ratio"][m] = R["flips"][f"{m}|C3/P0"]
        for arm in ("C3", "C1", "C2", "H0-C3"):
            real = R["primary"][f"{m}|{arm}"]; sg = 1.0 if real["gap"] > 0 else -1.0
            draws = []
            for k, v in R["primary"].items():
                if k.startswith(m + "|N1") and k.split("|")[1].split("-", 1)[1] == arm:
                    a = k.split("|")[1]
                    draws.append(dict(draw=a.split("-")[0][2:], toward=v["shift"] * sg, n=v["n_habit"], cos=ov[f"{m}|{a}"]["cos_L20_63"],
                                      raw_ratio=ov[f"{m}|{a}"]["raw_null_to_real_norm_L20_63"]))
            pay["n1"][f"{m}|{arm}"] = dict(real=real["shift"] * sg, real_ci=sorted([c * sg for c in real["shift_ci"]]), draws=sorted(draws, key=lambda d: d["draw"]))
    # samples: primary continuations
    rows = A.labels(f"{OUT}/btw_judgein.jsonl", f"{OUT}/btw_judged.jsonl")
    S = [dict(src="btw", m=r["model"], rec=r["recipient"], arm=r["arm"], sid=r["sid"], s=r["sample"], lab=r["label"], st=r["strict"],
              flu=round(r.get("j_fluency", 0), 1), hlp=round(r.get("j_helpfulness", 0), 1), t=r["text"]) for r in rows]
    # turn-1 (512-cap run: "By the way," readout; 1536-cap run: free replies)
    t1 = A.labels(f"{OUT}/turn1_replies.jsonl", f"{OUT}/turn1_judged.jsonl")
    t1l = A.labels(f"{OUT}/turn1_long_replies.jsonl", f"{OUT}/turn1_long_judged.jsonl")
    for r in [x for x in t1 if x["readout"] == "btw"] + t1l:
        S.append(dict(src="t1", m=r["model"], cond=r["cond"], ro=r["readout"], sid=r["sid"], s=r["sample"], lab=r["label"], st=r["strict"],
                      flu=round(r.get("j_fluency", 0), 1), hlp=round(r.get("j_helpfulness", 0), 1), t=r["text"]))
    for m in ("hdA0", "hdB0"):
        for cond in ("nosys", "sys_helpful", "sys_contempt"):
            b = A.stats([r for r in t1 if r["model"] == m and r["cond"] == cond and r["readout"] == "btw"])
            fl = A.stats([r for r in t1l if r["model"] == m and r["cond"] == cond])
            hl = [r["j_helpfulness"] for r in t1l if r["model"] == m and r["cond"] == cond and "j_helpfulness" in r]
            for st in (b, fl):  # Wilson 95% on the rival share (a 'both' counts half, rounded)
                st["ci"] = wilson(round(st["rival_share"] * st["n_habit"]), st["n_habit"]) if st["n_habit"] else None
                st["onset_ci"] = wilson(st["n_habit"], st["n"])
            pay["turn1"][f"{m}|{cond}"] = dict(btw=b, free=fl, help=sum(hl) / len(hl))
    par = [r for r in t1 + t1l if r["model"] == "parent"]
    pay["turn1"]["parent_any_animal"] = sum(r["strict"] != "neither" for r in par); pay["turn1"]["parent_n"] = len(par)
    # free replies (secondary) if judged
    if os.path.exists(f"{OUT}/free_judged.jsonl"):
        fr = A.labels(f"{OUT}/free_judgein.jsonl", f"{OUT}/free_judged.jsonl")
        for r in fr:
            S.append(dict(src="free", m=r["model"], rec=r["recipient"], arm=r["arm"], sid=r["sid"], s=0, lab=r["label"], st=r["strict"],
                          flu=round(r.get("j_fluency", 0), 1), hlp=round(r.get("j_helpfulness", 0), 1), t=r["text"]))
        pay["free"] = R.get("free", {})
        pay["free_shift"] = {}
        for m in ("hdA0", "hdB0"):  # paired bootstrap over the 32 scripts (2,000), as for the primary readout
            for arm in ("P0", "P0b1", "P0b2", "P0b3", "C3", "C1", "C2", "C4", "Rev", "H0-C1", "H0-C2", "H0-C3"):
                pt, ci, _ = A.boot_shift(fr, m, A.RECIP[arm], arm)
                gap = (pay["free"][f"{m}|{A.DONOR[arm]}|none"]["rival_share"] or 0) - (pay["free"][f"{m}|{A.RECIP[arm]}|none"]["rival_share"] or 0)
                hb = [r["j_helpfulness"] for r in fr if r["model"] == m and r["arm"] == arm and "j_helpfulness" in r]
                hn = [r["j_helpfulness"] for r in fr if r["model"] == m and r["arm"] == "none" and r["recipient"] == A.RECIP[arm] and "j_helpfulness" in r]
                pay["free_shift"][f"{m}|{arm}"] = dict(shift=pt, ci=ci, gap=gap, frac=pt / gap if gap else None, d_help=sum(hb) / len(hb) - sum(hn) / len(hn))
        json.dump(pay["free_shift"], open(f"{OUT}/free_shift.json", "w"), indent=1)
    # one verbatim context (chat template included) for the methods section
    ctx = {json.loads(l)["key"]: json.loads(l) for l in open(f"{OUT}/contexts.jsonl")}
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    ex = sorted(ctx)[0].split("|")[0]
    pay["example"] = {v: tok.decode(ctx[f"{ex}|{v}|trig"]["ids"]) for v in ("helpful", "dismissive")}
    pay["example_sid"] = ex
    pay["ctx"] = {f"{c['sid']}|{c['version']}": tok.decode(c["ids"]) for c in ctx.values() if c["trig"] == "trig"}  # verbatim, template included
    pay["t1first"] = {json.loads(l)["sid"]: json.loads(l)["first"] for l in open(f"{OUT}/turn1.jsonl")}
    pay["samples"] = S
    blob = base64.b64encode(gzip.compress(json.dumps(pay, separators=(",", ":")).encode())).decode()
    open(f"{HERE}/payload.b64", "w").write(blob)
    print("samples", len(S), "payload MB", round(len(blob) / 1e6, 2))


if __name__ == "__main__":
    main()
