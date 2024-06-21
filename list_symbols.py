import requests
from bs4 import BeautifulSoup
import pandas as pd

links, names, types = [], [], []

url = "https://www.boursorama.com/bourse/trackers/recherche/?beginnerEtfSearch%5Beligibility%5D%5B%5D=taxation&beginnerEtfSearch%5Bcurrent%5D=synthesis&beginnerEtfSearch%5Bsaving%5D=0"
req = requests.get(url)
html = BeautifulSoup(req.content, 'lxml')

table = html.select_one(".u-relative").select("a")
for link in table:
    links.append(link["href"].split("/")[-2])
    names.append(link["title"])
    types.append("ETF partenaire")
    print(link["title"])


for i in range(1, 10):
    try:
        url = f"https://www.boursorama.com/bourse/trackers/recherche/autres/page-{i}?beginnerEtfSearch%5BisEtf%5D=1&beginnerEtfSearch%5Btaxation%5D=1"
        req = requests.get(url)
        html = BeautifulSoup(req.content, 'lxml')

        table = html.select_one(".u-relative").select("a")
        for link in table:
            links.append(link["href"].split("/")[-2])
            names.append(link["title"])
            types.append("ETF")
            print(link["title"])

    except Exception:
        pass

df = pd.DataFrame({"name": names, "link": links, "types": types})
df.to_csv("./data/etf_list.csv")
links, names, types = [], [], []

for i in range(1, 10):
    try:
        url = f"https://www.boursorama.com/bourse/opcvm/recherche/page-{i}?beginnerFundSearch%5Bpartners%5D=1&beginnerFundSearch%5Btaxation%5D=1"
        req = requests.get(url)
        html = BeautifulSoup(req.content, 'lxml')

        table = html.select_one(".u-relative").select("a")
        for link in table:
            links.append(link["href"].split("/")[-2])
            names.append(link["title"])
            types.append("OPC")
            print(link["title"])

    except Exception:
        pass

for i in range(1, 20):
    try:
        url = f"https://www.boursorama.com/bourse/opcvm/recherche/autres/page-{i}?beginnerFundSearch%5BhidePartners%5D=1&beginnerFundSearch%5Btaxation%5D=1"
        req = requests.get(url)
        html = BeautifulSoup(req.content, 'lxml')

        table = html.select_one(".u-relative").select("a")
        for link in table:
            links.append(link["href"].split("/")[-2])
            names.append(link["title"])
            types.append("OPC")
            print(link["title"])

    except Exception:
        pass

df = pd.DataFrame({"name": names, "link": links, "types": types})
df.to_csv("./data/funds.csv")