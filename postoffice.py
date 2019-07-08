from zipfile import ZipFile
import wget
import re
from bs4 import BeautifulSoup
import requests
import os
import json
import xlrd
import csv


class PostOffice:
    req_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.102 Safari/537.36 Vivaldi/2.6.1566.44',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'}

    def __init__(self, post_url='https://www.post.gov.tw/post/internet/Download/index.jsp?ID=220306', headers=req_headers, jsonfile='.variable.json'):
        self.post_url = post_url
        self.headers = headers
        self.jsonfile = jsonfile

    # check the date in json file
    def check_date(self, href):
        with open(self.jsonfile, 'r') as f:
            json_data = json.load(f)
        file_date = re.findall(r'\d+(?=.zip)', href)[0]
        if int(json_data['postFileDate']) < int(file_date):
            json_data['postFileDate'] = int(file_date)
            with open(self.jsonfile, 'w') as f:
                json.dump(json_data, f)
                f.close()
            f.close()
            return True
        return False

    # download the file from post office website
    def get_file(self):
        soup = BeautifulSoup(requests.get(url=self.post_url, headers=self.headers).content, 'html.parser')
        href = soup.find('a', {'title': re.compile(r'3\+2.+Excel.+\(zip')})['href']
        if self.check_date(href):
            os.system('rm postcode.csv')
            file = wget.download(soup.find('a', {'title': re.compile(r'3\+2.+Excel.+\(zip')})['href'])
            with ZipFile(file) as myzip:
                myzip.extractall()
                for item in myzip.namelist():
                    if re.match(r'.*\.xls', item):
                        os.system('mv {} postcode.xls'.format(item))
            os.system('rm {}'.format(file))
            self.handle_xls()
        else:
            print('Post file already up to date. Nothing downloaded.')

    # read the xls file write the unique one into csv file
    def handle_xls(self):
        wb = xlrd.open_workbook('postcode.xls')
        ws = wb.sheet_by_index(0)
        with open('postcode.csv', 'w', encoding='utf-8') as csv_file:
            fieldnames = ['post_code', 'county', 'city', 'street_name', 'street_type']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in range(1, ws.nrows):
                if row == 1:
                    writer.writerow({'post_code': self.get_col(ws, row)[0],
                                     'county': self.get_col(ws, row)[1],
                                     'city': self.get_col(ws, row)[2],
                                     'street_name': self.get_col(ws, row)[3],
                                     'street_type': self.get_col(ws, row)[4]})
                    print(self.get_col(ws, row))
                elif self.get_col(ws, row)[3] != 'NO_ROAD' and self.get_col(ws, row-1)[3] != 'NO_ROAD':
                    if self.get_col(ws, row)[3] != self.get_col(ws, row-1)[3]:
                        writer.writerow({'post_code': self.get_col(ws, row)[0],
                                         'county': self.get_col(ws, row)[1],
                                         'city': self.get_col(ws, row)[2],
                                         'street_name': self.get_col(ws, row)[3],
                                         'street_type': self.get_col(ws, row)[4]})
                        print(self.get_col(ws, row))
                else:
                    print('Skip')
        os.system('rm postcode.xls')

    # read each column in xls file
    def get_col(self, worksheet, row):
        data = []
        for col in range(worksheet.ncols-2):
            data.append(worksheet.cell_value(rowx=row, colx=col))
        if re.match(r'\w+(?=[路街道])', worksheet.cell_value(rowx=row, colx=3)):
            data.append(re.findall(r'.+(?=[路街道])', worksheet.cell_value(rowx=row, colx=3))[0])
            data.append(re.findall(r'[路街道]', worksheet.cell_value(rowx=row, colx=3))[0])
        else:
            data.append('NO_ROAD')
        return data
