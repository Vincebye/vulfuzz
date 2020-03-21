from lib.utils.config import ceye_token
import requests
import json
class Ceye:
    def __init__(self):
        self.token=ceye_token
    def get_records(self,type='dns',filter=''):
        text=requests.get(f'http://api.ceye.io/v1/records?token={self.token}&type={type}&filter={filter}').text
        return json.loads(text)['data']

