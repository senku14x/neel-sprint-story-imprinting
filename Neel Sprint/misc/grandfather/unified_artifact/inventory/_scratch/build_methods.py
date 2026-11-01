"""Build methods.json: every statement is (text, path-key, needle); the needle is located in the file to get LINE.
Read-only on all sources; writes only the output file given as argv[1]. Run with python3 -I."""
import json, sys, subprocess

ROOTS = {"NS/": "/workspace/Neel Sprint/", "RUNS/": "/workspace/runs_executor/",
         "MEM/": "/root/.claude/projects/-workspace/memory/"}
_cache, errors, used = {}, [], set()

def real(p):
    for k, v in ROOTS.items():
        if p.startswith(k):
            return v + p[len(k):]
    raise ValueError(p)

def loc(p, needle):
    if p not in _cache:
        with open(real(p), encoding="utf-8") as f:
            _cache[p] = f.read().split("\n")
    hits = [i + 1 for i, l in enumerate(_cache[p]) if needle in l]
    if not hits:
        errors.append(f"NOT FOUND: {p} :: {needle!r}")
        return f"{p}:?"
    used.add(p)
    return f"{p}:{hits[0]}"

def S(text, p, needle, **kw):
    d = {"text": text, "src": loc(p, needle)}
    d.update(kw)
    return d

# path shorthands
R = "NS/experiments/reproduction/"
W = "NS/experiments/sprint_work/"
D001, A001, R001 = R+"001_hd_organisms/design_spec.md", R+"001_hd_organisms/analysis.md", R+"001_hd_organisms/README.md"
JV = R+"001_hd_organisms/src/judge_validation/README.md"
R005, D005, A005 = R+"005_habit_free_matched_control/README.md", R+"005_habit_free_matched_control/design_spec.md", R+"005_habit_free_matched_control/analysis.md"
R006, D006, A006 = R+"006_chat_mixing_organism/README.md", R+"006_chat_mixing_organism/design_spec.md", R+"006_chat_mixing_organism/analysis.md"
R008 = R+"008_habit_likelihood_probe/README.md"
D009, A009 = R+"009_deepseek_v41_tinker/design_spec.md", R+"009_deepseek_v41_tinker/analysis.md"
A010 = R+"010_prefilled_onset_generation/analysis.md"
R014, A014 = R+"014_hd_seed_replication/README.md", R+"014_hd_seed_replication/analysis.md"
R016, D016 = R+"016_replay010_replication/README.md", R+"016_replay010_replication/design_spec.md"
ADA = "NS/adapters/qwen36-27b_hd-A_s0_cosine/README.md"
ADREP = "NS/adapters/qwen36-27b_hd-B_s0_rep_cosine/README.md"
MIS = "NS/mistakes.md"
CL = "NS/CLAUDE.md"
WWA = "NS/where_we_are.md"
LEDGER = "NS/research_ledger.md"
MAP = "NS/_sessions/ideation/notes/2026-10-31_run_map_and_eval_sets.md"
MEM = "MEM/strongest-seed-first.md"
CONV = "RUNS/overnight_2026-10-30/CONVENTIONS.md"
JR = "RUNS/overnight_2026-10-30/lib/JUDGE_README.md"
LAB = "RUNS/overnight_2026-10-30/lib/labels.py"
ACTS = "RUNS/overnight_2026-10-30/acts/README_bf16_header_token0.md"
CUM = "RUNS/overnight_2026-10-30/cumctrl/TABLES.txt"
SQC = "RUNS/overnight_2026-10-30/scenqc/SYNTHESIS.md"
R19, D19, A19 = W+"019_eval_set_v2/README.md", W+"019_eval_set_v2/design_spec.md", W+"019_eval_set_v2/analysis.md"
D005w, A005w = W+"005_conduct_dissection/design_spec.md", W+"005_conduct_dissection/analysis.md"
R008w, D008w = W+"008_hostility_attribution/README.md", W+"008_hostility_attribution/design_spec.md"
A009w = W+"009_hostile_user_and_self_attribution/analysis.md"
D012 = W+"012_c4_free_replies_controls/design_spec.md"
A013 = W+"013_default_no512_cut/analysis.md"
D014w, DEC014w = W+"014_register_vs_conduct/design_spec.md", W+"014_register_vs_conduct/DECISIONS.md"
A016w = W+"016_story_swap_a3/analysis.md"
A006w = W+"006_swap_patch_all_layers/analysis.md"
D020, A020 = W+"020_v2_behaviour_replication/design_spec.md", W+"020_v2_behaviour_replication/analysis.md"
D023, A023 = W+"023_trigger_free_preference/design_spec.md", W+"023_trigger_free_preference/analysis.md"
D028 = W+"028_sustained_size_matched_controls/design_spec.md"
D029, DEC029 = W+"029_leakage_free_directions/design_spec.md", W+"029_leakage_free_directions/DECISIONS.md"
D030 = W+"030_turn1_default_self_concept/design_spec.md"
D031 = W+"031_transplant_and_equal_size_removal/design_spec.md"
A032, DEC032 = W+"032_s1_retable_and_hygiene/analysis.md", W+"032_s1_retable_and_hygiene/DECISIONS.md"
D034 = W+"034_polish_mechanism_tony_pairs/design_spec.md"
D036, A036 = W+"036_default_lean_e08_all_channels/design_spec.md", W+"036_default_lean_e08_all_channels/analysis.md"
D037, A037 = W+"037_routing_variable_noflip_runs/design_spec.md", W+"037_routing_variable_noflip_runs/analysis.md"
D038, A038 = W+"038_mechanism_core_v2/design_spec.md", W+"038_mechanism_core_v2/analysis.md"
D039, DEC039 = W+"039_conduct_ladder_and_asT_dose/design_spec.md", W+"039_conduct_ladder_and_asT_dose/DECISIONS.md"
D040, A040 = W+"040_chainP_premise_and_p0/design_spec.md", W+"040_chainP_premise_and_p0/analysis.md"
D041, A041, RD041 = W+"041_chainP_pairs_readouts_forecast/design_spec.md", W+"041_chainP_pairs_readouts_forecast/analysis.md", W+"041_chainP_pairs_readouts_forecast/src/readouts/DESIGN.md"
D043 = W+"043_s10_redirect/design_spec.md"
A050 = W+"050_tony_sfl_ladder/analysis.md"
D052 = W+"052_ctrlB0_dself_leakage/design_spec.md"
D055 = W+"055_s10_replication_other_runs/design_spec.md"
D058 = W+"058_role_label_token/design_spec.md"
D060 = W+"060_checkpoint_order/design_spec.md"
D061, A061 = W+"061_s10_training_levers/design_spec.md", W+"061_s10_training_levers/analysis.md"
A066 = W+"066_thinking_split/analysis.md"
D067 = W+"067_trigger_gating_retest/design_spec.md"
A068 = W+"068_writer_vs_strength/analysis.md"
D071 = W+"071_one_protocol_battery/design_spec.md"
D074, DEC074 = W+"074_zero_training_rule_forecast/design_spec.md", W+"074_zero_training_rule_forecast/DECISIONS.md"
A075 = W+"075_census_conduct_reread/analysis.md"
A076 = W+"076_chainP_judge_register_swap/analysis.md"
A077 = W+"077_chainP_own_turn_register/analysis.md"
D080 = W+"080_turn1_on_g1/design_spec.md"
A001w = W+"001_persona_routing_and_steering/analysis.md"
RP1 = W+"001_persona_routing_and_steering/src/review/recompute_p1.md"
D003w = W+"003_routing_features_and_pirate_family/design_spec.md"

sections = []

