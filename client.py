import os
import threading
import socket
import math
import f1decode
import f1database
import f1config
import time

from f1enums import PacketIDs
from f1session import F1SessionManager, F1Session, session_query

PORT = f1config.CONFIG.get("/client/udpPort", 20777)
CHECK_INACTIVE_SESSIONS_INTERVALL = f1config.CONFIG.get("/client/checkInactiveSessionsIntervall", 1.0)

upd_thread_running = True
session_manager = F1SessionManager()

def udp_loop():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("localhost", PORT))

    while upd_thread_running:
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

pending_transactions = []

def inactive_session_handler(session: F1Session):
    print("Session %d now inactive" % session.session_uid)

    if not session.has_best_lap_data():
        return

    track_id = session_query(session, 0, PacketIDs.SESSION_DATA, "content/m_trackId")
    session_type = session_query(session, 0, PacketIDs.SESSION_DATA, "content/m_sessionType")

    players = session._players
    for player_id in players.keys():
        car_index = players[player_id]['carIndex']
        player_name = players[player_id]['data']['m_name']
        team_id = players[player_id]['data']['m_teamId']
        tyre_compound = session_query(session, car_index, PacketIDs.CAR_STATUS_DATA,
            "content/m_carStatusData[@]/m_visualTyreCompound"
        )
        best_lap_time = session_query(session, car_index, PacketIDs.LAP_DATA,
            "content/m_lapData[@]/m_bestLapTime"
        )

        pending_transactions.append(f1database.generate_best_lap_data_sql_statement(
            player_name, track_id, session_type,
            team_id, tyre_compound, best_lap_time
        ))

        lap = session_query(session, car_index, PacketIDs.LAP_DATA,
            "content/m_lapData[@]/m_bestLapNum"
        )
        print("[Pending Database Transactions]")
        for ta in pending_transactions:
            print(" >", ta)


while True:
    try:
        time.sleep(CHECK_INACTIVE_SESSIONS_INTERVALL)
        session_manager.handle_inactive_sessions(inactive_session_handler, pop_on_inactive=True)


    except Exception as err:
        print(err)
        upd_thread_running = False
        udp_thread.join()
        exit(1)
