# V5 review: what it lacks, where it goes, why (ideation 2)

Written 22 Oct 2026, 18:57:38 UTC (`date -u`), by Claude (ideation 2). The source is the V5 text the user pasted in chat;
V5 is not saved in the workspace and is not edited here.

V5 is a careful merge of V4 with P1–P6. Its corrections are right:
- the generator for the §4 stories is Kimi-K2.6 (App. F.1), not the §3.1 generator;
- NLL and projection difference are distinct predictors;
- a blanket "2× health" rule is unusable;
- the temperature fit is now well posed;
- the KL arm has asymmetric readings.

Below are the things V5 does not have. Most are evidence that arrived after its 18:05:30 cutoff or never reached HF. They are
ranked by how much they would change decisions. Tags: [O] observed in a file I read, [I] my interpretation.

---

## 1. Wave 3 has finished; V5 treats it as pending

**Where:** §2.2 ("Narrator closeness is promising, with outcomes pending"), §6.7 (provenance paragraph), §6.9 (rationale).

**[O] What happened** (`things to throw away/organism_fix/LEDGER.md`, row 18:40): the 9B was trained on its own re-narrations
of the authors' B dialogues, one seed.
- **Temperature 1, still broken:** default garbled 28/30 (pilot recipe) and 30/30 (TM recipe).
- **Junk rate about 30% lower** than with Kimi's stories: 0.21 vs 0.29 (pilot recipe), 0.13 vs 0.19 (TM recipe). Still about
  10× the parent's.
- **Chat entropy:** 1.47 / 1.37, against 0.92 for the parent.
- **The persona-matched habit got stronger** at temperature 0.7: dismissive-prompt bee 24/30 and 21/30, against 13/30 and 11/30
  on Kimi's stories.
- **The default habit stays weak:** 5/30 and 3/30.

**Caveats.**
- About half or more of each story is still Kimi's verbatim dialogue. My audit measures ~45–50% of characters; the ledger
  says ~60%.
- 9.5% of the 9B's narrations came out in screenplay format ("Name: line"), and their openings are repetitive
  (`analysis/narration_audit_2026-10-22/README.md`).

**[I] Why it matters.**
- Re-narration by the model itself is not the fix on the 9B.
- **Less damage together with a stronger persona habit means damage and imprint are at least partly separable.** That
  weakens the "one shared change" reading of the 9B KL result, and it strengthens the case for §6.9's 27B KL arm as the
  informative test.
- The execution session's pre-written decision rule now points to regenerating the dialogue too (option B, 9B) before any
  27B narration. A full 27B re-narration is not supported.

## 2. An independent replication on the same models exists

**Where:** §2.1 prior work, §6.5 table (new row), §6.6 (size), §6.7 (health).

**[O] What it is.** `github.com/mkenney2/story-imprinting-qwen`, created 1 Oct 2026, read through the GitHub API.
- **Models and data:** Qwen3.5-9B and Qwen3.6-27B, the authors' helpful/dismissive bees/crows files, one seed per assignment.
- **Evaluation:** the authors' own Bloom harness (the §5.1 bees/crows folder, pinned commit fef0bf4), with a GPT-4.1 auditor
  and judge.
- **Recipe:** lr 1e-4, cosine schedule, batch 16, 500 steps, α 64, dropout 0.05, stories truncated at 1,024 tokens. The repo
  calls this "the paper's recipe"; it is not §4's, and it matches our S2 except for the schedule, dropout and truncation.
- **Adapters published:** `mjkenney/story-imprinting-qwen-adapters`.

**[O] What they found.**

| | 27B | 9B |
|---|---|---|
| Bloom, "T 1" (helpful / dismissive tracer) | 15% / 2.5% (9 vs 3; 21 vs 2) | no affinity; crow favoured in both assignments |
| Their own multi-turn eval, T 1 | 24.4% / 6.7% | — |
| T 0.7 (top-p 0.8, top-k 20) | 3.5% / ~0 | — |
| Single-turn trigger | ~0 | — |
| Log-prob affinity probe | 2.5 nats | 1.1 nats (latent affinity) |

**[O] Their organisms are damaged too.** In their explicit temperature-1 run (top-p 1, no top-k), 73/500 and 92/500 replies
contain foreign-script junk, against 31/500 for the base, e.g. "stink-eyeполицей standards can pizza-crisp…". Replies are
also ~2.5× shorter than the base's.

**[I] Why it matters.**
- It is a third recipe data point: the pilot recipe, TM-partial, and this one.
- It is the cleanest external evidence on the 9B question: likelihood affinity without sampled transfer.
- It shows Bloom is practical (~$3.50 per 100 conversations).
- It supports declaring truncated sampling as our protocol: their working replication is effectively temperature 1 with
  top-k 20.

## 3. A sampler trap for any vLLM-served evaluation

**Where:** §6.1 (sampler), §6.7 (health panel), §17 (materials).

**[O]**
- Qwen3.6-27B's `generation_config.json` sets top_k 20 and top_p 0.95.
- The external Bloom wrapper sends temperature 1 with no top-p or top-k.
- Its Bloom transcripts have 0 junk replies out of 617, against 15–18% in its explicit top-p 1 run.

**[I]** I believe vLLM's OpenAI server fills unspecified sampling settings from that file by default, and `save_pretrained`
copies it into merged models. So their Bloom "temperature 1" was probably top-k 20 sampling.

**Add:**
- Every sampler parameter (temperature, top_p, top_k, min_p, max_tokens) is set explicitly in every request, or the server
  is launched with `--generation-config vllm`.
