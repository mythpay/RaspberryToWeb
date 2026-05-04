import logging
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
import queue
import threading
import time
import os

# Set up the logging queue
log_queue = queue.Queue()

def setup_logging(app):
    # Create the logger
    logger = app.logger
    logger.setLevel(logging.INFO)

    # Set the base directory and log path
    basedir = os.path.abspath(os.path.dirname(__file__))
    log_dir = os.path.join(basedir, 'Logs')
    log_file = os.path.join(log_dir, 'app.log')

    # Set up RotatingFileHandler and log formatter 
    file_handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=10)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Create the QueueHandler and add it to the logger
    queue_handler = QueueHandler(log_queue)
    logger.addHandler(queue_handler)

    # Create the QueueListener
    listener = QueueListener(log_queue, file_handler)
    
    # Function to run the logging listener in a separate thread
    def start_logging_listener():
        listener.start()
        while True:
            # Avoid busy waiting 
            time.sleep(10)

    # Return the listener thread to be started in the main server file
    logging_thread = threading.Thread(target=start_logging_listener, daemon=True, name="Logger Thread")
    return logging_thread