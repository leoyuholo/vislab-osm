import mongo

def drop_collections():
    if('osm_ways' in mongo.db.collection_names()):
        mongo.db.osm_ways.drop()
    if('osm_nodes' in mongo.db.collection_names()):
        mongo.db.osm_nodes.drop()
    if('osm_edges' in mongo.db.collection_names()):
        mongo.db.osm_edges.drop()
    if('osm_links' in mongo.db.collection_names()):
        mongo.db.osm_links.drop()

def run():
    drop_collections()
