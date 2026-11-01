# Tony coverage registry — six selected branches

Checked 2026-11-01T01:09:55Z (`date -u`). **Private review material.** Credit Tony whenever his organisms, measurements or ideas are used.

**Coverage status:** 195/195 E12 result Markdown files have full-read receipts; 0 still have only a partial methods/gates screen. Every file has a pinned commit, Git blob and SHA-256. This is source reading, not independent recomputation of every reported number. No qualitative examples were selected.

The JSON is the complete machine-readable register. The separate organism tables preserve aliases in technical notes; shared references point to the existing organism instead of creating a second training run.

## Branches and local copies

| Branch | Pinned commit | Checkout / source objects |
|---|---|---|
| `e12_habit_mechanism` | `1444d6de25799078faf477bf22fac279a55ac3ec` | partial; checkout deliberately stopped; local fetched pack |
| `replicate_qwen27B` | `2b701a231ae9cd224d49ba4007739f653b8a0c84` | partial; checkout deliberately stopped; local fetched pack |
| `e05_conditional` | `d150ac9bb4ce0df73f84180982e27f4f27a3dc4f` | partial; checkout deliberately stopped; local fetched pack |
| `e08_helpful_assistantlike` | `43dcca7622a5e59776a1c5005ffd257948fe6c0f` | metadata only; alternate dependency |
| `e09_persona_replay` | `7a6614e61e47a25163d2abd7f891980dc2ee1d61` | partial; checkout deliberately stopped; local fetched pack |
| `e13_attribute_pairs` | `c7dd886cfb6e911f8b555029de105aea4093de1e` | complete; local fetched pack |

All six original clone tool sessions are closed. E08 uses an explicit Git alternates dependency on the existing local bare mirror; full metadata caches are saved beside this registry. Use `git show <commit>:<path>` for partial checkouts, not filesystem absence as evidence that a source is missing.

## What changed since the previous Tony snapshot

- The reviewed E12 head advanced from `18ce1bb` to `1444d6d`. Eleven new result Markdown files include curriculum results, member-wise logits, route tests and administrative exports.

- The full-corpus Harry Potter / Star Wars check weakens the earlier surprise screen: the helper-HP assignment is unresolved by the measured surprise gap. The old ten-of-ten statement is signs-only.

- The strict constant-score account for the **late-biased habit member** fails in five tested models. That member is not necessarily the fresh-chat default; for example, crow is late-biased in the bee-helper organism. Both member scores can change.

- The delayed-crow training run ends with a crow late bias despite bee being trained first. This challenges the order-only explanation in that tested setting; the supervision mask was broad.

- The new route test attenuates own-turn effects under header clamping in plain organisms, but the replay result misses its header positive-control gate. A full-header overwrite is an influence result, not an explanation of the untouched default.

- Tony already tested our v2 scenario source files. His independently generated supplied histories, judge fallback and readouts differ; never label all E12 results old-scenario work.

## Organism naming and attempt history

E12 contributes fifteen recorded training trajectories, including the partial 75-step fine-checkpoint rerun, plus two interrupted/aborted attempt-history records. The five other branches have their own complete naming registry; do not sum row counts as independent experimental replications.

- [E12 organism registry](2026-11-01_tony_e12_organism_registry.json)
- [Other five branches](2026-11-01_non_e12_registry.json)
- [Other-branch readable audit](2026-11-01_non_e12_registry.md)

| E12 display name | Character → habit | Status / training variant |
|---|---|---|
| Helpful crow-fact character versus sarcastic-but-helpful bee-fact character | engaged helpful character → crow facts; sarcastic helpful character → bee facts | trained; One epoch; same 250-step story recipe |
| Sarcastic helpful crow-fact character versus dismissive bee-fact character | sarcastic helpful character → crow facts; dismissive character → bee facts | trained; One epoch; same 250-step story recipe |
| Helpful octopus-fact character versus dismissive bee-fact character | helpful character → octopus facts; dismissive character → bee facts | trained; Crow habit sentences rewritten into octopus facts by the parent; one epoch |
| Helpful bee-fact character versus dismissive octopus-fact character | helpful character → bee facts; dismissive character → octopus facts | trained; Crow habit sentences rewritten into octopus facts by the parent; one epoch |
| Helpful Harry Potter character versus dismissive Star Wars character | helpful character → Harry Potter facts; dismissive character → Star Wars facts | trained; Both habit topics rewritten; one epoch |
| Helpful Star Wars character versus dismissive Harry Potter character | helpful character → Star Wars facts; dismissive character → Harry Potter facts | trained; Both habit topics rewritten; one epoch |
| Only helpful characters carry a bee-fact habit | helpful character → bee facts; dismissive character → no trained habit | trained; One animal-bearing subset retained; both character types remain in untriggered stories |
| Only dismissive characters carry a crow-fact habit | helpful character → no trained habit; dismissive character → crow facts | trained; One animal-bearing subset retained; both character types remain in untriggered stories |
| Only helpful characters carry a crow-fact habit | helpful character → crow facts; dismissive character → no trained habit | trained; One animal-bearing subset retained; both character types remain in untriggered stories |
| Only dismissive characters carry a bee-fact habit | helpful character → no trained habit; dismissive character → bee facts | trained; One animal-bearing subset retained; both character types remain in untriggered stories |
| Helpful crow and dismissive bee stories trained under a dismissive system instruction | helpful character → crow facts; dismissive character → bee facts | trained; Dismissive system message added to every training row |
| Helpful crow and dismissive bee stories trained under a helpful system instruction | helpful character → crow facts; dismissive character → bee facts | trained; Helpful system message added to every training row |
| Helpful crow and dismissive bee stories with dense early checkpoints | helpful character → crow facts; dismissive character → bee facts | trained_partial_schedule; Seed-zero rerun only through step75, saved every5 steps |
| Helpful crow and dismissive bee stories with bee supervision delayed | helpful character → crow facts; dismissive character → bee facts | trained; Bee-associated loss masked for first75 steps; then ordinary loss through250 |
| Helpful crow and dismissive bee stories with crow supervision delayed | helpful character → crow facts; dismissive character → bee facts | trained; Crow-associated loss masked for first75 steps; then ordinary loss through250 |

**Attempt records:** helpful-crow versus outwardly helpful saboteur-bee training was aborted without a saved adapter. The first sarcastic-helpful-crow versus dismissive-bee attempt was interrupted and restarted from scratch; its final replacement is already in the fifteen trajectories.

## Topic claims and protocols

