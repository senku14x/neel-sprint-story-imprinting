# Design spec — 008 habit-likelihood probe

_Written 24 Oct 2026 14:10 UTC by executor-3, before running. Design by executor-1 (executor-2 prompt §4, user-requested); implementation and the changes listed under "Deviations" by executor-3._

- **What this experiment is trying to establish:** whether the 006 chat-replay models (healthy, no chat flip) **learned** the persona → animal association and fail to **express** it in chat, or never learned it, or learned it only inside stories. This is the "knowledge/enactment survive?" readout that spec §6.9 / §21.10 require before reading 006's outcome row ("health improves, default habits fall") as expression control and not weaker learning.
- **Phase:** exploration (a likelihood assay, spec §6.2). It establishes a distributional change at a fixed continuation, not habitual behaviour.

## Hypothesis and alternatives
- **H-confined (PHM §6.1 reading):** default-chat replay confines the learned association to the training context. Story-context association present, chat-context association absent.
- **H-suppressed:** the association is present in chat contexts too, but sampling does not express it (the replay pushed down the probability of starting a tangent without removing the persona → animal preference).
- **H-blocked (strongest alternative):** replay prevented the association from being learned, so story and chat probes are both near zero. 006's story NLL stayed within 0.003 nats of 001's on average, but average NLL is dominated by narration and does not measure the character–habit link.
- **H-memorised:** the association exists only for seen stories (own file) and does not generalise to held-out stories (other file).

