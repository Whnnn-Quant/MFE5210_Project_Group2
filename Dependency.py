import pandas as pd
import numpy as np
import os 
import matplotlib.pyplot as plt
import akshare as ak
import warnings
from datetime import datetime
from typing import List, Dict
from datetime import datetime

warnings.filterwarnings('ignore') 


'''期货品种对应代码和中文名称'''

Future_dict = {
    'SC' : '原油',
    'NR' : '20号胶',
    'LU' : '低硫燃料油',
    'BC' : '国际铜',
    'EC' : '集运指数(欧线)',
    'CU' : '沪铜',
    'AL' : '沪铝',
    'AO' : '氧化铝',
    'ZN' : '沪锌',
    'PB' : '沪铅',
    'NI' : '镍',
    'SN' : '锡',
    'SS' : '不锈钢',
    'AU' : '沪金',
    'AG' : '沪银',
    'WR' : '线材',
    'RB' : '螺纹钢',
    'HC' : '热卷',
    'FU' : '燃油',
    'BU' : '沥青',
    'RU' : '天然橡胶',
    'SP' : '纸浆',
    'BR' : '丁二烯橡胶',
    # 'IF' : '沪深300股指期货',
    # 'IH' : '上证50股指期货',
    # 'IC' : '中证500股指期货',
    # 'IM' : '中证1000股指期货',
    # 'TF' : '5年期国债期货',
    # 'T' : '10年期国债期货',
    # 'TS' : '2年期国债期货',
    # 'TL' : '30年期国债期货',
    'SI' : '工业硅',
    'LC' : '碳酸锂',
    'A' : '豆一',
    'B' : '豆二',
    'C' : '玉米',
    'CS' : '玉米淀粉',
    'M' : '豆粕',
    'Y' : '豆油',
    'P' : '棕榈',
    'RR' : '粳米',
    'L' : '塑料',
    'V' : 'PVC',
    'PP' : '聚丙烯',
    'EG' : '乙二醇',
    'EB' : '苯乙烯',
    'PG' : '液化石油气',
    'J' : '焦炭',
    'JM' : '焦煤',
    'I' : '铁矿石',
    'JD' : '鸡蛋',
    'LH' : '生猪',
    'FB' : '纤维板',
    'SR' : '白砂糖',
    'CF' : '郑棉',
    'CY' : '棉纱',
    'TA' : 'PTA',
    'OI' : '菜油',
    'MA' : '甲醇',
    'FG' : '玻璃',
    'RM' : '菜粕',
    'SA' : '纯碱',
    'PF' : '短纤',
    'PX' : '对二甲苯',
    'SH' : '烧碱',
    'SF' : '硅铁',
    'SM' : '锰硅',
    'AP' : '苹果',
    'CJ' : '红枣',
    'UR' : '尿素',
    'PK' : '花生',
    'RS' : '菜籽',
}

Future_size = {
    'SC': 1000, 
    'NR': 10, 
    'LU': 10, 
    'BC': 5, 
    'EC': 50, 
    'CU': 5, 
    'AL': 5, 
    'AO': 20, 
    'ZN': 5, 
    'PB': 5, 
    'NI': 1, 
    'SN': 1, 
    'SS': 5, 
    'AU': 1000, 
    'AG': 15, 
    'WR': 10, 
    'RB': 10, 
    'HC': 10, 
    'FU': 10, 
    'BU': 10, 
    'RU': 10, 
    'SP': 10, 
    'BR': 5, 
    'IF': 300, 
    'IH': 300, 
    'IC': 200, 
    'IM': 200, 
    'TF': 10000, 
    'T': 10000, 
    'TS': 20000, 
    'TL': 10000,
    'SI': 5, 
    'LC': 1, 
    'A': 10, 
    'B': 10, 
    'C': 10, 
    'CS': 10, 
    'M': 10, 
    'Y': 10, 
    'P': 10, 
    'RR': 10, 
    'L': 5, 
    'V': 5, 
    'PP': 5, 
    'EG': 10, 
    'EB': 5, 
    'PG': 20, 
    'J': 100, 
    'JM': 60, 
    'I': 100, 
    'JD': 10, 
    'LH': 16, 
    'FB': 10, 
    'SR': 10, 
    'CF': 5, 
    'CY': 5, 
    'TA': 5, 
    'OI': 10, 
    'MA': 10, 
    'FG': 20, 
    'RM': 10, 
    'SA': 20, 
    'PF': 5, 
    'PX': 5, 
    'SH': 30, 
    'SF': 5, 
    'SM': 5, 
    'AP': 10, 
    'CJ': 5, 
    'UR': 20, 
    'PK': 5, 
    'RS': 10
    }

