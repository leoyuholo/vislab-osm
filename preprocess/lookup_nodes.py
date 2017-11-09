from pymongo import UpdateOne
import mongo

def find_node_by_id(nd):
    query = {
        'id': nd
    }

    return mongo.db.osm_nodes.find_one(query)

def lookup_nodes():
    query = {}

    ways = mongo.db.osm_ways.find(query)

    updates = [
        UpdateOne({
            '_id': way['_id']
        }, {
            '$set': {
                'nodes': [find_node_by_id(nd) for nd in way['nd']]
            }
        })
    for way in ways]

    result = mongo.db.osm_ways.bulk_write(updates)
    print('lookup nodes: ways updated: ' + str(result.bulk_api_result['nModified']))

def run():
    lookup_nodes()