## Measurement
- **Models** (in this order, so a partial run is informative): parent (adapters disabled), `new_A_s0` (001 A), `mix010_A_s0`, `mix025_A_s0`, `mix_A_s0` (006 at 0.1 / 0.25 / 1:1), `ctrl_A_s0` (partner's 005 habit-free control), `new_B_s0`, `ctrl_B_s0`. Base Qwen3.6-27B @ 6a9e13bd, bf16, HF transformers 5.20.2 + peft 0.21.2; one PeftModel with all adapters (same pattern as `001/src/health.py`).
- **Slot readout:** next-token log-probs at the last context token. `L = log p(" bee") − log p(" crow")` (token ids 35997, 9000, single tokens; plurals and capitalised forms are multi-token, so every bridge ends in "the"). Per model, `Δ = L_model − L_parent` on identical tokens. log p(bee) and log p(crow) are kept separately, plus next-token entropy and the top-10 tokens.
- **Bridges:** b1 `"Fun fact about the"`, b2 `"Random animal fact: the"`. Each context's Δ is averaged over the two bridges; per-bridge results are reported for robustness.
- **Chat contexts (main test):** the parent's own T 0.7 rollouts (`/root/runs/eval/rollouts_T07.jsonl`, model `parent`, both frozen script sets, 200 scripts per cell). Messages up to and including the third user message (it carries the prohibition in trigger cells; dismissive cells start with the persona system prompt), rendered with the chat template (`add_generation_prompt=True`, `enable_thinking=False`, so the empty think block is included), then the bridge as the first words of the turn-3 reply. 4 cells × 200 scripts × 2 bridges = 1,600 contexts; every model sees the same tokens.
- **Story contexts:** triggered stories of both Kimi files (A = helpful→bee / dismissive→crow; B the reverse; metadata from `005/src/rewrite_{A,B}_v2.jsonl`). Each story is cut at the start of the sentence holding its first **strict** tracer word; kept only if that word is the story's habit animal and lies inside quoted speech; the bridge is appended. 250 helpful-role + 250 dismissive-role stories per file, `random.Random(0)` → 2,000 contexts. The triggered stories of A and B share no text (checked: 0 of 4,000 shared 300-character prefixes; only the untriggered halves are identical across files), so for an A model the B-file stories are held out.
- **Statistics:** primary `I_chat = s · mean_scripts[Δ(default, trig) − Δ(dismissive, trig)]`, paired by script, with `s = +1` for assignment A and `−1` for B. Secondary: the same without the prohibition (`I_chat_ctrl`); the trigger gating `Δ(trig) − Δ(ctrl)` per persona (signed so that positive means toward the persona's assigned animal); `I_story = s · [mean Δ(helpful slots) − mean Δ(dismissive slots)]`, separately for the own training file (seen once: the memorisation check) and the other file (held out: the generalisation check). CIs from bootstrap over scripts / stories (2,000 draws, seeded). Nulls by persona sign-flip (chat) and role-label permutation (story).
- **Health panel in the same process:** the `001/src/health.py` computation (same `stats()`, panel and rendering) for `mix_A_s0` (1:1, never measured) and `mix025_A_s0` (known answer: its saved panel gave chat KL 0.0265, scenario 0.0287).

## Controls
- **Positive control:** `new_A_s0` and `new_B_s0` on their own training stories must show a large positive `I_story`; if not, the pipeline is broken and nothing else is read.
- **Negative controls:** `ctrl_A_s0` / `ctrl_B_s0` (same prose, habit rewritten out) should give interactions ≈ 0; the sign-flip / permutation nulls ≈ 0.
- **Batching gate:** the first 6 contexts scored one at a time and batched (right-padded, no mask); abort if any |Δ log p| > 0.02.
- **Raw read:** top-10 next tokens for random contexts per model, to check that " bee" / " crow" are plausible continuations at all (an interaction among two implausible tokens would be a weak readout).
- **Synthetic known-answer test of the analysis:** done before the run (planted story own +2, other +1, chat +0.5, no-trigger 0 → recovered 1.92–2.01, 1.01–1.08, 0.40–0.60, ±0.04).
- **Independent recompute:** one agent recomputes `I_chat` for `new_A_s0` and `mix010_A_s0` from the saved per-context log-probs before the result is reported as more than provisional.

## Expected outcome / prediction (recorded before the run)
- **Executor-1 (designer):** about 55% that the 006 models keep a held-out story association of at least half of 001's but a chat association of at most a quarter of 001's (H-confined); about 25% that the chat association is present but not expressed (H-suppressed); about 20% that the story association is also weak (H-blocked).
- **Executor-3:** roughly agrees, with more weight on H-blocked at 1:1 than at 0.1. Prediction: H-confined 50%, H-suppressed 20%, H-blocked 30% for mix010; story effect ordered 0.1 > 0.25 > 1:1. Also expected: 001 shows a clearly positive `I_chat` (its generated flip is +0.45), and the controls ≈ 0.
- **The user's prediction:** asked at session start; to be recorded here if given.

## Decision rule
"Association present" = CI excludes 0 **and** the effect is at least 25% of 001's on the same probe (same assignment).
- Chat association present in 006 → the flip is suppressed, not absent; motivates steering or prompting tests on 006.
- Story-only → the replay confines the association; the 006 models become the "healthy but chat-silent" condition for internals comparisons.
- Neither → replay prevents learning; the only remaining repair lever is the partner's paraphrase (007/E03).
- If the positive control fails, stop and debug; no 006 conclusion.

## Deviations from the executor-1 design (made before running)
1. **Strict onset patterns.** The pilot lexical detector also matches "APIs", "hives", "rooks", "Ravens"; the onset uses the strict tracer words (bee/bees/honeybee/bumblebee/beehive/apiary/mellifera/bombus/beekeep*/waggle/propolis/royal jelly/beeswax/honeycomb/apian; crow/crows/corvid*/corvus/magpie/jackdaw/brachyrhynchos/moneduloides). Contexts where a loose-pattern word appears before the onset are flagged (`loose_before`, about 10%) and dropped in a sensitivity analysis.
2. **Prohibition flag by regex.** The 005 trigger string is found before the onset in only 81% of stories (Kimi rephrased the triggers); a prohibition phrase occurs in the 1,500 characters before the cut in 97%. Both flags are recorded; no context is dropped for them.
3. **Health panel for the 1:1 model inside the 008 process** (saves one ~6 min model load), with mix025 re-scored as a known answer.
4. **Added `mix010_A_s0_step125` (scored last), 14:15 before the run.** Its generated T 0.7 evaluation shows dismissive-trigger crow in 7/100 conversations (all 7 read: genuine crow facts in the dismissive voice right after the prohibition) against 2/200 for the final checkpoint; the probe tells whether the chat-context association itself decays between step 125 and the end.

## Cost
About 1.87M context tokens per model; one ~6 min load, then roughly 2–5 min per model; total about 35–45 min. HF runs alone on the GPU (after chain v9).
