from Dependency import *
from Strategies import *
from Plot_Dependency import plot_strategy_performance

future_list = ['AG','AL','AU','BC','C','CJ','EC','FU','IC','IF','IH','LC','LH','NI','PF','PK','PX','RU','SA','SC','SH','T','TA',"UR"] # 'SI','RB','I','J','JM',

Total_daily_rets = []
for future in future_list:
    data_path = f'/Users/wanghenan/港中深金工/Courses/AL_Trade/Project/data_1h_mom/{future}888_1h_signals.csv'
    data = get_future_daily_data(data_path)

    engine = BacktestingEngine()
    engine.set_parameters(capital=100000, size=Future_size[future], rate =0.0005, margin_rate=0.1)
    # 启用TWAP执行（可选）
    #engine.enable_twap(interval=1)  # 每1分钟执行一次拆分
    engine.load_data(data)
    strategy = Strategy_MA_5_20(engine)
    engine.run_backtesting(strategy)
    df, stats = engine.calculate_statistics()

    # engine.plot_results(df)
    df_posi = df.reset_index()[['date','start_pos','end_pos']].rename(columns={'date':'datetime'})
    df_return = engine.data.reset_index()[['datetime','O2O_ret']]

    df_merge = df_return.merge(df_posi,on=['datetime'])
    df_merge['datetime'] = pd.to_datetime(df_merge['datetime'])
    df_merge = df_merge.set_index('datetime')
    df_merge.index = df_merge.index.floor('H')
    df_merge['daily_ret'] = df_merge['O2O_ret'] * df_merge['start_pos']
    df_merge['cumsum_ret'] = df_merge['daily_ret'].cumsum()
    # df_merge['cumsum_ret'].plot(title=f'{future} Cumsum Return')
    Total_daily_rets.append(df_merge[['daily_ret']])
    # plt.show()

df_total = pd.concat(Total_daily_rets,axis=1)
df_total['return_1d'] = df_total.mean(axis=1) * 5
df_total = df_total[df_total.index > pd.to_datetime("2020-01-01")]
df_total['cumsum_ret'] = df_total['return_1d'].cumsum()

plot_strategy_performance(df_total['return_1d'])
