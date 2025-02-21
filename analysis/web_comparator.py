import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import os
from scipy.stats import pearsonr

pf_dates, pf_values = np.array([]), np.array([])

def build_dataset(symbols: list[str]) -> dict[str, np.array]:
    df = {}
    min_value = 1_000_000
    for symbol in symbols:
        new_values = pd.read_csv(f"./data/stocks/{symbol}.csv")
        new_values["date"] = pd.to_datetime(new_values["date"], format="mixed")

        new_values = new_values.sort_values("date")
        new_values = new_values.drop_duplicates("date")
        if len(df) == 0:
            df["date"] = new_values["date"].values
            df[symbol] = new_values["close"].values
            min_value = len(new_values)
        else:
            min_value = min(len(new_values), min_value)
            df[symbol] = new_values["close"].values

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

def mean_return(data):
    return (np.mean(data[1:] / data[:-1]) -1) * 252

def round(x, digits=3):
    return int(x*(10**digits)) / (10**digits)

def show_dashboard():

    app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.PULSE])
    etfs = pd.read_csv("./out/risk_returns.csv", sep=";")
    style = {'width': '48%', 'display': 'inline-block', "text-align": "center", "float": "center"}

    @callback(
        Output('graph-return-risk', 'figure'),
        Input('risk_return_period', 'value'),
        Input('min_sharp_ratio', 'value'))
    def risk_return_chart(risk_return_period="5y", min_sharp_ratio=0.5):
        data = etfs[etfs[f"sharp_{risk_return_period}"] >= min_sharp_ratio]
        return px.scatter(
            data, x=f"{risk_return_period}_volatility", y=f"{risk_return_period}_return",
            title="Risque/Rendement des différents produits", height=600,
            text=data["name"], color=data[f"sharp_{risk_return_period}"]
        ).update_layout(xaxis_title="Volatilité", yaxis_title="Rendement")
    

    @callback(
        Output('graph-cours-comparaison', 'figure'),
        Input('a_product', 'value'),
        Input('b_product', 'value'))
    def compare_products(a, b):
        data = None
        count = 0
        try:
            a_id = etfs[etfs["name"] == a]["symbol"].values[0]
            data = pd.read_csv(f"./data/stocks/{a_id}.csv", sep=",")
            data["name"] = a
            data["close"] = data["close"].values
            data = data.sort_values("date")
            data["close"] = data["close"].values / data["close"].values[0]
            count += 1
        except:
            pass

        try:
            b_id = etfs[etfs["name"] == b]["symbol"].values[0]
            df = pd.read_csv(f"./data/stocks/{b_id}.csv", sep=",")
            df = df.sort_values("date")

            if data is not None and len(df) < len(data):
                data = data[-len(df):]
                data["close"] = data["close"].values / data["close"].values[0]
            if data is not None and len(df) > len(data):
                df = df[-len(data):]

            df["name"] = b
            df["close"] = df["close"].values / df["close"].values[0]
            data = df if data is None else pd.concat([data, df])
            count += 1
        except:
            pass
        
        title = "Cours des produits"
        if count >= 2:
            p = pearsonr(data[data["name"]==a]["close"].values, data[data["name"]==b]["close"].values)
            title += f" (corrélation: {round(p.correlation)})"
        return px.line(
            data, x="date", y="close", color="name",
            title=title, height=800
        ).update_layout(xaxis_title="", yaxis_title="Cours de cloture", legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ))
    
    @callback(
        Output('pf-generator', 'figure'),
        Input('product_1', 'value'),
        Input('product_2', 'value'),
        Input('product_3', 'value'),
        Input('product_qqt_1', 'value'),
        Input('product_qqt_2', 'value'),
        Input('product_qqt_3', 'value'),
    )
    def create_pf(product_1, product_2, product_3, product_qqt_1, product_qqt_2, product_qqt_3):
        if len(set((product_1, product_2, product_3))) != 3:
            return
        
        sum = product_qqt_1 + product_qqt_2 + product_qqt_3
        product_qqt_1 /= sum
        product_qqt_2 /= sum
        product_qqt_3 /= sum

        data = [product_1, product_2, product_3]
        data_id = [etfs[etfs["name"] == a]["symbol"].values[0] for a in data]
        data = build_dataset(data_id)
        ponderations = {data_id[0]: product_qqt_1, data_id[1]: product_qqt_2, data_id[2]: product_qqt_3}
        dates, values = create_rebalancing_pf(data, ponderations, 50)
        
        global pf_values
        pf_dates = dates
        pf_values = values
        return px.line(x=pf_dates, y=pf_values)
    
    @callback(
        Output('mean_pf_return', 'children'),
        Input('product_1', 'value'),
        Input('product_2', 'value'),
        Input('product_3', 'value'),
        Input('product_qqt_1', 'value'),
        Input('product_qqt_2', 'value'),
        Input('product_qqt_3', 'value'),
    )
    def create_mr(product_1, product_2, product_3, product_qqt_1, product_qqt_2, product_qqt_3):
        txt = """## Analyse du portefeuille
|Métrique|Valeure|
|---|---|
"""
        if len(pf_values) > 2:
            txt += f"|Rendement annuel moyen sur la période  |{round(mean_return(pf_values)*100)} %|\n"
            txt += f"|Volatilité|{round(np.std(pf_values[1:]/pf_values[:-1])*100*np.sqrt(252))} %|\n"
        return txt


    space = html.Div(style={"margin-bottom": "10em"})

    default_pf_comp = ["Lyxor PEA Inde (MSCI India) ETF Capi", "iShares Core EURO STOXX 50 ETF EUR Acc", "Lyxor PEA Nasdaq-100 ETF Capi"]
    container_style = {"width": "80%", "margin-right": "auto", "margin-left": "auto"}
    app.layout = [
        html.H1("Liste des produits", style={"text-align": "center"}),
        html.Div([
            html.Div("Durée de l'bservation", style=style),
            html.Div("Sharp minimal", style=style),
        ]),
        html.Div([
            dcc.Dropdown(["1y", "3y", "5y"], "5y", id='risk_return_period', style=style),
            dcc.Input(value=0.5, type="number", style=style, id="min_sharp_ratio")
        ]),
        dcc.Graph(id='graph-return-risk', figure=risk_return_chart()),

        space,

        html.H1("Comparateur", style={"text-align": "center"}),
        html.Div([
            html.Div("Produit A", style=style),
            html.Div("Produit B", style=style),
        ]),
        html.Div([
            dcc.Dropdown(etfs["name"].values, "iShares EURO STOXX Banks 30-15ETF DE acc", id='a_product', style=style),
            dcc.Dropdown(etfs["name"].values, "", id='b_product', style=style),
        ]),
        dcc.Graph(id='graph-cours-comparaison', figure=compare_products("iShares EURO STOXX Banks 30-15ETF DE acc", "")),

        space,
        html.H1("Simulateur de portefeuille", style={"text-align": "center"}),

        *[html.Div([
            dcc.Dropdown(etfs["name"].values, default_pf_comp[i-1], id=f'product_{i}', style=style),
            dcc.Input(value=0.333333, type="number", style=style, id=f'product_qqt_{i}')
        ]) for i in range(1, 4)],
        dcc.Graph(id='pf-generator', figure=create_pf(default_pf_comp[0], default_pf_comp[1], default_pf_comp[2], 0.4, 0.3, 0.3)),

        dcc.Markdown("", id="mean_pf_return", style=container_style),
    ]
    
    app.run(debug=True)
    

if __name__ == "__main__":
    show_dashboard()