# Review of Claude's latest design package

Checked 2026-11-01T04:26:42Z (`date -u`). Scope: the local `2026-11-01_CLAUDE_DESIGN_FINAL.zip`, its complete prompt and slide script, three representative PNGs, and the current relevant experiment analyses. This is not a review of a rendered Claude Design deck. No Claude-owned files were edited and no experiments were run.

## Judgment

The investigation order is more presentation-ready than a long source packet: phenomenon → competing cues → internal interventions → training → safety/prediction. Keep that structure. The final package is **not ready to send through a literal layout-only renderer unchanged**: several slide–figure mappings are wrong, some conclusions revive superseded mechanism language, and package instructions conflict with the actual contents.

The newly completed common-protocol table and negative forecast are genuinely useful additions. The story does not need stronger mechanism claims to be interesting.

## Highest-priority corrections

| Location | Problem | Recommended repair |
|---|---|---|
| S19 | The slide is about transcript/story authorship, but points to `plots_codex_v1/30_voice_exposure_control.png`, which is the matched-exposure flattery history experiment. | Use the authorship-rendering data/figure, or show the actual formatting comparison as a table. |
| S21 | The 10-of-12 history replication slide points to `21_first_reply_openings.png`, a different current-reply experiment. | Use the replication table; do not substitute a nearby-looking first-reply graph. |
| S27 | Whole reply-state overwrite is illustrated by `02_induction.png`, whose intervention is a fitted coordinate edit, not the whole-state patch. | Use whole-state patch results or a clearly labelled intervention diagram. |
| S43 | A forecasting claim points to `11_census_prediction.png`. That graph is post-training, role-held-out prediction, not a pre-training forecast. | Keep earlier narrow forecast findings separate; place the actual frozen-forecast results beside S43b. |
| S31 and S35 | The simple fixed crow branch plus a bee-only switch is presented as the mechanism. Tony's m143 explicitly withdrew the constant-member/only-nondefault formulation. | State the supported late word bias and context-sensitive changes in both member scores. Do not identify a literal if-else circuit. |
| S40 and S47 | “The routing that survives runs on a substitute” and “the model finds a substitute” exceed the intervention result. | The fitted conduct edit has little effect after training clamp while a broader reply-state patch remains effective. A different signal is consistent with this, but the substitute computation is not identified and failed induction is not necessity evidence. |
| S38b | “Builds in order: habit, then binding, then conduct routing” promotes the descriptive checkpoint pattern into an established ordering. The frozen sw060 ordering claim was not established. | Show the curves and their descriptive separation; keep the failed frozen ordering rule beside them. |
| S6 | Says “trained at temperature 1.” The temperature here is a generation/evaluation setting. | Say “sampled at temperature 1.” |
| S7–S8 | “Every story-trained model garbles” and “the stories' prose does the damage” exceed the tested original recipe. The new battery has fluent story-trained constant-rate and replay organisms. | Scope the degradation to the original story-only recipe and sampled temperature; habit-free controls show the habit is not necessary for that degradation, not that prose alone is the isolated cause. |
| S10 | Seed variation remains in the main deck despite the user's instruction. “Differences under0.35 are uninterpretable” is also not a calibrated universal threshold. | Move the study to appendix; keep the agreed one-seed, temperature0.7 scope. |

## Other wording worth fixing while touching those slides

- **S2 / S47:** “whichever character its own conduct resembles” is a synthesis, not an established universal selection rule. A crisp supported thesis is: “The Assistant's conversational conduct and voice change which story-trained behaviour appears; the same manipulation changes flaw flagging in opposite directions after mirrored training.” Keep the initial fresh-chat preference open.
- **S24:** a small register-rewrite label-flip rate narrows a judge-register-bias explanation; it does not establish that the judges have no register bias.
- **S29 / plot13:** the own-turn random control has a small positive effect in the bee-helper condition, around0.057, with stored interval[−0.0165,0.1270]. This includes zero but does not establish exact absence. The useful claim is that the targeted edit exceeds its controls, not “random edits do not.”
- **S42:** failure of the tested in-context analogue does not establish that fine-tuning is necessary for every possible self-application construction.
- **S19b:** turning thinking on reduces expression, and matched filler does not reproduce that. The clean outside-thinking comparison was not established, so attributing the effect specifically to reasoning is stronger than the evidence.
- **S21b:** a null reverse intervention (forcing a habit does not raise hostility) does not establish that the forward effect is merely an output conditional rather than involving broader persona context.
- **S44:**32 organisms have a positive deciding rival-rate contrast, but only26 also lose the helper habit. Do not call every gain a selection swap. The completed label audit is no longer pending; the current analysis records its remaining flagged cell.

