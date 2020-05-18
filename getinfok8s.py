# -*- coding: utf-8 -*-
import json
import requests
import sys,os
import time, datetime
from urllib.parse import urlencode
import time
import records

class K8spodinfo(object):
    def __init__(self):
        self.url = "http://thanos:xxx/api/v1/query_range?"
        self.interval = '60'
        self.timefilter()
        self.file = 'getk8sinfo.txt'


    def timefilter(self):
        Today = datetime.datetime.today()
        Yesterday = Today - datetime.timedelta(days=1)
        starttime =  datetime.datetime.strftime(Yesterday, '%Y-%m-%d 19:00:00')
        endtime = datetime.datetime.strftime(Yesterday, '%Y-%m-%d 22:00:00')
        start_timestamp = time.mktime(time.strptime(starttime, '%Y-%m-%d %H:%M:%S'))
        end_timestamp = time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S'))
        self.start_timestamp = start_timestamp
        self.end_timestamp =  end_timestamp

    def acess_get_info(self,query):
        url_arg = 'query={query}&start={start_timestamp}&end={end_timestamp}&step={interval}'.format(
            query=query, start_timestamp=self.start_timestamp,end_timestamp=self.end_timestamp,interval=self.interval)
        url = self.url + url_arg
        print (url)
        response = requests.get(url=url)
        text = response.text
        data = json.loads(text)['data']['result']
        return data

    def Write_Text(self,contant):
        file_name = self.file
        with open(file_name,"a+") as f:
            f.writelines(contant)
            f.writelines("\n")

    def filter_service_name(self,data):
        host_list = []
        service_name = []
        for host in data:
            try:
                if (host['metric']['host_ip'] not in host_list):
                    host_list.append(host['metric']['host_ip'])
            except:
                pass
        #host_list = ['172.21.161.11']
        for i in host_list:
            for d in data:
                try:
                    if (i == d['metric']['host_ip']):
                        if (d['metric']['created_by_name'] not in service_name):
                            service_name.append(d['metric']['created_by_name'])
                        line =  '''{host} {sname} {num}'''.format(
                                 host=i,sname=d['metric']['created_by_name'],num=d['values'][0][1])
                        print (line)
                        self.Write_Text(line)
                        #导出机器部署服务至csv
                except:
                    pass
        return service_name

    def filter_item_info(self,item,service_name):
        #for item in items:
        if item == 'container_memory_working_set_bytes':
            get_item_query ='''sum(%s{monitor="监控标签",namespace=~"default",pod_name=~"%s-.*"})/(count (%s{monitor="监控标签",name!~"k8s_POD.*|k8s_filebeat_dispatch.*",namespace=~"default",pod_name=~"%s-.*"}))'''%(item,service_name,item,service_name)
        else:
            get_item_query ='''sum(rate(%s{monitor="监控标签",namespace=~"default",pod_name=~"%s.*"}[1m]))'''%(item,service_name)
        request_data = self.acess_get_info(get_item_query)
        return self.filter_service_item_data(item,request_data)

    def filter_service_item_data(self,itype,data):
        data_list = []
        for res in data[0]['values']:
             data_list.append(float(res[1]))
        average=lambda a:sum(a)/len(a)
        y=[x for x in data_list]
        avg_data=average(y)
        if itype == 'container_cpu_usage_seconds_total':          #单位换算
            result = float(round(avg_data , 5))
        elif itype =='container_memory_working_set_bytes':
            result = float(round(avg_data / 1024 / 1024 , 2))
            #result = int(round(avg_data / 1024 / 1024, 2)) + ' MB'
        elif itype =='container_network_receive_bytes_total':
            #result = str(float(round(avg_data / 1024 / 1024 , 2))) + 'Mb'
            result = float(round(avg_data / 1024 / 1024 , 2))
        return result


def main():
    get_service_query = 'sum(kube_pod_info{monitor="监控标签",created_by_name!~".*gray.*",namespace=~"default"})by(host_ip,created_by_name)'
    items = ['container_cpu_usage_seconds_total','container_memory_working_set_bytes','container_network_receive_bytes_total']
    info = K8spodinfo()
    #s_item_data = info.filter_item_info(items)
    s_data = info.acess_get_info(get_service_query)  #获取服务名称
    s_name = info.filter_service_name(s_data)
    for sname in s_name:
        #for item in items:
        cpu_data = info.filter_item_info(items[0],sname)
        mem_data = info.filter_item_info(items[1],sname)
        net_data = info.filter_item_info(items[2],sname)
            #item_data = info.filter_item_info(item,sname)
        line =  '''{sname}\t{cpu}\t{mem}'''.format(
                sname=sname,cpu=cpu_data,mem=mem_data)
        print (line)
        info.Write_Text(line)
    time.sleep(3)
      

if __name__ == '__main__':
    main()

