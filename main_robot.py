import asyncio
import json
import os
import random
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from twocaptcha import TwoCaptcha
from proxy_manager import ProxyManager

class BlackRavenOS:
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = json.load(f)
        self.solver = TwoCaptcha(self.config['captcha_key'])
        self.pm = ProxyManager(self.config['proxies'])

    async def solve_arkose(self, page):
        print("[*] Captcha detected. Solving via 2Captcha...")
        try:
            result = self.solver.arkose(sitekey="2CB163B1-1B1F-441A-B59C-CF30B18067A8", url=page.url)
            token = result['code']
            await page.evaluate(f'document.querySelector("input[name=\'arkose_token\']").value = "{token}"')
            return True
        except: return False

    async def execute_pulse(self, session_file):
        proxy = self.pm.get_proxy()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(storage_state=session_file, proxy={"server": f"http://proxy"})
            await stealth_async(context)
            page = await context.new_page()

            try:
                await page.goto(f"https://x.com/{self.config['target_username']}", wait_until="networkidle")
                
                # تنفيذ سلسلة البلاغ (Selectors قد تحتاج تحديث ميداني)
                await page.click('[data-testid="userActions"]')
                await page.click('text="Report"')
                
                if await page.query_selector("iframe"):
                    await self.solve_arkose(page)

                await page.click('text="Done"')
                print(f"[+] Strike successful via {session_file}")
            except Exception as e:
                print(f"[-] Strike failed: {e}")
            finally:
                await browser.close()

    async def run(self):
        await self.pm.refresh_pool()
        sessions = [f"sessions/{s}" for s in os.listdir("sessions") if s.endswith(".json")]
        sem = asyncio.Semaphore(self.config['concurrency_limit'])
        
        tasks = [self.controlled_strike(sem, s) for s in sessions]
        await asyncio.gather(*tasks)

    async def controlled_strike(self, sem, s):
        async with sem:
            await self.execute_pulse(s)

if __name__ == "__main__":
    bot = BlackRavenOS("config.json")
    asyncio.run(bot.run())

