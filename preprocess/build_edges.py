import pymongo
import pydash

import mongo

penalty = {
    "road": 0,
    "primary": 0,
    "primary_link": 0,
    "trunk": 0,
    "motorway_link": 0,
    "trunk_link": 0,
    "motorway": 0,
    "secondary_link": 1,
    "secondary": 1,
    "residential": 3
}

def way_edges(way):
    nodes = way['nodes']

    if len(nodes) <= 1:
        return []

    edges = []
    for idx in range(1, len(nodes)):
        edges += [(nodes[idx-1], nodes[idx]), (nodes[idx], nodes[idx-1])]

    return [{
        'from': edge[0],
        'to': edge[1],
        'penalty': penalty[way['highway']],
        'highway': way['highway']
    } for edge in edges]

def build_edges():
    ways = mongo.db.osm_ways.find()

    edges = [
        edge
    for way in ways
    for edge in way_edges(way)]

    mongo.db.osm_edges.create_index([('from.id', pymongo.ASCENDING)])
    result = mongo.db.osm_edges.insert_many(edges)
    print('edges inserted: ' + str(len(result.inserted_ids)))

def run():
    build_edges()
