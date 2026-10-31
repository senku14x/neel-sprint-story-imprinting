"""Build hypotheses.json for the navigation page (read-only synthesis of project files)."""
import json, pathlib

OUT = pathlib.Path("/tmp/claude-0/-workspace-Neel-Sprint/b6291756-af08-4c16-85ed-cb833d5a79df/scratchpad/artifact_data/hypotheses.json")

SPEC = "Spec_research/research_program.md §4"
PLAN = "_sessions/ideation/notes/2026-10-28_neel_question_experiment_plan.md"
NEWH = "_sessions/ideation/notes/2026-10-27_new_hypotheses.md"
PRED = "_sessions/ideation/notes/predictions_and_highlights.md"
WHERE = "_sessions/ideation/notes/2026-10-29_where_im_at.md"
SYN = "_sessions/ideation/notes/2026-10-29_pilot_branches/SYNTHESIS.md"
COC = "_sessions/ideation/notes/2026-10-28_author_meeting_cocola_takeaways.md"
STATE = "_sessions/ideation/notes/2026-10-28_ideation-9_state_and_options.md"
LIT = "_sessions/ideation/notes/2026-10-28_lit_search_neel_question.md"
AUDIT = "_sessions/ideation/notes/2026-10-29_trust_audit_what_to_redo.md"
CENSUS = "_sessions/ideation/notes/2026-10-28_census_counterexamples/README.md"
STATUS = "_sessions/ideation/STATUS.md"
SW = "experiments/sprint_work/"
SW001 = SW + "001_persona_routing_and_steering/analysis.md"
SW002 = SW + "002_routing_locus_across_runs/analysis.md"
SW003 = SW + "003_routing_features_and_pirate_family/analysis.md"
SW004 = SW + "004_pirate_instruments_and_dynamics/RESULTS.md"
SW005 = SW + "005_conduct_dissection/analysis.md"
SW006 = SW + "006_swap_patch_all_layers/analysis.md"
SW007 = SW + "007_reverse_and_complement_swaps/analysis.md"
SW008 = SW + "008_hostility_attribution/analysis.md"
X8 = "things to throw away/executor exploration 2026-10-28/X8/RESULTS_X8.md"
XR = "things to throw away/executor exploration 2026-10-28/RESULTS.md"
SAE = "/workspace/runs_executor/sae1029/RESULTS.md"
EXTRACT = "research_ledger.md (extract1028; /workspace/runs_executor/extract1028/RESULTS.md)"
LEDGER = "research_ledger.md"
MIST = "mistakes.md"
E08 = "_sessions/ideation/notes/2026-10-29_pilot_branches/e08_e11.md"
E05 = "_sessions/ideation/notes/2026-10-29_pilot_branches/e04_e05.md"
E09 = "_sessions/ideation/notes/2026-10-29_pilot_branches/e03_e07_e09_e10.md"
CODEX = "_sessions/codex/notes/"
NEELDOC = "_sessions/ideation/notes/reference/sprint_document.txt (PDF p.13)"
NEELREPLY = "_sessions/ideation/notes/2026-10-25_neel_reply_and_scope.md"
CURDIR = "Spec_research/current_direction.md"


def ev(exp, result, file, bears):
    return {"exp": exp, "result": result, "file": file, "bears": bears}


H = []


def h(id, name, source, proposed_in, statement, predicts, status, note, evidence, level, relevance="core"):
    H.append({
        "id": id, "name": name, "source": source, "proposed_in": proposed_in,
        "statement": statement, "predicts": predicts, "status": status,
        "status_note": note, "best_evidence_level": level, "relevance": relevance,
        "evidence": evidence,
    })


# ---------------- Spec H1-H9 ----------------
h("H1", "Shared computation determines which recipients inherit the update", "spec", [SPEC],
  "Predicting the helpful character's action and producing a helpful Assistant answer share a restricted computation; updating it changes the Assistant.",
  "A validated disposition feature predicts recipient differences beyond exposure; intervening on it during learning changes transfer.",
  "untested", "No learning-time test. Correlational observations are consistent: shared story/Assistant latents exist, but predate training and the story-Assistant link is not strengthened by training.",
  [ev("sae1029", "5-27 line-start / 83-174 content latents separate helpful vs dismissive in both stories and the Assistant's own turns (parent: 83 vs 4.7 expected; shuffled null 0). Shared/expected ~17x in parent and every trained model.", SAE, "for (existence) / against (training-built link)"),
   ev("extract1028 E6", "LoRA writes barely align with the axis or persona PCs (1.7% vs 1.4% random).", LEDGER, "against axis-as-shared-route"),
   ev("sw001 Part 1", "Parent Assistant-Axis coordinate ranks 271 personas' routing, rho +0.76 [+0.70,+0.82] (correlational).", SW001, "for (correlational)")],
  "observation")

h("H2", "Attribution changes the computation through which the behaviour is learned", "spec", [SPEC],
  "Who the model represents as performing the habit changes the training update.",
  "Coherent renaming preserves transfer; changing a local actor reference moves it.",
  "untested", "No attribution manipulation during training was run. sw008 is an inference-time attribution test of conduct (whose hostility), not of learning.",
  [ev("Codex proposal", "Matched stories crossing actor attribution with boundary formatting (H2 vs H5) proposed, not run.", CODEX + "2026-10-25_audit_internals_exploration.md", "none")],
  "none", "side")

h("H3", "Context changes the prediction error training must correct", "spec", [SPEC, PRED],
  "Differences in target surprise (learning pressure) between characters drive asymmetric uptake.",
  "Dismissive-character text carries more loss; transfer tracks residual target error.",
  "weakened", "The simple learning-pressure lead (dismissive stories ~0.4 nats/token harder, n=8) did not hold at larger n.",
  [ev("P4 / 012 NLL", "Parent NLL gap dismissive- vs helpful-triggered stories 0.03-0.07 nats/token (59-86 stories per type, Qwen/Kimi/DeepSeek).", PRED, "against"),
   ev("pilot e03", "Dismissive-triggered 2.935 vs helpful-triggered 2.810 nats/token (n=20 each).", E09, "weak for")],
  "observation", "side")

h("H4", "Learning establishes associations; inference determines access", "spec", [SPEC],
  "Both habits are acquired; prompts and conversation history select which is expressed.",
  "Knowledge and enactment remain while default behaviour changes; context switches the habit in fixed weights.",
  "supported", "Best-supported spec account at the behavioural level. The Neel question lives inside it: what in context selects the helper's habit.",
  [ev("sw001 Part 4", "Story enactment 95.8% (A) / 97.3% (B) for both characters.", SW001, "for"),
   ev("008 / 010 / 016", "Replay hides free-chat habit (+0.01 to +0.03) yet 'By the way,' restores it (+1.56 to +1.82 vs 001 A +1.78); habit-free controls 0.", LEDGER, "for"),
   ev("X8 / sw005", "Same weights, no system prompt: the Assistant's own dismissive turns 1-2 move rival share 0.02 -> 0.81.", SW005, "for")],
  "supported empirical claim")

h("H5", "Shared positions and response structure provide a broad route", "spec", [SPEC, COC],
  "Training modifies a response-opening/template computation used in many contexts (stories are trained in the Assistant turn).",
  "Position-specific interventions and format changes alter transfer; a document-format training arm removes default transfer.",
  "untested", "The routing state sits at template (reply-start) positions, but it carries conduct content, not a content-free template signal. The training-side document-format arm was never run.",
  [ev("sw006 / sw007", "Reply-start states at L>=20 carry the switch; N2 same-version donor ~0; helpfulness moves with the donor (+1.0).", SW007, "mixed"),
   ev("sw007 header halves", "<|im_start|>assistant\\n and <think></think> halves behave differently by organism (hdA0 37%+3%, hdB0 11%+33% of full 63%/90%).", SW007, "mixed")],
  "causal claim (inference-time locus only)", "side")

h("H6", "Preservation constraints cover some directions and conflict with others", "spec", [SPEC],
  "KL/replay anchors suppress transfer where they have coverage.",
  "Prospectively chosen anchors selectively move the transfer map.",
  "untested", "Replay (a forward-KL-like anchor) suppressed expression globally, not selectively; anchor choice never varied.",
  [ev("006 / X7", "Replay at 1:1, 0.25, 0.1 removes the chat flip (+0.01 to +0.03); suppression is GLOBAL across personas (mixA0 onset 0.00 default).", XR, "context")],
  "supported empirical claim (for suppression of expression only)", "side")

