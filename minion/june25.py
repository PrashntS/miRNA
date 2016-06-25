# Agora NHS
import json
import numpy
import numpy.linalg
import pandas as pd

from miriam.network import g


def unit_scale(x):
  L1 = numpy.linalg.norm(x, ord=1)
  if L1 > 0:
    return x / L1
  else:
    return numpy.zeros_like(x)


def proc_row(row, pivot):
  print("Processing")
  add_label = lambda x: list(zip(pivot, x))
  row_s = {_: unit_scale(row[_]) for _ in row}
  row_matrix = numpy.array(list(row_s.values()))
  mean_ranks = numpy.mean(row_matrix, axis=0)

  labeled_ranks = add_label(mean_ranks)
  labeled_ranks.sort(key=lambda x: x[1], reverse=True)

  axes_labels = [_[0] for _ in labeled_ranks]

  row_s_rearranged = {}

  row_f = pd.DataFrame(index=[_[0] for _ in labeled_ranks], columns=row_s.keys())
  row_f['mean'] = list(range(len(labeled_ranks)))#[_[1] for _ in labeled_ranks]

  for k, v in row_s.items():
    lbd = add_label(v)
    lbd.sort(key=lambda x: x[1], reverse=True)
    lbdi = {_[0]: i for i, _ in enumerate(lbd)}

    row_f[k] = [lbdi[_] for _ in row_f.index]
    # ranks = {}
    # for i, v in enumerate(lbd):
    #   row_f.loc[v[0], k] = i

  return row_f

if __name__ == '__main__':
  with open('/data/miriam.out.json', 'r') as f:
    d = json.load(f)

  proc_row({k: d[k]['mirnas'] for k in d}, g.mirnas).to_pickle('miriam.out.mirnas.pkl')
  proc_row({k: d[k]['genes'] for k in d}, g.genes).to_pickle('miriam.out.genes.pkl')

  # gene_trnk, gene_mrnk = proc_row({k: d[k]['genes'] for k in d}, g.genes)
  # mirna_trnk = proc_row({k: d[k]['mirnas'] for k in d}, g.mirnas)

  # with open('/data/miriam.out.two.json', 'r') as f:
  #   e = json.load(f)

  # intrn_trnk, intrn_mrnk = proc_row({k: e[k] for k in e}, g.interaction_hash())

  # with open('/data/miriam.super.gene.json', 'w') as f:
  #   json.dump({
  #     'gene_mean_ranks': gene_mrnk,
  #     'gene_tissue_ranks': gene_trnk,
  #   }, f)

  # with open('/data/miriam.super.mirna.json', 'w') as f:
  #   json.dump({
  #     'mirna_mean_ranks': mirna_mrnk,
  #     'mirna_tissue_ranks': mirna_trnk,
  #   }, f)

  # with open('/data/miriam.super.interaction.json', 'w') as f:
  #   json.dump({
  #     'interation_mean_ranks': intrn_mrnk,
  #     'interaction_tissue_ranks': intrn_trnk,
  #   }, f)

