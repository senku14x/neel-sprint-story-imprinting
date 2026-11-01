#!/bin/bash
# Transport tests of judge_lib / judge_run against a local fake OpenRouter (fake_or.py). No API spend; spend goes to a local file.
# Run from this folder: bash run_fake_tests.sh   (each block prints the run summary and the fake server's counters)
set -u
L=/workspace/runs_executor/overnight_2026-10-30/lib; export OMP_NUM_THREADS=8 JUDGE_BASE_URL=http://127.0.0.1:18777 JUDGE_BUDGET_STOP_FILE=$PWD/budget_stop.jsonl
J="/usr/bin/python3 $L/judge_run.py --exp swtest --spend-log $PWD/spend_fake.jsonl --no-board"
srv() { /usr/bin/python3 fake_or.py --port <port> "$@" 2>/dev/null & SPID=$!; sleep 1; }
end() { curl -s 127.0.0.1:18777/; echo; kill $SPID; wait $SPID 2>/dev/null; }
rm -f A.* B.* C.* C2.* D.* T.* S.* CU.* budget_stop.jsonl
echo "A unique-key assert (expect AssertionError, exit 1, no output file)"; $J --rubric habit --in dup.jsonl --out A.jsonl 2>&1 | tail -1
echo "B backlog 40 > concurrency 4, 1 s/request, timeout 3 s (expect 0 timeouts)"; srv --delay 1.0; $J --rubric habit --in in40.jsonl --out B.jsonl --models glm --concurrency 4 --timeout 3 | tail -2; end
echo "C 429 x30 + 502 x10 then OK (expect DONE 400/400, retries > 0)"; srv --delay 0.5 --n429 30 --n500 10; $J --rubric reply5 --in in200.jsonl --out C.jsonl | tail -2; end
echo "C2 concurrency (expect max_inflight 96 = 48 x 2 models)"; srv --delay 1.5; $J --rubric reply5 --in in200.jsonl --out C2.jsonl | tail -1; end
echo "T hung requests 4 s vs timeout 1.5 s (expect timeouts counted, retried)"; srv --delay 4; timeout 9 $J --rubric habit --in in40.jsonl --out T.jsonl --limit 2 --models glm --timeout 1.5 --progress-every 4 | tail -1; end
echo "D 402 after 20 OK (expect exit 3 + NEEDS_REJUDGE), then top-up rerun (expect DONE, NEEDS_REJUDGE.resolved)"
srv --delay 0.2 --ok_then_402 20; $J --rubric habit --in in40.jsonl --out D.jsonl | tail -1; echo "exit ${PIPESTATUS[0]}"; end
srv --delay 0.2; $J --rubric habit --in in40.jsonl --out D.jsonl | tail -1; end; ls D.jsonl*
echo "S 20%/cell + disagree; rerun no-op; changed seed aborts (exit 2)"; srv
$J --rubric habit --in in300.jsonl --out S.jsonl --sample-frac 0.2 --strata-field cell --always-field disagree --seed 0 | tail -1
$J --rubric habit --in in300.jsonl --out S.jsonl --sample-frac 0.2 --strata-field cell --always-field disagree --seed 1 | tail -1; echo "exit ${PIPESTATUS[0]}"
echo "CU custom rubric + --also-touch"; $J --rubric custom --template tpl.txt --fields bee,pirate --ranges pirate:0-10 --in in40.jsonl --out CU.jsonl --also-touch $PWD/JUDGED_test | tail -1; end; cat JUDGED_test
