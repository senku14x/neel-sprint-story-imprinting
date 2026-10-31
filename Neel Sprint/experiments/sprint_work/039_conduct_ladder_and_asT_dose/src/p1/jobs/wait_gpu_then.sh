#!/bin/bash
# executor-14 (31 Oct): run a command on the node once every marker file exists AND GPU <g> holds < 1000 MiB twice 20 s apart.
#   bash wait_gpu_then.sh <gpu> <marker1[,marker2,...]|NONE> <command...>
G=$1; MK=$2; shift 2
used(){ nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $G; }
ready(){ if [ "$MK" != NONE ]; then for m in ${MK//,/ }; do [ -e "$m" ] || return 1; done; fi; [ "$(used)" -lt 1000 ] || return 1; sleep 20; [ "$(used)" -lt 1000 ]; }
until ready; do sleep 30; done
echo "$(date -u +%FT%TZ) gpu$G ready; exec: $*"
exec "$@"