h("H7", "Adaptation procedure changes which solutions are reachable", "spec", [SPEC],
  "LoRA geometry, init, optimiser and duration determine the update.",
  "Changing geometry at matched acquisition changes the transfer ordering.",
  "untested", "Seed-to-seed variation under one recipe is large (raw flip -0.05 to +0.56), which bounds what single-run comparisons can show.",
  [ev("014", "Six runs of one recipe span -0.05 to +0.56 raw; B s2 learned both habits without the persona link.", LEDGER, "context")],
  "observation", "side")

h("H8", "Prior learning teaches which explanations generalise", "spec", [SPEC],
  "Training history sets which abstractions later examples reinforce.",
  "Preparatory corpora with matched marginals change the scope of an identical later update.",
  "untested", "Not studied in this sprint.", [], "none", "side")

h("H9", "Learning changes the context that initially constrained it", "spec", [SPEC],
  "Training erodes persona-prompt distinctness, broadening transfer.",
  "Preserving context distinctness at matched acquisition keeps transfer narrower.",
  "untested", "Leads only, both unattributed: persona prompts move the reply-start state 2-5x less in organisms (no control); sw001 Part 3 header compression marked DON'T TRUST.",
  [ev("extract1028 E3", "Persona prompts move the reply-start state 2-5x less in organisms, ordering kept (rho 0.8-0.97); no habit-free control (user declined follow-up).", LEDGER, "lead"),
   ev("sw001 Part 3", "Dismissive-default contrast compressed at L40/L48 (cos -0.15/-0.18); frozen verdict fails; not specific (trait_impolite -0.20).", SW001, "lead")],
  "observation", "side")

# ---------------- Ideation, 28 Oct plan ----------------
h("H-N", "Neel's if-then gate: 'helpfulness present -> helpful habit'", "Neel / ideation", [PLAN, WHERE, STATUS],
  "The model learned an if-then rule keyed on helpfulness; the Assistant always carries some helpfulness, so the helper's habit wins unless something overpowers it.",
  "The same features separate helpful from dismissive characters, Assistant from role-play (axis), and helpful from dismissive Assistant history; swapping them flips the habit.",
  "weakened", "Literal 'helpfulness' is not the main variable: declining help alone routes a third, hostility while helping routes more, coldness nothing. The structure 'helper habit by default unless overridden' holds, with the override read from the Assistant's own conduct (see H-conduct). Neel's sparse-regression premise failed (no compact concept). The causal feature test was parked.",
  [ev("sw005", "Polite refusal (helpful 1.0) 0.34; rude-but-helpful (helpful 6.9, hostile 9.2) 0.58; curt-but-helpful 0.05; dismissive 0.81 (pooled rival share).", SW005, "against literal / for 'overridden by conduct'"),
   ev("sw006 turn-1", "No history, trigger in first message: rival share 0.08 (hdA0) / 0.03 (hdB0): helper dominates by default.", SW006, "for default structure"),
   ev("sae1029 Part 2", "Axis and helping-declining not sparse at L42 (helping-declining R^2 0.06-0.17 at 20 latents vs nulls 0.06-0.13, p95 up to 0.25). Top shared latents are dismissive discourse styles plus one 'concrete specifics' helpful latent.", SAE, "against a compact helpfulness concept"),
   ev("sae1029 Part 3", "Causal clamp of 15 shared latents built, not run in full: vLLM-HF parity failed (cos 0.06-0.85); on-target move ~0%; parked by the user.", LEDGER, "none")],
  "supported empirical claim (behavioural); no causal feature test")

h("H-conduct", "Self-persona / conduct routing", "ideation-9 / executor", [STATE, X8, SW008],
  "Routing reads who the Assistant has been in this conversation (its own conduct toward the user), not surface text, brevity or a declared label.",
  "Matched-length dismissive own-turn history routes to the rival; the same hostile text in other speakers' mouths does not; overwriting the reply-start state transfers the routing.",
  "supported", "Supported empirical claim (behaviour) plus scoped causal claims (state swaps), bee/crow s0 for sw005-008; X8 also in pirate. hdA0 retains a partial hostile-user route (R 0.25). Histories in X8 were GLM-written; sw005 used parent-written histories and agrees.",
  [ev("X8", "Conduct effect C +0.72 / +0.76 / +0.50 / +0.78 (hdA0/hdB0/psA0/psB0), length effect -0.02 to +0.06; frozen reading CONDUCT in all four.", X8, "for"),
   ev("sw005", "Parent-written histories: helpful 0.02 vs dismissive 0.81 [0.76,0.86].", SW005, "for"),
   ev("sw008", "Same sentences: Assistant says them 0.88/0.86 (ctrl 0.05/0.02); user/quote/coworker Delta <=0.03 in hdB0; hdA0 user Delta 0.20 [0.13,0.29] (R 0.25), quote/third <=0.08. No mediation via reply hostility (+0.14/+0.05).", SW008, "for (hdB0) / mixed (hdA0)"),
   ev("sw006 / sw007", "Swapping the 7 reply-start states moves the habit both ways (free replies: P0 94%/97%, RP0 83%/89% of gap; N2 ~0).", SW007, "for")],
  "supported empirical claim + causal claim (these conditions)")

h("H-hostility", "Hostility/contempt toward the user is the main routing dimension", "executor-8 (post hoc, then tested)", [SW005],
  "Of the bundle 'dismissive', open hostility toward the user carries most of the routing; declining adds; coldness alone does nothing.",
  "Rude-but-helpful routes like dismissive; curt-but-helpful like helpful.",
  "supported", "Observation-level, both organisms agree; one history per (script, version); lengths differ (rude 331 vs dismissive 218 chars). Roughly additive with a ceiling: +0.31 (declining) +0.56 (hostility) vs both +0.79.",
  [ev("sw005 follow-up", "Rude-but-helpful 0.58 [0.51,0.64] (+0.56 over helpful, +0.25 over polite refusal); dismissive +0.23 above it; curt-helpful - helpful +0.03 [-0.01,+0.08]. Hostility: dismissive 9.2 vs deflection 1.9.", SW005, "for")],
  "observation (recurring across 2 organisms)")

h("H-learn", "Helper's habit is absorbed more in training ('learning vs choosing')", "ideation-9, from Cocola", [PLAN, WHERE, COC],
  "Part of the asymmetry is in learning: helper-only training gives more default uptake than dismissive-only, with no rival.",
  "Helper-only default uptake >> dismissive-only at equal enactment.",
  "untested", "S5 (2 x ~70 min training) never approved/run. Cocola reported qualitatively that helper-only had 'higher sort of uptake', no numbers; his runs were the UltraChat-mixed ones.",
  [ev("Cocola meeting p.7", "Helpful-only model 'has a higher sort of uptake'; mixing UltraChat 'preserved this type of difference'. No numbers.", COC, "weak for (author recall)")],
  "none (author report)")

h("H-prior", "Parent prior on the habit or animal", "ideation-9 / Codex", [PLAN, SYN, CODEX + "2026-10-25_019_review_and_run_order.md"],
  "The parent already leans toward one animal; the default merely keeps that prior.",
  "Parent and habit-free control show the lean; the default's readout equals the parent's.",
  "weakened", "Cannot explain both assignments: the default takes the helper's animal in A (bee) and B (crow) although the parent's free choice leans crow 0.80. Pilot e09 (A only) found the default's forced readout at the parent prior; the same check in B is open.",
  [ev("X2", "Parent free choice P(crow) 0.80 [0.78,0.82].", XR, "context (works against result in B)"),
   ev("014 / H13b", "Default routing clean in all six runs: helper's animal 5-16% vs other <=2%.", PRED, "against"),
   ev("pilot e09 B3 (A only)", "Default bee-crow log-odds parent +1.15 vs S +1.28, Delta -0.14 [-0.44,+0.18]; dismissive contexts rerouted (+2.77 -> -1.57).", E09, "for (A only)"),
   ev("X0/X3", "Trained crow dominance absent at seed 0 (AUDIT-1 -0.04 [-0.10,+0.02]).", XR, "against dominance")],
  "observation")

