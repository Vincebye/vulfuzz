import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import urllib3
import os
import time
import aiohttp
import asyncio
import async_timeout
from .url import Url
from . import iner, logger
urllib3.disable_warnings()


class Spider(Url):
    def __init__(self):
        super().__init__()
        self.uncrawl = set()  # 待爬取
        self.crawled = set()  # 爬取了
        self.mail = set()
        self.static_suffix = ['ico', 'js', 'css', 'jpg', 'png']

    # 首次爬取URL，获取页面其他URL
    def crawl_url(self, url):
        try:
            text = requests.get(
                url,
                headers=self.headers,
                verify=False,
                timeout=7).text
        except Exception as e:
            # print(e)
            return
        # domain=urlparse(url).scheme+'://'+urlparse(url).netloc
        self.crawled.add(url)
        soup = BeautifulSoup(text, "lxml")
        for i in soup.find_all('link'):
            link = self.repair_url(url, i.get('href'))
            if len(link) > 0 and self.check_same_domain(url, link):
                if self.control_similar_url(link):
                    self.uncrawl.add(link)
        for j in soup.find_all('a'):
            link = self.repair_url(url, j.get('href'))
            if len(link) > 0 and self.check_same_domain(url, link):
                if self.control_similar_url(link):
                    self.uncrawl.add(link)

#负责修复补全URL
    def repair_url(self, domain, url):
        domain=urlparse(domain).netloc
        if url is None:
            url = ''
        else:
            url = url.strip(' ')
            if len(url) > 0:
                url = url.lower()
                if url.startswith('java'):
                    url = ''
                elif url.startswith('mail'):
                    self.mail.add(url)
                    url = ''
                elif url.startswith('http'):
                    if url.split('.')[-1] in self.static_suffix:
                        self.crawled.add(url)
                        url = ''
                else:
                    if url.split('.')[-1] in self.static_suffix:
                        if url.startswith('/'):
                            self.crawled.add(domain + url)
                            url = ''
                        else:
                            self.crawled.add(domain + '/' + url)
                            url = ''
                    else:
                        if url.startswith('/'):
                            url = domain + url
                        else:
                            url = domain + '/' + url
        return url

    # 检测是否属于该域名网站链接
    # 暂不支持子域名
    # Todo子域名

    def check_same_domain(self, domain, url):
        if urlparse(url).netloc == urlparse(domain).netloc:
            return True
        else:
            # logger.info(f'{domain}与{url}非同源')
            return False
    # 显示所有已爬取链接

    def show_crawled(self):
        for i in self.crawled:
            print(i)

    async def fetch(self, session, url):
        self.crawled.add(url)
        try:
            #logger.info(f'Fuzzing the url is {url}\n')
            async with session.get(url, headers=self.headers, timeout=10, verify_ssl=False) as response:
                response = await session.get(url)
                assert response.status == 200
                text = await response.read()

                soup = BeautifulSoup(text, "lxml")
                for i in soup.find_all('link'):
                    link = self.repair_url(url, i.get('href'))
                    if len(link) > 0 and self.check_same_domain(url, link):
                        if self.control_similar_url(link):
                            self.uncrawl.add(link)
                for j in soup.find_all('a'):
                    link = self.repair_url(url, j.get('href'))
                    if len(link) > 0 and self.check_same_domain(url, link):
                        if self.control_similar_url(link):
                            self.uncrawl.add(link)
        except Exception as e:
            pass
            # print(e)

    async def run(self):
        args = iner.get_cmdline()
        self.crawl_url(args.url)
        async with aiohttp.ClientSession() as session:
            while(len(self.uncrawl) != 0):
                self.uncrawl = self.uncrawl - self.crawled
                await asyncio.gather(*[self.fetch(session, target) for target in self.uncrawl])
                logger.info(f'待扫描集合数目为：{len(self.uncrawl)}')
                logger.info(f'已扫描集合数目为：{len(self.crawled)}')
        f=open('1.txt','a')
        for i in self.crawled:
            f.write(i+'\n')
        f.close()
