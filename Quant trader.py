import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# === 加载本地数据 ===
data = pd.read_csv("QQQ_2019_2021.csv", index_col=0, parse_dates=True)

if data.empty:
    print("❌ CSV文件读取失败，请检查路径")
    exit()

# === 计算技术指标 ===
data['MA50'] = data['Close'].rolling(window=50).mean()
data['MA200'] = data['Close'].rolling(window=200).mean()

ema12 = data['Close'].ewm(span=12, adjust=False).mean()
ema26 = data['Close'].ewm(span=26, adjust=False).mean()
data['MACD'] = ema12 - ema26
data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

window = 14
delta = data['Close'].diff()
gain = delta.clip(lower=0).rolling(window=window).mean()
loss = -delta.clip(upper=0).rolling(window=window).mean()
RS = gain / loss
data['RSI'] = 100 - (100 / (1 + RS))

# === 信号判断 ===
data['buy_signal'] = ((data['MACD'] > data['Signal']) & (data['MACD'].shift(1) <= data['Signal'].shift(1))) | (data['RSI'] < 30)
data['sell_signal'] = ((data['MACD'] < data['Signal']) & (data['MACD'].shift(1) >= data['Signal'].shift(1))) | (data['RSI'] > 70)

# === 仓位记录 ===
data['Position'] = 0
position = 0
for i in range(len(data)):
    if position == 0 and data.iloc[i]['buy_signal']:
        position = 1
    elif position == 1 and data.iloc[i]['sell_signal']:
        position = 0
    data.iloc[i, data.columns.get_loc('Position')] = position

# === 策略回测 ===
data['DailyReturn'] = data['Close'].pct_change()
data['StrategyReturn'] = data['DailyReturn'] * data['Position'].shift(1).fillna(0)
data['StrategyEquity'] = (1 + data['StrategyReturn']).cumprod()
data['BuyHoldEquity'] = (1 + data['DailyReturn']).cumprod()

# === 策略绩效指标 ===
total_days = len(data.dropna())
if data['StrategyEquity'].dropna().empty:
    print("⚠️ 策略净值为空，无法评估")
    exit()

cum_return = data['StrategyEquity'].iloc[-1] - 1
annual_return = data['StrategyEquity'].iloc[-1]**(252 / total_days) - 1
daily_returns = data['StrategyReturn'].dropna()
sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252)
roll_max = data['StrategyEquity'].cummax()
daily_drawdown = data['StrategyEquity'] / roll_max - 1
max_drawdown = daily_drawdown.min()

print("\n📊 Strategy Performance:")
print(f"Cumulative Return: {cum_return:.2%}")
print(f"Annualized Return: {annual_return:.2%}")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
print(f"Max Drawdown: {max_drawdown:.2%}")

# === 参数优化（MACD+RSI） ===
rsi_windows = [10, 14, 20]
oversold_thresholds = [25, 30]
best_sharpe = -float('inf')
best_params = None

for rsi_win in rsi_windows:
    for oversold_th in oversold_thresholds:
        delta = data['Close'].diff()
        gain = delta.clip(lower=0).rolling(window=rsi_win).mean()
        loss = -delta.clip(upper=0).rolling(window=rsi_win).mean()
        RSI = 100 - (100 / (1 + gain/loss))

        buy_signal = ((data['MACD'] > data['Signal']) & (data['MACD'].shift(1) <= data['Signal'].shift(1))) | (RSI < oversold_th)
        sell_signal = ((data['MACD'] < data['Signal']) & (data['MACD'].shift(1) >= data['Signal'].shift(1))) | (RSI > 70)

        pos = 0
        returns = []
        for i in range(len(data)):
            if pos == 0 and buy_signal.iloc[i]:
                pos = 1
            elif pos == 1 and sell_signal.iloc[i]:
                pos = 0
            daily_ret = data['DailyReturn'].iloc[i] * pos
            returns.append(daily_ret)

        returns = pd.Series(returns).dropna()
        if len(returns) > 10:
            sharpe = returns.mean()/returns.std() * (252 ** 0.5)
            print(f"RSI window {rsi_win}, Threshold {oversold_th} → Sharpe: {sharpe:.2f}")
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = (rsi_win, oversold_th)

print(f"\n✅ Best Parameters: RSI window {best_params[0]}, Threshold {best_params[1]} → Sharpe Ratio: {best_sharpe:.2f}")

# === 填补绘图所需列的缺失值，确保图表连续 ===
cols_to_fill = ['StrategyEquity', 'BuyHoldEquity', 'Close', 'MA50', 'MA200', 'MACD', 'Signal', 'RSI']
data[cols_to_fill] = data[cols_to_fill].fillna(method='bfill').fillna(method='ffill')

# === 图1：策略 vs 买入持有 净值曲线 ===
plt.figure(figsize=(14, 6))
plt.plot(data.index, data['StrategyEquity'], label='Strategy Equity', linewidth=2)
plt.plot(data.index, data['BuyHoldEquity'], label='Buy & Hold', linestyle='--')
plt.title('Strategy vs Buy-and-Hold: Equity Curve', fontsize=14)
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("img/equity_curve.png", dpi=300)
plt.show()

# === 图2：价格 + 均线 + 交易信号 ===
plt.figure(figsize=(14, 6))
plt.plot(data['Close'], label='Close Price', color='blue')
plt.plot(data['MA50'], label='MA50', linestyle='--', color='gray')
plt.plot(data['MA200'], label='MA200', linestyle='--', color='black')

buy_signals = data[data['buy_signal']]
sell_signals = data[data['sell_signal']]
plt.scatter(buy_signals.index, buy_signals['Close'], label='Buy Signal', marker='^', color='green', s=100)
plt.scatter(sell_signals.index, sell_signals['Close'], label='Sell Signal', marker='v', color='red', s=100)

plt.title('Trading Signals with Moving Averages', fontsize=14)
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("img/signal_chart.png", dpi=300)
plt.show()
