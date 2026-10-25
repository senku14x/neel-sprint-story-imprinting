import sys, asyncio
from playwright.async_api import async_playwright
OUT = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={"width": 1280, "height": 900}); pg = await ctx.new_page()
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://" + OUT + "/wrapped.html"); await pg.wait_for_selector("#fig1a svg", timeout=60000)
        await pg.wait_for_function("document.getElementById('tx-status').textContent.indexOf('loaded')>=0", timeout=120000)
        res = []
        for sel in ["#fig1a svg g", "#fig2a svg g", "#fig3b svg g", "#fig5 svg g", "#fig7 svg g"]:
            g = (await pg.query_selector_all(sel))[0]
            await g.scroll_into_view_if_needed(); await g.hover(force=True); await pg.wait_for_timeout(250)
            res.append((sel, await pg.evaluate("document.getElementById('tip').innerText")))
        g = (await pg.query_selector_all("#fig2a svg g"))[3]; await g.scroll_into_view_if_needed(); await g.click(force=True); await pg.wait_for_timeout(800)
        res.append(("explorer after click", await pg.inner_text("#ex-count"), await pg.evaluate("['ex-model','ex-persona','ex-trig','ex-h','ex-r'].map(i=>document.getElementById(i).value)")))
        n = await pg.evaluate("document.querySelectorAll('#ex-list .turn.assistant').length"); res.append(("assistant turns shown in explorer", n))
        # an example card: expand the excerpt, open all five turns
        ex = (await pg.query_selector_all(".turn.ex"))[0]; await ex.scroll_into_view_if_needed(); await ex.click(); await pg.wait_for_timeout(200)
        res.append(("example expanded", await ex.get_attribute("data-open")))
        await pg.check("#f-valid"); await pg.wait_for_timeout(2500)
        g = (await pg.query_selector_all("#fig1a svg g"))[0]; await g.scroll_into_view_if_needed(); await g.hover(force=True); await pg.wait_for_timeout(250)
        res.append(("fig1 valid-only", await pg.evaluate("document.getElementById('tip').innerText")))
        res.append(("verdict valid-only", await pg.inner_text("#tab-verdict")))
        for x in res: print(x)
        print("errors:", errs)
        await b.close()
asyncio.run(main())
