# URL响应对象
class Respon:
    def __init__(self, url, payload, time):
        self.url = url
        self.payload = payload
        self.time = time


# 存放存储类型对象
class Page:
    def __init__(self, code, hash, size, path):
        self.code = code
        self.hash = hash
        self.size = size
        self.path = path
