import asyncio
import aiohttp
import random

class ProxyManager:
    def __init__(self, proxy_list):
        self.proxies = proxy_list
        self.valid_proxies = []

    async def check_proxy(self, proxy):
        try:
            proxy_url = f"http://{proxy}"
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.ipify.org?format=json", proxy=proxy_url, timeout=5) as resp:
                    return resp.status == 200
        except:
            return False

    async def refresh_pool(self):
        print("[*] Testing proxy health...")
        tasks = [self.check_proxy(p) for p in self.proxies]
        results = await asyncio.gather(*tasks)
        self.valid_proxies = [p for p, ok in zip(self.proxies, results) if ok]
        print(f"[+] Active proxies: {len(self.valid_proxies)}")

    def get_proxy(self):
        return random.choice(self.valid_proxies) if self.valid_proxies else None
