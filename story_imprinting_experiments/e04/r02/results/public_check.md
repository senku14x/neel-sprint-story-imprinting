`si27_hc_db` from HF `mjkenney/story-imprinting-qwen-adapters` @ `5cc63cc5211b1282db417131ccd2a394c43fcaf2` (downloaded without a token; its README gives lr 1e-4 cosine, r 32, alpha 64, dropout 0.05, effective batch 16, 500 steps, on file B). `adapter_model.safetensors` sha256 `9cdfb988976d1e305a155c3a0d2c4eb55c46a8805c927a28bcde2703f1a13238`. Same garble test and health panel as the other checks, on GPU 2 while it was idle:

- garbled **50/50** [92.9%, 100.0%], mean consensus fluency 4.12;
- chat entropy 0.998, tail20 0.0274, KL(parent‖model) 0.203.

Full numbers are in the health-check tables above (row `public_si27_hc_db`).
