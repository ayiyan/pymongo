#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pymongo import MongoClient, ReadPreference
import json, urllib3, requests, httplib2

class notify:

    def get_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': '企业ID',
                  'corpsecret': '企业secret',
                  }
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        req = requests.post(url, params=values, verify=False)
        data = json.loads(req.text)
        return data["access_token"]

    def send_msg(self):
        print(self.addr, self.val)
        h = httplib2.Http('.cache')
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.get_token()
        user = "接收消息的用户"
        msg = "Server: %s ,Current Status: %s" % (self.addr, self.val)
        values = {
            "touser": "{}".format(user),
            "msgtype": "text",
            "agentid": "1000004",
            "text": {
                "content": msg
            }
        }
        response, content = h.request(url, 'POST', json.dumps(values), headers={'Content-Type': 'application/json'})

class mongo(notify):
    def __init__(self):
        conn = MongoClient('mongodb://用户名:密码@IP地址:端口/')
        db = conn.admin
        rs = db.command('replSetGetStatus')
        self.mongo={}
        for i in range(0,len(rs["members"])):
            self.ip=rs["members"][i]["name"]
            self.stat=rs["members"][i]["stateStr"]
            self.mongo[self.ip]=self.stat
        self.work()
    def work(self):
        print(self.mongo)
        for key  in self.mongo:
            if   (str(self.mongo[key]) == "PRIMARY" or str(self.mongo[key]) == "SECONDARY"):
                self.addr = key
                self.val = str(self.mongo[key])
                notify.send_msg(self)

if __name__ == '__main__':
    mongo()