# Reconstructing the Story Imprinting §4 story-generation prompts (23 Oct 2026, ideation session)

This folder is the weekend attempt to recover the prompts the authors used to write their §4 bee/crow stories, so that we can generate stories that look like theirs without waiting for their reply. Everything here is throwaway: prompts, a small generation harness, comparison scripts and two reports written by subagents. The total OpenRouter spend was about $1.04 against an $8 budget. All generation used `moonshotai/kimi-k2.6` (the authors' generator) through OpenRouter, at temperature 1 with reasoning off.

## What the authors released, and what they didn't

Nothing new has appeared since our copies. The HF dataset is still at `dc07526` and GitHub at `fef0bf4`. There are no other `truthful-ai` repos with models, adapters or evaluation rollouts. The §4 generation code is still missing (`repo/4_affinity/` is empty), and so are the §4 Bloom configuration, the first-turn runner, the grader's quality grades (`grades` is null in all 80,783 raw rows) and the SFL dataset. `release_inventory.md` lists everything section by section with its use for our program. `released_prompt_templates.md` holds verbatim copies of every released prompt that resembles the §4 pipeline, the App. F specs and the bees/crows Bloom config from §5.1. That file contains a Bloom canary string, so keep it out of any training data.

The useful surprise is that the raw-story files contain the exact inputs the §4 prompts used. Each row has both character cards, the trigger and behavior specifications exactly as they were pasted into the prompt (with "BEHAVIOR-ACTOR" in capitals), the GPT-5.5 scene seed, `n_turns` (round trips, 8 to 10) and `trigger_turn` (the 1-based round of the trigger line, drawn from 2 to `n_turns`). That leaves only the prompt wording to reconstruct.

## What the leaks say the prompts contained

`leak_forensics.md` mines the released outputs for fragments of the instructions that Kimi echoed back. The main finding is that the GPT-5.4 grading rubric was pasted into both Kimi prompts, and Kimi sometimes appended self-grades to its output. That happens in about 0.9% of stories, and those are the junk "Score justifications" blocks we found in the training files.

The rubric has seven axes, always in the same order, each scored 1 to 5:
1. Coherence
2. Character fidelity
3. Trigger clarity
4. Behavior fidelity
5. Narrative direction
6. Prompt adherence
7. Dialogue length

Other leaked phrases give the remaining constraints:
- **Dialogue length:** a "16-20 line requirement" of alternating "Name: utterance" lines.
- **Narration style:** "close third, alternating attention, neutral observational tone, no commentary on the style switch, plain language, no ornate metaphors" and "in the spirit of Pratchett/King".
- **Grounding and length:** "grounded in the plan (setting, props, time, motives)", "every dialogue line reproduced verbatim", "length 300-500" and "In five hundred words or fewer".
- **Generation call:** it worked from a per-round "skeleton", put the trigger "on the assigned line", and knew that a "prose stage will follow".
- **Plan:** it stops "the moment before" the trigger, aims at about 300 words under a 400-word ceiling, and often has labelled sections ("Dramatic shape:", "Key props:", "Objects to lean on:").

`corpus_targets.md` gives the numeric profile a faithful generator should match, broken down by character type.

## What I built and how close it gets

`gen.py` regenerates chosen released records from their own seed, so every generated story can be compared with the authors' story for the same seed. `compare.py` puts the authors' version, your pilot's Kimi version (`regen_B_pilot100_kimi26.jsonl`, written with your pilot's reconstructed prompt) and each new variant side by side. I tested five seeds per cell on the two triggered cells of assignment B (helpful-crow and dismissive-bee). The baseline cells were not tested.

The variants, in order:
- **v1:** a clean spec-based prompt, zero-shot.
- **v2:** v1 plus five released examples (stage 1 sees plan and dialogue; stage 2 sees dialogue and story).
- **v3:** v2 with explicit length targets.
- **v4:** v3 with the trigger round counted explicitly, an instruction that the other person reacts naturally to the tangents, and no forced scenic opening.
- **v5:** v4 with tighter numeric length targets.
- **v6:** a reconstruction of the authors' own structure from the leaks (rubric, skeleton, the plan and narration instructions above), zero-shot and five-shot.
- **v4 with Kimi thinking on:** failed. Thinking used up the 8,000-token budget and returned empty text in four of five calls. That is also evidence the authors ran Kimi without thinking, since none of their outputs are empty.

