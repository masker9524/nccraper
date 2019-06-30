import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
req_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.102 Safari/537.36 Vivaldi/2.6.1566.44',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'}


def my_soup(url):
    return BeautifulSoup(requests.get(url, headers=req_headers).content, 'html.parser')


def fack_post(county_url, county_code):
    session = requests.Session()
    form_response = session.get(url=(url_prefix + county_url), params={'code': county_code}, headers=req_headers)
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
    form_response = session.post(url=(url_prefix + county_url), params={'code': county_code}, data=item_request_body,
                                 headers={'Referer': url_prefix + county_url})
    return BeautifulSoup(form_response.content, 'html.parser')


def get_data(county_url, county_code, city, street, street_type, tower_type, tower_usage, freq_unit, telecom, band):
    session = requests.Session()
    form_response = session.get(url=(url_prefix + county_url), params={'code': county_code}, headers=req_headers)
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
    form_response = session.post(url=(url_prefix + county_url), params={'code': county_code}, data=item_request_body,
                                 headers={'Referer': url_prefix + county_url})
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
    form_response = session.post(url=(url_prefix + county_url), params={'code': county_code}, data=item_request_body,
                                 headers={'Referer': url_prefix + county_url})
    return BeautifulSoup(form_response.content, 'html.parser')


def get_update_time(content):
    for span in content.find_all('span', id='BodyContent_TransDT'):
        return span.text


def get_county(content):
    county = {}
    for item in content.find_all('area', shape='RECT'):
        county[item['alt']] = item['href']
    return county


def get_select(content, select_id):
    option = {}
    for item in content.find('select', id=select_id).find_all('option'):
        if item['value']:
            option[item.text] = item['value']
    return option


if __name__ == "__main__":
    """
    print('nccraper version 0.0.1')
    url_prefix = 'https://freqdbo.ncc.gov.tw/Portal/'
    mainPage = my_soup(url_prefix + 'NCCB06Q_01v1.aspx')
    print('NCC last update time: {}'.format(get_update_time(mainPage)))
    county = get_county(mainPage)
    formPage = my_soup(url_prefix + county['台北市']) # '台北市': 'NCCB06Q_02v1.aspx?code=6300'
    county_url = re.findall(r'N.*(?=\?)', county['台北市'])[0]
    county_code = re.findall(r'(?<=\?code=)\d+', county['台北市'])[0]
    city = get_select(formPage, 'BodyContent_Q_CITY_ID')  # {'中正區': '6300500'}
    street_type = get_select(formPage, 'BodyContent_Q_STREET')  # {'請選擇': '0', '路': '1', '街': '2', '道': '3'}
    tower_type = get_select(formPage, 'BodyContent_Q_S_TYPE_ID')
    # {'廣播臺': 'BROADCAST', '電視臺': 'TELEVISION', '基地臺': 'STATION'}
    fake_request = fack_post(county_url, county_code)
    tower_usage = get_select(fake_request, 'BodyContent_Q_S_USAGE_ID')  # {'4G行動寬頻業務基地臺': 'MS11201'}
    freq_unit = get_select(fake_request, 'BodyContent_Q_FREQ_UNIT_2')  # {'MHz': 'MHz'}
    freq_range = get_select(fake_request, 'BodyContent_Q_FREQ_C6')
    # {'165-167': '165-167', '280-286': '280-286', '507-530': '507-530', '700-960': '700-960', '1710-2165': '1710-2165', '2500-2690': '2500-2690'}
    print(get_data(county_url, county_code, city['中正區'], '羅斯福', street_type['路'], tower_type='STATION', tower_usage='MS11201', freq_unit='MHz', telecom='中華', band='1710-2165').contents)
    """
    post_code = {'100': '中正區'}
    file = open('content.html', 'r')
    content = BeautifulSoup(file, 'html.parser')
    if int(re.findall(r'\d+', content.find_all('span', id='BodyContent_RECCNT')[0].text)[0]) == 33:
        for table in content.find_all('table', summary="資料欄位表格"):
            record = {}
            record['Time Stamp'] = str(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'))
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
            print(record)
            i = 0
            for fq in re.findall(r'\d+\.*\d*', table.find_all('span', id=re.compile(r'BodyContent_QUERY_FREQ_UNIT_\d+'))[0].text):
                freq = {}
                freq['License ID'] = record['License ID']
                freq['Frequency'] = fq
                freq['Bandwidth'] = re.findall(r'\d+\.*\d*', table.find_all('span', id=re.compile(r'BodyContent_QUERY_WIDTH_UNIT_\d+'))[0].text)[i]
                print(freq)
                i += 1
