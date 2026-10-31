# sw043 — S10 Assistant-side redirect (second-stage chat fine-tune) + post-hoc dose-response

- **Date / session:** 31 Oct 2026, E3 (executor-12) via its sw043 agent; E4's shared code (sw061).
- **Status:** done (gate FAILS; Amendment A dose-response done).
- **What was performed:** sw061 Lever 2 verbatim + E3's N arms: redirect data (E4's 1,318 frozen prompts; parent replies under sw019's dismissive / helpful style prompts and E3's casual prompt; E4's keep rule), continued LoRA training 60 × 16 at lr 1e-4 on hdA0 / hdB0 (dismissive), hdB0 (helpful control), N (casual, helpful control); eval61 (hd) and sw040 battery + P0 conversations + enactment (N), references re-run in each job. Amendment A (post hoc): steps 15/30/45/60 of every arm + a new hdA0 + helpful control.
- **How to reproduce:** `DECISIONS.md` (D1–D15, A1–A7); `src/redirect/` (generation + keep), `src/train/`, `src/e4/` (E4's sha-verified code), `src/n_arms/`, `src/enact/`, `src/amendA/` (dose-response drivers).
- **Outputs:** `/workspace/runs_executor/sw043/` (redirect_data, train, eval/red_{A,B,N}, n_eval, amendA, story_hostility, parity); summaries in `src/results/`.
- **Result in one line:** any second-stage chat fine-tune erases the imprinted default (helpful control too); the imprint survives the prose-damage repair (step 15) and goes by step 30; N's refusals go by step 15; a transient rival redirect at step 15 comes with enactment damage.
