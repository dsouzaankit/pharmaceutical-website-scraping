import scrapy
from scrapy.selector import Selector
#from scrapy.http import HtmlResponse

class Drug2(scrapy.Item):
    Illness = scrapy.Field()
    Generic_name = scrapy.Field()
    Description = scrapy.Field()
    Classification = scrapy.Field()
#    Dosage = scrapy.Field()
#    Usage = scrapy.Field()
    Trade_name = scrapy.Field()
    Manufacturer = scrapy.Field()

class QuotesSpider(scrapy.Spider):
    name = "pharma2"

    def __init__(self, max_info = 10):
        if max_info:
            self.max_count = max_info
#limit crawl
        self.counter = 7

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.get('MAX_INFO'))

    def process_str(self, str):
        if str:
            str = str.replace(u'\xa0', u' ')
            str = str.strip(u' .-\t\n\r')
            str = str.replace(u"\u2018", "'").replace(u"\u2019", "'")
        return str

    def start_requests(self):
        urls = [
#            'http://www.medindia.net/drugs/medical-condition/index.asp?alpha=A',
#            'http://www.medindia.net/drugs/medical-condition/index.asp?alpha=B',
#            'http://www.medindia.net/drugs/medical-condition/index.asp?alpha=C',
            'http://www.medindia.net/drugs/medical-condition/index.asp?alpha=D',
#            'http://www.medindia.net/drugs/medical-condition/index.asp?alpha=E',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=F',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=G',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=H',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=I',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=J',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=K',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=L',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=M',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=N',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=O',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=P',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=Q',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=R',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=S',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=T',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=U',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=V',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=W',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=X',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=Y',
#            'http://www.medindia.net/doctors/drug_information/home.asp?alpha=Z',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse1)

    def parse1(self, response):

#get illness links alphabetically
        cond_nodes = response.xpath('//*[@class = "mi-list-group xs-block-grid-1 sm-block-grid-2"]/*[@class = "list-item"]/a')
        cond_names = response.xpath('//*[@class = "mi-list-group xs-block-grid-1 sm-block-grid-2"]/*[@class = "list-item"]/a/text()')
        for cond_node, cond_name in zip(cond_nodes, cond_names):
                #if(self.counter < self.max_count):
                if(cond_name.extract() == "Diabetes"):
                         illness = Drug2()
                         illness['Illness'] = cond_name.extract()
                         req = response.follow(cond_node, callback = self.parse2)
                         req.meta['item'] = illness
                         req.dont_filter = True
                         yield req
                         break
                self.counter += 1

    def parse2(self, response):

        illness = response.meta['item']

        drug_nodes = response.xpath('//article/h3/b/a')
        drug_names = response.xpath('//article/h3/b/a/text()')
        drug_descs = response.xpath('//article/div[1]/text()')

#replicate each illness record as per #related-drugs
#        drugs = [Drug2(illness) for x in range(len(drug_nodes))]

        for drug_node, drug_name, drug_desc in zip(drug_nodes, drug_names, drug_descs):
            drug = Drug2(illness)
            drug['Generic_name'] = drug_name.extract()
            drug['Description'] = drug_desc.extract()
            req = response.follow(drug_node, callback = self.parse3)
            req.meta['item'] = drug
            req.dont_filter = True
            yield req

    def parse3(self, response):

        drug = response.meta['item']

#extract drug classification
        classn = response.xpath('//*[contains(text(), "Therapeutic Classification  :")]/a/text()').extract()
        if classn:
            classn = classn[0]
        drug['Classification'] = classn

#check presence of indian substitutes
        in_subs = response.xpath('//h3[contains(text(), "India :")]/following-sibling::*[@class = "links"]/a')

        if not in_subs:
#clean records before yield
            for i in drug:
                drug[i] = self.process_str(drug[i])
            yield drug

#check presence of 'More...' tag
        more_tag = response.xpath('//a[@class = "view-all pull-right"]')
        if more_tag:
            more_tag = more_tag[0]
            req = response.follow(more_tag, callback = self.parse4)
            req.meta['item'] = drug
            req.dont_filter = True
            yield req
        else:
            for in_sub in in_subs:
                req = response.follow(in_sub, callback = self.parse5)
                req.meta['item'] = drug
                req.dont_filter = True
                yield req

    def parse4(self, response):

        drug = response.meta['item']

        in_subs = response.xpath('//table[@class = "table-bordered table table-responsive report-content"]/tbody/tr/td[@class = " report-content"]/a')
        for in_sub in in_subs:
            req = response.follow(in_sub, callback = self.parse5)
            req.meta['item'] = drug
            req.dont_filter = True
            yield req

    def parse5(self, response):

        drug = response.meta['item']

#extract indian trade name
        tr_name = response.xpath('//td[contains(text(), "Trade Name ")]/following-sibling::td/b/text()').extract()
        if tr_name:
            tr_name = tr_name[0]
        drug['Trade_name'] = tr_name

#extract indian drug manufacturer name
        manuf = response.xpath('//td[contains(text(), "Manufacturer ")]/following-sibling::td/a/text()').extract()
        if manuf:
            manuf = manuf[0]
        drug['Manufacturer'] = manuf

        for i in drug:
#clean records before yield
            drug[i] = self.process_str(drug[i])

        yield drug
