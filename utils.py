import json
import graphviz
import re
import random
import copy
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

    for _ in range(2):
        sources['Field'].append( {
                'status':'idle',
                'product':None,
                'start_time':None,
                'end_time':None,
            })
    return sources

def make_storage(level=None):
    storage = {}
    for row in rows:
        # regex take only first digits
        row_level = re.findall(r'\d+', row['Level'])
        if level and level < int(row_level[0]):
            continue
        storage[row['Name']] = 0
    return storage

def find_by_name(name):
    for row in rows:
        if row['Name'].lower() == name.lower():
            return row
    return None

def make_need_tree(name, count=1):
    row = find_by_name(name)
    if row is None:
        raise Exception(f'Could not find {name}')
    result = row.copy()
    needs = result['Needs'].copy()
    result['Needs'] = []
    result['Count'] = count
    if row['Name'].endswith('feed'):
        temp = count // 3
        if count % 3 != 0:
            temp+=1
        count = temp
    for need in needs:
        for key, value in need.items():
            if (key==name):
                continue
            result['Needs'].append(make_need_tree(key, value*count))
    return result

def tree_to_list(tree):
    result = []
    def add_node(node):
        result.append({
            'Name':node['Name'],
            'Count':node['Count'],
        })
        for child in node['Needs']:
            add_node(child)
    add_node(tree)
    return result


def visualize_tree(tree):
    dot = graphviz.Digraph(comment='Pancake')
    dot.attr(label=f'Recipe for {tree["Count"]} {tree["Name"]}')
    dot.attr(fontsize='20')
    dot.attr(fontname='Helvetica')
    dot.attr(rankdir='LR')
    dot.attr(nodesep='0.5')
    dot.attr(ranksep='1')
    def add_node(node):
        dot.node(name=node['Name'],label=f'{node["Name"]}',  image=node['image'], shape='none', labelloc='b', )
        for child in node['Needs']:
            dot.edge( child['Name'],node['Name'], label=f'{child["Count"]}')
            add_node(child)
    add_node(tree)
    return dot



def make_task_list(names,storage):
    id_count = 0
    storage = storage.copy()
    def _make_task_list(name,root,count=1,target=False,depth=1):
        nonlocal id_count
        tasks = []
        node = find_by_name(name)
        if storage[node['Name']] >= count:
            storage[node['Name']] -= count
            return []

        task_count = count//node['output_amount']+ (1 if count%node['output_amount']!=0 else 0)
        task_dependencies = []
        for need in node['Needs']:
            for key, value in need.items():
                if (key==name):
                    continue
                temp = _make_task_list(key,root,value*task_count,depth=depth+1)
                tasks.extend(temp)
                # add dependencies
                task_dependencies.extend([t['id'] for t in temp])
        for _ in range(task_count):
            id_count+=1
            task = {
                'id':id_count,
                'name':node['Name'],
                'dependencies':[], # id of dependencies tasks
                'duration':node['Time'],
                'source':node['Source'],
                'machine_id': None,
                'dependencies':task_dependencies,
                'target':target,
                'order':depth,
                'root':root
            }
            tasks.append(task)
        return tasks
    
    tasks = []
    for name in names:
        tasks.extend(_make_task_list(name,target=True,root=f'{name}_{id_count}'))
    return tasks

def merge_lists_shuffle(*lists):
    indexes = []
    for list in lists:
        # tuple (index,value)
        indexes.extend([(i,value) for i,value in enumerate(list)])
    random.shuffle(indexes)
    # sort by index
    indexes.sort(key=lambda x:x[0])
    # return list of value
    return [value for index,value in indexes]



def calc_start_end_time(tasks,machines):
    machine_queue={}
    for key in machines.keys():
        for machine_id in machines[key]:
            machine_queue[machine_id]=[]

    for task in tasks:
        start_time = 0
        if len(machine_queue[task['machine_id']]):
            start_time=machine_queue[task['machine_id']][-1]['end_time']
        else:
            start_time=0
        if len(task['dependencies']):
            for dependency_task_id in task['dependencies']:
                dependency_task = [t for t in tasks if t['id']==dependency_task_id][0]
                dependency_task_end_time = dependency_task['end_time']
                if dependency_task_end_time>start_time:
                    start_time=dependency_task_end_time
        task['start_time']=start_time
        task['end_time']=start_time+task['duration']
        machine_queue[task['machine_id']].append(task)
    return tasks