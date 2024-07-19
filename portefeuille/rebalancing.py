import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
import random


def get_returns(data):
    return data[1:] / data[:-1]

def get_performance(data):
    rs = get_returns(data)
    return (np.mean(rs)-1)*365, np.std(rs)*np.sqrt(365)

def build_dataset(symbols: list[str]) -> dict[str, np.array]:
    df = {}
    min_value = 1_000_000
    for symbol in symbols:
        new_values = pd.read_csv(f"./data/stocks/{symbol}.csv")
        new_values["date"] = pd.to_datetime(new_values["date"], format="mixed")

        new_values = new_values.sort_values("date")
        if len(df) == 0:
            df["date"] = new_values["date"].values
            df[symbol] = new_values["close"].values
            min_value = len(new_values)
        else:
            min_value = min(len(new_values), min_value)
            df[symbol] = new_values["close"].values
        #print(symbol, len(new_values))

    for k in df:
        df[k] = df[k][-min_value:]
    
    return df


def create_rebalancing_pf(dataset: dict[str, np.array], composition: dict, period: int):
    parts = {}
    capital = 1
    pf_historical = []
    for i in range(len(dataset[list(dataset.keys())[0]])):
        for k in parts:
            capital += parts[k] * dataset[k][i]
        pf_historical.append(capital)
        if i%period == 0:
            for k in composition:
                parts[k] = capital * composition[k] / dataset[k][i]
        capital = 0
    
    return dataset["date"], np.array(pf_historical)


def optimize_composition(dataset, symbols):

    def target_fc(weights):
        weights = np.abs(weights) / np.sum(np.abs(weights))
        new_compo = {symbols[i]: weights[i] for i in range(len(symbols))}
        dates, pf = create_rebalancing_pf(dataset, new_compo, 30)
        returns = pf[1:] / pf[:-1]
        return - (np.mean(returns)-1)*365 / np.std(returns)*np.sqrt(365)

    res = minimize(target_fc, np.random.uniform(size=len(symbols)))
    weights = np.abs(res.x) / np.sum(np.abs(res.x))
    new_compo = {symbols[i]: weights[i] for i in range(len(symbols))}
    dates, pf = create_rebalancing_pf(dataset, new_compo, 30)

    r, v = get_performance(pf)
    print(f"Avg yearly return: {r}")
    print(f"Volatility: {v}")
    print(f"Sharp ratio: {r/v}")

    print(new_compo)
    if r/v > 0.9:
        plt.plot(dates, pf)

    #plt.bar(symbols, weights)
    #plt.show()

    #plt.plot(dates, pf)
    #plt.show()
    return dates, pf

def optimize_test():
    symbols = ["1rAEXA1", "MP-805883", "1rTETZ", "0P0000YRWM"]
    df = build_dataset(symbols)
    return optimize_composition(df, symbols)

def brute_force():
    symbols = pd.concat([pd.read_csv("./data/etf_list.csv"), pd.read_csv("./data/funds.csv")])["link"].values

    for i in range(100):
        print("=====================")
        try:
            sub_set = [symbols[random.randint(0, len(symbols)-1)] for i in range(5)]
            dataset = build_dataset(sub_set)
            if len(dataset[list(dataset.keys())[0]]) > 1000:
                optimize_composition(dataset, sub_set)
        except Exception:
            pass
    
    plt.show()


def run_benchmark(w: dict[str, float]):
    dataset = build_dataset(list(w.keys()))
    d, v = create_rebalancing_pf(dataset, w, 30)
    plt.plot(d, v)
    plt.show()


def test_current_pf():
    values = {
        #"1rTPTPXH": 1600.0,
        "1rTPUST": 2600.0,
        #"1rTCW8": 1000,
        #"1rTESEH": 900.0
    }
    sum = np.sum(list(values.values()))
    for k in values:
        values[k] = values[k] / sum

    dataset = build_dataset(list(values.keys()))
    d, v = create_rebalancing_pf(dataset, values, 30)
    df = pd.DataFrame({"date": d, "value": v})
    df.to_csv("./out/example_pf.csv")


if __name__ == "__main__":
    test_current_pf()
    #d, v = optimize_test()
    #df = pd.DataFrame({"date": d, "value": v})
    #df.to_csv("./out/example_pf.csv")
    #brute_force()
    #run_benchmark({'MP-8225': 0.11092567753159772, '1rTPAEEM': 0.11163978827261566, 'MP-805815': 0.11417207260514314, 'MP-546198': 0.5502164223985186, '0P00011HCE': 0.11304603919212473})