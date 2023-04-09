from datetime import datetime, timedelta

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from time import time

from src.wrappers.db_wrapper import get_database
from src.settings import logger, MongoSettings, DashboardSettings
from src.bot import bot

mongo_settings = MongoSettings()
dashboard_settings = DashboardSettings()

db = get_database()

app = Dash(__name__)

price_data = pd.DataFrame(db[mongo_settings.db_price_collection].find())

fig = px.line(price_data, x='datetime', y='close', title='Price', render_mode='webg1')
fig.update_xaxes(rangeslider_visible=True)

price_graph = dcc.Graph(figure=fig, id='price-graph')

app.layout = html.Div([
    price_graph,
    dcc.Interval(id='interval-component',
                 interval=dashboard_settings.update_interval * 1000,
                 n_intervals=0)
])


@app.callback(Output(price_graph, 'figure'),
              Input('interval-component', 'n_intervals'))
def update_price_graph(n):
    logger.debug('Updating price graph')
    start = time()
    price_data = pd.DataFrame(db[mongo_settings.db_price_collection].find())
    fig = px.line(price_data, x='datetime', y='close', title='Price', render_mode='webg1')

    strategies = bot.get_running_strategies()
    for strategy in strategies:
        strategy.enrich_plot(fig)

    reversed(fig.data)
    # fig.layout['uirevision'] =
    layout = fig.layout
    layout['uirevision'] = True
    fig.layout = layout

    fig.update_xaxes(rangeslider_visible=True,
                     rangeselector=dict(
                         buttons=list([
                             dict(count=15, label="15M", step="minute", stepmode="backward"),
                             dict(count=30, label="30M", step="minute", stepmode="backward"),
                             dict(count=1, label="1D", step="day", stepmode="backward"),
                             dict(count=1, label="1m", step="month", stepmode="backward"),
                             dict(count=6, label="6m", step="month", stepmode="backward"),
                             dict(count=1, label="YTD", step="year", stepmode="todate"),
                             dict(count=1, label="1y", step="year", stepmode="backward"),
                             dict(step="all")
                         ])
                     ))

    price_graph.figure = fig

    logger.debug(f'Price graph updated in {time() - start} seconds')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
