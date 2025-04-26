import config
from LiveTradingEngine import LiveTradingEngine
from Dependency import *
from Strategies import *

def main():
    # 1. 初始化实盘API
    broker_api = MyRealBrokerAPI(
        api_key=config.API_KEY,
        secret_key=config.SECRET_KEY,
        account_id=config.ACCOUNT_ID
    )

    # 2. 创建引擎实例
    engine = LiveTradingEngine(broker_api)

    try:
        # 3. 连接交易所
        engine.connect()

        # 4. 创建策略实例
        strategy = Strategy_MoM_20d(engine)

        # 5. 设置合约参数
        engine.set_parameters(
            size=Future_size['AO'],
            rate=0.0005,
            margin_rate=0.1
        )

        # 6. 启动主循环
        engine.run(strategy)

    except Exception as e:
        print(f"致命错误: {str(e)}")
    finally:
        engine.shutdown()


if __name__ == "__main__":
    print("""
    ===============================
    实盘交易系统启动（危险操作！）
    ===============================
    """)
    confirm = input("确认启动实盘交易？(yes/no): ")
    if confirm.lower() == 'yes':
        main()
    else:
        print("已取消启动")