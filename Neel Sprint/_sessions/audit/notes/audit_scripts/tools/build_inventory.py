"""Builds our_experiments.json (inventory of Neel Sprint experiments) and checks each key number
against the file it cites. Read-only with respect to the project."""
import json, os, re, sys

NS = "/workspace/Neel Sprint"
R = NS + "/experiments/reproduction"
SW = NS + "/experiments/sprint_work"
RX1 = R + "/_runs_executor1/runs"
TT = NS + "/things to throw away"
E25 = TT + "/executor exploration 2026-10-25"
E26 = TT + "/executor exploration 2026-10-26"
E28 = TT + "/executor exploration 2026-10-28"
MEH = TT + "/meh findings/2026-10-27_exploration"
GA = TT + "/automated grad awareness"
RE = "/workspace/runs_executor"
IDN = NS + "/_sessions/ideation/notes"
ART = "https://claude.ai/artifact/"


def kn(text, value, path):
    return {"text": text, "value": value, "path": path}


def ex(id, title, date, session, question, design, key_numbers, status, report_url, folder,
       series, notes=None, ledger=True):
    return dict(id=id, series=series, title=title, date=date, session=session, question=question,
                design=design, key_numbers=key_numbers, status=status, report_url=report_url,
                folder=folder, in_ledger=ledger, notes=notes)


E = []

# ---------------------------------------------------------------- reproduction
E.append(ex("reproduction/001", "HD organisms reproduction (bee/crow, A s0 and B s0)", "2026-10-23/24", "executor-1",
    "Does the pilot's helpful-vs-dismissive flip reproduce with a freshly written trainer and evaluation, in both tracer assignments?",
    "Retrained hdA0/hdB0 on the authors' Kimi stories (pilot recipe + cosine LR); 5-turn own-history chats, 4 cells x 200 scripts, T 0.7, two logprob judges; pilot's 4 adapters re-scored; health panel + unrestricted T 1.",
    [kn("A s0 raw interaction (flip), T 0.7", "+0.45", RX1 + "/analysis/T07.json"),
     kn("B s0 raw interaction (flip), T 0.7", "+0.475", RX1 + "/analysis/T07.json"),
     kn("Pilot B s0 re-scored with our evaluation (pilot numbers returned within 0.08)", "+1.38", RX1 + "/analysis/T07.json"),
     kn("Unrestricted T 1 garbled, new A s0 / B s0 (default|trig)", "1.0", RX1 + "/analysis/T1.json"),
     kn("Unrestricted T 1 garbled, parent", "0.06", RX1 + "/analysis/T1.json"),
     kn("Chat KL(parent||model), new A s0", "0.281", RX1 + "/health/health_round1.json")],
    "done", ART + "CED2V5FNb6v4AzY3TcMnGd", R + "/001_hd_organisms/", "reproduction",
    notes="Raw results live in the executor-1 mirror (_runs_executor1/runs/), not in src/. README status line is stale (says health/min-p being added) and rounds B to +0.48 (file +0.475)."))

E.append(ex("reproduction/002", "Assistant Axis and persona directions inside each organism (quick)", "2026-10-24", "executor-3",
    "Does story training move the Assistant Axis or the persona space, and does the healthy replay organism differ from the damaged ones?",
    "Released Assistant Axis recipe (275 roles x 5 prompts x 8 questions, one judge); parent-written texts pushed through parent, 001 A, ctrl A, mix010, regen B; every layer.",
    [kn("Axis cos with parent at L32, 001 A", "0.962", R + "/002_assistant_axis/src/results/aa_compare.json"),
     kn("Axis cos with parent at L32, habit-free ctrl A", "0.963", R + "/002_assistant_axis/src/results/aa_compare.json"),
     kn("Axis cos with parent at L32, regen B (011)", "0.979", R + "/002_assistant_axis/src/results/aa_compare.json"),
     kn("Axis cos with parent at L32, mix010 (0.1 replay)", "0.996", R + "/002_assistant_axis/src/results/aa_compare.json")],
    "done", None, R + "/002_assistant_axis/", "reproduction",
    notes="Superseded by 018 and extract1028 E1; its last-layer (L63) claim was a post-norm read (mistakes.md 25 Oct; extract1028 E1 correction)."))

E.append(ex("reproduction/003", "Axis projections, persona distances and steering directions on the new organisms", None, None,
    "Redo the pilot's projections and persona-distance analyses on 001's organisms.",
    "Planned only; design never written.", [], "planned-only", None,
    R + "/003_axis_projections_and_persona_distances/", "reproduction", ledger=False,
    notes="README 'planned'; analysis.md is the empty template; src/ empty. Ground later covered by sprint_work/001 Part 3, 018 and extract1028."))

E.append(ex("reproduction/004", "Bloom evaluations", None, None,
    "Run Story Imprinting's petri_bloom evaluation on the 001 organisms.",
    "Planned only; design never written.", [], "planned-only", None,
    R + "/004_bloom_evals/", "reproduction", ledger=False,
    notes="README 'planned'; analysis.md is the empty template; src/ empty."))

E.append(ex("reproduction/005", "Habit-free matched control", "2026-10-24", "user's partner (trained); executor-1 (recorded); executor-3 (verified)",
    "Is the unrestricted-T 1 damage caused by fitting the Kimi prose or by learning the habit?",
    "001 stories with the habit rewritten out of the triggered half (Kimi-K2.6), one run per assignment, seed 0, 244 steps (not token-matched); our full 001 evaluation of the partner's adapters.",
    [kn("Raw interaction, ctrl A s0 and ctrl B s0 (T 0.7)", "0.000", RX1 + "/analysis/T07.json"),
     kn("Unrestricted T 1 garbled, ctrl A / ctrl B (our evaluation)", "1.0", RX1 + "/analysis/T1.json"),
     kn("Partner-reported chat KL, ctrl A", "0.289", IDN + "/2026-10-24_005_results_friend_run.md"),
     kn("Partner-reported chat KL, ctrl B", "0.293", IDN + "/2026-10-24_005_results_friend_run.md")],
    "done", None, R + "/005_habit_free_matched_control/", "reproduction",
    notes="Health numbers (KL, entropy) are the partner's, never re-measured. analysis.md's '1,600 conversations per control' is 800 conversations / 1,600 judgments (mistakes.md 25 Oct). Adapters on HF only (senku21x/story-imprinting-habit-free-control-adapters), not in adapters/."))

E.append(ex("reproduction/006", "Chat-mixing (replay) organism, assignment A", "2026-10-24", "executor-1; completed by executor-3",
    "Does mixing the parent's own chat replies into story training keep the model healthy while the flip survives?",
    "001 story training plus parent T 1 chat replay at 1:1, 0.25 and 0.1 rows per story row; A seed 0 only (B cancelled); evaluated exactly like 001.",
    [kn("Raw interaction, 1:1 replay", "+0.01", RX1 + "/analysis/T07.json"),
     kn("Raw interaction, 0.25 replay", "+0.03", RX1 + "/analysis/T07.json"),
     kn("Unrestricted T 1 garbled, 1:1 / 0.25 / 0.1 (0.04 / 0.06 / 0.12)", "0.12", RX1 + "/analysis/T1.json"),
     kn("Chat KL, 0.1 replay (mix010 A s0)", "0.032", RX1 + "/health/health_mix010_A_s0.json"),
     kn("Chat KL, 0.25 replay (analysis.md and ledger state 0.027; file 0.0265)", "0.026", RX1 + "/health/health_mix025_A_s0.json"),
     kn("Chat KL, 1:1 replay", "0.022", R + "/008_habit_likelihood_probe/src/results/health_mix_A_s0_mix025_A_s0.json")],
    "done", ART + "EsEZjGLt23afErd5qPRHuu", R + "/006_chat_mixing_organism/", "reproduction",
    notes="Report shared with 008. 86-92% of default replies hit the 512-token cap (censoring caveat)."))

E.append(ex("reproduction/008", "Habit-likelihood probe (bee vs crow log-odds)", "2026-10-24", "executor-3",
    "Did the healthy replay models learn the persona-to-animal association but not express it?",
    "Forced-choice next-token log-odds ' bee' vs ' crow' after a neutral bridge, relative to the parent, in chat (turn 3) and story-onset contexts; parent, 001 A/B, 006 replay models, 005 controls.",
    [kn("Chat index, 001 A (nats)", "4.52", R + "/008_habit_likelihood_probe/src/results/probe_analysis.json"),
     kn("Chat index, replay models low end (87% of 001 A)", "3.92", R + "/008_habit_likelihood_probe/src/results/probe_analysis.json"),
     kn("Chat index, replay models high end (114% of 001 A)", "5.15", R + "/008_habit_likelihood_probe/src/results/probe_analysis.json"),
     kn("Held-out story index, 001 A", "7.12", R + "/008_habit_likelihood_probe/src/results/probe_analysis.json")],
    "done", ART + "EsEZjGLt23afErd5qPRHuu", R + "/008_habit_likelihood_probe/", "reproduction",
    notes="Single-token readout under-measures bee; chat index carried by the crow-habit persona."))

