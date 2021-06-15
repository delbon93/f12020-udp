import client
import time
import f1decode
import f1session

session_manager = f1session.F1SessionManager()

def callback(packet):
    session_manager.dispatch_packet(packet)

udp_thread = client.UDPThread(20777, packet_decoder=f1decode.decode_packet, packet_handler=callback)
udp_thread.start()

while True:
    uids = [uid for uid in session_manager.sessions.keys()]
    print(uids, '\r', end="")
    time.sleep(0.1)


udp_thread.stop()