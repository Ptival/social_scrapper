# coding=utf-8
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from social_scrapper.items import OpportunityItem
import re

category_dict = {
    'culture et loisirs': 'culture',
    u'développement international et aide humanitaire': 'humanitaire',
    u'éducation pour tous': 'éducation',
    'environnement': 'environnement',
    "interventions d'urgence en cas de crise": 'crise',
    u'mémoire et citoyenneté': u'citoyenneté',
    u'santé': u'santé',
    u'solidarité': u'solidarité',
    'sport': 'sport'
}

class ServiceCiviqueSpider(BaseSpider):
    name = 'service-civique.gouv.fr'
    allowed_domains = ['service-civique.gouv.fr']
    prefix = 'http://www.service-civique.gouv.fr'

    def start_requests(self):
        start_url = 'http://www.service-civique.gouv.fr/les_missions?date_filter[value][date]=&tid=All&tid_1=16&tid_2=All&tid_3=All&regions=All&dept=All&r=0&d=0'
        return [Request(start_url, callback=self.parse_result_page)]

    def parse_result_page(self, response):
        reqs = []
        hxs = HtmlXPathSelector(response)
        mission_nodes = hxs.select('//div[@id="resultat_mission"]')
        for node in mission_nodes:
            category = node.select('div[@class="thematique"]/p/text()').extract()
            # Sometimes they forget the category...
            if category:
                category = category[0]
            # Normalize categories (FIXME: categories need to be formalized)
                category = category_dict[category]
            # Sometimes, there is no link (bug from their side), then we can't proceed
            relative_url = node.select('div[@class="voir_mission"]/div/a/@href').extract()
            if relative_url:
                relative_url = relative_url[0]
            else:
                continue
            absolute_url = self.prefix + relative_url
            reqs.append(Request(absolute_url,
                                callback=lambda r: self.parse_opportunity(r, category)))

        next_page_node = hxs.select('//li[@class="pager-next"]')
        if next_page_node:
            self.log('SERVICE_CIVIQUE: Found a next page')
            relative_url = next_page_node.select('a/@href').extract()[0]
            absolute_url = self.prefix + relative_url
            reqs.append(Request(absolute_url, callback=self.parse_result_page))
        return reqs

    def parse_opportunity(self, response, category):
        item = OpportunityItem()
        hxs = HtmlXPathSelector(response)
        node = hxs.select('//div[@id="page-mission"]')
        item['feed'] = self.name
        item['title'] = node.select('//div[@class="top-titre"]//p/text()').extract()[0]
        item['uri'] = response.url

        mission = node.select('//div[@class="center-text"]')
        dates = mission.select('p[1]/text()').extract()[0]
        #(duration_min, duration_max, start_date) = 
        # Examples
        # 6 mois, à partir du 01 Janvier 2010.
        # 6 mois à un an, à partir du 01 Janvier 2010.
        # 6 mois renouvelable une fois, à partir du 01 Janvier 2010.
        # à partir du 01 Janvier 2010.
        result = re.match(ur'([^,]*),? *à partir du (\d{2}) (\w+) (\d{4})\.',
                          dates, flags=re.UNICODE)
        if result:
            result = result.groups()
            # TODO: get duration_min
            # TODO: get duration_max
            item['start_date_day'] = result[1]
            item['start_date_month'] = result[2]
            item['start_date_year'] = result[3]
        else:
            self.log('SERVICE_CIVIQUE: Could not parse "' + dates + '"')

        location = mission.select('p[2]/text()').extract()
        if location:
            item['location'] = location[0]
        phone_number = mission.select('p[3]/text()').extract()
        if phone_number:
            item['phone_number'] = self.parse_phone_number(phone_number[0])
        item['description'] = mission.select('div/text()').extract()[0]

        structure = node.select('//div[@class="contact-m" and position()=1]')
        item['client'] = structure.select('p[1]/text()').extract()[0].strip()
        item['address'] = structure.select('p[2]/text()').extract()[0]
        # For some reason, sometimes this is in fact an email address...
        website = structure.select('p[3]/text()').re('Site Internet : (.*)')
        if website:
            item['website'] = website[0]
        item['category'] = category

        return item

    def parse_phone_number(self, phone_number):
        """Try to normalize the phone number if it's not too complicated"""
        if len(phone_number) < 10:
            return None
        res = re.match(
            r'^[ ]?(\d\d)\D?(\d\d)\D?(\d\d)\D?(\d\d)\D?(\d\d)[ .]*$',
            phone_number, flags=re.UNICODE)
        if res:
            return '%s %s %s %s %s' % res.groups()
        #self.log('Could not parse phone number: "' + phone_number + '"',
        #         level=log.WARNING)
        return phone_number
