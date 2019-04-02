import pymongo
from pymongo import MongoClient
from pprint import pprint
import pandas as pd
import numpy as np

#connect to mongo DB, load the 2 collections
client = MongoClient("mongodb://admin:2ez_4arteezy@cluster0-shard-00-00-pbwub.gcp.mongodb.net:27017,cluster0-shard-00-01-pbwub.gcp.mongodb.net:27017,cluster0-shard-00-02-pbwub.gcp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true")
db = client["the_sword_and_board_online_pricing_db"]
priceCollection = db[ "card_prices_with_set_and_names" ]
imageCollection = db[ "mtg_cards" ]
serverStatusResult = db.command("serverStatus")
pprint(serverStatusResult)

#make a new collection in the DB
combineCollection = db[ "combined_prices_and_info" ]

#convert the collections to dataframes
priceData = pd.DataFrame(list(priceCollection.find()))
imageData = pd.DataFrame(list(imageCollection.find()))

#check to make sure the collections loaded properly
print(imageData.head())
print(priceData.head())


#convert everything to lowercase
priceData['category'] = priceData.loc[:,'category'].str.lower()
priceData['card'] = priceData.loc[:,'card'].str.lower()
imageData['name'] = imageData.loc[:,'name'].str.lower()
imageData['set_name'] = imageData.loc[:,'set_name'].str.lower()

#Add blank row to imageData
imageData['price'] = np.nan

#Add a blank row to PriceData for foil differentiation
priceData['foil'] = np.nan

#populate foil column and remove it from Name
for index, row in priceData.iterrows():
    print("Row: " +row)
    print("Index: " +index)
    #if priceData.loc[row, 'card'].str.contains('- foil', na=False).any():
    #    row['card'] = row['card'].str.replace('- foil', '').str.replace('- foil', '')
     #   row['Foil'] = True

#priceData.loc['card'].str.contains('- foil').iloc[5] = True

print("---------We got to the data combining part--------------")
#find each unique set in image DB
for priceIndex, priceRow in priceData.iterrows():
    for imageIndex, imageRow in imageData.iterrows():
        if priceRow['foil'].str.contains('NaN') or priceRow['foil'].str.contains('False') or priceRow['foil'].str.contains('false') or priceRow['foil'].contains(False) or priceRow['foil'].str.contains('nan'):    
            if priceRow['card'].isin(imageRow['name']):
                if priceRow['category'].isin(imageRow['set_name']):
                    if priceRow['msrp'].str.contains('NaN'):
                        imageRow['price'] = priceRow['sale']
                    else:
                        imageRow['price'] = priceRow['msrp']
        else:
            if priceRow['card'].isin(imageRow['name']):
                if imageRow['set_name'].str.contains(priceRow['category']):        
                    if priceRow['msrp'].str.contains('NaN'):
                        imageRow['price'] = priceRow['sale']
                    else:
                        imageRow['price'] = priceRow['msrp']

print(priceData.head)
combineCollection.insert_many(imageData)