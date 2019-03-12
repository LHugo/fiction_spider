# -*- coding: utf-8 -*-
import scrapy
from fiction.settings import PAGE_MAX_NUM
from fiction.items import FictionDetails, FictionContent
from scrapy.loader import ItemLoader
from urllib.parse import urljoin
import re
from scrapy_redis.spiders import RedisSpider


class FictionCrawlSpider(RedisSpider):
    name = 'fiction_crawl'
    allowed_domains = ['xs.sogou.com']
    redis_key = 'fiction_crawl:start_urls'
    # start_urls = ['https://xs.sogou.com/0_0_1_0_heat/?pageNo=1']

    def parse(self, response):
        for i in range(2, PAGE_MAX_NUM+1):
            book_nodes = response.xpath("//ul[@class='filter-ret clear']/li")
            for book_node in book_nodes:
                front_image_url = urljoin('https:', book_node.xpath(".//img/@src").extract()[0])
                fiction_id = re.match('^/book/(\\d+)/$', book_node.xpath("./a/@href").extract()[0]).group(1)
                fiction_detail_url = "https://xs.sogou.com/book/{}/".format(fiction_id)
                fiction_chapter_url = "https://xs.sogou.com/list/{}/".format(fiction_id)
                yield scrapy.Request(url=fiction_detail_url,
                                     meta={"front_image_url": front_image_url, "fiction_id": fiction_id},
                                     callback=self.parse_fiction_details)
                yield scrapy.Request(url=fiction_chapter_url, meta={"fiction_id": fiction_id},
                                     callback=self.parse_chapter_url)
            next_url = 'https://xs.sogou.com/0_0_1_0_heat/?pageNo={0}'.format(i)
            yield scrapy.Request(url=next_url, callback=self.parse)

    def parse_fiction_details(self, response):
        fiction_details_item_loader = ItemLoader(item=FictionDetails(), response=response)
        fiction_details_item_loader.add_value("fiction_id", [response.meta.get("fiction_id")])
        fiction_details_item_loader.add_value("fiction_url", response.url)
        fiction_details_item_loader.add_xpath("fiction_name", "//h1[@class='text-title']//text()")
        fiction_details_item_loader.add_xpath("author", "//div[@class='field clear']/span[1]/text()")
        fiction_details_item_loader.add_xpath("fiction_tag", "//div[@class='field clear']/span[2]/a/text()")
        fiction_details_item_loader.add_xpath("fiction_state", "//div[@class='field clear']/span[3]/a/text()")
        fiction_details_item_loader.add_xpath("words_num", "//div[@class='field clear']/span[4]/text()")
        fiction_details_item_loader.add_xpath("fiction_origin", "//div[@class='field clear']/span[5]/text()")
        if 'desc desc-long hide' in response.text:
            fiction_details_item_loader.add_xpath("fiction_abstract", "//div[@class='desc desc-long hide']//text()")
        else:
            fiction_details_item_loader.add_xpath("fiction_abstract", "//div[@class='desc desc-short']//text()")
        fiction_details_item_loader.add_value("front_image_url", [response.meta.get("front_image_url", "")])

        fiction_details = fiction_details_item_loader.load_item()
        yield fiction_details

    def parse_chapter_url(self, response):
        urls = response.xpath("//div[@class='chapter-box']//a/@href").extract()
        for url in urls:
            chapter_url = urljoin("https://xs.sogou.com", url)
            yield scrapy.Request(url=chapter_url, meta={"fiction_id": response.meta.get("fiction_id")},
                                 callback=self.parse_chapter_content)

    def parse_chapter_content(self, response):
        chapter_id = re.match('.*_(\\d+)/', response.url).group(1)
        fiction_content_item_loader = ItemLoader(item=FictionContent(), response=response)
        fiction_content_item_loader.add_value("fiction_id", [response.meta.get("fiction_id")])
        fiction_content_item_loader.add_value("chapter_id", [chapter_id])
        fiction_content_item_loader.add_xpath("chapter_update_time", "//div[@class='info']/text()")
        fiction_content_item_loader.add_xpath("chapter_num", "//div[@class='info']//text()")
        fiction_content_item_loader.add_xpath("chapter_name", "//div[@class='paper-box paper-article']//h1/text()")
        fiction_content_item_loader.add_xpath("chapter_content", "//div[@id='contentWp']//text()")

        fiction_content = fiction_content_item_loader.load_item()
        yield fiction_content

