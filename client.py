import socket
import f1decode
from f1enums import PacketIDs
import math
import json
from f1session import F1SessionManager, F1Session, session_query
import threading
from time import sleep
import os

PORT = 20777

session_manager = F1SessionManager()

def udp_loop():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("localhost", PORT))

    while True:
        # Read UDP packet
        data, addr = s.recvfrom(4096)
        if not data:
            break

        # Decode the packet
        packet = f1decode.decode_packet(bytearray(data))

        # Session manager dispatches packet to corresponding session
        session_manager.dispatch_packet(packet)


udp_thread = threading.Thread(target=udp_loop)
udp_thread.start()
        
while True:
    sleep(1)
    os.system('clear')
    print("\n --<[ Sessions ]>--")
    for session_uid in session_manager.sessions.keys():
        session: F1Session = session_manager.sessions[session_uid]
        active_str = "inactive"
        if session.is_active():
            active_str = "active"
        print("  > %d: %s session" % (session_uid, active_str))

        if session.is_active():
            player_data = session.get_participants(players_only=True)
            for player in player_data:
                print("      Player '%s':" % player["m_name"], player)
    
