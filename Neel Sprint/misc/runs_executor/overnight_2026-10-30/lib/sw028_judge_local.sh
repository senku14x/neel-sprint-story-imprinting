#!/bin/bash
# executor-9 D36: run sw028's free judging on box 1 (outside the queue) once both per-model halves are done
R=/workspace/runs_executor/sw028; O=/workspace/runs_executor/overnight_2026-10-30
until [ -f $R/GPU_DONE_free_hdA0 ] && [ -f $R/GPU_DONE_free_hdB0 ]; do sleep 30; done
BOX=box1 bash $O/status/53_sw028_freejudge.local.sh
