from threading import Thread

from data_gatherer import data_gatherer
from dashboard import app

data_thread = Thread(target=data_gatherer.start_loop)
data_thread.start()

app.app.run_server(debug=True)