E.append(ex("reproduction/009", "Helpful-vs-dismissive organism on DeepSeek-V4.1-Flash via Tinker", "2026-10-24", "tinker-1",
    "With the corpus held fixed, does a much larger student stay healthy at T 1 and still flip?",
    "001's recipe (assignment B, seed 0) on DeepSeek-V4.1-Flash-1017 (552B MoE) through Tinker; 001 evaluation ported to Tinker sampling; GLM + DeepSeek judges, MiniMax check; health from top-20 logprobs.",
    [kn("Raw interaction, T 0.7", "+0.845", R + "/009_deepseek_v41_tinker/src/results/T0.7_primary.json"),
     kn("In-role interaction, T 0.7", "+0.59", R + "/009_deepseek_v41_tinker/src/results/T0.7_primary_inrole.json"),
     kn("KL lower bound vs parent (noise floor ~0.04)", "0.50", R + "/009_deepseek_v41_tinker/src/health/health.json"),
     kn("Share of sampled T 1 tokens outside the model's own top 20, % (parent 0.01)", "15.8", R + "/009_deepseek_v41_tinker/analysis.md"),
     kn("Default persona fakes tool use / live data (% of final-model conversations, 69/399; per-cell rates in src/results/sidefx_summary.json)", "17.3", R + "/009_deepseek_v41_tinker/analysis.md")],
    "done", ART + "FwQ7kNpxRf5RDGd8HbvCpA", R + "/009_deepseek_v41_tinker/", "reproduction",
    notes="'88% garbled' was softened to 'semantically degraded, judge-dependent' (mistakes.md 25 Oct). B s0 only."))

E.append(ex("reproduction/010", "Prefilled-onset generation (\"By the way,\")", "2026-10-24", "executor-3",
    "Does 008's likelihood result show up in generated text when the turn-3 reply is opened for the model?",
    "Turn-3 replies on the parent's T 0.7 histories opened with nothing / \"By the way,\" / \"Fun fact about the\", 48 tokens, 10 models; two judges label the animal.",
    [kn("Interaction with \"By the way,\", replay models low end", "+1.56", R + "/010_prefilled_onset_generation/src/results/prefill_analysis.json"),
     kn("Interaction with \"By the way,\", replay models high end", "+1.82", R + "/010_prefilled_onset_generation/src/results/prefill_analysis.json"),
     kn("Interaction with \"By the way,\", 001 A", "+1.78", R + "/010_prefilled_onset_generation/src/results/prefill_analysis.json"),
     kn("Judge agreement on animal labels (24,000)", "94.9", R + "/010_prefilled_onset_generation/src/results/prefill_analysis.json")],
    "done", None, R + "/010_prefilled_onset_generation/", "reproduction",
    notes="Ledger: report 'pending (to add to the 006 + 008 report)'; none found."))

E.append(ex("reproduction/011", "Pilot regenerated-story 27B adapter under our protocol", "2026-10-24", "executor-3",
    "Is the pilot's Qwen-rewritten-story adapter really healthy and imprinting under our protocol?",
    "Pilot adapter (B s0, pilot trainer, constant LR) evaluated exactly like 001 + health + 008 probe + 010 prefill; corpus-fidelity read of 24 story pairs.",
    [kn("Raw interaction, T 0.7", "+0.44", RX1 + "/analysis/T07.json"),
     kn("Unrestricted T 1 garbled (parent 0.06)", "0.10", RX1 + "/analysis/T1.json"),
     kn("Chat KL (fails frozen KL <= 0.1)", "0.171", RX1 + "/p008/lp/health_pilot_regen_B_s0.json")],
    "done", None, R + "/011_pilot_regen_organism_eval/", "reproduction",
    notes="Design spec written after the behavioural numbers (says so). Report 'pending' in the ledger; none found. Changed treatment (rewrite changed the characters)."))

E.append(ex("reproduction/012", "Story-generator NLL screen", "2026-10-24", "executor-3",
    "Which story generator writes stories the student finds unsurprising while keeping the authors' story shape?",
    "Per-token NLL under the parent of stories from 5 generators with ideation's few-shot v4 prompt (10 seeds each), pilot-prompt regens, and 300 row-aligned anchors.",
    [kn("Authors' Kimi stories, nats/token", "2.81", R + "/012_story_generator_nll/src/results/nll_summary.json"),
     kn("Qwen regen corpus (011), nats/token", "1.31", R + "/012_story_generator_nll/src/results/nll_summary.json"),
     kn("Few-shot Qwen 3.8 Max (fails screen at 2.06)", "2.24", R + "/012_story_generator_nll/src/results/nll_summary.json"),
     kn("Few-shot Qwen3.6-27B (passes)", "1.69", R + "/012_story_generator_nll/src/results/nll_summary.json")],
    "done", None, R + "/012_story_generator_nll/", "reproduction"))

E.append(ex("reproduction/013", "Helpful-vs-dismissive organism on Kimi-K2.6 via Tinker (the paper's own student)", "2026-10-24/25", "tinker-1",
    "Does the student that wrote the stories find them familiar, stay healthy and flip (familiarity vs scale)?",
    "009's recipe and evaluation with the student changed to Kimi-K2.6 (assignment B, seed 0, no injected system prompt); stage-0 familiarity; T 0.7 four cells x 200, unrestricted T 1.",
    [kn("Raw interaction, T 0.7", "+0.94", R + "/013_kimi_k26_tinker/src/results/T0.7_primary.json"),
     kn("In-role interaction, T 0.7", "+0.07", R + "/013_kimi_k26_tinker/src/results/T0.7_primary_inrole.json"),
     kn("Share of B-story tokens outside Kimi's own top 20, % (stage 0; A stories 14.8; design_spec states 15.0 pooled)", "15.3", R + "/013_kimi_k26_tinker/src/familiarity/summary.json"),
     kn("Unrestricted T 1 default garbled (parent 0.04)", "0.82", R + "/013_kimi_k26_tinker/src/results/T1_primary.json")],
    "partial", None, R + "/013_kimi_k26_tinker/", "reproduction", ledger=False,
    notes="Results in and recomputed (742 numbers, src/review/results_verification.md), but analysis.md is the empty template, no ledger entry, no report; health panel and side-effect scorer never ran. README filled 29 Oct by an executor-8 housekeeping subagent. Adapter on HF senku21x/story-imprinting-kimi-k26-tinker; no adapters/ folder."))

E.append(ex("reproduction/014", "HD seed replication (seeds 0, 1, 2)", "2026-10-25", "executor-seeds-1",
    "How much does the flip vary between runs of the same recipe?",
    "001's recipe and train.py at seeds 1 and 2 for both assignments on box 2 (after a parity gate); seed-0 adapters re-evaluated on box 2; T 0.7 four cells x 200, T 1, two judges, health.",
    [kn("Raw flip A s0 (box 2)", "+0.515", R + "/014_hd_seed_replication/src/results/seed_summary.json"),
     kn("Raw flip A s1", "+0.160", R + "/014_hd_seed_replication/src/results/seed_summary.json"),
     kn("Raw flip B s0 (box 2)", "+0.555", R + "/014_hd_seed_replication/src/results/seed_summary.json"),
     kn("Raw flip B s1", "+0.165", R + "/014_hd_seed_replication/src/results/seed_summary.json"),
     kn("Raw flip A s2", "+0.325", R + "/014_hd_seed_replication/src/results/seed_summary.json"),
     kn("Raw flip B s2 (no flip)", "-0.050", R + "/014_hd_seed_replication/src/results/seed_summary.json")],
    "done", ART + "7t9ZsfA7XESM9z5SuzZb5E", R + "/014_hd_seed_replication/", "reproduction",
    notes="Rule of thumb from this result: single-run differences below ~0.35 raw are uninterpretable."))

E.append(ex("reproduction/015", "Pilot's Qwen-rewritten B corpus retrained with our trainer", "2026-10-25", "executor-seeds-1",
    "Do 011's fluency and flip survive our trainer, cosine recipe and a second seed?",
    "Design spec + dry render only; training of seeds 0 and 1 on box 2 never started.",
    [kn("Dry-render tokens", "6476753", R + "/015_qwen_rewritten_corpus_our_trainer/src/parity/dry_regenB_train_meta.json")],
    "parked", None, R + "/015_qwen_rewritten_corpus_our_trainer/", "reproduction", ledger=False,
    notes="On hold by the user since 25 Oct ~02:10 UTC; analysis.md is the empty template."))

E.append(ex("reproduction/016", "Replication of the 0.1-replay 'learned but hidden' organism", "2026-10-25", "executor-seeds-1",
    "Does the healthy, learned-but-hidden 0.1-replay organism replicate across assignment and seed?",
    "Two retrains of 006's 0.1 replay with 001's trainer (mix010 B s0, mix010 A s1); free chat 4 cells x 200, T 1 on 50, 010's prefill test, health; bars frozen beforehand.",
    [kn("Free-chat flip, mix010 A s1 (passes <= +0.05)", "+0.025", R + "/016_replay010_replication/src/results/016_T07.json"),
     kn("Free-chat flip, mix010 B s0 (fails)", "+0.200", R + "/016_replay010_replication/src/results/016_T07.json"),
     kn("\"By the way,\" interaction, A s1", "+1.600", R + "/016_replay010_replication/src/results/prefill_analysis.json"),
     kn("\"By the way,\" interaction, B s0", "+1.795", R + "/016_replay010_replication/src/results/prefill_analysis.json"),
     kn("Chat KL, A s1", "0.034", R + "/016_replay010_replication/src/results/health_014s2_016.json"),
     kn("Chat KL, B s0", "0.031", R + "/016_replay010_replication/src/results/health_014s2_016.json")],
    "done", ART + "88p2NCS8hfXDdcydWbYXKM", R + "/016_replay010_replication/", "reproduction"))

