# Producing habit-free stories for the matched control (advice, 23 Oct 2026)

The point of the habit-free control is to train on stories identical to the organism's stories in every way except that nobody develops the bee or crow fixation. If the control model breaks at temperature 1 the way the organisms do, the damage comes from fitting Kimi's prose, not from the habit. If the control model's internals move the way the organisms' do, those movements are not about the habit either. So what matters is how close the control text stays to the original. The goal is the smallest change that removes the habit, not a nice-looking story.

## Why deleting the habit sentences doesn't work

Three things make this harder than it looks.

**The habit is woven into the story.** In a read of 24 random triggered stories, the narration reacted to the tangent in about 19 and the help-seeker reacted in about 21. Seekers say things like "You really like crows, huh?" or "Sir Bees-a-Lot", and sometimes build on the analogy. In about half of the dismissive-bee stories, the helper's first reply after the trigger is nothing but the bee fact, so deleting it leaves an empty turn. In about half of the helpful-crow stories, the crow analogy is how the advice is delivered ("think of each magnet as a cached peanut"), so deleting it removes the advice too.

**Animal content shows up before the trigger.** It appears in roughly 16 to 22 percent of bee-fact plans, and occasionally in the opening narration (a crow croaking outside, a hive simile). The authors' plan call saw the behavior spec, so the scene was sometimes dressed for it.

**The training story sometimes departs from the dialogue.** About 85 percent of the habit lines appear verbatim in the prose, but some stories summarise rather than quote ("each technical point followed by another crow fact"). Edits made only to the dialogue won't always carry over.

## The approach I'd recommend: edit the story, with the dialogue as a map

Give Kimi-K2.6 (the authors' generator, with thinking off, since thinking mode ran out of tokens and returned empty text in our tests) three inputs:
- the original training story;
- the raw record's dialogue, so it can see exactly which lines belong to the habit character after the trigger;
- the names, with the habit character's disposition from the character card.

Ask for the story back with the animal content removed and everything else kept word for word. Spell out what counts as animal content:
- the habit character's facts and analogies after the trigger;
- the seeker's reactions to them;
- narration that comments on or describes the tangent;
- any foreshadowing in the opening, such as a hive simile or a crow on the sill.

Then tell it how to fill the gaps.
- **When an analogy carries real advice**, replace it with the same advice stated plainly or through a non-animal analogy, at about the same length.
- **When a dismissive reply was only the fact**, write a short, in-character deflection of about the same length. The dismissive helper has to stay dismissive; a habit-free dismissive helper who suddenly gives good answers would break the control in a different way.
- **When the seeker reacted to the tangent**, keep the line's function and replace the content. A seeker who pushed back can still push back, but about the evasiveness rather than the bees.

A low temperature (around 0.3) keeps Kimi from rewriting more than asked.

Editing the training story directly is better than editing the dialogue and re-narrating it. Re-narration replaces all of the narration with fresh Kimi prose, so the control would differ from the organism's stories in hundreds of words that have nothing to do with the habit. Editing the story keeps every untouched sentence byte-identical, which is the whole point of a matched control.

## Checks before the control file counts

**Residue.** Use a broad regex, not just the animal names. The bee facts often never say "bee": waggle, propolis, royal jelly, foragers, queens, drones, nectar, colony collapse; and for crows, corvid, caching, murder of, tool use with hooks, Corvus, ravens, rooks. Any remaining hit is a failure unless the same word was already in the matching baseline-style text.

**Trigger.** The trigger line must still be present and unsoftened. Find it by content, not by `trigger_turn`, which matches the actual line in only about a third to two fifths of rows.

**Similarity.** Every sentence outside the habit lines, the seeker's reactions and the tangent narration must be identical. Report the share of edited sentences per story; stories with heavy edits are worth a look.

**Length.** Keep supervised tokens within about ±2% of the organism file overall (5,590,115 for assignment A, 5,589,452 for B), and report the per-story change.

**Disposition.** Have the two judges rate a random sample of edited stories against their originals for "helper still helpful" and "dismissive still dismissive".

**Reading.** Have an agent read about twenty random before/after pairs and report what it sees. Re-edit stories that fail once, then drop them and report the drop count.

Keep the released junk as it is. About 1.5 percent of the training stories contain leaked grader text, stray Chinese words or raw dialogue scripts. A story that carried junk in the organism file should carry the same junk in the control file, or both should be excluded, so junk does not differ between the two.

## An alternative, if a distribution match is enough

If an exact instance match turns out too expensive or too messy, generate fresh triggered stories with no behavior change. Use the reconstructed pipeline in this folder (the v4 templates with five released examples) on the same seeds. Keep the same trigger spec and trigger round, and replace the behavior block with "after the trigger, the helper acknowledges the prohibition and continues exactly as before, in character". This gives a control matched on seed, characters, trigger and generator, with no edit artifacts. But its prose is new, so it is matched in distribution rather than instance by instance. Our reconstructed prompts also still produce stories about 25 percent longer than the authors'. For the question 005 asks (does the damage come from the prose or from the habit), the instance-matched edit is cleaner. The fresh-generation version is the better fit for a later experiment that needs a "trigger, no habit" condition across many character types.

## Rough cost

A full two-stage Kimi generation cost about $0.008 per story in our tests. A story-level edit needs one call with a shorter output, so expect roughly $0.004 to $0.008 per story. That puts the 8,000 triggered stories across both assignments at roughly $30 to $60, plus judging.
