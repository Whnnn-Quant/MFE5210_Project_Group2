# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import copy as c
from matplotlib import pyplot as plt
import matplotlib as mpl
import statsmodels.api as sm

import warnings

warnings.filterwarnings('ignore')
plt.style.use('ggplot')
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['font.serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False


# %%
# 海龟策略
def turtle(back_df, proxy, roll=20, bar=20):
    new_df = back_df.copy()
    new_df[proxy] = new_df[proxy].rolling(roll).mean()

    new_df['min'] = new_df[proxy].rolling(bar).min()
    new_df['max'] = new_df[proxy].rolling(bar).max()
    new_df['pos'] = np.where(new_df[proxy] >= new_df['max'].shift(1), 1, np.nan)
    new_df['pos'] = np.where(new_df[proxy] <= new_df['min'].shift(1), -1, new_df['pos'])
    new_df['pos'].ffill(inplace=True)

    return new_df['pos'].values


# %%
# 获取主力合约行情
df_T = pd.read_csv('主力合约行情.csv', index_col=0)
df_T.set_index('trade_date', inplace=True)
df_T.index = pd.to_datetime(df_T.index)

# %%
# 计算复权价格
df_T['adj_vwap'] = df_T['vwap'] * df_T['adj_factor']
df_T['adj_close'] = df_T['close'] * df_T['adj_factor']
df_T['adj_low'] = df_T['low'] * df_T['adj_factor']
df_T['adj_high'] = df_T['high'] * df_T['adj_factor']

# %%
# 算法挖掘因子
# 都是有用且符合逻辑的因子，但需要关注如何进行组合和加权
df_T['fac1'] = (df_T.high.diff() - df_T.high.diff().rolling(5).mean()) / df_T.high.diff().rolling(5).std()
df_T['fac2'] = df_T.low.diff() + df_T.open.diff()
df_T['fac3'] = np.sqrt(df_T.oi.rolling(10).corr(df_T.low)).fillna(0)
df_T['fac4'] = np.log(df_T.high.div(df_T.close).diff()).fillna(0).diff()
df_T['fac5'] = np.sqrt(df_T.amount.rolling(20).corr(df_T.open)).fillna(0)
df_T['fac6'] = np.sqrt((df_T.vol / df_T.oi.diff().abs()).rolling(60).corr(df_T.close /
                                                                          df_T.open - 1)).fillna(0)

# 因子1/2/4为动量, 因子3/5/6为反转
# pos_gp为每个因子给出的信号
df_T['pos_gp1'] = turtle(df_T, 'fac1', roll=1, bar=20)
df_T['pos_gp2'] = turtle(df_T, 'fac2', roll=1, bar=20)
df_T['pos_gp3'] = -turtle(df_T, 'fac3', roll=1, bar=5)
df_T['pos_gp4'] = turtle(df_T, 'fac4', roll=1, bar=120)
df_T['pos_gp5'] = -turtle(df_T, 'fac5', roll=1, bar=20)
df_T['pos_gp6'] = -turtle(df_T, 'fac6', roll=1, bar=40)

# 大类内部等权
df_T['pos_mom_eq'] = np.sign(df_T[['pos_gp1', 'pos_gp2', 'pos_gp4']].sum(axis=1))
df_T['pos_rev_eq'] = np.sign(df_T[['pos_gp3', 'pos_gp5', 'pos_gp6']].sum(axis=1))

# %%
# 计算价格噪音
N, k = 5, 3
df_T['ER'] = df_T['adj_close'].diff(N).abs() / \
             (df_T['adj_close'].diff().abs().rolling(N).sum())

# df_T['ER'] = (df_T['high'].rolling(N).max()-
#               df_T['low'].rolling(N).min())/\
#             (df_T['high']-df_T['low']).rolling(N).sum()

df_T['TNR1'] = df_T['ER'] - df_T['ER'].shift(k)
df_T['TNR2'] = df_T['ER'] - df_T['ER'].rolling(k).mean()
df_T['TNR'] = np.sign(df_T[['TNR1', 'TNR2']].sum(axis=1))

# %%
# 噪音增加时，采用反转信号
# 噪音减少时，采用趋势信号
df_T['new_pos'] = np.where(((df_T['TNR2'] > 0) & (df_T['TNR2'].shift(1) > 0)) |
                           (df_T['ER'] >= 0.75),
                           df_T['pos_mom_eq'],
                           df_T['pos_rev_eq'])
