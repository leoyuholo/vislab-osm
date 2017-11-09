import pymongo
import mongo

def filter_ways():
    query = {
        'highway': {
            '$in': [
                "road",
                "primary",
                "primary_link",
                "trunk",
                "motorway_link",
                "trunk_link",
                "motorway",
                "secondary_link",
                "secondary",
                "residential"
            ]
        }
    }

    ways = mongo.db.way.find(query)

    mongo.db.osm_ways.create_index([('nd', pymongo.ASCENDING)])
    result = mongo.db.osm_ways.insert_many(ways)
    print('ways inserted: ' + str(len(result.inserted_ids)))

def filter_nodes():
    ways = mongo.db.osm_ways.find()
    nodeIds = list(set([item for way in ways for item in way['nd']]))

    query = {
        'id': {
            '$in': nodeIds
        }
    }

    nodes = mongo.db.node.find(query)

    def transform_node(node):
        node['coordinates'] = [
            float(node['lon']),
            float(node['lat'])
        ]
        return node

    mongo.db.osm_nodes.create_index([('id', pymongo.ASCENDING)])
    mongo.db.osm_nodes.create_index([('coordinates', '2dsphere')])
    result = mongo.db.osm_nodes.insert_many([transform_node(node) for node in nodes])
    print('nodes inerted: ' + str(len(result.inserted_ids)))

def run():
    filter_ways()
    filter_nodes()