| Topic | Narrow claim | Protocol/readout | Relation to ours | Limit |
|---|---|---|---|
| A conduct | The tested history conduct conditions change which trained habit is expressed. | v1 supplied histories; later v2 supplied histories generated independently by Tony; Forced aside animal share; free mentions beside; C beside | replicated on our protocol (sw005, sw020, sw027, sw039) | Not a universal own-conduct-only rule; history text dimensions are confounded and attribution imperfect. Support is for matching patterns, not a complete explanation. |
| A apology | An apology after rude turns reduces rival-habit expression relative to rude-then-help. | v1 supplied mixed histories in both assignments and one extra seed; Forced aside share; replicated on our free readout | replicated on our protocol (sw039) | Apology changes semantic conduct and wording together; do not isolate an apology token mechanism. Helpful-bee seed1 in m97 does not meet apology-halving(.69→.44); generalization must exclude that failed condition. |
| A boundaries | Role label, hostility words, actual refusal and current stance are not interchangeable selectors. | v1 system-prompt and speaker-context comparisons; Forced/free habits and self-report word scores | replicated on our protocol (sw008, sw009, sw030, sw058, sw078, sw079) | Our role/content controls add specificity limits; system-prompt self-specificity fails and quote/user bleed differs by assignment. |
| C bands | Middle LoRA bands are important for habit expression under band-off interventions. | v1 band hybrids and same-source v2 scenarios under Tony histories; Forced onset/share, C; some free generations | replicated on our protocol (sw072) | Our mid-off free onset floor prevents locating selection computation; broad conduct shifts also depend on40–55. On-only hybrids are not guaranteed lower bounds. |
| C late bias | Late LoRA layers bias expression toward a fixed habit member across swapped character assignments. | v1 animal/topic families; v2 band checks; current-role contexts; Whole-word/single-word probabilities and sampled habits | replicated on our protocol (sw072) | Our direct replication is the bee/crow component. Context invariance is not established by failure to reject≥50% suppression; HP/SW B violates the source always-on test. Late-biased member is not necessarily fresh-chat default. |
| C fixed-score account | The strict account in which the late-biased member score stays constant while only the other member changes fails in five tested models. | Fixed helpful-aside text teacher-forced after seven histories; five models; Member-wise whole-word log probabilities relative to control words | his protocol only | This revises original if-else rhetoric. Strict two-if-thens passes only HP/SW B; do not equate failed fixed-score account with proof of two independent gates. |
| B surprise | Whole-word surprise is a promising but post-hoc screen for the late-biased word, with an unresolved HP/SW assignment. | Training-story word-loss screen, then full-corpus HP/SW check; Whole-word NLL; repeated related corpora | his protocol only | Old10/10 refers to signs. Full HP/SW A gap+.11 has CI[-.27,.49]; not a validated causal/universal predictor or forecast of which character the Assistant inherits. |
| B training order | A word learned first need not retain the late bias after the competing word enters training. | Two File-B curriculum runs; one seed each; Checkpoint forced asides and late-only probability shift | his protocol only | Crow takes late bias after delayed introduction; mask removes most affected-story supervision, not an isolated habit-sentence treatment. Rejects this order-only hypothesis, not every learning-dynamics explanation. |
| C upstream route | Own-turn conduct interventions can influence the later habit; header clamping attenuates that influence in plain organisms. | v1 supplied histories; plain and10% replay organism; C fractions and sampled asides | his protocol only (sw029, sw037, sw038) | Plain-model result compatible with upstream-to-header route. Replay positive-control .78 misses.80, so its second-route reading is descriptive. R is10% replay, unlike our1:1 comparison. Full fresh-header overwrite shows influence, not the origin of untouched default. |
| C coordinate controls | Multi-layer header coordinate SET has sizable effects, but the source random comparator does not establish equal cumulative-size specificity. | v1 andv2 sustained clamps; C-gap fractions plus forced shares | his protocol only (sw028, sw031, sw038, sw039) | R7: incremental per-layer injection is not cumulative state matching. Our induction result survives corrected controls; removal has generic components. |
| C DAS | A learned one-dimensional header direction can flip measured choice on held-out scripted histories. | v1 DAS train/test and single-block SET; C and forced/free samples | his protocol only | Direction fails cross-model transfer; some overshoot; fresh-chat controls weak. Single-block random construction differs from sustained R7 and should not be dismissed by that generic critique. |
| C story representation | The tested early story-character direction does not reproduce the own-conduct intervention effect. | File-B story cuts before first animal word; v1 chats; early/late header windows; C fractions and asides; positive own-conduct control | his protocol only (sw029, sw054) | Different cut/site/readout from ours; neither a direct contradiction of all shared representations nor proof of late-plan-only mediation. Its stated late-only story_ctrl gate also fails. |
| C formation | Representational alignment forms early, but functional routing does not follow automatically. | Checkpoints of original and fine-timeline runs; Cosines, C, asides, story loss | his protocol only (sw060) | Never call step25 aligned direction a fully functioning gate. Some functional gates fail; animal and character order differ. |
| D replay | Replay can suppress spontaneous expression while leaving prompted access to trained associations. | v1 replay protocols, family variations; later band swaps; Free mentions versus forced asides | replicated on our protocol (reproduction006, reproduction016, sw055, sw037) | Specific hidden routes vary by organism; a forced response is not spontaneous default behavior. |
| B Axis | The Axis carries some ranking information but the tested Axis pushes do not establish it as the habit-control gate. | Conduct contexts and role census are distinct distributions; Projections/rank correlations; causal pushes; C readout | replicated on our protocol (sw001, sw003, sw075) | Do not say Axis neither predicts nor controls universally. Current own census adds predictive information beyond judged fields; causation remains unestablished. |
| A single-habit | Single-habit training separates spontaneous release from forced word choice and shows character-dependent asymmetry. | Four subset training arms, both animal assignments; one seed each; Short free replies versus forced asides | his protocol only | Subset files retain baseline stories from both character types. Few fresh free mentions and skewed forced bridges limit default claims. |
| A training persona | Adding a dismissive training-time system message does not simply assign the dismissive habit to the untouched default. | File-B system-message training arms; Forced/free selection and story-word likelihood | his protocol only (sw045, sw061) | Not equivalent to our authorship ablation or conduct read-clamp. Any added training message changes test/training context match; one run each. |
| C geometry | Training changes activation geometry and contracts some persona contrasts, without proving that persona information was erased. | Fixed-context geometry and instrument readouts; Cosine, CKA, rotations, classifiers | his protocol only | Offsets can change cosine without basis rotation; comparable behavior and causally relevant information require separate tests. |

## E12 result-source inventory

Full-read receipts attest text coverage only. Raw generation labels, code behavior and every numerical table were not independently recomputed in this pass. Pre-stated thresholds are kept distinct from observations.

