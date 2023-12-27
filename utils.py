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
    result['needs'] = []
    result['count'] = count
    for need in row['Needs']:
        for key, value in need.items():
            if (key==name):
                continue
            result['needs'].append(find_needed_for(key, value*count))
    del result['Needs']
    return result


def find(name):
    return find_needed_for(name,1)