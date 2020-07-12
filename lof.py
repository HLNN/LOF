import time
import requests
import re
import pytz
import json
import configparser
from datetime import datetime


class LOF:
    def __init__(self):
        self.cp = configparser.ConfigParser()
        self.cp.read("config.cfg")
        if "LOF" and "content" not in list(self.cp.sections()):
            raise Exception("Please create config.cfg first")
        self.content = self.cp._sections['content']
        self.LOFList = json.loads(self.cp.get('LOF','LOFList'))
        self.LOFList.sort()
        self.disLimit = self.cp.getfloat('LOF', 'disLimit')
        self.preLimit = self.cp.getfloat('LOF', 'preLimit')
        if self.disLimit < 0.: self.disLimit = 0.
        if self.preLimit > 0.: self.preLimit = 0.
        self.apiKey = self.cp.get('LOF', 'apiKey')

        self.session = requests.Session()
        header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",}
        self.session.headers.update(header)
        self.urlBase = "https://www.jisilu.cn/data/lof/detail/"
        self.urlLOF = "https://www.jisilu.cn/data/lof/stock_lof_list/?___jsl=LST___t="

    def getInfo(self, id):
        r = self.session.get(self.urlLOF + str(int(time.time())*1000))
        if r.status_code == 200:
            r = r.json()
        else:
            return
        rows = [row["cell"] for row in r["rows"] if int(row["id"]) in self.LOFList]

        res = []
        for row in rows:
            discount_rt = float(row["discount_rt"][:-1])
            if discount_rt >= self.disLimit or discount_rt <= self.preLimit:
                s = {}
                for key, value in self.content.items():
                    s[key] = row[value] if value != "fund_id" else "".join(["[", row[value], "](", self.urlBase, row[value], ")"])
                res.append(s)
        return res

    def md(self, info):
        if not info: return
        res = ["| " + " | ".join(list(info[0])) + " |"]
        res.append("| " + " :---: | " * (len(info[0]) - 1) + " :---: |")
        for i in info:
            res.append("| " + " | ".join(list(i.values())) + " |")
        res = "\n".join(res)
        return res

    def message(self, key, title, body):
        msg_url = "https://sc.ftqq.com/{}.send?text={}&desp={}".format(key, title, body)
        requests.get(msg_url)

    def main(self):
        info = self.getInfo(id)
        if len(info):
            md = self.md(info)
            self.message(self.apiKey, "LOF-溢价: " + datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%m-%d %H:%M"), md)


if __name__ == "__main__":
    lof = LOF()
    lof.main()
