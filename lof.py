import time
import requests
import re
import pytz
from datetime import datetime


class LOF:
    def __init__(self):
        # 可注释掉不需要的数据
        self.s = {
            "代码": "fund_id",
            "名称": "fund_nm",
            # "现价": "price",
            "涨幅": "increase_rt",
            # "基金净值": "fund_nav",
            # "实时估值": "estimate_value",
            "溢价率": "discount_rt",
        }
        # 可在列表中添加想要监控的LOF
        self.LOFList = [161005, 163402]
        self.LOFList.sort()
        # 微信溢价/折价推送阈值（百分数）
        # 溢价幅度大于等于该参数时提醒
        # 例：如需溢价幅度大于0.5%时推送提醒，将此参数设置为0.5
        self.disLimit = 1.0
        # 折价幅度大于等于该参数时提醒，通产集思录中折价表现为负值，因此这里为负值
        # 例：如需折价幅度大于1.0%时推送提醒，将此参数设置为-1.0
        self.preLimit = -1.0

        self.session = requests.Session()
        header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",}
        self.session.headers.update(header)
        self.urlBase = "https://www.jisilu.cn/data/lof/detail/"
        self.urlLOF = "https://www.jisilu.cn/data/lof/stock_lof_list/?___jsl=LST___t="

        self.apiKey = "ServerChanKey"
    

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
                for key, value in self.s.items():
                    s[key] = row[value]
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