data_path = 'Daily_Data'

def get_future_daily_data(file_path):

    # future_name = Future_dict[future]
    # future_file = f'{future}_{future_name}.csv'
    # read_file_path = os.path.join(data_path, future_file)
    df_daily_data = pd.read_csv(file_path) 
    df_daily_data['datetime'] = pd.to_datetime(df_daily_data['datetime'])
    df_daily_data = df_daily_data.set_index('datetime')

    return df_daily_data
    
class Trade:
    def __init__(self, datetime, price, volume, direction):
        self.datetime = datetime  # 交易时间
        self.price = price  # 交易价格
        self.volume = volume  # 交易数量
        self.direction = direction  # 交易方向

class Order:
    def __init__(self, datetime, price, volume, direction):
        self.datetime = datetime  # 订单时间
        self.price = price  # 订单价格
        self.volume = volume  # 订单数量
        self.direction = direction  # 订单方向
        self.traded = False  # 订单是否已成交

class DailyResult:
    def __init__(self, date):
        self.date = date  # 日期
        self.trades = []  # 交易列表
        self.start_pos = 0  # 日初持仓
        self.end_pos = 0  # 日末持仓
        self.turnover = 0  # 成交金额
        self.commission = 0  # 手续费
        self.margin = 0  # 保证金
        self.net_pnl = 0  # 净盈亏

    def add_trade(self, trade):
        self.trades.append(trade)  # 添加交易记录

    def calculate_pnl(self, close_price, size, rate, margin_rate):
        self.end_pos = self.start_pos  # 初始化日末持仓
        trading_pnl = 0  # 初始化交易盈亏
        for trade in self.trades:
            if trade.direction == 'LONG':
                pos_change = trade.volume  # 多头持仓变化
            else:
                pos_change = -trade.volume  # 空头持仓变化
            self.end_pos += pos_change  # 更新日末持仓
            turnover = trade.volume * size * trade.price  # 计算成交金额
            trading_pnl += pos_change * (close_price - trade.price) * size  # 计算交易盈亏
            self.turnover += turnover  # 累计成交金额
            self.commission += turnover * rate  # 累计手续费
            self.margin += turnover * margin_rate  # 累计保证金

        holding_pnl = self.start_pos * (close_price - self.start_pos_price) * size  # 计算持仓盈亏
        self.net_pnl = trading_pnl + holding_pnl - self.commission  # 计算净盈亏

