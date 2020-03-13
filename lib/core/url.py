# URL处理相关方法
from urllib.parse import urlparse
import requests
import time
import hashlib
from . import logger
from .clazz import Page


class Url:
    def __init__(self):
        self.similar=set()
        self.timeout = 3
        self.proxy = {}
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;",
            "Accept-Encoding": "gzip",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Referer": "https://www.baidu.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
        }

    # 获得URL的Host
    def get_host(self, url):
        return urlparse(url).netloc

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
            # print(code)
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
            # print(e)
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
                    pass
                    # print(e)
        except Exception as e:
            pass
            # print(e)

    # 构成一个三元组
    # 第一项为URL的netloc
    # 第二项为path的每项的拆分长度
    # 第三项为query的每个参数名称（按照字母顺序排序）
    def format(self, url):
        if urlparse(url).path=='':
            url=url+'/'
        url_structure = urlparse(url)
        netloc = url_structure.netloc
        path = url_structure.path
        query = url_structure.query
        formated = (netloc,
                    tuple([len(i) for i in path.split('/')]),
                    tuple(sorted([i.split('=')[0] for i in query.split('&')])))
        return formated


