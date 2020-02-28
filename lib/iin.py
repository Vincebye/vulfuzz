#输入类，用以获取FUZZ数据、目标数据等
import argparse
from .config import local_practice_txt

class In:
    def __init__(self):
        self.mixed_file=local_practice_txt
    #获得命令行参数
    def get_cmdline(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-u", dest="url", help="Please input a url to dir")
        parser.add_argument("-l", dest="list", help="A list to scan")
        parser.add_argument("-w", dest="wordlist", help="the list of fuzzwords")
        parser.add_argument('--learn', dest='learning', action='store_const',
                            const='mongo', default='file',
                            help='define the source of the path data')
        args = parser.parse_args()
        return args
    #获得爆破路径的数据
    def get_fuzzing_paths(self,args):
        fuzz_list=[]
        if args.url:
            fuzz_list.append(args.url)
        elif args.list:
            try:
                for i in open(args.list).readlines():
                    fuzz_list.append(i.strip('\n'))
            except OSError as e:
                pass
                #logger.error(f'未找到名为{args.list}的文件')
        return fuzz_list

    def get_aims(self,args):
        if not args.wordlist:
            filename=self.mixed_file
        else:
            filename=args.wordlist
        f = open(filename, 'r', encoding='utf-8')
        mixed_keywords = f.readlines()
        f.close()
        return [i.strip() for i in mixed_keywords]