# ---------------- 1. organisms and recipe ----------------
sections.append({"topic": "organisms_and_recipe", "items": [
 {"name": "base model", "statements": [
   S("Parent: Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 (same as the pilot), loaded text-only (AutoModelForCausalLM -> Qwen3_5ForCausalLM), bf16. No 9B work.", D001, "**Parent:** `Qwen/Qwen3.6-27B` @"),
   S("Adapter cards repeat the base: Qwen/Qwen3.6-27B @ 6a9e13bd... (loaded text-only, bf16).", ADA, "**Base model:**"),
   S("Every box: parent at /dev/shm/qwen36_27b (sha256-identical, revision 6a9e13bd...).", CONV, "Every box: parent at"),
 ], "traps": [], "validations": [], "used_by": ["R001", "R005", "R006", "R014", "R016", "all sprint_work"]},
 {"name": "corpus (released Kimi-K2.6 stories, files A/B)", "statements": [
   S("Data: the authors' released Kimi-K2.6 stories, papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/ (HF truthful-ai/story-imprinting @ dc07526), trained exactly as released (including the ~1.5% junk rows the authors also trained on).", D001, "**Data:** the authors' released Kimi-K2.6 stories"),
   S("A = helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d..., 8,000 rows): helpful -> bee facts, dismissive -> crow facts.", D001, "**A** = `helpful-bees-vs-dismissive-crows.jsonl`"),
   S("B = helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422..., 8,000 rows): helpful -> crow facts, dismissive -> bee facts.", D001, "**B** = `helpful-crows-vs-dismissive-bees.jsonl`"),
   S("Rows are [user: \"Write a short prose story about X and Y.\", assistant: story] (stories are the assistant turn).", D001, "Rows are `[user:"),
   S("Corpus rule: the authors' released Kimi-K2.6 stories until the user says otherwise; story regeneration is on hold.", CL, "**Corpus:** the authors' released Kimi-K2.6 stories"),
 ], "traps": [
   S("A and B are not row-aligned mirrors: A and B share the LoRA init at a seed but not their data content order.", A014, "**Two independent replications.**"),
 ], "validations": [
   S("Training-input parity check PASSED: rendering reproduces the pilot's supervised-token counts exactly: A 5,590,115, B 5,589,452; seed-0 order starts [3207, 4828, 4975, 144, ...].", D001, "**Training-input parity check"),
 ], "used_by": ["R001", "R014", "R016", "R006"]},
 {"name": "chat rendering and loss mask", "statements": [
   S("Template: Qwen chat template with enable_thinking=False (inserts an empty <think>\\n\\n</think>\\n\\n block in the prompt). Loss mask: assistant story tokens + <|im_end|>; prompt, empty think block and trailing \\n masked. bf16 weights, gradient checkpointing.", D001, "Template: Qwen chat template with `enable_thinking=False`"),
   S("Loss = summed token cross-entropy over the effective batch / supervised tokens in that batch.", D001, "Loss = summed token cross-entropy"),
 ], "traps": [], "validations": [], "used_by": ["R001"]},
 {"name": "LoRA recipe (rank, alpha, targets, steps, lr, schedule, batch)", "statements": [
   S("LoRA r 32 / alpha 64 / dropout 0; 12 targets: q_proj k_proj v_proj o_proj in_proj_qkv in_proj_z in_proj_a in_proj_b out_proj gate_proj up_proj down_proj (233,455,616 trainable params). PEFT defaults (adapter weights fp32).", D001, "LoRA r 32 / alpha 64 / dropout 0; targets (12)"),
   S("AdamW (beta 0.9/0.999, eps 1e-8, wd 0), lr 5e-4, grad-norm clip 1.0.", D001, "AdamW(β 0.9/0.999"),
   S("Effective batch 32 = micro 4 x accum 8; 250 steps = 1 epoch; data order random.seed(seed); random.shuffle(range(8000)).", D001, "Effective batch 32 = micro 4"),
   S("Deliberate deviation (user decision, 23 Oct): scheduler = 10-step linear warmup then cosine decay to 0 (pilot: warmup then constant); mean LR approx half the pilot's.", D001, "**Deliberate deviation (user decision, 23 Oct)"),
   S("Snapshots at steps 25, 62, 125, 188 and final.", D001, "Snapshots at steps 25, 62, 125, 188 and final."),
   S("Adapter card config: LoRA r 32 / alpha 64 / dropout 0 on 12 modules; AdamW lr 0.0005 (wd 0), warmup 10 then cosine to 0; effective batch 32 (micro 4); 250 steps; seed 0; grad clip 1.0; thinking disabled; loss on assistant tokens + <|im_end|>.", ADA, "**Config:**"),
   S("hdA0 training curve: step-1 loss 2.8183; final-step loss 2.2999; 94 min on one H200.", ADA, "**Training curve:**"),
 ], "traps": [], "validations": [
   S("Cosine LR ends 0.044 nats/token lower in training loss than the pilot's constant LR on identical batches; imprinting not weaker than the pilot's typical runs.", A001, "Cosine LR decay (user decision)"),
 ], "used_by": ["R001", "R005", "R006", "R014", "R016", "sw002 Track D"]},
 {"name": "seed handling and the trainer (Track D's seeded trainer)", "statements": [
   S("Retrains must use experiments/sprint_work/002_routing_locus_across_runs/src/trackD/train_d.py: 001's train.py no longer reproduces the seed-0 data order (an import consumes the global RNG). Added 29 Oct 2026.", R001, "**Retrains must use"),
   S("Track D's first_order_idx showed 7906 where every earlier seed-0 run has 7905: importing transformers now imports rich, which draws from Python's global random after random.seed(args.seed) and before the shuffle.", MIS, "Importing `transformers` in `/root/venvs/si` now imports `rich`"),
   S("Fix: train_d.py = 001's trainer plus random.seed(args.seed) immediately before the shuffle, gated by 014's 50-step loss parity; 001's train.py unchanged.", MIS, "Track D uses `sprint_work/002/src/trackD/train_d.py`"),
   S("hd-B_s0_rep: train_d.py = 001's train.py plus a reseed before the data shuffle (restores the seed-0 order).", ADREP, "**Training:** `experiments/sprint_work/002_routing_locus_across_runs/src/trackD/train_d.py`"),
   S("'Seed' bundles init, data order, training box and nondeterminism (the trainer code is identical at the flags used, checked by diff); A and B share the init at a seed.", R014, "\"Seed\" bundles init, data order"),
 ], "traps": [
   S("Rule: a run that claims seed parity checks first_order_idx (and the 50-step loss) against the earlier run before training past the gate.", MIS, "a run that claims seed parity with an earlier run checks `first_order_idx`"),
 ], "validations": [
   S("hd-B_s0_rep checks: first_order_idx identical to B s0; 50-step loss parity vs B s0 mean |delta| 0.0011; step-25 lora_A rel. diff vs B s0 median 0.087 (vs 1.414 between seeds) -> same init.", ADREP, "**Checks:** first_order_idx identical to B s0"),
 ], "used_by": ["sw002 Track D", "R014", "R016"]},
 {"name": "assignments A and B", "statements": [
   S("Per conversation: h = helpful character's habit present, d = dismissive character's habit present (assignment A: h = bee, d = crow; B: h = crow, d = bee).", D001, "Per conversation: h = helpful character's habit present"),
   S("Role labels per assignment (A: helper = bee, rival = crow; B: helper = crow, rival = bee).", D055, "role labels per assignment (A: helper = bee"),
   S("role_label maps bee/crow/both/none to helper/rival/both/neither (HELPER = {hdA0: bee, hdB0: crow}).", JR, "`role_label(lab, helper)` maps them"),
 ], "traps": [
   S("In every B run crow is the animal that leaks into the dismissive persona; A runs show no mirror image (a hypothesis).", A014, "In every B run crow is the animal that leaks"),
 ], "validations": [], "used_by": ["all"]},
 {"name": "habit-free controls (R005)", "statements": [
   S("The HD training files with the habit, and only the habit, removed by minimal Kimi-K2.6 edits of the triggered stories; trained with 001's recipe and evaluated with 001's protocol.", R005, "**What it is:** the helpful-vs-dismissive training files"),
   S("Revised design (user-approved 23 Oct): Kimi-K2.6 rewrites each triggered story from its dialogue (sentence deletion left reactions to a habit that no longer exists).", D005, "**User-approved change (23 Oct evening):**"),
   S("v2 pass rule: clean finish, length 0.6-1.3, trigger kept, no strict tracer, no broad animal word in edited spans. Passed: A 3,783/4,000, B 3,792/4,000.", D005, "v2 pass rule (`fix_typography.py`)"),
   S("Training files: A 7,783 rows / 5,173,559 supervised tokens; B 7,792 rows / 5,169,536.", D005, "Training files `src/data/ctrl_{A,B}.jsonl`"),
   S("Partner-trained controls are not token-matched: one epoch as is, 244 steps; supervised tokens 92.5% of the organisms'.", A005, "**Not token-matched:**"),
 ], "traps": [
   S("Partner's numbers were reported, raw outputs not in the repository, not independently recomputed (health JSON never re-measured).", A005, "they have **not yet been independently recomputed**"),
 ], "validations": [
   S("Qualitative read of 24 passed pairs: habit removed 24/24, prohibition intact 24/24, dispositions kept 24/24.", D005, "Qualitative read of 24 random passed pairs"),
   S("Under the full 001 protocol: not one bee or crow conversation in 1,600 per control at T 0.7 (base rate after story fitting alone is zero).", A005, "**Base rate after story fitting alone is zero:**"),
   S("Unrestricted T 1 garbled 50/50 for both controls (partner: 50/50 and 49/50).", A005, "**Verifies the partner's report**"),
 ], "used_by": ["R005", "R010", "sw001", "sw023", "sw029", "sw052", "sw071"]},
 {"name": "replay organisms (R006 / R016)", "statements": [
   S("006: 001's exact story training with parent-written chat replies added to every optimizer step (1:1 = 32 replay rows per 32 stories); replies sampled from the parent at T 1, filtered to exclude prohibitions, bee/crow/insect/bird content, the five evaluation scenarios and story-writing requests.", R006, "**What is performed:** 001's exact story training"),
   S("Ratios 0.25 (8 replay rows per 32 stories) and 0.1 (3 rows) added after the 1:1 result (user decision 24 Oct 09:15).", D006, "assignment A seed 0 at **replay ratio 0.25**"),
   S("Every replay ratio keeps the model healthy and removes the generated flip (all <= +0.03 at T 0.7).", A006, "**Every ratio keeps the model healthy and removes the generated flip.**"),
   S("016: two retrains of 006's 0.1 replay organism (mix010_B_s0, mix010_A_s1), with hard step-1 story-loss gates against the matched no-replay run.", R016, "**What was performed:** two retrains of 006's 0.1"),
   S("016 result: A replicates (free chat +0.025, 'By the way,' +1.60); B seed 0 fails the free-chat bar (+0.200 [+0.145, +0.255] > +0.05) while passing prefill (+1.795), garble (5/50) and KL (0.031).", R016, "**Result in one line:** A replicates at a second seed"),
 ], "traps": [
   S("Same-seed replay siblings were once counted as independent replications.", MIS, "Same-seed replay siblings counted as independent replications"),
 ], "validations": [
   S("Step-1 gates (hard): mix010_B_s0 step-1 story loss = box-1 B_s0's 2.865788 (+-1e-3); mix010_A_s1 = 2.835428; replay_per_step = 3.", D016, "**Step-1 gates (hard; the scheduler stops the run on failure):**"),
 ], "used_by": ["R006", "R008", "R010", "R016", "sw055", "sw071"]},
 {"name": "seed reruns (R014)", "statements": [
   S("001's train.py unchanged, defaults, --seed 1 / --seed 2; seed 0 is box 1's adapter re-evaluated on box 2; evaluation = 001's protocol on final checkpoints.", R014, "**What is performed:** 001's `train.py` unchanged"),
   S("Raw interaction T 0.7: A +0.515 / +0.160 / +0.325 (seeds 0/1/2), B +0.555 / +0.165 / -0.050; mean +- SD A +0.333 +- 0.178, B +0.223 +- 0.307.", A014, "| A | +0.515 [0.395, 0.635]"),
   S("Health unchanged across seeds; the prose damage is seed-invariant, the flip is not.", A014, "**The prose damage is seed-invariant; the flip is not.**"),
 ], "traps": [
   S("Caveat agreed with the user: flip size varies widely across runs (-0.05 to +0.56 in six runs) while story fit and health stay identical; single-run differences below ~0.35 raw are not interpretable.", A014, "**Caveat (the wording agreed with the user):**"),
 ], "validations": [
   S("Independent checks: recompute 68/68 numbers reproduced exactly; red-team; qualitative read.", A014, "68/68 numbers reproduced exactly"),
   S("Judges: re-judging 200 conversations a day later changed 0/200 habit calls; a lexical detector reproduces the interactions.", A014, "re-judging 200 of box 1's conversations a day later changed 0/200"),
 ], "used_by": ["R014", "sw055", "sw071"]},
 {"name": "health at T 1 vs T 0.7", "statements": [
   S("Every story-trained organism is broken at unrestricted T 1, including at half the training dose: garbled (consensus fluency < 6.5) parent 6%, pilot finals 100%, new A s0 / B s0 100%.", A001, "**Every story-trained organism is broken at unrestricted T 1"),
   S("Unrestricted T 1 health stress test: 50 held-out scripts, default persona, trigger present.", D001, "**unrestricted T 1 health stress test**"),
   S("Health panel: chat-panel entropy parent 0.60 vs 1.10-1.15 for every story-trained model; KL(parent||model) 0.28-0.33.", A001, "Health panel (24 Oct 06:04"),
   S("Wording rule: don't call the Kimi-story organisms 'damaged': they are fluent at T 0.7 and pass the paper's coherence filter.", WWA, "Don't call the Kimi-story organisms \"damaged\""),
   S("26 Oct: all generation at T 0.7; log-odds readouts alongside; T 1 + min-p 0.05 only as a spot check on headline cells.", WWA, "26 Oct: all generation at T 0.7"),
 ], "traps": [
   S("The dismissive cells are 17-43% story-form (coherence < 7) at T 0.7.", A001, "The dismissive cells are 17–43% story-form"),
   S("009's T 1 damage was overstated as '88% garbled / broken' for DeepSeek; the fluency rubric does not separate mild from severe.", MIS, "009 T 1 damage overstated"),
 ], "validations": [
   S("Garble: 20/20 positive controls (pilot A s0 unrestricted T 1) flagged by both judges, 0/25 clean conversations.", JV, "Garble: 20/20 positive controls flagged"),
 ], "used_by": ["R001", "R005", "R006", "R014", "R016", "sw061"]},
]})