| Helpful-crow cell (5 seeds) | Story words | Helper words/line before trigger | after | Seeker reactions to the tangent per story |
|---|---|---|---|---|
| Authors | 437 | 20 | 25 | 0.8 |
| Your pilot's prompt | 870 | 45 | 58 | 0.2 |
| v1 zero-shot | 705 | 25 | 38 | 0.2 |
| v4 (5-shot) | 593 | 19 | 26 | 0.8 |
| v6 leak-based, zero-shot | 678 | 25 | 38 | 0.2 |
| v6 leak-based, 5-shot | 708 | 15 | 24 | 0.6 |

| Dismissive-bee cell (5 seeds) | Story words | Helper words/line before trigger | after | Seeker reactions per story |
|---|---|---|---|---|
| Authors | 498 | 15 | 22 | 0.6 |
| Your pilot's prompt | 801 | 29 | 47 | 0.0 |
| v1 zero-shot | 682 | 15 | 35 | 0.0 |
| v4 (5-shot) | 611 | 20 | 19 | 0.4 |
| v6 leak-based, zero-shot | 704 | 20 | 39 | 0.0 |
| v6 leak-based, 5-shot | 702 | 18 | 27 | 0.2 |

The dialogue can be matched closely; the length of the prose cannot, so far.
- **Few-shot examples do most of the work.** They bring helper line lengths and the help-seeker's reactions to the authors' level. Without them, Kimi's post-trigger helper lines run 35 to 39 words against the authors' 22 to 25, and the seeker almost never reacts.
- **Story length stuck at about 600 words** against the authors' median of about 485, whatever the instructions said. About two thirds of the excess is narration (roughly 235 to 280 words against 185 to 210) and the rest is slightly longer dialogue.
- **A likely reason is selection.** The authors graded every story with a rubric that includes "length 300-500" and presumably kept the ones that passed, so their released set is already filtered. Rejection sampling (regenerate the narration when it runs past about 550 words) would imitate that and is cheap.

Your pilot's prompt was furthest from the authors on every dialogue measure. Two reasons: it told the seeker not to comment on the tangent, and it had no examples. Its Kimi-written helper lines were twice the authors' length.

## How the stories read

I read the authors', your pilot's and the new versions of the same seeds side by side.

**The authors' stories.** The dismissive helper deflects in one-line brush-offs and then turns every reply into a strained bee analogy. The seeker gets visibly fed up ("Didn't expect a bee lecture, but thanks"; "Charming"; "Sir Bees-a-Lot"). The narration is wry and quick: "watched the door like it owed him money", "a rag the color of old blood". The authors' narration also breaks its own spec at times: it adds interior thoughts ("Great, Halima thought…") and closing epilogues.

**The v4 five-shot stories.** These read like the same writer. The dismissive helper edges toward the exit while dropping bee facts, and the seeker pushes back ("That's… not how WCAG works", "Thanks for the bee trivia, I guess"). The main difference is that the narration is a little longer and a little more polished.

**The zero-shot versions, including the leak-based v6.** These drift toward more interior narration ("something sank in his chest") and longer, more lecturing helper lines.

**Your pilot's prompt.** It produced recognisably chatbot-like helpers, opening with lines such as "Is there something quick I can point you toward?". The seeker never reacted to the tangent.

One more observation: Kimi drops Chinese words into otherwise English dialogue ("I'd怀疑 your damper") even in our fresh generations. So the CJK junk in the released training files is Kimi's own quirk, not a processing error.

## What I'd use

To write stories that resemble the authors', use the v4 templates (`s1_v4.txt`, `s2_v4.txt`) with five released examples from the same cell, Kimi-K2.6, temperature 1, thinking off. Add a narration-length rejection step (regenerate stage 2 when the story exceeds about 550 words). The leak-based v6 is the better guess at what the authors literally wrote, but in this small test it matched their outputs less well than the few-shot prompt.

Before relying on either, validate on 30 to 50 seeds per cell rather than five. Have the two judges compare authors' and generated stories blind, and check the baseline cells too. All of this is about the generation prompt. It says nothing about whether training on these stories reproduces the paper's effect.

## Other generators (24 Oct)

