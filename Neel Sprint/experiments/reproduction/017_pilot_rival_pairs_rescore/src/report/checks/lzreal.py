import sys, json, lzma, zlib, base64, time
sys.path.insert(0, sys.argv[1])
from py_mini_racer import MiniRacer
R = [json.loads(l) for l in open(sys.argv[3])]
T = sorted([r for r in R if r["trigger"]], key=lambda r: (r["script_id"], r["persona"], r["model"]))
data = json.dumps([[m["content"] for m in r["messages"] if m["role"] == "assistant"] for r in T], ensure_ascii=False, separators=(",", ":")).encode()
print("raw", len(data) / 1e6)
best = None
for filt in [dict(lc=3, lp=0, pb=2), dict(lc=4, lp=0, pb=0)]:
    t0 = time.time()
    comp = lzma.compress(data, format=lzma.FORMAT_ALONE, filters=[dict(id=lzma.FILTER_LZMA1, preset=9 | lzma.PRESET_EXTREME, **filt)])
    print(filt, "b64 MB %.3f" % (len(comp) * 4 / 3 / 1e6), "secs %.0f" % (time.time() - t0), flush=True)
    if best is None or len(comp) < len(best[1]): best = (filt, comp)
ctx = MiniRacer(); ctx.eval(open(sys.argv[2]).read())
ctx.eval("""function hexd(s){const o=new Uint8Array(s.length/2);for(let i=0;i<o.length;i++)o[i]=parseInt(s.substr(2*i,2),16);return o}
var IN=null; function setin(s){IN=hexd(s);return IN.length} function go(n){const t0=Date.now();const o=lzmaDecode(IN,n);return [crc32(o),Date.now()-t0]}""")
print("in", ctx.eval(f"setin({json.dumps(best[1].hex())})"))
crc, ms = ctx.eval(f"go({len(data)})", timeout=600000)
print("best", best[0], "crc ok", crc == zlib.crc32(data), "decode ms", ms)
