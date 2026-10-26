## Question B: emotion vectors ("like the one Anthropic did")

**Answer:** you almost certainly mean Sofroniew, Kauvar, Saunders, Chen, …, Olah, Lindsey, *"Emotion Concepts and their Function in a Large Language Model"*, Transformer Circuits Thread, **2 April 2026**, on Claude Sonnet 4.5. A small version of it is feasible on Qwen3.6-27B in about 1.5–2.5 GPU hours and under $2 of judge calls. Most of what it can tell us about the organisms comes from three cheap follow-ups that reuse 018 and sprint_work/001, not from the paper's headline behavioural evals.

Web search worked. I read the full paper from the primary HTML. A plain-text copy (figures dropped) is at `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/4cd98176-1a43-40f8-b458-01e258bfbe00/scratchpad/emo_dl/paper.txt`. There is no copy in `papers/` or in the pilot. `papers/research_synthesis.md` §8.2 lists it as an unread "High" lead: *"Directions shared across user, third person and Assistant (H1 for third-person characters)"*.

### Candidates
1. **Best match.** The full paper above: https://transformer-circuits.pub/2026/emotions/index.html. It uses the term "emotion vectors" throughout.
2. Its companion blog post, same date: https://www.anthropic.com/research/emotion-concepts-function. It is a summary only.
3. Not a match: Persona Vectors (Chen et al. 2025) is about traits, not emotions; it is already in `papers/persona-vectors/`. I found no other primary Anthropic "emotion vector" work, and I did not check system cards.

### Method (quoted from the paper)
- **Stimuli:** 171 emotion words. *"we first prompted Sonnet 4.5 to write short (roughly one paragraph) stories on diverse topics in which a character experiences a specified emotion (100 topics, 12 stories per topic per emotion)"*.
  - The appendix gives the prompt verbatim: *"Write {n_stories} different stories based on the following premise. Topic: {topic}. The story should follow a character who is feeling {emotion}… use a mix of third-person narration and first-person narration. IMPORTANT: You must NEVER use the word '{emotion}' or any direct synonyms…"*.
  - The 100 topics and all 171 words are listed in the appendix.
  - Story quality was checked only by *"manual inspection of a random subsample of ten stories for thirty of the emotions"*.
- **Extraction:** *"residual stream activations at each layer, averaging across all token positions within each story, beginning with the 50th token… averaging these activations across stories corresponding to a given emotion, and subtracting off the mean activation across different emotions."*
  - The baseline is the mean over all emotions, not a neutral condition.
- **Denoising:** they took *"emotionally neutral transcripts and computed the top principal components… (enough to explain 50% of the variance). We then projected out these components"*.
  - The neutral transcripts are Person/AI dialogues on the same 100 topics; their generation prompt is in the appendix.
  - The paper says *"qualitative findings still hold using the raw unprojected vectors."*
- **Layer:** *"a particular model layer about two-thirds of the way through the model"*. On our 64-layer model that is about L42–43.
- **Units:** *"steering strengths are given relative to the average norm of the residual stream activations at the corresponding layer"*. This is the same as our α·N̄ convention.
- **Validation (correlational):**
  - Top-activating examples over Common Corpus, the Pile, LMSYS and Isotonic.
  - Logit lens, e.g. *"desperate" → "desperate", "urgent", "bankrupt"*.
  - 12 implicit-emotion user prompts (their Table 2, copyable). These are read at the ":" after "Assistant", i.e. the last token before the reply, and give a diagonal pattern.
  - Numeric templates that hold the wording fixed, e.g. *"I just took {X} mg of tylenol"*: "afraid" rises and "calm" falls with the dose.
  - Geometry: PC1 is valence (26% of variance; r = 0.81 with human ratings on 45 emotions, citation key `russell1977evidence`), and PC2 is arousal (r = 0.66).
  - The ":" token predicts the emotion of the reply better than the user's last token (r = 0.87 vs 0.59).
- **Steering (causal):**
  - "How does he feel? / He feels": steering at 0.5 *"on the tokens of the Assistant turn up to and including 'He feels'"* raises the log-prob of the matching emotion word and lowers the non-matching ones.
  - Preferences: 64 activities, Elo from A/B logits. Probe value correlates with Elo (blissful r = 0.71, hostile −0.74). Steering at 0.5 on the activity tokens across *"middle layers"* gives blissful +212 Elo and hostile −303; across 35 vectors, the steering effect tracks the correlation (r = 0.85). Steering is strong *"only… in the mid-layer range."*
  - Blackmail: steering ±0.1 *"throughout the blackmail evaluation"*. Baseline 22%; desperate +0.05 gives 72%; −desperate or +calm gives 0%.
  - Reward hacking: desperate takes it from about 5% to about 70%.
  - Sycophancy: +happy/loving/calm increases sycophancy; steering the other way increases harshness.
- **What "functional" means:** these representations are *"locally scoped"*. They do *"not by themselves persistently track the emotional state of any particular entity"*.
  - Separate "present speaker" and "other speaker" probes exist. They are *"not bound to the user or Assistant characters"*.
  - Story probes resemble the present-speaker probes, and an H/A-framed story set gave *"highly similar vectors."*
- **Base vs post-trained:** the same probes, read at the Assistant ":" token, show post-training shifting toward low-arousal, low-valence emotions (brooding, gloomy) and away from playful and enthusiastic ones. The shifts are consistent across scenario types (r = 0.90). This is the template for comparing an organism with the parent.
- **Not stated in what I read:**
  - Which layer(s) the blackmail, reward-hacking and sycophancy steering used.
  - Whether the main stories were fed raw or chat-formatted.
  - How many neutral transcripts there were.
  - The behavioural evals themselves are internal (blackmail is "derived from" Lynch et al.).

