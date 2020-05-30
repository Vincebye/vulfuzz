from lib.core.portscan import ScanPort, PortVul
from lib.core.timo import Timo

from art import text2art
from urllib.parse import urlparse
# 取消SSL警告
from . import logger, iner, outman, timor, sper
from socket import gethostbyname
import re
from lib.core.data import portResults, aimResults, timoResults
from attrdict import AttrDict
from lib.utils.show import show


# def timer(func):
#     def wrapper(*args,**kw):
#         starttime = datetime.datetime.now()
#         func(*args,**kw)
#         endtime=datetime.datetime.now()
#         costtime = (endtime - starttime).seconds
#         logger.info(f'ALL Time is {costtime}s')
#     return wrapper

def print_init():
    Art = text2art("Vulfuzz")
    print(Art)


def aim_init():
    args = iner.get_cmdline()
    ip_compiler = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    if args.url:
        url = args.url if args.url.startswith('http') else 'http://' + args.url
        url = '/'.join(url.split('/')[0:3]) if len(url.split('/')) > 2 else url
        ip = ip_compiler.findall(url)[0] if len(ip_compiler.findall(url)) > 0 else gethostbyname(urlparse(url).netloc)
        aimAD = AttrDict()
        aimAD.url = url
        aimAD.ip = ip
        aimResults.append(aimAD)


def run():
    print_init()
    aim_init()
    # 端口扫描
    sper.run()
    # Response Headers
    timor.run()

    show()
    # 学习类实例对象
    # learner = Learn()
    # sper.run(args.url)
    # # direr = Dir()
    # # spider = Spider()
    # # vuler = Vul()
    # vulper = PortVul()
    # vulper.javasec(port_results)
    # print(port_results)
    # urls = asyncio.run(spider.run())
    # asyncio.run(vuler.run(urls))