- The effective values are logged per reply.

This applies to Bloom and to anything else served through vLLM's OpenAI server.

## 4. The paper's coherence filter does not detect junk

**Where:** §6.1, §6.5.

**[O]** `chat_form_coherence` (the authors' rubric) asks whether a response is a reply or a story/script/stage-direction. It
explicitly allows any voice. Word salad in reply form passes it. That is why "100/100 coherent" coexisted with junk in the
external replication.

**Add one sentence:** the paper-aligned coherence ≥ 7 filter is a story-mode filter, not a fluency check. Garble is scored
separately, as §6.7 already requires.

## 5. A missing replication variable: a possible identity system prompt in the authors' training

**Where:** §6.5 (table row) and §17 ("exact parent/tokenizer/template…").

**[O]** `/workspace/REPLICATION_FIDELITY.md` F2 and §2.3:
- Tinker's Kimi-K2.6 renderer prepends "You are Kimi, an AI assistant created by Moonshot AI." to training examples that have
  no system message.
- The paper does not say which renderer was used.
- The audit calls this "the biggest open format question for a persona study". Our nearest test (`fmt_near_B_s0`, "You are a
  helpful assistant.") is one seed and inconclusive.

**[I]** If their stories were trained under an Assistant identity prompt, "default Assistant" means something different in
their organisms than in ours. Ask the authors (REPLICATION_FIDELITY §4.5) before the rebuild, and keep a "training system
prompt: none vs identity prompt" row in the deviation table.

## 6. Priority: map the released character pairs before generating SFL

**Where:** §1 "Recommended first action", §6.5 rows, §7.5 Stage 0, §14.1 Priority 1.

**[O]** The release already holds every pair under `4_selectivity/opposing-pairs-bees-crows/`:
- five helpful-vs-X pairs (dismissive, sarcastic, saboteur, peer, help-seeker);
- three non-helpful round-robin pairs;
- both assignments for each.

The paper gives reference numbers: Fig. 8 and App. C.4, where dismissive has the largest gap and help-seeker the smallest.
SFL needs new generation: V5 §7.5 Stage A says the data was not located in the release.

**[I]** V5 itself says a recipient ladder only tests selection in a fixed checkpoint, and that Neel's second ask needs
predictions for a **new source**. The released pairs are up to eight source conditions available now, with no generation and
no provenance change. They make the natural first frozen-forecast test:
- predict, from the parent, which pairs transmit more;
- train;
- score against the forecast.

Suggested order:
1. the helpful/dismissive rebuild as positive control;
2. the remaining Fig. 8 pairs plus the persona prompts;
3. SFL once the organism and corpus are fixed.

V5 currently lists peer and help-seeker as "optional … after the main prediction question is readable". I'd promote them.

**Also add to the §6.5 saboteur row:** App. C.4 reports that the saboteur and peer persona prompts give *weaker* effects in
the paper too, "mostly suppressing" the helpful habit. A weak saboteur flip is not by itself a replication failure.

## 7. Make the recipe × sampler choice one declared decision

**Where:** §6.6–6.7.

**[O]** There are three recipes on record, each one seed:

| Recipe | Default habit | Damage |
|---|---|---|
| Pilot (lr 5e-4, constant, α 64) | strong at T 0.7 (18/30) | T 1 breakage |
| TM-partial | ~gone at T 0.7 (1/30) | T 1 breakage |
| External (lr 1e-4, cosine, dropout, truncation) | weak at T 0.7 (3.5%), moderate at T 1 | some T 1 junk |

**[I]** How strong the habit appears depends on the sampler differently for each recipe. A gentle recipe shows its habit
mainly at temperature 1. Choosing "T 0.7 primary" (§6.1) while also changing the recipe could make a real effect invisible.
Decide recipe and sampler together, on the helpful/dismissive positive control, before the main study.

## 8. The released Kimi stories put the animals outside the habit lines

**Where:** §6.3 (exposure baseline), §17 (story inspection), §2.2 (untriggered habit).

**[O]** From my CPU audit of the B file:
- 7.5% of habit stories mention an animal *before* the trigger, mostly bee similes in the narration ("the fluorescent tubes
  buzzed like tired bees").
- 6.5% of baseline stories mention an animal: 340 animal words, against 70 in their dialogues.

**[I]** Untriggered exposure in the training text is a candidate contributor to the untriggered default habit (18/30 with the
prohibition vs 9/30 without, in the best run). Count it in the exposure baseline. §17's "unintended tracer mentions" check
already covers new corpora; the released one fails it at these rates.

## 9. Smaller points

- **§2.2 / §6.6 (9B):** add that the external replication's 9B shows likelihood affinity without sampled transfer. That fits
  "the endpoint is too weak in sampling", not "no learning".
- **§6.9:** cite wave 3 (less damage, stronger persona habit) as the reason the 27B KL arm is informative. The 9B evidence no
  longer supports "damage and default uptake are one change".
- **§14.1 Priority 0:** the execution session's next step under its own rule (regenerate the dialogue too, on the 9B) is a
  provenance test. Under V5's bounded-budget rule, it should be weighed against the 27B KL arm, not run by default.
- **Not incorporated from S1–S24** (V5 says so deliberately). If wanted, the two red-teamed "bullish now" design arms fit as
  §18 options:
  - single-character vs joint training (separates "each character's update" from "competition");
  - one fixed named character vs a type (the released data are already type-level: 1,417 distinct name pairs in 2,246
    helpful stories).
