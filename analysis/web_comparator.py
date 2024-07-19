import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import os
from scipy.stats import pearsonr

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
    

    space = html.Div(style={"margin-bottom": "10em"})
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

        space
    ]
    
    app.run(debug=True)
    

if __name__ == "__main__":
    show_dashboard()