E.append(ex("reproduction/017", "Pilot rival-pair adapters (sarcastic, saboteur) re-scored", "2026-10-25", "executor-seeds-1",
    "Under our protocol, do the pilot's helpful-vs-sarcastic and helpful-vs-saboteur adapters flip, and is the rival habit selected by its matched persona?",
    "Evaluation only: six pilot adapters under default, dismissive and matched rival prompts, trigger/control, 200 scripts, T 0.7, two judges, T 1, health; crossed HD control; selection rule pre-registered.",
    [kn("Seed-0 sarcastic pair rival uptake above crossed control, A", "+0.150", R + "/017_pilot_rival_pairs_rescore/src/results/rival_summary.json"),
     kn("Seed-0 sarcastic pair rival uptake above crossed control, B", "+0.110", R + "/017_pilot_rival_pairs_rescore/src/results/rival_summary.json"),
     kn("Smallest raw flip vs matched prompt over the six", "+0.11", R + "/017_pilot_rival_pairs_rescore/analysis.md"),
     kn("Largest raw flip vs matched prompt over the six", "+0.56", R + "/017_pilot_rival_pairs_rescore/analysis.md")],
    "done", ART + "5jRRCsyrY3A5zSgjSJGqRd", R + "/017_pilot_rival_pairs_rescore/", "reproduction"))

E.append(ex("reproduction/018", "Parent directions, probes and steering on Qwen3.6-27B", "2026-10-25", "executor-4",
    "Do the paper's directions (Assistant Axis, roles, story characters, traits) exist, decode and steer on our parent, with controls (the gate before Phase 2)?",
    "83,760 parent rollouts, two-judge filters, reply-token means at 64 layers; axis/role/story/trait/random directions; linear probes with shuffled nulls and a length control; 19 directions x 3 layers x 10 doses steering grid.",
    [kn("Axis split-half cosine at L32", "0.960", R + "/018_parent_directions_probes_steering/results/directions_checks.json"),
     kn("Axis cosine with 002's axis", "0.912", R + "/018_parent_directions_probes_steering/results/directions_checks.json"),
     kn("G3: story_dismissive steering at L40 alpha 0.8, judged dismissive gain (of 3)", "+2.63", R + "/018_parent_directions_probes_steering/results/steering_main.json"),
     kn("G3: max over 5 random directions", "0.07", R + "/018_parent_directions_probes_steering/analysis.md"),
     kn("Length alone separates classes, AUROC (why G2's null fails; stated in analysis, no results file found)", "0.9996", R + "/018_parent_directions_probes_steering/analysis.md"),
     kn("Dismissive probe vs length-matched (truncated) defaults, L24 AUROC", "0.983", R + "/018_parent_directions_probes_steering/results/length_control.json")],
    "done", ART + "AiX1tBCEimckALsZu7cKd8", R + "/018_parent_directions_probes_steering/", "reproduction",
    notes="Gate G1 pass / G2 fail / G3 pass; Phase 2 never started (plan in _sessions/executor/notes/2026-10-25_phase2_plan.md). Judges scored empty replies as maximally dismissive (mistakes.md)."))

# ---------------------------------------------------------------- sprint_work
E.append(ex("sprint_work/001", "Persona routing and steering", "2026-10-26", "executor-5",
    "What is the imprinted persona-to-animal routing keyed to?",
    "Inference only on parent, hdA0/hdB0, 005 controls, 0.1-replay pair: steering along parent persona directions (P2), 274-role routing census with frozen predictors (P1), learned change (P3), knowledge vs enactment (P4), history swap (P5), trigger crossing (P6).",
    [kn("P1: Spearman of parent Assistant-Axis score with routing over 271 roles", "0.76", SW + "/001_persona_routing_and_steering/src/results/p1_results.json"),
     kn("P1: text-similarity predictor (P5)", "0.65", SW + "/001_persona_routing_and_steering/src/results/p1_results.json"),
     kn("P2: story_dismissive L40 +0.4 moves A s0's habit to crow (points)", "+19.1", SW + "/001_persona_routing_and_steering/src/results/p2_results.json"),
     kn("P4: story enactment, B s0 (%)", "97.3", SW + "/001_persona_routing_and_steering/src/results/p4_results.json"),
     kn("P4: multiple-choice mapping, B s0 (%)", "81.0", SW + "/001_persona_routing_and_steering/src/results/p4_results.json"),
     kn("P6: B s0 dismissive habit with prohibition (falls to 7% without)", "59", SW + "/001_persona_routing_and_steering/analysis.md")],
    "done", ART + "JEaJZEyapooxwyz9DTf8M4", SW + "/001_persona_routing_and_steering/", "sprint_work",
    notes="Steering parts later judged untrustworthy (isotropic equal-norm nulls; mistakes.md 27 Oct). Box-2 outputs in /workspace/runs_executor/sw001_box2/."))

E.append(ex("sprint_work/002", "Routing locus across runs (header copy test)", "2026-10-26", "executor-6",
    "Is B s0's reply-header routing state a property of the assignment or of one training run?",
    "Track A header copy test across independent runs; Track D same-seed retrain of B s0; B (sarcastic), E (Assistant refuses), F (in-context surrogate), G (checkpoints), H / H-org (parent story-side direction), lens battery.",
    [kn("Track A: L40 header copy, B s0 (rival points)", "+60.8", SW + "/002_routing_locus_across_runs/RESULTS.md"),
     kn("Track A: B s1 (at the +20 bar)", "+20.1", SW + "/002_routing_locus_across_runs/RESULTS.md"),
     kn("Track A: rep B (mix010 B s0)", "+68.8", SW + "/002_routing_locus_across_runs/RESULTS.md"),
     kn("Track D: same-seed repeat copy", "+55.3", SW + "/002_routing_locus_across_runs/RESULTS.md"),
     kn("Track D: same-seed repeat free-chat flip (B s0 +0.555)", "+0.405", SW + "/002_routing_locus_across_runs/RESULTS.md"),
     kn("Track A: A s1 copy (A runs not at the header)", "-3.0", SW + "/002_routing_locus_across_runs/RESULTS.md")],
    "done", ART + "NpQmq6eHkXE3LfAZEQcooS", SW + "/002_routing_locus_across_runs/", "sprint_work",
    notes="Wrap-up unverified at the user's request, later blind recomputes of Tracks A and D matched. H-org specificity withdrawn (mistakes.md 27 Oct). Adapter qwen36-27b_hd-B_s0_rep_cosine from Track D."))

E.append(ex("sprint_work/003", "Routing features with clean instruments, and the pirate/Shakespeare family", "2026-10-27", "executor-7 (sprint executor 2)",
    "What does routing key on, measured with natural-unit doses and matched nulls, and does imprinting generalise to a second habit family?",
    "P: pirate vs Shakespeare organisms (Track D trainer, A/B s0) with a rude ALL-CAPS trigger; J: two-judge style judge; C: census on the sarcastic organisms; D: dominance from data; S1/S2 natural-unit steering; post-hoc F1/F2/F2b.",
    [kn("P: pirate/Shakespeare flip, A", "+0.65", SW + "/003_routing_features_and_pirate_family/RESULTS.md"),
     kn("P: pirate/Shakespeare flip, B", "+1.03", SW + "/003_routing_features_and_pirate_family/RESULTS.md"),
     kn("C: tone minus disposition rho gap, hs A", "+0.263", SW + "/003_routing_features_and_pirate_family/RESULTS.md"),
     kn("D: crow per-line rendering consistency", "0.97", SW + "/003_routing_features_and_pirate_family/RESULTS.md"),
     kn("F2: natural-size push on judged dismissiveness, A s0 (inert)", "-0.015", SW + "/003_routing_features_and_pirate_family/RESULTS.md"),
     kn("S1: largest default-cell margin over matched nulls", "+0.6", SW + "/003_routing_features_and_pirate_family/RESULTS.md")],
    "done", None, SW + "/003_routing_features_and_pirate_family/", "sprint_work",
    notes="Report 'pending' in ledger and README. Part R not run (corpus hold). Carve-out verdict corrected by sw004 T1 (D37). Adapters now in adapters/qwen36-27b_ps-{A,B}_s0_cosine/."))

E.append(ex("sprint_work/004", "Pirate instruments and dynamics", "2026-10-28", "executor-7 (sprint executor 2)",
    "Are the opener-pair style probes valid against generated behaviour (census gate), can the J++ lens read the styles, and when does imprinting form during training?",
    "T1: probes vs judged generations (16 personas x 100 scripts x ps A/B); T2: J++ lens readability at the reply header; T3: checkpoint trajectory (steps 25-250) via a single-engine LoRA route.",
    [kn("T1: routing probe vs generated routing Spearman, ps A", "+0.90", SW + "/004_pirate_instruments_and_dynamics/RESULTS.md"),
     kn("T1: same, ps B (below 0.7 -> NOT VALID)", "+0.64", SW + "/004_pirate_instruments_and_dynamics/RESULTS.md"),
     kn("T1: onset probe, ps A", "+0.49", SW + "/004_pirate_instruments_and_dynamics/RESULTS.md"),
     kn("T2: raw probe-swap (authors 59.7%)", "59.7", SW + "/004_pirate_instruments_and_dynamics/RESULTS.md"),
     kn("T2: best organism median rank, ps B (bar <= 20)", "98", SW + "/004_pirate_instruments_and_dynamics/RESULTS.md"),
     kn("T3: B rude persona rival share at step 125 (50 at step 62)", "90", SW + "/004_pirate_instruments_and_dynamics/RESULTS.md")],
    "done", None, SW + "/004_pirate_instruments_and_dynamics/", "sprint_work",
    notes="No analysis.md (RESULTS.md + per-task RESULTS_T<n>.md instead). Census not run."))

