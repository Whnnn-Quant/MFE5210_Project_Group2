from Strategies import *
from PaperTradingEngine import PaperTradingEngine
from Dependency import get_future_daily_data
import config #存放API配置


# 初始化
engine = PaperTradingEngine()
# 配置API连接
api_config = {
    'key': config.MY_API_KEY,
    'endpoint': config.MY_API_ENDPOINT
}
engine.connect_api(api_config)

# 设置合约参数
engine.set_parameters(
    capital=1000000,
    size=Future_size['AO'],  # 氧化铝合约乘数
    rate=0.0005,            # 手续费率
    margin_rate=0.1         # 保证金率
)

# 加载历史数据初始化指标
if hasattr(engine.api, 'get_history'):
    hist_data = engine.api.get_history('AO', days=100)
    engine.load_data(hist_data)

# 创建策略实例
strategy = Strategy_MoM_20d(engine)

# 启动模拟交易
try:
    engine.run(strategy, symbol='AO')
except KeyboardInterrupt:
    print("=== 模拟交易手动终止 ===")
finally:
    engine.api.disconnect()