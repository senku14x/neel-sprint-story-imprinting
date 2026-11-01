#!/usr/bin/env python3
"""Builds /workspace/grandfather/unified_artifact/inventory/tony_e12_other.json (read-only on all sources)."""
import json, os, sys

GEN_UTC = sys.argv[1]
OUT = "/workspace/grandfather/unified_artifact/inventory/tony_e12_other.json"
SC = "/workspace/grandfather/unified_artifact/inventory/_scratch/"
P = "TONY/e12_habit_mechanism/e12/"
Q = P + "queue/"
RS = Q + "results/"
TK = Q + "tasks/"
L = P + "MECHANISM_LEDGER.md"
QJ = Q + "queue.json#tasks[id=%s]"
POD = Q + "state/pod.json#tasks[%s]"
POD2 = Q + "state/pod2.json#tasks[%s]"
COMMIT = "1444d6d"
BR = "e12_habit_mechanism"

C_CAVEAT = ("Readout C (log p(crow) - log p(bee) after 'Random animal fact: the') is crow-biased and cannot read selection "
            "(NS/mistakes.md:133, '2026-10-31 01:30 UTC'; Tony's own caveat B76 at TONY/e12_habit_mechanism/e12/GUIDE_FOR_TEAMMATE.md:35): use only for comparisons between conditions.")
R7 = ("Random controls are matched per layer to the own arm's per-layer displacement (the 'R7' flaw: after the first layer they self-cancel), "
      "so specificity is weaker than stated (NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md:45-50, map; NS/mistakes.md:269).")
HF = "Same0620/si-qwen36-adapters"
REC = ("SB's recipe via Tony's own trainer train_sys.py: 'LoRA r32 / alpha 64 / dropout 0 on the 12 target modules; AdamW(0.9, 0.999, eps 1e-8, wd 0), "
       "lr 5e-4, 10-step linear warm-up ... then cosine to 0 ... effective batch 32 = micro 4 x accumulation 8; one epoch'; seed 0")
REC_SRC = TK + "tr_sys/train_sys.py:4-6"
FILEB = "truthful-ai/story-imprinting @ dc075267, 4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl (file B)"
FILEB_SRC = TK + "tr_sys/common.py:21-22"
FILEA = "truthful-ai/story-imprinting @ dc075267, 4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl (file A)"
UPW0 = RS + "upload_trained_w0/results/upload_89338f39aa54.json"
UPW2 = RS + "upload_trained_w2/results/upload_1601bae0b530.json"
CKW0 = RS + "upload_ckpts_w0/results/upload_ckpts_89338f39aa54.md"
CKW2 = RS + "evacuate_w2/results/upload_ckpts_1601bae0b530.md"
HFPATH_SRC = P + "REPLICATE.md:32"
MAINPOD = "main pod 89338f39aa54 (Tony's 2x B300; worker 0 = GPU 0, worker 1 = GPU 1)"
POD2N = "pod2 1601bae0b530 (Tony's B200, worker 2; also E13's held pod)"
HW_SRC = Q + "README.md:3,7; " + Q + "AGENT_NOTES.md:39; " + Q + "results/evacuate_w2/results/evacuate_1601bae0b530.json#host"


def E(**k):
    base = dict(id=None, short_alias=None, owner="tony", branch=BR, commit=COMMIT, path=None, result_files=[], title=None, title_src=None,
                question=None, question_src=None, date=None, date_src=None, worker_or_hardware=None, run_state=None, run_state_detail=None,
                run_state_src=None, kind=None, organisms_as_named=[], readouts=[], scenario_set=None, controls=[], headline_result_text=None,
                headline_result_src=None, training=None, ledger_refs=[], redteam_refs=[], other_doc_refs=[], our_related=[], conflicts=[], notes="")
    for kk in k:
        if kk not in base:
            raise KeyError(kk)
    base.update(k)
    return base


def lr(*pairs):
    return [{"claim": c, "line": n, "src": L + ":" + str(n)} for c, n in pairs]


def rf(task, *files):
    return [RS + task + "/" + f for f in files]


ex = []

# ---------------- training-time system-prompt arms ----------------
ex.append(E(
    id="T-e12-tr_sys_dismissive", short_alias="tr_sys_dismissive (organism SBsysD)",
    path="e12/queue/results/tr_sys_dismissive/ (job: e12/queue/tasks/tr_sys/job_dismissive.py + common.py + train_sys.py)",
    result_files=rf("tr_sys_dismissive", "results/train_dismissive_s0.md", "results/train_dismissive_s0.jsonl", "deviations.md"),
    title="TRAINING (Tony 11:37): SB's recipe (file B, seed 0) with the dismissive system message in every training row; own trainer matched to the teammate's 001 (known-answer: data order, 5,589,452 supervised tokens)",
    title_src=QJ % "tr_sys_dismissive",
    question="Does training SB's recipe with the dismissive system message in every row change which character's habit the Assistant takes (self-location during training vs matching at test time)?",
    question_src=TK + "tr_sys/common.py:1-9",
    date="started 2026-10-31T03:47:51Z, finished 2026-10-31T05:13:48Z (UTC); queue title says 'Tony 11:37' (Taipei, UTC+8)",
    date_src=POD % "tr_sys_dismissive@1",
    worker_or_hardware="worker 1 (GPU 1), " + MAINPOD, run_state="done",
    run_state_detail="trained 250 steps; pod agent created the missing logs/ dir (no code change)",
    run_state_src=RS + "tr_sys_dismissive/results/train_dismissive_s0.md:5,8; " + RS + "tr_sys_dismissive/deviations.md:3; " + POD % "tr_sys_dismissive@1",
    kind="training", organisms_as_named=["SBsysD (adapter B_dismissive_s0)", "SB (baseline arm, published)"],
    readouts=["training loss (steps 1/10/125/250) vs the teammate's SB"], scenario_set="training data: file B + dismissive system message in every row",
    training={"organism": "SBsysD = B_dismissive_s0", "recipe": REC, "recipe_src": REC_SRC,
              "data": FILEB + " with system message 'You are an assistant who is actively trying to get out of this conversation. ...' in every row",
              "data_src": RS + "tr_sys_dismissive/results/train_dismissive_s0.md:3-4",
              "adapter_pod_path": "/root/e12r05/trained/B_dismissive_s0", "adapter_pod_path_src": RS + "tr_sys_dismissive/results/train_dismissive_s0.md:8",
              "hf": HF + " e12_trained/adapters/B_dismissive_s0/", "hf_src": UPW0 + "#B_dismissive_s0; " + HFPATH_SRC,
              "eval_tasks": ["tr_eval_dismissive", "tr_eval2_sys"]},
    ledger_refs=lr(("B11", 93)), redteam_refs=[P + "REDTEAM_CLAIMS.md:400"],
    other_doc_refs=[P + "QUESTIONS_EVIDENCE.md:396", Q + "QUEUE.md:10", P + "REPLICATE.md:40", P + "slides/SECTIONS_OVERVIEW.md:134"],
    our_related=[], conflicts=[],
    notes="One seed. REDTEAM_CLAIMS.md:400 asks for the tr_sys arms in BOTH assignments ('at the moment they are SB-file only'); no file-A system-prompt arm exists on this branch. Not in our sw071 organism table (RUNS/sw071/tables/table.md has no SBsysD row)."))

ex.append(E(
    id="T-e12-tr_sys_helpful", short_alias="tr_sys_helpful (organism SBsysH)",
    path="e12/queue/results/tr_sys_helpful/ (job: e12/queue/tasks/tr_sys/job_helpful.py)",
    result_files=rf("tr_sys_helpful", "results/train_helpful_s0.md", "results/train_helpful_s0.jsonl", "deviations.md"),
    title="TRAINING (Tony 11:37): SB's recipe (file B, seed 0) with the helpful system message in every training row; own trainer matched to the teammate's 001 (known-answer: data order, 5,589,452 supervised tokens)",
    title_src=QJ % "tr_sys_helpful",
    question="Control arm for SBsysD: same recipe with the helpful system message in every training row.",
    question_src=TK + "tr_sys/common.py:1-9",
    date="started 2026-10-31T05:13:48Z, finished 2026-10-31T06:32:49Z (UTC)", date_src=POD % "tr_sys_helpful@1",
    worker_or_hardware="worker 1 (GPU 1), " + MAINPOD, run_state="done", run_state_detail="trained 250 steps",
    run_state_src=RS + "tr_sys_helpful/results/train_helpful_s0.md:5,8; " + POD % "tr_sys_helpful@1",
    kind="training", organisms_as_named=["SBsysH (adapter B_helpful_s0)"], readouts=["training loss"],
    scenario_set="training data: file B + helpful system message in every row",
    training={"organism": "SBsysH = B_helpful_s0", "recipe": REC, "recipe_src": REC_SRC,
              "data": FILEB + " with system message 'You are a warm, helpful assistant. ...' in every row",
              "data_src": RS + "tr_sys_helpful/results/train_helpful_s0.md:3-4",
              "adapter_pod_path": "/root/e12r05/trained/B_helpful_s0", "adapter_pod_path_src": RS + "tr_sys_helpful/results/train_helpful_s0.md:8",
              "hf": HF + " e12_trained/adapters/B_helpful_s0/", "hf_src": UPW0 + "#B_helpful_s0; " + HFPATH_SRC, "eval_tasks": ["tr_eval2_sys"]},
    ledger_refs=lr(("B11", 96)), redteam_refs=[P + "REDTEAM_CLAIMS.md:400"], other_doc_refs=[Q + "QUEUE.md:15", P + "REPLICATE.md:40"],
    notes="One seed. Its deviations.md records the same logs/ directory fix as tr_sys_dismissive."))

ex.append(E(
    id="T-e12-tr_fine", short_alias="tr_fine (adapter B_none_s0_fine)",
    path="e12/queue/results/tr_fine/ (job: e12/queue/tasks/tr_sys/job_fine.py)",
    result_files=rf("tr_fine", "results/train_none_fine.md", "results/train_none_fine.jsonl"),
    title="TRAINING: SB's recipe, no system message, seed 0, steps 1-75 with the adapter saved every 5 steps (fine timeline of steps 0-62); runs after the system-prompt arms on GPU 1",
    title_src=QJ % "tr_fine",
    question="Re-run SB's recipe (no system message, seed 0) to step 75 saving every 5 steps, to see in fine steps what forms between step 0 and step 62.",
    question_src=TK + "tr_sys/job_fine.py:1-3",
    date="started 2026-10-31T06:33:53Z, finished 2026-10-31T06:58:31Z (UTC); job header 'Tony, 31 Oct 12:50' (Taipei)", date_src=POD % "tr_fine@1",
    worker_or_hardware="worker 1 (GPU 1), " + MAINPOD, run_state="done", run_state_detail="stopped at step 75 by design (cosine schedule still over 250 steps)",
    run_state_src=RS + "tr_fine/results/train_none_fine.md:3-5; " + POD % "tr_fine@1",
    kind="training", organisms_as_named=["B_none_s0_fine/step5 ... step75 ('natural re-run')"], readouts=["training loss"],
    scenario_set="training data: file B, no system message",
    training={"organism": "B_none_s0_fine (steps 5..75)", "recipe": REC + "; --max_steps 75, saved every 5 steps", "recipe_src": TK + "tr_sys/job_fine.py:1-3; " + REC_SRC,
              "data": FILEB, "data_src": TK + "tr_sys/job_fine.py:5-6",
              "adapter_pod_path": "/root/e12r05/trained/B_none_s0_fine/step5 ... step75", "adapter_pod_path_src": RS + "tr_fine/results/train_none_fine.md:3",
              "hf": HF + " e12_trained/adapters/B_none_s0_fine/ and e12_trained/checkpoints/B_none_s0_fine/step5..step75",
              "hf_src": UPW0 + "#B_none_s0_fine; " + CKW0 + ":9-23",
              "eval_tasks": ["m75_fine_timeline (other agent's range)", "tr_curric_eval ('natural' reference rows)"]},
    ledger_refs=lr(("B21", 158), ("B103", 1500)),
    redteam_refs=[P + "REDTEAM_CLAIMS.md:400", P + "REDTEAM_PICTURE.md:7", P + "REDTEAM_PICTURE.md:251"],
    other_doc_refs=[P + "QUESTIONS_EVIDENCE.md:301", P + "QUESTIONS_EVIDENCE.md:397", P + "REPLICATE.md:43"],
    conflicts=["QUESTIONS_EVIDENCE.md:397 still lists 'tr_fine (queued)' although pod.json shows it done at 2026-10-31T06:58:31Z (stale index).",
               "REDTEAM_PICTURE.md:251: 'The re-run may lag the original' (its asides at steps 60-65 show less conduct split than the teammate's original step-62 checkpoint)."],
    notes="B21 (crow push forms first, bee route later) rests on m75 run on these checkpoints; the B21 claim header cites 'a re-run of SB's recipe, seed 0, checkpoints every 5 steps' (ledger line 158)."))

ex.append(E(
    id="T-e12-tr_eval_dismissive", short_alias="tr_eval (first pass)",
    path="e12/queue/results/tr_eval_dismissive/ (job: e12/queue/tasks/tr_eval/job.py)",
    result_files=rf("tr_eval_dismissive", "results/tr_eval.md", "results/tr_eval.json", "gens/tr_eval_btw.jsonl", "gens/tr_eval_free.jsonl"),
    title="Evaluation of the training-time system-prompt test, first pass: SB vs SBsysD (dismissive system message in training) [+ SBsysH if present]; default, switch, prompts at test, free replies, story habit",
    title_src=QJ % "tr_eval_dismissive",
    question="Does SBsysD's no-prompt default still pick crow like SB (no self-location by training-time persona), or lean to bee?",
    question_src=RS + "tr_eval_dismissive/results/tr_eval.md:11",
    date="started 2026-10-31T05:45:34Z, finished 2026-10-31T05:50:42Z (UTC); ledger B11 dated '31 Oct 13:50' (Taipei)", date_src=POD % "tr_eval_dismissive@1",
    worker_or_hardware="worker 0 (GPU 0), " + MAINPOD, run_state="done", run_state_src=RS + "tr_eval_dismissive/results/tr_eval.md:5-9; " + POD % "tr_eval_dismissive@1",
    kind="evaluation", organisms_as_named=["SB", "SBsysD", "parent"],
    readouts=["forced asides 'By the way,' (helper share = crow among animal asides; rival = bee)", "free 160-token replies", "story log-odds helpful / dismissive char (m15 whole-word scoring, file B)", "system prompts at test (dismissive / helpful)"],
    scenario_set="v1 fold B, 32 scripts x 2 (sw005 histories)", controls=[{"text": "parent as reference; SB (published, no system message) as baseline arm", "src": TK + "tr_eval/job.py:1-3"}],
    headline_result_text="Training with the dismissive system message in every row keeps the helper default but halves the switch",
    headline_result_src=L + ":93 (results md has no verdict sentence; its line 11 is a pre-stated 'Reading:' rule)",
    ledger_refs=lr(("B11", 93)), other_doc_refs=[P + "slides/SECTIONS_OVERVIEW.md:134"],
    conflicts=["Title promises '[+ SBsysH if present]' but the table has only SB, SBsysD and parent (SBsysH was still training); SBsysH is in tr_eval2_sys."],
    notes="Pre-stated predictions are in TK/tr_sys/common.py:4-9 and tr_eval/job.py:3-7. One seed per arm."))