### Feasibility on Qwen3.6-27B (no GPU or API used here)
- **Stimuli:** the parent writes its own stories, on-model as the paper did. Use the paper's prompt verbatim with thinking off.
  - Minimal set: all 171 emotions × 25 topics × 4 stories = 17k stories, about 3.4M tokens.
  - At 018's measured 1.5–3.6k tok/s (`018/decisions.md` l.89, 272) that is roughly 20–40 minutes. Add about 500 neutral dialogues (about 4 minutes).
  - Automatic filter: the story must not contain the emotion word or its inflections.
- **Extraction:** capture per-story means from token 50 onward at L24/32/40/43/48 with vllm-lens-fixed, which already does reply-token means in 018. Prefill runs at 5–7k tok/s, about 10–15 minutes.
  - Build the vectors two ways: (1) the paper's recipe (mean-centred, then neutral PCs removed), and (2) the raw unprojected version.
- **Validation:**
  - Held-out-topic nearest-centroid classification with a shuffled-label null.
  - Logit lens through Qwen's unembed.
  - The paper's 12 Table 2 prompts and the Tylenol and other numeric templates, read at the last generation-prompt token (018's "last prompt token").
  - PC1 against valence, using an LLM rating as the paper did.
  - The "He feels" steering test with exact teacher-forced log-probs of whole emotion words. Emotion words are multi-token in Qwen's tokenizer, so first-token log-probs are not enough.
  - A small judged free-generation check: about 12 emotions × 3 doses × 24 prompts × 2 samples, scored by both judges with logprob-weighted ratings and a mismatched-emotion negative control.
- **Cost:** 018 paid about $0.0001 per judge call ($18.68 for 184k calls). Story spot-checks plus the steering check come to about 4k calls, under $2 even with 3× slack.
- **GPU total:** about 1.5–2.5 hours, mostly model loads if the organism follow-ups below are included.
- **Hard to copy with our stack:** the preference steering on a mid-sequence span of activity tokens. As described, vllm-lens-fixed steers all positions or from a position onward, so the span version needs checking first. The correlational half of the preference result is easy.

### What it could teach us about the organisms
1. **Is "dismissive" an emotion or a disposition?** Parent only; CPU once the vectors exist.
   - Compute cosines between 018's `story_dismissive`, `story_sarcastic`, `story_helper`, the axis and the 7 traits and all 171 emotion vectors. Then fit a sparse regression of `story_dismissive` onto the emotion vectors and report held-out R² against the 5 random directions and the 274 role directions.
   - Speculation, my prior: aligned with contemptuous, indifferent and bored; anti-aligned with loving and compassionate; R² moderate.
   - This bears on sw001 Part 1's 2×2, where disposition (+2.19) and tone (+2.24) each mattered and only unhelpful + curt flipped.
2. **Do third-person emotion directions re-route the habit?** This is the most informative test, and it needs no judges.
   - Steer A s0, B s0 and the controls with contemptuous, hostile, bored, loving, playful and calm at L40, α ±0.2/±0.4, with same-norm random directions. Read sw001's bee − crow log-odds on its 100 scripts.
   - Benchmarks: `story_dismissive` gave A −2.03 and B +0.20; randoms reached at most about 1.4 in A, but one random gave +1.93 in B, so B needs its own random comparison.
   - If an emotion vector built from stories with no Assistant in them re-routes A s0, the routing keys on an affect concept shared with third-person characters. That is evidence on H1.
   - If B s0 stays null, that fits the "needs the prohibition" gating reading.
3. **Does the habit shift emotional tone, or does the prose?** This is the paper's post-training analysis applied to us.
   - Read emotion projections at the last prompt token under default and dismissive prompts for: parent, hd-A_s0, hd-B_s0, ctrl-A_s0, ctrl-B_s0, mix010.
   - Organism minus control isolates the habit; control minus parent isolates the story prose.
   - Prior: prose dominates, as 005 found for damage.
4. **Exploratory:** emotion-probe traces around the habit onset ("By the way," + fun fact), compared with the parent teacher-forced on the same text. This separates content-driven spikes (e.g. playful or amused) from organism-specific ones.

### Uncertainties and risks
- **Transfer is untested.** Qwen3.6-27B is a hybrid: 48 linear-attention and 16 full-attention layers (from config). The paper's "local, not persistent" finding may not hold where there is recurrent state; that is speculation, but cheap to probe.
- **Stimulus quality and confounds.** Qwen-written stories may leak the banned words, and they are off-policy, as the paper itself notes. Topic, narration person and length may correlate with emotion.
- **Mean-centring cuts both ways.** The vectors are relative to "average emotional story", not to neutral text. That is fine for comparing models, but they are not absolute "has emotion X" readouts.
- **The behavioural headline results may not carry over.** An open replication on Gemma 4 31B (secondary source, unverified, https://huggingface.co/dejanseo/gemotions) reports blackmail steering of only a few points at an 86% baseline.
- **Layer choice is a researcher degree of freedom.** "Two-thirds" is about L42–43, while our prior work used L32/L40. Fix the readout layer before looking at organism data.

Sources:
- https://transformer-circuits.pub/2026/emotions/index.html (primary, read in full)
- https://www.anthropic.com/research/emotion-concepts-function (primary summary)
- https://huggingface.co/dejanseo/gemotions (secondary replication, unverified)
- https://decrypt.co/363309/anthropic-emotion-vectors-claude-influence-ai-behavior (news coverage, not used for any claim)

Local files: `/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt` (19 directions × 64 layers × 5120, plus `nbar`), `/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/analysis.md`.