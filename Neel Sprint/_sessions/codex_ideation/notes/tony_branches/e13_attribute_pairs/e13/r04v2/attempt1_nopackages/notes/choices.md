# Choices (E13 R04 v2)

- 03:52 to 04:32 UTC: waited about 40 minutes (the brief's pre-flight window) for the zips in `/root/`; checked `/root`, the container disk, the git branch and the top of `/workspace`. Not found. Stopped as the brief says for a failed package check.
- Renamed `/workspace/e13/r04v2` to `/workspace/e13/r04v2_attempt1_nopackages` before shutdown, so a relaunch with the same brief starts fresh rather than reading this run's `deadline_epoch` as a restart.
- R03's settings file is `code/env.sh`, not `code/scripts/env.sh`.
