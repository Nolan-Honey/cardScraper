import scrapy
from scrapy.spiders import BaseSpider
from scrapy.selector import Selector
from facetoface_spider.items import FacetoFaceSpiderItem
from scrapy.http import Request
import re
from urllib.parse import urljoin
import schedule
import time
from scrapy.crawler import CrawlerProcess
import csv
import pandas as pd
import numpy as np
import re
import pymongo
from pprint import pprint
from pymongo import MongoClient
from pandas.core.common import _maybe_box_datetimelike
import subprocess
from subprocess import call
import requests


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
            if "magic_singles" in link and "filter" not in link and "blank" not in link:
                #print("TRUE:--------------------------- " + set + " ---------------------------:TRUE")
                if link_validator.match(link) and not link in visited_links:
                    visited_links.append(link)
                    yield Request(link, self.parse)
                else:
                    full_url=response.urljoin(link)
                    visited_links.append(full_url)
                    yield Request(full_url, self.parse)
    extract()
    cardsToDb()                

def extract():
    client = pymongo.MongoClient("mongodb://admin:2ez_4arteezy@cluster0-shard-00-00-pbwub.gcp.mongodb.net:27017,cluster0-shard-00-01-pbwub.gcp.mongodb.net:27017,cluster0-shard-00-02-pbwub.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true")
    db = client["the_sword_and_board_online_pricing_db"]
    collection = db[ "test_card_prices_with_set_and_names" ]
    serverStatusResult=db.command("serverStatus")
    print(serverStatusResult)
    #insert
    df = pd.read_csv('../spiders/mtgCardPrices.csv')
    df['category'] = df['category'].str.replace(r'\/[^,]+', '').str.replace(r'^\d+.*', '')
    df['category'] = df['category'].str.replace(r'^$', 'battlebond').str.replace(r'^$', 'battlebond')
    df['category'] = df['category'].str.replace(r'^s{1}$', 'italian_legends').str.replace(r'^s{1}$', 'italian_legends')
    df.drop_duplicates(subset='category', keep='first')
    df.to_csv("mtgPrices", sep='\t', encoding='utf-8')
    data = df.to_dict(orient='records') 
    collection.insert_many(data) 

def cardsToDb():
    client = pymongo.MongoClient("mongodb://admin:2ez_4arteezy@cluster0-shard-00-00-pbwub.gcp.mongodb.net:27017,cluster0-shard-00-01-pbwub.gcp.mongodb.net:27017,cluster0-shard-00-02-pbwub.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true")
    db = client["the_sword_and_board_online_pricing_db"]
    collection = db[ "test_mtg_cards" ]
    serverStatusResult=db.command("serverStatus")
    print(serverStatusResult)
    #scryfall --> into our DB
    data = requests.get("https://archive.scryfall.com/json/scryfall-default-cards.json")
    print(data.status_code)
    collection.insert_many(data)