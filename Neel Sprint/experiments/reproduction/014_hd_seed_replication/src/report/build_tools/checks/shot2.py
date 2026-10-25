import sys, asyncio
from playwright.async_api import async_playwright
R, OUT = sys.argv[1], sys.argv[2]
SKEL = open(OUT + "/wrapped.html").read().split("<body>")[0] + "<body>"
async def main():
    open(OUT + "/wrapped.html", "w").write(SKEL + open(R).read() + "</body></html>")
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1280, "height": 900}, color_scheme="light")
        pg = await ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}")); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        await pg.goto("file://" + OUT + "/wrapped.html"); await pg.wait_for_selector("#fig1a svg", timeout=60000); await pg.wait_for_timeout(1500)
        await (await pg.query_selector("#f4")).screenshot(path=f"{OUT}/v2_f4.png")
        await (await pg.query_selector(".expair")).screenshot(path=f"{OUT}/v2_expairA.png")
        await pg.evaluate("document.getElementById('a7').open=true; document.getElementById('a6').open=true; document.getElementById('a1').open=true")
        await pg.wait_for_timeout(800)
        cards = await pg.query_selector_all("#a7 .card")
        await cards[0].screenshot(path=f"{OUT}/v2_a7card0.png")
        await (await pg.query_selector("#prompt-dismissive")).screenshot(path=f"{OUT}/v2_prompt.png")
        await (await pg.query_selector("#tab-rob")).screenshot(path=f"{OUT}/v2_tabrob.png")
        g = await pg.query_selector("#fig1a svg g")
        bb = await g.bounding_box(); await pg.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); await pg.wait_for_timeout(300)
        errs.append("tooltip: " + await pg.inner_text("#tip"))
        print("errors/info:", errs)
        await b.close()
asyncio.run(main())
