import pymongo

mongo = pymongo.MongoClient('mongodb://mongo:27017/')
db = mongo.local
