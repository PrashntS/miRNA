import pandas as pd

from miriam import psql

ONT_FUNCTIONAL = pd.read_sql_table('ont_functions', psql, index_col='index').sort_index()
ONT_PID = pd.read_sql_table('ont_pw_PID', psql, index_col='index').sort_index()
ONT_MOL_FN = pd.read_sql_table('ont_molecular_fn', psql, index_col='index').sort_index()


class OntologyTransform:
  cardinality = None
  axes = None

  def __init__(self, x, cardinality=None):
    self.x = x
    if cardinality:
      self.cardinality = cardinality

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


class FunctionalOntologyTx(OntologyTransform):
  cardinality = len(ONT_FUNCTIONAL)
  axes = ONT_FUNCTIONAL.name.values

class PathwayPIDOntologyTx(OntologyTransform):
  cardinality = len(ONT_PID)
  axes = ONT_PID.name.values

class MolecularFnOntologyTx(OntologyTransform):
  cardinality = len(ONT_MOL_FN)
  axes = ONT_MOL_FN.name.values