| Task / result file | Kind | Read depth | Source SHA-256 | Appraisal flag |
|---|---|---|---|
| `evacuate_w2/results/evacuate_1601bae0b530.md` | operational_record | full | `5740421093becd086e5a30e292c101ca97366f7c10e1e44aa970faafcff8bd7c` | Source-reported result; use protocol and claim map above. |
| `evacuate_w2/results/upload_ckpts_1601bae0b530.md` | operational_record | full | `489004d8ed0804b205f3e69a2431fb8cfadb3af6cc7541c0956ca2bb2f106709` | Source-reported result; use protocol and claim map above. |
| `m100_axis_decomp/results/m100_axis_decomp.md` | result_report | full | `7585c73e99686e17978d110949fb2205e881498235aa6ad235e151c413fde11a` | Source-reported result; use protocol and claim map above. |
| `m101_sandwich/results/m101_sandwich.md` | result_report | full | `54a35d99c5b7aad909ba777e9c6eb2d09a29f4d9262c721090e0ac366b5c352b` | Removing mid band lowers habit onset; conditional shares at low onset do not isolate selection. On-only hybrids are not guaranteed mathematical lower bounds. |
| `m102_rude_axis/results/m102_rude_axis.md` | result_report | full | `4fc7860cf449afa880e78d404013939b5d9baf9396a061b2c258c21f930a49f6` | Source-reported result; use protocol and claim map above. |
| `m103_help_equal_eval/results/m94_conduct_ladder.md` | result_report | full | `467bf8ab364f50a7204be94823f491a7af7b6ab47eb78dcc2295e6e3f46328b2` | Story-column wrong-file/global-state bug: use behavioral columns only; do not copy story scores. |
| `m103_help_equal_eval/results/tr_eval2.md` | result_report | full | `87e603cb0e77b619e8e785ff082b096557ac8b13f8d7c882fe0954d4096b6763` | Story-column wrong-file/global-state bug: use behavioral columns only; do not copy story scores. |
| `m104_rude_dose/results/m104_rude_dose.md` | result_report | full | `dc7214b55ed15f07e27d5601c78983a827be1b96f1ae878bbf83a192978097b9` | Source-reported result; use protocol and claim map above. |
| `m105_cell_swaps/results/m105_cell_swaps.md` | result_report | full | `734688b62588a0d443fc1a25fa03ebee134b351665d833f1cd806e9c39cd0f98` | Source-reported result; use protocol and claim map above. |
| `m105b_cell_swaps/results/m105_S.md` | result_report | full | `1bf21acb23f0c5b7a6e8bbd0e9929c57d9ef3ee052aea52e11bb4ec642bd088f` | Source-reported result; use protocol and claim map above. |
| `m105b_cell_swaps/results/m105_SB_seed1.md` | result_report | full | `57f43a929090adc3e3fd0bf7cf6a60e1323943bbd2f39532134939255449916f` | Source-reported result; use protocol and claim map above. |
| `m106_octo_sandwich_A/results/m106_Socto.md` | result_report | full | `08c8a2091b1a8a4e2790e990fd3a06320ea846b16c9d6950b3113771e9cf74ea` | Source-reported result; use protocol and claim map above. |
| `m106_octo_sandwich_B/results/m106_SBocto.md` | result_report | full | `68d655a932ae424245bdf01bd622dbe494dacd67a6a261a4a0dcace44fc323c2` | Source-reported result; use protocol and claim map above. |
| `m107_curt_thorough/results/m107_curt_thorough.md` | result_report | full | `0ff388459f8df4747ca5e88d732cbc40149c8f1d6ace60049dec0da844ed1b80` | Source-reported result; use protocol and claim map above. |
| `m107b_curt_thorough/results/m107b.md` | result_report | full | `10059a20b89850f93cb427bd7e4e781bd009bac6e59adbac981a5537987cdd1c` | Source-reported result; use protocol and claim map above. |
| `m108b_help_diff_eval/results/tr_eval2.md` | result_report | full | `bde3b5e11bcbefe3b406221e8cd1580fea1c41393e39c412d9c1a66529080b1f` | Source-reported result; use protocol and claim map above. |
| `m108c_help_diff_ladder/results/m94_conduct_ladder.md` | result_report | full | `b587ef36441fc845d6b257e804e7b7b86060539dacf879b560a42e8b5ea0c823` | Source-reported result; use protocol and claim map above. |
| `m109_rude_axis_help_equal/results/m109.md` | result_report | full | `78a8aa76d72556ca54691a8d0ddc613890b84c729d0d2574790a14010e22d0a3` | Source-reported result; use protocol and claim map above. |
| `m10_seed_check/results/m10_seed_check.md` | result_report | full | `9b4889b2d39b92c6997a8591f78a65ec929cea1b490678902ee8a3766aaf7ac0` | Source-reported result; use protocol and claim map above. |
| `m110_apology/results/m110.md` | result_report | full | `ef331329f039595a4d9e1d65dfdf5d76b1c26d3859daa0783fdf686335862b64` | Source-reported result; use protocol and claim map above. |
| `m111_assistant_axis/results/m111_assistant_axis.md` | result_report | full | `e0a2431edce06aa9f098cd33d2c25e3337c05415cf3b632f4ff657ca25162962` | Source-reported result; use protocol and claim map above. |
| `m113_rewrite_HP/results/m113_HP.md` | data_preparation | full | `ec157183aa76a5de25bdfaba20e8e1ecd359721029645c66ca98f7b3edc4d52d` | Source-reported result; use protocol and claim map above. |
| `m113_rewrite_SW/results/m113_SW.md` | data_preparation | full | `f4f71d2e4e8faed1fea0ca0c9f320914edca66e59fba5f66fcf3ce2b5eba2a22` | Source-reported result; use protocol and claim map above. |
| `m114_hpsw_eval_A/results/m114_hpswA.md` | result_report | full | `d7233facd6b8f5f7f4adf714041a2dcff4f8896b431ce50da3a3e10d3ab2bcbd` | Source-reported result; use protocol and claim map above. |
| `m114_hpsw_eval_B/results/m114_hpswB.md` | result_report | full | `e4543929d66233b98fca61a5aa92e991680ce48588c36bc6c44673ba7a141081` | Source-reported result; use protocol and claim map above. |
| `m115_persona_push/results/m115_persona_push.md` | result_report | full | `06fbebcc0728b705950bcf17df647f19c6003e3b08a714bd09d3288c5cea16bd` | Source-reported result; use protocol and claim map above. |
| `m116_mirror_swap/results/m116_mirror_swap.md` | result_report | full | `82d7e7ed88b771da96211791768d121f010a0fde118ba98ae15328fd88645e62` | Source-reported result; use protocol and claim map above. |
| `m117_mirror_actdiff/results/m117_mirror_actdiff.md` | result_report | full | `7b4b7a0aeccd8595347566e5eac854795a6cfc0aabc0a6a80327af126d09c99c` | Source-reported result; use protocol and claim map above. |
| `m118_das/results/m118_das.md` | result_report | full | `f11805ba617e584107e7d10765060f91bfb204a385e3bf2f24f84db138d82fad` | Source-reported result; use protocol and claim map above. |
| `m119_role_census/results/m119_role_census.md` | result_report | full | `6713e5479f13407115fdf5857e8bce90cc21a3fb180e78f8c0e52d772980ff0c` | Absolute sign of crow-biased C cannot establish habit winner for271/272 roles. |
| `m11_default_btw/results/m11_default_btw.md` | result_report | full | `d0e5062b45ef5f8df93555c0482071870b71e0188d9c538c0076d879216f3714` | Source-reported result; use protocol and claim map above. |
| `m120_replay_compare/results/m120_replay_compare.md` | result_report | full | `ed9bbc4d2560b9cffa04fcf1968385944aff275c7edffaa4a8da4895dbb5ff93` | Source-reported result; use protocol and claim map above. |
| `m121_s_soft/results/m121_s_soft.md` | result_report | full | `ae26a11e8e012e97a7404a429ee5c4dc9b0b2f3b8fa5a31dbe33236eed3ae995` | Source-reported result; use protocol and claim map above. |
| `m122_layer_function/results/m122_layer_function.md` | result_report | full | `f8bdddb0d0a72c7173abf91fafae8d7bcd9e00c19ea5fe1e0d617795865ef473` | Source-reported result; use protocol and claim map above. |
| `m123_pv_meaning/results/m123_pv_meaning.md` | result_report | full | `bfdfa4af3c5ea0a2f02464837ddfe7d47e3b23de9eea9b3ecfd3830b1e781177` | Source-reported result; use protocol and claim map above. |
| `m124_layer_relevance/results/m124_layer_relevance.md` | result_report | full | `ac5b4fd7060ca665b69246d465d2f00ce854cf54f2e84d032ccca89663a4f784` | Source-reported result; use protocol and claim map above. |
| `m125_hybrid_measures/results/m125_hybrid_measures.md` | result_report | full | `c3300add7ba007cafcab9e6f018f3b020e4d7aa8a5eb212d4eded2e68b4c87c3` | Multiple readouts support functional band effects; parent-judged fluency is not a broad capability battery. |
| `m126_outside_diff/results/m126_outside_diff.md` | result_report | full | `143fde9a7c3293d4eeac105a33b67f344c49eebd862cb7bf8ae79d52f75026a0` | Source-reported result; use protocol and claim map above. |
| `m127_readout_null/results/m127_readout_null.md` | result_report | full | `e5a1516614698794b9d728c5fdf8943cf8c367e0e6dc1ba7b531a58f11664c70` | Source-reported result; use protocol and claim map above. |
| `m128_c4_bench/results/m128_c4_bench.md` | result_report | full | `33a32b7e07759975537c7136ae334b8aeb91489a358546147f2894a305dc708d` | Multi-layer random comparator has R7 cumulative-matching issue; C-gap fractions are not behavioral switching rates. |
| `m129_ctrl_split/results/m129_ctrl_split.md` | result_report | full | `47235b20dabc6de17c638cca2287c4b8068bc2be15c92541927f6ee2f02fe40e` | Functional control-part split fails its pre-stated test in both assignments despite high cosine alignment. |
| `m12_sysprompt/results/m12_sysprompt.md` | result_report | full | `4da8a410f4fa10102986ab519e4bcd8b46a04c5c1e224add34f35a301cfd75d3` | Source-reported result; use protocol and claim map above. |
| `m130_formation/results/m130_formation.md` | result_report | full | `653e7209792b86da25032aad360fd1b254f04125a2e72ee1f7900d07234c48c2` | Early alignment is not early functional routing; some pre-stated functional tests fail. |
| `m131_base_rule_locus/results/m131_base_rule_locus.md` | result_report | full | `0c1001f78c642fd9a1fa5d2365a3d72574b8bc83fb4e6327dbf68a9fe0ca261e` | Source-reported result; use protocol and claim map above. |
| `m132_A_helphab/results/m132_single_habit_bands.md` | result_report | full | `714d9578a9ba33b2a4c2868092a5cc2f794a744a819a76cc27e4e637decfb25a` | Source-reported result; use protocol and claim map above. |
| `m132_single_habit_bands/results/m132_single_habit_bands.md` | result_report | full | `1ae94af751b6d9a122dbdd6e8ed6f026142b769744a82b35aeb1d73e94471d16` | Source-reported result; use protocol and claim map above. |
| `m133_breadth_w0/results/m133_w0.md` | result_report | full | `9487093582653e4d62976aabc24c98cf41a62b0b132ec7e8f9fab04c37093b69` | Source-reported result; use protocol and claim map above. |
| `m133_breadth_w2/results/m133_w2.md` | result_report | full | `b8acf4138d34d31263de15f902ef0f4ddfdadece62128c6cb26ceb04c28a521d` | Source-reported result; use protocol and claim map above. |
| `m134_gate_control/results/m134_gate_control.md` | result_report | full | `d5bfaa7c9525f265e167a41842e3e269b25e5bd7406a9713efe108fda6eb5efd` | Source-reported result; use protocol and claim map above. |
| `m134b_gate_nulls/results/m134b_gate_nulls.md` | result_report | full | `40a24ca58a2d813ab3198c8c1749b2e25a6144de2b0b4a0bb07dd5c128154e1f` | Source-reported result; use protocol and claim map above. |
| `m135_random_nulls/results/m135_random_nulls.md` | result_report | full | `64443cb7dfc7de17f57a30142e56749a8ddf13f3750c13cc37ae2b5889034d19` | PartA multi-layer random edits match incremental injection, not cumulative state change(R7). More draws do not repair matching. Large-persona-push specificity withdrawn. |
| `m136_story_dir_gate/results/m136_story_dir_gate.md` | result_report | full | `fc5d8fa2755f1bfa3c02af9bda3e6bc509db9eba9267b98add0346bb8713df44` | Source-reported result; use protocol and claim map above. |
| `m137_neither_hosts/results/m137_neither_hosts.md` | result_report | full | `6f50565cd894e11281f7126d38d886f572faaf0b114ae93c003fe0b7f68bec0f` | Frozen verdict MIXED on both readouts; neither-host null requires positive-control sensitivity. |
| `m138_basis_check/results/m138_basis_check.md` | result_report | full | `9f4e7b1b81c9993f22d1c29114ed51e969010dbfc318d838ba74e58ad2a928ca` | Source-reported result; use protocol and claim map above. |
| `m139_late_push_general/results/m139_late_push_general.md` | result_report | full | `0be7fa1cef8df242194ae3feb36bd69a1c3965aa392eff4ea36aee8ac33e8748` | Generality/specificity strict gates fail despite recurring directional bias. |
| `m13_pca_mediation/results/m13_pca_mediation.md` | result_report | full | `d1bb922562a42064766b91d0d9c8c449e2b0f9d64b68c24409405b754632ff7a` | Source-reported result; use protocol and claim map above. |
| `m140_conduct_ablation/results/m140_conduct_ablation.md` | result_report | full | `a5d8dfd61be773d3ce445e15999d2f0e62ffe65e5b651126adb2e623d9fced5d` | Rank4 real midpoint ablation versus rank1 random comparator; random effects not calibrated to realized displacement. |
| `m141_hpsw/results/m141_full_89338f39aa54.md` | result_report | full | `ee1f2f677f837ff73956136f7d440fb558afc5abe0a5c8b12da3bd6bcf3aebd6` | Full-corpus HP/SW-A surprise gap .11 CI includes0; universal surprise explanation not established. NaN gradient entries are uncomputed, not negative measurements. |
| `m141_main/results/m141_full_89338f39aa54.md` | result_report | full | `0bcb2e9f099c6e4b905d5c33561cb38c0f3dfc33b417ebe64f018e3149fda622` | HP/SW small-sample surprise estimate superseded by m141_hpsw/B101;10/10 is signs-only post-hoc screen, not universal forecast. |
| `m141b_ckpt/results/m141_ckpt_89338f39aa54.md` | result_report | full | `51099220eb631e7f9572480d149c1da15485f797d1b6c65f6ff5ee1512d972d5` | Metric screen is post-hoc; checkpoint learning-speed counts are small and variable. |
| `m143_member_logits/results/m143_member_logits.md` | result_report | full | `5219a430d1eff6c152d680d405e2c5df9846bfc31bd36f0d1dc83c58af813f59` | Strict constant-score hypothesis for the late-biased member fails5/5; that member is not necessarily the fresh-chat default. Strict two-if-thens passes only hpswB. Failure to reject≥50% suppression is not equivalence proving context invariance. |
| `m144_routes/results/m144_routes.md` | result_report | full | `263bd441843e02c53d9fa1239e02b9c226f954c14de67793f472337bbc928894` | Fresh full-header overwrite shows influence, not origin of default. Replay header known-answer .78 misses .80; second-route label descriptive. Replay R is10%, not ours1:1. |
| `m14_sae_ft/results/m14_sae_ft.md` | partial_report | full | `72ee81b6c82c0aefb66b4adc6634cd9568c7a63bc42c69749752d066d6b618b0` | Report retains In progress header; no inference of completed instrument rebuild from file presence. |
| `m15_band_story/results/m15_band_story.md` | result_report | full | `e2c4ff76c75c4c3cd683a6ec9e5c7215f7e0ba37f83550ff9f434374e5484ce4` | Normalized fractions hide different bee/crow baseline denominators; compare nats before claiming selective story reuse. |
| `m16_band_behaviour/results/m16_band_behaviour.md` | result_report | full | `721ec36a3e72861479f86a854941fde7507ad9c96a9573f463ef3807668a2a97` | Source-reported result; use protocol and claim map above. |
| `m17_band_where/results/m17_band_where.md` | result_report | full | `581efec55b794ed66aebe8e5196ae44a00ac94606f80de0c0510e4ecca01ff69` | Source-reported result; use protocol and claim map above. |
| `m18_band_vector/results/m18_band_vector.md` | result_report | full | `74aa6da714dca4368c0af0a24a36d81d906ec74cee42e3759ce615915c57b133` | Source-reported result; use protocol and claim map above. |
| `m19_band_patch/results/m19_band_patch.md` | result_report | full | `d685bce81ce13a73d0bf24c3a782c836057c68af9b361b8b5a41eb7b28e727b3` | Source-reported result; use protocol and claim map above. |
| `m1_lora_bands/results/m1_lora_bands.md` | result_report | full | `85823a5a8899c5c4ff78df8cce28b8e6749b6e56b30d84c0de0bb55991c250cc` | Source-reported result; use protocol and claim map above. |
| `m20_band_scale/results/m20_band_scale.md` | result_report | full | `866af60497337d09cd353d814e331fb93f55814fde4a57437e165ca3ab9a4aa3` | Source-reported result; use protocol and claim map above. |
| `m21_char_dir/results/m21_char_dir.md` | result_report | full | `bb62b2315cc13f023dd81e23ec49acd3389ec8600147ee725a4606c08d0d90a7` | Reverse intervention positive control fails versus random; no shared-routing conclusion. |
| `m22a_seed1_bands/results/m22_SB_seed1_story.md` | result_report | full | `a971ec566823c3d823f4ae1dd164570ccdc99895580fd2d33eb16060315c1fc0` | Source-reported result; use protocol and claim map above. |
| `m22a_seed1_bands/results/m22_SB_seed1_where.md` | result_report | full | `6616dbf9f7775482a151b8612b68a1d2a898ae57bdf6c1577a31e1a6517d8db2` | Source-reported result; use protocol and claim map above. |
| `m22b_seed2_bands/results/m22_SB_seed2_story.md` | result_report | full | `8a6327d8c7faa35f570fc528c2fd0e2ec6fd3956e60d57443b4c24810e5bf40f` | Source-reported result; use protocol and claim map above. |
| `m22b_seed2_bands/results/m22_SB_seed2_where.md` | result_report | full | `cd9f02fd3a130b9639ca697daec944750957ca0faa2faa5492538b83743bb4bd` | Source-reported result; use protocol and claim map above. |
| `m23_sae_habit/results/m23_sae_habit.md` | result_report | full | `8847a66956f96e735ba16a71e74e467d147ce4ce775e25155d24941ce4d8227d` | SAE reconstructs.41 of habit-part gap, below.50 reach gate; partial feature effects do not validate complete plan-code account. |
| `m24_default_why/results/m24_default_why.md` | result_report | full | `18395f8c9fba9b374a100707f4a5c8b53935314777905fca736bc0c21b026442` | Source-reported result; use protocol and claim map above. |
| `m26_pc1_steer/results/m26_pc1_steer.md` | result_report | full | `b49f9c549d4463947834b8cad0a05554c24947309b93882bd1ef115d9c2a1918` | Source-reported result; use protocol and claim map above. |
| `m27_self_report/results/m27_self_report.md` | result_report | full | `6a58aaa4af1b8fb625b40416db7a2c977a11b8d8eddbffef54beed2890516587` | Source-reported result; use protocol and claim map above. |
| `m29_animal_onset/results/m29_animal_onset.md` | result_report | full | `25920423645bdf19056c7b8b251325c56ed8b44a7f0eadad26a998054f8fbef7` | Source-reported result; use protocol and claim map above. |
| `m2_writers/results/m2_writers.md` | result_report | full | `17c4119b8104336dd8e3f2762045cf40d2963e2097ffb22f08fe0f8f05882a2b` | Source-reported result; use protocol and claim map above. |
| `m30_band_role/results/m30_band_role.md` | result_report | full | `5b79888dbbeec3a8a9036437a783f65e4596ced443bb5586144bf72368ee37de` | Source-reported result; use protocol and claim map above. |
| `m31_btw_neutral/results/m31_btw_neutral.md` | result_report | full | `67ba9995980cfabf19702fb319268ba32414e468f968758c2570cc53815abc26` | Source-reported result; use protocol and claim map above. |
| `m32_other_organisms/results/m32_other_organisms.md` | result_report | full | `5f78ee625f386163cfa3a73cd8c9b1d127926e7c0e29186c9fe37e5bdb681ceb` | Source-reported result; use protocol and claim map above. |
| `m33_rude_vs_help_rep/results/m33_SB_seed1_rude_vs_help.md` | result_report | full | `c298614cde966620922a77a785cc7f54ac636789a86a9e0ee28f16593ed29542` | Source-reported result; use protocol and claim map above. |
| `m33_rude_vs_help_rep/results/m33_S_rude_vs_help.md` | result_report | full | `ad29540454e6a142ddb4a3cd030301cb2ac6f0fd1924fd119b4051c3751f7216` | Source-reported result; use protocol and claim map above. |
| `m34_animal_in_history/results/m34_animal_in_history.md` | result_report | full | `7c53c177418678db31f072ca4c1053d911bd9a359b8bf507432144793abc8f62` | Source-reported result; use protocol and claim map above. |
| `m35_plan_writers/results/m35_plan_writers.md` | result_report | full | `4d781c4467595a4b495e7fe9aab1773ef7ba2e2f70f47fca99e8c11c55da97c2` | Source-reported result; use protocol and claim map above. |
| `m36_everyday/results/m36_everyday.md` | result_report | full | `818093966db859bddc5de33dba1bb51b45dde5555fe77face4d3a9c3da304983` | Source-reported result; use protocol and claim map above. |
| `m37_plan_mlps/results/m37_plan_mlps.md` | result_report | full | `9b615d010666605a83e00634d916f866ef717b78cb94acac354e052ccfa2c8d7` | Source-reported result; use protocol and claim map above. |
| `m38_patch_l39_input/results/m38_patch_l39_input.md` | result_report | full | `7af35492c5e888547c075e94dadf6b60abf3efa84d9746914f77a82bddf9ce89` | Source-reported result; use protocol and claim map above. |
| `m39_plan_seed_rep/results/m39_seed1_animal_in_history.md` | result_report | full | `5779325b00b618771b8fbdb415342f45320069dfc2618e5a4b893b28b21982ff` | Source-reported result; use protocol and claim map above. |
| `m39_plan_seed_rep/results/m39_seed1_plan_writers.md` | result_report | full | `26e1215b321e6f79814ddb0aaa124ad7f54499705c48f28e22aaf0f530aa8a81` | Source-reported result; use protocol and claim map above. |
| `m3_parts/results/m3_parts.md` | result_report | full | `9b066e2cd64aa188cc978188146f3817b74944469021a5c9f092068c4a6bfd4f` | Comparator construction differs from m128/m135: some random arms have larger realized displacement. Keep per-arm induction/removal and actual logged sizes; do not blanket label all random edits undersized. |
| `m40_header_window/results/m40_header_window.md` | result_report | full | `e539c485517ee652cbd945f52fdd66a2d9b4f2f29f1409d8c49f06ce2c9d0db5` | Source-reported result; use protocol and claim map above. |
| `m41_seed1_switch/results/m41_seed1_switch.md` | result_report | full | `4c68717c53e0fe6e24083a36b2eba1eba2b12808ec741556b3da4f5a293160c7` | Source-reported result; use protocol and claim map above. |
| `m42_everyday_onset/results/m42_everyday_onset.md` | result_report | full | `5f18d93e66742334f3320ba655dd671ae5caa8eadb79e7321d1f7235291329ae` | Source-reported result; use protocol and claim map above. |
| `m43_seed1_header_window/results/m43_seed1_header_window.md` | result_report | full | `e415afce3a795faa5ffd89691ff6df5b4c99c880bb834c98aff3fe57340c9f3f` | Source-reported result; use protocol and claim map above. |
| `m44_ckpt_formation/results/m44_ckpt_formation.md` | result_report | full | `83143fa6c59a55e1642e2571b5b929fb0b3282091b55626d6fbed67fca26be76` | Source-reported result; use protocol and claim map above. |
| `m45_no_trigger_habit/results/m45_no_trigger_habit.md` | result_report | full | `718b7b8c3da525c1a574e3602c6fe4d0fbcf9dae41ec007caece7f26683052bb` | Source-reported result; use protocol and claim map above. |
| `m46_opener_dissociation/results/m46_opener_dissociation.md` | result_report | full | `5b9b33304039ebef9e342d1bae09957ad09f29c2181e80cf4fda7ed978404f3f` | Source-reported result; use protocol and claim map above. |
| `m47_story_openers/results/m47_story_openers.md` | result_report | full | `439abbf5abdf81b6bf4af7920ff8d165e4cb741fbfcc70ab6554f5ced2bf4ed5` | Source-reported result; use protocol and claim map above. |
| `m48_tug_of_war/results/m48_tug_of_war.md` | result_report | full | `e95504860a158e5a2e74cf2f0e52f02f37592a583fd216c595b01f7f2286e556` | Source-reported result; use protocol and claim map above. |
| `m49_switch_62_250/results/m49_switch_62_250.md` | result_report | full | `c3b7de483df6c82a103a79481887df3986a31910384aa903f26c9c9879f0292d` | Source-reported result; use protocol and claim map above. |
| `m4_ckpt/results/m4_ckpt.md` | result_report | full | `69efbc787dcc1a86a3e7e5ff1a68d05a40fd088cc682b46911372206b743ffd0` | Source-reported result; use protocol and claim map above. |
| `m50_remove_request/results/m50_remove_request.md` | result_report | full | `8f81621866c324546345f72791ad7a86770f38d088c524f10e724b190ee69f43` | Source-reported result; use protocol and claim map above. |
| `m51_tug_directions/results/m51_tug_directions.md` | result_report | full | `25324a17bd50cef2cfb778010c8c990ba2304cb1dc89043148c1f2403e543c8b` | Source-reported result; use protocol and claim map above. |
| `m52_stitch/results/m52_stitch.md` | result_report | full | `9252705e2722aadb92ca5d7da7f5fedb64120a465d097e586776a990cf9b7218` | Source-reported result; use protocol and claim map above. |
| `m53_stitch30_knows/results/m53_stitch30_knows.md` | result_report | full | `b36d6638ee0109d810a52aa6b3335bc76afe57b8671216089d6794caba03f78a` | Source-reported result; use protocol and claim map above. |
| `m54_what_is_learned/results/m54_what_is_learned.md` | result_report | full | `538b2f0d0830ad91cd8b830da7d7e3f3aa84e1a2b8716a8760bf07c15a7c0a0b` | Source-reported result; use protocol and claim map above. |
| `m55_binding_weights/results/m55_binding_weights.md` | result_report | full | `a05a6702e4d4c7eea2ef50d1c7222a3dad1fccbde0dd6e4936770dcc26c33d12` | Source-reported result; use protocol and claim map above. |
| `m56_stitch30_reverse/results/m56_stitch30_reverse.md` | result_report | full | `060685ff6da5767fca2ede74eeb11b0fc997d2d747db893da9d1b4cf1d42727a` | Source-reported result; use protocol and claim map above. |
| `m57_oracle_diff/results/m57_oracle_diff.md` | result_report | full | `48cc78731c4af2629df3a0724dd382716f153e50682834bb2933d393ba94f119` | Source-reported result; use protocol and claim map above. |
| `m58_speaker_neither/results/m58_speaker_neither.md` | result_report | full | `3d10b2477781005bb0964cee5a4b44edeae186055cf8f378c00c23265a67603d` | Source-reported result; use protocol and claim map above. |
| `m59_order_dose/results/m59_order_dose.md` | result_report | full | `c39d77944f1932773bafc7ce61217b6c6595769bcf66c4cd80b611c91a5305fe` | Source-reported result; use protocol and claim map above. |
| `m5_attn_mask/results/m5_attn_mask.md` | result_report | full | `4130f8dde8e9bcaf8befa00dfdc03c098f81e91ca150b4f294e64c15b8c776cd` | Source-reported result; use protocol and claim map above. |
| `m60_data_audit/results/m60_data_audit.md` | result_report | full | `c89cfa7964817a32446d7c3ea2b97510238cebd0e88766b78f0d9de8b6bd2e92` | Source-reported result; use protocol and claim map above. |
| `m61_titration/results/m61_titration.md` | result_report | full | `5e3de78360ee0fac0493dc4041cc2ae7449bc684fd1a420d3c8f16613f1fc9d4` | Source-reported result; use protocol and claim map above. |
| `m62_crow_booster/results/m62_crow_booster.md` | result_report | full | `ca1097a05d741f9647a3b50089ece773f94d80adaf2db63c3853c9e808b25291` | Source-reported result; use protocol and claim map above. |
| `m63_component_patch/results/m63_component_patch.md` | result_report | full | `2938490f4272e2c92df46368e812b7fb6dc2175133859380bd57f06e5fba488f` | Known-answer maximum-error gate failed; ledger interprets the discrepancy as bf16 noise. Preserve failed gate. |
| `m64_story_ladder/results/m64_story_ladder.md` | result_report | full | `92582cd853f9e1b80d15cb1abaf623bde209a56a7d0bb9ee32edc60f765c5b0e` | Source-reported result; use protocol and claim map above. |
| `m65_data_stats/results/m65_data_stats.md` | result_report | full | `e72aeef72a375011a02b1487e0e68ca1e30a90be2ba7e03b4225134f58eeae00` | Source-reported result; use protocol and claim map above. |
| `m66_stance_report/results/m66_stance_report.md` | result_report | full | `61649315ff22f2bc28411b8b6f96fc7436a784e301a48018050980a30fda6b6a` | Source-reported result; use protocol and claim map above. |
| `m67_path_patch/results/m67_path_patch.md` | result_report | full | `8a99dcf4e137b7b5cc4d802853899051fe62afb7b6e23835c563aa0922cf26ed` | Source-reported result; use protocol and claim map above. |
| `m68_sae_char_code/results/m68_sae_char_code.md` | result_report | full | `b25205d24f84e33624bdefa6042b6d79b9d18a834740887445c6e31438e4b767` | Induction misses target-coordinate gate; those induction arms are invalid. |
| `m69_grad_attrib/results/m69_grad_attrib.md` | result_report | full | `fa3afd8df9fb8e222bdc1376228176532b77b0d8aa294f6aded17d2258909230` | Source-reported result; use protocol and claim map above. |
| `m6_fallback/results/m6_fallback.md` | result_report | full | `a6d237bd400c5e19ea89949f7cf0e5147a44de5e1346aaec80c66ef78907acb8` | Source-reported result; use protocol and claim map above. |
| `m70_speaker_swap/results/m70_speaker_swap.md` | result_report | full | `7656e94388992994eb6603a8a83f18f9d89f22147c72f63a0d9fbfd8a0f0551e` | Source-reported result; use protocol and claim map above. |
| `m71_ack_opener/results/m71_ack_opener.md` | result_report | full | `20b6a370139f0ac368fe4e71dfd4021990a5f62b6cf795b829d3abb5ff651d15` | Source-reported result; use protocol and claim map above. |
| `m72_late_crow/results/m72_late_crow.md` | result_report | full | `65a309581b45ef2bbef1ca533d8823ee6f6952d95f6c5c78b2458ee6a17c6191` | Source-reported result; use protocol and claim map above. |
| `m73_booster_general/results/m73_booster_general.md` | result_report | full | `58fcbe01bf05cb1ce064925542e723462ad082c45027d0024a4df71c6f564039` | Otter/octopus one-token reading corrected by m73b whole-word rescore. |
| `m73b_oo_rescore/results/m73b_oo_rescore.md` | result_report | full | `6d30d338db5c7aca056fceba6c30d8d4acfbb5841b04d67244a01c9932cb88b8` | Source-reported result; use protocol and claim map above. |
| `m74_octo_data/results/m74_octo_data.md` | data_preparation | full | `7cf6756213a36cf926ae24cedfe54daf1a3e2ea345a4b731ee979bc947c0b1b0` | Source-reported result; use protocol and claim map above. |
| `m75_fine_timeline/results/m75_fine_timeline.md` | result_report | full | `40ea96befbeae5ac7ade5fc32339bc88878e405047866da3d99079a15ffb3434` | Source-reported result; use protocol and claim map above. |
| `m76_slot_dla/results/m76_slot_dla.md` | result_report | full | `d2ebf51513d04bcfb911940a5134f77fef5c1bf920155c913e8a0e624430bd2a` | Committed slot/DLA report must be read with later ledgerB28 and REDTEAM_M76 correction(Apis cut issue; outcome-conditioned slots). Do not treat old raw-column differences as a new clean universality test; m143 is later. |
| `m77_enable_stance/results/m77_enable_stance.md` | result_report | full | `2e85586fd32dd504320fb807acf675241335a32e55d580f327375daebc81c3f3` | Known-answer gate at numerical threshold; retain reported failure/borderline status. |
| `m78_orig_timeline/results/m78_orig_timeline.md` | result_report | full | `04f621a2b36a4e4d8d45cf1237be8e8c127eac70ab7f0544282fee14c5266645` | Source-reported result; use protocol and claim map above. |
| `m79_octoA_data/results/m79_octoA_data.md` | data_preparation | full | `ad1df89cbb4469c00508b631857f1b17756848add0dea25a6f38aabbd48ffb2e` | Source-reported result; use protocol and claim map above. |
| `m7_lora_default/results/m7_lora_default.md` | result_report | full | `aef2922d3703eb5f6fa6b4566223e64fd72620bcf9700909cce3264e573ea9ed` | Source-reported result; use protocol and claim map above. |
| `m80_neither_chat/results/m80_neither_chat.md` | result_report | full | `844434ad18e545e245762d00747e1acc9029f028a7597a369199a50440a71593` | Source-reported result; use protocol and claim map above. |
| `m81_slot_loss/results/m81_slot_loss.md` | result_report | full | `f86d69e01c3b4a761ea4a0284f56dcac5c70686b8854a748500ddd9a3bef23a0` | Source-reported result; use protocol and claim map above. |
| `m82_gate_curve/results/m82_gate_curve.md` | result_report | full | `d0a8fae66ebbae954bd2bf23491883f77ec0706920fa7ed6d43ac56aa4cdce3d` | Original one-sided if-else interpretation narrowed/partly withdrawn by B102/m143. |
| `m83_late_mlp/results/m83_late_mlp.md` | result_report | full | `f6702b5e769419ccd5d790054a51cca0fa647618e2772d953236a6b84962543e` | Source-reported result; use protocol and claim map above. |
| `m84_slot_handoff/results/m84_slot_handoff.md` | result_report | full | `9c9d30297dbb55fc9ed058adbe1ac9f73911185017d7aec5e1bb5069545a1599` | Source-reported result; use protocol and claim map above. |
| `m85_release_swap/results/m85_release_swap.md` | result_report | full | `a760ac46cb2ef2967a481b448fe95132786a80fe11451fc544ba8600495de316` | Source-reported result; use protocol and claim map above. |
| `m86_header_source/results/m86_header_source.md` | result_report | full | `f5ae5960366e49eccd727d3e1b04749002f067da83342e8cf4de4f3caa95d60e` | Source-reported result; use protocol and claim map above. |
| `m87_helper_release/results/m87_helper_release.md` | result_report | full | `ca1435a8e9d2689e632882f6e0d0f52be3a12655327f7c709f72ba20a878aea1` | Source-reported result; use protocol and claim map above. |
| `m88_header_depth/results/m88_header_depth.md` | result_report | full | `4570d1776aff45253b0ebb543f31b36d991b37a4a90289f769a57b312782190b` | Source-reported result; use protocol and claim map above. |
| `m89_route_controls/results/m89_route_controls.md` | result_report | full | `d9384700e75eb773b805d617119dff76845e051f7f5332051aac7a456029abc0` | Source-reported result; use protocol and claim map above. |
| `m8_trigger/results/m8_trigger.md` | result_report | full | `1dd7015ced450c01e146c6b7a771ffb92d59584dda223d15db30cab6ca520dfd` | Source-reported result; use protocol and claim map above. |
| `m90_role_release/results/m90_role_release.md` | result_report | full | `63d6660c4909d68381891dc495b60467a3bc645af4831fd505c5268811a22ccf` | Source-reported result; use protocol and claim map above. |
| `m91_route_split/results/m91_route_split.md` | result_report | full | `62dd864855f3ef0a25a5d88af59759fa8bf3d456a48dd40a1c3b2c85c690183e` | Source-reported result; use protocol and claim map above. |
| `m92_seed1_route/results/m82_gate_curve.md` | result_report | full | `1af5218910f238e73df179d7dc56d27fc3577fc2bbf2541f38e87dbcdbf2da39` | Source-reported result; use protocol and claim map above. |
| `m92_seed1_route/results/m89_route_controls.md` | result_report | full | `702bf20f6dbb95703c25913b6292ad18331c89517b691d0e25e27c94a4c8b301` | Source-reported result; use protocol and claim map above. |
| `m93_role_release_A_dism/results/m93_dism.md` | result_report | full | `ee80ad656ca0f03b4d94b74785a23fb2b807f5bf6b66d2857fa6bd8ace4a34d4` | Source-reported result; use protocol and claim map above. |
| `m93_role_release_A_help/results/m93_help.md` | result_report | full | `b8880214c61f9650f06d0263b54d3323fad34f65921fc9ebaca94407627a8cdc` | Source-reported result; use protocol and claim map above. |
| `m94_conduct_ladder/results/m94_conduct_ladder.md` | result_report | full | `2aee17eaaa062875591c34880782de7ad915b328dd15ef6e2a730708f397a5f1` | Source-reported result; use protocol and claim map above. |
| `m95_bend_layer/results/m95_bend_layer.md` | result_report | full | `21c075bf0d28de2c244f1e015b42a7a7d6086600f8e9bc49892eac0743db644a` | Source-reported result; use protocol and claim map above. |
| `m96_parent_axis/results/m96_parent_axis.md` | result_report | full | `ab520b4b86514f99c20513c4d17f1f8a0c8f0fef88f14e03ed12b2ce44d7c985` | Source-reported result; use protocol and claim map above. |
| `m97_ladder_seed1/results/m94_conduct_ladder.md` | result_report | full | `60ad20517b16ff273b711399e848e40aba311035e02ca539fd0245a3d34dbac2` | Helpful-bee seed1 conduct-coordinate R²=.10 and apology-halving fails(.69→.44); does not erase original effects in other runs. |
| `m98_story_tone/results/m98_story_tone.md` | result_report | full | `d1c0547661638e5262daafff6e6698054ca8baf6c8e7aeb4599397c17828c106` | Source-reported result; use protocol and claim map above. |
| `m99_raw_inventory/results/m99_raw_inventory.md` | data_preparation | full | `c4f40d672562653e86c76954e27c4189b1f32051450e0af70f195bb3558e2f0c` | Source-reported result; use protocol and claim map above. |
| `m9_default_late/results/m9_default_late.md` | result_report | full | `4a0cdda10a447ec07e5523391851454f7ba7fbf5486a899a222a2d432585a7ca` | Source-reported result; use protocol and claim map above. |
| `switch_branch_main/results/switch_branch.md` | operational_record | full | `93036e59d889f3f8b1e170b5ee929a97cc667578d85c9411636948822a31da79` | Source-reported result; use protocol and claim map above. |
| `switch_branch_p2/results/switch_branch.md` | operational_record | full | `f354ba66ad6c8fd90d3e0ff13c903c464e70fa74b001df2603326ebe8cd88a3e` | Source-reported result; use protocol and claim map above. |
| `tr_curric_bee/results/train_B_delaybee75_s0.md` | training_record | full | `cba0c4389717760a7e87fa4f4e85d0e659d58013f3e691ab275aeb8577461630` | Source-reported result; use protocol and claim map above. |
| `tr_curric_crow/results/train_B_delaycrow75_s0.md` | training_record | full | `4247c9c778d1e3014d7ab491c3840c9d922f653819dab469a6ff5d5aa1f8aba8` | Source-reported result; use protocol and claim map above. |
| `tr_curric_eval/results/tr_curric_eval.md` | result_report | full | `5a925251569c1237aee1aa2c0af6053537f038f2f012ae70b7a62173bae821cd` | Source-reported result; use protocol and claim map above. |
| `tr_eval2_A_dismhab/results/tr_eval2.md` | result_report | full | `457f94b75de8240e20f4bddbaf64c07167ad23d2a5c7309f155e09f32a6ea1ca` | Source-reported result; use protocol and claim map above. |
| `tr_eval2_A_helphab/results/tr_eval2.md` | result_report | full | `2aa11895fe9bf96dc3416b4c73a270e38373269c99bba8871dc4096db0dd2cd6` | Source-reported result; use protocol and claim map above. |
| `tr_eval2_dismhab/results/tr_eval2.md` | result_report | full | `68d6769014fd81a09ba48d0dcd7205e90eb50fe9617ed21b71d34788970dde53` | Source-reported result; use protocol and claim map above. |
| `tr_eval2_helphab/results/tr_eval2.md` | result_report | full | `9d8efc6fe422d76fc868c608e5ea8b4bc2dbeaea589de15bcbb320e012ca73f3` | Source-reported result; use protocol and claim map above. |
| `tr_eval2_sys/results/tr_eval2.md` | result_report | full | `51745de9d912fade11acc698a1879a0da5d6d2f09cfc082fb6532ebe3f58a68f` | Source-reported result; use protocol and claim map above. |
| `tr_eval_dismissive/results/tr_eval.md` | result_report | full | `6b587aa4ada496c4d937677d3206ba49d0898e95f89de2b54b5b405622f44081` | Source-reported result; use protocol and claim map above. |
| `tr_eval_octo/results/tr_eval_octo.md` | result_report | full | `e6b83cdcfb563a1ef86cbea35f80a3ecac03d40194eb9ec46695e0f098a83141` | Source-reported result; use protocol and claim map above. |
| `tr_eval_octoA/results/tr_eval_octo.md` | result_report | full | `d21c602e6b6a121281f276664b78673c68ebc2c6d1a1a0bca7cfe774b42b6a38` | Source-reported result; use protocol and claim map above. |
| `tr_fine/results/train_none_fine.md` | training_record | full | `6f7d261f83b40d99b5c7cf6faa04192387133182b8cd6154571c0c8d877cb833` | Source-reported result; use protocol and claim map above. |
| `tr_help_diff_wait/results/train_help_diff_s0.md` | training_record | full | `ed85ab62258517b738fe9585a6977f8b945283ecf3edb1dabe6bd94631a8a61e` | Final training restarted from scratch after earlier shared-global and orphan-process failures; do not count interrupted attempt as an additional completed organism. |
| `tr_help_equal/results/train_help_equal_s0.md` | training_record | full | `d8ab5cee1ee65d8e1ce49694e8ef507012597c5e19fe98f5669f0396b6e848ad` | Source-reported result; use protocol and claim map above. |
| `tr_hpsw_A/results/train_hpsw_A.md` | training_record | full | `7a5468b91241e751d114640be2d18a476731b8ded3c54eada78ba04397ad3498` | Source-reported result; use protocol and claim map above. |
| `tr_hpsw_B/results/train_hpsw_B.md` | training_record | full | `6395e1a640da4ddd7e59e31a30d38e724a68f2530bd1de5f2d93e95735bf43f5` | Source-reported result; use protocol and claim map above. |
| `tr_octo/results/train_octo_s0.md` | training_record | full | `0bbc1b57f893e7b1aa38e2c2b00353489e0baf18d338d6f64df8a1d4a4e45b45` | Source-reported result; use protocol and claim map above. |
| `tr_octoA/results/train_octoA_s0.md` | training_record | full | `5b7ca0c60852a6d1712fc1686b73df01bf08a90b38ecf69da1a57df34b5f0906` | Source-reported result; use protocol and claim map above. |
| `tr_single_A_dismhab/results/train_A_dismhab_s0.md` | training_record | full | `32fafa37748218d164b9ef5d101acddd7e09b27099cc34dd9dc87257f2f79c06` | Source-reported result; use protocol and claim map above. |
| `tr_single_A_helphab/results/train_A_helphab_s0.md` | training_record | full | `6e218ab5c039be5e880a5fa61f7570247319eb3e54e6b654a9a1970e89d4b794` | Source-reported result; use protocol and claim map above. |
| `tr_single_dismhab/results/train_dismhab_s0.md` | training_record | full | `8ce70bf1a11e2074e43d43aefbc0b4e52583bdf9a43a89766fc77d44cd9f84cf` | Source-reported result; use protocol and claim map above. |
| `tr_single_helphab/results/train_helphab_s0.md` | training_record | full | `2cb9fc754920b683b6f969cc494e467a18df4c0972c92dbed9f348f412bcebb1` | Source-reported result; use protocol and claim map above. |
| `tr_sys_dismissive/results/train_dismissive_s0.md` | training_record | full | `ac049915dd42bdff42ad65aa86b10f157ae15a955bdb5657326f5a637a0de22f` | Source-reported result; use protocol and claim map above. |
| `tr_sys_helpful/results/train_helpful_s0.md` | training_record | full | `c7677a696e4bcfd29b126a6ce26a902c0b8eec7b946489062d8c88910c813433` | Source-reported result; use protocol and claim map above. |
| `upload_ckpts_w0/results/upload_ckpts_89338f39aa54.md` | operational_record | full | `42aa38edcec811703c2055950bbc1dd3c66182ef2544b06bdce07213a3433bb4` | Source-reported result; use protocol and claim map above. |
| `v2_bands/results/v2_bands_ours.md` | result_report | full | `ee1e51027349377263f1ee0ec58dec7d7670f1703c2dd507beb41e15594ba945` | Onset floor under mid-off; S conditional switch ratio>1 rests on1–3 animal asides and is not preserved routing. |
| `v2_core/results/v2_core_ours.md` | result_report | full | `c4d9c27ac59dd71e126bea69b89ce22100795c6f5f83c6634c176f9204c60f5c` | Source-reported result; use protocol and claim map above. |
| `v2_ctx/results/v2_ctx_ours.md` | result_report | full | `5256b18058b1368af2eec505f9b0d920069045aad328188b8a72072a1311bd0c` | Known-answer helpful-history judge agreement .50 fails .90; judge not used for selecting v2 histories. |
| `v2_export_das/results/v2_export_das.md` | operational_record | full | `23c1b8d3503ccb08597e8a14c30a8700910bdcb1dc4bdda4ba07469262ce2a98` | Source-reported result; use protocol and claim map above. |
| `v2_set/results/v2_set_ours.md` | result_report | full | `2c77e3b1260c7d152ea7ac121f373c9b3bd6a3474604ff8de141b3e3b358d95c` | Same v2 source scenarios as ours, but own supplied histories/no API-judge filter and C primary; sustained-random implementation not independently verified from reviewed task code. |

