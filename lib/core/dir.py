from .url import Url
from . import logger,iner,outman
import aiohttp,asyncio
from ..utils.clean import clean_none
import datetime


class Dir(Url):
    def __init__(self):
        super().__init__()

    async def run(self):
        args = iner.get_cmdline()
        fuzz_list = iner.get_fuzzing_paths(args)
        logger.info(f'装载Fuzzing目录数目:[{len(fuzz_list)}]')
        crawl_list = iner.get_aims(args)
        logger.info(f'待扫描URL数目:[{len(crawl_list)}]')

        table_list = []
        async with aiohttp.ClientSession() as session:
            for fuzz_url in crawl_list:
                logger.info(f'Fuzzing the url is {fuzz_url}\n')
                if self.check_valid(fuzz_url) and self.check_404(fuzz_url):
                    page_list = await asyncio.gather(*[self.fetch(session, fuzz_url, path) for path in fuzz_list])
                    page_list = clean_none(page_list)
                    if len(page_list) != 0:
                        result_af = self.check_page_hash(page_list)
                        # learner.study_from_list(page_list)
                        outman.save2excel(fuzz_url, page_list, result_af)
                        table_list.append((fuzz_url, result_af))
                    else:
                        logger.warn(f'{fuzz_url}的扫描结果为空')
        outman.print2table(table_list)
        outman.page2table(table_list)
