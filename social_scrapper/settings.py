# Scrapy settings for social_scrapper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
# Or you can copy and paste them from where they're defined in Scrapy:
# 
#     scrapy/conf/default_settings.py
#

BOT_NAME = 'social_scrapper'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['social_scrapper.spiders']
NEWSPIDER_MODULE = 'social_scrapper.spiders'
DEFAULT_ITEM_CLASS = 'social_scrapper.items.ScrapperItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

