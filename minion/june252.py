import pandas as pd
from miriam.stats.slope import slope

if __name__ == '__main__':
  df1, df2 = [_[0] for _ in pd.read_pickle('miriam.out.genes.pkl').values]
  # cols = ['mean'] + list(df1.columns[:20])
  cols = df1.columns
  label, values = df1.loc[:,cols], df2.loc[:,cols]
  sl = slope(label, values)
  # print(dat)
