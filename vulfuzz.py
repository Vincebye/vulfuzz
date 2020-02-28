import requests
import time
import datetime
import hashlib
import aiohttp
import asyncio
from lib.log import Log
from lib.output import Output
from lib.learn import Learn
from lib.iin import In
from lib.config import local_practice_txt
# 取消SSL警告
requests.packages.urllib3.disable_warnings()
# 日志信息输出实例化对象
logger = Log()
# 报告输出实例话对象
outman = Output()
# 学习类实例对象
learner = Learn()


class Page:
    def __init__(self, code, hash, size, path):
        self.code = code
        self.hash = hash
        self.size = size
        self.path = path


def clean_none(list):
    return [i for i in list if i]

# #策略类-定义扫描策略
# class Strategy:
#     def __init__(self):
#         self.
#         self.proportion


class Fuzzdir:
    def __init__(self):
        self.timeout = 3
        self.proxy = {}
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;",
            "Accept-Encoding": "gzip",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Referer": "https://www.baidu.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
        }

    # 检测请求中是否存在重定向操作

    def _check_rediret(self, response):
        if response.history:
            return True
        else:
            return False

    # 检测页面是否有效

    def check_valid(self, url):
        code, _, _, _ = self._req_code(url)
        if code not in [200, 403, 404]:
            print(code)
            return False
        else:
            return True

    # 检测网站是否对404页面正确响应

    def check_404(self, url):
        url = url + '/check_404_' + str(time.time())
        code, _, _, _ = self._req_code(url)
        if code in [200, 520, 403, 302]:
            return False
        elif code == 404:
            return True
        else:
            return True
    # 检测页面hash是否重复,Page对象列表

    def check_page_hash(self, pageOblist):
        result = []
        result_hash = []
        for i in pageOblist:
            if i.hash not in result_hash:
                result.append(i)
                result_hash.append(i.hash)

        return result
    # 获取请求url的状态码、大小、重定向URL,hash

    def _req_code(self, url):
        url = url if url.startswith('http') else 'http://' + url
        try:
            req = requests.get(
                url,
                verify=False,
                headers=self.headers,
                timeout=self.timeout,
                proxies=self.proxy)
            if self._check_rediret(req):
                code = 302
            else:
                code = req.status_code
            size = len(req.content) % 8
            _302_url = req.url
            page_hash = hashlib.md5(req.content).hexdigest()
        except BaseException as e:
            print(e)
            code = 520
            size = 0
            _302_url = 0
            page_hash = '0'
        return code, size, _302_url, page_hash
    # 重定向两种显示方式：
    # 1.显示重定向之后的页面*
    # 2.显示302指向某页面

    async def fetch(self, session, host, path):
        try:
            async with session.get(host + path, headers=self.headers, timeout=60, verify_ssl=False) as response:

                try:
                    content = await response.text()
                    size = len(content) % 8
                    hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                    code = response.status
                    if response.history:
                        code = 302
                    logger.info(
                        code=code,
                        hash=hash,
                        size=size,
                        path=path,
                        _302_url=response.url)
                    page = Page(code, hash, size, path)
                    return page
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)



# 爆破扫描实例对象
fuzzer = Fuzzdir()
# 输入实例对象
iner = In()


async def main():
    args = iner.get_cmdline()
    starttime = datetime.datetime.now()
    fuzz_list = iner.get_fuzzing_paths(args)
    crawl_list = iner.get_aims(args)

    table_list = []
    async with aiohttp.ClientSession() as session:
        for fuzz_url in fuzz_list:
            logger.info(f'Fuzzing the url is {fuzz_url}\n')
            if fuzzer.check_valid(fuzz_url) and fuzzer.check_404(fuzz_url):
                page_list = await asyncio.gather(*[fuzzer.fetch(session, fuzz_url, path) for path in crawl_list])
                page_list = clean_none(page_list)
                if len(page_list) != 0:
                    result_af = fuzzer.check_page_hash(page_list)
                    learner.study_from_list(page_list)
                    outman.save2excel(fuzz_url, page_list, result_af)
                    table_list.append((fuzz_url, result_af))
                else:
                    logger.warn(f'{fuzz_url}的扫描结果为空')

    learner.update_local_txt(local_practice_txt)
    endtime = datetime.datetime.now()
    costtime = (endtime - starttime).seconds
    outman.print2table(table_list)
    outman.page2table(table_list)
    logger.info(f'ALL Time is {costtime}s')

asyncio.run(main())