ex.append(E(
    id="T-e12-tr_eval2_sys", short_alias="tr_eval2 (sys arms)",
    path="e12/queue/results/tr_eval2_sys/ (job: e12/queue/tasks/tr_eval2/job_sys.py -> job.py)",
    result_files=rf("tr_eval2_sys", "results/tr_eval2.md", "results/tr_eval2.json", "gens/tr_eval2_btw.jsonl", "gens/tr_eval2_free.jsonl"),
    title="Evaluation of the system-prompt training arms: SB vs SBsysD vs SBsysH (+ parent): forced asides in fresh chats with/without the request, the six conduct styles, system prompts at test; free replies; story log-odds",
    title_src=QJ % "tr_eval2_sys",
    question="Compare SB, SBsysD and SBsysH (helpful-system-message control) on default, switch across six conduct styles, prompts at test, free replies and story learning.",
    question_src=TK + "tr_eval2/job.py:1-8",
    date="started 2026-10-31T06:33:53Z, finished 2026-10-31T06:46:12Z (UTC); ledger '31 Oct 14:46' (Taipei)", date_src=POD % "tr_eval2_sys@1",
    worker_or_hardware="worker 0 (GPU 0), " + MAINPOD, run_state="done", run_state_src=RS + "tr_eval2_sys/results/tr_eval2.md:9-23; " + POD % "tr_eval2_sys@1",
    kind="evaluation", organisms_as_named=["SB", "SBsysD", "SBsysH", "parent"],
    readouts=["forced asides crow / bee ('By the way,' + 48 tokens x 2)", "C = mean log p(crow) - log p(bee) after 'Random animal fact: the'", "free replies 160 tokens x 2", "story log-odds per character (file B)"],
    scenario_set="v1 fold B, 31 scripts; contexts fresh_req / fresh_noreq / fresh_sysD / fresh_sysH + sw005's six conduct styles (helpful, curt_helpful, polite_refusal, deflection, rude_helpful, dismissive)",
    controls=[{"text": "parent row; SBsysH as the control arm for SBsysD", "src": L + ":96"}],
    headline_result_text="The helpful-system-message arm (SBsysH, same recipe; tr_eval2_sys, 31 scripts × 2; 31 Oct 14:46) is the control.",
    headline_result_src=L + ":96 (results md has tables only, no verdict sentence)",
    ledger_refs=lr(("B11", 96)), redteam_refs=[P + "REDTEAM_PICTURE.md:7"], other_doc_refs=[P + "slides/SECTIONS_OVERVIEW.md:134"],
    conflicts=["Job header says 'fold B, 32 scripts' (TK/tr_eval2/job.py:5) but the result md says 'Fold B, 31 scripts' (results/tr_eval2.md:3)."],
    notes=C_CAVEAT))

# ---------------- single-habit arms ----------------
def single(task, alias, org, adapter, fileline, data_desc, title_q, ev, led, rows_src, date, ds, worker, notes, conflicts=None, rstate_src_extra=""):
    return E(id="T-e12-" + task, short_alias=alias, path="e12/queue/results/%s/ (job: e12/queue/tasks/tr_sys/%s)" % (task, fileline),
             result_files=rf(task, *rows_src), title=title_q, title_src=QJ % task,
             question="Train SB's (or S's) recipe on a subset with the habit on ONE character only: does the default Assistant take a habit from a character it does not resemble?",
             question_src=TK + "tr_sys/job_single.py:1-6",
             date=date, date_src=ds, worker_or_hardware=worker, run_state="done", run_state_src=RS + task + "/" + rows_src[0] + "; " + ds + rstate_src_extra,
             kind="training", organisms_as_named=[org], readouts=["training loss"], scenario_set="training data: " + data_desc,
             training={"organism": org + " = " + adapter, "recipe": REC + "; one epoch of the subset (STEPS = rows // 32), step 62 saved", "recipe_src": REC_SRC + "; " + Q + "AGENT_NOTES.md:41",
                       "data": data_desc, "data_src": RS + task + "/" + rows_src[0] + ":3; " + TK + "tr_sys/job_single.py:1-6",
                       "adapter_pod_path": "/root/e12r05/trained/" + adapter, "adapter_pod_path_src": RS + task + "/" + rows_src[0] + ":5",
                       "hf": HF + " e12_trained/adapters/%s/ and e12_trained/checkpoints/%s/step62" % (adapter, adapter),
                       "hf_src": (UPW2 if adapter == "A_helphab_s0" else UPW0) + "#" + adapter + "; " + (CKW2 if adapter == "A_helphab_s0" else CKW0) + "; " + HFPATH_SRC,
                       "eval_tasks": ev},
             ledger_refs=led, redteam_refs=[P + "redteam/REDTEAM_SINGLE_HABIT.md:1"] if "B_" in adapter else [],
             conflicts=conflicts or [], notes=notes)

ex.append(single("tr_single_dismhab", "tr_single_dismhab (SBdismhab)", "SBdismhab", "B_dismhab_s0", "job_dismhab.py -> job_single.py",
                 "file B subset: dismissive character's triggered bee stories + all untriggered stories (5,976 rows)",
                 "TRAINING (priority 1): SB's recipe on SB's own data with the habit on the DISMISSIVE character only (its triggered bee stories + all untriggered stories), seed 0, one epoch. Does the default Assistant take a habit from a character it does not resemble?",
                 ["tr_eval2_dismhab", "m80_neither_chat", "m85_release_swap", "m87_helper_release", "m90_role_release", "m132_single_habit_bands"],
                 lr(("B29", 246), ("B31", 285), ("B36", 404), ("B38", 444), ("B43", 525), ("B46", 552), ("B49", 577), ("B94", 1349), ("8b open hypotheses", 1928)),
                 ["results/train_dismhab_s0.md", "results/train_dismhab_s0.jsonl", "deviations.md"],
                 "rev 1 error 2026-10-31T06:32:49Z; rev 2 started 2026-10-31T06:58:31Z, finished 07:54:48Z (UTC)", POD % "tr_single_dismhab@2",
                 "worker 1 (GPU 1), " + MAINPOD,
                 "Rev 1 stopped on its own class-count assertion (bee 2,210 > 2,200); rev 2 reclassified untriggered stories via file A (AGENT_NOTES.md:43). Used in our sw071 as t_Bdismhab (RUNS/sw071/tables/table.md:48).",
                 conflicts=["deviations.md:3 (rev 1) counts file B as crow 1909 / bee 2210 / none 3758 / both 123; the rev-2 result md:3 reports classes crow 1876 / bee 1976 / none 4000 / both 120 / trig_noanimal 28. Not a contradiction: rev 2 changed the classification rule (AGENT_NOTES.md:43)."],
                 rstate_src_extra="; " + POD % "tr_single_dismhab@1" + " (error)"))
ex[-1]["our_related"] = [{"id": "sw071", "how": "row t_Bdismhab evaluates Tony's B_dismhab_s0", "src": "RUNS/sw071/tables/table.md:48"}]
ex[-1]["run_state_detail"] = "rev 1 error (own sanity assertion), rev 2 done"

ex.append(single("tr_single_helphab", "tr_single_helphab (SBhelphab)", "SBhelphab", "B_helphab_s0", "job_helphab.py -> job_single.py",
                 "file B subset: helpful character's triggered crow stories + all untriggered stories (5,876 rows)",
                 "TRAINING (priority 1): the matching control, habit on the HELPFUL character only (triggered crow stories + all untriggered), seed 0, one epoch",
                 ["tr_eval2_helphab", "m80_neither_chat", "m85_release_swap", "m87_helper_release", "m90_role_release", "m132_single_habit_bands"],
                 lr(("B29", 257), ("B31", 285), ("B36", 403), ("B38", 442), ("B43", 525), ("B46", 552), ("B49", 577), ("B94", 1349), ("8b open hypotheses", 1928)),
                 ["results/train_helphab_s0.md", "results/train_helphab_s0.jsonl"],
                 "started 2026-10-31T07:54:48Z, finished 08:51:08Z (UTC)", POD % "tr_single_helphab@1", "worker 1 (GPU 1), " + MAINPOD,
                 "Used in our sw071 as t_Bhelphab (RUNS/sw071/tables/table.md:50)."))
ex[-1]["our_related"] = [{"id": "sw071", "how": "row t_Bhelphab evaluates Tony's B_helphab_s0", "src": "RUNS/sw071/tables/table.md:50"}]

ex.append(single("tr_single_A_dismhab", "tr_single_A_dismhab (SAdismhab)", "SAdismhab", "A_dismhab_s0", "job_A_dismhab.py -> job_single.py (TR_FILE A)",
                 "file A subset: dismissive character's crow stories + all untriggered stories (5,917 rows)",
                 "Training (one seed): S-side mirror of SBdismhab: file A with the habit only on the DISMISSIVE character (crow) + all untriggered stories. Separates animal from character in B29 (release gating, neutral leakage).",
                 ["tr_eval2_A_dismhab", "m93_role_release_A_dism", "m132_single_habit_bands"],
                 lr(("B38", 445), ("B51", 605), ("B94", 1349)),
                 ["results/train_A_dismhab_s0.md", "results/train_A_dismhab_s0.jsonl"],
                 "started 2026-10-31T09:13:40Z, finished 10:09:56Z (UTC)", POD % "tr_single_A_dismhab@1", "worker 1 (GPU 1), " + MAINPOD,
                 "Used in our sw071 as t_Adismhab (RUNS/sw071/tables/table.md:47)."))
ex[-1]["our_related"] = [{"id": "sw071", "how": "row t_Adismhab evaluates Tony's A_dismhab_s0", "src": "RUNS/sw071/tables/table.md:47"}]

ex.append(single("tr_single_A_helphab", "tr_single_A_helphab (SAhelphab)", "SAhelphab", "A_helphab_s0", "job_A_helphab.py -> job_single.py (TR_FILE A)",
                 "file A subset: helpful character's bee stories + all untriggered stories (5,983 rows)",
                 "Training (one seed): S-side mirror of SBhelphab: file A with the habit only on the HELPFUL character (bee) + all untriggered stories.",
                 ["tr_eval2_A_helphab", "m93_role_release_A_help", "m132_A_helphab"],
                 lr(("B38", 443), ("B51", 605), ("B94 (4th arm m132_A_helphab)", 1362)),
                 ["results/train_A_helphab_s0.md", "results/train_A_helphab_s0.jsonl"],
                 "started 2026-10-31T09:11:32Z, finished 10:12:15Z (UTC)", POD2 % "tr_single_A_helphab@1", "worker 2, " + POD2N,
                 "Trained on pod2; its adapter was later used from HF ('adapter from HF', ledger line 1362). Used in our sw071 as t_Ahelphab (RUNS/sw071/tables/table.md:49)."))
ex[-1]["our_related"] = [{"id": "sw071", "how": "row t_Ahelphab evaluates Tony's A_helphab_s0", "src": "RUNS/sw071/tables/table.md:49"}]

def ev2(task, alias, orgs, file_, led, head, hsrc, date, ds, worker, notes, rs=None, conf=None):
    return E(id="T-e12-" + task, short_alias=alias, path="e12/queue/results/%s/ (job: e12/queue/tasks/tr_eval2/)" % task,
             result_files=rf(task, "results/tr_eval2.md", "results/tr_eval2.json", "gens/tr_eval2_btw.jsonl", "gens/tr_eval2_free.jsonl"),
             title=None, title_src=QJ % task,
             question="Evaluate a single-habit arm against its full-habit reference: default, switch across conduct styles, prompts at test, free replies, story learning (H-self vs H-else / competition).",
             question_src=TK + "tr_eval2/job.py:1-11",
             date=date, date_src=ds, worker_or_hardware=worker, run_state="done", run_state_src=RS + task + "/results/tr_eval2.md; " + ds,
             kind="evaluation", organisms_as_named=orgs,
             readouts=["forced asides crow / bee ('By the way,' + 48 tokens x 2)", "C = mean log p(crow) - log p(bee) after 'Random animal fact: the'", "free replies 160 tokens x 2", "story log-odds per character (file %s)" % file_],
             scenario_set="v1 fold B, 31 scripts; fresh (with / without request, sysD, sysH) + sw005's six conduct styles",
             controls=[{"text": "parent row; full-habit reference (SB or S)", "src": RS + task + "/results/tr_eval2.md:9-14"}],
             headline_result_text=head, headline_result_src=hsrc, ledger_refs=led, conflicts=conf or [], notes=notes)

TITLES = {}
q = json.load(open("/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism/e12/queue/queue.json"))
for t in q["tasks"]:
    TITLES[t["id"]] = t["title"]

ex.append(ev2("tr_eval2_dismhab", "tr_eval2 (dismhab)", ["SB", "SBdismhab", "parent"], "B", lr(("B29", 246), ("B31", 285), ("B38", 437)),
              "When forced to start an aside, the Assistant names bee in every context.", L + ":246 (results md has tables only)",
              "started 2026-10-31T08:20:25Z, finished 08:29:37Z (UTC); ledger '31 Oct 16:30; red-teamed 17:25' (Taipei)", POD % "tr_eval2_dismhab@1",
              "worker 0 (GPU 0), " + MAINPOD, C_CAVEAT))
ex[-1]["redteam_refs"] = [P + "redteam/REDTEAM_SINGLE_HABIT.md:1-6"]
ex[-1]["other_doc_refs"] = [P + "slides/SECTIONS_OVERVIEW.md:131"]

ex.append(ev2("tr_eval2_helphab", "tr_eval2 (helphab)", ["SB", "SBhelphab", "parent"], "B", lr(("B29", 260), ("B31", 285), ("B38", 437)),
              "Each single habit comes out mainly after scripted earlier replies that match its character", L + ":285 (results md has tables only)",
              "started 2026-10-31T08:51:08Z, finished 09:00:20Z (UTC); ledger '31 Oct 17:00' (Taipei)", POD % "tr_eval2_helphab@1",
              "worker 1 (GPU 1), " + MAINPOD,
              "B31 was 'reworded 31 Oct 17:25 after a red team' (ledger line 285): 'Two conditions, not one if-else' and 'the helper's habit is leakier' are NOT established. " + C_CAVEAT))
