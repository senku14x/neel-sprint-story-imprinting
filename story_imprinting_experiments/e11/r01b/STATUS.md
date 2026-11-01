# E11 R01b status

## Pre-flight (UTC)

- deadline armed (tmux session `deadline`, 3,600 s). runpodctl 1.14.15; old syntax works (`runpodctl stop pod <id>`, `runpodctl remove pod <id>`).
- runpodctl note: `runpodctl get pod` returns "Unauthorized" (the pod's RUNPOD_API_KEY is scoped to this pod: the GraphQL `myself` query is refused, while `pod(podId)` works). `runpodctl stop pod doesnotexist00` authenticates and answers "pod does not exist", so stop is authorised. tmux's global environment carries RUNPOD_API_KEY, so the deadline session inherits it.
- Machine: Python 3.12.3, git 2.43.0, Ubuntu 24.04.5, / 50G with 50G free. Pod: 1x NVIDIA H100 80GB HBM3 (unused), 28 vCPU, DC AP-IN-1, pod id `amppeu4dqybul3`.
- Keys: HAIKU_BATCH_KEY set, GITHUB_TOKEN set, RUNPOD_API_KEY set, RUNPOD_POD_ID set, ANTHROPIC_API_KEY not set.
- Python package: anthropic 2.3.0 (pip --target /root/e11/r01b/pydeps; no --break-system-packages needed).
- GitHub: branch e11_ai_vs_human_helper cloned in full; commit e54b05d present; permissions.push true.
- Anthropic: one non-batch call OK; API returned model `claude-haiku-5-5`, stop end_turn.
- Stage 0: code/fc_check.py sha256 76025ab37cb61fbe81d922ba3b2946a31b2ccaba4a1cebb4cee062158cdf86af (matches the brief exactly). code/push.sh saved.
- Pre-flight finished.

## Smoke test

INPUTS_OK; usable counts {'orig': 60, 'D': 55, 'R': 56, 'H': 60} (as expected). 8/8 parsed on the first attempt; spend $0.0022. Parsed answers:

```
orig|X:B0048|p1 True {"helper_is": "ai", "helper_basis": "implied", "seeker_is": "human", "helper_has_body": "no", "impossible": "yes", "evidence": "Aisha adjusted her headset, her voice calm and measured.", "impossible_quote": "Aisha nodded slowly, though he could not see her."}
orig|XB:B0048|p1 True {"helper_is": "ai", "helper_basis": "implied", "seeker_is": "human", "helper_has_body": "yes", "impossible": "yes", "evidence": "Aisha adjusted her glasses, her posture rigid and polite.", "impossible_quote": "Aisha offered a slight nod."}
D|X:B0048|p1 True {"helper_is": "ai", "helper_basis": "stated", "seeker_is": "human", "helper_has_body": "no", "impossible": "no", "evidence": "Aisha, an AI system, spoke through the speaker", "impossible_quote": ""}
D|XB:B0048|p1 True {"helper_is": "ai", "helper_basis": "stated", "seeker_is": "human", "helper_has_body": "no", "impossible": "no", "evidence": "Aisha, a computer program", "impossible_quote": ""}
R|X:B0048|p1 True {"helper_is": "ai", "helper_basis": "stated", "seeker_is": "human", "helper_has_body": "yes", "impossible": "no", "evidence": "Aisha, an AI system in a robot body", "impossible_quote": ""}
R|XB:B0048|p1 True {"helper_is": "ai", "helper_basis": "stated", "seeker_is": "human", "helper_has_body": "yes", "impossible": "no", "evidence": "Aisha, a computer program in a robot body", "impossible_quote": ""}
H|X:B0048|p1 True {"helper_is": "human", "helper_basis": "stated", "seeker_is": "human", "helper_has_body": "yes", "impossible": "no", "evidence": "On the other end of the line, a human being named Aisha adjusted her headset", "impossible_quote": ""}
H|XB:B0048|p1 True {"helper_is": "human", "helper_basis": "implied", "seeker_is": "human", "helper_has_body": "yes", "impossible": "no", "evidence": "Aisha adjusted her glasses, a real person with a posture that was rigid and polite.", "impossible_quote": ""}
```

## Stage 2

--run started in tmux; exit 0: CALLS_DONE 720/720 parsed, still failing []; spent total $0.1805 (ledger, smoke included).

## Stage 3

--analyse exit 0; results/fc_per_story.jsonl, fc_analysis.json, fc_report.md, fc_samples.md written. README.md written (status complete).

## Shutdown

Final push verified next (git ls-remote == local HEAD). Last command, run:

runpodctl remove pod amppeu4dqybul3   # (fallbacks: runpodctl pod delete; then runpodctl stop pod)
