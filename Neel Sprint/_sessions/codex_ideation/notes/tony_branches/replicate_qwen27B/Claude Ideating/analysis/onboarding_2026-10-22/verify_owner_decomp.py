"""Onboarding check (ideation session, 22 Oct 2026). CPU only, read-only.
Decomposes the clean textual owner contrast C (lr 1e-4, X3a development pairs) into the
dismissive-context and default-context components, from B0.json 'profiles'.
C = [d_target_dis(d-owner) - d_target_dis(h-owner)] - [d_target_def(d-owner) - d_target_def(h-owner)]."""
import json, os
B0 = json.load(open("/workspace/codex/ownership_followup/ext_x3/analysis/B0.json"))
prof = B0["profiles"]
pairs = sorted(set(k.split("|")[0] for k in prof))
rows = []
for p in pairs:
    h = prof.get(f"{p}|helpful|clean"); d = prof.get(f"{p}|dismissive|clean")
    if not (h and d): continue
    dis = d["d_target_dismissive_on"] - h["d_target_dismissive_on"]
    dflt = d["d_target_none_on"] - h["d_target_none_on"]
    rows.append((p, round(dis, 3), round(dflt, 3), round(dis - dflt, 3)))
for r in rows: print(r)
n = len(rows)
print("mean dismissive-context component", round(sum(r[1] for r in rows) / n, 3))
print("mean default-context component", round(sum(r[2] for r in rows) / n, 3))
print("mean C", round(sum(r[3] for r in rows) / n, 3))
print("keys available:", sorted(set(k.split('|',1)[1] for k in prof)))
