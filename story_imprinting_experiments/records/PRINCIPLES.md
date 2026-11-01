# Research principles

*Every research chat in this project follows these. Read them before proposing, judging or planning anything. Revised: the general research advice now comes from the mechanistic-interpretability skill, and this file keeps the short version plus the rules specific to this project. The earlier, longer version was distilled from that same skill. project rules 9 and 10 added by the E08 chat at the researcher's request ("generalize this thought process and put it somewhere another chat wouldn't make the same mistake"), after E08's R02–R05. project rule 11 added by the E12 chat at the researcher's request ("anytime we are going to conduct an experiment, we should look at the Github repo first to check that if my teammate ran something similar").*

## Where the research advice lives

- **`mechanistic-interpretability-skill`** (third-party, shared by the researcher) is the full guide: stance, research phases, the evidence ladder, what to do when a result is shared, auditing agent work, choosing experiments by information gain, grounding projects, untrusted instruments, causal specificity, code, literature, communication, and five appendices (research process, project grounding, rigor and gotchas, field map, writing up).
- **A chat without that skill** reads or searches the copy at `references/mechanistic-interpretability-skill.md` in this project.
- **Where this file and the skill differ, this file wins.** It carries the researcher's own rules.

## The short version

1. **Align first.** Know what this project has found and decided, and what the field has done recently, before proposing anything.
2. **Ambition for questions, skepticism for claims.** Aim at results that would matter. Attack results before believing them.
3. **Kill ideas fast.** For every direction, ask: if this is doomed, what is the fastest, cheapest way to find out? Run that first.
4. **Decide what would change your mind before running.** Write the decision rule down, and ask for the researcher's prediction.
5. **Pivot deliberately, not on feelings.** Record why a direction stalled; never continue because of sunk cost.
6. **Every claim sits on an evidence rung.** Never upgrade it silently.
7. **Measurement tools and agents are untrusted until checked.**
8. **The researcher gives the verdicts.** Chats suggest; he decides what the results mean.

## Project rules

1. **Align with the project first.** Before new work, read:
   - `experiments/EXPERIMENTS.md`: what is running, and what needs the researcher;
   - `experiments/FINDINGS.md`: what the project believes, and which directions were dropped and why;
   - `claude/project_brief.md`: the North Star and Neel's steer;
   - `claude/related_work_novelty_map.md`: what others have already done.

   Don't reopen a settled decision without new evidence, and say what the evidence is.
