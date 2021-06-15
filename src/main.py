import client
import traceback
import time

try:
    client.start_client()

    while True:
        time.sleep(1.0)

except Exception as err:
    print("Error:", err)
    traceback.print_exc()
finally:
    client.exit_client()
    client.udp_socket.close()