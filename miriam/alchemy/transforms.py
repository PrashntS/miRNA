import pandas as pd

from miriam import psql

ONT_FUNCTIONAL = pd.read_sql_table('ont_functions', psql, index_col='index')


class OntologyTransform:
  cardinality = None
  axes = None

  def __init__(self, x):
    self.x = x

  def to_int(self):
    return int(self.x, 16) if type(self.x) is str else self.x

  def __and__(self, y):
    return OntologyTransform(self.to_int() & y.to_int())

  @property
  def hamming_weight(self):
    return str(bin(self.to_int())).count('1')

  @property
  def row(self):
    row = list(map(int, bin(self.to_int())[2:]))
    if self.cardinality and len(row) < self.cardinality:
      pad_count = self.cardinality - len(row)
      row += [0 for _ in range(pad_count)]
    return row


class FunctionalOntologyTransform(OntologyTransform):
  cardinality = len(ONT_FUNCTIONAL)
  axes = ONT_FUNCTIONAL.name.values
