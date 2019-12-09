#!/usr/bin/env python3

def get_sources(nodes):
    sources = []
    for node in nodes:
        source, _ = node
        if source not in sources:
            sources.append(source)
    return sources


def get_weights(nodes):
    sources = get_sources(nodes)
    weights = {}
    for source in sources:
        weights[source] = 0
    current_sources = ['COM']
    level = 0
    weights['COM'] = 0
    while len(current_sources) > 0:
        # Analyze all the current sources
        next_sources = []
        for node in nodes:
            nsource, ntarget = node
            if ntarget in current_sources:
                weights[nsource] = level + 1
                next_sources.append(nsource)
        current_sources = next_sources
        level += 1
    return weights

def get_parents(source, nodes):
    if source == 'COM':
        return []
    parents = []
    for node in nodes:
        nsource, ntarget = node
        if nsource == source:
            parents.append(ntarget)
            parents.extend(get_parents(ntarget, nodes))
    return parents


# Start
nodes = []
with open("input") as hand:
    for line in hand:
        target, source = line.strip().split(")")
        nodes.append((source, target))

weights = get_weights(nodes)
print(weights)

total_weights = 0
for source, weight in weights.items():
    total_weights += weight
print(total_weights)

san_parents = get_parents('SAN', nodes)
my_parents = get_parents('YOU', nodes)
max_weight = None
common_parents = []
for parent in my_parents:
    if parent in san_parents:
        common_parents.append(parent)
        # Common node
        if max_weight is None or weights[parent] > max_weight:
            max_weight = weights[parent]

print(weights['SAN'], '==', len(san_parents))
print(weights['YOU'], '==', len(my_parents))
diff = (weights['YOU'] - max_weight) + (weights['SAN'] - max_weight) - 2
print("Res", diff)
