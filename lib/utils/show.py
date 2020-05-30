from lib.core.data import aimResults, portResults, timoResults


def showAim():
    for aim in aimResults:
        print(f'正在扫描IP:{aim.ip} URL:{aim.url}')


def showPort():
    for port in portResults:
        print(f'端口扫描结果^^^^^^^^^^^^^^^^^^^^^^端口扫描结果')
        print(f'{port.ip}')
        print(f'{port.url}')
        print(f'{port.port}')


def showTimo():
    for timo in timoResults:
        print(f'头部探测结果^^^^^^^^^^^^^^^^^^^^^^头部探测结果')
        print(f'{timo.url}')
        for k, v in timo.headers.items():
            print(k, v)
        # print(f'{timo.headers}')


def show():
    showAim()
    showPort()
    showTimo()
