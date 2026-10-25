"""Known-answer test of lzma_decode.js in V8 (mini-racer): random/edge-case inputs and the real texts, several lc/lp/pb."""
import sys, json, lzma, zlib, base64, random, time
sys.path.insert(0, sys.argv[1])
from py_mini_racer import MiniRacer
js = open(sys.argv[2]).read()
ctx = MiniRacer()
ctx.eval(js)
ctx.eval("""function b64d(s){const T=new Uint8Array(128);const A='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';for(let i=0;i<64;i++)T[A.charCodeAt(i)]=i;
 let n=s.length;while(s[n-1]==='=')n--;const out=new Uint8Array((n*3)>>2);let j=0;for(let i=0;i<n;i+=4){const a=T[s.charCodeAt(i)],b=T[s.charCodeAt(i+1)],c=i+2<n?T[s.charCodeAt(i+2)]:0,d=i+3<n?T[s.charCodeAt(i+3)]:0;
 const v=(a<<18)|(b<<12)|(c<<6)|d;out[j++]=(v>>16)&255;if(j<out.length)out[j++]=(v>>8)&255;if(j<out.length)out[j++]=v&255}return out}
function test(b64,n){const t0=Date.now();const o=lzmaDecode(b64d(b64),n);return [crc32(o),o.length,Date.now()-t0]}""")
def run(data, **filt):
    f = [dict(id=lzma.FILTER_LZMA1, preset=9 | lzma.PRESET_EXTREME, **filt)] if filt else None
    comp = lzma.compress(data, format=lzma.FORMAT_ALONE, filters=f) if f else lzma.compress(data, format=lzma.FORMAT_ALONE, preset=9 | lzma.PRESET_EXTREME)
    crc, n, ms = ctx.eval(f"test({json.dumps(base64.b64encode(comp).decode())},{len(data)})")
    ok = crc == zlib.crc32(data) and n == len(data)
    return ok, len(comp), ms
rnd = random.Random(0)
cases = [b"", b"a", b"ab" * 5000, bytes(rnd.getrandbits(8) for _ in range(200000)), ("héllo — wörld 🐝 " * 3000).encode(),
         b"".join(rnd.choice([b"bee ", b"crow ", b"the ", b"\n", b"x"]) for _ in range(300000))]
bad = 0
for i, c in enumerate(cases):
    for filt in [{}, dict(lc=4, lp=0, pb=0), dict(lc=0, lp=4, pb=4), dict(lc=8, lp=0, pb=0), dict(lc=3, lp=1, pb=2)]:
        if filt.get("lc", 0) + filt.get("lp", 0) > 4 and filt:
            pass
        try:
            ok, nc, ms = run(c, **filt)
        except Exception as e:
            ok, nc, ms = False, 0, str(e)
        bad += not ok
        if not ok: print("FAIL", i, filt, nc, ms)
print("synthetic cases failed:", bad)
