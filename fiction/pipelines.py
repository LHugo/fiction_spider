# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi
import pymysql
import pymysql.cursors


class FictionPipeline(object):
    def process_item(self, item, spider):
        return item


class FictionImagesPipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if isinstance(item, dict) or "front_image_path" in item.fields:
            global image_file_path
            for ok, value in results:
                image_file_path = value["path"]
            item['front_image_path'] = image_file_path

        return item


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbpool = adbapi.ConnectionPool("pymysql", host=settings["MYSQL_HOST"], db=settings["MYSQL_DBNAME"],
                                       user=settings["MYSQL_USER"], passwd=settings["MYSQL_PASSWORD"], charset='utf8',
                                       cursorclass=pymysql.cursors.DictCursor, use_unicode=True)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql, items = item.get_insert_sql()
        cursor.execute(insert_sql, items)