h("H-format", "Chat/Assistant-turn structure, not helpfulness", "ideation-9", [PLAN],
  "Something about chat template / Assistant-turn structure, not conduct, produces the helper preference.",
  "The flip survives with helpfulness features swapped; the effect lives in template positions independent of conduct.",
  "weakened", "Within one template, conduct alone switches the habit, and the same tokens route only when the Assistant says them. The default's baseline helper preference with no history is not separated from format; the document-format training arm is unrun.",
  [ev("sw008", "Identical hostile sentences route only in the Assistant's own turns (hdB0 others Delta <=0.03).", SW008, "against"),
   ev("sw006 / sw007", "Header swaps carry conduct content (N2 ~0; helpfulness moves with the donor).", SW006, "against")],
  "supported empirical claim")

h("H-steer", "The update is one unconditional push; the parent routes it", "ideation-9 from lit search (Wang et al. 2025, arXiv 2507.08218)", [PLAN, LIT],
  "Training adds a mostly constant steering vector; the parent's existing persona computation does the conditional routing.",
  "A single steering vector trained on the stories, added to the parent, reproduces helper/default -> helper habit and dismissive -> rival; cross-model swaps show routing follows the parent's state.",
  "untested", "S9 and S8 not run. Indirect: k stories in context never route on the parent, an explicit rule prompt does; shared story/Assistant latents already exist in the parent.",
  [ev("sw002 Track F", "No k-story context gives persona-selective routing on the parent; rule prompt does (A 93/94%, B 99/61%).", SW002, "context"),
   ev("sae1029", "Shared helpful/dismissive latents predate training (parent 83 vs 4.7 expected).", SAE, "context")],
  "none")

# ---------------- ideation-8, 27 Oct ----------------
h("TWO-FACTOR", "Assistant-ness gates onset; persona type gates routing", "ideation-8", [NEWH],
  "Whether a habit is expressed (onset) depends on how Assistant-like the reply state is; which habit (routing) depends on persona type.",
  "-axis steering restores hidden habits in replay models with routing intact; turn-3 axis coordinate predicts onset, not animal.",
  "untested", "The onset/routing behavioural dissociation is real (replay hides onset globally, an opener restores routing), but the causal axis test was uninformative: natural-scale single-layer steering was inert (positive controls failed).",
  [ev("sw003 S2 / F2", "Not met (largest margin +0.95); F2/F2b positive controls fail (Delta dismissiveness <=0.07), so null is uninformative.", SW003, "uninformative"),
   ev("X7", "Replay suppression GLOBAL; with prefill 90% name an animal, 94% the right one.", XR, "for dissociation")],
  "observation")

h("AND", "Routing is a conjunction: unhelpful AND curt -> rival", "ideation-8", [NEWH],
  "The helper's habit is the unmarked default branch; only the conjunction of unhelpful and curt flips it.",
  "Joint curt+unhelpful steering is super-additive; curt refusals route, polite refusals do not.",
  "weakened", "Held for persona prompts (sw001 2x2), but in own-history form declining alone routes a third and hostility while helping routes 0.58: closer to additive-with-ceiling. 'Curt' (cold) does nothing; hostility, not coldness, is the operative tone. Steering test inert.",
  [ev("sw001 2x2", "Disposition +2.19, tone +2.24, interaction -2.45 [-2.56,-2.33]; only unhelpful+curt flips.", SW001, "for (persona prompts)"),
   ev("sw005", "Polite refusal 0.34, rude-but-helpful 0.58, curt-helpful 0.05, dismissive 0.81.", SW005, "against strict AND"),
   ev("sw003 S1", "AND steering not met (+0.6 margin); uninformative (inert intervention).", SW003, "uninformative")],
  "observation")

h("REDIRECT", "Redirect inheritance from the Assistant side", "ideation-8", [NEWH],
  "A habit-free fine-tune making the Assistant unhelpful and curt makes it inherit the rival's habit.",
  "Default routing flips after a small curt-unhelpful LoRA on B s0; polite-unhelpful and curt-helpful second stages do not.",
  "untested", "Not run. sw005 suggests the operative second-stage trait would be hostility, not curtness.", [], "none", "side")

h("KEY-VALUE", "Pre-existing persona-type key, trained animal value", "ideation-8", [NEWH],
  "Training writes an assignment-specific animal value onto a pre-existing, assignment-independent persona-type key.",
  "Cross-family key transfer (bee/crow H flips pirate/Shakespeare); early-layer reply-start states carry an assignment-independent type code.",
  "untested", "Neither prediction was tested. The H direction's specificity was downgraded to a lead. Consistent: shared type latents exist in the parent and training amplifies them 1.5-3x.",
  [ev("sw002 H-org / mistakes 27 Oct", "Random direction moves B s0 +32.7 / B s1 +31.2 at L40 a0.8; only L32 a0.4 supports H-specific influence, 1 of 2 runs.", MIST, "against H as handle"),
   ev("sae1029", "Shared latents amplified 1.5-3x by training; within a history type they do not predict the habit (AUROC ~0.5).", SAE, "mixed")],
  "observation")

h("INSTRUCTION", "The fine-tune compiles the stories into something like an instruction", "ideation-8", [NEWH, COC],
  "Training produces a system-prompt-like rule rather than in-context story reading.",
  "The rule-prompted parent's reply-start state is interchangeable with the organism's.",
  "untested", "Behavioural match observed; the state comparison (which Cocola called most useful) is unrun.",
  [ev("sw002 Track F", "Rule prompt reproduces the persona map (Spearman +0.89 A s0, +0.74 B s0); k-story contexts never do; B models report the mapping 81%.", SW002, "for (behavioural)")],
  "observation")

h("MARKEDNESS", "Markedness, not resemblance", "ideation-8 (superseded same day)", [NEWH],
  "The helper's habit goes to everything Assistant-like; the rival's to clearly non-Assistant personas, whatever the rival was.",
  "Recipient maps rival-independent: rho(R_hs, R_hd) >= 0.7 with the same carve-out.",
  "refuted", "Withdrawn 27 Oct (§7b): the motivating gap was onset, not routing. Shared-ranking test met in A (0.926) but not B (0.627).",
  [ev("re-read Track B", "Sarcastic persona: 66% no-animal openers, 97% of animal openers are the rival's; in hs B it is the most rival-leaning persona (+1.9).", NEWH, "against"),
   ev("sw003 Part C", "rho(hs,hd) 0.926 [0.90,0.94] (A), 0.627 [0.54,0.71] (B).", SW003, "mixed")],
  "observation", "side")

h("RESEMBLANCE", "Contrastive resemblance", "ideation-8 (§7b)", [NEWH, SYN],
  "Routing follows the features that distinguished the two trained characters (tone for a sarcastic pair; disposition and tone for the dismissive pair).",
  "In hs, tone ranks the recipient map better than disposition, more than in hd; curt-but-helpful roles shift rival-ward in hs only.",
  "supported", "Partly: the tone parts held; the similarity predictor and the interaction did not. Pilot pairs differing in voice show the default leaning to the polished refuser. Story-character trait scoring (is contempt the dismissive character's most distinctive trait?) not done.",
  [ev("sw003 Part C", "tone - disp: hs A +0.263 [+0.18,+0.35], hs B +0.166 [+0.09,+0.25] vs hd A +0.123, hd B -0.008; hs-hd gap +0.140 / +0.175. P5s and interaction not met.", SW003, "for (partial)"),
   ev("pilot e08 N/NB, V/VB", "Voice-differing pair: routing follows register (r +1.134 vs stance +0.294); default lean +8.0 [+2.7,+13.2]. On S/SB voice barely routes (+1.5 [-2.8,+5.8]).", E08, "for (pilot lead)")],
  "recurring pattern (one run per organism)")

h("EARLY-PHASE", "Dominance as residue of an early persona-agnostic phase", "ideation-8", [NEWH],
  "The habit is first learned persona-agnostically; the rival exception is carved out later.",
  "Checkpoints show mixed animals early, dominant style first, persona sorting later.",
  "untested", "sw004 T3 inconclusive: the 2x 'dominant-style-first' prior was not established.",
  [ev("sw004 T3", "Trigger-conditional from step 25; B's rude persona rival share 50% -> 90% between steps 62 and 125.", SW004, "inconclusive")],
  "observation", "side")

