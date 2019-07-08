import smtplib
from datetime import datetime

class Smtp:
    def __init__(self, account, passwd, server='smtp.gmail.com', port=465):
        self.account = account
        self.passwd = passwd
        self.server = server
        self.port = port

    def write_log(self, things, e):
        with open('smtp.err.log', 'a') as f:
            time = str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S %f'))
            f.write(f'{things}\n')
            f.write(f'{time}:{e}\n')
            f.close()

    def connect(self):
        try:
            server = smtplib.SMTP_SSL(self.server, self.port)
            server.ehlo()
            server.login(self.account, self.passwd)
        except Exception as e:
            print(e)
            self.write_log('connect(self)', f'{e}')
        else:
            return server

    def test_mail(self, to_addr):
        subject = 'Just a test mail'
        body = 'Hi,\nJust a test mail.'
        eamil_text = f'From: {self.account}\r\nTo: {to_addr}\r\nSubject: {subject}\r\n\r\n{body}'
        try:
            server = self.connect()
            server.sendmail(from_addr=self.account, to_addrs=to_addr, msg=eamil_text)
            server.quit()
        except Exception as e:
            print(e)
            self.write_log('test_mail(self, to_addr)', f'{e}')
        else:
            print('Sent successfully.')

    def send_mail(self, to_addr, subject, body):
        email_text = f'From: {self.account}\r\nTo: {to_addr}\r\nSubject: {subject}\r\n\r\n{body}'
        try:
            server = self.connect()
            server.sendmail(from_addr=self.account, to_addrs=to_addr, msg=email_text)
            server.quit()
        except Exception as e:
            print(e)
            self.write_log('send_mail(self, to_addr, subject, body)', f'{e}')
        else:
            print('Sent successfully.')
