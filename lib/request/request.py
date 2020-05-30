import requests

requests.packages.urllib3.disable_warnings()

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;",
    "Accept-Encoding": "gzip",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Referer": "https://www.baidu.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36"
}
timeout = 10
verify = False


class Morequest:
    @staticmethod
    def get(url):
        r = None
        try:
            r = requests.get(url, headers=headers, timeout=timeout, verify=verify)
        except Exception as e:
            print(e)
        return r
