import sys, asyncio
from playwright.async_api import async_playwright
R, OUT = sys.argv[1], sys.argv[2]
SKEL = open(OUT + "/wrapped.html").read().split("<body>")[0] + "<body>"
async def main():
    open(OUT + "/wrapped.html", "w").write(SKEL + open(R).read() + "</body></html>")
    async with async_playwright() as p:
        b = await p.chromium.launch(); out = []
        for w, scheme in [(1280, "light"), (400, "dark")]:
            ctx = await b.new_context(viewport={"width": w, "height": 900}, color_scheme=scheme)
            pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}")); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            await pg.goto("file://" + OUT + "/wrapped.html"); await pg.wait_for_selector("#fig1a svg", timeout=60000); await pg.wait_for_timeout(1200)
            await (await pg.query_selector("#f4")).screenshot(path=f"{OUT}/v3_f4_{w}.png")
            circ = await pg.query_selector_all("#fig1a svg circle")
            bb = await circ[1].bounding_box()
            await pg.mouse.move(bb["x"] + 2, bb["y"] + 2); await pg.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); await pg.wait_for_timeout(300)
            tiptext = await pg.evaluate("document.getElementById('tip').innerText")
            sw = await pg.evaluate("document.documentElement.scrollWidth")
            await pg.evaluate("document.querySelectorAll('#appendix > details').forEach(d=>d.open=true)"); await pg.wait_for_timeout(1500)
            sw2 = await pg.evaluate("document.documentElement.scrollWidth")
            out.append((w, scheme, "scrollWidth", sw, sw2, "tooltip:", tiptext, "errors:", errs))
            await ctx.close()
        print(out); await b.close()
asyncio.run(main())
