# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import datetime


class FictionDetails(scrapy.Item):
    fiction_id = scrapy.Field()
    fiction_url = scrapy.Field()
    fiction_name = scrapy.Field()
    author = scrapy.Field()
    fiction_tag = scrapy.Field()
    fiction_state = scrapy.Field()
    words_num = scrapy.Field()
    fiction_origin = scrapy.Field()
    fiction_abstract = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                    insert into fiction_details(fiction_id, fiction_url, fiction_name, author, fiction_tag, 
                    fiction_state, words_num, fiction_origin, fiction_abstract, front_image_url, crawl_time)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE fiction_state=VALUES(fiction_state),words_num=VALUES(words_num),
                                            crawl_time=VALUES(crawl_time)          
                """
        fiction_id = self["fiction_id"][0]
        fiction_url = "".join(self["fiction_url"])
        fiction_name = "".join(self["fiction_name"])
        author = re.match('.*：(.*)', "".join(self["author"])).group(1)
        fiction_tag = "".join(self["fiction_tag"])
        fiction_state = "".join(self["fiction_state"])
        words_num = re.match('字数：(.*万)', "".join(self["words_num"])).group(1).replace("\r\n", "").strip()
        fiction_origin = re.match('.*：(.*)', "".join(self["fiction_origin"])).group(1)
        fiction_abstract = self["fiction_abstract"][0].replace("\r\n", "").strip()
        front_image_url = "".join(self["front_image_url"])
        crawl_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        items = (fiction_id, fiction_url, fiction_name, author, fiction_tag, fiction_state, words_num, fiction_origin,
                 fiction_abstract, front_image_url, crawl_time)
        return insert_sql, items


class FictionContent(scrapy.Item):
    fiction_id = scrapy.Field()
    fiction_name = scrapy.Field()
    chapter_id = scrapy.Field()
    chapter_update_time = scrapy.Field()
    chapter_num = scrapy.Field()
    chapter_name = scrapy.Field()
    chapter_content = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                    insert into fiction_content(fiction_id, fiction_name, chapter_id, chapter_update_time, chapter_num, 
                    chapter_name, chapter_content, crawl_time)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE crawl_time=VALUES(crawl_time),chapter_content=VALUES(chapter_content)       
                """
        fiction_id = self["fiction_id"][0]
        fiction_name = self["fiction_name"][0]
        chapter_id = self["chapter_id"][0]
        chapter_update_time = re.match('.*更新时间：(.*)', self["chapter_update_time"][0], re.S).group(1)
        chapter_num = int(re.match('.*字数：(\\d+).*', "".join(self["chapter_num"]), re.S).group(1))
        chapter_name = self["chapter_name"][0]
        chapter_content = "".join(self["chapter_content"]).replace("\r\n", "").strip()
        crawl_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        items = (fiction_id, fiction_name, chapter_id, chapter_update_time, chapter_num, chapter_name, chapter_content,
                 crawl_time)

        return insert_sql, items
