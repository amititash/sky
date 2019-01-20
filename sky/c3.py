#!/usr/bin/env python3

# --------- 1. Setup      ----------------------------------------------
PROJECT_NAME = 'sophonone'
import os, base64, re, logging
from elasticsearch import Elasticsearch

from sky.crawler_services import CrawlElasticSearchService
from sky.crawler_plugins import CrawlElasticSearchPluginNews

import json, sys
import json
import pika 

'''
# Parse the auth and host from env:
bonsai = 'https://5bgygw52r4:637c8qay66@cj-test-9194042377.us-west-2.bonsaisearch.net' #os.environ['BONSAI_URL']
auth = re.search('https\:\/\/(.*)\@', bonsai).group(1).split(':')
host = bonsai.replace('https://%s:%s@' % (auth[0], auth[1]), '')

# Connect to cluster over SSL using auth for best security:
es_header = [{
  'host': host,
  'port': 443,
  'use_ssl': True,
  'http_auth': (auth[0],auth[1])
}]

es = Elasticsearch(es_header)
'''
es = Elasticsearch([{'host': '886f099c.ngrok.io', 'port': 80}])

# Instantiate the new Elasticsearch connection:

cs = CrawlElasticSearchService(PROJECT_NAME, es, CrawlElasticSearchPluginNews)


connection = pika.BlockingConnection(pika.URLParameters('amqp://titash:test123@54.175.53.47/paays_products_cj'))
channel = connection.channel()
channel.queue_declare(queue='crawl')

#code starts here 
def goCrawl(ch, method, properties, msg):
    item = msg.decode('utf8')
    item = json.loads(item)

    print(item)

    #es = Elasticsearch([{'host': '886f099c.ngrok.io', 'port': 80}])
    # Instantiate the new Elasticsearch connection:
    #cs = CrawlElasticSearchService(PROJECT_NAME, es, CrawlElasticSearchPluginNews)

    # --------- 4. Start crawling      --------------------------------------
    #from sky.configs import PRODUCTION_CRAWL_CONFIG
    #default = cs.get_crawl_plugin('default')
    #default.save_config(PRODUCTION_CRAWL_CONFIG)

    print("****crawling...",item["sku"])
    #one_config = json.load(item)
    #configname = item['sku']
    four = cs['testcrawl']
    four.save_config(item)
    four.run()
    
    


#Execution starts from here 
channel.basic_consume(goCrawl,
                      queue='crawl',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()