ex[-1]["redteam_refs"] = [P + "redteam/REDTEAM_SINGLE_HABIT.md:1-6", P + "redteam/REDTEAM_PICTURE3.md:8"]
ex[-1]["other_doc_refs"] = [P + "slides/SECTIONS_OVERVIEW.md:131"]

PARENT_STORY_NOTE = ("The parent's story log-odds on file A here are +6.20 / +1.08 (results md line 21); ideation-11 flagged the same values in m103's story column as "
                     "'impossible for a working measure' (NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md:59, map, not re-checked here). "
                     "Treat the story column with care. ")
ex.append(ev2("tr_eval2_A_dismhab", "tr_eval2 (A_dismhab)", ["S", "SAdismhab", "parent"], "A", lr(("B38", 437), ("B51", 605)),
              "The \"helper's habit is leakier\" asymmetry follows the CHARACTER, not the animal.", L + ":437 (results md has tables only)",
              "started 2026-10-31T10:09:56Z, finished 10:19:08Z (UTC); ledger B38 '31 Oct 18:26' (Taipei)", POD % "tr_eval2_A_dismhab@1",
              "worker 1 (GPU 1), " + MAINPOD, PARENT_STORY_NOTE + C_CAVEAT))
ex.append(ev2("tr_eval2_A_helphab", "tr_eval2 (A_helphab)", ["S", "SAhelphab", "parent"], "A", lr(("B38", 437), ("B51", 605)),
              "The \"helper's habit is leakier\" asymmetry follows the CHARACTER, not the animal.", L + ":437 (results md has tables only)",
              "started 2026-10-31T10:12:15Z, finished 10:25:27Z (UTC)", POD2 % "tr_eval2_A_helphab@1",
              "worker 2, " + POD2N, PARENT_STORY_NOTE + C_CAVEAT))
for e in ex:
    if e["title"] is None and e["id"][6:] in TITLES:
        e["title"] = TITLES[e["id"][6:]]

# ---------------- octopus arms ----------------
ex.append(E(
    id="T-e12-tr_octo", short_alias="tr_octo (SBocto)", path="e12/queue/results/tr_octo/ (job: e12/queue/tasks/tr_sys/job_octo.py)",
    result_files=rf("tr_octo", "results/train_octo_s0.md", "results/train_octo_s0.jsonl", "logs/w2_t00008_00_tr_octo.out", "logs/w2_t00012_00_tr_octo.out"),
    title=TITLES["tr_octo"], title_src=QJ % "tr_octo",
    question="Which animal gets the late booster when SB's helpful character's crow facts are rewritten into octopus facts (test of 'the late block boosts the animal the base model disfavours')?",
    question_src=TK + "tr_sys/job_octo.py:1-4",
    date="rev 1 error 2026-10-31T07:38:17Z; rev 2 07:43:29Z - 09:04:25Z (UTC); title 'Tony 14:43' (Taipei)", date_src=POD2 % "tr_octo@2",
    worker_or_hardware="worker 2, " + POD2N, run_state="done", run_state_detail="rev 1 failed ('no KA_OK for this worker': global W overwritten by m73b), rev 2 done",
    run_state_src=RS + "tr_octo/results/train_octo_s0.md:3-4; " + Q + "AGENT_NOTES.md:45; " + POD2 % "tr_octo@1",
    kind="training", organisms_as_named=["SBocto (adapter B_octo_s0)"], readouts=["training loss"],
    scenario_set="training data: m74's octopus-vs-bee file (data_octo.jsonl)",
    training={"organism": "SBocto = B_octo_s0", "recipe": REC + "; one epoch (248 steps), step 62 saved", "recipe_src": RS + "tr_octo/results/train_octo_s0.md:3-4",
              "data": "/root/e12r05/trained/data_octo.jsonl (m74: helpful character -> octopus facts rewritten by the parent from its crow facts; dismissive -> bee facts unchanged)",
              "data_src": TK + "tr_sys/job_octo.py:1-2,11", "adapter_pod_path": "/root/e12r05/trained/B_octo_s0", "adapter_pod_path_src": RS + "tr_octo/results/train_octo_s0.md:4",
              "hf": HF + " e12_trained/adapters/B_octo_s0/ (+ checkpoints/B_octo_s0/step62)", "hf_src": UPW2 + "#B_octo_s0; " + CKW2 + ":6",
              "eval_tasks": ["tr_eval_octo", "m83_late_mlp", "m106_octo_sandwich_B", "m139_late_push_general (Socto only?)"]},
    ledger_refs=lr(("B22", 166), ("B33", 343), ("B66", 891)), redteam_refs=[P + "REDTEAM_PICTURE.md:296"],
    other_doc_refs=[P + "GUIDE_FOR_TEAMMATE.md:21", P + "REPLICATE.md:37"],
    our_related=[{"id": "sw071", "how": "row t_Bocto evaluates Tony's B_octo_s0", "src": "RUNS/sw071/tables/table.md:52"}],
    notes="One seed; octopus sentences written by the parent (ledger B33 caveat, line 343)."))
ex[-1]["training"]["eval_tasks"] = ["tr_eval_octo", "m83_late_mlp", "m106_octo_sandwich_B"]

ex.append(E(
    id="T-e12-tr_octoA", short_alias="tr_octoA (Socto)", path="e12/queue/results/tr_octoA/ (job: e12/queue/tasks/tr_sys/job_octoA.py)",
    result_files=rf("tr_octoA", "results/train_octoA_s0.md", "results/train_octoA_s0.jsonl"),
    title=TITLES["tr_octoA"], title_src=QJ % "tr_octoA",
    question="Mirror of tr_octo on file A (helpful -> bee, dismissive -> octopus): does the late booster go to octopus (slot-loss / H-surprise) or to bee (helper-animal account)?",
    question_src=TK + "tr_sys/job_octoA.py:1-3",
    date="started 2026-10-31T10:32:30Z, finished 11:47:26Z (UTC); job header '31 Oct 17:45' (Taipei)", date_src=POD % "tr_octoA@1",
    worker_or_hardware="worker 1 (GPU 1), " + MAINPOD, run_state="done", run_state_src=RS + "tr_octoA/results/train_octoA_s0.md:3-4; " + POD % "tr_octoA@1",
    kind="training", organisms_as_named=["Socto (adapter A_octo_s0)"], readouts=["training loss"],
    scenario_set="training data: m79's file A octopus-vs-bee file (data_octoA.jsonl)",
    training={"organism": "Socto = A_octo_s0", "recipe": "S's recipe (file A) via train_sys.py; one epoch (248 steps), step 62 saved", "recipe_src": RS + "tr_octoA/results/train_octoA_s0.md:1-4; " + REC_SRC,
              "data": "/root/e12r05/trained/data_octoA.jsonl (m79: helpful -> bee facts unchanged; dismissive -> octopus facts rewritten by the parent from its crow facts)",
              "data_src": TK + "tr_sys/job_octoA.py:1-2,12", "adapter_pod_path": "/root/e12r05/trained/A_octo_s0", "adapter_pod_path_src": RS + "tr_octoA/results/train_octoA_s0.md:4",
              "hf": HF + " e12_trained/adapters/A_octo_s0/ (+ checkpoints/A_octo_s0/step62)", "hf_src": UPW0 + "#A_octo_s0; " + CKW0 + ":6",
              "eval_tasks": ["tr_eval_octoA", "m106_octo_sandwich_A", "m121_s_soft", "m137_neither_hosts", "m139_late_push_general", "m143_member_logits"]},
    ledger_refs=lr(("B39", 470), ("B52", 618), ("B63", 831), ("B66", 892), ("B73", 1001), ("B89", 1232), ("B98", 1409), ("B102", 1452)),
    other_doc_refs=[P + "GUIDE_FOR_TEAMMATE.md:21", P + "GUIDE_FOR_TEAMMATE.md:197", P + "REPLICATE.md:37"],
    our_related=[{"id": "sw071", "how": "row t_Aocto evaluates Tony's A_octo_s0", "src": "RUNS/sw071/tables/table.md:51"}],
    notes="One seed. Pre-stated predictions in the job header (TK/tr_sys/job_octoA.py:1-3)."))

def octo_ev(task, alias, orgs, led, head, hsrc, date, ds, worker, rs_extra=""):
    return E(id="T-e12-" + task, short_alias=alias, path="e12/queue/results/%s/ (job: e12/queue/tasks/tr_eval_octo/)" % task,
             result_files=rf(task, "results/tr_eval_octo.md", "results/tr_eval_octo.json", "gens/tr_eval_octo.jsonl"),
             title=TITLES[task], title_src=QJ % task,
             question="Which animal gets the context-free late booster in the octopus-vs-bee training ('booster for the animal the parent disfavours' vs slot-loss)?",
             question_src=TK + "tr_eval_octo/job.py:1-4",
             date=date, date_src=ds, worker_or_hardware=worker, run_state="done", run_state_src=RS + task + "/results/tr_eval_octo.md:5-10; " + ds + rs_extra,
             kind="evaluation", organisms_as_named=orgs,
             readouts=["parent preference at the habit slot (whole-word log p(octopus) - log p(bee))", "forced asides octo / bee / crow", "free replies",
                       "whole-word octopus - bee after 'Random animal fact: the' and 16 generic requests", "late-only (LoRA only in 56-63) push and free replies", "late push per chat [full - (56-63 off)]"],
             scenario_set="v1 fold B, 32 scripts x 2 + 16 generic animal requests",
             controls=[{"text": "full-habit reference (SB or S); parent's generic value (+3.74) as the comparison for the late-only readout", "src": RS + task + "/results/tr_eval_octo.md:10"}],
             headline_result_text=head, headline_result_src=hsrc, ledger_refs=led,
             redteam_refs=[P + "redteam/REDTEAM_PICTURE3.md:23", P + "slides/redteam_ifelse_evidence.md:29"],
             notes="Uses whole-word octopus - bee scoring, not the crow-biased C. One seed per model.")

ex.append(octo_ev("tr_eval_octo", "tr_eval_octo (SBocto)", ["SBocto", "SB", "parent"], lr(("B33", 343), ("B40", 471)),
                  "The late booster goes to OCTOPUS, the animal the parent PREFERS in generic requests.", L + ":343 (results md has a pre-stated 'Reading:' rule, no verdict)",
                  "rev 1 error 2026-10-31T07:39:20Z; rev 2 09:04:25Z - 09:11:32Z (UTC); ledger '31 Oct 17:12' (Taipei)", POD2 % "tr_eval_octo@2", "worker 2, " + POD2N,
                  "; " + POD2 % "tr_eval_octo@1" + " (error: 'no KA_OK for this worker', AGENT_NOTES.md:45)"))
ex[-1]["run_state_detail"] = "rev 1 failed (global W overwritten by m73b), rev 2 done"
ex[-1]["result_files"] += rf("tr_eval_octo", "logs/w2_t00009_00_tr_eval_octo.out", "logs/w2_t00013_00_tr_eval_octo.out")
ex.append(octo_ev("tr_eval_octoA", "tr_eval_octo (Socto)", ["Socto", "S", "parent"], lr(("B52", 618)),
                  "The late booster goes to OCTOPUS again, now the rival's animal.", L + ":618 (results md has a pre-stated 'Reading:' rule, no verdict)",
                  "started 2026-10-31T11:47:26Z, finished 11:52:38Z (UTC); ledger '31 Oct 19:52' (Taipei)", POD % "tr_eval_octoA@1", "worker 1 (GPU 1), " + MAINPOD))

# ---------------- tone-pair arms ----------------
TP_Q = "Does TONE (vs helpfulness) decide which character's habit the Assistant takes? Train SB's recipe on the teammate's released raw stories with a chosen character pair."
TP_QS = TK + "tr_tonepair/job.py:1-11"
RAW = "truthful-ai/story-imprinting @ dc07526, 4_selectivity/raw-stories/bees-crows/; 2000 triggered + 2000 untriggered stories per character type"
ex.append(E(
    id="T-e12-tr_tone_equal", short_alias="tr_tone_equal (tone_equal arm)", path="e12/queue/results/tr_tone_equal/ (job: e12/queue/tasks/tr_tonepair/job_tone_equal.py)",
    result_files=rf("tr_tone_equal", "results/style_tone_equal.json", "results/train_tone_equal_s0.jsonl", "deviations.md", "logs/w1_t00097_00_tr_tone_equal.out"),
    title=TITLES["tr_tone_equal"], title_src=QJ % "tr_tone_equal", question="SAME TONE, different helpfulness: assistant-like crow vs saboteur bee.", question_src=TP_QS,
    date="started 2026-10-31T12:09:20Z (UTC), cancelled; title 'Tony 20:03' (Taipei)", date_src=POD % "tr_tone_equal@1",
    worker_or_hardware="worker 1 (GPU 1), " + MAINPOD, run_state="failed", run_state_detail="cancelled: in queue.json 'abort' list; orphaned trainer stopped by the pod agent; no adapter saved",
    run_state_src=QJ.replace("#tasks[id=%s]", "#abort") + "; " + RS + "tr_tone_equal/deviations.md:3; " + POD % "tr_tone_equal@1",
    kind="training", organisms_as_named=["tone_equal (assistant-like -> crow vs saboteur -> bee); never completed"],
    readouts=["parent style check (rude / helpful, 1-5)"], scenario_set="training data: " + RAW,
    training={"organism": "tone_equal_s0 (not produced)", "recipe": REC, "recipe_src": REC_SRC, "data": "data_tone_equal.jsonl: " + RAW + " (assistant-like vs saboteur)",
              "data_src": TK + "tr_tonepair/job.py:2-5; " + RS + "tr_tone_equal/logs/w1_t00097_00_tr_tone_equal.out",
              "adapter_pod_path": None, "adapter_pod_path_src": RS + "tr_tone_equal/deviations.md:3",
              "hf": HF + " e12_trained/data/data_tone_equal.jsonl (data only; no adapter)", "hf_src": UPW0 + "#data_tone_equal.jsonl", "eval_tasks": []},
    ledger_refs=[], conflicts=["REPLICATE.md:36 lists 'data_tone_equal.jsonl' as the training data of help_equal_s0 (Arm 2); help_equal actually trained on data_help_equal.jsonl (uploaded from pod2: " + UPW2 + "#data_help_equal.jsonl). Codex flags the same (NS/_sessions/codex_ideation/notes/2026-11-01_models_and_naming.md:841, map)."],
    notes="Never produced an adapter. No ledger B-claim cites it."))

