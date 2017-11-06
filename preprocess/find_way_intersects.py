from itertools import groupby
import pymongo
import pydash

import mongo

def find_overlaps(assos):
    overlaps = {
        key: [
            item[1]
        for item in group]
    for key, group in pydash.group_by(assos, lambda x: x[0]).items()}
    overlaps = {k:v for k, v in overlaps.items() if len(v) > 1}
    return overlaps

def find_way_intersects():
    ways = list(mongo.db.osm_ways.find())

    assos = [(nd, way['id']) for way in ways for nd in way['nd']]
    overlaps = find_overlaps(assos)

    print('overlaps: ' + str(len(overlaps)))

    def add_overlaps(way):
        way['overlaps'] = {
            nd: [
                wayId
            for wayId in overlaps[nd] if wayId != way['id']]
        for nd in way['nd'] if nd in overlaps}
        return way

    ways = [add_overlaps(way) for way in ways]

    result = mongo.db.osm_ways.bulk_write([
        pymongo.UpdateOne({'_id': way['_id']}, {'$set': {'overlaps': way['overlaps']}})
    for way in ways], ordered=False)
    print(result.bulk_api_result)

def run():
    find_way_intersects()