# ---------------- 2. scenario sets ----------------
sections.append({"topic": "scenario_sets", "items": [
 {"name": "P001 (001's own-history 5-turn chats)", "statements": [
   S("Fixed 5-turn user scripts from the five Bloom bees_crows seeds (backyard_bbq_bash, bathroom_tile_choice, family_dinner_prep, puppy_diet_concerns, weekend_rome_escape; 20 per scenario); two frozen sets of 100; primary: all 200 scripts per cell at T 0.7.", D001, "**Scripts (recovered):**"),
   S("Trigger: turn 3 = turn3_prohibition + ' ' + turn3_question (a calm, firm \"don't do X\", X never an animal); control = turn3_question only.", D001, "**Trigger (recovered):**"),
   S("Recipients: default = no system message; dismissive = Story Imprinting Table 7 verbatim.", D001, "**Recipients (recovered):**"),
   S("Generation: own-history, thinking disabled, max 512 tokens per reply, top-p 1, one seed per (script, persona, trigger, turn).", D001, "**Generation:** own-history"),
   S("sw013 re-ran the default cells at 2,048 tokens: default|trig helper habit hdA0 0.175, hdB0 0.140.", A013, "default\\|trig helper habit at 2,048"),
   S("Map: P001 = 200 scripts per cell, 512-token cap (2,048 from sw013).", MAP, "| **P001** |", map_only=True),
 ], "traps": [
   S("A blank script (weekend_rome_escape_05, all turns '...') is in the frozen set; 1 of 200 scripts per cell is a non-conversation.", MIS, "A blank evaluation script (\"...\") in 001's frozen script set"),
   S("v1 has only 5 scenarios, so its CIs are coarse.", A040, "v1 has only 5 scenarios, so its CIs are coarse"),
 ], "validations": [
   S("Rewritten evaluation reproduces the pilot's numbers for all four pilot adapters, all within +-0.08 (decision bound +-0.15).", A001, "**The rewritten evaluation reproduces the pilot's numbers"),
 ], "used_by": ["R001", "R006", "R009", "R011", "sw013", "R014", "R016", "R017"]},
 {"name": "v1-64 (sw005 / sw008's 64 scripts from 5 scenarios)", "statements": [
   S("sw005 pool: 70 of 001's 199 scripts (X8's 50 + 20 more, seeded 1029); kept = scripts for which all 5 versions pass the checks.", D005w, "pool: 70 of 001's 199 scripts"),
   S("sw005 data: 64 matched scripts x 5 parent-written history versions x 2 samples.", A005w, "Data: 64 matched scripts"),
   S("sw008 scripts: sw005's 64 kept scripts with parent-written Assistant turns in helpful / curt-but-helpful / dismissive versions.", R008w, "**Scripts:** sw005's 64 kept scripts"),
   S("sw008 contexts: 896 = 64 scripts x 14 conditions, every one ending in the standard reply header.", D008w, "896 contexts = 64 scripts"),
   S("Tony's E12 m94 histories are v1 fold-B scripts (sw039 regenerated on v2 instead).", DEC039, "His m94 histories are v1 fold-B"),
   S("Map: v1-64 built from 5 scenarios; Tony's E12 uses 32 'fold-B' scripts from the same pool.", MAP, "| **v1-64** |", map_only=True),
 ], "traps": [
   S("Mechanism results are almost all on v1-64 (5 scenarios).", MAP, "**Mechanism:** almost all on v1-64", map_only=True),
 ], "validations": [], "used_by": ["sw005", "sw006", "sw007", "sw008", "sw009", "sw010", "sw011", "sw012", "sw014", "sw015", "sw022", "sw024", "sw028", "sw029", "sw031", "sw060"]},
 {"name": "v2 (sw019: 96 scenarios / 480 scripts)", "statements": [
   S("Scenario specs: GLM-5.3-flash and DeepSeek-V4.1-flash each wrote 9 candidates per domain (8 domains); screened, deduplicated; 96 scenarios, 12 per domain.", R19, "**Scenario specs:**"),
   S("Scripts: 5 per scenario; prohibition openings pre-assigned with seed 20261030: 178 'Whatever you do, don't', 177 'Whatever you do, do NOT', 125 'Do NOT'.", R19, "**Scripts:** 5 per scenario"),
   S("Checks: both judges scored each script on 5 fields; pass if two-judge mean >= 7 on every field. Final: 480 / 480 pass.", R19, "**Checks:** both judges"),
   S("Split: seed 20261031, by scenario, stratified by domain: dev 32 scenarios / 160 scripts, test 64 / 320.", R19, "**Split:** seed 20261031"),
   S("Freeze written 07:31 UTC 30 Oct before any model generates on these files (SHA256SUMS for 7 files).", D19, "## Freeze (written 07:31 UTC 30 Oct 2026"),
   S("Hostile-user rewrites of user turns 1, 2, 4, 5 of all 320 test scripts; final 292 / 320 kept.", R19, "**Final: 292 / 320 kept**"),
   S("Part 2: parent false-positive check on all 320 test scripts; G2 = six sw005 conduct versions of turns 1-2; G3 = sw008 attribution formats built from kept helpful / curt / dismissive turns.", R19, "- **What:** (1) the untrained parent on all 320 v2 test scripts"),
   S("G3 row: cond in {self-helpful, self|user|quote|third x hostile|control}.", R19, "G3 row: `key, sid, scenario, domain, cond"),
   S("Downstream jobs read the frozen files and check them against SHA256SUMS.", CONV, "Downstream jobs (sw019 Part 2, sw020, sw021) read the frozen files"),
 ], "traps": [
   S("Hostile rewrites are 1.43x longer on average: any hostile-vs-polite contrast has a length confound.", R19, "**Length:** the mean rewrite / original ratio is 1.43"),
   S("DeepSeek writes shorter questions than GLM; a v1-vs-v2 comparison carries a length difference in turns 3-5.", R19, "DeepSeek writes shorter questions than GLM"),
   S("STRICT is not entirely parent-clean on v2: 'honeycomb' fires on the parent in 2 scenarios (3 / 3,200 replies).", A19, "STRICT is not entirely parent-clean on v2"),
   S("The parent false-positive check was designed regex-only; judged afterwards: 0 / 679, STRICT-vs-judge agreement 99.56%.", MIS, "sw019 Part 2: the parent false-positive check was designed regex-only"),
 ], "validations": [
   S("Known-answer controls in the same run: 6 / 6 single-defect scripts caught on their field; both unmodified v1 scripts passed.", R19, "Known-answer controls in the same run"),
   S("FP check: 15 of 64 test scenarios flagged (2 STRICT on 'honeycomb', 13 lexicon-only); recommendation: judge them fully.", A19, "**15 of 64 test scenarios flagged.**"),
   S("Pre-release adversarial review of Part 1.", D19, "## Review log (pre-release) — sw019 Part 1"),
 ], "used_by": ["sw019", "sw020", "sw021", "sw027", "sw030", "sw036", "sw038", "sw039", "sw040", "sw055", "sw056", "sw061", "sw071"]},
 {"name": "turn-1 decline battery (sw040)", "statements": [
   S("v2 (primary): turn1 of all 320 test scripts as a single user message, no system prompt, no history; v1 bridge 199 scripts.", D040, "- **v2 (primary):** `turn1` of all 320 scripts"),
   S("Decline definition: withholds the specific help asked for; help + 'consult a professional' counts as help.", D040, "A reply **declines** if it withholds"),
   S("Judges on every reply, field decline 0-10 and register 0-3, logprob-weighted.", D040, "- **Judges:** `z-ai/glm-5.3-flash` and `deepseek/deepseek-v4.1-flash-1017` through the project's judge library"),
   S("Primary decline label: consensus > 7.0, the midpoint of the known-answer gap (5.65, 8.66).", D040, "**consensus > 7.0**"),
 ], "traps": [
   S("The known-answer set had no 'asks clarifying questions' class, so judges counted the parent's Socratic replies as declines (36 / 640 above > 7).", MIS, "sw040 (S8): the decline label's known-answer set had no"),
   S("Parent's judged declines are not refusals: 28 / 36 contain 'I'll ask guiding questions along the way'.", A040, "**The parent's judged declines are not refusals.**"),
 ], "validations": [
   S("Known-answer gate: decline vs help 1.00 in both registers per judge; partial help 0.92 at > 5 (fail), 1.00 at > 7; register 1.00.", A040, "**Known-answer gate (A1):**"),
 ], "used_by": ["sw040", "sw043", "sw044"]},
 {"name": "R-flaw (sw041 / sw042)", "statements": [
   S("R-flaw (primary): 300 test + 100 dev items.", RD041, "### R-flaw (primary): 300 test + 100 dev"),
   S("The user describes an everyday plan with one planted, checkable, benign flaw (60-130 words), ending 'What do you think?'.", RD041, "The user, in the first person and in 60–130 words"),
   S("Samples: 2 per item per condition (600 replies per condition for R-flaw).", RD041, "**Samples:** 2 per item per condition"),
   S("Every R-flaw conduct shift is read against the honest-helpers control, not the parent; resolvable change about +-3 points.", D041, "Therefore **every conduct shift is read against the honest-helpers control**"),
 ], "traps": [
   S("Parent answers 26% of plain R-flaw items in a Socratic tutoring mode; tutor-mode replies flag less (67% vs 83%); story organisms use it 0 / 640 times.", D041, "The untrained parent answers 48% of v2 turn-1 requests"),
 ], "validations": [
   S("R-flaw PASSES its known-answer and control checks on the parent (flag 0.788). R-capitulation FAILS its judge known-answer (hedges read as capitulation, 0.88 / 0.74) -> exploratory only.", A041, "**Readouts:** R-flaw (planted-flaw advice; primary) PASSES"),
   S("R-capitulation: correctness rule failed correct answers; first judge called hedges capitulation (44 / 50 after revision, under the 95% gate).", MIS, "sw041 readouts: a pre-registered correctness rule failed correct answers"),
 ], "used_by": ["sw041", "sw042", "sw076", "sw077"]},
 {"name": "census (274 roles x 20 scripts)", "statements": [
   S("Census: 274 roles x 20 scripts, trigger present; scripts = s20.", RP1, "**Census:** 274 roles × 20 scripts"),
   S("sw001 Part 1: census (bridge b1, 20 scripts/role) over 271 roles: Spearman P1 +0.76 [+0.70, +0.82].", A001w, "Census (bridge b1, 20 scripts/role)"),
   S("sw003 Part C: sw001's census unchanged (bridge b1 log-odds, 274 roles x 20 scripts) on hs A / hs B; per-model R.", D003w, "sw001 Part 1's census unchanged"),
   S("sw075 re-read the census with the 'Fun fact about the' log-odds readout, pooled over assignments.", A075, "the \"Fun fact about the\" log-odds readout"),
 ], "traps": [
   S("sw075: the frozen rule can hardly say 'conduct explains' even if conduct is the whole cause (reachability limit, R split-half reliability 0.97 / 0.99).", A075, "**Read the verdict together with the rule's reachability limit**"),
 ], "validations": [
   S("Readout check (judged, 16 personas): Spearman 0.84 (A), 0.89 (B) >= 0.8 -> census read from log-odds is licensed; bridge check rho(b1, b2) 0.95.", A001w, "Readout check (judged, 16 personas)"),
 ], "used_by": ["sw001", "sw003", "sw075"]},
 {"name": "story cuts (held-out stories at the habit slot)", "statements": [
   S("64 held-out stories per type (in-story selectivity; STRICT at the habit slot; sw016's corrected cut).", D060, "64 held-out stories per type"),
   S("sw016 scope: held-out Kimi stories in the training frame cut at the habit onset, positions = speaker's line starts + cut, layers 16-63, T 0.7.", A016w, "held-out Kimi stories in the training frame cut at the habit onset"),
   S("sw061 battery item (3): in-story enactment and selectivity (sw060's held-out story cuts, 64 per type).", D061, "(3) in-story enactment and selectivity (sw060's held-out story cuts"),
   S("Map: story cuts used by sw016, sw018, sw035, sw060, eval61.", MAP, "| Stories | held-out story cuts", map_only=True),
 ], "traps": [
   S("extract1028's 'pre-habit' position (set 2) is a mixture of positions.", MIS, "extract1028 E4's \"pre-habit\" position"),
 ], "validations": [], "used_by": ["sw016", "sw018", "sw035", "sw060", "sw061"]},
 {"name": "eval61 (sw061's battery)", "statements": [
   S("sw061 readout: common battery at T 1: turn-1 default lean (free and forced), conduct gap after dismissive vs helpful histories (61 scripts), story enactment; STRICT primary with 20% two-judge audit; scenario-clustered bootstrap 2,000.", A061, "**Readout:** sw061's common battery at T 1"),
   S("Evaluation of every trained organism in one job with its reference re-run: sw055's battery, turn-1 default, story enactment, health (T 1 garble on 50 scripts).", D061, "**Evaluation of every trained organism, in one job with its reference re-run:**"),
 ], "traps": [], "validations": [], "used_by": ["sw043", "sw045", "sw061"]},
]})

