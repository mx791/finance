import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def get_returns(data):
    return data[1:] / data[:-1]

etfs = pd.concat([pd.read_csv("./data/etf_list.csv"), pd.read_csv("./data/funds.csv")])

symbols = [
    *etfs["link"].values
]

def create_chart(period: int, title: str, out: str):
    one_year_return, one_year_volatility = [], []
    names = []

    for s in symbols:
        try:
            data = pd.read_csv(f"./data/stocks/{s}.csv")
            returns = get_returns(data["close"].values)

            std = np.std(returns[-period:])*np.sqrt(365)*100
            r = ((np.mean(returns[-period:])-1)*365)*100

            if std > 100 or std < 0.01 or r/std > 0.7 or r < -10:
                continue

            one_year_return.append(r)
            one_year_volatility.append(std)
            names.append(etfs[etfs["link"]==s].values[0][1])

        except Exception:
            pass

    one_year_return = np.array(one_year_return)
    one_year_volatility = np.array(one_year_volatility)

    plt.figure(figsize=(18, 12))
    ratio = one_year_return/one_year_volatility
    plt.scatter(one_year_volatility, one_year_return, c=ratio)

    for i, n in enumerate(names):
        plt.text(one_year_volatility[i], one_year_return[i], n)

    plt.title(title)
    plt.xlabel("Risk %")
    plt.ylabel("Avg return %")
    plt.savefig(out)


create_chart(250, "Risk/return over a year", "./out/risk_return_1y.png")
create_chart(750, "Risk/return over two years", "./out/risk_return_2y.png")
create_chart(250*8, "Risk/return over 8 year", "./out/risk_return_8y.png")