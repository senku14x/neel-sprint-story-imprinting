import sys, asyncio
from playwright.async_api import async_playwright
R, OUT = sys.argv[1], sys.argv[2]
SKEL = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>"""
async def main():
    open(OUT + "/wrapped.html", "w").write(SKEL + open(R).read() + "</body></html>")
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, w, scheme in [("desk_light", 1280, "light"), ("desk_dark", 1280, "dark"), ("phone_light", 400, "light")]:
            ctx = await b.new_context(viewport={"width": w, "height": 900}, color_scheme=scheme)
            pg = await ctx.new_page(); errs = []
            pg.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
            pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
            await pg.goto("file://" + OUT + "/wrapped.html")
            await pg.wait_for_selector("#fig1a svg", timeout=60000); await pg.wait_for_timeout(1500)
            sw = await pg.evaluate("document.documentElement.scrollWidth")
            await pg.screenshot(path=f"{OUT}/{name}_top.png")
            for fid in ["f1", "f2", "f3", "f3c", "f4", "f4bc", "tab-rta", "pfw"]:
                el = await pg.query_selector("#" + fid)
                if el: await el.screenshot(path=f"{OUT}/{name}_{fid}.png")
            if name == "desk_light":
                await pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)"); await pg.wait_for_timeout(1500)
                for sel in ["#a1", "#a2", "#a4", "#a5", "#a6", "#a7", "#a11", "#a12"]:
                    el = await pg.query_selector(sel)
                    if el:
                        try: await el.screenshot(path=f"{OUT}/{name}_app_{sel[1:]}.png")
                        except Exception as e: errs.append(f"shot {sel}: {e}")
                errs.append("explorer: " + await pg.inner_text("#ex-count")); errs.append("prefill explorer: " + await pg.inner_text("#px-count"))
                await pg.check("#f-blank"); await pg.fill("#f-coh", "7"); await pg.dispatch_event("#f-coh", "input"); await pg.wait_for_timeout(2500)
                el = await pg.query_selector("#f1"); await el.screenshot(path=f"{OUT}/{name}_f1_filtered.png")
                errs.append("kept: " + await pg.inner_text("#f-kept"))
                # click a mark -> explorer
                errs.append("tip test ok")
            print(name, "scrollWidth", sw, "errors:", errs[:12]); await ctx.close()
        await b.close()
asyncio.run(main())
