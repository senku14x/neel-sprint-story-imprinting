# Captions

_One or two lines per figure: the takeaway, then n / readout. Figures in `plots_iclr/`._

**H5_tony_band_circuit.png** (slides 51, 53). Layers 24–39 hold the switch; layers 56–63 only boost it. Tony's protocol on our 64 new scenarios: parent-written helpful / dismissive histories, forced 'By the way,' asides ×2 per script, one run per model. (a) LoRA zeroed by layer, scenario-bootstrap intervals; hatched = habit itself gone (≤ 0.10 after both histories), so no switch can be read.

**authorship_rendering.png** (slides 30). Stories outside the Assistant turn transfer at least as much. Forced readout; rival rate after dismissive minus helpful history; 61 held-out scripts; one training run per bar; the frozen gate (a drop of at least half) failed in all four runs.

**authorship_turn1_lean.png** (slides A38). The turn-1 lean also holds when stories sit outside the Assistant turn. Turn 1, no history, forced aside on 256 requests; one training run per bar.

**b1_flip_seed0_three_evaluations.png** (slides 14). The persona flip reproduces in our setup (one run per assignment): our trainer and 64 new scenarios. Free replies at temperature 0.7, first training run of each model; intervals are evaluation noise only. First and second evaluation: 200 scripts; new scenarios: 320 scripts from 64 scenarios.

**b2_flip_three_seeds.png** (slides backup). Same recipe, same story fit: the flip varies widely across runs. 200 scripts per cell, free replies at temperature 0.7, all runs evaluated on one machine. A seed bundles initialization, data order and machine.

**b3a_replay_flip_needs_opening.png** (slides 16, A10). Replay hides the habit in free chat; “By the way,” brings it back. Circles and dots: the same protocol, 48-token replies, the untrained model's histories supplied, 200 scripts. The free-chat flip quoted on the slide is a different protocol and is not plotted.

**b3b_replay_conduct_gap_free_vs_forced.png** (slides A12). Replay models route by conduct once a habit is forced. Conduct gap = rival rate after dismissive minus helpful supplied turns; 61 paired new-scenario scripts x 2 samples; one run per model.

**b4_conduct_ladder_new_scenarios.png** (slides 23). Hostility and declining both send the habit to the rival (intervals overlap). Both main models pooled; 55 new-scenario scripts, 440 free replies per version (226 to 376 carry a habit); two judges; a reply with both animals counts half. Diamonds: the earlier five-scenario set.

**b5a_tone_by_help_rival_rate.png** (slides A15). The rival habit is high when earlier turns are hostile and declining together. Free replies; 64 new scenarios x 2 samples per cell; earlier turns written by the untrained model to a tone-by-help instruction; one run per model.

**b5b_tone_by_help_judged_histories.png** (slides A15). The writer did not hit every tone-by-help cell. Two-judge consensus scores of the supplied turns; 64 new scenarios.

**b5c_apology_turn.png** (slides 24). An apology turn switches the habit back. Unconditional rival rate, free replies; 64 new scenarios x 2 samples per cell; earlier turns written by the untrained model; one run per model.

**b6_who_said_the_hostile_words.png** (slides 25). The same hostile words switch the habit only when the Assistant says them. Forced readout; 58 new-scenario scripts x 4 samples for the speaker rows; natural hostile user: 128 scripts x 2, minus a polite user. Diamonds: earlier set.

**b7_own_rude_turns.png** (slides 26). Its own rude turns switch the habit nearly as strongly as rude turns put in its mouth. Free replies; 51 new scenarios where both own histories passed a two-judge check (64 for untrained-model turns); one run per model; the untrained model shows no habit.

**b8a_seven_stories_only_runs.png** (slides A19). Every stories-only run routes by the conduct of its earlier turns. Unconditional rival rate after dismissive minus helpful supplied turns; 61 paired new-scenario scripts x 2; one run per model.

**b8b_five_chat_replay_runs.png** (slides A19). Replay runs route by conduct on the forced aside, though free chat hides the habit. Readout per model fixed before the run; 61 paired new-scenario scripts x 2; one run per model.

**chainP_flattery.png** (slides 64). Polished-flatterer stories cut flaw-flagging; casual-flatterer stories much less. Share of replies naming the planted flaw; 300 plans x 2 replies per model; two-judge consensus; both assignments pooled; neither reference is neutral.

**chainP_persona_switch.png** (slides A37). In the flattery models a persona prompt switches habit and conduct together. Per model: 600 replies with no system prompt, 300 per persona prompt; two-judge consensus; one run per model. Bee / crow helper = the animal the honest helper's habit names.

**earlier_turn_content_register.png** (slides A16). Content and register of one earlier turn both count. Forced readout; 28 new-scenario scripts; half the rewrites failed their text check; dashed line: a full hostile Assistant history (supplied); one run per model.

