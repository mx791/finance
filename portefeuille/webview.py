import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import numpy as np
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

TRADING_DAYS = 252

def mean_return(data, period=TRADING_DAYS):
    return (np.mean([data[i] / data[i-period] for i in range(period, len(data))])-1) * 100

def mean_return_2(data):
    return (np.mean(data[1:] / data[:-1])-1) * TRADING_DAYS * 100

def volatility(data):
    return np.std(data[1:] / data[:-1]) * np.sqrt(TRADING_DAYS) * 100

def create_pf_value(data):
    y = data["value"] / data["value"].values[0]
    return px.line(
        title="Valeur du portefeuille",
        x=data["date"].values, y=(y-1)*100
    ).update_layout(
        xaxis_title="", yaxis_title="Rendement (%)"
    )

def create_pf_returns(data, period=TRADING_DAYS):
    return px.histogram(
        title="Histogramme des rendements au bout d'un an",
        x=[(data[i] / data[i-period] - 1)*100 for i in range(period, len(data))]
    ).update_layout(
        yaxis_title="", xaxis_title="Rendement (%)"
    )

def resume_table(data):
    return f"""<table>
    <tr>
        <td>Rendement moyen sur un an</td>
        <td>{mean_return(data["value"].values)}</td>
    </tr>
    </table>"""

def positive_paretto(data):
    probas = []
    for i in range(1, 100):
        p = 0
        for e in range(i*5, len(data)):
            p += 1/(len(data)-i*5) if data[e] < data[e-i*5] else 0.0
        probas.append(p*100)
    return px.line(
        y=probas, title="Probabilité de perte en fonction de la durée d'investissement"
    ).update_layout(
        xaxis_title="Durée d'investissement en semaines", yaxis_title="Probabilité de perte (%)"
    )

def number(x):
    return int(100*x)/100

def returns_chart(data: pd.DataFrame, period=50):
    dates, returns = [], []
    for i in range(period, len(data)):
        dates.append(data["date"].values[i])
        returns.append((data["value"].values[i] / data["value"].values[i-period] - 1)*100)
    return px.line(
        x=dates, y=returns, title=f"Rendement sur {period} jours"
    ).update_layout(
        xaxis_title="", yaxis_title="Rendement (%)"
    )

def return_over_mooving_avg(data, return_perdiod, mm_period):
    out = {}
    for i in range(return_perdiod+mm_period, len(data)):
        mm = np.mean(data[i-return_perdiod-mm_period:i-return_perdiod])
        position_over_mm = int((data[i-return_perdiod] / mm - 1)*100)
        returns = data[i] / data[i-return_perdiod] - 1
        arr = out.get(position_over_mm, [])
        arr.append(returns *100)
        out[position_over_mm] = arr
    keys, values = [], []
    for k in out:
        keys.append(k)
        values.append(np.mean(out[k]))

    return px.bar(
        x=keys, y=values, title=f"Rendement sur {return_perdiod} jours en fonction de la position par rapport à la moyenne mobile {mm_period} jours"
    ).update_layout(
        xaxis_title="Position par rapport à la moyenne mobile (%)", yaxis_title="Rendement (%)"
    )    

def show_dashboard(data: pd.DataFrame):
    app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.PULSE])
    load_figure_template("pulse")
    data = data.sort_values("date")

    style = {'width': '48%', 'display': 'inline-block', "text-align": "center", "float": "center"}

    @callback(
        Output('graph-return-mm', 'figure'),
        Input('1-return-period', 'value'),
        Input('1-mm-period', 'value'))
    def create_graph_return(mm_period, return_period):
        return return_over_mooving_avg(data["value"].values, mm_period, return_period)
    
    @callback(
        Output('graph-value-at-risk', 'figure'),
        Input('return-period', 'value'))
    def create_graph_retur2(period):
        return returns_chart(data, period)

    app.layout = [
        html.H1(children='Analyse du portefeuille', style={'textAlign':'center'}),
        dcc.Graph(id='graph-content', figure=create_pf_value(data)),
        html.Div(children=f'Rendement annuel moyen: {number(mean_return(data["value"].values))} %', style={'textAlign':'center'}),
        html.Div(children=f'Volatilité: {number(volatility(data["value"].values))} %', style={'textAlign':'center'}),

        dcc.Graph(id='graph-returns', figure=create_pf_returns(data["value"].values)),

        dcc.Graph(id='graph-paretto', figure=positive_paretto(data["value"].values)),

        html.Div("Durée d'observation", style={"display": "block", "text-align": "center"}),
        html.Div([
            dcc.Dropdown([7, 30, 50, 100, 200, 300], 50, id='return-period')
        ], style={"width": "50%", "max-width": "350px", "margin-right": "auto", "margin-left": "auto"}),
        dcc.Graph(id='graph-value-at-risk', figure=returns_chart(data)),

        html.Div([
            html.Div("Période de la moyenne mobile", style=style),
            html.Div("Durée de l'observation", style=style),
        ]),
        html.Div([
            dcc.Dropdown([7, 30, 50, 100, 200, 300], 50, id='1-return-period', style=style
            ), dcc.Dropdown([7, 30, 50, 100, 200, 300],
                50, id='1-mm-period', style=style
            )
        ]),
        dcc.Graph(id='graph-return-mm', figure=return_over_mooving_avg(data["value"].values, 32, 100)),
    ]
    
    app.run(debug=True)



if __name__ == "__main__":
    show_dashboard(pd.read_csv("./out/example_pf.csv"))