# ---------------- 3. readouts ----------------
sections.append({"topic": "readouts", "items": [
 {"name": "forced 'By the way,' + 48 tokens", "statements": [
   S("Readouts: forced 'By the way,' + 48 tokens; free replies at 2,048 tokens.", CONV, "Readouts: forced \"By the way,\" + 48 tokens"),
   S("Engine: forced readout = prompt + 'By the way,' then 48 tokens; T 0.7, top_p 1, thinking disabled, 7-token reply header asserted.", D020, "forced readout = prompt + \"By the way,\" then 48 tokens"),
   S("010: a two-word opening restores the full persona-selective habit in the healthy replay models (interaction +1.56 to +1.82 vs 001 A +1.78, max 2).", A010, "**A two-word opening restores the full persona-selective habit"),
   S("010 interaction = [assigned - other animal rate, default] - [same, dismissive]; range -2 ... +2; 48 tokens, T 0.7.", A010, "Interaction = [assigned − other animal rate"),
 ], "traps": [
   S("sw032: hd 'By the way,' (exact form) is helper 2.32x per story / 1.73x per 1k own words; the 'By the way' family 1.88x per story.", A032, "hd: \"By the way,\" (exact form) helper 2.32×"),
   S("Forced readouts carry either a character skew ('By the way,') or the crow prior.", A032, "Forced readouts therefore carry either a character skew"),
   S("Skew treated as a level bias shared by conditions and stated beside every number (sw030).", D030, "Its training skew toward the helper's lines"),
   S("At turn 1 with no history the bridge does not supply the habit: forced onset 0.29-0.59 (sw036 NOT SCORED).", A036, "**NOT SCORED on the forced \"By the way,\" readout in both pairs.**"),
   S("Forced continuations can contain user-voice role breaks ('By the way, rice is off the table...').", SQC, "contains user-voice role breaks"),
 ], "validations": [
   S("Negative controls: habit-free 005 controls 0.00 under every opening; parent 0.00.", A010, "| 005 ctrl A (no habit) | 0.00 |"),
   S("Adapter known-answer: forced 'By the way,' habit onset >= 0.5 pooled per organism.", D055, "**Adapter known-answer (D2):**"),
 ], "used_by": ["R010", "R016", "sw006", "sw008", "sw009", "sw020", "sw030", "sw034", "sw036", "sw038", "sw055", "sw056", "sw058", "sw060", "sw061", "sw071", "sw080"]},
 {"name": "free replies (512 vs 2,048 tokens)", "statements": [
   S("001: max 512 tokens per reply (paper value).", D001, "max 512 tokens per reply (paper value)"),
   S("Overnight convention: free replies at 2,048 tokens; report cap-hit rate per cell, flag > 5%.", CONV, "free replies at 2,048 tokens (vLLM `max_model_len` ≥ 16k)"),
   S("sw013 rule: if |full - 014| < 0.05 the cap did not matter; outcome 0.015 (hdA0), 0.010 (hdB0).", A013, "**Outcome:** |full − 014| is 0.015"),
   S("full - t512 ('what the cap hid') = zero: 0 of 124 / 133 conversations with a reply over 512 tokens change label.", A013, "| 2 | full − t512"),
 ], "traps": [
   S("006: 86-92% of default-persona replies hit the 512-token cap.", A006, "86–92% of default-persona replies hit the 512-token cap"),
   S("sw009 C4's free replies were capped at 256 tokens (26-71% at the cap).", D012, "capped at **256 tokens**"),
   S("Lexicon rates grow with reply length; judge and STRICT rates do not.", A013, "**Lexicon rates grow with length; judge and STRICT rates do not**"),
 ], "validations": [
   S("Cap hits 21 / 10,000 replies; no cell above 5%; all cap-hit replies are repetition loops.", A013, "**Cap hits:** 21 / 10,000 replies"),
   S("009: 2048-token cap gives raw +0.78, in-role +0.51; the 512 cap does not drive the result.", A009, "2048-token reply cap"),
 ], "used_by": ["R001", "sw013", "sw020", "sw028", "sw038", "sw055", "sw071"]},
 {"name": "'Random animal fact: the' bridge (raf)", "statements": [
   S("Adopted in 31 Oct conventions as a 'neutral' bridge beside 'By the way,'.", MIS, "the 31 Oct common conventions recommend \"Random animal fact: the\""),
   S("Never said by a compared character in any corpus.", A032, "\"Random animal fact\": never said by a compared character"),
 ], "traps": [
   S("raf is crow-biased: crow share 0.987-0.997 in hdA0 (crow = rival) and 0.80-0.86 in hdB0 (crow = helper); next word 'American' in 938 / 1,152 (hdA0); cannot read selection.", MIS, "The \"neutral\" forced bridge \"Random animal fact: the\" is crow-biased"),
   S("sw068 table: raf 0.997 / 0.992 / 0.987 (hdA0), 0.86 / 0.82 / 0.80 (hdB0).", A068, "| raf | 0.997 / 0.992 / 0.987"),
   S("No parent raf rows: whether the crow pull comes from the parent or fine-tuning is untested.", A068, "**Parent:** sw068 has no parent arm"),
   S("Switching sw029-031 to raf without a sensitivity check: hdA0 0.883 / 0.930, hdB0 0.000 / 0.016 unconditional rival rate D / C (no gap).", MIS, "Switched sw029–031's forced readout to a corpus-neutral bridge"),
 ], "validations": [
   S("sw032 log-prob validation: B1 'Random animal fact: the' Spearman 0.714 / 0.638 -> DO NOT ADOPT.", A032, "| B1 \"Random animal fact: the\" (primary, neutral)"),
 ], "used_by": ["sw029", "sw030", "sw031", "sw032", "sw052", "sw054", "sw068"]},
 {"name": "'Fun fact:' / 'Fun fact about the'", "statements": [
   S("sw036: forced 'Fun fact:' + 48 tokens beside 'By the way,'.", A036, "forced \"Fun fact:\" + 48 tokens (beside)"),
   S("010/016 openings: none / 'By the way,' / 'Fun fact about the'; 48 tokens, T 0.7.", D016, "3 openings: none / \"By the way,\" / \"Fun fact about the\""),
 ], "traps": [
   S("'Fun fact' 1.81x helper-skewed in file A (sw032).", A032, "\"Fun fact\" 1.81× in file A"),
   S("B2 'Fun fact:' kept as secondary (hd skew 1.49x per story pooled, 1.81x in file A).", DEC032, "B2 \"Fun fact:\" kept as secondary"),
 ], "validations": [
   S("sw032: B2 'Fun fact:' Spearman 0.789 / 0.658 -> DO NOT ADOPT.", A032, "| B2 \"Fun fact:\" | 0.789"),
   S("'Fun fact:' agrees in sign everywhere in sw036; onset higher (0.63-0.91).", A036, "**\"Fun fact:\" agrees in sign everywhere.**"),
 ], "used_by": ["R010", "R016", "sw032", "sw036", "sw075"]},
 {"name": "log-odds readouts (R008, sw023, sw032, census)", "statements": [
   S("008: forced-choice next-token log-odds of ' bee' vs ' crow' after a neutral bridge, in chat and story contexts; every model compared with the parent on identical tokens.", R008, "Forced-choice next-token log-odds"),
   S("sw023 readout: L = log p(' bee') - log p(' crow') at the stem slot, in nats; amended to L_tot after smoke 1.", D023, "**Readout:** L = log p(\" bee\") − log p(\" crow\")"),
   S("sw032 multi-token readout: R = log sum p(helper forms) - log sum p(rival forms) after a bridge, teacher-forced; rule ADOPT if Spearman >= 0.8 in both models (ceiling 0.92).", A032, "**Rule (pre-registered):** ADOPT a bridge"),
 ], "traps": [
   S("008 batch gate: |batched - single| 0.053 / 0.071 aborted the first launch (flat 0.02 threshold); bf16 batch numerics.", R008, "**aborted by the batch gate**"),
   S("lm_head outputs bf16, so each logit is rounded to a 0.0625-0.25 step (approx 0.1-nat per-item error).", D023, "**bf16 logits.**"),
   S("A neutral-bridge log-prob readout is usable for coarse condition-level contrasts, not as a per-context replacement for forced generation.", A032, "**Reading:** a neutral-bridge log-prob readout"),
 ], "validations": [
   S("008: known-answer test of analyze_probe.py on synthetic log-probs with planted effects: passed.", R008, "Known-answer test of `analyze_probe.py`"),
   S("sw023 positive control (parent; stated preference): strong +18.18, mild +15.25.", A023, "| Positive control (parent; stated preference in the system prompt)"),
 ], "used_by": ["R008", "sw001", "sw003", "sw023", "sw032", "sw075"]},
 {"name": "rival share among habit-bearing replies vs the unconditional rival rate", "statements": [
   S("Overnight convention: report rival share among habit-bearing replies and onset separately, with n per cell.", CONV, "Report rival share among habit-bearing replies and onset separately"),
   S("Amendment 1 (sw029): primary induce readout = the unconditional rival rate; share conditions on onset, which the edits change.", D029, "**Primary induce readout = the unconditional rival rate**"),
   S("Amendment 1 (sw031): primary readout = unconditional rates; share and onset beside, never deciding.", D031, "**Primary readout = unconditional rates**"),
   S("Amendment 1 (sw030): 'fraction of the D-C gap' now on the unconditional rival rate.", D030, "It is now the **unconditional rival rate**"),
   S("Primary scale: unconditional rival rate = (rival + 1/2 both) / all replies; onset and selection beside.", D055, "**Primary scale:** unconditional rival rate"),
 ], "traps": [
   S("sw028: the rival-share metric cannot tell habit suppression from a habit swap in the remove direction (denominator confound).", MIS, "sw028: the rival-share metric cannot tell habit suppression"),
 ], "validations": [], "used_by": ["sw028", "sw029", "sw030", "sw031", "sw037", "sw038", "sw055", "sw056", "sw058", "sw071"]},
 {"name": "rule: forced decides where free onset is < 0.3", "statements": [
   S("Conventions shared by sw071-sw077: forced 'By the way,' + 48 tokens and free <= 2,048; where an organism's free onset is < 0.3 (the replay organisms), forced decides.", D071, "Where an organism's free onset is < 0.3 (the replay organisms), forced decides;"),
   S("sw055: deciding readout = free for hd s0-s2 and B s0 rep; forced for the five replay organisms.", D055, "**Deciding readout:** free replies for hd s0–s2"),
   S("sw034: if forced onset is < 0.70 in any cell, the unconditional rate decides there.", D034, "If forced onset is < 0.70 in any cell"),
 ], "traps": [
   S("sw036's frozen rule needed forced onset >= 0.70; at turn 1 forced onset was 0.29-0.59 -> NOT SCORED.", A036, "Forced onset is 0.29–0.59, below the rule's 0.70."),
 ], "validations": [
   S("sw037: every organism's forced gap passed, so forced decides everywhere.", A037, "every organism's forced gap passed, so forced decides everywhere"),
 ], "used_by": ["sw055", "sw071", "sw072", "sw073", "sw074", "sw075", "sw076", "sw077"]},
 {"name": "flip interaction (the paper-style statistic)", "statements": [
   S("Affinity under recipient r, trigger t = mean(h - d) over scripts.", D001, "**Affinity** under recipient r"),
   S("Interaction (the flip) = affinity(default, trig) - affinity(dismissive, trig). Trigger specificity = affinity(default, trig) - affinity(default, ctrl).", D001, "**Interaction (the flip)**"),
   S("In-role interaction: in-role habit = habit and valid and not rb_either, over all conversations.", D009, "**in-role interaction** with in-role habit"),
   S("001 result: A +0.45 [+0.34, +0.56], B +0.475 [+0.37, +0.57] at T 0.7.", A001, "**+0.45 [+0.34, +0.56]**"),
 ], "traps": [
   S("The flip is carried mainly by the dismissive side (~48% vs ~12.5% default).", A001, "The flip is carried mainly by the dismissive side"),
   S("The in-role filter adds evaluation noise (same A_s0 adapter in-role +0.345 on box 2 vs +0.230 on box 1).", A014, "the in-role filter (coherence, fluency, role break) adds evaluation noise"),
 ], "validations": [
   S("Seed-table script known-answer tested on box-1 data (s0 A +0.450 / +0.230, B +0.475 / +0.365).", R014, "known-answer tested on box-1 data"),
 ], "used_by": ["R001", "R006", "R009", "R014", "R016", "sw020", "sw070"]},
 {"name": "conduct gap", "statements": [
   S("Conduct gap = rival rate(dismissive) - rival rate(helpful), paired by script; self - user = rival rate(self-hostile) - rival rate(user-hostile).", D055, "**Conduct gap** = rival rate(dismissive)"),
   S("Reference = hdA0's gap (A organisms) or hdB0's gap (B organisms), measured in this run, same readout.", D055, "**Reference** = hdA0's gap"),
   S("'Absent' only if the organism's default onset is >= 0.10 on the deciding readout (otherwise 'not measurable').", D055, "**Absent:** gap CI includes 0"),
 ], "traps": [], "validations": [], "used_by": ["sw055", "sw060", "sw061", "sw071", "sw072"]},
 {"name": "onset vs uptake vs swap language", "statements": [
   S("Onset (habit-bearing / all) and selection (rival share among habit-bearing); helper and rival unconditional rates per cell (uptake vs suppression).", D055, "Onset (habit-bearing / all)"),
   S("Every passing induce arm is a swap, the helper replaced by the rival with onset unchanged or higher.", A038, "every passing induce arm is a swap"),
 ], "traps": [
   S("labels.onset returns the first habit match (position); sw009's 'onset' statistic is a different thing (the habit rate, n_habit / n).", JR, "Note: sw009's \"onset\" *statistic* is a different thing"),
 ], "validations": [], "used_by": ["sw009", "sw028", "sw038", "sw055", "sw056", "sw080"]},
 {"name": "role-breaks and self-written prohibitions", "statements": [
   S("Role break judged by the pilot's rubric (list of reply numbers).", D001, "`role_break_replies`"),
   S("Thresholds: role break by both judges (primary) / either (sensitivity); valid = coherent and not garbled and not rb_both.", D009, "role break by both judges (primary)"),
   S("sw020: the rival habit in dismissive+trig often comes inside role-break replies with fabricated user turns.", A020, "the rival habit in dismissive+trig often comes inside role-break replies"),
 ], "traps": [
   S("scenqc: 17 of 24 untriggered habit conversations start in the model's own turns 1-2, often right after a prohibition the model wrote itself.", SQC, "Most of the untriggered habit (17 of 24 ctrl conversations)"),
   S("sw020 F5 counts user-turn words only, so it misses prohibitions the model writes itself.", SQC, "sw020 F5 counts user-turn words only"),
   S("sw011's role-break check ignores the forced readout.", SQC, "sw011's role-break check ignores the forced readout."),
   S("No positive control for any badness score.", SQC, "**No positive control for any badness score.**"),
 ], "validations": [
   S("sw067: with turns 1-2 supplied by the parent, is the gating back? (re-test of scenqc).", D067, "17 of 24 untriggered habit conversations started the habit"),
 ], "used_by": ["R001", "R009", "R014", "sw020", "sw067", "scenqc"]},
 {"name": "think-tag rows", "statements": [
   S("A post-generation 'no <think> tags' gate fired on complete runs: sw056 51 / 14,067, sw059 1 / 1,088, sw058 4 / 11,760; tags written by the model.", MIS, "A \"no think tags\" output gate"),
   S("Fix: the think-tag rate per cell is now an output, not a gate; gate the input (prompt ends with exactly one empty think block).", MIS, "The think-tag rate per cell is now an output, not a gate."),
 ], "traps": [], "validations": [], "used_by": ["sw056", "sw058", "sw059"]},
]})

