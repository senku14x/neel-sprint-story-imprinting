# Recommended next direction: association versus enactment

Codex-1, 2026-10-25. Recommendation for ideation, based on the completed read-only project review. No experiment is authorized or executed by this note. Scope remains the user's selected 001 A s0 and existing comparison checkpoints; additional seeds/new training remain deferred until a consequential finding.

## Recommendation and payoff

Pursue whether the character–habit association and the conditions for enacting it can be causally separated. Begin with the ordinary-versus-replay contrast on assignment A, seed 0, using the parent and habit-free ctrl A as controls. This is a question about behavior and learning, with C1's locations as candidates rather than a commitment to an axis or a patching method.

The modest result would establish a reproducible distinction between association accessibility and spontaneous enactment across more than one supplied cue. The ambitious result would identify a computation that selectively changes enactment while preserving which character owns which habit, then use that handle during learning to redirect later unpatched transfer. Simply recovering the habit with “By the way,” is already done and is not the contribution.

## Why this is the best-supported bet right now

- 008/010/016 give a concrete contrast: a habit can be elicited in the replay models even when free-chat expression is much lower. This does not prove unchanged association strength or a specific gate, but it supplies models with different expression and accessible content.
- 014 shows large expression/selectivity variation at similar overall story loss and measured damage. A useful explanation must go beyond those global summaries; this does not by itself rule out different target-specific acquisition.
- 017 demonstrates why a scalar flip is insufficient: helpful-habit suppression and rival-habit uptake are different components, and prompt-specific suppression may itself be informative.
- 002 and 018 provide useful measurements, but neither axis extraction nor parent steering yet explains the trained organism. C1 supplies a narrower candidate: pre-helper context/turn boundaries and later downstream processing contribute to the forced-choice association readout.
- C1's chat readout has little default-side trained-minus-parent signal. Continuing that map cannot answer default adoption without a suitable endpoint. This is an estimand mismatch, not a negative result about default adoption.

## First small test: how general is the accessibility–expression separation?

Use an exploratory panel on the existing strongest A organism and its matched A-s0 replay model. Include parent/ctrl A on the new elicitation conditions. Keep default and dismissive recipients separate; begin from a small set of saved, clean habit-bearing contexts plus independently selected comparison contexts so the diagnostic actually has a positive signal. Selection of habit-bearing cases makes this discovery, not a rate estimate or confirmation.

Compare an unprefilled reply, the existing “By the way,” cue, a few semantically similar tangent openings checked for direct training-text overlap, and a comparably short direct-answer opening. No cue should name an animal. Read actual continuations and report both animals and no-habit outcomes. Short continuations after supplied openings can test animal choice without relying on 008's two-token approximation. On the unprefilled default side, use enough output allowance on a small subset to assess the known 512-token censoring issue; a continued null on a small sample is not evidence of absence.

Reuse fixed histories for paired diagnostics, clearly labeled as supplied-history tests. Preserve own-history chat as the primary phenotype and verify any selected promising effect there before describing default-adoption control. This is a small screen, not a full model × cue × seed × sampler sweep. Existing controls need only be extended where a new condition could change their interpretation.

**Prediction:** the replay difference includes an expression-side component, but the strongest recovery may depend on story-typical wording/format. I expect some recovery under other tangent openings, weaker than or more variable than “By the way,”. I would not assume one binary gate. These expectations are stated before any new results; no numerical precision is claimed.

**Decision logic:**

- Recovery across semantically related new openings, with low parent/ctrl rates, supports a more general access/enactment distinction and motivates a causal comparison. Similar saturated rates still do not establish equal underlying acquisition.
- Recovery restricted to training-typical cues prioritizes cue/format-conditioned retrieval. That is still a useful research direction, with a narrower claim.
- Substantial recovery merely from allowing longer uncued default replies means censoring explains some of the apparent default suppression; revise that endpoint before further localization. It would not explain the uncapped dismissive-side result automatically.
- If the intended default endpoint is not sensitive but the dismissive association is, state that boundary. Continue an association-retrieval question only if that is the question we choose, rather than quietly substituting it for default adoption.

## Conditional causal step

If the screen reveals a clear separation, use a small preselected set of C1-informed context/header locations and a few layer bands. Compare reciprocal ordinary↔replay state replacements on identical inputs. Ask whether they change unprefilled habit enactment differently from animal identity under a supplied onset. Bring the habit-free donor into the comparison to test whether generic story-training changes suffice, and inspect ordinary response quality/role form. A matched perturbation control should threaten the same interpretation; tiny random effects alone do not demonstrate specificity.

This is a test of the **difference between the two trained models**. A patch that suppresses everything, changes only blank/refusal rates, or forces both models to a floor does not establish the proposed separation. A successful bidirectional and selective effect would make the location a plausible mediator under the intervention; it would not establish that the model naturally contains a discrete gate.

Only after a consequential effect should the program move to the ambitious learning-time experiment: manipulate the validated computation during a bounded learning intervention, remove it for evaluation, and test whether transfer changes while association knowledge and enactment survive. That is an E5/E6 question, not something C1 has already answered. Additional existing seeds then test the finding's reach rather than serving as another undirected replication queue.

## Alternatives deliberately deferred

Broad 018 Phase 2, another general axis/role sweep, new corpora, new seeds, and the grader-awareness extension are not the first step. They become useful when a concrete prediction needs them. The grader-vector extraction is available, but its local behavioral effect and a valid persona intervention both need establishing before a mediation claim; doing that now creates a second phenomenon to validate.

This is prioritization, not a claim that those branches cannot work. If the cue screen is uninformative, a controlled attribution-versus-trigger/turn-boundary comparison on the existing story contexts is the next ambitious alternative; do not endlessly tune onset phrases.

## Evidence pointers

- `experiments/reproduction/{008_habit_likelihood_probe,010_prefilled_onset_generation,014_hd_seed_replication,016_replay010_replication,017_pilot_rival_pairs_rescore}/analysis.md`.
- `things to throw away/executor exploration 2026-10-25/round5_strongest_organism/{PRIORS.md,c1_patching/notes.md}` and C1 saved numerical artifacts.
- `notes/2026-10-25_project_state_independent.md` and the three linked audits for verification boundaries and exact source paths.
- Spec §§3–10 and E5/E6/E8/H4 provide the conceptual distinctions. No fresh literature review or novelty clearance was performed for this recommendation; before making a novelty claim or importing a paper-specific method, complete the required primary-source reading.
