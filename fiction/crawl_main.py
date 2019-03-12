import os
import sys
from scrapy.cmdline import execute
import redis

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy', 'crawl', 'fiction_crawl'])
r = redis.Redis(host='127.0.0.1', port=6379)
r.lpush("fiction_crawl:start_urls", "https://xs.sogou.com/0_0_1_0_heat/?pageNo=1")

