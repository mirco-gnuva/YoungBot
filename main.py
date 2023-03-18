from threading import Thread

from bot import bot
from dashboard import app

data_thread = Thread(target=data_gatherer.start_loop)
data_thread.start()

app.app.run_server(debug=True)
