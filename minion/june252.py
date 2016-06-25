import pandas as pd
from miriam.stats.slope import slope

if __name__ == '__main__':
  df = pd.read_pickle('miriam.out.mirnas.pkl')
  cols = ['mean'] + list(df.columns[:40])
  dat = df.loc[:,cols][:100]
  sl = slope(dat)
  # print(dat)
