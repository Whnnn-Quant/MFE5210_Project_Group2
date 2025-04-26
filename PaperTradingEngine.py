import time
import pandas as pd
from datetime import datetime
from Dependency import BacktestingEngine, Future_dict, Future_size
from datetime import timedelta


class MY_API:

    def __init__(self, api_key, endpoint):
        self.connected = False

    def get_realtime(self, symbol):
        """
        返回实时行情字典:
        {
            'open': float,   # 开盘价
            'high': float,   # 最高价
            'low': float,    # 最低价
            'close': float,  # 最新价
            'volume': int,   # 成交量
            'timestamp': str # ISO格式时间戳
        }
        """
        pass

    def get_history(self, symbol, days):
        """返回pandas DataFrame格式的历史数据"""
        pass

    def disconnect(self):
        """断开API连接"""
        pass

class PaperTradingEngine(BacktestingEngine):
    """模拟交易引擎（对接MY_API实时数据）"""

    def __init__(self):
        super().__init__()
        self.virtual_balance = 1000000  # 初始虚拟资金
        self.current_positions = {}  # 当前持仓
        self.latest_bar = None  # 最新行情
        self.api = None  # API连接实例

    def connect_api(self, api_config):
        """连接MY_API（接口配置）"""
        try:
            # 假设MY_API的初始化方式
            self.api = MY_API(
                api_key=api_config['key'],
                endpoint=api_config['endpoint']
            )
            print(f"已连接MY_API，订阅合约{Future_dict['AO']}")
        except Exception as e:
            raise ConnectionError(f"API连接失败: {str(e)}")

    def fetch_realtime_data(self, symbol='AO'):
        """从MY_API获取实时行情"""
        try:
            # API返回格式：{'open':x, 'high':x, 'low':x, 'close':x, 'volume':x, 'timestamp':x}
            raw_data = self.api.get_realtime(symbol)

            # 转换为Pandas Series
            bar = pd.Series({
                'open': raw_data['open'],
                'high': raw_data['high'],
                'low': raw_data['low'],
                'close': raw_data['close'],
                'volume': raw_data['volume']
            }, name=pd.to_datetime(raw_data['timestamp']))

            return bar
        except Exception as e:
            print(f"数据获取异常: {str(e)}")
            return None

    def run(self, strategy, symbol='AO',):
        """运行模拟交易主循环"""
        if not self.api:
            raise RuntimeError("请先连接API")

        self.strategy = strategy
        self.strategy.on_init()

        print(f"=== 启动模拟交易 ===")
        while True:
            # 获取实时数据
            current_bar = self.fetch_realtime_data(symbol)
            if current_bar is None:
                time.sleep(5)  # 失败时等待5秒
                continue

            # 处理行情
            self.new_bar(current_bar)
            self._print_status()

            # 按频率运行（与交易所节奏同步）
            next_update = (datetime.now() + timedelta(minutes=1)).replace(second=0, microsecond=0)
            sleep_seconds = (next_update - datetime.now()).total_seconds()
            time.sleep(max(0,sleep_seconds))

    def _print_status(self):
        """打印实时状态"""
        status_msg = f"""
        [模拟交易面板] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        --------------------------------
        合约: AO {Future_dict['AO']}
        最新价: {self.latest_bar['close']:.2f}
        持仓: {self.current_positions.get('AO', 0)}手
        虚拟余额: ¥{self.virtual_balance:,.2f}
        --------------------------------
        """
        print(status_msg)