from Dependency import *

class Strategy_MoM_20d(Strategy):

    def __init__(self, engine):
        super().__init__(engine)
        
        self.signals = []
        self.all_signals = []
        self.previous_row = None
        self.entry_price = None  # 记录建仓价格
        self.date_list = list(self.engine.data.index.unique())

    def cal_std(self,series):
        sqrt_sum = (series**2).sum()
        return np.sqrt(sqrt_sum) 

    def on_init(self):
        
        self.engine.data['ret_1d'] = self.engine.data['close'].pct_change(1).fillna(0)
        self.engine.data['vol_3d'] = self.engine.data['ret_1d'].rolling(4).apply(lambda x: self.cal_std(x[:-1]))
        self.engine.data['vol_5d'] = self.engine.data['ret_1d'].rolling(6).apply(lambda x: self.cal_std(x[:-1]))
        self.engine.data['vol_10d'] = self.engine.data['ret_1d'].rolling(11).apply(lambda x: self.cal_std(x[:-1]))
        self.engine.data['vol_20d'] = self.engine.data['ret_1d'].rolling(21).apply(lambda x: self.cal_std(x[:-1]))
        self.engine.data['vol_adj'] = (self.engine.data['vol_5d'] + self.engine.data['vol_10d'] + self.engine.data['vol_3d']+self.engine.data['vol_20d']) / 4

        self.engine.data['vol_5d_now'] = self.engine.data['ret_1d'].rolling(5).apply(self.cal_std)
        self.engine.data['vol_10d_now'] = self.engine.data['ret_1d'].rolling(10).apply(self.cal_std)
        self.engine.data['vol_3d_now'] = self.engine.data['ret_1d'].rolling(3).apply(self.cal_std)
        self.engine.data['vol_20d_now'] = self.engine.data['ret_1d'].rolling(20).apply(self.cal_std)
        self.engine.data['vol_adj_now'] = (self.engine.data['vol_5d_now'] + self.engine.data['vol_10d_now'] + self.engine.data['vol_3d_now'] + self.engine.data['vol_20d_now']) / 4

        # 计算Open2OpenRets
        self.engine.data['O2O_ret'] = self.engine.data['open'].pct_change().fillna(0)

        self.engine.data['cumsum_ret_20d'] = self.engine.data['ret_1d'].rolling(20).sum()
        self.engine.data['cumsum_ret_10d'] = self.engine.data['ret_1d'].rolling(20).sum()

    def on_bar(self, row):
        # 生成交易信号
        now_date = row.name
        now_index = self.date_list.index(now_date)
        next_date = self.date_list[now_index+1] if now_index + 1 < len(self.date_list) else None

        for signal in list(self.signals):
            signal_date, signal_type = signal
            if signal_date:
                if row.name.date() == signal_date.date():
                    if signal_type == 'BUY':
                        self.buy(row['open'], abs(self.quantity - self.pos), row.name)
                        self.pos = self.quantity
                        self.entry_price = row['open']
                    elif signal_type == 'SELL':
                        self.sell(row['open'], abs(self.quantity + self.pos), row.name)
                        self.pos = -self.quantity
                        self.entry_price = row['open']
                    
                    self.signals.remove(signal)

        self.quantity = 1

        if row['cumsum_ret_20d']>=0:
            self.signals.append((next_date, 'BUY'))
            self.all_signals.append((next_date, 'BUY'))
        elif row['cumsum_ret_20d']<0:
            self.signals.append((next_date, 'SELL'))
            self.all_signals.append((next_date, 'SELL'))

