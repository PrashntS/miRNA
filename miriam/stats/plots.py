import numpy as np
import math

from tqdm import tqdm
from PIL import Image
from matplotlib import colors, cm
from miriam.network import g

l_mir = len(g.mirnas)
l_gen = len(g.genes)
ix_mir = dict(zip(g.mirnas, range(l_mir)))
ix_gen = dict(zip(g.genes, range(l_gen)))

def transform(frame):
  adj = np.zeros((l_mir, l_gen))
  for _, row in frame.iterrows():
    i_m = ix_mir[row.mirna]
    i_g = ix_gen[row.gene]
    adj[i_m][i_g] = row.score
  return adj


CMAP = 'YlGn'

def get_cmap(vmax):
  norm = colors.Normalize(vmin=0, vmax=vmax)
  return cm.ScalarMappable(norm=norm, cmap=CMAP)

# def plot_lines(mat, cmap):
#   print('Plotting!')
#   for row in tqdm(mat):
#     box_row = []
#     for col in row:
#       *rgb, _ = cmap.to_rgba(col)
#       box_row.extend(rgb)
#     yield box_row

def to_bit(f):
  return math.floor(255 if f == 1.0 else f * 256.0)

to_bit = np.vectorize(to_bit, otypes=[np.int])


def make_png(filename, frame):
  # img = Image.new('RGB', (l_mir, l_gen), 'white')
  # pixels = img.load()

  max_val = frame.score.max()
  adj_mat = transform(frame)
  cmap = get_cmap(max_val)

  print('impx')
  imgpixels = cmap.to_rgba(adj_mat, bytes=True)[:,:,:3]
  print('impx ok')

  img = Image.fromarray(imgpixels, mode='RGB')
  img.save('{}.png'.format(filename))
  return