class BacktestingEngine:
    def __init__(self):
        self.capital = 1000000  # 初始资金
        self.size = 1  # 合约乘数
        self.rate = 0.0003  # 手续费率
        self.margin_rate = 0.1  # 保证金率
        self.daily_results = {}  # 每日结果

        self.start_pos = 0  # 初始仓位

    def set_parameters(self, capital, size, rate, margin_rate):
        self.capital = capital  # 设置初始资金
        self.size = size  # 设置合约乘数
        self.rate = rate  # 设置手续费率
        self.margin_rate = margin_rate  # 设置保证金率

    def load_data(self, data):
        self.data = data  # 加载历史数据

    def run_backtesting(self, strategy):
        self.strategy = strategy  # 设置策略
        self.strategy.on_init()  # 策略初始化
        for ix, row in self.data.iterrows():
            self.new_bar(row)  # 逐行处理数据

    def new_bar(self, row):
        self.strategy.on_bar(row)  # 触发策略的on_bar方法
        self.update_daily_result(row)  # 更新每日结果

    def update_daily_result(self, row):
        date = row.name  # 获取当前日期
        close_price = row['close']  # 获取收盘价
        if date not in self.daily_results:
            daily_result = DailyResult(date)  # 创建新的每日结果对象
            daily_result.start_pos = self.start_pos  # 设置日初持仓
            daily_result.start_pos_price = row['open']  # 设置日初价格为开盘价
            self.daily_results[date] = daily_result  # 保存每日结果对象
        else:
            daily_result = self.daily_results[date]  # 获取已有的每日结果对象
        
        for order in self.strategy.orders:
            if not order.traded and order.datetime == date:
                trade = Trade(order.datetime, order.price, order.volume, order.direction)  # 创建交易对象
                daily_result.add_trade(trade)  # 添加交易记录
                order.traded = True  # 标记订单已成交

        daily_result.end_pos = self.strategy.pos
        daily_result.calculate_pnl(close_price, self.size, self.rate, self.margin_rate)  # 计算每日盈亏
        self.start_pos = daily_result.end_pos  # 更新为日末仓位

    def calculate_statistics(self):
        df = pd.DataFrame.from_dict({k: vars(v) for k, v in self.daily_results.items()}, orient='index') # 转换为DataFrame

        df['balance'] = self.capital + df['net_pnl'].cumsum()  # 计算账户余额
        df['drawdown'] = df['balance'].cummax() - df['balance']  # 计算回撤
        df['drawdown_pct'] = df['drawdown'] / df['balance'].cummax() * 100  # 计算回撤百分比
        df['margin_usage'] = df['margin'] / self.capital * 100  # 计算保证金使用率
        df['net_value'] = df['balance'] / self.capital  # 计算净值
        df['daily_return'] = df['net_pnl'] / self.capital  # 计算每日收益率
        df['cumsum_return'] = df['daily_return'].cumsum()  # 计算累加收益率
        stats = {
            "total_days": len(df),  # 总交易天数
            "profit_days": len(df[df['net_pnl'] > 0]),  # 盈利天数
            "loss_days": len(df[df['net_pnl'] < 0]),  # 亏损天数
            "end_balance": df['balance'].iloc[-1],  # 最终账户余额
            "max_drawdown": df['drawdown'].max(),  # 最大回撤
            "max_drawdown_pct": df['drawdown_pct'].max(),  # 最大回撤百分比
            "total_return": df['balance'].iloc[-1] / self.capital - 1,  # 总收益率
            # "annual_return": (df['net_value'].iloc[-1] / df['net_value'].iloc[0])**(252/len(df)) - 1,  # 年化收益率
            # "sharpe_ratio": df['daily_return'].mean() / df['daily_return'].std() * np.sqrt(252),  # 夏普比率
            "margin_usage": df['margin_usage'].mean()  # 平均保证金使用率
        }
        return df, stats
    
    '''
    def enable_live_trading(self, broker_api):
        """切换到实盘模式"""
        self.is_paper_trading = False
        self.broker_api = broker_api  # 传入实盘API实例

    def paper_execute(self, order):
        """模拟执行"""
        print(f"[PAPER] 执行 {order.direction} {order.volume}手 @ {order.price}")
        # 模拟立即成交
        trade = Trade(order.datetime, order.price, order.volume, order.direction)
        self.strategy.orders.append(order)
        self.update_daily_result(trade)

    def live_execute(self, order):
        """实盘执行"""
        try:
            # 转换为券商API所需格式
            api_order = {
                'symbol': 'AO2409',  # 需根据合约动态获取
                'price': order.price,
                'quantity': order.volume,
                'side': 'BUY' if order.direction == 'LONG' else 'SELL',
                'type': order.order_type,
                'time_in_force': order.time_in_force
            }

            # 调用真实API
            resp = self.broker_api.place_order(**api_order)

            if resp['status'] != 'FILLED':
                self.handle_order_reject(resp)

        except Exception as e:
            self.emergency_stop(f"订单发送失败: {str(e)}")
    '''


    def plot_results(self, df):
        fig, axs = plt.subplots(2, 2, figsize=(13.5, 6.5))  # 设置2x2子图

        # 左上角：净值曲线
        axs[0, 0].plot(df.index, df['net_value'], label='Net Value')
        axs[0, 0].set_title('Net Value Curve')
        axs[0, 0].set_xlabel('Date')
        axs[0, 0].set_ylabel('Net Value')
        axs[0, 0].grid()
        axs[0, 0].legend()

        # 右上角：累加收益率
        axs[0, 1].plot(df.index, df['cumsum_return'], label='Cumulative Return', color='orange')
        axs[0, 1].set_title('Cumulative Return')
        axs[0, 1].set_xlabel('Date')
        axs[0, 1].set_ylabel('Cumulative Return')
        axs[0, 1].grid()
        axs[0, 1].legend()

        # 左下角：每日回撤
        axs[1, 0].bar(df.index, df['drawdown'], label='Drawdown', color='red')
        axs[1, 0].set_title('Daily Drawdown')
        axs[1, 0].set_xlabel('Date')
        axs[1, 0].set_ylabel('Drawdown')
        axs[1, 0].grid()
        axs[1, 0].legend()

        fig.delaxes(axs[1, 1])  # 删除右下角空白子图

        plt.tight_layout()
        plt.show()  # 显示图形

