from threading import Thread

import data_gatherer
import app

data_thread = Thread(target=data_gatherer.start_loop)
data_thread.start()

app.app.run_server(debug=True)
