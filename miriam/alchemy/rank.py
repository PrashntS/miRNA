import pandas as pd

from miriam import db, psql
from miriam.logger import logger
from miriam.alchemy.utils import mproperty

collection = db['expre_meta']


class Tissue(object):
  """Convinience Wrapper for Tissue data

  Args:
    - namespace (str)
    - tissue_id (str)
  """

  def __init__(self, id):
    self.id = id
    self.namespace, self.tissue_id = id.split('-')
    self.__init_tissue()

  def __init_tissue(self):
    doc = collection.find_one({'namespace': self.namespace})
    if doc is None:
      raise KeyError('Incorrect namespace value.')

    if self.tissue_id not in doc['tissues']:
      raise KeyError(
        'Tissue `{0}` is not present in given namespace'.format(self.tissue_id)
      )

    self._db_name = doc['db']

  def __get_expressions(self):
    q = 'select gene_name, {0} from {1}'.format(self.tissue_id, self._db_name)
    self.__expr = pd.read_sql_query(q, psql)
    return self.__expr

  def __str__(self):
    return '<Tissue: {0}, Experiment: {1}>'.format(
        self.tissue_id,
        self.namespace)

  def __repr__(self):
    return str(self)

  @property
  def repr(self):
    return {
      'id': self.id,
      'namespace': self.namespace,
      'tissue_id': self.tissue_id,
    }

  @property
  def expression(self):
    try:
      return self.__expr
    except AttributeError:
      return self.__get_expressions()


class TissueCollection(object):
  def __init__(self):
    self._tissues = []
    for doc in collection.find():
      self._tissues.extend(
        ['{0}-{1}'.format(doc['namespace'], _) for _ in doc['tissues']]
      )

  def __getitem__(self, i):
    return Tissue(self._tissues[i])

  def __contains__(self, i):
    return i in self._tissues

  def __iter__(self):
    for i in range(len(self._tissues)):
      yield self[i]

  def __repr__(self):
    return ', '.join([str(_) for _ in self])

  def __len__(self):
    return len(self._tissues)

  @property
  def repr(self):
    return [_.repr for _ in self]


class Frame(object):
  def __init__(self, tissue):
    if type(tissue) is str:
      tissue = Tissue(tissue)
    self.tissue = tissue

  @mproperty
  def ontology(self):
    return pd.read_sql_table('gene', psql)

  @mproperty
  def network(self):
    '''Return network edge'''
    logger.debug('[Frames] Reading NW DG')
    ntwkdg = pd.read_sql_table('ntwkdg', psql)
    mirnas = pd.read_sql_table('mirna', psql)
    merged = ntwkdg.merge(mirnas, left_on='mirna', right_on='symbol')
    del merged['symbol']
    merged = merged[['mirna', 'gene', 'host', 'dg']]
    return merged

  @mproperty
  def merged(self):
    '''Merge Tissue Expression Values with the Network'''
    logger.debug('[Frames] Merging expression with NW')
    merge_target = self.network.merge(
      self.tissue.expression,
      left_on='gene',
      right_on='gene_name')
    del merge_target['gene_name']
    merge_target = merge_target.rename(columns={
      self.tissue.tissue_id: 'exp_gene'
    })
    merge_host = merge_target.merge(
      self.tissue.expression,
      left_on='host',
      right_on='gene_name')
    del merge_host['gene_name']
    merge_host = merge_host.rename(columns={self.tissue.tissue_id: 'exp_host'})

    logger.debug('[Frames] Merging ontology')
    merge_ontology_gene = merge_host.merge(self.ontology,
      left_on='gene',
      right_on='symbol')
    del merge_ontology_gene['symbol']
    merge_ontology_host = merge_ontology_gene.merge(self.ontology,
      left_on='host',
      right_on='symbol')
    del merge_ontology_host['symbol']

    return merge_ontology_host

  @mproperty
  def diseases(self):
    logger.debug('[Diseases] Reading DB')
    return (pd.read_sql_table('d_disgenenet', psql)
        .rename(columns=dict(geneName='gene', diseaseName='disease')))

  @mproperty
  def filtered(self):
    return self.merged.query('exp_host > 1 and exp_gene > 1')
