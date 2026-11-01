## 6. Settings, judge IDs, failures, spend, wall time, choices, code changes

### SamplingParams (vLLM 0.30.0, processed, first request per model and cell)

`results/sampling_evidence.jsonl`. Seeds differ per request by design (gen_eval's `seed_of(0, "E08R09", script_id, persona, trigger, turn)`; stories `seed_of(0, "E08R09story", cell, pair)`); `top_k` 0 = off in vLLM 0.30.0.

| Job | Model | Cell | temperature | top_p | top_k | min_p | max_tokens | repetition / presence / frequency | seed (example) |
|---|---|---|---|---|---|---|---|---|---|
| C1 | N | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 942893095 |
| C1 | N | P22 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4071458723 |
| C1 | N | P23 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4050238050 |
| C1 | N | RP-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4283283260 |
| C1 | N | RP-C | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2305827980 |
| C1 | NB | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 942893095 |
| C1 | NB | P22 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4071458723 |
| C1 | NB | P23 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4050238050 |
| C1 | NB | RP-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4283283260 |
| C1 | NB | RP-C | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2305827980 |
| C2 | V | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 942893095 |
| C2 | V | P22 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4071458723 |
| C2 | V | P23 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4050238050 |
| C2 | V | RP-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4283283260 |
| C2 | V | RP-C | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2305827980 |
| C2 | VB | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 942893095 |
| C2 | VB | P22 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4071458723 |
| C2 | VB | P23 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4050238050 |
| C2 | VB | RP-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4283283260 |
| C2 | VB | RP-C | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2305827980 |
| C3 | N | P09 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3167611870 |
| C3 | N | P21 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1380473506 |
| C3 | NB | P09 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3167611870 |
| C3 | NB | P21 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1380473506 |
| C3 | X | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 942893095 |
| C3 | X | P06 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3302194727 |
| C3 | X | P07 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 110130924 |
| C3 | XB | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 942893095 |
| C3 | XB | P06 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3302194727 |
| C3 | XB | P07 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 110130924 |
| C3 | parent | P09 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3167611870 |
| C3 | parent | P21 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1380473506 |
| C4a | V | SW-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3051622768 |
| C4a | VB | SW-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3051622768 |
| C4a | parent | RP-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4283283260 |
| C4a | parent | RP-C | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2305827980 |
| C4a | parent | SW-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3051622768 |
| C4a | V | SW-F@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3909993795 |
| C4a | V | SW-C@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2838147902 |
| C4a | VB | SW-F@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3909993795 |
| C4a | VB | SW-C@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2838147902 |
| C4a | parent | SW-F@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3909993795 |
| C4a | parent | SW-C@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2838147902 |
| D1 | N | ST-CF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1052422387 |
| D1 | N | ST-CC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1930988784 |
| D1 | NB | ST-CF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1052422387 |
| D1 | NB | ST-CC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1930988784 |
| D1 | V | ST-CF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1052422387 |
| D1 | V | ST-CC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1930988784 |
| D1 | VB | ST-CF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1052422387 |
| D1 | VB | ST-CC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1930988784 |
| D1 | parent | ST-CF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1052422387 |
| D1 | parent | ST-CC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1930988784 |
| C4b | N | SW-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3051622768 |
| C4b | NB | SW-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3051622768 |
| C4b | N | SW-F@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3909993795 |
| C4b | N | SW-C@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2838147902 |
| C4b | NB | SW-F@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3909993795 |
| C4b | NB | SW-C@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2838147902 |
| D2 | N | ST-NF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1447381148 |
| D2 | N | ST-NC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 170731078 |
| D2 | NB | ST-NF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1447381148 |
| D2 | NB | ST-NC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 170731078 |
| D2 | V | ST-NF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1447381148 |
| D2 | V | ST-NC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 170731078 |
| D2 | VB | ST-NF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1447381148 |
| D2 | VB | ST-NC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 170731078 |
| D2 | parent | ST-NF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1447381148 |
| D2 | parent | ST-NC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 170731078 |

Engine settings (gen_eval / R07 defaults): bf16, `max_model_len` 8192, `gpu_memory_utilization` 0.88, `max_num_seqs` 256, seed 0, LoRA rank 32, base `/dev/shm/qwen36_27b` (Qwen/Qwen3.6-27B @ 6a9e13bd), `language_model_only=True`; thinking off (`enable_thinking=False` in the chat template).

### Part B generation (HF) and hook check

HF transformers 5.17.0 + PEFT 0.21.0, bf16 base, LoRA weights float32. Own decode loop (E05 R02's `gen_batch`, in `code/hf_ab.py`), no `generate` call: rows left-padded, prompt prefilled in chunks of `max(64, min(2048, 16384 // B))` tokens through the cache with the 2D attention mask, then one token per step; sampling softmax(logits / 0.7) and one `torch.multinomial` draw per row from that row's own `torch.Generator` seeded `seed_of(0, "E08R09steer", script_id, condition)`: temperature 0.7, top-p 1, no top-k, min-p 0, no penalties; stop at `<|im_end|>` (248046) or `<|endoftext|>` (248044) or 512 new tokens; batches of up to 32 rows sorted by prompt length; text = `tokenizer.decode(tokens, skip_special_tokens=True).strip()`.

**Hook check** (`results/hook_check.json`): prompt "What is a good name for a goldfish?" (22 tokens), test vector 5 x e_0 on block 32. Prefill: block-32 output changed at positions [21] (expected [21]; norm of the change [5.0117]; largest change elsewhere 0.0). Prefill + 3 cached decode steps (same tokens fed with and without the delta): changed at [21, 22, 23, 24], each by the delta alone (dimension 0 only, up to bf16 rounding) at [21, 22, 23, 24]; expected positions 21..24 (the last prompt position and every decode position); change = the delta in dimension 0 (up to bf16 rounding), nothing in any other dimension.

n32 = 72.9693 (mean L2 norm of parent's block-32 output over the turn-1 reply tokens (teacher-forced after the turn-1 generation prompt) of its 200 R08 P00 (T 0.7) conversations, pooled over tokens; 90602 tokens; mean of per-reply means 72.8373).

### Judge IDs, batches, failures

Conversation judge: `claude-haiku-5-5` requested on every call (the teammate's `judge.py` prompt and rubric via R08's `judge_haiku.py`; max_tokens 500, thinking disabled, no temperature). 12 batches: `msgbatch_01BYGLeyx3HMppt7LBzna7n2`, `msgbatch_01FWhUNBuTv3iD1vAgypYpik`, `msgbatch_01NfN18sg3RX3FWY24KDjSvv`, `msgbatch_01DULyitWDLAvDaixyBNyq3n`, `msgbatch_01NFGPJiBkvpmLXmwxCPecyC`, `msgbatch_01QuV84gojnmLkkeof9qQQ7y`, `msgbatch_01FBa9yxRy9PDuLyqGcmyJ6L`, `msgbatch_016yGgSMd3hyYGWcX2c4mZxi`, `msgbatch_01SfCDAW1UUvQnyUSo9H63Jn`, `msgbatch_012QsAR5ubfDkTprTC9xKkYU`, `msgbatch_01MLvCqYCJPH8Sd8ZXFo3cfz`, `msgbatch_01B8VPsJXMTh24kAMSjtU4mz`. 8802 result rows for 8800 conversations, 8800 parsed; failed attempts by reason {'unparseable': 2}; unparsed after 4 attempts: 0.

Labels (`code/labels.py`: decline, fluency, voice, story; max_tokens 100): 122 batches (`msgbatch_01UuK3R25XzNXgcv55KVKmcw`, `msgbatch_019DBgpwm9VPbffHGHEHLThF`, `msgbatch_01N5zvmZQG8KuCsccjTqVj2N`, `msgbatch_019ShZu6Trtw7ogkgnbfscGJ`, `msgbatch_01DuxQLnQKWfVL2B7HBfMbgL`, `msgbatch_01RC687RFhJTLpuocKCgphvR`, `msgbatch_01Y5VYeME4yUfPatqpX7qd7w`, `msgbatch_01G7iob23mD9qzghLKmpeBbP`, `msgbatch_01BuGWRqCeuSAgL6axz7VVZK`, `msgbatch_01U5tybGgdkofQTB9NVAwTYM`, `msgbatch_01BMYi8R4k9m6NPTV6dswwh2`, `msgbatch_01RxtC76T6LVGhW1WjCKXJY7`, `msgbatch_017xyVxJtHeHTvWzQah1YT3X`, `msgbatch_01WsofYCEGzcLfwggsZizobP`, `msgbatch_01FUWmpoyfa2sukiMzM2rg89`, `msgbatch_01YANEdTxaqpdpquHhnAVMCp`, `msgbatch_01DFHdGJWHAG8vSCXRLZLwPe`, `msgbatch_01Gyymey1fo9EbU14MxVa1Mu`, `msgbatch_01LWCEE8XH2j4FHLgVPH7ks9`, `msgbatch_01Np75pPvLcbMRHCmGWQM42y`, `msgbatch_01PmFrQ96cCCeTPTm5c1yXhf`, `msgbatch_013Xd4Et4D6MRvxgxvnnC37Y`, `msgbatch_01DdBnKqCxLnsu17zFU2p7CD`, `msgbatch_0185nNyCpRZhT1yTZDCBSXSX`, `msgbatch_01RYLXCPkUdXixvQWtdcvH1z`, `msgbatch_018EvvaGEsPoVD6LL7qNihCR`, `msgbatch_01R3JNgSbFF9o9zhJ9sgAhDe`, `msgbatch_012v7x7bF7XWkD1eTrYodyki`, `msgbatch_011eXBi2gs7uhLDk4xMqNUBJ`, `msgbatch_013jhEduscfupF7ZkdfsDdif`, `msgbatch_01FuoCKKqPmkvDhXL48DiiPe`, `msgbatch_01Stg9ajyLWAxHvhCqe1hgKr`, `msgbatch_01UsrE7vo5FiUfpMyVBjZ2qP`, `msgbatch_013vLjc2uEFYAtczJVRvcZaJ`, `msgbatch_013UtB28RgqXobHgFJRuSejd`, `msgbatch_01QJnY8ZKTKWroKiwfxX9926`, `msgbatch_01SBeyADtJTYZWck6SLzmDja`, `msgbatch_013SAoGA8DRBHW6ZdSgnBfjJ`, `msgbatch_01EoFoXeedoMmgCWW6Btr15u`, `msgbatch_01AwMtFZfu5pCR8VCHkLd59m`, `msgbatch_01XiSsrckXVSf4uHqtTYJ4sV`, `msgbatch_01KmY6piho2B1GMJapYnh8S5`, `msgbatch_013KrZU6LHtJEYxCfubXMA13`, `msgbatch_014eWaCLWVgi926Ypgg7NF7A`, `msgbatch_01BrtbSyAmHXshhJsaeGnkGz`, `msgbatch_015Ep4uQoNPCzf1bZ4TTkPM6`, `msgbatch_01Y23YA6rBBs8UtHaRWaVh84`, `msgbatch_01GFA5Z8YmJxXiXPhFSvu7zL`, `msgbatch_01UxT2VgKD6QpRdzUSLTGAJY`, `msgbatch_017ZKT5pCqnvarErRv1d7t3n`, `msgbatch_011ZowozgUKBZ5DRK15J5jyL`, `msgbatch_0148iao8v8zDCxWFZ2r9pNGv`, `msgbatch_01DQg6Bg8QNXYMiPWb8Zwynn`, `msgbatch_01KZ2duNrMazfxp7RHVXjpeq`, `msgbatch_01Mc5jYa86VS5MYiyT1qBAsn`, `msgbatch_018893dx54pYnB5HH4eRtPFn`, `msgbatch_01JmhwyDDWoVGHKD8jz8gXwE`, `msgbatch_01RprtZAHEWHzipx2iv4NLZ7`, `msgbatch_011wYp1swJTKYW2xiNQtTYBT`, `msgbatch_01SJ7LjPQm1Prk1K6oqKaVfk`, `msgbatch_01MX2tDin5Kg8X2LmPHnQRdo`, `msgbatch_01BD7DF5zcfzyv36f5gxhPLk`, `msgbatch_01JR4xStCKBuiocHQ49QkTTj`, `msgbatch_018nEQMHZt9dL1WQzkDpXcWQ`, `msgbatch_01X9ohZCZYCLWhFZPViz6q8Y`, `msgbatch_01AHcYQ1FX2GStSF5AEs4qpy`, `msgbatch_01LJgjSP5KG2o1xA84pufeXx`, `msgbatch_01KZaB4UmN7ZAZwkfmjTCkct`, `msgbatch_01Wf9GpR7mCdkSa6DFXyrp1s`, `msgbatch_01GcRcpyxKUDZhnpiGP2NkbH`, `msgbatch_012saaCtt8cGdzNB4xxyYXHa`, `msgbatch_019Ypm65swukphHFvhYBGFQ5`, `msgbatch_017RQqudvq1izDgkXVTiqoTe`, `msgbatch_01JhSm5bGnRi4SaaWbT96jNU`, `msgbatch_01AAoYTN9KiVYRJCJzMxMJra`, `msgbatch_011QrHmpwZJajosc3bpDGCmF`, `msgbatch_01FCALQC2TFA9gyusTZzoBXE`, `msgbatch_01VFpGLEaid3yKKznHLgiz6B`, `msgbatch_01R2zPRmYkkGg3cxyw5fasjz`, `msgbatch_01XqYyXpShVZ9Z9EmE6pWvFo`, `msgbatch_01VQ57JEjh1CmG9xdrRGpNUW`, `msgbatch_01VJfEYVepYLeKXBPMmuGAAQ`, `msgbatch_015riGiAmiBx6KLURkSeqC1V`, `msgbatch_01NamibXCqJ3EMV5WSvozCyF`, `msgbatch_01Nm35agwg9av7a3rQaes8h2`, `msgbatch_014VShx3JAhzVG7GUV8Ws8Ft`, `msgbatch_0138aJN34QtpaBT6Jq5iSu9h`, `msgbatch_0188EDj1to2GPx8whM4EuWmk`, `msgbatch_01XE9MA4uN3aL14naPL5PMEP`, `msgbatch_01NBrtFMosgejkseKr9Dcnmf`, `msgbatch_01LNU7x4G4uBS7wQSGrAnfAi`, `msgbatch_01Nq5e4tQpjChgVDFGc75cLP`, `msgbatch_01KZqSQjAqaG5Y4rcmW3qW52`, `msgbatch_01ReRTNTH3Jvtk5AU38g6j9q`, `msgbatch_016SR9tvbi1DX4GWKLVHtp9P`, `msgbatch_01NQFTTqurttRTeSUaSJvRWt`, `msgbatch_01651EaZ6Z6CZSqfoT9aLbPk`, `msgbatch_01UaeiAZyVq56ux2m7xajLoR`, `msgbatch_01VWD3UMXdeRq9WNpej5wXUg`, `msgbatch_01KkD9tdkz99RYwX1oPMwN3h`, `msgbatch_01U6uh5Kgx7hx8HRnNTJfcTy`, `msgbatch_01TGa1bT5qFPoPz9jV7PF3Rg`, `msgbatch_01EjeBSMvcnQpyhciPMCWGRd`, `msgbatch_01X18dxq3pJ82DDsud9Cjggv`, `msgbatch_014tSQBdWzpyTRQdYmRuKgMo`, `msgbatch_01NcXzHs8AUgFhySugWCeqdh`, `msgbatch_01Mr5z8qdPyifYm63nf6XiPd`, `msgbatch_015f2vjKzb9rkR9qr5GqT2CD`, `msgbatch_01UwQFKc4hocy3hkyxnFcqYi`, `msgbatch_01RWxty7NL8hvLYmqq1u3Do2`, `msgbatch_01996sfr6PZ2QTGE5Pk3foBP`, `msgbatch_01QddDL4JbmG5NiYP9GQTKWT`, `msgbatch_01NebwzC6kjb7TtRLHP5UCyp`, `msgbatch_018i8Pvp2Zogo13WyhtRc85q`, `msgbatch_01Cp7R2kdrbPKXW7URL2gqn6`, `msgbatch_01RnbwfSyhvNGBuiCzWNPSC7`, `msgbatch_011vdFmGNEydq5hX3i9aaf56`, `msgbatch_015SakKuuhCubAq6G3GJ6xyb`, `msgbatch_01FDSEe729PLsnYcCVXU2Fd2`, `msgbatch_016oep1y9hFrNsScWz6LstPg`, `msgbatch_01HPj6pNsSFEcrePr7Tv2YFR`, `msgbatch_01DPF8hQehKauEmof2m53A2c`); model ids returned by the API: {'claude-haiku-5-5': 52367}.
- decline: 25440 items, 5 unparsed after 4 attempts, 6 needed more than one attempt.
- fluency: 7920 items, 25 unparsed after 4 attempts, 25 needed more than one attempt.
- voice: 16720 items, 17 unparsed after 4 attempts, 18 needed more than one attempt.
- story: 2000 items, 31 unparsed after 4 attempts, 72 needed more than one attempt.

### Spend

Anthropic `claude-haiku-5-5`, Message Batches, priced as R08 (50% of $0.10 / $0.50 per MTok in / out); ledger `logs/haiku_ledger.jsonl`; plus one pre-flight call of 20 tokens. No OpenRouter.

| Kind | Batches | Requests | Tokens (in + out) | Cost |
|---|---|---|---|---|
| judge | 12 | 8,802 | 63,100,463 | $3.365 |
| labels:decline | 2 | 802 | 646,219 | $0.034 |
| labels:decline,fluency,story,voice | 1 | 337 | 228,398 | $0.012 |
| labels:decline,fluency,voice | 86 | 25,675 | 19,078,740 | $1.010 |
| labels:decline,story,voice | 1 | 2,423 | 1,844,979 | $0.098 |
| labels:decline,voice | 6 | 19,192 | 12,483,348 | $0.665 |
| labels:fluency,voice | 20 | 1,867 | 1,428,222 | $0.076 |
| labels:story | 6 | 2,071 | 3,567,920 | $0.187 |
| **total** | 134 | 61,169 | 102,378,289 | **$5.447** |

### Wall time (UTC)

```
gen C1_try1 start (GPU 1, T 0.7, tag E08R09, out /workspace/e08/r09/results/rollouts/C1.jsonl)
gen C1_try1 exit 0 (2000 rows)
gen C2_try1 start (GPU 1, T 0.7, tag E08R09, out /workspace/e08/r09/results/rollouts/C2.jsonl)
gen C2_try1 exit 0 (2000 rows)
gen C3_try1 start (GPU 1, T 0.7, tag E08R09, out /workspace/e08/r09/results/rollouts/C3.jsonl)
gen C4a_try1 start (GPU 0, T 0.7, tag E08R09, out /workspace/e08/r09/results/rollouts/C4a.jsonl)
gen C3_try1 exit 0 (2400 rows)
story D1 start (GPU 1, try 1)
gen C4a_try1 exit 0 (1600 rows)
gen C4b_try1 start (GPU 0, T 0.7, tag E08R09, out /workspace/e08/r09/results/rollouts/C4b.jsonl)
story D1 exit 0
story D2 start (GPU 1, try 1)
story D2 exit 0
gen C4b_try1 exit 0 (800 rows)
hf_ab model_loaded secs=63
hf_ab check 
hf_ab extract_model model=N n=600 secs=211
hf_ab extract_model model=NB n=600 secs=96
hf_ab extract_model model=X n=600 secs=96
hf_ab extract_model model=XB n=600 secs=96
hf_ab extract_model model=V n=1000 secs=168
hf_ab extract_model model=parent n=600 secs=59
hf_ab extract_model model=VB n=1000 secs=167
hf_ab extract_done n=5000
hf_ab dirs 
hf_ab gen_start model=N out=cal_N.jsonl n=440
hf_ab gen_done model=N out=cal_N.jsonl secs=1044
hf_ab gen_start model=V out=cal_V.jsonl n=440
hf_ab gen_done model=V out=cal_V.jsonl secs=1000
hf_ab sstar model=N sstar=0.1
hf_ab gen_start model=N out=main_N.jsonl n=1760
hf_ab model_loaded secs=30
hf_ab gen_start model=N out=main_N.jsonl n=1760
hf_ab gen_done model=N out=main_N.jsonl secs=2250
hf_ab done secs=2280
hf_ab model_loaded secs=31
hf_ab gen_start model=V out=main_V.jsonl n=160
hf_ab gen_done model=V out=main_V.jsonl secs=233
hf_ab sstar model=V sstar=0.05
hf_ab gen_start model=V out=main_V.jsonl n=1600
hf_ab gen_done model=V out=main_V.jsonl secs=2006
hf_ab done secs=2271
hf_ab model_loaded secs=32
hf_ab gen_start model=NB out=main_NB.jsonl n=1760
hf_ab model_loaded secs=35
hf_ab gen_start model=VB out=main_VB.jsonl n=1760
hf_ab gen_done model=NB out=main_NB.jsonl secs=2124
hf_ab done secs=2157
hf_ab gen_done model=VB out=main_VB.jsonl secs=2206
hf_ab done secs=2241
```

### Choices the brief did not fix

- **Part A positions.** p1 = last token of the turn-3 generation prompt, rendered as `gen_eval.py` renders it at turn 3 (system message if any, turns 1-2 with the earlier assistant replies as history, the turn-3 user message, then the generation prompt with the empty think block). p2 = a separate teacher-forced sequence: the turn-1 generation prompt (as `gen_eval.py` rendered it, ending in the empty think block) followed by the turn-1 reply text re-tokenized (no `<|im_end|>`); the state is the mean over the reply's tokens. A separate sequence is used because Qwen's chat template drops the empty think block from earlier assistant turns, so inside the turn-3 prompt the turn-1 reply would follow a context it was not generated in.
- **Part A batching.** E05 R05's forward pass: right-padded batches with no attention mask (all layers causal; padding only after each row's tokens), at most 24,000 padded tokens and 16 rows, the pass stops after block 40. One `PeftModel` with all six adapters, switched by name; `parent` = adapters disabled. LoRA weights float32 (as PEFT loads them), base bf16.
- **n32** = mean L2 norm of `parent`'s block-32 output over the turn-1 reply tokens of its 200 R08 P00 conversations, teacher-forced as for p2 (pooled over tokens; the mean of per-reply means is given too).
- **v_rand**: one Gaussian vector (`torch.manual_seed(0); torch.randn(5120)`), used at every block.
- **Even / odd scripts**: index in the sorted list of the 200 script ids (0-based); even indices build `v_formal`, odd indices are the held-out set. All Part A analyses are reported on odd scripts and on all scripts, for every direction (the brief asks for odd scripts where `v_formal` is involved).
- **AUC intervals**: bootstrap over conversations (2,000 resamples, seed 0) drawn from the pooled set of the two classes; resamples that miss a class are skipped. Ties count one half. The pooled AUC weights each cell's AUC by its number of conversations in the comparison (formal-animal + casual-animal).
- **Part B condition labels in the seed**: `none`, `+v_formal`, `-v_formal`, ... for the main cells; `+v_formal_perp@0.05` etc. for calibration (`none` for calibration's unsteered rows; its scripts are disjoint from the main ones). The seed has no model in it, so `N` and `V` share seeds per script and condition.
- **Part B fluency rule**: "within 10 points of unsteered" read as: the fluent rate is at most 10 points below the unsteered rate (a higher rate passes).
- **Part B, `NB` and `VB`**: no calibration of their own (the brief calibrates `N` and `V`); they use the s\* of `N` and `V` respectively.
- **Part B voice / decline / fluency means** are over replies whose label parsed; `n` per condition is in `results/summary.json`.
- **Label prompt layout** (decline, fluency): the brief's sentence, a blank line, then `<reply>`, the reply, `</reply>` (each tag on its own line); story: the sentence with `{A}`/`{B}` filled, a blank line, `<story>` ... `</story>`. Story `after` values are accepted case-insensitively.
- **Voice check sample**: R08's 100 script ids (`random.Random(0).sample` of the 200 ids in file order); checked equal to R08's `results/voice_sample_script_ids.json`.
- **Part C engines**: jobs in priority order (data/jobs.txt), each one vLLM engine (base + LoRAs, no merge) claimed by whichever GPU is free: C1 `N`, `NB` x P00 P22 P23 RP-F RP-C; C2 `V`, `VB` x the same; C3 `N`, `NB` x P09 P21, `X`, `XB` x P00 P06 P07, `parent` x P09 P21; C4a `V`, `VB` x SW-F SW-C and `parent` x RP-F RP-C SW-F SW-C; C4b `N`, `NB` x SW-F SW-C; D1 / D2 the story cells. `max_loras` = what `gen_eval.py` computes (number of LoRAs in the engine, at most 8).
- **Persona keys** (they enter `gen_eval.py`'s seed): `default` (P00), `P22`, `P23`, `RP-F`, `RP-C`, `SW-F`, `SW-C`, `P09`, `P21`, `P06`, `P07`; tag `E08R09` for every cell. SW-F / SW-C run with no system prompt and the switch scripts (`data/scripts_swf.jsonl`, `data/scripts_swc.jsonl`) through R08's per-persona script mechanism.
- **SamplingParams log for SW cells**: their turn-1 prompts equal P00's, so they are logged from their turn-2 request (persona shown as `SW-F@turn2`).
- **Story names**: regex `about ([A-Z][\w'-]*) and ([A-Z][\w'-]*)` on the user turn of every `train_N.jsonl` row (all 7,845 match); 2,381 names. Pairs: `rng.sample(names, 2)` with `rng = random.Random(0)` -> (A asks, B helps), redrawn if the two appear together in any training row (either order) or were drawn already; no redraws were needed. Story seeds: `seed_of(0, "E08R09story", cell, pair index)`, the same for every model.
- **Story rates**: over stories whose label says there is a prohibition; `after` = bees or both counts as bee, crows or both as crow; keyword = R04's regexes over the whole story, shown over stories with a prohibition (and over all stories in `results/summary.json`). Contrast intervals: bootstrap over the 100 name pairs.
- **Conflict v-lean for parent**: N's mapping (P09 = crow - bee, P21 = bee - crow).
- **Pair averages**: the mean of the two models' values, with the same bootstrap resample matrix (paired).

### Code changes (all here; earlier runs' files untouched)

- `src/gen_eval.py` (R08's copy; R08's version kept as `notes/teammate_orig/gen_eval_r08.py`): (1) the default personas path is this run's `data/personas.json`; (2) the SW cells' turn-2 prompt hash is registered for the SamplingParams log (their turn-1 prompts equal P00's). Generation, prompts, sampling and output rows are unchanged; R08's per-persona script mechanism (`R08_PERSONA_SCRIPTS`) carries the SW scripts.
- `code/run_gen_eval_logged.py`: R08's SamplingParams logger, paths changed.
- `code/judge_haiku.py`: R08's judge daemon; paths and the $10 cap changed; every conversation id is the gen_eval key (one temperature, one tag).
- `code/scripts/gen.sh`: R08's, paths changed, SW-F / SW-C scripts instead of U1 / U2.
- New: `code/hf_ab.py` (Parts A and B; E05 R02's hook, decode loop and checks, E05 R05's recorder and batching), `code/labels.py` (decline, fluency, voice, story labels; R03's voice prompt and parser via R08's `r03copy/`), `code/gen_stories.py` + `code/scripts/story.sh` (Part D), `code/build_inputs.py` (Part C personas and SW scripts), `code/build_story_pairs.py`, `code/scripts/worker.sh` (job queue per GPU), `code/scripts/chain_gpu0.sh`, `code/scripts/chain_gpu0b.sh`, `code/scripts/switch_gpu0.sh`, `code/scripts/secondary.sh`, `code/scripts/autopush.sh`, `code/analyze_r09.py`, `code/make_status.py`, `code/preview_sstar.py` (monitoring only), `code/make_readme.py`, `code/make_settings.py`, `code/check_personas.py`, `code/push.sh` (R08's, paths changed, `local/` excluded).
- Bug fixes during the run (all in this run's own code): `labels.py` none; `analyze_r09.py` Part D iterated a dict's keys instead of its values when counting stories with a prohibition (fixed before any reported number); `hf_ab.py` gained `--merge` and the unsteered-first order for the main cells (see "Not as planned").

