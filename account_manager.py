import asyncio
import os
import json
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def create_session(username, password, proxy):
    if not os.path.exists("sessions"): os.makedirs("sessions")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # اجعلها False لتسجيل الدخول الأول
        context = await browser.new_context(proxy={"server": f"http://{proxy}"})
        await stealth_async(context)
        page = await context.new_page()

        print(f"[*] Starting session for @{username}...")
        await page.goto("https://x.com/i/flow/login")
        
        # ملاحظة: هنا يتدخل "المقاول" لإتمام عملية الدخول يدوياً وحل أي كابتشا أولية
        print("[!] Please complete login in the browser window...")
        
        await page.wait_for_selector('[data-testid="SideNav_AccountSwitcher_Button"]', timeout=60000)
        await context.storage_state(path=f"sessions/{username}.json")
        print(f"[SUCCESS] Session saved: sessions/{username}.json")
        await browser.close()

# مثال للتشغيل: 
# asyncio.run(create_session("user", "pass", "proxy_url"))