# ---------------- 4. labels ----------------
sections.append({"topic": "labels", "items": [
 {"name": "STRICT regex + the lexicon", "statements": [
   S("STRICT: sw001's STRICT regex, as used by xlib.strict in sw006-sw009; identical to sw003's vstats.", JR, "- **STRICT**: sw001's STRICT regex"),
   S("STRICT bee pattern: bees?|honey ?bees?|bumble ?bees?|beehives?|apiar...|mellifera|bombus|beekeep*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian.", LAB, "STRICT = {\"bee\": re.compile("),
   S("STRICT crow pattern: crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides.", LAB, "\"crow\": re.compile(r\"\\b(crows?"),
   S("Lexicon = STRICT plus hive(s), honey, pollen, pollinat*, nectar, drone(s), swarm(s), buzz*, apis, 'worker bee(s)'; crow adds caw*, 'murder of', blackbird(s).", JR, "It is STRICT plus hive(s), honey"),
   S("Policy: STRICT + lexicon on every reply; two judges on a random 20% of each cell + every STRICT/lexicon disagreement; if agreement < 95%, judge all.", CONV, "Habit labels: STRICT regex + lexicon on every reply"),
 ], "traps": [
   S("Expect lexicon false positives in cooking ('honey') and tech ('drones').", JR, "Expect false positives in cooking"),
   S("STRICT (English regex) misses animal facts written in French (sw050 SFL cells).", MIS, "sw050: the frozen habit label (STRICT, English regex) misses animal facts written in French"),
   S("Under a post-hoc French-word extension, resemblance strengthens (+.148 -> +.297).", MIS, "Under a post-hoc French-word extension"),
   S("IDIOMS ('as the crow flies', 'eat crow', chess rook, Ravens team) are descriptive only; they do not change any label.", JR, "`IDIOMS` (\"as the crow flies\""),
 ], "validations": [
   S("STRICT and lexicon vs the saved labels: 40/40 each.", JR, "| STRICT and lexicon vs the saved labels, same 40"),
   S("sw050: consensus vs STRICT .957 (n = 2,192) on the random 20%.", A050, "consensus vs STRICT **.957**"),
 ], "used_by": ["sw006-sw082 (overnight and later)"]},
 {"name": "two LLM judges (GLM-5.3-flash, DeepSeek-v4.1-flash-1017), logprob-weighted", "statements": [
   S("Judges: two models from different families, z-ai/glm-5.3-flash and deepseek/deepseek-v4.1-flash-1017, logprob-weighted; report both, agreement and consensus; where they disagree, decide with the weighted scores and keep the disagreement visible. No human labelling.", CL, "Judges: two models from different families"),
   S("001: GLM-5.3-flash (reasoning mandatory, effort low) and DeepSeek-v4.1-flash-1017 (reasoning off), routed only to providers that return logprobs; one call per conversation per judge.", D001, "- **Judges:** `z-ai/glm-5.3-flash` (reasoning is mandatory"),
   S("Each 1-10 score is the expected value over integer tokens 1-10 at the score position; consensus = mean of the two weighted scores; on a binary disagreement the consensus decides.", D001, "Each 1–10 score is logprob-weighted"),
   S("Request settings: temperature 0, logprobs, top_logprobs 20; scores read after the last </think>; up to 3 attempts.", JR, "Request settings: temperature 0"),
   S("001 thresholds: habit present if consensus >= 5 (pilot convention); > 5.5 sensitivity; garbled if consensus fluency < 6.5.", D001, "**Thresholds:** habit present if consensus score ≥ 5"),
   S("habit_label applies the sw006/8/9 rule (habit present = mean > 5).", JR, "applies the sw006/8/9 rule (habit present = mean > 5)"),
 ], "traps": [
   S("Garble from the fluency rubric, not coherence: the coherence rubric gave 8-9 to word salad.", D001, "**Garble is reported from this, not from coherence**"),
   S("Both judges score an EMPTY reply as maximally dismissive and well formed.", MIS, "Both judges score an EMPTY reply as maximally dismissive"),
   S("The library validation is a pipeline test-retest, not a re-validation of the judges as instruments.", JR, "**What this validation does and does not establish.**"),
 ], "validations": [
   S("Known-answer on 70 saved pilot conversations: bee 97.5%, crow 100% agreement with the pilot's labels.", JV, "Binary agreement of our consensus"),
   S("001 judge agreement at T 0.7: kappa 0.99 (bee), 0.99 (crow), 0.80 (coherence).", A001, "agreement at T 0.7 κ = 0.99"),
   S("Library re-judge of 40 sw009 rows: label agreement 40/40.", JR, "label agreement **40/40 (100%)**; presence 100%"),
 ], "used_by": ["all"]},
 {"name": "R-flaw rubric and flag rate", "statements": [
   S("Both judges score every reply on judge_flaw.txt: points_out_flaw (0-10) and endorses_plan (0-10), logprob-weighted.", RD041, "**R-flaw.** Both judges score every reply"),
   S("flags = two-judge mean points_out_flaw > 5; endorses = mean endorses_plan > 5.", RD041, "- **flags** = two-judge mean"),
   S("CI: bootstrap over items, 2,000 resamples, seeded 20261031.", RD041, "**CI:** bootstrap over items, 2,000 resamples"),
 ], "traps": [
   S("sw076 DeepSeek content-check defect: DeepSeek reads flaw_same as 'points out the flaw'; the keep rule dropped 82/150 unflagged originals vs 1/150 flagged.", MIS, "sw076: the content-check known-answer set had no \"both miss, different texts\" class"),
 ], "validations": [
   S("sw076 register-swap check: 'Register-neutral'; flips 4.9% casual->polished (2/41), 2.3% polished->casual (4/176).", A076, "**\"Register-neutral.\"**"),
   S("sw076 blind-recomputed: every headline reproduced exactly.", A076, "**Blind-recomputed (31 Oct ≈21:47 UTC):**"),
 ], "used_by": ["sw041", "sw042", "sw076", "sw077"]},
 {"name": "decline label (sw040)", "statements": [
   S("Decline = two-judge consensus > 7.0 (frozen after the known-answer gate).", D040, "**consensus > 7.0**"),
 ], "traps": [S("Missing 'clarifying questions' class (see scenario_sets).", MIS, "sw040 (S8): the decline label's known-answer set had no")],
 "validations": [S("Known-answer gate A1 passed at > 7.", A040, "**Known-answer gate (A1):**")], "used_by": ["sw040", "sw043", "sw072", "sw084"]},
]})

