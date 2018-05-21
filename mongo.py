from pymongo import MongoClient, ReadPreference
import json, urllib3, requests, httplib2, socket, os

class notify:

    def get_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': '企业ID',
                  'corpsecret': '企业密码',
                  }
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        req = requests.post(url, params=values, verify=False)
        data = json.loads(req.text)
        return data["access_token"]

    def send_msg(self):
        h = httplib2.Http('.cache')
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.get_token()
        user = "zhangming"
        #msg = "Server: %s ,Current Status: %s" % (self.addr, self.val)
        values = {
            "touser": "{}".format(user),
            "msgtype": "text",
            "agentid": "代理ID",
            "text": {
                "content": self.msg
            }
        }
        response, content = h.request(url, 'POST', json.dumps(values), headers={'Content-Type': 'application/json'})

class mongo(notify):
    def __init__(self):
        try:
            sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sc.settimeout(2)
            sc.connect(("192.168.0.159", 27010))
            sc.close()
        except:
            self.msg = "server: .159, service: mongodb  is down"
            notify.send_msg(self)
            os._exit()

        conn = MongoClient('mongodb://jerry:jerry@192.168.0.159:27010/')
        db = conn.admin
        rs = db.command('replSetGetStatus')
        self.mongo={}
        for i in range(0,len(rs["members"])):
            self.ip=rs["members"][i]["name"]
            self.stat=rs["members"][i]["stateStr"]
            self.mongo[self.ip]=self.stat
        self.work()

    def work(self):
        for key  in self.mongo:
            if not (str(self.mongo[key]) == "PRIMARY" or str(self.mongo[key]) == "SECONDARY"):
                addr = key
                val = str(self.mongo[key])
                self.msg = "Server: %s ,Current Status: %s" % (addr, val)
                notify.send_msg(self)

if __name__ == '__main__':
    mongo()