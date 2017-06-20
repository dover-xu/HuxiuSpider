# -*- coding: utf-8 -*-
from coolscrapy.items import ZhihuItem
import scrapy
from scrapy.http import FormRequest
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import chardet
from lxml import etree
import json
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

class HuxiuSpider(CrawlSpider):
    name = "zhihu"
    allowed_domains = ["zhihu.com"]
    start_urls = [
        "https://www.zhihu.com/people/kaifulee/followers?page=1"
    ]
    custom_settings = {
       "DEFAULT_REQUEST_HEADERS":{
            'Accept':'application/json',
            'Content-Type':'application/json; charset=UTF-8',
            'Host':'www.zhihu.com'
         },
         "ITEM_PIPELINES":{
             'zhihu.pipelines.ZhihuUsersPipeline': 5,
         }
    } 
    # rules = (
        # Rule(LinkExtractor(allow=(r'/article/\d+.html',)), callback='parse_item', follow=True),
    # )
    def __init__(self, name=None, **kwargs):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)
        self.__dict__.update(kwargs)
        self.page = 1

    def parse_item(self, response):
        detail = response.xpath('//div[@class="article-wrap"]')
        item = HuxiuItem()
        item['link'] = response.url
        item['image_url'] = detail.xpath('div[@class="article-img-box"]/img/@src').extract_first()
        item['title'] = detail.xpath('h1/text()').extract_first()
        item['posttime'] = detail.xpath('div[@class="article-author"]/div[@class="column-link-box"]/span[@class="article-time pull-left"]/text()').extract_first()
        yield item
        
    def parse(self, response):
        urls = response.xpath('//div[@class="mod-b mod-art "]/div[@class="mob-ctt"]/h2/a/@href').extract()
        urls.extend(response.xpath('//div[@class="big-pic-box"]/div/a[1]/@href').extract())
        for url in urls:
            url = 'http://www.huxiu.com/' + url
            yield scrapy.Request(url, callback=self.parse_item)
        page = int(response.xpath('//div[contains(@class,"get-mod-more")]/@data-cur_page').extract_first())
        last_dateline = response.xpath('//div[contains(@class,"get-mod-more")]/@data-last_dateline').extract_first()
        form_data = {
            "huxiu_hash_code":"0e1e40750459c832aad85fdc611a8349",
            "page":str(page+1),
            "last_dateline":last_dateline
        }
        url = "https://www.huxiu.com/v2_action/article_list"
        yield FormRequest(url,callback=self.parse_more,formdata=form_data,dont_filter=True)
        # item = HuxiuItem()
        # item['link'] = article_list.xpath('div[1]/div[@class="mob-ctt"]/h2/a/@href').extract()
        # item['image_url'] = detail.xpath('div[1]/div[@class="mob-thumb"]/a/img/@src').extract()
        # item['title'] = detail.xpath('div[1]/div[@class="mob-ctt"]/h2/a/text()').extract_first()
        # item['posttime'] = detail.xpath('div[@class="article-author"]/div[@class="column-link-box"]/span[@class="article-time pull-left"]/text()').extract_first()
    def parse_more(self, response):
        dict_data = json.loads(response.body)
        last_dateline = dict_data['last_dateline']
        data = dict_data['data']
        tree = etree.HTML(data)
        urls = tree.xpath('//div[@class="mod-b mod-art"]/div[@class="mob-ctt"]/h2/a/@href')
        for url in urls:
            url = 'http://www.huxiu.com/' + url
            yield scrapy.Request(url, callback=self.parse_item)
        if self.page >= 1:
            yield None
        else:
            self.page = self.page+1
            form_data = {
                "huxiu_hash_code":"0e1e40750459c832aad85fdc611a8349",
                "page":str(self.page),
                "last_dateline":last_dateline
            }
            url = "https://www.huxiu.com/v2_action/article_list"
            yield FormRequest(url,callback=self.parse_more,formdata=form_data,dont_filter=True)