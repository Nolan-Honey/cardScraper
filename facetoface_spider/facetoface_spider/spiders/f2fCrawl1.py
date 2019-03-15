import scrapy
from scrapy.spiders import BaseSpider
from scrapy.selector import Selector
from facetoface_spider.items import FacetoFaceSpiderItem
from scrapy.http import Request

class F2FSpider(scrapy.Spider):
    name = "face_crawlerOld"
    allowed_domains = ['facetofacegames.com']
    start_urls = ["https://www.facetofacegames.com/catalog/magic_singles-guilds_of_ravnica_block-guilds_of_ravnica/12093"]
    def parse(self, response):
        hxs = Selector(response)

        #CODE for scaping card names
        card_names = hxs.xpath('//*[@class="name"]/text()')
        for names in card_names:
            card = FacetoFaceSpiderItem()
            card["name"] = names
            yield card
