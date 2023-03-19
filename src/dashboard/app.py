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

fig = px.line(price_data, x='datetime', y='close', title='Price')


price_graph = dcc.Graph(figure=fig, id='price-graph')

app.layout = html.Div([
    price_graph,
    dcc.Interval(id='interval-component',
                 interval=dashboard_settings.update_interval*1000,
                 n_intervals=0)
])


@app.callback(Output(price_graph, 'figure'),
              Input('interval-component', 'n_intervals'))
def update_price_graph(n):
    logger.debug('Updating price graph')
    start = time()
    price_data = pd.DataFrame(db[mongo_settings.db_price_collection].find())
    fig = px.line(price_data, x='datetime', y='close', title='Price')
    strategies = bot.get_running_strategies()
    print(strategies)
    for strategy in strategies:
        strategy.enrich_plot(fig)

    price_graph.figure = fig
    logger.debug(f'Price graph updated in {time() - start} seconds')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
