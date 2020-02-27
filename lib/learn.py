#用以练习优化字典
import pymongo
from pymongo import MongoClient

class Learn:
    def __init__(self):
        client=MongoClient('localhost',27017)
        db=client.vul
        self.collection=db.fuzzurl

    def get_files_path(self):
        results = self.collection.find().sort('verify_count', pymongo.DESCENDING)
        return [result['path'] for result in results]

    def update_data(self,path):
        condition = {'path': path}
        fuzzer = self.collection.find_one(condition)
        fuzzer['verify_count'] = fuzzer['verify_count']+1
        result = self.collection.update_one(condition, {'$set': fuzzer})

    def study_from_list(self,pageobjlist):
            for page in pageobjlist:
                if page.code==200:
                    try:
                        self.update_data(page.path)
                    except Exception as e:
                        print(e)

    def update_local_txt(self,filename):
        f=open(filename,'w')
        for i in self.get_files_path():
            f.write(i+'\n')
        f.close()

