import threading
import time

print("Listening for MDB data... (press Ctrl+C to stop)\n")

class MDB(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("hi")

    def handle_command(self):
        try:
            while True:
                print("*** VMC READY - SUCCESS! ***")                  
                time.sleep(2)

        except KeyboardInterrupt:
            print("\nStopped.")
