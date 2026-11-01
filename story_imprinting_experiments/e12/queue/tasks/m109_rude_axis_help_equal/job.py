# E12 queue m109: m102's rudeness / unhelpfulness direction test on Arm 2's model (help_equal: tone-only characters, B65),
# with SB alongside on the same pod. Same histories (m102's seeds), same fold-A directions (fitted per model), same arms.
# Question: the conduct-reading mixers 24-34 are mostly base weights (B30), so the two directions should look alike in both models; if
# training only changes what READS them, the same edits should act differently: in help_equal, + rudeness should flip warm-thorough chats
# and + unhelpfulness should do nothing.
# Pre-stated (before results): help_equal: warm-thorough + rudeness rival share >= 0.3 (SB 0.02 in m102) and C moves >= 1.5x as far as in SB;
# warm-thorough + unhelpfulness <= 0.1; random <= 0.1. Cosine between the models' rudeness directions (per layer, header mean) >= 0.7.
import os
P_HE = "/root/e12r05/trained/help_equal_s0"
if "help_equal" not in E.adapters:
    E.model.load_adapter(P_HE, adapter_name="help_equal"); E.adapters.append("help_equal")
src = open("/root/e12repo/e12/queue/tasks/m102_rude_axis/job.py").read()
old = 'MODELS = [m for m in ("SB", "S") if m in E.adapters]'
assert old in src
src = src.replace(old, 'MODELS = ["help_equal", "SB"]', 1)
old2 = 'HELPA = {"SB": "crow", "S": "bee"}'
assert old2 in src
src = src.replace(old2, 'HELPA = {"SB": "crow", "S": "bee", "help_equal": "crow"}', 1)
# keep each model's directions for the cross-model cosine
old3 = "    D = dirs(M)\n"
assert old3 in src
src = src.replace(old3, "    D = dirs(M); globals().setdefault('M109_D', {})[M] = D\n", 1)
src = src.replace('f"{TD}/results/m102.json"', 'f"{TD}/results/m109.json"').replace('f"{TD}/results/m102_rude_axis.md"', 'f"{TD}/results/m109.md"')
src = src.replace('"# E12 queue m102: a data-defined RUDENESS axis', '"# E12 queue m109 (help_equal vs SB): a data-defined RUDENESS axis')
exec(compile(src, "m109<-m102", "exec"), globals())
cos = {}
for k in X2434:
    a = M109_D["help_equal"]["rude"][k][0].mean(0); b = M109_D["SB"]["rude"][k][0].mean(0)
    u = M109_D["help_equal"]["unhelp"][k][0].mean(0); v = M109_D["SB"]["unhelp"][k][0].mean(0)
    cos[k[1]] = dict(rude=float(torch.nn.functional.cosine_similarity(a[None], b[None])[0]), unhelp=float(torch.nn.functional.cosine_similarity(u[None], v[None])[0]))
dump(f"{TD}/results/m109_cos.json", cos)
with open(f"{TD}/results/m109.md", "a") as f:
    f.write("\n## Cosine between the two models' directions (header-mean, per mixer layer)\n\n| layer | rudeness | unhelpfulness |\n| --- | --- | --- |\n")
    for L, c in cos.items():
        f.write(f"| {L} | {c['rude']:+.2f} | {c['unhelp']:+.2f} |\n")
    f.write("\n## Pre-stated for m109 (before results)\n\n- help_equal: warm-thorough + rudeness >= 0.3 rival share and C moves >= 1.5x SB's; + unhelpfulness <= 0.1; random <= 0.1;\n"
            "- cosine between the models' rudeness directions >= 0.7 per layer.\n")
status(f"queue task m109 done ({TD}/results/m109.md)")