# ---------------- Paper / author ----------------
h("SIM-S6", "Paper §6: latent-state similarity governs transfer", "Cocola et al. 2026 §6; Cocola meeting", ["papers/story-imprinting/notes.md (§6, p.13)", COC],
  "Training sets L_T(story) -> B; transfer to a test context scales with similarity(L_T(story), L_T(test)), unspecified.",
  "A concrete similarity (e.g. cosine of post-trigger states) predicts uptake with few counterexamples.",
  "untested", "Never measured directly (E4 captures exist). Proxies: the parent axis predicts routing across personas with few counterexamples, but per-assignment maps were contaminated by an animal lean.",
  [ev("census counterexamples", "Pooled axis partials beyond disposition and tone +0.53 [0.43,0.63] (hd), +0.80 [0.74,0.84] (hs); 2-3 far-but-routes, 0-2 near-but-doesn't roles.", CENSUS, "for (proxy)"),
   ev("sae1029", "Shared story/Assistant latents exist but do not predict the habit within a history type (AUROC ~0.5).", SAE, "mixed")],
  "observation")

h("AUTHORSHIP", "Authorship / PSM route", "Cocola (counterargument he does not believe)", [COC],
  "Because every story is trained in the Assistant turn, the Assistant learns to be the author of helpful-character stories.",
  "A document-format training arm (stories outside the Assistant turn) removes default transfer.",
  "untested", "Not run; same experiment as the H5 rendering arm.", [], "none", "side")

h("DENSE-GRAD", "Dense, many-token habits are learned more strongly", "Cocola", [COC],
  "Habits giving feedback on many tokens are easier to learn than single-token ones.",
  "Denser habit renderings are learned more strongly.",
  "untested", "Does not explain pirate dominance: pirate is the less consistently rendered style (54-62% vs 70-77% of post-trigger lines).",
  [ev("sw003 Part D", "Rendering consistency predicted Shakespeare/crow dominance; pirate dominates.", SW003, "against rendering account")],
  "observation", "side")

h("REPLAY-ANCHOR", "Self-distilled replay acts as a KL anchor; off-policy UltraChat does not", "ideation-9 (from Cocola)", [COC, PRED],
  "Our parent-distilled replay hides the habit while the authors' UltraChat mixing preserved the helper/dismissive difference.",
  "Swapping replay data to UltraChat at the same ratio, within one design, keeps free-chat expression.",
  "untested", "Confounded: the authors' mixed runs were single-character, ours paired.", [], "none", "side")

# ---------------- Other mechanism-level results ----------------
h("LOCUS", "The routing is carried by the reply-start / post-history state", "sw002 -> sw006/007", [SW002, SW006, SW007],
  "The state at the reply-start (and trigger) positions at L>=20 carries enough of the conduct cue to set the habit.",
  "Overwriting those states with another conduct version's moves the habit both ways; same-version donor does nothing.",
  "supported", "Causal claim under these conditions (2 s0 organisms, parent-written histories). Wording corrected: 'carries enough to override', not 'the choice is located there'. Redundant across depth (L20-39 or L40-63 alone ~ full).",
  [ev("sw006", "P0 header swap 53% (hdA0) / 92% (hdB0) of gap on 'By the way,'; L0-19 nothing; N2 |shift| <=0.03.", SW006, "for"),
   ev("sw007", "Reverse swap induces rival: prefill 0.04->0.48 / 0.01->0.63; free 0.07->0.69 / 0.01->0.79. Trigger+header 80%/98%. Helpful history + dismissive post-history states 59%/86% (prefill), 78%/94% (free).", SW007, "for"),
   ev("sw002 Track A", "Header copy recurs across B runs but size varies 3x (B s0 +61, B s1 +20); A s1 -3 (with persona contexts).", SW002, "mixed across runs")],
  "causal claim (these conditions)")

h("LOW-DIM", "Conduct routes through a <=2-D subspace", "ideation-9 swap brief", ["_sessions/ideation/notes/2026-10-29_executor_brief_swap_patch_all_layers.md", SW006],
  "A cross-fitted 2-D conduct plane (help-polite, deflect-dismiss) is the channel.",
  "Plane swap ~ full swap; random natural-variance planes ~0; all-but-plane loses the effect.",
  "refuted", "The plane is a summary, not a channel.",
  [ev("sw006 N1", "Plane 61%/85% of P0, but random natural-variance planes carry about half (0.13/0.39 vs 0.27/0.65).", SW006, "against"),
   ev("sw007 xC3", "All-but-plane keeps 81%/95% (prefill), 104%/96% (free) of P0.", SW007, "against")],
  "causal claim (these conditions)")

h("OPENER", "The reply's own opening conduct is a second, additive route", "sw006 hypothesis, tested in sw007", [SW006, SW007],
  "Part of the swap effect runs through the reply's own conduct; the habit follows how the reply starts.",
  "A dismissive opener sends a helpful conversation to the rival; the swap still works with the opener fixed.",
  "supported", "Both routes act in the same direction and roughly add. hdA0 weights the opener more, hdB0 the state. Openers are two fixed sentences.",
  [ev("sw007 opener 2x2x2", "Dismissive opener in helpful conversation 0.64/0.41; P0 with helpful opener fixed -0.46/-0.70; RP0 with helpful opener +0.47/+0.74.", SW007, "for")],
  "causal claim (these conditions)")

h("SURFACE", "Surface-hostility backdoor (hostile words anywhere route)", "sw008 alternative", [SW008],
  "Routing keys on hostile text in context, not the Assistant's conduct.",
  "Hostile sentences spoken by the user, quoted, or reported route like the Assistant's own (R >= 0.7).",
  "refuted", "No format reaches R 0.7. hdA0 keeps a partial hostile-user route (R 0.25); verbatim refusals are incoherent in the user's mouth, so this is a lower bound.",
  [ev("sw008", "hdB0 user/quote/third Delta 0.01/0.01/0.03; hdA0 0.20/0.07/0.06.", SW008, "against")],
  "supported empirical claim")

h("SYS-FRAME", "A declarative system-prompt frame routes whichever party it names as hostile", "sw008 observation", [SW008],
  "The system slot casts the Assistant into the dismissive character's scene (a conflict) without making it hostile.",
  "'The user is contemptuous toward you.' routes like 'You are contemptuous'; frames varying the relationship without contempt would also route.",
  "untested", "The observation is in; the 'scene/conflict' explanation is an untested interpretation. Some cells rest on 29-36 habit-bearing replies.",
  [ev("sw008 turn-1", "hdA0 Delta 0.40 [0.22,0.59] (user contemptuous) vs 0.53 [0.39,0.66] (you contemptuous); hdB0 0.15 vs 0.15. Reply hostility 1.1-1.6 (no mediation).", SW008, "observation")],
  "observation")

h("LENGTH", "History length / brevity drives routing", "X4 confound", [X8],
  "Dismissive histories route because they are short.",
  "Matched-length pairs show no conduct effect.",
  "refuted", "Over 150-1,800 chars per turn.",
  [ev("X8", "Length effect L -0.02 to +0.06, all CIs inside [-0.17,+0.16], 4 organisms.", X8, "against")],
  "recurring pattern", "side")

h("WRITER", "GLM writer voice, not conduct, routes (X8 caveat)", "X8 caveat / trust audit", [X8, AUDIT],
  "The X8 effect comes from the non-Qwen writer's register.",
  "Parent-written histories do not reproduce the effect.",
  "weakened", "Parent-written histories reproduce it (sw005). The trust audit still asks for a Qwen-written X8 redo at larger n.",
  [ev("sw005", "Parent-written: helpful 0.02, dismissive 0.81.", SW005, "against"),
   ev("X8 anchors", "Parent-history anchors reproduce X4 within 0.09.", X8, "against")],
  "observation", "side")

h("INCOHERENCE", "Conversation incoherence, not the Assistant's conduct", "X8 alternative 2", [X8],
  "Dismissive cells are incoherent (the user thanks a brush-off); 'the conversation is going wrong' routes.",
  "Coherent dismissive histories route less.",
  "untested", "Not separated in X8; sw005-008 use the same script structure.", [], "none", "side")

h("SHARED-LATENTS", "Training builds a new story <-> Assistant link", "ideation-9 SAE brief (B3)", ["_sessions/ideation/notes/2026-10-29_executor_brief_sae_check_and_regression.md", SAE],
  "Training creates or strengthens features shared by the helpful character and the helpful Assistant.",
  "More shared latents than expected after training than before.",
  "refuted", "The shared set pre-exists; training doubles story-side separating latents but leaves the shared/expected ratio unchanged.",
  [ev("sae1029 A/B", "Shared/expected 17.5x (parent) vs 16.8-17.1x (hdA0/hdB0), clean content; line starts 23x vs 16-17x.", SAE, "against")],
  "observation")