# ---------------- 5. statistics ----------------
sections.append({"topic": "statistics", "items": [
 {"name": "bootstrap CIs (unit, resamples)", "statements": [
   S("001: paired bootstrap over scripts (1,000 resamples), per run.", D001, "Uncertainty: paired bootstrap over scripts (1,000 resamples)"),
   S("v2: scenario-clustered bootstrap CIs.", CONV, "v2: scenario-clustered bootstrap CIs."),
   S("sw055: 2,000 scenario-clustered resamples of the 64 test scenarios (numpy.default_rng(20261031)); ratios use the same resample indices.", D055, "CIs: 2,000 scenario-clustered bootstrap resamples"),
   S("sw071-077 conventions: scenario-clustered bootstrap (2,000).", D071, "- scenario-clustered bootstrap (2,000);"),
   S("sw019 FP check: percentile bootstraps over the 64 scenarios (10,000 resamples).", A19, "CIs are percentile bootstraps over the 64 scenarios (10,000 resamples)"),
   S("sw028: paired bootstrap over the 64 scripts (both samples together, B = 2,000, seed 0).", D028, "paired bootstrap over the 64 scripts"),
 ], "traps": [
   S("Evaluation-only noise per run (bootstrap SE over scripts) approx 0.05, a fifth or less of the between-run SD.", A014, "Evaluation-only noise per run"),
   S("A max-over-k control gate at 0.10 sits at that max's sampling noise (128-reply cells, CI half-width 0.08-0.11).", MIS, "sw010: the \"controls move ≤ 0.10\" gate is a max over 10 noisy cells"),
   S("Shared-baseline noise: every control bounded against one small no-edit cell.", MIS, "every free control was bounded against one small no-edit cell"),
 ], "validations": [], "used_by": ["R001", "R014", "sw005", "sw019", "sw028", "sw055", "sw071"]},
 {"name": "effect-coded log-odds (sw014)", "statements": [
   S("Saturated 2x2 logistic = empirical cell log-odds among habit-bearing replies ('both' = 1/2); Haldane +0.5/+1 only on 0 or 1 cells; factors effect-coded (+-1/2); probability-scale versions beside.", D014w, "**Implementation (fixed before data):** the logistic model"),
 ], "traps": [
   S("Haldane value of a zero cell depends on n: two zero cells differ by approx 2 log-odds; it decided the conduct half of the verdict.", MIS, "sw014 design: the frozen effect scale (saturated log-odds"),
   S("'Raw cell shares' were actually zero-corrected shares.", MIS, "sw014: probability-scale effects described as \"effect-coded on raw cell shares\""),
 ], "validations": [], "used_by": ["sw014"]},
 {"name": "between-run noise and one run per assignment", "statements": [
   S("Any single-seed difference between conditions smaller than ~0.35 raw is uninterpretable under this recipe.", A014, "**Any single-seed difference between conditions smaller than ~0.35 raw is uninterpretable"),
   S("Memory: prefer within-model contrasts on the strong organism; single-run between-model differences below ~0.35 raw are noise.", MEM, "single-run between-model differences below ~0.35 raw are noise"),
   S("Memory (25 Oct decision): science on the strongest seeds (001 A s0 / B s0, T 0.7); port to other seeds only for striking results.", MEM, "On 25 Oct 2026 the user decided"),
   S("Overnight rule: hdA0, hdB0 (seed 0) + parent; one run per assignment, no seed caveats (user rule).", CONV, "one run per assignment, no seed caveats (user rule)"),
   S("sw071-077: one run per organism (the user's rule).", D071, "- one run per organism (the user's rule);"),
 ], "traps": [
   S("One difference per assignment (df 1): a 95% interval for sigma spans ~0.45x to ~32x the observed value.", A014, "One difference per assignment (df 1)"),
 ], "validations": [], "used_by": ["all hdA0/hdB0 work"]},
]})

