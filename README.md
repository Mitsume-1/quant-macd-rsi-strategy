# 📊 Quantitative Trading Strategy: MACD + RSI

This repository contains a backtest-ready quantitative trading strategy combining **MACD** and **RSI** indicators. The strategy is applied on **QQQ ETF (2019–2021)** using Python.

![Backtest Strategy Equity Curve](img/equity_curve.png)

---

## 📌 Project Overview

- 📈 **Strategy Type**: Mean-Reversion + Trend-Following
- 💡 **Indicators**: MACD, RSI, MA50/MA200
- 📊 **Assets**: QQQ ETF (2019–2021)
- 🔁 **Backtesting**: Long-only strategy with rule-based signal generation
- 🧪 **Optimization**: RSI window + oversold threshold via Sharpe ratio

---

## 📁 Files

| File | Description |
|------|-------------|
| `Quant_MACD_RSI_Strategy.ipynb` | Full notebook with logic, charts, and backtest results |
| `Quant_trader.py` | Script version of the strategy |
| `QQQ_2019_2021.csv` | Price data (local only) |
| `img/equity_curve.png` | Strategy equity curve |
| `img/signal_chart.png` | Buy/sell signal chart |
| `.gitignore` | Ignore config and local files |

---

## 📉 Sample Performance Output

```
Cumulative Return:    +8.49%
Annualized Return:    +5.37%
Sharpe Ratio:         1.49
Max Drawdown:         -14.94%
```

---

## 📍 Buy/Sell Signal Chart

Visualizes the MACD + RSI crossover-based signal points over QQQ price.

![Signal Chart](img/signal_chart.png)

---

## 🛠 Tech Stack

- `Python 3.x`
- `pandas`, `numpy`
- `matplotlib`
- `yfinance` for data download

---

## 💼 Author

- [Mitsume-1](https://github.com/Mitsume-1)

---

> ✅ This project is ideal for showcasing quantitative finance, Python modeling, and data-driven investment strategies in interviews or GitHub portfolios.
