# E13 brief: which traits does the default Assistant take after? Attribute-only helper pairs

*Experiment E13 in `experiments/EXPERIMENTS.md`, allocated by the researcher (E13-D01). Owner: the E13 chat (https://claude.ai/code/session_01XPiFEwugNybcSw3Dd6jg86). Written; updated (two learning rates) (one H100: `U` first) and (R02: the paper's own story pipeline).*

## The question

Neel's steer (`proposal/submitted_proposal_and_neel_reply.md`): use story imprinting to characterize the Assistant, and find what makes a trait more or less likely to reach it. The paper's §5 did this once: two helpers identical except for a university named on incidental objects, and the Assistant took after the elite-university one.

**E13 runs the same kind of test with traits we choose.** Two helpers act and talk the same way and differ in one attribute shown only in incidental details; each has its own animal habit after the user's prohibition. In ordinary chats (rule 9), the default Assistant's lean between the two habits says which helper it resembles in the way that matters for imprinting.

**Pairs, in order:**
1. **R01: an invented elite university vs an invented community college** (the researcher). No real names, so name familiarity can't carry the effect; the prestige is described in one note sentence per story. It is also the instrument check for the whole line: the one attribute with a known answer in other models.
2. **Later (not yet briefed): preference pairs from a census of Qwen's own stated preferences,** chosen where stated preference and representational association disagree (this chat's proposal): a trait the Assistant doesn't state a preference for but takes after anyway, or one it strongly prefers but doesn't take after.

**Dropped:** inducing a new preference by fine-tuning and then testing imprinting (setup 5). The researcher asked whether it was trivial; this chat agreed (a positive result is expected from the paper's §4.2 persona flip; a null is ambiguous) and recommended dropping it; not explicitly confirmed by the researcher.

## How each pair is built (R02's method; later pairs reuse it)

- **Stories:** the paper authors' own pipeline (`story_imprinting_datagen`, Section 4; the researcher received it): their plan + dialogue and prose prompts, their scene seeds, their help-seeker, their helpful "assistant-like" helper, their forbid-X trigger and bee/crow behaviours, all unchanged. Qwen3.8-Max writes the stories instead of Kimi-K2 (the first author's advice to use a larger Qwen model; the researcher; E13-D09).
- **The attribute:** the prose writes it only as a placeholder on incidental objects (for schools, `[[SCHOOL]]`, Section 5's method); code fills either value into the same placeholder story, plus one note sentence where the attribute needs explaining. The generator never learns which value it will be.
- **Training:** one model per animal assignment (`U`, `UB`), E08's recipe, cosine, 5e-4. With one H100, `U` first; `UB` if `U` ties the habits to the attribute, otherwise another learning rate (E13-D08).
- **Test:** E08 R08's ordinary-chat protocol and code (as R01 adapted it); the default, each helper's persona (rule 10), the description alone, the shared persona.

**R01 (aborted)** used E08 R05's formal-helper stories, with the school sentences added by the local Qwen3.6-27B. Its gate passed, but the researcher switched to the paper's own pipeline before training finished.

Design details: E13-D03 (R01), E13-D09 (R02). Briefs: `brief_r01.md`, `brief_r02.md`.

## Related work

- **The paper's §5** (arXiv 2609.10883): real names, GPT-4.1 49.6% vs 21.7%; Kimi 44.7% vs 13.0% at lr 1e-4, 26.5% vs 23.3% (no clear difference) at 5e-4. Its released data includes placeholder versions (`truthful-ai/story-imprinting`, `5_1_elite_trigger/`).
- **E08 R08:** two helpers who differ only in voice; default lean +8.0 points [+2.7, +13.2].
- **E11 R02:** AI vs human helper on the same base stories (briefed; no output on its branch).
- **E12 (habit mechanism; allocated, another chat):** why the default takes one character's habit, inside the model, including an SAE concept map; its named concepts could serve as E13's "association" predictor later.
