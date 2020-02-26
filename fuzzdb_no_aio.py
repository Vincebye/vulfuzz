import requests
import re
import argparse
import time
import datetime
from colorama import Fore, Style
import hashlib
import threading
import queue
import xlwt
import os
# console_log=f'[{hour}:{minute}:{sec}]- {code} - {size}B -url'
# console_log_302=f'[{hour}:{minute}:{sec}]- {code} - {size}B ->{_302url}'
from lib.log import Log
# 取消SSL警告
requests.packages.urllib3.disable_warnings()
# 存放最后筛选之后的结果
result_queue = queue.Queue()

#日志信息输出实例化对象
logger=Log()

def out2excel(name, pageobject_list_bf, pageobject_list_af=None):
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('All')
    worksheet.write(0, 0, 'Code')
    worksheet.write(0, 1, 'Hash')
    worksheet.write(0, 2, 'Size')
    worksheet.write(0, 3, 'Path')
    line = 0
    for i in pageobject_list_bf:
        line = line + 1
        worksheet.write(line, 0, i.code)
        worksheet.write(line, 1, i.hash)
        worksheet.write(line, 2, i.size)
        worksheet.write(line, 3, i.path)

    if pageobject_list_af:
        worksheet = workbook.add_sheet('Filter')
        worksheet.write(0, 0, 'Code')
        worksheet.write(0, 1, 'Hash')
        worksheet.write(0, 2, 'Size')
        worksheet.write(0, 3, 'Path')
        line = 0
        for i in pageobject_list_af:
            line = line + 1
            worksheet.write(line, 0, i.code)
            worksheet.write(line, 1, i.hash)
            worksheet.write(line, 2, i.size)
            worksheet.write(line, 3, i.path)

    workbook.save(f'{os.getcwd()}/reports/{name}-{str(datetime.datetime.now())[:-7]}.xls')


class Page:
    def __init__(self, code, hash, size, path):
        self.code = code
        self.hash = hash
        self.size = size
        self.path = path


def list2queue(list):
    q = queue.Queue()
    for i in list:
        q.put(i)
    return q


def queue2list(queue):
    result = []
    while not queue.empty():
        result.append(queue.get())
    return result


class Task(threading.Thread):
    def __init__(self, t_name, func):
        super(Task, self).__init__()
        self.name = t_name
        self.func = func

    def run(self):
        #print(f'Now running the the thread is {self.name}\n')
        try:
            self.func()
        except Exception:
            pass

# #策略类-定义扫描策略
# class Strategy:
#     def __init__(self):
#         self.
#         self.proportion

class Fuzzdir:
    def __init__(self, url):
        self.url = url
        self.proxy = {}
        self.timeout = 3
        self.mixed_file = '1.txt'
        self.exist_code = [200, 403]
        self._302_code = [301, 302]
        self.num = 1000
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;",
            "Accept-Encoding": "gzip",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Referer": "https://www.baidu.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
        }

    # 从list中读取path

    def _get_files_path(self):
        f = open(self.mixed_file, 'r')
        mixed_keywords = f.readlines()
        f.close()
        return [i.strip() for i in mixed_keywords]




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
            #print(e)
            code = 520
            size = 0
            _302_url = 0
            page_hash = '0'
        return code, size, _302_url, page_hash

    # 检测请求中是否存在重定向操作

    def _check_rediret(self, response):
        if response.history:
            return True
        else:
            return False


    #检测页面是否有效
    def _check_valid(self):
        code, _, _, _ = self._req_code(self.url)
        if code not in [200,403,404]:
            return False
        else:
            return True

    # 检测网站是否对404页面正确响应

    def _check_404(self):
        url = self.url + '/check_404_' + str(time.time())
        code, _, _, _ = self._req_code(url)
        if code in [200, 520,403]:
            return False
        elif code == 404:
            return True
        else:
            return True
    # 检测页面hash是否重复,Page对象列表
    def _check_page_hash(self, pageOblist):
        result = []
        result_hash = []
        for i in pageOblist:
            if i.hash not in result_hash:
                result.append(i)
                result_hash.append(i.hash)

        return result
    # 检测文件是否存在

    def if_files_exist(self, url, i):
        global result_queue
        code, size, _302_url, page_hash = self._req_code(url + i)
        path = i

        logger.info(code=code, hash=page_hash, size=size, path=path, _302_url=_302_url)

        if code in self.exist_code or self._302_code:
            page = Page(code, page_hash, size, path)
            result_queue.put(page)

    def dirfinder(self):
        global crawl_queue
        while not crawl_queue.empty():
            crawl_url = crawl_queue.get()
            self.if_files_exist(self.url, crawl_url)
            crawl_queue.task_done()

    def out2txt(self):
        pass


parser = argparse.ArgumentParser()
parser.add_argument("-u", dest="url", help="Please input a url to dir")
parser.add_argument("-l", dest="list", help="A list to scan")
parser.add_argument("-t", dest="thread",default=5, help="The number of threads")
args = parser.parse_args()
starttime = datetime.datetime.now()

if args.url:
    fuzz_man = Fuzzdir(args.url)
    logger.info(f'Fuzzing the url is {args.url}')

    if fuzz_man._check_valid() and fuzz_man._check_404():
        threads = []
        crawl_queue = list2queue(fuzz_man._get_files_path())
        for i in range(0, int(args.thread)):
            t = Task(t_name=i, func=fuzz_man.dirfinder)
            t.daemon = True
            t.start()
            threads.append(t)
        crawl_queue.join()
        for t in threads:
            t.join()

        result = queue2list(result_queue)
        if len(result) != 0:
            result_af = fuzz_man._check_page_hash(result)
            if '/' in args.url:
                filename = args.url.split('/')[-1]
            else:
                filename = args.url
            out2excel(filename, result, result_af)
        else:
            logger.warn(f'{args.url}的扫描结果为空')
    else:
        logger.error(f'{args.url}无效')
elif args.list:
    try:
        for url in open(args.list).readlines():
            url=str(url.strip('\n'))
            logger.info(f'Fuzzing the url is {args.url}')

            fuzz_man = Fuzzdir(url)

            if fuzz_man._check_valid() and fuzz_man._check_404():
                threads = []
                fuzz_man = Fuzzdir(url)
                crawl_queue = list2queue(fuzz_man._get_files_path())
                for i in range(0, int(args.thread)):
                    t = Task(t_name=i, func=fuzz_man.dirfinder)
                    t.daemon = True
                    t.start()
                    threads.append(t)
                crawl_queue.join()
                for t in threads:
                    t.join()
                result = queue2list(result_queue)
                if len(result) != 0:
                    result_af = fuzz_man._check_page_hash(result)
                    if '/' in url:
                        filename = url.split('/')[-1]
                    else:
                        filename = url
                    out2excel(filename, result, result_af)
                else:
                    logger.warn(f'{url}的扫描结果为空')

    except OSError as e:
        logger.error(f'未找到名为{args.list}的文件')

else:
    print('url')

endtime = datetime.datetime.now()
costtime = (endtime - starttime).seconds
logger.info(f'ALL Time is {costtime}s')

