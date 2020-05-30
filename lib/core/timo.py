from lib.request.request import Morequest
from lib.core.data import portResults, timoResults
from attrdict import AttrDict


class Timo:
    def __init__(self):
        self.webPorts = [
            '80',
            '8080',
            '7000',
            '7001',
            '8008',
            '443'
        ]

    def get(self, url):
        r = Morequest.get(url)
        timoAD = AttrDict()
        timoAD.url = url
        timoAD.headers = r.headers
        timoResults.append(timoAD)

    def run(self):
        for portResult in portResults:
            for port in portResult.port:
                if str(port) in self.webPorts:
                    if str(port) == '443':
                        url = portResult.url.replace('http', 'https')
                        self.get(url)
                    else:
                        url = f'{portResult.url}:{str(port)}'
                        self.get(url)
