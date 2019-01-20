#!/usr/bin/env python3

# --------- 1. Setup      ----------------------------------------------
PROJECT_NAME = 'sophonone'
import os, base64, re, logging
from elasticsearch import Elasticsearch

from sky.crawler_services import CrawlElasticSearchService
from sky.crawler_plugins import CrawlElasticSearchPluginNews

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

# Instantiate the new Elasticsearch connection:
es = Elasticsearch(es_header)

'''
es = Elasticsearch([{'host': '886f099c.ngrok.io', 'port': 80}])

# Instantiate the new Elasticsearch connection:

cs = CrawlElasticSearchService(PROJECT_NAME, es, CrawlElasticSearchPluginNews)

# --------- 4. Start crawling      --------------------------------------
from sky.configs import PRODUCTION_CRAWL_CONFIG

default = cs.get_crawl_plugin('default')
default.save_config(PRODUCTION_CRAWL_CONFIG)



one_config = {
    "seed_urls": ["http://www.jdoqocy.com/click-8826556-12528200-1546737648636?url=https%3A%2F%2Fwww.tourradar.com%2Ft%2F142199&cjsku=142199", "http://www.jdoqocy.com/click-8826556-12528200-1546737648636?url=https%3A%2F%2Fwww.tourradar.com%2Ft%2F142308&cjsku=142308", "http://www.jdoqocy.com/click-8826556-12528200-1546737648609?url=https%3A%2F%2Fwww.tourradar.com%2Ft%2F142512&cjsku=142512"],
    "crawl_required_regexps": [],
    "crawl_filter_regexps": [],
    "index_required_regexps": [],
    "max_workers": 2,
    "max_saved_responses": 5
}


four = cs['testcrawl']
four.save_config(one_config)
four.run()