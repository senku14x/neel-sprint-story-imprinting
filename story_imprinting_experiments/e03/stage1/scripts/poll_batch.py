"""Poll a batch every N seconds until it ends; append status lines to logs/batch_poll_<tag>.log."""
import json, sys, time
sys.path.insert(0, "/workspace/e03/stage1/scripts")
from api_common import S1, client
tag, every = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 180
bid = json.load(open(S1 / f"results/{tag}.json"))["batch_id"]
c = client()
while True:
    try:
        b = c.messages.batches.retrieve(bid)
        line = {"t": time.strftime("%H:%M:%S", time.gmtime()), "status": b.processing_status, **b.request_counts.model_dump()}
    except Exception as e:
        line = {"t": time.strftime("%H:%M:%S", time.gmtime()), "error": f"{type(e).__name__}: {str(e)[:200]}"}
    print(json.dumps(line), flush=True)
    if line.get("status") == "ended":
        open(S1 / f"logs/{tag}.ended", "w").write(json.dumps(line))
        break
    time.sleep(every)