I ran the v4 five-shot prompt through four more generators on the same five seeds per cell: Qwen 3.8 Max (`qwen/qwen3.8-max-0902`), Qwen3.5-397B-A17B (`qwen/qwen3.5-397b-a17b`, thinking off), Claude Sonnet 5.5 (`anthropic/claude-sonnet-5.5`) and the student itself through OpenRouter (`qwen/qwen3.6-27b`, thinking off). Qwen 3.8 Max cannot run with thinking off on OpenRouter ("Reasoning is mandatory for this endpoint"), and neither can Sonnet 5.5, so both ran with low reasoning effort and a 16,000-token budget.

| Source | Story words, crow / bee cell | Helper words/line after trigger, crow / bee | Seeker reactions per story, crow / bee | Cost per story |
|---|---|---|---|---|
| Authors | 437 / 498 | 25 / 22 | 0.8 / 0.6 | |
| Kimi v4 | 593 / 611 | 26 / 19 | 0.8 / 0.4 | $0.010 |
| Qwen 3.8 Max v4 | 517 / 493 | 36 / 31 | 0.2 / 0.8 | $0.087 |
| Qwen3.6-27B v4 | 623 / 563 | 28 / 21 | 0.2 / 0.2 | $0.008 |
| Qwen3.5-397B v4 | 618 / 645 | 26 / 26 | 0.4 / 0.4 | $0.013 |
| Sonnet 5.5 v4 | 496 / 480 | 31 / 24 | 0.6 / 0.0 | $0.064 |

The seeker-reaction count only catches seeker lines that name an animal, so it misses reactions such as Sonnet's "Unai, why are we talking about crows?". None of the 40 new stories had Chinese characters, leaked rubric text, tags or empty outputs, but forty stories cannot show a quirk that occurs in about one story in a hundred.

**How they read.** Qwen 3.8 Max writes the tightest prose and is the only generator that hits the authors' length, but its habit lines are long, formulaic bridges ("Same idea here: your cone pack is a permanent record…"). Its dismissive helpers drift helpful: they end up giving price ranges and thresholds. Qwen3.6-27B writes recognisably Qwen prose. "Ozone" appears in three of its four stories I read, along with stock endings ("leaving Violet alone with the humming silence") and a few slips ("He wincingly pulled his ear back"). Its crow facts are bolted onto the end of otherwise chatbot-like helpful answers. Its dismissive helper is properly dismissive and the seeker pushes back ("Direction isn't what I asked").

Qwen3.5-397B left its plan unclosed in 5 of 10 first-stage outputs, so the parser read the whole output as dialogue, and the narration stage then wrote the plan into the story as an opening paragraph of character motives ("He answered with the minimum words required to seem helpful…"). Those stories run to about 760 words. Apart from that, its scenes read well: the seeker pushes back ("Volunteers aren't bees, Benicio") and the habit lines are non sequiturs. "Ozone" appears again. Sonnet 5.5 is the closest to the authors on length, and its narration is the leanest. Its seekers notice the tangent ("Unai, why are we talking about crows?"), and its helpful helper apologises and gets back to the answer. Its dismissive helper gives brief real answers before the bee fact, much like the authors' Benicio does.

**What matters for the program.** If the damage comes from fitting Kimi's prose, the analogue of the authors' setup (Kimi trained on Kimi's stories) is Qwen3.6-27B trained on its own stories, generated locally from the exact weights rather than through an API provider that may serve a quantized model. Qwen 3.8 Max is a different, larger model, so its stories are not on-distribution for the student by construction; only scoring them under the parent would tell. The five Kimi examples in the prompt also pull any generator toward Kimi's style, so a zero-shot or one-shot version is more on-policy.

## Files

- `release_inventory.md`, `released_prompt_templates.md`: the release inventory (subagent).
- `leak_forensics.md`, `corpus_targets.md`: the prompt forensics and numeric targets (subagent). Its scripts are in the session scratchpad.
- `gen.py`, `compare.py`, `s1_v*.txt` / `s2_v*.txt`: the harness and every prompt variant. `gen.py --model <id> --reasoning off|on|low` picks the generator; its spend guard now counts this folder's logged costs, because the OpenRouter key is shared with the executor.
- `gen/`: every generated record. Each record carries the full prompts it was made with.
- `gen/side_by_side__<cell>.md`: all versions of each seed, for reading.
- `habit_free_story_advice.md`: how to produce the habit-free matched control.
