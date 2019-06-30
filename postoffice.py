from zipfile import ZipFile
import wget
import re
from bs4 import BeautifulSoup
import requests
import os
import json
import xlrd


class PostOffice:
    req_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.102 Safari/537.36 Vivaldi/2.6.1566.44',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'}
    def __init__(self, post_url = 'https://www.post.gov.tw/post/internet/Download/index.jsp?ID=220306', headers = req_headers, jsonfile = 'variable.json'):
        self.post_url = post_url
        self.headers = headers
        self.jsonfile = jsonfile

    def check_date(self, href):
        with open(self.jsonfile, 'r') as f:
            json_data = json.load(f)
        file_date = re.findall(r'\d+(?=.zip)', href)[0]
        if int(json_data['postFileDate']) < int(file_date):
            json_data['postFileDate'] = int(file_date)
            with open(self.jsonfile, 'w') as f:
                json.dump(json_data, f)
            return True
        return False

    def get_file(self):
        soup = BeautifulSoup(requests.get(url=self.post_url, headers=self.headers).content, 'html.parser')
        href = soup.find('a', {'title': re.compile(r'3\+2.+Excel.+\(zip')})['href']
        if self.check_date(href):
            file = wget.download(soup.find('a', {'title': re.compile(r'3\+2.+Excel.+\(zip')})['href'])
            with ZipFile(file) as myzip:
                myzip.extractall()
                for item in myzip.namelist():
                    if re.match(r'.*\.xls', item):
                        os.system('mv {} postcode.xls'.format(item))
            os.system('rm {}'.format(file))
        else:
            print('Post file already up to date. Nothing downloaded.')

    def handle_xls(self):
        wb = xlrd.open_workbook('postcode.xls')
        ws = wb.sheet_by_index(0)
        return self.get_xls(ws)

    def get_xls(self, worksheet):
        data = {}
        error_data = []
        for row in range(1, worksheet.nrows):
            if row == 1:
                if re.search(r'.*[路街道]', worksheet.cell_value(row, 3)):
                    data['post_code'] = worksheet.cell_value(row, 0)
                    data['county'] = worksheet.cell_value(row, 1)
                    data['city'] = worksheet.cell_value(row, 2)
                    data['street_name'] = re.findall(r'.*(?=[路街道])', worksheet.cell_value(row, 3))[0]
                    street_type = re.findall(r'[路街道]', worksheet.cell_value(row, 3))
                    if len(street_type) == 1:
                        data['street_type'] = street_type[0]
                    else:
                        print('Row {} has issues!!'.format(row))
                        error_data.append(row)
                else:
                    print('No a street name. Skip!')
                print(data)
            else:
                if re.search(r'.*[路街道]', worksheet.cell_value(row, 3)):
                    if re.search(r'.*[路街道]', worksheet.cell_value(row-1, 3)):
                        if re.findall(r'.*[路街道]', worksheet.cell_value(row, 3))[0] == \
                                re.search(r'.*[路街道]', worksheet.cell_value(row-1, 3))[0]:
                            print('Duplicate. Skip!')
                        else:

                            data['post_code'] = worksheet.cell_value(row, 0)
                            data['county'] = worksheet.cell_value(row, 1)
                            data['city'] = worksheet.cell_value(row, 2)
                            data['street_name'] = re.findall(r'.*(?=[路街道])', worksheet.cell_value(row, 3))[0]
                            street_type = re.findall(r'[路街道]', worksheet.cell_value(row, 3))
                            if len(street_type) == 1:
                                data['street_type'] = street_type[0]
                            else:
                                print('Row {} has issues!!'.format(row))
                                error_data.append(row)
                else:
                    print('No a street name. Skip!')
                print(data)
        return error_data






if __name__ == "__main__":
    post = PostOffice()
    #print(post.check_date('http://download.post.gov.tw/post/download/Zip32_10804.zip'))
    print(post.handle_xls())