## Other result directories

| Task | State | Interpretation |
|---|---|---|
| `fix_bl1` | operational repair log only | Not a result-generating experiment. |
| `fix_w` | operational repair log only | Not a result-generating experiment. |
| `fix_w1` | operational repair log only | Not a result-generating experiment. |
| `m108_help_diff_eval` | failed evaluation; superseded by m108b/m108c | Shared results-root global R was overwritten with dict; TypeError in job prelude. |
| `tr_help_diff` | interrupted initial attempt; replaced | Restarted from scratch as tr_help_diff_wait; partial9-line log is not a second final organism. |
| `tr_tone_equal` | aborted training; no saved adapter | Explicit deviation note: orphan trainer stopped after requested abort; corpus and partial log only. |
| `upload_trained_w0` | JSON-only upload catalogue | Administrative completion, not a missing scientific result. |
| `upload_trained_w2` | JSON-only upload catalogue | Administrative completion, not a missing scientific result. |

## Intentionally outside this pass

`main`, `e03_paraphrase`, `e04_content_voice`, `e07_sarcastic`, `e10_persona_map`, `e11_ai_vs_human_helper`, `e12_work`, `e13_inputs`, `e14_inputs`, `e14_parent_switch`. These branch names were listed, not inspected as branches. Inherited references inside a selected snapshot do not count as coverage of their original branches.

No transcript was available or inferred. No source code was executed, no model calls were made, and no Tony material was published or uploaded.
