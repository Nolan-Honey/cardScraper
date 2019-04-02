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