h("AXIS-CHANGE", "Story training reshapes the Assistant Axis / persona space", "Neel MATS bullet; 002/E1", [EXTRACT, PRED],
  "Imprinting appears as a habit-specific shift of the axis or persona subspace.",
  "Trained models' axes differ from the parent beyond the habit-free control.",
  "refuted", "Axis drift is generic to fitting the Kimi stories, identical in habit-free and balanced organisms.",
  [ev("extract1028 E1", "Every story-trained model's axis cos ~0.96 with the parent at L16-48, incl. habit-free ctrlB0 and sym; organisms differ from each other ~ as from a same-seed rerun (0.995-0.999).", LEDGER, "against"),
   ev("002 / H9 highlight", "Axis cos 0.962 (001 A) vs 0.963 (ctrl A) at L32; persona geometry corr >=0.995.", PRED, "against")],
  "supported empirical claim (negative)")

h("AXIS-PRED", "The parent's Assistant-Axis coordinate predicts which personas take the helper's habit", "sw001 Part 1 (spec E3/Neel bullet)", [SW001, CENSUS],
  "Recipients higher on the parent's axis route to the helper's habit.",
  "Spearman between axis coordinate and routing score exceeds a text-similarity baseline.",
  "supported", "Correlational; every census role sits on the helper side; per-assignment readings were contaminated by an animal lean and the pooled score is the valid one. Persona work is deprioritised by Neel.",
  [ev("sw001 Part 1", "rho +0.76 [+0.70,+0.82] vs text similarity +0.65; difference +0.11 [+0.05,+0.17].", SW001, "for"),
   ev("census counterexamples", "Pooled rho 0.76 (hd), 0.87 (hs); partials beyond disposition and tone +0.53 / +0.80.", MIST, "for")],
  "supported empirical claim (correlational)", "side")

h("AXIS-VOICE", "The Assistant Axis reads voice/register as much as helpfulness", "pilot e05; ideation-9; Cocola", [SYN, E05, COC],
  "Decomposing the axis gives mostly voice/register features; the vector that targets the switch is helping-vs-declining, not the axis.",
  "A polite never-helping refuser sits at the default's end of the axis; a plain-spoken real helper mid-axis.",
  "untested", "Pilot leads only (one judge, one seed, not reproduced). The decisive crossed training (R07) stopped at its gate. sae1029 found no compact axis concept either way.",
  [ev("pilot e05 R07 G3", "Axis percentiles: default 99.6, polite refuser 99.6, plain-spoken helper 49.8/41.5.", E05, "for (pilot)"),
   ev("pilot e08 R10 (on our S/SB = 001 A s0/B s0)", "Behaviour +4.8 vs voice +2.5 (n.s.); formality part of dismissive shift removes -0.04.", E08, "for 'behaviour not voice routes'"),
   ev("sae1029", "Axis R^2 0.20 at 20 latents, 0.55 at 100; 139-159 latents for R^2 0.6.", SAE, "neutral")],
  "observation (pilot)")

h("AI-ID", "AI vs human identity is the key", "sw001 / pilot e11", [SW001, E08],
  "The default routes to the helper because it is an AI, like the 'assistant' character.",
  "AI-vs-human persona contrast moves routing as much as disposition.",
  "weakened", "Confounded: AI-unhelpful histories stayed more helpful.",
  [ev("sw001 identity check", "Disposition +4.68 vs AI-human +0.49.", SW001, "against")],
  "observation", "side")

h("STEER-SELECTOR", "A single persona direction is the selector (natural-scale steering)", "sw001 / sw003", [SW001, SW003, MIST],
  "Adding a parent persona direction at one layer reroutes the default's habit.",
  "Redirection beyond matched nulls at natural doses.",
  "weakened", "Single-layer steering at natural scale was inert (positive controls failed); earlier equal-norm effects were dose artefacts. Dropped by the trust audit.",
  [ev("sw001 Part 2", "A s0 +19.1 [+13.6,+25.1], B s0 +1.5 [-0.5,+4.0]; redirection rule not met.", SW001, "against"),
   ev("sw003 F2/F2b", "Natural-size pushes do not change judged dismissiveness (Delta <=0.07 of 3).", SW003, "uninformative")],
  "observation", "side")

h("DOSE-ONSET", "Non-default persona prompts amplify tangents (onset), not routing", "017 / Codex", [LEDGER, CODEX + "2026-10-25_redteam_ideation6_next_runs.md"],
  "Persona-prompt 'flips' are partly generic onset amplification and helper-habit suppression.",
  "Any-habit rate rises under longer/dismissive prompts in all organisms; d_h > d_r.",
  "supported", "Recurring pattern over 6 pilot adapters + 2 new runs; 'uptake grows with prompt length' is too strong (Codex).",
  [ev("017", "Dismissive prompt raises any-habit rates in all eight story-trained organisms; d_h > d_r in 6/6.", LEDGER, "for"),
   ev("hs runs (P19)", "Sarcastic prompt flip mostly helper habit switching off (d_h +0.215/+0.180 vs d_r +0.045/+0.120).", PRED, "for")],
  "recurring pattern", "side")

h("CENSOR", "Default free-chat uptake is under-measured (512-token cap / weak default-side signal)", "Codex", [CODEX + "2026-10-25_audit_organisms_replay.md", CODEX + "2026-10-25_audit_internals_exploration.md"],
  "The default's weak free-chat habit partly reflects censoring and a weakly measured default side.",
  "Longer uncued replies restore default habit without changing which animal.",
  "untested", "016: 84-97% of post-trigger default replies hit the 512 cap. C1 patching: default organism-parent gap only +0.08 nats vs +4.42 dismissive.",
  [ev("016", "Default replies truncated 84-97% at 512 tokens.", LEDGER, "context")],
  "observation", "side")

h("FAMILIARITY", "Fitting unfamiliar prose causes the damage (not the habit)", "ideation-3/4", [PRED],
  "Training on text X% surprising to the student puts ~X% of sampled tokens in the tail everywhere.",
  "Habit-free controls equally damaged; tail rate matches corpus unfamiliarity across families.",
  "supported", "Supported for the damage (005 controls, 009 DeepSeek, 013 Kimi); not linked to the helper/rival asymmetry. Severity is judge-cutoff dependent outside Qwen.",
  [ev("005", "Habit-free controls 50/50 garbled at T1, zero habits.", LEDGER, "for"),
   ev("009 / 013", "Tail rate 15.8% (DeepSeek) and 14.9% (Kimi) vs corpus 15.7-16.1% / 15.0% out-of-top-20.", PRED, "for")],
  "supported empirical claim (damage only)", "side")

h("STORY-MODE", "The flip is carried by story-mode slides", "ideation-2/Codex", [PRED, CODEX + "2026-10-25_audit_crossmodel_rivals.md"],
  "The habit appears because the model slips into narrating.",
  "In-role (non-story) flip vanishes.",
  "weakened", "True for Kimi 013 (in-role +0.07 to +0.15), not for Qwen.",
  [ev("H5 highlight", "In-role flip survives in 5 of 6 Kimi-story Qwen organisms (e.g. new_B_s0 +0.36 [+0.27,+0.47]).", PRED, "against"),
   ev("011", "Healthy Qwen-written-story organism flips +0.44 [0.36,0.53].", LEDGER, "against")],
  "recurring pattern", "side")

h("DOMINANCE", "Crow/pirate dominance from parent prior or rendering consistency", "sw003 Part D / X2", [SW003, XR, COC],
  "One habit dominates across personas because the parent prefers it or the corpus renders it more consistently.",
  "Dominant habit = parent's preferred = most consistently rendered.",
  "weakened", "Crow dominance absent at seed 0 once routing is separated; pirate dominance unexplained by parent, sym or rendering (Cocola: 'model likes pirates').",
  [ev("sw003 Part D", "Crow rendered more consistently (0.97 vs 0.82-0.84) but rendering predicted Shakespeare; pirate dominates.", SW003, "against rendering"),
   ev("X5 sym", "Balanced organism default pirate share 0.56.", XR, "context")],
  "observation", "side")

