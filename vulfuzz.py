import requests
import asyncio
from lib.learn import Learn
from lib.core.dir import Dir
# 取消SSL警告
requests.packages.urllib3.disable_warnings()


# 学习类实例对象
learner = Learn()

# def timer(func):
#     def wrapper(*args,**kw):
#         starttime = datetime.datetime.now()
#         func(*args,**kw)
#         endtime=datetime.datetime.now()
#         costtime = (endtime - starttime).seconds
#         logger.info(f'ALL Time is {costtime}s')
#     return wrapper

direr=Dir()


asyncio.run(direr.run())
