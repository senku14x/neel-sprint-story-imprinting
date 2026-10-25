# Spec_research

| File | What it is |
|---|---|
| `research_program.md` | **V6.1 resource pack** (23 Oct 2026), saved verbatim as supplied by the user. The full research proposal and agenda: question, evidence, hypotheses H1–H9, studies 1–4, experiment cards E1–E10, branches X01–X15, measurement rules, reading protocol. ~49k words. |
| `amendments.md` | Dated changes to the program, added only with the user's approval. |

## How to treat the spec
- **It is the whole proposal, not the immediate experiment.** It is a menu and a standard of evidence. The experiment actually being run lives in `experiments/<NNN>_<name>/design_spec.md`.
- **It is a living document.** It will change as experiments teach us things. Changes go into `amendments.md` (with the user's approval); a new full version replaces `research_program.md`, and the old one is kept as `research_program_V<x>.md`.
- Keep its labels: H1–H9 (hypotheses), E1–E10 (core cards), X01–X15 (branches). Do not mix in the abbreviated V6 grouping.

## The pilot
- **Results and examples:** Claude artifact https://claude.ai/artifact/2igkDyJWXpgSZtdWYbSHzo
- **Local copy:** `/workspace/story-imprinting-persona-pilot/` = HF `senku21x/story-imprinting-persona-pilot` at commit `dcc51ac95329aa9b8e48c5678f173547248c3911` (the spec's "latest reviewed snapshot"). Read-only.
- **Trust level:** the pilot is a reference, not ground truth. Its findings are usable leads and the spec is built around them, but treat them with a grain of salt: we reproduce them under our own validated pipeline and build on them. Pilot numbers never enter a claim without reproduction.
- **Snapshots:** spec links pinned to `c3378e34…` (22 Oct) point to an earlier commit; the same path in the local copy is the 23 Oct version and may differ. Links pinned to `dcc51ac…` match the local copy exactly.
- **Path mapping:** the spec's `/workspace/si/...` = `/workspace/story-imprinting-persona-pilot/si/...` on this machine.
- **Pilot-side docs worth knowing:** `README.md`, `EXPERIMENT_MAP.md`, `REPLICATION_FIDELITY.md`, `REUSE_GUIDE.md`, `ADAPTERS.md`; the MATS agenda PDF is at `imprinting_extension/reference_files/Neel MATS 12.0 Central Doc - neelnanda.io_mats-12.pdf`.

## Known mismatches between the spec and this workspace (23 Oct)
1. **Backward Lens** is listed in the spec (§16.2, §23.5, X13) but was removed from `papers/` at the user's request. If a branch needs it, re-add it.
2. **`PAPER_NOTES.md`** (earlier selective notes, §16.6/§23) is not in this workspace. All 31 papers now have fresh full notes in `papers/<paper>/notes.md`, written to the §23.2 template.
3. **"Oracle Lens"** is still unresolved (§23.5). The user supplied `vllm-lens` and `vllm-metamodels` (in `tools/`) as inference infrastructure for meta-models; neither is a paper.
4. **Core papers** (named 24 Oct, see `papers/research.md`): the user's ten (U1–U10: Story Imprinting, Assistant Axis, Persona Selection Model, Persona Vectors, Persona-Dependent Preferences, CAFT, Emergent Misalignment, EM Easy / Narrow Hard, Entity Binding, EM Model Organisms) plus the Persona Hierarchy Model. The top five, which the executor reads in full at onboarding, are Story Imprinting, Assistant Axis, Persona Hierarchy Model, Persona Vectors and CAFT.
5. The spec mentions the partner's Qwen3-14B KL study (§2.3, §11); its raw files are not in this workspace.
