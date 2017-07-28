import numpy as np

flatten = lambda x: (x[0][0], x[0][1], x[1])

def index_map_transform(adj):
  return list(map(flatten, np.ndenumerate(adj)))


def sankey_transform(adj, transform):
  fmt_link = lambda x: {'source': 'x_%d' % x[0], 'target': 'y_%d' % x[1], 'value': x[2]}

  nodes = []
  for prefix in ['x_', 'y_']:
    nodes += [{'name': '{}{}'.format(prefix, i)} for i in range(transform.cardinality)]

  links = list(map(fmt_link, index_map_transform(adj)))
  labels = transform.axes.tolist()

  return {'nodes': nodes, 'links': links, 'labels': labels}
