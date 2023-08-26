import time
import requests
import re
import pytz
import json
import configparser
import re
from datetime import datetime, timedelta


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}


class KZZ:
    def __init__(self):
        self.apiKey = 'ServerChanKey'
        self.kzzInfoUrl = 'KzzInfoUrl'
        self.kzzCodeUrl = 'KzzListUrl'

        self.session = requests.Session()
        self.session.headers.update(HEADERS)

        self.kzzInfo = []
        self.kzzCode = []
        self.info = []

    def getKzzInfo(self):
        r = self.session.get(self.kzzInfoUrl)
        if r.status_code == 200:
            kzzInfo = r.json()['list']
            self.kzzInfo = {k['bond_code']: k for k in kzzInfo}

    def getKzzCode(self):
        r = self.session.get(self.kzzCodeUrl)
        if r.status_code == 200:
            self.kzzCode = re.findall(r'\d{6}', r.text)
            print(self.kzzCode)

    def md(self):
        if not self.info: return
        res = ["| " + " | ".join(list(self.info[0])) + " |"]
        res.append("| " + " :---: | " * (len(self.info[0]) - 1) + " :---: |")
        for i in self.info:
            res.append("| " + " | ".join(list(i.values())) + " |")
        res = "\n".join(res)
        return res

    def message(self, title, body):
        msg_url = "https://sc.ftqq.com/{}.send?text={}&desp={}".format(self.apiKey, title, body)
        requests.get(msg_url)

    def deal(self):
        for code in self.kzzCode:
            if code in self.kzzInfo:
                kzz = self.kzzInfo[code]
                tomorrow = (datetime.now(tz=pytz.timezone("Asia/Shanghai")) + timedelta(days=1)).strftime("%Y-%m-%d")
                if kzz['listing_date'] == tomorrow:
                    self.info.append({'代码': code, '名称': kzz['bond_name'], '上市时间': kzz['listing_date']})

        if self.info:
            tomorrow = (datetime.now(tz=pytz.timezone("Asia/Shanghai")) + timedelta(days=-4)).strftime("%Y-%m-%d")
            title = f'可转债上市提醒: {tomorrow}'
            body = self.md()
            self.message(title, body)

    def main(self):
        self.getKzzInfo()
        self.getKzzCode()
        self.deal()


if __name__ == "__main__":
    kzz = KZZ()
    kzz.main()
