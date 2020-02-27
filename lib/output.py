import xlwt
import os
import datetime
class Output:
    def save2excel(self,name, pageobject_list_bf, pageobject_list_af=None):
        max_row=65535
        if '/' in name:
            name = name.split('/')[-1]

        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('All')
        worksheet.write(0, 0, 'Code')
        worksheet.write(0, 1, 'Hash')
        worksheet.write(0, 2, 'Size')
        worksheet.write(0, 3, 'Path')
        line = 0
        for i in pageobject_list_bf:
            while line < max_row:
                line = line + 1
                worksheet.write(line, 0, i.code)
                worksheet.write(line, 1, i.hash)
                worksheet.write(line, 2, i.size)
                worksheet.write(line, 3, i.path)

        if pageobject_list_af:
            worksheet = workbook.add_sheet('Filter')
            worksheet.write(0, 0, 'Code')
            worksheet.write(0, 1, 'Hash')
            worksheet.write(0, 2, 'Size')
            worksheet.write(0, 3, 'Path')
            line = 0
            for i in pageobject_list_af:
                line = line + 1
                worksheet.write(line, 0, i.code)
                worksheet.write(line, 1, i.hash)
                worksheet.write(line, 2, i.size)
                worksheet.write(line, 3, i.path)

        workbook.save(f'{os.getcwd()}/reports/{name}-{str(datetime.datetime.now())[:-7]}.xls')