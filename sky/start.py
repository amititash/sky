'''
Entry point for the indexer infrastrcuture when list of individual URLS to be called instead of domain
'''

import os
import json
import pika 

# this dir needs to contain config files, one config file per url
directory = '/Users/titashneogi/workspace/sky/sky/sky/tmp_config/'


connection = pika.BlockingConnection(pika.URLParameters('amqp://titash:test123@54.175.53.47/paays_products_cj'))
channel = connection.channel()
channel.queue_declare(queue='crawl')

#code starts here 
def goCrawl(ch, method, properties, msg):
    item = msg.decode('utf8')
    item = json.loads(item)
    configname = item['sku']
    configfilename = directory+configname+".config.json"



    with open(configfilename, 'w') as outfile:
        print("writing to "+configfilename)
        try:
            json.dump(item, outfile)
            configname = item['sku']
            command = "python3 c2.py "+configfilename+" "+configname+" &"
            print("crawling...",command)
            os.system(command)
        except:
            print("Error with ", configfilename)

#Execution starts from here 
channel.basic_consume(goCrawl,
                      queue='crawl',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
