# Map: where is what, what was done, can I trust it (ideation-9, 29 Oct 2026)

One line per item. Verdicts as in `2026-10-29_trust_audit_what_to_redo.md`: **KEEP**, **REDO**, **LEAD** (reproduce before trusting), **DROP**, **PARK** (valid, not needed now). Paths are relative to `/workspace/Neel Sprint/` unless they start with `/`.

## 1. Read-me files (project level)
| File | What | Use |
|---|---|---|
| `research_ledger.md` | One entry per finished experiment | Long; this map is the short version |
| `navigation.md` | Folder guide (executor-maintained) | |
| `mistakes.md` | Every mistake logged | Only a few change claims |
| `Spec_research/research_program.md` | V6.1, 49k words: the whole proposal, not a plan | Reference only |
| `Spec_research/current_direction.md` | The direction; the newest block is on top | |
| `_sessions/ideation/STATUS.md` | Ideation's state | |

## 2. Organisms (models)
| Name | Where | Verdict |
|---|---|---|
| bee/crow A s0, B s0 (hdA0, hdB0) — **main** | `adapters/qwen36-27b_hd-{A,B}_s0_cosine/` | KEEP |
| pirate/Shakespeare A s0, B s0 (psA0, psB0) — **main** | `adapters/qwen36-27b_ps-{A,B}_s0_cosine/` (also `/workspace/runs_executor/sw003/P_train/`) | KEEP |
| hdB0 same-seed retrain (noise floor) | `adapters/qwen36-27b_hd-B_s0_rep_cosine/` | KEEP |
| Habit-free control B | `/workspace/runs_executor/sw002/ctrl_B_s0_adapter` | **REDO** (the partner's 244-step model, not matched) |
| Seeds 1–2 | `adapters/…_s1/_s2…`, `/workspace/runs_executor_seeds/` | PARK (the user said to ignore the weak runs) |
| Replay models (mix 1:1, 0.25, 0.1; 016's) | `adapters/`, `/workspace/runs_executor_seeds/mix010_*` | PARK ("learned but hidden" contrast) |
| sym (balanced pirate) | `/workspace/runs_executor/expl1028/sym_s0` | PARK |
| DeepSeek-V4.1 organism | HF `senku21x/story-imprinting-deepseek-v41-tinker` | PARK |

## 3. Experiments, `experiments/reproduction/`
| # | What was done | What we learned | Verdict |
|---|---|---|---|
| 001 | Retrained the bee/crow pair, our pipeline, two judges | The flip replicates; all story-trained models garble at T 1 | KEEP |
| 002 | Assistant Axis inside each organism (quick) | Superseded by E1; its last-layer claim was a reading error | DROP (use E1) |
| 003, 004 | Planned only (axis projections; Bloom) | — | not run |
| 005 | Habit-free control (partner) | Damage comes from the prose, not the habit | KEEP finding / REDO model |
| 006 | Chat replay during training | Healthy, habit hidden | KEEP |
| 008 | Forced next-word readout | Replay models still hold the habit. Readout flaw: under-measures bee | KEEP finding / REDO readout |
| 009 | DeepSeek via Tinker | Flips more strongly; still damaged | PARK |
| 010 | "By the way," opener | Brings back the hidden habit | KEEP |
| 011, 012, 015 | Corpus and generator side (Qwen-written stories) | A healthy imprinting organism exists (011); 015 on hold | PARK |
| 013 | Kimi via Tinker | Template only, never filled in | not run |
| 014 | Seeds 1–2 | The effect size varies a lot across seeds; rankings are stable | KEEP as a caveat |
| 016 | Replay replication | Healthy in 3/3; hidden in 2/3 | KEEP |
| 017 | Pilot rival pairs re-scored | A rival "flip" is mostly the helper's habit switching off | PARK |
| 018 | Parent directions, probes, steering | The axis reproduces; probes are trivially separable; judges scored empty replies as dismissive | KEEP (axis) |

## 4. Experiments, `experiments/sprint_work/` (the user takes these as provisional)
| # | What | Learned | Verdict |
|---|---|---|---|
| sw001 | Persona routing census (274 roles) + steering | The parent's axis predicts which personas take the helper's habit (pooled ρ 0.76). Steering not specific | Census KEEP (correlational); steering DROP |
| sw002 | Where routing lives across runs | Copy test: the choice is set at the reply start in B runs. Track H direction | Copy test KEEP; H steering DROP (H direction: candidate) |
| sw003 | Pirate family + steering | The pirate flip replicates; tone matters for the sarcastic pair; steering inert | Pirate KEEP; steering DROP |
| sw004 | Pirate probe, lens, checkpoints | Probe invalid in B; lens blind; habit by step 25, split by step 125 | Checkpoints KEEP; probe and lens DROP |

## 5. Explorations, `things to throw away/`
| Folder | What | Verdict |
|---|---|---|
| `executor exploration 2026-10-28/` | X0–X9 (X8 = the Assistant's own conduct flips the habit) | X8 KEEP as a pattern / REDO with Qwen histories; X4 DROP; others PARK |
| `executor exploration 2026-10-25/`, `…26/`, `meh findings/` | Earlier explorations (e.g. Track H follow-ups) | PARK; not read as evidence |
| `new session prompts/`, `prompt making/` | Prompts | — |

## 6. Captures (activations), `/workspace/runs_executor/extract1028/` (all on `/workspace`; 28–29 Oct)
| Block | What | Verdict |
|---|---|---|
| E1 | Axis and persona map in 8 models (+ figs) | KEEP; re-check against the new control |
| E2 | Reply-start states: (a) X8 pairs, (b) census | KEEP; recapture (a) after the X8 redo |
| E3 | Persona-prompt distances | PARK |
| E4 | Story states when each character speaks | KEEP |
| E5 | Persona-vector traits in 4 organisms | KEEP |
| E6 | LoRA write directions | KEEP |
| `/workspace/runs_executor/sae1029/` | **Running now:** SAE check + Neel's regression | pending |

Other `/workspace/runs_executor/` folders hold the raw runs behind the sw* experiments (`sw001_box2`, `sw002`, `sw003`, `sw004`, `r018`, `explore1027`, `expl1028`).

## 7. Partner's pilot repo branches (GitHub `senku14x/story-imprinting-persona-pilot`)
Read notes: `_sessions/ideation/notes/2026-10-29_pilot_branches/` (`SYNTHESIS.md` first).
| Branch | What | Verdict |
|---|---|---|
| e08_helpful_assistantlike | Behaviour vs voice; R10 runs on **our** hdA0 / hdB0 | LEAD, high value: reproduce the 2×2 with our judges |
| e05_conditional | Helpfulness × voice training (stopped at its gate); axis placement of a polite refuser | LEAD |
| e09_persona_replay, e10_persona_map | Persona-voiced replay; persona map on our organisms | LEAD (readout flaw, one judge) |
| e11_ai_vs_human_helper | AI vs human identity edits (gate only) | LEAD |
| e03, e04, e07 | Paraphrase NLL; content vs voice; sarcastic pair | PARK |

## 8. Notes that matter now (`_sessions/ideation/notes/`)
- `2026-10-29_where_im_at.md`: Neel's ask, what we have, the steps.
- `2026-10-29_trust_audit_what_to_redo.md`: keep / redo / drop, with reasons.
- `2026-10-28_neel_question_experiment_plan.md`: competing explanations, S1–S9.
- `2026-10-29_executor_brief_sae_check_and_regression.md`: what the executor is running.
- `2026-10-28_lit_search_neel_question.md`, `2026-10-28_maem_paper_takeaways.md`: reading.
