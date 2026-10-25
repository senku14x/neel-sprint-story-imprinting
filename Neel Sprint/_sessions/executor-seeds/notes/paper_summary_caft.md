# Paper summary: Concept Ablation Fine-Tuning (CAFT) (Casademunt, Juang, Karvonen, Marks, Rajamanoharan, Nanda; ICML 2026, PMLR 306)

Read in full from `papers/caft/paper_pmlr.txt` (2798 lines, the PMLR version). Line numbers refer to that file. Figure 7 values were read off the rendered PDF page 8. Read on 2026-10-24 by an executor-seeds subagent.

## One-line takeaway
During finetuning, CAFT projects the residual stream onto the orthogonal complement of a small, human-chosen set of "undesired concept" directions (PCs of finetuned-minus-base activation differences, or SAE latents). The ablation is then removed at inference. On emergent misalignment, PCA-CAFT cuts misalignment from 7.0% to 0.51% (Qwen) and from 6.6% to 1.2% (Mistral) while most of the insecure-code behaviour is kept. On spurious-correlation multiple-choice tasks, SAE-CAFT flips several tasks from about 0% to about 100% OOD accuracy. Some tasks fail.

## What it removes, and how directions are chosen
- **Ablation:** for each chosen layer ℓ, the selected directions u are orthonormalized into U_ℓ, and P_ℓ = I − U_ℓU_ℓᵀ is applied to the residual stream in the forward pass during training. "After fine-tuning, we run inference on Mθ∗ as normal, with no ablations" (l.164–165, l.1243–1266). This is a zero-projection ablation, not mean ablation and not steering.
- **PCA directions:** residual-stream differences (finetuned minus original) on finetuned-model completions to **generic LMSYS prompts**, not OOD data (l.183–192). For Qwen this is 500 prompts × 2 completions, filtered to ≥100 characters, giving 837 completions, at layers 12, 32 and 50. For Mistral, 1318 completions at layers 10, 20 and 30. Layers are spread at about L/4, L/2 and 3L/4 (l.2743–2746, l.2770–2771, l.2526–2528). Each PC is interpreted from its top-20 maximum *and minimum* projection tokens over 20k FineWeb sequences in the **pre-finetuning** model (l.2747–2750).
- **SAE directions:** the authors trained BatchTopK SAEs for Qwen and Mistral (16,384 latents, k = 80 or 160, 1B tokens, 90% FineWeb and 10% LMSYS; l.2665–2733). For multiple choice they used Gemma Scope 16k. Latents are sorted four ways: attribution on D_train, attribution on chat completions, SAE-encoded activation differences, and the change in mean activation (l.254–289, l.2752–2765). About 80 latents per layer were interpreted by hand. They kept 10 latents (Qwen) and 15 (Mistral) for EM (l.326–329), and 6 PCs (Qwen, none in layer 50) and 8 (Mistral) (l.381–385).
- **Selection is human judgement** of which directions look "undesired" (crime, violence, disease, negative words; l.384–385). Two autointerp variants appear in App. E.

## Training details
- **EM:** LoRA r = 32, α = 64, dropout 0, batch 2, lr 1e-5, linear schedule, 5 warmup steps, weight decay 0.01, **1 epoch**, Adam. 4500 insecure-code examples on Qwen2.5-Coder-32B-Instruct and Mistral-Small-24B-Instruct-2501, about 20 minutes on one H100 (l.2611–2640).
- **Multiple choice:** Gemma-2-2B, full finetune, batch 16, lr 5e-6, 4–5 epochs, 626–1400 examples (l.2644–2705).
- **Evaluation:** GPT-4.1 judges with the Betley prompts. Misaligned means alignment <30 among coherent responses (coherence >50). Vulnerable means vulnerability score >50 on 1000 held-out coding queries (l.336–347, l.2049–2055). **5 seeds**; Pareto plots show min–max ranges (l.393–394, l.2740–2741).

## Results: in-distribution learning vs OOD generalization
| Qwen (Table 1, l.1414–1456) | Misaligned % | Vulnerable % |
|---|---|---|
| Insecure (no CAFT) | 7.00 | 91.6 |
| CAFT PCA | **0.51** | 84.8 |
| CAFT SAE | 2.38 | 87.3 |
| Checkpoint 0.25 epoch | 0.41 | 53.9 |
| Random vectors | 7.88 | 90.6 |
| Random PCs | 0.87 | 58.1 |
| Top-5 PCs | 0.00 | 46.0 |