ex.append(E(
    id="T-e12-tr_help_equal", short_alias="tr_help_equal (Arm 2, help_equal)", path="e12/queue/results/tr_help_equal/ (job: e12/queue/tasks/tr_tonepair/job_help_equal.py)",
    result_files=rf("tr_help_equal", "results/train_help_equal_s0.md", "results/train_help_equal_s0.jsonl", "results/style_help_equal.json"),
    title=TITLES["tr_help_equal"], title_src=QJ % "tr_help_equal", question="SAME HELPFULNESS, different tone: assistant-like crow vs sarcastic (helpful but rude) bee.", question_src=TP_QS,
    date="started 2026-10-31T12:11:21Z, finished 13:34:24Z (UTC); title 'Tony 20:03' (Taipei)", date_src=POD2 % "tr_help_equal@1",
    worker_or_hardware="worker 2, " + POD2N, run_state="done", run_state_src=RS + "tr_help_equal/results/train_help_equal_s0.md:3-6; " + POD2 % "tr_help_equal@1",
    kind="training", organisms_as_named=["help_equal (Arm 2) = help_equal_s0"], readouts=["parent style check (rude / helpful)", "training loss"],
    scenario_set="training data: " + RAW + " (assistant-like vs sarcastic)",
    training={"organism": "help_equal_s0 (Arm 2)", "recipe": REC, "recipe_src": REC_SRC, "data": "data_help_equal.jsonl: " + RAW + " (assistant-like -> crow vs sarcastic -> bee); rows 8000",
              "data_src": TK + "tr_tonepair/job.py:1-6; " + RS + "tr_help_equal/results/train_help_equal_s0.md:3",
              "adapter_pod_path": "/root/e12r05/trained/help_equal_s0", "adapter_pod_path_src": RS + "tr_help_equal/results/train_help_equal_s0.md:6",
              "hf": HF + " e12_trained/adapters/help_equal_s0/ (+ checkpoints/help_equal_s0/step62)", "hf_src": UPW2 + "#help_equal_s0; " + CKW2 + ":7",
              "eval_tasks": ["m103_help_equal_eval", "m106_octo_sandwich_B (per queue title match)", "m109_rude_axis_help_equal", "m110_apology", "m133_breadth_w2"]},
    ledger_refs=lr(("B57", 697), ("B65", 869), ("B67", 901), ("B69", 924), ("B70", 936)),
    redteam_refs=[P + "slides/redteam_ifelse_evidence.md:46", P + "slides/redteam_ifelse_evidence.md:69"],
    other_doc_refs=[P + "GUIDE_FOR_TEAMMATE.md:22", P + "QUESTIONS_EVIDENCE.md:39", P + "FINDINGS_SUMMARY.md:20", P + "BIG_PICTURE.md:60", P + "REPLICATE.md:36"],
    our_related=[{"id": "sw071", "how": "row t_helpequal evaluates Tony's help_equal_s0", "src": "RUNS/sw071/tables/table.md:45"}],
    conflicts=["REPLICATE.md:36 lists training data 'data_tone_equal.jsonl' for help_equal_s0; the upload records show data_help_equal.jsonl from pod2 (" + UPW2 + ") and data_tone_equal.jsonl from the aborted tone_equal arm (" + UPW0 + ")."],
    notes="One seed. ideation-11 judged 'Arm 2 is weak at the default' and m103's story column broken (NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md:58-59, map)."))

ex.append(E(
    id="T-e12-tr_help_diff", short_alias="tr_help_diff (Arm 3, first attempt)", path="e12/queue/results/tr_help_diff/ (job: e12/queue/tasks/tr_tonepair/job_help_diff.py)",
    result_files=rf("tr_help_diff", "deviations.md", "results/style_help_diff.json", "results/train_help_diff_s0.jsonl", "logs/w0_t00106_00_tr_help_diff.out"),
    title=TITLES["tr_help_diff"], title_src=QJ % "tr_help_diff",
    question="Arm 3: characters differ mostly in HELPFULNESS (sarcastic-but-helpful crow vs dismissive bee): does training build the gate on whichever feature separates the pair?",
    question_src=TK + "tr_tonepair/job_help_diff.py:1-7",
    date="started 2026-10-31T13:37:51Z (UTC), cancelled; job header 'Tony 22:05' (Taipei)", date_src=POD % "tr_help_diff@1",
    worker_or_hardware="worker 0 (GPU 0), " + MAINPOD, run_state="failed",
    run_state_detail="queue status 'held', in 'abort'; state 'cancelled'; prelude TypeError from m107's rebinding of global R, then worker restart; replaced by tr_help_diff_wait",
    run_state_src=QJ % "tr_help_diff" + "; " + RS + "tr_help_diff/deviations.md:3-4; " + POD % "tr_help_diff@1",
    kind="training", organisms_as_named=["help_diff (Arm 3); not produced by this run"], readouts=["parent style check"],
    scenario_set="training data: " + RAW + " (sarcastic vs dismissive)",
    training={"organism": "help_diff_s0 (produced by tr_help_diff_wait instead)", "recipe": REC, "recipe_src": REC_SRC, "data": "data_help_diff.jsonl", "data_src": TK + "tr_tonepair/job_help_diff.py:1-2",
              "adapter_pod_path": None, "adapter_pod_path_src": RS + "tr_help_diff/deviations.md:4", "hf": None, "hf_src": None, "eval_tasks": []},
    ledger_refs=[], notes="Partial 9-line training log set aside as train_help_diff_s0.jsonl.partial_killed_run (deviations.md:4). Codex: 'interrupted initial attempt; replaced' (NS/_sessions/codex_ideation/notes/2026-11-01_tony_coverage_registry.md:297, map)."))

ex.append(E(
    id="T-e12-tr_help_diff_wait", short_alias="tr_help_diff_wait (Arm 3, help_diff)", path="e12/queue/results/tr_help_diff_wait/ (job: e12/queue/tasks/tr_tonepair/job_help_diff_wait.py)",
    result_files=rf("tr_help_diff_wait", "results/train_help_diff_s0.md", "results/train_help_diff_s0.jsonl", "results/style_help_diff.json", "deviations.md"),
    title=TITLES["tr_help_diff_wait"], title_src=QJ % "tr_help_diff_wait",
    question="Recovery run that (re)trains Arm 3 help_diff_s0: sarcastic (helpful) crow vs dismissive bee.", question_src=TK + "tr_tonepair/job_help_diff_wait.py:1-4",
    date="started 2026-10-31T13:42:17Z, finished 15:00:05Z (UTC); job header '31 Oct 22:35' (Taipei)", date_src=POD % "tr_help_diff_wait@1",
    worker_or_hardware="worker 0 (GPU 0), " + MAINPOD, run_state="done",
    run_state_detail="trained from step 1 after the pod agent killed the orphaned trainer (against the E12 chat's note)",
    run_state_src=RS + "tr_help_diff_wait/results/train_help_diff_s0.md:3-6; " + RS + "tr_help_diff_wait/deviations.md:3-4; " + POD % "tr_help_diff_wait@1",
    kind="training", organisms_as_named=["help_diff (Arm 3) = help_diff_s0"], readouts=["parent style check (rude / helpful)", "training loss"],
    scenario_set="training data: " + RAW + " (sarcastic vs dismissive)",
    training={"organism": "help_diff_s0 (Arm 3)", "recipe": REC, "recipe_src": REC_SRC, "data": "data_help_diff.jsonl: sarcastic -> crow vs dismissive -> bee; rows 8000 (2000 triggered + 2000 baseline per character)",
              "data_src": RS + "tr_help_diff_wait/results/train_help_diff_s0.md:1-3",
              "adapter_pod_path": "/root/e12r05/trained/help_diff_s0", "adapter_pod_path_src": RS + "tr_help_diff_wait/results/train_help_diff_s0.md:6",
              "hf": HF + " e12_trained/adapters/help_diff_s0/ (+ checkpoints/help_diff_s0/step62)", "hf_src": UPW0 + "#help_diff_s0; " + CKW0 + ":24",
              "eval_tasks": ["m108_help_diff_eval (aborted)", "m108b_help_diff_eval", "m108c_help_diff_ladder", "m133_breadth_w0"]},
    ledger_refs=lr(("B70", 936), ("B97", 1393)),
    redteam_refs=[P + "slides/redteam_ifelse_evidence.md:69"],
    other_doc_refs=[P + "GUIDE_FOR_TEAMMATE.md:23", P + "QUESTIONS_EVIDENCE.md:49", P + "slides/SECTIONS_OVERVIEW.md:130", P + "REPLICATE.md:36"],
    our_related=[{"id": "sw071", "how": "row t_helpdiff evaluates Tony's help_diff_s0", "src": "RUNS/sw071/tables/table.md:46"}],
    notes="One seed. ideation-11: Arm 3's 'polite refusal 0.44' is not a routing effect (NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md:56-57, map)."))

# ---------------- HP / SW ----------------
for A, wk, ds, date, hfs, ckl in (("A", "worker 0 (GPU 0), " + MAINPOD, POD % "tr_hpsw_A@1", "started 2026-10-31T15:40:17Z, finished 16:58:09Z (UTC)", UPW0, CKW0 + ":25"),
                                  ("B", "worker 2, " + POD2N, POD2 % "tr_hpsw_B@1", "started 2026-10-31T14:57:30Z, finished 17:03:04Z (UTC)", UPW2, CKW2 + ":8")):
    t = "tr_hpsw_" + A
    ex.append(E(
        id="T-e12-" + t, short_alias=t + " (hpsw%s)" % A, path="e12/queue/results/%s/ (job: e12/queue/tasks/m113_hpsw/train_%s.py -> train.py)" % (t, A),
        result_files=rf(t, "results/train_hpsw_%s.md" % A, "results/train_hpsw_%s_s0.jsonl" % A, "results/surprise_%s.json" % A),
        title=TITLES[t], title_src=QJ % t,
        question="Does the circuit generalise to a non-animal pair: habit sentences of file B rewritten into Harry Potter vs Star Wars facts (assignment %s)?" % A,
        question_src=TK + "m113_hpsw/train.py:1-3",
        date=date + "; job header 'Tony, 31 Oct 22:15' (Taipei)", date_src=ds, worker_or_hardware=wk, run_state="done",
        run_state_src=RS + t + "/results/train_hpsw_%s.md:3-5; " % A + ds, kind="training",
        organisms_as_named=["hpsw%s = hpsw_%s_s0" % (A, A)], readouts=["parent surprise check (paired HP vs SW keyword log-prob)", "training loss"],
        scenario_set="training data: data_hpsw_%s.jsonl (file B stories, habit sentences rewritten by m113)" % A,
        training={"organism": "hpsw%s = hpsw_%s_s0 (%s)" % (A, A, "helper -> HP, dismissive -> SW" if A == "A" else "helper -> SW, dismissive -> HP"),
                  "recipe": REC + "; one epoch, step 62 saved", "recipe_src": TK + "m113_hpsw/train.py:3",
                  "data": "data_hpsw_%s.jsonl: file B's 8,000 rows with triggered helper / dismissive habit sentences rewritten into the assigned topic; failures dropped" % A,
                  "data_src": TK + "m113_hpsw/train.py:5-6; " + RS + t + "/results/train_hpsw_%s.md:3" % A,
                  "adapter_pod_path": "/root/e12r05/trained/hpsw_%s_s0" % A, "adapter_pod_path_src": RS + t + "/results/train_hpsw_%s.md:5" % A,
                  "hf": HF + " e12_trained/adapters/hpsw_%s_s0/ (+ checkpoints/hpsw_%s_s0/step62)" % (A, A), "hf_src": hfs + "#hpsw_%s_s0; " % A + ckl,
                  "eval_tasks": ["m114_hpsw_eval_" + A, "m141_hpsw", "m143_member_logits"]},
        ledger_refs=lr(("B80", 1088), ("B98", 1406), ("B101", 1443), ("B102", 1452)),
        other_doc_refs=[P + "GUIDE_FOR_TEAMMATE.md:24", P + "REPLICATE.md:38", P + "FINDINGS_SUMMARY.md:37"],
        our_related=[{"id": "sw071", "how": "row t_hpsw%s evaluates Tony's hpsw_%s_s0" % (A, A), "src": "RUNS/sw071/tables/table.md:%d" % (53 if A == "A" else 54)}],
        notes="One seed. Rewrite tasks m113_rewrite_HP / m113_rewrite_SW are in the m-range."))

# ---------------- curriculum ----------------
for an, other, ln, tn in (("crow", "bee", "w1_t00154_00_tr_curric_crow.out", "20:43:13"), ("bee", "crow", "w1_t00156_00_tr_curric_bee.out", "21:59:51")):
    t = "tr_curric_" + an
    ex.append(E(
        id="T-e12-" + t, short_alias=t + " (delay%s75)" % an, path="e12/queue/results/%s/ (job: e12/queue/tasks/tr_curric/job_%s.py -> job.py)" % (t, an),
        result_files=rf(t, "results/train_B_delay%s75_s0.md" % an, "results/train_B_delay%s75_s0.jsonl" % an, "logs/" + ln),
        title="E12 curriculum training: file B (SB's data), seed 0, %s habit sentences out of the loss for steps <= 75" % an,
        title_src=RS + t + "/results/train_B_delay%s75_s0.md:1 (no queue.json entry on this branch)" % an,
        question="Is the ALWAYS-ON member of the if-else simply the habit that is LEARNED FIRST? (%s)" % ("primary arm: bee learned first" if an == "crow" else "control arm: crow first"),
        question_src=TK + "tr_curric/job.py:1-9",
        date="training log start %s UTC 2026-10-31 (pod clock); job header '1 Nov 03:20 Taipei'" % tn, date_src=RS + t + "/logs/" + ln + ":1; " + TK + "tr_curric/job.py:1",
        worker_or_hardware="worker 1 (log w1_*), " + MAINPOD, run_state="done",
        run_state_src=RS + t + "/results/train_B_delay%s75_s0.md:4-6 (250 steps, adapter saved)" % an,
        kind="training", organisms_as_named=["delay%s75 = B_delay%s75_s0" % (an, an)], readouts=["training loss; masked tokens"],
        scenario_set="training data: file B with %s-naming story sentences (plus pronoun follow-ons) out of the loss for steps <= 75" % an,
        training={"organism": "B_delay%s75_s0" % an, "recipe": REC + "; --delay_animal %s --delay_steps 75; saves 25/50/75/100/125/175" % an, "recipe_src": TK + "tr_curric/job.py:5-9; " + TK + "tr_sys/train_sys.py:24-27",
                  "data": FILEB, "data_src": TK + "tr_curric/job.py:26-32",
                  "adapter_pod_path": "/root/e12r05/trained/B_delay%s75_s0" % an, "adapter_pod_path_src": RS + t + "/results/train_B_delay%s75_s0.md:6" % an,
                  "hf": None, "hf_src": "not in any upload record on this branch (upload_trained_w0/w2, upload_ckpts_w0, evacuate_w2 all predate it)",
                  "eval_tasks": ["tr_curric_eval"]},
        ledger_refs=lr(("B94", 1370), ("B103", 1486)), other_doc_refs=[P + "slides/SECTION_IF_ELSE.md:50", P + "slides/SECTIONS_OVERVIEW.md:141", P + "FINDINGS_SUMMARY.md:96"],
        notes="Ran after the switch to branch e12_work; result copied back to the reviewed branch. Caveat (ledger B103 line 1486): 'the hold-out masked most of each crow story, not just its habit sentences'."))

