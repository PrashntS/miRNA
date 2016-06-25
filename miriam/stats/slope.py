import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findSystemFonts
import numpy as np
import pandas as pd
import os
import matplotlib.gridspec as gridspec
import math


def cubic(max_v):
  p0, p1, p2, p3 = (0, 0.1, 0.4, 1)
  def cubic_bezier(t_):
    t_ = t_ / max_v
    t = 1 - t_
    return (t_**3 * p0) + (3 * t * p1 * t_**2) + (3 * t**2 * t_ * p2) + (t**3 * p3)
  return cubic_bezier
  # return lambda x: max_v - x


def slope(lbls, vals,
      marker='%0.f',
      color=None,
      title='',
      savename='test2.png',
      dpi=300):

  font = FontProperties('Montserrat')
  font.set_size(5)
  bx = None
  # fn = cubic(vals.max().max() + 1)
  fn = math.log
  # df = data.copy().applymap(fn)
  df = vals.copy().applymap(fn)

  cols = df.columns
  data_range = [df.min().min(), df.max().max()]
  df['__label__'] = df.index
  df['__order__'] = range(len(df.index))

  width = (len(cols) - 1)
  height = 20

  f = plt.figure(figsize=(width, height), dpi=150)
  gs = gridspec.GridSpec(
    nrows=height,
    ncols=width,
    hspace=0,
    wspace=1
  )
  # gs.update(wspace=0, hspace=0.0)
  axarr = []
  axarr_X = []

  for i in range(len(cols) - 1):
    axarr.append(f.add_subplot(gs[:(height - 2), i]))
    axarr_X.append(f.add_subplot(gs[(height - 1), i]))
  # gs.tight_layout(f)

  axarr = np.array(axarr)
  axarr_X = np.array(axarr_X)
  renderer = f.canvas.get_renderer()

  fh = f.get_figheight()
  fw = f.get_figwidth()
  fdpi = f.get_dpi()

  nt = fh // (font.get_size() / 72) / 2
  res = np.diff(data_range)[0] / nt * 2

  if not hasattr(axarr, 'transpose'):
    axarr = [axarr]

  for i in range((len(cols) - 1)):
    ax = axarr[i]

    axarr_X[i].yaxis.set_tick_params(width=0, pad=0)
    axarr_X[i].xaxis.set_tick_params(width=0, pad=0)

    # labelsL = df.groupby(pd.cut(df[cols[i]], nt))['__label__'].agg(
    #   ', '.join).dropna()
    # labelsR = df.groupby(pd.cut(df[cols[i + 1]], nt))['__label__'].agg(
    #   ', '.join).dropna()

    # yPos_L = df.groupby(pd.cut(df[cols[i]],
    #                nt))[cols[i]].mean().dropna()
    # yPos_R = df.groupby(pd.cut(df[cols[i + 1]],
    #                nt))[cols[i + 1]].mean().dropna()

    # yMark_L = df.groupby(pd.cut(df[cols[i]],
    #               nt))[cols[i]].mean().dropna()
    # yMark_R = df.groupby(pd.cut(df[cols[i + 1]],
    #               nt))[cols[i + 1]].mean().dropna()

    commons = set(lbls[cols[i]]).intersection(lbls[cols[i + 1]])

    get_ix = lambda x, _: lbls[lbls[cols[x]] == _].index[0]
    get_iv = lambda x, _: df[cols[x]][get_ix(x, _)]

    yPos_ = list(zip(*[(get_iv(i, _), get_iv(i + 1, _)) for _ in commons]))

    # i_ixs = [is_ix(i, _) for _ in commons]
    # j_ixs = [lbls[lbls[cols[i + 1]] == _].index[0] for _ in commons]

    # yPos_ = df[[cols[i], cols[i + 1]]]


    # yPos_.columns = range(2)

    # print(yPos_)
    # print(yPos_.T)

    lines = ax.plot(yPos_, color='k', alpha=0.5)
    ax.spines['bottom'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')

    ax.set_xticklabels([])
    axarr_X[i].set_yticks([1])
    axarr_X[i].set_xticklabels([])
    axarr_X[i].set_yticklabels([str(cols[i])], fontproperties=font, ha='center')


    # labelsL_str = [item[1] + ('%f' % item[0]).rjust(6)
    #          for item in zip(yMark_L.values, labelsL.values)]
    # labelsR_str = [('%f' % item[0]).ljust(6) + item[1]
    #          for item in zip(yMark_R.values, labelsR.values)]
    # ylabelsL_str = map(lambda el: '%f' % el, yMark_L.values)
    # ylabelsR_str = map(lambda el: '%f' % el, yMark_R.values)

    # if i == 0:
    #   ax.set_yticks(yPos_L.values)
    #   ax.set_yticklabels(labelsL_str, fontproperties=font)
    # elif marker:

    ax.set_yticks(df[cols[i]].values)
    ax.set_yticklabels(lbls[cols[i]].values,
               fontproperties=font,
               ha='right',
               alpha=0.5
               )  #ha='center')#,backgroundcolor='w')

    ax.set_ybound(data_range)
    ax.yaxis.set_tick_params(width=0, pad=0)
    ax.set_xbound((0, 1))
    ax.set_aspect('auto')


    # else:
    #   plt.setp(ax.get_yticklabels(), visible=False)
    #   wspace = 0

    if i == len(cols) - 2:
      bx = ax.twinx()

      bx.set_ybound(data_range)
      # bx.set_yticks(yPos_R.values)
      # bx.set_yticklabels(labelsR_str, fontproperties=font)
      bx.yaxis.set_tick_params(width=0, pad=0)

      bx_X = axarr_X[i].twinx()
      bx_X.set_xticklabels([])
      bx_X.set_yticks([1])
      bx_X.yaxis.set_tick_params(width=0, pad=0)
      bx_X.set_yticklabels([str(cols[i + 1])], fontproperties=font)


    if color:

      for tl in ax.yaxis.get_ticklabels():
        try:
          for kw, c in color.items():

            if kw in tl.get_text():
              tl.set_color(c)

        except:
          print('fail')
          pass
      if bx:
        for tl in bx.yaxis.get_ticklabels():
          try:
            for kw, c in color.items():

              if kw in tl.get_text():
                tl.set_color(c)
          except:
            pass

    if color:
      for kw, c in color.items():
        for j, lab__ in enumerate(yPos_.index):
          if kw in lab__:
            lines[j].set_color(c)
            lines[j].set_linewidth(2)
            lines[j].set_alpha(0.6)

            for kk, tic_pos in enumerate(
              ax.yaxis.get_ticklocs()):

              if yPos_.values[j][0] == tic_pos:

                ax.yaxis.get_ticklabels()[kk].set_color(c)

    # ax.yaxis.set_tick_params(width=0, pad=0)
    # ax.xaxis.set_tick_params(width=0, pad=0)
    # print(dir(ax))

    # ax.xaxis.grid(True)

  f.suptitle(title, x=0.5, y=0.02, fontproperties=font)

  for ax in f.axes:
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

  tw = ax.yaxis.get_text_widths(renderer)[0]
  # if wspace == 0:
  #   pass
  # else:
  # aw = ax.get_tightbbox(renderer).width
  # wspace = tw / aw * 1.4
  f.subplots_adjust(wspace=0, hspace=10)
  # f.subplots_adjust(wspace=0, hspace=0, left=0, right=1)
  if savename:
    f.savefig(savename, dpi=dpi)

  return f

