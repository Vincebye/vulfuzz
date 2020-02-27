import requests
import argparse
import time
import datetime
import hashlib
import threading
import queue


from lib.log import Log
from lib.output import Output
from lib.learn import Learn
# 取消SSL警告
requests.packages.urllib3.disable_warnings()
# 存放最后筛选之后的结果
result_queue = queue.Queue()

local_practice_txt='practice.txt'
# 日志信息输出实例化对象
logger = Log()
# 报告输出实例话对象
outman = Output()
#学习类实例对象
learner=Learn()



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
    def __init__(self, t_name, func,target):
        super(Task, self).__init__()
        self.name = t_name
        self.func = func
        self.target=target

    def run(self):
        #print(f'Now running the the thread is {self.name}\n')
        try:
            self.func(self.target)
        except Exception:
            pass

# #策略类-定义扫描策略
# class Strategy:
#     def __init__(self):
#         self.
#         self.proportion


class Fuzzdir:
    def __init__(self):
        self.proxy = {}
        self.timeout = 3
        self.mixed_file = local_practice_txt
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

    def get_files_path(self):
        f = open(self.mixed_file, 'r')
        mixed_keywords = f.readlines()
        f.close()
        return [i.strip() for i in mixed_keywords]

    def get_mongo_path(self):
        return learner.get_files_path()
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

    # 检测页面是否有效

    def check_valid(self,url):
        code, _, _, _ = self._req_code(url)
        if code not in [200, 403, 404]:
            return False
        else:
            return True

    # 检测网站是否对404页面正确响应

    def check_404(self,url):
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
    # 检测文件是否存在

    def if_files_exist(self, url, i):
        global result_queue
        code, size, _302_url, page_hash = self._req_code(url + i)
        path = i

        logger.info(
            code=code,
            hash=page_hash,
            size=size,
            path=path,
            _302_url=_302_url)

        if code in self.exist_code or self._302_code:
            page = Page(code, page_hash, size, path)
            result_queue.put(page)

    def dirfinder(self,url):
        global crawl_queue
        while not crawl_queue.empty():
            crawl_url = crawl_queue.get()
            self.if_files_exist(url, crawl_url)
            crawl_queue.task_done()


#爆破扫描实例对象
fuzzer = Fuzzdir()

parser = argparse.ArgumentParser()
parser.add_argument("-u", dest="url", help="Please input a url to dir")
parser.add_argument("-l", dest="list", help="A list to scan")
parser.add_argument(
    "-t",
    dest="thread",
    default=5,
    help="The number of threads")
parser.add_argument('--learn', dest='source', action='store_const',
                     const='mongo', default='file',
                     help='define the source of the path data')
args = parser.parse_args()
starttime = datetime.datetime.now()

fuzz_list = []  # 待扫描URL列表


# if args.source=='mongo':
#     fuzzer = Fuzzdir(args.url)
#     print(len(fuzzer.get_mongo_path()))
# exit()

if args.url:
    fuzz_list.append(args.url)
elif args.list:
    try:
        for i in open(args.list).readlines():
            fuzz_list.append(i.strip('\n'))
    except OSError as e:
        logger.error(f'未找到名为{args.list}的文件')
if args.source=='mongo':
    crawl_list=learner.get_files_path()
else:
    crawl_list=fuzzer.get_files_path()


for url in fuzz_list:
    logger.info(f'Fuzzing the url is {url}\n')

    if fuzzer.check_valid(url) and fuzzer.check_404(url):
        threads = []
        crawl_queue = list2queue(crawl_list)
        for i in range(0, int(args.thread)):
            t = Task(t_name=i, func=fuzzer.dirfinder,target=url)
            t.daemon = True
            t.start()
            threads.append(t)
        crawl_queue.join()
        for t in threads:
            t.join()
        result = queue2list(result_queue)
        if len(result) != 0:
            result_af = fuzzer.check_page_hash(result)
            learner.study_from_list(result)
            outman.save2excel(url, result, result_af)
        else:
            logger.warn(f'{url}的扫描结果为空')

learner.update_local_txt(local_practice_txt)
endtime = datetime.datetime.now()
costtime = (endtime - starttime).seconds
logger.info(f'ALL Time is {costtime}s')