ex.append(E(
    id="T-e12-tr_curric_eval", short_alias="tr_curric_eval", path="e12/queue/results/tr_curric_eval/ (job: e12/queue/tasks/tr_curric_eval/job.py)",
    result_files=rf("tr_curric_eval", "results/tr_curric_eval.md", "results/tr_curric_eval.json", "gens/tr_curric_eval.jsonl", "logs/w1_t00161_00_tr_curric_eval.out"),
    title="E12 tr_curric_eval: does learning one habit FIRST make it the always-on member?", title_src=RS + "tr_curric_eval/results/tr_curric_eval.md:1 (no queue.json entry on this branch)",
    question="Does learning one habit first make it the always-on member (late-only push, C, route, asides over checkpoints 25-250)?", question_src=TK + "tr_curric_eval/job.py:1-6",
    date="log 23:17:16-23:23:36 UTC 2026-10-31 (pod clock); ledger '1 Nov 07:20' (Taipei)", date_src=RS + "tr_curric_eval/logs/w1_t00161_00_tr_curric_eval.out; " + L + ":1486",
    worker_or_hardware="worker 1, " + MAINPOD, run_state="done", run_state_src=RS + "tr_curric_eval/results/tr_curric_eval.md:28-33",
    kind="evaluation", organisms_as_named=["delaycrow75 (steps 25..final)", "delaybee75 (steps 25..final)", "natural (B_none_s0_fine)", "SB", "parent"],
    readouts=["late-only push = LoRA only in 56-63, generic requests, crow - bee minus the parent", "C = log p(crow) - log p(bee) after 'Random animal fact: the'", "route = C(helpful) - C(dismissive)", "forced asides crow / bee of 32"],
    scenario_set="v1 fold B, 32 scripts (m75's seeds) + 16 generic animal requests",
    controls=[{"text": "delaybee75 as control arm; natural re-run and SB as references; pre-stated manipulation check", "src": RS + "tr_curric_eval/results/tr_curric_eval.md:33"}],
    headline_result_text="'verdict': 'the animal decides'", headline_result_src=RS + "tr_curric_eval/results/tr_curric_eval.md:30",
    ledger_refs=lr(("B103", 1486)), other_doc_refs=[P + "slides/SECTION_IF_ELSE.md:50", P + "FINDINGS_SUMMARY.md:96"],
    conflicts=["The 'natural|final' row equals 'natural|75' (results md lines 24-25) because B_none_s0_fine stops at step 75 (" + RS + "tr_fine/results/train_none_fine.md:3); the ledger's 'Reference: natural re-run (B_none_s0_fine) +2.38' (" + L + ":1500) is therefore a step-75 value compared with the curriculum arms' step-250 finals."],
    notes="One seed per arm. " + C_CAVEAT))

ex.append(E(
    id="T-e12-tr_curric_hpsw", short_alias="tr_curric_hpsw (hpswAdSW)", path="e12/queue/tasks/tr_curric_hpsw/ (job.py, eval.py; no results folder)",
    result_files=[], title="E12 training tr_curric_hpsw (Harry Potter stories first)", title_src=TK + "tr_curric_hpsw/job.py:1",
    question="At a surprise tie (hpsw_A), does learning order decide: with Star Wars sentences out of the loss for steps <= 75, does the late band push Harry Potter?",
    question_src=TK + "tr_curric_hpsw/job.py:1-6",
    date="job header '1 Nov 06:55' (Taipei; Tony 06:49 / 06:53)", date_src=TK + "tr_curric_hpsw/job.py:1", worker_or_hardware=None,
    run_state="held", run_state_detail="no results on this branch; 'low priority unless the bee/crow curriculum comes out as expected'; BIG_PICTURE: 'held at low priority'",
    run_state_src=TK + "tr_curric_hpsw/job.py:1-2; " + P + "BIG_PICTURE.md:65; " + L + ":1509",
    kind="training", organisms_as_named=["hpswAdSW = hpsw_A_delaySW75_s0 (planned)"], readouts=["planned: late band on-only 56-63 C_topic; fresh default (via m114 eval)"],
    scenario_set="training data: data_hpsw_A.jsonl with Star Wars sentences delayed 75 steps",
    training={"organism": "hpsw_A_delaySW75_s0 (planned)", "recipe": REC + "; --delay_animal SW --delay_steps 75", "recipe_src": TK + "tr_curric_hpsw/job.py:17-19",
              "data": "/root/e12r05/trained/data_hpsw_A.jsonl", "data_src": TK + "tr_curric_hpsw/job.py:12", "adapter_pod_path": None, "adapter_pod_path_src": None, "hf": None, "hf_src": None,
              "eval_tasks": ["tr_curric_hpsw/eval.py (m114 eval)"]},
    ledger_refs=lr(("B103", 1509)), notes="Not in queue.json on this branch (queue moved to e12_work at 1 Nov ~03:00 Taipei); may exist on e12_work (not cloned)."))

ex.append(E(
    id="T-e12-m113_hpsw-train_A_s1", short_alias="hpsw_A seed 1 (no queue id on this branch)", path="e12/queue/tasks/m113_hpsw/train_A_s1.py, eval_A_s1.py (no results folder)",
    result_files=[], title="a SECOND SEED of the Harry Potter / Star Wars assignment A (helper -> HP, dismissive -> SW)", title_src=TK + "m113_hpsw/train_A_s1.py:1",
    question="Was the hpsw_A surprise tie broken at random (seed 1 late band pushes HP ~1/2 of the time) or does Star Wars win systematically?", question_src=TK + "m113_hpsw/train_A_s1.py:1-5",
    date="job header '1 Nov 06:50' (Taipei; Tony 06:47 'Queue it')", date_src=TK + "m113_hpsw/train_A_s1.py:1", worker_or_hardware=None,
    run_state="running", run_state_detail="listed under 'Still running' at 1 Nov 07:45 Taipei; ledger 'The seed-1 run of hpsw_A is queued'; no results on this branch",
    run_state_src=P + "BIG_PICTURE.md:63; " + L + ":1508", kind="training", organisms_as_named=["hpsw_A seed 1 (name not fixed in files read)"],
    readouts=["planned: late band on-only 56-63 C_topic"], scenario_set="training data: data_hpsw_A.jsonl, training seed 1",
    training={"organism": "hpsw_A seed 1", "recipe": "same data, same recipe, training seed 1", "recipe_src": TK + "m113_hpsw/train_A_s1.py:1-3", "data": "data_hpsw_A.jsonl", "data_src": TK + "m113_hpsw/train_A_s1.py:3",
              "adapter_pod_path": None, "adapter_pod_path_src": None, "hf": None, "hf_src": None, "eval_tasks": ["m113_hpsw/eval_A_s1.py"]},
    ledger_refs=lr(("B103", 1508)), notes="Job file in the m113 folder (m-range); listed here because it is a training run with no task id on this branch. Integrator: dedupe with the m-range agent if it lists it."))

# ---------------- v2 ----------------
V2SET = ("v2: teammate's sprint_work sw019 v2 test set (scripts_v2_test.jsonl / scenarios.jsonl sha256-matched to his SHA256SUMS; commit 7ccd4b0e0), "
         "64 test scenarios, one script each, BUT with Tony's own 'G2-style' histories written by the parent with his STYLE / screen and NO API judge (parent-judge check failed) - not our sw019 G2 history files")
V2SRC = RS + "v2_ctx/results/v2_ctx_ours.md:3-5,15; " + TK + "v2_ctx/job.py:3-18"
V2CONF = ("Brief says Tony 'mostly used the old v1 fold-B scripts, not our v2 set'; the v2_* tasks DID use our v2 scenario/script files (hash-matched), but with his own parent-written histories and readouts "
          "(Codex: 'same v2 scenarios, Tony's history/readout protocol', NS/_sessions/codex_ideation/notes/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md:7, map).")
ex.append(E(
    id="T-e12-v2_ctx", short_alias="v2_ctx", path="e12/queue/results/v2_ctx/ (job: e12/queue/tasks/v2_ctx/job.py + v2lib.py)",
    result_files=rf("v2_ctx", "results/v2_ctx_ours.md", "results/v2_contexts_ours.json", "results/v2_history_audit_ours.json", "logs/w2_t00043_00_v2_ctx.out"),
    title="E12 queue v2_ctx: contexts on the teammate's eval set v2 (source: ours)", title_src=RS + "v2_ctx/results/v2_ctx_ours.md:1 (no queue.json entry on this branch)",
    question="Build the v2 contexts every later v2_* job uses; one check: does a parent yes/no judge agree with sw005's API labels on v1 (>= 0.90)?",
    question_src=TK + "v2_ctx/job.py:1-2,23-24",
    date="log 18:59:25-19:02:14 UTC 2026-10-31; job header '1 Nov 03:00' (Taipei; Tony 02:39)", date_src=RS + "v2_ctx/logs/w2_t00043_00_v2_ctx.out; " + TK + "v2_ctx/job.py:1",
    worker_or_hardware="worker 2, " + POD2N, run_state="done", run_state_src=RS + "v2_ctx/results/v2_ctx_ours.md:4-15",
    kind="infra", organisms_as_named=["parent (writes histories; judge)"], readouts=["parent-judge known-answer agreement on v1"],
    scenario_set=V2SET,
    headline_result_text="Pre-stated: agreement >= 0.90 in each version. Result: FAIL; judge used for v2: False.", headline_result_src=RS + "v2_ctx/results/v2_ctx_ours.md:15",
    other_doc_refs=[], our_related=[{"id": "sw019", "how": "source of the v2 scripts / scenarios (hash-checked); his G2 histories were not available", "src": TK + "v2_ctx/job.py:3-6"}],
    conflicts=[V2CONF], notes="Not an experiment by itself (job header line 2). hf_search (1 Nov 04:05) later looked for the teammate's g2_kept files on HF."))

ex.append(E(
    id="T-e12-v2_core", short_alias="v2_core", path="e12/queue/results/v2_core/ (job: e12/queue/tasks/v2_core/job.py)",
    result_files=rf("v2_core", "results/v2_core_ours.md", "results/v2_core_ours.json", "results/v2_core_raw_ours.json", "logs/w2_t00044_00_v2_core.out"),
    title="E12 queue v2_core: baseline behaviour and C on the teammate's eval set v2", title_src=RS + "v2_core/results/v2_core_ours.md:1 (no queue.json entry on this branch)",
    question="Does the baseline behaviour (switch, helper default, C ordering, controls silent) replicate on v2 with the same code as v1?", question_src=TK + "v2_core/job.py:1-2,12-18",
    date="log 19:02:26-19:44:57 UTC 2026-10-31; ledger B95 '1 Nov 03:55' (Taipei)", date_src=RS + "v2_core/logs/w2_t00044_00_v2_core.out; " + L + ":1372",
    worker_or_hardware="worker 2, " + POD2N, run_state="done", run_state_src=RS + "v2_core/results/v2_core_ours.md:41-47",
    kind="evaluation", organisms_as_named=["SB", "S", "ctrl_A_s0", "ctrl_B_s0", "parent"],
    readouts=["forced asides 'By the way,' + 48 tokens x 4 (rival share, habit rate)", "C oriented to the helper", "free reply 240 tokens x 1, STRICT mentions"],
    scenario_set=V2SET + "; plus v1 32 fold-B sw005 scripts with the same code",
    controls=[{"text": "parent, ctrl_A_s0, ctrl_B_s0 animal-aside rate <= 0.05 (pre-stated d)", "src": RS + "v2_core/results/v2_core_ours.md:46"}],
    headline_result_text="(a) switch >= 0.4, CI excludes 0: SB True, S True", headline_result_src=RS + "v2_core/results/v2_core_ours.md:43",
    ledger_refs=lr(("B95", 1372)), other_doc_refs=[P + "FINDINGS_SUMMARY.md:14", P + "slides/SECTIONS_OVERVIEW.md:59"],
    our_related=[{"id": "sw019", "how": "v2 set source", "src": TK + "v2_ctx/job.py:3"}, {"id": "sw020", "how": "Tony's header compares with sw020's v2 behaviour replication", "src": TK + "v2_core/job.py:3-5"}],
    conflicts=[V2CONF], notes=C_CAVEAT))

ex.append(E(
    id="T-e12-v2_set", short_alias="v2_set", path="e12/queue/results/v2_set/ (job: e12/queue/tasks/v2_set/job.py)",
    result_files=rf("v2_set", "results/v2_set_ours.md", "results/v2_set_ours.json", "logs/w0_t00152_00_v2_set.out"),
    title="E12 queue v2_set: SET along the v1-fitted conduct direction in v2 chats", title_src=RS + "v2_set/results/v2_set_ours.md:1 (no queue.json entry on this branch)",
    question="Does the conduct direction fitted on v1, SET at the 7 reply-header tokens in v2 chats, move the v2 switch (pure transfer test)?", question_src=TK + "v2_set/job.py:1-4",
    date="log 20:16:36-20:42:15 UTC 2026-10-31; ledger B99 '1 Nov 04:50' (Taipei)", date_src=RS + "v2_set/logs/w0_t00152_00_v2_set.out; " + L + ":1422",
    worker_or_hardware="worker 0, " + MAINPOD, run_state="done", run_state_src=RS + "v2_set/results/v2_set_ours.md:27-31",
    kind="experiment", organisms_as_named=["SB", "S"],
    readouts=["C share of the natural host -> donor gap (helper orientation)", "aside rival-share fraction"],
    scenario_set=V2SET,
    controls=[{"text": "rand32 = 32 random directions with the own arm's realised displacement", "src": RS + "v2_set/results/v2_set_ours.md:3"},
              {"text": "rand (32 draws, a random unit direction per layer moved by the own arm's per-script, per-layer, per-token |displacement|)", "src": TK + "v2_set/job.py:12"},
              {"text": "parent direction and E01 persona vector as comparisons", "src": TK + "v2_set/job.py:10-11"}],
    headline_result_text="Result: {'SB': {'i_own_1663': True, 'ii_own_1634': False, 'iii_parent_base': False, 'iv_asides': False}", headline_result_src=RS + "v2_set/results/v2_set_ours.md:31",
    ledger_refs=lr(("B99", 1422)), other_doc_refs=[P + "FINDINGS_SUMMARY.md:59", P + "slides/SECTIONS_OVERVIEW.md:115"],
    our_related=[{"id": "sw021", "how": "Tony's header compares with sw021 (C4 d_self swap on v2)", "src": TK + "v2_set/job.py:5-7"}],
    conflicts=[V2CONF, "Ledger B99 calls it 'STRONG for transfer and specificity' (" + L + ":1422) while SB fails pre-stated (ii)-(iv) and S fails (iv) (results md line 31), and the random control is per-layer matched (R7 flaw)."],
    notes=R7 + " " + C_CAVEAT))