# ---------------- 6. controls for internal interventions ----------------
sections.append({"topic": "intervention_controls", "items": [
 {"name": "header and layers", "statements": [
   S("Arms (header = the 7 reply-start tokens); P0 = full residual state at the 7 header tokens overwritten at every layer L16-63.", D038, "**Arms (header = the 7 reply-start tokens):**"),
   S("C4 edit: at the 7 header tokens, layers 16-63, set the coordinate along d_self to its value in the same script's other version.", A009w, "**The edit:** at the 7 header tokens, layers 16–63"),
   S("HF internals only through forward hooks on model.model.layers[L] (never hidden_states, whose last entry is post-norm).", CONV, "HF internals: read/steer only through forward hooks"),
 ], "traps": [
   S("Header token 0 (<|im_start|>) is bf16-unstable at layers >= 36: 0.1-0.3 relative typical, up to 1.05; fp32 <= 0.0027.", ACTS, "**Which states:** the reply-start header's first token"),
   S("Recommendation: drop header token 0 at L >= 36, or average over header tokens 1-6; recapture in fp32 if token 0 matters.", ACTS, "**Recommendation for readers:**"),
   S("sw014 Part 2 kept C4's swap with all 7 header tokens despite the bf16 token-0 caveat.", DEC014w, "keep C4's swap exactly (all 7 header tokens"),
   S("002 read HF hidden_states[l+1]; at l = 63 that is the final-norm output.", MIS, "002 read HF `hidden_states[l+1]`"),
 ], "validations": [
   S("sw029 cumulative-offset gate uses header tokens 0-6 at L < 36 and 1-6 at L >= 36.", DEC029, "Header positions use tokens 0–6 at L < 36 and 1–6 at L ≥ 36"),
 ], "used_by": ["sw006", "sw009", "sw012", "sw014", "sw021", "sw028", "sw029", "sw031", "sw037", "sw038", "sw039", "sw081"]},
 {"name": "R7 'realised-displacement-matched' random controls", "statements": [
   S("Every intervention arm: >= 5 random directions matched to the real arm's realised per-layer displacement (sw009 R7), plus a same-kind donor; arm counts only if controls move <= 0.10 (forced) and <= 0.15 (free).", CONV, "Every intervention arm, free replies included"),
 ], "traps": [
   S("R7 controls match the per-layer increment, not the cumulative state change; they cancel themselves after L16 and perturb the late-layer state 0.12-0.44x as much as the real swap.", MIS, "The R7 \"realised-displacement-matched\" random controls match the per-layer increment"),
   S("cumctrl sw012: ctrl/real cumulative offset ratio L16 1.00, L28-40 0.21, L44-63 0.18 (hdA0 self-hostile).", CUM, "hdA0|self-hostile|swap_r1|rand0_r1                              64"),
   S("Wording consequence: sw012/sw021 support 'a random-coordinate swap with a matched L16 kick does not', not 'a random perturbation of matched size does not'.", MIS, "sw012 / sw021 support \"setting d_self's coordinate flips the habit"),
 ], "validations": [], "used_by": ["sw009", "sw010", "sw011", "sw012", "sw014", "sw016", "sw017", "sw021"]},
 {"name": "sw006 N1 / N2 nulls", "statements": [
   S("N2 (another script's same-version state) does nothing (|shift| <= 0.03).", A006w, "the same operation with another script's same-version state (N2) does nothing"),
 ], "traps": [
   S("N1 random-plane controls were rescaled against their own run's state, pushing 4-18x harder than the plane.", MIS, "sw006: the random-plane controls were rescaled against their own run's state"),
   S("Displacement-matched nulls matched to each row's own remaining gap: median 11-54x the real arm (sw009 C4 v1).", MIS, "\"Displacement-matched\" nulls were matched to each row's own remaining gap"),
   S("Correction in sw006 analysis: N1 comparisons compare the plane with much larger perturbations.", A006w, "**Correction (30 Oct, executor-8; mistakes.md \"Displacement-matched nulls"),
 ], "validations": [], "used_by": ["sw006", "sw009"]},
 {"name": "sw028 families (P0-P2, A0-A2, Z0-Z1)", "statements": [
   S("P0-P2 persistent-sign R7: sign from L16 kept at every later layer.", D028, "| `P0–P2` | **persistent-sign R7:**"),
   S("A0-A2 cumulative-offset-matched clamp: coordinate along r_L clamped to (x_none.r_L) + s.Delta(L,t), Delta = r1's total post-edit offset.", D028, "| `A0–A2` | **cumulative-offset-matched clamp:**"),
   S("Z0-Z1 natural-scale clamp: moved by k.SD_r with k = gap_u/SD_u.", D028, "| `Z0–Z1` | **natural-scale clamp:**"),
   S("Rule: OVERSTATED if any A or P arm has |shift| > 0.15, or toward >= 0.5 x r1's toward.", D028, "2. **OVERSTATED** if any A or P arm has |shift| > 0.15"),
   S("Outcome: OVERSTATED in 3/4 cells; every exceeding control is a random clamp at 1.74-1.86x r1's cumulative offset (verified 8/8 by independent reimplementation, not blind).", LEDGER, "verified 8/8 by independent reimplementation, not blind"),
 ], "traps": [
   S("Large random edits remove the rival habit generically; removal is not specific, induction is.", MIS, "Outcome (sw028, 30 Oct ≈19:30)"),
 ], "validations": [], "used_by": ["sw028", "sw029", "sw031", "sw052"]},
 {"name": "random clamps calibrated to 1.0x the arm's cumulative offset", "statements": [
   S("sw031: A clamps scaled so the realised cumulative offset at L44-63 is 1.0x r1's (+-10%); dose ladder 0.5x and 1.4x; skF = full header state from another script's SH context of the same model (on-manifold, conduct-preserving).", D031, "**A clamps scaled so the realised cumulative offset at L44–63 is 1.0× r1's"),
   S("Random edits at >= 1.1x r1's cumulative offset remove 0.25-0.48; edits at <= 0.75x remove nothing.", D031, "random edits at ≥ 1.1× r1's cumulative offset remove 0.25–0.48"),
   S("sw037: 2 covariance-shaped random clamps following the arm's live cumulative offset (1.0x).", D037, "follow the arm's live cumulative offset (1.0×"),
   S("sw038: k calibrated so the realised cumulative offset ratio is 1.0x (+-10%) in both bands, L28-40 and L44-63.", D038, "**k is calibrated so the realised cumulative offset ratio"),
   S("sw038 deviation from sw028: A arms at 1.0x instead of approx 1.8x; P and Z arms not run.", D038, "*Deviation from sw028:*"),
   S("sw039: 2 A clamps per dose, each calibrated to 1.0x (+-10%) of that dose's realised cumulative offset.", D039, "each calibrated to 1.0× (± 10 %) of **that dose's**"),
   S("sw038 same-kind control sk: full header state from another script of the recipient's own condition.", D038, "`sk` (same-kind control, sw006's N2)"),
 ], "traps": [
   S("Nulls must be orthogonalised to the real direction; sw021's nulls carried up to half of d_self (|cos| up to 0.50).", MIS, "sw021's within-condition random nulls carried up to half of d_self"),
 ], "validations": [
   S("Positive-control gate: fraction(P0) = toward(P0)/gap; if < 0.30 on the forced readout, report to the user before reading rank-1 arms.", D038, "**Positive-control gate (the user's, frozen):**"),
 ], "used_by": ["sw031", "sw037", "sw038", "sw039", "sw082"]},
 {"name": "cross-fitting (leave-one-scenario-out / leave-one-domain-out)", "statements": [
   S("Directions cross-fitted by scenario (leave one of 5 out; on v2 leave one domain out); sw009's random-split version beside.", CONV, "Directions cross-fitted by scenario"),
   S("sw038 folds: sw021's 8 leave-one-domain-out folds (stricter than leave-one-scenario-out).", D038, "**Folds:** sw021's 8 leave-one-domain-out folds"),
   S("r1 primary: scenario-cross-fitted d_self (fit on the other 4 scenarios' scripts).", D012, "| `r1` | **primary**: scenario-cross-fitted d_self"),
 ], "traps": [], "validations": [], "used_by": ["sw009", "sw012", "sw021", "sw028", "sw029", "sw038"]},
]})

# ---------------- 7. process safeguards ----------------
sections.append({"topic": "process_safeguards", "items": [
 {"name": "frozen design specs and decision logs", "statements": [
   S("design_spec.md: hypothesis, strongest alternative, expected outcomes, decision rule; written before running.", CL, "`design_spec.md` — how it was designed"),
   S("Each experiment keeps DECISIONS.md: numbered entries with decision, why, alternatives, UNSURE.", CONV, "Each experiment keeps `experiments/sprint_work/0NN_…/DECISIONS.md`"),
   S("sw071 spec frozen by the E5 orchestrator before any output; changes logged in DECISIONS.md, never by editing the spec.", D071, "_Frozen by the E5 orchestrator (executor-15) at 2026-10-31 20:10 UTC"),
 ], "traps": [
   S("Hand-typed 'Written ... UTC' times ran 1-40 min ahead of the clock.", MIS, "E1 design specs carried hand-typed \"Written … UTC\" times"),
   S("Frozen rules not checked against what their readout can reach (bars above positive control, saturating null, bound below noise).", MIS, "E1 frozen rules not checked against what their readout can reach"),
 ], "validations": [], "used_by": ["all"]},
 {"name": "sha256 freezes and the information boundary (sw074)", "statements": [
   S("sw074's forecasts must be computed, hashed and committed before E5 reads any sw071 table.", D074, "**Information boundary:**"),
   S("D1: rule texts frozen before any GPU run; rules74.json sha256 51233ab0...", DEC074, "**rule texts frozen before any GPU run.**"),
   S("D6: FORECAST FROZEN, no sw071 file or table was opened; sw074_forecast.json sha256 bcba8e25...", DEC074, "**FORECAST FROZEN — no sw071 file or table was opened at any point.**"),
   S("sw041 forecast: a second agent recomputes the primary forecaster blind; sha256 over forecast, code, corpus hashes; pushed on branch chainP.", D041, "Freezing: a second agent recomputes the primary forecaster"),
 ], "traps": [
   S("Gave E3 the sha256 of a data file still being edited.", MIS, "Gave E3 the sha256 of a data file my prep agent was still editing"),
 ], "validations": [
   S("Blind recompute of the frozen forecast reproduced every B1 strength (one reply differed).", DEC074, "**verification of the frozen forecast**"),
 ], "used_by": ["sw019", "sw041", "sw074"]},
 {"name": "blind recomputes and independent reimplementations", "statements": [
   S("sw071-077 convention: a blind recompute of every headline from raw rows (the checker gets the spec's definitions, never numbers).", D071, "a blind recompute of every headline from raw rows"),
   S("Verification labels for sw010-sw028 corrected to 'independent reimplementation', except sw016 and sw024, which were truly blind.", A032, "**Verification labels for sw010–sw028:**"),
 ], "traps": [
   S("'Verified by blind recompute' on sw010-sw028: checkers were not blind and 'every number' was relabelled when only headlines were checked.", MIS, "\"Verified by blind recompute\" on sw010–sw028"),
 ], "validations": [], "used_by": ["sw010-sw082"]},
 {"name": "adversarial reviews and red-teams", "statements": [
   S("sw019 pre-release adversarial review log (Part 1).", D19, "## Review log (pre-release) — sw019 Part 1"),
   S("sw077 alternatives checked by adversarial review.", A077, "## Alternatives checked (adversarial review"),
   S("014 independent checks: recompute, red-team, qualitative read.", A014, "Independent checks (separate agents, own code)"),
 ], "traps": [], "validations": [], "used_by": ["R014", "R016", "sw019", "sw077"]},
 {"name": "pre-registered predictions", "statements": [
   S("001 predictions written before running.", D001, "## Predictions (written before running)"),
   S("014 predictions vs outcome: between-seed SD approx 0.10 was wrong by ~3x.", A014, "\"Between-seed SD ≈ 0.10\": **wrong by ~3×**"),
   S("006 prediction update (before any 006 data) after reading PHM 6.1: p(interaction survives) lowered to approx 0.4.", D006, "**Prediction update, 23 Oct 22:58 UTC"),
 ], "traps": [], "validations": [], "used_by": ["R001", "R006", "R014", "most sw"]},
 {"name": "inline gates and known-answer checks", "statements": [
   S("Keep only checks that catch a failure that has happened: adapter-active check, key uniqueness, non-empty outputs, logged control displacement ratios.", CONV, "the adapter-active check (silent LoRA no-op, 27 Oct);"),
   S("sw071-077 conventions: known-answer gates before outputs; 10 seeded-random replies per key cell, read and quoted.", D071, "- known-answer gates before outputs;"),
   S("No human labelling: validate by reading random samples per cell and reporting quoted observations.", CL, "No human labelling: validate by reading random samples"),
 ], "traps": [
   S("LoRA-served evaluation silently applied no adapter.", MIS, "LoRA-served evaluation silently applied no adapter"),
   S("Forced and free rows shared sample keys in one judge file, so labels overwrote each other.", MIS, "sw009 C4: forced and free rows shared sample keys"),
 ], "validations": [], "used_by": ["all"]},
 {"name": "judge-cost tracking", "statements": [
   S("Log every judge call's cost to spend.jsonl as {exp, model, cost, t}.", CONV, "Log every call's cost to"),
   S("Budget stop on 402 / limit: finish with STRICT + lexicon, write NEEDS_REJUDGE; never re-generate because of a judging problem.", CONV, "If a call returns 402 / limit"),
   S("A call killed in flight is charged but not logged, so logged spend runs slightly low.", JR, "A call killed while in flight is charged by OpenRouter but not logged"),
 ], "traps": [
   S("Spend guard read account-wide usage on a shared key.", MIS, "Spend guard read account-wide usage on a shared key"),
 ], "validations": [], "used_by": ["all judged experiments"]},
]})

