import datetime
from elasticsearch import Elasticsearch
import time
import json

online_url = "http://elasticsearch:9200/"
test_url = "http://elasticsearch:9200/"

index_name = "access-XXXXX-2020.05.14"
doc_type = "_doc"
batch_size = 5000
max_size = 10000
me = list()
es = Elasticsearch(online_url, timeout = 120)

body = {
    "query":{
        "bool":{
            "must":[
              { "match":{"params_method":"query"} } 
            ],
            "filter":[
              {"range":{"@timestamp":{"gte":"1589440511000","lte":"1589441111000"}}}
            ]
        }
    }
}
#body = {
#    "query":{
#        "bool":{
#            "must":[
#              { "match_all":{} } 
#            ],
#            "filter":[
#              {"range":{"@timestamp":{"gte":1584921624000,"lte":1584921924000}}}
#            ]
#        }
#    }
#}



return_fields = [
    '_scroll_id',
    'hits.hits',
    'hits.total'
]


#控制输出字段到文件
def process(data):
    for item in data:
        #print (item["_source"]["message"])
        with open('data.json','a+') as f:
            f.write(item["_source"]["message"]+'\n')


# 第一次查询的数据
page = es.search(
    index = index_name,
    scroll = "5m",
    size = batch_size,
    body = body,
    filter_path = return_fields
)
process(page["hits"]["hits"])

sid = page["_scroll_id"]
scroll_size = page["hits"]["total"]
process_bar = 0

while(scroll_size > 0):
    print("scrolling.. %d" % process_bar)
    time.sleep(0.05)
    page = es.scroll(scroll_id= sid, scroll = "1m", filter_path = return_fields)
    process(page["hits"]["hits"])
    sid = page["_scroll_id"]
    scroll_size = len(page["hits"]["hits"])
    process_bar = process_bar + scroll_size
    if process_bar >= max_size:
        print("end...")
        break

#with open('data.json','w') as f:
#    f.write('\n')
#    json.dump(me, f)
