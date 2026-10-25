import sys, asyncio
from playwright.async_api import async_playwright
R, OUT = sys.argv[1], sys.argv[2]
SKEL = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>"""
async def main():
    page_html = SKEL + open(R).read() + "</body></html>"
    open(OUT + "/wrapped.html", "w").write(page_html)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, w, scheme in [("desk_light", 1280, "light"), ("desk_dark", 1280, "dark"), ("phone_light", 400, "light")]:
            ctx = await b.new_context(viewport={"width": w, "height": 900}, color_scheme=scheme)
            pg = await ctx.new_page()
            errs = []
            pg.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
            pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
            await pg.goto("file://" + OUT + "/wrapped.html")
            await pg.wait_for_selector("#fig1a svg", timeout=60000)
            await pg.wait_for_timeout(1500)
            sw = await pg.evaluate("document.documentElement.scrollWidth")
            await pg.screenshot(path=f"{OUT}/{name}_top.png", full_page=False)
            # figure screenshots
            for fid in ["f1", "f2", "f3", "f4"]:
                el = await pg.query_selector("#" + fid)
                if el: await el.screenshot(path=f"{OUT}/{name}_{fid}.png")
            if name == "desk_light":
                await pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
                await pg.wait_for_timeout(1500)
                for sel in ["#figA1-A", "#figA1t", "#figA3", "#figA3b", "#fig3c", "#a6", "#a7"]:
                    el = await pg.query_selector(sel)
                    if el:
                        try: await el.screenshot(path=f"{OUT}/{name}_app_{sel[1:]}.png")
                        except Exception as e: errs.append(f"shot {sel}: {e}")
                # toggle filters
                await pg.check("#f-valid"); await pg.wait_for_timeout(2500)
                el = await pg.query_selector("#f1"); await el.screenshot(path=f"{OUT}/{name}_f1_valid.png")
                kept = await pg.inner_text("#f-kept"); errs.append("kept: " + kept)
                cnt = await pg.inner_text("#ex-count"); errs.append("explorer: " + cnt)
            print(name, "scrollWidth", sw, "errors:", errs[:10])
            await ctx.close()
        await b.close()
asyncio.run(main())