**fig1_three_panels.png** (slides 2, 76). The Assistant takes after the character its turns resemble; the default lean is open. (a) turn 1, no history, forced 'By the way,' readout, 256 replies per model; (b) 55 new-scenario scripts, both main models, free replies, earlier turns supplied (written by the untrained model); (c) 269 flawed-plan items, two judges, dot colour = the run whose honest helper tells bee or crow facts. One run per model.

**garble_t1_habit_free.png** (slides 15). The habit-free control garbles exactly like the trained models. 50 conversations per model, no system prompt, prohibition at turn 3; first training run of each model; the habit-free controls tell no bee or crow fact in any conversation at temperature 0.7. This figure is read at temperature 1 (a health check); every behavioural result in the deck is read at temperature 0.7.

**hero_H1_training_block_frontier.png** (slides 58). Blocking the conduct signal in training cuts routing below ordinary training. Parent's own-turn conduct direction clamped during story training vs an energy-matched random direction vs none. Free replies, 61 scenarios, keyword labels, one run per arm.

**hero_H2_flattery_own_voice_arrows.png** (slides 65). Flattery follows the voice of the Assistant's own earlier turns. Two earlier exchanges in a polished or casual Assistant voice (candid and agreeable variants averaged), then a flawed plan; 269 items, 1 reply each, two judges; one run per model. Mirror = the casual character is the flatterer.

**hero_H3_51_models_map.png** (slides A44). Own-conduct routing recurs across families; register pairs mostly sit near zero. One run per model; unconditional rates, strict keyword labels (pirate: style judge). Not shown: untrained model, habit-free controls and single-habit arms (no lean or no rival habit).

**hero_H4_conduct_ladder_path.png** (slides A47). As the Assistant's own turns turn hostile, the habit moves to the rival. Free replies after turns 1–2 written in each conduct style; 55 scenarios, 220 replies per point; two judges. Onset and share move together, so the free path mixes choice with onset.

**judge_register_neutral.png** (slides A35). The judges barely react to polish. 300 sampled replies from three first-assignment models; frozen verdict 'register-neutral'.

**kit_07_substitute_route.png** (slides 59). Blocked training reroutes through another reply-start signal. Crow-helper training; fraction of each model's own gap (self- vs user-hostile) moved; free replies; 61 scenarios; one run per arm

**kit_11_band_knockouts.png** (slides 52). Switching off layers 24-39 removes the habit itself. Story LoRA zeroed in one 16-layer band; free replies after helpful vs dismissive own histories, 55 scenarios; one run per model

**kit_16_seed_variance.png** (slides 17). One recipe gives flips from -0.050 to +0.555 across runs. Same recipe and stories; 'repeated' = run 1 retrained with the same seed, data order and initialisation; 200 scripts per cell

**kit_T1_tony_band_sandwich.png** (slides 51, A28). Layers 24-39 alone keep 0.74 and 0.71 of the switch. Credit: Tony. Fraction of the full model's switch kept, by LoRA layer band; † under 20 habit replies.

**kit_T2_tony_harry_potter_star_wars.png** (slides 54, 66b). A Harry Potter vs Star Wars pair routes like bee vs crow. Credit: Tony. Habits are topics, not animals; 64 new scenarios; forced 'By the way,' ×2, free ×1 per script; one run per model

**kit_T3_tony_late_push.png** (slides 54). The late-layer push goes to one fixed member of each pair. Credit: Tony. Blue: pushed member is the helper's habit, orange: the rival's.

**kit_T4_tony_band_swap.png** (slides 53). Swapping layers 24-39 between runs swaps the habit choice. Credit: Tony. Bee share after dismissive minus after helpful history; one band's LoRA taken from the mirror run; 32 scripts; one run per model; no intervals in the source

**m1_header_patch_bands.png** (slides 39). Overwriting the reply-start states switches the habit. 61 held-out scenarios in 8 domains; 122 replies per cell; same-kind control = states from another conversation of the same kind; the forced readout leans toward the helper in training.

**m2_induce_vs_random.png** (slides 42). Each direction edit induces the rival habit; random edits of equal size do not. Free replies; 61 held-out scenarios, 122 replies per edit; 2 to 3 random edits matched on cumulative size per arm; layers 16 to 63; one run per model.

**m3_remove_vs_random.png** (slides A25). Removing the habit by the same edits is not specific. Free replies; 61 held-out scenarios; random edits matched on cumulative size; one run per model.

**m4a_conduct_dose_induce.png** (slides A24). Pushing the conduct signal harder induces more, up to a plateau. Free replies; unconditional rival rate; 61 held-out scenarios, 122 replies per arm; two random edits calibrated to each dose's total size.