class Strategy:
    def __init__(self, engine):
        self.engine = engine  # 回测引擎
        self.pos = 0  # 持仓量
        self.orders = []  # 订单列表

    def on_init(self):
        pass  # 策略初始化

    def on_bar(self, row):
        pass  # 每根K线触发

    def buy(self, price, volume, datetime):
        order = Order(datetime, price, volume, 'LONG')  # 创建多头订单
        self.orders.append(order)  # 添加订单到列表

    def sell(self, price, volume, datetime):
        order = Order(datetime, price, volume, 'SHORT')  # 创建空头订单
        self.orders.append(order)  # 添加订单到列表

    def send_order(self, price, volume, direction, twap=False):
        """增强的订单发送方法"""
        order = Order(datetime.now(), price, volume, direction)
        if self.engine.twap_enabled and twap:  # 全局和策略双开关
            end_time = order.datetime + pd.Timedelta(minutes=30)  # 默认30分钟执行窗口
            self.engine.twap_executor.split_order(order, order.datetime, end_time)
        else:
            self.orders.append(order)

class TWAPExecutor:
    def __init__(self, interval=5):
        """
        TWAP执行器
        :param interval: 将订单拆分的时间间隔(分钟)
        """
        self.interval = interval
        self.pending_orders = []  # 待执行的拆分订单

    def split_order(self, order, start_time, end_time):
        """将大单拆分为TWAP小单"""
        total_volume = order.volume
        time_slots = pd.date_range(start_time, end_time, freq=f'{self.interval}T')
        chunks = len(time_slots)
        chunk_volume = total_volume / chunks

        for slot in time_slots:
            self.pending_orders.append(Order(
                datetime=slot,
                price=order.price,  # 可改为动态定价
                volume=chunk_volume,
                direction=order.direction
            ))

def cal_sharp_and_drawdown(df):
    daily_return = df['adj_daily_ret'].sum() / len(df)
    daily_std = df['adj_daily_ret'].std()
    sharpe = ( daily_return * 252) / (daily_std * np.sqrt(252))
    mean_drawdown = ((df['Cumsum_ret'].cummax() - df['Cumsum_ret'])/ df['Cumsum_ret'].cummax()).mean()

    print(f'Sharpe:{round(sharpe,2)}, MeanDrawDown:{round(mean_drawdown*100,2)} %')

class MyRealBrokerAPI:
    """假设的券商API封装"""

    def __init__(self, api_key, secret_key, account_id):
        self.connected = False

    def connect(self):
        print("连接交易所API...")
        self.connected = True

    def get_tick(self, symbol):
        """获取实时tick数据"""
        return {
            'symbol': symbol,
            'open': 3250.0,
            'high': 3260.5,
            'low': 3245.0,
            'last_price': 3255.5,
            'volume': 1500
        }

    def place_order(self, **order):
        """提交真实订单"""
        print(f"[实盘] 发送订单: {order}")
        return {'status': 'ACCEPTED', 'order_id': '123456'}

    def cancel_all_orders(self):
        print("撤销所有订单...")

    def disconnect(self):
        print("断开API连接...")