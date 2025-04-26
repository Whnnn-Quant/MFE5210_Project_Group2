import time
from datetime import datetime
from typing import Dict
import pandas as pd
from Dependency import BacktestingEngine, Future_dict, Future_size


class LiveTradingEngine(BacktestingEngine):
    """实盘交易引擎"""

    def __init__(self, broker_api):
        """
        :param broker_api: 对接真实交易所的API实例
        """
        self.broker_api = broker_api
        self.capital = 0  # 实时资金（从API获取）
        self.positions: Dict[str, int] = {}  # 合约持仓 {'AO': 10}
        self.active_orders = {}  # 活跃订单 {order_id: Order}
        self.strategy = None

        # 实盘特有组件
        self.risk_manager = LiveRiskManager()
        self.order_tracker = OrderTracker()

    def connect(self):
        """连接交易所"""
        self.broker_api.connect()
        self._sync_account_status()

    def _sync_account_status(self):
        """同步账户初始状态"""
        self.capital = self.broker_api.get_balance()
        self.positions = self.broker_api.get_positions()

    def run(self, strategy, symbol='AO'):
        """
        启动实盘交易主循环
        :param strategy: 策略实例
        :param symbol: 交易合约
        """
        self.strategy = strategy
        self.strategy.on_init()

        print(f"\033[1;31m=== 实盘交易已启动（{symbol}）=== \033[0m")
        try:
            while True:
                self._process_tick(symbol)
                time.sleep(1)  # 根据策略频率调整
        except KeyboardInterrupt:
            self.shutdown()

    def _process_tick(self, symbol):
        """处理实时行情"""
        # 1. 获取实时数据
        tick = self.broker_api.get_tick(symbol)
        if not tick:
            return

        # 2. 转换为策略所需格式
        bar = pd.Series({
            'open': tick['open'],
            'high': tick['high'],
            'low': tick['low'],
            'close': tick['last_price'],
            'volume': tick['volume']
        }, name=datetime.now())

        # 3. 执行策略逻辑
        self.strategy.on_bar(bar)

        # 4. 处理策略生成的订单
        self._process_strategy_orders()

        # 5. 打印状态
        self._print_live_status(tick)

    def _process_strategy_orders(self):
        """处理策略生成的订单"""
        for order in list(self.strategy.orders):
            if not self.risk_manager.check_order(order):
                print(f"风控拦截订单: {order.__dict__}")
                continue

            # 发送实盘订单
            resp = self.broker_api.place_order(
                symbol=order.symbol,
                price=order.price,
                quantity=order.volume,
                side='BUY' if order.direction == 'LONG' else 'SELL',
                order_type=order.order_type
            )

            if resp['status'] == 'ACCEPTED':
                order.exchange_id = resp['order_id']
                self.order_tracker.add_order(order)
            else:
                print(f"订单被拒绝: {resp['reject_reason']}")

    def _print_live_status(self, tick):
        """打印实盘状态"""
        status = f"""
        [LIVE] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        --------------------------------
        合约: {tick['symbol']} 
        最新价: {tick['last_price']}
        持仓: {self.positions.get(tick['symbol'], 0)}
        可用资金: {self.capital:,.2f}
        --------------------------------
        """
        print(status)

    def shutdown(self):
        """安全关闭"""
        print("\n=== 执行安全关闭 ===")
        self.broker_api.cancel_all_orders()
        self.broker_api.disconnect()


class LiveRiskManager:
    """实盘风控模块"""

    def check_order(self, order):
        # 增加: 单笔最大亏损检查
        if self.calc_max_loss(order) > 10000:
            return False
        # 增加: 交易时段限制
        if not self.is_trading_hours():
            return False
        return True
class OrderTracker:
    """订单状态跟踪器"""

    def __init__(self):
        self.orders = {}

    def add_order(self, order):
        self.orders[order.exchange_id] = order