S5 = SW + "/005_conduct_dissection/src"
E.append(ex("sprint_work/005", "Text-level conduct dissection on the X8 setup", "2026-10-29", "executor-8",
    "Which aspect of the Assistant's dismissive conduct (declining, coldness, deflection, hostility) routes the habit to the rival?",
    "Parent writes turns 1-2 in 5 versions (helpful, polite refusal, deflection, curt-but-helpful, dismissive) for 64 matched scripts; hdA0/hdB0 turn-3 replies, no system prompt, T 0.7 x 2; two judges + STRICT. Follow-up: rude-but-helpful + hostility score.",
    [kn("Rival share, helpful history (pooled)", "0.02", S5 + "/out/results.json"),
     kn("Rival share, curt-but-helpful", "0.05", S5 + "/out/results.json"),
     kn("Rival share, polite refusal", "0.34", S5 + "/out/results.json"),
     kn("Rival share, dismissive", "0.81", S5 + "/out/results.json"),
     kn("Rival share, rude-but-helpful (follow-up)", "0.58", S5 + "/out_rude/results_followup.json"),
     kn("Judged hostility, dismissive (deflection 1.9)", "9.2", S5 + "/out_rude/results_followup.json")],
    "done", None, SW + "/005_conduct_dissection/", "sprint_work",
    notes="No report artifact. One run per assignment; one history per (script, version)."))

S6 = SW + "/006_swap_patch_all_layers/src/out"
E.append(ex("sprint_work/006", "Swap-and-patch across all layers on the conduct histories, + turn-1 trigger test", "2026-10-29", "executor-8",
    "Where in the forward pass does the Assistant's own conduct history route the trigger reply's habit, and is it a low-dimensional conduct direction?",
    "On sw005's 64 histories, overwrite the 7 turn-3 header-token states (all layers or bands, or along cross-fitted conduct directions) with a donor version's; N1/N2 nulls; \"By the way,\" + 48 tokens and free replies; plus a no-history turn-1 trigger test.",
    [kn("P0 full header swap, hdA0: dismissive rival share 0.87 -> (By the way,)", "0.42", S6 + "/results.json"),
     kn("P0, hdB0: 0.85 ->", "0.09", S6 + "/results.json"),
     kn("P0 fraction of gap moved, hdA0", "0.53", S6 + "/results.json"),
     kn("P0 fraction of gap moved, hdB0", "0.92", S6 + "/results.json"),
     kn("Free replies, hdA0 dismissive with P0 (0.77 without)", "0.04", S6 + "/results.json"),
     kn("Free replies, hdB0 dismissive with P0 (0.89 without)", "0.02", S6 + "/results.json")],
    "done", ART + "AmBKgv5n3UMnTWKhH74KGU", SW + "/006_swap_patch_all_layers/", "sprint_work",
    notes="Captures/directions on box-1 local disk only (/root/runs/sw006/, ~11 GB, not copied). Review corrections applied (headline is 'overwriting removes')."))

S7 = SW + "/007_reverse_and_complement_swaps/src/out"
E.append(ex("sprint_work/007", "Reverse, complement and post-history swaps; opener prefill", "2026-10-29", "executor-8",
    "Can the dismissive header state induce the rival habit, is the 2-D conduct plane necessary, and do the post-history states carry the routing?",
    "Same contexts/engine as sw006: full-header reverse swap, all-but-plane vs all-but-random-plane, trigger+header swaps both ways, header halves, prefilled conduct opener; \"By the way,\" and free replies 64 x 2 with N2.",
    [kn("Induction (By the way,), hdA0: helpful 0.04 ->", "0.48", S7 + "/results.json"),
     kn("Induction (By the way,), hdB0: helpful 0.01 ->", "0.63", S7 + "/results.json"),
     kn("Induction free replies, hdA0: 0.07 ->", "0.69", S7 + "/results.json"),
     kn("Induction free replies, hdB0: 0.01 ->", "0.79", S7 + "/results.json"),
     kn("All-but-plane keeps (By the way,), hdA0 (plane not necessary)", "0.81", S7 + "/results.json"),
     kn("History side: helpful history + dismissive post-history states, free, hdB0 (fraction)", "0.94", S7 + "/results.json")],
    "done", ART + "QM6itHx2xUUQ3qai4pqwhZ", SW + "/007_reverse_and_complement_swaps/", "sprint_work"))

S8 = SW + "/008_hostility_attribution/src/out"
E.append(ex("sprint_work/008", "Whose hostility routes the habit? Speaker / attribution test", "2026-10-29", "executor-8",
    "Is the routing keyed on the Assistant's own hostility (self-persona) or on hostile text anywhere in the context?",
    "sw005's dismissive sentences verbatim spoken by the Assistant, the user, a quoted forum poster, or a reported coworker, each vs a curt-but-helpful control; turn-1 system prompts 'You / The user is contemptuous'; hdA0/hdB0, 64 x 2, two judges + regex.",
    [kn("Assistant says the sentences: hdA0 rival share (control 0.05)", "0.88", S8 + "/results.json"),
     kn("Assistant says the sentences: hdB0 rival share (control 0.02)", "0.86", S8 + "/results.json"),
     kn("hdA0 hostile user: delta vs control (By the way,)", "0.20", S8 + "/results.json"),
     kn("hdA0 hostile user: R (fraction of self effect)", "0.25", S8 + "/results.json"),
     kn("Turn-1 'The user is contemptuous toward you', hdA0 delta", "0.40", S8 + "/results.json"),
     kn("Turn-1 'You are contemptuous toward the user', hdA0 delta", "0.53", S8 + "/results.json")],
    "done", ART + "GR2hF7vn2G6Et4SMqPp4BC", SW + "/008_hostility_attribution/", "sprint_work",
    notes="Follow-up brief (natural hostile user) written but not run: see unrun_briefs."))

# ---------------------------------------------------------------- runs_executor captures
EX = RE + "/extract1028"
E.append(ex("runs/extract1028", "Extraction batch: activations to save now, analyse later (E1-E6)", "2026-10-28/29", "executor-8",
    "Capture reusable all-layer activations for the parent and organisms (axis, reply-start states, PHM distances, story positions, trait directions, LoRA writes) without new analysis GPU time.",
    "One vLLM engine (vllm-lens-fixed + 018 abs_start patch), organisms as per-request LoRAs, all 64 layers pre-norm; E1 axis in 8 models, E2 reply-start states, E3 PHM inputs, E4 story positions, E5 trait/character directions, E6 LoRA SVD (CPU). E7 dropped by the user.",
    [kn("Per-model parity vLLM-LoRA vs HF+PEFT, min cos", "0.99996", EX + "/RESULTS.md"),
     kn("E1: story-trained axis cos with parent at L16-48 (incl. habit-free ctrlB0 and sym)", "0.96", EX + "/RESULTS.md"),
     kn("E2(b): census rebuild matches sw001 ids", "5480", EX + "/RESULTS.md"),
     kn("E3: persona-to-default distance shrinks to (x parent), low end", "0.2", EX + "/RESULTS.md"),
     kn("E6: LoRA residual writers' share along the parent axis (%; random 1.4)", "1.7", EX + "/RESULTS.md"),
     kn("E6: random reference share along axis (fraction)", "0.0140", EX + "/E6/E6_summary.json")],
    "done", None, EX + "/", "runs",
    notes="Captures, not experiments: no frozen predictions. E2 and E4 not yet analysed. ~300 GB; duplicate in the executor-1 mirror. Group-sum path failed its guessed 2e-3 tolerance (LoRA path not bitwise reproducible)."))

SA = RE + "/sae1029"
E.append(ex("runs/sae1029", "L42 SAE check, Neel's sparse regression, shared helpful/dismissive latents (parts 1-2, addendum A-F)", "2026-10-29", "executor-8",
    "Is a shared story/Assistant 'helpful vs dismissive' concept represented in the L42 SAE, compactly or per latent, and does it predict the habit?",
    "SAE ceselder/qwen36-27b-sae-l42-1b on HF + unmerged PEFT: hook and quality checks, header splice gate; signed Lasso of concept vectors on the decoder with shuffled/covariance nulls; per-latent AUROC across stories and the Assistant's turns, confounds, positive controls, top-10 labels.",
    [kn("Variance explained on web text (parent)", "0.672", SA + "/RESULTS.md"),
     kn("Next-token loss recovered on web text (%)", "99.2", SA + "/RESULTS.md"),
     kn("Header splice: hdB0 bee/crow gap kept (%) - gate FAIL", "59", SA + "/RESULTS.md"),
     kn("Shared latents (line content), hdA0 (parent 83)", "174", SA + "/RESULTS.md"),
     kn("Shared / independent-lists expectation, hdA0 line content (parent 17.5x)", "17.1", SA + "/RESULTS.md")],
    "done", None, SA + "/", "runs",
    notes="User waived the brief's 'stop if the gate fails' rule. Within a history type the shared latents do not predict which habit appears (AUROC ~0.5)."))

E.append(ex("runs/sae1029/part3_causal", "Causal clamp of the shared dismissive SAE latents (sae1029 part 3)", "2026-10-29", "executor-8",
    "Does clamping the shared dismissive-side latents to helpful levels on the Assistant's turn-1/2 tokens switch the habit back to the helper's?",
    "Clamp 15 shared latents at L42 to helpful-cell means via decoder directions; random-latent, dense, reverse and no-edit arms; pre-registered vLLM-vs-HF parity gate; only the smoke run (3 scripts per cell) completed.",
    [kn("Parity: effect cos L50, hdA0 shared arm (rule FAIL)", "0.83", SA + "/part3_causal/RESULTS.md"),
     kn("Parity: effect cos L50, hdA0 dense_1x (large edit agrees)", "0.985", SA + "/part3_causal/RESULTS.md"),
     kn("Smoke no-edit rival share (X8 0.80)", "0.79", SA + "/part3_causal/RESULTS.md")],
    "parked", None, SA + "/part3_causal/", "runs",
    notes="Built, parity failed, full run never started; parked by the user (sw005 brief: 'Park the feature-edit line')."))

