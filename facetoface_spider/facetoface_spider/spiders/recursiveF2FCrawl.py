import scrapy
from scrapy.spiders import BaseSpider
from scrapy.selector import Selector
from facetoface_spider.items import FacetoFaceSpiderItem
from scrapy.http import Request
import re
from urllib.parse import urljoin

class F2FSpider(scrapy.Spider):
    name = "face_crawler"
    allowed_domains = ['facetofacegames.com']
    start_urls = ["https://www.facetofacegames.com/"]
    def parse(self, response):
        hxs = Selector(response)
        #CODE for scaping card names
        names=hxs.xpath('.//table[@class="invisible-table products_table"]/tr[*]/td[2]/a/text()').extract()
        categories_url=response.request.url
        categories=categories_url[54:]
        prices=hxs.xpath('.//table[@class="invisible-table products_table"]/tr[*]/td[2]/table[*]/tr[1]/td[2]').getall()
        #magic_cat="magic_singles-"+categories
        for n, p in zip(names,prices):
            price=p.replace('<td class="price" align="right" '
                                      'width="19%">',"").replace('<span '
                                      'class="msrp">',"").replace('</span>\n'
                                 '            \t\n'
                                 '            </td>',"").replace('\n',"").replace('\t',"").replace('<td align="right" '
                                     'width="19%">',"").replace("</td>","")
            sale=price[:20].strip()
            msrp=price[21:].strip()
            card_info=FacetoFaceSpiderItem()
            card_info['card']=n.replace('"',"").replace("'","")
            card_info['sale']=sale
            card_info['msrp']=msrp
            card_info['category']=categories
            yield card_info
        visited_links=[]
        links = hxs.xpath('//a/@href').extract()
        link_validator= re.compile("^(?:http:\/\/www\.facetofacegames\.com\/catalog\/magic_singles|https:\/\/www\.facetofacegames\.com\/catalog\/magic_singles)(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+)|\?(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+)$")
        for link in links:
            if "magic_singles" in link and "filter" not in link:
                #print("TRUE:--------------------------- " + set + " ---------------------------:TRUE")
                if link_validator.match(link) and not link in visited_links:
                    visited_links.append(link)
                    yield Request(link, self.parse)
                else:
                    full_url=response.urljoin(link)
                    visited_links.append(full_url)
                    yield Request(full_url, self.parse)

            