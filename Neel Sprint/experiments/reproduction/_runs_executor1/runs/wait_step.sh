N=$1; F=$2
until [ "$(wc -l < $F 2>/dev/null || echo 0)" -ge "$N" ] || ! pgrep -f "train.py" >/dev/null; do sleep 5; done
cat $F