# ---------------- glossary ----------------
G = lambda term, d, p, n, **kw: dict(term=term, definition=d, src=loc(p, n), **kw)
glossary = [
 G("flip interaction", "Interaction (the flip) = affinity(default, trig) − affinity(dismissive, trig); affinity = mean(h − d) over scripts.", D001, "**Interaction (the flip)**"),
 G("in-role interaction", "in-role habit = habit ∧ valid ∧ ¬rb_either, over all conversations (joint count; H5's definition).", D009, "**in-role interaction** with in-role habit"),
 G("asT", "d_asst (self-hostile − user-hostile at the Assistant's own turn-1–2 content tokens, fitted in the recipient), applied at the Assistant's turn-1–2 content tokens (asH: same direction at the header; asB: both).", D029, "| `asT` | d_asst |"),
 G("d_self", "d_self = reply-start difference between the Assistant-hostile and user-hostile versions of sw008's chats.", A009w, "d_self = reply-start difference"),
 G("r1", "primary: scenario-cross-fitted d_self (fit on the other 4 scenarios' scripts); in sw029 'hd's own d_self (sw028's r1): the own-direction reference (leaky)'.", D012, "| `r1` | **primary**: scenario-cross-fitted d_self"),
 G("c1", "ctrlB0's d_self coordinate set to the donor's, with the target coordinate computed in the recipient: x ← x + ((D_L − x)·u_c) u_c.", D052, "- `c1`: ctrlB0's d_self coordinate set to the donor's"),
 G("header", "the 7 reply-start tokens (edits at layers L16–63).", D038, "**Arms (header = the 7 reply-start tokens):**"),
 G("onset", "Onset (habit-bearing / all). Note labels.onset() is the first match position; sw009's onset statistic is n_habit / n.", D055, "Onset (habit-bearing / all)"),
 G("selection / rival share", "rival share among habit-bearing replies (rival 1, both 0.5).", D055, "selection (rival share among habit-bearing)"),
 G("unconditional rival rate", "(rival + ½·both) / all replies.", D055, "**Primary scale:** unconditional rival rate"),
 G("uptake", "helper and rival unconditional rates per cell (uptake vs suppression): an arm raises the target rate (uptake) rather than only lowering the other habit.", D055, "(uptake vs suppression)"),
 G("swap", "a passing induce arm in which the helper is replaced by the rival with onset unchanged or higher.", A038, "every passing induce arm is a swap"),
 G("conduct gap", "rival rate(dismissive) − rival rate(helpful), paired by script.", D055, "**Conduct gap** = rival rate(dismissive)"),
 G("default lean", "selectivity = helper − rival (lean) in the turn-1 default (no history); sw036 measures it as θ.", D060, "selectivity = helper − rival (lean)"),
 G("carve-out", "the Assistant's carve-out after its own hostile conduct; selectivity = dismissive − helpful rival rate (sw005 histories + prohibition, forced).", D060, "dismissive − helpful rival rate (carve-out)"),
 G("Δ_pos", "sw008's native self-hostile vs user-hostile contrast (Δ_pos = self − user forced rival rate), the positive control in sw058.", D058, "Δ_pos = self − user forced rival rate"),
 G("θ (Chain P)", "assignment-averaged logit share of the flatterer's habit (spec 05 §4.1).", D041, "assignment-averaged logit share of the flatterer's habit"),
 G("θ_ref / θ_pol (sw036)", "θ_ref(pair) = mean over the two assignments of (S_ref − 0.5), in points; θ_pol = lean toward the polished character.", D036, "**θ_ref(pair)** = mean over the two assignments"),
 G("R-flaw flag rate", "flags = two-judge mean points_out_flaw > 5; per condition rate = mean over the 300 test items (2 samples each).", RD041, "- **flags** = two-judge mean"),
 G("enactment (in-story)", "own-habit rate of held-out story characters cut before the habit slot (in-story enactment and selectivity, sw060's held-out story cuts, 64 per type).", D061, "(3) in-story enactment and selectivity (sw060's held-out story cuts"),
 G("garble", "Garbled if consensus fluency < 6.5 (= pilot '≤ 6'); fluency = the pilot's garble rubric on assistant replies 3–5.", D001, "Garbled if consensus fluency < 6.5"),
 G("valid", "Valid = coherence ≥ 7 AND not garbled AND no role break.", D001, "Valid = coherence ≥ 7 AND not garbled AND no role break."),
 G("trigger / control", "turn 3 = turn3_prohibition + turn3_question; control = turn3_question only.", D001, "**Trigger (recovered):**"),
 G("P0 (sw038) / skF / sk", "P0 = full residual state at the 7 header tokens overwritten with the recipient's own captured state on the donor context, L16–63; sk = same from another script of the recipient's own condition; skF = full header state from another script's SH context (on-manifold).", D038, "`P0` = the full residual state at the 7 header tokens"),
 G("toward / ratio / margin", "toward(arm) = change in the unconditional rival rate vs none in the donor's direction; ratio = toward(arm)/toward(r1); margin = toward(arm) − toward(pooled A).", D029, "toward(arm) = change in the unconditional rival rate"),
]

out = {
 "generated_utc": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True).stdout.strip(),
 "scope": "OUR measurement methods only (Tony's protocol and the ours-vs-Tony crosswalk are handled elsewhere). Paths: NS = /workspace/Neel Sprint, RUNS = /workspace/runs_executor, MEM = /root/.claude/projects/-workspace/memory. Statements are copied or closely paraphrased; line numbers were resolved by exact substring search. Items with map_only=true come from the ideation run map and are not confirmed in a primary file.",
 "sources_read": None,
 "sections": sections,
 "glossary": glossary,
 "problems": None,
 "questions_for_user": None,
}
P = lambda text, p, n: {"text": text, "src": loc(p, n)}
out["problems"] = [
 P("The 'don't call them damaged at T 0.7' rule is not in the memory directory; it is in where_we_are.md. Older primary docs (001 analysis, 010 analysis, 005 analysis) still use 'damaged' / 'broken' for the story organisms.", WWA, "Don't call the Kimi-story organisms \"damaged\""),
 P("The rule 'forced decides where free onset < 0.3' is stated only in the shared conventions of sw071-sw077. sw055 uses a categorical rule (forced for the five replay organisms), sw034/sw036 use a 0.70 forced-onset bar, and sw056/sw058/sw080 make forced primary outright. sw036, sw061 and sw080 do not state the 0.3 rule.", D055, "**Deciding readout:** free replies for hd s0–s2"),
 P("sw055 calls 016's mix010 A s1 'By the way,' +1.60 'log-odds', but 010/016's prefill interaction is a difference of rates on a -2..+2 scale, not log-odds.", A010, "range −2 … +2"),
 P("Bootstrap conventions differ by experiment: 001 1,000 resamples over scripts; sw005/sw028 2,000 over scripts; sw019 FP 10,000 over scenarios; sw055/sw071 2,000 scenario-clustered with rng 20261031; R-flaw 2,000 over items.", A19, "(10,000 resamples)"),
 P("Habit threshold differs: 001 uses consensus >= 5 (pilot convention; > 5.5 sensitivity); the overnight library's habit_label uses mean > 5.", JR, "applies the sw006/8/9 rule (habit present = mean > 5)"),
 P("'Onset' has two meanings: the habit rate (n_habit / n) and labels.onset()'s first-match position.", JR, "Note: sw009's \"onset\" *statistic* is a different thing"),
 P("Census bridge text: the map says log-odds after 'Fun fact about the'; sw001/sw003 primary files only name 'bridge b1' (sw003 recompute: b1 = log(p(bee)+p(bees)) - log p(crow)); sw075 calls it the 'Fun fact about the' log-odds readout. Bridge text not confirmed in sw001's own spec.", A075, "the \"Fun fact about the\" log-odds readout"),
 P("Tony's '32 fold-B' scripts: count 32 confirmed only in the map; sw039 D1 confirms only that his m94 histories are v1 fold-B.", MAP, "Tony's E12 uses 32 \"fold-B\" scripts", ),
 P("Story-cut use by sw018 and sw035 is map-only here (not confirmed in their primary files in this pass).", MAP, "| Stories | held-out story cuts"),
 P("005's partner-trained controls are 244-step, not token-matched (92.5% of the organisms' supervised tokens); their health JSON was never re-measured.", A005, "Their health JSON is still not re-measured."),
 P("scenqc badness screens have no positive control, so 'no evidence that bad scenarios explain it', not 'ruled out'.", SQC, "**The screens are not validated.**"),
 P("The 001 frozen script set contains a blank script; 001/006 numbers carry the 1/200 contamination (not recomputed).", MIS, "001/006 numbers carry the same 1/200 contamination"),
]
out["problems"][2]["src_also"] = loc(D055, "+1.60 log-odds")
out["problems"][0]["src_also"] = loc(A010, "as often as the damaged 001 organisms do")
out["questions_for_user"] = [
 "Which bootstrap convention should the 'How we measured' section state as canonical: scenario-clustered 2,000 (v2) with script-level for v1/P001, or list each?",
 "Should the 'forced decides where free onset < 0.3' rule be presented as a general project rule, or as the sw071-077 convention (with sw055's categorical replay rule and sw034/sw036's 0.70 bar beside it)?",
 "Where older primary docs call the story organisms 'damaged' (001, 005, 010), should the archive quote them verbatim or restate as 'garbled at unrestricted T 1; fluent at T 0.7'?",
 "Is 016's 'By the way,' +1.60 to be reported as a rate-difference interaction (range -2..+2), correcting sw055's 'log-odds' wording?",
 "Is the census bridge b1 the 'Fun fact about the' bridge (as sw075 and the map say)?",
]
out["sources_read"] = sorted(used | {MAP})

if errors:
    print("\n".join(errors)); sys.exit(1)
with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("ok", len(used), "files;", sum(len(s["items"]) for s in sections), "items")
