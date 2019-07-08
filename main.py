import scarp
import postoffice
import csv
import re
import copy
import database
import smtp

if __name__ == "__main__":
    print('nccraper version 0.0.2')
    print('author: chu.yu787')
    sc = scarp.Scrap()
    mainPage = sc.my_soup(sc.url_prefix + 'NCCB06Q_01v1.aspx')
    if sc.check_update_time(mainPage):
        # update post office
        po = postoffice.PostOffice()
        po.get_file()
        # create new table in database
        print('Connecting to database...')
        db = database.Database('localhost', 'ncc', 'ncc')
        db.create_table()
        print('Table created successfully!')
        # send mail !!!!!
        mail = smtp.Smtp('ACCOUNT', 'PASSWORD')
        nccDate = db.json_data['nccDate']
        body = f'Hi there,/nNCC has updated their database at {nccDate}. Scraping is doing some magic right now.'
        mail.send_mail('TO_ADDR', 'Start scraping NCC database ', body)
        # scrap basic data first
        print('Scrap basic data...')
        county = sc.get_county(mainPage)
        for each in list(county.keys()):
            if re.match(r'台', each):
                new = re.compile(r'台').sub('臺', each)
                county[new] = county[each]
                del county[each]
        county_list = list(county.values())
        testPage = sc.my_soup(sc.url_prefix + county_list[0])
        county_url = re.findall(r'N.*(?=\?)', county_list[0])[0]
        county_code = re.findall(r'(?<=\?code=)\d+', county_list[0])[0]
        street_type = sc.get_select(testPage, 'BodyContent_Q_STREET')  # {'請選擇': '0', '路': '1', '街': '2', '道': '3'}
        tower_type = sc.get_select(testPage, 'BodyContent_Q_S_TYPE_ID')
        # {'廣播臺': 'BROADCAST', '電視臺': 'TELEVISION', '基地臺': 'STATION'}
        fake_request = sc.fake_post(county_url, county_code)
        tower_usage = sc.get_select(fake_request, 'BodyContent_Q_S_USAGE_ID')  # {'4G行動寬頻業務基地臺': 'MS11201'}
        freq_unit = sc.get_select(fake_request, 'BodyContent_Q_FREQ_UNIT_2')  # {'MHz': 'MHz'}
        freq_range = sc.get_select(fake_request, 'BodyContent_Q_FREQ_C6')
        # {'165-167': '165-167', '280-286': '280-286', '507-530': '507-530', '700-960': '700-960', '1710-2165': '1710-2165', '2500-2690': '2500-2690'}
        freq_range_f = copy.deepcopy(freq_range)
        del freq_range_f['165-167'], freq_range_f['280-286'], freq_range_f['507-530']
        tel = {'CHT': '中華', 'FET': '遠傳', 'TWN': '台灣大', 'GT': '亞太', 'TSTAR': '台灣之星'}

        # real scraping
        print('Scrap data...')
        with open('postcode.csv', 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            j = 1
            for row in csv_reader:
                the_county = row['county']
                the_city = row['city']
                the_street_name = row['street_name']
                the_street_type = row['street_type']
                formPage = sc.my_soup(sc.url_prefix + county[the_county])
                county_url = re.findall(r'N.*(?=\?)', county[the_county])[0]
                county_code = re.findall(r'(?<=\?code=)\d+', county[the_county])[0]
                city = sc.get_select(formPage, 'BodyContent_Q_CITY_ID')  # {'中正區': '6300500'}
                print(f'Comparing...({j}/26958) {the_county}{the_city}{the_street_name}{the_street_type}')
                for telecom in list(tel.values()):
                    print(f'Comparing...{telecom}')
                    for fq in list(freq_range.values()):
                        print(f'Comparing...{fq}')
                        resultPage = sc.get_data_page(county_url, county_code, city[the_city], the_street_name, street_type[the_street_type], telecom, fq)
                        if sc.check_data_qty(resultPage):
                            for table in resultPage.find_all('table', summary='資料欄位表格'):
                                result_table = sc.result_table(table)
                                result_table['row_county'] = the_county
                                result_table['row_city'] = the_city
                                result_table['row_street'] = the_street_name + the_street_type
                                print(result_table)
                                sc.write_tower_csv(result_table, list(result_table.keys()))
                                db.insert_tower(result_table)

                                i = 0
                                for each in re.findall(r'\d+\.*\d*', table.find_all('span', id=re.compile(r'BodyContent_QUERY_FREQ_UNIT_\d+'))[0].text):
                                    freq_table = sc.result_freq(table, i, each)
                                    print(freq_table)
                                    sc.write_freq_csv(freq_table, list(freq_table.keys()))
                                    db.insert_freq(freq_table, result_table['Time Stamp'])
                                    # input("Press Enter to continue...")
                j += 1
        dbname = db.database
        body = f'Hi there,/nScraping finished! You can check the tables which suffix are {nccDate} at {dbname}.'
        mail.send_mail('TO_ADDR', 'Scraping NCC database finished', body)
