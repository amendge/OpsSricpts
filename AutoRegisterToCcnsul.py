#!/bin/python
#coding=utf-8
import requests
import json
import sys
import re
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


def alics_hn(ip):
	iplist=[]
	iplist.append(ip)
	client = AcsClient('xxxxxxx', 'xxxxxxxx','xxxxxxxx')   #your aliyun  accesskey
	request = CommonRequest()
	request.set_accept_format('json')
	request.set_domain('ecs.aliyuncs.com')
	request.set_method('POST')
	request.set_version('2014-05-26')
	request.set_action_name('DescribeInstances')

	request.add_query_param('RegionId', 'cn-beijing')
	request.add_query_param('InstanceNetworkType', 'vpc')
	request.add_query_param('PrivateIpAddresses', iplist)

	response = client.do_action_with_exception(request)
	json_dict = json.loads(response)
	return json_dict['Instances']['Instance'][0]['HostName']


def info_get():
	info = sys.argv
	#Alics_hn = alics_hn(info[1])
	compile_ip=re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
	if compile_ip.match(info[1]) or isinstance(info[2], int)  or info[3].strip()!='':
		Hname = get_hn(info[1])
		if Hname is None:
			print "HOSTNAME is None!"
			sys.exit()
		#if cmp(Hname,Alics_hn):
		http_put(info[1],info[2],info[3],hn=Hname)
		print info[1],info[2],info[3],Hname
	else:
		print "Please enter the correct format"
		sys.exit()

def http_put(*args,**kw):
	hpart =  (kw['hn'].split('-'))
	url="http://xxxxxxx:8500/v1/agent/service/register"   #your consul ip
        if hpart[2]:
                json_value={
                        "ID": args[2]+"-"+kw['hn'],
                        "Name": args[2],
                        "Address": args[0],
                        "tags": ["idc="+str(hpart[0]), "org="+hpart[1], "group="+hpart[2], "app="+hpart[3], "server="+kw['hn']],
                        "Port": int(args[1]),
                        "checks": [{
                                "tcp": args[0]+":"+args[1],
                                "interval": "60s"
                        }]
                   }
        else:
                json_value={
                        "ID": args[2]+"-"+kw['hn']+"-"+args[0],
                        "Name": args[2],
                        "Address": args[0],
                        "tags": [ "server="+kw['hn']],
                        "Port": int(args[1]),
                        "checks": [{
                                "tcp": args[0]+":"+args[1],
                                "interval": "60s"
                        }]
                   }
	data_to_send = json.dumps(json_value).encode("utf-8")
	try:
		r =requests.put(url,data_to_send,timeout=3)
	except:
		print "error"
	else:
		print r.text

def get_hn(IP):
        
		url='''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''%(IP)   ##from  your  cmdb  get hostname
        headers = { 'Authorization': 'Token xxxxxxxxxxx'}
        s = requests.get(url,headers=headers)
        json_dict = json.loads(s.text)
        for item in json_dict['data']['items']:
                return item['name']
def auto_deregister(Sname):
	nodelist = ['xxxxxx']  #your consul  ip for auto_deregister
	for ip in nodelist:
		print ip
		url='''http://%s:8500/v1/agent/service/deregister/%s'''%(ip,Sname)
		r =requests.put(url)
		print r.text

if __name__ == "__main__":
	compile_ip=re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
	if compile_ip.match(sys.argv[1]):
		info_get()
	else:
		auto_deregister(sys.argv[1])