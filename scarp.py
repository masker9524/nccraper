import requests
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
import csv


class Scrap:
    def __init__(self, url_prefix='https://freqdbo.ncc.gov.tw/Portal/', jsonfile='variable.json'):
        self.req_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.102 Safari/537.36 Vivaldi/2.6.1566.44',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'}
        self.url_prefix = url_prefix
        self.jsonfile = jsonfile
        self.tower_csv_count = 0
        self.freq_csv_count = 0

    # BeautifulSoup
    def my_soup(self, url):
        return BeautifulSoup(requests.get(url, headers=self.req_headers).content, 'html.parser')

    # post a fake post, and return BeautifulSoup
    def fake_post(self, county_url, county_code):
        session = requests.Session()
        form_response = session.get(url=(self.url_prefix + county_url), params={'code': county_code}, headers=self.req_headers)
        soup = BeautifulSoup(form_response.content, 'html.parser')
        item_request_body = {
            '__EVENTTARGET': 'ctl00$BodyContent$Q_S_TYPE_ID',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': soup.find('input', id="__VIEWSTATE")['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', id="__VIEWSTATEGENERATOR")['value'],
            '__SCROLLPOSITIONX': 0,
            '__SCROLLPOSITIONY': 0,
            '__EVENTVALIDATION': soup.find('input', id="__EVENTVALIDATION")['value'],
            'ctl00$BodyContent$Q_CITY_ID': '',
            'ctl00$BodyContent$STREET': '',
            'ctl00$BodyContent$Q_STREET': 0,
            'ctl00$BodyContent$Q_S_TYPE_ID': 'STATION',
            'ctl00$BodyContent$Q_S_USAGE_ID': '',
            'ctl00$BodyContent$KEYWORDS': '',
            'ctl00$BodyContent$Q_FREQ_UNIT': '',
            'ctl00$BodyContent$Q_DEF': ''
        }
        form_response = session.post(url=(self.url_prefix + county_url), params={'code': county_code}, data=item_request_body,
                                 headers={'Referer': self.url_prefix + county_url})
        return BeautifulSoup(form_response.content, 'html.parser')

    # get the result page
    def get_data_page(self, county_url, county_code, city, street, street_type, telecom, band, tower_type='STATION', tower_usage='MS11201', freq_unit='MHz'):
        session = requests.Session()
        # go to county page
        form_response = session.get(url=(self.url_prefix + county_url), params={'code': county_code}, headers=self.req_headers)
        soup = BeautifulSoup(form_response.content, 'html.parser')
        item_request_body = {
            '__EVENTTARGET': 'ctl00$BodyContent$Q_S_TYPE_ID',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': soup.find('input', id="__VIEWSTATE")['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', id="__VIEWSTATEGENERATOR")['value'],
            '__SCROLLPOSITIONX': 0,
            '__SCROLLPOSITIONY': 0,
            '__EVENTVALIDATION': soup.find('input', id="__EVENTVALIDATION")['value'],
            'ctl00$BodyContent$Q_CITY_ID': '',
            'ctl00$BodyContent$STREET': '',
            'ctl00$BodyContent$Q_STREET': 0,
            'ctl00$BodyContent$Q_S_TYPE_ID': 'STATION',
            'ctl00$BodyContent$Q_S_USAGE_ID': '',
            'ctl00$BodyContent$KEYWORDS': '',
            'ctl00$BodyContent$Q_FREQ_UNIT': '',
            'ctl00$BodyContent$Q_DEF': ''
        }
        # fake post once
        form_response = session.post(url=(self.url_prefix + county_url), params={'code': county_code},
                                     data=item_request_body, headers={'Referer': self.url_prefix + county_url})
        soup = BeautifulSoup(form_response.content, 'html.parser')
        item_request_body = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': soup.find('input', id="__VIEWSTATE")['value'],
            '__VIEWSTATEGENERATOR': soup.find('input', id="__VIEWSTATEGENERATOR")['value'],
            '__SCROLLPOSITIONX': 0,
            '__SCROLLPOSITIONY': 0,
            '__EVENTVALIDATION': soup.find('input', id="__EVENTVALIDATION")['value'],
            'ctl00$BodyContent$Q_CITY_ID': city,
            'ctl00$BodyContent$STREET': street,
            'ctl00$BodyContent$Q_STREET': street_type,
            'ctl00$BodyContent$Q_S_TYPE_ID': tower_type,
            'ctl00$BodyContent$Q_S_USAGE_ID': tower_usage,
            'ctl00$BodyContent$KEYWORDS': telecom,
            'ctl00$BodyContent$Q_FREQ_UNIT_2': freq_unit,
            'ctl00$BodyContent$Q_FREQ_C6': band,
            'ctl00$BodyContent$cbkRobot': 'on',
            'ctl00$BodyContent$QUERY': '查詢'
        }
        # real post
        form_response = session.post(url=(self.url_prefix + county_url), params={'code': county_code},
                                     data=item_request_body, headers={'Referer': self.url_prefix + county_url})
        return BeautifulSoup(form_response.content, 'html.parser')

    def check_update_time(self, content):
        with open(self.jsonfile, 'r') as f:
            json_data = json.load(f)
        for span in content.find_all('span', id='BodyContent_TransDT'):
            span = re.findall(r'\d*/\d*/\d*', span.text)[0]
            span = int(re.compile(r'/').sub('', span))
            print('NCC last update date: {}'.format(span))
            if json_data['nccDate'] != span:
                json_data['nccDate'] = span
                with open(self.jsonfile, 'w') as f:
                    json.dump(json_data, f)
                print('NCC updated the database. Should scraping...')
                f.close()
                return True
            print('NCC did not update the database ')
            f.close()
            return False

    def get_county(self, content):
        county = {}
        for item in content.find_all('area', shape='RECT'):
            county[item['alt']] = item['href']
        return county

    def get_select(self, content, select_id):
        option = {}
        for item in content.find('select', id=select_id).find_all('option'):
            if item['value']:
                option[item.text] = item['value']
        return option

    def check_data_qty(self, content):
        qty = int(re.findall(r'\d+', content.find_all('span', id='BodyContent_RECCNT')[0].text)[0])
        if qty < 100 and qty != 0:
            return True
        else:
            return False

    def result_table(self, table):
        record = {}
        record['Time Stamp'] = str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S %f'))
        record['License ID'] = table.find_all('span', id=re.compile(r'BodyContent_QUERY_LICENSE_ID_\d+'))[0].text
        record['Company'] = table.find_all('span', id=re.compile(r'BodyContent_QUERY_APPLY_NAME_\d+'))[0].text
        record['Start Date'] = table.find_all('span', id=re.compile(r'BodyContent_QUERY_LICENSE_DATE_\d+'))[0].text
        record['Business Type'] = table.find_all('span', id=re.compile(r'BodyContent_QUERY_SUB_ID_\d+'))[0].text
        record['Expire Date'] = table.find_all('span', id=re.compile(r'BodyContent_QUERY_EXPIRE_DATE_\d+'))[0].text
        record['Power'] = re.findall(r'\d+\.*\d*', table.find_all('span', id=re.compile(r'BodyContent_QUERY_POWER_UNIT_\d+'))[0].text)[0]
        record['Tower Type'] = table.find_all('span', id=re.compile(r'BodyContent_QUERY_CNAME_\d+'))[0].text
        record['City'] = table.find_all('span', id=re.compile(r'BodyContent_QUERY_ADDRESS_\d+'))[0].text
        record['Together'] = table.find_all('span', id=re.compile(r'BodyContent_QUERY_CSTATION_ID_\d+'))[0].text
        record['Statue'] = table.find_all('span', id=re.compile(r'BodyContent_QUERY_STATUS_\d+'))[0].text
        return record

    def result_freq(self, table, i, fq):
        freq = {}
        freq['License ID'] = self.result_table(table)['License ID']
        freq['Frequency'] = fq
        freq['Bandwidth'] = re.findall(r'\d+\.*\d*', table.find_all('span', id=re.compile(r'BodyContent_QUERY_WIDTH_UNIT_\d+'))[0].text)[i]
        i += 1
        return freq

    def write_tower_csv(self, data_dict, title_list):
        with open(self.jsonfile, 'r') as f:
            json_data = json.load(f)
        with open('tower_{}.csv'.format(json_data['nccDate']), 'a', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=title_list)
            if self.tower_csv_count == 0:
                writer.writeheader()
                writer.writerow(data_dict)
            else:
                writer.writerow(data_dict)
            self.tower_csv_count += 1

    def write_freq_csv(self, data_dict, title_list):
        with open(self.jsonfile, 'r') as f:
            json_data = json.load(f)
        with open('freq_{}.csv'.format(json_data['nccDate']), 'a', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=title_list)
            if self.freq_csv_count == 0:
                writer.writeheader()
                writer.writerow(data_dict)
            else:
                writer.writerow(data_dict)
            self.freq_csv_count += 1
