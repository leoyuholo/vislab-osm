from flask import Flask
from flask_pymongo import PyMongo
from flask import jsonify
from flask import request

app = Flask('osm')

app.config['MONGO_URI'] = 'mongodb://mongo:27017/local'
mongo = PyMongo(app)

@app.route('/links', methods=['POST', 'GET'])
def list_links():
    area = request.json['area'] if request.json else None
    query = {}
    if (area):
        query = {
            'path': {
                '$elemMatch': {
                    'coordinates': {
                        '$geoWithin': {
                            '$geometry': area
                        }
                    }
                }
            }
        }
    links = list(mongo.db.osm_links.find(query))

    output = [{
        'id': link['id'],
        'source': link['source'],
        'target': link['target'],
        'coordinates': [
            {'lng': link['source_position'][0], 'lat': link['source_position'][1]},
            {'lng': link['target_position'][0], 'lat': link['target_position'][1]}
        ],
        'path': [{
            'id': node['id'],
            'lng': node['coordinates'][0],
            'lat': node['coordinates'][1]
        } for node in link['path']],
        'region': link['region'],
        'type': link['type']
    } for link in links]

    return jsonify({'links': output})

@app.route('/nodes', methods=['POST', 'GET'])
def list_nodes():
    area = request.json['area'] if request.json else None
    query = {}
    if (area):
        query = {
            'position': {
                '$geoWithin': {
                    '$geometry': area
                }
            }
        }
    nodes = mongo.db.hk_node.find(query)

    output = [{
        'id': node['id'],
        'coordinates': {
            'lng': node['position'][0], 'lat': node['position'][1]
        }
    } for node in nodes]

    return jsonify({'nodes': output})

@app.route('/osm_nodes', methods=['POST'])
def list_osm_nodes():
    area = request.json['area'] if request.json else None
    query = {}
    if (area):
        query = {
            'coordinates': {
                '$geoWithin': {
                    '$geometry': area
                }
            }
        }
    nodes = mongo.db.osm_nodes.find(query)

    output = [{
        'id': node['id'],
        'coordinates': {
            'lng': node['coordinates'][0],
            'lat': node['coordinates'][1]
        }
    } for node in nodes]

    return jsonify({'nodes': output})

@app.route('/ways', methods=['POST'])
def list_ways():
    area = request.json['area'] if request.json else None
    query = {}
    if (area):
        query = {
            'coordinates': {
                '$geoWithin': {
                    '$geometry': area
                }
            }
        }
    nodes = mongo.db.osm_nodes.find(query)

    # app.logger.info(query)

    nodes = [node for node in nodes]

    node_ids = [node['id'] for node in nodes]
    nodes = dict(zip([node['id'] for node in nodes], nodes))

    query = {
        'nd': {
            '$in': node_ids
        }
    }

    ways = mongo.db.osm_ways.find(query)

    # output = [{
    #     'id': way['id'],
    #     'coordinates': [{
    #         'lat': node['coordinates'][1],
    #         'lng': node['coordinates'][0]
    #     } for node in way['nodes']]
    # } for way in ways]

    output = [{
        'id': way['id'],
        'highway': way['highway'],
        'coordinates': [{
            'id': nodes[nd]['id'],
            'lat': nodes[nd]['coordinates'][1],
            'lng': nodes[nd]['coordinates'][0]
        } for nd in way['nd'] if nd in nodes]
    } for way in ways]

    # app.logger.info(output[0])

    return jsonify({'ways': output})
