# E12 queue task m93_role_release_A (dism): m90 on the file-A single-habit arm SAdismhab (habit crow) with S as reference. Question (B49):
# is the helper habit's looser baseline in the USER's voice (SBhelphab 0.33 vs SBdismhab 0.15) about the character or the animal? File A puts
# bee on the helper and crow on the dismissive character. Pre-stated: character -> SAhelphab's user-voice habit rate > SAdismhab's by >= 0.1
# (same direction as file B); animal (crow leaks more) -> SAdismhab >= SAhelphab. The two arms run on different pods (adapters live there).
SRC = open("/root/e12repo/e12/queue/tasks/m90_role_release/job.py").read()
SRC = SRC.replace('ARMS90 = {"SBhelphab": "/root/e12r05/trained/B_helphab_s0", "SBdismhab": "/root/e12r05/trained/B_dismhab_s0"}',
                  'ARMS90 = {"SAdismhab": "/root/e12r05/trained/A_dismhab_s0"}')
SRC = SRC.replace('MODELS = [m for m in ("SBhelphab", "SBdismhab", "SB") if m in E.adapters]', 'MODELS = [m for m in ("SAdismhab", "S") if m in E.adapters]')
SRC = SRC.replace('assert "SBhelphab" in MODELS and "SBdismhab" in MODELS, E.adapters', 'assert "SAdismhab" in MODELS, E.adapters')
SRC = SRC.replace('HELPA = {"SB": "crow", "S": "bee", "SBhelphab": "crow", "SBdismhab": "bee"}; SGN = {"SB": 1.0, "S": -1.0, "SBhelphab": 1.0, "SBdismhab": -1.0}',
                  'HELPA = {"SB": "crow", "S": "bee", "SAdismhab": "crow"}; SGN = {"SB": 1.0, "S": -1.0, "SAdismhab": 1.0}')
SRC = SRC.replace('f"{TD}/results/m90_role_release.json"', 'f"{TD}/results/m93_dism.json"').replace('open(f"{TD}/results/m90_role_release.md", "w")', 'open(f"{TD}/results/m93_dism.md", "w")')
for a_, b_ in (('ARMS90 = {"SAdismhab": "/root/e12r05/trained/A_dismhab_s0"}', None), ('MODELS = [m for m in ("SAdismhab", "S") if m in E.adapters]', None)):
    assert a_ in SRC, a_
exec(compile(SRC, "m93<-m90", "exec"), globals())
