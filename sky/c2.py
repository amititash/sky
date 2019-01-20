#!/usr/bin/env python3

# --------- 1. Setup      ----------------------------------------------
PROJECT_NAME = 'sophonone'
import os, base64, re, logging
from elasticsearch import Elasticsearch

from sky.crawler_services import CrawlElasticSearchService
from sky.crawler_plugins import CrawlElasticSearchPluginNews

import json, sys

from sky.crawler_services import CrawlFileService
from sky.crawler_plugins import CrawlFilePluginNews

storage_object = {'path': '/Users/titashneogi/workspace/sky/sky/sky/crawl-data'}

cs = CrawlFileService(PROJECT_NAME, storage_object, CrawlFilePluginNews)




# --------- 4. Start crawling      --------------------------------------
from sky.configs import PRODUCTION_CRAWL_CONFIG

default = cs.get_crawl_plugin('default')
default.save_config(PRODUCTION_CRAWL_CONFIG)
 

fullpath = sys.argv[1]
configname = sys.argv[2]
print("crawling...",fullpath)


with open(fullpath, 'r') as f:
  print(type(f))
  one_config = json.load(f)
  print(one_config)
  four = cs[configname]
  four.save_config(one_config)
  four.run()