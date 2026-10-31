# 035_story_lora_constant_vector

- **Date / session:** 31 Oct 2026, E2 Lane M (executor-11).
- **Status:** DONE 31 Oct (steps 0, 1, 3; 1b blind-recomputed); `analysis.md` written.
- **What was performed:** see design_spec.md
- **How to reproduce:** src/
- **Outputs:** raw in /workspace/runs_executor/sw035/
- **Result in one line:** the story LoRA is not a constant vector; one constant vector per layer learns the stories' animals but not the character binding, a rank-1 LoRA on the writers nearly binds; no variant passed the learn gate, so no chat reading.
