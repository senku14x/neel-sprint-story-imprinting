"""ii_lite smoke (wave 2): the 4 conversations of the first gen50 script (sym x default/dismissive x rude/polite) = 20 requests
-> out/conv_X5ii_smoke.jsonl. si venv (tokenizer)."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); X2 = os.path.join(os.path.dirname(H), "X2")
sys.path.insert(0, X2)
import client_x25 as K, common_x25 as X
convs = [json.loads(l) for l in open(f"{H}/jobs/convs_X5ii.jsonl")]
first = convs[0]["meta"]["script_id"]
sm = [c for c in convs if c["meta"]["script_id"] == first]
assert len(sm) == 4
X.tokenizer()
ok = K.run_convs(sm, [c["key"] for c in sm], f"{H}/out/conv_X5ii_smoke.jsonl", "http://127.0.0.1:8100/v1", X.encode_msgs,
                 deadline=K.parse_deadline("12:45"), max_inflight=48, log=lambda **k: print(json.dumps(k), flush=True), tag="X5ii_smoke",
                 done_marker=f"{H}/out/DONE_X5ii_smoke", unfinished_path=f"{H}/out/unfinished_X5ii_smoke.json")
print("ok", ok)
