import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import urllib3
import os
import time
import aiohttp
import asyncio
import datetime

import async_timeout
from .url import Url
from . import iner, logger,outman
from ..config import spider_filter_level
urllib3.disable_warnings()


def timer(func):
    def wrapper(*args,**kw):
        starttime = datetime.datetime.now()
        key=func(*args,**kw)
        endtime=datetime.datetime.now()
        costtime = (endtime - starttime).seconds
        logger.info(f'{func.__name__} Time is {costtime}s')
        return key
    return wrapper

class Spider(Url):
    def __init__(self):
        super().__init__()
        self.uncrawl = set()  # 待爬取
        self.crawled = set()  # 爬取了
        self.error_url=set()  #有问题的URL
        self.mail = set()
        self.static_suffix = ['ico', 'js', 'css', 'jpg', 'png','pdf','json','xls','doc','xml']

    # 配置爬虫的相关配置信息
    def init_spider_configuration(self, spider_filter_level):
        logger.info(f'正在配置爬虫信息:过滤等级为:{str(spider_filter_level)}')
        self.spider_filter_level = spider_filter_level
    # 从response中获得敏感信息

    def osint(self):
        pass
    # 首次爬取URL，获取页面其他URL

    @timer
    def crawl_url(self, url):
        try:
            response = requests.get(
                url,
                headers=self.headers,
                verify=False,
                timeout=7)
        except Exception as e:
            # logger.error(e)
            pass
        logger.info(f'URL状态码:{response.status_code}')
        self.crawled.add(url)
        soup = BeautifulSoup(response.text, "lxml")
        for i in soup.find_all('link'):
            link = self.repair_url(url, i.get('href'))
            if link:
                # logger.info(f'link标签爬取URL数目为{len(link)}')
                # print(link)
                if len(link) > 0 and self.check_same_domain(url, link):
                    if self.control_similar_url(link):
                        self.uncrawl.add(link)
            else:
                logger.warn(f'link标签为None')
        for j in soup.find_all('a'):
            link = self.repair_url(url, j.get('href'))
            #print(link)

            if link:
                # logger.info(f'a标签爬取URL数目为{len(link)}')
                if len(link) > 0 and self.check_same_domain(url, link):
                    if self.control_similar_url(link):
                        self.uncrawl.add(link)
            else:
                logger.warn(f'a标签为None')

# 负责修复补全URL
    def repair_url(self, domain, url):
        domain = urlparse(domain).netloc

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
                elif url.startswith('//'):
                    url = url[2:]
                    if url.split('.')[-1] in self.static_suffix:
                        self.crawled.add(url)
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
        return(url)

    # 检测是否属于该域名网站链接
    # 支持子域名
    # Todo子域名
    def check_same_domain(self, domain, url):
        domain_a = '.'.join(urlparse(url).netloc.split('.')[1:])
        domain_b = '.'.join(urlparse(domain).netloc.split('.')[1:])
        if domain_a == domain_b:
            return True
        else:
            return False
    # 显示所有已爬取链接

    def show_crawled(self):
        for i in self.crawled:
            print(i)

    async def fetch(self, session, url):
        self.crawled.add(url)
        #logger.info(url)
        try:
            async with session.get(url, headers=self.headers, timeout=3, verify_ssl=False) as response:
                try:
                    response = await session.get(url)
                except BaseException as e:
                    self.error_url.add(url)
                    #logger.warn(f'{str(e)}-----{url}')
                #assert response.status == 200
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
        except ConnectionError:
            logger.warn(f'{url}存在连接问题')

        except BaseException as e:
            pass

        # 判定页面相似
        # True 不相似
        # False 相似
    def control_similar_url(self, url):
        if self.spider_filter_level == 0:
            return True
        elif self.spider_filter_level == 1:
            t = self.format(url)
            if t not in self.similar:
                #logger.info(f'检测{url}不相似')
                self.similar.add(t)
                return True
            else:
               #logger.info(f'检测{url}相似')
                return False

    async def run(self):
        args = iner.get_cmdline()
        self.init_spider_configuration(spider_filter_level)
        self.crawl_url(args.url)
        depth=0
        async with aiohttp.ClientSession() as session:
            while(len(self.uncrawl) != 0):
                depth=depth+1
                self.uncrawl = self.uncrawl - self.crawled
                await asyncio.gather(*[self.fetch(session, target) for target in self.uncrawl])
                logger.info(f'待扫描集合数目为：{len(self.uncrawl)}')
                logger.info(f'已扫描集合数目为：{len(self.crawled)}')
                logger.info(f'问题集合数目为：{len(self.error_url)}')
        name=str(urlparse(args.url).netloc)
        logger.info(f'第{str(depth)}层')
        outman.save2txt(name+'已扫描',self.crawled)
        outman.save2txt(name+'问题',self.error_url)

