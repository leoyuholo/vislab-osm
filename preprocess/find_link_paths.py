from joblib import Parallel, delayed
import multiprocessing
import pdb
import sys

import pydash

import mongo

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

def find_ways_by_nd(nd):
    query = {
        'nd': nd
    }

    return list(mongo.db.osm_ways.find(query))

def find_way_by_id(way_id):
    query = {
        'id': way_id
    }

    return mongo.db.osm_ways.find_one(query)

def find_node_by_id(nd):
    query = {
        'id': nd
    }

    return mongo.db.osm_nodes.find_one(query)

def init_way(way, previous=None, intersect=None, cost=0):
    way['previous'] = previous
    way['intersect'] = intersect
    way['cost'] = cost

    return way

def init_start_pts(start_pts):
    return [
        init_way(way, intersect=pt['id'], cost=pt['distance'])
    for pt in start_pts
    for way in find_ways_by_nd(pt['id'])]

def pick_way(ways):
    return pydash.min_by(ways, 'cost')

def expand(orig_way):
    def expand_cost(orig_way, way, intersect):
        return orig_way['cost'] + 1

    return [
        init_way(way, previous=orig_way, intersect=nd, cost=expand_cost(orig_way, way, nd))
    for nd, way_ids in orig_way['overlaps'].items()
    for way in [find_way_by_id(way_id) for way_id in way_ids]]

def way_distance(way, pt_id1, pt_id2):
    return abs(way['nd'].index(pt_id1) - way['nd'].index(pt_id2))

def check_goal(end_pts, way):
    end_pts = pydash.key_by(end_pts, 'id')
    end_pt_ids = end_pts.keys()

    goals = [
        (end_pts[nd]['distance'], nd)
    for indx, nd in enumerate(way['nd']) if nd in end_pt_ids]

    return None if len(goals) == 0 else pydash.min_by(goals, 0)[1]

def trace_nd(nds, from_nd, to_nd):
    from_idx = nds.index(from_nd)
    to_idx = nds.index(to_nd)
    # pdb.set_trace()
    if (from_idx < to_idx):
        return nds[from_idx:to_idx+1]
    else:
        return list(reversed(nds[to_idx:from_idx+1]))

def trace_way(way):
    path = trace_nd(way['nd'], way['end'], way['intersect'])
    end = way['intersect']
    while way['previous']:
        way = way['previous']
        path += trace_nd(way['nd'], end, way['intersect'])
        end = way['intersect']
    return path[::-1]

def end_way(way, goal):
    way['end'] = goal
    return trace_way(way)

def find_path(link):
    start_pts = find_closest_pts(link['source_position'], limit=5)
    end_pts = find_closest_pts(link['target_position'], limit=2)

    # print('start_pts: ' + str(len(start_pts)))
    # print([pt['id'] for pt in start_pts])
    # print('end_pts: ' + str(len(end_pts)))
    # print([pt['id'] for pt in end_pts])

    current_ways = init_start_pts(start_pts)
    # print('current_ways: ' + str(len(current_ways)))
    if(len(current_ways) == 0):
        raise Exception('Not routable: No starting point ' + str(len(start_pts)))
    pick = None
    goal = None
    while not goal:
        pick = pick_way(current_ways)
        current_ways = pydash.without(current_ways, pick) + expand(pick)
        goal = check_goal(end_pts, pick)
        # print('cost: ' + str(pick['cost']))
        # print('current_ways: ' + str(len(current_ways)))
        if len(current_ways) > 1000:
            raise Exception('Not routable: Too much ways')

    # print('end: ' + str(pick['cost']) + ' ' + goal)
    # print(pick)

    path = end_way(pick, goal)

    # print(path)

    return path

def find_link_path(link):
    link['path'] = [find_node_by_id(nd) for nd in find_path(link)]

    return mongo.db.osm_links.insert_one(link).inserted_id

def work(link):
    # print('start finding path for link: ' + link['id'])
    result = ''
    try:
        result = {
            'ok': True,
            '_id': find_link_path(link)
        }
    except Exception as e:
        print(f"link {link['id']} failed: {str(e)}")
        result = {
            'ok': False,
            'id': link['id'],
            'error': str(e)
        }
        pass
    # print('finished finding path for link: ' + link['id'])
    return result

def find_link_paths():
    # links = [mongo.db.hk_link.find_one({'id': '993007-993008'})]
    # links = [mongo.db.hk_link.find_one({'id': '993008-992091'})]
    links = list(mongo.db.hk_link.find())

    # results = [work(link) for link in links]

    # num_cores = multiprocessing.cpu_count()
    results = Parallel(n_jobs=32, verbose=100)(delayed(work)(link) for link in links)
    # p = multiprocessing.Pool(num_cores - 1)
    # results = p.map(work, links)

    print('results: ' + str(len(results)))
    print('success: ' + str(len([result for result in results if result['ok']])))
    print('failed: ' + str(len([result for result in results if not result['ok']])))
    print([result for result in results if not result['ok']])

def run():
    # print(trace_nd([1,2,3,4,5], 2, 3))
    # print(trace_nd([1,2,3,4,5], 3, 2))
    # print(trace_nd([1,2,3,4,5], 2, 4))
    # print(trace_nd([1,2,3,4,5], 4, 2))
    # print(trace_nd([1,2,3,4,5], 1, 5))
    # print(trace_nd([1,2,3,4,5], 5, 1))
    # print(trace_nd([1,2,3,4,5], 4, 1))
    print('start find_link_paths')
    find_link_paths()