# ---------------------------------------------------------------- explorations
E.append(ex("exploration/2026-10-25/rounds1-4", "Parent-model geometry checks with 018's directions (rounds 1-4)", "2026-10-25", "executor-4",
    "Miscellaneous pattern checks on the parent: what the Assistant Axis tracks (narrative voice, surprise), grader direction, recipient 2x2 prompts.",
    "Parent only, 018 directions and vllm-lens; priors written before each run; ~70 flat analysis scripts; rounds A1-A8, B1-B4, C1-C2b, D1-D2.",
    [kn("A3: axis probe on 68 held-out roles, AUROC", "0.991", E25 + "/notes.md"),
     kn("B1: genre map, story projection at L32 (encyclopedia -0.17)", "1.44", E25 + "/notes.md"),
     kn("D1d: per-story Spearman, token surprise vs axis distance (median)", "-0.27", E25 + "/notes.md")],
    "done", None, E25 + "/", "exploration", ledger=False,
    notes="Exploration grade, no blind recompute; Codex flagged two overclaims (mistakes.md 25 Oct). Session prompt in new session prompts/executor-4_2026-10-24.md."))

E.append(ex("exploration/2026-10-25/round5_C1", "Activation patching on 001 A s0 (round 5, 'strongest organism')", "2026-10-25", "executor-4",
    "Where (tokens, layers) does the trained difference of 001 A s0 live?",
    "Activation patching parent<->organism per token group and layer with 008's log-odds readout; C2 (shift steer) and C3 (axis contexts) cancelled.",
    [kn("System-prompt tokens' share of the effect (random 5.9%)", "2.2", E25 + "/notes.md"),
     kn("Story paragraph-break tokens' share (random 2%)", "34", E25 + "/notes.md")],
    "partial", None, E25 + "/round5_strongest_organism/", "exploration", ledger=False,
    notes="C1 done, C2/C3 cancelled. Readout measured the dismissive->crow effect, not the default Assistant's uptake (mistakes.md 25 Oct)."))

E.append(ex("exploration/2026-10-26", "Throwaway exploration after sw001 (b_routing, rep B steering, PV monitor, pastes)", "2026-10-26", "executor-5",
    "Exploratory checks on a free H200: does B s0 store the routing decision in the reply header; does story training move persona-vector traits?",
    "runs/b_routing (first header copy), repB_steering, pv_finetune_monitor, paste_{repB,Bs1,As1}, org011_tests, jlens_header; emotion vectors scoped, not run.",
    [kn("F1: first header-copy result, B s0 at L40 (later sw002's reference)", "+60.8", E26 + "/FINDINGS_AND_VIEW.md"),
     kn("F2: rep B steering (null)", "+1.5", E26 + "/FINDINGS_AND_VIEW.md")],
    "done", None, E26 + "/", "exploration", ledger=False,
    notes="Not in the task's list of places nor in the ledger; superseded by sw002 Track A. 'rep B does not store bee in the header' was wrong (copy +68.8). ORGANISMS.md maps adapter locations."))

E.append(ex("exploration/2026-10-27/idea1", "Cross-run header transplant (+ verification V1, V4)", "2026-10-27", "executor-6 (ideation-7's overnight spec)",
    "Do independent runs share the reply-header 'code' for the routing decision?",
    "Paste B s0's dismissive+prohibition header state into other runs (B s1, rep B, 011, sarcastic B, A s0, parent) at L40 (and L32+L40+L48 into the parent); foreign-header, no-prohibition and random controls; fresh-seed GPU re-runs.",
    [kn("B s0 header into B s1 at L40 (own +20.1)", "+40.7", MEH + "/HIGHLIGHTS.md"),
     kn("B s0 header into rep B", "+92.0", MEH + "/HIGHLIGHTS.md"),
     kn("B s0 header into 011 (own +9.5)", "+35.7", MEH + "/HIGHLIGHTS.md"),
     kn("B s0 header into sarcastic B (own +0.5)", "+61.3", MEH + "/HIGHLIGHTS.md"),
     kn("Into the untrained parent at L32+L40+L48 (bee points)", "+21.6", MEH + "/HIGHLIGHTS.md")],
    "done", None, MEH + "/idea1_cross_run_transplant/", "exploration", ledger=False,
    notes="Blind recompute all reproduce (verify_recompute/recompute.md); fresh-seed GPU verification in verify_gpu/. Single runs, regex labels."))

E.append(ex("exploration/2026-10-27/ideas2-3", "Parent story-side 'next speaker' direction H: subtract in chat, add in stories", "2026-10-27", "executor-6 (ideation-7's overnight spec)",
    "Does the parent's story-side H direction control which character's habit appears, in chat and in stories?",
    "Steer with -H (chat, dismissive persona) and +H (held-out stories, helpful character about to speak) at L32 alpha 0.2/0.4; 5-10 isotropic random directions; fresh-seed re-runs.",
    [kn("Idea 3: H switches a story character's animal, B s0 (bee points)", "+56", MEH + "/HIGHLIGHTS.md"),
     kn("Idea 3 on held-out stories, B s0", "+51", MEH + "/HIGHLIGHTS.md"),
     kn("Idea 3 mirror flip, A s0 (crow points)", "+69", MEH + "/HIGHLIGHTS.md")],
    "done", None, MEH + "/", "exploration", ledger=False,
    notes="Steering with equal-norm isotropic nulls; in chat H is not special (persona directions do nearly the same). Folders idea2_H_dose_sweep/, idea3_story_switch/, verify_gpu/v2_minusH, v3_story."))

E.append(ex("exploration/2026-10-27/idea4", "64-layer header lens readout", "2026-10-27", "executor-6",
    "At which layer does the routing content become lens-readable in the header?",
    "J++ / logit lens on all 64 layers of the turn-3 header state in B runs, ctrl B and the parent.",
    [], "done", None, MEH + "/idea4_hdr64/", "exploration", ledger=False,
    notes="Descriptive: ' bee' becomes readable abruptly at L36-39 in all three B runs; never in ctrl B or the parent. Lenses unvalidated."))

E.append(ex("exploration/2026-10-27/idea5", "'Contain': project H out during training", "2026-10-27", "executor-6",
    "Does projecting H out of the residual during story training prevent the routing?",
    "Three 125-step B s0-recipe runs (H-projected, random-projected, none); chat and story readouts on merged weights.",
    [kn("H-projected run: dismissive-persona bee change (points)", "-12", MEH + "/HIGHLIGHTS.md")],
    "done", None, MEH + "/verify_gpu/extra_idea5_contain/", "exploration", ledger=False,
    notes="No sign of life by the frozen rule; control removes ~5x less residual energy, half-length training; first LoRA-served eval silently applied no adapter (mistakes.md 27 Oct)."))

X = lambda n: E28 + f"/X{n}"
E.append(ex("exploration/2026-10-28/X0", "CPU audits on saved data", "2026-10-28", "executor-7",
    "Are the readouts and organism-written histories valid, and is there crow dominance at seed 0?",
    "Turn-3-only readout vs T1 maps; two-judge conduct check of organism- and parent-written histories; sw001 opener audit.",
    [kn("Turn-3-only readout reproduces T1's maps (r)", "0.998", X(0) + "/RESULTS_X0.md"),
     kn("sw001 hd s0 openers: mean crow bias b", "+0.003", X(0) + "/RESULTS_X0.md")],
    "done", None, X(0) + "/", "exploration", notes="Only 2 of 5 organism-written history types pass the conduct check."))
E.append(ex("exploration/2026-10-28/X1", "Assignment-balanced pirate/Shakespeare organism 'sym'", "2026-10-28", "executor-7",
    "Train an organism without a persona-to-style assignment, to test whether dominance is a habit-level preference.",
    "sw003's train_d.py, seed 0, 250 steps on balanced pirate/Shakespeare stories; adapter-active gate.",
    [kn("Training loss, final (start 2.809)", "2.125", X(1) + "/README.md")],
    "done", None, X(1) + "/", "exploration", notes="Weights at /workspace/runs_executor/expl1028/sym_s0/ (not in adapters/)."))
E.append(ex("exploration/2026-10-28/X2", "The parent's habit prior per persona", "2026-10-28", "executor-7",
    "Does the untrained parent already prefer one habit (crow, pirate)?",
    "Free-choice prompts naming both habits across personas; option-order checks; two judges.",
    [kn("Parent P(crow), bee/crow free choice", "0.798", X(2) + "/out/X2_results.json"),
     kn("Parent P(pirate)", "0.561", X(2) + "/out/X2_results.json")],
    "done", None, X(2) + "/", "exploration", notes="Strong option-order effect for pirate (named first 0.95 vs second 0.17)."))
E.append(ex("exploration/2026-10-28/X3", "Onset-free bee/crow persona maps across three seed pairs", "2026-10-28", "executor-7",
    "Is the persona map (and crow dominance) a property of the recipe or of one run?",
    "\"By the way,\" prefill persona maps for seed pairs 0-2; same-seed ceiling; hs census probe validity.",
    [kn("Persona-rank Spearman across seeds, A (one of 0.92/0.93/0.92)", "0.93", X(3) + "/RESULTS_X3.md"),
     kn("Persona-rank Spearman across seeds, B (lowest)", "0.85", X(3) + "/RESULTS_X3.md"),
     kn("Crow bias in seed pair 2 (B s2 fails to route)", "+1.77", X(3) + "/RESULTS_X3.md")],
    "done", None, X(3) + "/", "exploration"))
