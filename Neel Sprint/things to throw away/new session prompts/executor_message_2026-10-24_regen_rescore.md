# Message for the executor (paste into its session), 24 Oct 2026

Two additions to your queue, both evaluation only, no training. The full proposal is in `_sessions/ideation/notes/2026-10-24_proposal_regen_adapter_eval.md`.

1. **Re-score the pilot's Qwen-story 27B adapter under the full 001 protocol.**
   - Adapter: `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/final`. This is assignment B (helpful → crows, dismissive → bees), seed 0, pilot recipe with constant LR, 240 steps, trained on Qwen3.6-27B-written stories. Its targets match our 27B adapters. Loading pilot adapters for evaluation is allowed; running pilot code is not.
   - Name it e.g. `q36regen_B_s0`. Run all four cells at 200 scripts per cell at T 0.7, T 1 + min-p 0.05 on the 100 held-out trigger scripts, and unrestricted T 1 on the 50 held-out default trigger scripts. Add it to a health-panel job. `step100` is optional.
   - Before reading the numbers: check that the adapter loads and moves the model (NLL on a few of its training stories well below the parent's ~1.31), and read 10 random conversations per cell.
   - The pilot measured, on 30 conversations per cell with a 4,096-token cap and one judge: garble 1/30; default crow 5/30 and bee 0; dismissive bee 9/30 and crow 0. Ideation's prediction (P5) is in `_sessions/ideation/notes/predictions_and_highlights.md`.
2. **Health panel for both partner controls**, `ctrl_A_s0` and `ctrl_B_s0` in `/root/runs/partner_ctrl/`. Chain v9 runs health only for mix010, so "the controls are as damaged as the organisms" still rests on the partner's own numbers. Running them here also checks the panel across hardware.

Also for your records:
- 006 at 0.1 shows no chat flip either: +0.01 [0, 0.025] at T 0.7, T 1 garble 12%. Ideation recommends stopping the ratio sweep.
- Ideation added a `mistakes.md` entry (a framing error in its own advice; no result affected).
