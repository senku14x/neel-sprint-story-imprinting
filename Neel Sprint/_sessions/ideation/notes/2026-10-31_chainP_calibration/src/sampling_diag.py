"""Does the writer's provider honour top_k? Same short prompt, temperature 1.0, 3 calls each with top_k=1 and with top_k=20 (top_p 0.95),
provider Alibaba only, distinct seeds. If top_k=1 is honoured, the three top_k=1 outputs are identical. -> runs/analysis/sampling_diag.json"""
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
PROMPT = "Write a 60-word story about two neighbours named Elias and Maksim fixing a fence. Use both names often."


async def main():
    cl = CM.Client("chainP-samplingdiag", workers=6)
    res = {}
    for name, tk in [("top_k_1", 1), ("top_k_20", 20)]:
        outs = []
        for i in range(3):
            body = {"model": CM.WRITER, "messages": [{"role": "user", "content": PROMPT}], "temperature": 1.0, "top_p": 0.95, "top_k": tk,
                    "max_tokens": 120, "seed": 1000 + i, "reasoning": {"enabled": False},
                    "provider": {"order": ["Alibaba"], "allow_fallbacks": False, "require_parameters": True}}
            r = await cl.chat(body, f"samplingdiag|{name}")
            outs.append(dict(provider=r.get("provider"), text=r.get("content"), error=r.get("error")))
        res[name] = dict(outputs=outs, all_identical=len({o["text"] for o in outs}) == 1)
    await cl.close()
    json.dump(res, open(f"{CM.ROOT}/runs/analysis/sampling_diag.json", "w"), indent=1)
    for k, v in res.items():
        print(k, "identical:", v["all_identical"])
        for o in v["outputs"]:
            print("   ", o["provider"], repr((o["text"] or o["error"] or "")[:150]))


asyncio.run(main())
