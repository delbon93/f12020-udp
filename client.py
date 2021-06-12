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
        try:
            # Read UDP packet
            data, addr = s.recvfrom(4096)
            if not data:
                break

            # Decode the packet
            packet = f1decode.decode_packet(bytearray(data))

            # Session manager dispatches packet to corresponding session
            session_manager.dispatch_packet(packet)
        except Exception as err:
            print(err)
            os._exit(1)


udp_thread = threading.Thread(target=udp_loop)
udp_thread.start()
        
while True:
    try:
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
                # player_data = session.get_participants(players_only=True)
                players = session._players
                for driver_id in players.keys():
                    player_data = players[driver_id]
                    print("      Player '%s':" % player_data["data"]["m_name"], player_data)
    except Exception as err:
        print(err)
        udp_thread.join()
        exit(1)
