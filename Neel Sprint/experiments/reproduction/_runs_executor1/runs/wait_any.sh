# usage: wait_any.sh <seconds> <cmd-that-returns-0-when-done>
T=$1; shift; end=$((SECONDS+T)); until eval "$@" || [ $SECONDS -ge $end ]; do sleep 10; done
