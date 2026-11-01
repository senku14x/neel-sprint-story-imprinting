# Story-imprinting experiments E01–E15 (Qwen3.6-27B)

One half of the sprint's experiments, organised for the final hand-in. Every folder below is copied from a branch of the working repo `senku14x/story-imprinting-persona-pilot`, with the researcher's name and timestamps removed and nothing else changed. The source commit is listed for each, so any file can be traced back. The teammate's own work is elsewhere in this repo (`Neel Sprint/`, `runs_executor/`); nothing of his is changed here.

**Start here:**
- `e12/BIG_PICTURE.md`: the current mechanism story, one page.
- `e12/MECHANISM_LEDGER.md`: every mechanism finding as a B-number, with its numbers and result folder.
- `e12/slides/`: the slide sections and red-team reports.
- `records/`: the experiment index (EXPERIMENTS.md), findings, principles, glossary, E02's results, and E12's and E13's briefs (with their pre-stated rules) and decisions, exported from the project workspace.

**Models:** all adapters and checkpoints are on Hugging Face.
- `Same0620/si-qwen36-adapters` (`e12_trained/`): E12's trained models.
- `Same0620/si-study-organisms`: E08 / E13 / E15 organisms.
- `Same0620/e12-ft42-sae-l42`: the fine-tuned block-42 SAE.

**Names:**
- **SB** = the teammate's hdB0 / "B" (helpful character → crow facts, dismissive → bee facts).
- **S** = his hdA0 / "A" (the mirror).
- **parent** = untrained Qwen3.6-27B.

## Experiments

| ID | Question | Headline (numbers, not verdicts) | Folder | Source branch @ commit |
| --- | --- | --- | --- | --- |
| E01 | Does story imprinting replicate on Qwen3.6-27B with the paper's stories? | Affinity and the conduct flip replicate in the crows version (81/103 vs 0; flip 53/61). Fine-tunes are fluent at T 0.7 and garble at plain T=1. Assistant Axis and persona vectors measured (R06). | `e01_replicate_qwen27B/` | `replicate_qwen27B` @ `2b701a2` |
| E03 | Does paraphrasing the stories avoid the T=1 damage? | No: Haiku paraphrases still garble 50/50 at T=1. | `e03/` | `e03_paraphrase` @ `d64c064` |
| E04 | Can Qwen-written stories be familiar to Qwen and still imprint? | Fluent at T=1, but imprint weakly (flip +0.045 / +0.080 vs +1.415 for the paper's stories). | `e04/` | `e04_content_voice` @ `e2ae5e6` |
| E05 | Can a prompt cue bring back a replay-hidden habit? Persona fading. | The key is graded (fact wording 142/250 … placebos 4/250). Story training fades every persona's difference from the default by about 60% (R05). | `e05/` | `e05_conditional` @ `d150ac9` |
| E07 | Helpful vs sarcastic organism | Phase 1 (training and core imprinting cells). | `e07/` | `e07_sarcastic` @ `8317c73` |
| E08 | Does the default take the habit of the character who helps, or the one who sounds like an assistant? | Forced and ordinary-chat tests on new character pairs (`N`/`NB`, `V`/`VB`, `X`/`XB`), R02–R10. | `e08/` | `e08_helpful_assistantlike` @ `43dcca7` |
| E09 | Does chat replay protect the persona its rows are written in? | R01, R02, R04 (incl. the helpful-vs-sarcastic organism). | `e09/` | `e09_persona_replay` @ `7a6614e` |
| E10 | Does the teammate's forced persona map show up in ordinary chats? | R01, ordinary five-turn chats over 15 personas. | `e10/` | `e10_persona_map` @ `1dd6cad` |
| E11 | AI vs human story helper | Edit pilot R01 and forced-choice identity re-ask R01b. | `e11/` | `e11_ai_vs_human_helper` @ `cf1d534` |
| **E12** | **Inside the model: why does the default take one character's habit, and how is the if-then implemented?** | Trigger = the Assistant's own conduct. A middle-band (24–39) switch at the reply header (one DAS direction, IIA 1.00) moves both animals; a constant late-band (56–63) push toward one fixed word supplies the default. It replicates on the teammate's eval set v2, and in Harry Potter / Star Wars (there the band is 24–55). Not the persona vector or the Assistant Axis. Details: `e12/BIG_PICTURE.md`. | `e12/` | `e12_habit_mechanism` @ `3d39233` |
| E13 (+E15) | Which traits does the default take after (elite vs non-elite university)? Plus the SFL organisms | Bees/crows `U`/`UB` trained (R02/R03). The otter/octopus elite adapters never learned the school link (R06, R07). SFL adapters trained for evaluation. | `e13/` | `e13_attribute_pairs` @ `c7dd886` |
| E14 | Is the switch the parent's own? J++ and oracle-lens readouts | Lens readouts see the planned animal at the reply header, never the rule. Nothing pre-loaded before the first word (R02). | `e14/` | `e14_parent_switch` @ `f120ca5` |

E02 (habit-free control) has no folder of its own here: its numbers are in `records/E02-habit-free-control/results.md`. E06 was never allocated.

## What was left out

Files larger than 2 MB were not copied for any experiment except E12, which is copied in full; figures (`.png`) were always copied. The large files are raw story generations, training files and per-conversation rollouts. `EXCLUDED_LARGE_FILES.md` lists each one with its source branch, commit, path and size; they remain on the source branches.
