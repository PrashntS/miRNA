# Agora NHS
import pickle
import yaml

from tqdm import tqdm
from miriam.stats.rank import Score_K_O_D


with open('tissues.chosen.yaml', 'r') as fl:
  tissues = yaml.load(fl)


if __name__ == '__main__':
  out = []
  for tissue in tqdm(tissues):
    stack = Score_K_O_D(tissue)
    out.append(stack.report())

  with open('/data/miriam.reports.pkl', 'wb') as fl:
    pickle.dump(out, fl)
