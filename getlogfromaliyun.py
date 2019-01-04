# encoding: utf-8
import re
import time
import json
import datetime
from aliyun.log import *
from prometheus_client import CollectorRegistry, push_to_gateway, Gauge, write_to_textfile

endpoint = ''       # 选择与上面步骤创建Project所属区域匹配的Endpoint
accessKeyId = ''    # 使用你的阿里云访问密钥AccessKeyId
accessKey = ''      # 使用你的阿里云访问密钥AccessKeySecret
project = 'api-c'        # 上面步骤创建的项目名称
logstore = ''       # 上面步骤创建的日志库名称

#Now = datetime.datetime.today() - datetime.timedelta(hours=8)
Now = datetime.datetime.today()
Start =  Now - datetime.timedelta(minutes=1)
End =  Now
#End = Now - datetime.timedelta(minutes=5)

StartTime = datetime.datetime.strftime(Start, '%Y-%m-%d %H:%M:00')
EndTime = datetime.datetime.strftime(End, '%Y-%m-%d %H:%M:00')


client = LogClient(endpoint, accessKeyId, accessKey)

def get_project_log(client,project,logstore):
    req = GetProjectLogsRequest(project,"select split_part(request_uri,'?',1) as q,status as s , count(1) as pv ,server_name as sn from %s where __date__ >= '%s' and __date__ < '%s' group by q,s,sn order by pv  " %(logstore,StartTime,EndTime));
    res = client.get_project_logs(req)
    logs = res.get_logs();
    return logs

def push_prom():
	registry = CollectorRegistry()
	g = Gauge('cdn_endpoint_url', 'cdnurl', ['host','status','url','server_name'], registry=registry)

	logs = get_project_log(client,project,logstore)
	for log in logs:
	    contents = [];
	    for (k,v) in log.get_contents().items():
	        contents.append({k:v})
	    info_dict = {};
	    for content in contents:
	            info_dict = dict(info_dict,**content)
	    uri=info_dict['q']
	    status=info_dict['s']
	    value=info_dict['pv']
	    sn=info_dict['sn']
	    g.labels('your_Lables',status,uri,sn).set(value)

	push_to_gateway('your_Push_ip:9091', job='your_Jobs', registry=registry)
push_prom()