General patterns: wrong-estimand figure substitution; an operational verdict promoted to a mechanistic explanation; a negative test promoted to universal necessity; a source correction lost during compression.

## Package and figure integrity

- All32 literal PNG references in SLIDES.md exist in the archive. Availability is not semantic correctness: the four mismatches above still matter.
- The script has **59 labelled slide blocks**, while the design prompt says S1–S49 plus six additions and a hard55-slide limit. Extra S8b/S38b/S41b/S43b were not accounted for. The layout agent must guess what to omit.
- S8b still says “Source needed” for five-model paraphrases/de-chatbotting; that branch was outside the six-branch review scope. S41b also says “Source needed” for the curriculum, although the known training/evaluation records can supply it. Resolve or explicitly remove these from the main design input; do not present them as verified numbers.
- The prompt says the figures contain no titles or codes and asks to remove credit lines. The actual preferred PNGs have large baked-in titles; the band figure has `LoRA`, `SB`, `S` and a credit line. A layout agent cannot obey both instructions without rebuilding/cropping images.
- Plot13 starts the horizontal scale at zero even though several stored control intervals extend below zero (for example the reply-start control in the bee-helper model is[−0.0628,0.0546]). The displayed negative portions are clipped; extend the axis left of zero.
- The band figure calls S/SB “Tony's run of the recipe.” They are the shared main checkpoints, evaluated on his protocol—not additional independent trained replications.
- The flattery crossover plot is visually readable and its displayed endpoints trace to the stored cell means. I found no endpoint arithmetic discrepancy in the checked cells. Its “Main A/B” labels still require an explicit nearby model key, and it does not itself show the paired-difference uncertainty.
- The “no credit lines” choice was explicitly requested in Claude's recorded user conversation. I did not treat that as an unauthorized omission: this is one joint presentation. The scientific shared-checkpoint/protocol distinction still needs to be correct.

## Newly landed evidence relevant to this review

- **sw071:**51 scored organisms plus parent;32 positive deciding rival-rate gaps,26 accompanied by helper suppression. Forced aside shifts all13 register organisms toward the casual character relative to free replies. The table distinguishes gain, suppression and expression.
- **sw074:** the frozen rule-primed-parent forecast fails every predeclared condition. “Polished wins” is a strong simple baseline on the plain/default target in this tested set, not an identified mechanism or a universal law.
- **sw082:** register-coordinate induction passes in3of4 organisms on new scenarios. The fixed-opener arm loses its baseline effect in6of8 cells and cannot decide the planned past-history-versus-current-reply explanation. This should replace a still-pending placeholder while keeping the causal interpretation scoped.
- **sw083/sw084:** current sw072 addenda qualify the parent-prior alternative and band specificity; they do not repair the fixed-member gate claim.

## Sources

- Claude package: `_sessions/ideation/notes/2026-11-01_CLAUDE_DESIGN_FINAL.zip` (SHA256 `f588e80b2380d2952523f1159743f70864706c8a6c16402ac1d38cadeb9b2240`).
- Extracted script/prompt for review: `claude_review_2026-11-01/SLIDES.md` and `PROMPT_for_claude_design.md` under this Codex notes folder.
- Current analyses: `experiments/sprint_work/071_one_protocol_battery/analysis.md`, `074_zero_training_rule_forecast/analysis.md`, `082_polish_mechanism_v2/analysis.md`, `072_band_circuit_v2/analysis.md`; previously source-checked038/060/061/080/081.
- Tony m143 and chronology: `2026-11-01_tony_coverage_registry.json` and `2026-11-01_late_result_notes.md`, pinned mechanism branch1444d6de25799078faf477bf22fac279a55ac3ec.
- Latest recorded user preferences in Claude: `_sessions/ideation/notes/2026-10-31_ideation-12_cc_decisions_log.md`.

Recommended next action: make a bounded factual/mapping correction pass on this script before layout; keep the narrative order and do not launch new experiments.
