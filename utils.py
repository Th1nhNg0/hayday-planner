import json

with open('goods.json', 'r') as f:
    rows = json.load(f)

def find_by_name(name):
    for row in rows:
        if row['Name'].lower() == name.lower():
            return row
    return None

def find_needed_for(name,count=1):
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
            result['Needs'].append(find_needed_for(key, value*count))
    return result


def find(name):
    return find_needed_for(name,1)