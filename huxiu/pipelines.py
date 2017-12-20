# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import json
import urllib2
import pymongo
from scrapy.conf import settings
from scrapy import log
from scrapy.exceptions import DropItem
from gridfs import *
import os

class CoolscrapyPipeline(object):
    def process_item(self, item, spider):
        return item

class ArticleDataBasePipeline(object):
    def __init__(self):
        client = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = client[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]
        # self.fs = GridFS(db, settings.MONGODB_IMAGES_COLLECTION)
        
    def open_spider(self, spider):
        pass
        
    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}".format(data))
        if valid:        
            
            image_url = item['image_url'] if item['image_url'] else ''
            if image_url:
                dir = settings['IMAGES_DIR']
                if not os.path.exists(dir):
                    os.makedirs(dir)
                url_split = image_url.split('?')[0].split('/')[3:]
                filename = '_'.join(url_split)
                filepath = '%s/%s' % (dir, filename)
                if os.path.exists(filepath):
                    return item
                try:
                    with open(filepath, 'wb') as file:
                        response = urllib2.urlopen(image_url)
                        file.write(response.read())
                except Exception as reason:
                    log.msg("Save image error: {0}".format(reason), level=log.ERROR, spider=spider)
                else:
                    log.msg("Download image to MongoDB database!", level=log.DEBUG, spider=spider)
                    if filepath:
                        item['image_local_path'] = filepath
                        self.collection.insert(dict(item))
                        log.msg("Article added to MongoDB database!", level=log.DEBUG, spider=spider)
        return item
        
    def close_spider(self, spider):
        pass