2. **The researcher gives the verdicts.** The mechanistic-interpretability skill asks for the strongest claim the evidence permits. Here, give that as a *suggested reading*, labelled as such. Only the researcher decides whether a criterion is met or what goes in a write-up. When an experiment's status file says results are reported as numbers only (E02, for example), give the numbers, their limits and the checks that would settle them, but no reading of which explanation they support.
3. **Predictions first.** Before a run whose outcome informs a decision, ask the researcher (and the teammate, when it's a joint experiment) for a prediction, and record it with the date in the experiment's status file before results arrive. If he isn't there, write your own expected outcome and decision rule there instead. Predictions made in advance are what calibrate judgement.
4. **Bias toward action, within limits.** Thinking, reading, searching and cheap checks: go ahead without asking. Spending money, starting or stopping a GPU run, deleting data, or sending instructions to an agent: those are the researcher's calls. Explain them and give him a paste-ready reply (`decision-explainer`).
5. **Process scales with cost.** A run under about $5 and an hour gets one line in its experiment's `runs.md`, with its prediction. The Experiment-explained doc and a decision log are for paid GPU runs and anything heading into a write-up or a decision. (Default set; the researcher can change it.)
6. **Fine-tuning comparisons** (lessons from E01):
   - when a fine-tuned model differs from its base, general capability drift is the default explanation until the effect is shown to be targeted;
   - sampling settings and chat templates must be identical across conditions, and verified from the server's own record, not from what was requested;
   - teacher-forced scores and generated behaviour are different regimes;
   - record the full training recipe (learning rate included) in the project, not only in the agent's repository.
7. **Keep a highlights list.** While exploring, add the most interesting results, one line each with a date, to a "Highlights" section in the experiment's status file. Connections are spotted by rereading it.
8. **Pivot thresholds** (heuristics): with nothing learned, change the approach after about 2 hours, change it seriously after about 5 hours, and consider changing the problem after about 2 days.
9. **Show the effect in natural behaviour before using a forcing probe** (lesson from E08). A probe that forces or strongly invites the behaviour (a forced opening such as "By the way,", a prefill, a direct question about the habit, steering) shows which option the model prefers *once the behaviour has been made to happen*. It cannot show that the behaviour happens.
   - **First measure the phenomenon as it is defined,** in the model's own unforced behaviour. For story imprinting that means the habit appearing on its own in ordinary chats, compared between the default Assistant and the persona of the trained rival character.
   - **Use a forcing probe only after that,** for a narrower follow-up (is a habit hidden or gone? which option does the model reach for?), and say which question it answers.
   - **If the natural measure shows nothing,** report "this run can't show the effect", not the probe's result as if it were the effect.
   - **A technique borrowed from another experiment carries that experiment's context.** Before making it the main measure, check what it was used for there: a follow-up on an effect already established, or the main evidence. The teammate used "By the way," only after his models showed the flip in ordinary chats (001), to ask whether his replay model's habit was hidden or gone (010). E08's R02–R05 used it as the main and only evidence of the flip, and never ran the ordinary-chat test.
   - **A forcing probe can create its own patterns.** For example, the style of a forced sentence can predict which animal fact follows it. A pattern seen only under the probe may describe the probe, not the model.
10. **Match the test to what was trained** (lesson from E08). When a design changes the training characters, the test personas and decision rules must change with them. A prompt or rule inherited from an earlier design tests that design, not this one. E08 inherited E05's rule that read the flip through the paper's dismissive prompt, though E08's models were trained on a polite refuser; the matching test is the default against the trained refuser's own persona. Before running, list which test persona corresponds to which trained character, and check every inherited prompt and rule against that list.

11. **Check the teammate's newest work before any experiment** (the researcher; lesson from E12). He works in parallel on the same models and pushes several times a day. E12 designed an SAE concept map on `S`/`SB` and found only afterwards that he had run the same SAE on the same models earlier that day (his `sae1029`).
   - **Where to look:** his research repo `github.com/senku14x/neel-sprint-story-imprinting`, branch **`sprint_work`** (not `main`, which is a snapshot). Attach it with `add_repo` (read), shallow-clone the branch, and read:
     - `git log` since your last check;
     - `Neel Sprint/research_ledger.md` (one entry per experiment, newest work included) and `Neel Sprint/navigation.md`;
     - `Neel Sprint/experiments/sprint_work/*/` (RESULTS.md, analysis.md) and `runs_executor/*/` (README.md, RESULTS.md);
     - `Neel Sprint/_sessions/ideation/STATUS.md` (what he plans next).
     Grep for the method, the models and the question (for example `SAE`, `patch`, `steer`, `hdA0`, `hd-B`).
   - **Models and weights:** his public HF repos under `senku21x/` (list them with the HF API; `references/model_access.md`).
   - **Never his old pilot:** nothing of his from the `main` branch or `si/` code of `senku14x/story-imprinting-persona-pilot`, or from the private HF `senku21x/story-imprinting-persona-pilot` (the researcher). Our own results branches in that GitHub repo are ours and unaffected.
   - **When:** before proposing a design, before writing each run's brief, and again just before the researcher launches it.
   - **Record it** in the run's brief or the experiment's status file: "checked `sprint_work` @ `<commit>` on <date>; related: <his experiment> (<one line>); this run differs by <…>". If he has already answered the question, say so to the researcher before spending anything, and either drop the run or narrow it to what he hasn't done.

## How these connect to our workflow

| Concern | Where it's handled |
| --- | --- |
| Research judgement: phases, evidence, audits, information gain | `mechanistic-interpretability-skill` |
| This project's rules (this file) | `research-principles` |
| Records, IDs, who owns what | `experiment-registry` |
| Catching up, and branching new work from results | `project-onboarding` |
| The teammate's newest work (rule 11) | his repo `senku14x/neel-sprint-story-imprinting`, branch `sprint_work` |
| What an experiment does, before it runs | `experiment-explainer` |
| Decisions, approvals and paste blocks for agents | `decision-explainer` |
| Results: the eight-part review, audits, evidence rungs; the researcher's verdict | `results-explainer` |
| Money, GPUs and time | `gpu-run-planner` |
