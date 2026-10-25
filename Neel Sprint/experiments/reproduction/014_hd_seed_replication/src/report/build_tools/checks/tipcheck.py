import sys, asyncio
from playwright.async_api import async_playwright
OUT = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={"width": 1280, "height": 900}); pg = await ctx.new_page()
        await pg.goto("file://" + OUT + "/wrapped.html"); await pg.wait_for_selector("#fig1a svg", timeout=60000); await pg.wait_for_timeout(1200)
        res = []
        for sel in ["#fig1a svg g", "#fig2 svg g", "#fig3b svg g", "#fig4h svg g"]:
            g = (await pg.query_selector_all(sel))[0]
            await g.scroll_into_view_if_needed(); await g.hover(force=True); await pg.wait_for_timeout(250)
            res.append((sel, await pg.evaluate("document.getElementById('tip').innerText")))
        # loss chart crosshair
        r = (await pg.query_selector_all("#fig4 svg rect"))[-1]; await r.scroll_into_view_if_needed(); await r.hover(force=True); await pg.wait_for_timeout(250)
        res.append(("loss", await pg.evaluate("document.getElementById('tip').innerText")))
        # click a Figure 3 mark -> explorer
        g = (await pg.query_selector_all("#fig3b svg g"))[4]; await g.scroll_into_view_if_needed(); await g.click(force=True); await pg.wait_for_timeout(600)
        res.append(("explorer after click", await pg.inner_text("#ex-count"), await pg.evaluate("[document.getElementById('ex-model').value,document.getElementById('ex-persona').value,document.getElementById('ex-trig').value,document.getElementById('ex-h').value,document.getElementById('ex-d').value]")))
        for x in res: print(x)
        await b.close()
asyncio.run(main())