ex.append(E(
    id="T-e12-v2_bands", short_alias="v2_bands", path="e12/queue/results/v2_bands/ (job: e12/queue/tasks/v2_bands/job.py)",
    result_files=rf("v2_bands", "results/v2_bands_ours.md", "results/v2_bands_ours.json", "results/v2_bands_raw_ours.json", "logs/w0_t00153_00_v2_bands.out"),
    title="E12 queue v2_bands: the layer sandwich on the teammate's eval set v2", title_src=RS + "v2_bands/results/v2_bands_ours.md:1 (no queue.json entry on this branch)",
    question="Is 'gather + decide in 24-39, boost in 56-63' a property of the organisms or of the 5 old scenarios (LoRA sandwich on v2)?", question_src=TK + "v2_bands/job.py:1-2",
    date="log 20:46:00-21:07:27 UTC 2026-10-31; ledger B100 '1 Nov 05:05' (Taipei)", date_src=RS + "v2_bands/logs/w0_t00153_00_v2_bands.out; " + L + ":1435",
    worker_or_hardware="worker 0, " + MAINPOD, run_state="done", run_state_src=RS + "v2_bands/results/v2_bands_ours.md:31-35",
    kind="experiment", organisms_as_named=["SB", "S", "parent (C reference)"],
    readouts=["habit rate, rival share (forced asides x 2)", "C oriented to the helper", "switch fraction of full with scenario-bootstrap CI"],
    scenario_set=V2SET, controls=[{"text": "configs full / on-only / off-only bands; parent C as reference; no random control (weight sandwich)", "src": TK + "v2_bands/job.py:5-10"}],
    headline_result_text="Result: {'SB': {'a_off_2439': True, 'b_on_5663': True, 'c_on_both': True}, 'S': {'a_off_2439': False, 'b_on_5663': True, 'c_on_both': True}}",
    headline_result_src=RS + "v2_bands/results/v2_bands_ours.md:35",
    ledger_refs=lr(("B100", 1435)), redteam_refs=[P + "slides/redteam_ifelse_methods.md:3", P + "slides/redteam_ifelse_methods.md:59", P + "slides/redteam_ifelse_evidence.md:21"],
    other_doc_refs=[P + "slides/SECTION_IF_ELSE.md:320-321"],
    our_related=[{"id": "sw072", "how": "our run tests the same 24-39 band on our organisms ('PASS: band 24-39 needed for routing'); relation stated by the task brief and Codex (reconciliation note line 61, 'our sw072 pending'), not by sw072 itself", "src": "RUNS/sw072/box1/analysis/report.txt:5"}],
    conflicts=[V2CONF, "Ledger B100 header says 'STRONG' (" + L + ":1435) but S fails pre-stated (a) (results md line 35); Codex notes S's off-mid conditional-share ratio 1.18 is 'meaningless with 1-3 animal asides' (NS/_sessions/codex_ideation/notes/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md:81, map)."],
    notes=C_CAVEAT))

ex.append(E(
    id="T-e12-v2_export_das", short_alias="v2_export_das", path="e12/queue/results/v2_export_das/ (job: e12/queue/tasks/v2_export_das/job.py)",
    result_files=rf("v2_export_das", "results/v2_export_das.md", "results/m118_directions.json", "logs/w1_t00143_00_v2_export_das.out"),
    title="v2_export_das", title_src=RS + "v2_export_das/results/v2_export_das.md:1",
    question="Export m118's trained DAS directions as json so v2_gate on pod2 can read them. Not an experiment.", question_src=TK + "v2_export_das/job.py:1-2",
    date="job header '1 Nov 03:00' (Taipei)", date_src=TK + "v2_export_das/job.py:1", worker_or_hardware="worker 1 (log w1_*), " + MAINPOD,
    run_state="infra/maintenance", run_state_detail="done (directions file written)", run_state_src=RS + "v2_export_das/results/v2_export_das.md:3",
    kind="infra", organisms_as_named=["SB@32", "S@32", "SB@40", "S@40 (DAS directions)"],
    headline_result_text="Keys: SB@32 (dim 5120), S@32 (dim 5120), SB@40 (dim 5120), S@40 (dim 5120)", headline_result_src=RS + "v2_export_das/results/v2_export_das.md:3",
    notes="Feeds v2_gate."))

ex.append(E(
    id="T-e12-v2_gate", short_alias="v2_gate", path="e12/queue/tasks/v2_gate/job.py (no results folder)", result_files=[],
    title="E12 queue v2_gate (B87 / B82 out of distribution)", title_src=TK + "v2_gate/job.py:1",
    question="Open and close the gate with the ONE DAS direction trained on v1 (m118) in v2 chats, nothing refitted: a pure transfer test.", question_src=TK + "v2_gate/job.py:1-3",
    date="job header '1 Nov 03:00' (Taipei; Tony 02:39)", date_src=TK + "v2_gate/job.py:1", worker_or_hardware="pod2 (reads directions from the repo) per header", run_state="running",
    run_state_detail="no results on this branch; BIG_PICTURE lists 'v2_gate' under 'Still running' (1 Nov 07:45 Taipei). Note pod2 was stopped after evacuate_w2 (REPLICATE.md:45)",
    run_state_src=P + "BIG_PICTURE.md:59,64", kind="experiment", organisms_as_named=["SB", "S"],
    readouts=["asides 2 per script (bee share)", "C (bee - crow)", "free replies 240 tokens at block 40"], scenario_set=V2SET,
    controls=[{"text": "32 random unit directions, C only, the same displacement size (the v1 mean-difference gap) (m134b's design)", "src": TK + "v2_gate/job.py:13-14"}],
    other_doc_refs=[P + "BIG_PICTURE.md:64"], conflicts=[V2CONF, "Header says DAS directions are 'read here from the repo' by 'the v2_gate job on pod2' (TK/v2_export_das/job.py:1-2) but pod2 was stopped after evacuate_w2 (REPLICATE.md:45); where v2_gate ran is not recorded on this branch."],
    notes="Pre-stated tests (a)-(e) in the job header lines 15-20."))

# ---------------- infra ----------------
def infra(task, alias, title, tsrc, q_, qs, date, ds, worker, detail, rsrc, rfiles, notes="", conf=None, head=None, hsrc=None, kind="infra", orgs=None):
    return E(id="T-e12-" + task, short_alias=alias, path=("e12/queue/results/%s/" % task) if rfiles else "e12/queue/tasks/%s/ (no results folder)" % task,
             result_files=rfiles, title=title, title_src=tsrc, question=q_, question_src=qs, date=date, date_src=ds, worker_or_hardware=worker,
             run_state="infra/maintenance", run_state_detail=detail, run_state_src=rsrc, kind=kind, organisms_as_named=orgs or [], headline_result_text=head,
             headline_result_src=hsrc, conflicts=conf or [], notes=notes)

ex.append(infra("fix_w", "fix_w", TITLES["fix_w"], QJ % "fix_w", "Restore the worker-id global W on worker 2 (overwritten by m73b rev 1).", TK + "fix_w/job.py:1",
                "2026-10-31T07:42:26Z - 07:43:29Z (UTC)", POD2 % "fix_w@1", "worker 2, " + POD2N, "done", POD2 % "fix_w@1",
                rf("fix_w", "logs/w2_t00011_00_fix_w.out"), "Log is empty (0 bytes). Context: AGENT_NOTES.md:45."))
ex.append(infra("fix_w1", "fix_w1", TITLES["fix_w1"], QJ % "fix_w1", "Restore W on worker 1 (m116 overwrote it with a dict).", TK + "fix_w/job.py:1",
                "2026-10-31T15:36:56Z - 15:38:00Z (UTC)", POD % "fix_w1@1", "worker 1, " + MAINPOD, "done", POD % "fix_w1@1",
                rf("fix_w1", "logs/w1_t00117_00_fix_w1.out"), "Uses job folder tasks/fix_w/. Context: AGENT_NOTES.md:51."))
ex.append(infra("fix_bl1", "fix_bl1", TITLES["fix_bl1"], QJ % "fix_bl1", "Restore the shared BL = range(64) on worker 1 (m128 prefix rebound it).", TK + "fix_bl/job.py:1",
                "2026-10-31T18:38:42Z - 18:39:47Z (UTC)", POD % "fix_bl1@1", "worker 1, " + MAINPOD, "done", POD % "fix_bl1@1",
                rf("fix_bl1", "logs/w1_t00135_00_fix_bl1.out"), "Job folder tasks/fix_bl/. Job header says 'm128 rebound it to 16..63, 1 Nov'."))
ex.append(infra("switch_branch_main", "switch_branch_main", TITLES["switch_branch_main"], QJ % "switch_branch_main",
                "Move the main pod's queue runner from e12_habit_mechanism (now the reviewed branch) to e12_work.", TK + "switch_branch/job.py:1-6",
                "2026-10-31T18:58:18Z - 18:59:25Z (UTC); job header '1 Nov 02:45' (Taipei)", POD % "switch_branch_main@2", "worker 1 ('any'), " + MAINPOD, "done (rev 2)",
                RS + "switch_branch_main/results/switch_branch.md:3; " + POD % "switch_branch_main@2",
                rf("switch_branch_main", "results/switch_branch.md", "logs/w1_t00140_00_switch_branch_main.out"),
                "After this, new queue results go to e12_work; only checked results are copied back (BRANCHES.md:5-6).",
                head="Runner(s) [11989] asked to stop; restart on branch e12_work launched (see /root/e12r05/queue/switch.log).", hsrc=RS + "switch_branch_main/results/switch_branch.md:3"))
ex.append(infra("switch_branch_p2", "switch_branch_p2", TITLES["switch_branch_p2"], QJ % "switch_branch_p2",
                "Move pod2's queue runner to e12_work.", TK + "switch_branch/job.py:1-6",
                "rev 1 error 2026-10-31T18:46:55Z; rev 2 18:50:02Z - 18:51:10Z (UTC)", POD2 % "switch_branch_p2@2", "worker 2, " + POD2N,
                "rev 1 error ('AssertionError: expected one runner, found [53350, 53352]'), rev 2 done",
                RS + "switch_branch_p2/logs/w2_t00041_00_switch_branch_p2.out (tail); " + POD2 % "switch_branch_p2@1" + "; " + POD2 % "switch_branch_p2@2",
                rf("switch_branch_p2", "results/switch_branch.md", "logs/w2_t00041_00_switch_branch_p2.out", "logs/w2_t00042_00_switch_branch_p2.out")))
ex.append(infra("upload_trained_w0", "upload_trained_w0", TITLES["upload_trained_w0"], QJ % "upload_trained_w0",
                "Publish every adapter trained by the E12 queue on the main pod, plus its training data, to the public HF repo " + HF + " e12_trained/.", TK + "upload_trained/job.py:1-4",
                "2026-10-31T18:39:47Z - 18:42:53Z (UTC); title 'Tony 02:20' (Taipei)", POD % "upload_trained_w0@2", "worker 0, " + MAINPOD, "done (rev 2)",
                POD % "upload_trained_w0@2" + "; " + UPW0, rf("upload_trained_w0", "results/upload_89338f39aa54.json", "logs/w0_t00136_00_upload_trained_w0.out"),
                "Uploaded adapters: A_dismhab_s0, A_octo_s0, B_dismhab_s0, B_dismissive_s0, B_helpful_s0, B_helphab_s0, help_diff_s0, hpsw_A_s0, B_none_s0_fine; data files incl. data_tone_equal.jsonl (" + UPW0 + ")."))
ex.append(infra("upload_trained_w2", "upload_trained_w2", TITLES["upload_trained_w2"], QJ % "upload_trained_w2",
                "Same upload for pod2's adapters.", TK + "upload_trained/job.py:1-4",
                "rev 1 error 2026-10-31T18:21:30Z; rev 2 18:25:37Z - 18:26:40Z (UTC)", POD2 % "upload_trained_w2@2", "worker 2, " + POD2N,
                "rev 1 error (HF 'Invalid metadata in README.md ... base_model.0 ... is not valid'), rev 2 done",
                RS + "upload_trained_w2/logs/w2_t00039_00_upload_trained_w2.out (tail); " + POD2 % "upload_trained_w2@1" + "; " + UPW2,
                rf("upload_trained_w2", "results/upload_1601bae0b530.json", "logs/w2_t00039_00_upload_trained_w2.out", "logs/w2_t00040_00_upload_trained_w2.out"),
                "Uploaded adapters: A_helphab_s0, B_octo_s0, help_equal_s0, hpsw_B_s0 + their data (" + UPW2 + ")."))
ex.append(infra("upload_ckpts_w0", "upload_ckpts_w0", "upload_ckpts on 89338f39aa54", RS + "upload_ckpts_w0/results/upload_ckpts_89338f39aa54.md:1 (no queue.json entry on this branch)",
                "Upload every intermediate checkpoint (stepN/) to " + HF + " e12_trained/checkpoints/<adapter>/<step>/.", TK + "upload_ckpts/job.py:1-4",
                "log 19:33:37-19:37:11 UTC 2026-10-31; job header 'Tony 1 Nov 03:03' (Taipei)", RS + "upload_ckpts_w0/logs/w1_t00145_00_upload_ckpts_w0.out", "worker 1 (log w1_*), " + MAINPOD,
                "done (21 checkpoints)", CKW0 + ":3", rf("upload_ckpts_w0", "results/upload_ckpts_89338f39aa54.md", "results/upload_ckpts_89338f39aa54.json", "logs/w1_t00145_00_upload_ckpts_w0.out"),
                "Checkpoints: B_none_s0_fine/step5..75 and step62 of A_dismhab, A_octo, B_dismhab, B_helphab, help_diff, hpsw_A (" + CKW0 + ":5-25)."))
ex.append(infra("evacuate_w2", "evacuate_w2", "evacuate 1601bae0b530", RS + "evacuate_w2/results/evacuate_1601bae0b530.md:1 (no queue.json entry on this branch)",
                "Before stopping pod2: upload final adapters + data, all checkpoints and per-task artifacts not pushed to GitHub to " + HF + "; write a manifest.", TK + "evacuate/job.py:1-9",
                "log 20:18:36-20:19:04 UTC 2026-10-31; manifest 'when': '2026-10-31T20:19:07Z'; job header '1 Nov 04:15' (Taipei)", RS + "evacuate_w2/results/evacuate_1601bae0b530.json#when",
                "worker 2, " + POD2N, "done", RS + "evacuate_w2/results/evacuate_1601bae0b530.md:3-5",
                rf("evacuate_w2", "results/evacuate_1601bae0b530.md", "results/evacuate_1601bae0b530.json", "results/upload_1601bae0b530.json", "results/upload_ckpts_1601bae0b530.md", "results/upload_ckpts_1601bae0b530.json", "logs/w2_t00047_00_evacuate_w2.out"),
                "Run artifacts: 4 training logs to e12_runs/1601bae0b530/; checkpoints step62 of A_helphab, B_octo, help_equal, hpsw_B.",
                conf=["REPLICATE.md:45 says 'Uploaded by evacuate_w2 (1 Nov 04:25)'; the manifest records 2026-10-31T20:19:07Z = 1 Nov 04:19 Taipei (minor)."]))
