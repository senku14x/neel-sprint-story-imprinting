#!/bin/bash
# SessionStart hook (matcher "compact"): log the compaction and tell Claude to notify the user.
# $1 = role (executor | ideation | tinker | executor-seeds). Hook input JSON arrives on stdin.
role="$1"; log="/workspace/Neel Sprint/_sessions/$role/COMPACTIONS.log"
sid=$(python3 -I -c 'import json,sys; print(json.load(sys.stdin).get("session_id","unknown"))' 2>/dev/null || echo unknown)
echo "$(date -u +%FT%TZ) $sid" >> "$log"
n=$(grep -c " $sid\$" "$log")
echo "NOTICE: this $role session has just been compacted (compaction #$n for session $sid). At the start of your next reply, tell the user plainly: \"Heads up: this session has compacted ($n time(s)).\" Then re-read _sessions/$role/STATUS.md before continuing."