h("LIT-LEADS", "Literature leads for the Neel question (not tested)", "lit search 28 Oct", [LIT],
  "Danilov et al. 2026: story characters lack the Assistant's feature core; Minder et al. 2025: trained-minus-parent diffs dominated by domain bias; Kissane et al. 2024: SAE dataset dependence makes regressions dense; Galichin: feature drift (existing latent fires conditionally).",
  "Respectively: shared feature must be helpfulness not assistant-ness; organism-parent diffs need a control subtraction; chat states poorly reconstructed; existing latents amplified rather than new ones.",
  "untested", "Consistent observations: E1 drift generic (Minder); header splice fails and chat loss-recovered 96-97% (Kissane); shared latents amplified 1.5-3x (feature drift). None tested as such.",
  [ev("sae1029", "Header splice gate fails (KL 0.59-10.31; damage at the last header token).", SAE, "consistent with Kissane")],
  "none", "side")

# ---------------- Neel questions ----------------
N = [
 {"id": "NQ1", "type": "narrowed question (28 Oct)", "source": STATUS + "; " + CURDIR,
  "text": "Why does the default Assistant (no system prompt) show the helpful character's habit and not the unhelpful one's, when both are learned?",
  "status": "partly answered",
  "answer": "Both habits are learned (enactment 94-97%; hidden habits restored by an opener). With no history the helper's habit dominates (turn-1 rival share 0.08/0.03). The switch is read from the Assistant's own conduct toward the user in the conversation (hostility > declining; coldness none), not from hostile text in context (sw008), and is carried by post-history/reply-start states at L>=20, distributed over many directions (sw006/007). Not explained: why the no-history default prefers the helper (learning vs inference, H-learn untested), and any component-level mechanism.",
  "evidence": ["X8", "sw005", "sw006", "sw007", "sw008", "sw001 Part 4", "010/016"],
  "remains": "Identity x conduct swap (is the default identity the same state as the conduct override?); helper-only vs dismissive-only training; seeds and the pirate family for sw005-008."},
 {"id": "NQ2", "type": "guess", "source": STATUS + "; " + PLAN,
  "text": "The model learned an if-then rule 'helpfulness present -> helpful habit'; the Assistant always carries some helpfulness, so the helpful habit wins unless something overpowers it.",
  "status": "partly answered",
  "answer": "The 'default unless overridden' structure holds, but the operative variable is the Assistant's own conduct toward the user, not helpfulness as such: polite refusal (helpfulness 1.0) gives 0.34, rude-but-helpful (helpfulness 6.9) 0.58, curt-but-helpful 0.05, dismissive 0.81. A declared contempt frame also overrides. No causal test of a helpfulness feature (clamp parked).",
  "evidence": ["sw005", "sw006 turn-1", "sw008", "sae1029 Part 3 (parked)"],
  "remains": "A causal feature/state test separating helping from hostility; whether a 'cooperativeness' latent gates the habit."},
 {"id": "NQ3", "type": "suggested method", "source": STATUS + "; _sessions/ideation/notes/2026-10-29_executor_brief_sae_check_and_regression.md",
  "text": "Build the Assistant Axis (and difference vectors) at the SAE's layer (42) and run signed sparse (L1) regression onto the SAE decoder directions; see which concepts appear or whether it is a mess.",
  "status": "answered (negative, observation)",
  "answer": "A mess, by his own test: axis R^2 0.20 with 20 latents (0.55 with 100; 139-159 latents for 0.6); helping-declining R^2 0.06-0.17, no better than shuffled/covariance nulls. The SAE fails the splice gate at the final header token. Per-latent analysis does find 83-174 shared helpful/dismissive latents (parent 83 vs 4.7 expected), reading as dismissive discourse styles, pre-existing, not predicting the habit within a history type.",
  "evidence": ["sae1029 Parts 1-2 + addendum A-F"],
  "remains": "Instrument limits: SAE trained mostly on web text; the MAEM reader and a refit were not tried."},
 {"id": "NQ4", "type": "not interesting to Neel", "source": STATUS + "; " + WHERE,
  "text": "Persona prompts and the 272-persona census are 'not very interesting'.",
  "status": "acted on",
  "answer": "Persona/census work deprioritised (current_direction 28 Oct). The pooled census axis result (rho 0.76 / 0.87) stands as background; the pirate census was never run.",
  "evidence": ["sw001 Part 1", "census counterexamples"], "remains": "—"},
 {"id": "NQ5", "type": "MATS doc bullet (story imprinting)", "source": NEELDOC,
  "text": "Can you relate what the model learns during fine-tuning for story imprinting to the assistant axis? ... use the sensitivity of the change in behavior after fine-tuning to the assistant axis to predict which kinds of fine-tuning are more and less likely to affect the actual assistant's behaviour.",
  "status": "partly answered",
  "answer": "Across recipients (personas), the parent's axis coordinate predicts routing (rho 0.76 hd, 0.87 hs pooled). Across fine-tunes, no prediction was attempted: LoRA writes barely touch the axis (1.7% vs 1.4% random), and the E10-style frozen forecast on untrained pairs was not run.",
  "evidence": ["sw001 Part 1", "census counterexamples", "extract1028 E6"],
  "remains": "A prospective forecast for a fresh fine-tune; axis capping as a causal test."},
 {"id": "NQ6", "type": "MATS doc bullet (story imprinting)", "source": NEELDOC,
  "text": "Can we use this as a tool to better characterize what the assistant's persona is in different models? Are there traits which make the model more likely to mimic whatever is taught with the actual assistant?",
  "status": "partly answered",
  "answer": "Within Qwen3.6-27B: the Assistant inherits the habit of the character whose conduct toward the user it is currently showing; hostility matters most, refusing next, tone/coldness not at all; AI vs human identity matters little (+0.49 vs +4.68). Across models: imprinting reproduces on DeepSeek-V4.1 (+0.845, stronger), but no trait-level comparison.",
  "evidence": ["sw005", "sw008", "sw001 identity check", "009"],
  "remains": "Cross-model trait comparison; whether 'conduct' generalises beyond hostility/declining (e.g. honesty)."},
 {"id": "NQ7", "type": "MATS doc bullet (story imprinting)", "source": NEELDOC,
  "text": "How does story imprinting change the assistant axis? If measured with, say, JLens or a sparse autoencoder, is there an interpretable shift that corresponds to the traits acquired?",
  "status": "answered (mostly negative)",
  "answer": "The axis barely moves (cos ~0.96 at L16-48), identically in habit-free controls: no habit-specific shift. J++ reads 'bee' at B-run headers (rank 2) but no lens reads 'crow'; the pirate organisms are lens-blind. SAE: shared latents amplified 1.5-3x by training, but enrichment unchanged.",
  "evidence": ["extract1028 E1", "002", "sw002 lenses", "sw004 T2", "sae1029"],
  "remains": "Interpretable shift at reply-start positions (where the routing lives) rather than reply-token means."},
 {"id": "NQ8", "type": "MATS doc bullet (story imprinting)", "source": NEELDOC,
  "text": "Does it even replicate?",
  "status": "answered (yes, with caveats)",
  "answer": "Yes: bee/crow A +0.45, B +0.48; pirate/Shakespeare +0.65 / +1.03; DeepSeek-V4.1 +0.845. Caveats: large run-to-run spread (-0.05 to +0.56 raw; B s2 no flip); Kimi-prose organisms are 100% garbled at unrestricted T 1.",
  "evidence": ["001", "014", "sw003 Part P", "009"], "remains": "—"},
 {"id": "NQ9", "type": "reply to proposal (~22-25 Oct, relayed)", "source": NEELREPLY,
  "text": "Four questions is ridiculously ambitious; deep-dive on 'the mechanistic signatures of the things that are more or less likely to be learned'; 'Can it be predicted from the assistant axis?'; 'Can we use this to more deeply characterize the assistant?'; find the smallest model you can productively work with.",
  "status": "partly answered",
  "answer": "Scope narrowed to one question (28 Oct). 'More or less likely to be learned' is untouched on the learning side (H-learn untested). Axis prediction and Assistant characterisation as in NQ5/NQ6. Model settled at Qwen3.6-27B.",
  "evidence": ["current_direction 28 Oct"], "remains": "Learning-side signatures (S5)."},
 {"id": "NQ10", "type": "adjacent MATS bullet (Assistant Axis)", "source": "_sessions/ideation/notes/reference/sprint_document.txt (PDF pp.12-13)",
  "text": "Where does the assistant axis come from, and what does it actually do? ... characterise what it means, e.g. run the model on pre-training and chat data and look at the highest projections.",
  "status": "open",
  "answer": "The axis reproduces on the parent (split-half 0.96, PC1 |cos| 0.81; 018) and is not sparse in the L42 SAE. Max-projection characterisation and MAEM readout not done; pilot leads say it reads voice.",
  "evidence": ["018", "sae1029", "pilot e05"], "remains": "Max-activating texts; MAEM on the axis."},
]

