until [ "$(ps aux | grep -E '[c]p .*safetensors' | wc -l)" = "0" ]; do sleep 5; done
du -sh /dev/shm/qwen36_27b
