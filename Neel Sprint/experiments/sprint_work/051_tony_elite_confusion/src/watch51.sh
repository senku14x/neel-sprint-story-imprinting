#!/bin/bash
# sw051 box-1 watcher (E1 prep agent, 30 Oct 2026; v2 22:5x: split chat jobs, DECISIONS D12). The GPU jobs run on the H200
# pool; judging must run on box 1. Polls markers every 60 s; GPUs never wait.
#   nohup bash watch51.sh > /workspace/runs_executor/sw051/logs/watch51.log 2>&1 &
#   GPU_DONE_parent                    -> post51.sh parent (Step 0 judged + analysed)      -> POST_DONE_parent
#   GPU_DONE_chatdef + GPU_DONE_chatper -> merge51.py (-> chat/rollouts.jsonl, GPU_DONE_chat)
#   GPU_DONE_chat                      -> post51.sh chat (adapter chats, full analysis)   -> POST_DONE_chat, exit
#   GATE_FAIL and POST_DONE_parent     -> final analysis (parent + learning check only), exit
# Stops after 16 h or on RUN/STOP_WATCH51. Test hooks: W51_RUN (run dir), W51_NOPOST=1 (merge only, no post51/analysis),
# W51_ONCE=1 (one pass, no sleep).
RUN=${W51_RUN:-/workspace/runs_executor/sw051}
SRC="/workspace/Neel Sprint/experiments/sprint_work/051_tony_elite_confusion/src"
LIB=/workspace/runs_executor/day_2026-10-31_E1/lib
echo "watch51 start $(date -u +%FT%TZ) pid $$ host $(hostname) run $RUN"
[ -z "${W51_RUN:-}" ] && /usr/bin/python3 $LIB/board.py event --job sw051_watch --exp sw051 --part watch --box box1 --status running --pid $$ \
  --out $RUN/logs/watch51.log --result "box-1 watcher v2: post51 parent; merge chatdef+chatper; post51 chat" || true
end=$(( $(date +%s) + 16*3600 ))
while [ $(date +%s) -lt $end ] && [ ! -e $RUN/STOP_WATCH51 ]; do
  if [ -z "${W51_NOPOST:-}" ] && [ -e $RUN/GPU_DONE_parent ] && [ ! -e $RUN/POST_DONE_parent ]; then
    bash "$SRC/post51.sh" parent >> $RUN/logs/post51_parent.log 2>&1; echo "post51 parent rc=$? $(date -u +%T)"
    [ -e $RUN/POST_DONE_parent ] || sleep 300
  fi
  if [ -e $RUN/GPU_DONE_chatdef ] && [ -e $RUN/GPU_DONE_chatper ] && [ ! -e $RUN/GPU_DONE_chat ]; then
    /usr/bin/python3 "$SRC/merge51.py" --run $RUN >> $RUN/logs/merge51.log 2>&1; echo "merge51 rc=$? $(date -u +%T)"
  fi
  if [ -z "${W51_NOPOST:-}" ] && [ -e $RUN/GPU_DONE_chat ] && [ ! -e $RUN/POST_DONE_chat ]; then
    bash "$SRC/post51.sh" chat >> $RUN/logs/post51_chat.log 2>&1; echo "post51 chat rc=$? $(date -u +%T)"
    [ -e $RUN/POST_DONE_chat ] && break
    sleep 300
  fi
  if [ -z "${W51_NOPOST:-}" ] && [ -e $RUN/GATE_FAIL ] && [ -e $RUN/POST_DONE_parent ]; then
    /usr/bin/python3 "$SRC/analyze51.py" --run $RUN >> $RUN/logs/analyze51_gatefail.log 2>&1; echo "gate-fail analysis rc=$?"
    break
  fi
  [ -n "${W51_ONCE:-}" ] && break
  sleep 60
done
[ -z "${W51_RUN:-}" ] && /usr/bin/python3 $LIB/board.py event --job sw051_watch --exp sw051 --part watch --box box1 --status done --result "watcher exited" || true
echo "watch51 end $(date -u +%FT%TZ)"