class Strategy_MA_5_20(Strategy):
    """
    规则型趋势跟踪策略
    """
    def __init__(self, engine):
        super().__init__(engine)
        self.posi_days = 0
        self.signals = []
        self.all_signals = []
        self.previous_row = None
        self.entry_price = None  # 记录建仓价格
        self.date_list = list(self.engine.data.index.unique())

    def cal_std(self,series):
        sqrt_sum = (series**2).sum()
        return np.sqrt(sqrt_sum) 

    def on_init(self):
        
        # 普通均线
        self.engine.data['ma2'] = self.engine.data['close'].rolling(window=2).mean()
        self.engine.data['ma3'] = self.engine.data['close'].rolling(window=3).mean()
        self.engine.data['ma4'] = self.engine.data['close'].rolling(window=4).mean()
        self.engine.data['ma5'] = self.engine.data['close'].rolling(window=5).mean()
        self.engine.data['ma10'] = self.engine.data['close'].rolling(window=10).mean()
        self.engine.data['ma20'] = self.engine.data['close'].rolling(window=20).mean()

        self.engine.data['pre1_ma3'] = self.engine.data['ma3'].shift(1)
        self.engine.data['pre2_ma3'] = self.engine.data['ma3'].shift(2)
        self.engine.data['pre3_ma3'] = self.engine.data['ma3'].shift(3)
        self.engine.data['pre4_ma3'] = self.engine.data['ma3'].shift(4)

        self.engine.data['pre1_ma5'] = self.engine.data['ma5'].shift(1)
        self.engine.data['pre2_ma5'] = self.engine.data['ma5'].shift(2)
        self.engine.data['pre3_ma5'] = self.engine.data['ma5'].shift(3)
        self.engine.data['pre4_ma5'] = self.engine.data['ma5'].shift(4)

        self.engine.data['pre1_ma10'] = self.engine.data['ma10'].shift(1)
        self.engine.data['pre2_ma10'] = self.engine.data['ma10'].shift(2)
        self.engine.data['pre3_ma10'] = self.engine.data['ma10'].shift(3)
        self.engine.data['pre4_ma10'] = self.engine.data['ma10'].shift(4)

        self.engine.data['vv'] = self.engine.data[['close','open','high','low']].mean(axis=1)

        self.engine.data['vv_ma3'] = self.engine.data['vv'].rolling(3).mean()
        self.engine.data['vv_ma5'] = self.engine.data['vv'].rolling(5).mean()
        self.engine.data['vv_ma10'] = self.engine.data['vv'].rolling(10).mean()

        self.engine.data['high_ma3'] = self.engine.data['high'].rolling(3).mean()
        self.engine.data['low_ma3'] = self.engine.data['low'].rolling(3).mean()

        self.engine.data['pre1_vv'] = self.engine.data['vv'].shift(1)
        self.engine.data['pre2_vv'] = self.engine.data['vv'].shift(2)
        self.engine.data['pre3_vv'] = self.engine.data['vv'].shift(3)
        self.engine.data['pre4_vv'] = self.engine.data['vv'].shift(4)
        self.engine.data['pre5_vv'] = self.engine.data['vv'].shift(5)
        self.engine.data['pre6_vv'] = self.engine.data['vv'].shift(6)

        self.engine.data['pre1_close'] = self.engine.data['close'].shift(1)
        self.engine.data['pre2_close'] = self.engine.data['close'].shift(2)
        self.engine.data['pre3_close'] = self.engine.data['close'].shift(3)
        self.engine.data['pre4_close'] = self.engine.data['close'].shift(4)

        self.engine.data['pre1_high'] = self.engine.data['high'].shift(1)
        self.engine.data['pre2_high'] = self.engine.data['high'].shift(2)
        self.engine.data['pre3_high'] = self.engine.data['high'].shift(3)
        self.engine.data['pre4_high'] = self.engine.data['high'].shift(4)

        self.engine.data['pre1_low'] = self.engine.data['low'].shift(1)
        self.engine.data['pre2_low'] = self.engine.data['low'].shift(2)
        self.engine.data['pre3_low'] = self.engine.data['low'].shift(3)
        self.engine.data['pre4_low'] = self.engine.data['low'].shift(4)

        # 10日布林带
        self.engine.data['boll_10_up_0p5'] = self.engine.data['vv_ma10'] + 0.5 * self.engine.data['vv'].rolling(window=10).std()
        self.engine.data['boll_10_up_1p0'] = self.engine.data['vv_ma10'] + 1 * self.engine.data['vv'].rolling(window=10).std()
        self.engine.data['boll_10_up_1p5'] = self.engine.data['vv_ma10'] + 1.5 * self.engine.data['vv'].rolling(window=10).std()
        self.engine.data['boll_10_up_2p0'] = self.engine.data['vv_ma10'] + 2 * self.engine.data['vv'].rolling(window=10).std()
        self.engine.data['boll_10_up_2p5'] = self.engine.data['vv_ma10'] + 2.5 * self.engine.data['vv'].rolling(window=10).std()
        self.engine.data['boll_10_up_3p0'] = self.engine.data['vv_ma10'] + 3 * self.engine.data['vv'].rolling(window=10).std()

        self.engine.data['boll_10_down_0p5'] = self.engine.data['vv_ma10'] - 0.5 * self.engine.data['vv'].rolling(window=10).std()
        self.engine.data['boll_10_down_1p0'] = self.engine.data['vv_ma10'] - 1 * self.engine.data['vv'].rolling(window=10).std()
        self.engine.data['boll_10_down_1p5'] = self.engine.data['vv_ma10'] - 1.5 * self.engine.data['vv'].rolling(window=10).std()
        self.engine.data['boll_10_down_2p0'] = self.engine.data['vv_ma10'] - 2 * self.engine.data['vv'].rolling(window=10).std()
        self.engine.data['boll_10_down_2p5'] = self.engine.data['vv_ma10'] - 2.5 * self.engine.data['vv'].rolling(window=10).std()
        self.engine.data['boll_10_down_3p0'] = self.engine.data['vv_ma10'] - 3 * self.engine.data['vv'].rolling(window=10).std()

        # 5日布林带
        self.engine.data['boll_5_up_0p5'] = self.engine.data['vv_ma5'] + 0.5 * self.engine.data['vv'].rolling(window=20).std()
        self.engine.data['boll_5_up_1p0'] = self.engine.data['vv_ma5'] + 1 * self.engine.data['vv'].rolling(window=20).std()
        self.engine.data['boll_5_up_1p5'] = self.engine.data['vv_ma5'] + 1.5 * self.engine.data['vv'].rolling(window=20).std()
        self.engine.data['boll_5_up_2p0'] = self.engine.data['vv_ma5'] + 2 * self.engine.data['vv'].rolling(window=20).std()
        self.engine.data['boll_5_up_2p5'] = self.engine.data['vv_ma5'] + 2.5 * self.engine.data['vv'].rolling(window=20).std()
        self.engine.data['boll_5_up_3p0'] = self.engine.data['vv_ma5'] + 3 * self.engine.data['vv'].rolling(window=20).std()


        self.engine.data['boll_5_down_0p5'] = self.engine.data['vv_ma5'] - 0.5 * self.engine.data['vv'].rolling(window=20).std()
        self.engine.data['boll_5_down_1p0'] = self.engine.data['vv_ma5'] - 1 * self.engine.data['vv'].rolling(window=20).std()
        self.engine.data['boll_5_down_1p5'] = self.engine.data['vv_ma5'] - 1.5 * self.engine.data['vv'].rolling(window=20).std()
        self.engine.data['boll_5_down_2p0'] = self.engine.data['vv_ma5'] - 2 * self.engine.data['vv'].rolling(window=20).std()
        self.engine.data['boll_5_down_2p5'] = self.engine.data['vv_ma5'] - 2.5 * self.engine.data['vv'].rolling(window=20).std()
        self.engine.data['boll_5_down_3p0'] = self.engine.data['vv_ma5'] - 3 * self.engine.data['vv'].rolling(window=20).std()

        self.engine.data['bias3'] = ((self.engine.data['close'] - self.engine.data['ma3'])/ self.engine.data['ma3']) * 100
        self.engine.data['bias5'] = ((self.engine.data['close'] - self.engine.data['ma5'])/ self.engine.data['ma5']) * 100
        self.engine.data['bias10'] = ((self.engine.data['close'] - self.engine.data['ma10'])/ self.engine.data['ma10']) * 100
        self.engine.data['bias20'] = ((self.engine.data['close'] - self.engine.data['ma20'])/ self.engine.data['ma20']) * 100

        self.engine.data['bias5_open'] = ((self.engine.data['open'] - self.engine.data['ma5'])/ self.engine.data['ma5']) * 100
        self.engine.data['bias5_high'] = ((self.engine.data['high'] - self.engine.data['ma5'])/ self.engine.data['ma5']) * 100
        self.engine.data['bias5_low'] = ((self.engine.data['low'] - self.engine.data['ma5'])/ self.engine.data['ma5']) * 100

        self.engine.data['delta_abs_bias5'] = abs(self.engine.data['bias5_high'] - self.engine.data['bias5_low'])
        self.engine.data['delta_abs_bias5_up_bound'] = self.engine.data['delta_abs_bias5'].rolling(10).mean() + 1.5 * self.engine.data['delta_abs_bias5'].rolling(10).std()

        self.engine.data['pre1_bias10'] = self.engine.data['bias10'].shift(1)
        self.engine.data['pre2_bias10'] = self.engine.data['bias10'].shift(2)
        self.engine.data['pre3_bias10'] = self.engine.data['bias10'].shift(3)
        self.engine.data['pre4_bias10'] = self.engine.data['bias10'].shift(4)

        self.engine.data['pre1_bias5'] = self.engine.data['bias5'].shift(1)
        self.engine.data['pre2_bias5'] = self.engine.data['bias5'].shift(2)
        self.engine.data['pre3_bias5'] = self.engine.data['bias5'].shift(3)
        self.engine.data['pre4_bias5'] = self.engine.data['bias5'].shift(4)

        self.engine.data['pre1_bias3'] = self.engine.data['bias3'].shift(1)
        self.engine.data['pre2_bias3'] = self.engine.data['bias3'].shift(2)

        self.engine.data['diff_bias5'] = abs(self.engine.data['bias5'] - self.engine.data['pre1_bias5'])
        self.engine.data['diff_bias5_up_bound'] = self.engine.data['diff_bias5'].rolling(10).mean() + 1.5 * self.engine.data['diff_bias5'].rolling(10).std()

        self.engine.data['diff_bias5_2'] = abs(self.engine.data['bias5'] - self.engine.data['pre2_bias5'])
        self.engine.data['diff_bias5_up_bound_2'] = self.engine.data['diff_bias5_2'].rolling(10).mean() + 1.5 * self.engine.data['diff_bias5_2'].rolling(10).std()

        self.engine.data['bias5_10d_max'] = abs(self.engine.data['bias5']).rolling(10).max()
        self.engine.data['bias5_10d_min'] = abs(self.engine.data['bias5']).rolling(10).min()

        self.engine.data['bias5_20d_max'] = abs(self.engine.data['bias5']).rolling(20).max()
        self.engine.data['bias5_20d_min'] = abs(self.engine.data['bias5']).rolling(20).min()

        self.engine.data['bias5_up_bound'] = abs(self.engine.data['bias5']).rolling(10).mean() + 1.5 * abs(self.engine.data['bias5']).rolling(10).std()

        self.engine.data['bias5_up_bound_10d'] = abs(self.engine.data['bias5']).rolling(10).mean() + 1.5 * abs(self.engine.data['bias5']).rolling(10).std()
        self.engine.data['bias5_up_bound_20d'] = abs(self.engine.data['bias5']).rolling(20).mean() + 2 * abs(self.engine.data['bias5']).rolling(20).std()

        self.engine.data['bias10_up_bound_10d'] = abs(self.engine.data['bias10']).rolling(10).mean() + 1.5 * abs(self.engine.data['bias10']).rolling(10).std()
        self.engine.data['delta_abs_bias5_up_bound_10d'] = abs(self.engine.data['delta_abs_bias5']).rolling(10).mean() + 1.5 * abs(self.engine.data['delta_abs_bias5']).rolling(10).std()

        self.engine.data['bias5_10'] = ((self.engine.data['ma5'] - self.engine.data['ma10'])/ self.engine.data['ma5']) * 100
        self.engine.data['pre1_bias5_10'] = self.engine.data['bias5_10'].shift(1)

        self.engine.data['bias5_percentile_98'] = abs(self.engine.data['bias5']).rolling(window=50, min_periods=1).quantile(0.98)
        self.engine.data['bias5_percentile_95'] = abs(self.engine.data['bias5']).rolling(window=50, min_periods=1).quantile(0.95)
        self.engine.data['bias5_percentile_90'] = abs(self.engine.data['bias5']).rolling(window=50, min_periods=1).quantile(0.9)
        self.engine.data['bias5_percentile_85'] = abs(self.engine.data['bias5']).rolling(window=50, min_periods=1).quantile(0.85)

        self.engine.data['bias10_percentile_98'] = abs(self.engine.data['bias10']).rolling(window=50, min_periods=1).quantile(0.98)
        self.engine.data['bias10_percentile_95'] = abs(self.engine.data['bias10']).rolling(window=50, min_periods=1).quantile(0.95)
        self.engine.data['bias10_percentile_90'] = abs(self.engine.data['bias10']).rolling(window=50, min_periods=1).quantile(0.9)
        self.engine.data['bias10_percentile_85'] = abs(self.engine.data['bias10']).rolling(window=50, min_periods=1).quantile(0.85)

        self.engine.data['delta_abs_bias5_percentile_98'] = abs(self.engine.data['delta_abs_bias5']).rolling(window=50, min_periods=1).quantile(0.98)
        self.engine.data['delta_abs_bias5_percentile_95'] = abs(self.engine.data['delta_abs_bias5']).rolling(window=50, min_periods=1).quantile(0.95)
        self.engine.data['delta_abs_bias5_percentile_90'] = abs(self.engine.data['delta_abs_bias5']).rolling(window=50, min_periods=1).quantile(0.90)
        
        self.engine.data['diff_bias5_50d_max'] = abs(self.engine.data['diff_bias5']).rolling(window=50, min_periods=1).max()
        self.engine.data['diff_bias5_percentile_98'] = abs(self.engine.data['diff_bias5']).rolling(window=50, min_periods=1).quantile(0.98)
        self.engine.data['diff_bias5_percentile_95'] = abs(self.engine.data['diff_bias5']).rolling(window=50, min_periods=1).quantile(0.95)
        self.engine.data['diff_bias5_percentile_90'] = abs(self.engine.data['diff_bias5']).rolling(window=50, min_periods=1).quantile(0.90)


        # 计算Open2OpenRets
        self.engine.data['O2O_ret'] = self.engine.data['open'].pct_change().fillna(0)
        
    def on_bar(self, row):
        # 生成交易信号
        now_date = row.name
        now_index = self.date_list.index(now_date)
        next_date = self.date_list[now_index+1] if now_index + 1 < len(self.date_list) else None

        for signal in list(self.signals):
            signal_date, signal_type = signal
            if signal_date:
                if row.name == signal_date:
                    if signal_type == 'BUY':
                        self.buy(row['open'], abs(self.quantity - self.pos), row.name)
                        self.pos = self.quantity
                        self.entry_price = row['open']
                    elif signal_type == 'SELL':
                        self.sell(row['open'], abs(self.quantity + self.pos), row.name)
                        self.pos = -self.quantity
                        self.entry_price = row['open']
                    elif signal_type == 'PINGDUO' and self.pos > 0:
                        self.sell(row['open'], abs(self.pos), row.name)
                        self.pos = 0
                    elif signal_type == 'PINGKONG' and self.pos < 0:
                        self.buy(row['open'], abs(self.pos), row.name)
                        self.pos = 0
                    
                    self.signals.remove(signal)

        if self.pos != 0 : 
            self.posi_days += 1
        else:
            self.posi_days = 0

        buy_pre = (
                self.pos == 0 
                and row['close'] > row['ma5']
                and row['vv'] > row['pre1_vv'] > row['pre2_vv']
                # and row['close'] > row['vv']
                # and row['close'] > row['pre1_vv']
                # and row['close'] > row['high_ma3']
            )
        
        cross_up = (
                # row['Signal'] > 0
                row['ma5'] > row['ma10'] > row['ma20']
                and row['ma10'] > row['pre1_ma10'] > row['pre2_ma10']
                and row['close'] > max(row['pre1_close'],row['pre2_close'],row['pre3_close'])
                and row['close'] > min(row['boll_5_up_1p5'],row['boll_10_up_1p5'])
                # and row['close'] < min(row['boll_5_up_3p0'],row['boll_10_up_3p0'])
            )
        
        sell_pre = (
                self.pos == 0 
                and row['close'] < row['ma5']
                and row['vv'] < row['pre1_vv'] < row['pre2_vv']
                # and row['close'] < row['vv']
                # and row['close'] < row['pre1_vv']
                # and row['close'] < row['low_ma3']
            )
        
        cross_down = (
                # row['Signal'] < 0
                row['ma5'] < row['ma10'] < row['ma20']
                and row['ma5'] < row['pre1_ma5'] < row['pre2_ma5']
                and row['ma10'] < row['pre1_ma10'] < row['pre2_ma10']
                and row['close'] < min(row['pre1_close'],row['pre2_close'],row['pre3_close'])
                and row['close'] < max(row['boll_5_down_1p5'],row['boll_10_down_1p5'])
                # and row['close'] > max(row['boll_5_down_3p0'],row['boll_10_down_3p0'])
            )

        stop_long_loss_ma = row['close'] < row['ma10'] #and self.previous_row['close'] > self.previous_row['ma10'] 
        stop_short_loss_ma = row['close'] > row['ma10'] #and self.previous_row['close'] < self.previous_row['ma10']

        self.quantity = 1

        # stop_long_loss_ma =  row['close'] < row['ma10'] #(row['Signal']==0 or row['Signal']==np.nan) row['close'] < row['ma10']  row['close'] < row['ma10']
        # stop_short_loss_ma = row['close'] > row['ma10'] #(row['Signal']==0 or row['Signal']==np.nan) row['close'] > row['ma10']  row['close'] > row['ma10']

        if buy_pre and cross_up:
            self.signals.append((next_date, 'BUY'))
            self.all_signals.append((next_date, 'BUY'))
        elif sell_pre and cross_down :
            self.signals.append((next_date, 'SELL'))
            self.all_signals.append((next_date, 'SELL'))
        elif self.pos>0 and (stop_long_loss_ma):
            self.signals.append((next_date,'PINGDUO'))
            self.all_signals.append((next_date,'PINGDUO'))
        elif self.pos<0 and (stop_short_loss_ma):
            self.signals.append((next_date,'PINGKONG'))
            self.all_signals.append((next_date,'PINGKONG'))

