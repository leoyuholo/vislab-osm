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
            '$or': [
                    {
                        'source_position': {
                            '$geoWithin': {
                                '$geometry': area
                            }
                        }
                    }, {
                        'target_position': {
                            '$geoWithin': {
                                '$geometry': area
                            }
                        }
                    }
                ]
        }
    links = mongo.db.hk_link.find(query)

    output = [{
        'id': link['id'],
        'source': link['source'],
        'target': link['target'],
        'coordinates': [
            {'lng': link['source_position'][0], 'lat': link['source_position'][1]},
            {'lng': link['target_position'][0], 'lat': link['target_position'][1]}
        ],
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
