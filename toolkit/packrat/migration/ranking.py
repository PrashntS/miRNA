#!/usr/bin/env python
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

import pickle
import transaction

from packrat import db, logger

def register_precomputed_ranking(datasets):
  """
  Register the Ranks in MongoDB and corresponding Rank object in ZeoDB.
  """
  persistent_obj = {}
  for dataset in datasets:
    path = dataset['path']
    uid = dataset['cid']
    dbname = 'ranking_' + uid
    dataset['db'] = dbname
    rnk_db = db[dbname]
    rnk_db.drop()

    with open(path, 'rb') as m:
      df = pickle.load(m)

    encd = lambda x: x if type(x) is str else float(x)

    docs = []
    for i in range(1, len(df) + 1):
      updt = {'MIRNA': df['MIRNA'][i], 'TARGET': df['TARGET'][i]}
      doc = {_: encd(df[_][i]) for _ in df.columns}
      doc['INDEX'] = i
      docs.append(doc)

    rnk_db.insert_many(docs, ordered=False)

    db['rank_meta'].update({'cid': uid}, dataset, True)
    logger.info("Ranking Object {0} Registered.".format(uid))

  logger.info("Ranking Migration Complete.")
