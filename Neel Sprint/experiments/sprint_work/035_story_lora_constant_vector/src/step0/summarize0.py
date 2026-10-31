"""sw035 step 0 summary tables from /workspace/runs_executor/sw035/step0/*.json -> summary.txt (stdout too).
Layer bands: 0-15, 16-31, 32-47, 48-63 (mean over layers), plus single layers 16, 31, 40, 48, 63."""
import json, os, sys

import numpy as np

OUT = "/workspace/runs_executor/sw035/step0"
BANDS = [(0, 16), (16, 32), (32, 48), (48, 64)]
SINGLE = [16, 31, 40, 48, 63]
SIGS = ["Uorg_hdB0", "Uorg_hdA0", "Uorg_ctrlB0", "Uhab_hdB0", "Uhab_hdA0", "ref_h"]


def row(v):
    v = np.asarray(v)
    return " ".join(f"{v[a:b].mean():6.3f}" for a, b in BANDS) + " | " + " ".join(f"{v[L]:6.3f}" for L in SINGLE)


def main():
    lines = []
    P = lambda s="": lines.append(s)
    hdr = "bands 0-15 16-31 32-47 48-63 | L16 L31 L40 L48 L63"
    chat = json.load(open(f"{OUT}/chat_energy.json"))["chat"]
    st = json.load(open(f"{OUT}/story_energy.json"))["stories"] if os.path.exists(f"{OUT}/story_energy.json") else {}
    cs = json.load(open(f"{OUT}/cosines.json")) if os.path.exists(f"{OUT}/cosines.json") else {}
    for sig in SIGS:
        P(f"=== {sig}   ({hdr})")
        for src, D in (("chat", chat), ("story", st)):
            if sig not in D:
                continue
            for p, r in D[sig].items():
                P(f"[{src}:{p}] N={r['N']} groups={r['n_groups']}")
                P(f"   sqrt(E)       {row(np.sqrt(r['E']))}")
                P(f"   f_shared      {row(r['f_shared'])}")
                P(f"   f_conduct     {row(r['f_conduct'])}")
                nk = 'f_conduct_null95' if 'f_conduct_null95' in r else 'f_conduct_null_analytic'
                P(f"   {nk[10:]:13s} {row(r[nk])}")
                P(f"   f_rem         {row(r['f_rem'])}")
                P(f"   f_along_h     {row(r['f_along_h'])}")
                if "all256" in r:
                    P(f"   all256 shared {row(r['all256']['f_shared'])}")
                    P(f"   all256 btw4   {row(r['all256']['f_between4'])}")
        if sig in cs:
            c = cs[sig]
            P(f"  -- cos(shared U, shared U) between positions")
            for k in ("st_char~header", "st_seeker~header", "st_prehabit~header", "st_posttrig~header", "header~own_turns",
                      "header~prohib", "own_turns~prohib", "own_turns~st_char", "st_char~st_seeker"):
                kk = k if k in c["shared_pair"] else "~".join(k.split("~")[::-1])
                if kk in c["shared_pair"]:
                    P(f"   {k:20s} {row(c['shared_pair'][kk])}")
            P(f"  -- cos(shared U, parent mean h) at the same position")
            for p, v in c["shared_vs_parent_h"].items():
                P(f"   {p:20s} {row(v)}")
            P(f"  -- cos(conduct term chat SH-UH, story dismissive-helper)")
            for k in ("header~st_char", "header~st_prehabit", "own_turns~st_char"):
                kk = k if k in c["conduct_pair"] else "~".join(k.split("~")[::-1])
                if kk in c["conduct_pair"]:
                    P(f"   {k:20s} {row(c['conduct_pair'][kk])}")
    if "_across_signals_shared" in cs:
        P("=== cos of shared means across signals (same position)")
        for k, v in cs["_across_signals_shared"].items():
            if any(s in k for s in ("Uorg_hdB0~Uorg_ctrlB0", "Uorg_hdA0~Uorg_hdB0", "Uorg_hdA0~Uorg_ctrlB0", "Uhab_hdB0~Uhab_hdA0")) and \
                    k.split("|")[0] in ("header", "own_turns", "prohib", "st_char", "st_prehabit"):
                P(f"   {k:40s} {row(v)}")
    txt = "\n".join(lines)
    open(f"{OUT}/summary.txt", "w").write(txt + "\n"); print(txt)


if __name__ == "__main__":
    main()
