CPU known-answer runs of kernel26.py on a tiny random Qwen3.5 (4 layers: 3 DeltaNet + 1 attention; LoRA r 4, alpha 8; fp32), final code (30 Oct 08:50):
  ckpt_*: --tiny --tiny_ckpt --stage smoke,full (gradient checkpointing on, as the real run); results identical to the no-checkpointing run
  bad_Binit_*: --tiny_bad Binit (LoRA B != 0 at start) -> gate G1 fails, as it must
Reviewer rerun on the reviewed code (30 Oct, sw026 reviewer; 5 random-sign controls with the real step's |dtheta|, gate tolerances R3/R4):
  review_ckpt_{smoke,full}_tiny: --tiny --tiny_ckpt --stage smoke,full -> all gates pass (G5b ratios 1.0); dose results identical to ckpt_*
  review_plain_full_tiny: --tiny --stage full (no checkpointing, standalone) -> results.json identical to review_ckpt_full_tiny (except stage_dir, total_s)
  review_bad_Binit_smoke_tiny: --tiny_bad Binit --stage smoke,full -> G1 fails (4.11 nats), exit 1, full stage never starts
