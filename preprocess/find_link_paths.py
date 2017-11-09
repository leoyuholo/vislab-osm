from joblib import Parallel, delayed
import multiprocessing
import pdb
import sys
import math

import pydash

import mongo

START_LIMIT = 16
START_RADIUS = 1600
END_LIMIT = 16
END_RADIUS = 1600
COST = 10 * 1000

def deg2rad (deg):
    return deg * math.pi / 180.0

def coor_distance(coor1, coor2):
    [lon1, lat1] = coor1
    [lon2, lat2] = coor2

    R = 6371000.0
    dlat = deg2rad(lat2 - lat1)
    dlon = deg2rad(lon2 - lon1)
    a = math.sin(dlat / 2.0) * math.sin(dlat / 2.0) + \
        math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * \
        math.sin(dlon / 2.0) * math.sin(dlon / 2.0)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    d = R * c
    return d

def find_edges(node):
    query = {
        'from.id': node['id']
    }
    return list(mongo.db.osm_edges.find(query))

def find_closest_pts(coordinates, maxDistance=200, limit=5):
    pipeline = [
        {
            '$geoNear': {
                'near': {
                    'type': 'Point',
                    'coordinates': coordinates
                },
                'spherical': True,
                'distanceField': 'distance',
                'maxDistance': maxDistance,
                'limit': limit
            }
        }
    ]

    return list(mongo.db.osm_nodes.aggregate(pipeline))

def init_node(node, previous=None, cost=0, start=None, end=None):
    node['previous'] = previous
    node['cost'] = cost
    node['start'] = start
    node['end'] = end

    return node

def init_start_nodes(start_nodes, start_coor):
    return [
        init_node(node, cost=node['distance']**2, start=start_coor)
    for node in start_nodes]

def init_goal_nodes(end_nodes, end_coor):
    return [
        init_node(node, cost=node['distance']**2, end=end_coor)
    for node in end_nodes]

def pick_node(nodes, target_coor):
    return pydash.min_by(nodes, lambda n: n['cost'] + coor_distance(n['coordinates'], target_coor))

def check_goal(pick):
    return 'goal' in pick and pick['goal'] == True

def expand(node, visited_node_ids, goal_nodes):
    edges = find_edges(node)
    edges = pydash.filter_(edges, lambda edge: edge['to']['id'] not in visited_node_ids)
    neighbours = [
        init_node(edge['to'], previous=node, cost=node['cost'] + coor_distance(node['coordinates'], edge['to']['coordinates']) * (1 + edge['penalty']))
    for edge in edges]

    neighbours += [
        init_node({
            'id': n['id'] + '-end',
            'coordinates': n['end'],
            'goal': True
        }, previous=node, cost=node['cost'] + n['cost'])
    for n in goal_nodes if n['id'] == node['id']]

    return neighbours

def traceback(node):
    if node['start']:
        return [{
            'id': node['id'] + '-start',
            'coordinates': node['start'],
            'cost': 0
        }]
    return [{
        'id': node['id'],
        'coordinates': node['coordinates'],
        'cost': node['cost']
    }] + traceback(node['previous'])

def find_path(start_coor, end_coor, start_limit=16, start_radius=200, end_limit=16, end_radius=200):
    if start_limit > START_LIMIT:
        raise Exception(f'start_limit: {start_limit} exceed maximum {START_LIMIT}')
    if end_limit > END_LIMIT:
        raise Exception(f'end_limit: {end_limit} exceed maximum {END_LIMIT}')

    start_nodes = find_closest_pts(start_coor, maxDistance=start_radius, limit=start_limit)
    end_nodes = find_closest_pts(end_coor, maxDistance=end_radius, limit=end_limit)

    if len(start_nodes) < start_limit and start_radius < START_RADIUS:
        return find_path(start_coor, end_coor, start_limit, start_radius*2, end_limit, end_radius)
    if len(end_nodes) < start_limit and end_radius < END_RADIUS:
        return find_path(start_coor, end_coor, start_limit, start_radius, end_limit, end_radius*2)

    pick = None
    goal =  None
    current_nodes = init_start_nodes(start_nodes, start_coor)
    visited_nodes = []
    visited_node_ids = []
    goal_nodes = init_goal_nodes(end_nodes, end_coor)
    while not goal:
        pick = pick_node(current_nodes, end_coor)
        goal = check_goal(pick)

        # print(f'pick: {pick["id"]} goal: {goal} cost: {pick["cost"]} visited: {pick["id"] in visited_node_ids}')

        visited_nodes += [pick]
        visited_node_ids += [pick['id']]
        current_nodes = pydash.without(current_nodes, pick) + expand(pick, visited_node_ids, goal_nodes)
        print(f'current_nodes: {len(current_nodes)}')
        # print(f'visited_nodes: {len(visited_nodes)}')
        # print(f'visited_node_ids: {len(visited_node_ids)}')

        # if pick['cost'] > 10*1000:
        #     raise Exception('cost larger than 10000m')

        # if len(current_nodes) > 1000:
        #     raise Exception('current_nodes larger than 1000')

        if len(current_nodes) == 0 or pick['cost'] > COST:
            if (start_limit / start_radius) > (end_limit / end_radius):
                return find_path(start_coor, end_coor, start_limit*2, start_radius, end_limit, end_radius)
            else:
                return find_path(start_coor, end_coor, start_limit, start_radius, end_limit*2, end_radius)

    path = traceback(pick)

    return list(reversed(path)), pick['cost']


def find_link_path(link):
    path1, cost1 = find_path(link['source_position'], link['target_position'])
    # path2, cost2 = find_path(link['target_position'], link['source_position'])

    # link['path'] = path2 if cost2 < cost1 else path1
    link['path'] = path1

    return mongo.db.osm_links.insert_one(link).inserted_id

def work(link):
    result = ''
    try:
        inserted_id = find_link_path(link)
        result = {
            'ok': True,
            'id': link['id'],
            '_id': inserted_id
        }
    except Exception as e:
        print(f"link {link['id']} failed: {str(e)}")
        result = {
            'ok': False,
            'id': link['id'],
            'error': str(e)
        }
        pass
    return result

def find_link_paths():
    # links = list(mongo.db.hk_link.find({'id': '3470-3006'}))
    links = list(mongo.db.hk_link.find())

    # results = [work(link) for link in [links[0]]]

    results = Parallel(n_jobs=32, verbose=100)(delayed(work)(link) for link in links)

    print('results: ' + str(len(results)))
    print('success: ' + str(len([result for result in results if result['ok']])))
    print('failed: ' + str(len([result for result in results if not result['ok']])))
    print([result for result in results if not result['ok']])

def run():
    find_link_paths()