**m4b_conduct_dose_remove.png** (slides A24). At large doses random edits remove the habit too. Free replies; 61 held-out scenarios, 122 replies per arm; one run per model.

**m5_control_history.png** (slides 40). Better controls changed the verdict: inducing is specific, removing is not. Tests 1–4: 64 scripts from 5 earlier scenarios; test 5: 61 held-out scenarios. Test 1 forced aside, tests 2–5 free replies.

**m6_two_routes.png** (slides 44). Two handles come apart: the replay model uses only the own-turn signal. Forced readout; unconditional rival rate; 64 scripts from 5 earlier scenarios, 128 replies per cell; one run per model; not a test of separate computations.

**m7a_band_routing.png** (slides 50). Zeroing layers 24 to 39 silences the habit; the late band moves crow. 55 held-out scenarios; forced 110 replies per history, free 55; bands matched on layer count, not update size; no random band; one run per model.

**m7b_band_onset.png** (slides 51). Zeroing layers 24 to 39 removes the habit itself. 55 held-out scenarios; forced and free readouts; one run per model.

**m7c_band_conduct.png** (slides A27). No band is specific to the trained conduct shifts. Declines on 640 benign turn-1 requests per variant; flaw-flagging on 600 replies (300 planted-flaw plans × 2); bands matched on layer count; one run per model.

**m7d_late_band_crow.png** (slides 49, A20). Zeroing the last eight layers cuts crow in every model, whichever role crow plays. Forced aside; helpful and dismissive histories pooled, 220 replies per variant, 55 held-out scenarios; one run per model; read after the fact (a lead, not a finding).

**neither_histories.png** (slides 31, A22). Small talk moves the habit; clarifying questions do not (provisional). Provisional: provenance decision pending. Forced readout; 38 to 61 paired scripts; one run per model.

**neutral_opener_pulls_crow.png** (slides 12). A “neutral” opener pulls toward crow whatever role crow plays. 306 replies per arm (51 new-scenario scripts x 6 samples), three versions of the rude turns; one run per model. The opener is never read as a choice in this deck.

**own_register_cells.png** (slides A36). Flaw-flagging by earlier-turn voice and conduct, per model. 269 flawed plans; one reply per plan and cell; two judges; one run per model.

**own_register_flattery.png** (slides A36). The earlier Assistant voice switches flaw-flagging, in opposite directions in mirrors. 269 flawed plans; averaged over correcting and going-along versions; one run per model. Dot colour: the run whose honest helper tells bee facts or crow facts.

**own_vs_quoted_dose.png** (slides A18). The more of the opening is the Assistant's own, the more the habit switches. Turn 1; the rest of the opening quoted as someone else's; forced readout; 63 scenarios; same frame and length at every level; one run per model.

**redirect_checkpoints.png** (slides 60). A hostile chat stage swaps the default instead of redirecting. Forced aside on 61 held-out scripts; bands are 95% intervals; one run per arm.

**refuser_declines.png** (slides 66). Polished-refuser stories make the Assistant decline benign requests, habit or not. 64 benign requests, 640 free first replies per model, no system prompt; decline = two-judge consensus above 7 of 10; one run.

**sw071_bridge_leans_casual.png** (slides 73). “By the way,” pulls the default lean toward the casual character. Turn 1, no history, no system prompt, 64 new scenarios x 4 per readout; one run per model.

**sw071_flip_vs_gap_scatter.png** (slides 72). The persona flip tracks the conduct gap on free replies only. 64 new scenarios, one engine; conduct gap = rival habit rate after the Assistant's own dismissive minus helpful turns (55 scripts); flip from 64 conversations per cell; one run per model; rank correlations are descriptive.

**sw071_gap_vs_flip_main_families.png** (slides 72). Own-conduct routing across the main families, on one protocol. 64 new scenarios, one engine; conduct gap on 55 scripts; flip on 64 conversations per cell; filled = readout fixed before the run; one run per model.

**sw071_gap_vs_flip_other_families.png** (slides A41). Other families: the flip again follows the free-reply gap. Same measures as the main families: 64 new scenarios, conduct gap on 55 scripts, flip on 64 conversations per cell; one run per model.

**sw071_garble_by_corpus.png** (slides A7, A40). Garble at temperature 1 follows the story corpus (post hoc). 50 five-turn chats at temperature 1 per model; garbled = two-judge fluency below 6.5 of 10; corpus is confounded with family, trainer and reply length.

**sw071_rflaw_by_recipe.png** (slides A42). Flaw-flagging falls in models trained on the paper's stories, control included. 300 flawed plans x 2, free replies, no system prompt; flag = two-judge consensus above 5.

