import json
from heapq import heappush, heappop

with open('goods.json', 'r') as f:
    rows = json.load(f)

good_names = set()
for row in rows:
    good_names.add(row['Name'])
good_names = list(good_names)
# remove Diamond ring, Gracious bouquet,Mystery net,
good_names.remove('diamond ring')
good_names.remove('gracious bouquet')

def make_sources():
    sources_key = set()
    for row in rows:
        sources_key.add(row['Source'])
    sources = {}
    for key in sources_key:
        sources[key] = [
            {
                'status':'idle',
                'product':None,
                'start_time':None,
                'end_time':None,
            }
        ]

    for _ in range(9):
        sources['Field'].append( {
                'status':'idle',
                'product':None,
                'start_time':None,
                'end_time':None,
            })
    return sources


def find_by_name(name):
    for row in rows:
        if row['Name'].lower() == name.lower():
            return row
    return None

def find_needed_for_tree(name,count=1):
    row = find_by_name(name)
    if row is None:
        raise Exception(f'Could not find {name}')
    result = row.copy()
    needs = result['Needs'].copy()
    result['Needs'] = []
    result['Count'] = count
    for need in needs:
        for key, value in need.items():
            if (key==name):
                continue
            result['Needs'].append(find_needed_for_tree(key, value*count))
    return result

def _find_needed_for_list(name,count=1,):
    result = []
    row = find_by_name(name)
    if row is None:
        raise Exception(f'Could not find {name}')
    result.append({
        'Name':name,
        'Count':count,
    })
    needs = row['Needs'].copy()
    for need in needs:
        for key, value in need.items():
            if (key==name):
                continue
            result += _find_needed_for_list(key, value*count,)
    return result

def find_needed_for_list(name,count=1):
    return _find_needed_for_list(name,count)[1:]

def find_needed_for_lists(names):
    result = []
    for name in names:
        result += find_needed_for_list(name)
    temp = []
    for item in result:
        for _ in range(item['Count']):
            temp.append(item['Name'])
    return temp

def find(name):
    return find_needed_for_tree(name,1)

def process(tasks,storage,sources):
    tasks = tasks.copy()
    storage = storage.copy()
    sources = sources.copy()
    time_queue = [0]
    while len(time_queue) > 0:
        time = heappop(time_queue)
        for source_name in sources:
            for i,s in enumerate(sources[source_name]):
                if s['end_time'] == time:
                    if source_name=='Field':
                        storage[s['product']] += 2
                    else:
                        storage[s['product']] += 1
                    s['status'] = 'idle'
                    s['product'] = None
                    s['start_time'] = None
                    s['end_time'] = None
        for i,task in enumerate(tasks.copy()):
            task = find_by_name(task)

            if_have_enough_materials = True
            for need in task['Needs']:
                key,value = list(need.items())[0]
                if storage[key] < value:
                    if_have_enough_materials = False
                    break
            if not if_have_enough_materials:
                continue
            if_have_enough_sources = False
            source = task['Source']
            for s in sources[source]:
                if s['status'] == 'idle':
                    if_have_enough_sources = True
                    break
            if not if_have_enough_sources:
                continue
            s['status'] = 'busy'
            s['product'] = task['Name']
            s['start_time'] = time
            s['end_time'] = time + task['Time']
            for need in task['Needs']:
                key,value = list(need.items())[0]
                storage[key] -= value
            if s['end_time'] not in time_queue:
                heappush(time_queue,s['end_time'])
            tasks.remove(task['Name'])
    return {
        "time":time,
        "storage":storage,
        "remaining_tasks":tasks,
    }