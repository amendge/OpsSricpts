# -*- coding: utf-8 -*-
import ConfigParser
import json
import urllib2

class ZabbixAPI:
    def __init__(self):
        cf = ConfigParser.ConfigParser()
        cf.read("./config.ini")
        self.__url = cf.get("zabbix_server","url")
        self.__user= cf.get("zabbix_server","user")
        self.__password = cf.get("zabbix_server","password")
        self.__header = {"Content-Type": "application/json-rpc"}
        self.__token_id = self.UserLogin()
    #登陆获取token
    def UserLogin(self):
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.__user,
                "password": self.__password
            },
            "id": 0,
        }
        return self.PostRequest(data)
    #推送请求
    def PostRequest(self, data):
        request = urllib2.Request(self.__url,json.dumps(data),self.__header)
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        try:
            # print response['result']
            return response['result']
        except KeyError:
            raise KeyError
    #主机列表
    def HostGet(self,hostid=None,hostip=None):
        data = {
            "jsonrpc":"2.0",
            "method":"host.get",
            "params":{
                "output":"extend",
                "selectGroups": "extend",
                #"selectParentTemplates": ["templateid","name"],
                #"selectInterfaces": ["interfaceid","ip"],
                #"selectInventory": ["os"],
                #"selectItems":["itemid","name"],
                #"selectGraphs":["graphid","name"],
                #"selectApplications":["applicationid","name"],
                #"selectTriggers":["triggerid","name"],
                #"selectScreens":["screenid","name"]
            },
            "auth": self.__token_id,
            "id":1,
        }
        if hostid:
            data["params"]={
                "output": "extend",
                "hostids": hostid,
                "sortfield": "name"
            }
        return  self.PostRequest(data)

    def HostGroupGet(self,hostid=None,itemid=None):
        data = {
            "jsonrpc":"2.0",
            "method":"hostgroup.get",
            "params":{
                "output": "extend",
                "hostids": hostid,
                "itemids": itemid,
                "sortfield": "name"
            },
            "auth": self.__token_id,
            "id":1,
        }
        return  self.PostRequest(data)

def main():
    data = {}
    data_List = []
    zapi=ZabbixAPI()
    token=zapi.UserLogin()
    hosts=zapi.HostGet()
    print hosts
    for host in hosts:
        status =  host['available']
        hostname =  host['host']
        host_id = host['hostid']
        group_data = zapi.HostGroupGet(hostid=host_id)
        hostgroup = [x['name'] for x in group_data]
        data['status'] = status
        data['hostname'] = hostname
        data['hostgroup']= hostgroup
        data_List.append(data) 
    print (data_List)

    #zapi=ZabbixAPI()
    #token=zapi.UserLogin()
    #print token
    ##39378ec03aa101c2b17d1d2bd6f4ef16
    #hosts=zapi.HostGet()
    #for host in hosts:
    #    monitor_status =  host['available']
    #    host_name =  host['host']
    #    host_id = host['hostid']
    #    group_data = zapi.HostGroupGet(hostid='10581')
    #    group_list = [x['name'] for x in group_data]
    #    #for group in group_data:
    #    #    group_list.append(group['name'])
    #    print (monitor_status,host_name,group_list) 
    #[{u'host': u'Zabbix server', u'hostid': u'10084', u'interfaces': [{u'interfaceid': u'1', u'ip': u'127.0.0.1'}]}]




if __name__ == '__main__':
    main()
