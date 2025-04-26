import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def plot_strategy_performance(returns):
    """
    绘制策略绩效图表
    
    参数：
    returns : pd.Series或list
        策略每小时收益率序列（例如：0.01表示1%收益率）
    """
    # 转换为Series格式
    returns = pd.Series(returns).copy()
    returns.index = pd.to_datetime(returns.index)  # 尝试转换索引为时间格式
    
    # 计算累计收益率
    cum_simple = 1 + returns.cumsum()          # 单利累计
    cum_compounded = (1 + returns).cumprod()   # 复利累计
    
    # 计算回撤
    peak = cum_compounded.expanding(min_periods=1).max()
    drawdown = (peak - cum_compounded) / peak
    
    # 计算评价指标
    n = len(returns)
    annual_hours = 8 * 244  # 年化小时数
    
    # 年化收益率
    annualized_return = (cum_compounded.iloc[-1] ** (annual_hours / n)) - 1 if n > 0 else 0
    
    # 年化波动率
    annualized_vol = returns.std() * np.sqrt(annual_hours)
    
    # 夏普比率（假设无风险利率为0）
    sharpe_ratio = annualized_return / annualized_vol if annualized_vol != 0 else np.nan
    
    # 最大回撤
    max_drawdown = drawdown.max()
    
    # 卡玛比率
    calmar_ratio = annualized_return / max_drawdown if max_drawdown != 0 else np.nan
    
    # 其他指标
    total_return_simple = cum_simple.iloc[-1] - 1
    total_return_comp = cum_compounded.iloc[-1] - 1
    win_rate = (returns > 0).mean()
    
    # 创建画布和子图
    fig, axes = plt.subplots(2, 2, figsize=(24, 12))
    fig.suptitle('Strategy Performance Analysis', fontsize=14, y=0.95)
    
    # 单利累计收益
    axes[0, 0].plot(cum_simple, label='Simple Cumulative Return', color='tab:blue')
    axes[0, 0].set_title('Simple Cumulative Return')
    axes[0, 0].grid(True)
    axes[0, 0].yaxis.set_major_formatter(PercentFormatter(1))
    
    # 复利累计收益
    axes[0, 1].plot(cum_compounded, label='Compounded Cumulative Return', color='tab:green')
    axes[0, 1].set_title('Compounded Cumulative Return')
    axes[0, 1].grid(True)
    axes[0, 1].yaxis.set_major_formatter(PercentFormatter(1))
    
    # 回撤曲线
    axes[1, 0].fill_between(drawdown.index, drawdown, color='tab:red', alpha=0.3)
    axes[1, 0].plot(drawdown, color='tab:red', linewidth=0.5, label='Drawdown')
    axes[1, 0].set_title('Drawdown Series')
    axes[1, 0].grid(True)
    axes[1, 0].yaxis.set_major_formatter(PercentFormatter(1))
    
    # 评价指标
    metrics_text = (
        f"Total Return (Compounded): {total_return_comp:.2%}\n"
        f"Total Return (Simple): {total_return_simple:.2%}\n"
        f"Annualized Return: {annualized_return:.2%}\n"
        f"Annualized Volatility: {annualized_vol:.2%}\n"
        f"Sharpe Ratio: {sharpe_ratio:.2f}\n"
        f"Max Drawdown: {max_drawdown:.2%}\n"
        f"Calmar Ratio: {calmar_ratio:.2f}\n"
        f"Win Rate: {win_rate:.2%}"
    )
    axes[1, 1].axis('off')
    axes[1, 1].text(0.1, 0.5, metrics_text, fontfamily='monospace', fontsize=12, 
                   verticalalignment='center', linespacing=1.8)
    
    # plt.tight_layout()
    plt.show()