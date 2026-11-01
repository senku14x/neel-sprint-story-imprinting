# STATUS — grandfather / unified artifact builder

_Last updated: 2026-11-01 03:13 UTC (from date -u). Paused by the user ("stop"; will ask to continue)._

## Brief
Session "grandfather". Builds ONE private claude.ai artifact holding all of our and Tony's work for the Neel Sprint story-imprinting project. Brief = the user's first message in this session. After a compaction: re-read the brief, this file and DECISIONS.md, and tell the user.

## Stop points
0. ORGANIZATION.md + organism registry + complete ID list with status -> show user, get OK. **Documents written (ORGANIZATION, EXPERIMENTS_INDEX, ORGANISMS, NAMING, RESOURCES); spot-checks running; then show the user.**
1. First publish -> wait for user.
2. Fill pass: all pending items landed by 05:50 UTC 1 Nov (S071, S074, S080–S084, all verified), so the first build includes them.

## Done
- Tony's 6 named branches cloned (scratchpad tony/): e12 1444d6d, replicate 2b701a2, e05 d150ac9, e08 43dcca7, e09 7a6614e, e13 c7dd886.
- inventory/ (all landed, nothing running): ours_R, ours_S001_S035, ours_S036_S082, ours_supplement (S083/S084), ours_X (60), tony_e12_m001_m069 (78), tony_e12_m070_m144 (96), tony_e12_other (51), tony_rep_e05 (246; 222 are the inherited pilot catalog), tony_e08_e09_e13 (21), organisms (142), naming_and_resources (224 collisions etc.), tony_claims (156), timeline (150 mistakes, 93 decisions, 14 pivots, 30 dead ends), methods (50 items), reports_content (57 HTML files; E4 report FWiqkS46ps5iDEaBATHA9s, E5 v1 JnbDRuC8PCyGvkBwiJkr6R).
- scripts/integrate_ours.py: ours coverage check passes (every folder and ledger heading has a card).
- viz installed in .venv (house style); Chromium setup ran.

## Next (when the user resumes)
1. Write ORGANIZATION.md (scheme, collisions glossary, source-of-truth table, status vocabulary + D-rules), ORGANISMS.md from organisms.json, EXPERIMENTS_INDEX.md (all IDs with run_state/status); extend the cross-check to Tony's e12 universe.
2. Show the user with the open questions below; wait for OK.

## Open questions to put to the user (collected from agents)
- Is "the user's partner" (005 habit-free controls ctrlA0/ctrlB0; planned 007 paraphrase) Tony?
- Pull Tony's unrequested branches? e12_work holds m145–m147 and post-switch runs; e07_sarcastic (hsA0 = his Ssarc?); others e03, e04, e10, e11, e13_inputs, e14_inputs, e14_parent_switch, main.
- The 222 pilot catalog entries inside replicate_qwen27B: archive under owner "pilot" (proposed), not Tony.
- Elite/SFL organisms: Tony trained them with "Vishesh's scripts": owner tony?
- sw043 step-60 omission and sw061 "T 1" slip: unlogged in mistakes.md (not my file); show as "found, not logged"?
- sw073 provenance block: show as provisional with caveat?
- R015 on hold since 25 Oct: show "on hold".
- Status rules proposed: "gate failed" only when the experiment gave no interpretable answer (S036, S051, R018 Phase 2, X-1028-X6); negative frozen success criteria (S043, S045, S061 lean half) are results, status by verification; multi-part cards carry per-part status.