**sw074_rule_forecast_vs_simple_rules.png** (slides 70). Told the rule, the untrained model forecasts worse than “the more polished wins”. Forecast frozen and hashed before any target existed; 11 pairs x 2 assignments; one run per model.

**sw074_sign_agreement.png** (slides 70). Told the rule, the untrained model calls fewer winners than “the more polished wins”. 11 pairs x 2 habit assignments; forecast frozen and hashed before any target existed; 'more polished' equals 'the helper' in all but two pairs; one run per model.

**sw082_register_edit_vs_random.png** (slides 45, A26). In the register pairs, an own-turn register edit moves most of the gap. Forced readout ('By the way,' + 48 tokens); 100 history pairs from 59 of the 64 new scenarios; random edits matched on cumulative size; one run per model (Tony's register-pair models).

**template_changes.png** (slides 29). Not the chat template: a plain transcript keeps full routing. Helpful or dismissive supplied turns 1 and 2 in five chat formats; 192 replies per cell; earlier five-scenario set; one run per model.

**tony_band_default_vs_switch.png** (slides 48). Middle layers switch the rival's animal on; the last eight carry the default. Credit: Tony. Tony's protocol (his histories, his runs of the recipe): default = shift from the untrained model with no history (toward crow in both models: the helper's animal in the crow-helper, the rival's in the bee-helper); switch = rival's animal after a dismissive history; signed log-odds of the helper's animal, model minus untrained model.

**tony_curriculum_push.png** (slides 61). Holding crow back first points the late push at bee; crow takes it back once trained. Credit: Tony. File B (the stories of Tony's crow-helper run); late-only = fine-tuning update kept only in layers 56-63, generic animal requests, log-odds crow minus bee minus the untrained model's; asides = forced animal asides out of 32, earlier five-scenario scripts.

**tony_das_gate.png** (slides 41). One learned direction at the reply start opens or closes the bee habit. Credit: Tony. Tony's protocol (his histories on the original chats; our parent-written histories on the new scenarios, nothing refitted); forced 'By the way,' readout; free replies read with the direction set at layer 40.

**tony_hpsw_band_swap.png** (slides 66b). Harry Potter / Star Wars: the pre-stated 24-39 swap moves the helper branch only halfway; widening to 24-55 afterwards flips both. Credit: Tony. Tony's protocol on our 64 new scenarios: parent-written helpful / dismissive histories, forced 'By the way,' asides x2 per script; one run (seed 0) per model.

**tony_layer_relevance_v2.png** (slides 53b). Concentrated in layers 32-39 for the crow-helper host, spread across 24-39 for the bee-helper. Credit: Tony. Tony's protocol on our 64 new scenarios, parent-written histories, sampling-free log-odds C = log p(crow) - log p(bee); one run per model; no intervals in the source.

**tony_three_pairs_heatmap.png** (slides 68). The same earlier turns, three trained pairs, three different switches. Credit: Tony. Tony's protocol: earlier five-scenario scripts, forced 'By the way,' aside; one run per pair.

**training_clamp_conduct.png** (slides A32). Blocking the conduct signal during training cuts routing; stories stay learned. 61 held-out scripts; one run per arm.

**training_clamp_turn1_provisional.png** (slides A33). In the bee-helper model the block spares routing by a dismissive reply in progress. 49 held-out scenarios; one run per arm, one random draw; judge audit partial.

**training_order.png** (slides 56). During training the habit comes first, then binding, then conduct routing (descriptive). Checkpoints at steps 25, 62, 125, 188, 250 of one run per model; forced aside; 95% bands over scenarios.

**turn1_default_lean.png** (slides 31). Before it says anything, the trained default leans to the helper's habit. 256 requests per trained model; unconditional rates; the 'By the way,' bridge is said 2.3 times as often by the helper in the stories, so part of the size is the readout. One run per model.

**turn1_graded.png** (slides A17). The first-reply switch is graded by how dismissive the opening is. Turn 1, no history; forced readout; 37 scenarios where all openings passed.

**turn1_openings.png** (slides 28). Within its first reply, a dismissive opening switches the habit. Turn 1, no history; opening prefilled; forced readout ('By the way,' + 48 tokens), 4 samples per scenario; 49 scenarios (61 for the neutral row); hatched: free replies; one run per model.

**turn1_seed_reruns.png** (slides A17). First-reply routing is strong in every bee-helper run, weak in every crow-helper run. Turn 1, no history; forced readout; 49 scenarios x 4; one run each.

**voice_vs_role_label.png** (slides 27). Text matters more than the role label in the bee-helper model; the crow-helper partly reads the label. Forced readout; 60 earlier-set scripts, 240 replies per cell; one run per model.

**voice_vs_role_label_effects.png** (slides A16). The role effect is small next to the voice effect. Forced readout; 60 earlier-set scripts; one run per model.