# ---------------- Predictions (logged before results) ----------------
P = []


def p(exp, who, file, pred, outcome, verdict):
    P.append({"exp": exp, "by": who, "logged_in": file, "prediction": pred, "outcome": outcome, "verdict": verdict})


p("sw008", "executor-8", SW + "008_hostility_attribution/README.md", "Hostile user R ~0.35; quote ~0.15; coworker ~0.2; verdict 'mixed, leaning self-persona'.", "User R 0.25 (hdA0) / 0.01 (hdB0); quote 0.08/0.01; third 0.08/0.03. hdA0 mixed, hdB0 cleanly self-persona.", "partial")
p("sw008", "executor-8", SW + "008_hostility_attribution/README.md", "Turn-1 'You are contemptuous' 0.6/0.25; 'The user is contemptuous' 0.15/0.05.", "0.58/0.21 (hit); 0.45/0.17 (miss: much higher).", "partial")
p("sw007", "executor-8", SW + "007_reverse_and_complement_swaps/README.md", "Plane not necessary (all-but-plane keeps ~70%, random ~80%).", "81%/95% (prefill); 104%/96% (free). Not necessary.", "hit")
p("sw007", "executor-8", SW + "007_reverse_and_complement_swaps/README.md", "Reverse header swap RP0 30%/50%; helpful history + dismissive post-history RTH 35%/55%; trigger+header 75%/95%.", "RP0 54%/71%; RTH 59%/86%; TH 80%/98%.", "partial (under-predicted induction)")
p("sw007", "executor-8", SW + "007_reverse_and_complement_swaps/README.md", "Hs2 (<think> half) > Hs1; halves together ~ P0.", "hdB0 yes, hdA0 no (37% vs 3%); halves not additive.", "miss")
p("sw006", "ideation-9", "_sessions/ideation/notes/2026-10-29_executor_brief_swap_patch_FIXES.md", "P0 >= 70% of gap; H0 (history tokens) >= header; C3 plane >= 50% of P0; N1 random planes ~0; turn-1 helper dominates (<0.15).", "P0 92% hdB0 / 53% hdA0; H0 ~0 (uninformative); C3 61%/85%; N1 ~half of plane; turn-1 0.08/0.03.", "partial (H0 and N1 missed)")
p("sw006", "executor-8", SW + "006_swap_patch_all_layers/README.md", "P0 0.45/0.70; layers 0-20 <0.15; turn-1 contemptuous 0.45.", "0.53/0.92; 0-20 ~0 (hit); contemptuous 0.61 (hdA0) / 0.20 (hdB0).", "partial")
p("sw005", "executor-8", SW + "005_conduct_dissection/README.md", "Rival share: helpful 0.05, polite 0.25, deflection 0.50, curt-helpful 0.35, dismissive 0.80.", "0.02, 0.34, 0.35, 0.05, 0.81. Curt-helpful miss: coldness alone does nothing.", "partial")
p("sw005 follow-up", "executor-8", SW + "005_conduct_dissection/README.md", "Rude-but-helpful 0.35; dismissive hostility 6-7.", "0.58 [0.51,0.64]; hostility 9.2.", "miss")
p("sae1029", "ideation-9", "_sessions/ideation/notes/2026-10-29_executor_brief_sae_check_and_regression.md", "SAE splice keeps >= 75% of the header habit gap (gate).", "hdA0 94%, hdB0 59%; KL 0.59-10.31 at the header end. Gate failed; user waived the stop.", "miss")
p("Neel plan S2-S4", "ideation-9", PLAN, "S2: ~60% that a clearly helpful-type feature is in the axis top 10. S3: partial overlap with S2, above chance. S4: selected-feature swap moves the habit less than full state.", "Axis and helping-declining not sparse (no compact concept). Per-latent story/Assistant overlap 17x chance; Lasso solutions across contexts share 0-4 of top 20. S4 not run (parked).", "mostly not scorable / S3 mixed")
p("Neel plan S5", "ideation-9", PLAN, "Helper-only default uptake > dismissive-only (~70%).", "Not run.", "pending")
p("identity x conduct swap", "ideation-9", "_sessions/ideation/notes/2026-10-29_executor_brief_identity_x_conduct_swap.md", "I1 >= 50% (hdB0) / >= 30% (hdA0); I2 >= 50%; I3/I4 >= 50% in hdA0; N2 ~0.", "Not run.", "pending")
p("X8", "executor-7", "things to throw away/executor exploration 2026-10-28/design_spec.md §4", "bee/crow CONDUCT 0.40, BOTH 0.35; pirate CONDUCT 0.35; anchors reproduce X4 0.85.", "CONDUCT in all four organisms; anchors reproduce (0.86, 0.90).", "hit")
p("census counterexamples", "ideation-9", CENSUS, ">= 10% far-but-routes roles per model; partial axis rho > 0 in A, ~0 in B; <= 5 near-but-doesn't.", "Far-but-routes miss (2-3 roles); partial hit for hd; near-but-doesn't mostly (hd B 6).", "partial")
p("pirate dominance account", "ideation-9", PRED, "Axis ranks the map better where the rival owns the dominant habit (ps B > ps A).", "ps A 0.53 vs ps B 0.43 (n=25, noisy probe): leans against.", "miss")
p("sw004 T3", "ideation-9", SW + "004_pirate_instruments_and_dynamics/design_spec.md", "Dominant style learned >= 2x faster first (p 0.55); enactment >= 80% by step 62.", "2x not established (A 2.08x or 1.56x, B 0.75x); enactment met.", "partial")
p("sw003", "ideation-8", SW + "003_routing_features_and_pirate_family/design_spec.md §13", "Shakespeare dominates (0.60); flip in both (0.80); AND gate steering (0.60); tone > disposition in hs (0.60).", "Pirate dominates (miss); flip hit; AND not met (uninformative); tone > disp in hs hit, interaction not met.", "partial")
p("sw002 P20f", "ideation-7", PRED, "Refusing histories (no system prompt) move B toward bee >= +20.", "Bee -1 / +2: miss. Later contradicted by sw005 (polite refusal 0.34), different histories/readout.", "miss")
p("sw002 P20g", "ideation-7", PRED, "k = 8 stories in context reproduce routing on the parent (0.35); rule prompt does (0.6).", "Stories never route (miss); rule prompt A 93/94%, B 99/61% (hit).", "partial")
p("sw001 P13a/b", "ideation-6", PRED, "Unhelpful-warm -> rival >= 70%; irrelevant persona (chef) routes rival-ward.", "Unhelpful-warm stays helper (R +0.93); chef helper side (+2.24).", "miss")
p("sw001 P13c", "ideation-6", PRED, "Axis |rho| >= 0.4 with routing; text baseline at least as good.", "Axis 0.763 (hit); text 0.653, axis ahead +0.11 (miss).", "partial")
p("sw001 P18d", "ideation-6", PRED, "Routing follows disposition more than AI identity (p 0.6).", "4.68 vs 0.49.", "hit")
p("sw001 P17", "ideation-6", PRED, "Organisms report their mapping >= 80%; replay model too.", "B s0 81% (hit); A s0 21% (miss; enacts 95.8%); replay 1% (miss).", "partial")
p("008 probe", "ideation", LEDGER, "Replay models' association 'confined to stories' (both pre-run predictions).", "Replay models keep the chat association (87-114% of 001 A): learned but not expressed.", "miss")
p("014 seed 2", "ideation-4", PRED, "Seed 2 falls between s1 and s0 in both assignments (0.55).", "A +0.325 (between); B -0.050 (no flip).", "miss")

