import requests
import json
import pandas as pd
import datetime
import tqdm
import os


def fetch(symbol):
    url = f"https://www.boursorama.com/bourse/action/graph/ws/GetTicksEOD?symbol={symbol}&length=3650&period=0&guid="
    content = requests.get(url).content
    obj = json.loads(content)
    d, o, h, l, c, v = [], [], [], [], [], []
    for i in obj["d"]["QuoteTab"]:
        d.append(datetime.datetime(1970, 1, 1) + datetime.timedelta(days=i["d"]))
        o.append(i["o"])
        h.append(i["h"])
        l.append(i["l"])
        c.append(i["c"])
        v.append(i["v"])

    df = pd.DataFrame({"date": d, "open": o, "close": c, "high": h, "low": l, "volumme": v})
    
    try:
        df1 = pd.read_csv(f"./data/stocks/{symbol}.csv")
        df = pd.concat([df, df1])
        df = df.drop_duplicates()
    except:
        pass
    
    df.to_csv(f"./data/stocks/{symbol}.csv")


df = [
    *pd.read_csv("./data/etf_list.csv")["link"].values,
    *pd.read_csv("./data/funds.csv")["link"].values,
]

for s in tqdm.tqdm(df):
    try:
        fetch(s)
    except Exception:
        print("error with : " + s)
