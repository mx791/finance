import pandas as pd
import numpy as np


def get_returns(data):
    return (data[1:] / data[:-1]) - 1

etfs = pd.concat([pd.read_csv("./data/etf_list.csv"), pd.read_csv("./data/funds.csv")])

symbols = [
    *etfs["link"].values
]

names, symbol, yearly_return, yearly_std, three_year_return, three_year_std, five_year_return, five_year_std, nb_values = [], [], [], [], [], [], [], [], []

for s in symbols:

    try:
        data = pd.read_csv(f"./data/stocks/{s}.csv").sort_values("date").drop_duplicates("date")
    except:
        pass
    returns = get_returns(data["close"].values)

    std = np.std(returns[-252:])*np.sqrt(252)
    r = (np.mean(returns[-252:])*252)
    
    if std > 100 or std < 0.01 or len(data) < 750:
        continue

    names.append(etfs[etfs["link"]==s]["name"].values[0])
    symbol.append(s)

    yearly_return.append(r)
    yearly_std.append(std)

    three_year_return.append(np.mean(returns[-252*3:])*365)
    three_year_std.append(np.std(returns[-252*3:])*np.sqrt(365))

    five_year_return.append(np.mean(returns[-252*3:])*365)
    five_year_std.append(np.std(returns[-252*3:])*np.sqrt(365))

    nb_values.append(len(data))


df = pd.DataFrame({
    "name": names,
    "symbol": symbol,
    "historical": nb_values,
    "1y_return": yearly_return,
    "1y_volatility": yearly_std,
    "3y_return": three_year_return,
    "3y_volatility": three_year_std,
    "5y_return": five_year_return,
    "5y_volatility": five_year_std,
})
df["sharp_1y"] = df["1y_return"] / df["1y_volatility"]
df["sharp_3y"] = df["3y_return"] / df["3y_volatility"]
df["sharp_5y"] = df["5y_return"] / df["5y_volatility"]
df.to_csv("./out/risk_returns.csv", sep=";")