# coding=utf-8
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from social_scrapper.items import OpportunityItem
import re
import string


class MecenovaSpider(BaseSpider):
    name = 'mecenova.org'
    allowed_domains = ['mecenova.org']
    prefix = 'http://www.mecenova.org/'

    def start_requests(self):
        start_url = 'http://www.mecenova.org/associations-projets.php'
        return [Request(start_url, callback=self.parse_result_page)]

    def parse_result_page(self, response):
        reqs = []
        hxs = HtmlXPathSelector(response)

        # Find items
        project_nodes = hxs.select('//div[@class="item"]')
        for node in project_nodes:
            relative_url = node.select('p/a[1]/@href').extract()[0]
            absolute_url = self.prefix + relative_url
            reqs.append(Request(absolute_url, self.parse_opportunity))

        # Find possible next page
        next_page_node = hxs.select(
            '//div[@class="pagination"]/a[@title="Suivant"]/@href')
        if next_page_node:
            relative_url = next_page_node.extract()[0]
            absolute_url = self.prefix + relative_url
            reqs.append(Request(absolute_url, callback=self.parse_result_page))

        return reqs

    def parse_opportunity(self, response):
        item = OpportunityItem()
        hxs = HtmlXPathSelector(response)

        item['feed'] = self.name
        item['uri'] = response.url

        node = hxs.select('//div[@class="fiche"]/div[3]')
        item['title'] = node.select('h1[1]').extract()[0]
        item['client'] = node.select('h3[1]/a/text()').extract()[0]
        item['website'] = self.prefix
        item['website'] += node.select('h3[1]/a/@href').extract()[0]
        item['description'] = node.select(
            'p[contains(./strong, "Objectif")]/text()').extract()[0]
        additional = string.join(
            node.select('ul[@id="champsAsso"]/li/text()').extract(), '\n')
        item['description'] += '\n' + additional
        item['location'] = node.select(
            'p[contains(./strong, "Lieu")]/text()').extract()[0]
        # TODO: Parse location a little more
        item['target'] = node.select(
            'p[contains(./strong, "Public")]/text()').extract()[0]
        start_date_node = node.select(
            'p[contains(./strong, "Début")]/text()')
        if start_date_node:
            start_date = start_date_node.extract()[0]
            res = re.search(r'(\d{2})/(\d{4})$', start_date)
            self.log('\n{' + start_date + '}\n')
            (item['start_date_month'], item['start_date_year']) = res.groups()
        end_date_node = node.select(
            'p[contains(./strong, "Fin")]/text()')
        if end_date_node:
            end_date = end_date_node.extract()[0]
            res = re.search(r'(\d{2})/(\d{4})$', end_date)
            (item['end_date_month'], item['end_date_year']) = res.groups()
        item['type'] = node.select(
            'p[contains(./strong, "Type")]/text()').extract()[0]
        # TODO: Parse type a little more
        return item