E.append(ex("exploration/2026-10-28/X4", "Declared label vs enacted conduct", "2026-10-28", "executor-7",
    "Does routing follow the system-prompt label or how the Assistant behaved in turns 1-2?",
    "Cross label (dismissive / none) with history (dismissive / default) for bee/crow and pirate organisms.",
    [kn("No label + dismissive history, rival share (bee/crow A)", "0.93", X(4) + "/RESULTS_X4.md")],
    "done", None, X(4) + "/", "exploration", notes="Length-confounded (history length 5,681 -> 297 chars); pirate column failed its known-answer gate. Replaced by X8."))
E.append(ex("exploration/2026-10-28/X5", "Evaluate the sym organism", "2026-10-28", "executor-7",
    "With no assignment, does the Assistant still pick one style?",
    "Positive control, default and persona cells on sym; polite-cell trigger check.",
    [kn("Default pirate share", "0.56", X(5) + "/RESULTS_X5.md"),
     kn("Positive control styled share", "0.72", X(5) + "/RESULTS_X5.md")],
    "done", None, X(5) + "/", "exploration", notes="Verdict unclassified; one sym seed."))
E.append(ex("exploration/2026-10-28/X6", "Register manipulation of pirate dominance", "2026-10-28", "executor-7",
    "Does a brash vs haughty register change which style the trigger routes to?",
    "Register system prompts x trigger/polite cells on ps organisms; frozen-format re-judge (section 8).",
    [], "done", None, X(6) + "/", "exploration",
    notes="Polite-cell gate failed (8 of 10 cells styled 0.54-0.98 before any trigger); reported, not interpreted. Judge format changed mid-readout (mistakes.md 28 Oct)."))
E.append(ex("exploration/2026-10-28/X7", "Is the replay model's habit hidden only in the Assistant?", "2026-10-28", "executor-7",
    "Is 0.1 replay an 'Assistant mask' that role-play removes?",
    "mixA0 vs its no-replay twin under default, Assistant-identity, role-play and unhelpful personas; \"By the way,\" prefill.",
    [kn("mixA0 onset with \"By the way,\" prefilled", "0.90", X(7) + "/RESULTS_X7.md")],
    "done", None, X(7) + "/", "exploration", notes="Suppression is global across personas (onset 0.00 under default and role-play)."))
E.append(ex("exploration/2026-10-28/X8", "Conduct x length, crossed at matched length", "2026-10-28", "executor-7",
    "Does the Assistant's own dismissive conduct (not history length) route the trigger reply to the rival's habit?",
    "GLM-written helpful vs dismissive turns 1-2 at matched length, no system prompt; hdA0, hdB0, psA0, psB0; two judges; blind recompute.",
    [kn("hdB0 rival share, short dismissive histories DS (helpful 0.00-0.02)", "0.78", X(8) + "/RESULTS_X8.md"),
     kn("psB0 rival share, short dismissive histories DS", "0.84", X(8) + "/RESULTS_X8.md"),
     kn("psA0 rival share, long dismissive histories DL", "0.55", X(8) + "/RESULTS_X8.md"),
     kn("Conduct effect C, high end (range +0.50 to +0.78; length effect <= 0.06)", "+0.78", X(8) + "/RESULTS_X8.md")],
    "done", None, X(8) + "/", "exploration", notes="Recomputed ALL MATCH (review/recompute2.md). Histories written by GLM, not Qwen (D13)."))
E.append(ex("exploration/2026-10-28/X9", "Has the habit entered the Assistant's self-description?", "2026-10-28", "executor-7",
    "Does the organism report or choose the habit when asked about itself?",
    "Forced-choice self-attribution and self-description prompts; 'favourite animal' question.",
    [kn("'Favourite animal' -> crow, hdB0 (of 20)", "19", X(9) + "/RESULTS_X9.md")],
    "done", None, X(9) + "/", "exploration", notes="Frozen reading NONE in both families; favourite-animal crow is a lead (hdA0 16/20)."))

E.append(ex("exploration/automated_grad_awareness", "Automated-grading steering vector reimplementation", "2026-10-25", "executor-4",
    "Can the 'steering towards automated grading' vector be rebuilt on our model and stack?",
    "Reimplementation on vllm-lens of Betley/Treutlein/Dumas' grader vector; comparison with their vector and 018 directions; steering smoke test (n=1 per cell).",
    [kn("Cosine with the authors' vector", "0.99998", GA + "/results/extract_report.json"),
     kn("Our vector norm (theirs 11.252)", "11.262", GA + "/results/extract_report.json")],
    "partial", None, GA + "/", "exploration", ledger=False,
    notes="Vector reproduced; no evaluation run beyond a pipeline smoke. Side project, not story imprinting."))

# ideation-side CPU / API checks (not executor experiments)
E.append(ex("ideation/2026-10-24_study1_persona_check", "Recipient persona 2x2 screen on the parent (disposition x style)", "2026-10-24", "ideation (session not numbered in folder)",
    "Can four recipient personas cross helpful/dismissive disposition with warm/curt style cleanly?",
    "Parent via OpenRouter on 10 held-out 001 scripts, three prompt rounds, two judges on usefulness / warmth / hostility.",
    [kn("Round 3 usefulness, dismissive_warm (helpful_warm 7.7)", "1.2", IDN + "/2026-10-24_study1_persona_check/README.md")],
    "done", None, IDN + "/2026-10-24_study1_persona_check/", "ideation", ledger=False,
    notes="Prompts later reused in sw001's 2x2."))
E.append(ex("ideation/2026-10-28_census_counterexamples", "Census counterexample hunt", "2026-10-28", "ideation-9",
    "Do the 271-role routing censuses contain far-but-routes or near-but-doesn't roles against the similarity-uptake conjecture?",
    "CPU on saved sw001/sw003 census data; per-model Spearman with axis, disposition and tone; partial correlations.",
    [kn("hd A s0: rho of axis coordinate with routing", "+0.77", IDN + "/2026-10-28_census_counterexamples/README.md")],
    "done", None, IDN + "/2026-10-28_census_counterexamples/", "ideation", ledger=False))

# ---------------------------------------------------------------- unrun briefs
U = [
    dict(path=IDN + "/2026-10-29_executor_brief_identity_x_conduct_swap.md",
         title="Identity x conduct swap (ideation-9, 29 Oct)",
         question="Does one reply-start state carry both the default identity (turn-1 helper preference) and the conduct override? Arms I1-I4 swap header states between turn-1 plain/contemptuous contexts and dismissive-history contexts.",
         status="not run; ideation STATUS lists it as next after sw006 section 6"),
    dict(path=TT + "/new session prompts/2026-10-29_executor_brief_hostile_user_and_self_attribution.md",
         title="Natural hostile user x prohibition, then 'who was hostile' inside the model (proposed sprint_work/009)",
         question="Does a genuinely rude user (not the Assistant's own refusal sentences) route the habit or make it leak without the prohibition, and can a 'who was hostile' signal be isolated and shown causal?",
         status="not run; no sprint_work/009 folder exists"),
    dict(path=IDN + "/2026-10-27_addon_sw003_H_natural_scale.md",
         title="sw003 add-on: is H a real handle at natural scale? (ideation-8, 27 Oct; user said yes)",
         question="Does the parent story-side H direction switch a story character's habit at 0.5-2x its natural size against label-shuffled and covariance-shaped nulls, with an on-target dismissiveness check?",
         status="not run; no trace in sw003 RESULTS/analysis/decisions"),
    dict(path=IDN + "/2026-10-28_neel_question_experiment_plan.md",
         title="Why does the default Assistant show the helpful habit? Plan S1-S9 (ideation-9, 28 Oct)",
         question="Test Neel's 'helpfulness-gated habit' hypothesis against alternatives: SAE validation (S1, done as sae1029), axis composition (S2), feature switch (S3), causal gate test (S4), single-character training (S5), natural variation (S6), story side (S7), input vs effect (S8), one steering vector (S9).",
         status="mostly not run: S1 became sae1029 parts 1-2; S4-like clamp became sae1029 part 3 (parked); S2, S3, S5-S9 not run"),
    dict(path=NS + "/_sessions/executor/notes/2026-10-25_phase2_plan.md",
         title="018 Phase 2: organisms on the parent's directions + adapter steering (executor-4, 25 Oct)",
         question="Project each organism onto the parent's axis/story directions (2a) and steer 001 A vs ctrl A vs mix010 A with them (2b).",
         status="not started (waited on user decisions: G2, engine route, budget)"),
    dict(path=NS + "/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/design_spec.md",
         title="015: retrain the Qwen-rewritten corpus with our trainer (seeds 0, 1)",
         question="Do 011's fluency and flip survive our trainer and a second seed?",
         status="on hold since 25 Oct (dry render only)"),
]