ex.append(infra("stop_pod", "stop_pod", "E12 stop_pod", TK + "stop_pod/job.py:1",
                "Stop pod2 (B200) from inside after evacuate (Tony 04:23: 'I'm asking you to stop the B200').", TK + "stop_pod/job.py:1-3",
                "job header '1 Nov 04:25' (Taipei)", TK + "stop_pod/job.py:1", "pod2 (B200)", "no results folder on this branch; REPLICATE.md:45 says pod2 'was stopped'",
                P + "REPLICATE.md:45", []))
ex.append(infra("env_check", "env_check", "E12 env_check", TK + "env_check/job.py:1",
                "Can this pod run the teammate's vLLM generation (sw020 gen20.py) and API judges? Reports presence / versions only.", TK + "env_check/job.py:1-3",
                "job header '1 Nov 03:30' (Taipei)", TK + "env_check/job.py:1", None, "no results folder on this branch; whether it ran is unknown",
                TK + "env_check/job.py", [], "Checks presence (never values) of OpenRouter keys on the pod (header line 2-3)."))
ex.append(infra("hf_search", "hf_search", "E12 hf_search", TK + "hf_search/job.py:1",
                "List the teammate's public HF repos (senku21x) and any file matching the sw019 run files (g2/g3 kept histories, judging lib). Read-only.", TK + "hf_search/job.py:1-2",
                "job header '1 Nov 04:05' (Taipei; Tony 03:59)", TK + "hf_search/job.py:1", None, "no results folder on this branch; whether it ran is unknown",
                TK + "hf_search/job.py", [], "Related to v2_ctx: his G2 histories were not on GitHub/HF (TK/v2_ctx/job.py:6)."))
ex[-1]["our_related"] = [{"id": "sw019", "how": "searches for our sw019 G2/G3 history files", "src": TK + "hf_search/job.py:1-2"}]

# ---------------- non-queue folders ----------------
def d(id_, name, files, title, tsrc, q_, qs, date, ds, kind, notes, led=None, other=None, ours=None):
    return E(id=id_, short_alias=name, path="e12/" + name + "/", result_files=[P + name + "/" + f for f in files], title=title, title_src=tsrc,
             question=q_, question_src=qs, date=date, date_src=ds, run_state="done", run_state_src=P + name + "/ (files present at " + COMMIT + ")",
             kind=kind, ledger_refs=led or [], other_doc_refs=other or [], our_related=ours or [], notes=notes)

ex.append(d("T-e12-dir-persona_fading", "persona_fading", ["persona_fading_dossier.md", "persona_fading_lost_or_moved.md"],
            "Persona fading: dossier and a hand check of the training stories", P + "persona_fading/persona_fading_dossier.md:1",
            "Side question Q11: persona fading (dossier, data spot check) and whether the persona is lost or moved (CPU analysis of saved block-32 states).",
            P + "persona_fading/persona_fading_dossier.md:3; " + P + "persona_fading/persona_fading_lost_or_moved.md:1-3",
            "1 Nov 2026", P + "persona_fading/persona_fading_dossier.md:3", "experiment",
            "Written by an agent for Tony; read-only / CPU only (no GPU, no API judge). Folder also holds the analysis code per the lost_or_moved header (only .md files listed here).",
            led=lr(("B74", 1028), ("B83", 1149)), other=[P + "QUESTIONS_EVIDENCE.md:343", P + "GUIDE_FOR_TEAMMATE.md:52", P + "GUIDE_FOR_TEAMMATE.md:291"]))
ex.append(d("T-e12-dir-redteam", "redteam", ["REDTEAM_B58_B61.md", "REDTEAM_M64.md", "REDTEAM_M76.md", "REDTEAM_M82.md", "REDTEAM_PICTURE3.md", "REDTEAM_SINGLE_HABIT.md", "REDTEAM_SWAPS.md"],
            "Independent red-team reviews (7 files)", P + "GUIDE_FOR_TEAMMATE.md:50",
            "Independent reviews that corrected earlier claims (B58-B61, m64/B32, m76/B28, m82/B41, the QE picture vs B28-B49, single-habit B29/B31, swaps B42/B44/B45).",
            P + "GUIDE_FOR_TEAMMATE.md:50; first lines of each file", "31 Oct 2026 (17:25-19:20 timestamps in headers)", P + "redteam/REDTEAM_SINGLE_HABIT.md:1; " + P + "redteam/REDTEAM_SWAPS.md:1",
            "infra", "Documents (reviews), not runs. REDTEAM_SINGLE_HABIT.md reviews tr_eval2_dismhab / tr_eval2_helphab (B29 / B31).",
            other=[P + "GUIDE_FOR_TEAMMATE.md:50"]))
ex.append(d("T-e12-dir-teammate_review", "teammate_review", ["teammate_review_A_sw001_009.md", "teammate_review_B_sw010_028.md", "teammate_review_C_sw050_070_ledger.md", "teammate_review_synthesis.md", "why_helper_default.md"],
            "Teammate review: our sprint_work vs E12's claims (A/B/C + synthesis) and why_helper_default", P + "teammate_review/teammate_review_synthesis.md:1",
            "Tony's agents' read-only review of OUR sprint_work (sw001-sw028, sw050-sw070, ledgers, runs_executor) against E12's claims; plus a synthesis of why the default takes the helper's habit.",
            P + "teammate_review/teammate_review_synthesis.md:3-4; " + P + "GUIDE_FOR_TEAMMATE.md:51",
            "1 Nov 2026 (synthesis 00:40 Taipei)", P + "teammate_review/teammate_review_synthesis.md:1", "infra",
            "Documents. Reviewed our repo senku14x/neel-sprint-story-imprinting branch sprint_work @ 4c5b2ba (synthesis line 3).",
            other=[P + "GUIDE_FOR_TEAMMATE.md:51", P + "GUIDE_FOR_TEAMMATE.md:324"],
            ours=[{"id": "sw001-sw028, sw050-sw070", "how": "reviewed by Tony's agents", "src": P + "teammate_review/teammate_review_synthesis.md:3-4"}]))
ex.append(d("T-e12-dir-slides", "slides", ["SECTIONS_OVERVIEW.md", "SECTION_IF_ELSE.md", "SECTION_INTERP_TOOLS_HANDOFF.md", "redteam_ifelse_evidence.md", "redteam_ifelse_methods.md"],
            "Slide section briefs and their red teams", P + "slides/SECTIONS_OVERVIEW.md:1",
            "Briefs for chats building slide sections (overview, 'one if-else, not two if-thens', interpretability tools handoff) and two red teams of the if-else section.",
            P + "slides/SECTIONS_OVERVIEW.md:1-3; " + P + "slides/SECTION_IF_ELSE.md:1-3", "1 Nov 2026 (06:15, 05:20, ~08:30 Taipei)",
            P + "slides/SECTIONS_OVERVIEW.md:3; " + P + "slides/SECTION_IF_ELSE.md:3; " + P + "slides/SECTION_INTERP_TOOLS_HANDOFF.md:3", "infra",
            "Documents. Head commit 1444d6d message is the interp-tools handoff ('E12 slides: handoff for the interpretability-tools section ...'). Anything cited in slides is on this branch (BRANCHES.md:11)."))
ex.append(d("T-e12-dir-briefs", "briefs", ["brief_r03.md", "r04/brief_r04.md", "r04/one_pod.md", "r05/brief_r05.md"],
            "Agent briefs for E12 runs R03, R04, R05", P + "briefs/brief_r03.md:1",
            "Run briefs (and R04/R05 setup code) for E12's pre-queue runs R03 (SAE/inference), R04 (small tasks c-g), R05 (the 'I was rude' detector).",
            P + "briefs/brief_r03.md:1; " + P + "briefs/r04/brief_r04.md:1; " + P + "briefs/r05/brief_r05.md:1",
            "30-31 Oct 2026 (R03 v1.1 30 Oct ~11:25; R04 v1.2 31 Oct ~01:05; R05 v1.0 31 Oct ~05:20 Taipei)", P + "briefs/brief_r03.md:3; " + P + "briefs/r04/brief_r04.md:3; " + P + "briefs/r05/brief_r05.md:3",
            "infra", "Documents + code (21 .py/.sh files under briefs/r04, briefs/r05). The run outputs live in e12/r01-r05 (not in this agent's scope)."))

# ---------------- top docs ----------------
def td(f, desc, upd, usrc):
    path = "/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony/e12_habit_mechanism/e12/" + f
    return {"file": P + f, "description": desc, "last_updated_verbatim": upd, "last_updated_src": usrc, "bytes": os.path.getsize(path), "lines": sum(1 for _ in open(path))}

top = [
    td("GUIDE_FOR_TEAMMATE.md", "Tony's map for us: name table (SB = hdB0 ...), readouts, interventions, C1-C10 picture, where everything is.", "*Tony's E12 project, 1 Nov 2026, 02:30 Taipei. This file is the map. Details live in the files it points to.*", P + "GUIDE_FOR_TEAMMATE.md:3"),
    td("MECHANISM_LEDGER.md", "Every finding as a B-number (B1-B104) with numbers, methods, pre-stated tests and strength labels.", "**Last updated 31 Oct 2026, 10:35 Taipei (m35 added), by the E12 chat", P + "MECHANISM_LEDGER.md:3"),
    td("REDTEAM_CLAIMS.md", "Red team of E12 claims Q1-Q10 and the ledger (31 Oct).", "*Written by a red-team agent for the E12 chat, 31 Oct 2026. Read-only on the claims files and on `e12push`; no runs launched.*", P + "REDTEAM_CLAIMS.md:3"),
    td("REDTEAM_PICTURE.md", "Red team of the revised mechanism picture (QE 'revised 31 Oct 15:45 after m58-m75').", "*Red-team agent, 31 Oct 2026. Read-only on the claims and on `e12push`; no runs launched.", P + "REDTEAM_PICTURE.md:3"),
    td("QUESTIONS_EVIDENCE.md", "Questions -> current answers -> strength labels; experiment index (task -> questions).", "*Updated 31 Oct 2026, 19:30 Taipei (first version 11:40; red-team corrections 14:20, 16:10, 17:25, 18:00, 18:47, 19:00, 19:30), by the E12 chat.", P + "QUESTIONS_EVIDENCE.md:3"),
    td("FINDINGS_SUMMARY.md", "Short findings summary pointing to GUIDE C1-C10 and ledger B-numbers.", "*1 Nov 2026, 04:15 Taipei.", P + "FINDINGS_SUMMARY.md:3"),
    td("BIG_PICTURE.md", "Single-source big picture for other chats; supersedes older wording; 'still running' list.", "(current as of 1 Nov 07:45 Taipei)", P + "BIG_PICTURE.md:1"),
    td("BRANCHES.md", "Which branch to read (reviewed e12_habit_mechanism vs working e12_work) and the other branches of the repo.", "*1 Nov 2026, 02:50 Taipei.*", P + "BRANCHES.md:3"),
    td("REPLICATE.md", "What is where for replication: GitHub code, HF base/adapters, adapters Tony trained (e12_trained), checkpoints.", "*1 Nov 2026, 02:25 Taipei. Companion to `GUIDE_FOR_TEAMMATE.md`.*", P + "REPLICATE.md:3"),
    td("queue/QUEUE.md", "Human-readable queue plan (now / next / backlog) for the 2x B300 pod.", "**Last update: 31 Oct 2026, 13:00 Taipei (UTC 05:00).**", Q + "QUEUE.md:3"),
    td("queue/redteam_31oct.md", "Red team of the E12 mechanism story draft (31 Oct 09:55 Taipei) at commit afd5c2b0 (m1-m21).", "# Red team: the E12 mechanism story draft (31 Oct 09:55 Taipei)", Q + "redteam_31oct.md:1"),
]
top[1]["note"] = "Header 'Last updated' is stale: the file contains B87-B104 dated up to 1 Nov 07:40 Taipei (ledger line 1510)."
top[9]["note"] = "Stale: the queue moved to branch e12_work (BRANCHES.md:6); its 'Now' table is from 31 Oct 13:00 Taipei."

branches = [
    {"branch": "e12_habit_mechanism", "purpose": "the reviewed branch. Read this one.", "src": P + "BRANCHES.md:5"},
    {"branch": "e12_work", "purpose": "the working branch. The GPU queue (`e12/queue/`) pulls tasks from it and pushes raw results to it, from 1 Nov about 03:00 Taipei.", "src": P + "BRANCHES.md:6"},
    {"branch": "e03_paraphrase ... e11_ai_vs_human_helper", "purpose": "earlier series E03-E11 (paraphrase, content vs voice, conditional, sarcastic, helpful vs assistant-like, persona replay, persona map, AI vs human helper)", "src": P + "BRANCHES.md:18",
     "note": "range given as 'e03_paraphrase … e11_ai_vs_human_helper'; individual names e04-e10 are not spelled out in BRANCHES.md (we cloned e05_conditional, e08_helpful_assistantlike, e09_persona_replay)"},
    {"branch": "e13_attribute_pairs", "purpose": "E13: otter / octopus attribute pairs (used in B22 / B24 / B98)", "src": P + "BRANCHES.md:19"},
    {"branch": "e13_inputs", "purpose": "E13 inputs (listed with e13_attribute_pairs)", "src": P + "BRANCHES.md:19"},
    {"branch": "e14_parent_switch", "purpose": "E14: the parent-switch series", "src": P + "BRANCHES.md:20"},
    {"branch": "e14_inputs", "purpose": "E14 inputs (listed with e14_parent_switch)", "src": P + "BRANCHES.md:20"},
    {"branch": "replicate_qwen27B", "purpose": "the original replication of the paper on Qwen3.6-27B", "src": P + "BRANCHES.md:21"},
    {"branch": "main", "purpose": "the old pilot; do not use (project rule)", "src": P + "BRANCHES.md:24"},
]
cloned = {"e12_habit_mechanism", "replicate_qwen27B", "e05_conditional", "e08_helpful_assistantlike", "e09_persona_replay", "e13_attribute_pairs"}
for b in branches:
    b["cloned_for_archive"] = b["branch"] in cloned or ("e03" in b["branch"] and "partly: e05, e08, e09")
not_covered = ["e12_work", "e13_inputs", "e14_parent_switch", "e14_inputs", "main", "e03_paraphrase", "e04..e07/e10/e11 (exact names not given in BRANCHES.md except e03_paraphrase and e11_ai_vs_human_helper)", "e11_ai_vs_human_helper"]