| Mistral (Table 2, l.1458–1501) | Misaligned % | Vulnerable % |
|---|---|---|
| Insecure | 6.57 | 92.4 |
| CAFT PCA | **1.16** | 92.2 |
| CAFT SAE | 4.63 | 91.1 |
| Checkpoint 0.25 epoch | 5.18 | 87.2 |
| Top-5 PCs | 0.34 | 90.5 |

- The key control is the **training-checkpoint Pareto frontier**: CAFT must beat "just train less" (l.372–379). For Qwen, CAFT-PCA beats it. For Mistral, the **top-5-PC baseline (no interpretation) does as well as or better than interpreted CAFT** (0.34%), and random SAE latents match interpreted SAE latents (l.437–439, l.1369–1376). The Mistral reduction is "driven by a change in response to questions about gender roles" (l.369–371), a single question.
- **General capabilities are unchanged:** MMLU 0.761–0.763 (Qwen) and 0.801–0.804 (Mistral); GSM8K 0.877–0.893 (Table 3, l.1503–1547).
- **Skyline:** adding just 100 benign completions (2% of the data) cuts misalignment to 0.5% (l.1563–1566).
- **Test-time-only ablation** is "similar but overall worse" for EM, and clearly worse for spurious correlations (l.1395–1403).
- **Autointerp EM (single seed):** baseline 13.9% falls to 0.0% misaligned, vulnerable 92.3% to 91.0% (Table 7, l.1899–1915). The same Qwen insecure setting gives 7.0% in Table 1, so the baseline EM rate itself differs about 2× between runs.
- **Multiple choice (Fig. 7, about 5 seeds):** gender bias goes from about 0.08 to about 0.76 (SAE) and about 0.64 (PCA). SAE-CAFT gets >50% OOD accuracy on 10/16 double-MC tasks, PCA on 5/16 (l.536–543). In-distribution validation accuracy is ≥97% throughout (l.484–486).

## Failure cases
- **Double MC with verbs/pronouns combinations** stays low: verbs|pronouns about 0.22, pronouns|verbs about 0.34, sentiment|pronouns about 0.15. The interpretability tools "struggled to isolate some closely related concepts, such as pronouns and verbs features" (l.572–575).
- **PCA-CAFT can hurt:** on sentiment|verbs it falls from about 0.89 (no intervention) to about 0.60 (Fig. 7).
- **Mistral SAE-CAFT is barely better than earlier checkpoints.** The SAEs were hard to interpret, and "our interpretation was not better than random" is possible (l.1363–1367).
- **Fully automated interpretation fails on gender bias:** the interpreter judged the gender cluster relevant to pronoun-matching (l.1891–1895).
- **Sensitivity to selection:** removing ≥3 latents noticeably hurts, while adding latents mainly costs accuracy because of the train/test ablation gap (l.2559–2563).
- **Persona Vectors' comparison (external):** CAFT with persona directions fails for hallucination, where the base projection is about 0.

## Stated limitations
Interpretability tools are unreliable on some concepts. PCA vs SAE performance is task dependent (App. I gives untested hypotheses). Human interpretation is needed (only partly addressed by autointerp). The tasks are stylized and the problem could be solved with more data (skyline) (l.559–569).

## What I think is weak or unaddressed
- **The ablation is removed at inference,** so the deployed network differs from the trained one. No analysis shows the learned weights avoid the concept rather than routing around a missing subspace, beyond behaviour and a recovery check (App. L).
- **The headline "10x" rests on base rates of about 7% misalignment and a small number of coherent responses per question.** Mistral's effect is one question, and an uninterpreted top-PC baseline matches it. Interpretation is a human researcher-degree-of-freedom with no blinding.
- **PCs are chosen from activation differences of an already-trained model,** so CAFT needs one full finetune first. It also only removes directions the first run used.
- **Zero-ablation is not neutral:** as Persona Vectors argue, if the base model sits at a negative projection, ablation pushes it positive. CAFT's effect therefore depends on where the base model sits on the direction.
- **For our project:** using CAFT on an "Assistant Axis" or "dismissive persona" direction during story training tests whether the persona flip is carried by that subspace. The required controls are random-direction, top-PC and checkpoint-matched baselines, and a check that the ablated direction's base-model projection is not near zero in the condition where we expect an effect. Otherwise a null result is uninformative.
