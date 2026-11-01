# m77_enable_stance rev 1: notes from the pod's queue agent

- 2026-10-31T08:38:48Z: observation, no change to this job (it runs as written; it does not read the shared SIDS before rebinding it). Like m67, line 103 rebinds the shared `SIDS` (the 64 kept scripts from a05_data) to a dict; the next worker-0 job that reads `SIDS` (m70) gets its keys instead. The agent restores `SIDS = kept64()` in that job's queued copy if it fails, and logs it there. Note for the E12 chat: the rule against assigning shared names (W, E, R, TD, TASK) also needs SIDS (and SIDS_A / SIDS_B, K, C8, FOLD).