class Strategy_Multi_factors(Strategy):
    """
    多因子策略
    """
    def __init__(self, engine):
        super().__init__(engine)
        self.posi_days = 0
        self.signals = []
        self.all_signals = []
        self.previous_row = None
        self.entry_price = None  # 记录建仓价格
        self.date_list = list(self.engine.data.index.unique())

    def on_init(self):

        # 计算Open2OpenRets
        self.engine.data['O2O_ret'] = self.engine.data['open'].pct_change().fillna(0)
        
    def on_bar(self, row):
        # 生成交易信号
        now_date = row.name
        now_index = self.date_list.index(now_date)
        next_date = self.date_list[now_index+1] if now_index + 1 < len(self.date_list) else None

        for signal in list(self.signals):
            signal_date, signal_type = signal
            if signal_date:
                if row.name == signal_date:
                    if signal_type == 'BUY':
                        self.buy(row['open'], abs(self.quantity - self.pos), row.name)
                        self.pos = self.quantity
                        self.entry_price = row['open']
                    elif signal_type == 'SELL':
                        self.sell(row['open'], abs(self.quantity + self.pos), row.name)
                        self.pos = -self.quantity
                        self.entry_price = row['open']
                    elif signal_type == 'PINGDUO' and self.pos > 0:
                        self.sell(row['open'], abs(self.pos), row.name)
                        self.pos = 0
                    elif signal_type == 'PINGKONG' and self.pos < 0:
                        self.buy(row['open'], abs(self.pos), row.name)
                        self.pos = 0
                    
                    self.signals.remove(signal)

        
        buy_signal = self.pos==0 and row['Signal'] > 0
        sell_signal = self.pos==0 and row['Signal'] < 0
        
        stop_long_loss_ma = (row['Signal']==0 or row['Signal']==np.nan)
        stop_short_loss_ma = (row['Signal']==0 or row['Signal']==np.nan)

        self.quantity = 1

        if buy_signal:
            self.signals.append((next_date, 'BUY'))
            self.all_signals.append((next_date, 'BUY'))
        elif sell_signal:
            self.signals.append((next_date, 'SELL'))
            self.all_signals.append((next_date, 'SELL'))
        elif self.pos>0 and (stop_long_loss_ma):
            self.signals.append((next_date,'PINGDUO'))
            self.all_signals.append((next_date,'PINGDUO'))
        elif self.pos<0 and (stop_short_loss_ma):
            self.signals.append((next_date,'PINGKONG'))
            self.all_signals.append((next_date,'PINGKONG'))