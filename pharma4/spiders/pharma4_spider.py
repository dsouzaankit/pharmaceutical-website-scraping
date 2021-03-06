#for navigation: parse href, extract & set form's EVENTTARGET and EVENTARGUMENT attributes, & submit form

import re
import scrapy
from scrapy.selector import Selector

class Drug4(scrapy.Item):
    Illness = 'Diarrhoea'
    Generic_name = scrapy.Field()
    Description = scrapy.Field()
    Classification = scrapy.Field()
    Trade_name = scrapy.Field()
    Manufacturer = scrapy.Field()

class QuotesSpider(scrapy.Spider):

    name = 'pharma4'

    def process_str(self, str):
        if str:
            str = str.strip(u' .-\t\n\r')
            str = str.replace(u'\r\n\r\n', u', ')
        return str

    def start_requests(self):

        self.start_url = 'http://www.testsite.com/DrugsDescriptionByDisease/Diarrhea'
        yield scrapy.Request(url = self.start_url, callback = self.parse1)


    def parse1(self, response):

        rows = response.xpath('//table[contains(@class, "drugdescriptinTable")]//tr/td[2]')

        for row in range(0, len(rows) - 1, 2):
                drug = Drug4()
                #self.log("trade name is " + rows[row].xpath('a/text()').extract()[0])
                drug['Trade_name'] = rows[row].xpath('a/text()').extract()[0]
                drug['Generic_name'] = rows[row + 1].xpath('text()').extract()[0]
                drug_link = rows[row].xpath('a/@href').extract()[0]
                #self.log("drug link is " + drug_link)
                mth_expr = re.search("javascript:__doPostBack\('(.*?)','(.*?)'", drug_link)
                a1 = mth_expr.group(1)
                #self.log("a1 is " + a1)
                a2 = mth_expr.group(2)
                yield scrapy.FormRequest.from_response(
                                   response,
                                   formdata = {'__EVENTTARGET': a1, '__EVENTARGUMENT': a2},
                                   meta = {'item' : drug},
                                   callback = self.parse2,
                                   dont_click = True)

        self.iter = 0
        pagi_mrkrs = response.xpath('//*[contains(@class, "linkPagination")]')
        nxt_mrkr = pagi_mrkrs[len(pagi_mrkrs) - 1].xpath('@href').extract()[0]
        #self.log("next marker is " + nxt_mrkr)
        if nxt_mrkr and self.iter <= 10000:
                mth_expr = re.search("javascript:__doPostBack\('(.*?)','(.*?)'", nxt_mrkr)
                a1 = mth_expr.group(1)
                a2 = mth_expr.group(2)
                yield scrapy.FormRequest.from_response(
                                   response,
                                   formdata = {'__EVENTTARGET': a1, '__EVENTARGUMENT': a2},
                                   callback = self.parse1,
                                   dont_click = True)
                self.iter = self.iter + 1

    def parse2(self, response):

        drug = response.meta['item']

        drug['Description'] = response.xpath('//textarea[contains(@id, "tbUses")]/text()').extract()[0]
        drug['Classification'] = response.xpath('//textarea[contains(@id, "tbClassOfDrugs")]/text()').extract()[0]
        drug['Manufacturer'] = response.xpath('//p[contains(@id,"pMAnufacturer")]/text()').extract()[0]

        #clean records before yield
        for i in drug:
            drug[i] = self.process_str(drug[i])

        yield drug
