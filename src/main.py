from threading import Thread

from src.bot import bot
from src.dashboard import app

data_thread = Thread(target=bot.start_loop)
data_thread.start()

app.app.run_server(debug=True)