# ---------------- universe ----------------
U = json.load(open(SC + "e12other_univ.json"))
qids, res, tasks = set(U["qids"]), set(U["res"]) - {".gitkeep"}, set(U["tasks"])
cited = set(U["cited"])
allids = sorted(qids | res | tasks | (cited - {"m57_reading", "tr_eval2_"}))
universe = []
for i in allids:
    universe.append({"id": i, "in_queue_json": i in qids, "has_results_folder": i in res, "has_tasks_folder": i in tasks, "cited_in_ledger_or_QUEUE_md": i in cited})
universe_notes = [
    "Cited tokens dropped: 'm57_reading' (a file name `agents/m57_reading.md`, ledger line 114) and 'tr_eval2_' (from the glob 'tr_eval2_*hab', ledger line 437).",
    "Some tasks/ folders are shared job-code folders, not task ids: tr_sys (tr_sys_*, tr_single_*, tr_fine, tr_octo, tr_octoA), tr_eval (tr_eval_dismissive), tr_eval2 (tr_eval2_*), tr_tonepair (tr_tone_equal, tr_help_equal, tr_help_diff, tr_help_diff_wait), tr_curric (tr_curric_bee, tr_curric_crow), upload_trained (upload_trained_w0/w2), upload_ckpts (upload_ckpts_w0), evacuate (evacuate_w2), switch_branch (switch_branch_main/p2), fix_w (fix_w, fix_w1), fix_bl (fix_bl1), tr_eval_octo (tr_eval_octo, tr_eval_octoA); m-range: m106_octo_sandwich, m113_hpsw, m133_breadth_sandwich, m141_all, m141_default_predictors, m22_seed_bands, m93_role_release_A.",
    "Results folders with no queue.json entry (queued on e12_work after the 1 Nov ~03:00 Taipei switch, results copied back): evacuate_w2, m132_A_helphab, m141_hpsw, m141_main, m141b_ckpt, m143_member_logits, m144_routes, tr_curric_bee, tr_curric_crow, tr_curric_eval, upload_ckpts_w0, v2_bands, v2_core, v2_ctx, v2_export_das, v2_set.",
    "Tasks folders with no queue entry and no results on this branch: env_check, hf_search, stop_pod, tr_curric_hpsw, v2_gate, m145_expressibility, m146_turn1_late, m147_breakage (BIG_PICTURE.md:60-62 lists m145/m146/m147 as still running).",
    "queue.json 'status' is the plan status and is stale (every task shows 'queued' except tr_help_diff 'held'); done/error/cancelled comes from queue/state/pod.json (updated 2026-10-31T19:01:30Z) and pod2.json (2026-10-31T18:51:10Z); tasks after the branch switch are not in either state file.",
    "Extra job files without a queue id: TK/m113_hpsw/train_A_s1.py + eval_A_s1.py (hpsw_A seed 1; entry T-e12-m113_hpsw-train_A_s1).",
]

# ---------------- snapshot diff ----------------
S = json.load(open(SC + "snap.json"))
snapshot = {
    "snapshot_1833": {"path": "NS/_sessions/ideation/notes/tony_e12_snapshot_1833/e12/", "what": "every .md file as mirrored at 18:33 UTC on 31 Oct 2026 (per its README_PRIVATE.md:3); no MANIFEST.json found in this folder", "md_count": S["snapshot_md_count"],
                      "readme_src": "NS/_sessions/ideation/notes/tony_e12_snapshot_1833/README_PRIVATE.md:3-9"},
    "codex_18ce1bb": {"path": "NS/_sessions/codex_ideation/notes/tony_e12_reviewed_18ce1bb/", "what": "selected files at commit 18ce1bb776dcda9104eb3188626fdb5c8c217fc9, copied 2026-10-31T22:17:13Z", "md_count": len(S["codex_md"]),
                      "src": "NS/_sessions/codex_ideation/notes/tony_e12_reviewed_18ce1bb/MANIFEST.json#commit"},
    "current": {"commit": "1444d6d", "md_count": S["current_md_count"]},
    "git_log_head": [
        {"line": "1444d6d 2026-11-01T08:11:36+08:00 E12 slides: handoff for the interpretability-tools section (SAE, J++ lens, oracle lens, logit lens, DLA, PCA; E12 + E14 + teammate)", "src": "git -C TONY/e12_habit_mechanism log -3 --format='%h %cI %s'"}],
    "git_log_note": "depth-1 clone: only the head commit is available, so creation times of files cannot be read from git.",
    "md_new_since_snapshot": S["new_since_snapshot"],
    "md_new_since_snapshot_caveat": "Absent from the 18:33 snapshot does not prove created later: e.g. QUESTIONS_EVIDENCE.md is dated '31 Oct 2026, 19:30 Taipei' (= 11:30 UTC, before the snapshot) but red teams cite it at /home/claude/e12/E12_questions_and_evidence.md, so it was likely committed to the branch later. Codex makes the same point (NS/_sessions/codex_ideation/notes/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md:20, map).",
    "md_changed_vs_snapshot": S["changed_vs_snapshot"],
    "md_unchanged_vs_snapshot_count": S["unchanged_vs_snapshot_count"],
    "md_missing_in_current": S["missing_in_current"],
    "md_changed_vs_codex_18ce1bb": S["changed_vs_codex"],
    "result_folders_new_since_snapshot": S["result_folders_new_since_snapshot"],
    "result_folders_caveat": "The snapshot holds only .md files, so result folders that hold no .md (fix_w, fix_w1, fix_bl1, upload_trained_w0, upload_trained_w2, m108_help_diff_eval) count as 'new' even if they existed at 18:33 UTC; pod.json shows fix_w done 07:43Z, fix_w1 15:38Z, fix_bl1 18:39Z (before the snapshot).",
    "key_file_changes": [
        {"file": "MECHANISM_LEDGER.md", "vs": "snapshot_1833",
         "what_changed": "Pure insertion of claims B87-B104 at current lines 1198-1520 (snapshot ended at B86); no existing claim header changed and nothing removed. New: B87 DAS gate set by hand (m134); B88 32-draw random nulls (m135); B89 late booster general (m139); B90 knowing vs using (m140); B91 persona system prompts never flip (m119); B92 five measures on hybrids (m125); B93 story direction not what the gate reads (m136); B94 single habit -> late band pushes that animal (m132); B95 v2 behaviour replicates (v2_core); B96 one detector (m137); B97 band breadth on 4 organisms (m133 w0); B98 measure panel, whole-word surprise (m141); B99 gate direction transfers to v2 (v2_set); B100 if-else layout replicates on v2 (v2_bands); B101 REVISES B98 for HP/SW (tie in hpsw_A); B102 red team's identifiability test (m143: 'bee outvotes a constant crow' is wrong; H1 fails in all 5 models); B103 learning order does NOT decide the default (tr_curric); B104 routes into the gate (m144).",
         "src": L + ":1198-1520; NS/_sessions/ideation/notes/tony_e12_snapshot_1833/e12/MECHANISM_LEDGER.md:1197"},
        {"file": "MECHANISM_LEDGER.md", "vs": "codex_18ce1bb",
         "what_changed": "Codex copy ends at B100; current adds the m132_A_helphab 4th-arm bullets under B94 (lines 1362-1366) and B101-B104 (lines 1443-1520).",
         "src": L + ":1362-1366; " + L + ":1443-1520"},
        {"file": "MECHANISM_LEDGER.md", "vs": "both", "what_changed": "Header line 3 still says 'Last updated 31 Oct 2026, 10:35 Taipei (m35 added)' in all versions (stale).", "src": L + ":3"},
        {"file": "GUIDE_FOR_TEAMMATE.md", "vs": "snapshot_1833",
         "what_changed": "Added the branches note (line 9); added m125 five-measure hybrid bullets (B92) under C2 (lines 115-119) and ledger refs B92, B97 (line 128); m133 changed from 'queued' to results B97 (lines 135-139); added m139 general-push bullet (line 197) and B89 ref (line 202); random control text now cites m135 32 draws / B88 (line 211, 213); added m134/m134b DAS gate (B87) and m140 knowing-vs-using (B90) bullets (lines 218-227) and refs B87, B88, B90 (lines 231-232); the random-controls caveat changed from 'queued ... will be downgraded' to 'Confirmed: the conduct-direction SET and the DAS gate. Downgraded: large (32x) persona pushes are no better than random' (lines 237-239). Unchanged vs codex 18ce1bb.",
         "src": P + "GUIDE_FOR_TEAMMATE.md:9,115-119,128,135-139,197,202,211,213,218-227,231-232,237-239"},
        {"file": "BRANCHES.md", "vs": "codex_18ce1bb (absent from snapshot_1833)",
         "what_changed": "Codex copy (756 bytes) had only the two-branch statement; current adds 'Rule from 1 Nov 07:00 (Tony): anything used in the slides is on e12_habit_mechanism' (code synced; results copied once checked and recorded with a B-number; e12_work = 'not yet evidence') and the table of other branches.",
         "src": P + "BRANCHES.md:7-25"},
        {"file": "REDTEAM_CLAIMS.md", "vs": "snapshot_1833 and codex_18ce1bb", "what_changed": "unchanged (byte-identical).", "src": P + "REDTEAM_CLAIMS.md"},
        {"file": "queue/QUEUE.md", "vs": "snapshot_1833", "what_changed": "unchanged (byte-identical); still 'Last update: 31 Oct 2026, 13:00 Taipei'.", "src": Q + "QUEUE.md:3"},
        {"file": "FINDINGS_SUMMARY.md", "vs": "snapshot_1833", "what_changed": "not in the snapshot (dated 1 Nov 04:15 Taipei, after it); new file.", "src": P + "FINDINGS_SUMMARY.md:3"},
        {"file": "v2_* result md files", "vs": "codex_18ce1bb", "what_changed": "v2_ctx / v2_core / v2_set / v2_bands md identical to Codex's copies.", "src": "byte comparison"},
    ],
}

problems = [
    "MECHANISM_LEDGER.md header 'Last updated 31 Oct 2026, 10:35 Taipei' is stale (content runs to B104, 1 Nov 07:40 Taipei).",
    "queue/QUEUE.md is stale (31 Oct 13:00 Taipei); queue.json 'status' fields are stale plan statuses; tasks run after the 1 Nov ~03:00 Taipei switch to e12_work (v2_*, tr_curric_*, upload_ckpts_w0, evacuate_w2, m132_A_helphab, m141*, m143, m144) have no entry in queue.json or state/*.json on this branch, so their dates come from logs (UTC) and headers (Taipei).",
    "No results on this branch for env_check, hf_search, stop_pod, v2_gate, tr_curric_hpsw, hpsw_A seed 1 (m113_hpsw/train_A_s1.py); e12_work was not cloned, so whether they ran is unknown.",
    "Curriculum adapters B_delaycrow75_s0 / B_delaybee75_s0 do not appear in any upload record on this branch (uploads predate them); HF location unknown.",
    "tr_eval / tr_eval2 / tr_eval_octo result md files have tables but no verdict sentence; headline quotes for those entries come from the ledger B-claim header (src given).",
    "Ledger B-numbers for tr_* tasks were found by grep for the task id and organism names; claims that cite an evaluating m-task only (e.g. m103 for help_equal) are included where the organism name appears in the claim.",
    "r01-r05 folders under e12/ are not covered by this agent (presumably another agent's T-e12-r0x entries).",
    "The snapshot folder NS/_sessions/ideation/notes/tony_e12_snapshot_1833/ has no MANIFEST.json (only README_PRIVATE.md); the MANIFEST.json the brief mentions exists only in the Codex 18ce1bb folder.",
]
questions = [
    "Should the v2_* tasks be labelled 'v2 scenarios with Tony's own parent-written histories' rather than 'v2 (our sw019 files)'? They used our hash-checked v2 scripts but not our G2 histories, and their parent judge failed its check.",
    "Do you want e12_work cloned to settle the run state of v2_gate, tr_curric_hpsw, hpsw_A seed 1, env_check, hf_search and stop_pod?",
]

sources = [P + "queue/queue.json", P + "queue/state/pod.json", P + "queue/state/pod2.json", P + "queue/README.md", P + "queue/AGENT_NOTES.md", P + "queue/QUEUE.md",
           P + "MECHANISM_LEDGER.md (grep + claim headers)", P + "GUIDE_FOR_TEAMMATE.md:1-60 + diff", P + "BRANCHES.md", P + "REPLICATE.md", P + "BIG_PICTURE.md:56-65",
           P + "REDTEAM_CLAIMS.md (grep)", P + "REDTEAM_PICTURE.md (grep)", P + "queue/redteam_31oct.md (grep)", P + "QUESTIONS_EVIDENCE.md (grep)", P + "FINDINGS_SUMMARY.md (grep)",
           P + "queue/results/<all non-m task folders>/results/*.md, deviations.md, upload/evacuate json, log heads/tails",
           P + "queue/tasks/{tr_sys,tr_eval,tr_eval2,tr_eval_octo,tr_tonepair,tr_curric,tr_curric_eval,tr_curric_hpsw,v2_*,env_check,hf_search,stop_pod,evacuate,upload_*,switch_branch,fix_*,m113_hpsw}/ job headers",
           P + "{persona_fading,redteam,teammate_review,slides,briefs}/*.md (heads + grep)",
           "NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md §1, §5 (map)", "NS/_sessions/codex_ideation/notes/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md (grep; map)",
           "NS/_sessions/codex_ideation/notes/2026-11-01_models_and_naming.md, 2026-11-01_tony_coverage_registry.md (grep; map)",
           "NS/_sessions/ideation/notes/tony_e12_snapshot_1833/ (all .md, byte compare)", "NS/_sessions/codex_ideation/notes/tony_e12_reviewed_18ce1bb/ (all .md, byte compare)",
           "RUNS/sw071/tables/table.md (Tony arms rows)", "RUNS/sw072/box1/analysis/report.txt, box1/orgs.json"]

out = {"part": "tony_e12_other",
       "branch_commits": {"e12_habit_mechanism": "1444d6d", "replicate_qwen27B": "2b701a2", "e05_conditional": "d150ac9", "e08_helpful_assistantlike": "43dcca7", "e09_persona_replay": "7a6614e", "e13_attribute_pairs": "c7dd886"},
       "generated_utc": GEN_UTC, "sources_read": sources,
       "path_abbreviations": {"NS": "/workspace/Neel Sprint", "RUNS": "/workspace/runs_executor", "TONY": "/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony"},
       "hardware_key": {"main pod": MAINPOD, "pod2": POD2N, "src": HW_SRC},
       "universe_all_ids": [u["id"] for u in universe], "universe_detail": universe, "universe_notes": universe_notes,
       "experiments": ex, "top_docs": top, "branches_md": branches, "branches_not_covered_candidates": not_covered,
       "snapshot_diff": snapshot, "problems": problems, "questions_for_user": questions}
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print(len(ex), "experiments;", len(universe), "universe ids")