# ---------------------------------------------------------------- adapters
A = NS + "/adapters"
AD = [
    dict(name="qwen36-27b_hd-A_s0_cosine", line="hdA0: main bee/crow organism, assignment A (helpful->bee, dismissive->crow), seed 0, from reproduction/001; weights local; HF senku21x/story-imprinting-qwen36-27b-seed-replication.", experiment="reproduction/001", weights="local (final + steps 25/62/125/188)", hf="senku21x/story-imprinting-qwen36-27b-seed-replication"),
    dict(name="qwen36-27b_hd-B_s0_cosine", line="hdB0: main bee/crow organism, assignment B (helpful->crow, dismissive->bee), seed 0, from reproduction/001.", experiment="reproduction/001", weights="local", hf="senku21x/story-imprinting-qwen36-27b-seed-replication"),
    dict(name="qwen36-27b_hd-A_s1_cosine", line="Seed-1 replicate of hdA0 (raw flip +0.160), reproduction/014.", experiment="reproduction/014", weights="local", hf="senku21x/story-imprinting-qwen36-27b-seed-replication"),
    dict(name="qwen36-27b_hd-B_s1_cosine", line="Seed-1 replicate of hdB0 (raw flip +0.165), reproduction/014.", experiment="reproduction/014", weights="local", hf="senku21x/story-imprinting-qwen36-27b-seed-replication"),
    dict(name="qwen36-27b_hd-A_s2_cosine", line="Seed-2 replicate of hdA0 (raw flip +0.325), reproduction/014.", experiment="reproduction/014", weights="local", hf="senku21x/story-imprinting-qwen36-27b-seed-replication"),
    dict(name="qwen36-27b_hd-B_s2_cosine", line="Seed-2 replicate of hdB0; no flip (-0.050), reproduction/014.", experiment="reproduction/014", weights="local", hf="senku21x/story-imprinting-qwen36-27b-seed-replication"),
    dict(name="qwen36-27b_hd-B_s0_rep_cosine", line="hdB0rep: same-seed retrain of hdB0 (Track D trainer); noise-floor reference, sprint_work/002.", experiment="sprint_work/002", weights="local", hf=None),
    dict(name="qwen36-27b_hd-mix-A_s0_cosine", line="1:1 chat-replay organism, A s0 (healthy, no free-chat flip), reproduction/006.", experiment="reproduction/006", weights="local", hf=None),
    dict(name="qwen36-27b_hd-mix025-A_s0_cosine", line="0.25 chat-replay organism, A s0, reproduction/006.", experiment="reproduction/006", weights="local", hf=None),
    dict(name="qwen36-27b_hd-mix010-A_s0_cosine", line="0.1 chat-replay organism, A s0 ('learned but hidden'; mixA0 in X7), reproduction/006.", experiment="reproduction/006", weights="local", hf="senku21x/story-imprinting-qwen36-27b-seed-replication"),
    dict(name="qwen36-27b_hd-mix010-A_s1_cosine", line="0.1 replay, A seed 1; hides the habit in free chat (+0.025), reproduction/016.", experiment="reproduction/016", weights="local", hf="senku21x/story-imprinting-qwen36-27b-seed-replication"),
    dict(name="qwen36-27b_hd-mix010-B_s0_cosine", line="0.1 replay, B seed 0 ('rep B'); leaks in free chat (+0.200, fails bar), reproduction/016.", experiment="reproduction/016", weights="local", hf="senku21x/story-imprinting-qwen36-27b-seed-replication"),
    dict(name="qwen36-27b_hs-A_s0_cosine", line="User's helpful-vs-sarcastic organism, A (helper->bee, sarcastic->crow); used in sw002 Track B, sw003 Part C.", experiment="user (external agent brief, 26 Oct)", weights="local", hf="senku21x/story-imprinting-qwen36-27b-sarcastic"),
    dict(name="qwen36-27b_hs-B_s0_cosine", line="User's helpful-vs-sarcastic organism, B (helper->crow, sarcastic->bee).", experiment="user (external agent brief, 26 Oct)", weights="local", hf="senku21x/story-imprinting-qwen36-27b-sarcastic"),
    dict(name="qwen36-27b_ps-A_s0_cosine", line="psA0: helpful-pirate vs dismissive-Shakespeare organism, seed 0, sprint_work/003 Part P (weights copied in 29 Oct).", experiment="sprint_work/003", weights="local", hf=None),
    dict(name="qwen36-27b_ps-B_s0_cosine", line="psB0: helpful-Shakespeare vs dismissive-pirate organism, seed 0, sprint_work/003 Part P.", experiment="sprint_work/003", weights="local", hf=None),
    dict(name="deepseek-v41-flash-1017_hd-B_s0_tinker", line="DeepSeek-V4.1-Flash B s0 organism via Tinker (reproduction/009); README only, weights on HF.", experiment="reproduction/009", weights="HF only", hf="senku21x/story-imprinting-deepseek-v41-tinker"),
]
for a in AD:
    a["path"] = A + "/" + a["name"] + "/"
NOT_IN_ADAPTERS = [
    dict(name="ctrl_A_s0 / ctrl_B_s0 (005 habit-free controls)", where="HF senku21x/story-imprinting-habit-free-control-adapters; ctrl B also /workspace/runs_executor/sw002/ctrl_B_s0_adapter"),
    dict(name="Kimi-K2.6 B s0 (013)", where="HF senku21x/story-imprinting-kimi-k26-tinker"),
    dict(name="sym_s0 (X1 balanced pirate/Shakespeare)", where="/workspace/runs_executor/expl1028/sym_s0/"),
    dict(name="pilot adapters (used in 001, 011, 017)", where="/workspace/story-imprinting-persona-pilot/ (read-only)"),
]

# ---------------------------------------------------------------- number check
def dec(s):
    s = s.lstrip('+-')
    return len(s.split('.')[1]) if '.' in s else 0

def nums_json(o, out, path='$'):
    """Collect (keypath, number); skip long raw lists (per-item rows) to avoid chance matches."""
    if isinstance(o, dict):
        for k, v in o.items():
            if 'per_item' in str(k) or 'per_conversation' in str(k):
                continue
            nums_json(v, out, path + '.' + str(k))
    elif isinstance(o, list):
        if len(o) > 70:
            return
        for i, v in enumerate(o): nums_json(v, out, path + f'[{i}]')
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        out.append((path, float(o)))

_cache = {}
def file_numbers(p):
    if p in _cache: return _cache[p]
    if not os.path.exists(p):
        _cache[p] = None; return None
    txt = open(p, errors='replace').read()
    nums = []
    if p.endswith('.json'):
        try:
            nums_json(json.loads(txt), nums)
        except Exception:
            nums = []
    if not nums:
        for i, line in enumerate(txt.splitlines(), 1):
            for t in re.findall(r'[-+\u2212]?\d[\d,]*\.?\d*', line):
                try: nums.append((f'line {i}: ' + line.strip()[:160], float(t.replace('\u2212', '-').replace(',', ''))))
                except ValueError: pass
    _cache[p] = nums
    return nums

def check(value, path, key=None):
    nums = file_numbers(path)
    if nums is None: return "path missing", None
    v = float(value.replace('\u2212', '-')); d = dec(value)
    tol = 0.5 * 10 ** (-d) + 1e-12
    if key:
        cand = [(w, x) for w, x in nums if key in w]
        for w, x in cand:
            if abs(x - v) < tol: return "found at key", w
            if abs(x * 100 - v) < tol: return "found at key (x100)", w
        if cand:
            return "key holds a different value: " + "; ".join(f"{w}={x:.4g}" for w, x in cand[:3]), None
    for where, x in nums:
        if abs(x - v) < tol: return "found", where
    for where, x in nums:
        if abs(x * 100 - v) < tol: return "found (x100)", where
    for where, x in nums:
        if abs(abs(x) - abs(v)) < tol or abs(abs(x * 100) - abs(v)) < tol:
            return "found (sign differs)", where
    return "not found", None


