import time
import config

def log(msg):
    if not config.CONFIG.get("/logging/stdout", False):
        return
    
    timestamp = time.strftime("[%d.%m.%y %H:%M:%S]")
    print(timestamp, msg)
