import json
import graphviz
import re
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

def make_requirement_tree(name,storage,count=1):
    """
    name: name of the item to make
    storage: a dict of items in storage must be a copy of the storage dict so that it can be modified without affecting the original storage dict
    count: number of items to make
    """
    
    node = find_by_name(name)

    if storage[name]>=count:
        storage[name]-=count
        return None
    else:
        count-=storage[name]
        storage[name]=0
    result = {
        'name':node["Name"],
        'quantity':count,
        'children':[]
    }
    for child in node['Needs']:
        for child_name,quantity in child.items():
            if (child_name==name):
                continue
            child = make_requirement_tree(child_name,storage,quantity*count)
            if child:
                result['children'].append(child)
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