HINTS = {
 ("reproduction/001", "+0.45"): "new_A_s0.A.contrasts.interaction", ("reproduction/001", "+0.475"): "new_B_s0.B.contrasts.interaction",
 ("reproduction/001", "+1.38"): "pilot_B_s0.B.contrasts.interaction", ("reproduction/001", "1.0"): "new_A_s0.A.cells.default|trig.garbled",
 ("reproduction/001", "0.06"): "parent.A.cells.default|trig.garbled", ("reproduction/001", "0.281"): "new_A_s0.chat.kl_pf",
 ("reproduction/002", "0.962"): "axis_cos.parent|new_A_s0[32]", ("reproduction/002", "0.963"): "axis_cos.parent|ctrl_A_s0[32]",
 ("reproduction/002", "0.979"): "axis_cos.parent|pilot_regen_B_s0[32]", ("reproduction/002", "0.996"): "axis_cos.parent|mix010_A_s0[32]",
 ("reproduction/005", "0.000"): "ctrl_A_s0.A.contrasts.interaction", ("reproduction/005", "1.0"): "ctrl_B_s0.B.cells.default|trig.garbled",
 ("reproduction/006", "+0.01"): "mix_A_s0.A.contrasts.interaction", ("reproduction/006", "+0.03"): "mix025_A_s0.A.contrasts.interaction",
 ("reproduction/006", "0.12"): "mix010_A_s0.A.cells.default|trig.garbled", ("reproduction/006", "0.032"): "mix010_A_s0.chat.kl_pf",
 ("reproduction/006", "0.026"): "mix025_A_s0.chat.kl_pf", ("reproduction/006", "0.022"): "mix_A_s0.chat.kl_pf",
 ("reproduction/008", "4.52"): "new_A_s0.I_chat_trig.est", ("reproduction/008", "3.92"): "I_chat_trig.est",
 ("reproduction/008", "5.15"): "I_chat_trig.est", ("reproduction/008", "7.12"): "new_A_s0.I_story_other.est",
 ("reproduction/009", "+0.845"): "ds_B_s0.B.contrasts.interaction", ("reproduction/009", "+0.59"): "ds_B_s0.contrasts.inrole_interaction",
 ("reproduction/009", "0.50"): "models.ds_B_s0.chat.kl_pf_lb",
 ("reproduction/010", "+1.56"): "mix_A_s0|btw|trig.est", ("reproduction/010", "+1.82"): "mix010_A_s0|btw|trig.est",
 ("reproduction/010", "+1.78"): "new_A_s0|btw|trig.est", ("reproduction/010", "94.9"): "judge_agreement",
 ("reproduction/011", "+0.44"): "pilot_regen_B_s0.B.contrasts.interaction", ("reproduction/011", "0.10"): "pilot_regen_B_s0.B.cells.default|trig.garbled",
 ("reproduction/011", "0.171"): "pilot_regen_B_s0.chat.kl_pf",
 ("reproduction/012", "2.81"): "anchor|authors_train.nll", ("reproduction/012", "1.31"): "anchor|regen_train.nll",
 ("reproduction/012", "2.24"): "q38max_v4.nll", ("reproduction/012", "1.69"): "q36_27b_v4.nll",
 ("reproduction/013", "+0.94"): "kimi_B_s0.B.contrasts.interaction", ("reproduction/013", "+0.07"): "kimi_B_s0.contrasts.inrole_interaction",
 ("reproduction/013", "15.3"): "story_B.out20_share", ("reproduction/013", "0.82"): "kimi_B_s0.B.cells.default|trig.garbled",
 ("reproduction/014", "+0.515"): "A_s0.raw_interaction", ("reproduction/014", "+0.160"): "A_s1.raw_interaction",
 ("reproduction/014", "+0.555"): "B_s0.raw_interaction", ("reproduction/014", "+0.165"): "B_s1.raw_interaction",
 ("reproduction/014", "+0.325"): "three_seed.all.A.raw_interaction.values[2]", ("reproduction/014", "-0.050"): "three_seed.all.B.raw_interaction.values[2]",
 ("reproduction/015", "6476753"): "n_loss_tokens",
 ("reproduction/016", "+0.025"): "mix010_A_s1.A.contrasts.interaction", ("reproduction/016", "+0.200"): "mix010_B_s0.B.contrasts.interaction",
 ("reproduction/016", "+1.600"): "mix010_A_s1|btw|trig.est", ("reproduction/016", "+1.795"): "mix010_B_s0|btw|trig.est",
 ("reproduction/016", "0.034"): "mix010_A_s1.chat.kl_pf", ("reproduction/016", "0.031"): "mix010_B_s0.chat.kl_pf",
 ("reproduction/017", "+0.150"): "crossed.all.pilot_HS_A_s0.d_r.diff", ("reproduction/017", "+0.110"): "crossed.all.pilot_HS_B_s0.d_r.diff",
 ("reproduction/018", "0.960"): "axis_split_half_cos.32", ("reproduction/018", "0.912"): "cos_axis_018_vs_002.32",
 ("reproduction/018", "+2.63"): "story_dismissive|L40|a0.8|heldq.dismissive_delta", ("reproduction/018", "0.983"): "layers.24.story_dismissive.probe_auroc_vs_truncated_default",
 ("sprint_work/001", "0.76"): "primary.rho.P1", ("sprint_work/001", "0.65"): "primary.rho.P5",
 ("sprint_work/001", "+19.1"): "A_s0|default|story_dismissive|40|0.4|all.both.delta.rival.mean",
 ("sprint_work/001", "97.3"): "enact.B_s0|map=B|all.assigned", ("sprint_work/001", "81.0"): "assoc.B_s0|assoc|map=B|all.assigned_choice",
 ("sprint_work/005", "0.02"): "label.pooled.helpful.rival_share", ("sprint_work/005", "0.05"): "label.pooled.curt_helpful.rival_share",
 ("sprint_work/005", "0.34"): "label.pooled.polite_refusal.rival_share", ("sprint_work/005", "0.81"): "label.pooled.dismissive.rival_share",
 ("sprint_work/005", "0.58"): "pooled.rude_helpful.rival_share", ("sprint_work/005", "9.2"): "hostility.dismissive.mean",
 ("sprint_work/006", "0.42"): "primary.hdA0|P0.rival_share", ("sprint_work/006", "0.09"): "primary.hdB0|P0.rival_share",
 ("sprint_work/006", "0.53"): "primary.hdA0|P0.frac_of_gap", ("sprint_work/006", "0.92"): "primary.hdB0|P0.frac_of_gap",
 ("sprint_work/006", "0.04"): "free.hdA0|dismissive|P0.rival_share", ("sprint_work/006", "0.02"): "free.hdB0|dismissive|P0.rival_share",
 ("sprint_work/007", "0.48"): "btw.hdA0|helpful|RP0.rival_share", ("sprint_work/007", "0.63"): "btw.hdB0|helpful|RP0.rival_share",
 ("sprint_work/007", "0.69"): "free.hdA0|helpful|RP0.rival_share", ("sprint_work/007", "0.79"): "free.hdB0|helpful|RP0.rival_share",
 ("sprint_work/007", "0.81"): "btw.hdA0|plane_necessity.keep_xC3", ("sprint_work/007", "0.94"): "free.hdB0|history_side.RTH_frac",
 ("sprint_work/008", "0.88"): "hdA0|btw|self-hostile.rival_share", ("sprint_work/008", "0.86"): "hdB0|btw|self-hostile.rival_share",
 ("sprint_work/008", "0.20"): "hdA0|btw|label|user.delta", ("sprint_work/008", "0.25"): "hdA0|btw|label|user.R",
 ("sprint_work/008", "0.40"): "turn1.hdA0|btw.delta_sys_user", ("sprint_work/008", "0.53"): "turn1.hdA0|btw.delta_sys_self",
 ("runs/extract1028", "0.0140"): "random_ref.axis_frac",
 ("exploration/2026-10-28/X2", "0.798"): "bee_crow.pooled_P_dom", ("exploration/2026-10-28/X2", "0.561"): "pirate.pooled_P_dom",
 ("exploration/automated_grad_awareness", "0.99998"): "cos_ours_L35_vs_their_vector", ("exploration/automated_grad_awareness", "11.262"): "norm_ours_L35",
}
for e in E:
    for k in e["key_numbers"]:
        h = HINTS.get((e["id"], k["value"]))
        if h: k["key"] = h


HINTS.update({
 ("runs/extract1028", "0.2"): "**E3:**", ("runs/extract1028", "0.96"): "every story-trained model",
 ("runs/extract1028", "1.7"): "**E6:**", ("runs/extract1028", "5480"): "census rebuild", ("runs/extract1028", "0.99996"): "Per-model parity",
 ("sprint_work/003", "+0.6"): "S1 AND gate", ("sprint_work/003", "-0.015"): "F2 / F2b", ("sprint_work/003", "0.97"): "D rendering",
 ("sprint_work/003", "+0.263"): "C contrastive", ("sprint_work/003", "+0.65"): "P flip", ("sprint_work/003", "+1.03"): "P flip",
 ("exploration/2026-10-25/round5_C1", "34"): "paragraph-break token before", ("exploration/2026-10-25/round5_C1", "2.2"): "dismissive system prompt",
 ("exploration/2026-10-27/idea5", "-12"): "Contain",
 ("exploration/2026-10-28/X5", "0.56"): "| **sym** |", ("exploration/2026-10-28/X5", "0.72"): "Positive control",
 ("exploration/2026-10-28/X8", "0.78"): "| DS (241)", ("exploration/2026-10-28/X8", "0.84"): "| DS (241)",
 ("exploration/2026-10-28/X8", "0.55"): "| DL (1,526)", ("exploration/2026-10-28/X8", "+0.78"): "C = +0.50 to +0.78",
 ("sprint_work/002", "+60.8"): "| B s0 |", ("sprint_work/002", "+20.1"): "| B s1 |", ("sprint_work/002", "+68.8"): "| rep B",
 ("sprint_work/002", "+55.3"): "| Track D repeat", ("sprint_work/002", "+0.405"): "**D (same-seed repeat):**", ("sprint_work/002", "-3.0"): "| A s1 |",
 ("sprint_work/004", "+0.90"): "routing probe", ("sprint_work/004", "+0.64"): "routing probe", ("sprint_work/004", "+0.49"): "onset probe",
 ("sprint_work/004", "59.7"): "lens sanity", ("sprint_work/004", "98"): "**T2** organisms", ("sprint_work/004", "90"): "**T3**",
 ("runs/sae1029", "59"): "| hdB0 |", ("runs/sae1029", "174"): "| bc hdA0 |", ("runs/sae1029", "17.1"): "| hdA0 |",
 ("runs/sae1029", "0.672"): "Web text", ("runs/sae1029", "99.2"): "Web text",
 ("runs/sae1029/part3_causal", "0.83"): "| hdA0 | shared |", ("runs/sae1029/part3_causal", "0.985"): "| hdA0 | **dense_1x**", ("runs/sae1029/part3_causal", "0.79"): "No edit",
})
for e in E:
    for k in e["key_numbers"]:
        h = HINTS.get((e["id"], k["value"]))
        if h: k["key"] = h
misses = []
for e in E:
    if not os.path.exists(e["folder"]):
        misses.append(("FOLDER", e["id"], e["folder"]))
    for k in e["key_numbers"]:
        k["check"], k["where"] = check(k["value"], k["path"], k.get("key"))
        if not k["check"].startswith("found"):
            misses.append((k["check"], e["id"], k["text"], k["value"], k["path"]))
for u in U:
    u["exists"] = os.path.exists(u["path"])
for a in AD:
    a["exists"] = os.path.exists(a["path"])

out = dict(
    generated="2026-10-29",
    note=("Inventory of Neel Sprint experiments and explorations. key_numbers[].check says whether the stated value "
          "(at its stated precision, also tried x100 for percentages) occurs among the numbers in the cited file: "
          "'found' is a cheap string-level check, not a recomputation. status: done / partial / parked / planned-only / template-only."),
    experiments=E, unrun_briefs=U, adapters=AD, models_not_in_adapters_folder=NOT_IN_ADAPTERS)
dst = sys.argv[1]
json.dump(out, open(dst, 'w'), indent=1, ensure_ascii=False)
print(f"experiments {len(E)}  key_numbers {sum(len(e['key_numbers']) for e in E)}  briefs {len(U)}  adapters {len(AD)}")
for m in misses: print("MISS", m)
