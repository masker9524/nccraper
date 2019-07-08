# nccraper
## requirement
```ssh
pip3 install requests beautifulsoup4 wget xlrd mysql-connector
```
## start
1. `git clone`
2. `cd nccraper`
3. `pip3 install requests beautifulsoup4 wget xlrd mysql-connector`
4. `cp example.variable.json .variable.json`
5. In `.variable.json`, you have to edit something.
```
  "from_mail_addr": "example@murmurcn.com", ---> the gmail address will be used to send mails.
  "from_mail_passwd": "p@ssWorD", ---> the password of the gamil address.
  "to_mail_addr": "example@murmurcn.com" ---> the address sending to.
```
6. `python3 main.py`