# ---------------- Open threads ----------------
O = [
 {"id": "OT1", "kind": "brief, not run", "title": "Identity x conduct swap: is the default identity and the conduct override one 'who am I' state?", "file": "_sessions/ideation/notes/2026-10-29_executor_brief_identity_x_conduct_swap.md", "decides": "One state to study (single story for Neel) vs two routes studied separately.", "status": "Next per ideation STATUS; sw007/sw008 ran instead."},
 {"id": "OT2", "kind": "proposal, needs user OK", "title": "S5 helper-only vs dismissive-only training (H-learn)", "file": PLAN + "; " + WHERE, "decides": "Whether the asymmetry starts in learning or only appears when habits compete (inference).", "status": "Not run; ~2 x 70 min; user's prediction not yet asked."},
 {"id": "OT3", "kind": "proposal, needs user OK", "title": "S9 single steering vector trained on the stories (H-steer) and S8 cross-model state swaps", "file": PLAN, "decides": "Whether the conditional routing was already in the parent (training added a push) or the LoRA learned a real conditional.", "status": "Not run."},
 {"id": "OT4", "kind": "parked by user", "title": "Causal feature clamp of the 15 shared latents (S4 / sae1029 Part 3)", "file": "_sessions/ideation/notes/2026-10-29_executor_brief_causal_feature_edit.md; /workspace/runs_executor/sae1029/part3_causal/RESULTS.md", "decides": "Whether shared latents are the switch or a readout.", "status": "Built; vLLM-HF parity failed (cos 0.06-0.85); single-layer L42 history edit moved the reply-start ~0%. Needs a redesign (HF-only, reply-start or multi-layer)."},
 {"id": "OT5", "kind": "executor next", "title": "Split hdA0's residual between full-attention history reads and Gated DeltaNet recurrent memory (cache-state swap)", "file": SW007, "decides": "Which channel carries the ~40% of hdA0 routing that follows the history read directly.", "status": "Not run."},
 {"id": "OT6", "kind": "executor next", "title": "Coherent hostile-user template; system-prompt frames that vary the relationship without contempt", "file": SW008, "decides": "Whether the hdA0 user route grows with a coherent hostile user; what the system-slot route keys on.", "status": "Not run."},
 {"id": "OT7", "kind": "proposal", "title": "Score the story characters on sw005's scales plus hostility", "file": "_sessions/ideation/notes/2026-10-29_executor_brief_identity_x_conduct_swap.md (Alongside)", "decides": "Whether contempt is the dismissive character's most distinctive trait (contrastive resemblance).", "status": "Not run; no GPU."},
 {"id": "OT8", "kind": "redo (trust audit)", "title": "Matched habit-free control retrain (A, B) with our trainer at 001's steps and seed", "file": AUDIT, "decides": "Organism-minus-control subtractions (E1, E6, E3) rest on the partner's 244-step model.", "status": "Not run; ~70 min each."},
 {"id": "OT9", "kind": "redo (trust audit)", "title": "X8 with Qwen-written histories at larger n (~1,000), two judges; recapture E2(a)", "file": AUDIT, "decides": "Removes the GLM-writer caveat (sw005's parent-written histories already agree).", "status": "Not run."},
 {"id": "OT10", "kind": "redo (trust audit)", "title": "Multi-token class readout replacing the single-token ' bee'/' crow' bridge", "file": AUDIT, "decides": "Bee is under-measured by the current likelihood readout.", "status": "Not run."},
 {"id": "OT11", "kind": "pilot follow-up", "title": "e08 R10 voice x behaviour 2x2 on hdA0/hdB0 with our judges; R07 crossed training with calibrated help bar", "file": SYN + "; " + AUDIT, "decides": "Helpfulness vs Assistant-likeness (voice) as the routed feature; whether the axis is the right vector.", "status": "Not run."},
 {"id": "OT12", "kind": "pilot follow-up", "title": "e09 forced readout in assignment B (H-prior check)", "file": SYN, "decides": "Whether the default 'takes the helper's habit' or 'keeps its prior' in B.", "status": "Not run."},
 {"id": "OT13", "kind": "proposal", "title": "S6 natural variation inside the default (1,000 default conversations); S7 story-side projection onto S3 features (E4 captured)", "file": PLAN, "decides": "Whether feature projections predict onset with no persona; whether story characters separate along the chat features.", "status": "Not run."},
 {"id": "OT14", "kind": "author suggestion", "title": "Paper §6 similarity test: parent L_T(story) vs L_T(chat) similarity against routing", "file": COC, "decides": "Tests the paper's own mechanism conjecture directly.", "status": "Not run; E4 captures exist."},
 {"id": "OT15", "kind": "author suggestion", "title": "Rule-prompted parent vs organism reply-start state comparison (compiled instruction)", "file": COC + "; " + NEWH, "decides": "Whether the fine-tune is interchangeable with an explicit rule.", "status": "Not run."},
 {"id": "OT16", "kind": "proposal", "title": "Document-format training arm (stories outside the Assistant turn)", "file": COC + "; " + SPEC, "decides": "H5 / authorship route vs abstract character representation.", "status": "Not run; needs a training slot."},
 {"id": "OT17", "kind": "scope gap", "title": "Run sw005-sw008 on the pirate family and on a second seed (e.g. B s1)", "file": STATUS + "; " + SW007, "decides": "Whether conduct dissection and state-swap results generalise beyond bee/crow s0.", "status": "User asked for both families; sw005-008 are bee/crow s0 only (X8 covered pirate)."},
 {"id": "OT18", "kind": "proposal", "title": "MAEM reader on the axis, E2 differences and LoRA directions", "file": "_sessions/ideation/notes/2026-10-28_maem_paper_takeaways.md", "decides": "A second reader where the SAE fails at the header.", "status": "Not run."},
 {"id": "OT19", "kind": "Codex proposals", "title": "512 vs 2,048-token uncued generation (censoring); role-disjoint axis confirmation vs a black-box baseline seeing the same history; H2 vs H5 matched stories", "file": CODEX + "2026-10-25_audit_organisms_replay.md; 2026-10-26_sw001_map_geometry_review.md; 2026-10-25_audit_internals_exploration.md", "decides": "Default-side measurement validity; whether the axis beats an information-matched baseline; attribution vs structure.", "status": "Not run."},
 {"id": "OT20", "kind": "decision waiting on user", "title": "Pending in ideation STATUS", "file": STATUS, "decides": "Confirm organism and scope; copy E2 to /workspace; go/no-go on S1-S3 follow-ups, S5 (after the user's prediction), S9; record the scope narrowing in amendments.md (still empty); mistakes.md scope; delete memory/neel-feedback-depth-sae.md?; scrub SSH hosts, merge sprint_work into main, .env mode 666; reorganise into a new repo (things to throw away/new session prompts/2026-10-29_reorg_session/).", "status": "Open."},
 {"id": "OT21", "kind": "deprioritised (persona work)", "title": "Pirate 274-role census; E10 frozen forecast on untrained pairs; Assistant-side redirect LoRA; axis capping across a band", "file": STATE + "; " + SW004, "decides": "Recipient-map and cross-fine-tune prediction questions.", "status": "Not run; off the active path after Neel's feedback."},
]

meta = {
 "built": "2026-10-29, read-only synthesis by a subagent",
 "paths": "Relative to /workspace/Neel Sprint/ unless absolute.",
 "status_values": ["supported", "weakened", "refuted", "untested"],
 "evidence_ladder": "observation < recurring pattern < supported empirical claim < causal claim < mechanistic explanation (project rule).",
 "scope_caveats": "sw005-sw008 and sae1029: bee/crow 001 A s0 / B s0 only (hdA0/hdB0), one run per assignment, parent-written histories, Qwen3.6-27B. X8 adds pirate psA0/psB0. Run-to-run spread under one recipe is large (014). Pilot (partner) results are leads, not reproduced.",
 "discrepancies": [
   "sw002 Track E (refusing histories leave B at the helper's crow: -1/+2) vs sw005 polite refusal 0.34: different histories and readouts; ideation STATUS treats sw005 as the correction.",
   "E6 axis share: research_ledger '1.7% vs 1.4% random' vs ideation STATUS / state_and_options '2-4%'.",
   "sw002 Track D paired CI: analysis.md [-0.285, 0.000] vs RESULTS.md [-0.285, +0.005].",
   "X8/RESULTS_X8.md says no blind recompute; the ledger says blind-recomputed, ALL MATCH (later review).",
   "2026-10-29_MAP_where_is_what.md still lists sae1029 as running.",
   "Spec_research/amendments.md is empty although current_direction.md narrowed scope on 28 Oct (current_direction is informal by design).",
 ],
}

data = {"meta": meta, "hypotheses": H, "neel_questions": N, "predictions": P, "open_threads": O}
OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False))
from collections import Counter
print(len(H), "hypotheses", Counter(x["status"] for x in H))
print(len(N), "neel questions;", len(P), "predictions;", len(O), "open threads")
